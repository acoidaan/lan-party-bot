import requests
from flask import Flask, request, redirect
from dotenv import load_dotenv
import os
import json

load_dotenv("config/.env")

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
REDIRECT_URI = os.getenv("TWITCH_REDIRECT_URI")
SCOPES = os.getenv("TWITCH_SCOPES")

app = Flask(__name__)

@app.route("/")
def login():
    return redirect(
        f"https://id.twitch.tv/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={SCOPES}"
    )

@app.route("/callback")
def callback():
    code = request.args.get("code")
    r = requests.post("https://id.twitch.tv/oauth2/token", params={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    })

    tokens = r.json()

    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    print("\n✅ Tokens recibidos:")
    print("Access Token:", access_token)
    print("Refresh Token:", refresh_token)

    username = input("Introduce el nombre del canal (ej: xstellar_): ").strip().lower()

    # Guarda tokens en twitch_auth.json
    try:
        with open("twitch_auth.json", "r") as f:
            content = f.read().strip()
            auth_data = json.loads(content) if content else {}
    except FileNotFoundError:
        auth_data = {}



    auth_data[username] = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

    with open("twitch_auth.json", "w") as f:
        json.dump(auth_data, f, indent=2)

    return f"Token guardado para {username}. Ya puedes cerrar esta pestaña."

if __name__ == "__main__":
    app.run(port=5000)
