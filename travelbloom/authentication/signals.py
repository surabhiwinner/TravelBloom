from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings
from . models import Traveller,Profile

import requests

def get_client_ip(request):
    """Get the IP address from the request (supports proxies)."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

def get_ip_location(ip):
    """Use ip-api.com to get location from IP."""
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=2)
        data = response.json()
        if data['status'] == 'success':
            return f"{data.get('city', '')}, {data.get('country', '')}"
    except Exception:
        pass
    return "Unknown location"

@receiver(user_logged_in)
def send_login_email(sender, request, user, **kwargs):
    ip = get_client_ip(request)
    location = get_ip_location(ip)

    send_mail(
        subject='Login Alert - SmartVoyager',
        message=(
            f"Hi {user.username},\n\n"
            f"You just logged into your SmartVoyager account on {now().strftime('%Y-%m-%d %H:%M:%S')}.\n"
            f"Location: {location}\n"
            f"IP Address: {ip}\n\n"
            f"If this wasn't you, please reset your password immediately."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True
    )


@receiver(post_save, sender=Profile)
def create_traveller_for_profile(sender, instance, created, **kwargs):

    if created:

        Traveller.objects.create(user =instance)