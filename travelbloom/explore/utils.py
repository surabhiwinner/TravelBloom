

import requests
import json

from math import radians, cos, sin, asin, sqrt


def send_trip_whatsapp(access_token, phone_number_id, to_number, message_text):
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": message_text
        }
    }

    print("🟢 Sending WhatsApp Message")
    print("📤 URL:", url)
    print("📞 To:", to_number)
    print("💬 Message:", message_text)
    print("🔐 Token (first 10 chars):", access_token[:10], "...")

    response = requests.post(url, headers=headers, json=payload)
    
    print("🔁 Response Status Code:", response.status_code)
    print("📩 Response Text:", response.text)

    try:
        return response.status_code, response.json()
    except Exception as e:
        print("⚠️ JSON decode error:", e)
        return response.status_code, {"error": str(e)}



def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius of the Earth in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c


