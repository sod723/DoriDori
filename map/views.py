from django.shortcuts import render
from django.http import HttpResponse
from .models import *

def index(request) :
    return render(request, 'main.html')
    #return HttpResponse("Hello meap.index")
    
def loginPage(request) :
    # return HttpResponse("Hello Add_AddressData")
    return render(request, 'login.html')

def testMap(request) :
    return render(request,'testMap.html')