"""
Views for the Farmers app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext as _
from django.db.models import Count, Q
from .models import Farmer
from .forms import FarmerRegistrationForm, FarmerProfileForm, CaseSubmissionForm
from cases.models import Case
from ml_engine.services import predict_disease, classify_severity
from vets.models import Vet
from vets.utils import find_nearby_vets, find_vets_by_region_with_distance
from .ai_knowledge import get_response_for_question, get_response_for_topic
from cases.notifications import notify_vet_of_assignment
from core.mailer import is_smtp_configured
from django.http import JsonResponse


@login_required
def dashboard(request):
    """
    Farmer dashboard showing case history and statistics.
    """
    if not request.user.is_farmer():
        messages.error(request, _('Access denied. Farmers only.'))
        return redirect('accounts:login')
    
    # Get or create farmer profile
    try:
        farmer = Farmer.objects.get(user=request.user)
    except Farmer.DoesNotExist:
        # Profile is missing (e.g. the user was created in the admin, or
        # registration half-failed). Send them to profile_edit, which can
        # create it. Sending them to farmers:register instead caused an
        # infinite redirect loop, because register bounces logged-in
        # farmers back to this dashboard.
        messages.info(request, _('Please complete your farmer profile.'))
        return redirect('farmers:profile_edit')
    
    # Get cases for this farmer
    cases = Case.objects.filter(farmer=farmer).order_by('-created_at')[:10]
    
    # Statistics
    total_cases = Case.objects.filter(farmer=farmer).count()
    active_cases = Case.objects.filter(farmer=farmer, status__in=['PENDING', 'ASSIGNED', 'IN_PROGRESS']).count()
    resolved_cases = Case.objects.filter(farmer=farmer, status__in=['RESOLVED', 'CLOSED']).count()
    critical_cases = Case.objects.filter(farmer=farmer, severity='CRITICAL', status__in=['PENDING', 'ASSIGNED']).count()
    
    # Disease distribution for donut chart
    disease_stats = Case.objects.filter(farmer=farmer).values('predicted_disease').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    # Monthly case counts for line chart (last 12 months)
    from datetime import timedelta
    from collections import defaultdict
    twelve_months_ago = timezone.now() - timedelta(days=365)
    farmer_cases = Case.objects.filter(farmer=farmer, created_at__gte=twelve_months_ago)
    monthly_totals = defaultdict(lambda: {'critical': 0, 'pending': 0, 'resolved': 0})
    for c in farmer_cases:
        key = c.created_at.strftime('%Y-%m')
        if c.severity == 'CRITICAL':
            monthly_totals[key]['critical'] += 1
        elif c.status in ('RESOLVED', 'CLOSED'):
            monthly_totals[key]['resolved'] += 1
        else:
            monthly_totals[key]['pending'] += 1
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
    
    # Severity breakdown for progress bars (+ normalised percentages that add to 100)
    critical_count = Case.objects.filter(farmer=farmer, severity='CRITICAL').count()
    severe_count = Case.objects.filter(farmer=farmer, severity='SEVERE').count()
    non_severe_count = Case.objects.filter(farmer=farmer, severity='NON_SEVERE').count()

    severity_total = critical_count + severe_count + non_severe_count
    if severity_total > 0:
        critical_pct = round(critical_count / severity_total * 100)
        severe_pct = round(severe_count / severity_total * 100)
        # Ensure percentages add up to 100 by adjusting the last bucket
        non_severe_pct = max(0, 100 - critical_pct - severe_pct)
    else:
        critical_pct = severe_pct = non_severe_pct = 0
    
    context = {
        'farmer': farmer,
        'cases': cases,
        'total_cases': total_cases,
        'active_cases': active_cases,
        'resolved_cases': resolved_cases,
        'critical_cases': critical_cases,
        'disease_stats': disease_stats,
        'chart_critical': chart_critical,
        'chart_pending': chart_pending,
        'chart_resolved': chart_resolved,
        'critical_count': critical_count,
        'severe_count': severe_count,
        'non_severe_count': non_severe_count,
        'critical_pct': critical_pct,
        'severe_pct': severe_pct,
        'non_severe_pct': non_severe_pct,
    }
    
    return render(request, 'farmers/dashboard.html', context)


@login_required
def active_cases(request):
    """
    Separate page showing only active (open) cases for the farmer.
    """
    if not request.user.is_farmer():
        messages.error(request, _('Access denied. Farmers only.'))
        return redirect('accounts:login')

    farmer = get_object_or_404(Farmer, user=request.user)
    cases = Case.objects.filter(
        farmer=farmer,
        status__in=['PENDING', 'ASSIGNED', 'IN_PROGRESS']
    ).order_by('-created_at')

    context = {
        'farmer': farmer,
        'cases': cases,
        'active_only': True,
    }
    return render(request, 'farmers/case_history.html', context)


@login_required
def profile_edit(request):
    """Farmer profile edit - update farmer details and user email."""
    if not request.user.is_farmer():
        messages.error(request, _('Access denied.'))
        return redirect('accounts:login')

    # May legitimately be absent - this view doubles as "complete your
    # profile" for a FARMER user who has no Farmer row yet.
    farmer = Farmer.objects.filter(user=request.user).first()
    is_new_profile = farmer is None

    if request.method == 'POST':
        profile_form = FarmerProfileForm(request.POST, instance=farmer)
        if profile_form.is_valid():
            farmer = profile_form.save(commit=False)
            farmer.user = request.user
            farmer.save()
            # Sync email and phone to User for password reset and auth
            farmer.refresh_from_db()
            if farmer.email:
                request.user.email = farmer.email
            if farmer.phone_number:
                request.user.phone_number = farmer.phone_number
            request.user.save()
            if is_new_profile:
                messages.success(request, _('Profile completed. Welcome!'))
                return redirect('farmers:dashboard')
            messages.success(request, _('Profile updated successfully.'))
            return redirect('farmers:profile_edit')
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        profile_form = FarmerProfileForm(instance=farmer)

    context = {
        'farmer': farmer,
        'profile_form': profile_form,
        'is_new_profile': is_new_profile,
    }
    return render(request, 'farmers/profile_edit.html', context)


@login_required
def ai_assistant(request):
    """AI Assistant API - returns guidance for farmers' questions."""
    if not request.user.is_farmer():
        return JsonResponse({'error': _('Access denied')}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': _('Method not allowed')}, status=405)

    question = request.POST.get('question', '').strip()
    topic = request.POST.get('topic', '').strip()
    lang = request.POST.get('lang', '').strip() or getattr(request, 'LANGUAGE_CODE', '') or 'en'

    if topic:
        response = get_response_for_topic(topic, lang=lang)
    elif question:
        response = get_response_for_question(question, lang=lang)
    else:
        response = _(
            "Please enter a question or select a topic. I can help with disease tips, herd health, and cattle care guidance."
        )

    # Enrich answer with data from this farmer's actual cases in the database
    try:
        farmer = Farmer.objects.get(user=request.user)
    except Farmer.DoesNotExist:
        farmer = None

    if farmer:
        # Latest case overall
        latest_case = Case.objects.filter(farmer=farmer).order_by('-created_at').first()

        # Try to find a recent case related to the question/topic disease name (if any)
        related_case = None
        text = (question or topic or '').lower()
        if text:
            possible_cases = Case.objects.filter(farmer=farmer).order_by('-created_at')[:20]
            for c in possible_cases:
                if c.predicted_disease and c.predicted_disease.lower() in text or any(
                    kw and kw in (c.predicted_disease or '').lower()
                    for kw in text.split()
                ):
                    related_case = c
                    break

        case_to_use = related_case or latest_case

        if case_to_use:
            from django.utils import formats

            created_str = formats.date_format(case_to_use.created_at, "M d, Y")
            severity = case_to_use.get_severity_display()
            status = case_to_use.get_status_display()
            disease = case_to_use.predicted_disease or _("Unknown disease")

            # Keep the snippet structure consistent for the UI; translate the wrapper text.
            db_snippet = _(
                "\n\nIn your own herd, the most recent recorded case is **%(disease)s** "
                "from %(date)s (severity: **%(severity)s**, status: **%(status)s**). "
                "Use this as a reference when monitoring similar symptoms."
            ) % {
                "disease": disease,
                "date": created_str,
                "severity": severity,
                "status": status,
            }

            response = response + db_snippet

    return JsonResponse({'response': response, 'success': True})


@login_required
def ai_insights_page(request):
    """
    Full-screen AI Insights page for farmers.
    Reuses the same AI assistant backend but in a dedicated layout.
    """
    if not request.user.is_farmer():
        messages.error(request, _('Access denied. Farmers only.'))
        return redirect('accounts:login')

    farmer = get_object_or_404(Farmer, user=request.user)

    # Basic stats to show alongside the assistant
    total_cases = Case.objects.filter(farmer=farmer).count()
    active_cases = Case.objects.filter(farmer=farmer, status__in=['PENDING', 'ASSIGNED', 'IN_PROGRESS']).count()
    resolved_cases = Case.objects.filter(farmer=farmer, status__in=['RESOLVED', 'CLOSED']).count()

    context = {
        'farmer': farmer,
        'total_cases': total_cases,
        'active_cases': active_cases,
        'resolved_cases': resolved_cases,
    }
    return render(request, 'farmers/ai_insights.html', context)


def register(request):
    """
    Public farmer registration view.
    Creates both User account and Farmer profile, then redirects to login.
    """
    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        if request.user.is_farmer():
            # Only to the dashboard if the profile exists; otherwise the two
            # views redirect to each other forever.
            if not Farmer.objects.filter(user=request.user).exists():
                return redirect('farmers:profile_edit')
            return redirect('farmers:dashboard')
        else:
            messages.info(request, 'You are already logged in.')
            return redirect('accounts:redirect_after_login')
    
    if request.method == 'POST':
        form = FarmerRegistrationForm(request.POST)
        if form.is_valid():
            from accounts.models import User
            
            # Create User account
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
                role='FARMER',
                phone_number=form.cleaned_data['phone_number'],
                email=form.cleaned_data['email'],
            )
            
            # Create Farmer profile
            farmer = Farmer.objects.create(
                user=user,
                full_name=form.cleaned_data['full_name'],
                phone_number=form.cleaned_data['phone_number'],
                email=form.cleaned_data['email'],
                province=form.cleaned_data['province'],
                district=form.cleaned_data['district'],
                latitude=form.cleaned_data.get('latitude'),
                longitude=form.cleaned_data.get('longitude'),
                cattle_breed=form.cleaned_data['cattle_breed'],
                number_of_cattle=form.cleaned_data['number_of_cattle'],
                farming_type='Mixed'  # Default, can be updated later
            )
            
            messages.success(
                request,
                f'Registration successful! Welcome {farmer.full_name}. Please login with your username and password.'
            )
            return redirect('accounts:login')
    else:
        form = FarmerRegistrationForm()
    
    return render(request, 'farmers/register.html', {'form': form})


