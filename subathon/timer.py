from datetime import datetime, timedelta
import threading
import time
import json

class SubathonTimer:
    def __init__(self, overlay_path="overlay_timer.txt", initial_minutes=60):
        self.lock = threading.Lock()
        self.overlay_path = overlay_path
        self.end_time = datetime.now() + timedelta(minutes=initial_minutes)
        self._start_auto_update()

    def add_time(self, minutes):
        with self.lock:
            self.end_time += timedelta(minutes=minutes)
            print(f"[TIMER] ⏱️ Añadidos {minutes} minutos → nuevo fin: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")

    def get_remaining(self):
        with self.lock:
            now = datetime.now()
            delta = self.end_time - now
            return max(delta, timedelta(seconds=0))

    def save_to_file(self):
        remaining = self.get_remaining()
        text = str(remaining).split('.')[0]  # hh:mm:ss

        with open(self.overlay_path, "w") as f:
            f.write(text)

    def _start_auto_update(self):
        def update_loop():
            while True:
                self.save_to_file()
                time.sleep(10)

        t = threading.Thread(target=update_loop, daemon=True)
        t.start()

# Instancia global
timer = SubathonTimer()
