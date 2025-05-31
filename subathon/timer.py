from datetime import datetime, timedelta
import threading
import time
import os

class SubathonTimer:
    def __init__(self, overlay_path="overlay_timer.txt", initial_minutes=60):
        self.lock = threading.Lock()
        self.overlay_path = overlay_path
        self.end_time = datetime.now() + timedelta(minutes=initial_minutes)
        self._paused = False
        self._paused_delta = timedelta()
        self._should_stop = False
        self._start_auto_update()

    def add_time(self, minutes):
        with self.lock:
            if self._paused:
                self._paused_delta += timedelta(minutes=minutes)
            else:
                self.end_time += timedelta(minutes=minutes)
            print(f"[TIMER] +{minutes} min")
            self._update_file_now()

    def get_remaining(self):
        with self.lock:
            if self._paused:
                return max(self._paused_delta, timedelta(seconds=0))
            else:
                return max(self.end_time - datetime.now(), timedelta(seconds=0))

    def pause(self):
        with self.lock:
            if not self._paused:
                self._paused_delta = max(self.end_time - datetime.now(), timedelta(seconds=0))
                self._paused = True
                print("⏸ Pausado.")
                self._update_file_now()

    def resume(self):
        with self.lock:
            if self._paused:
                self.end_time = datetime.now() + self._paused_delta
                self._paused = False
                self._paused_delta = timedelta()
                print("▶️ Reanudado.")
                self._update_file_now()

    def is_paused(self):
        with self.lock:
            return self._paused

    def _update_file_now(self):
        """Actualiza el archivo inmediatamente (llamada interna)"""
        if self._paused:
            remaining = self._paused_delta
            display = f"PAUSADO - {str(remaining).split('.')[0]}"
        else:
            remaining = max(self.end_time - datetime.now(), timedelta(seconds=0))
            display = str(remaining).split('.')[0]

        # Escritura atómica para evitar errores en OBS
        temp_path = self.overlay_path + ".tmp"
        with open(temp_path, "w", encoding='utf-8') as f:
            f.write(display)
        os.replace(temp_path, self.overlay_path)

    def save_to_file(self):
        """Método público para forzar actualización"""
        with self.lock:
            self._update_file_now()

    def _start_auto_update(self):
        def update_loop():
            while not self._should_stop:
                with self.lock:
                    # Solo actualizar si NO está pausado
                    if not self._paused:
                        self._update_file_now()
                time.sleep(1)
        
        t = threading.Thread(target=update_loop, daemon=True)
        t.start()

    def stop(self):
        """Para el timer completamente"""
        self._should_stop = True

# Instancia global del timer
timer = SubathonTimer()