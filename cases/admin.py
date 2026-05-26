"""
Admin configuration for cases app.
"""
from django.contrib import admin
from .models import Case


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    """Admin interface for Case model."""
    list_display = ['id', 'farmer', 'predicted_disease', 'severity', 'status', 'assigned_vet', 'created_at']
    list_filter = ['status', 'severity', 'created_at']
    search_fields = ['farmer__full_name', 'predicted_disease', 'farmer__province']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Case Information', {
            'fields': ('farmer', 'assigned_vet', 'status', 'severity')
        }),
        ('Symptoms & Notes', {
            'fields': ('symptoms', 'notes')
        }),
        ('ML Prediction', {
            'fields': ('predicted_disease', 'confidence_score')
        }),
        ('Vet Consultation', {
            'fields': ('vet_diagnosis', 'vet_recommendations', 'vet_consultation_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'resolved_at')
        }),
    )
