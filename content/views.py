import math

import geocoder
from folium import plugins
import folium
from haversine import haversine  # 거리측정
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from content.models import Content
from json import dumps
from json import loads
from urllib.parse import urlencode
from django.http.response import HttpResponse
import json, requests
from content.models import Content
from content.models import Bus_Stop
from content.models import User_Stop
from sklearn.cluster import KMeans
from . import RouteSearch
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core import serializers

start=0
end=0
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "appKey": "l7xxa21398bdba4947eba835e6c00ec9ffaf"  # my app key
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

driver_data = {
    'path': [],
    'viaPoints': [],
    'time': [],
    'distance': []
}

g = geocoder.ip('me')


def map(request):
    try:
        userid=request.user.id
        user=Content.objects.get(id=userid)
    except Content.DoesNotExist:
        userid = None
    # getDriverRoute(userid)

    # user info return
    map = folium.Map(location=g.latlng, zoom_start=15, width='100%', height='100%', )
    plugins.LocateControl().add_to(map)
    plugins.Geocoder().add_to(map)

    maps = map._repr_html_()  # 지도를 템플릿에 삽입하기위해 iframe이 있는 문자열로 반환 (folium)

    return render(request, "map.html", {
        'map': maps,
        'content': Content,
    })

def SetStartEnd(bus_group):
    print(bus_group)
    print(set)
    c=0
    for bus1 in Bus_Stop.objects.filter(bus_group=bus_group,start_or_end=0):
        for bus2 in Bus_Stop.objects.filter(bus_group=bus_group,start_or_end=1):
            print(bus2)
            temp = math.sqrt(math.pow(bus1.latitude-bus2.latitude, 2) + math.pow(bus1.longitude-bus2.longitude, 2))
            print(temp)
            if temp>c:
                c=temp
                start=bus1
                end=bus2
                print(end)

    start.first=1
    start.save()
    end.first=1
    end.save()
    return start,end

def ClusterExist(userid):
    if Content.objects.filter(id=userid,s_busid='').exists():
        return 1
    else :
        return 0

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


# def get_location_info(lat, lon):

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
    viaPoints = []
    times = []
    distance = []

    for elem in resultData:
        geometry = elem["geometry"]
        properties = elem["properties"]

            
        if(geometry["type"] == "LineString"):
            resultList.append(geometry["coordinates"])
            times.append(properties['time'])
            distance.append(properties['distance'])
        # 경유지        
        elif (geometry["type"] == "Point") and ("viaPointId" in properties):
            viaPoints.append({'lat' : geometry["coordinates"][1], 'lon':geometry["coordinates"][0], 'name': properties["viaPointName"][4:]})
    
    # 경유지 경로를 구하는 경우 경로, 경유지(위도, 경도)반환
    if viaPoints:
        return {
            'path' : resultList,
            'viapoints' : viaPoints[1:-1],
            'times': times,
            'distance': distance
        }
    else:
        return resultList
  

# 경로 구하기

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
    print('경로정보')

    for i in range(0, 3, 2):
        response = get_pedestrian_routedata(points[i], points[i + 1])
        dic['path'].append(getPath(response))
        dic['time'].append(response[0]['properties']['totalTime'])
        dic['distance'].append(response[0]['properties']['totalDistance'])


def slicing_list(start, end, data):
    path_list = data['path']
    coordi_list = data['viaPoints']
    time_list = data['time']
    distacne_list = data['distance']

    print('via')
    print(coordi_list)

    start_idx = coordi_list.index(start)
    end_idx = coordi_list.index(end)

    return {
        'path': path_list[start_idx:end_idx],
        'viapoints': coordi_list[start_idx + 1:end_idx],
        'times': time_list[start_idx:end_idx],
        'distance': distacne_list[start_idx:end_idx]
    }

def set_bus_data(start, end, dic):
    user_bus_info = slicing_list(start, end, driver_data)
    print(user_bus_info)

    dic['path'] = user_bus_info['path']
    dic['viaPoints'] = user_bus_info['viapoints']
    dic['time'] = user_bus_info['times']
    dic['distance'] = user_bus_info['distance']


