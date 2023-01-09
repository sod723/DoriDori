from django.shortcuts import render, redirect
from content.models import Content
# Create your views here.

def map(request):
    return render(request, "map.html",)

def userRoute(request):
    pointInfoList = [
    {"lat": 37.39725123, "lon": 126.95650002, "name": "한가람신라아파트"}, 
    {"lat": 37.39555694, "lon": 126.95380587, "name": "세경아파트후문[버스정류장]"}, 
    {"lat": 37.49093773, "lon": 127.11953810, "name": "문정로데오거리입구[버스정류장]"}, 
    {"lat": 37.49632607, "lon": 127.12345426, "name": "국립경찰병원"}]

    return render(request, "map.html", {
        'pointInfoList': pointInfoList
    })

