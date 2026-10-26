#!/usr/bin/env python3
"""Standalone Mod Menu App for Idle Slayer

Native macOS app window that displays cheat toggles.
Runs independently with Flask embedded server.
"""

import sys
import json
import threading
import webbrowser
import time
from pathlib import Path
from flask import Flask, render_template_string
from .core import engine, CheatMode
from .cheats import CHEATS, get_cheat_descriptions

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# HTML for standalone mod menu
MOD_MENU_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Idle Slayer Mod Menu</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 0;
            overflow: hidden;
        }

        .container {
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        header {
            background: linear-gradient(90deg, #00d4ff, #ff00ff);
            color: #000;
            padding: 16px;
            font-weight: 700;
            font-size: 18px;
            box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3);
        }

        .tabs {
            display: flex;
            gap: 0;
            background: rgba(0, 0, 0, 0.3);
            border-bottom: 1px solid #00d4ff;
        }

        .tab-btn {
            flex: 1;
            padding: 12px;
            background: none;
            border: none;
            color: #909090;
            cursor: pointer;
            transition: all 0.3s;
            border-bottom: 3px solid transparent;
            font-weight: 600;
            font-size: 14px;
        }

        .tab-btn.active {
            color: #00d4ff;
            border-bottom-color: #00d4ff;
            background: rgba(0, 212, 255, 0.05);
        }

        .content {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            display: none;
        }

        .content.active {
            display: block;
        }

        .content::-webkit-scrollbar {
            width: 8px;
        }

        .content::-webkit-scrollbar-track {
            background: rgba(0, 212, 255, 0.1);
        }

        .content::-webkit-scrollbar-thumb {
            background: #00d4ff;
            border-radius: 4px;
        }

        .cheat-item {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid #00d4ff;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            transition: all 0.2s;
        }

        .cheat-item:hover {
            background: rgba(0, 212, 255, 0.1);
            transform: translateX(4px);
        }

        .cheat-item.active {
            background: rgba(0, 255, 0, 0.1);
            border-color: #00ff00;
        }

        .cheat-info h3 {
            color: #00d4ff;
            font-size: 14px;
            margin-bottom: 4px;
        }

        .cheat-info p {
            color: #909090;
            font-size: 12px;
        }

        .toggle {
            width: 50px;
            height: 26px;
            background: #444;
            border: none;
            border-radius: 13px;
            cursor: pointer;
            position: relative;
            transition: background 0.3s;
        }

        .toggle.on {
            background: #00ff00;
        }

        .toggle::after {
            content: '';
            position: absolute;
            width: 22px;
            height: 22px;
            background: white;
            border-radius: 11px;
            top: 2px;
            left: 2px;
            transition: left 0.3s;
        }

        .toggle.on::after {
            left: 26px;
        }

        .setting-item {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid #00d4ff;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
        }

        .setting-item label {
            color: #00d4ff;
            font-weight: 600;
            display: block;
            margin-bottom: 8px;
            font-size: 12px;
        }

        .setting-value {
            color: #e0e0e0;
            font-size: 13px;
        }

        .button-group {
            display: flex;
            gap: 8px;
            margin-top: 16px;
        }

        button.btn {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 13px;
            transition: all 0.3s;
        }

        .btn-start {
            background: linear-gradient(135deg, #00ff00, #00aa00);
            color: #000;
        }

        .btn-start:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 255, 0, 0.4);
        }

        .btn-stop {
            background: linear-gradient(135deg, #ff4444, #aa0000);
            color: #fff;
        }

        .btn-stop:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 68, 68, 0.4);
        }

        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            background: #00d4ff;
            color: #000;
            border-radius: 4px;
            font-weight: 600;
            font-size: 11px;
        }

        .status-badge.running {
            background: #00ff00;
        }

        footer {
            border-top: 1px solid #00d4ff;
            padding: 12px 16px;
            background: rgba(0, 0, 0, 0.3);
            font-size: 12px;
            color: #909090;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>⚔️ Idle Slayer Mod Menu</header>

        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('cheats')">Cheats</button>
            <button class="tab-btn" onclick="switchTab('settings')">Settings</button>
        </div>

        <div id="cheats-tab" class="content active" style="padding: 16px;">
            <!-- Cheats will be injected here -->
        </div>

        <div id="settings-tab" class="content" style="padding: 16px;">
            <div class="setting-item">
                <label>Engine Status</label>
                <div class="setting-value">
                    <span class="status-badge running" id="engine-status">🟢 Stopped</span>
                </div>
            </div>

            <div class="setting-item">
                <label>Active Cheats</label>
                <div class="setting-value" id="active-count">0 / 18</div>
            </div>

            <div class="setting-item">
                <label>Version</label>
                <div class="setting-value">v1.0.0 (Latest)</div>
            </div>

            <div class="button-group">
                <button class="btn btn-start" onclick="startEngine()">▶️ START</button>
                <button class="btn btn-stop" onclick="stopEngine()">⏹ STOP</button>
            </div>
        </div>

        <footer>
            Mod Menu v1.0 | Press <strong>⌘ + M</strong> to toggle (when in game)
        </footer>
    </div>

    <script>
        let activeCount = 0;

        function switchTab(tab) {
            // Hide all
            document.querySelectorAll('.content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));

            // Show selected
            document.getElementById(tab + '-tab').classList.add('active');
            event.target.classList.add('active');
        }

        function toggleCheat(element, cheatId) {
            const toggle = element.querySelector('.toggle');
            const isActive = element.classList.toggle('active');
            toggle.classList.toggle('on');

            // Send to backend
            fetch('/api/toggle/' + cheatId, { method: 'POST' });

            activeCount += isActive ? 1 : -1;
            document.getElementById('active-count').textContent = activeCount + ' / 18';
        }

        function startEngine() {
            fetch('/api/start', { method: 'POST' });
            document.getElementById('engine-status').textContent = '🟢 Running';
        }

        function stopEngine() {
            fetch('/api/stop', { method: 'POST' });
            document.getElementById('engine-status').textContent = '⚫ Stopped';
        }

        // Load cheats
        fetch('/api/cheats')
            .then(r => r.json())
            .then(data => {
                const container = document.querySelector('#cheats-tab');
                container.innerHTML = '';

                for (const [id, info] of Object.entries(data.cheats)) {
                    const div = document.createElement('div');
                    div.className = 'cheat-item' + (info.enabled ? ' active' : '');
                    div.onclick = function() { toggleCheat(this, id); };

                    div.innerHTML = `
                        <div class="cheat-info">
                            <h3>${info.name}</h3>
                            <p>${info.desc}</p>
                        </div>
                        <button class="toggle${info.enabled ? ' on' : ''}"></button>
                    `;

                    container.appendChild(div);
                    if (info.enabled) activeCount++;
                }

                document.getElementById('active-count').textContent = activeCount + ' / 18';
            });

        // Update status every 2s
        setInterval(() => {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    const status = document.getElementById('engine-status');
                    if (data.running) {
                        status.textContent = '🟢 Running';
                        status.className = 'status-badge running';
                    } else {
                        status.textContent = '⚫ Stopped';
                        status.className = 'status-badge';
                    }
                });
        }, 2000);
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(MOD_MENU_HTML)


