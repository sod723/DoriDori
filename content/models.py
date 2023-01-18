from django.db import models
from django.db.models import ForeignKey
from django.contrib.auth.models import User


# Create your models here.
class Content(models.Model):
    user_id = ForeignKey(User, on_delete=models.CASCADE, related_name='map_user')
    s_latitude = models.FloatField(default = True)
    s_longitude = models.FloatField(default = True)
    e_latitude = models.FloatField(default=True)
    e_longitude = models.FloatField(default=True)
    boarding_time = models.TextField()
