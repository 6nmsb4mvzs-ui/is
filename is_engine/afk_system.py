#!/usr/bin/env python3
"""
AFK System - Based on proven AutoIt automation patterns
Uses exact pixel detection + action sequences (not random key presses)
"""

import time
import threading
import logging
import subprocess
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass

try:
    from PIL import ImageGrab
    import numpy as np
    HAS_CV = True
except ImportError:
    HAS_CV = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('AFKSystem')


@dataclass
class Pixel:
    """Exact pixel marker for game state detection"""
    x: int
    y: int
    color: str  # Hex format: "0xABCDEF"
    name: str = ""

    @property
    def hex_value(self) -> int:
        return int(self.color, 16)

    @property
    def rgb(self) -> Tuple[int, int, int]:
        """Convert hex to RGB"""
        val = self.hex_value
        return ((val >> 16) & 255, (val >> 8) & 255, val & 255)

    def detect(self, tolerance: int = 20, debug: bool = False) -> bool:
        """Check if this exact pixel is at this location"""
        try:
            screenshot = ImageGrab.grab()
            if self.x < 0 or self.y < 0 or self.x >= screenshot.width or self.y >= screenshot.height:
                if debug:
                    logger.debug(f"{self.name}: Out of bounds ({self.x}, {self.y})")
                return False

            pixel = screenshot.getpixel((self.x, self.y))[:3]
            expected = self.rgb
            match = all(abs(pixel[i] - expected[i]) <= tolerance for i in range(3))

            if debug:
                if match:
                    logger.info(f"✓ {self.name} DETECTED at ({self.x},{self.y}): {pixel} vs {expected}")
                else:
                    logger.debug(f"✗ {self.name}: got {pixel}, expected {expected} (±{tolerance})")

            return match
        except Exception as e:
            if debug:
                logger.error(f"{self.name}: Error: {e}")
            return False


class GameState:
    """Game state detector - mirrors AutoIt script logic"""

    # UI Markers (from AutoIt script analysis)
    SILVER_BOX = Pixel(650, 36, "0xCA9700", "silver_box")
    MEGAHORDE = Pixel(385, 280, "0x140C1C", "megahorde_ready")
    QUEST_AVAILABLE = Pixel(1130, 610, "0xCBCB4C", "quest_popup")
    SOUL_BONUS = Pixel(625, 143, "0xA86D0A", "soul_bonus")  # Range: 625-629, 143-214
    MINION_READY = Pixel(99, 113, "0xFFFF7A", "minion_ready")
    CHEST_HUNT_ICON = Pixel(187, 296, "0xFFBB31", "chest_hunt_icon")
    CHEST_HUNT_READY = Pixel(187, 303, "0xF68F37", "chest_hunt_ready")
    BONUS_STAGE = Pixel(660, 254, "0xFFE737", "bonus_stage")
    BOSS_FIGHT = Pixel(639, 224, "0xFF878A", "boss_fight_start")

    def __init__(self):
        self.state_cache = {}
        self.last_check = 0
        self.check_interval = 0.2  # Check every 200ms

    def is_silver_box_ready(self) -> bool:
        return self.SILVER_BOX.detect()

    def is_megahorde_ready(self) -> bool:
        return self.MEGAHORDE.detect()

    def is_quest_available(self) -> bool:
        return self.QUEST_AVAILABLE.detect()

    def is_soul_bonus(self) -> bool:
        return self.SOUL_BONUS.detect(tolerance=30)

    def is_minion_ready(self) -> bool:
        return self.MINION_READY.detect(tolerance=20)

    def is_chest_hunt(self) -> bool:
        """Chest hunt available when BOTH icons are visible"""
        return self.CHEST_HUNT_ICON.detect() and self.CHEST_HUNT_READY.detect()

    def is_bonus_stage(self) -> bool:
        return self.BONUS_STAGE.detect()

    def is_boss_fight(self) -> bool:
        return self.BOSS_FIGHT.detect()


class GameInput:
    """Input system - keyboard and mouse via AppleScript"""

    def __init__(self):
        self.lock = threading.Lock()

    def key_press(self, key: str, duration: float = 0.1, repeat: int = 1):
        """Press key N times"""
        keycodes = {
            "up": 126, "down": 125, "left": 123, "right": 124,
            "space": 49, "return": 36, "tab": 48, "esc": 53,
            "q": 12, "w": 13, "e": 14, "r": 15, "a": 0, "s": 1, "d": 2, "f": 3,
            "b": 11, "n": 45, "p": 35,  # Additional keys
        }

        keycode = keycodes.get(key)
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
                logger.debug(f"Click: ({x}, {y})")
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Click failed: {e}")

    def click_multiple(self, x: int, y: int, times: int = 2, delay: float = 0.3):
        """Click same position N times"""
        for _ in range(times):
            self.click(x, y, delay=delay)


class AutoAction:
    """Base class for automatic actions"""

    def __init__(self, name: str, input_handler: GameInput, game_state: GameState):
        self.name = name
        self.input = input_handler
        self.state = game_state
        self.enabled = False
        self.last_action = 0
        self.min_cooldown = 1.0

    def can_run(self) -> bool:
        """Check cooldown"""
        return time.time() - self.last_action >= self.min_cooldown

    def run(self):
        """Execute action - override in subclass"""
        pass

    def log(self, msg: str):
        logger.info(f"[{self.name}] {msg}")


