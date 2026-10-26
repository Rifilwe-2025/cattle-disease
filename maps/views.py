"""
Views for maps and disease surveillance.
"""
from collections import Counter, defaultdict
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.dateparse import parse_date

from cases.models import Case

# Severity colours, matching the heatmap gradient so the two pages agree.
SEVERITY_COLOURS = {
    'NON_SEVERE': '#2F7D4F',
    'SEVERE': '#E0A325',
    'CRITICAL': '#C1352B',
}

# Worst-first, for deciding the colour of a point that holds several cases.
SEVERITY_RANK = {'CRITICAL': 3, 'SEVERE': 2, 'NON_SEVERE': 1}

# Approximate centroids of Zimbabwe's ten provinces.
#
# Farmers supply their own GPS coordinates and most have not, so plotting only
# the cases that carry a lat/long hides most of the outbreak. A province with
# cases but no coordinates is drawn at its centroid instead, which is the
# resolution national surveillance actually reports at. Keys are matched
# case-insensitively against Farmer.province, which is free text.
PROVINCE_CENTROIDS = {
    'bulawayo': (-20.1700, 28.5800),
    'harare': (-17.8292, 31.0522),
    'manicaland': (-18.9216, 32.1746),
    'mashonaland central': (-16.7700, 31.0700),
    'mashonaland east': (-18.0000, 31.5000),
    'mashonaland west': (-17.4000, 30.0000),
    'masvingo': (-20.0744, 30.8328),
    'matabeleland north': (-18.5000, 27.5000),
    'matabeleland south': (-21.0000, 29.0000),
    'midlands': (-19.4500, 29.8167),
}


def ministry_required(view):
    """
    Restrict a view to ministry users.

    Anonymous users are handled by login_required, which sends them to the
    login page with ?next= so they land back here afterwards. An authenticated
    user who is simply the wrong role goes to their OWN dashboard instead:
    redirecting them to the login page - as this module used to - bounces
    through login_view, which sees an authenticated user and forwards to
    redirect_after_login, so they ended up on their dashboard anyway but via
    an extra hop that made the denial look like the page was broken.
    """
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_ministry():
            messages.error(
                request,
                'The disease surveillance map is available to Ministry '
                'administrators only.'
            )
            return redirect('accounts:redirect_after_login')
        return view(request, *args, **kwargs)
    return wrapper


def _case_filters(request):
    """
    Read the filter parameters off the querystring.

    Dates are parsed rather than passed through as strings: an unparseable
    value like ?date_from=yesterday reached the ORM directly before and raised
    ValidationError, turning a mistyped URL into a 500.
    """
    return {
        'disease': request.GET.get('disease', '').strip(),
        'province': request.GET.get('province', '').strip(),
        'date_from': parse_date(request.GET.get('date_from', '').strip() or ''),
        'date_to': parse_date(request.GET.get('date_to', '').strip() or ''),
    }


def _apply_filters(cases, filters):
    """Narrow a Case queryset by the active filters."""
    if filters['disease']:
        cases = cases.filter(predicted_disease__icontains=filters['disease'])
    if filters['province']:
        cases = cases.filter(farmer__province=filters['province'])
    # __date__gte/__date__lte compare calendar days. created_at is a datetime,
    # so a plain __lte=<date> was read as midnight and silently dropped every
    # case submitted later on the end date - including, most of the time, all
    # of today's.
    if filters['date_from']:
        cases = cases.filter(created_at__date__gte=filters['date_from'])
    if filters['date_to']:
        cases = cases.filter(created_at__date__lte=filters['date_to'])
    return cases


def _severity_colour(severity):
    return SEVERITY_COLOURS.get(severity, SEVERITY_COLOURS['NON_SEVERE'])


