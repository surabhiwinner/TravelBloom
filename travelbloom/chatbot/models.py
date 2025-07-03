from django.db import models

from django.contrib.auth.models import User

# Create your models here.

class ChatMessage(models.Model):

    user = models.ForeignKey('authentication.Profile', on_delete=models.CASCADE)

    message = models.TextField()

    response = models.TextField()

    timestamp = models.DateTimeField(auto_now_add=True)

    