# 사용자의 경로를 반환
@csrf_exempt
def userRoute(request):
    user_data = {
        'walking': {
            'points': [],
            'path': [],
            'time': [],
            'distance': []
        },
        'bus': {
            'path': [],
            'viaPoints': [],
            'time': [],
            'distance': []
        }
    }
    try:
        user=Content.objects.get(id=request.user.id)
        startbus=Bus_Stop.objects.get(id=user.s_busid)
        endbus = Bus_Stop.objects.get(id=user.e_busid)
        print(SetStartEnd(user.bus_group))
    except Content.DoesNotExist:
        return HttpResponse('/user/login')
    # 출발지
    # 탑승지(클러스터링)
    # 하차지(클러스터링)
    # 목적지
    route = [{"lat": user.s_latitude, "lon": user.s_longitude, "name": "출발지"},
             {"lat": startbus.latitude, "lon": startbus.longitude, "name": startbus.bus_name},
             {"lat": endbus.latitude, "lon": endbus.longitude, "name": endbus.bus_name},
             {"lat": user.e_latitude, "lon": user.e_longitude, "name": "목적지"}]


    set_walking_data(route, user_data['walking'])

    set_bus_data(route[1], route[2], user_data['bus'])
    # { 도보 정보 :
    #   { 입력 지점(위도&경도) : [출발지, 탑승지, 하차지, 목적지]
    #     경로(위도&경도) : [[출발지-탑승지], [하차지-목적지]], (경로 그리기 좌표)
    #     시간 : [[출발지-탑승지], [하차지-목적지]],
    #     거리 : [[출발지-탑승지], [하차지-목적지]]
    #   },
    #  차도 정보 : {
    #     경로(위도&경도) : [경로 ...], (경로 그리기 좌표)
    #     경유지(위도&경도) : [지점 ...],
    #     시간 : 시간,
    #     거리 : 거리
    #   }
    # }
    return HttpResponse(dumps(user_data))


def get_driver_route_data(payload):
    apiUrl = url + "/routeOptimization10?version=1"
    response = requests.post(apiUrl, json=payload, headers=headers)
    return loads(response.text)


# data: API JSON data
def set_driver_data(start, viapoints, end, dic):

    load = get_busroute_payload(start, viapoints, end)
    response = get_driver_route_data(load)
    # print(response)
    route_data = getPath(response['features'])
    
    dic['path'] = route_data['path']
    dic['viaPoints'] = route_data['viapoints']
    dic['time'] = route_data['times']
    dic['distance'] = route_data['distance']

# 운전자의 경로를 반환
@csrf_exempt
def driverRoute(request):
    return HttpResponse(dumps(driver_data))

def getDriverRoute(userid):
    if not userid:
        return HttpResponse("Please login")

    user=Content.objects.get(id=userid)
    print('getdriver')
    first_end=SetStartEnd(user.bus_group)
    print('퍼스트엔드')
    print(first_end)
    # 클러스터링 데이터
    start = {"lat": str(first_end[0].latitude), "lon": str(first_end[0].longitude), "name": first_end[0].bus_name}
    print(start)
    viapoints = [
        {"viaPointId": str(bus.id), "viaPointName": bus.bus_name, "viaY": str(bus.latitude),
         "viaX": str(bus.longitude)} for bus in Bus_Stop.objects.filter(bus_group=0).all()]
    print(viapoints)
    end = {"lat": str(first_end[1].latitude), "lon": str(first_end[1].longitude), "name": first_end[1].bus_name}
    print(end)
    set_driver_data(start, viapoints, end, driver_data)
    # {
    #   경로 : [경로 ...], (경로 그리기)
    #   경유지 : [경유지 ...],
    #   시간 : 시간,
    #   거리 : 거리
    # }
    return driver_data
