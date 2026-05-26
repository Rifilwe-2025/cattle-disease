"""
URL configuration for maps app.
"""
from django.urls import path
from . import views

app_name = 'maps'

urlpatterns = [
    path('disease-map/', views.disease_map, name='disease_map'),
    path('heatmap/', views.heatmap, name='heatmap'),
]
