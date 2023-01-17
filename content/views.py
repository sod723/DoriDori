import geocoder
from folium import plugins
import folium
from haversine import haversine  # 거리측정
from django.shortcuts import render, redirect
from content.models import Content
from json import dumps
from json import loads
from urllib.parse import urlencode
from django.http.response import HttpResponse
import json, requests
from content.models import Content
from . import RouteSearch


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core import serializers

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

g = geocoder.ip('me')

def map(request):
    # user info return
    map = folium.Map(location=g.latlng, zoom_start=15, width='100%', height='100%', )
    plugins.LocateControl().add_to(map)
    plugins.Geocoder().add_to(map)

    # passenger_info = userRoute()
    # bus_info = driverRoute()
    #
    # passenger_route = passenger_info['route']
    # passenger_path = passenger_info['path']
    # bus_route = bus_info['route']
    # via_points = bus_info['viapoints']

    maps = map._repr_html_()  # 지도를 템플릿에 삽입하기위해 iframe이 있는 문자열로 반환 (folium)
    return render(request, "map.html", {
                                        'map': maps,
                                        'content' : Content,
                                        # "passenger_route": passenger_route,  # list
                                        # "passenger_path": passenger_path,
                                        # "bus_route": bus_route,
                                        # "viapoints": via_points  # list
                                        })

def getUsrLatLng(request):
    content = Content.objects.all()
    content_list = serializers.serialize('json', content)
    return HttpResponse(content_list, content_type="text/json=comment-filtered")