@login_required
def submit_case(request):
    """
    Submit a new disease case with symptom reporting.
    """
    if not request.user.is_farmer():
        messages.error(request, 'Access denied. Farmers only.')
        return redirect('accounts:login')
    
    farmer = get_object_or_404(Farmer, user=request.user)
    
    if request.method == 'POST':
        form = CaseSubmissionForm(request.POST)
        if form.is_valid():
            # Get symptoms from form
            symptoms = form.cleaned_data['symptoms']
            notes = form.cleaned_data.get('notes', '')
            
            # Get contextual features from form (9 new features)
            contextual_features = {
                'age_years': form.cleaned_data['age_years'],
                'sex': form.cleaned_data['sex'],
                'breed': form.cleaned_data['breed'],
                'vaccinated': form.cleaned_data['vaccinated'],
                'herd_size': form.cleaned_data['herd_size'],
                'farming_type': form.cleaned_data['farming_type'],
                'recent_movement': form.cleaned_data['recent_movement'],
                'season': form.cleaned_data['season'],
                'province': form.cleaned_data['province']
            }
            
            # Predict disease using ML model (now with all 102 features)
            prediction_result = predict_disease(symptoms, contextual_features)
            predicted_disease = prediction_result['disease']
            confidence = prediction_result['confidence']
            top_3_diseases = prediction_result.get('top_3_diseases') or []

            # Severity = disease-based + confidence escalation (vet-centred: all cases need vet)
            severity = classify_severity(confidence, predicted_disease)

            # Store top 3 for low-confidence cases (vet sees these; farmer sees only vet recommendation)
            from django.conf import settings as django_settings
            low_conf = confidence < django_settings.SEVERITY_THRESHOLDS.get('NON_SEVERE', 0.40)
            top_diseases_to_store = top_3_diseases if low_conf else None

            case = Case.objects.create(
                farmer=farmer,
                symptoms=symptoms,
                notes=notes,
                predicted_disease=predicted_disease,
                confidence_score=confidence,
                severity=severity,
                status='PENDING',
                top_diseases=top_diseases_to_store,
            )

            # Vet-centred: every case is assigned/sent to a vet; vet gives final recommendation
            if severity == 'CRITICAL':
                messages.error(
                    request,
                    f'🚨 CRITICAL case detected! Please select a vet from your region ({farmer.province}) URGENTLY for immediate consultation.'
                )
            elif severity == 'SEVERE':
                messages.warning(
                    request,
                    f'⚠️ Severe case detected. Please select a vet from your region ({farmer.province}) for consultation.'
                )
            else:
                messages.success(
                    request,
                    '✅ Case submitted. Please select a vet so they can provide their recommendation.'
                )
            return redirect('farmers:select_vet', case_id=case.id)
    else:
        # Pre-fill contextual fields from farmer profile where possible
        initial = {}

        # Map farmer.cattle_breed to one of the case form breed choices if possible
        if farmer.cattle_breed:
            breed_value = farmer.cattle_breed.strip().lower()
            breed_map = {
                'brahman': 'Brahman',
                'mashona': 'Mashona',
                'tuli': 'Tuli',
                'crossbreed': 'Crossbreed',
            }
            initial_breed = None
            for key, val in breed_map.items():
                if key in breed_value:
                    initial_breed = val
                    break
            if initial_breed:
                initial['breed'] = initial_breed

        # Herd size from farmer profile
        if farmer.number_of_cattle:
            initial['herd_size'] = farmer.number_of_cattle

        # Farming type – map farmer.farming_type to case form choices as best as possible
        if farmer.farming_type:
            if farmer.farming_type == 'Commercial':
                initial['farming_type'] = 'Commercial'
            else:
                # Subsistence or Mixed → default to Communal / Small-scale
                initial['farming_type'] = 'Communal'

        # Province from farmer profile (must match one of the choices)
        if farmer.province:
            initial['province'] = farmer.province

        form = CaseSubmissionForm(initial=initial)
    
    return render(request, 'farmers/submit_case.html', {'form': form, 'farmer': farmer})


