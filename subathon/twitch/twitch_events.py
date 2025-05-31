from flask import Flask, request
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.timer_instance import timer
import json
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

TWITCH_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET", "supersecreto123")

app = Flask(__name__)

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

@app.route("/twitch", methods=["POST"])
def twitch_webhook():
    raw_body = request.data.decode("utf-8")
    headers = request.headers

    print("⚠️ Simulando evento (firma no verificada)")


    data = request.json
    event_type = headers.get("Twitch-Eventsub-Message-Type")

    if event_type == "webhook_callback_verification":
        return data["challenge"], 200

    event = data.get("event", {})
    subscription_type = data.get("subscription", {}).get("type")

    user = event.get("broadcaster_user_name", "").lower()

    if subscription_type == "channel.subscribe":
        print(f"[SUB] Sub en {user}")
        timer.add_time(30)

    elif subscription_type == "channel.cheer":
        bits = int(event.get("bits", 0))
        minutos = (bits // 100) * 10
        print(f"[BITS] {bits} bits en {user} → +{minutos} minutos")
        timer.add_time(minutos)

    return "", 200

if __name__ == "__main__":
    app.run(port=5002)
