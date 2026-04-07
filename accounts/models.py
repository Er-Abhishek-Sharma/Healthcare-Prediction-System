"""
Accounts App - Models
=====================
Custom User model with role-based access for patients, doctors, and admins.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """
    Extended User model with role-based access control.
    Roles: patient, doctor, admin
    """

    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    ]

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    # Role field - determines dashboard access
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')

    # Personal information
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # Doctor-specific fields
    specialization = models.CharField(max_length=100, blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    hospital_name = models.CharField(max_length=200, blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    # Account status
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    def is_patient(self):
        return self.role == 'patient'

    def is_doctor(self):
        return self.role == 'doctor'

    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser

    def get_age(self):
        """Calculate age from date of birth."""
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
