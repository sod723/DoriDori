from django.shortcuts import render, redirect
from content.models import Content
from json import dumps, loads
import requests

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "appKey": "l7xx846db5f3bc1e48d29b7275a745d501c8" #my app key
}

url = "https://apis.openapi.sk.com/tmap/routes"

def map(request):
    user_info = userRoute()
    bus_info = driverRoute()

    # bus_route = bus_info['route']
    # via_points = bus_info['viapoints']
    
    return render(request, "map.html", {
        "user_info" : user_info,
        # "bus_route": bus_route, 
        # "viapoints": via_points #list
    })

# 위도 경도 => 근처 버스정류장 정보 return
# parameter : 클러스터링한 위도 경도(문자열)
def get_around_busstop(lat, lng):
    apiUrl = "https://apis.openapi.sk.com/tmap/pois/search/around?version=1&centerLon=" + lng + "&centerLat=" + lat +"&categories=버스정류장&page=1&count=1&radius=1&reqCoordType=WGS84GEO&resCoordType=WGS84GEO&multiPoint=N&sort=distance"
    
    response = requests.get(apiUrl, headers=headers)
    # 가장 가까운 버스정류장 정보
    busstop_info = loads(response.text)['searchPoiInfo']['pois']['poi'][0]

    return {
        'id' : busstop_info['id'],
        'lat' : busstop_info['noorLat'],
        'lon' : busstop_info['noorLon'],
        'name' : busstop_info['name']
    }

# API parameter JSON
def get_busroute_payload(start, viapoints, end):
    return {
        "startName": start['name'],
        "startX": start['lon'],
        "startY": start['lat'],
        "startTime": "201709121938",
        "endName": end['name'],
        "endX": end['lon'],
        "endY": end['lat'],
        "viaPoints": viapoints
    }

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
    viaPoins = []
    for elem in resultData:
        geometry = elem["geometry"]
        properties = elem["properties"]

        if(geometry["type"] == "LineString"):
            resultList.append(geometry["coordinates"])
        elif "viaPointId" in properties:
            viaPoins.append(geometry["coordinates"])
    
    # 경유지 경로를 구하는 경우 경로, 경유지(위도, 경도)반환
    if viaPoins:
        return {
            'path' : resultList,
            'viapoints' : viaPoins
        }
    else:
        return resultList
  
# 경로 구하기
def create_bus_route(payload):
    apiUrl = url + "/routeOptimization10?version=1"
    response = requests.post(apiUrl, json=payload, headers=headers)
    x = loads(response.text)

    return getPath(x['features'])

def get_pedestrian_routedata(start, end):
    payload = getRouteJSON(start, end)
    api_url = url + "/pedestrian?version=1&callback=function"
    response = requests.post(api_url, json=payload, headers=headers)
    response = loads(response.text)
    return response['features']

def dumps_data(data):
    for elem in data:
        dumps(elem, ensure_ascii=False)

    return dumps(data)

# user의 보행자 경로정보
def set_walking_data(points, dic):
    dic['points'] = points

    for i in range(0, 3, 2):
        response = get_pedestrian_routedata(points[i], points[i+1])
        dic['path'].append(getPath(response))
        dic['time'].append(response[0]['properties']['totalTime'])
        dic['distance'].append(response[0]['properties']['totalDistance'])

def set_bus_data(start, end, dic):
    start = {"lat": "37.39641804", "lon": "126.95858318", "name": "세경아파트후문[버스정류장]"} 
    viapoints = [
        {"viaPointId": "2000091219", "viaPointName": "스마트베이(마을)[버스정류장]", "viaY": "37.39894570", "viaX": "126.96849888"},
        {"viaPointId": "2000116823", "viaPointName": "한국교통안전공단안양검사소[버스정류장]", "viaY": "37.39627945", "viaX": "126.97441508"},
        {"viaPointId": "2000104485", "viaPointName": "중촌마을.동안치매안심센터[버스정류장]", "viaY": "37.40480608", "viaX": "126.96552676"},

        {"viaPointId": "2000178688", "viaPointName": "문정로데오거리입구[버스정류장]", "viaY": "37.49093773", "viaX": "127.11953810"},
        {"viaPointId": "2000087334", "viaPointName": "샛별어린이공원입구[버스정류장]", "viaY": "37.49768698", "viaX": "127.12114887"},
        {"viaPointId": "2000109544", "viaPointName": "가락2동극동아파트[버스정류장]", "viaY": "37.49535410", "viaX": "127.13128691"},
    ]
    end = {"lat": "37.50335308", "lon": "127.12639824", "name": "오금동현대아파트[버스정류장]"}

    # load = get_busroute_payload(start, viapoints, end)
    # bus_route = create_bus_route(load)

    # print(bus_route['viapoints'])
    # print(bus_route['path'])
