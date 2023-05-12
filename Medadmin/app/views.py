from django.shortcuts import render, redirect
import requests
from .models import PrimaryUser
import re
from django.contrib import messages

# Create your views here.
def index(request):
    # get all doctors
    url = "https://medico-production-fa1c.up.railway.app/api/all/docs" 
    
    # Get doc data
    response = requests.get(url)
    data = response.json()
    
    return render(request, "basic_files/index.html", {"data":data})

def signin(request):
    return render(request, "basic_files/auth-signin.html")

def signup(request):
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        staff_number = request.POST["staff_no"]

        # Check Password Length
        if len(password) < 5:
            messages.error(request, "The minimum length for a password is 5 characters")
            return redirect("app:signup")

        # Check for Upper Case and Numbers 
        if not re.search(r"[A-Z]", password) or not re.search(r"\d", password):
            messages.error(request, "The password must contain at least one capital letter and one number")
            return redirect("app:signup")

        # Check Staff Number
        if not staff_number:
            messages.error(request, "Please input your Staff Number")
            return redirect("app:signup")

        # Check if Email already exists
        if PrimaryUser.objects.filter(email=email).exists():
            messages.error(request, "Sorry! The email is already registered")
            return redirect("app:signup")
        
        # Create new user
        admin = PrimaryUser(first_name=first_name, last_name=last_name, email=email, staff_number=staff_number)
        admin.set_password(password)
        admin.save()
        messages.success(request, "Registered successfully")
        return redirect("app:signin")

    return render(request, "basic_files/auth-signup.html")