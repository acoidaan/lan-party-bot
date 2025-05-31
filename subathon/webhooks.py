# webhooks_enhanced.py - Con sistema de overlays integrado (restaurado completo)
from flask import Flask, jsonify, request, render_template_string
from timer_instance import timer
import json
import hmac
import hashlib
import os
import threading
import time
from dotenv import load_dotenv

# Importar socketio solo si está disponible
try:
    import socketio
    SOCKETIO_AVAILABLE = True
except ImportError:
    SOCKETIO_AVAILABLE = False

load_dotenv()

app = Flask(__name__)

# Configuración para Twitch
TWITCH_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET", "djs8Dd01Ad28k38z")

# Tokens de Socket API de Streamlabs
SOCKET_TOKENS = {
    "xstellar_": os.getenv("STREAMLABS_SOCKET_XSTELLAR"),
    "andresmanueh": os.getenv("STREAMLABS_SOCKET_ANDRES")
}

# Cliente Socket global
streamlabs_clients = {}

# Template del overlay limpio (sin partículas)
OVERLAY_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Subathon Timer Overlay</title>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: 'Segoe UI', 'Arial Black', sans-serif;
            overflow: hidden;
            position: relative;
            width: 100vw;
            height: 100vh;
        }

        .timer-container {
            position: absolute;
            top: 50px;
            right: 50px;
            text-align: center;
            z-index: 10;
        }

        .timer-main {
            font-size: 4em;
            font-weight: 900;
            text-shadow: 
                0 0 10px rgba(255, 255, 255, 0.8),
                0 0 20px rgba(255, 255, 255, 0.6),
                0 0 30px rgba(255, 255, 255, 0.4),
                4px 4px 8px rgba(0, 0, 0, 0.8);
            color: white;
            letter-spacing: 0.05em;
            transition: all 0.3s ease;
            filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.7));
        }

        .timer-main.paused {
            color: rgb(255, 107, 107);
            animation: pulse-red 2s infinite;
        }

        .timer-main.danger {
            color: rgb(255, 71, 87);
            animation: danger-pulse 1s infinite;
        }

        .timer-main.warning {
            color: rgb(255, 165, 2);
            animation: warning-glow 2s infinite;
        }

        .timer-label {
            font-size: 1.2em;
            font-weight: 600;
            margin-top: 10px;
            color: white;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
            opacity: 0.9;
        }

        /* Animaciones */
        @keyframes pulse-red {
            0%, 100% { 
                color: rgb(255, 107, 107);
                text-shadow: 0 0 20px rgba(255, 107, 107, 0.8);
            }
            50% { 
                color: rgb(255, 82, 82);
                text-shadow: 0 0 30px rgba(255, 82, 82, 1);
            }
        }

        @keyframes danger-pulse {
            0%, 100% { 
                color: rgb(255, 71, 87);
                transform: scale(1);
                text-shadow: 0 0 25px rgba(255, 71, 87, 1);
            }
            50% { 
                color: rgb(255, 56, 56);
                transform: scale(1.05);
                text-shadow: 0 0 35px rgba(255, 56, 56, 1);
            }
        }

        @keyframes warning-glow {
            0%, 100% { 
                color: rgb(255, 165, 2);
                text-shadow: 0 0 20px rgba(255, 165, 2, 0.8);
            }
            50% { 
                color: rgb(255, 149, 0);
                text-shadow: 0 0 30px rgba(255, 149, 0, 1);
            }
        }

        /* Efectos de tiempo añadido */
        .time-added-effect {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 2em;
            font-weight: bold;
            color: rgb(76, 175, 80);
            text-shadow: 0 0 20px rgba(76, 175, 80, 0.8);
            animation: time-added-animation 2s ease-out forwards;
            pointer-events: none;
            z-index: 20;
        }

        @keyframes time-added-animation {
            0% {
                opacity: 0;
                transform: translate(-50%, -50%) scale(0.5);
            }
            20% {
                opacity: 1;
                transform: translate(-50%, -50%) scale(1.2);
            }
            100% {
                opacity: 0;
                transform: translate(-50%, -100%) scale(1);
            }
        }

        @media (max-width: 1200px) {
            .timer-main { font-size: 3em; }
            .timer-container { top: 30px; right: 30px; }
        }
    </style>
