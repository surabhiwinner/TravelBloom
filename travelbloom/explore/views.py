from django.shortcuts import render

from django.http import JsonResponse

from django.utils.decorators import method_decorator

from django.views.decorators.http import require_POST

from django.views.decorators.csrf import csrf_protect, csrf_exempt

import json
# Create your views here.
from django.views import View

from .models import Touristplace

from django.conf import settings

from google import generativeai as genai  # new client class

import requests

from django.views.decorators.http import require_POST

import math 

GOOGLE = "https://maps.googleapis.com/maps/api/place/textsearch/json"

def map_view(request):

        places = Touristplace.objects.all()

        data = {'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY,
                'page':'map-page'}

        return render(request,'explore/map.html',context=data)
    
@require_POST
@csrf_protect
def save_user_location(request):
        
    try:
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        if latitude is not None and longitude is not None:
            latitude = float(latitude)
            longitude = float(longitude)

            print(f"Django Backend Received: Latitude = {latitude}, Longitude = {longitude}")

            # --- Your Python logic to use latitude and longitude goes here ---
            # E.g., save to a database, perform server-side calculations, etc.

            return JsonResponse({'status': 'success', 'message': 'Location received and processed by backend.', 'latitude': latitude, 'longitude': longitude})
        else:
            return JsonResponse({'status': 'error', 'message': 'Latitude or Longitude not provided in request.'}, status=400)
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON in request body.'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'An internal server error occurred: {str(e)}'}, status=500)

class YourTripView(View):
     
     def get(self, request, *args,**kwargs):

        data ={
                 'page' : 'your-trip-page'
            }
        return render(request, 'explore/trip-list.html',context=data)  

def get_nearby_places(lat,lng,keyword=None, radius=5000):
   
    url= "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
         'location': f"{lat},{lng}",
         'radius': radius,
         'key': settings.GOOGLE_MAPS_API_KEY
    }

    response = requests.get(url, params=params)
    return response.json().get('results', [])[:5]

class PlannerView(View):
    
    def get(self, request, *args, **kwargs):
        data = {
            'page': 'planner-page',
            'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
        }
        return render(request, 'explore/planner.html', context=data)
    
@require_POST
@csrf_exempt
def fetch_places(request):
        
      body = json.loads(request.body)

      city = body.get('city')

      kind = body.get("kind")

      query = f"tourist attractions in {city}" if kind == "attraction"  else f"hotels in {city}"

      params = {
          "query" : query,
          "key" : settings.GOOGLE_MAPS_API_KEY,
          "type" : "tourist_attraction" if kind == "attraction" else "lodging",
          "fields" :"place_id,name,formatted_address,phpto,geometry"

      }

      res = requests.get(GOOGLE, params=params).json()

      return JsonResponse({"results" : res.get("results", [])})
        
@require_POST
@csrf_exempt
def build_route(request):
    try:
        body = json.loads(request.body)
        place_ids = body.get("place_ids", [])
        print("Received place_ids:", place_ids)
        return JsonResponse({"waypoints": place_ids})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def haversine(lat1, lon1, lat2, lon2):
    # Haversine formula to calculate distance between two lat/lng points in km
    R = 6371  # Earth radius in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) ** 2 + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


@require_POST
@csrf_exempt
def build_route(request):
    try:
        body = json.loads(request.body)
        place_ids = body.get("place_ids", [])

        if len(place_ids) < 2:
            return JsonResponse({"error": "Select at least two places."}, status=400)

        details_url = "https://maps.googleapis.com/maps/api/place/details/json"

        # Fetch lat/lng of all places
        places = []
        for pid in place_ids:
            res = requests.get(details_url, params={
                "place_id": pid,
                "key": settings.GOOGLE_MAPS_API_KEY,
                "fields": "geometry/location"
            }).json()

            loc = res.get("result", {}).get("geometry", {}).get("location")
            if loc:
                places.append({
                    "place_id": pid,
                    "lat": loc["lat"],
                    "lng": loc["lng"]
                })

        # Sort by distance from the first location (greedy sort)
        start = places[0]
        ordered = [start]
        places_left = places[1:]

        while places_left:
            last = ordered[-1]
            nearest = min(places_left, key=lambda p: haversine(last["lat"], last["lng"], p["lat"], p["lng"]))
            ordered.append(nearest)
            places_left.remove(nearest)

        ordered_ids = [p["place_id"] for p in ordered]

        return JsonResponse({"waypoints": ordered_ids})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)