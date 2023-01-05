from django.shortcuts import render, redirect
from content.models import Content
# Create your views here.

def map(request):
    return render(request, "map.html",)