</head>
<body>
    <div class="timer-container">
        <div id="timer" class="timer-main">00:00:00</div>
        <div id="label" class="timer-label">SUBATHON TIMER</div>
    </div>

    <script>
        let lastTime = '';
        let lastTimeValue = 0;

        function parseTimeToSeconds(timeStr) {
            const parts = timeStr.split(':').map(Number);
            return parts.length === 3 ? parts[0] * 3600 + parts[1] * 60 + parts[2] : 0;
        }

        function showTimeAddedEffect(addedMinutes) {
            const effect = document.createElement('div');
            effect.className = 'time-added-effect';
            effect.textContent = `+${addedMinutes} min!`;
            document.body.appendChild(effect);
            
            setTimeout(() => {
                if (effect.parentNode) document.body.removeChild(effect);
            }, 2000);
        }

        function updateTimer() {
            fetch('/api/time')
                .then(response => response.json())
                .then(data => {
                    const timerElement = document.getElementById('timer');
                    const labelElement = document.getElementById('label');
                    const currentTime = data.time;
                    const currentTimeValue = parseTimeToSeconds(currentTime);
                    
                    // Detectar tiempo añadido
                    if (lastTime && currentTimeValue > lastTimeValue + 5) {
                        const addedSeconds = currentTimeValue - lastTimeValue;
                        const addedMinutes = Math.round(addedSeconds / 60);
                        showTimeAddedEffect(addedMinutes);
                    }
                    
                    timerElement.textContent = currentTime;
                    timerElement.className = 'timer-main';
                    
                    if (data.paused) {
                        timerElement.classList.add('paused');
                        labelElement.textContent = '⏸ PAUSADO';
                    } else {
                        if (currentTimeValue <= 1800) timerElement.classList.add('danger');
                        else if (currentTimeValue <= 3600) timerElement.classList.add('warning');
                        labelElement.textContent = 'SUBATHON TIMER';
                    }
                    
                    lastTime = currentTime;
                    lastTimeValue = currentTimeValue;
                })
                .catch(error => {
                    console.error('Error fetching time:', error);
                    document.getElementById('timer').textContent = 'ERROR';
                });
        }

        updateTimer();
        setInterval(updateTimer, 1000);
    </script>
