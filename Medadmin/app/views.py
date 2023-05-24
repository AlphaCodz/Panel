from django.shortcuts import render, redirect, HttpResponse
import requests
from .models import PrimaryUser
import re
from django.contrib import messages, auth
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.views import View
from django.views.generic import ListView
import json
# Create your views here.

# AJAX 
@cache_page(60 * 30, key_prefix='/app/')
def index(request):
    # user_url = "https://medico-production-fa1c.up.railway.app/api/admin/data"
    doc_data_url = "https://medico-production-fa1c.up.railway.app/api/all/docs"
    patient_url = "https://medico-production-fa1c.up.railway.app/api/all/users"
    assigned_patients = "https://medico-production-fa1c.up.railway.app/api/assigned/patients"
    
    # user_response = requests.get(user_url)
    doc_data_url = requests.get(doc_data_url)
    patient_response = requests.get(patient_url)
    assigned_patients_response = requests.get(assigned_patients)
    
    if (
        # user_response.status_code == 200 and
        doc_data_url.status_code == 200 and
        patient_response.status_code == 200 and
        assigned_patients_response.status_code == 200
    ):
        # Pagination
        # user_data = user_response.json().get('admin')
        doc_data = doc_data_url.json().get('doctors')
        patients_data = patient_response.json().get('patients')
        assigned_patient = assigned_patients_response.json().get('data')
        
        # Total Number of Doctors    
        doc_count = len(doc_data)
        
        # Total Number of Patients
        patient_count = len(patients_data)
        
        # Total number of assigned patients
        assigned_patients_count = len(assigned_patient) 
        
        # Paginate
        paginator = Paginator(doc_data, 7)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            # "user": user_data,
            "docs": page_obj,
            "total_no_of_docs": doc_count,
            "total_no_of_patients": patient_count,
            "assigned_patients": assigned_patients_count,
            "patients_data": [],
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
            "has_previous": page_obj.has_previous(),
            "has_next": page_obj.has_next()
        }
        
        # Additional check for patient_response status code
        if patient_response.status_code == 200:
            patients_data = patient_response.json().get('patients')
            
            # Pagination
            paginator = Paginator(patients_data, 7)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            for patient in page_obj:
                data = {
                    "current_page": page_obj.number,
                    "total_pages": paginator.num_pages,
                    "has_previous": page_obj.has_previous(),
                    "has_next": page_obj.has_next(), 
                    "first_name": patient.get('first_name'),
                    "last_name": patient.get('last_name'),
                    "email": patient.get('email'),
                    "username": patient.get('username'),
                    "is_patient": patient.get('is_patient'),
                    "is_medic": patient.get('is_medic'),
                    "is_admin": patient.get('is_admin'),
                }
                context["patients_data"].append(data)
                
            return render(request, "basic_files/index.html", context)
        
    # Error handling for failed data retrieval
    print("Error: Failed to retrieve data")
    return HttpResponse("Failed to retrieve data", status=500)

    
    
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
        
        # Check if Staff Number Exists
        if PrimaryUser.objects.filter(staff_number=staff_number).exists():
            messages.error(request, "Staff already exists")
            return redirect("app:signup")
        
        # Create new user
        admin = PrimaryUser(first_name=first_name, last_name=last_name, email=email, staff_number=staff_number)
        admin.set_password(password)
        admin.save()
        messages.success(request, "Registered successfully")
        return redirect("app:signin")

    return render(request, "basic_files/auth-signup.html")

def signin(request):
    if request.method == "POST":
        url = "https://medico-production-fa1c.up.railway.app/api/login"
        email = request.POST["email"]
        password = request.POST["password"]
        
        # DICTIONARY DATA
        data = {
            "email":email,
            "password":password
        }
        # make a POST request to the API endpoint with the data
        response = requests.post(url, data=data)
        
        # check response status
        if response.status_code == 200:
            token = response.json().get("token")
            messages.success(request, "Login Successful")
            return redirect("app:index")
        else:
            # Login Failed
            error_message = response.json().get("error")
            messages.error(request, error_message)
            print(f"Login failed: {error_message}")
            return redirect("app:signin")
             
    return render(request, "basic_files/auth-signin.html")

def hospital_card_generator(request):
    users = "https://medico-production-fa1c.up.railway.app/api/all/users"

    if request.method == "POST" and "card_submit" in request.POST:
        patient_id = request.POST.get("patient_id")
        hospital_branch = request.POST.get("hospital_branch")
        card_url = f"https://medico-production-fa1c.up.railway.app/api/create/card/{patient_id}"

        payload = {
            "patient_id": patient_id,
            "hospital_branch": hospital_branch
        }
        resp = requests.post(card_url, payload)

        if resp.status_code == 200:
            messages.success(request, "Card Generated Successfully")
            print(f"ERROR: {resp.status_code}")
        else:
            messages.error(request, "ERROR")
            print(f"ERROR: {resp.status_code}")
    return redirect("app:card")

    context = {
        "patients": users,
    }
    return render(request, "sections/hospital_card.html", context)




def notifications(request):
    url = "https://medico-production-fa1c.up.railway.app/api/notify"
    
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        new_users = data.get('new_users', [])
        new_docs = data.get('new_docs', [])
    else:
        new_users = []
        new_docs = []

    context = {
        'new_users': new_users,
        'new_docs': new_docs
    }
    return render(request, "sections/notifications.html", context)
                
                
                
@cache_page(60 * 30, key_prefix='/app/diagnosis/')
class Forms:
    def diagnosis_form(request):
        
        users = "https://medico-production-fa1c.up.railway.app/api/all/users"
        if request.method == "POST":
            patient_id = request.POST.get("patient_id")
            prescription = request.POST.get("prescription")
            additional_notes = request.POST.get("additional_notes")
            diagnosis = request.POST.get("diagnosis")
            diagnose_url = f"https://medico-production-fa1c.up.railway.app/api/create/diag/{patient_id}"

            payload = {
                "patient_id": patient_id,
                "prescription": prescription,
                "additional_notes": additional_notes,
                "diagnosis": diagnosis
            }

            resp = requests.post(diagnose_url, payload)

            if resp.status_code == 201:
                messages.success(request, "Diagnosed Successfully")
            else:
                # error_message = resp.json().get("error")
                messages.error(request, "ERROR")
                # print(f"Login failed: {error_message}")

        response = requests.get(users)
        

        if response.status_code == 200:
            users = response.json().get("patients")
            # print(f"PATIENTS {response.status_code}")


        context = {
            "patients": users,
            # "user": admin_data,
        }
        
        url = "https://medico-production-fa1c.up.railway.app/api/notify"
        response = requests.get(url)
        
        new_users = response.json().get('new_users')

        return render(request, "basic_files/diag_form.html", context)