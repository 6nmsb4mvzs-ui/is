#!/usr/bin/env python3
"""Idle Slayer macOS Cheat Engine - Core Module"""

import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CheatMode(Enum):
    # TIER 1: Core Farming
    COINS = "autofarm_coins"
    SLAYER = "autofarm_slayer"
    QUEST_TEMP = "autofarm_quest_temp"
    QUEST_NORM = "autofarm_quest_normal"
    QUEST_EVENT = "autofarm_quest_event"
    ASCEND = "auto_ascend"
    MINIONS = "auto_minions"
    UPGRADES_1 = "auto_upgrades_1"
    UPGRADES_2 = "auto_upgrades_2"
    CRAFT = "auto_craft"
    ADS = "auto_ads"

    # TIER 2: Advanced Systems
    RAGE = "auto_rage"
    QUEST_ROUTER = "quest_router"
    GEAR_CRAFT_AI = "gear_craft_ai"

    # TIER 3: Complex & Specialized
    BONUS_STAGE = "bonus_stage"
    CHEST_HUNT_SOLVER = "chest_hunt_solver"
    UA_PLANNER = "ua_planner"
    MINIGAME_RUNNER = "minigame_runner"


@dataclass
class CheatState:
    """Holds state for all active cheats"""
    active_cheats: dict = field(default_factory=dict)  # CheatMode -> bool
    running: bool = False
    paused: bool = False
    config: dict = field(default_factory=dict)

    def toggle_cheat(self, mode: CheatMode):
        """Toggle a cheat on/off"""
        current = self.active_cheats.get(mode, False)
        self.active_cheats[mode] = not current
        logger.info(f"Cheat {mode.value} toggled to {not current}")
        return not current


class AutomationEngine:
    """Core automation engine for Idle Slayer"""

    def __init__(self):
        self.state = CheatState()
        self.handlers: dict[CheatMode, Callable] = {}
        self.main_thread: Optional[threading.Thread] = None
        self.running = False

    def register_handler(self, mode: CheatMode, handler: Callable):
        """Register a handler for a cheat mode"""
        self.handlers[mode] = handler

    def start(self):
        """Start the automation engine"""
        if self.running:
            return
        self.running = True
        self.state.running = True
        self.main_thread = threading.Thread(target=self._run_loop, daemon=True)
        self.main_thread.start()
        logger.info("Automation engine started")

    def stop(self):
        """Stop the automation engine"""
        self.running = False
        self.state.running = False
        if self.main_thread:
            self.main_thread.join(timeout=5)
        logger.info("Automation engine stopped")

    def pause(self):
        """Pause all cheats"""
        self.state.paused = True
        logger.info("Automation paused")

    def resume(self):
        """Resume all cheats"""
        self.state.paused = False
        logger.info("Automation resumed")

    def _run_loop(self):
        """Main event loop"""
        while self.running:
            if not self.state.paused:
                for mode, enabled in self.state.active_cheats.items():
                    if enabled and mode in self.handlers:
                        try:
                            self.handlers[mode]()
                        except Exception as e:
                            logger.error(f"Error in {mode.value}: {e}")
            time.sleep(0.5)

    def get_status(self) -> dict:
        """Get current status"""
        return {
            "running": self.running,
            "paused": self.state.paused,
            "active_cheats": {k.value: v for k, v in self.state.active_cheats.items()},
            "config": self.state.config
        }


# Global engine instance
engine = AutomationEngine()
