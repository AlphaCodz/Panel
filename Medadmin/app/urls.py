from django.urls import path, re_path
from . import views

app_name = "app"

urlpatterns = [
    path("", views.index, name="index"),
    path("signin/", views.signin, name="signin"),
    path("signup/", views.signup, name="signup")
    
]
