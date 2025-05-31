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

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Subathon Timer</title>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { 
            background: #111; 
            color: white; 
            text-align: center; 
            font-family: 'Segoe UI', sans-serif; 
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 { 
            font-size: 5em; 
            margin: 0.5em 0; 
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        .paused {
            color: #ff6b6b;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0.5; }
        }
        .controls {
            margin: 2em 0;
        }
        button {
            background: #333; 
            color: white; 
            padding: 1em 2em; 
            margin: 0.5em;
            border: none; 
            border-radius: 8px; 
            font-size: 1.2em;
            cursor: pointer;
            transition: all 0.3s ease;
            min-width: 120px;
        }
        button:hover { 
            background: #555; 
            transform: translateY(-2px);
        }
        button:active {
            transform: translateY(0);
        }
        .btn-add { background: #4CAF50; }
        .btn-add:hover { background: #45a049; }
        .btn-pause { background: #ff9800; }
        .btn-pause:hover { background: #e68900; }
        .btn-resume { background: #2196F3; }
        .btn-resume:hover { background: #1976D2; }
        .status {
            margin: 1em 0;
            font-size: 1.2em;
            opacity: 0.8;
        }
        .manual-add {
            margin: 2em 0;
            padding: 1em;
            background: #222;
            border-radius: 8px;
        }
        .manual-add input {
            background: #333;
            color: white;
            border: 1px solid #555;
            padding: 0.5em;
            margin: 0.5em;
            border-radius: 4px;
            font-size: 1em;
        }
        .connection-status {
            margin: 1em 0;
            padding: 0.5em;
            background: #333;
            border-radius: 4px;
            font-size: 0.9em;
        }
        .connected { color: #4CAF50; }
        .disconnected { color: #ff6b6b; }
    </style>
</head>
<body>
    <div class="container">
        <h1 id="timer">00:00:00</h1>
        <div class="status" id="status">Cargando...</div>
        
        <div class="connection-status">
            <div>🎮 Twitch EventSub: <span class="connected">Conectado</span></div>
            <div id="streamlabs-status">💰 Streamlabs Socket: <span id="socket-status" class="disconnected">Desconectado</span></div>
        </div>
        
        <div class="controls">
            <button class="btn-add" onclick="addTime(5)">+5 min</button>
            <button class="btn-add" onclick="addTime(10)">+10 min</button>
            <button class="btn-add" onclick="addTime(30)">+30 min</button>
        </div>
        
        <div class="controls">
            <button class="btn-pause" onclick="pauseTimer()">⏸ Pausar</button>
            <button class="btn-resume" onclick="resumeTimer()">▶️ Reanudar</button>
        </div>
        
        <div class="manual-add">
            <div style="margin-bottom: 1em;">
                <input type="number" id="customMinutes" placeholder="Minutos" min="1" max="999">
                <button onclick="addCustomTime()">Añadir tiempo</button>
            </div>
            <div>
                <input type="number" id="setMinutes" placeholder="Establecer tiempo total" min="1" max="9999">
                <button onclick="setTime()" style="background: #9C27B0;">Establecer timer</button>
            </div>
        </div>
    </div>

    <script>
        let isUpdating = false;

        function fetchTime() {
            if (isUpdating) return;
            
            fetch("/api/time")
                .then(response => {
                    if (!response.ok) throw new Error('Network error');
                    return response.json();
                })
                .then(data => {
                    const timerElement = document.getElementById("timer");
                    const statusElement = document.getElementById("status");
                    
                    timerElement.textContent = data.time;
                    
                    if (data.paused) {
                        timerElement.className = "paused";
                        statusElement.textContent = "⏸ PAUSADO";
                        statusElement.style.color = "#ff6b6b";
                    } else {
                        timerElement.className = "";
                        statusElement.textContent = "▶️ EN VIVO";
                        statusElement.style.color = "#4CAF50";
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
                    const statusElement = document.getElementById("socket-status");
                    if (data.connected > 0) {
                        statusElement.textContent = `Conectado (${data.connected} canales)`;
                        statusElement.className = "connected";
                    } else {
                        statusElement.textContent = "Desconectado";
                        statusElement.className = "disconnected";
                    }
                })
                .catch(error => {
                    document.getElementById("socket-status").textContent = "Error";
                });
        }

        function addTime(mins) {
            isUpdating = true;
            fetch("/add_time", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ minutes: mins })
            })
            .then(response => response.json())
            .then(data => {
                console.log(`Añadidos ${mins} minutos`);
                fetchTime();
            })
            .catch(error => console.error('Error adding time:', error))
            .finally(() => {
                isUpdating = false;
            });
        }

        function addCustomTime() {
            const input = document.getElementById("customMinutes");
            const minutes = parseInt(input.value);
            
            if (minutes && minutes > 0) {
                addTime(minutes);
                input.value = "";
            } else {
                alert("Por favor introduce un número válido de minutos");
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
                .then(response => response.json())
                .then(data => {
                    console.log(`Timer establecido a ${minutes} minutos`);
                    fetchTime();
                    input.value = "";
                })
                .catch(error => console.error('Error setting time:', error))
                .finally(() => {
                    isUpdating = false;
                });
            } else {
                alert("Por favor introduce un número válido de minutos");
            }
        }

        function pauseTimer() {
            isUpdating = true;
            fetch("/pause", { method: "POST" })
                .then(response => response.json())
                .then(data => {
                    console.log("Timer pausado");
                    fetchTime();
                })
                .catch(error => console.error('Error pausing:', error))
                .finally(() => {
                    isUpdating = false;
                });
        }

        function resumeTimer() {
            isUpdating = true;
            fetch("/resume", { method: "POST" })
                .then(response => response.json())
                .then(data => {
                    console.log("Timer reanudado");
                    fetchTime();
                })
                .catch(error => console.error('Error resuming:', error))
                .finally(() => {
                    isUpdating = false;
                });
        }

        // Permitir enter en los inputs
        document.getElementById("customMinutes").addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                addCustomTime();
            }
        });
        
        document.getElementById("setMinutes").addEventListener("keypress", function(event) {
            if (event.key === "Enter") {
                setTime();
            }
        });

        // Actualizar cada segundo
        setInterval(fetchTime, 1000);
        setInterval(checkSocketStatus, 5000);
        
        // Primera carga
        fetchTime();
        checkSocketStatus();
    </script>
</body>
</html>
"""

# ================================
# STREAMLABS SOCKET CLIENT INTEGRADO
# ================================

def setup_streamlabs_socket():
    """Configura clientes Socket de Streamlabs integrados"""
    if not SOCKETIO_AVAILABLE:
        print("⚠️ python-socketio no está instalado. Socket API deshabilitado.")
        return
    
    connected_count = 0
    
    for channel, token in SOCKET_TOKENS.items():
        if token.startswith("tu_socket_token_"):
            print(f"⚠️ Token no configurado para {channel}")
            continue
            
        try:
            # Crear cliente Socket.IO
            sio = socketio.Client()
            
            @sio.event
            def connect():
                print(f"🎉 Socket conectado - {channel}")
                
            @sio.event  
            def disconnect():
                print(f"🔌 Socket desconectado - {channel}")
            
            @sio.event
            def event(data):
                """Procesa eventos de Streamlabs"""
                try:
                    event_type = data.get('type')
                    
                    if event_type == 'donation':
                        process_streamlabs_donation(data, channel)
                    elif event_type == 'follow':
                        print(f"👥 [{channel}] FOLLOW: {data.get('message', [{}])[0].get('name', 'Anónimo')}")
                    else:
                        print(f"📝 [{channel}] Evento no procesado: {event_type}")
                        
                except Exception as e:
                    print(f"❌ Error procesando evento {channel}: {e}")
            
            # Conectar
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
    """Procesa donaciones de Streamlabs usando el timer compartido"""
    try:
        messages = data.get('message', [])
        
        for donation in messages:
            amount = float(donation.get('amount', 0))
            name = donation.get('name', 'Anónimo')
            message = donation.get('message', '')
            currency = donation.get('currency', 'USD')
            
            # Conversión de moneda simplificada
            if currency == 'EUR':
                amount_eur = amount
            elif currency == 'USD':
                amount_eur = amount * 0.85
            else:
                amount_eur = amount
            
            # 10 minutos por euro
            minutes = int(amount_eur * 10)
            
            print(f"💰 [{channel}] DONACIÓN Socket: {name} donó {amount} {currency} → +{minutes} min")
            if message:
                print(f"   💬 Mensaje: {message}")
            
            # ✅ USAR EL TIMER COMPARTIDO
            timer.add_time(minutes)
            
    except Exception as e:
        print(f"❌ Error procesando donación Socket {channel}: {e}")

# ================================
# RUTAS DE LA API
# ================================

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

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
        print(f"Error en /api/time: {e}")
        return jsonify({
            "time": "00:00:00",
            "paused": False,
            "status": "error"
        }), 500

@app.route("/socket_status")
def socket_status():
    """Estado de conexiones Socket"""
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
        print(f"Error en /pause: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/resume", methods=["POST"])
def resume():
    try:
        timer.resume()
        return jsonify({"status": "resumed"})
    except Exception as e:
        print(f"Error en /resume: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ================================
# WEBHOOKS DE DONACIONES (BACKUP)
# ================================

@app.route("/webhook", methods=["POST"])
def handle_donation():
    """Webhook para donaciones - backup del Socket API"""
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

# ================================
# EVENTOS DE TWITCH
# ================================

@app.route("/twitch", methods=["POST"])
def twitch_webhook():
    """Webhook para eventos de Twitch EventSub"""
    try:
        raw_body = request.data.decode("utf-8")
        headers = request.headers
        
        print("📡 Evento de Twitch recibido")
        
        data = request.json
        event_type = headers.get("Twitch-Eventsub-Message-Type")

        if event_type == "webhook_callback_verification":
            challenge = data.get("challenge", "")
            print(f"✅ Verificación de webhook: {challenge}")
            return challenge, 200

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
    print("🚀 Iniciando servidor consolidado con Socket API...")
    
    # Configurar Socket API en hilo separado
    def start_socket_api():
        time.sleep(2)  # Esperar a que Flask se inicie
        setup_streamlabs_socket()
    
    socket_thread = threading.Thread(target=start_socket_api, daemon=True)
    socket_thread.start()
    
    print("🌐 Interfaz web: http://localhost:5000")
    print("💰 Webhook donaciones: http://localhost:5000/webhook") 
    print("🎮 Webhook Twitch: http://localhost:5000/twitch")
    print("📊 Estado: http://localhost:5000/health")
    
    app.run(host="0.0.0.0", port=5000, debug=False)