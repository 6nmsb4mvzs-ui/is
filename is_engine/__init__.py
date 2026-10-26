#!/usr/bin/env python3
"""Idle Slayer Cheat Engine for macOS"""

__version__ = "1.0.0"
__author__ = "0x5A"

from .core import engine, CheatMode
from .game_interact import interaction
from .cheats import CHEATS

__all__ = ["engine", "interaction", "CHEATS", "CheatMode"]
