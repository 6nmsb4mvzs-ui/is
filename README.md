# Idle Slayer Cheat Engine v2.0

**Native macOS SwiftUI app** for Idle Slayer automation. Zero web UI bullshit, pure native window.

![macOS 13+](https://img.shields.io/badge/macOS-13%2B-blue) ![Swift 5.7](https://img.shields.io/badge/Swift-5.7-orange) ![License MIT](https://img.shields.io/badge/License-MIT-green)

## Installation

### Method 1: Pre-built (Easiest)
1. Download the latest release from GitHub
2. Unzip → **Double-click `run.command`**
3. Done! App launches in ~/Applications/

### Method 2: Build from Source
```bash
git clone https://github.com/YOUR-USERNAME/is_engine_swift.git
cd is_engine_swift
./run.command
```

The script handles everything:
- ✅ Xcode Command Line Tools (auto-installs if needed)
- ✅ Swift build in release mode
- ✅ Python dependencies (PyAutoGUI, PIL, NumPy)
- ✅ Creates ~/.idle_slayer_cheat/ config
- ✅ Installs to ~/Applications/Idle Slayer Cheat.app
- ✅ Launches automatically

## Features

**18 Cheats** across 3 tiers:

### Tier 1 (Core Automation)
- AutoFarm Coins - Farm coins only
- AutoFarm Slayer - Farm slayer points
- Auto Temp Quests - Complete temp quests
- Auto Normal Quests - Complete normal quests
- Auto Event Quests - Complete event quests
- Auto Ascend - Ascend at 25%
- Auto Minions - Start minions
- Auto Ads - Watch ads

### Tier 2 (Smart Upgrades)
- Budget Upgrades - Cost-effective buys
- All Upgrades - Buy everything
- Auto Craft - Craft items automatically

### Tier 3 (Advanced Strategies)
- Rage Automation - Megahorde trigger
- Quest Router - Smart quest routing
- Gear Craft AI - AI equipment crafting
- Bonus Stages - Auto-run bonus stages
- Chest Hunt AI - Minigame solver with smart ad watching
- UA Planner - Ultra Ascension planning
- Minigame Runner - Pattern detection runner

## Usage

1. **Toggle Cheats** - Click any cheat to enable/disable (green = ON)
2. **Search** - Use the search bar to find specific cheats
3. **Start/Stop** - Use START button to run selected cheats, STOP to halt
4. **Status** - See live status (Running/Stopped) and active cheat count

## Architecture

- **SwiftUI Frontend** - Native macOS app with real window (not a browser)
- **Python Backend** - Existing pixel-based automation (PyAutoGUI, PIL, NumPy)
- **State Persistence** - Saves cheat selections to `~/.idle_slayer_cheat/cheats.json`

## Requirements

- macOS 13+
- Xcode Command Line Tools (auto-installed if missing)
- Python 3
- Idle Slayer (Steam/macOS version)

## Personal Use Only

This tool is for personal testing and educational purposes only. Do not distribute or share with the Idle Slayer community.

---

Built with Swift 5.7 + SwiftUI. Python automation via PyAutoGUI.
