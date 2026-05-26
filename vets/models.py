"""
Models for the Vets app.

Vet doctors must apply and be approved by Ministry before they can register.
"""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
import random
import string


def generate_application_id():
    """
    Generate a unique application ID in format: VET-2026-A1B2C3
    Format: VET-YEAR-RANDOM6CHARS
    """
    from django.utils import timezone
    year = timezone.now().year
    # Generate 6 random alphanumeric characters
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"VET-{year}-{random_part}"


class VetApplication(models.Model):
    """
    Vet application model.
    Vets submit applications which must be approved by Ministry.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    # Unique application tracking ID
    application_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Unique application tracking ID (e.g., VET-2026-A1B2C3)"
    )
    
    # Application details
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    license_number = models.CharField(max_length=100, unique=True, help_text="Veterinary license/registration number")
    qualification = models.CharField(max_length=200, help_text="Veterinary qualifications")
    years_of_experience = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(50)])
    
    # Service area
    provinces_served = models.JSONField(help_text="List of provinces where vet provides services")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Application status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection (if rejected)")
    
    # Approval details
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_vet_applications'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Vet Application"
        verbose_name_plural = "Vet Applications"
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """Generate application ID on first save."""
        if not self.application_id:
            # Generate unique application ID
            while True:
                app_id = generate_application_id()
                if not VetApplication.objects.filter(application_id=app_id).exists():
                    self.application_id = app_id
                    break
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} - {self.application_id} - {self.get_status_display()}"
    
    def is_approved(self):
        """Check if application is approved."""
        return self.status == 'APPROVED'
    
    def is_pending(self):
        """Check if application is pending."""
        return self.status == 'PENDING'
    
    def is_rejected(self):
        """Check if application is rejected."""
        return self.status == 'REJECTED'
    
    def get_provinces_list(self):
        """Return provinces as a list (handles both list and single string)."""
        if not self.provinces_served:
            return []
        if isinstance(self.provinces_served, list):
            return self.provinces_served
        return [self.provinces_served]


class Vet(models.Model):
    """
    Vet profile model.
    Created after vet application is approved and vet registers.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vet_profile')
    application = models.OneToOneField(VetApplication, on_delete=models.CASCADE, related_name='vet_profile')
    
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField()
    license_number = models.CharField(max_length=100, unique=True)
    qualification = models.CharField(max_length=200)
    years_of_experience = models.PositiveIntegerField()
    
    # Service area
    provinces_served = models.JSONField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Profile photo
    profile_photo = models.ImageField(upload_to='vet_avatars/', null=True, blank=True)
    
    # Status
    is_approved = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True, help_text="Whether vet is currently accepting new cases")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Vet Doctor"
        verbose_name_plural = "Vet Doctors"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Dr. {self.full_name} ({self.license_number})"
    
    def has_location(self):
        """Check if vet has GPS coordinates."""
        return self.latitude is not None and self.longitude is not None
    
    def get_provinces_list(self):
        """Return provinces as a list (handles both list and single string)."""
        if not self.provinces_served:
            return []
        if isinstance(self.provinces_served, list):
            return self.provinces_served
        return [self.provinces_served]


class VaccineRequest(models.Model):
    """
    Vaccine / medical stock request raised by a vet to the Ministry.
    """
    PRIORITY_CHOICES = [
        ('NORMAL', _('Normal')),
        ('URGENT', _('Urgent')),
    ]

    STATUS_CHOICES = [
        ('PENDING', _('Pending')),
        ('APPROVED', _('Approved')),
        ('PARTIAL', _('Partially fulfilled')),
        ('REJECTED', _('Rejected')),
    ]

    vet = models.ForeignKey(Vet, on_delete=models.CASCADE, related_name='vaccine_requests')
    title = models.CharField(max_length=200, help_text="Short title e.g. 'FMD vaccines for Mashonaland East'")
    vaccine_name = models.CharField(max_length=200, help_text="Vaccine or medical product requested")
    quantity = models.PositiveIntegerField(help_text="Estimated quantity required (doses)")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='NORMAL')
    description = models.TextField(help_text="Brief explanation and justification for this request")

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    ministry_response = models.TextField(blank=True, help_text="Response or decision from Ministry")
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vaccine_request_responses'
    )
    responded_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vaccine Request"
        verbose_name_plural = "Vaccine Requests"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class VetAreaReport(models.Model):
    """
    Narrative report from a vet to the Ministry about cases and herd health
    in their area (e.g., monthly or outbreak reports).
    """
    STATUS_CHOICES = [
        ('SUBMITTED', _('Submitted')),
        ('READ', _('Read')),
        ('RESPONDED', _('Responded')),
    ]

    vet = models.ForeignKey(Vet, on_delete=models.CASCADE, related_name='area_reports')
    title = models.CharField(max_length=200, help_text="e.g. 'Monthly report – Midlands North cluster'")
    summary = models.CharField(max_length=300, help_text="Short summary of the main points")
    body = models.TextField(help_text="Detailed report (situation, trends, recommendations)")

    province = models.CharField(max_length=100, help_text="Province the report focuses on")
    district = models.CharField(max_length=100, blank=True, help_text="District or specific area (optional)")
    period_start = models.DateField(null=True, blank=True, help_text="Start of reporting period")
    period_end = models.DateField(null=True, blank=True, help_text="End of reporting period")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUBMITTED')
    ministry_response = models.TextField(blank=True, help_text="Response or follow-up notes from Ministry")
    responded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vet_area_report_responses'
    )
    responded_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vet Area Report"
        verbose_name_plural = "Vet Area Reports"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} – Dr. {self.vet.full_name}"