from django.db import models

class s_address(models.Model) :
    lat = models.BigIntegerField()
    lon = models.BigIntegerField()
    
    def __str__(self) :
        return self.memo_text
    