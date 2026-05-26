"""
Admin configuration for farmers app.
"""
from django.contrib import admin
from .models import Farmer


@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    """Admin interface for Farmer model."""
    list_display = ['full_name', 'user', 'province', 'district', 'number_of_cattle', 'farming_type', 'created_at']
    list_filter = ['province', 'farming_type', 'created_at']
    search_fields = ['full_name', 'user__username', 'province', 'district']
    readonly_fields = ['created_at', 'updated_at']
