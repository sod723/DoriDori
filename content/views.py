import math
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
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core import serializers

start = 0
end = 0
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "appKey": "l7xx0540ab9b13084d30b44950c8a1b7f405"  # my app key
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


def map(request):
    try:
        userid = request.user.id
        user = Content.objects.get(id=userid)
    except Content.DoesNotExist:
        userid = None

    return render(request, "map.html", {
        'content': Content,
        'userid': userid
    })


def SetStartEnd(bus_group):
    print(bus_group)
    print(set)
    c = 0
    for bus1 in Bus_Stop.objects.filter(bus_group=bus_group, start_or_end=0):
        for bus2 in Bus_Stop.objects.filter(bus_group=bus_group, start_or_end=1):
            print(bus2)
            temp = math.sqrt(math.pow(bus1.latitude - bus2.latitude, 2) + math.pow(bus1.longitude - bus2.longitude, 2))
            print(temp)
            if temp > c:
                c = temp
                start = bus1
                end = bus2
                print(end)

    start.first = 1
    start.save()
    end.first = 1
    end.save()
    return start, end


def ClusterExist(userid):
    if Content.objects.filter(user_id=userid, s_busid='').exists():
        content = Content.objects.get(user_id=userid)
        if Content.objects.filter(sigungucode=content.sigungucode, service=0, bus_group='').count() > 1:
            return 2  ##클러스터가 아예처음
        elif Content.objects.filter(sigungucode=content.sigungucode, service=0, ).count() > 3:
            return 1
        else:
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
        "searchOption": "2",
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

        if (geometry["type"] == "LineString"):
            resultList.append(geometry["coordinates"])
            times.append(int(properties['distance']) // 16)
            distance.append(int(properties['distance']))
        # 경유지        
        elif (geometry["type"] == "Point") and ("viaPointId" in properties):
            viaPoints.append({'lat': geometry["coordinates"][1], 'lon': geometry["coordinates"][0],
                              'name': properties["viaPointName"][4:]})

    # 경유지 경로를 구하는 경우 경로, 경유지(위도, 경도)반환
    if viaPoints:
        return {
            'path': resultList,
            'viapoints': viaPoints,
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
        dic['time'].append(int(response[0]['properties']['totalTime']))
        dic['distance'].append(int(response[0]['properties']['totalDistance']))


def slicing_list(start, end, data):
    path_list = data['path']
    coordi_list = data['viaPoints']
    time_list = data['time']
    distacne_list = data['distance']

    print('via')
    print(coordi_list)
    print(time_list)
    print(distacne_list)

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

    dic['path'] = user_bus_info['path']
    dic['viaPoints'] = user_bus_info['viapoints']
    print('s via')
    print(user_bus_info['viapoints'])
    print(user_bus_info['times'])
    print(user_bus_info['distance'])
    dic['time'] = user_bus_info['times']
    dic['distance'] = user_bus_info['distance']


# 사용자의 경로를 반환
@csrf_exempt
def userRoute(userid):
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
        user = Content.objects.get(id=userid)
        startbus = Bus_Stop.objects.get(id=user.s_busid)
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
def driverRoute():
    return HttpResponse(dumps(driver_data))


def getDriverRoute(userid):
    if not userid:
        return HttpResponse("Please login")

    user = Content.objects.get(id=userid)
    print('getdriver')
    first_end = SetStartEnd(user.bus_group)
    print('퍼스트엔드')
    print(first_end)
    # 클러스터링 데이터
    start = {"lat": str(first_end[0].latitude), "lon": str(first_end[0].longitude), "name": first_end[0].bus_name}
    print(start)
    viapoints = []
    end = {"lat": str(first_end[1].latitude), "lon": str(first_end[1].longitude), "name": first_end[1].bus_name}
    print(end)

    for bus in Bus_Stop.objects.filter(bus_group=user.bus_group).all():
        if start["name"] != bus.bus_name and end["name"] != bus.bus_name:
            viapoints.append({"viaPointId": str(bus.id), "viaPointName": bus.bus_name, "viaY": str(bus.latitude),
                              "viaX": str(bus.longitude)})
    print(viapoints)

    set_driver_data(start, viapoints, end, driver_data)
    # {
    #   경로 : [경로 ...], (경로 그리기)
    #   경유지 : [경유지 ...],
    #   시간 : 시간,
    #   거리 : 거리
    # }
    return driver_data


@csrf_exempt
def getRoute(request):
    try:
        user_type = request.user.first_name
        userid = request.user.id
    except AttributeError:
        user_type = "none"
        return HttpResponse("/user/login")

    getDriverRoute(userid)
    if user_type == "passenger":
        return userRoute(userid)
    else:
        return driverRoute()


def GetSpotPoint(request):
    start_coordinate = getLatLng(request.POST.get('StartAddr'))
    end_coordinate = getLatLng(request.POST.get('EndAddr'))
    code = request.POST.get('code')
    if request.user.is_authenticated:
        userid = request.user.id
        if Content.objects.filter(user_id=userid).exists():
            content = Content.objects.get(user_id=userid)

            content.s_latitude = start_coordinate[0]
            content.s_longitude = start_coordinate[1]
            content.e_latitude = end_coordinate[0]
            content.e_longitude = end_coordinate[1]
            content.sigungucode = code
            content.bus_group = ''
            content.s_busid = ''
            content.e_busid = ''
            if User_Stop.objects.filter(user_id=userid).exists():
                stop = User_Stop.objects.filter(user_id=userid)
                stop.delete()
            content.save()


        else:
            content = Content(user_id=userid, s_latitude=start_coordinate[0], s_longitude=start_coordinate[1],
                              e_latitude=end_coordinate[0], e_longitude=end_coordinate[1], sigungucode=code
                              ).save()

        print(ClusterExist(userid))
        if ClusterExist(userid) == 2:
            first_start_clustering(userid)
            first_end_clustering(userid)
        else:
            start_clustering(userid)
            end_clustering(userid)

        context = {'startaddr': start_coordinate, 'endaddr': end_coordinate}
        return HttpResponse(json.dumps(context), content_type='application/json')
    else:
        return HttpResponse('/user/login')


def getLatLng(addr):
    url = 'https://dapi.kakao.com/v2/local/search/address.json?query=' + addr
    headers = {"Authorization": "KakaoAK 894cfd738b31d10baba806317025d155"}
    result = json.loads(str(requests.get(url, headers=headers).text))
    match_first = result['documents'][0]['address']
    return float(match_first['y']), float(match_first['x'])


def start_clustering(user_id):
    print('스타트클러스터링')
    user_content = Content.objects.get(user_id=user_id)
    rows = Content.objects.filter(sigungucode=user_content.sigungucode, service=0).count()
    cols = 2
    index = 0
    arr = [[0 for j in range(cols)] for i in range(rows)]

    tempCon = Content.objects.filter(sigungucode=user_content.sigungucode, service=0).first()

    bus_group = Bus_Stop.objects.filter(start_or_end=0, service=0, bus_group=tempCon.bus_group).first()

    bus_group = bus_group.bus_group
    bus_group = int(float(bus_group))

    for people in Content.objects.filter(sigungucode=user_content.sigungucode).all():
        arr[index][0] = people.s_longitude
        arr[index][1] = people.s_latitude
        index += 1
    km = KMeans(n_clusters=4, init='k-means++', random_state=10)
    start_km = km.fit_predict(arr)
    for i in range(4):
        center_x = km.cluster_centers_[i][0]
        center_y = km.cluster_centers_[i][1]
        a = str(center_x)
        b = str(center_y)
        bus = get_around_busstop(b, a)
        start = Bus_Stop.objects.get(id=8 * bus_group + i + 1)

        start.longitude = bus['lon']
        start.latitude = bus['lat']
        start.bus_name = bus['name']
        start.save()
    index = 0;

    for people in Content.objects.filter(sigungucode=user_content.sigungucode).all():
        start = Bus_Stop.objects.get(id=start_km[index] + 8 * bus_group + 1)
        print(people.user_id)
        people.s_busid = start.id
        people.bus_group = bus_group
        people.save()
        if User_Stop.objects.filter(user_id=people.user_id).exists():
            user_stop = User_Stop.objects.get(user_id=people.user_id)
            user_stop.start_bus_id = start.id
            user_stop.start_bus_name = start.bus_name
            user_stop.bus_group = bus_group
            user_stop.save()
        else:
            User_Stop(user_id=people.user_id, start_bus_id=start.id, start_bus_name=start.bus_name,
                      bus_group=bus_group).save()
        index += 1

    return start_km


def end_clustering(user_id):
    user_content = Content.objects.get(user_id=user_id)
    rows = Content.objects.filter(sigungucode=user_content.sigungucode, service=0).count()
    cols = 2
    index = 0
    arr = [[0 for j in range(cols)] for i in range(rows)]
    tempCon = Content.objects.filter(sigungucode=user_content.sigungucode, service=0).first()
    bus_group = Bus_Stop.objects.filter(start_or_end=1, service=0, bus_group=tempCon.bus_group).first()
    bus_group = bus_group.bus_group
    bus_group = int(float(bus_group))
    for people in Content.objects.filter(sigungucode=user_content.sigungucode, service=0).all():
        arr[index][0] = people.e_longitude
        arr[index][1] = people.e_latitude
        index += 1
    km = KMeans(n_clusters=4, init='k-means++', random_state=10)
    end_km = km.fit_predict(arr)
    for i in range(4):
        center_x = km.cluster_centers_[i][0]
        center_y = km.cluster_centers_[i][1]
        a = str(center_x)
        b = str(center_y)
        bus = get_around_busstop(b, a)
        end = Bus_Stop.objects.get(id=8 * bus_group + i + 5)
        end.longitude = bus['lon']
        end.latitude = bus['lat']
        end.bus_name = bus['name']
        end.save()
    index = 0;

    for people in Content.objects.filter(sigungucode=user_content.sigungucode, service=0).all():
        end = Bus_Stop.objects.get(id=end_km[index] + 8 * bus_group + 5)

        people.e_busid = end.id
        people.bus_group = bus_group
        people.save()
        if User_Stop.objects.filter(user_id=people.user_id).exists():
            user_stop = User_Stop.objects.get(user_id=people.user_id)
            user_stop.end_bus_id = end.id
            user_stop.end_bus_name = end.bus_name
            user_stop.bus_group = bus_group
            user_stop.save()
        else:
            User_Stop(user_id=people.user_id, end_bus_id=end.id, end_bus_name=end.bus_name,
                      bus_group=bus_group).save()
        index += 1

    return end_km


def first_start_clustering(user_id):
    print('퍼스트스타트클러스터링')
    user_content = Content.objects.get(user_id=user_id)
    rows = Content.objects.filter(sigungucode=user_content.sigungucode, service=0).count()
    cols = 2
    index = 0
    arr = [[0 for j in range(cols)] for i in range(rows)]
    if Content.objects.filter(sigungucode=user_content.sigungucode, bus_group='').exists():
        bus_group = Bus_Stop.objects.filter(start_or_end=0).count() / 4
    else:
        bus_group = Content.objects.filter(sigungucode=user_content.sigungucode).first().bus_group
    bus_group = int(bus_group)

    for people in Content.objects.filter(sigungucode=user_content.sigungucode, service=0).all():
        arr[index][0] = people.s_longitude
        arr[index][1] = people.s_latitude
        index += 1
    km = KMeans(n_clusters=4, init='k-means++', random_state=10)
    start_km = km.fit_predict(arr)
    for i in range(4):
        center_x = km.cluster_centers_[i][0]
        center_y = km.cluster_centers_[i][1]
        a = str(center_x)
        b = str(center_y)
        bus = get_around_busstop(b, a)
        start = Bus_Stop(bus_group=bus_group, longitude=bus['lon'], latitude=bus['lat'], bus_name=bus['name'],
                         start_or_end=0).save()
    index = 0;

    for people in Content.objects.filter(sigungucode=user_content.sigungucode, service=0).all():
        start = Bus_Stop.objects.get(id=start_km[index] + 8 * bus_group + 1)

        people.s_busid = start.id
        people.bus_group = bus_group
        people.save()
        if User_Stop.objects.filter(user_id=people.user_id).exists():
            user_stop = User_Stop.objects.filter(user_id=people.user_id)
            user_stop.start_bus_id = start.id
            user_stop.start_bus_id = start.bus_name
            user_stop.bus_group = bus_group
            user_stop.save()
        else:
            User_Stop(user_id=people.user_id, start_bus_id=start.id, start_bus_name=start.bus_name,
                      bus_group=bus_group).save()
        index += 1

    return start_km


def first_end_clustering(user_id):
    user_content = Content.objects.get(user_id=user_id)
    rows = Content.objects.filter(sigungucode=user_content.sigungucode, service=0).count()
    cols = 2
    index = 0
    arr = [[0 for j in range(cols)] for i in range(rows)]
    if Content.objects.filter(sigungucode=user_content.sigungucode, bus_group='').exists():
        bus_group = Bus_Stop.objects.filter(start_or_end=1).count() / 4
    else:
        bus_group = Content.objects.filter(sigungucode=user_content.sigungucode).first().bus_group
    bus_group = int(bus_group)
    print(bus_group)
    for people in Content.objects.filter(sigungucode=user_content.sigungucode, service=0).all():
        arr[index][0] = people.e_longitude
        arr[index][1] = people.e_latitude
        index += 1
    km = KMeans(n_clusters=4, init='k-means++', random_state=10)
    end_km = km.fit_predict(arr)
    for i in range(4):
        center_x = km.cluster_centers_[i][0]
        center_y = km.cluster_centers_[i][1]
        a = str(center_x)
        b = str(center_y)
        bus = get_around_busstop(b, a)
        end = Bus_Stop(bus_group=bus_group, longitude=bus['lon'], latitude=bus['lat'], bus_name=bus['name'],
                       start_or_end=1).save()
    index = 0;

    for people in Content.objects.filter(sigungucode=user_content.sigungucode, service=0).all():
        end = Bus_Stop.objects.get(id=end_km[index] + 8 * bus_group + 5)
        people.e_busid = end.id
        people.bus_group = bus_group
        people.save()
        user_stop = User_Stop.objects.get(user_id=people.user_id)
        user_stop.end_bus_id = end.id
        user_stop.end_bus_name = end.bus_name
        user_stop.bus_group = bus_group
        user_stop.save()
        index += 1
    return end_km
