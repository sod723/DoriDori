from django.urls import path
from . import views

app_name = 'content'

urlpatterns = [
    path('map/', views.map, name="map"),
    path('getUsrLatLng/', views.getUsrLatLng, name='getApi'),
    path('SetSpot', views.GetSpotPoint, name='getspotpoint'),
    path('getRoute', views.getRoute, name='getRoute'),
]
