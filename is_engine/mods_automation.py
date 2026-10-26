#!/usr/bin/env python3
"""
Mods automation system - reimplementation of Idle Slayer mods for macOS
Based on: AutoBoost, BonusStageCompleter, DoorPuzzleSkip, RestoreLastMap, etc.
"""

import time
import threading
import logging
import subprocess
from typing import Optional, Dict
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('ModsAutomation')


class GameInput:
    """Input automation via AppleScript"""

    def __init__(self):
        self.lock = threading.Lock()

    def key_press(self, key: str, duration: float = 0.1, repeat: int = 1):
        """Press key via AppleScript"""
        keycodes = {
            # Letters and common keys
            "a": 0, "s": 1, "d": 2, "f": 3, "h": 4, "g": 5, "z": 6, "x": 7, "c": 8, "v": 9,
            "b": 11, "q": 12, "w": 13, "e": 14, "r": 15, "y": 16, "t": 17, "1": 18, "2": 19,
            "3": 20, "4": 21, "6": 22, "5": 23, "=": 24, "9": 25, "7": 26, "-": 27, "8": 28,
            "0": 29, "]": 30, "o": 31, "u": 32, "[": 33, "i": 34, "p": 35, "return": 36,
            "l": 37, "j": 38, "'": 39, "k": 40, ";": 41, "\\": 42, ",": 43, "/": 44, "n": 45,
            "m": 46, ".": 47, "tab": 48, "space": 49,

            # Arrow keys and special
            "up": 126, "down": 125, "left": 123, "right": 124,
            "esc": 53, "delete": 51, "shift": 56, "control": 59, "option": 58,
        }

        keycode = keycodes.get(key.lower())
        if keycode is None:
            logger.warning(f"Unknown key: {key}")
            return

        with self.lock:
            for _ in range(repeat):
                try:
                    subprocess.run(
                        ['osascript', '-e', f'tell application "System Events" to key code {keycode}'],
                        capture_output=True, timeout=1
                    )
                    time.sleep(duration)
                except Exception as e:
                    logger.error(f"Key press failed: {e}")

    def click(self, x: int, y: int, delay: float = 0.2):
        """Click at position"""
        with self.lock:
            try:
                subprocess.run(
                    ['osascript', '-e', f'tell application "System Events" to click at {{{x}, {y}}}'],
                    capture_output=True, timeout=1
                )
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Click failed: {e}")


class Mod:
    """Base class for mod automation"""

    def __init__(self, name: str, input_handler: GameInput):
        self.name = name
        self.input = input_handler
        self.enabled = False
        self.last_run = 0
        self.min_interval = 1.0

    def can_run(self) -> bool:
        return time.time() - self.last_run >= self.min_interval

    def run(self):
        """Override in subclass"""
        pass

    def log(self, msg: str):
        logger.info(f"[{self.name}] {msg}")


class AutoBoost(Mod):
    """Auto Boost and Wind Dash - press B/N on cooldown"""

    def __init__(self, input_handler: GameInput):
        super().__init__("AutoBoost", input_handler)
        self.min_interval = 15.0  # Boost cooldown ~15s

    def run(self):
        if not self.enabled or not self.can_run():
            return

        # Press B for boost
        self.input.key_press("b", duration=0.1)
        self.log("Boost activated")
        self.last_run = time.time()

        # Optionally press N for wind dash (5s later)
        time.sleep(5)
        self.input.key_press("n", duration=0.1)
        self.log("Wind dash activated")


class AutoRage(Mod):
    """Auto Rage - press R on cooldown"""

    def __init__(self, input_handler: GameInput):
        super().__init__("AutoRage", input_handler)
        self.min_interval = 12.0  # Rage cooldown ~12s

    def run(self):
        if not self.enabled or not self.can_run():
            return

        self.input.key_press("r", duration=0.1)
        self.log("Rage activated")
        self.last_run = time.time()


class AutoClimbTower(Mod):
    """Auto climb tower - continuous jump + move"""

    def __init__(self, input_handler: GameInput):
        super().__init__("AutoClimbTower", input_handler)
        self.min_interval = 0.5  # Action every 0.5s

    def run(self):
        if not self.enabled or not self.can_run():
            return

        # Jump up
        self.input.key_press("space", duration=0.2)
        # Move right to avoid hazards
        self.input.key_press("right", duration=0.2)

        self.last_run = time.time()


