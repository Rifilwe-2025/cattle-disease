"""
Landing page views.
"""
from django.shortcuts import render
from farmers.forms import FarmerProfileForm
from vets.forms import VetApplicationForm


def home(request):
    """
    Public landing page.
    """
    farmer_form = FarmerProfileForm()
    vet_form = VetApplicationForm()
    
    context = {
        'farmer_form': farmer_form,
        'vet_form': vet_form,
    }
    
    return render(request, 'landing/home.html', context)


def about(request):
    """Dedicated About page."""
    return render(request, 'landing/about.html')


def services(request):
    """Dedicated Services page."""
    return render(request, 'landing/services.html')


def how_it_works(request):
    """Dedicated How It Works page."""
    return render(request, 'landing/how_it_works.html')


def privacy_policy(request):
    """Privacy Policy page."""
    return render(request, 'landing/privacy_policy.html')


def terms_of_service(request):
    """Terms of Service page."""
    return render(request, 'landing/terms_of_service.html')
