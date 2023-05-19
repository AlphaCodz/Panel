from django.shortcuts import render, redirect, HttpResponse
import requests
from .models import PrimaryUser
import re
from django.contrib import messages, auth
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.views import View
# Create your views here.

@cache_page(60 * 15, key_prefix='/app/')
def index(request):
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxMDMyMzk3MDgxMiwiaWF0IjoxNjgzOTcwODEyLCJqdGkiOiI1ZjMwNzE4Y2Y3NDg0MGNmYTRmOTUxY2QwYzEzN2I3NiIsInVzZXJfaWQiOjg2fQ.dvgBFacSU6w4z5AHN0MQls6DvKEk-PwrbX1tgikR8Wk"
    headers = {'Authorization' : f'Bearer {token}'}
    
    user_url = "https://medico-production-fa1c.up.railway.app/api/admin/data"
    doc_data_url = "https://medico-production-fa1c.up.railway.app/api/all/docs"
    patient_url = "https://medico-production-fa1c.up.railway.app/api/all/users"
    assigned_patients = "https://medico-production-fa1c.up.railway.app/api/assigned/patients"
    
    user_response = requests.get(user_url, headers=headers)
    doc_data_url = requests.get(doc_data_url, headers=headers)
    patient_response = requests.get(patient_url, headers=headers)
    assigned_patients_response = requests.get(assigned_patients, headers)
    
    if user_response.status_code == 200 and doc_data_url.status_code == 200:
        
        # Pagination
        user_data = user_response.json().get('admin')
        doc_data = doc_data_url.json().get('doctors')
        patients_data = patient_response.json().get('patients')
        assigned_patient = assigned_patients_response.json().get('data')
        
            # Total Number of Doctors    
        doc_count = len(doc_data)
        
            #Total Number of Patients
        patient_count = len(patients_data)
        
            #Total number of assigned patients
        assigned_patients_count = len(assigned_patient) 
        
            # Paginate
        paginator = Paginator(doc_data, 7)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            "user": user_data,
            "docs": page_obj,
            "total_no_of_docs": doc_count,
            "total_no_of_patients": patient_count,
            "assigned_patients":assigned_patients_count,
            "patients_data": [],
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
            "has_previous": page_obj.has_previous(),
            "has_next": page_obj.has_next()
        }
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
        else:
            print("Error: Failed to Retrieve data")
            return HttpResponse("Failed to retrieve data")
    
    
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


# class DiagnosisFormView(View):
#     def post(self, request):
#         token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxMDMyMzk3MDgxMiwiaWF0IjoxNjgzOTcwODEyLCJqdGkiOiI1ZjMwNzE4Y2Y3NDg0MGNmYTRmOTUxY2QwYzEzN2I3NiIsInVzZXJfaWQiOjg2fQ.dvgBFacSU6w4z5AHN0MQls6DvKEk-PwrbX1tgikR8Wk"  # Your token here
#         headers = {'Authorization': f'Bearer {token}'}
#         users_url = "https://medico-production-fa1c.up.railway.app/api/all/users"
        
#         # Retrieve the list of patients from the API
#         response = requests.get(users_url, headers=headers)
#         if response.status_code == 200:
#             users = response.json().get("patients")
#         else:
#             # Handle the error case when the API request fails
#             users = []
        
#         # Extract the necessary data from the POST request
#         patient_id = request.POST.get("patient_id")
#         prescription = request.POST.get("prescription")
#         additional_notes = request.POST.get("additional_notes")
#         diagnose_url = f"https://medico-production-fa1c.up.railway.app/api/create/diag/{patient_id}"
        
#         # Prepare the payload for the POST request
#         payload = {
#             "patient_id": patient_id,
#             "prescription": prescription,
#             "additional_notes": additional_notes
#         }
        
#         # Make the POST request to submit the diagnosis
#         response = requests.post(diagnose_url, json=payload)
#         if response.status_code == 200:
#             messages.success(request, "Diagnosed successfully")
#             return redirect("app:diagnosis_form")
#         else:
#             error_message = response.json().get('error')
#             messages.error(request, error_message)
#             print(f"ERROR: {error_message}")
#             return redirect("app:diagnosis_form")
        
#         # Pass the users data to the template context
#         context = {
#             "patients": users
#         }
        
#         return render(request, "basic_files/diag_form.html", context)

class Forms:
    def diagnosis_form(request):
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxMDMyMzk3MDgxMiwiaWF0IjoxNjgzOTcwODEyLCJqdGkiOiI1ZjMwNzE4Y2Y3NDg0MGNmYTRmOTUxY2QwYzEzN2I3NiIsInVzZXJfaWQiOjg2fQ.dvgBFacSU6w4z5AHN0MQls6DvKEk-PwrbX1tgikR8Wk"
        headers = {'Authorization': f'Bearer {token}'}

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
            if resp.status_code == 200:
                messages.success(request, "Diagnosed Successfully")
            else:
                error_message = resp.json().get('error')
                if error_message:
                    messages.error(request, error_message)
                    print(f"ERROR: {error_message}")
                else:
                    messages.error(request, "An error occured during diagnosis")
            return redirect("app:diagnosis_form")

        response = requests.get(users, headers)
        if response.status_code == 200:
            users = response.json().get("patients")

        context = {
            "patients": users
        }

        return render(request, "basic_files/diag_form.html", context)

    

def HospitalCardGenerator(request):
    return render(request, "sections/id_card.html")