###########################################################
def saferoute(request):
    SafePath = []
    totalDistance = 0

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
    code=request.POST.get('code')
    if request.user.is_authenticated:
        userid=request.user.id
        if Content.objects.filter(user_id=userid).exists():
            content=Content.objects.get(user_id=userid)
            content.s_latitude=start_coordinate[0]
            content.s_longitude=start_coordinate[1]
            content.e_latitude=end_coordinate[0]
            content.e_longitude=end_coordinate[1]
            content.sigungucode=code
            content.save()
            print('버스그룹')

        else:
            content=Content(user_id=userid,s_latitude=start_coordinate[0],s_longitude=start_coordinate[1],e_latitude=end_coordinate[0],e_longitude=end_coordinate[1],sigungucode=code
                            ).save()

        if ClusterExist(userid) == 1:
            first_start_clustering(userid)
            first_end_clustering(userid)
        else:
            print('else')
            start_clustering(userid)
            end_clustering(userid)

        context = {'startaddr': start_coordinate, 'endaddr': end_coordinate}
        return HttpResponse(json.dumps(context), content_type='application/json')
    else:
        print("heelo")
        #회원가입창으로 돌려야하는기능구현해야함
        return HttpResponse('/user/login')



def getLatLng(addr):
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + addr
    headers = {"Authorization": "KakaoAK 894cfd738b31d10baba806317025d155"}
    result = json.loads(str(requests.get(url, headers=headers).text))
    match_first = result['documents'][0]['address']
    return float(match_first['y']), float(match_first['x'])

def start_clustering(user_id):
    user_content=Content.objects.get(user_id=user_id)
    rows = Content.objects.filter(sigungucode=user_content.sigungucode,service=0).count()
    cols = 2
    index=0
    arr = [[0 for j in range(cols)] for i in range(rows)]
    print('버스그룹')
    tempCon=Content.objects.filter(sigungucode=user_content.sigungucode,service=0).first()
    print(tempCon)
    print(tempCon.bus_group)
    bus_group=Bus_Stop.objects.filter(start_or_end=0,service=0,bus_group=tempCon.bus_group).first()
    print(bus_group)
    bus_group=bus_group.bus_group
    bus_group=int(float(bus_group))
    print('버스그룹')
    print(bus_group)

    for people in Content.objects.filter(sigungucode=user_content.sigungucode).all():
        print(people.user_id)
        arr[index][0]=people.s_longitude
        arr[index][1]=people.s_latitude
        index+=1
    km = KMeans(n_clusters=4, init='k-means++', random_state=10)
    start_km=km.fit_predict(arr)
    for i in range(4):
        center_x=km.cluster_centers_[i][0]
        center_y = km.cluster_centers_[i][1]
        a=str(center_x)
        b=str(center_y)
        bus=get_around_busstop(b,a)
        start = Bus_Stop.objects.get(id=4 * bus_group + i + 1)
        print(start)
        start.longitude = bus['lon']
        start.latitude = bus['lat']
        start.bus_name = bus['name']
        start.save()
    index=0;
    print(start_km)
    for people in Content.objects.filter(sigungucode=user_content.sigungucode).all():
        start=Bus_Stop.objects.get(id=start_km[index]+4*bus_group+1)
        people.s_busid=start.id
        people.bus_group=bus_group
        people.save()
        user_stop=User_Stop.objects.get(user_id=people.user_id)
        user_stop.start_bus_id=start.id
        user_stop.start_bus_name = start.bus_name
        user_stop.bus_group = bus_group
        user_stop.save()
        index+=1
    print(km.cluster_centers_)
    return start_km

def end_clustering(user_id):
    user_content=Content.objects.get(user_id=user_id)
    rows = Content.objects.filter(sigungucode=user_content.sigungucode,service=0).count()
    cols = 2
    index=0
    arr = [[0 for j in range(cols)] for i in range(rows)]
    tempCon=Content.objects.filter(sigungucode=user_content.sigungucode,service=0).first()
    bus_group=Bus_Stop.objects.filter(start_or_end=1,service=0,bus_group=tempCon.bus_group).first()
    bus_group=bus_group.bus_group
    bus_group=int(float(bus_group))
    for people in Content.objects.filter(sigungucode=user_content.sigungucode,service=0).all():
        print(people.user_id)
        arr[index][0]=people.e_longitude
        arr[index][1]=people.e_latitude
        index+=1
    km = KMeans(n_clusters=4, init='k-means++', random_state=10)
    end_km=km.fit_predict(arr)
    for i in range(4):
        center_x=km.cluster_centers_[i][0]
        center_y = km.cluster_centers_[i][1]
        a=str(center_x)
        b=str(center_y)
        bus=get_around_busstop(b,a)
        end=Bus_Stop.objects.get(id=4*bus_group+i+5)
        end.longitude=bus['lon']
        end.latitude=bus['lat']
        end.bus_name=bus['name']
        end.save()
    index=0;
    print(end_km)
    for people in Content.objects.filter(sigungucode=user_content.sigungucode,service=0).all():
        end=Bus_Stop.objects.get(id=end_km[index]+4*bus_group+5)
        print('end id')
        print(end.id)
        user_stop = User_Stop.objects.get(user_id=people.user_id)
        people.e_busid=end.id
        people.bus_group=bus_group
        people.save()
        user_stop.end_bus_id = end.id
        user_stop.end_bus_name = end.bus_name
        user_stop.bus_group = bus_group
        user_stop.save()
        index+=1
    print(km.cluster_centers_)
    return end_km



