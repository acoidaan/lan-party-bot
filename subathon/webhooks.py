from flask import Flask, jsonify, request, render_template_string
from timer_instance import timer
import json
import hmac
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configuración para Twitch
TWITCH_SECRET = os.getenv("TWITCH_EVENTSUB_SECRET", "djs8Dd01Ad28k38z")

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
        .endpoints-info {
            margin: 2em 0;
            padding: 1em;
            background: #222;
            border-radius: 8px;
            font-size: 0.9em;
            text-align: left;
        }
        .endpoint {
            margin: 0.5em 0;
            padding: 0.5em;
            background: #333;
            border-radius: 4px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 id="timer">00:00:00</h1>
        <div class="status" id="status">Cargando...</div>
        
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

        <div class="endpoints-info">
            <h3>📡 Endpoints Disponibles:</h3>
            <div class="endpoint">🎥 Interfaz Web: {{ base_url }}/</div>
            <div class="endpoint">💰 Donaciones: {{ base_url }}/webhook</div>
            <div class="endpoint">🎮 Twitch Events: {{ base_url }}/twitch</div>
            <div class="endpoint">🔗 Auth Callback: {{ base_url }}/callback</div>
            <div class="endpoint">📊 API Status: {{ base_url }}/health</div>
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
        
        // Primera carga
        fetchTime();
    </script>
</body>
</html>
"""

def verify_twitch_signature(headers, body):
    """Verifica la firma de Twitch EventSub"""
    message_id = headers.get("Twitch-Eventsub-Message-Id")
    timestamp = headers.get("Twitch-Eventsub-Message-Timestamp")
    signature = headers.get("Twitch-Eventsub-Message-Signature")

    if not all([message_id, timestamp, signature]):
        return False

    hmac_message = message_id + timestamp + body
    expected_signature = "sha256=" + hmac.new(
        TWITCH_SECRET.encode("utf-8"),
        hmac_message.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected_signature)

# ================================
# INTERFAZ WEB PRINCIPAL
# ================================

@app.route("/")
def index():
    base_url = request.host_url.rstrip('/')
    return render_template_string(HTML_TEMPLATE, base_url=base_url)

@app.route("/api/time")
def api_time():
    try:
        remaining = timer.get_remaining()
        # ✅ USAR EL MÉTODO DE FORMATO DEL TIMER
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
# WEBHOOKS DE DONACIONES
# ================================

@app.route("/webhook", methods=["POST"])
def handle_donation():
    """Webhook para donaciones de Streamlabs"""
    try:
        data = request.json
        print("[DONACIÓN] Evento recibido:")
        print(json.dumps(data, indent=2))

        # Procesar donaciones de Streamlabs
        messages = data.get("message", [])
        for donation in messages:
            amount = float(donation.get("amount", 0))
            nombre = donation.get("from", "Desconocido")
            minutos = int(amount * 10)  # 10 minutos por euro

            print(f"[DONACIÓN] {nombre} donó {amount}€ → +{minutos} minutos")
            timer.add_time(minutos)

        return jsonify({"status": "ok"}), 200
    except Exception as e:
        print(f"❌ Error procesando donación: {e}")
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

        # Verificación de webhook (requerido por Twitch)
        if event_type == "webhook_callback_verification":
            challenge = data.get("challenge", "")
            print(f"✅ Verificación de webhook: {challenge}")
            return challenge, 200

        # Procesar eventos
        event = data.get("event", {})
        subscription_type = data.get("subscription", {}).get("type")
        user = event.get("broadcaster_user_name", "").lower()

        if subscription_type == "channel.subscribe":
            print(f"[SUB] Nueva suscripción en {user}")
            timer.add_time(30)  # 30 minutos por sub

        elif subscription_type == "channel.cheer":
            bits = int(event.get("bits", 0))
            minutos = (bits // 100) * 10  # 10 min cada 100 bits
            print(f"[BITS] {bits} bits en {user} → +{minutos} minutos")
            timer.add_time(minutos)

        return jsonify({"status": "ok"}), 200
        
    except Exception as e:
        print(f"❌ Error procesando evento de Twitch: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# ================================
# AUTENTICACIÓN DE TWITCH
# ================================

@app.route("/auth")
def twitch_auth():
    """Inicia el proceso de autenticación con Twitch"""
    CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
    REDIRECT_URI = os.getenv("TWITCH_REDIRECT_URI")
    SCOPES = os.getenv("TWITCH_SCOPES")
    
    auth_url = (
        f"https://id.twitch.tv/oauth2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={SCOPES}"
    )
    
    return f'<a href="{auth_url}">Autorizar con Twitch</a>'

@app.route("/callback")
def auth_callback():
    """Callback de autenticación de Twitch"""
    code = request.args.get("code")
    if not code:
        return "Error: No se recibió código de autorización", 400
    
    return "Autorización completada. Puedes cerrar esta pestaña."

# ================================
# ENDPOINTS DE ESTADO
# ================================

@app.route("/health")
def health():
    """Endpoint para verificar estado del sistema"""
    try:
        remaining = timer.get_remaining()
        time_str = timer.format_time(remaining)
        
        return jsonify({
            "status": "ok",
            "timer_running": True,
            "current_time": time_str,
            "is_paused": timer.is_paused(),
            "endpoints": {
                "web_interface": "/",
                "donations": "/webhook",
                "twitch_events": "/twitch",
                "twitch_auth": "/auth",
                "api_time": "/api/time",
                "add_time": "/add_time",
                "set_time": "/set_time"
            }
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route("/test")
def test_endpoints():
    """Endpoint para testear que todo funciona"""
    try:
        remaining = timer.get_remaining()
        time_str = timer.format_time(remaining)
        
        return jsonify({
            "message": "¡Todos los servicios están funcionando!",
            "timer": time_str,
            "paused": timer.is_paused(),
            "available_endpoints": [
                "/ - Interfaz web",
                "/webhook - Donaciones", 
                "/twitch - Eventos Twitch",
                "/health - Estado del sistema",
                "/api/time - API del timer",
                "/add_time - Añadir tiempo",
                "/set_time - Establecer tiempo"
            ]
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    print("🚀 Iniciando servidor consolidado en puerto 5000...")
    print("🌐 Interfaz web: http://localhost:5000")
    print("💰 Webhook donaciones: http://localhost:5000/webhook") 
    print("🎮 Webhook Twitch: http://localhost:5000/twitch")
    print("📊 Estado: http://localhost:5000/health")
    
    app.run(host="0.0.0.0", port=5000, debug=False)