from django.db import models

# Create your models here.
class Content(models.Model):
    user_id = models.TextField()
    s_latitude = models.FloatField(default = True)
    s_longitude = models.FloatField(default = True)
    e_latitude = models.FloatField(default=True)
    e_longitude = models.FloatField(default=True)
    boarding_time = models.TextField()