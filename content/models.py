from django.db import models

# Create your models here.
class Content(models.Model):
    user_id = models.TextField()
    s_latitude = models.FloatField(default = True)
    s_longitude = models.FloatField(default = True)
    e_latitude = models.FloatField(default=True)
    e_longitude = models.FloatField(default=True)
    sigungucode= models.TextField(null=True, default='')
    boarding_time = models.TextField()



class Start_Stop(models.Model):
    bus_group=models.TextField()
    user_id=models.TextField()
    bus_name=models.TextField(null=True, default='')
    s_latitude = models.FloatField(default = True)
    s_longitude = models.FloatField(default = True)

    class Meta:
        db_table='start_stop'

class User_Stop(models.Model):
    user_id=models.TextField()
    bus_id=models.TextField()
    bus_name=models.TextField(null=True, default='')

    class Meta:
        db_table='user_stop'


class Alltimeshop(models.Model):
    name = models.AutoField(primary_key=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'alltimeshop'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)










class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Lamp(models.Model):
    name = models.AutoField(primary_key=True)
    lat = models.FloatField()
    lon = models.FloatField()

    class Meta:
        managed = False
        db_table = 'lamp'


class Loadpoint(models.Model):
    name = models.AutoField(primary_key=True)
    lat = models.FloatField()
    lon = models.FloatField()

    class Meta:
        managed = False
        db_table = 'loadpoint'


class Securitycenter(models.Model):
    name = models.AutoField(primary_key=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'securitycenter'