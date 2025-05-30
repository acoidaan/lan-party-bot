import threading
import os
from dotenv import load_dotenv
from timer import timer
import twitch_events
from datetime import datetime, timedelta

load_dotenv()

# ✅ Arranca el servidor de eventos de Twitch en segundo plano
def run_twitch_events():
    twitch_events.app.run(host="0.0.0.0", port=5002)

# 🔧 Si en el futuro tienes otro webhook, agrégalo igual
# def run_donations_webhook():
#     donations_webhook.app.run(host="0.0.0.0", port=5001)

# ✅ Ejecuta los servidores en hilos aparte
t1 = threading.Thread(target=run_twitch_events, daemon=True)
t1.start()

# t2 = threading.Thread(target=run_donations_webhook, daemon=True)
# t2.start()

print("✅ Bot subathon iniciado. Escribe comandos para controlarlo.\n")

paused = False

# ✅ Comandos por consola
while True:
    command = input("⌨️ > ").strip().lower()

    if command.startswith("add "):
        try:
            mins = int(command.split(" ")[1])
            if not paused:
                timer.add_time(mins)
                print(f"✅ Añadidos {mins} minutos manualmente.")
            else:
                print("⏸ Está pausado. No se puede añadir manualmente.")
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
        paused = True
        print("⏸ Contador pausado (solo afecta comandos manuales).")

    elif command == "resume":
        paused = False
        print("▶️ Contador reanudado.")

    elif command == "show":
        print("⏱ Tiempo restante:", str(timer.get_remaining()).split(".")[0])

    elif command == "exit":
        print("👋 Cerrando bot.")
        break

    else:
        print("❓ Comandos disponibles: add [min], set [min], pause, resume, show, exit")
