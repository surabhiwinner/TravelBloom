from django.contrib import admin

from . import models
# Register your models here.

# Profile model stays the same
admin.site.register(models.Profile)
admin.site.register(models.Traveller)
# Custom admin for Traveller
# @admin.register(models.Traveller)
# class TravellerAdmin(admin.ModelAdmin):
#     list_display = ('name', 'email', 'number', 'has_premium_access')
#     list_filter = ('has_premium_access',)