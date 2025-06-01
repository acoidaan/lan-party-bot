import json
import random
import threading
from datetime import datetime

class QuizGame:
    def __init__(self, questions_file="questions.json"):
        self.lock = threading.Lock()
        self.questions_file = questions_file
        self.current_question = None
        self.current_options = []
        self.correct_answer = None
        self.question_visible = False
        self.options_visible = False
        self.answer_revealed = False
        self.score = 0
        self.question_count = 0
        self.max_questions = 15
        self.used_lifelines = {
            "50_50": False,
            "phone_call": False,
            "audience": False
        }
        self.eliminated_options = []
        self.load_questions()
    
    def load_questions(self):
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                self.questions = json.load(f)
        except FileNotFoundError:
            # Crear archivo de ejemplo si no existe
            self.questions = [
                {
                    "question": "¿Cuál es la capital de Francia?",
                    "options": ["Madrid", "París", "Londres", "Roma"],
                    "correct": 1,
                    "difficulty": "easy"
                },
                {
                    "question": "¿En qué año llegó el hombre a la Luna?",
                    "options": ["1967", "1969", "1971", "1973"],
                    "correct": 1,
                    "difficulty": "medium"
                },
                {
                    "question": "¿Cuál es el elemento químico con símbolo Au?",
                    "options": ["Plata", "Oro", "Aluminio", "Argon"],
                    "correct": 1,
                    "difficulty": "hard"
                }
            ]
            self.save_questions()
    
    def save_questions(self):
        with open(self.questions_file, 'w', encoding='utf-8') as f:
            json.dump(self.questions, f, indent=2, ensure_ascii=False)
    
    def new_question(self, difficulty=None):
        with self.lock:
            # Inicializar atributos si no existen (compatibilidad)
            if not hasattr(self, 'question_count'):
                self.question_count = 0
            if not hasattr(self, 'max_questions'):
                self.max_questions = 15
                
            if self.question_count >= self.max_questions:
                return False
                
            available_questions = self.questions
            if difficulty:
                available_questions = [q for q in self.questions if q.get("difficulty") == difficulty]
            
            if not available_questions:
                return False
            
            question_data = random.choice(available_questions)
            self.current_question = question_data["question"]
            self.current_options = question_data["options"].copy()
            self.correct_answer = question_data["correct"]
            self.question_visible = False
            self.options_visible = False
            self.answer_revealed = False
            self.eliminated_options = []
            self.question_count += 1
            return True
    
    def show_question(self):
        with self.lock:
            self.question_visible = True
    
    def show_options(self):
        with self.lock:
            self.options_visible = True
    
    def reveal_answer(self):
        with self.lock:
            self.answer_revealed = True
    
    def use_50_50(self):
        with self.lock:
            if self.used_lifelines["50_50"] or len(self.eliminated_options) > 0:
                return False
            
            # Eliminar 2 opciones incorrectas
            incorrect_indices = [i for i in range(len(self.current_options)) if i != self.correct_answer]
            to_eliminate = random.sample(incorrect_indices, 2)
            self.eliminated_options = to_eliminate
            self.used_lifelines["50_50"] = True
            return True
    
    def use_phone_call(self):
        with self.lock:
            if self.used_lifelines["phone_call"]:
                return False
            self.used_lifelines["phone_call"] = True
            # Simular respuesta del teléfono (80% probabilidad de respuesta correcta)
            if random.random() < 0.8:
                return self.correct_answer
            else:
                incorrect = [i for i in range(len(self.current_options)) if i != self.correct_answer]
                return random.choice(incorrect)
    
    def use_change_question(self):
        with self.lock:
            if self.used_lifelines["change_question"]:
                return False
            self.used_lifelines["change_question"] = True
            return self.new_question()
    
    def use_audience(self):
        with self.lock:
            if self.used_lifelines["audience"]:
                return False
            self.used_lifelines["audience"] = True
            # Simular votación del público (60% en respuesta correcta)
            percentages = [10, 10, 10, 10]  # Base 10% cada opción
            remaining = 60
            
            # Dar más peso a la respuesta correcta
            percentages[self.correct_answer] += 50
            remaining -= 50
            
            # Distribuir el resto
            for i in range(len(percentages)):
                if i != self.correct_answer:
                    extra = random.randint(0, remaining // 2)
                    percentages[i] += extra
                    remaining -= extra
            
            # Ajustar para que sume 100
            percentages[self.correct_answer] += remaining
            
            return percentages
    
    def reset_lifelines(self):
        with self.lock:
            self.used_lifelines = {
                "50_50": False,
                "phone_call": False,
                "audience": False
            }
    
    def get_state(self):
        with self.lock:
            # Inicializar atributos si no existen (compatibilidad)
            if not hasattr(self, 'question_count'):
                self.question_count = 0
            if not hasattr(self, 'max_questions'):
                self.max_questions = 15
                
            return {
                "question": self.current_question if self.question_visible else "",
                "options": [
                    opt if i not in self.eliminated_options else ""
                    for i, opt in enumerate(self.current_options)
                ] if self.options_visible else ["", "", "", ""],
                "question_visible": self.question_visible,
                "options_visible": self.options_visible,
                "answer_revealed": self.answer_revealed,
                "correct_answer": self.correct_answer if self.answer_revealed else None,
                "score": self.score,
                "question_count": self.question_count,
                "max_questions": self.max_questions,
                "game_finished": self.question_count >= self.max_questions,
                "lifelines": self.used_lifelines,
                "eliminated_options": self.eliminated_options
            }

# Instancia global del juego
game = QuizGame()