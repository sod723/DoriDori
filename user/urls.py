from django.urls import path
from . import views
from .views import Join, Login, LogOut

urlpatterns = [
    #path('login', views.login, name="login"),
    path('join/', Join.as_view(), name='join'),
    path('login/', Login.as_view(), name='login'),
    path('join', Join.as_view(), name='join'),
    path('login', Login.as_view(), name='login'),
]
