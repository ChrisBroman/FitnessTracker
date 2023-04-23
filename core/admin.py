from django.contrib import admin

from .models import Athlete, HealthRecord, WorkoutRecord

admin.site.register(Athlete)
admin.site.register(HealthRecord)
admin.site.register(WorkoutRecord)