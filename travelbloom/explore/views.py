from django.shortcuts import render
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
import json
# Create your views here.
from django.views import View

from .models import Touristplace

from django.conf import settings



def map_view(request):

        places = Touristplace.objects.all()

        return render(request,'explore/map.html',{'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY})
    
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
    