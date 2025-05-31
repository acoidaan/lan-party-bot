#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import signal
import sys
import os
from datetime import datetime, timedelta
from timer_instance import timer

def signal_handler(sig, frame):
    print('\n👋 Cerrando bot subathon...')
    timer.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def show_help():
    """Muestra la ayuda de comandos"""
    help_text = """
📋 COMANDOS DISPONIBLES:
─────────────────────────
• add [minutos]    → Añade tiempo al contador
• set [minutos]    → Establece el tiempo total
• pause            → Pausa el contador
• resume           → Reanuda el contador
• show             → Muestra tiempo restante
• status           → Muestra estado completo
• web              → Muestra URLs del servidor
• test             → Testa que todo funciona
• help             → Muestra esta ayuda
• exit/quit        → Cierra el bot

💡 EJEMPLOS:
─────────
add 15      → Añade 15 minutos
set 120     → Establece el timer a 2 horas
pause       → Pausa el contador
resume      → Reanuda el contador

🌐 SERVIDOR WEB CONSOLIDADO:
────────────────────────────
• Interfaz:     http://localhost:5000
• Donaciones:   http://localhost:5000/webhook
• Twitch:       http://localhost:5000/twitch
• Estado:       http://localhost:5000/health

🔗 CON NGROK:
─────────────
• Interfaz:     https://4017-2-137-225-184.ngrok-free.app
• Donaciones:   https://4017-2-137-225-184.ngrok-free.app/webhook
• Twitch:       https://4017-2-137-225-184.ngrok-free.app/twitch
    """
    print(help_text)

def show_status():
    """Muestra el estado completo del timer"""
    remaining = timer.get_remaining()
    paused = timer.is_paused()
    
    print("📊 ESTADO DEL SUBATHON:")
    print("─" * 50)
    print(f"⏱️  Tiempo restante: {str(remaining).split('.')[0]}")
    print(f"▶️  Estado: {'🔴 PAUSADO' if paused else '🟢 ACTIVO'}")
    print(f"🌐 Servidor local: http://localhost:5000")
    print(f"🔗 Servidor ngrok: https://4017-2-137-225-184.ngrok-free.app")
    print("─" * 50)

def show_web_info():
    """Muestra información de las URLs web"""
    print("🌐 INFORMACIÓN DEL SERVIDOR WEB:")
    print("─" * 50)
    print("📱 INTERFAZ PRINCIPAL:")
    print("   Local:  http://localhost:5000")
    print("   Ngrok:  https://4017-2-137-225-184.ngrok-free.app")
    print()
    print("🔗 ENDPOINTS PARA CONFIGURAR:")
    print("   💰 Streamlabs: https://4017-2-137-225-184.ngrok-free.app/webhook")
    print("   🎮 Twitch:     https://4017-2-137-225-184.ngrok-free.app/twitch")
    print("   📊 Estado:     https://4017-2-137-225-184.ngrok-free.app/health")
    print("   🧪 Test:       https://4017-2-137-225-184.ngrok-free.app/test")
    print("─" * 50)

def test_system():
    """Testa que el sistema funciona"""
    try:
        import requests
        response = requests.get("http://localhost:5000/test", timeout=5)
        if response.status_code == 200:
            print("✅ Sistema funcionando correctamente!")
            print("📊 Estado del servidor:", response.json().get("message"))
        else:
            print(f"⚠️ Servidor respondió con código: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor web.")
        print("💡 Asegúrate de que el servidor esté corriendo.")
    except ImportError:
        print("⚠️ Módulo 'requests' no disponible para test automático.")
        print("🌐 Prueba manualmente: http://localhost:5000/test")
    except Exception as e:
        print(f"❌ Error en test: {e}")

def main():
    print("🚀 BOT SUBATHON - MODO CONSOLA")
    print("=" * 50)
    print("🌐 El servidor web debe estar corriendo en otro proceso.")
    print("📝 Para iniciarlo: python webhooks.py")
    print("💡 Escribe 'help' para ver comandos disponibles")
    print("💡 Escribe 'web' para ver URLs de configuración")
    print()
    
    show_status()
    print()

    # ✅ Consola interactiva
    while True:
        try:
            command = input("\n⌨️  Subathon > ").strip().lower()
            
            if not command:
                continue
                
            elif command.startswith("add "):
                try:
                    parts = command.split(" ", 1)
                    mins = int(parts[1])
                    if mins <= 0:
                        print("❌ Los minutos deben ser positivos.")
                        continue
                    timer.add_time(mins)
                    print(f"✅ Añadidos {mins} minutos al contador.")
                    print(f"⏱️  Nuevo tiempo: {str(timer.get_remaining()).split('.')[0]}")
                except (ValueError, IndexError):
                    print("❌ Uso correcto: add [minutos] (ej: add 15)")

            elif command.startswith("set "):
                try:
                    parts = command.split(" ", 1)
                    mins = int(parts[1])
                    if mins < 0:
                        print("❌ El tiempo no puede ser negativo.")
                        continue
                        
                    with timer.lock:
                        if timer.is_paused():
                            timer._paused_delta = timedelta(minutes=mins)
                        else:
                            timer.end_time = datetime.now() + timedelta(minutes=mins)
                        timer.save_to_file()
                        
                    print(f"✅ Tiempo establecido a {mins} minutos.")
                    print(f"⏱️  Tiempo actual: {str(timer.get_remaining()).split('.')[0]}")
                except (ValueError, IndexError):
                    print("❌ Uso correcto: set [minutos] (ej: set 90)")

            elif command == "pause":
                if timer.is_paused():
                    print("⚠️  El contador ya está pausado.")
                else:
                    timer.pause()
                    print("⏸️  Contador pausado.")

            elif command == "resume":
                if not timer.is_paused():
                    print("⚠️  El contador ya está activo.")
                else:
                    timer.resume()
                    print("▶️  Contador reanudado.")

            elif command in ["show", "time"]:
                remaining = timer.get_remaining()
                paused_text = " 🔴 (PAUSADO)" if timer.is_paused() else " 🟢"
                print(f"⏱️  Tiempo restante: {str(remaining).split('.')[0]}{paused_text}")

            elif command in ["status", "info"]:
                show_status()

            elif command in ["web", "urls", "url"]:
                show_web_info()

            elif command in ["test", "check"]:
                test_system()

            elif command in ["help", "h", "?"]:
                show_help()

            elif command in ["exit", "quit", "q"]:
                print("👋 Cerrando bot subathon...")
                timer.stop()
                break

            elif command == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                print("✅ Bot subathon - Consola limpiada")
                show_status()

            else:
                print("❓ Comando no reconocido. Escribe 'help' para ver comandos disponibles.")
                
        except KeyboardInterrupt:
            print("\n👋 Cerrando bot...")
            timer.stop()
            break
        except Exception as e:
            print(f"❌ Error ejecutando comando: {e}")

    print("🔚 Bot subathon cerrado.")

if __name__ == "__main__":
    main()