</body>
</html>
"""

# Interfaz completa restaurada
MAIN_INTERFACE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Subathon Control Panel</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            background: linear-gradient(to bottom right, rgb(30, 60, 114), rgb(42, 82, 152));
            color: white; 
            text-align: center; 
            font-family: 'Segoe UI', sans-serif; 
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        
        .timer-display {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2em;
            margin: 2em 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }
        
        h1 { 
            font-size: 5em; 
            margin: 0.2em 0; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            transition: all 0.3s ease;
        }
        
        .paused {
            color: rgb(255, 107, 107);
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0.7; }
        }
        
        .controls-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1em;
            margin: 2em 0;
        }
        
        button {
            background: linear-gradient(to bottom right, rgb(102, 126, 234), rgb(118, 75, 162));
            color: white; 
            padding: 1em 2em; 
            border: none; 
            border-radius: 12px; 
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }
        
        .btn-add { background: linear-gradient(to bottom right, rgb(76, 175, 80), rgb(69, 160, 73)); }
        .btn-pause { background: linear-gradient(to bottom right, rgb(255, 152, 0), rgb(230, 137, 0)); }
        .btn-resume { background: linear-gradient(to bottom right, rgb(33, 150, 243), rgb(25, 118, 210)); }
        .btn-set { background: linear-gradient(to bottom right, rgb(156, 39, 176), rgb(123, 31, 162)); }
        
        .status-bar {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1em;
            margin: 2em 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1em;
        }
        
        .status-item {
            text-align: center;
        }
        
        .status-value {
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 0.5em;
        }
        
        .overlay-links {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 15px;
            padding: 1.5em;
            margin: 2em 0;
        }
        
        .overlay-links h3 {
            margin-top: 0;
            color: rgb(76, 175, 80);
        }
        
        .link-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1em;
            margin-top: 1em;
        }
        
        .overlay-link {
            background: rgba(255, 255, 255, 0.1);
            padding: 1em;
            border-radius: 8px;
            text-decoration: none;
            color: white;
            transition: all 0.3s ease;
        }
        
        .overlay-link:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        
        .manual-controls {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1.5em;
            margin: 2em 0;
        }
        
        .input-group {
            display: flex;
            gap: 1em;
            justify-content: center;
            align-items: center;
            margin: 1em 0;
            flex-wrap: wrap;
        }
        
        input[type="number"] {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.2);
            padding: 0.8em;
            border-radius: 8px;
            font-size: 1em;
            width: 120px;
        }
        
        input[type="number"]:focus {
            outline: none;
            border-color: rgb(76, 175, 80);
        }
        
        .connected { color: rgb(76, 175, 80); }
        .disconnected { color: rgb(255, 107, 107); }
    </style>
</head>
<body>
    <div class="container">
        <div class="timer-display">
            <h1 id="timer">00:00:00</h1>
            <div class="status" id="status">Cargando...</div>
        </div>
        
        <div class="status-bar">
            <div class="status-item">
                <div class="status-value">🎮</div>
                <div>Twitch EventSub</div>
                <div class="connected">Conectado</div>
            </div>
            <div class="status-item">
                <div class="status-value" id="socket-status">💰</div>
                <div>Streamlabs Socket</div>
                <div id="socket-text" class="disconnected">Desconectado</div>
            </div>
        </div>
        
        <div class="controls-grid">
            <button class="btn-add" onclick="addTime(5)">+5 minutos</button>
            <button class="btn-add" onclick="addTime(10)">+10 minutos</button>
            <button class="btn-add" onclick="addTime(30)">+30 minutos</button>
            <button class="btn-pause" onclick="pauseTimer()">⏸ Pausar</button>
            <button class="btn-resume" onclick="resumeTimer()">▶️ Reanudar</button>
        </div>
        
        <div class="manual-controls">
            <h3>Control Manual</h3>
            <div class="input-group">
                <input type="number" id="customMinutes" placeholder="Minutos" min="1" max="999">
                <button class="btn-add" onclick="addCustomTime()">Añadir Tiempo</button>
            </div>
            <div class="input-group">
                <input type="number" id="setMinutes" placeholder="Tiempo total" min="1" max="9999">
                <button class="btn-set" onclick="setTime()">Establecer Timer</button>
            </div>
        </div>
        
        <div class="overlay-links">
            <h3>🎬 Enlace para OBS Studio</h3>
            <div class="link-grid">
                <a href="/overlay" target="_blank" class="overlay-link">
                    <strong>⏱️ Timer Overlay</strong><br>
                    Timer con efectos y animaciones
                </a>
            </div>
            <p style="font-size: 0.9em; opacity: 0.8; margin-top: 1em;">
                💡 Copia este enlace como "Browser Source" en OBS Studio
            </p>
        </div>
    </div>

    <script>
        let isUpdating = false;

        function fetchTime() {
            if (isUpdating) return;
            
            fetch("/api/time")
                .then(response => response.json())
                .then(data => {
                    const timerElement = document.getElementById("timer");
                    const statusElement = document.getElementById("status");
                    
                    timerElement.textContent = data.time;
                    
                    if (data.paused) {
                        timerElement.className = "paused";
                        statusElement.innerHTML = "⏸ <strong>PAUSADO</strong>";
                        statusElement.style.color = "rgb(255, 107, 107)";
                    } else {
                        timerElement.className = "";
                        statusElement.innerHTML = "▶️ <strong>EN VIVO</strong>";
                        statusElement.style.color = "rgb(76, 175, 80)";
                    }
                })
                .catch(error => {
                    console.error('Error fetching time:', error);
                    document.getElementById("status").textContent = "❌ Error de conexión";
                });
        }

        function checkSocketStatus() {
            fetch("/socket_status")
                .then(response => response.json())
                .then(data => {
                    const statusElement = document.getElementById("socket-text");
                    if (data.connected > 0) {
                        statusElement.textContent = "Conectado (" + data.connected + ")";
                        statusElement.className = "connected";
                    } else {
                        statusElement.textContent = "Desconectado";
                        statusElement.className = "disconnected";
                    }
                })
                .catch(error => {
                    document.getElementById("socket-text").textContent = "Error";
                });
        }

        function addTime(mins) {
            isUpdating = true;
            fetch("/add_time", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ minutes: mins })
            })
            .then(() => fetchTime())
            .finally(() => isUpdating = false);
        }

        function addCustomTime() {
            const input = document.getElementById("customMinutes");
            const minutes = parseInt(input.value);
            
            if (minutes && minutes > 0) {
                addTime(minutes);
                input.value = "";
            } else {
                alert("Por favor introduce un número válido");
            }
        }

        function setTime() {
            const input = document.getElementById("setMinutes");
            const minutes = parseInt(input.value);
            
            if (minutes && minutes > 0) {
                isUpdating = true;
                fetch("/set_time", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ minutes: minutes })
                })
                .then(() => {
                    fetchTime();
                    input.value = "";
                })
                .finally(() => isUpdating = false);
            }
        }

        function pauseTimer() {
            isUpdating = true;
            fetch("/pause", { method: "POST" })
                .then(() => fetchTime())
                .finally(() => isUpdating = false);
        }

        function resumeTimer() {
            isUpdating = true;
            fetch("/resume", { method: "POST" })
                .then(() => fetchTime())
                .finally(() => isUpdating = false);
        }

        // Event listeners para Enter
        document.getElementById("customMinutes").addEventListener("keypress", function(e) {
            if (e.key === "Enter") addCustomTime();
        });
        
        document.getElementById("setMinutes").addEventListener("keypress", function(e) {
            if (e.key === "Enter") setTime();
        });

        // Actualizar datos
        setInterval(fetchTime, 1000);
        setInterval(checkSocketStatus, 5000);
        fetchTime();
        checkSocketStatus();
    </script>
</body>
</html>
"""

