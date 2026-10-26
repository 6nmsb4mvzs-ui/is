#!/usr/bin/env python3
"""Game interaction module - macOS native via AppleScript + pixel detection"""

import time
import subprocess
from typing import Tuple, Optional
import logging
import threading

logger = logging.getLogger(__name__)

try:
    from PIL import ImageGrab
    import numpy as np
    HAS_IMAGE = True
except ImportError:
    HAS_IMAGE = False
    logger.warning("Missing dependencies: PIL, numpy. Install with: pip install pillow numpy")


class GameInteraction:
    """Handles game interaction via AppleScript (native macOS, no pynput needed)"""

    def __init__(self):
        self.lock = threading.Lock()
        self.game_window_bounds = (0, 0, 1280, 720)

    def key_press(self, key: str, duration: float = 0.1):
        """Press a key using AppleScript"""
        try:
            # KeyCode mappings for common keys
            keycodes = {
                "up": 126,
                "down": 125,
                "left": 123,
                "right": 124,
                "space": 49,
                "return": 36,
                "tab": 48,
                "esc": 53,
                "q": 12,
                "w": 13,
                "e": 14,
                "r": 15,
                "a": 0,
                "s": 1,
                "d": 2,
                "f": 3,
            }

            keycode = keycodes.get(key, None)
            if keycode is None:
                logger.debug(f"Unknown key: {key}")
                return

            with self.lock:
                script = f'tell application "System Events" to key code {keycode}'
                result = subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                if result.returncode == 0:
                    logger.debug(f"Key press: {key} (code {keycode})")
                    time.sleep(duration)
                else:
                    logger.debug(f"Key press failed: {key}")
        except Exception as e:
            logger.debug(f"Key press error: {e}")

    def mouse_click(self, x: int, y: int, button: str = "left", clicks: int = 1, delay: float = 0.1):
        """Click mouse at location"""
        try:
            with self.lock:
                for _ in range(clicks):
                    script = f'tell application "System Events" to click at {{{x}, {y}}}'
                    result = subprocess.run(
                        ['osascript', '-e', script],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )

                    if result.returncode == 0:
                        logger.debug(f"Click at ({x}, {y})")
                        time.sleep(delay)
        except Exception as e:
            logger.debug(f"Mouse click error: {e}")

    def mouse_move(self, x: int, y: int, duration: float = 0):
        """Move mouse to location"""
        try:
            script = f'tell application "System Events" to mouse move {{{x}, {y}}}'
            subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                timeout=2
            )
            if duration > 0:
                time.sleep(duration)
        except Exception as e:
            logger.debug(f"Mouse move error: {e}")

    def pixel_search(self, x: int, y: int, color: Tuple[int, int, int],
                    tolerance: int = 0, area: Optional[Tuple] = None) -> bool:
        """Search for pixel with color at location"""
        if not HAS_IMAGE:
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
        """Find first pixel of color in region"""
        if not HAS_IMAGE:
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

    def activate_game_window(self):
        """Focus the Idle Slayer window"""
        try:
            script = 'tell application "Idle Slayer" to activate'
            subprocess.run(['osascript', '-e', script], check=False, timeout=2)
        except Exception as e:
            logger.debug(f"Window activation error: {e}")

    def is_game_focused(self) -> bool:
        """Check if Idle Slayer is focused"""
        try:
            result = subprocess.run(
                ['osascript', '-e', 'tell application "System Events" to name of active application'],
                capture_output=True, text=True, timeout=2
            )
            return "Idle Slayer" in result.stdout
        except:
            return False


# Global instance
interaction = GameInteraction()
