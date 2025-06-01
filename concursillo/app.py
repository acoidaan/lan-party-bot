from flask import Flask, render_template, jsonify, request, Response
from game_state import game
import json
import time
import threading
from queue import Queue

app = Flask(__name__)

# Cola para eventos SSE
event_queue = Queue()

def send_event(event_type, data):
    """Envía evento a todos los clientes conectados via SSE"""
    event_queue.put({
        'type': event_type,
        'data': data,
        'timestamp': time.time()
    })

@app.route('/')
def control_panel():
    """Panel de control principal"""
    with open('control.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/overlay')
def overlay():
    """Overlay para OBS"""
    with open('overlay.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/api/game-state')
def get_game_state():
    """Obtiene el estado actual del juego"""
    return jsonify(game.get_state())

@app.route('/api/new-question', methods=['POST'])
def new_question():
    """Genera una nueva pregunta"""
    data = request.get_json() or {}
    difficulty = data.get('difficulty')
    
    # Inicializar atributos si no existen (compatibilidad)
    if not hasattr(game, 'question_count'):
        game.question_count = 0
    if not hasattr(game, 'max_questions'):
        game.max_questions = 15
    
    if game.question_count >= game.max_questions:
        return jsonify({
            'success': False,
            'message': f'Juego completado. Ya has respondido las {game.max_questions} preguntas.'
        })
    
    success = game.new_question(difficulty)
    if success:
        return jsonify({
            'success': True,
            'message': f'Pregunta {game.question_count}/{game.max_questions} generada ({difficulty})'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'No hay preguntas disponibles para esa dificultad'
        })

@app.route('/api/show-question', methods=['POST'])
def show_question():
    """Muestra la pregunta en el overlay"""
    game.show_question()
    return jsonify({
        'success': True,
        'message': 'Pregunta mostrada'
    })

@app.route('/api/show-options', methods=['POST'])
def show_options():
    """Muestra las opciones en el overlay"""
    game.show_options()
    return jsonify({
        'success': True,
        'message': 'Opciones mostradas'
    })

@app.route('/api/reveal-answer', methods=['POST'])
def reveal_answer():
    """Revela la respuesta correcta"""
    game.reveal_answer()
    return jsonify({
        'success': True,
        'message': 'Respuesta revelada'
    })

@app.route('/api/lifeline/50-50', methods=['POST'])
def lifeline_5050():
    """Usa el comodín 50/50"""
    success = game.use_50_50()
    if success:
        send_event('lifeline_used', {'message': 'Has usado: Comodín 50/50'})
        return jsonify({
            'success': True,
            'message': 'Comodín 50/50 usado - 2 opciones eliminadas'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Comodín 50/50 ya usado o no disponible'
        })

@app.route('/api/lifeline/phone-call', methods=['POST'])
def lifeline_phone():
    """Usa el comodín de llamada"""
    success = game.use_phone_call()
    if success is not False:
        send_event('lifeline_used', {'message': 'Has usado: Comodín de Llamada'})
        print(f"[DEBUG] Enviando evento: Comodín de Llamada")  # Debug
        return jsonify({
            'success': True,
            'message': 'Comodín de llamada usado'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Comodín de llamada ya usado'
        })

@app.route('/api/lifeline/audience', methods=['POST'])
def lifeline_audience():
    """Usa el comodín del público"""
    percentages = game.use_audience()
    if percentages:
        send_event('lifeline_used', {'message': 'Has usado: Comodín del Público'})
        print(f"[DEBUG] Enviando evento: Comodín del Público")  # Debug
        return jsonify({
            'success': True,
            'message': 'Comodín del público usado'
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Comodín del público ya usado'
        })

@app.route('/api/add-score', methods=['POST'])
def add_score():
    """Añade puntos al marcador"""
    data = request.get_json() or {}
    points = data.get('points', 100)
    
    with game.lock:
        game.score += points
    
    return jsonify({
        'success': True,
        'message': f'+{points} puntos añadidos'
    })

@app.route('/api/reset-lifelines', methods=['POST'])
def reset_lifelines():
    """Resetea todos los comodines"""
    game.reset_lifelines()
    return jsonify({
        'success': True,
        'message': 'Comodines reseteados'
    })

@app.route('/api/reset-game', methods=['POST'])
def reset_game():
    """Resetea todo el juego"""
    with game.lock:
        game.current_question = None
        game.current_options = []
        game.correct_answer = None
        game.question_visible = False
        game.options_visible = False
        game.answer_revealed = False
        game.score = 0
        game.question_count = 0
        game.eliminated_options = []
        game.reset_lifelines()
    
    return jsonify({
        'success': True,
        'message': 'Juego reseteado completamente'
    })

@app.route('/api/events')
def events():
    """Server-Sent Events para comunicación en tiempo real"""
    def event_stream():
        client_events = Queue()
        
        # Función para enviar eventos al cliente
        def send_to_client():
            while True:
                try:
                    # Intentar obtener evento de la cola global
                    event = event_queue.get(timeout=1)
                    yield f"data: {json.dumps(event)}\n\n"
                except:
                    # Heartbeat cada segundo
                    yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': time.time()})}\n\n"
        
        return send_to_client()
    
    return Response(event_stream(), 
                   mimetype='text/event-stream',
                   headers={'Cache-Control': 'no-cache'})

# Función para limpiar eventos antiguos
def cleanup_events():
    """Limpia eventos antiguos de la cola cada 30 segundos"""
    while True:
        time.sleep(30)
        current_time = time.time()
        # Limpiar eventos más antiguos de 10 segundos
        temp_queue = Queue()
        while not event_queue.empty():
            try:
                event = event_queue.get_nowait()
                if current_time - event.get('timestamp', 0) < 10:
                    temp_queue.put(event)
            except:
                break
        
        # Reemplazar cola
        while not temp_queue.empty():
            event_queue.put(temp_queue.get())

# Iniciar hilo de limpieza
cleanup_thread = threading.Thread(target=cleanup_events, daemon=True)
cleanup_thread.start()

if __name__ == '__main__':
    print("🎮 Quiz Game iniciado!")
    print("📱 Panel de control: http://localhost:5001")
    print("📺 Overlay para OBS: http://localhost:5001/overlay")
    print("🎯 Usa el panel de control desde tu móvil para controlar el juego")
    
    app.run(host='0.0.0.0', port=5001, debug=True, threaded=True)