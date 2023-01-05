
from django.shortcuts import render, redirect
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from .models import User
from content.models import Content


# Create your views here.


class Join(APIView):
    def get(self, request):
        return render(request, "user/join.html")

    def post(self, request):
        # TODO 회원가입
        email = request.data.get('email', None)
        phone = request.data.get('phone', None)
        name = request.data.get('name', None)
        password = request.data.get('password', None)
        is_passenger = request.data.get('is_passenger', None)

        User.objects.create(email=email,
                            phone=phone,
                            name=name,
                            password=make_password(password),
                            is_passenger=is_passenger)

        return Response(status=200)


class Login(APIView):
    def get(self, request):
        return render(request, "user/login.html")

    def post(self, request):
        # TODO 로그인
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        user = User.objects.filter(email=email).first()

        if user is None:
            return Response(status=400, data=dict(message="회원정보가 잘못되었습니다."))

        if user.check_password(password):
            # TODO 로그인을 했다. 세션 or 쿠키
            request.session['email'] = email
            return Response(status=200)
        else:
            return Response(status=400, data=dict(message="회원정보가 잘못되었습니다."))


class LogOut(APIView):
    def get(self, request):
        request.session.flush()
        return render(request, "user/login.html")

# def login(request):
#     return render(request, "user/login.html",)
#
# def join(request):
#     return render(request, "user/join.html", )
