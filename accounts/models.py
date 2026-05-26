"""
User models for the Cattle Disease Prediction System.

This module defines custom user models with role-based access control.
Three user roles: Farmer, Vet Doctor, Ministry Admin
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Supports role-based authentication for Farmers, Vets, and Ministry.
    """
    ROLE_CHOICES = [
        ('FARMER', 'Farmer'),
        ('VET', 'Vet Doctor'),
        ('MINISTRY', 'Ministry of Agriculture'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")],
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_farmer(self):
        """Check if user is a farmer."""
        return self.role == 'FARMER'
    
    def is_vet(self):
        """Check if user is a vet doctor."""
        return self.role == 'VET'
    
    def is_ministry(self):
        """Check if user is ministry admin."""
        return self.role == 'MINISTRY' or self.is_superuser
