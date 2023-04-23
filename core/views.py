from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import logout
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from .forms import SignupForm,  NewProfileForm, EditProfileForm, CreateHealthRecordForm, CreateWorkoutRecordForm
from .models import Athlete, WorkoutRecord, HealthRecord

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import urllib
import base64
from decimal import Decimal
from datetime import datetime

def convert_to_kilos(weight):
    return float(weight) * 0.45359237

def blood_pressure_category(systolic, diastolic):
    if systolic < 120 and diastolic < 80:
        return Athlete.BP_NORMAL
    elif 120 <= systolic <= 129 and diastolic < 80:
        return Athlete.BP_ELEVATED
    elif 130 <= systolic <= 139 or 80 <= diastolic <= 89:
        return Athlete.BP_HYPERTENSION_STAGE_1
    elif systolic >= 140 or diastolic >= 90:
        return Athlete.BP_HYPERTENSION_STAGE_2
    else:
        return Athlete.BP_HYPERTENSIVE_CRISIS
    
def bmi_category(bmi):
    if bmi < 18.5:
        bmi_class = Athlete.UNDERWEIGHT
    elif bmi >= 18.5 and bmi < 25:
        bmi_class = Athlete.NORMAL
    elif bmi >= 25 and bmi < 30:
        bmi_class = Athlete.OVERWEIGHT
    elif bmi >= 30 and bmi < 35:
        bmi_class = Athlete.OBESE_MODERATE
    elif bmi >= 35 and bmi < 40:
        bmi_class = Athlete.OBESE_SEVERE
    else:
        bmi_class = Athlete.OBESE_VERY_SEVERE
    return bmi_class

def calculate_bmi(weight, height):
    height_m = height / 100
    bmi_unround = weight / (height_m ** 2)
    bmi_round = round(bmi_unround, 2)
    return bmi_round

class Index(View):
    def get(self, request):
        user = request.user
        athlete = Athlete.objects.filter(user=user).first()
        context = {
            'user': user,
            'athlete': athlete,
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
        new_profile.current_bmi_class = bmi_category(new_profile.current_bmi)
        new_profile.current_blood_pressure_status = blood_pressure_category(systolic, diastolic)    
        new_profile.save()
        return redirect("core:index")

class ViewProfile(View, LoginRequiredMixin):
    def get(self, request, athlete_pk):
        user = request.user
        athlete = Athlete.objects.get(user=user, pk=athlete_pk)
        context = {'athlete': athlete}
        return render(request, 'core/view_profile.html', context)            
    
class EditProfile(View, LoginRequiredMixin):
    def get(self, request, athlete_pk):
        user = request.user
        athlete = Athlete.objects.get(user=user, pk=athlete_pk)
        form = EditProfileForm()
        context = {
            'form': form,
            'athlete': athlete,    
        }
        return render(request, 'core/edit_profile.html', context)
    
    def post(self, request, athlete_pk):
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
        edited_profile.current_bmi_class = bmi_category(edited_profile.current_bmi)
        edited_profile.current_blood_pressure_status = blood_pressure_category(systolic, diastolic)
        edited_profile.save()
        return redirect('core:view_profile', athlete_pk=athlete_pk)

def delete_profile(request, athlete_pk):
    user = request.user
    athlete = Athlete.objects.get(user=user, pk=athlete_pk)
    athlete.delete()
    return redirect('core:index')

class CreateHealthRecord(View, LoginRequiredMixin):
    def get(self, request, athlete_pk):
        form = CreateHealthRecordForm()
        context = {'form': form}
        return render(request, 'core/new_health_record.html', context)
    
    def post(self, request, athlete_pk):
        user = request.user
        athlete = Athlete.objects.get(user=user, pk=athlete_pk)
        form = CreateHealthRecordForm(request.POST)
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'core/new_health_record.html', context)
        new_record = form.save(commit=False)
        new_record.athlete = athlete
        new_record.save()
        weight = form.cleaned_data['weight']
        systolic = form.cleaned_data['blood_pressure_sys']
        diastolic = form.cleaned_data['blood_pressure_dia']
        weight_kg = convert_to_kilos(weight)
        athlete.current_weight = weight
        athlete.current_bmi = calculate_bmi(weight_kg, athlete.height)
        athlete.current_bmi_class = bmi_category(athlete.current_bmi)
        athlete.current_blood_pressure_sys = systolic
        athlete.current_blood_pressure_dia = diastolic
        athlete.current_blood_pressure_status = blood_pressure_category(systolic, diastolic)
        athlete.save(update_fields=['current_weight', 'current_bmi', 'current_bmi_class','current_blood_pressure_sys', 'current_blood_pressure_dia', 'current_blood_pressure_status'])
        return redirect('core:view_health_records', athlete_pk=athlete_pk)
    
class ViewHealthRecords(View, LoginRequiredMixin):
    def get(self, request, athlete_pk):
        user = request.user
        athlete = Athlete.objects.get(user=user, pk=athlete_pk)
        records = HealthRecord.objects.filter(athlete=athlete)
        context = {
            'athlete': athlete,
            'records': records,
        }
        return render(request, 'core/view_health_records.html', context)
    
