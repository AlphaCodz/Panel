from django.urls import path, re_path
from . import views
from .views import Forms

app_name = "app"

urlpatterns = [
    path("", views.index, name="index"),
    path("signin/", views.signin, name="signin"),
    path("signup/", views.signup, name="signup"),
    path("diagnosis/", Forms.diagnosis_form, name="diagnosis_form")
]
