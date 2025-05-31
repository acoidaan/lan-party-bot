# overlay_routes.py - Rutas para overlays separados
from flask import render_template_string

# ================================
# OVERLAY PRINCIPAL - SOLO TIMER
# ================================

OVERLAY_TIMER_TEMPLATE = """
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
            color: #ffffff;
            letter-spacing: 0.05em;
            transition: all 0.3s ease;
            filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.7));
        }

        .timer-main.paused {
            color: #ff6b6b;
            animation: pulse-red 2s infinite;
        }

        .timer-main.danger {
            color: #ff4757;
            animation: danger-pulse 1s infinite;
        }

        .timer-main.warning {
            color: #ffa502;
            animation: warning-glow 2s infinite;
        }

        .timer-label {
            font-size: 1.2em;
            font-weight: 600;
            margin-top: 10px;
            color: #ffffff;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
            opacity: 0.9;
        }

        /* Animaciones */
        @keyframes pulse-red {
            0%, 100% { 
                color: #ff6b6b;
                text-shadow: 0 0 20px rgba(255, 107, 107, 0.8);
            }
            50% { 
                color: #ff5252;
                text-shadow: 0 0 30px rgba(255, 82, 82, 1);
            }
        }

        @keyframes danger-pulse {
            0%, 100% { 
                color: #ff4757;
                transform: scale(1);
                text-shadow: 0 0 25px rgba(255, 71, 87, 1);
            }
            50% { 
                color: #ff3838;
                transform: scale(1.05);
                text-shadow: 0 0 35px rgba(255, 56, 56, 1);
            }
        }

        @keyframes warning-glow {
            0%, 100% { 
                color: #ffa502;
                text-shadow: 0 0 20px rgba(255, 165, 2, 0.8);
            }
            50% { 
                color: #ff9500;
                text-shadow: 0 0 30px rgba(255, 149, 0, 1);
            }
        }

        /* Efectos de partículas para tiempo añadido */
        .time-added-effect {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 2em;
            font-weight: bold;
            color: #4CAF50;
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

        /* Partículas de fondo (sutiles) */
        .particle {
            position: absolute;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            pointer-events: none;
            animation: float 6s infinite ease-in-out;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            33% { transform: translateY(-20px) rotate(120deg); }
            66% { transform: translateY(10px) rotate(240deg); }
        }

        /* Estilo para diferentes tamaños de pantalla */
        @media (max-width: 1200px) {
            .timer-main { font-size: 3em; }
            .timer-container { 
                top: 30px; 
                right: 30px; 
            }
        }

        @media (max-width: 800px) {
            .timer-main { font-size: 2.5em; }
            .timer-container { 
                top: 20px; 
                right: 20px; 
            }
        }
    </style>
</head>
<body>
    <div class="timer-container">
        <div id="timer" class="timer-main">00:00:00</div>
        <div id="label" class="timer-label">SUBATHON TIMER</div>
    </div>

    <!-- Partículas de fondo -->
    <div id="particles"></div>

    <script>
        let lastTime = '';
        let lastTimeValue = 0;

        // Crear partículas de fondo sutiles
        function createParticles() {
            const particlesContainer = document.getElementById('particles');
            
            for (let i = 0; i < 15; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                
                // Tamaño aleatorio
                const size = Math.random() * 4 + 2;
                particle.style.width = size + 'px';
                particle.style.height = size + 'px';
                
                // Posición aleatoria
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = Math.random() * 100 + '%';
                
                // Delay aleatorio
                particle.style.animationDelay = Math.random() * 6 + 's';
                
                particlesContainer.appendChild(particle);
            }
        }

        function parseTimeToSeconds(timeStr) {
            const parts = timeStr.split(':').map(Number);
            if (parts.length === 3) {
                return parts[0] * 3600 + parts[1] * 60 + parts[2];
            }
            return 0;
        }

        function showTimeAddedEffect(addedMinutes) {
            const effect = document.createElement('div');
            effect.className = 'time-added-effect';
            effect.textContent = `+${addedMinutes} min!`;
            document.body.appendChild(effect);
            
            setTimeout(() => {
                document.body.removeChild(effect);
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
                    
                    // Detectar si se añadió tiempo
                    if (lastTime && currentTimeValue > lastTimeValue + 5) {
                        const addedSeconds = currentTimeValue - lastTimeValue;
                        const addedMinutes = Math.round(addedSeconds / 60);
                        showTimeAddedEffect(addedMinutes);
                    }
                    
                    // Actualizar tiempo
                    timerElement.textContent = currentTime;
                    
                    // Cambiar estilos según estado
                    timerElement.className = 'timer-main';
                    
                    if (data.paused) {
                        timerElement.classList.add('paused');
                        labelElement.textContent = '⏸ PAUSADO';
                    } else {
                        // Determinar color según tiempo restante
                        if (currentTimeValue <= 1800) { // <30 min
                            timerElement.classList.add('danger');
                        } else if (currentTimeValue <= 3600) { // <1 hora
                            timerElement.classList.add('warning');
                        }
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

        // Inicializar
        createParticles();
        updateTimer();
        setInterval(updateTimer, 1000);
    </script>
</body>
</html>
"""

