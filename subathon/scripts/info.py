import os
import sys

# Añadir carpeta raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def show_structure():
    print("📁 ESTRUCTURA DEL PROYECTO")
    print("-" * 40)
    print("""
📁 core/           → Sistema principal
📁 scripts/        → Inicio y configuración
📁 twitch/         → Integración Twitch
📁 external/       → Servicios externos  
📁 config/         → Configuración
📁 output/         → Overlay para OBS
📁 docs/           → Documentación
    """)

def show_usage():
    print("🎯 CÓMO USAR")
    print("-" * 40)
    print("python scripts/start.py     → Inicio rápido")
    print("python scripts/main.py      → Menú completo")
    print("python scripts/setup.py     → Configuración inicial")
    print("python scripts/info.py      → Esta información")

def show_urls():
    print("🌐 URLs DISPONIBLES")
    print("-" * 40)
    print("http://localhost:5000           → Control")
    print("http://localhost:5000/overlay   → Timer OBS")
    print("http://localhost:5000/stats     → Estadísticas")
    print("http://localhost:5000/webhook   → Donaciones")
    print("http://localhost:5000/twitch    → Eventos Twitch")

def main():
    print("📋 INFORMACIÓN DEL SISTEMA")
    print("=" * 50)
    
    show_structure()
    show_usage()
    show_urls()
    
    print("\n💡 Servidor único en puerto 5000")
    print("🔗 Un solo túnel ngrok necesario")

if __name__ == "__main__":
    main()