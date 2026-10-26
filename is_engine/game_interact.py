#!/usr/bin/env python3
"""Game interaction module - Pixel detection, mouse/keyboard control"""

import time
from typing import Tuple, Optional
import logging
import threading

logger = logging.getLogger(__name__)

try:
    from pynput.mouse import Mouse, Button
    from pynput.keyboard import Key, Controller as KeyboardController
    from PIL import ImageGrab
    import numpy as np
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False
    logger.warning("Missing dependencies: pynput, PIL, numpy. Install with: pip install pynput pillow numpy")


class GameInteraction:
    """Handles all game interaction"""

    def __init__(self):
        self.mouse = Mouse() if HAS_DEPS else None
        self.keyboard = KeyboardController() if HAS_DEPS else None
        self.lock = threading.Lock()
        self.game_window_bounds = (0, 0, 1280, 720)  # Default bounds

    def pixel_search(self, x: int, y: int, color: Tuple[int, int, int],
                    tolerance: int = 0, area: Optional[Tuple] = None) -> bool:
        """Search for pixel with color at location. Area = (x1,y1,x2,y2)"""
        if not HAS_DEPS:
            return False

        try:
            if area:
                x1, y1, x2, y2 = area
                screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
                search_x, search_y = x - x1, y - y1
            else:
                screenshot = ImageGrab.grab()
                search_x, search_y = x, y

            if search_x < 0 or search_y < 0 or search_x >= screenshot.width or search_y >= screenshot.height:
                return False

            pixel = screenshot.getpixel((search_x, search_y))
            if len(pixel) >= 3:
                pixel = pixel[:3]

            return all(abs(pixel[i] - color[i]) <= tolerance for i in range(3))
        except Exception as e:
            logger.debug(f"Pixel search error: {e}")
            return False

    def find_color_in_region(self, x1: int, y1: int, x2: int, y2: int,
                            color: Tuple[int, int, int], tolerance: int = 10) -> Optional[Tuple[int, int]]:
        """Find first pixel of color in region, return (x, y) or None"""
        if not HAS_DEPS:
            return None

        try:
            screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            pixels = np.array(screenshot)

            r, g, b = color
            matches = np.all(np.abs(pixels[..., :3] - [r, g, b]) <= tolerance, axis=2)
            coords = np.argwhere(matches)

            if len(coords) > 0:
                y_offset, x_offset = coords[0]
                return (x1 + x_offset, y1 + y_offset)
            return None
        except Exception as e:
            logger.debug(f"Find color error: {e}")
            return None

    def mouse_click(self, x: int, y: int, button: str = "left", clicks: int = 1, delay: float = 0.1):
        """Click mouse at location"""
        if not HAS_DEPS:
            return

        with self.lock:
            try:
                btn = Button.left if button == "left" else Button.right
                self.mouse.position = (x, y)
                for _ in range(clicks):
                    self.mouse.click(btn)
                    if delay > 0:
                        time.sleep(delay)
            except Exception as e:
                logger.error(f"Mouse click error: {e}")

    def mouse_move(self, x: int, y: int, duration: float = 0):
        """Move mouse to location"""
        if not HAS_DEPS:
            return

        with self.lock:
            try:
                self.mouse.position = (x, y)
                if duration > 0:
                    time.sleep(duration)
            except Exception as e:
                logger.error(f"Mouse move error: {e}")

    def key_press(self, key_name: str):
        """Press and release a key"""
        if not HAS_DEPS:
            return

        with self.lock:
            try:
                key_map = {
                    "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right,
                    "space": Key.space, "enter": Key.enter, "esc": Key.esc,
                    "m": "m", "r": "r", "w": "w", "a": "a", "s": "s", "d": "d"
                }
                key = key_map.get(key_name.lower(), key_name)
                self.keyboard.press(key)
                time.sleep(0.05)
                self.keyboard.release(key)
            except Exception as e:
                logger.error(f"Key press error: {e}")

    def key_hold(self, key_name: str, duration: float):
        """Hold key for duration"""
        if not HAS_DEPS:
            return

        with self.lock:
            try:
                key_map = {"up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right}
                key = key_map.get(key_name.lower(), key_name)
                self.keyboard.press(key)
                time.sleep(duration)
                self.keyboard.release(key)
            except Exception as e:
                logger.error(f"Key hold error: {e}")

    def activate_game_window(self):
        """Focus the Idle Slayer window (macOS)"""
        import subprocess
        try:
            script = 'tell application "Idle Slayer" to activate'
            subprocess.run(['osascript', '-e', script], check=False, timeout=2)
        except Exception as e:
            logger.debug(f"Window activation error: {e}")

    def is_game_focused(self) -> bool:
        """Check if Idle Slayer window is focused"""
        import subprocess
        try:
            result = subprocess.run(
                ['osascript', '-e', 'tell application "System Events" to name of active application'],
                capture_output=True, text=True, timeout=2
            )
            return "Idle Slayer" in result.stdout
        except Exception:
            return False


# Global instance
interaction = GameInteraction()
