from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import Athlete, HealthRecord, WorkoutRecord

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
    
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your username',
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your password',
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Repeat password',
    }))
    
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Your username',
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Your password',
    }))
    
class NewProfileForm(forms.ModelForm):
    class Meta:
        model = Athlete
        fields = ('name', 'height', 'current_weight', 'current_blood_pressure_sys', 'current_blood_pressure_dia',)
        widgets = {
            'name': forms.TextInput(),
            'height': forms.TextInput(),
            'current_weight': forms.TextInput(),
            'current_blood_pressure_sys': forms.TextInput(),
            'current_blood_pressure_dia': forms.TextInput(),
        }
        
class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Athlete
        fields = ('name', 'height', 'current_weight', 'current_blood_pressure_sys', 'current_blood_pressure_dia',)
        widgets = {
            'name': forms.TextInput(),
            'height': forms.TextInput(),
            'current_weight': forms.TextInput(),
            'current_blood_pressure_sys': forms.TextInput(),
            'current_blood_pressure_dia': forms.TextInput(),
        }