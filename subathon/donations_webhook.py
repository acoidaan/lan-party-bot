from flask import Flask, request
from timer_instance import timer
import json

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def handle_donation():
    data = request.json

    print("[WEBHOOK] Evento recibido:")
    print(json.dumps(data, indent=2))

    try:
        # ⚠️ Ajusta según el formato exacto que te envíe Streamlabs
        # En donaciones reales, los datos están dentro de una lista en el campo 'message'
        messages = data.get("message", [])

        for donation in messages:
            amount = float(donation.get("amount", 0))
            nombre = donation.get("from", "Desconocido")
            minutos = int(amount * 10)

            print(f"[DONACIÓN] {nombre} donó {amount}€ → +{minutos} minutos")
            timer.add_time(minutos)

    except Exception as e:
        print("❌ Error procesando donación:", e)

    return "OK", 200

if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    load_dotenv()

    with open("config.json") as f:
        config = json.load(f)

    port = config.get("webhook_port", 5001)
    app.run(host="0.0.0.0", port=port)
