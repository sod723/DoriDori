from django.shortcuts import render
from rest_framework.views import APIView
from content.models import Content


class Main(APIView):
    def get(self, request):
        location_list = Content.objects.all()
        return render(request, 'home.html', context=dict(location_list=location_list))

    def post(self, request):
        return render(request, 'home.html')