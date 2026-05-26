"""
URL configuration for ministry app.
"""
from django.urls import path
from . import views

app_name = 'ministry'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('farmers/', views.farmers_list, name='farmers_list'),
    path('farmers/<int:farmer_id>/contact/', views.farmer_contact_edit, name='farmer_contact_edit'),
    path('vets/', views.vets_list, name='vets_list'),
    path('cases/', views.cases_overview, name='cases_overview'),
    path('tasks/', views.tasks_overview, name='tasks'),
    path('vet-applications/', views.vet_applications, name='vet_applications'),
    path('vet-application/<int:application_id>/approve/', views.approve_vet, name='approve_vet'),
    path('vet-application/<int:application_id>/reject/', views.reject_vet, name='reject_vet'),
    path('analytics/', views.analytics, name='analytics'),
    path('reports/', views.reports, name='reports'),
    path('vaccine-requests/', views.vaccine_requests, name='vaccine_requests'),
    path('vet-reports/', views.vet_reports_admin, name='vet_reports_admin'),
    path('settings/', views.settings_page, name='settings'),
    path('notifications/', views.notifications_page, name='notifications'),
]
