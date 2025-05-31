import requests
import json
import os
from dotenv import load_dotenv

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv("config/.env")

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
CALLBACK_URL = os.getenv("TWITCH_EVENTSUB_CALLBACK")
EVENTSUB_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET", "supersecreto123")

print("🔐 PASO 1: Obteniendo App Access Token...")

def get_app_access_token():
    r = requests.post("https://id.twitch.tv/oauth2/token", params={
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_SECRET,
        "grant_type": "client_credentials"
    })
    
    if r.status_code != 200:
        print(f"❌ Error obteniendo token: {r.status_code}")
        print(f"   Respuesta: {r.text}")
        return None
        
    data = r.json()
    if "access_token" not in data:
        print(f"❌ No se encontró access_token en respuesta: {data}")
        return None
        
    print(f"✅ App Access Token obtenido")
    return data["access_token"]

APP_ACCESS_TOKEN = get_app_access_token()
if not APP_ACCESS_TOKEN:
    print("❌ No se pudo obtener App Access Token. Verifica credenciales.")
    exit(1)

print("\n🔍 PASO 2: Obteniendo User IDs...")

# Cargar tokens de usuario desde twitch_auth.json
try:
    with open("twitch_auth.json") as f:
        tokens = json.load(f)
    print(f"✅ Tokens cargados para: {list(tokens.keys())}")
except FileNotFoundError:
    print("❌ Archivo twitch_auth.json no encontrado")
    print("   Ejecuta primero: python auth_server.py")
    exit(1)

def get_user_id(username):
    """Obtiene user_id usando App Access Token"""
    headers = {
        "Authorization": f"Bearer {APP_ACCESS_TOKEN}",
        "Client-Id": TWITCH_CLIENT_ID
    }
    
    print(f"🔍 Buscando user_id para: {username}")
    r = requests.get(f"https://api.twitch.tv/helix/users?login={username}", headers=headers)
    
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text[:200]}...")
    
    if r.status_code != 200:
        print(f"❌ Error obteniendo user_id para {username}: {r.status_code}")
        return None
        
    data = r.json()
    
    if "data" not in data or len(data["data"]) == 0:
        print(f"❌ Usuario {username} no encontrado")
        return None
        
    user_id = data["data"][0]["id"]
    print(f"✅ User ID para {username}: {user_id}")
    return user_id

def create_subscription(event_type, user_id, username):
    """Crea una suscripción EventSub"""
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
    
    print(f"\n📡 Registrando {event_type} para {username}...")
    print(f"   User ID: {user_id}")
    print(f"   Callback: {CALLBACK_URL}")
    
    r = requests.post("https://api.twitch.tv/helix/eventsub/subscriptions", headers=headers, json=body)
    
    print(f"   Status: {r.status_code}")
    
    if r.status_code == 202:
        response_data = r.json()
        subscription_id = response_data["data"][0]["id"]
        print(f"✅ {event_type} registrado exitosamente (ID: {subscription_id})")
        return True
    else:
        print(f"❌ Error registrando {event_type}: {r.text}")
        return False

print("\n🚀 PASO 3: Registrando EventSub webhooks...")

# Lista de usuarios para registrar
usernames = list(tokens.keys())
success_count = 0
total_count = 0

for username in usernames:
    print(f"\n👤 Procesando usuario: {username}")
    
    user_id = get_user_id(username)
    if not user_id:
        print(f"❌ Saltando {username} (no se pudo obtener user_id)")
        continue
    
    # Registrar eventos
    events = [
        ("channel.subscribe", "Suscripciones"),
        ("channel.cheer", "Bits")
    ]
    
    for event_type, description in events:
        total_count += 1
        if create_subscription(event_type, user_id, username):
            success_count += 1
        else:
            print(f"❌ Falló registro de {description} para {username}")

print("\n" + "="*50)
print(f"📊 RESUMEN:")
print(f"✅ Registros exitosos: {success_count}/{total_count}")
print(f"👥 Usuarios procesados: {len(usernames)}")

if success_count > 0:
    print(f"\n🎉 EventSub configurado! Ahora puedes usar:")
    print(f"   twitch event trigger subscribe")
    print(f"   twitch event trigger cheer")
    print(f"\n🌐 Callback URL: {CALLBACK_URL}")
    
    print(f"\n🧪 Para testear eventos reales:")
    for username in usernames:
        print(f"   • Suscríbete a: https://twitch.tv/{username}")
else:
    print(f"\n❌ No se pudieron registrar webhooks")
    print(f"   Verifica que:")
    print(f"   • CALLBACK_URL esté bien configurado")
    print(f"   • ngrok esté corriendo")
    print(f"   • Los usuarios existan en Twitch")