class CollectSilverBox(AutoAction):
    """Collect silver box when available"""

    def __init__(self, input_handler: GameInput, game_state: GameState):
        super().__init__("CollectSilverBox", input_handler, game_state)
        self.min_cooldown = 2.0

    def run(self):
        if not self.enabled or not self.can_run():
            return

        if self.state.is_silver_box_ready():
            self.input.click(644, 49)
            self.log("Collected silver box")
            self.last_action = time.time()


class ClaimQuests(AutoAction):
    """Claim quests when popup appears"""

    def __init__(self, input_handler: GameInput, game_state: GameState):
        super().__init__("ClaimQuests", input_handler, game_state)
        self.min_cooldown = 3.0

    def run(self):
        if not self.enabled or not self.can_run():
            return

        if self.state.is_quest_available():
            self.log("Quest available - claiming")
            self.input.click(1130, 610)  # Click quest button
            time.sleep(0.5)
            self.input.key_press("return")  # Confirm
            self.last_action = time.time()


class RageWhenSoulBonus(AutoAction):
    """Use rage when soul bonus appears"""

    def __init__(self, input_handler: GameInput, game_state: GameState):
        super().__init__("RageWhenSoulBonus", input_handler, game_state)
        self.min_cooldown = 0.5

    def run(self):
        if not self.enabled or not self.can_run():
            return

        if self.state.is_soul_bonus():
            self.input.key_press("r")  # Rage hotkey
            self.log("Soul bonus - rage!")
            self.last_action = time.time()


class RageWhenMegahorde(AutoAction):
    """Use rage when megahorde appears"""

    def __init__(self, input_handler: GameInput, game_state: GameState):
        super().__init__("RageWhenMegahorde", input_handler, game_state)
        self.min_cooldown = 1.0

    def run(self):
        if not self.enabled or not self.can_run():
            return

        if self.state.is_megahorde_ready():
            self.input.key_press("r", repeat=2)  # Press rage twice
            self.log("Megahorde - rage!")
            self.last_action = time.time()


class CollectMinion(AutoAction):
    """Collect minion rewards"""

    def __init__(self, input_handler: GameInput, game_state: GameState):
        super().__init__("CollectMinion", input_handler, game_state)
        self.min_cooldown = 3.0

    def run(self):
        if not self.enabled or not self.can_run():
            return

        if self.state.is_minion_ready():
            self.input.click(99, 113)
            self.log("Minion ready - collected")
            self.last_action = time.time()


class BasicFarming(AutoAction):
    """Basic farming - jump and attack"""

    def __init__(self, input_handler: GameInput, game_state: GameState):
        super().__init__("BasicFarming", input_handler, game_state)
        self.min_cooldown = 0.5

    def run(self):
        if not self.enabled or not self.can_run():
            return

        # Jump towards enemies
        self.input.key_press("up", duration=0.2)
        # Move right
        self.input.key_press("right", duration=0.2)
        # Click to attack
        self.input.click(640, 360, delay=0.1)

        self.last_action = time.time()


class AFKSystem:
    """Main AFK automation system"""

    def __init__(self):
        self.input = GameInput()
        self.game_state = GameState()
        self.actions: Dict[str, AutoAction] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.loop_interval = 0.1  # 100ms loop

        self._setup_actions()

    def _setup_actions(self):
        """Initialize all actions"""
        self.actions = {
            "collect_silver_box": CollectSilverBox(self.input, self.game_state),
            "claim_quests": ClaimQuests(self.input, self.game_state),
            "rage_soul_bonus": RageWhenSoulBonus(self.input, self.game_state),
            "rage_megahorde": RageWhenMegahorde(self.input, self.game_state),
            "collect_minion": CollectMinion(self.input, self.game_state),
            "basic_farming": BasicFarming(self.input, self.game_state),
        }
        logger.info(f"Initialized {len(self.actions)} actions")

    def enable_action(self, action_name: str):
        """Enable an action"""
        if action_name in self.actions:
            self.actions[action_name].enabled = True
            logger.info(f"Enabled: {action_name}")

    def disable_action(self, action_name: str):
        """Disable an action"""
        if action_name in self.actions:
            self.actions[action_name].enabled = False
            logger.info(f"Disabled: {action_name}")

    def start(self):
        """Start AFK system"""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._main_loop, daemon=True)
        self.thread.start()
        logger.info("AFK System started")

    def stop(self):
        """Stop AFK system"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("AFK System stopped")

    def _main_loop(self):
        """Main automation loop"""
        while self.running:
            try:
                # Execute all enabled actions
                for action in self.actions.values():
                    if action.enabled:
                        try:
                            action.run()
                        except Exception as e:
                            logger.error(f"Action error: {e}")

                time.sleep(self.loop_interval)
            except Exception as e:
                logger.error(f"Loop error: {e}")
                time.sleep(1)

    def get_status(self) -> dict:
        """Get system status"""
        return {
            "running": self.running,
            "enabled_actions": [k for k, v in self.actions.items() if v.enabled],
            "total_actions": len(self.actions),
        }


# Global instance
system = AFKSystem()
