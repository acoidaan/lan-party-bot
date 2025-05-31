# timer_instance.py - Versión simple SIN locks
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.timer import SubathonTimer

timer = SubathonTimer(overlay_path="output/overlay_timer.txt")
