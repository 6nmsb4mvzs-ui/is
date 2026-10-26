#!/usr/bin/env python3
"""Advanced Chest Hunt Minigame AI Solver

Solves Chest Hunt minigame intelligently by:
1. Tracking which chests are safe/mimic/guardian
2. Learning guardian patterns from unlocked count
3. Strategically watching ads for reveals
4. Avoiding guardians intelligently
5. Maximizing rewards per run
"""

import logging
import time
from typing import Set, Dict, List, Optional, Tuple
from enum import Enum
from .game_interact import interaction

logger = logging.getLogger(__name__)


class ChestType(Enum):
    """Chest content classification"""
    UNKNOWN = 0
    MIMIC = 1  # Safe, teaches about guardians
    GUARDIAN = 2  # Dangerous, triggers if first/second isn't mimic
    REWARD = 3  # Safe, gives loot
    EMPTY = 4  # Already opened


class ChestHuntAI:
    """Intelligent solver for Chest Hunt minigame"""

    # Grid positions (3x3 array)
    CHEST_POSITIONS = [
        (200, 250), (400, 250), (600, 250),   # Row 1
        (200, 400), (400, 400), (600, 400),   # Row 2
        (200, 550), (400, 550), (600, 550),   # Row 3
    ]

    # Color values for detection
    CHEST_CLOSED = (200, 150, 100)  # Approximate
    CHEST_OPENED = (100, 100, 100)  # Darker
    GUARDIAN_ALERT = (255, 0, 0)  # Red border
    AD_BUTTON = (100, 200, 255)  # Blue button

    def __init__(self):
        self.run_number = 0
        self.total_runs = 0
        self.total_rewards = 0
        self.state: Dict[int, ChestType] = {i: ChestType.UNKNOWN for i in range(9)}
        self.guardians_unlocked = 0
        self.current_run_opened = set()  # Indices of opened chests this run
        self.current_run_mimics = []  # Indices that revealed mimics
        self.current_run_guardians = []  # Indices that revealed guardians
        self.ad_watched_this_run = 0
        self.max_ads_per_run = 3

    def detect_opened_chests(self) -> Set[int]:
        """Scan screen for already-opened chests"""
        opened = set()
        for i, (x, y) in enumerate(self.CHEST_POSITIONS):
            # Opened chest appears darker (0x333333 ~ 51,51,51)
            if interaction.pixel_search(x, y, self.CHEST_OPENED, tolerance=40):
                opened.add(i)
                self.state[i] = ChestType.EMPTY
        return opened

    def detect_guardian_triggered(self) -> bool:
        """Check if guardian was just triggered (red alert)"""
        # Guardian triggered = red border flashes (0xFF0000)
        return interaction.pixel_search(640, 360, self.GUARDIAN_ALERT, tolerance=30)

    def should_watch_ad(self, chests_opened: int) -> bool:
        """Determine if watching ad would be beneficial"""
        # Strategy:
        # - If 3+ chests opened and haven't watched ad, watch for safety
        # - If new run just started, don't watch immediately
        # - If nearly all chests opened, definitely watch

        if self.ad_watched_this_run >= self.max_ads_per_run:
            return False

        if chests_opened >= 5 and self.ad_watched_this_run == 0:
            logger.info("Safe checkpoint reached - watching ad for extra reveal")
            return True

        if chests_opened >= 7:
            return True

        return False

    def watch_ad(self) -> bool:
        """Attempt to watch ad for extra chest reveal"""
        logger.info("Looking for ad button...")
        # Check common ad button positions
        ad_positions = [(1200, 680), (1000, 680), (600, 680)]

        for x, y in ad_positions:
            if interaction.pixel_search(x, y, self.AD_BUTTON, tolerance=40):
                logger.info(f"Ad button found at ({x}, {y}) - watching ad")
                interaction.mouse_click(x, y)
                time.sleep(2)  # Let ad play
                self.ad_watched_this_run += 1
                logger.info(f"Ad watched ({self.ad_watched_this_run}/{self.max_ads_per_run})")
                return True

        logger.debug("Ad button not found")
        return False

    def learn_from_result(self, chest_index: int, is_mimic: bool):
        """Update knowledge from opened chest result"""
        if is_mimic:
            self.current_run_mimics.append(chest_index)
            self.state[chest_index] = ChestType.MIMIC
            logger.info(f"Chest {chest_index} is MIMIC - safe to open")
        else:
            self.current_run_guardians.append(chest_index)
            self.state[chest_index] = ChestType.GUARDIAN
            logger.info(f"Chest {chest_index} is GUARDIAN - dangerous")

    def choose_next_chest(self, opened_indices: Set[int]) -> Optional[int]:
        """Intelligently choose next chest to open

        Guardian Rules:
        - If 0-2 chests opened: can be aggressive (testing)
        - If FIRST chest opened was mimic: other chests likely safe
        - If FIRST chest opened was guardian: must be careful
        - If 2+ mimics found: safe zone identified
        """

        available = [i for i in range(9) if i not in opened_indices]

        if not available:
            logger.info("All chests opened - run complete!")
            return None

        # Scoring system: higher = more likely to be safe
        scores: List[Tuple[int, int]] = []

        for chest_idx in available:
            score = 50  # Neutral baseline

            # If we know it's a mimic, high score (safe, educational)
            if self.state[chest_idx] == ChestType.MIMIC:
                score = 90
            # If we know it's guardian, very low score
            elif self.state[chest_idx] == ChestType.GUARDIAN:
                score = 5
            else:
                # Unknown: use heuristics
                chests_opened = len(opened_indices)

                # Early game (0-2 opened): test aggressively
                if chests_opened < 2:
                    score = 75
                # Mid game (3-5 opened): be careful
                elif chests_opened < 5:
                    score = 50
                    # If we found mimics, favor other areas
                    if len(self.current_run_mimics) > 0:
                        score = 65
                # Late game (6+ opened): very conservative
                else:
                    score = 30
                    # If we found safe zone, explore adjacent
                    if len(self.current_run_mimics) >= 2:
                        score = 40

            scores.append((chest_idx, score))

        # Pick highest-scoring chest
        if scores:
            scores.sort(key=lambda x: x[1], reverse=True)
            chosen = scores[0][0]
            logger.info(f"Choosing chest {chosen} (score: {scores[0][1]})")
            return chosen

        return available[0] if available else None

    def click_chest(self, position_index: int) -> bool:
        """Click chest at grid position"""
        if position_index < 0 or position_index >= len(self.CHEST_POSITIONS):
            logger.error(f"Invalid chest index: {position_index}")
            return False

        x, y = self.CHEST_POSITIONS[position_index]
        logger.info(f"Clicking chest {position_index} at ({x}, {y})")
        interaction.mouse_click(x, y)
        time.sleep(0.4)
        return True

    def detect_result(self) -> bool:
        """Detect if chest contained mimic or guardian"""
        time.sleep(0.5)  # Wait for animation

        # If red alert is showing, it was guardian
        if interaction.pixel_search(640, 360, self.GUARDIAN_ALERT, tolerance=30):
            logger.info("Result: GUARDIAN - triggered!")
            return False  # Guardian
        else:
            logger.info("Result: MIMIC or REWARD - safe!")
            return True  # Mimic/reward (safe)

    def run_solver(self):
        """Main solver loop for one Chest Hunt session"""
        logger.info("=" * 50)
        logger.info("CHEST HUNT SOLVER STARTED")
        logger.info("=" * 50)

        interaction.activate_game_window()
        self.run_number += 1
        self.total_runs += 1
        self.ad_watched_this_run = 0
        self.current_run_opened.clear()
        self.current_run_mimics.clear()
        self.current_run_guardians.clear()

        for attempt in range(15):  # Max 15 chests per run
            logger.info(f"\n--- Attempt {attempt + 1} ---")

            # Detect current state
            opened = self.detect_opened_chests()
            self.current_run_opened = opened

            if len(opened) == 9:
                logger.info("RUN COMPLETE - All chests opened!")
                self.total_rewards += self._estimate_rewards(len(self.current_run_mimics))
                break

            # Check if should watch ad
            if self.should_watch_ad(len(opened)):
                self.watch_ad()

            # Choose next chest
            next_chest = self.choose_next_chest(opened)
            if next_chest is None:
                break

            # Click it
            self.click_chest(next_chest)

            # Detect result
            is_safe = self.detect_result()
            self.learn_from_result(next_chest, is_safe)

            # If guardian triggered, watch ad and continue carefully
            if not is_safe and self.ad_watched_this_run < self.max_ads_per_run:
                logger.info("Guardian triggered - watching protective ad")
                self.watch_ad()

            time.sleep(0.3)

        logger.info(f"\nRUN SUMMARY:")
        logger.info(f"  Chests opened: {len(self.current_run_opened)}/9")
        logger.info(f"  Mimics found: {len(self.current_run_mimics)}")
        logger.info(f"  Guardians hit: {len(self.current_run_guardians)}")
        logger.info(f"  Ads watched: {self.ad_watched_this_run}")
        logger.info(f"  Total runs completed: {self.total_runs}")
        logger.info("=" * 50)

    def _estimate_rewards(self, safe_count: int) -> int:
        """Estimate rewards from number of safe chests opened"""
        # Rough estimate: 100 coins per safe chest
        return safe_count * 100

    def get_statistics(self) -> dict:
        """Get overall statistics"""
        return {
            "total_runs": self.total_runs,
            "total_rewards": self.total_rewards,
            "avg_chests_per_run": self.total_rewards / max(self.total_runs, 1) / 100,
            "current_run_mimics": len(self.current_run_mimics),
            "current_run_guardians": len(self.current_run_guardians),
            "ads_watched_total": self.ad_watched_this_run,
        }


# Global instance
chest_hunt_solver = ChestHuntAI()
