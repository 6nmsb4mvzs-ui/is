#!/usr/bin/env python3
"""
Launcher - Starts mods automation with enabled cheats
Implements mod functionality via input automation
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
    """Start the mods automation system"""
    try:
        from .mods_automation import system
    except (ImportError, ValueError):
        try:
            from is_engine.mods_automation import system
        except ImportError:
            logger.error("Failed to import mods_automation")
            return

    logger.info("Starting Idle Slayer Mods Automation...")
    logger.info("Based on: AutoBoost, AutoRage, AutoFarm, BonusStageCompleter, QuestAutoComplete, MinionCollector")

    # Load enabled cheats from config
    config = load_config()
    logger.info(f"Loaded cheat config: {list(config.keys())}")

    # Map cheats to mod names
    cheat_to_mod = {
        "autofarm_coins": "auto_farm",
        "autofarm_slayer": "auto_farm",
        "auto_ascend": "auto_boost",
        "auto_minions": "minion_collect",
        "auto_rage": "auto_rage",
        "quest_router": "quest_complete",
        "bonus_stage": "bonus_complete",
    }

    # Enable mods based on cheat config
    enabled_count = 0
    for cheat_id, enabled in config.items():
        if enabled and cheat_id in cheat_to_mod:
            mod_name = cheat_to_mod[cheat_id]
            system.enable_mod(mod_name)
            logger.info(f"Enabled: {cheat_id} → {mod_name}")
            enabled_count += 1

    logger.info(f"Total enabled mods: {enabled_count}")
    logger.info(f"Status: {system.get_status()}")

    # Start system
    system.start()
    logger.info("Mods automation running. Press Ctrl+C to stop.")

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        system.stop()
        logger.info("Mods automation stopped.")


if __name__ == "__main__":
    main()
