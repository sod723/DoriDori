from django.urls import path
from . import views

urlpatterns = [
    path('map', views.map, name="map"),
    path('userRoute', views.userRoute, name="userRoute"),
]
