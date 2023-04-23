from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

class Athlete(models.Model):
    class Meta:
        ordering = ('name',)
        
    UNDERWEIGHT = 'Underweight'
    NORMAL = 'Normal'
    OVERWEIGHT = 'Overweight'
    OBESE_MODERATE = 'Obese Moderate'
    OBESE_SEVERE = 'Obese Severe'
    OBESE_VERY_SEVERE = 'Obese Very Severe'
    BMI_CHOICE = (
        (UNDERWEIGHT, 'Underweight'),
        (NORMAL, 'Normal'),
        (OVERWEIGHT, 'Overweight'),
        (OBESE_MODERATE,'Obese Moderate'),
        (OBESE_SEVERE, 'Obese Severe'),
        (OBESE_VERY_SEVERE, 'Obese Very Severe'),
    )
    
    BP_NORMAL = 'Normal Blood Pressure'
    BP_ELEVATED = 'Elevated Blood Pressure'
    BP_HYPERTENSION_STAGE_1 = 'Hypertension Stage 1'
    BP_HYPERTENSION_STAGE_2 = 'Hypertension Stage 2'
    BP_HYPERTENSIVE_CRISIS = 'Hypertensive Crisis'
    BP_CHOICES = (
        (BP_NORMAL, 'Normal Blood Pressure'),
        (BP_ELEVATED, 'Elevated Blood Pressure'),
        (BP_HYPERTENSION_STAGE_1, 'Hypertension Stage 1'),
        (BP_HYPERTENSION_STAGE_2, 'Hypertension Stage 2'),
        (BP_HYPERTENSIVE_CRISIS, 'Hypertensive Crisis')
    )
        
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    height = models.IntegerField(validators=[MinValueValidator(50), MaxValueValidator(300)])
    current_weight = models.DecimalField(decimal_places=1, max_digits=4)
    current_bmi = models.DecimalField(decimal_places=4, max_digits=6, null=True, blank=True)
    current_bmi_class = models.CharField(max_length=32, choices=BMI_CHOICE, null=True, blank=True)
    current_blood_pressure_sys = models.IntegerField(validators=[MinValueValidator(30), MaxValueValidator(170)], null=True, blank=True)
    current_blood_pressure_dia = models.IntegerField(validators=[MinValueValidator(30), MaxValueValidator(170)], null=True, blank=True)
    current_blood_pressure_status = models.CharField(max_length=32, choices=BP_CHOICES, null=True, blank=True)
    
    def __str__(self):
        return self.name
    
class HealthRecord(models.Model):
    class Meta:
        ordering = ('-date',)
    
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.DecimalField(decimal_places=1, max_digits=4)
    blood_pressure_sys = models.IntegerField(validators=[MinValueValidator(30), MaxValueValidator(170)], null=True, blank=True)     
    blood_pressure_dia = models.IntegerField(validators=[MinValueValidator(30), MaxValueValidator(170)], null=True, blank=True)

    def __str__(self):
        return f'Health Record {self.date}'
    
class WorkoutRecord(models.Model):
    class Meta:
        ordering = ('-date',)
    
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.CharField(max_length=256)
    duration = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(180)])