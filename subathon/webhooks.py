from flask import Flask, jsonify, request, render_template_string, redirect, url_for
from timer_instance import timer

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Subathon Timer</title>
    <meta charset="UTF-8" />
    <style>
        body { background: #111; color: white; text-align: center; font-family: sans-serif; }
        h1 { font-size: 5em; margin-top: 1em; }
        button {
            background: #333; color: white; padding: 1em; margin: 0.5em;
            border: none; border-radius: 5px; font-size: 1em;
        }
        button:hover { background: #555; cursor: pointer; }
    </style>
</head>
<body>
    <h1 id="timer">00:00:00</h1>
    <div>
        <button onclick="addTime(5)">+5 min</button>
        <button onclick="addTime(10)">+10 min</button>
        <button onclick="pause()">⏸ Pausar</button>
        <button onclick="resume()">▶️ Reanudar</button>
    </div>
    <script>
        function fetchTime() {
            fetch("/api/time")
                .then(response => response.json())
                .then(data => {
                    const label = data.paused ? "PAUSADO - " : "";
                    document.getElementById("timer").textContent = label + data.time;
                });
        }

        function addTime(mins) {
            fetch("/add_time", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ minutes: mins })
            }).then(fetchTime);
        }

        function pause() {
            fetch("/pause", { method: "POST" }).then(fetchTime);
        }

        function resume() {
            fetch("/resume", { method: "POST" }).then(fetchTime);
        }

        setInterval(fetchTime, 1000);
        fetchTime();
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/time")
def api_time():
    return jsonify({
        "time": str(timer.get_remaining()).split('.')[0],
        "paused": timer.is_paused()
    })

@app.route("/add_time", methods=["POST"])
def add_time():
    data = request.get_json()
    minutes = data.get("minutes", 0)
    timer.add_time(minutes)
    return jsonify({"status": "ok"})

@app.route("/pause", methods=["POST"])
def pause():
    timer.pause()
    return jsonify({"status": "paused"})

@app.route("/resume", methods=["POST"])
def resume():
    timer.resume()
    return jsonify({"status": "resumed"})
