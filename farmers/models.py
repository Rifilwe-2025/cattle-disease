"""
Models for the Farmers app.

Farmers register directly and can submit disease cases.
Each case represents a disease incident, not individual cattle registration.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Farmer(models.Model):
    """
    Farmer profile model.
    Extends user information with farming-specific details.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farmer_profile')
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15, blank=True, help_text="Contact phone number")
    email = models.EmailField(blank=True, help_text="Contact email (for password reset and admin)")
    province = models.CharField(max_length=50)
    district = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="GPS Latitude")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="GPS Longitude")
    cattle_breed = models.CharField(max_length=100, help_text="Primary cattle breed")
    number_of_cattle = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    farming_type = models.CharField(
        max_length=20,
        choices=[
            ('Commercial', 'Commercial'),
            ('Subsistence', 'Subsistence'),
            ('Mixed', 'Mixed'),
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Farmer"
        verbose_name_plural = "Farmers"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} ({self.province})"
    
    def has_location(self):
        """Check if farmer has GPS coordinates."""
        return self.latitude is not None and self.longitude is not None