# ================================
# OVERLAY DE ALERTAS - SOLO EVENTOS
# ================================

OVERLAY_ALERTS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Subathon Alerts Overlay</title>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: 'Segoe UI', sans-serif;
            overflow: hidden;
            position: relative;
            width: 100vw;
            height: 100vh;
        }

        .alerts-container {
            position: absolute;
            bottom: 100px;
            left: 50px;
            right: 50px;
            z-index: 100;
        }

        .alert {
            background: linear-gradient(135deg, rgba(0, 0, 0, 0.9), rgba(0, 0, 0, 0.7));
            border-left: 6px solid #4CAF50;
            color: white;
            padding: 20px;
            margin-bottom: 10px;
            border-radius: 8px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            transform: translateX(-100%);
            animation: slideIn 0.5s ease-out forwards;
            max-width: 500px;
        }

        .alert.donation {
            border-left-color: #FFD700;
        }

        .alert.subscription {
            border-left-color: #9146FF;
        }

        .alert.follow {
            border-left-color: #1DA1F2;
        }

        .alert-icon {
            font-size: 1.5em;
            margin-right: 10px;
            vertical-align: middle;
        }

        .alert-content {
            display: inline-block;
            vertical-align: middle;
        }

        .alert-title {
            font-weight: bold;
            font-size: 1.2em;
            margin-bottom: 5px;
        }

        .alert-details {
            opacity: 0.9;
            font-size: 0.9em;
        }

        @keyframes slideIn {
            from {
                transform: translateX(-100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(-100%);
                opacity: 0;
            }
        }

        .alert.removing {
            animation: slideOut 0.5s ease-in forwards;
        }
    </style>
</head>
<body>
    <div class="alerts-container" id="alerts-container">
        <!-- Las alertas se añaden aquí dinámicamente -->
    </div>

    <script>
        let lastEventCheck = Date.now();

        function createAlert(type, data) {
            const alertsContainer = document.getElementById('alerts-container');
            const alert = document.createElement('div');
            alert.className = `alert ${type}`;
            
            let icon, title, details;
            
            switch(type) {
                case 'donation':
                    icon = '💰';
                    title = `¡${data.name} donó ${data.amount}€!`;
                    details = `+${data.minutes} minutos añadidos`;
                    if (data.message) {
                        details += ` • "${data.message}"`;
                    }
                    break;
                    
                case 'subscription':
                    icon = '🟣';
                    title = `¡${data.name} se suscribió!`;
                    details = '+30 minutos añadidos';
                    break;
                    
                case 'follow':
                    icon = '👥';
                    title = `¡${data.name} siguió el canal!`;
                    details = 'Nuevo seguidor';
                    break;
            }
            
            alert.innerHTML = `
                <span class="alert-icon">${icon}</span>
                <div class="alert-content">
                    <div class="alert-title">${title}</div>
                    <div class="alert-details">${details}</div>
                </div>
            `;
            
            alertsContainer.appendChild(alert);
            
            // Remover automáticamente después de 5 segundos
            setTimeout(() => {
                alert.classList.add('removing');
                setTimeout(() => {
                    if (alert.parentNode) {
                        alert.parentNode.removeChild(alert);
                    }
                }, 500);
            }, 5000);
        }

        // Simular eventos para testing (remover en producción)
        function simulateEvent() {
            const events = [
                { type: 'donation', data: { name: 'TestUser', amount: 15, minutes: 150, message: 'Great stream!' } },
                { type: 'subscription', data: { name: 'NewSub123' } },
                { type: 'follow', data: { name: 'NewFollower' } }
            ];
            
            const randomEvent = events[Math.floor(Math.random() * events.length)];
            createAlert(randomEvent.type, randomEvent.data);
        }

        // Para testing: simular eventos cada 10 segundos
        // setInterval(simulateEvent, 10000);
        
        // En producción, aquí conectarías con tu API para obtener eventos reales
        function checkForNewEvents() {
            // TODO: Implementar endpoint para obtener eventos recientes
            // fetch('/api/recent_events')
            //     .then(response => response.json())
            //     .then(events => {
            //         events.forEach(event => {
            //             createAlert(event.type, event.data);
            //         });
            //     });
        }

        // setInterval(checkForNewEvents, 2000);
    </script>
</body>
</html>
"""

# ================================
# OVERLAY COMBINADO - TODO EN UNO
# ================================

OVERLAY_COMBINED_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Subathon Full Overlay</title>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: 'Segoe UI', sans-serif;
            overflow: hidden;
            width: 100vw;
            height: 100vh;
            position: relative;
        }

        /* Timer en esquina superior derecha */
        .timer-container {
            position: absolute;
            top: 30px;
            right: 30px;
            text-align: center;
            z-index: 10;
            background: rgba(0, 0, 0, 0.3);
            padding: 15px 20px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }

        .timer-main {
            font-size: 2.5em;
            font-weight: 900;
            color: #ffffff;
            text-shadow: 0 0 15px rgba(255, 255, 255, 0.8), 2px 2px 4px rgba(0, 0, 0, 0.8);
            margin-bottom: 5px;
        }

        .timer-main.paused { color: #ff6b6b; animation: pulse 2s infinite; }
        .timer-main.danger { color: #ff4757; animation: danger-pulse 1s infinite; }
        .timer-main.warning { color: #ffa502; }

        .timer-label {
            font-size: 0.8em;
            color: #ffffff;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Alertas en parte inferior */
        .alerts-container {
            position: absolute;
            bottom: 50px;
            left: 50px;
            right: 350px;
            z-index: 20;
        }

        .alert {
            background: linear-gradient(135deg, rgba(0, 0, 0, 0.9), rgba(0, 0, 0, 0.7));
            border-left: 4px solid #4CAF50;
            color: white;
            padding: 15px;
            margin-bottom: 8px;
            border-radius: 6px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(10px);
            transform: translateX(-100%);
            animation: slideIn 0.4s ease-out forwards;
            max-width: 400px;
        }

        .alert.donation { border-left-color: #FFD700; }
        .alert.subscription { border-left-color: #9146FF; }

        /* Efectos de tiempo añadido */
        .time-boost {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 3em;
            font-weight: bold;
            color: #4CAF50;
            text-shadow: 0 0 20px rgba(76, 175, 80, 1);
            animation: boost-animation 2.5s ease-out forwards;
            pointer-events: none;
            z-index: 30;
        }

        /* Animaciones */
        @keyframes slideIn {
            from { transform: translateX(-100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }

        @keyframes danger-pulse {
            0%, 100% { transform: scale(1); color: #ff4757; }
            50% { transform: scale(1.05); color: #ff3838; }
        }

        @keyframes boost-animation {
            0% { opacity: 0; transform: translate(-50%, -50%) scale(0.5); }
            20% { opacity: 1; transform: translate(-50%, -50%) scale(1.3); }
            100% { opacity: 0; transform: translate(-50%, -100%) scale(1); }
        }
    </style>
</head>
<body>
    <!-- Timer Container -->
    <div class="timer-container">
        <div id="timer" class="timer-main">00:00:00</div>
        <div id="timer-label" class="timer-label">Subathon Timer</div>
    </div>

    <!-- Alerts Container -->
    <div class="alerts-container" id="alerts-container">
    </div>

    <script>
        let lastTime = '';
        let lastTimeValue = 0;

        function parseTimeToSeconds(timeStr) {
            const parts = timeStr.split(':').map(Number);
            return parts.length === 3 ? parts[0] * 3600 + parts[1] * 60 + parts[2] : 0;
        }

        function showTimeBoost(minutes) {
            const boost = document.createElement('div');
            boost.className = 'time-boost';
            boost.textContent = `+${minutes} MIN!`;
            document.body.appendChild(boost);
            
            setTimeout(() => {
                if (boost.parentNode) boost.parentNode.removeChild(boost);
            }, 2500);
        }

        function createAlert(type, data) {
            const container = document.getElementById('alerts-container');
            const alert = document.createElement('div');
            alert.className = `alert ${type}`;
            
            let content = '';
            if (type === 'donation') {
                content = `💰 <strong>${data.name}</strong> donó <strong>${data.amount}€</strong> (+${data.minutes} min)`;
            } else if (type === 'subscription') {
                content = `🟣 <strong>${data.name}</strong> se suscribió (+30 min)`;
            }
            
            alert.innerHTML = content;
            container.appendChild(alert);
            
            setTimeout(() => {
                alert.style.animation = 'slideIn 0.4s ease-in reverse';
                setTimeout(() => {
                    if (alert.parentNode) alert.parentNode.removeChild(alert);
                }, 400);
            }, 4000);
        }

        function updateTimer() {
            fetch('/api/time')
                .then(response => response.json())
                .then(data => {
                    const timerElement = document.getElementById('timer');
                    const labelElement = document.getElementById('timer-label');
                    const currentTime = data.time;
                    const currentTimeValue = parseTimeToSeconds(currentTime);
                    
                    // Detectar tiempo añadido
                    if (lastTime && currentTimeValue > lastTimeValue + 5) {
                        const addedMinutes = Math.round((currentTimeValue - lastTimeValue) / 60);
                        showTimeBoost(addedMinutes);
                    }
                    
                    timerElement.textContent = currentTime;
                    timerElement.className = 'timer-main';
                    
                    if (data.paused) {
                        timerElement.classList.add('paused');
                        labelElement.textContent = 'PAUSADO';
                    } else {
                        if (currentTimeValue <= 1800) timerElement.classList.add('danger');
                        else if (currentTimeValue <= 3600) timerElement.classList.add('warning');
                        labelElement.textContent = 'SUBATHON TIMER';
                    }
                    
                    lastTime = currentTime;
                    lastTimeValue = currentTimeValue;
                })
                .catch(error => console.error('Error:', error));
        }

        updateTimer();
        setInterval(updateTimer, 1000);
    </script>
</body>
</html>
"""