"""Context for farmer dashboard templates."""
from .models import Farmer
from cases.models import Case


def farmer_dashboard_context(request):
    """Expose farmer profile and alert counts on all farmer pages."""
    if not request.user.is_authenticated or not request.user.is_farmer():
        return {}
    try:
        farmer = Farmer.objects.get(user=request.user)
    except Farmer.DoesNotExist:
        return {'farmer': None, 'critical_cases': 0, 'active_cases': 0}

    critical_cases = Case.objects.filter(
        farmer=farmer, severity='CRITICAL', status__in=['PENDING', 'ASSIGNED']
    ).count()
    active_cases = Case.objects.filter(
        farmer=farmer, status__in=['PENDING', 'ASSIGNED', 'IN_PROGRESS']
    ).count()

    return {
        'farmer': farmer,
        'critical_cases': critical_cases,
        'active_cases': active_cases,
    }
