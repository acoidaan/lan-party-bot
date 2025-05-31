import os
import json
import subprocess
import sys

# Añadir carpeta raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def install_requirements():
    print("📦 Instalando dependencias...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas")
        return True
    except:
        print("❌ Error instalando dependencias")
        return False

def create_folders():
    print("📁 Creando carpetas...")
    folders = ["config", "output", "templates", "analytics", "core", "scripts", "twitch", "external", "docs"]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    print("✅ Carpetas creadas")

def create_config_files():
    print("⚙️ Creando archivos de configuración...")
    
    # config.json
    config = {
        "channels": ["tu_canal"],
        "overlay_path": "output/overlay_timer.txt"
    }
    
    os.makedirs("config", exist_ok=True)
    
    if not os.path.exists("config/config.json"):
        with open("config/config.json", "w") as f:
            json.dump(config, f, indent=2)
    
    if not os.path.exists("config/twitch_auth.json"):
        with open("config/twitch_auth.json", "w") as f:
            json.dump({}, f, indent=2)
    
    if not os.path.exists("config/.env"):
        env_content = """# Twitch
TWITCH_CLIENT_ID=tu_client_id
TWITCH_CLIENT_SECRET=tu_client_secret
TWITCH_REDIRECT_URI=http://localhost:5000/callback
TWITCH_SCOPES=channel:read:subscriptions+bits:read
TWITCH_EVENTSUB_CALLBACK=https://tu-dominio.ngrok.io/twitch
TWITCH_EVENTSUB_SECRET=supersecret123
"""
        with open("config/.env", "w") as f:
            f.write(env_content)
    
    if not os.path.exists("output/overlay_timer.txt"):
        os.makedirs("output", exist_ok=True)
        with open("output/overlay_timer.txt", "w") as f:
            f.write("1:00:00")
    
    print("✅ Archivos de configuración creados")

def main():
    print("🔧 CONFIGURACIÓN INICIAL")
    print("=" * 40)
    
    create_folders()
    create_config_files()
    # install_requirements()
    
    print("\n✅ ¡Configuración completada!")
    print("🚀 Ejecuta: python scripts/start.py")

if __name__ == "__main__":
    main()
