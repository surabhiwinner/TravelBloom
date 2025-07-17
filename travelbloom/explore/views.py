from django.shortcuts import render, redirect, get_object_or_404

from django.http import JsonResponse

from django.utils.decorators import method_decorator

from django.views.decorators.http import require_POST

from django.views.decorators.csrf import csrf_protect, csrf_exempt

from django.http import JsonResponse

import json
# Create your views here.
from django.views import View

from .models import Touristplace,Trip

from django.conf import settings

from google import generativeai as genai  # new client class

import requests

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

import math 
import pytz
from requests.exceptions import RequestException
from authentication.models import Traveller

from .models import Trip
from datetime import datetime, timedelta

from django.utils.timezone import now,localtime

GOOGLE = "https://maps.googleapis.com/maps/api/place/textsearch/json"

GOOGLE_NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

AMADEUS_API_KEY = settings.AMADEUS_API_KEY
AMADEUS_API_SECRET = settings.AMADEUS_API_SECRET


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

UNWANTED_KEYWORDS = ["gym","bank", "fitness", "lab","stop", "hospital", "clinic", "pharmacy"]
WANTED_TYPES = {
    # "bus_station": ["bus_station"],
    # "train_station": ["train_station"],
    # "airport": ["international_airport", "airport"],
    # "metro_station": ["subway_station"],
    "attraction": ["tourist_attraction", "point_of_interest", "museum","sea","beach","lake", "zoo", "park", "amusement_park"]
}

def is_relevant_place(place, kind):
    name = place.get("name", "").lower()
    types = place.get("types", [])
    if any(bad in name for bad in UNWANTED_KEYWORDS):
        return False
    if kind in WANTED_TYPES:
        return any(t in types for t in WANTED_TYPES[kind])
    return True


