from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .forms import LoginForm

app_name = "core"

urlpatterns = [
    path('', views.Index.as_view(), name="index"),
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html', authentication_form=LoginForm), name='login'),
    path('signup/', views.Signup.as_view(), name="signup"),
    path('logout/', views.logout_view, name="logout"),
    
    path('create_profile/', views.CreateAthlete.as_view(), name="create_profile"),
    path('<int:athlete_pk>/view_profile/', views.ViewProfile.as_view(), name="view_profile"),
    path('<int:athlete_pk>/edit_profile/', views.EditProfile.as_view(), name='edit_profile'),
    path('<int:athlete_pk>/delete_profile/', views.delete_profile, name='delete_profile'),
    
    path('<int:athlete_pk>/view_health_records/', views.ViewHealthRecords.as_view(), name='view_health_records'),
    path('<int:athlete_pk>/create_health_record/', views.CreateHealthRecord.as_view(), name='create_health_record'),
    path('<int:athlete_pk>/<int:record_pk>/view_record', views.ViewHealthRecord.as_view(), name="view_record"),
    path('<int:athlete_pk>/<int:record_pk>/edit_record/', views.EditHealthRecord.as_view(), name='edit_record'),
    path('<int:athlete_pk>/<int:record_pk>/delete_record/', views.delete_health_record, name="delete_record"),
    
    path('<int:athlete_pk>/view_workout_records/', views.ViewWorkoutRecords.as_view(), name='view_workout_records'),
    path('<int:athlete_pk>/create_workout_record/', views.CreateWorkoutRecord.as_view(), name='create_workout_record'),
    path('<int:athlete_pk>/<int:record_pk>/view_workout_record/', views.ViewWorkoutRecord.as_view(), name='view_workout_record'),
    path('<int:athlete_pk>/<int:record_pk>/edit_workout_record/', views.EditWorkoutRecord.as_view(), name='edit_workout_record'),
    path('<int:athlete_pk>/<int:record_pk>/delete_workout_record/', views.delete_workout_record, name='delete_workout_record'),
    
    path('<int:athlete_pk>/select_equipment/', views.SelectEquipment.as_view(), name='select_equipment'),
    path('<int:athlete_pk>/generate_workout/', views.GenerateWorkout.as_view(), name='generate_workout'),   
]
