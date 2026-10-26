#!/usr/bin/env python3
"""Idle Slayer Cheat - Web UI"""

from flask import Flask, jsonify, request
import json
from pathlib import Path
import threading
import time
from .core import engine, CheatMode

CONFIG = Path.home() / ".idle_slayer_cheat" / "cheats.json"
CONFIG.parent.mkdir(exist_ok=True)

CHEATS = [
    ("autofarm_coins", "AutoFarm Coins", "Farm coins only"),
    ("autofarm_slayer", "AutoFarm Slayer", "Farm slayer points"),
    ("autofarm_quest_temp", "Auto Temp Quests", "Complete temp quests"),
    ("autofarm_quest_normal", "Auto Normal Quests", "Complete normal quests"),
    ("autofarm_quest_event", "Auto Event Quests", "Complete event quests"),
    ("auto_ascend", "Auto Ascend", "Ascend at 25%"),
    ("auto_minions", "Auto Minions", "Start minions"),
    ("auto_upgrades_1", "Budget Upgrades", "Cost-effective"),
    ("auto_upgrades_2", "All Upgrades", "Buy everything"),
    ("auto_craft", "Auto Craft", "Craft items"),
    ("auto_ads", "Auto Ads", "Watch ads"),
    ("auto_rage", "Rage Automation", "Megahorde trigger"),
    ("quest_router", "Quest Router", "Smart routing"),
    ("gear_craft_ai", "Gear Craft AI", "AI crafting"),
    ("bonus_stage", "Bonus Stages", "Auto-run stages"),
    ("chest_hunt_solver", "Chest Hunt AI", "Minigame AI"),
    ("ua_planner", "UA Planner", "Ascension plan"),
    ("minigame_runner", "Minigame Runner", "Pattern runner"),
]

app = Flask(__name__)

class CheatState:
    def __init__(self):
        self.states = {}
        self.load()

    def load(self):
        try:
            if CONFIG.exists():
                with open(CONFIG) as f:
                    self.states = json.load(f)
        except:
            pass
        for cid, _, _ in CHEATS:
            if cid not in self.states:
                self.states[cid] = False

    def save(self):
        try:
            with open(CONFIG, "w") as f:
                json.dump(self.states, f)
        except:
            pass

    def toggle(self, cid):
        self.states[cid] = not self.states[cid]
        try:
            mode = CheatMode(cid)
            engine.state.toggle_cheat(mode)
        except:
            pass
        self.save()

state = CheatState()

@app.route("/")
def index():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Idle Slayer Cheats</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: #0d0d1f;
            color: #e0e0e0;
            padding: 0;
        }
        header {
            background: #1a1a3f;
            padding: 25px;
            text-align: center;
            border-bottom: 2px solid #00d4ff;
        }
        h1 {
            font-size: 28px;
            color: #00d4ff;
            font-weight: bold;
        }
        .status-bar {
            background: #16213e;
            padding: 15px 25px;
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #00d4ff;
            font-weight: bold;
        }
        .status-item {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .status-label {
            color: #888;
            font-size: 13px;
        }
        .status-value {
            color: #00d4ff;
            font-size: 14px;
        }
        #status {
            color: #ff4444;
        }
        #status.running {
            color: #00cc00;
        }
        .container {
            max-width: 700px;
            margin: 0 auto;
            padding: 20px;
        }
        .cheat-item {
            background: #1a1a3f;
            border: 1px solid #2a2a4f;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            transition: all 0.2s;
        }
        .cheat-item:hover {
            background: #202050;
            border-color: #00d4ff;
        }
        .cheat-info h3 {
            color: #00d4ff;
            font-size: 13px;
            margin-bottom: 4px;
        }
        .cheat-info p {
            color: #666;
            font-size: 12px;
        }
        .toggle {
            width: 60px;
            height: 32px;
            background: #444;
            border: none;
            border-radius: 16px;
            cursor: pointer;
            font-weight: bold;
            font-size: 12px;
            transition: all 0.2s;
            color: white;
        }
        .toggle.on {
            background: #00cc00;
            color: black;
        }
        .controls {
            display: flex;
            gap: 10px;
            margin-top: 25px;
        }
        button.control {
            flex: 1;
            padding: 15px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
        }
        .start {
            background: #00cc00;
            color: black;
        }
        .start:hover {
            background: #00ff00;
        }
        .stop {
            background: #ff3333;
            color: white;
        }
        .stop:hover {
            background: #ff5555;
        }
    </style>
