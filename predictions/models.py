"""
Predictions App - Models
========================
Stores prediction results, symptom inputs, and prediction history.
"""

from django.db import models
from django.conf import settings
from patients.models import Disease, Symptom
from django.utils import timezone
import json


class Prediction(models.Model):
    """
    Main prediction model that stores the ML prediction results.
    Tracks what symptoms were entered, what disease was predicted,
    and with what confidence.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('reviewed', 'Reviewed by Doctor'),
    ]

    # Who made this prediction
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='predictions'
    )

    # What symptoms were selected
    symptoms = models.ManyToManyField(Symptom, through='PredictionSymptom')

    # Additional context from patient
    age = models.IntegerField(help_text='Patient age at time of prediction')
    additional_notes = models.TextField(blank=True, null=True)

    # ML Prediction results
    predicted_disease = models.ForeignKey(
        Disease,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='predictions'
    )
    predicted_disease_name = models.CharField(max_length=200)  # Store name even if disease deleted

    # Algorithm comparison results (stored as JSON)
    algorithm_results = models.JSONField(default=dict, blank=True)
    # Example: {"Decision Tree": 0.85, "Random Forest": 0.92, "Naive Bayes": 0.78}

    # Best model used
    model_used = models.CharField(max_length=100, default='Random Forest')
    confidence_score = models.FloatField(help_text='Prediction confidence (0-1)')

    # Top 3 possible diseases
    alternative_predictions = models.JSONField(default=list, blank=True)
    # Example: [{"disease": "Flu", "probability": 0.72}, ...]

    # Status and timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Doctor review
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reviewed_predictions'
    )
    doctor_notes = models.TextField(blank=True, null=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Prediction'
        verbose_name_plural = 'Predictions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Prediction #{self.id} - {self.patient.username} - {self.predicted_disease_name}"

    def get_confidence_percentage(self):
        """Return confidence as a percentage string."""
        return f"{self.confidence_score * 100:.1f}%"

    def get_risk_color(self):
        """Return Bootstrap color class based on confidence."""
        if self.confidence_score >= 0.8:
            return 'danger'
        elif self.confidence_score >= 0.6:
            return 'warning'
        else:
            return 'info'

    def get_algorithm_results_formatted(self):
        """Return algorithm results sorted by accuracy."""
        results = self.algorithm_results
        if isinstance(results, dict):
            return sorted(results.items(), key=lambda x: x[1], reverse=True)
        return []


class PredictionSymptom(models.Model):
    """
    Through table connecting Prediction and Symptom.
    Allows storing the severity of each symptom for this prediction.
    """

    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE)
    symptom = models.ForeignKey(Symptom, on_delete=models.CASCADE)
    severity = models.IntegerField(
        default=1,
        choices=[(1, 'Mild'), (2, 'Moderate'), (3, 'Severe')],
        help_text='Severity of this symptom'
    )

    class Meta:
        unique_together = ['prediction', 'symptom']

    def __str__(self):
        return f"{self.prediction.id} - {self.symptom.name} (Severity: {self.severity})"


class PredictionReport(models.Model):
    """Stores generated PDF reports for predictions."""

    prediction = models.OneToOneField(
        Prediction,
        on_delete=models.CASCADE,
        related_name='report'
    )
    pdf_file = models.FileField(upload_to='reports/', null=True, blank=True)
    generated_at = models.DateTimeField(default=timezone.now)
    sent_via_email = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Report for Prediction #{self.prediction.id}"
