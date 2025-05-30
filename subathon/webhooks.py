from flask import Flask, request
from timer_instance import timer
import json
import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

TWITCH_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET", "defaultsecret")

app = Flask(__name__)

# ======================================
# 🟡 DONACIONES - /webhook/donations
# ======================================
@app.route("/webhook/donations", methods=["POST"])
def handle_donation():
    data = request.json
    print("[DONACIÓN] Payload recibido:")
    print(json.dumps(data, indent=2))

    try:
        messages = data.get("message", [])
        for donation in messages:
            amount = float(donation.get("amount", 0))
            user = donation.get("from", "Anon")
            minutos = int(amount * 10)
            timer.add_time(minutos)
            print(f"✅ {user} donó {amount}€ → +{minutos} minutos")
    except Exception as e:
        print("❌ Error en donación:", e)

    return "OK", 200

# ======================================
# 🟣 TWITCH EVENTSUB - /webhook/twitch
# ======================================
def verify_signature(headers, body):
    message_id = headers.get("Twitch-Eventsub-Message-Id")
    timestamp = headers.get("Twitch-Eventsub-Message-Timestamp")
    signature = headers.get("Twitch-Eventsub-Message-Signature")

    hmac_message = message_id + timestamp + body
    expected_signature = "sha256=" + hmac.new(
        TWITCH_SECRET.encode("utf-8"),
        hmac_message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)

@app.route("/webhook/twitch", methods=["POST"])
def twitch_webhook():
    raw_body = request.data.decode("utf-8")
    headers = request.headers

    if not verify_signature(headers, raw_body):
        print("⚠️ Firma inválida de Twitch")
        return "Invalid signature", 403

    data = request.json
    event_type = headers.get("Twitch-Eventsub-Message-Type")

    if event_type == "webhook_callback_verification":
        return data["challenge"], 200

    event = data.get("event", {})
    subscription_type = data.get("subscription", {}).get("type")
    user = event.get("broadcaster_user_name", "desconocido")

    if subscription_type == "channel.subscribe":
        print(f"📥 Sub en {user} → +30 minutos")
        timer.add_time(30)

    elif subscription_type == "channel.cheer":
        bits = int(event.get("bits", 0))
        minutos = (bits // 100) * 10
        print(f"📥 {bits} bits en {user} → +{minutos} minutos")
        timer.add_time(minutos)

    return "OK", 200

@app.route("/overlay.txt")
def serve_timer_file():
    try:
        with open("overlay_timer.txt", "r") as f:
            content = f.read()
        return content, 200, {'Content-Type': 'text/plain'}
    except Exception as e:
        return f"Error: {e}", 500
