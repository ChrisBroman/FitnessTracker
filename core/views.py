from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import logout
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .forms import SignupForm,  NewProfileForm, EditProfileForm
from .models import Athlete, WorkoutRecord, HealthRecord

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import urllib
import base64
from decimal import Decimal

def convert_to_kilos(weight):
    return float(weight) * 0.45359237

def blood_pressure_category(systolic, diastolic):
    if systolic < 120 and diastolic < 80:
        return 1  #Normal
    elif 120 <= systolic <= 129 and diastolic < 80:
        return 2 #Elevated
    elif 130 <= systolic <= 139 or 80 <= diastolic <= 89:
        return 3 #Hypertension Stage 1
    elif systolic >= 140 or diastolic >= 90:
        return 4 #Hypertension Stage 2
    elif systolic > 180 or diastolic > 120:
        return 5 #Hypertensive crisis (emergency care needed)
    else:
        return 0

def calculate_bmi(weight, height):
    height_m = height / 100
    bmi_unround = weight / (height_m ** 2)
    bmi_round = round(bmi_unround, 2)
    return bmi_round

class Index(View):
    def get(self, request):
        user = request.user
        context = {
            'user': user,
        }
        return render(request, 'core/index.html', context)
    
class Signup(View):
    def get(self, request):
        form = SignupForm()
        context = {'form': form}
        return render(request, 'core/signup.html', context)
    
    def post(self, request):
        form = SignupForm(request.POST)
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'core/signup.html', context)
        form.save()
        return redirect('core:index')

def logout_view(request):
    logout(request)
    return redirect('core:index')

class CreateAthlete(View, LoginRequiredMixin):
    def get(self, request):
        form = NewProfileForm()
        context = {'form': form}
        return render(request, 'core/create_profile.html', context)
    
    def post(self, request):
        user = request.user
        form = NewProfileForm(request.POST)
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'core/create_profile.html', context)
        new_profile = form.save(commit=False)
        new_profile.user = user
        weight_in_lbs = form.cleaned_data['current_weight']
        weight = convert_to_kilos(weight_in_lbs)
        height = form.cleaned_data['height']
        systolic = form.cleaned_data['current_blood_pressure_sys']
        diastolic = form.cleaned_data['current_blood_pressure_dia'] 
        new_profile.current_bmi = calculate_bmi(weight, height)
        
        if new_profile.current_bmi < 18.5:
            new_profile.current_bmi_class = Athlete.UNDERWEIGHT
        elif new_profile.current_bmi >= 18.5 and new_profile.current_bmi < 25:
            new_profile.current_bmi_class = Athlete.NORMAL
        elif new_profile.current_bmi >= 25 and new_profile.current_bmi < 30:
            new_profile.current_bmi_class = Athlete.OVERWEIGHT
        elif new_profile.current_bmi >= 30 and new_profile.current_bmi < 35:
            new_profile.current_bmi_class = Athlete.OBESE_MODERATE
        elif new_profile.current_bmi >= 35 and new_profile.current_bmi < 40:
            new_profile.current_bmi_class = Athlete.OBESE_SEVERE
        else:
            new_profile.current_bmi_class = Athlete.OBESE_VERY_SEVERE
            
        bp_index = blood_pressure_category(systolic, diastolic)
        if bp_index == 1:
            new_profile.current_blood_pressure_status = Athlete.BP_NORMAL
        elif bp_index == 2:
            new_profile.current_blood_pressure_status = Athlete.BP_ELEVATED
        elif bp_index == 3:
            new_profile.current_blood_pressure_status = Athlete.BP_HYPERTENSION_STAGE_1
        elif bp_index == 4:
            new_profile.current_blood_pressure_status = Athlete.BP_HYPERTENSION_STAGE_2
        else:
            new_profile.current_blood_pressure_status = Athlete.BP_HYPERTENSIVE_CRISIS
            
        new_profile.save()
        return redirect("core:index")

class ViewProfile(View, LoginRequiredMixin):
    def get(self, request):
        user = request.user
        athlete = Athlete.objects.get(user=user)
        context = {'athlete': athlete}
        return render(request, 'core/view_profile.html', context)            
    
class EditProfile(View, LoginRequiredMixin):
    def get(self, request):
        user = request.user
        athlete = Athlete.objects.get(user=user)
        form = EditProfileForm()
        context = {
            'form': form,
            'athlete': athlete,    
        }
        return render(request, 'core/edit_profile.html', context)
    
    def post(self, request):
        user = request.user
        athlete = Athlete.objects.get(user=user)
        form = EditProfileForm(request.POST, instance=athlete)
        if not form.is_valid():
            context = {
                'athlete': athlete,
                'form': form,
            }
            return render(request, 'core/edit_profile.html', context)
        edited_profile = form.save(commit=False)
        weight_in_lbs = form.cleaned_data['current_weight']
        weight = convert_to_kilos(weight_in_lbs)
        height = form.cleaned_data['height']
        systolic = form.cleaned_data['current_blood_pressure_sys']
        diastolic = form.cleaned_data['current_blood_pressure_dia'] 
        edited_profile.current_bmi = calculate_bmi(weight, height)
        if edited_profile.current_bmi < 18.5:
            edited_profile.current_bmi_class = Athlete.UNDERWEIGHT
        elif edited_profile.current_bmi >= 18.5 and edited_profile.current_bmi < 25:
            edited_profile.current_bmi_class = Athlete.NORMAL
        elif edited_profile.current_bmi >= 25 and edited_profile.current_bmi < 30:
            edited_profile.current_bmi_class = Athlete.OVERWEIGHT
        elif edited_profile.current_bmi >= 30 and edited_profile.current_bmi < 35:
            edited_profile.current_bmi_class = Athlete.OBESE_MODERATE
        elif edited_profile.current_bmi >= 35 and edited_profile.current_bmi < 40:
            edited_profile.current_bmi_class = Athlete.OBESE_SEVERE
        else:
            edited_profile.current_bmi_class = Athlete.OBESE_VERY_SEVERE
            
        bp_index = blood_pressure_category(systolic, diastolic)
        if bp_index == 1:
            edited_profile.current_blood_pressure_status = Athlete.BP_NORMAL
        elif bp_index == 2:
            edited_profile.current_blood_pressure_status = Athlete.BP_ELEVATED
        elif bp_index == 3:
            edited_profile.current_blood_pressure_status = Athlete.BP_HYPERTENSION_STAGE_1
        elif bp_index == 4:
            edited_profile.current_blood_pressure_status = Athlete.BP_HYPERTENSION_STAGE_2
        else:
            edited_profile.current_blood_pressure_status = Athlete.BP_HYPERTENSIVE_CRISIS
            
        edited_profile.save()
        return redirect('core:view_profile')

def delete_profile(request):
    user = request.user
    athlete = Athlete.objects.get(user=user)
    athlete.delete()
    return redirect('core:index')