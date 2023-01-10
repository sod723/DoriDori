from django.shortcuts import render, redirect
from content.models import Content
from json import dumps
# Create your views here.

def map(request):
    return render(request, "map.html",)

# 사용자의 경로를 반환
def userRoute(request):
    
    startJSON = dumps({"lat": 37.39725123, "lon": 126.95650002, "name": "한가람신라아파트", }, ensure_ascii=False)
    onJSON = dumps({"lat": 37.39641804, "lon": 126.95858318, "name": "세경아파트후문[버스정류장]", }, ensure_ascii=False) 
    offJSON = dumps({"lat": 37.49093773, "lon": 127.11953810, "name": "문정로데오거리입구[버스정류장]", }, ensure_ascii=False)
    endJSON = dumps({"lat": 37.49632607, "lon": 127.12345426, "name": "국립경찰병원", }, ensure_ascii=False)

    return render(request, "map.html", {
        'start': startJSON,
        'onpoint': onJSON,
        'offpoint': offJSON,
        'end': endJSON
    })

def driverRoute(request):
    startJSON = dumps({"lat": 37.39641804, "lon": 126.95858318, "name": "세경아파트후문[버스정류장]", }, ensure_ascii=False) 
    viapoints = [
        dumps({"id": 2000091219, "lat": 37.39894570, "lon": 126.96849888, "name": "스마트베이(마을)[버스정류장]"}, ensure_ascii=False),
        dumps({"id": 2000116823, "lat": 37.39627945, "lon": 126.97441508, "name": "한국교통안전공단안양검사소[버스정류장]"}, ensure_ascii=False),
        dumps({"id": 2000104485, "lat": 37.40480608, "lon": 126.96552676, "name": "중촌마을.동안치매안심센터[버스정류장]"}, ensure_ascii=False),
        dumps({"id": 1135886, "lat": 37.40100116, "lon": 126.97647032, "name": "인덕원역 4번출구"}, ensure_ascii=False)]

    endJSON = dumps({"lat": 37.49632607, "lon": 127.12345426, "name": "국립경찰병원", }, ensure_ascii=False)

    return render(request, "map.html", {
        'start': startJSON,
        'viapoints': dumps(viapoints),
        'end': endJSON
    })
