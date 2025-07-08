from django.db import models

from django.contrib.auth.models import User

import uuid 


class BaseClass(models.Model):
    uuid = models.SlugField(unique=True, default=uuid.uuid4)
    active_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Touristplace(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='tourist-places/')
    description = models.TextField(blank=True, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Touristplaces'
        verbose_name_plural = 'Touristplaces'
        ordering = ['id']


class TripStatusChoices(models.TextChoices):

    PLANNING =   "Planning", "Planning"
    ON_GOING = "Ongoing", "Ongoing",
    COMPLETED = "Completed", "Completed"
    

class Trip(BaseClass):
    user = models.ForeignKey('authentication.Profile', on_delete=models.CASCADE, related_name="trips")
    name = models.CharField(max_length=255)
    distance = models.FloatField()
    city = models.CharField(max_length=100)
    status = models.CharField(max_length=10,choices=TripStatusChoices.choices,default=TripStatusChoices.PLANNING)
    place_ids = models.JSONField(help_text="List of Google Place IDs in selected order")
    final_place_lat = models.FloatField(null=True, blank=True)
    final_place_lng = models.FloatField(null=True, blank=True)
    visited_places = models.JSONField(default=list, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.name} ({self.city})"

    class Meta:
        ordering = ['-created_at']