def _build_hotspots(cases):
    """
    Collapse cases onto the points where they actually occurred.

    One marker per case stacked 23 pins on a single farm and read as a single
    case. Grouping by coordinate turns that into one sized marker labelled
    with its case count, which is what makes a hotspot visible.
    """
    groups = defaultdict(list)
    for case in cases:
        if case.farmer.latitude is None or case.farmer.longitude is None:
            continue
        key = (round(float(case.farmer.latitude), 4), round(float(case.farmer.longitude), 4))
        groups[key].append(case)

    hotspots = []
    for (lat, lng), group in groups.items():
        worst = max(group, key=lambda c: SEVERITY_RANK.get(c.severity, 0)).severity
        diseases = Counter(c.predicted_disease for c in group)
        severities = Counter(c.severity for c in group)
        hotspots.append({
            'latitude': lat,
            'longitude': lng,
            'count': len(group),
            'province': group[0].farmer.province or 'Unknown',
            'district': group[0].farmer.district or '',
            'worst_severity': worst,
            'colour': _severity_colour(worst),
            'critical': severities.get('CRITICAL', 0),
            'severe': severities.get('SEVERE', 0),
            'non_severe': severities.get('NON_SEVERE', 0),
            'top_diseases': [
                {'name': name, 'count': n} for name, n in diseases.most_common(3)
            ],
            'latest': max(c.created_at for c in group).strftime('%Y-%m-%d'),
        })

    # Biggest first, so the worst hotspot draws underneath the smaller ones
    # rather than swallowing them.
    return sorted(hotspots, key=lambda h: h['count'], reverse=True)


def _build_provinces(cases):
    """
    Aggregate the filtered cases by province.

    Driven off Farmer.province rather than coordinates, so a province reports
    its true case load even when no farmer there has supplied a GPS fix.
    """
    groups = defaultdict(list)
    for case in cases:
        groups[(case.farmer.province or 'Unknown').strip()].append(case)

    provinces = []
    for name, group in groups.items():
        severities = Counter(c.severity for c in group)
        diseases = Counter(c.predicted_disease for c in group)
        worst = max(group, key=lambda c: SEVERITY_RANK.get(c.severity, 0)).severity
        centroid = PROVINCE_CENTROIDS.get(name.lower())
        top_disease, top_disease_count = diseases.most_common(1)[0]
        provinces.append({
            'name': name,
            'count': len(group),
            'critical': severities.get('CRITICAL', 0),
            'severe': severities.get('SEVERE', 0),
            'non_severe': severities.get('NON_SEVERE', 0),
            'worst_severity': worst,
            'colour': _severity_colour(worst),
            'top_disease': top_disease,
            'top_disease_count': top_disease_count,
            # None for a province name that is not one of the ten - 'Unknown',
            # or a typo. It still appears in the table, just not on the map.
            'latitude': centroid[0] if centroid else None,
            'longitude': centroid[1] if centroid else None,
        })

    return sorted(provinces, key=lambda p: p['count'], reverse=True)


@ministry_required
def disease_map(request):
    """
    Display disease distribution map with filters.
    """
    filters = _case_filters(request)
    cases = list(_apply_filters(Case.objects.select_related('farmer'), filters))

    hotspots = _build_hotspots(cases)
    provinces = _build_provinces(cases)

    # Filter options come from ALL cases, never from the filtered queryset.
    # Building the province list out of the filtered set meant that picking a
    # province left that province as the only option, so there was no way to
    # switch to another one without clearing the filter by hand.
    province_options = (
        Case.objects.exclude(farmer__province='')
        .values_list('farmer__province', flat=True)
        .distinct()
        .order_by('farmer__province')
    )
    disease_options = (
        Case.objects.exclude(predicted_disease='')
        .exclude(predicted_disease__isnull=True)
        .values_list('predicted_disease', flat=True)
        .distinct()
        .order_by('predicted_disease')
    )

    mapped_cases = sum(h['count'] for h in hotspots)

    context = {
        'hotspots': hotspots,
        'provinces': provinces,
        'province_options': province_options,
        'disease_options': disease_options,
        'total_cases': len(cases),
        'mapped_cases': mapped_cases,
        'unmapped_cases': len(cases) - mapped_cases,
        'affected_provinces': len(provinces),
        'critical_total': sum(p['critical'] for p in provinces),
        'severity_colours': SEVERITY_COLOURS,
        'disease_filter': filters['disease'],
        'province_filter': filters['province'],
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'active_menu': 'disease_map',
    }

    return render(request, 'maps/disease_map.html', context)


@ministry_required
def heatmap(request):
    """
    Display disease heatmap visualization.
    """
    cases = Case.objects.select_related('farmer').filter(
        farmer__latitude__isnull=False,
        farmer__longitude__isnull=False,
    )

    intensities = {'NON_SEVERE': 1, 'SEVERE': 2, 'CRITICAL': 3}
    heatmap_data = [
        {
            'lat': float(case.farmer.latitude),
            'lng': float(case.farmer.longitude),
            'intensity': intensities.get(case.severity, 1),
        }
        for case in cases
    ]

    context = {
        'heatmap_data': heatmap_data,
        'total_points': len(heatmap_data),
        'active_menu': 'heatmap',
    }

    return render(request, 'maps/heatmap.html', context)
