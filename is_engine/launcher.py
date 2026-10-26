#!/usr/bin/env python3
"""
Launcher - Starts AFK system with enabled cheats
Uses pixel-based game state detection (like AutoIt script)
"""

import logging
import time
import json
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('Launcher')


def load_config() -> dict:
    """Load cheat configuration from JSON"""
    config_path = Path.home() / ".idle_slayer_cheat" / "cheats.json"

    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")

    return {}


def main():
    """Start the AFK system"""
    try:
        from .afk_system import system
    except (ImportError, ValueError):
        # Try absolute import
        try:
            from is_engine.afk_system import system
        except ImportError:
            logger.error("Failed to import afk_system")
            return

    logger.info("Starting Idle Slayer AFK System...")
    logger.info("Using pixel-based game state detection")

    # Load enabled cheats
    config = load_config()
    logger.info(f"Loaded cheat config: {list(config.keys())}")

    # Map cheats to actions
    cheat_to_action = {
        "autofarm_coins": "basic_farming",
        "autofarm_slayer": "basic_farming",
        "auto_ascend": "collect_silver_box",
        "auto_minions": "collect_minion",
        "auto_ads": "collect_silver_box",
        "auto_rage": "rage_megahorde",
        "quest_router": "claim_quests",
    }

    # Enable actions based on cheat config
    for cheat_id, enabled in config.items():
        if enabled and cheat_id in cheat_to_action:
            action_name = cheat_to_action[cheat_id]
            system.enable_action(action_name)
            logger.info(f"Enabled: {cheat_id} → {action_name}")

    # Always enable core collection actions
    core_actions = ["collect_silver_box", "claim_quests", "rage_soul_bonus", "collect_minion"]
    for action in core_actions:
        system.enable_action(action)

    logger.info("Core actions enabled: " + ", ".join(core_actions))
    logger.info(f"Status: {system.get_status()}")

    # Start system
    system.start()
    logger.info("AFK System running. Press Ctrl+C to stop.")

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        system.stop()
        logger.info("AFK System stopped.")


if __name__ == "__main__":
    main()
