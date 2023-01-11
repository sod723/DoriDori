from django.shortcuts import render, redirect
from content.models import Content
from json import dumps
from json import loads
from urllib.parse import urlencode
import requests

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "appKey": "l7xx846db5f3bc1e48d29b7275a745d501c8"  # my app key
}

load = {
    "startX": 0,
    "startY": 0,
    "endX": 0,
    "endY": 0,
    "startName": "",
    "endName": "",
}

url = "https://apis.openapi.sk.com/tmap/routes"


def map(request):
    # user info return
    return render(request, "map.html", )


# API parameter JSON
def getRouteJSON(start, end):
    return {
        "startX": start["lon"],
        "startY": start["lat"],
        "endX": end["lon"],
        "endY": end["lat"],
        "startName": start["name"],
        "endName": end["name"]
    }


# 경로 point 반환
def getPath(resultData):
    resultList = []

    for elem in resultData:
        geometry = elem["geometry"]
        properties = elem["properties"]

        if (geometry["type"] == "LineString"):
            resultList.append(geometry["coordinates"])
        else:
            pass

    return resultList


# 경로 구하기
def fetchRoute(option, routeType=""):
    apiUrl = url + routeType + "?version=1&callback=function"
    response = requests.post(apiUrl, json=option, headers=headers)
    x = loads(response.text)
    return getPath(x["features"])


def createUserRoute(path, marker):
    resultData = []
    for i in range(0, len(path)):
        marker.append([path[i]["lat"], path[i]["lon"]])
        if (i < len(path) - 1):
            load = getRouteJSON(path[i], path[i + 1])

            if (i == 1):
                resultData.append(fetchRoute(load))  # 운전자 경로
            else:
                resultData.append(fetchRoute(load, "/pedestrian"))

    return resultData


# 사용자의 경로를 반환
def userRoute(request):
    markerPoint = []

    # 출발지
    # 탑승지(클러스터링)
    # 하차지(클러스터링)
    # 목적지
    route = [{"lat": 37.39725123, "lon": 126.95650002, "name": "한가람신라아파트"},
             {"lat": 37.39641804, "lon": 126.95858318, "name": "세경아파트후문[버스정류장]"},
             {"lat": 37.49093773, "lon": 127.11953810, "name": "문정로데오거리입구[버스정류장]"},
             {"lat": 37.49632607, "lon": 127.12345426, "name": "국립경찰병원", }]

    path = createUserRoute(route, markerPoint)

    for point in route:
        dumps(point, ensure_ascii=False)

    return render(request, "map.html", {
        'full_path': path,
        'user_route': dumps(route),
    })


# 운전자의 경로를 반환
def driverRoute(request):
    # 클러스터링 데이터
    startJSON = dumps({"lat": 37.39641804, "lon": 126.95858318, "name": "세경아파트후문[버스정류장]", }, ensure_ascii=False)
    viapoints = [
        dumps({"id": 2000091219, "lat": 37.39894570, "lon": 126.96849888, "name": "스마트베이(마을)[버스정류장]"},
              ensure_ascii=False),
        dumps({"id": 2000116823, "lat": 37.39627945, "lon": 126.97441508, "name": "한국교통안전공단안양검사소[버스정류장]"},
              ensure_ascii=False),
        dumps({"id": 2000104485, "lat": 37.40480608, "lon": 126.96552676, "name": "중촌마을.동안치매안심센터[버스정류장]"},
              ensure_ascii=False),
        dumps({"id": 1135886, "lat": 37.40100116, "lon": 126.97647032, "name": "인덕원역 4번출구"}, ensure_ascii=False)]

    endJSON = dumps({"lat": 37.49632607, "lon": 127.12345426, "name": "국립경찰병원", }, ensure_ascii=False)

    return render(request, "map.html", {
        'start': startJSON,
        'viapoints': dumps(viapoints),
        'end': endJSON
    })