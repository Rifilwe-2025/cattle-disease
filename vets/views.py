"""
Views for the Vets app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.formats import date_format
from django.db.models import Count, Q
from datetime import timedelta
from collections import defaultdict
from django.http import HttpResponse
import csv
from .models import VetApplication, Vet, VaccineRequest, VetAreaReport
from .forms import (
    VetApplicationForm,
    VetRegistrationForm,
    VetConsultationForm,
    VetProfileForm,
    VaccineRequestForm,
    VetAreaReportForm,
)
from cases.models import Case


def apply(request):
    """
    Public view for vet doctors to apply for registration.
    """
    if request.method == 'POST':
        form = VetApplicationForm(request.POST)
        if form.is_valid():
            application = form.save()
            messages.success(
                request,
                f'Application submitted successfully! Your Application ID is: {application.application_id}. Please save this ID to track your application status.'
            )
            # Redirect to success page showing application ID
            return redirect('vets:application_success', application_id=application.application_id)
    else:
        form = VetApplicationForm()
    
    return render(request, 'vets/apply.html', {'form': form})


def application_success(request, application_id):
    """
    Show application success page with tracking information.
    """
    application = get_object_or_404(VetApplication, application_id=application_id)
    
    context = {
        'application': application,
    }
    
    return render(request, 'vets/application_success.html', context)


def track_application(request):
    """
    Allow vets to track their application status using Application ID.
    """
    application = None
    error_message = None
    
    if request.method == 'POST':
        application_id = request.POST.get('application_id', '').strip().upper()
        
        if not application_id:
            error_message = "Please enter your Application ID."
        else:
            try:
                application = VetApplication.objects.get(application_id=application_id)
            except VetApplication.DoesNotExist:
                error_message = f"Application ID '{application_id}' not found. Please check your ID and try again."
    
    context = {
        'application': application,
        'error_message': error_message,
    }
    
    return render(request, 'vets/track_application.html', context)


def save_id_guide(request):
    """
    Show guide on how to save Application ID.
    """
    return render(request, 'vets/save_application_id_guide.html')


@login_required
def help_center(request):
    """
    Help center for vet doctors: explains the vet dashboard,
    how to work with cases, and how to communicate with the Ministry.
    """
    if not request.user.is_vet():
        messages.error(request, 'Access denied. Vet doctors only.')
        return redirect('accounts:login')

    vet = None
    try:
        vet = Vet.objects.get(user=request.user)
    except Vet.DoesNotExist:
        vet = None

    # Basic quick stats for context
    total_cases = Case.objects.filter(assigned_vet=vet).count() if vet else 0
    resolved_cases = Case.objects.filter(
        assigned_vet=vet,
        status__in=['RESOLVED', 'CLOSED']
    ).count() if vet else 0
    pending_cases = Case.objects.filter(
        assigned_vet=vet,
        status__in=['ASSIGNED', 'IN_PROGRESS']
    ).count() if vet else 0

    context = {
        'vet': vet,
        'total_cases': total_cases,
        'resolved_cases': resolved_cases,
        'pending_cases': pending_cases,
    }
    return render(request, 'vets/help_center.html', context)


@login_required
def dashboard(request):
    """
    Vet dashboard showing assigned cases and statistics.
    """
    if not request.user.is_vet():
        messages.error(request, 'Access denied. Vet doctors only.')
        return redirect('accounts:login')
    
    try:
        vet = Vet.objects.get(user=request.user)
    except Vet.DoesNotExist:
        messages.error(request, 'Vet profile not found. Please contact administrator.')
        return redirect('accounts:login')
    
    # Get cases assigned to this vet
    assigned_cases = Case.objects.filter(assigned_vet=vet).order_by('-created_at')[:10]
    total_cases = Case.objects.filter(assigned_vet=vet).count()
    pending_cases = Case.objects.filter(assigned_vet=vet, status='ASSIGNED').count()
    in_progress_cases = Case.objects.filter(assigned_vet=vet, status='IN_PROGRESS').count()
    resolved_cases = Case.objects.filter(assigned_vet=vet, status__in=['RESOLVED', 'CLOSED']).count()
    critical_cases = Case.objects.filter(assigned_vet=vet, severity='CRITICAL', status__in=['ASSIGNED', 'IN_PROGRESS']).count()
    
    # Unique farmers served
    farmers_served = Case.objects.filter(assigned_vet=vet).values('farmer').distinct().count()
    
    # New cases this month
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_cases_month = Case.objects.filter(assigned_vet=vet, created_at__gte=month_start).count()
    
    # Disease distribution for donut chart
    disease_stats = Case.objects.filter(assigned_vet=vet).values('predicted_disease').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    # Simple case statistics over last 12 months, by actual day
    today = timezone.now().date()
    chart_start = today - timedelta(days=364)
    chart_end = today

    recent_cases = Case.objects.filter(
        assigned_vet=vet,
        created_at__date__gte=chart_start,
    ).order_by('created_at')

    daily_totals = defaultdict(int)
    for c in recent_cases:
        day = c.created_at.date()
        daily_totals[day] += 1

    chart_labels = []
    chart_counts = []
    for i in range(365):
        day = chart_start + timedelta(days=i)
        chart_labels.append(date_format(day, format='d M Y'))
        chart_counts.append(daily_totals.get(day, 0))
    
    # Top diagnoses for bar chart
    top_diagnoses = Case.objects.filter(assigned_vet=vet).values('predicted_disease').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Farmers under care (recent cases with farmer info)
    farmers_with_cases = []
    seen = set()
    for case in Case.objects.filter(assigned_vet=vet).select_related('farmer').order_by('-created_at')[:5]:
        if case.farmer_id not in seen:
            seen.add(case.farmer_id)
            farmers_with_cases.append({'farmer': case.farmer, 'case': case})
    
    # Resolution rate
    resolution_rate = int((resolved_cases / total_cases * 100)) if total_cases > 0 else 0

    # Monthly resolution rate for the last 12 months (for mini chart)
    twelve_months_ago = timezone.now() - timedelta(days=365)
    recent_for_resolution = Case.objects.filter(
        assigned_vet=vet,
        created_at__gte=twelve_months_ago
    )
    month_buckets = defaultdict(lambda: {'total': 0, 'resolved': 0})
    for c in recent_for_resolution:
        month_key = c.created_at.strftime('%Y-%m')
        month_buckets[month_key]['total'] += 1
        if c.status in ('RESOLVED', 'CLOSED'):
            month_buckets[month_key]['resolved'] += 1

    res_month_labels = []
    res_month_values = []
    now = timezone.now()
    res_current_total = 0
    res_current_resolved = 0
    for i in range(12):
        month_num = now.month - 11 + i
        year = now.year
        if month_num <= 0:
            month_num += 12
            year -= 1
        key = f'{year}-{month_num:02d}'
        label_dt = timezone.datetime(year, month_num, 1, tzinfo=timezone.get_current_timezone()).date()
        label = date_format(label_dt, format='M Y')
        bucket = month_buckets.get(key, {'total': 0, 'resolved': 0})
        total_m = bucket['total']
        resolved_m = bucket['resolved']
        percent = int((resolved_m / total_m * 100)) if total_m > 0 else 0
        res_month_labels.append(label)
        res_month_values.append(percent)
        if year == now.year and month_num == now.month:
            res_current_total = total_m
            res_current_resolved = resolved_m
    res_current_rate = int((res_current_resolved / res_current_total * 100)) if res_current_total > 0 else 0
    
    context = {
        'vet': vet,
        'assigned_cases': assigned_cases,
        'total_cases': total_cases,
        'pending_cases': pending_cases,
        'in_progress_cases': in_progress_cases,
        'resolved_cases': resolved_cases,
        'critical_cases': critical_cases,
        'farmers_served': farmers_served,
        'new_cases_month': new_cases_month,
        'disease_stats': disease_stats,
        'chart_labels': chart_labels,
        'chart_counts': chart_counts,
        'chart_start': chart_start,
        'chart_end': chart_end or today,
        'res_month_labels': res_month_labels,
        'res_month_values': res_month_values,
        'res_current_total': res_current_total,
        'res_current_resolved': res_current_resolved,
        'res_current_rate': res_current_rate,
        'top_diagnoses': top_diagnoses,
        'farmers_with_cases': farmers_with_cases,
        'resolution_rate': resolution_rate,
    }
    
    return render(request, 'vets/dashboard.html', context)


@login_required
def vaccine_requests(request):
    """
    Vet-facing page to create and track vaccine / medical stock requests
    sent to the Ministry.
    """
    if not request.user.is_vet():
        messages.error(request, 'Access denied. Vet doctors only.')
        return redirect('accounts:login')

    vet = get_object_or_404(Vet, user=request.user)

    if request.method == 'POST':
        form = VaccineRequestForm(request.POST)
        if form.is_valid():
            vaccine_request = form.save(commit=False)
            vaccine_request.vet = vet
            vaccine_request.save()
            messages.success(request, 'Vaccine request sent to Ministry successfully.')
            return redirect('vets:vaccine_requests')
        else:
            messages.error(request, 'Please fix the errors in the form below.')
    else:
        form = VaccineRequestForm()

    requests_qs = VaccineRequest.objects.filter(vet=vet).order_by('-created_at')

    context = {
        'vet': vet,
        'form': form,
        'requests': requests_qs,
    }
    return render(request, 'vets/vaccine_requests.html', context)


@login_required
def area_reports(request):
    """
    Vet-facing page to submit situation / area reports to the Ministry.
    """
    if not request.user.is_vet():
        messages.error(request, 'Access denied. Vet doctors only.')
        return redirect('accounts:login')

    vet = get_object_or_404(Vet, user=request.user)

    if request.method == 'POST':
        form = VetAreaReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.vet = vet
            report.save()
            messages.success(request, 'Report submitted to Ministry successfully.')
            return redirect('vets:area_reports')
        else:
            messages.error(request, 'Please fix the errors in the form below.')
    else:
        form = VetAreaReportForm()

    reports_qs = VetAreaReport.objects.filter(vet=vet).order_by('-created_at')

    context = {
        'vet': vet,
        'form': form,
        'reports': reports_qs,
    }
    return render(request, 'vets/area_reports.html', context)


@login_required
def export_cases_csv(request):
    """
    Export all cases for this vet as a CSV file that can be opened in Excel.
    """
    if not request.user.is_vet():
        messages.error(request, 'Access denied. Vet doctors only.')
        return redirect('accounts:login')

    vet = get_object_or_404(Vet, user=request.user)
    cases = Case.objects.filter(assigned_vet=vet).select_related('farmer').order_by('-created_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cattlecare_cases_vet.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Farmer', 'Predicted disease', 'Severity', 'Status'])

    for c in cases:
        writer.writerow([
            timezone.localtime(c.created_at).strftime('%Y-%m-%d %H:%M'),
            c.farmer.full_name if c.farmer else '',
            c.predicted_disease,
            c.severity,
            c.status,
        ])

    return response


@login_required
def farmers_list(request):
    """
    Page showing all farmers assigned to this vet with their cases.
    """
    if not request.user.is_vet():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    vet = get_object_or_404(Vet, user=request.user)
    
    # Get unique farmers with their cases
    farmer_ids = Case.objects.filter(assigned_vet=vet).values_list('farmer_id', flat=True).distinct()
    farmers_with_cases = []
    for farmer_id in farmer_ids:
        farmer = None
        farmer_cases = Case.objects.filter(assigned_vet=vet, farmer_id=farmer_id).select_related('farmer').order_by('-created_at')
        if farmer_cases.exists():
            farmer = farmer_cases.first().farmer
            farmers_with_cases.append({
                'farmer': farmer,
                'cases': farmer_cases,
                'case_count': farmer_cases.count(),
                'resolved_count': farmer_cases.filter(status__in=['RESOLVED', 'CLOSED']).count(),
            })
    
    context = {
        'vet': vet,
        'farmers_with_cases': farmers_with_cases,
        'total_farmers': len(farmers_with_cases),
    }
    return render(request, 'vets/farmers_list.html', context)


@login_required
def profile_edit(request):
    """Vet profile edit."""
    if not request.user.is_vet():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')

    vet = get_object_or_404(Vet, user=request.user)

    if request.method == 'POST':
        form = VetProfileForm(request.POST, request.FILES, instance=vet)
        if form.is_valid():
            form.save()
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('vets:profile_edit')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = VetProfileForm(instance=vet)

    return render(request, 'vets/profile_edit.html', {'vet': vet, 'form': form})


@login_required
def cases_list(request):
    """
    Page showing all cases grouped by status (Assigned, In Progress, Resolved).
    """
    if not request.user.is_vet():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    vet = get_object_or_404(Vet, user=request.user)

    query = request.GET.get('q', '').strip()
    filter_flag = request.GET.get('filter', '').strip()

    # Base queryset
    base_qs = Case.objects.filter(assigned_vet=vet).select_related('farmer').order_by('-created_at')

    if query:
        base_qs = base_qs.filter(
            Q(farmer__full_name__icontains=query) |
            Q(predicted_disease__icontains=query) |
            Q(status__icontains=query)
        )

    # Group cases by status (with optional "critical" filter used by bell icon)
    if filter_flag == 'critical':
        base_qs = base_qs.filter(severity='CRITICAL', status__in=['ASSIGNED', 'IN_PROGRESS'])

    assigned_cases = base_qs.filter(status='ASSIGNED')
    in_progress_cases = base_qs.filter(status='IN_PROGRESS')
    resolved_cases = base_qs.filter(status__in=['RESOLVED', 'CLOSED'])
    
    total_resolved = Case.objects.filter(assigned_vet=vet, status__in=['RESOLVED', 'CLOSED']).count()
    total_assigned = Case.objects.filter(assigned_vet=vet).count()
    
    context = {
        'vet': vet,
        'assigned_cases': assigned_cases,
        'in_progress_cases': in_progress_cases,
        'resolved_cases': resolved_cases,
        'total_resolved': total_resolved,
        'total_assigned': total_assigned,
        'search_query': query,
        'filter_flag': filter_flag,
    }
    return render(request, 'vets/cases_list.html', context)


def register_by_app_id(request, application_id):
    """
    Approved vets can register using their Application ID (e.g., VET-2026-A1B2C3).
    This is the preferred method for vets who tracked their application.
    """
    try:
        application = VetApplication.objects.get(application_id=application_id, status='APPROVED')
    except VetApplication.DoesNotExist:
        messages.error(request, 'Application not found or not yet approved.')
        return redirect('vets:track_application')
    
    # Check if vet already registered
    if Vet.objects.filter(application=application).exists():
        messages.info(request, 'You have already registered with this application. Please login.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        form = VetRegistrationForm(request.POST)
        if form.is_valid():
            from accounts.models import User
            
            # Create user account
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                role='VET',
                phone_number=form.cleaned_data['phone_number'],
                email=form.cleaned_data['email']
            )
            
            # Prepare provinces_served
            provinces_served = application.provinces_served if isinstance(application.provinces_served, list) else []
            selected_province = form.cleaned_data['province']
            if selected_province not in provinces_served:
                provinces_served.append(selected_province)
            
            # Create vet profile
            vet = Vet.objects.create(
                user=user,
                application=application,
                full_name=application.full_name,
                phone_number=form.cleaned_data['phone_number'],
                email=form.cleaned_data['email'],
                license_number=application.license_number,
                qualification=application.qualification,
                years_of_experience=application.years_of_experience,
                provinces_served=provinces_served,
                latitude=form.cleaned_data.get('latitude') or application.latitude,
                longitude=form.cleaned_data.get('longitude') or application.longitude,
                is_approved=True,
                is_available=form.cleaned_data.get('is_available', True)
            )
            
            messages.success(
                request, 
                f'✅ Registration successful, Dr. {application.full_name}! You can now login with your credentials.'
            )
            return redirect('accounts:login')
    else:
        # Pre-fill form with application data
        initial_data = {
            'email': application.email,
            'phone_number': application.phone_number,
            'latitude': application.latitude,
            'longitude': application.longitude,
            'is_available': True
        }
        form = VetRegistrationForm(initial=initial_data)
    
    context = {
        'form': form,
        'application': application,
    }
    
    return render(request, 'vets/register.html', context)


def register(request, application_id):
    """
    Legacy register view using database ID (for backward compatibility).
    Redirects to application ID-based registration.
    """
    application = get_object_or_404(VetApplication, id=application_id, status='APPROVED')
    return redirect('vets:register_by_app_id', application_id=application.application_id)
    
    # Check if vet already registered
    if Vet.objects.filter(application=application).exists():
        messages.info(request, 'You have already registered with this application. Please login.')
        return redirect('accounts:login')
    
    if request.method == 'POST':
        form = VetRegistrationForm(request.POST)
        if form.is_valid():
            from accounts.models import User
            
            # Create user account
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                role='VET',
                phone_number=form.cleaned_data['phone_number'],
                email=form.cleaned_data['email']
            )
            
            # Prepare provinces_served - add the selected province if not in application provinces
            provinces_served = application.provinces_served if isinstance(application.provinces_served, list) else []
            selected_province = form.cleaned_data['province']
            if selected_province not in provinces_served:
                provinces_served.append(selected_province)
            
            # Create vet profile
            vet = Vet.objects.create(
                user=user,
                application=application,
                full_name=application.full_name,
                phone_number=form.cleaned_data['phone_number'],
                email=form.cleaned_data['email'],
                license_number=application.license_number,
                qualification=application.qualification,
                years_of_experience=application.years_of_experience,
                provinces_served=provinces_served,
                latitude=form.cleaned_data.get('latitude') or application.latitude,
                longitude=form.cleaned_data.get('longitude') or application.longitude,
                is_approved=True,
                is_available=form.cleaned_data.get('is_available', True)
            )
            
            messages.success(
                request, 
                f'✅ Registration successful, Dr. {application.full_name}! You can now login with your credentials.'
            )
            return redirect('accounts:login')
    else:
        # Pre-fill form with application data
        initial_data = {
            'email': application.email,
            'phone_number': application.phone_number,
            'latitude': application.latitude,
            'longitude': application.longitude,
            'is_available': True
        }
        form = VetRegistrationForm(initial=initial_data)
    
    context = {
        'form': form,
        'application': application,
    }
    
    return render(request, 'vets/register.html', context)


@login_required
def case_detail(request, case_id):
    """
    View case details and submit consultation.
    """
    if not request.user.is_vet():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    vet = get_object_or_404(Vet, user=request.user)
    case = get_object_or_404(Case, id=case_id, assigned_vet=vet)
    
    if request.method == 'POST':
        form = VetConsultationForm(request.POST)
        if form.is_valid():
            case.vet_diagnosis = form.cleaned_data['diagnosis']
            case.vet_recommendations = form.cleaned_data['recommendations']
            case.vet_consultation_date = timezone.now()
            case.status = 'IN_PROGRESS'
            case.save()
            
            messages.success(request, 'Consultation submitted successfully.')
            return redirect('vets:dashboard')
    else:
        form = VetConsultationForm()
    
    context = {
        'case': case,
        'vet': vet,
        'form': form,
    }
    
    return render(request, 'vets/case_detail.html', context)


@login_required
def accept_case(request, case_id):
    """
    Vet accepts an assigned case.
    """
    if not request.user.is_vet():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    vet = get_object_or_404(Vet, user=request.user)
    case = get_object_or_404(Case, id=case_id, assigned_vet=vet)
    
    case.status = 'IN_PROGRESS'
    case.save()
    
    messages.success(request, 'Case accepted and marked as in progress.')
    return redirect('vets:case_detail', case_id=case.id)


@login_required
def resolve_case(request, case_id):
    """
    Vet marks a case as resolved.
    """
    if not request.user.is_vet():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    vet = get_object_or_404(Vet, user=request.user)
    case = get_object_or_404(Case, id=case_id, assigned_vet=vet)
    
    case.status = 'RESOLVED'
    case.resolved_at = timezone.now()
    case.save()
    
    messages.success(request, 'Case marked as resolved.')
    return redirect('vets:dashboard')
