# timer_instance.py - Versión simple SIN locks
import os
import threading
import time
from datetime import datetime, timedelta

class SimpleTimer:
    def __init__(self, overlay_path="overlay_timer.txt", initial_minutes=60):
        self.overlay_path = overlay_path
        self.end_time = datetime.now() + timedelta(minutes=initial_minutes)
        self.paused = False
        self.paused_time = timedelta()
        self.should_stop = False
        
        print(f"🎯 Timer simple iniciado: {initial_minutes} minutos")
        
        # Actualizar archivo inmediatamente
        self.update_file()
        
        # Iniciar hilo de actualización
        self.start_update_thread()

    def format_time(self, delta):
        """Formato HH:MM:SS"""
        if delta.total_seconds() <= 0:
            return "00:00:00"
            
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_remaining(self):
        """Obtiene tiempo restante"""
        if self.paused:
            return self.paused_time
        else:
            remaining = self.end_time - datetime.now()
            return max(remaining, timedelta(seconds=0))

    def add_time(self, minutes):
        """Añade tiempo"""
        if self.paused:
            self.paused_time += timedelta(minutes=minutes)
        else:
            self.end_time += timedelta(minutes=minutes)
        
        remaining = self.get_remaining()
        formatted = self.format_time(remaining)
        print(f"[TIMER] +{minutes} min → {formatted}")
        self.update_file()

    def set_time(self, minutes):
        """Establece el tiempo total"""
        new_time = timedelta(minutes=minutes)
        
        if self.paused:
            self.paused_time = new_time
        else:
            self.end_time = datetime.now() + new_time
        
        remaining = self.get_remaining()
        formatted = self.format_time(remaining)
        print(f"[TIMER] Establecido a {minutes} min → {formatted}")
        self.update_file()

    def pause(self):
        """Pausa el timer"""
        if not self.paused:
            self.paused_time = max(self.end_time - datetime.now(), timedelta(seconds=0))
            self.paused = True
            print("⏸ Pausado")
            self.update_file()

    def resume(self):
        """Reanuda el timer"""
        if self.paused:
            self.end_time = datetime.now() + self.paused_time
            self.paused = False
            self.paused_time = timedelta()
            print("▶️ Reanudado")
            self.update_file()

    def is_paused(self):
        """Verifica si está pausado"""
        return self.paused

    def update_file(self):
        """Actualiza el archivo de overlay"""
        try:
            remaining = self.get_remaining()
            formatted = self.format_time(remaining)
            
            if self.paused:
                display = f"PAUSADO - {formatted}"
            else:
                display = formatted
            
            with open(self.overlay_path, "w", encoding='utf-8') as f:
                f.write(display)
                
        except Exception as e:
            print(f"❌ Error escribiendo archivo: {e}")

    def start_update_thread(self):
        """Inicia hilo de actualización"""
        def update_loop():
            print("🔄 Hilo de actualización iniciado")
            while not self.should_stop:
                try:
                    if not self.paused:
                        self.update_file()
                except Exception as e:
                    print(f"❌ Error en actualización: {e}")
                time.sleep(1)
            print("🛑 Hilo de actualización detenido")
        
        thread = threading.Thread(target=update_loop, daemon=True)
        thread.start()

    def stop(self):
        """Para el timer"""
        self.should_stop = True

# Crear instancia única
timer = SimpleTimer()