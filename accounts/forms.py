"""
Accounts App - Forms
====================
Registration, login, and profile update forms.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class PatientRegistrationForm(UserCreationForm):
    """Registration form for patients."""

    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    gender = forms.ChoiceField(
        choices=[('', 'Select Gender'), ('M', 'Male'), ('F', 'Female'), ('O', 'Other')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Address'})
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone',
                  'date_of_birth', 'gender', 'address', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        if commit:
            user.save()
        return user


class DoctorRegistrationForm(UserCreationForm):
    """Registration form for doctors."""

    first_name = forms.CharField(max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    specialization = forms.CharField(max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Cardiologist, Neurologist'}))
    license_number = forms.CharField(max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    hospital_name = forms.CharField(max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    consultation_fee = forms.DecimalField(max_digits=8, decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'phone',
                  'specialization', 'license_number', 'hospital_name',
                  'consultation_fee', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'doctor'
        if commit:
            user.save()
        return user


class CustomLoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password'
        })
    )


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone',
                  'date_of_birth', 'gender', 'address', 'profile_picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }
