import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
CALLBACK_URL = os.getenv("TWITCH_EVENTSUB_CALLBACK")
EVENTSUB_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET", "supersecreto123")

# ✅ Paso 1: Obtener App Access Token
def get_app_access_token():
    print("🔐 Obteniendo app access token...")
    r = requests.post("https://id.twitch.tv/oauth2/token", params={
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_SECRET,
        "grant_type": "client_credentials"
    })
    return r.json()["access_token"]

APP_ACCESS_TOKEN = get_app_access_token()

# ✅ Paso 2: Cargar access tokens de los canales desde twitch_auth.json
with open("twitch_auth.json") as f:
    tokens = json.load(f)

# ✅ Paso 3: Obtener user_id de Twitch con token de usuario
def get_user_id(username, access_token):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Client-Id": TWITCH_CLIENT_ID
    }
    r = requests.get(f"https://api.twitch.tv/helix/users?login={username}", headers=headers)
    data = r.json()
    return data["data"][0]["id"]

# ✅ Paso 4: Crear la subscripción con el token de la app
def create_subscription(event_type, user_id):
    headers = {
        "Client-Id": TWITCH_CLIENT_ID,
        "Authorization": f"Bearer {APP_ACCESS_TOKEN}",
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

# ✅ Paso 5: Registrar eventos para cada canal autorizado
for username, data in tokens.items():
    user_token = data["access_token"]
    user_id = get_user_id(username, user_token)
    print(f"\n🔗 Registrando eventos para {username} (ID: {user_id})...")
    create_subscription("channel.subscribe", user_id)
    create_subscription("channel.cheer", user_id)
