#!/usr/bin/env python3
# debug_token.py - Debuggear problema de App Access Token

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

print("🔍 Debuggeando App Access Token...")
print("=" * 50)

print(f"📋 Client ID: {TWITCH_CLIENT_ID}")
print(f"📋 Client Secret: {'*' * len(TWITCH_SECRET) if TWITCH_SECRET else 'NO ENCONTRADO'}")

if not TWITCH_CLIENT_ID or not TWITCH_SECRET:
    print("❌ ERROR: Credenciales no encontradas en .env")
    print("   Asegúrate de tener:")
    print("   TWITCH_CLIENT_ID=tu_client_id")
    print("   TWITCH_CLIENT_SECRET=tu_client_secret")
    exit(1)

print("\n🔐 Intentando obtener App Access Token...")

# Hacer petición a Twitch
try:
    r = requests.post("https://id.twitch.tv/oauth2/token", params={
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_SECRET,
        "grant_type": "client_credentials"
    })
    
    print(f"📡 Status Code: {r.status_code}")
    print(f"📄 Response Headers: {dict(r.headers)}")
    print(f"📝 Response Body: {r.text}")
    
    if r.status_code == 200:
        data = r.json()
        print("\n✅ RESPUESTA EXITOSA:")
        print(json.dumps(data, indent=2))
        
        if "access_token" in data:
            print(f"\n🎉 App Access Token obtenido: {data['access_token'][:20]}...")
        else:
            print("\n❌ ERROR: No se encontró 'access_token' en la respuesta")
            print("   Campos disponibles:", list(data.keys()))
    else:
        print(f"\n❌ ERROR HTTP {r.status_code}")
        try:
            error_data = r.json()
            print("Error details:", json.dumps(error_data, indent=2))
        except:
            print("Error response:", r.text)

except Exception as e:
    print(f"❌ EXCEPCIÓN: {e}")

print("\n" + "=" * 50)
print("🔍 Diagnóstico:")

# Verificar credenciales
if len(TWITCH_CLIENT_ID or "") < 10:
    print("⚠️  Client ID parece muy corto")

if len(TWITCH_SECRET or "") < 10:
    print("⚠️  Client Secret parece muy corto")

# Test de conectividad
try:
    test_response = requests.get("https://id.twitch.tv/oauth2/validate", timeout=5)
    print("✅ Conectividad con Twitch API: OK")
except:
    print("❌ Problema de conectividad con Twitch API")