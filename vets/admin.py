"""
Admin configuration for vets app.
"""
from django.contrib import admin
from .models import VetApplication, Vet


@admin.register(VetApplication)
class VetApplicationAdmin(admin.ModelAdmin):
    """Admin interface for VetApplication model."""
    list_display = ['full_name', 'license_number', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'license_number', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Vet)
class VetAdmin(admin.ModelAdmin):
    """Admin interface for Vet model."""
    list_display = ['full_name', 'license_number', 'is_approved', 'is_available', 'created_at']
    list_filter = ['is_approved', 'is_available', 'created_at']
    search_fields = ['full_name', 'license_number', 'email']
    readonly_fields = ['created_at', 'updated_at']
