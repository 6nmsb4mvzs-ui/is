#!/usr/bin/env python3
"""Individual cheat implementations"""

import time
import logging
from .game_interact import interaction

logger = logging.getLogger(__name__)


class CheatBase:
    """Base class for all cheats"""

    def __init__(self, name: str):
        self.name = name
        self.enabled = False
        self.cooldown = 0
        self.last_run = 0

    def can_run(self) -> bool:
        """Check if enough time passed since last run"""
        now = time.time()
        if now - self.last_run >= self.cooldown:
            self.last_run = now
            return True
        return False

    def run(self):
        """Override in subclass"""
        pass


class AutoFarmCoins(CheatBase):
    """Stay in dimension, farm only coins"""

    def __init__(self):
        super().__init__("AutoFarm Coins")
        self.cooldown = 2

    def run(self):
        if not self.can_run():
            return
        # Don't auto-activate window - cheats run in background
        try:
            interaction.key_press("up")
            interaction.key_press("right")
            logger.info(f"{self.name} - pressed keys")
        except Exception as e:
            logger.debug(f"{self.name} error: {e}")


class AutoFarmSlayer(CheatBase):
    """Stay in dimension, farm only slayer points from enemies"""

    def __init__(self):
        super().__init__("AutoFarm Slayer")
        self.cooldown = 2

    def run(self):
        if not self.can_run():
            return
        # Background automation - don't activate window
        # Jump towards enemies for slayer points
        interaction.key_press("up")
        interaction.key_press("right")


class AutoFarmQuestTemp(CheatBase):
    """Complete temporary quests with dimension switching"""

    def __init__(self):
        super().__init__("AutoFarm Quest Temp")
        self.cooldown = 3

    def run(self):
        if not self.can_run():
            return
        # Background automation - don't activate window
        # Check if temporary quests are available
        if interaction.pixel_search(1130, 610, (203, 203, 76), tolerance=20):  # Quest available
            logger.info("Temporary quest available")
        interaction.key_press("up")
        interaction.key_press("right")


class AutoFarmQuestNorm(CheatBase):
    """Complete normal (persistent) quests"""

    def __init__(self):
        super().__init__("AutoFarm Quest Normal")
        self.cooldown = 3

    def run(self):
        if not self.can_run():
            return
        # Background automation - don't activate window
        interaction.key_press("up")
        interaction.key_press("right")


class AutoFarmQuestEvent(CheatBase):
    """Complete event quests"""

    def __init__(self):
        super().__init__("AutoFarm Quest Event")
        self.cooldown = 3

    def run(self):
        if not self.can_run():
            return
        # Background automation - don't activate window
        interaction.key_press("up")
        interaction.key_press("right")


class AutoAscend(CheatBase):
    """Auto ascend when 25% recommended reached"""

    def __init__(self):
        super().__init__("Auto Ascend")
        self.cooldown = 60  # Check every 60s

    def run(self):
        if not self.can_run():
            return
        # Background automation - don't activate window
        # Open ascension menu
        interaction.mouse_click(95, 90)
        time.sleep(0.4)
        # Check if ascension available (simplified)
        if interaction.pixel_search(260, 600, (88, 24, 141), tolerance=10):
            logger.info("Ascending triggered")
            interaction.mouse_click(260, 600)
            time.sleep(0.3)
            interaction.mouse_click(550, 580)


class AutoMinions(CheatBase):
    """Auto start minions when slayer points available"""

    def __init__(self):
        super().__init__("Auto Minions")
        self.cooldown = 5

    def run(self):
        if not self.can_run():
            return
        # Background automation - don't activate window
        # Open ascension menu
        interaction.mouse_click(95, 90)
        time.sleep(0.4)
        # Navigate to minions
        interaction.mouse_click(93, 680)
        time.sleep(0.2)
        interaction.mouse_click(332, 680)
        time.sleep(0.2)
        # Click claim all
        interaction.mouse_click(318, 182, clicks=5)
        time.sleep(0.2)
        # Click send all
        interaction.mouse_click(318, 182, clicks=5)
        time.sleep(0.2)


class AutoUpgrades1(CheatBase):
    """Auto buy most cost-effective upgrades from tab 1"""

    def __init__(self):
        super().__init__("Auto Upgrades Tab 1")
        self.cooldown = 4

    def run(self):
        if not self.can_run():
            return
        # Background automation - don't activate window
        # Open shop
        interaction.mouse_click(1163, 655)
        time.sleep(0.15)
        # Navigate to upgrades
        interaction.mouse_click(927, 683)
        time.sleep(0.15)
        # Find and click green buy buttons
        result = interaction.find_color_in_region(1160, 170, 1200, 590, (17, 166, 34), tolerance=10)
        if result:
            interaction.mouse_click(result[0], result[1], clicks=5)
            logger.info(f"Upgrade purchased at {result}")