# 위도 경도 => 근처 버스정류장 정보 return
# parameter : 클러스터링한 위도 경도(문자열)
def get_around_busstop(lat, lng):
    apiUrl = "https://apis.openapi.sk.com/tmap/pois/search/around?version=1&centerLon=" + lng + "&centerLat=" + lat + "&categories=버스정류장&page=1&count=1&radius=1&reqCoordType=WGS84GEO&resCoordType=WGS84GEO&multiPoint=N&sort=distance"

    response = requests.get(apiUrl, headers=headers)
    # 가장 가까운 버스정류장 정보
    busstop_info = loads(response.text)['searchPoiInfo']['pois']['poi'][0]

    return {
        'id': busstop_info['id'],
        'lat': busstop_info['noorLat'],
        'lon': busstop_info['noorLon'],
        'name': busstop_info['name']
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
    resultPoins = []
    for elem in resultData:
        geometry = elem["geometry"]
        properties = elem["properties"]

        if (geometry["type"] == "LineString"):
            resultList.append(geometry["coordinates"])
        elif "viaPointId" in properties:
            resultPoins.append(geometry["coordinates"])

    print(resultPoins)
    return resultList


# 경로 구하기
def fetchRoute(option, routeType=""):
    apiUrl = url + routeType + "?version=1&callback=function"
    response = requests.post(apiUrl, json=option, headers=headers)
    x = loads(response.text)
    return getPath(x["features"])


# user의 보행자 경로
def createUserRoute(path, marker):
    resultData = []
    for i in range(0, 3, 2):
        load = getRouteJSON(path[i], path[i + 1])
        resultData.append(fetchRoute(load, "/pedestrian"))

    return resultData


def create_bus_route(payload):
    resultData = []
    apiUrl = url + "/routeOptimization10?version=1"
    response = requests.post(apiUrl, json=payload, headers=headers)
    x = loads(response.text)

    return getPath(x["features"])


# 사용자의 경로를 반환
def userRoute():
    markerPoint = []

    # 출발지
    # 탑승지(클러스터링)
    # 하차지(클러스터링)
    # 목적지
    route = [{"lat": 37.39725123, "lon": 126.95650002, "name": "한가람신라아파트"},
             {"lat": 37.39641804, "lon": 126.95858318, "name": "세경아파트후문[버스정류장]"},
             {"lat": 37.49093773, "lon": 127.11953810, "name": "문정로데오거리입구[버스정류장]"},
             {"lat": 37.49632607, "lon": 127.12345426, "name": "국립경찰병원", }]

    # print(get_around_busstop(str(37.39725123), str(126.95650002)))

    path = createUserRoute(route, markerPoint)

    for point in route:
        dumps(point, ensure_ascii=False)

    # { 도보 정보 :
    #   { 입력 지점(위도&경도) : [출발지, 탑승지, 하차지, 목적지]
    #     경로(위도&경도) : [[출발지-탑승지], [하차지-목적지]],
    #     시간 : [[출발지-탑승지], [하차지-목적지]],
    #     거리 : [[출발지-탑승지], [하차지-목적지]]
    #   },
    #  차도 정보 : {
    #     경로(위도&경도) : [경로 ...],
    #     시간 : 시간,
    #     거리 : 거리
    #   }
    # }

    return {
        'path': path,
        'route': dumps(route),
    }


# 운전자의 경로를 반환
def driverRoute():
    # 클러스터링 데이터
    start = {"lat": "37.39641804", "lon": "126.95858318", "name": "세경아파트후문[버스정류장]"}
    viapoints = [
        {"viaPointId": "2000091219", "viaPointName": "스마트베이(마을)[버스정류장]", "viaY": "37.39894570", "viaX": "126.96849888"},
        {"viaPointId": "2000116823", "viaPointName": "한국교통안전공단안양검사소[버스정류장]", "viaY": "37.39627945",
         "viaX": "126.97441508"},
        {"viaPointId": "2000104485", "viaPointName": "중촌마을.동안치매안심센터[버스정류장]", "viaY": "37.40480608",
         "viaX": "126.96552676"},

        {"viaPointId": "2000178688", "viaPointName": "문정로데오거리입구[버스정류장]", "viaY": "37.49093773", "viaX": "127.11953810"},
        {"viaPointId": "2000087334", "viaPointName": "샛별어린이공원입구[버스정류장]", "viaY": "37.49768698", "viaX": "127.12114887"},
        {"viaPointId": "2000109544", "viaPointName": "가락2동극동아파트[버스정류장]", "viaY": "37.49535410", "viaX": "127.13128691"},
    ]
    end = {"lat": "37.50335308", "lon": "127.12639824", "name": "오금동현대아파트[버스정류장]"}

    load = get_busroute_payload(start, viapoints, end)

    # { 경로 : [경로 ...],
    #   경유지 : [경유지 ...]
    # }
    for viapoint in viapoints:
        dumps(viapoint, ensure_ascii=False)

    bus_route = create_bus_route(load)
    return {
        'route': bus_route,
        'viapoints': dumps(viapoints)
    }


###########################################################
def saferoute(request):
    SafePath = []
    totalDistance = 0;

    startx = request.POST.get('startX')
    starty = request.POST.get('startY')
    endx = request.POST.get('endX')
    endy = request.POST.get('endY')
    start_coordinate = [starty, startx]
    end_coordinate = [endy, endx]

    # type : list(Hmap), grid(Hex), list
    Hexlist, grid, path, TileValue_map = RouteSearch.startSetting(start_coordinate, end_coordinate)
    Before_Hex = path[0]
    increase = [0, 0]  # q,r 증가율
    count = 1

    for idx, HexPoint in enumerate(path):
        if Before_Hex is not HexPoint:
            # 첫 노드 증가율 기록 - 두번째 노드
            if increase[0] == 0 and increase[1] == 0:
                x = int(HexPoint[0]) - int(Before_Hex[0])
                y = int(HexPoint[1]) - int(Before_Hex[1])
                increase = [x, y]
                Before_Hex = HexPoint

                continue
            # 증가율 비교
            else:
                x = int(HexPoint[0]) - int(Before_Hex[0])
                y = int(HexPoint[1]) - int(Before_Hex[1])
                if increase[0] == x and increase[1] == y:
                    Before_Hex = HexPoint
                    continue
                else:
                    increase = [x, y]

        # print(count,' ',HexPoint)
        count += 1
        Before_Hex = HexPoint
        geo_center = grid.hex_center(HexPoint)
        SafePath.append([geo_center.y, geo_center.x])

        if len(SafePath) > 1:
            totalDistance += haversine(SafePath[len(SafePath) - 2], SafePath[len(SafePath) - 1])
        increase = [0, 0]

    # 마지막 노드 추가
    geo_center = grid.hex_center(path[-1])
    SafePath.append([geo_center.y, geo_center.x])
    totalDistance += haversine(SafePath[len(SafePath) - 2], SafePath[len(SafePath) - 1])

    print('토탈 거리:', totalDistance)
    soc = 1 / 16
    totalTime = totalDistance // soc
    print('토탈 시간', totalTime)
    return HttpResponse(json.dumps({'result': SafePath, 'totalDistance': totalDistance, 'totalTime': totalTime}),
                        content_type="application/json");


def PathFinder(request):
    shortData = []
    SafePath = []
    SPoint = []

    # ------------------------- 최단 루트 (SPoint) -----------------------------------------
    start_coordinate = getLatLng(request.POST.get('StartAddr'))
    end_coordinate = getLatLng(request.POST.get('EndAddr'))

    shortData = request.POST.get('shortestRoute').split(",")

    for i in shortData:
        if (shortData.index(i) % 2 == 0):
            lat = i;  # 위도
            lon = shortData[(shortData.index(i)) + 1]  # 경도
            point = [float(lat), float(lon)]
            SPoint.append(point)

    # -----------------------------맵핑-----------------------------------------
    map = folium.Map(location=start_coordinate, zoom_start=15, width='100%', height='100%', )

    folium.PolyLine(locations=SPoint, weight=4, color='red').add_to(map)

    folium.Marker(
        location=start_coordinate,
        popup=request.POST.get('StartAddr'),
        icon=folium.Icon(color="red"),
    ).add_to(map)

    folium.Marker(
        location=end_coordinate,
        popup=request.POST.get('EndAddr'),
        icon=folium.Icon(color="red"),
    ).add_to(map)

    plugins.LocateControl().add_to(map)

    # ---------------------------안전 루트--------------------------------------
    # type : list(Hmap), grid(Hex), list
    Hexlist, grid, path = RouteSearch.startSetting(start_coordinate, end_coordinate)
    Before_Hex = path[0]
    increase = [0, 0]  # q,r 증가율
    count = 1

    for idx, HexPoint in enumerate(path):
        if Before_Hex is not HexPoint:
            # 첫 노드 증가율 기록 - 두번째 노드
            if increase[0] == 0 and increase[1] == 0:
                x = int(HexPoint[0]) - int(Before_Hex[0])
                y = int(HexPoint[1]) - int(Before_Hex[1])
                increase = [x, y]
                Before_Hex = HexPoint

                continue
            # 증가율 비교
            else:
                x = int(HexPoint[0]) - int(Before_Hex[0])
                y = int(HexPoint[1]) - int(Before_Hex[1])
                if increase[0] == x and increase[1] == y:
                    Before_Hex = HexPoint
                    continue
                else:
                    increase = [x, y]

        print(count, ' ', HexPoint)
        count += 1
        Before_Hex = HexPoint
        geo_center = grid.hex_center(HexPoint)
        SafePath.append([geo_center.y, geo_center.x])

        increase = [0, 0]
    folium.PolyLine(locations=SafePath, weight=4, color='blue').add_to(map)

    maps = map._repr_html_()  # 지도를 템플릿에 삽입하기위해 iframe이 있는 문자열로 반환 (folium)

    return render(request, '../templates/home.html', {'map': maps})


def GetSpotPoint(request):
    start_coordinate = getLatLng(request.POST.get('StartAddr'))
    end_coordinate = getLatLng(request.POST.get('EndAddr'))
    if request.user.is_authenticated:
        id=request.user.id
        content=Content(user_id=id,s_latitude=start_coordinate[0],s_longitude=start_coordinate[1],e_latitude=end_coordinate[0],e_longitude=end_coordinate[1]).save()
        context = {'startaddr': start_coordinate, 'endaddr': end_coordinate}
    return HttpResponse(json.dumps(context), content_type='application/json')


def getLatLng(addr):
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + addr
    headers = {"Authorization": "KakaoAK 894cfd738b31d10baba806317025d155"}
    result = json.loads(str(requests.get(url, headers=headers).text))
    match_first = result['documents'][0]['address']

    return float(match_first['y']), float(match_first['x'])