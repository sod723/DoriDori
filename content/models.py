from django.db import models

# Create your models here.
class Content(models.Model):
    user_id = models.TextField()
    s_latitude = models.FloatField(default = True)
    s_longitude = models.FloatField(default = True)
    e_latitude = models.FloatField(default=True)
    e_longitude = models.FloatField(default=True)
    sigungucode= models.TextField(null=True, default='')
    bus_group=models.TextField(null=True, default='')
    s_busid=models.TextField(null=True, default='')
    e_busid = models.TextField(null=True, default='')
    service=models.TextField(default='0')
    boarding_time = models.TextField()



class Bus_Stop(models.Model):
    bus_group=models.TextField(null=True, default='')
    bus_name=models.TextField(null=True, default='')
    latitude = models.FloatField(default = True)
    longitude = models.FloatField(default = True)
    start_or_end=models.TextField(null=True, default='')
    first=models.TextField(default='0')
    service=models.TextField(default='0')
    class Meta:
        db_table='bus_stop'

class User_Stop(models.Model):
    user_id=models.TextField()
    start_bus_id=models.TextField(null=True, default='')
    end_bus_id = models.TextField(null=True, default='')
    start_bus_name=models.TextField(null=True, default='')
    end_bus_name = models.TextField(null=True, default='')
    bus_group=models.TextField(null=True, default='')

    class Meta:
        db_table='user_stop'


