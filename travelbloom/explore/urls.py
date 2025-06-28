from django.urls import path

from . import views

urlpatterns = [
    path('map/', views.map_view, name='map_page'),
    # path('home/', views.HomeView.as_view(), name='home'),
    path('save-user-location/', views.save_user_location, name='save_user_location'),

]