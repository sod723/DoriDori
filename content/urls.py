from django.urls import path
from . import views

urlpatterns = [
    path('map', views.map, name="map"),
]