class ViewHealthRecord(View, LoginRequiredMixin):
    def get(self, request, athlete_pk, record_pk):
        user = request.user
        athlete = Athlete.objects.get(user=user, pk=athlete_pk)
        record = HealthRecord.objects.get(athlete=athlete, pk=record_pk)
        context = {
            'athlete': athlete,
            'record': record,
        }
        return render(request, 'core/view_record.html', context)
    
class EditHealthRecord(View, LoginRequiredMixin):
    def get(self, request, athlete_pk, record_pk):
        user = request.user
        athlete = Athlete.objects.get(user=user, pk=athlete_pk)
        record = HealthRecord.objects.get(athlete=athlete, pk=record_pk)
        form = CreateHealthRecordForm()
        context = {
            'athlete': athlete,
            'record': record,
            'form': form
        }
        return render(request, 'core/edit_health_record.html', context)
        
    def post(self, request, athlete_pk, record_pk):
        user = request.user
        athlete = Athlete.objects.get(user=user, pk=athlete_pk)
        record = HealthRecord.objects.get(athlete=athlete, pk=record_pk)
        form = CreateHealthRecordForm(request.POST, instance=record)
        if not form.is_valid():
            context = {
                'athlete': athlete,
                'record': record,
                'form': form,
            }
            return render(request, 'core/edit_health_record.html', context)
        edited = form.save(commit=False)
        current_date = HealthRecord.objects.filter(athlete=athlete).first().date
        if form.cleaned_data['date'] > current_date:
            weight = form.cleaned_data['weight']
            systolic = form.cleaned_data['blood_pressure_sys']
            diastolic = form.cleaned_data['blood_pressure_dia']
            weight_kg = convert_to_kilos(weight)
            athlete.current_weight = weight
            athlete.current_bmi = calculate_bmi(weight_kg, athlete.height)
            athlete.current_bmi_class = bmi_category(athlete.current_bmi)
            athlete.current_blood_pressure_sys = systolic
            athlete.current_blood_pressure_dia = diastolic
            athlete.current_blood_pressure_status = blood_pressure_category(systolic, diastolic)
            athlete.save(update_fields=['current_weight', 'current_bmi', 'current_bmi_class','current_blood_pressure_sys', 'current_blood_pressure_dia', 'current_blood_pressure_status'])
        edited.save()    
        return redirect('core:view_record', athlete_pk=athlete_pk, record_pk=record_pk)
    
def delete_health_record(request, athlete_pk, record_pk):
    user = request.user
    athlete = Athlete.objects.get(user=user, pk=athlete_pk)
    record = HealthRecord.objects.get(athlete=athlete, pk=record_pk)
    record.delete()
    return redirect('core:view_health_records', athlete_pk=athlete_pk)

class ViewWorkoutRecords(View, LoginRequiredMixin):
    def get(self, request, athlete_pk):
        user = request.user
        athlete = Athlete.objects.get(user=user, pk=athlete_pk)
        records = WorkoutRecord.objects.filter(athlete=athlete)
        context = {
            'athlete': athlete,
            'records': records,
        }
        return render(request, 'core/view_workout_records.html', context)
    
class CreateWorkoutRecord(View, LoginRequiredMixin):
    def get(self, request, athlete_pk):
        user = request.user
        form = CreateWorkoutRecordForm()
        context = {'form': form}
        return render(request, 'core/create_workout_record.html', context)
    
    def post(self, request, athlete_pk):
        user = request.user
        athlete = Athlete.objects.get(user=user, pk=athlete_pk)
        form = CreateWorkoutRecordForm(request.POST)
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'core/create_workout_record.html', context)
        new_record = form.save(commit=False)
        new_record.athlete = athlete
        new_record.save()
        return redirect('core:view_workout_records', athlete_pk=athlete_pk)
    
class ViewWorkoutRecord(View, LoginRequiredMixin):
    def get(self, request, athlete_pk, record_pk):
        user = request.user
        athlete = Athlete.objects.get(user=user, pk=athlete_pk)
        record = WorkoutRecord.objects.get(athlete=athlete, pk=record_pk)
        context = {
            'athlete': athlete,
            'record': record,
        }
        return render(request, 'core/view_workout_record.html', context)
    
class EditWorkoutRecord(View, LoginRequiredMixin):
    def get(self, request, athlete_pk, record_pk):
        user = request.user
        athlete = Athlete.objects.get(user=user, pk=athlete_pk)
        record = WorkoutRecord.objects.get(athlete=athlete, pk=record_pk)
        form = CreateWorkoutRecordForm()
        context = {
            'form': form,
            'record': record,
        }
        return render(request, 'core/edit_workout_record.html', context)
    
    def post(self, request, athlete_pk, record_pk):
        user = request.user
        athlete = Athlete.objects.get(user=user, pk=athlete_pk)
        record = WorkoutRecord.objects.get(athlete=athlete, pk=record_pk)
        form = CreateWorkoutRecordForm(request.POST, instance=record)
        if not form.is_valid():
            context = {'form': form}
            return render(request, 'core/edit_workout_record.html', context)
        form.save()
        return redirect('core:view_workout_record', athlete_pk=athlete_pk, record_pk=record_pk)
    
def delete_workout_record(request, athlete_pk, record_pk):
    user = request.user
    athlete = Athlete.objects.get(user=user, pk=athlete_pk)
    record = WorkoutRecord.objects.get(athlete=athlete, pk=record_pk)
    record.delete()
    return redirect('core:view_workout_records', athlete_pk=athlete_pk)