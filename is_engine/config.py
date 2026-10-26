#!/usr/bin/env python3
"""Configuration management"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager with auto-save"""

    def __init__(self, app_dir: Path):
        self.app_dir = app_dir
        self.config_file = app_dir / "config.json"
        self.data: Dict[str, Any] = {}
        self._load()

    def _load(self):
        """Load config from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.data = json.load(f)
                logger.info(f"Config loaded from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                self.data = {}
        else:
            self._init_defaults()

    def _init_defaults(self):
        """Initialize default config"""
        self.data = {
            "cheats": {
                "autofarm_coins": False,
                "autofarm_slayer": False,
                "autofarm_quest_temp": False,
                "autofarm_quest_normal": False,
                "autofarm_quest_event": False,
                "auto_ascend": False,
                "auto_minions": False,
                "auto_upgrades_1": False,
                "auto_upgrades_2": False,
                "auto_craft": False,
                "auto_ads": False,
            },
            "settings": {
                "game_resolution": "1280x720",
                "ui_port": 5000,
                "auto_update": True,
                "check_updates_interval": 3600,
                "autofarm_coins_stay_dimension": True,
            }
        }
        self._save()

    def _save(self):
        """Save config to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.data, f, indent=2)
            logger.info(f"Config saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value"""
        keys = key.split('.')
        val = self.data
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
        return val if val is not None else default

    def set(self, key: str, value: Any):
        """Set config value and save"""
        keys = key.split('.')
        d = self.data
        for k in keys[:-1]:
            if k not in d:
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value
        self._save()

    def toggle_cheat(self, cheat_id: str) -> bool:
        """Toggle cheat enabled state"""
        key = f"cheats.{cheat_id}"
        current = self.get(key, False)
        self.set(key, not current)
        return not current

    def is_cheat_enabled(self, cheat_id: str) -> bool:
        """Check if cheat is enabled"""
        return self.get(f"cheats.{cheat_id}", False)