@login_required
def case_result(request, case_id):
    """
    Display prediction results and recommendations.
    """
    if not request.user.is_farmer():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    farmer = get_object_or_404(Farmer, user=request.user)
    case = get_object_or_404(Case, id=case_id, farmer=farmer)

    from django.utils import translation
    from farmers.disease_advice import get_waiting_advice_for_case

    waiting_advice = None
    if not case.vet_recommendations:
        waiting_advice = get_waiting_advice_for_case(case, translation.get_language())
    
    context = {
        'case': case,
        'farmer': farmer,
        'waiting_advice': waiting_advice,
    }
    
    return render(request, 'farmers/case_result.html', context)


@login_required
def select_vet(request, case_id):
    """
    Allow farmer to select a vet from their region for severe cases.
    Only shows vets who serve the farmer's province.
    """
    if not request.user.is_farmer():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    farmer = get_object_or_404(Farmer, user=request.user)
    case = get_object_or_404(Case, id=case_id, farmer=farmer)
    
    # Vet-centred: all cases require vet assignment (farmer selects vet for every case)
    # Find all vets in the same region (province)
    vets_in_region = find_vets_by_region_with_distance(
        province=farmer.province,
        district=farmer.district,
        farmer_lat=farmer.latitude,
        farmer_lon=farmer.longitude
    )
    
    if request.method == 'POST':
        vet_id = request.POST.get('vet_id')
        if vet_id:
            # Verify the selected vet is approved and serves this region
            vet = get_object_or_404(Vet, id=vet_id, is_approved=True)
            
            # Double-check vet serves this province
            if isinstance(vet.provinces_served, list):
                provinces_lower = [p.lower().strip() for p in vet.provinces_served]
                if farmer.province.lower().strip() not in provinces_lower:
                    messages.error(request, 'Selected vet does not serve your region.')
                    return redirect('farmers:select_vet', case_id=case.id)
            
            case.assigned_vet = vet
            case.status = 'ASSIGNED'
            case.save(update_fields=['assigned_vet', 'status', 'updated_at'])

            # Email the vet. Queued on a background thread by core.mailer, so
            # this adds no measurable time to the farmer's request even when
            # Gmail is slow to answer - and a failure is logged rather than
            # raised, because the assignment above is the thing that matters
            # and it has already been committed.
            notified = notify_vet_of_assignment(case, request=request)

            if notified and is_smtp_configured():
                messages.success(
                    request,
                    f'✅ Dr. {vet.full_name} has been assigned to your case and '
                    f'notified by email. They will contact you soon.'
                )
            else:
                # Either the vet has no address on file or the site is still on
                # the console email backend. Say what will actually happen
                # rather than promise an email that is not going anywhere.
                messages.success(
                    request,
                    f'✅ Dr. {vet.full_name} has been assigned to your case. '
                    f'They will see it on their dashboard.'
                )
            return redirect('farmers:case_result', case_id=case.id)
        else:
            messages.error(request, 'Please select a vet.')
    
    context = {
        'case': case,
        'farmer': farmer,
        'vets_in_region': vets_in_region,
        'total_vets': len(vets_in_region),
    }
    
    return render(request, 'farmers/select_vet.html', context)


