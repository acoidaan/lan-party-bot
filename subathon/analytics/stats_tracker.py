import json
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
import threading

class StatsTracker:
    def __init__(self):
        self.lock = threading.Lock()
        self.session_start = datetime.now()
        
        # Estadísticas básicas
        self.total_donated = 0.0
        self.total_donations = 0
        self.total_subs = 0
        self.total_bits = 0
        self.total_time_added = 0  # en minutos
        
        # Historial de eventos (últimas 24 horas)
        self.donation_history = deque(maxlen=1000)
        self.sub_history = deque(maxlen=1000)
        self.time_history = deque(maxlen=1000)
        
        # Datos por hora para gráficos
        self.hourly_stats = defaultdict(lambda: {
            'donations': 0,
            'amount': 0.0,
            'subs': 0,
            'time_added': 0
        })
        
        # Top donadores
        self.top_donors = defaultdict(float)
        
        print("📊 Sistema de estadísticas iniciado")
    
    def add_donation(self, amount, donor_name, currency='EUR', message=''):
        """Registra una donación"""
        with self.lock:
            # Convertir a EUR si es necesario
            if currency == 'USD':
                amount_eur = amount * 0.85
            else:
                amount_eur = amount
            
            # Actualizar totales
            self.total_donated += amount_eur
            self.total_donations += 1
            
            # Calcular tiempo añadido (10 min por euro)
            time_added = int(amount_eur * 10)
            self.total_time_added += time_added
            
            # Guardar en historial
            event = {
                'timestamp': datetime.now().isoformat(),
                'amount': amount_eur,
                'donor': donor_name,
                'message': message,
                'time_added': time_added
            }
            self.donation_history.append(event)
            
            # Actualizar top donadores
            self.top_donors[donor_name] += amount_eur
            
            # Estadísticas por hora
            hour_key = datetime.now().strftime('%Y-%m-%d %H:00')
            self.hourly_stats[hour_key]['donations'] += 1
            self.hourly_stats[hour_key]['amount'] += amount_eur
            self.hourly_stats[hour_key]['time_added'] += time_added
            
            print(f"📊 Donación registrada: {donor_name} - €{amount_eur:.2f}")
    
    def add_subscription(self, subscriber_name, tier=1):
        """Registra una suscripción"""
        with self.lock:
            self.total_subs += 1
            time_added = 30  # 30 min por sub
            self.total_time_added += time_added
            
            event = {
                'timestamp': datetime.now().isoformat(),
                'subscriber': subscriber_name,
                'tier': tier,
                'time_added': time_added
            }
            self.sub_history.append(event)
            
            # Estadísticas por hora
            hour_key = datetime.now().strftime('%Y-%m-%d %H:00')
            self.hourly_stats[hour_key]['subs'] += 1
            self.hourly_stats[hour_key]['time_added'] += time_added
            
            print(f"📊 Suscripción registrada: {subscriber_name}")
    
    def add_bits(self, bits, user_name):
        """Registra bits/cheers"""
        with self.lock:
            self.total_bits += bits
            time_added = (bits // 100) * 10  # 10 min por cada 100 bits
            self.total_time_added += time_added
            
            # Estadísticas por hora
            hour_key = datetime.now().strftime('%Y-%m-%d %H:00')
            self.hourly_stats[hour_key]['time_added'] += time_added
            
            print(f"📊 Bits registrados: {user_name} - {bits} bits")
    
    def get_stats_summary(self):
        """Obtiene resumen de estadísticas"""
        with self.lock:
            # Calcular tiempo de sesión
            session_duration = datetime.now() - self.session_start
            hours_streaming = session_duration.total_seconds() / 3600
            
            # Promedio de donación
            avg_donation = self.total_donated / max(1, self.total_donations)
            
            # Donaciones por hora
            donations_per_hour = self.total_donations / max(1, hours_streaming)
            
            # Top 5 donadores
            top_5_donors = sorted(
                self.top_donors.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
            
            return {
                'session_start': self.session_start.isoformat(),
                'session_duration_hours': round(hours_streaming, 2),
                'total_donated': round(self.total_donated, 2),
                'total_donations': self.total_donations,
                'total_subs': self.total_subs,
                'total_bits': self.total_bits,
                'total_time_added': self.total_time_added,
                'avg_donation': round(avg_donation, 2),
                'donations_per_hour': round(donations_per_hour, 2),
                'top_donors': [{'name': name, 'amount': round(amount, 2)} for name, amount in top_5_donors]
            }
    
    def get_hourly_data(self, hours_back=24):
        """Obtiene datos por hora para gráficos"""
        with self.lock:
            now = datetime.now()
            data = []
            
            for i in range(hours_back, 0, -1):
                hour = now - timedelta(hours=i)
                hour_key = hour.strftime('%Y-%m-%d %H:00')
                hour_label = hour.strftime('%H:00')
                
                stats = self.hourly_stats.get(hour_key, {
                    'donations': 0,
                    'amount': 0.0,
                    'subs': 0,
                    'time_added': 0
                })
                
                data.append({
                    'hour': hour_label,
                    'donations': stats['donations'],
                    'amount': round(stats['amount'], 2),
                    'subs': stats['subs'],
                    'time_added': stats['time_added']
                })
            
            return data
    
    def get_recent_events(self, limit=10):
        """Obtiene eventos recientes"""
        with self.lock:
            # Combinar y ordenar eventos recientes
            all_events = []
            
            # Agregar donaciones
            for donation in list(self.donation_history)[-limit:]:
                all_events.append({
                    'type': 'donation',
                    'timestamp': donation['timestamp'],
                    'data': donation
                })
            
            # Agregar suscripciones
            for sub in list(self.sub_history)[-limit:]:
                all_events.append({
                    'type': 'subscription',
                    'timestamp': sub['timestamp'],
                    'data': sub
                })
            
            # Ordenar por timestamp (más recientes primero)
            all_events.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return all_events[:limit]

# Instancia global del tracker
stats_tracker = StatsTracker()

# Dashboard HTML con gráficos
STATS_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Subathon Analytics Dashboard</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        body { 
            background: linear-gradient(to bottom right, rgb(15, 32, 56), rgb(21, 41, 76));
            color: white; 
            font-family: 'Segoe UI', sans-serif; 
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            margin-bottom: 2em;
            color: rgb(76, 175, 80);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5em;
            margin-bottom: 2em;
        }
        
        .stat-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 1.5em;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 0.2em;
            color: rgb(76, 175, 80);
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 2em;
            margin-bottom: 2em;
        }
        
        .chart-container {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 1.5em;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .chart-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 1em;
            text-align: center;
        }
        
        .recent-events {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 1.5em;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .event-item {
            padding: 0.8em;
            margin-bottom: 0.5em;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            border-left: 4px solid rgb(76, 175, 80);
        }
        
        .event-donation { border-left-color: rgb(255, 193, 7); }
        .event-subscription { border-left-color: rgb(156, 39, 176); }
        
        .top-donors {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 1.5em;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .donor-item {
            display: flex;
            justify-content: space-between;
            padding: 0.5em 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .refresh-btn {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgb(76, 175, 80);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            cursor: pointer;
            font-size: 1.2em;
        }
        
        @media (max-width: 768px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }
            .stats-grid {
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            }
        }
    </style>
</head>
<body>
    <button class="refresh-btn" onclick="loadData()" title="Actualizar datos">🔄</button>
    
    <div class="container">
        <h1>📊 Subathon Analytics Dashboard</h1>
        
        <!-- Estadísticas principales -->
        <div class="stats-grid" id="stats-grid">
            <!-- Se cargan dinámicamente -->
        </div>
        
        <!-- Gráficos -->
        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">📈 Actividad por Hora</div>
                <canvas id="hourlyChart"></canvas>
            </div>
            
            <div>
                <div class="top-donors">
                    <div class="chart-title">🏆 Top Donadores</div>
                    <div id="top-donors-list">
                        <!-- Se carga dinámicamente -->
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Eventos recientes -->
        <div class="recent-events">
            <div class="chart-title">🕒 Eventos Recientes</div>
            <div id="recent-events">
                <!-- Se cargan dinámicamente -->
            </div>
        </div>
    </div>

    <script>
        let hourlyChart = null;

        function loadData() {
            // Cargar estadísticas principales
            fetch('/api/stats/summary')
                .then(response => response.json())
                .then(data => updateStatsCards(data))
                .catch(error => console.error('Error loading stats:', error));

            // Cargar datos por hora para gráfico
            fetch('/api/stats/hourly')
                .then(response => response.json())
                .then(data => updateHourlyChart(data))
                .catch(error => console.error('Error loading hourly data:', error));

            // Cargar eventos recientes
            fetch('/api/stats/events')
                .then(response => response.json())
                .then(data => updateRecentEvents(data))
                .catch(error => console.error('Error loading events:', error));
        }

        function updateStatsCards(stats) {
            const statsGrid = document.getElementById('stats-grid');
            
            const cards = [
                { label: 'Total Donado', value: '€' + stats.total_donated, icon: '💰' },
                { label: 'Donaciones', value: stats.total_donations, icon: '🎁' },
                { label: 'Suscripciones', value: stats.total_subs, icon: '🟣' },
                { label: 'Tiempo Añadido', value: stats.total_time_added + ' min', icon: '⏱️' },
                { label: 'Promedio Donación', value: '€' + stats.avg_donation, icon: '📊' },
                { label: 'Donaciones/Hora', value: stats.donations_per_hour.toFixed(1), icon: '📈' },
                { label: 'Bits Total', value: stats.total_bits, icon: '💎' },
                { label: 'Horas Stream', value: stats.session_duration_hours + 'h', icon: '🕐' }
            ];

            statsGrid.innerHTML = cards.map(card => `
                <div class="stat-card">
                    <div class="stat-value">${card.icon} ${card.value}</div>
                    <div class="stat-label">${card.label}</div>
                </div>
            `).join('');

            // Actualizar top donadores
            updateTopDonors(stats.top_donors);
        }

        function updateTopDonors(topDonors) {
            const container = document.getElementById('top-donors-list');
            
            if (topDonors.length === 0) {
                container.innerHTML = '<p style="text-align: center; opacity: 0.6;">No hay donaciones aún</p>';
                return;
            }

            container.innerHTML = topDonors.map((donor, index) => `
                <div class="donor-item">
                    <span>${index + 1}. ${donor.name}</span>
                    <span>€${donor.amount}</span>
                </div>
            `).join('');
        }

        function updateHourlyChart(data) {
            const ctx = document.getElementById('hourlyChart').getContext('2d');
            
            if (hourlyChart) {
                hourlyChart.destroy();
            }

            hourlyChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.map(d => d.hour),
                    datasets: [
                        {
                            label: 'Donaciones €',
                            data: data.map(d => d.amount),
                            borderColor: 'rgb(255, 193, 7)',
                            backgroundColor: 'rgba(255, 193, 7, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y'
                        },
                        {
                            label: 'Suscripciones',
                            data: data.map(d => d.subs),
                            borderColor: 'rgb(156, 39, 176)',
                            backgroundColor: 'rgba(156, 39, 176, 0.1)',
                            tension: 0.4,
                            yAxisID: 'y1'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            labels: { color: 'white' }
                        }
                    },
                    scales: {
                        x: {
                            ticks: { color: 'white' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            ticks: { color: 'white' },
                            grid: { color: 'rgba(255, 255, 255, 0.1)' }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            ticks: { color: 'white' },
                            grid: { drawOnChartArea: false }
                        }
                    }
                }
            });
        }

        function updateRecentEvents(events) {
            const container = document.getElementById('recent-events');
            
            if (events.length === 0) {
                container.innerHTML = '<p style="text-align: center; opacity: 0.6;">No hay eventos recientes</p>';
                return;
            }

            container.innerHTML = events.map(event => {
                const time = new Date(event.timestamp).toLocaleTimeString();
                
                if (event.type === 'donation') {
                    const data = event.data;
                    return `
                        <div class="event-item event-donation">
                            <strong>${data.donor}</strong> donó <strong>€${data.amount}</strong>
                            <br><small>${time} • +${data.time_added} min</small>
                        </div>
                    `;
                } else if (event.type === 'subscription') {
                    const data = event.data;
                    return `
                        <div class="event-item event-subscription">
                            <strong>${data.subscriber}</strong> se suscribió
                            <br><small>${time} • +${data.time_added} min</small>
                        </div>
                    `;
                }
            }).join('');
        }

        // Cargar datos inicial
        loadData();

        // Auto-refresh cada 30 segundos
        setInterval(loadData, 30000);
    </script>
</body>
</html>
"""