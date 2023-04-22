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
    path('view_profile/', views.ViewProfile.as_view(), name="view_profile"),
    path('edit_profile/', views.EditProfile.as_view(), name='edit_profile'),
    path('delete_profile/', views.delete_profile, name='delete_profile'),
]
