from django.shortcuts import render, redirect

from django.http import JsonResponse

from django.utils.decorators import method_decorator

from django.views.decorators.http import require_POST

from django.views.decorators.csrf import csrf_protect, csrf_exempt

import json
# Create your views here.
from django.views import View

from .models import Touristplace,Trip

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
        

def haversine(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return None  # Return None instead of crashing

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


@require_POST
@csrf_exempt
def render_selected_list(request):
    """
    POST JSON body:
        {
            "place_ids": ["ChI...", "ChI...", ...]   # ordered, hotel first
        }

    Returns:
        {
            "html": "<li>(A) 🏨 Hotel Foo …</li> …"
        }
    """
    try:
        body = json.loads(request.body)
        place_ids = body.get("place_ids", [])

        if len(place_ids) < 1:
            return JsonResponse({"error": "No places supplied."}, status=400)

        # Fetch name & coordinates for each place_id
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        stops = []
        for pid in place_ids:
            res = requests.get(details_url, params={
                "place_id": pid,
                "key": settings.GOOGLE_MAPS_API_KEY,
                "fields": "name,types,geometry/location"
            }).json()
            result = res.get("result", {})
            loc = result.get("geometry", {}).get("location", {})
            stops.append({
                "place_id": pid,
                "name": result.get("name", "Unknown"),
                "kind": "hotel" if "lodging" in result.get("types", []) else "attraction",
                "lat": loc.get("lat"),
                "lng": loc.get("lng"),
            })

        # Build distances array (km) between consecutive stops
        distances = [None]  # First item has no previous
        for i in range(1, len(stops)):
            lat1, lon1 = stops[i-1].get("lat"), stops[i-1].get("lng")
            lat2, lon2 = stops[i].get("lat"), stops[i].get("lng")

            if None in (lat1, lon1, lat2, lon2):
                distances.append(None)
            else:
                km = haversine(lat1, lon1, lat2, lon2)
                distances.append(round(km, 1))

        # Build HTML list
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        lis = []
        for idx, (s, km) in enumerate(zip(stops, distances)):
            icon = "🏨" if s["kind"] == "hotel" else "📍"
            dist_txt = f" — {km} km" if km is not None else ""
            lis.append(
                f'<li class="mb-1">'
                f'<strong class="text-primary">({letters[idx]})</strong> '
                f'{icon} {s["name"]}{dist_txt}'
                f'</li>'
            )
        html = "".join(lis)

        return JsonResponse({"html": html})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def calculate_total_distance(place_coords):
    total = 0.0
    for i in range(1, len(place_coords)):
        p1 = place_coords[i - 1]
        p2 = place_coords[i]
        dist = haversine(p1["lat"], p1["lng"], p2["lat"], p2["lng"])
        if dist:
            total += dist
    return round(total, 2)


@require_POST
@csrf_exempt
def save_trip(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required."}, status=401)

    try:
        data = json.loads(request.body)
        name = data.get("name", "My Trip")
        city = data.get("city")
        place_ids = data.get("place_ids", [])

        if not city or not place_ids:
            return JsonResponse({"error": "City and place_ids are required."}, status=400)

        # 1. Fetch coordinates of all place_ids
        details_url = "https://maps.googleapis.com/maps/api/place/details/json"
        coords = []
        for pid in place_ids:
            res = requests.get(details_url, params={
                "place_id": pid,
                "key": settings.GOOGLE_MAPS_API_KEY,
                "fields": "geometry/location"
            }).json()

            loc = res.get("result", {}).get("geometry", {}).get("location")
            if loc:
                coords.append({
                    "lat": loc["lat"],
                    "lng": loc["lng"]
                })

        if len(coords) < 2:
            return JsonResponse({"error": "Need at least 2 valid locations to calculate distance."}, status=400)

        # 2. Calculate total distance
        total_distance = calculate_total_distance(coords)

        # 3. Save trip
        trip = Trip.objects.create(
            user=request.user,
            name=name,
            city=city,
            place_ids=place_ids,
            distance=total_distance
        )

        return JsonResponse({"status": "success", "trip_id": trip.uuid, "distance": total_distance})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



class TripListView(View):
    def get(self, request, *args, **kwargs):
        trips = Trip.objects.all()
        grouped_trips = [
            {
                "status": "Planning",
                "label": "Planned",
                "icon": "📝",
                "color": "info",
                "trips": trips.filter(status="Planning")
            },
            {
                "status": "Ongoing",
                "label": "On Going",
                "icon": "🚀",
                "color": "warning",
                "trips": trips.filter(status="Ongoing")
            },
            {
                "status": "Completed",
                "label": "Completed",
                "icon": "✅",
                "color": "success",
                "trips": trips.filter(status="Completed")
            }
        ]
        return render(request, "explore/trip-list.html", {
            "grouped_trips": grouped_trips,
            "page": "your-trip-page"
        })


class TripListDeleteView(View):

    def get(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')

        trip = Trip.objects.get(uuid=uuid)

        trip.delete()

        return redirect('your-trip')