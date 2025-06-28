from django.db import models

from django.contrib.auth.models import User

import uuid 

class BaseClass(models.Model):

    uuid = models.SlugField(unique=True,default =uuid.uuid4)

    active_status = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now= True)

    class Meta :

        abstract  = True


class Touristplace(models.Model):

    name =models.CharField(max_length=200)

    image = models.ImageField(upload_to='tourist-places/')

    description = models.TextField(blank=True,null=True)

    latitude = models.FloatField()

    longitude = models.FloatField()

    def __str__(self):

        return self.name
    
    class Meta :

        verbose_name = 'Touristplaces'

        verbose_name_plural = 'Touristplaces'

        ordering = ['id']


# Create your models here.
