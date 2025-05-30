import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
EVENTSUB_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET", "supersecreto123")

# 👇 CAMBIA esto con tu URL actual de ngrok
CALLBACK_URL = "https://287b-2-137-225-184.ngrok-free.app/twitch"

# Carga tokens
with open("twitch_auth.json") as f:
    tokens = json.load(f)

def get_user_id(username, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-Id": TWITCH_CLIENT_ID
    }
    r = requests.get(f"https://api.twitch.tv/helix/users?login={username}", headers=headers)
    data = r.json()
    return data["data"][0]["id"]

def create_subscription(event_type, user_id, access_token):
    headers = {
        "Client-Id": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    body = {
        "type": event_type,
        "version": "1",
        "condition": {
            "broadcaster_user_id": user_id
        },
        "transport": {
            "method": "webhook",
            "callback": CALLBACK_URL,
            "secret": EVENTSUB_SECRET
        }
    }
    r = requests.post("https://api.twitch.tv/helix/eventsub/subscriptions", headers=headers, json=body)
    print(f"📡 {event_type} → {r.status_code}: {r.text}")

# 👇 Registra eventos para cada canal
for username, data in tokens.items():
    access_token = data["access_token"]
    user_id = get_user_id(username, access_token)
    print(f"\n🔗 Registrando eventos para {username} (ID: {user_id})...")
    create_subscription("channel.subscribe", user_id, access_token)
    create_subscription("channel.cheer", user_id, access_token)