def get_place_detail(place_id):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&key={settings.GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    return response.json().get("result", {})

@csrf_exempt
@login_required
def save_trip(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            trip = Trip.objects.create(
                user=request.user,
                name=data.get("name"),
                city=data.get("city"),
                place_ids=data.get("place_ids"),
                hotel_id=data.get("hotel_id"),
                hotel_lat=data.get("hotel_lat"),
                hotel_lng=data.get("hotel_lng"),
                distance=data.get("distance")
            )

            return JsonResponse({"message": "Trip saved successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

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
    try:
        data = json.loads(request.body)
        city = data.get("city")
        kind = data.get("kind")
        lat = data.get("lat")
        lng = data.get("lng")

        api_key = settings.GOOGLE_MAPS_API_KEY

        # Use Text Search for attractions regardless of lat/lng
        if kind == "attraction":
            query = f"{kind} in {city}"
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": query,
                "key": api_key,
            }
        elif lat and lng:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{lat},{lng}",
                "radius": 8000,
                "type": kind,
                "key": api_key,
            }
        else:
            query = f"{kind} in {city}"
            url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params = {
                "query": query,
                "key": api_key,
            }

        response = requests.get(url, params=params)
        results = response.json().get("results", [])

        filtered_results = [p for p in results if is_relevant_place(p, kind)]

        return JsonResponse({"results": filtered_results})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def haversine(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return None  # Prevents crash if any value is missing

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


def calculate_total_distance(place_coords):
    total = 0.0
    for i in range(1, len(place_coords)):
        p1 = place_coords[i - 1]
        p2 = place_coords[i]
        dist = haversine(p1["lat"], p1["lng"], p2["lat"], p2["lng"])
        if dist:
            total += dist
    return round(total, 2)




class TripListView(View):
    def get(self, request, *args, **kwargs):
        trips = Trip.objects.filter(user=request.user)

        IST =pytz.timezone("Asia/Kolkata")
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

          # ✅ Format dates to IST and attach to each trip
        for group in grouped_trips:
            for trip in group["trips"]:
                trip.created_ist = localtime(trip.created_at, IST).strftime('%d-%m-%Y %I:%M %p') if trip.created_at else ''
                trip.started_ist = localtime(trip.started_at, IST).strftime('%d-%m-%Y %I:%M %p') if trip.started_at else ''
                trip.completed_ist = localtime(trip.completed_at, IST).strftime('%d-%m-%Y %I:%M %p') if trip.completed_at else ''



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


class TripStartView(View):

    def post(self, request, *args, **kwargs):

        uuid = kwargs.get('uuid')

        trip = get_object_or_404(Trip, uuid=uuid, status='Planning')

        if trip.status == 'Planning' :

            trip.status = 'Ongoing'

            trip.started_at = now()

            trip.save(update_fields=["status", "started_at"])

            return redirect('your-trip')

@method_decorator(csrf_exempt,name='dispatch')       
class TripCompleteView(View):

    def post(self, request, *args, **kwargs):

        data = json.loads(request.body)

        uuid = data.get('uuid')

        trip = get_object_or_404(Trip, uuid=uuid)

        trip.status = "Completed"

        trip.completed_at = now()

        trip.save()

        return JsonResponse({'success' :True })



class TripDetailView(View):
    def get(self, request, uuid):
        trip = get_object_or_404(Trip, uuid=uuid)
        visited = trip.visited_places or []
        all_visited = set(visited) == set(trip.place_ids)

        def fetch_place(pid):
            try:
                res = requests.get(
                    "https://maps.googleapis.com/maps/api/place/details/json",
                    params={
                        "place_id": pid,
                        "fields": "name,geometry",
                        "key": settings.GOOGLE_MAPS_API_KEY,
                    },
                    timeout=5
                ).json()
                result = res.get("result", {})
                return {
                    "place_id": pid,
                    "name": result.get("name", "Unknown"),
                    "lat": result.get("geometry", {}).get("location", {}).get("lat"),
                    "lng": result.get("geometry", {}).get("location", {}).get("lng"),
                    "is_visited": pid in visited,
                }
            except Exception as e:
                print(f"Error fetching place {pid}: {e}")
                return None

        all_places = [fetch_place(pid) for pid in trip.place_ids]
        all_places = [p for p in all_places if p and p["lat"] and p["lng"]]

        if not all_places:
            ordered_place_details = []
        else:
            # Identify the hotel (either by name or your own logic)
            hotel_index = next((i for i, p in enumerate(all_places) if "hotel" in p["name"].lower()), 0)
            hotel = all_places.pop(hotel_index)
            hotel["is_hotel"] = True

            # Mark others and sort by distance from hotel
            for p in all_places:
                p["is_hotel"] = False
                p["distance_from_hotel"] = haversine(hotel["lat"], hotel["lng"], p["lat"], p["lng"])

            attractions = sorted(all_places, key=lambda p: p["distance_from_hotel"])

            ordered_place_details = [hotel] + attractions

        # Annotate visited status
        for p in ordered_place_details:
            p["all_visited"] = all_visited

        traveller = Traveller.objects.get(profile=request.user)

        context = {
            "trip": trip,
            "places": ordered_place_details,
            "GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY,
            "traveller": traveller,
            "razorpay_key": settings.RAZORPAY_PUBLIC_KEY,
        }
        return render(request, "explore/trip_detail.html", context)



# New logic to mark visited places (based on proximity)
@csrf_exempt
@require_POST
def mark_place_visited(request):
    import json
    try:
        data = json.loads(request.body)
        uuid = data.get("uuid")
        lat = data.get("lat")
        lng = data.get("lng")

        trip = Trip.objects.get(uuid=uuid)
        visited = trip.visited_places or []

        if trip.place_ids:
            for pid in trip.place_ids:
                detail = get_place_detail(pid)
                loc = detail['geometry']['location']
                if haversine(lat, lng, loc['lat'], loc['lng']) < 0.5 and pid not in visited:
                    visited.append(pid)

        trip.visited_places = visited
        trip.save(update_fields=['visited_places'])

        return JsonResponse({"success": True, "visited": visited})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# View to check visited places
@csrf_exempt
@require_POST
def check_trip_progress(request):
    import json
    data = json.loads(request.body)
    uuid = data.get("uuid")
    user_lat = data.get("lat")
    user_lng = data.get("lng")

    trip = Trip.objects.filter(uuid=uuid).first()
    if not trip:
        return JsonResponse({"error": "Trip not found."}, status=404)

    visited = []
    for pid in trip.place_ids:
        detail = get_place_detail(pid)
        if not detail:
            continue
        loc = detail['geometry']['location']
        dist = haversine(user_lat, user_lng, loc['lat'], loc['lng'])
        if dist <= 0.5:
            visited.append(pid)

    all_visited = set(visited) == set(trip.place_ids)

    return JsonResponse({
        "visited_places": visited,
        "all_visited": all_visited
    })