def first_start_clustering(user_id):
    user_content=Content.objects.get(user_id=user_id)
    rows = Content.objects.filter(sigungucode=user_content.sigungucode,service=0).count()
    cols = 2
    index=0
    arr = [[0 for j in range(cols)] for i in range(rows)]
    bus_group=Bus_Stop.objects.filter(start_or_end=0).count()/4
    bus_group=int(bus_group)
    for people in Content.objects.filter(sigungucode=user_content.sigungucode,service=0).all():
        print(people.user_id)
        arr[index][0]=people.s_longitude
        arr[index][1]=people.s_latitude
        index+=1
    km = KMeans(n_clusters=4, init='k-means++', random_state=10)
    start_km=km.fit_predict(arr)
    for i in range(4):
        center_x=km.cluster_centers_[i][0]
        center_y = km.cluster_centers_[i][1]
        a=str(center_x)
        b=str(center_y)
        bus=get_around_busstop(b,a)
        start=Bus_Stop(bus_group=bus_group,longitude=bus['lon'],latitude=bus['lat'],bus_name=bus['name'],start_or_end=0).save()
    index=0;
    print(start_km)
    for people in Content.objects.filter(sigungucode=user_content.sigungucode,service=0).all():
        start=Bus_Stop.objects.get(id=start_km[index]+4*bus_group+1)

        people.s_busid=start.id
        people.bus_group=bus_group
        people.save()
        User_Stop(user_id=people.user_id,start_bus_id=start.id,start_bus_name=start.bus_name).save()
        index+=1
    print(km.cluster_centers_)
    return start_km

def first_end_clustering(user_id):
    user_content=Content.objects.get(user_id=user_id)
    rows = Content.objects.filter(sigungucode=user_content.sigungucode,service=0).count()
    cols = 2
    index=0
    arr = [[0 for j in range(cols)] for i in range(rows)]
    bus_group=Bus_Stop.objects.filter(start_or_end=1).count()/4
    bus_group = int(bus_group)
    for people in Content.objects.filter(sigungucode=user_content.sigungucode,service=0).all():
        print(people.user_id)
        arr[index][0]=people.e_longitude
        arr[index][1]=people.e_latitude
        index+=1
    km = KMeans(n_clusters=4, init='k-means++', random_state=10)
    end_km=km.fit_predict(arr)
    for i in range(4):
        center_x=km.cluster_centers_[i][0]
        center_y = km.cluster_centers_[i][1]
        a=str(center_x)
        b=str(center_y)
        bus=get_around_busstop(b,a)
        end=Bus_Stop(bus_group=bus_group,longitude=bus['lon'],latitude=bus['lat'],bus_name=bus['name'],start_or_end=1).save()
    index=0;
    print(end_km)
    for people in Content.objects.filter(sigungucode=user_content.sigungucode,service=0).all():
        end=Bus_Stop.objects.get(id=end_km[index]+4*bus_group+1)
        people.e_busid=end.id
        people.bus_group=bus_group
        people.save()
        user_stop = User_Stop.objects.get(user_id=people.user_id)
        user_stop.end_bus_id = end.id
        user_stop.end_bus_name = end.bus_name
        user_stop.bus_group = bus_group
        user_stop.save()
        index+=1
    print(km.cluster_centers_)
    return end_km

