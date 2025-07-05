from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from google import generativeai as genai # new client class

# ── create the client once ────────────────────────────────────────────
# settings.GEMNI_AI_KEY  must be set
genai.configure(api_key = settings.GEMNI_API_KEY)

@method_decorator(csrf_exempt, name='dispatch')
class ChatBotView(LoginRequiredMixin, View):
    """
    POST /chatbot/chat/ with form field message=...
    Optionally include latitude and longitude
    Returns JSON { "response": "<assistant reply>" }
    """

    def post(self, request, *args, **kwargs):
        user_msg = request.POST.get('message', '').strip()

        latitude = request.POST.get('latitude', None)
        longitude = request.POST.get('longitude', None)
        
        if not user_msg:
            return JsonResponse({'error': 'Login First or Register your account!.'}, status=400)

        try:
            reply = self.get_bot_reply(user_msg,latitude,longitude)
            # return JsonResponse({'response': reply})
            return JsonResponse({'response': reply})

        except Exception as exc:
            return JsonResponse({'error': f'Failed to fetch reply: {exc}'}, status=500)

    # ------------------------------------------------------------------
    def get_bot_reply(self, message,latitude = None,longitude= None):
        model = genai.GenerativeModel(model_name='models/gemini-2.5-pro')  # ✅ pick one that supports 'generateContent'
        msg_lower = message.lower().strip()

         # 🧠 Trip Planner Trigger
        trip_keywords = ['trip', 'travel', 'vacation', 'holiday', 'plan a trip', 'itinerary', 'travel plan']

        # 🧠 Hotel Query Trigger
        hotel_keywords = ['hotel', 'stay', 'resort', '5-star', 'accommodation']

        # 🧠 Fallback for vague prompts like "trip"
        if msg_lower in ['trip', 'plan', 'travel']:
            return (
                "Sure! You can say things like:\n"
                "- 'Plan a 3-day trip to Ooty'\n"
                "- 'Suggest a budget-friendly Goa itinerary'\n"
                "- 'Help me plan a solo trip to Kerala'"
            )

         # 🧳 Trip Planning
        if any(keyword in msg_lower for keyword in trip_keywords):
            prompt = f"""
You are a smart AI travel planner inside the TravelBloom app.
Do not mention UI elements like "Book a Trip" or "My Trips."
Instead, respond with:

- A short 3–5 day travel itinerary
- Suggested locations, routes, experiences
- Estimated daily budget
- Travel tips (weather, transport, packing)
Use bullet points and keep the answer helpful and friendly.

User request: {message}
"""
        # 🏨 Hotel Suggestion
        elif any(keyword in msg_lower for keyword in hotel_keywords) and latitude and longitude:
            prompt = f"""
You are a travel assistant inside the TravelBloom app.
The user is looking for good hotels near their location.
Coordinates: Latitude {latitude}, Longitude {longitude}.

Suggest 3–5 nearby **5-star hotels** or resorts.
Give names, a short description, and known landmarks or area names.
Do not mention UI buttons or features. Be brief and helpful.

User request: {message}
"""
        # 💬 Generic Chat Assistant
        else:
            prompt = f"""
You are a helpful chatbot for the TravelBloom app.
Provide short, accurate replies to the user's travel-related questions.
Avoid lengthy explanations and do not reference app UI elements.

User message: {message}
"""

        # 🧠 Generate and clean reply
        response = model.generate_content(prompt)
        reply = response.text.strip()

        # Shorten generic replies to 2 sentences max
        if not any(keyword in msg_lower for keyword in trip_keywords + hotel_keywords):
            reply = '. '.join(reply.split('. ')[:2]) + '.'

        return reply
