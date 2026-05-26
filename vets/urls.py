"""
URL configuration for vets app.
"""
from django.urls import path
from . import views

app_name = 'vets'

urlpatterns = [
    # Application
    path('apply/', views.apply, name='apply'),
    path('application/success/<str:application_id>/', views.application_success, name='application_success'),
    path('track/', views.track_application, name='track_application'),
    path('guide/save-id/', views.save_id_guide, name='save_id_guide'),
    
    # Registration
    path('register/<int:application_id>/', views.register, name='register'),  # Legacy (backward compatibility)
    path('register/<str:application_id>/', views.register_by_app_id, name='register_by_app_id'),
    
    # Dashboard & Cases
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_edit, name='profile_edit'),
    path('farmers/', views.farmers_list, name='farmers_list'),
    path('cases/', views.cases_list, name='cases_list'),
    path('cases/export/', views.export_cases_csv, name='export_cases_csv'),
    path('vaccine-requests/', views.vaccine_requests, name='vaccine_requests'),
    path('area-reports/', views.area_reports, name='area_reports'),
    path('help/', views.help_center, name='help_center'),
    path('case/<int:case_id>/', views.case_detail, name='case_detail'),
    path('case/<int:case_id>/accept/', views.accept_case, name='accept_case'),
    path('case/<int:case_id>/resolve/', views.resolve_case, name='resolve_case'),
]
