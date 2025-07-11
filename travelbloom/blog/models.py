from django.db import models
from authentication.models import Traveller,Profile
from explore.models import BaseClass



class BlogPost(BaseClass):
    author = models.ForeignKey('authentication.Profile', on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    
    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Blogs'
        verbose_name_plural = 'Blogs'