# ================================
# STREAMLABS SOCKET CLIENT
# ================================

def setup_streamlabs_socket():
    """Configura clientes Socket de Streamlabs integrados"""
    if not SOCKETIO_AVAILABLE:
        print("⚠️ python-socketio no está instalado. Socket API deshabilitado.")
        return
    
    connected_count = 0
    
    for channel, token in SOCKET_TOKENS.items():
        if not token or token.startswith("tu_socket_token_"):
            print(f"⚠️ Token no configurado para {channel}")
            continue
            
        try:
            sio = socketio.Client()
            
            @sio.event
            def connect():
                print(f"🎉 Socket conectado - {channel}")
                
            @sio.event  
            def disconnect():
                print(f"🔌 Socket desconectado - {channel}")
            
            @sio.event
            def event(data):
                try:
                    event_type = data.get('type')
                    
                    if event_type == 'donation':
                        process_streamlabs_donation(data, channel)
                    elif event_type == 'follow':
                        print(f"👥 [{channel}] FOLLOW: {data.get('message', [{}])[0].get('name', 'Anónimo')}")
                except Exception as e:
                    print(f"❌ Error procesando evento {channel}: {e}")
            
            url = f"https://sockets.streamlabs.com?token={token}"
            sio.connect(url)
            streamlabs_clients[channel] = sio
            connected_count += 1
            
        except Exception as e:
            print(f"❌ Error conectando Socket {channel}: {e}")
    
    if connected_count > 0:
        print(f"✅ {connected_count} canal(es) Socket conectado(s)")
    
    return connected_count

def process_streamlabs_donation(data, channel):
    """Procesa donaciones de Streamlabs"""
    try:
        messages = data.get('message', [])
        
        for donation in messages:
            amount = float(donation.get('amount', 0))
            name = donation.get('name', 'Anónimo')
            message = donation.get('message', '')
            currency = donation.get('currency', 'USD')
            
            if currency == 'EUR':
                amount_eur = amount
            elif currency == 'USD':
                amount_eur = amount * 0.85
            else:
                amount_eur = amount
            
            minutes = int(amount_eur * 10)
            
            print(f"💰 [{channel}] DONACIÓN Socket: {name} donó {amount} {currency} → +{minutes} min")
            if message:
                print(f"   💬 Mensaje: {message}")
            
            timer.add_time(minutes)
            
    except Exception as e:
        print(f"❌ Error procesando donación Socket {channel}: {e}")

