from django.urls import path
from . import views

from .views import save_trip, save_user_location
urlpatterns = [
    path('map/', views.map_view, name='map'),

    # Save user location (POST from JS)
    path('save-user-location/', views.save_user_location, name='save_user_location'),

    # User's saved trips
    path('your-trip/', views.TripListView.as_view(), name='your-trip'),

    # Smart planner page
    path('planner/', views.PlannerView.as_view(), name='planner'),

    # AJAX: Fetch places (Google Places API)
    path('planner/places/', views.fetch_places, name='fetch_places'),

    # AJAX: Build optimised route
    path('planner/route/', views.build_route, name='build_route'),

    path("planner/list/", views.render_selected_list, name="render_selected_list"),

    path("trip/save/", save_trip, name="save_trip"),

    path('trip-delete/<str:uuid>/',views.TripListDeleteView.as_view(),name='trip-delete')
]
