from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('map/', views.map, name="map"),
    path('getUsrLatLng/', views.getUsrLatLng, name='getApi'),
    path('getspotpoint', views.GetSpotPoint, name='getspotpoint'),
    # path('pathfinder', views.PathFinder, name='pathfinder'),
    # path('saferoute', views.saferoute, name='saferoute'),
    # path('userRoute', views.userRoute, name="userRoute"),
    # path('driverRoute', views.driverRoute, name="driverRoute"),
]
