"""
Views for the Ministry of Agriculture admin module.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from vets.models import VetApplication, Vet, VaccineRequest, VetAreaReport
from cases.models import Case
from farmers.models import Farmer
from accounts.models import User


@login_required
def dashboard(request):
    """
    Ministry admin dashboard with statistics and overview.
    """
    if not request.user.is_ministry():
        messages.error(request, 'Access denied. Ministry administrators only.')
        return redirect('accounts:login')
    
    # Statistics
    total_farmers = Farmer.objects.count()
    total_vets = Vet.objects.filter(is_approved=True).count()
    total_cases = Case.objects.count()
    pending_cases = Case.objects.filter(status='PENDING').count()
    critical_cases = Case.objects.filter(severity='CRITICAL', status__in=['PENDING', 'ASSIGNED']).count()
    
    # Pending vet applications
    pending_applications = VetApplication.objects.filter(status='PENDING').count()
    
    # Recent cases
    recent_cases = Case.objects.order_by('-created_at')[:10]
    
    # Disease distribution
    disease_stats = Case.objects.values('predicted_disease').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Cases by province for donut chart
    province_stats = Case.objects.values('farmer__province').annotate(
        count=Count('id')
    ).order_by('-count')[:4]
    
    # Monthly case counts for line chart (last 12 months)
    from datetime import timedelta
    from collections import defaultdict
    twelve_months_ago = timezone.now() - timedelta(days=365)
    cases_in_range = Case.objects.filter(created_at__gte=twelve_months_ago)
    monthly_totals = defaultdict(lambda: {'critical': 0, 'pending': 0, 'resolved': 0})
    for c in cases_in_range:
        key = c.created_at.strftime('%Y-%m')
        if c.severity == 'CRITICAL':
            monthly_totals[key]['critical'] += 1
        elif c.status in ('RESOLVED', 'CLOSED'):
            monthly_totals[key]['resolved'] += 1
        else:
            monthly_totals[key]['pending'] += 1
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    chart_critical, chart_pending, chart_resolved = [], [], []
    for i in range(12):
        month_num = timezone.now().month - 12 + i
        year = timezone.now().year
        if month_num <= 0:
            month_num += 12
            year -= 1
        key = f'{year}-{month_num:02d}'
        d = monthly_totals.get(key, {'critical': 0, 'pending': 0, 'resolved': 0})
        chart_critical.append(d['critical'])
        chart_pending.append(d['pending'])
        chart_resolved.append(d['resolved'])
    
    context = {
        'total_farmers': total_farmers,
        'total_vets': total_vets,
        'total_cases': total_cases,
        'pending_cases': pending_cases,
        'critical_cases': critical_cases,
        'pending_applications': pending_applications,
        'recent_cases': recent_cases,
        'disease_stats': disease_stats,
        'province_stats': province_stats,
        'chart_critical': chart_critical,
        'chart_pending': chart_pending,
        'chart_resolved': chart_resolved,
        'month_names': month_names,
        'active_menu': 'dashboard',
    }
    
    return render(request, 'ministry/dashboard.html', context)


@login_required
def vet_applications(request):
    """
    View and manage vet applications.
    """
    if not request.user.is_ministry():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    applications = VetApplication.objects.all().order_by('-created_at')
    pending = applications.filter(status='PENDING')
    approved = applications.filter(status='APPROVED')
    rejected = applications.filter(status='REJECTED')
    
    context = {
        'applications': applications,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'active_menu': 'applications',
    }
    
    return render(request, 'ministry/vet_applications.html', context)


@login_required
def approve_vet(request, application_id):
    """
    Approve a vet application.
    """
    if not request.user.is_ministry():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    application = get_object_or_404(VetApplication, id=application_id)
    
    if application.status != 'PENDING':
        messages.error(request, 'This application has already been processed.')
        return redirect('ministry:vet_applications')
    
    application.status = 'APPROVED'
    application.approved_by = request.user
    application.approved_at = timezone.now()
    application.save()
    
    messages.success(request, f'Vet application for {application.full_name} has been approved.')
    return redirect('ministry:vet_applications')


@login_required
def reject_vet(request, application_id):
    """
    Reject a vet application.
    """
    if not request.user.is_ministry():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    application = get_object_or_404(VetApplication, id=application_id)
    
    if application.status != 'PENDING':
        messages.error(request, 'This application has already been processed.')
        return redirect('ministry:vet_applications')
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        application.status = 'REJECTED'
        application.rejection_reason = rejection_reason
        application.approved_by = request.user
        application.approved_at = timezone.now()
        application.save()
        
        messages.success(request, f'Vet application for {application.full_name} has been rejected.')
        return redirect('ministry:vet_applications')
    
    return render(request, 'ministry/reject_vet.html', {'application': application})


@login_required
def analytics(request):
    """
    Disease analytics and statistics.
    """
    if not request.user.is_ministry():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    # Disease distribution
    disease_stats = Case.objects.values('predicted_disease').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Severity distribution
    severity_stats = Case.objects.values('severity').annotate(
        count=Count('id')
    )
    
    # Cases by province
    province_stats = Case.objects.values('farmer__province').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Cases over time (last 30 days)
    from datetime import timedelta
    from django.utils import timezone
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_cases = Case.objects.filter(created_at__gte=thirty_days_ago).count()
    
    context = {
        'disease_stats': disease_stats,
        'severity_stats': severity_stats,
        'province_stats': province_stats,
        'recent_cases': recent_cases,
        'active_menu': 'analytics',
    }
    
    return render(request, 'ministry/analytics.html', context)


@login_required
def reports(request):
    """
    Generate and view reports.
    """
    if not request.user.is_ministry():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    # Get filter parameters
    disease_filter = request.GET.get('disease', '')
    province_filter = request.GET.get('province', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Build query
    cases = Case.objects.all()
    
    if disease_filter:
        cases = cases.filter(predicted_disease__icontains=disease_filter)
    if province_filter:
        cases = cases.filter(farmer__province=province_filter)
    if date_from:
        cases = cases.filter(created_at__gte=date_from)
    if date_to:
        cases = cases.filter(created_at__lte=date_to)
    
    cases = cases.order_by('-created_at')
    
    context = {
        'cases': cases,
        'disease_filter': disease_filter,
        'province_filter': province_filter,
        'date_from': date_from,
        'date_to': date_to,
        'active_menu': 'reports',
    }
    
    return render(request, 'ministry/reports.html', context)


@login_required
def cases_overview(request):
    """
    High-level view of all cases for the Ministry, separate from the reports page.
    Provides quick filters for status and severity.
    """
    if not request.user.is_ministry():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')

    status_filter = request.GET.get('status', '').lower()
    search_query = request.GET.get('q', '').strip()

    cases = Case.objects.select_related('farmer', 'assigned_vet').order_by('-created_at')

    # Apply status / severity filters
    if status_filter == 'critical':
        cases = cases.filter(severity='CRITICAL')
    elif status_filter == 'pending':
        cases = cases.filter(status__in=['PENDING', 'ASSIGNED', 'IN_PROGRESS'])
    elif status_filter == 'resolved':
        cases = cases.filter(status__in=['RESOLVED', 'CLOSED'])

    # Simple search by farmer name or predicted disease
    if search_query:
        cases = cases.filter(
            Q(farmer__full_name__icontains=search_query) |
            Q(predicted_disease__icontains=search_query)
        )

    # Summary metrics
    total_cases = Case.objects.count()
    active_cases = Case.objects.filter(status__in=['PENDING', 'ASSIGNED', 'IN_PROGRESS']).count()
    resolved_cases = Case.objects.filter(status__in=['RESOLVED', 'CLOSED']).count()
    critical_cases = Case.objects.filter(severity='CRITICAL').count()

    context = {
        'cases': cases[:200],  # limit for performance
        'total_cases': total_cases,
        'active_cases': active_cases,
        'resolved_cases': resolved_cases,
        'critical_cases': critical_cases,
        'status_filter': status_filter,
        'search_query': search_query,
        'active_menu': 'cases',
    }

    return render(request, 'ministry/cases_overview.html', context)


@login_required
def tasks_overview(request):
    """
    Task centre for the Ministry admin.
    Groups pending work items like vet applications, critical cases,
    vaccine requests and unread vet reports.
    """
    if not request.user.is_ministry():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')

    pending_applications = VetApplication.objects.filter(status='PENDING').order_by('-created_at')[:20]
    critical_cases = Case.objects.filter(
        severity='CRITICAL',
        status__in=['PENDING', 'ASSIGNED', 'IN_PROGRESS']
    ).select_related('farmer')[:20]
    open_vaccine_requests = VaccineRequest.objects.filter(
        status__in=['PENDING', 'PARTIAL']
    ).select_related('vet')[:20]
    unread_area_reports = VetAreaReport.objects.filter(status='SUBMITTED').select_related('vet')[:20]

    context = {
        'pending_applications': pending_applications,
        'critical_cases': critical_cases,
        'open_vaccine_requests': open_vaccine_requests,
        'unread_area_reports': unread_area_reports,
        'total_tasks':
            pending_applications.count()
            + critical_cases.count()
            + open_vaccine_requests.count()
            + unread_area_reports.count(),
        'active_menu': 'tasks',
    }

    return render(request, 'ministry/tasks.html', context)


@login_required
def vaccine_requests(request):
    """
    Ministry view to see and respond to vaccine / medical stock requests
    coming from vets.
    """
    if not request.user.is_ministry():
        messages.error(request, 'Access denied. Ministry administrators only.')
        return redirect('accounts:login')

    if request.method == 'POST':
        req_id = request.POST.get('request_id')
        status = request.POST.get('status')
        response_text = request.POST.get('ministry_response', '').strip()
        vaccine_request = get_object_or_404(VaccineRequest, id=req_id)
        if status in dict(VaccineRequest.STATUS_CHOICES):
            vaccine_request.status = status
        if response_text:
            vaccine_request.ministry_response = response_text
        vaccine_request.responded_by = request.user
        vaccine_request.responded_at = timezone.now()
        vaccine_request.save()
        messages.success(request, 'Response saved for vaccine request.')
        return redirect('ministry:vaccine_requests')

    # List all requests (newest first)
    all_requests = VaccineRequest.objects.select_related('vet', 'vet__user').order_by('-created_at')

    context = {
        'all_requests': all_requests,
        'active_menu': 'vaccine_requests',
    }
    return render(request, 'ministry/vaccine_requests.html', context)


@login_required
def vet_reports_admin(request):
    """
    Ministry view to see narrative vet reports and respond / mark as read.
    """
    if not request.user.is_ministry():
        messages.error(request, 'Access denied. Ministry administrators only.')
        return redirect('accounts:login')

    if request.method == 'POST':
        report_id = request.POST.get('report_id')
        status = request.POST.get('status')
        response_text = request.POST.get('ministry_response', '').strip()
        report = get_object_or_404(VetAreaReport, id=report_id)
        if status in dict(VetAreaReport.STATUS_CHOICES):
            report.status = status
        if response_text:
            report.ministry_response = response_text
        report.responded_by = request.user
        report.responded_at = timezone.now()
        report.save()
        messages.success(request, 'Response saved for vet report.')
        return redirect('ministry:vet_reports_admin')

    reports = VetAreaReport.objects.select_related('vet', 'vet__user').order_by('-created_at')

    context = {
        'reports': reports,
        'active_menu': 'vet_reports',
    }
    return render(request, 'ministry/vet_reports.html', context)


@login_required
def farmers_list(request):
    """
    View all registered farmers on the platform.
    """
    if not request.user.is_ministry():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    farmers = Farmer.objects.select_related('user').all().order_by('-created_at')
    
    # Get province filter
    province_filter = request.GET.get('province', '')
    if province_filter:
        farmers = farmers.filter(province=province_filter)
    
    # Province statistics
    province_stats = Farmer.objects.values('province').annotate(
        count=Count('id')
    ).order_by('-count')
    
    context = {
        'farmers': farmers,
        'total_farmers': farmers.count(),
        'province_filter': province_filter,
        'province_stats': province_stats,
        'active_menu': 'farmers',
    }
    
    return render(request, 'ministry/farmers_list.html', context)


@login_required
def farmer_contact_edit(request, farmer_id):
    """
    Legacy view that used to allow Ministry to edit farmer contact details.
    For data protection, Ministry can no longer edit farmer information directly.
    Farmers should update their own profiles from the farmer portal.
    """
    if not request.user.is_ministry():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')

    messages.error(
        request,
        'Ministry administrators cannot edit farmer contact details directly. '
        'Please ask the farmer to update their profile in their own account.'
    )
    return redirect('ministry:farmers_list')


@login_required
def vets_list(request):
    """
    View all approved vets on the platform.
    """
    if not request.user.is_ministry():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    vets = Vet.objects.select_related('user').filter(is_approved=True).order_by('-created_at')
    
    # Get province filter
    province_filter = request.GET.get('province', '')
    if province_filter:
        # Filter vets whose provinces_served JSON field contains the selected province
        vets = [vet for vet in vets if province_filter in vet.provinces_served]
    else:
        vets = list(vets)
    
    # Province statistics - count vets by provinces they serve
    from collections import Counter
    province_counter = Counter()
    for vet in Vet.objects.filter(is_approved=True):
        if isinstance(vet.provinces_served, list):
            for province in vet.provinces_served:
                province_counter[province] += 1
    
    province_stats = [{'province': k, 'count': v} for k, v in province_counter.most_common()]
    
    context = {
        'vets': vets,
        'total_vets': len(vets) if province_filter else Vet.objects.filter(is_approved=True).count(),
        'province_filter': province_filter,
        'province_stats': province_stats,
        'active_menu': 'vets',
    }
    
    return render(request, 'ministry/vets_list.html', context)


@login_required
def settings_page(request):
    """Admin settings page - profile edit, preferences."""
    if not request.user.is_ministry():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number) or None
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('ministry:settings')

    return render(request, 'ministry/settings.html', {'active_menu': 'settings'})


@login_required
def notifications_page(request):
    """Notifications center - vet applications, critical cases."""
    if not request.user.is_ministry():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    pending_apps = VetApplication.objects.filter(status='PENDING').order_by('-created_at')[:20]
    critical = Case.objects.filter(severity='CRITICAL', status__in=['PENDING', 'ASSIGNED']).order_by('-created_at')[:20]
    recent_cases = Case.objects.filter(status='PENDING').order_by('-created_at')[:10]
    context = {
        'pending_applications': pending_apps,
        'critical_cases': critical,
        'recent_pending_cases': recent_cases,
        'active_menu': 'notifications',
    }
    return render(request, 'ministry/notifications.html', context)