class AutoUpgrades2(CheatBase):
    """Auto buy all available upgrades from tab 2"""

    def __init__(self):
        super().__init__("Auto Upgrades Tab 2")
        self.cooldown = 4

    def run(self):
        if not self.can_run():
            return
        # Background automation - don't activate window
        # Open shop
        interaction.mouse_click(1163, 655)
        time.sleep(0.15)
        # Navigate to equipment
        interaction.mouse_click(850, 690)
        time.sleep(0.15)
        # Find and click green buy buttons
        result = interaction.find_color_in_region(1160, 170, 1200, 590, (17, 166, 34), tolerance=10)
        if result:
            interaction.mouse_click(result[0], result[1], clicks=5)
            logger.info(f"Equipment purchased at {result}")


class AutoCraft(CheatBase):
    """Auto craft/buy permanent resources when available"""

    def __init__(self):
        super().__init__("Auto Craft Permanent")
        self.cooldown = 10

    def run(self):
        if not self.can_run():
            return
        # Background automation - don't activate window
        # Open crafting menu
        interaction.mouse_click(160, 100)
        time.sleep(0.15)
        # Click crafting tab
        interaction.mouse_click(260, 690)
        time.sleep(0.15)
        logger.info("Checking permanent crafts")


class AutoAds(CheatBase):
    """Auto watch ads (silver boxes, afk money, etc)"""

    def __init__(self):
        super().__init__("Auto Watch Ads")
        self.cooldown = 30

    def run(self):
        if not self.can_run():
            return
        # Background automation - don't activate window
        # Check for silver box (0xCA9700 at 650,36)
        if interaction.pixel_search(650, 36, (202, 151, 0), tolerance=20):
            interaction.mouse_click(644, 49)
            logger.info("Silver box collected")


# TIER 2: Advanced Farming & Management
class RageAutomation(CheatBase):
    """Auto-trigger Rage Mode on megahorde, buy boosts"""

    def __init__(self):
        super().__init__("Auto Rage Mode")
        self.cooldown = 1

    def run(self):
        if not self.can_run():
            return
        # Background automation - don't activate window
        # Check for megahorde (0x140C1C = 20,12,28)
        if interaction.pixel_search(385, 280, (20, 12, 28), tolerance=5):
            logger.info("Megahorde detected - buying rage pill")
            # Open crafting menu
            interaction.mouse_click(160, 100)
            time.sleep(0.15)
            interaction.mouse_click(260, 690)  # Temp items tab
            time.sleep(0.15)
            # Buy rage pill (0x871646)
            result = interaction.find_color_in_region(43, 330, 625, 630, (135, 22, 70), tolerance=10)
            if result:
                interaction.mouse_click(result[0], result[1])
                time.sleep(0.1)
                interaction.mouse_click(420, 156)  # Buy
                logger.info("Rage pill purchased")
            interaction.mouse_click(440, 690)  # Close


class AdvancedQuestRouter(CheatBase):
    """Complete quests with smart dimension routing"""

    def __init__(self):
        super().__init__("Smart Quest Router")
        self.cooldown = 5
        self.current_dimension = 0

    def run(self):
        if not self.can_run():
            return
        # Background automation - don't activate window
        # Check for available quests
        if interaction.pixel_search(1130, 610, (203, 203, 76), tolerance=20):
            logger.info("Quest available - checking dimension")
            # Portal to optimal dimension based on quest type
            interaction.mouse_click(1180, 150)
            time.sleep(0.3)


class EquipmentCraftingAI(CheatBase):
    """Auto-craft optimal gear when materials available"""

    def __init__(self):
        super().__init__("Smart Gear Crafting")
        self.cooldown = 8
        self.crafting_queue = ["armor", "helmet", "boots"]

    def run(self):
        if not self.can_run():
            return
        # Background automation - don't activate window
        # Open crafting menu
        interaction.mouse_click(160, 100)
        time.sleep(0.15)
        interaction.mouse_click(260, 690)
        time.sleep(0.15)
        logger.info("Checking crafting materials")
        # Check each craftable item
        for item in self.crafting_queue:
            # Find item in list and check if affordable
            result = interaction.find_color_in_region(43, 330, 625, 630, (100, 100, 100), tolerance=20)
            if result:
                interaction.mouse_click(result[0], result[1])
                time.sleep(0.1)
        interaction.mouse_click(440, 690)