class AutoFarm(Mod):
    """Auto Farm - continuous attack and movement"""

    def __init__(self, input_handler: GameInput):
        super().__init__("AutoFarm", input_handler)
        self.min_interval = 0.3

    def run(self):
        if not self.enabled or not self.can_run():
            return

        # Jump towards enemies
        self.input.key_press("up", duration=0.2)
        # Move right
        self.input.key_press("right", duration=0.2)
        # Attack (spacebar or mouse click)
        self.input.key_press("space", duration=0.1)

        self.last_run = time.time()


class BonusStageAutoComplete(Mod):
    """Bonus Stage Completer - auto-complete bonus stages"""

    def __init__(self, input_handler: GameInput):
        super().__init__("BonusStageAutoComplete", input_handler)
        self.min_interval = 1.0

    def run(self):
        if not self.enabled or not self.can_run():
            return

        # In bonus stage: collect spheres and complete
        # This is done via spacebar to interact/collect
        self.input.key_press("space", duration=0.5)
        self.log("Bonus stage interaction")
        self.last_run = time.time()


class QuestAutoComplete(Mod):
    """Auto-complete quests - click quest button and claim"""

    def __init__(self, input_handler: GameInput):
        super().__init__("QuestAutoComplete", input_handler)
        self.min_interval = 5.0

    def run(self):
        if not self.enabled or not self.can_run():
            return

        # Click quest button location (approximate - needs calibration)
        self.input.click(1130, 610, delay=0.3)
        # Press return to confirm
        self.input.key_press("return", duration=0.2)

        self.log("Quest claimed")
        self.last_run = time.time()


class MinionCollector(Mod):
    """Auto-collect minion rewards"""

    def __init__(self, input_handler: GameInput):
        super().__init__("MinionCollector", input_handler)
        self.min_interval = 30.0  # Check every 30s

    def run(self):
        if not self.enabled or not self.can_run():
            return

        # Click minion button (approximate - needs calibration)
        self.input.click(99, 113, delay=0.3)

        self.log("Minion collected")
        self.last_run = time.time()


class ModsAutomation:
    """Master automation system - all mods"""

    def __init__(self):
        self.input = GameInput()
        self.mods: Dict[str, Mod] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.loop_interval = 0.1  # 100ms main loop

        self._setup_mods()

    def _setup_mods(self):
        """Initialize all mods"""
        self.mods = {
            "auto_boost": AutoBoost(self.input),
            "auto_rage": AutoRage(self.input),
            "auto_climb": AutoClimbTower(self.input),
            "auto_farm": AutoFarm(self.input),
            "bonus_complete": BonusStageAutoComplete(self.input),
            "quest_complete": QuestAutoComplete(self.input),
            "minion_collect": MinionCollector(self.input),
        }
        logger.info(f"Initialized {len(self.mods)} mods")

    def enable_mod(self, mod_name: str):
        """Enable a mod"""
        if mod_name in self.mods:
            self.mods[mod_name].enabled = True
            logger.info(f"Enabled: {mod_name}")
        else:
            logger.warning(f"Mod not found: {mod_name} (available: {list(self.mods.keys())})")

    def disable_mod(self, mod_name: str):
        """Disable a mod"""
        if mod_name in self.mods:
            self.mods[mod_name].enabled = False
            logger.info(f"Disabled: {mod_name}")
        else:
            logger.warning(f"Mod not found: {mod_name}")

    def start(self):
        """Start automation"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._main_loop, daemon=True)
        self.thread.start()
        logger.info("Mods automation started")

    def stop(self):
        """Stop automation"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Mods automation stopped")

    def _main_loop(self):
        """Main automation loop"""
        while self.running:
            try:
                # Run all enabled mods
                for mod in self.mods.values():
                    if mod.enabled:
                        try:
                            mod.run()
                        except Exception as e:
                            logger.error(f"Mod error: {e}")

                time.sleep(self.loop_interval)
            except Exception as e:
                logger.error(f"Loop error: {e}")
                time.sleep(1)

    def get_status(self) -> dict:
        """Get system status"""
        return {
            "running": self.running,
            "enabled_mods": [k for k, v in self.mods.items() if v.enabled],
            "total_mods": len(self.mods),
        }


# Global instance
system = ModsAutomation()
