"""
Context processor for Ministry admin pages.
Adds sidebar data (total_farmers, total_vets, pending_applications, critical_cases) to all ministry views.
"""
from farmers.models import Farmer
from vets.models import Vet, VetApplication
from cases.models import Case


def ministry_sidebar_context(request):
    """Add ministry dashboard stats to context for sidebar badges and notification badge."""
    if request.user.is_authenticated and getattr(request.user, 'is_ministry', lambda: False)():
        pending = VetApplication.objects.filter(status='PENDING').count()
        critical = Case.objects.filter(severity='CRITICAL', status__in=['PENDING', 'ASSIGNED']).count()
        return {
            'sidebar_total_farmers': Farmer.objects.count(),
            'sidebar_total_vets': Vet.objects.filter(is_approved=True).count(),
            'sidebar_pending_applications': pending,
            'sidebar_critical_cases': critical,
            'sidebar_notification_count': pending + critical,
        }
    return {
        'sidebar_total_farmers': 0,
        'sidebar_total_vets': 0,
        'sidebar_pending_applications': 0,
        'sidebar_critical_cases': 0,
        'sidebar_notification_count': 0,
    }
