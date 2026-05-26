"""
Views for maps and disease surveillance.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from cases.models import Case
from farmers.models import Farmer


@login_required
def disease_map(request):
    """
    Display disease distribution map with filters.
    """
    if not request.user.is_ministry():
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'Access denied. Ministry administrators only.')
        return redirect('accounts:login')
    
    # Get filter parameters
    disease_filter = request.GET.get('disease', '')
    province_filter = request.GET.get('province', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Build query
    cases = Case.objects.select_related('farmer').all()
    
    if disease_filter:
        cases = cases.filter(predicted_disease__icontains=disease_filter)
    if province_filter:
        cases = cases.filter(farmer__province=province_filter)
    if date_from:
        cases = cases.filter(created_at__gte=date_from)
    if date_to:
        cases = cases.filter(created_at__lte=date_to)
    
    # Get cases with location data for mapping
    cases_with_location = cases.filter(
        farmer__latitude__isnull=False,
        farmer__longitude__isnull=False
    )
    
    # Prepare data for map
    map_data = []
    for case in cases_with_location:
        map_data.append({
            'id': case.id,
            'disease': case.predicted_disease,
            'severity': case.severity,
            'latitude': float(case.farmer.latitude),
            'longitude': float(case.farmer.longitude),
            'province': case.farmer.province,
            'district': case.farmer.district,
            'date': case.created_at.strftime('%Y-%m-%d'),
        })
    
    # Get province-level statistics
    province_stats = cases.values('farmer__province').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Get disease list for filter
    diseases = Case.objects.values_list('predicted_disease', flat=True).distinct()
    
    import json
    
    context = {
        'map_data': json.dumps(map_data),
        'province_stats': province_stats,
        'diseases': diseases,
        'disease_filter': disease_filter,
        'province_filter': province_filter,
        'date_from': date_from,
        'date_to': date_to,
        'active_menu': 'disease_map',
    }
    
    return render(request, 'maps/disease_map.html', context)


@login_required
def heatmap(request):
    """
    Display disease heatmap visualization.
    """
    if not request.user.is_ministry():
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'Access denied. Ministry administrators only.')
        return redirect('accounts:login')
    
    # Get all cases with location
    cases = Case.objects.select_related('farmer').filter(
        farmer__latitude__isnull=False,
        farmer__longitude__isnull=False
    )
    
    # Prepare heatmap data
    heatmap_data = []
    for case in cases:
        heatmap_data.append({
            'lat': float(case.farmer.latitude),
            'lng': float(case.farmer.longitude),
            'intensity': 1 if case.severity == 'NON_SEVERE' else (2 if case.severity == 'SEVERE' else 3),
        })
    
    context = {
        'heatmap_data': heatmap_data,
    }
    
    return render(request, 'maps/heatmap.html', context)
