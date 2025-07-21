from django.db.models.signals import post_save
from django.dispatch import receiver
from explore.models import Trip
from explore.utils import send_trip_whatsapp
from authentication.models import Traveller  # ✅ Import Traveller model
from django.conf import settings


@receiver(post_save, sender=Trip)
def send_trip_details_on_save(sender, instance, created, **kwargs):
    if not created:
        return  # Only send message when trip is first created

    trip = instance

    # ✅ Try to get Traveller by profile
    try:
        traveller = Traveller.objects.get(profile=trip.user)
    except Traveller.DoesNotExist:
        print("❌ Traveller not found for user:", trip.user)
        return  # No Traveller found — skip sending WhatsApp

    # ✅ Format WhatsApp message
    message_text = f"""🗺️ Trip Saved!

Trip Name: {trip.name}
City: {trip.city}
Start Date: {localtime(trip.started_at).strftime('%d %b %Y %I:%M %p') if trip.started_at else 'Not started'}
Status: {trip.status.capitalize()}
Total Distance: {trip.distance or 0:.2f} km
Places:"""

    if trip.places:
        for place in trip.places:
            message_text += f"\n- {place.get('name', 'Unknown')}"
    else:
        message_text += "\n- No places selected"

    # ✅ Format phone number correctly
    to_number = f"91{traveller.number}"

    # ✅ Log details for debugging
    print("📤 Sending WhatsApp trip message via signal...")
    print("📞 To:", to_number)
    print("📦 Message:", message_text)

    # ✅ Send WhatsApp message
    status_code, meta_response = send_trip_whatsapp(
        access_token=settings.WHATSAPP_ACCESS_TOKEN,
        phone_number_id=settings.WHATSAPP_PHONE_NUMBER_ID,
        to_number=to_number,
        message_text=message_text
    )

    print("✅ WhatsApp API status:", status_code)
    print("🧾 Response:", meta_response)
