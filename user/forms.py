from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

import content.models
from content.models import Content

MEMBER_TYPE = [
    ('passenger', 'Passenger'),
    ('driver', 'Driver')
]
class UserForm(UserCreationForm):
    email = forms.EmailField(label="이메일")
    first_name = forms.CharField(widget=forms.RadioSelect(choices=MEMBER_TYPE), label="회원 종류를 선택하세요.")
    class Meta:
        model = User
        fields = ("username", "password1", "password2", "email", "first_name")