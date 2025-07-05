from django.urls import path

from . import views

from . views import fetch_places, build_route

urlpatterns = [
    path('map/', views.map_view, name='map'),
    # path('home/', views.HomeView.as_view(), name='home'),
    path('save-user-location/', views.save_user_location, name='save_user_location'),
    path('your-trip/',views.YourTripView.as_view(),name= 'your-trip'),
    path("planner/", views.PlannerView.as_view(), name="planner"),
    path("planner/places/", fetch_places, name="fetch_places"),   # AJAX JSON
    path("planner/route/", build_route, name="build_route"),      # AJAX JSON
    
    ]