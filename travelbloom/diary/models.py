from django.db import models
from django.conf import settings
from django.utils import timezone

from explore.models import BaseClass
from django.contrib.auth.models import User

# Create your models here.


class DiaryEntry(BaseClass):

    profile = models.OneToOneField('authentication.Profile', on_delete=models.CASCADE)

    title = models.CharField(max_length=200)
    notes = models.TextField(blank=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return f"{self.title} ({self.created_at.date()})"
    
    class Meta:

        verbose_name = 'Diary'

        verbose_name_plural = 'Diary'

class MediaChoices(models.TextChoices):

    IMAGE = 'Image', 'Image'

    VIDEO = 'Video' , 'Video'

    AUDIO = 'Audio' , 'Audio' 


class DiaryMedia(BaseClass):

    diary = models.ForeignKey('DiaryEntry', on_delete=models.CASCADE, related_name = 'media_files')

    file = models.FileField(upload_to='diary_media/')

    media_type = models.CharField(max_length=10,choices=MediaChoices.choices)

    def __str__(self):
        return f"{self.media_type} - {self.file.name}"
    

    class Meta:

        verbose_name = 'Media'

        verbose_name_plural = 'Media'

    