@login_required
def help_center(request):
    """
    Farmer help center: explains how to use the dashboard and submit cases.
    """
    if not request.user.is_farmer():
        messages.error(request, 'Access denied. Farmers only.')
        return redirect('accounts:login')

    farmer = get_object_or_404(Farmer, user=request.user)

    # Basic stats reused from dashboard so help content can reference real numbers
    total_cases = Case.objects.filter(farmer=farmer).count()
    active_cases = Case.objects.filter(farmer=farmer, status__in=['PENDING', 'ASSIGNED', 'IN_PROGRESS']).count()
    resolved_cases = Case.objects.filter(farmer=farmer, status__in=['RESOLVED', 'CLOSED']).count()

    context = {
        'farmer': farmer,
        'total_cases': total_cases,
        'active_cases': active_cases,
        'resolved_cases': resolved_cases,
    }
    return render(request, 'farmers/help_center.html', context)


@login_required
def case_history(request):
    """
    View all cases submitted by the farmer.
    """
    if not request.user.is_farmer():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    farmer = get_object_or_404(Farmer, user=request.user)
    cases = Case.objects.filter(farmer=farmer).order_by('-created_at')
    
    context = {
        'farmer': farmer,
        'cases': cases,
    }
    
    return render(request, 'farmers/case_history.html', context)


@login_required
def vet_recommendations(request):
    """
    Farmer view: list cases and show recommendations given by the vet.
    """
    if not request.user.is_farmer():
        messages.error(request, 'Access denied.')
        return redirect('accounts:login')
    
    farmer = get_object_or_404(Farmer, user=request.user)
    # Cases that have a vet recommendation (farmer follows vet's recommendation)
    cases_with_rec = Case.objects.filter(
        farmer=farmer
    ).exclude(vet_recommendations='').order_by('-vet_consultation_date')
    all_cases = Case.objects.filter(farmer=farmer).order_by('-created_at')
    
    context = {
        'farmer': farmer,
        'cases_with_recommendations': cases_with_rec,
        'all_cases': all_cases,
    }
    return render(request, 'farmers/vet_recommendations.html', context)
