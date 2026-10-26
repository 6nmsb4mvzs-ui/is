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
    logger.info("=" * 70)
    logger.info("LAUNCHER STARTUP")
    logger.info("=" * 70)

    try:
        from .mods_automation import system
        logger.info("✓ Imported mods_automation (relative)")
    except (ImportError, ValueError) as e:
        logger.warning(f"Relative import failed: {e}")
        try:
            from is_engine.mods_automation import system
            logger.info("✓ Imported mods_automation (absolute)")
        except ImportError as e2:
            logger.error(f"✗ Failed to import mods_automation: {e2}")
            return

    logger.info("Starting Idle Slayer Mods Automation...")

    # Load enabled cheats from config
    config_path = Path.home() / ".idle_slayer_cheat" / "cheats.json"
    logger.info(f"Config file: {config_path}")
    logger.info(f"Config exists: {config_path.exists()}")

    config = load_config()
    logger.info(f"Config contents ({len(config)} items):")
    for cheat_id, enabled in sorted(config.items()):
        logger.info(f"  {cheat_id:30} = {enabled}")

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
    disabled_count = 0
    unmapped_count = 0

    logger.info("-" * 70)
    logger.info("Enabling mods:")

    for cheat_id, enabled in config.items():
        if enabled:
            if cheat_id in cheat_to_mod:
                mod_name = cheat_to_mod[cheat_id]
                system.enable_mod(mod_name)
                logger.info(f"  ✓ {cheat_id:28} → {mod_name}")
                enabled_count += 1
            else:
                logger.info(f"  ⚠ {cheat_id:28} (no mod implementation)")
                unmapped_count += 1
        else:
            disabled_count += 1

    logger.info("-" * 70)
    logger.info(f"Summary: {enabled_count} enabled | {disabled_count} disabled | {unmapped_count} unmapped")

    status = system.get_status()
    logger.info(f"System status: {status}")
    logger.info("-" * 70)

    # Start system
    if enabled_count > 0:
        logger.info("Starting mods automation loop...")
        system.start()
        logger.info("✓ Mods automation started. Press Ctrl+C to stop.")
        logger.info("=" * 70)
    else:
        logger.warning("✗ No mods enabled - nothing to do")
        logger.info("=" * 70)
        return

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
