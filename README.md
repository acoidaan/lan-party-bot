# Lan Party Bot

Bot para Twitch que gestiona un contador de subathon compartido entre varios streamers. Soporta subs, bits y donaciones de Streamlabs.

## Funcionalidades

- Contador que se actualiza automáticamente y se muestra en OBS.
- Soporte para dos canales de Twitch.
- Soporte para donaciones vía Streamlabs Webhook.
- Comandos para personalizar el contador.
- Contador sincronizado por red.
- Interfaz web moderna para control del timer.
- Pausa/reanudación del contador.
- Webhooks consolidados en un solo servidor.

## Requisitos

- [Python 3.10+](https://www.python.org/downloads/).
- Cuenta de [Twitch Developer](https://dev.twitch.tv/).
- [OBS Studio](https://obsproject.com/es/download).
- ngrok para pruebas y producción.
- Streamlabs (opcional, para donaciones).

## Instalación

```bash
git clone git@github.com:acoidaan/lan-party-bot.git
cd lan-party-bot/subathon

pip install -r requirements.txt
```

## Configuración rápida

### 1. Configurar Twitch Developer

1. Ve a [Twitch Developer Console](https://dev.twitch.tv/console)
2. Crea una nueva aplicación
3. **OAuth Redirect URL**: `https://TU-URL-NGROK.ngrok-free.app/callback`
4. Guarda tu Client ID y Client Secret

### 2. Crear archivo .env

```env
TWITCH_CLIENT_ID=tu_client_id_aqui
TWITCH_CLIENT_SECRET=tu_client_secret_aqui
TWITCH_SCOPES=channel:read:subscriptions bits:read
TWITCH_REDIRECT_URI=https://TU-URL-NGROK.ngrok-free.app/callback
TWITCH_EVENTSUB_CALLBACK=https://TU-URL-NGROK.ngrok-free.app/twitch
TWITCH_EVENTSUB_SECRET=supersecreto123
WEBHOOK_URL=https://TU-URL-NGROK.ngrok-free.app/webhook
```

### 3. Iniciar ngrok

```bash
ngrok http 5000
```

### 4. Actualizar URLs

Reemplaza `TU-URL-NGROK` en el archivo `.env` con tu URL de ngrok.

## Uso

### Iniciar el sistema

```bash
# Servidor principal (interfaz web + webhooks)
python3 scripts/start.py

# Servidor con consola de comandos (opcional)
python3 scripts/main.py

# Ejecutar el setup 
python3 scripts/setup.py

# Mostrar información del sistema
python3 scripts/info.py
```

### Interfaz web

Abre tu URL de ngrok en el navegador para acceder al panel de control, o bien,
puedes usar la IP si estás en una red local, con el puerto 5000.

## Configuración OBS

1. **Fuente** → **Navegador**
2. **Poner de URL**: `https://TU-URL-NGROK.ngrok-free.app`

## URLs para servicios externos

Con tu URL de ngrok (`https://xxxx.ngrok-free.app`):

- **🌐 Panel de control**: `https://xxxx.ngrok-free.app`
- **⏳ Overlay del contador**: `https://xxxx.ngrok-free.app/overlay`
- **📊 Estadísticas del stream**: `https://xxx.ngrok-free.app/stats`
- **💰 Streamlabs webhook**: `https://xxxx.ngrok-free.app/webhook`
- **🎮 Twitch EventSub**: `https://xxxx.ngrok-free.app/twitch`

## API Testing

### Añadir tiempo

```bash
curl -X POST https://xxxx.ngrok-free.app/add_time \
  -H "Content-Type: application/json" \
  -d '{"minutes": 10}'
```

### Pausar/Reanudar

```bash
curl -X POST https://xxxx.ngrok-free.app/pause
curl -X POST https://xxxx.ngrok-free.app/resume
```

### Ver estado

```bash
curl https://xxxx.ngrok-free.app/api/time
```

## Configuración de eventos

### Donaciones (Streamlabs)

- **URL**: `https://xxxx.ngrok-free.app/webhook`
- **Método**: POST
- **Formato**: JSON

### Twitch EventSub

- **URL**: `https://xxxx.ngrok-free.app/twitch`
- **Eventos**: Suscripciones, Bits
- **Secret**: Configurado en `.env`

## Valores predeterminados

- **Suscripción**: +30 minutos
- **Donación**: +10 minutos por euro
- **Bits**: +10 minutos por cada 100 bits

## Troubleshooting

### Timer se actualiza doble

```bash
# Matar todos los procesos Python
pkill -f python           # Linux/Mac
taskkill /f /im python.exe # Windows

# Eliminar archivos lock
rm overlay_timer.txt.lock

# Ejecutar solo webhooks.py
python webhooks.py
```

### No se puede conectar

- Verificar que ngrok esté corriendo
- Verificar que `python webhooks.py` esté activo
- Usar HTTPS en las URLs

### Webhooks no funcionan

- Verificar URLs en servicios externos
- Comprobar que las URLs incluyen `/webhook` o `/twitch`
- Verificar que ngrok no cambió la URL

## Estructura del proyecto

```plaintext
subathon/
├── scripts/                 # Puntos de entrada
│   ├── start.py            # Inicio rápido
│   ├── main.py             # Menú completo  
│   ├── setup.py            # Configuración inicial
│   └── info.py             # Información del sistema
├── core/                   # Sistema principal
│   ├── webhooks.py         # Servidor principal (TODO EN UNO)
│   ├── timer.py            # Lógica del timer
│   └── timer_instance.py   # Timer singleton
├── twitch/                 # Integración Twitch
├── external/               # Servicios externos
├── analytics/              # Sistema de estadísticas
├── config/                 # Configuración
│   ├── .env                # Variables de entorno
│   ├── config.json         # Configuración general
│   └── twitch_auth.json    # Tokens (se genera automáticamente)
├── output/                 # Archivos de salida
│   └── overlay_timer.txt   # Archivo para OBS
└── requirements.txt        # Dependencias Python
```

## Autor

- [@acoidaan](https://www.github.com/acoidaan)

## Redes Sociales

Puedes encontrarnos en:

- Todas las redes sociales de CalceTeam en este [link](https://linktr.ee/calceteam_).

---

## 🚀 Configuración completa paso a paso

### Paso 1: Configuración inicial

```bash
git clone git@github.com:acoidaan/lan-party-bot.git
cd lan-party-bot/subathon
pip install -r requirements.txt
```

### Paso 2: Twitch Developer

1. [Crear aplicación](https://dev.twitch.tv/console)
2. Obtener Client ID y Secret
3. Configurar redirect URL: `http://localhost:5000/callback`

### Paso 3: ngrok

```bash
# Instalar ngrok desde https://ngrok.com/download
ngrok http 5000
# Guardar la URL que aparece (ej: https://xxxx.ngrok-free.app)
```

### Paso 4: Archivo .env

Crear archivo `.env` con las credenciales de Twitch y URL de ngrok.

### Paso 5: Ejecutar

```bash
python3 scripts/start.py
```

### Paso 6: Verificar

- Abrir URL de ngrok en navegador
- Testear con curl o interfaz web

### Paso 7: Configurar servicios

- **Streamlabs**: URL webhook
- **Twitch**: Registrar EventSub webhooks

---

💡 **Tip**: Para production, considera usar un servidor VPS en lugar de ngrok para tener una URL permanente.