@app.route('/api/cheats')
def get_cheats():
    descriptions = get_cheat_descriptions()
    cheats = {}
    for key, cheat in CHEATS.items():
        cheats[key] = {
            "name": cheat.name,
            "desc": descriptions.get(key, ""),
            "enabled": engine.state.active_cheats.get(CheatMode(key), False)
        }
    return {"cheats": cheats}


@app.route('/api/toggle/<cheat_id>', methods=['POST'])
def toggle_cheat(cheat_id):
    try:
        mode = CheatMode(cheat_id)
        engine.state.toggle_cheat(mode)
        return {"success": True}
    except:
        return {"error": "Invalid cheat"}, 400


@app.route('/api/status')
def status():
    return engine.get_status()


@app.route('/api/start', methods=['POST'])
def start():
    engine.start()
    return {"success": True}


@app.route('/api/stop', methods=['POST'])
def stop():
    engine.stop()
    return {"success": True}


def launch_app(port=5001):
    """Launch the mod menu with in-game overlay"""
    # Start Flask in background
    def run_flask():
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)

    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Wait for server to start
    time.sleep(1)

    # Launch in-game overlay instead of browser
    try:
        from .overlay import launch_overlay
        overlay = launch_overlay(port=port)
    except ImportError:
        # Fallback to browser if overlay fails
        webbrowser.open(f'http://localhost:{port}')

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        engine.stop()


if __name__ == '__main__':
    launch_app()
