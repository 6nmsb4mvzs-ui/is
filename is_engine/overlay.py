#!/usr/bin/env python3
"""In-game overlay - opens web UI in browser"""

import threading
import webbrowser
import time
import logging

logger = logging.getLogger(__name__)


class CheatOverlay:
    def __init__(self, port=5001):
        self.port = port

    def run(self):
        """Launch the cheat menu UI"""
        logger.info(f"Opening Idle Slayer Cheat Menu at localhost:{self.port}")
        time.sleep(0.5)

        try:
            webbrowser.open(f'http://localhost:{self.port}')
        except Exception as e:
            logger.error(f"Could not open browser: {e}")

        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass


def launch_overlay(port=5001):
    """Launch overlay in background thread"""
    overlay = CheatOverlay(port=port)

    thread = threading.Thread(target=overlay.run, daemon=True)
    thread.start()

    return overlay
