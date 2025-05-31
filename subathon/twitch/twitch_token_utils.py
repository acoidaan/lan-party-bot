import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def refresh_access_token(username):
    with open("twitch_auth.json") as f:
        auth_data = json.load(f)

    refresh_token = auth_data[username]["refresh_token"]

    r = requests.post("https://id.twitch.tv/oauth2/token", params={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": os.getenv("TWITCH_CLIENT_ID"),
        "client_secret": os.getenv("TWITCH_CLIENT_SECRET")
    })

    if r.status_code != 200:
        raise Exception(f"Error al refrescar token de {username}: {r.text}")

    tokens = r.json()

    # Actualiza tokens en el archivo
    auth_data[username]["access_token"] = tokens["access_token"]
    auth_data[username]["refresh_token"] = tokens["refresh_token"]

    with open("twitch_auth.json", "w") as f:
        json.dump(auth_data, f, indent=2)

    print(f"[{username}] 🔁 Token refrescado")

    return tokens["access_token"]
