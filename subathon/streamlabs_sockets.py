#!/usr/bin/env python3
# streamlabs_socket.py - Cliente Socket API según documentación oficial

import socketio
import json
from timer_instance import timer

# Tokens de Socket API (necesitas obtenerlos)
SOCKET_TOKENS = {
    "xstellar_": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IkU1QzE3NDE1RkMxMEQzQ0I1Rjc3IiwicmVhZF9vbmx5Ijp0cnVlLCJwcmV2ZW50X21hc3RlciI6dHJ1ZSwidHdpdGNoX2lkIjoiMjIzNjQ1MzkyIn0.WFXvS0fmIMtTL_e5d0JPwgsutBgK42fbyhLON251xRg",
    "andresmanueh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IjZGRDExNzBDODQ2QjJDNDc4OTY0IiwicmVhZF9vbmx5Ijp0cnVlLCJwcmV2ZW50X21hc3RlciI6dHJ1ZSwidHdpdGNoX2lkIjoiMjQ2NzQ2OTkyIn0.2682vEPZfY26F6_NI1mnhfWT_HcRaxdBcYQzv92sNkY"
}

class StreamlabsSocketClient:
    def __init__(self):
        self.clients = {}
        
    def connect_channel(self, channel, token):
        """Conecta un canal específico"""
        if token == f"tu_socket_token_{channel}":
            print(f"⚠️ Token no configurado para {channel}")
            return False
            
        # Crear cliente Socket.IO
        sio = socketio.Client()
        
        @sio.event
        def connect():
            print(f"🎉 Conectado a Streamlabs Socket - {channel}")
        
        @sio.event
        def disconnect():
            print(f"🔌 Desconectado de Streamlabs - {channel}")
        
        @sio.event
        def event(data):
            """Procesa eventos de Streamlabs"""
            try:
                print(f"📡 [{channel}] Evento Streamlabs: {data}")
                
                event_type = data.get('type')
                
                if event_type == 'donation':
                    self.process_donation(data, channel)
                elif event_type == 'follow':
                    self.process_follow(data, channel)
                else:
                    print(f"📝 [{channel}] Evento no procesado: {event_type}")
                    
            except Exception as e:
                print(f"❌ Error procesando evento {channel}: {e}")
        
        # Conectar con token
        try:
            url = f"https://sockets.streamlabs.com?token={token}"
            sio.connect(url)
            self.clients[channel] = sio
            return True
        except Exception as e:
            print(f"❌ Error conectando {channel}: {e}")
            return False
    
    def process_donation(self, data, channel):
        """Procesa donaciones según formato oficial"""
        try:
            messages = data.get('message', [])
            
            for donation in messages:
                # Formato según documentación Streamlabs
                amount = float(donation.get('amount', 0))
                name = donation.get('name', 'Anónimo')
                message = donation.get('message', '')
                currency = donation.get('currency', 'USD')
                
                # Convertir según moneda (simplificado)
                if currency == 'EUR':
                    amount_eur = amount
                elif currency == 'USD':
                    amount_eur = amount * 0.85  # Conversión aproximada
                else:
                    amount_eur = amount
                
                # 10 minutos por euro
                minutes = int(amount_eur * 10)
                
                print(f"💰 [{channel}] DONACIÓN: {name} donó {amount} {currency} → +{minutes} min")
                if message:
                    print(f"   💬 Mensaje: {message}")
                
                # Añadir tiempo al timer
                timer.add_time(minutes)
                
        except Exception as e:
            print(f"❌ Error procesando donación {channel}: {e}")
    
    def process_follow(self, data, channel):
        """Procesa follows (opcional)"""
        try:
            messages = data.get('message', [])
            for follow in messages:
                name = follow.get('name', 'Anónimo')
                print(f"👥 [{channel}] FOLLOW: {name}")
                # Opcional: añadir tiempo por follow
                # timer.add_time(1)  # 1 minuto por follow
        except Exception as e:
            print(f"❌ Error procesando follow {channel}: {e}")
    
    def connect_all(self):
        """Conecta todos los canales configurados"""
        connected = 0
        
        for channel, token in SOCKET_TOKENS.items():
            if self.connect_channel(channel, token):
                connected += 1
        
        if connected > 0:
            print(f"✅ {connected} canal(es) conectado(s) a Streamlabs Socket")
            return True
        else:
            print("❌ No se pudo conectar ningún canal")
            return False
    
    def disconnect_all(self):
        """Desconecta todos los clientes"""
        for channel, client in self.clients.items():
            try:
                client.disconnect()
                print(f"🔌 {channel} desconectado")
            except:
                pass

def main():
    """Función principal para ejecutar el cliente Socket"""
    print("🚀 Iniciando cliente Streamlabs Socket API...")
    
    # Verificar tokens configurados
    valid_tokens = sum(1 for token in SOCKET_TOKENS.values() if not token.startswith("tu_socket_token_"))
    
    if valid_tokens == 0:
        print("❌ NO HAY TOKENS CONFIGURADOS")
        print("\n📋 Para obtener tokens:")
        print("1. Ve a https://streamlabs.com/dashboard")
        print("2. Settings → API Settings → API Tokens")
        print("3. Copia 'Socket API Token'")
        print("4. Actualiza SOCKET_TOKENS en este archivo")
        print("\nPor ejemplo:")
        print('SOCKET_TOKENS = {')
        print('    "xstellar_": "abc123def456...",')
        print('    "andresmanueh": "ghi789jkl012..."')
        print('}')
        return
    
    client = StreamlabsSocketClient()
    
    try:
        if client.connect_all():
            print("🎉 Socket API funcionando. Escuchando donaciones...")
            print("Press Ctrl+C to stop")
            
            # Mantener corriendo
            import time
            while True:
                time.sleep(1)
        else:
            print("❌ No se pudo iniciar Socket API")
            
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo Socket API...")
        client.disconnect_all()
    except Exception as e:
        print(f"❌ Error: {e}")
        client.disconnect_all()

if __name__ == "__main__":
    main()