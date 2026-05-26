"""
URL configuration for landing app.
"""
from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-of-service/', views.terms_of_service, name='terms_of_service'),
]
