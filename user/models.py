from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models

# Create your models here.
class User(AbstractBaseUser):

    # user_id = models.CharField(max_length=24, unique=True)
    # user_name = models.CharField(max_length=24)
    # user_email = models.EmailField(max_length=128, unique=True)
    # user_phone = models.CharField(max_length=13)
    # #is_passenger = models.BooleanField(default=True)
    #
    # USERNAME_FIELD = 'user_email'
    #
    #
    # class Meta:
    #     db_table = "User"

    phone = models.CharField(max_length=24, unique=True)
    name = models.CharField(max_length=24)
    email = models.EmailField(unique=True)
    is_passenger = models.TextField()  # 프로필 이미지

    USERNAME_FIELD = 'phone'

    class Meta:
        db_table = "User"