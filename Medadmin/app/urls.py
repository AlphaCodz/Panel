from django.urls import path, re_path
from . import views
from .views import Forms


# from .views import PatientsList

app_name = "app"

urlpatterns = [
    path("", views.index, name="index"),
    path("signin/", views.signin, name="signin"),
    path("signup/", views.signup, name="signup"),
    path("diagnosis/", Forms.diagnosis_form, name="diagnosis_form"),
    path("card/", views.hospital_card_generator, name="card"),
    path("notifications/", views.notifications, name="notification")
    # path("", PatientsList.as_view(), name="list")
]
