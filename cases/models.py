"""
Models for disease cases.

Each case represents a disease incident reported by a farmer.
Cases are linked to farmers and optionally assigned to vets.
"""
from django.db import models
from django.conf import settings
from farmers.models import Farmer
from vets.models import Vet


class Case(models.Model):
    """
    Disease case model.
    Represents a single disease incident reported by a farmer.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ASSIGNED', 'Assigned to Vet'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]

    SEVERITY_CHOICES = [
        ('NON_SEVERE', 'Non-Severe'),
        ('SEVERE', 'Severe'),
        ('CRITICAL', 'Critical'),
    ]

    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE, related_name='cases')
    assigned_vet = models.ForeignKey(
        Vet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_cases'
    )

    # Symptom data (stored as JSON or comma-separated) – legacy field used by ML & UI
    # Kept for backwards compatibility; new normalized tables below provide structured view.
    symptoms = models.JSONField(help_text="List of symptoms reported")
    notes = models.TextField(blank=True, help_text="Additional notes from farmer")

    # ML Prediction results (denormalised snapshot for fast access)
    predicted_disease = models.CharField(max_length=200, help_text="Disease predicted by ML model (top pick)")
    confidence_score = models.FloatField(help_text="ML model confidence (0-1)")
    # For low-confidence cases: top 3 diseases by probability for vet to consider
    top_diseases = models.JSONField(
        blank=True,
        null=True,
        help_text="When confidence is low: list of {disease, probability} for top 3"
    )
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='NON_SEVERE')

    # Vet consultation
    vet_diagnosis = models.TextField(blank=True, help_text="Vet's diagnosis")
    vet_recommendations = models.TextField(blank=True, help_text="Vet's treatment recommendations")
    vet_consultation_date = models.DateTimeField(null=True, blank=True)

    # Case status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Case"
        verbose_name_plural = "Cases"
        ordering = ['-created_at']

    def __str__(self):
        return f"Case #{self.id} - {self.predicted_disease} ({self.farmer.full_name})"

    def is_critical(self):
        """Check if case is critical."""
        return self.severity == 'CRITICAL'

    def is_severe(self):
        """Check if case is severe."""
        return self.severity == 'SEVERE'

    def requires_vet(self):
        """All cases require vet (vet-centred design)."""
        return True

    def is_low_confidence(self):
        """True when we should show top 3 diseases and hide AI treatment (use vet rec only)."""
        from django.conf import settings
        th = getattr(settings, 'SEVERITY_THRESHOLDS', {})
        low_threshold = th.get('SEVERE', 0.40)
        return self.confidence_score < low_threshold


class Symptom(models.Model):
    """
    Reference table for all supported symptoms.
    This is a normalised view that complements Case.symptoms JSON.
    """
    code = models.CharField(max_length=100, unique=True, help_text="Stable code used in ML features, e.g. 'fever'")
    name = models.CharField(max_length=255, help_text="Human readable name, e.g. 'Fever'")
    description = models.TextField(blank=True, help_text="Optional description / examples")

    class Meta:
        verbose_name = "Symptom"
        verbose_name_plural = "Symptoms"
        ordering = ["code"]

    def __str__(self):
        return self.name or self.code


class Disease(models.Model):
    """
    Reference table for diseases that the model can predict.
    """
    code = models.CharField(max_length=100, unique=True, help_text="Stable code, e.g. 'foot_and_mouth'")
    name = models.CharField(max_length=255, help_text="Human readable disease name")
    severity = models.CharField(
        max_length=20,
        choices=Case.SEVERITY_CHOICES,
        help_text="Base clinical severity for this disease"
    )
    description = models.TextField(blank=True, help_text="Optional notes / clinical description")

    class Meta:
        verbose_name = "Disease"
        verbose_name_plural = "Diseases"
        ordering = ["code"]

    def __str__(self):
        return self.name or self.code


class CaseSymptom(models.Model):
    """
    Normalised link between a Case and individual Symptoms.
    Does NOT replace Case.symptoms JSON; it mirrors it for reporting/analytics.
    """
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="case_symptoms")
    symptom = models.ForeignKey(Symptom, on_delete=models.PROTECT, related_name="case_links")
    is_primary = models.BooleanField(default=False, help_text="Main/most prominent symptom for this case")
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Case Symptom"
        verbose_name_plural = "Case Symptoms"
        unique_together = ("case", "symptom")

    def __str__(self):
        return f"Case #{self.case_id} – {self.symptom.code}"


class CasePrediction(models.Model):
    """
    Structured storage for ML prediction outputs per case.
    Mirrors Case.predicted_disease and Case.top_diseases JSON.
    """
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="predictions")
    disease = models.ForeignKey(Disease, on_delete=models.PROTECT, related_name="case_predictions")
    probability = models.FloatField(help_text="Predicted probability (0-1)")
    rank = models.PositiveIntegerField(help_text="1 for top disease, 2 for second, etc.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Case Prediction"
        verbose_name_plural = "Case Predictions"
        ordering = ["case", "rank"]
        unique_together = ("case", "rank", "disease")

    def __str__(self):
        return f"Case #{self.case_id} – {self.disease.code} (rank {self.rank}, p={self.probability:.2f})"
