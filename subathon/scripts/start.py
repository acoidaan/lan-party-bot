import os
import sys
import subprocess

# Añadir carpeta raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def quick_start():
    print("🚀 INICIO RÁPIDO - SUBATHON TIMER")
    print("=" * 40)
    
    # Verificar dependencias básicas
    try:
        import flask
        import requests
    except ImportError:
        print("📦 Instalando dependencias...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "requests", "python-dotenv"])
    
    # Crear archivos mínimos si no existen
    if not os.path.exists("output/overlay_timer.txt"):
        os.makedirs("output", exist_ok=True)
        with open("output/overlay_timer.txt", "w") as f:
            f.write("1:00:00")
    
    if not os.path.exists("config/config.json"):
        os.makedirs("config", exist_ok=True)
        import json
        config = {"channels": ["tu_canal"], "overlay_path": "output/overlay_timer.txt"}
        with open("config/config.json", "w") as f:
            json.dump(config, f, indent=2)
    
    print("🌐 Iniciando servidor: http://localhost:5000")
    print("⌨️  Comandos: add 15 | pause | resume | exit")
    
    # Importar y    ncar
    from core.webhooks import app
    from core.timer_instance import timer
    import threading
    
    def run_server():
        app.run(host="0.0.0.0", port=5000, debug=False)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Consola básica
    while True:
        try:
            cmd = input("⌨️ > ").strip().lower()
            
            if cmd.startswith("add "):
                mins = int(cmd.split()[1])
                timer.add_time(mins)
                print(f"✅ +{mins} min")
            elif cmd == "pause":
                timer.pause()
                print("⏸️ Pausado")
            elif cmd == "resume":
                timer.resume()
                print("▶️ Reanudado")
            elif cmd == "exit":
                break
            else:
                print("❓ add [min] | pause | resume | exit")
        except (ValueError, IndexError):
            print("❌ Formato: add 15")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    quick_start()