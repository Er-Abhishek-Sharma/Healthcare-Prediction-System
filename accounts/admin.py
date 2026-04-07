"""
Accounts Admin Configuration
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'gender']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']

    fieldsets = UserAdmin.fieldsets + (
        ('Role & Profile', {
            'fields': ('role', 'phone', 'date_of_birth', 'gender', 'address',
                       'profile_picture', 'is_verified')
        }),
        ('Doctor Info', {
            'fields': ('specialization', 'license_number', 'hospital_name', 'consultation_fee'),
            'classes': ('collapse',)
        }),
    )
