#!/usr/bin/env python3
"""Main entry point for Idle Slayer Cheat Engine"""

import sys
import logging
import webbrowser
from pathlib import Path
from .core import engine, CheatMode
from .cheats import CHEATS
from .ui import UIServer
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_app_dir() -> Path:
    """Setup application directory"""
    app_dir = Path.home() / ".idle_slayer_cheat"
    app_dir.mkdir(exist_ok=True)
    logs_dir = app_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    return app_dir


def register_cheat_handlers():
    """Register all cheat handlers with engine"""
    for cheat_id, cheat_obj in CHEATS.items():
        mode = CheatMode(cheat_id)
        engine.register_handler(mode, cheat_obj.run)


def main():
    """Main entry point"""
    logger.info("=" * 50)
    logger.info("Idle Slayer Cheat Engine macOS v1.0.0")
    logger.info("=" * 50)

    # Setup
    app_dir = setup_app_dir()
    logger.info(f"App directory: {app_dir}")

    # Register cheats
    register_cheat_handlers()
    logger.info(f"Registered {len(CHEATS)} cheats")

    # Start UI server
    ui = UIServer(app_dir, port=5000)
    logger.info("Starting UI server...")

    # Open browser
    logger.info("Opening browser...")
    time.sleep(1)  # Give server time to start
    webbrowser.open('http://localhost:5000')

    # Run Flask app
    try:
        ui.run(debug=False)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        engine.stop()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
