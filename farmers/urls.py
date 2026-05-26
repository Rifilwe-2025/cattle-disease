"""
URL configuration for farmers app.
"""
from django.urls import path
from . import views

app_name = 'farmers'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cases/active/', views.active_cases, name='active_cases'),
    path('ai-insights/', views.ai_insights_page, name='ai_insights'),
    path('profile/', views.profile_edit, name='profile_edit'),
    path('ai-assistant/', views.ai_assistant, name='ai_assistant'),
    path('register/', views.register, name='register'),
    path('submit-case/', views.submit_case, name='submit_case'),
    path('case/<int:case_id>/result/', views.case_result, name='case_result'),
    path('case/<int:case_id>/select-vet/', views.select_vet, name='select_vet'),
    path('cases/', views.case_history, name='case_history'),
    path('vet-recommendations/', views.vet_recommendations, name='vet_recommendations'),
    path('help/', views.help_center, name='help_center'),
]
