import threading
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from timer_instance import timer
from webhooks import app as unified_webhook_app

load_dotenv()

def run_webhooks():
    unified_webhook_app.run(host="0.0.0.0", port=5000)

t_webhooks = threading.Thread(target=run_webhooks, daemon=True)
t_webhooks.start()

print("✅ Bot subathon iniciado. Escribe comandos para controlarlo.\n")

# ✅ Consola interactiva
while True:
    command = input("⌨️ > ").strip().lower()

    if command.startswith("add "):
        try:
            mins = int(command.split(" ")[1])
            timer.add_time(mins)
            print(f"✅ Añadidos {mins} minutos manualmente.")
        except:
            print("❌ Uso correcto: add 15")

    elif command.startswith("set "):
        try:
            mins = int(command.split(" ")[1])
            if mins < 0:
                print("❌ El tiempo no puede ser negativo.")
                continue
            with timer.lock:
                timer.end_time = datetime.now() + timedelta(minutes=mins)
            print(f"✅ Tiempo establecido manualmente a {mins} minutos.")
        except:
            print("❌ Uso correcto: set 90")

    elif command == "pause":
        timer.pause()
        print("Contador pausado.")

    elif command == "resume":
        timer.resume()
        print("Contador reanudado.")

    elif command == "show":
        print("⏱ Tiempo restante:", str(timer.get_remaining()).split(".")[0])

    elif command == "exit":
        print("👋 Cerrando bot.")
        break

    else:
        print("❓ Comandos disponibles: add [min], set [min], pause, resume, show, exit")