# 사용자의 경로를 반환
def userRoute():
    user_data = {
        'walking' : {
            'points' : [],
            'path' : [],
            'time' : [],
            'distance' : []
        }
        ,
        'bus' : {
            'path' : [],
            'viaPoints' : [],
            'time' : [],
            'distance' : []
        }
    }
    # 출발지
    # 탑승지(클러스터링)
    # 하차지(클러스터링)
    # 목적지
    route = [{"lat": 37.39725123, "lon": 126.95650002, "name": "한가람신라아파트"},
             {"lat": 37.39641804, "lon": 126.95858318, "name": "세경아파트후문[버스정류장]"},
             {"lat": 37.49093773, "lon": 127.11953810, "name": "문정로데오거리입구[버스정류장]"},
             {"lat": 37.49632607, "lon": 127.12345426, "name": "국립경찰병원", }]
    
    set_walking_data(route, user_data['walking'])
    # print(get_around_busstop(str(37.39725123), str(126.95650002)))
    
    set_bus_data(route[1], route[2], user_data)
    # { 도보 정보 : 
    #   { 입력 지점(위도&경도) : [출발지, 탑승지, 하차지, 목적지]
    #     경로(위도&경도) : [[출발지-탑승지], [하차지-목적지]],
    #     시간 : [[출발지-탑승지], [하차지-목적지]],  
    #     거리 : [[출발지-탑승지], [하차지-목적지]]
    #   },
    #  차도 정보 : {
    #     경로(위도&경도) : [경로 ...],
    #     경유지(위도&경도) : [지점 ...],
    #     시간 : 시간,
    #     거리 : 거리
    #   }
    # }

    dumps_data(user_data['walking'])
    dumps_data(user_data['bus'])
    dumps_data(user_data)
    return dumps(user_data)

# 운전자의 경로를 반환
def driverRoute():
    driver_data = {
        'path': [],
        'viaPoints' : [],
        'time' : [],
        'distance' : []
    }

    # 클러스터링 데이터
    start = {"lat": "37.39641804", "lon": "126.95858318", "name": "세경아파트후문[버스정류장]"} 
    viapoints = [
        {"viaPointId": "2000091219", "viaPointName": "스마트베이(마을)[버스정류장]", "viaY": "37.39894570", "viaX": "126.96849888"},
        {"viaPointId": "2000116823", "viaPointName": "한국교통안전공단안양검사소[버스정류장]", "viaY": "37.39627945", "viaX": "126.97441508"},
        {"viaPointId": "2000104485", "viaPointName": "중촌마을.동안치매안심센터[버스정류장]", "viaY": "37.40480608", "viaX": "126.96552676"},

        {"viaPointId": "2000178688", "viaPointName": "문정로데오거리입구[버스정류장]", "viaY": "37.49093773", "viaX": "127.11953810"},
        {"viaPointId": "2000087334", "viaPointName": "샛별어린이공원입구[버스정류장]", "viaY": "37.49768698", "viaX": "127.12114887"},
        {"viaPointId": "2000109544", "viaPointName": "가락2동극동아파트[버스정류장]", "viaY": "37.49535410", "viaX": "127.13128691"},
    ]
    end = {"lat": "37.50335308", "lon": "127.12639824", "name": "오금동현대아파트[버스정류장]"}

    load = get_busroute_payload(start, viapoints, end)
    
    # { 경로 : [경로 ...],
    #   경유지정보 : [경유지 ...],
    #   경유지 : [경유지 ...],
    #   시간 : 시간,
    #   거리 : 거리
    # }
    for viapoint in viapoints:
        dumps(viapoint, ensure_ascii=False)
    
    bus_route = create_bus_route(load)
    driver_data['path'] = bus_route['path']
    return driver_data
