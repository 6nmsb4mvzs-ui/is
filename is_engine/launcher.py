#!/usr/bin/env python3
"""Idle Slayer Cheat Engine - Proper launcher with handler registration"""

import sys
import json
import time
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    try:
        # Import after path is set
        from .core import engine, CheatMode
        from .cheats import CHEATS

        logger.info("Idle Slayer Cheat Engine v2.1 Starting...")
        logger.info(f"Cheats available: {len(CHEATS)}")

        # Register all cheat handlers
        for cheat_id, cheat_obj in CHEATS.items():
            try:
                mode = CheatMode(cheat_id)
                engine.register_handler(mode, cheat_obj.run)
                logger.info(f"  ✓ Registered {mode.value}")
            except Exception as e:
                logger.error(f"  ✗ Failed to register {cheat_id}: {e}")

        logger.info(f"Total handlers registered: {len(engine.handlers)}")

        # Load saved state
        config_file = Path.home() / ".idle_slayer_cheat" / "cheats.json"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    saved_state = json.load(f)
                    loaded_count = 0
                    for cheat_id, enabled in saved_state.items():
                        try:
                            mode = CheatMode(cheat_id)
                            engine.state.active_cheats[mode] = enabled
                            if enabled:
                                loaded_count += 1
                        except:
                            pass
                    logger.info(f"Loaded state: {loaded_count} cheats enabled")
            except Exception as e:
                logger.error(f"Failed to load state: {e}")

        # Start engine
        logger.info("Starting automation engine...")
        engine.start()
        logger.info("Engine running. Press Ctrl+C to stop.")

        # Keep alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping engine...")
            engine.stop()
            logger.info("Engine stopped.")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
