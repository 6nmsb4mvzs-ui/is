#!/usr/bin/env python3
"""
Calibration tool - Find exact pixel values from your game
Run this, move mouse to UI elements, click to capture colors
"""

import logging
import time
from typing import Tuple

try:
    from PIL import ImageGrab, Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install pillow")
    exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Calibrate')


class PixelCalibrator:
    """Interactive pixel calibration tool"""

    def __init__(self):
        self.captures = []

    def capture_at_mouse(self) -> Tuple[int, int, int]:
        """Capture RGB at current mouse position"""
        import pyautogui

        x, y = pyautogui.position()
        screenshot = ImageGrab.grab()

        if x < 0 or y < 0 or x >= screenshot.width or y >= screenshot.height:
            logger.error(f"Mouse outside screen: ({x}, {y})")
            return None

        pixel = screenshot.getpixel((x, y))[:3]
        hex_val = f"0x{pixel[0]:02X}{pixel[1]:02X}{pixel[2]:02X}"

        logger.info(f"Position: ({x}, {y})")
        logger.info(f"RGB: {pixel}")
        logger.info(f"Hex: {hex_val}")
        logger.info("")

        return (x, y, pixel, hex_val)

    def interactive_mode(self):
        """Interactive calibration mode"""
        logger.info("=== Idle Slayer Pixel Calibrator ===")
        logger.info("")
        logger.info("Instructions:")
        logger.info("1. Start Idle Slayer and position game window")
        logger.info("2. Move mouse to UI element you want to calibrate")
        logger.info("3. Press Enter to capture pixel at cursor")
        logger.info("4. Repeat for all UI elements you need")
        logger.info("5. Copy the hex values into afk_system.py")
        logger.info("")
        logger.info("Elements to calibrate:")
        logger.info("  - Quest popup button")
        logger.info("  - Megahorde icon")
        logger.info("  - Silver box indicator")
        logger.info("  - Minion ready indicator")
        logger.info("  - Chest hunt icons")
        logger.info("  - Bonus stage indicator")
        logger.info("  - Boss fight indicator")
        logger.info("")

        while True:
            try:
                input("Press Enter to capture pixel at cursor (or Ctrl+C to exit)...")
                self.capture_at_mouse()
            except KeyboardInterrupt:
                logger.info("\nCalibration complete!")
                break

    def screenshot_mode(self):
        """Save full screenshot for manual inspection"""
        logger.info("Taking screenshot...")
        screenshot = ImageGrab.grab()
        screenshot.save("idle_slayer_screenshot.png")
        logger.info("Saved: idle_slayer_screenshot.png")
        logger.info("You can open this and use a color picker tool to find exact RGB values")


def main():
    """Run calibrator"""
    import sys

    calibrator = PixelCalibrator()

    if len(sys.argv) > 1 and sys.argv[1] == "screenshot":
        calibrator.screenshot_mode()
    else:
        calibrator.interactive_mode()


if __name__ == "__main__":
    main()
