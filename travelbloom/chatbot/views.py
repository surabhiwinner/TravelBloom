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
    POST /chatbot/chat/  with form‑field  message=...
    Returns JSON  { "response": "<assistant reply>" }
    """

    def post(self, request, *args, **kwargs):
        user_msg = request.POST.get('message', '').strip()
        if not user_msg:
            return JsonResponse({'error': 'Empty message.'}, status=400)

        try:
            reply = self.get_bot_reply(user_msg)
            return JsonResponse({'response': reply})
        except Exception as exc:
            return JsonResponse({'error': f'Failed to fetch reply: {exc}'}, status=500)

    # ------------------------------------------------------------------
    def get_bot_reply(self, message):
        model = genai.GenerativeModel(model_name='models/gemini-2.5-pro')  # ✅ pick one that supports 'generateContent'
        response = model.generate_content(message)
        return response.text.strip()
