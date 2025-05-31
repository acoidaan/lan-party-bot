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
        self._start_auto_update()

    def add_time(self, minutes):
        with self.lock:
            if self._paused:
                self._paused_delta += timedelta(minutes=minutes)
            else:
                self.end_time += timedelta(minutes=minutes)
            print(f"[TIMER] +{minutes} min")
            self.save_to_file()

    def get_remaining(self):
        with self.lock:
            return self._paused_delta if self._paused else max(self.end_time - datetime.now(), timedelta(seconds=0))

    def pause(self):
        with self.lock:
            if not self._paused:
                self._paused_delta = self.end_time - datetime.now()
                self._paused = True
                print("⏸ Pausado.")
                self.save_to_file()

    def resume(self):
        with self.lock:
            if self._paused:
                self.end_time = datetime.now() + self._paused_delta
                self._paused = False
                self._paused_delta = timedelta()
                print("▶️ Reanudado.")
                self.save_to_file()

    def is_paused(self):
        return self._paused

    def save_to_file(self):
        with self.lock:
            if self._paused:
                display = f"PAUSADO - {str(self._paused_delta).split('.')[0]}"
            else:
                remaining = self.end_time - datetime.now()
                display = str(max(remaining, timedelta())).split('.')[0]

            # Escritura atómica para evitar errores en OBS
            temp_path = self.overlay_path + ".tmp"
            with open(temp_path, "w") as f:
                f.write(display)
            os.replace(temp_path, self.overlay_path)

    def _start_auto_update(self):
        def update_loop():
            while True:
                self.save_to_file()
                time.sleep(1)
        t = threading.Thread(target=update_loop, daemon=True)
        t.start()

timer = SubathonTimer()
