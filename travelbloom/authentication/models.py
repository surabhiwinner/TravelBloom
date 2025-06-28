from django.db import models

from django.contrib.auth.models import AbstractUser

# Create your models here.

class RoleChoices(models.TextChoices):

    ADMIN = 'Admin' , 'Admin'

    USER = 'User' , 'User'


class Profile(AbstractUser):

    role = models.CharField(max_length=20, choices=RoleChoices.choices)

    def __str__(self):

        return f'{self.first_name}-{self.last_name}-{self.role}'

    class Meta:

        verbose_name = 'Profile'

        verbose_name_plural = 'Profile'