</head>
<body>
    <header>
        <h1>⚔️  IDLE SLAYER CHEATS</h1>
    </header>

    <div class="status-bar">
        <div class="status-item">
            <span class="status-label">Status:</span>
            <span class="status-value" id="status">● STOPPED</span>
        </div>
        <div class="status-item">
            <span class="status-label">Active:</span>
            <span class="status-value" id="active">0 / 18</span>
        </div>
    </div>

    <div class="container">
        <div id="cheats-list"></div>

        <div class="controls">
            <button class="control start" onclick="startEngine()">▶  START</button>
            <button class="control stop" onclick="stopEngine()">⏹  STOP</button>
        </div>
    </div>

    <script>
        const cheats = %CHEATS%;

        async function loadCheats() {
            const res = await fetch('/api/cheats');
            const data = await res.json();

            const list = document.getElementById('cheats-list');
            list.innerHTML = '';

            for (const [id, info] of Object.entries(data.cheats)) {
                const div = document.createElement('div');
                div.className = 'cheat-item';

                const infoDiv = document.createElement('div');
                infoDiv.className = 'cheat-info';
                infoDiv.innerHTML = `<h3>${info.name}</h3><p>${info.desc}</p>`;

                const btn = document.createElement('button');
                btn.className = `toggle${info.enabled ? ' on' : ''}`;
                btn.textContent = info.enabled ? 'ON' : 'OFF';
                btn.onclick = async (e) => {
                    e.stopPropagation();
                    await fetch(`/api/toggle/${id}`, {method: 'POST'});
                    loadCheats();
                    updateStatus();
                };

                div.appendChild(infoDiv);
                div.appendChild(btn);
                list.appendChild(div);
            }
        }

        async function updateStatus() {
            const res = await fetch('/api/status');
            const data = await res.json();

            const status = document.getElementById('status');
            if (data.running) {
                status.textContent = '● RUNNING';
                status.classList.add('running');
            } else {
                status.textContent = '● STOPPED';
                status.classList.remove('running');
            }

            const active = Object.values(data.active_cheats).filter(v => v).length;
            document.getElementById('active').textContent = `${active} / 18`;
        }

        async function startEngine() {
            await fetch('/api/start', {method: 'POST'});
            updateStatus();
        }

        async function stopEngine() {
            await fetch('/api/stop', {method: 'POST'});
            updateStatus();
        }

        loadCheats();
        updateStatus();
        setInterval(updateStatus, 1000);
    </script>
</body>
</html>
""".replace("%CHEATS%", json.dumps({c[0]: {"name": c[1], "desc": c[2]} for c in CHEATS}))

@app.route("/api/cheats")
def get_cheats():
    return jsonify({
        "cheats": {
            cid: {
                "name": name,
                "desc": desc,
                "enabled": state.states.get(cid, False)
            }
            for cid, name, desc in CHEATS
        }
    })

@app.route("/api/toggle/<cid>", methods=["POST"])
def toggle(cid):
    state.toggle(cid)
    return jsonify({"ok": True})

@app.route("/api/status")
def get_status():
    return jsonify({
        "running": engine.running,
        "active_cheats": state.states
    })

@app.route("/api/start", methods=["POST"])
def start():
    engine.start()
    return jsonify({"ok": True})

@app.route("/api/stop", methods=["POST"])
def stop():
    engine.stop()
    return jsonify({"ok": True})

def run():
    """Launch the web server"""
    import webbrowser
    import time

    # Start server in background
    def run_server():
        app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to start and open browser
    time.sleep(1)
    webbrowser.open('http://localhost:5001')

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        engine.stop()

if __name__ == "__main__":
    run()
