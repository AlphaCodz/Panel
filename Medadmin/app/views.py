from django.shortcuts import render
import requests
from .models import PrimaryUser

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
        first_name = ["first_name"],
        
    return render(request, "basic_files/auth-signup.html")