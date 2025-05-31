import os
import sys
import threading
import time
from datetime import datetime, timedelta

# Añadir carpeta raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_menu():
    print("📋 OPCIONES DISPONIBLES:")
    print("1. 🚀 Iniciar Sistema Completo")
    print("2. ⏱️  Solo Timer + Web")
    print("3. 🔧 Configurar Twitch OAuth")
    print("4. 📡 Registrar EventSub")
    print("5. ❌ Salir")

def start_full_system():
    from core.webhooks import app
    from core.timer_instance import timer
    
    def run_server():
        print("🌐 Servidor iniciado: http://localhost:5000")
        app.run(host="0.0.0.0", port=5000, debug=False)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Consola
    while True:
        try:
            cmd = input("⌨️ > ").strip().lower()
            if cmd.startswith("add "):
                mins = int(cmd.split()[1])
                timer.add_time(mins)
            elif cmd == "pause":
                timer.pause()
            elif cmd == "resume":
                timer.resume()
            elif cmd == "exit":
                break
        except KeyboardInterrupt:
            break

def setup_twitch_oauth():
    from twitch.auth_server import app as auth_app
    print("🔧 OAuth: http://localhost:5000")
    auth_app.run(host="0.0.0.0", port=5000)

def register_eventsub():
    import twitch.register_eventsub
    print("✅ EventSub configurado")

def main():
    print("🎮 SUBATHON TIMER - MENÚ PRINCIPAL")
    print("=" * 50)
    
    while True:
        print_menu()
        choice = input("👉 Opción (1-5): ").strip()
        
        if choice == "1":
            start_full_system()
            break
        elif choice == "2":
            start_full_system()  # Mismo servidor
            break
        elif choice == "3":
            setup_twitch_oauth()
        elif choice == "4":
            register_eventsub()
        elif choice == "5":
            print("👋 ¡Hasta luego!")
            break

if __name__ == "__main__":
    main()