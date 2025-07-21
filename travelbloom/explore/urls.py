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

    path('trip-delete/<str:uuid>/',views.TripListDeleteView.as_view(),name='trip-delete'),

    path('start-trip/<str:uuid>/',views.TripStartView.as_view(), name= 'start-trip'),

    path('trip-complete/',views.TripCompleteView.as_view(), name= "complete-trip"),

    path('trip/<str:uuid>/', views.TripDetailView.as_view(), name='view-trip'),
    
    # path('trip/edit/', views.TripEditView.as_view(), name='trip-edit'), #edit trip 

    # path('trip/edit/<slug:uuid>/', views.TripEditFormView.as_view(), name='edit-trip-page'),

    # path('api/hotel-offers/', views.HotelOffersView.as_view(), name='hotel_offers'),

    path('send-trip-whatsapp/', views.SendMessageView.as_view(), name='send_trip_whatsapp'),

]
