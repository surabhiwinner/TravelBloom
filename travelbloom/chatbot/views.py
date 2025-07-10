from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from google import generativeai as genai

# ── Configure Gemini API ────────────────────────────────────────────────
genai.configure(api_key=settings.GEMINI_API_KEY)

@method_decorator(csrf_exempt, name='dispatch')
class ChatBotView(LoginRequiredMixin, View):
    """
    POST /chatbot/chat/ with form field message=...
    Optionally include latitude and longitude
    Returns JSON: { "response": "<assistant reply>" }
    """

    def post(self, request, *args, **kwargs):
        user_msg = request.POST.get('message', '').strip()
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if not user_msg:
            return JsonResponse({'error': 'Message required.'}, status=400)

        try:
            reply = self.get_bot_reply(user_msg, latitude, longitude)
            return JsonResponse({'response': reply})
        except Exception as exc:
            return JsonResponse({'error': f'Failed to generate reply: {exc}'}, status=500)

    def get_bot_reply(self, message, latitude=None, longitude=None):
        model = genai.GenerativeModel(model_name='models/gemini-2.5-pro')
        msg_lower = message.lower().strip()

        # 🧠 Trigger Keywords
        trip_keywords = ['trip', 'travel', 'vacation', 'holiday', 'plan a trip', 'itinerary', 'travel plan']
        hotel_keywords = ['hotel', 'stay', 'resort', '5-star', 'accommodation']

        # 🎯 Example Suggestions for vague prompts
        if msg_lower in ['trip', 'plan', 'travel']:
            return (
                "Sure! You can say things like:\n"
                "- Plan a 3-day trip to Ooty\n"
                "- Suggest a budget-friendly Goa itinerary\n"
                "- Help me plan a solo trip to Kerala"
            )

        # ✈️ Trip Planning
        if any(keyword in msg_lower for keyword in trip_keywords):
            prompt = f"""
You are a smart AI travel planner inside the TravelBloom app.

Generate a 3-5 day travel itinerary based on the user request:
- Include top attractions, routes, and activities.
- Suggest ideal seasons or travel tips (e.g., packing/weather).
- Mention estimated daily budget.
- Format in clean bullet points.

User request: {message}
"""
        # 🏨 Hotel Recommendation (only if lat/lon provided)
        elif any(keyword in msg_lower for keyword in hotel_keywords) and latitude and longitude:
            prompt = f"""
You are a helpful hotel assistant inside the TravelBloom app.
The user is asking for nearby hotels.

Use coordinates: Latitude {latitude}, Longitude {longitude}
Suggest 3–5 **5-star or top-rated** hotels/resorts:
- Include names, area or landmark, and 1-sentence description.

User said: {message}
"""
        # 🤖 Generic Travel Help
        else:
            prompt = f"""
You are a friendly travel chatbot for the TravelBloom app.
Answer concisely and helpfully. Avoid UI references.

User asked: {message}
"""

        # ✨ Generate response from Gemini
        response = model.generate_content(prompt)
        reply = response.text.strip()

        # Limit generic replies to 2 sentences
        if not any(keyword in msg_lower for keyword in trip_keywords + hotel_keywords):
            reply = '. '.join(reply.split('. ')[:2]) + '.'

        return reply
