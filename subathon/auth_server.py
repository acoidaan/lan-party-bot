import requests
from flask import Flask, request, redirect
from dotenv import load_dotenv
import os

load_dotenv()

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

  print("\n ACCESS TOKEN (copia y guarda en twitch_auth.json):\n")
  print(access_token)

  return "Token recibido correctamente. Ya puedes cerrar esta pestaña."


if __name__ == "__main__":
  app.run(port=5000)