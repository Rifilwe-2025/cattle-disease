"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model."""
    list_display = ['username', 'email', 'role', 'phone_number', 'is_active', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number')}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone_number')}),
    )