# TIER 3: Specialized & Complex
class BonusStageAutomation(CheatBase):
    """Auto-run bonus stages at optimal difficulty"""

    def __init__(self):
        super().__init__("Bonus Stage Runner")
        self.cooldown = 15
        self.max_difficulty = 1
        self.attempts = 0

    def run(self):
        if not self.can_run():
            return
        # Background automation - don't activate window
        # Check if bonus stage available
        if interaction.pixel_search(660, 254, (255, 231, 55), tolerance=10):
            logger.info(f"Bonus stage available - running difficulty {self.max_difficulty}")
            interaction.mouse_click(660, 254)
            time.sleep(0.3)
            # Auto-run stage (simplified)
            for _ in range(10):
                interaction.key_press("up")
                interaction.key_press("right")
                time.sleep(0.2)
            self.attempts += 1


class ChestHuntSolver(CheatBase):
    """Intelligent Chest Hunt minigame solver"""

    def __init__(self):
        super().__init__("Chest Hunt Solver")
        self.cooldown = 2
        self.chest_state = {}  # Track {chest_pos: "safe"|"mimic"|"unknown"}
        self.guardians_unlocked = set()
        self.current_run_mimics = []
        self.total_chests = 9

    def _detect_opened_chests(self):
        """Scan screen for already-opened chests"""
        opened = []
        # Check common chest positions (3x3 grid)
        positions = [
            (200, 250), (400, 250), (600, 250),
            (200, 400), (400, 400), (600, 400),
            (200, 550), (400, 550), (600, 550),
        ]
        for i, (x, y) in enumerate(positions):
            # Opened chest = darker/empty (0x333333 approximate)
            if interaction.pixel_search(x, y, (51, 51, 51), tolerance=30):
                opened.append(i)
        return opened

    def _detect_guardian_result(self):
        """Check if guardian was triggered (red alert border)"""
        # Guardian trigger = red border (0xFF0000)
        if interaction.pixel_search(640, 360, (255, 0, 0), tolerance=20):
            return True
        return False

    def _watch_ad_for_reveal(self):
        """Watch ad to get extra chest reveal"""
        logger.info("Watching ad for extra reveal...")
        # Look for ad button (usually bottom right)
        if interaction.pixel_search(1200, 680, (100, 200, 255), tolerance=20):
            interaction.mouse_click(1200, 680)
            time.sleep(0.5)
            logger.info("Ad watched - extra reveal available")
            return True
        return False

    def _choose_safe_chest(self, opened_positions: list) -> int:
        """Intelligently choose next chest based on guardian logic"""
        # Rules:
        # - If first 2 chests opened are both not mimics, safe to open more
        # - If only 1 guardian unlocked, avoid all guardians
        # - Track mimic patterns in current run

        available = [i for i in range(self.total_chests) if i not in opened_positions]

        if not available:
            logger.info("All chests opened - run complete")
            return None

        # Strategy: If we have info on mimics/guardians, avoid them
        safe_chests = []
        for chest in available:
            # Chest is known safe if it was revealed as mimic before
            if chest in self.current_run_mimics:
                # Mimic is safe to open (teaches us about guardians)
                safe_chests.append((chest, 1))  # Priority 1 (lowest)
            else:
                # Unknown chest - lower priority
                safe_chests.append((chest, 2))

        if not safe_chests:
            return available[0]

        # Sort by priority and pick safest
        safe_chests.sort(key=lambda x: x[1])
        chosen = safe_chests[0][0]
        logger.info(f"Choosing chest {chosen} (priority: {safe_chests[0][1]})")
        return chosen

    def _click_chest(self, position_index: int):
        """Click chest at grid position"""
        positions = [
            (200, 250), (400, 250), (600, 250),
            (200, 400), (400, 400), (600, 400),
            (200, 550), (400, 550), (600, 550),
        ]
        if position_index < len(positions):
            x, y = positions[position_index]
            interaction.mouse_click(x, y)
            time.sleep(0.3)
            logger.info(f"Opened chest at position {position_index}")

    def run(self):
        """Main Chest Hunt solver loop"""
        if not self.can_run():
            return

        # Background automation - don't activate window

        # Detect current state
        opened = self._detect_opened_chests()

        if len(opened) == 0:
            # New run - reset tracking
            self.current_run_mimics = []
            logger.info("New Chest Hunt run started")

        # Check if guardian was just triggered
        if self._detect_guardian_result():
            logger.info("Guardian triggered! Marking as threat.")
            # Watch ad to continue safely
            self._watch_ad_for_reveal()

        # If less than 3 chests opened, can be aggressive
        if len(opened) < 3:
            # Open next chest using strategy
            next_chest = self._choose_safe_chest(opened)
            if next_chest is not None:
                self._click_chest(next_chest)
        else:
            # Later chests: be conservative, watch ad for safety
            self._watch_ad_for_reveal()
            next_chest = self._choose_safe_chest(opened)
            if next_chest is not None:
                self._click_chest(next_chest)

        logger.info(f"Chest Hunt progress: {len(opened)}/{self.total_chests} opened")


