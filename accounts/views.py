"""
Accounts App - Views
====================
Handles user registration, login, logout, and profile management.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import PatientRegistrationForm, DoctorRegistrationForm, CustomLoginForm, ProfileUpdateForm
from .models import User


def register_patient(request):
    """Handle patient registration."""
    if request.user.is_authenticated:
        return redirect('patient_dashboard')

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.get_full_name()}! Your account has been created.')
            return redirect('patient_dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PatientRegistrationForm()

    return render(request, 'accounts/register_patient.html', {'form': form, 'title': 'Patient Registration'})


def register_doctor(request):
    """Handle doctor registration."""
    if request.user.is_authenticated:
        return redirect('patient_dashboard')

    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Doctor account created! Awaiting admin verification.')
            return redirect('login')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DoctorRegistrationForm()

    return render(request, 'accounts/register_doctor.html', {'form': form, 'title': 'Doctor Registration'})


def user_login(request):
    """Handle user login with role-based redirection."""
    if request.user.is_authenticated:
        return redirect_based_on_role(request.user)

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                return redirect_based_on_role(user)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()

    return render(request, 'accounts/login.html', {'form': form, 'title': 'Login'})


def redirect_based_on_role(user):
    """Redirect user to appropriate dashboard based on role."""
    from django.shortcuts import redirect
    if user.is_admin_user():
        return redirect('/admin/')
    elif user.is_doctor():
        return redirect('doctor_dashboard')
    else:
        return redirect('patient_dashboard')


@login_required
def user_logout(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def profile_view(request):
    """View and update user profile."""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form, 'title': 'My Profile'})


@login_required
def change_password(request):
    """Handle password change."""
    from django.contrib.auth.forms import PasswordChangeForm
    from django.contrib.auth import update_session_auth_hash

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    # Style form fields
    for field in form.fields:
        form.fields[field].widget.attrs.update({'class': 'form-control'})

    return render(request, 'accounts/change_password.html', {'form': form, 'title': 'Change Password'})
