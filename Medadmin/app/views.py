from django.shortcuts import render
import requests

# Create your views here.
def index(request):
    
    # get all doctors
    url = "https://medico-production-fa1c.up.railway.app/api/all/docs" 
    
    # Get doc data
    response = requests.get(url)
    data = response.json()
    
    return render(request, "basic_files/index.html", {"data":data})