#!/usr/bin/env python3
"""macOS native interaction using AppleScript - more reliable than pynput"""

import subprocess
import time
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class MacOSInteraction:
    """Handles macOS automation via AppleScript"""

    def __init__(self):
        pass

    def key_press(self, key: str, duration: float = 0.1):
        """Press a key using AppleScript"""
        try:
            # Map key names to AppleScript equivalents
            key_map = {
                "up": "up arrow",
                "down": "down arrow",
                "left": "left arrow",
                "right": "right arrow",
                "space": "space",
                "return": "return",
                "tab": "tab",
                "esc": "escape",
                "q": "q",
                "w": "w",
                "e": "e",
                "r": "r",
                "a": "a",
                "s": "s",
                "d": "d",
                "f": "f",
            }

            mapped_key = key_map.get(key, key)
            script = f'tell application "System Events" to key code (key code "{mapped_key}")'

            # Try different approach - use direct key codes
            if key == "up":
                script = 'tell application "System Events" to key code 126'
            elif key == "down":
                script = 'tell application "System Events" to key code 125'
            elif key == "left":
                script = 'tell application "System Events" to key code 123'
            elif key == "right":
                script = 'tell application "System Events" to key code 124'
            elif key == "space":
                script = 'tell application "System Events" to key code 49'
            elif key == "return":
                script = 'tell application "System Events" to key code 36'

            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                logger.debug(f"Key press: {key}")
                time.sleep(duration)
            else:
                logger.debug(f"Key press failed: {key} - {result.stderr}")
        except Exception as e:
            logger.debug(f"Key press error: {e}")

    def mouse_click(self, x: int, y: int, button: str = "left", clicks: int = 1, delay: float = 0.1):
        """Click mouse using AppleScript"""
        try:
            button_name = "left button" if button == "left" else "right button"

            for _ in range(clicks):
                script = f'tell application "System Events" to click at {{{x}, {y}}} using {button_name}'
                result = subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                if result.returncode == 0:
                    logger.debug(f"Mouse click at ({x}, {y})")
                    time.sleep(delay)
                else:
                    logger.debug(f"Mouse click failed: {result.stderr}")
        except Exception as e:
            logger.debug(f"Mouse click error: {e}")

    def mouse_move(self, x: int, y: int, duration: float = 0):
        """Move mouse using AppleScript"""
        try:
            script = f'tell application "System Events" to mouse move {{{x}, {y}}}'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                time.sleep(duration)
        except Exception as e:
            logger.debug(f"Mouse move error: {e}")

    def is_game_focused(self) -> bool:
        """Check if Idle Slayer is in focus"""
        try:
            result = subprocess.run(
                ['osascript', '-e', 'tell application "System Events" to name of active application'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return "Idle Slayer" in result.stdout
        except:
            return False


# Global instance
interaction = MacOSInteraction()
