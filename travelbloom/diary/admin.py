from django.contrib import admin

from . import models
# Register your models here.


admin.site.register(models.DiaryEntry)

admin.site.register(models.DiaryMedia)