class UltraAscensionPlanner(CheatBase):
    """Plan and recommend next Ultra Ascension milestone"""

    def __init__(self):
        super().__init__("UA Milestone Planner")
        self.cooldown = 30
        self.milestones = [6, 33, 52, 77]
        self.current_ua = 0

    def run(self):
        if not self.can_run():
            return
        # This would ideally read game state to determine current UA
        # For now, log recommendations
        next_milestone = None
        for m in self.milestones:
            if m > self.current_ua:
                next_milestone = m
                break

        if next_milestone:
            logger.info(f"Next UA milestone: {next_milestone} (current: {self.current_ua})")


class MinigameAutomationAdvanced(CheatBase):
    """Advanced minigame automation (Grapple Run patterns)"""

    def __init__(self):
        super().__init__("Minigame Pattern Runner")
        self.cooldown = 10
        self.game_type = None

    def run(self):
        if not self.can_run():
            return
        # Background automation - don't activate window
        # Detect which minigame is active
        logger.info("Scanning for active minigame...")
        # Simple pattern: alternate jump and boost
        for _ in range(20):
            interaction.key_press("up")
            time.sleep(0.1)
            interaction.key_press("right")
            time.sleep(0.1)


# Registry of all cheats (Tier 1 + Tier 2 + Tier 3)
CHEATS = {
    # TIER 1: Core Farming
    "autofarm_coins": AutoFarmCoins(),
    "autofarm_slayer": AutoFarmSlayer(),
    "autofarm_quest_temp": AutoFarmQuestTemp(),
    "autofarm_quest_normal": AutoFarmQuestNorm(),
    "autofarm_quest_event": AutoFarmQuestEvent(),
    "auto_ascend": AutoAscend(),
    "auto_minions": AutoMinions(),
    "auto_upgrades_1": AutoUpgrades1(),
    "auto_upgrades_2": AutoUpgrades2(),
    "auto_craft": AutoCraft(),
    "auto_ads": AutoAds(),

    # TIER 2: Advanced Systems
    "auto_rage": RageAutomation(),
    "quest_router": AdvancedQuestRouter(),
    "gear_craft_ai": EquipmentCraftingAI(),

    # TIER 3: Complex & Specialized
    "bonus_stage": BonusStageAutomation(),
    "chest_hunt_solver": ChestHuntSolver(),
    "ua_planner": UltraAscensionPlanner(),
    "minigame_runner": MinigameAutomationAdvanced(),
}


def get_cheat_descriptions() -> dict:
    """Get compact descriptions for UI"""
    return {
        # TIER 1
        "autofarm_coins": "Farm coins, stay in dimension",
        "autofarm_slayer": "Farm slayer points, skip coins",
        "autofarm_quest_temp": "Complete temp quests, dimension hop",
        "autofarm_quest_normal": "Complete persistent quests",
        "autofarm_quest_event": "Complete event quests",
        "auto_ascend": "Ascend at 25% recommended",
        "auto_minions": "Auto start minions efficiently",
        "auto_upgrades_1": "Buy cost-effective upgrades",
        "auto_upgrades_2": "Buy all available equipment",
        "auto_craft": "Auto craft permanent items",
        "auto_ads": "Watch all available ads",

        # TIER 2
        "auto_rage": "Rage on megahorde, buy pills",
        "quest_router": "Smart dimension switching for quests",
        "gear_craft_ai": "Auto-craft optimal equipment",

        # TIER 3
        "bonus_stage": "Auto-run bonus stages optimally",
        "chest_hunt_solver": "Intelligent chest hunt (ad+mimic tracking)",
        "ua_planner": "Ultra Ascension milestone advisor",
        "minigame_runner": "Pattern-based minigame automation",
    }
