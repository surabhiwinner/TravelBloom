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

        # 🧠 Travel Keywords for filtering
        travel_keywords = [
            'trip', 'travel', 'vacation', 'holiday', 'itinerary', 'destination', 'places to visit',
            'tourist', 'city', 'country', 'flight', 'hotel', 'stay', 'transport', 'airport',
            'bus', 'train', 'metro', 'resort', 'activities', 'plan', 'travel plan'
        ]

        # ❌ Reject unrelated queries
        if not any(keyword in msg_lower for keyword in travel_keywords):
            return (
                "I'm here to help with travel planning and related queries only! ✈️\n"
                "You can ask me things like:\n"
                "- Plan a 2-day trip to Jaipur\n"
                "- Suggest top attractions in Kerala\n"
                "- Recommend hotels near Mumbai Airport"
            )

        # 🎯 Vague input suggestions
        if msg_lower in ['trip', 'plan', 'travel']:
            return (
                "Sure! You can ask me things like:\n"
                "- Plan a 2-day trip to Ooty\n"
                "- Suggest a Goa itinerary with beach spots\n"
                "- Recommend a solo travel plan for Manali"
            )

        # 🏨 Hotel Recommendation Logic
        trip_keywords = ['trip', 'travel', 'vacation', 'holiday', 'plan a trip', 'itinerary', 'travel plan']
        hotel_keywords = ['hotel', 'stay', 'resort', '5-star', 'accommodation']

        if any(keyword in msg_lower for keyword in trip_keywords):
            prompt = f"""
You are a smart AI travel planner inside the TravelBloom app.

Create a 2–3 day itinerary in this format:

Best time to visit: <one short sentence>

Day 1:
- <activity 1>
- <activity 2>

Day 2:
- <activity 1>
- <activity 2>

(Optional Day 3 if needed)

End with:
Budget: <one line only>

Guidelines:
- Use bullet style, no long paragraphs
- Keep it short, helpful, and specific to the user's destination

User request: {message}
"""
        elif any(keyword in msg_lower for keyword in hotel_keywords) and latitude and longitude:
            prompt = f"""
You are a helpful hotel assistant inside the TravelBloom app.
The user is asking for nearby hotel suggestions.

Use coordinates: Latitude {latitude}, Longitude {longitude}

List 3–5 top-rated or 5-star hotels:
- Include hotel name
- Area or landmark nearby
- 1-line description only

User message: {message}
"""
        else:
            prompt = f"""
You are a friendly travel chatbot for the TravelBloom app.

Reply briefly and helpfully about travel only.
Avoid any generic AI responses or technical talk.

User asked: {message}
"""

        # ✨ Generate response using Gemini
        response = model.generate_content(prompt)
        reply = response.text.strip()

        # For general replies, limit to 2 short lines
        if not any(keyword in msg_lower for keyword in trip_keywords + hotel_keywords):
            reply = '. '.join(reply.split('. ')[:2]) + '.'

        return reply
