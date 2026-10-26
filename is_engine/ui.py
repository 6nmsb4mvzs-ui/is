#!/usr/bin/env python3
"""Web-based UI for Idle Slayer Cheat Engine"""

import json
import logging
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from .core import engine, CheatMode
from .cheats import CHEATS, get_cheat_descriptions
from .updater import GitHubUpdater
import threading

logger = logging.getLogger(__name__)


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Idle Slayer Cheat Engine</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1e1e2e 0%, #2a2a3e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 900px; margin: 0 auto; }
        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px 0;
            border-bottom: 2px solid #00d4ff;
        }
        h1 {
            font-size: 32px;
            background: linear-gradient(90deg, #00d4ff, #ff00ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .status {
            display: flex;
            gap: 20px;
            justify-content: center;
            margin-top: 15px;
            flex-wrap: wrap;
        }
        .status-item {
            background: rgba(0, 0, 0, 0.3);
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 14px;
            border-left: 3px solid #00d4ff;
        }
        .status-item.running { border-left-color: #00ff00; }
        .status-item.paused { border-left-color: #ff9800; }

        .controls {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
        }
        .btn-start {
            background: linear-gradient(135deg, #00ff00, #00aa00);
            color: white;
        }
        .btn-start:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,255,0,0.4); }
        .btn-stop {
            background: linear-gradient(135deg, #ff4444, #aa0000);
            color: white;
        }
        .btn-pause {
            background: linear-gradient(135deg, #ff9800, #cc7700);
            color: white;
        }
        .btn-update {
            background: linear-gradient(135deg, #00d4ff, #0099cc);
            color: white;
        }

        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #00d4ff;
            overflow-x: auto;
        }
        .tab {
            padding: 10px 20px;
            background: none;
            border: none;
            color: #909090;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        .tab.active {
            color: #00d4ff;
            border-bottom-color: #00d4ff;
        }

        .cheats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .cheat-card {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid #00d4ff;
            border-radius: 8px;
            padding: 15px;
            transition: all 0.3s;
        }
        .cheat-card:hover {
            background: rgba(0, 212, 255, 0.1);
            transform: translateY(-2px);
        }
        .cheat-card.active {
            background: rgba(0, 255, 0, 0.1);
            border-color: #00ff00;
        }
        .cheat-name {
            font-weight: 600;
            margin-bottom: 5px;
            color: #00d4ff;
        }
        .cheat-desc {
            font-size: 12px;
            color: #909090;
            margin-bottom: 10px;
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

        .settings {
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid #00d4ff;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .setting-item {
            margin-bottom: 15px;
        }
        .setting-label {
            font-weight: 600;
            margin-bottom: 5px;
            display: block;
        }
        .version-check {
            background: rgba(0, 212, 255, 0.1);
            padding: 15px;
            border-radius: 8px;
            border-left: 3px solid #00d4ff;
        }
        .version-new {
            color: #00ff00;
        }
        .version-current {
            color: #ff9800;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .pulsing { animation: pulse 1s infinite; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>⚔️ Idle Slayer Cheat Engine</h1>
            <div class="status">
                <div class="status-item" id="engine-status">Stopped</div>
                <div class="status-item" id="game-status">Game: Inactive</div>
                <div class="status-item" id="cheat-count">Active: 0</div>
            </div>
        </header>

        <div class="controls">
            <button class="btn-start" onclick="startEngine()">▶️ START</button>
            <button class="btn-pause" onclick="pauseEngine()">⏸ PAUSE</button>
            <button class="btn-stop" onclick="stopEngine()">⏹ STOP</button>
            <button class="btn-update" onclick="checkUpdates()">🔄 CHECK UPDATES</button>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('cheats')">Cheats</button>
            <button class="tab" onclick="switchTab('settings')">Settings</button>
        </div>

        <div id="cheats-tab">
            <div class="cheats-grid" id="cheats-container"></div>
        </div>

        <div id="settings-tab" style="display:none;">
            <div class="settings">
                <h2>Update Status</h2>
                <div class="version-check">
                    <div class="setting-item">
                        <span class="setting-label">Current Version:</span>
                        <span class="version-current" id="current-version">v1.0.0</span>
                    </div>
                    <div class="setting-item">
                        <span class="setting-label">Latest Version:</span>
                        <span class="version-new" id="latest-version">-</span>
                    </div>
                    <div class="setting-item">
                        <button class="btn-update" onclick="applyUpdate()">Apply Update</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let updateStatus = null;

        async function apiCall(endpoint, method = 'GET', data = null) {
            const opts = { method };
            if (data) {
                opts.headers = { 'Content-Type': 'application/json' };
                opts.body = JSON.stringify(data);
            }
            const resp = await fetch(`/api${endpoint}`, opts);
            return resp.json();
        }

        async function loadCheats() {
            const data = await apiCall('/cheats');
            const container = document.getElementById('cheats-container');
            container.innerHTML = '';
            for (const [id, cheat] of Object.entries(data.cheats)) {
                const card = document.createElement('div');
                card.className = 'cheat-card' + (cheat.enabled ? ' active' : '');
                card.innerHTML = `
                    <div class="cheat-name">${cheat.name}</div>
                    <div class="cheat-desc">${cheat.desc}</div>
                    <button class="toggle${cheat.enabled ? ' on' : ''}"
                            onclick="toggleCheat('${id}')"></button>
                `;
                container.appendChild(card);
            }
            updateStatus();
        }

        async function toggleCheat(id) {
            await apiCall(`/toggle_cheat/${id}`, 'POST');
            loadCheats();
        }

        async function startEngine() {
            await apiCall('/start', 'POST');
            updateStatus();
        }

        async function pauseEngine() {
            await apiCall('/pause', 'POST');
            updateStatus();
        }

        async function stopEngine() {
            await apiCall('/stop', 'POST');
            updateStatus();
        }

        async function updateStatus() {
            const data = await apiCall('/status');
            document.getElementById('engine-status').textContent =
                data.running ? '🟢 Running' : '⚫ Stopped';
            document.getElementById('engine-status').className =
                'status-item' + (data.running ? ' running' : '');
            document.getElementById('cheat-count').textContent =
                `Active: ${Object.values(data.active_cheats).filter(x => x).length}`;
        }

        async function checkUpdates() {
            updateStatus = await apiCall('/check_updates');
            document.getElementById('latest-version').textContent =
                updateStatus.latest_version || 'Up to date';
            document.getElementById('current-version').textContent =
                `v${updateStatus.current_version}`;
        }

        async function applyUpdate() {
            if (updateStatus?.update_available) {
                if (confirm('Update will restart the app. Continue?')) {
                    await apiCall('/apply_update', 'POST');
                }
            }
        }

        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('[id$="-tab"]').forEach(t => t.style.display = 'none');
            event.target.classList.add('active');
            document.getElementById(`${tab}-tab`).style.display = 'block';
        }

        setInterval(updateStatus, 2000);
        setInterval(checkUpdates, 60000);
        loadCheats();
    </script>
</body>
</html>
"""


class UIServer:
    """Flask UI server"""

    def __init__(self, app_dir: Path, port: int = 5000):
        self.app = Flask(__name__)
        self.app_dir = app_dir
        self.port = port
        self.updater = GitHubUpdater(app_dir)
        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route('/')
        def index():
            return render_template_string(HTML_TEMPLATE)

        @self.app.route('/api/cheats', methods=['GET'])
        def get_cheats():
            descriptions = get_cheat_descriptions()
            cheats = {}
            for key, cheat in CHEATS.items():
                cheats[key] = {
                    "name": cheat.name,
                    "desc": descriptions.get(key, ""),
                    "enabled": engine.state.active_cheats.get(CheatMode(key), False)
                }
            return jsonify({"cheats": cheats})

        @self.app.route('/api/toggle_cheat/<cheat_id>', methods=['POST'])
        def toggle_cheat(cheat_id):
            try:
                mode = CheatMode(cheat_id)
                engine.state.toggle_cheat(mode)
                return jsonify({"success": True})
            except Exception as e:
                return jsonify({"error": str(e)}), 400

        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            return jsonify(engine.get_status())

        @self.app.route('/api/start', methods=['POST'])
        def start():
            engine.start()
            return jsonify({"success": True})

        @self.app.route('/api/stop', methods=['POST'])
        def stop():
            engine.stop()
            return jsonify({"success": True})

        @self.app.route('/api/pause', methods=['POST'])
        def pause():
            engine.pause()
            return jsonify({"success": True})

        @self.app.route('/api/resume', methods=['POST'])
        def resume():
            engine.resume()
            return jsonify({"success": True})

        @self.app.route('/api/check_updates', methods=['GET'])
        def check_updates():
            return jsonify(self.updater.get_status())

        @self.app.route('/api/apply_update', methods=['POST'])
        def apply_update():
            from .updater import restart_app
            status = self.updater.get_status()
            if status['update_available']:
                if self.updater.download_update(status['latest_version']):
                    restart_app()
                    return jsonify({"success": True})
            return jsonify({"error": "No update available"}), 400

    def run(self, debug: bool = False):
        """Start the UI server"""
        logger.info(f"Starting UI server on port {self.port}")
        self.app.run(host='127.0.0.1', port=self.port, debug=debug, use_reloader=False)