@app.route("/")
def index():
    return render_template_string(MAIN_INTERFACE_TEMPLATE)

@app.route("/overlay")
def overlay():
    return render_template_string(OVERLAY_TEMPLATE)

@app.route("/api/time")
def api_time():
    try:
        remaining = timer.get_remaining()
        time_str = timer.format_time(remaining)
        
        return jsonify({
            "time": time_str,
            "paused": timer.is_paused(),
            "status": "ok"
        })
    except Exception as e:
        return jsonify({
            "time": "00:00:00",
            "paused": False,
            "status": "error"
        }), 500

@app.route("/socket_status")
def socket_status():
    connected = len([c for c in streamlabs_clients.values() if c.connected])
    return jsonify({
        "connected": connected,
        "total": len(SOCKET_TOKENS),
        "channels": list(streamlabs_clients.keys())
    })

@app.route("/add_time", methods=["POST"])
def add_time():
    try:
        data = request.get_json()
        minutes = data.get("minutes", 0)
        
        if minutes <= 0:
            return jsonify({"status": "error", "message": "Minutes must be positive"}), 400
            
        timer.add_time(minutes)
        return jsonify({"status": "ok", "added": minutes})
    except Exception as e:
        print(f"Error en /add_time: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/set_time", methods=["POST"])
def set_time():
    try:
        data = request.get_json()
        minutes = data.get("minutes", 0)
        
        if minutes <= 0:
            return jsonify({"status": "error", "message": "Minutes must be positive"}), 400
            
        timer.set_time(minutes)
        return jsonify({"status": "ok", "set_to": minutes})
    except Exception as e:
        print(f"Error en /set_time: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/pause", methods=["POST"])
def pause():
    try:
        timer.pause()
        return jsonify({"status": "paused"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/resume", methods=["POST"])
def resume():
    try:
        timer.resume()
        return jsonify({"status": "resumed"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Webhooks
@app.route("/webhook", methods=["POST"])
def handle_donation():
    try:
        data = request.json
        print("[DONACIÓN] Webhook recibido:")
        print(json.dumps(data, indent=2))

        messages = data.get("message", [])
        for donation in messages:
            amount = float(donation.get("amount", 0))
            nombre = donation.get("from", "Desconocido")
            minutos = int(amount * 10)

            print(f"[DONACIÓN] Webhook: {nombre} donó {amount}€ → +{minutos} minutos")
            timer.add_time(minutos)

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"❌ Error procesando donación webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/twitch", methods=["POST"])
def twitch_webhook():
    try:
        data = request.json
        event_type = request.headers.get("Twitch-Eventsub-Message-Type")

        if event_type == "webhook_callback_verification":
            return data.get("challenge", ""), 200

        event = data.get("event", {})
        subscription_type = data.get("subscription", {}).get("type")
        user = event.get("broadcaster_user_name", "").lower()

        if subscription_type == "channel.subscribe":
            print(f"[SUB] Nueva suscripción en {user}")
            timer.add_time(30)
        elif subscription_type == "channel.cheer":
            bits = int(event.get("bits", 0))
            minutos = (bits // 100) * 10
            print(f"[BITS] {bits} bits en {user} → +{minutos} minutos")
            timer.add_time(minutos)

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"❌ Error procesando evento de Twitch: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/health")
def health():
    try:
        remaining = timer.get_remaining()
        time_str = timer.format_time(remaining)
        
        return jsonify({
            "status": "ok",
            "timer_running": True,
            "current_time": time_str,
            "is_paused": timer.is_paused(),
            "streamlabs_connected": len(streamlabs_clients)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print("🚀 Iniciando servidor con overlays integrados...")
    
    def start_socket_api():
        time.sleep(2)
        setup_streamlabs_socket()
    
    socket_thread = threading.Thread(target=start_socket_api, daemon=True)
    socket_thread.start()
    
    print("🌐 Interfaz principal: http://localhost:5000")
    print("⏱️  Overlay timer: http://localhost:5000/overlay")
    print("💰 Webhook donaciones: http://localhost:5000/webhook")
    print("🎮 Webhook Twitch: http://localhost:5000/twitch")
    
    app.run(host="0.0.0.0", port=5000, debug=False)