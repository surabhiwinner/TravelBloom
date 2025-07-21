from django.db import models

from explore.models import BaseClass
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

        verbose_name_plural = 'Profiles'


class Traveller(BaseClass):

    profile = models.OneToOneField('Profile', on_delete=models.CASCADE,related_name='traveller')

    name = models.CharField(max_length=40)

    email = models.EmailField()

    image = models.ImageField(upload_to='Traveller-images/', blank=True, null=True)

    number = models.CharField(max_length=10)


    has_premium_access = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name}'
    
    class Meta:

        verbose_name = 'Traveller'

        verbose_name_plural = 'Travellers'

    

