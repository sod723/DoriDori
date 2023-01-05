from django.db import models

# Create your models here.
class Content(models.Model):
    user_id = models.TextField()
    latitude = models.TextField()
    longitude = models.TextField()
    boarding_time = models.TextField()