# Idle Slayer Cheat - Setup Guide

## Quick Setup

### Option 1: Automatic Setup (Recommended)

1. Clone or download this repo
2. Run the setup script:
   ```bash
   cd /path/to/is_repo
   chmod +x setup.sh
   ./setup.sh
   ```
3. Build and run the app
4. Toggle your cheats and click START

### Option 2: Manual Setup

1. Copy `is_engine` folder to `~/.idle_slayer_cheat/`:
   ```bash
   cp -r is_engine ~/.idle_slayer_cheat/
   ```

2. Install Python dependencies:
   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. Build and run the app

## What Happens on Start

1. App loads cheats from `~/.idle_slayer_cheat/cheats.json`
2. When you click START, the Python launcher reads your enabled cheats
3. Launcher maps cheats to mods (e.g., `autofarm_coins` → `auto_farm`)
4. Mods automation starts running the enabled mods

## Available Mods

- **AutoFarm** - Continuous farming (up, right, space loop)
- **AutoBoost** - Boost ability (B key every 15s)
- **AutoRage** - Rage ability (R key every 12s)
- **AutoClimbTower** - Tower climbing (up, right, jump)
- **BonusStageAutoComplete** - Auto-complete bonus stages
- **QuestAutoComplete** - Click and claim quests
- **MinionCollector** - Collect minion rewards every 30s

## Troubleshooting

### "Active mod counter drops to 0/18 after clicking START"

This is fixed in the latest version. The counter now shows enabled cheats from the UI, not from the Python engine.

### "Mods aren't working in-game"

1. Check that `is_engine` folder exists:
   ```bash
   ls -la ~/.idle_slayer_cheat/is_engine/
   ```

2. Check app logs for errors - click START and watch for error messages

3. Verify Idle Slayer window is focused when mods run

4. Some mods require specific in-game conditions (e.g., QuestAutoComplete needs a quest available)

### "Permission denied" on setup.sh

Run:
```bash
chmod +x setup.sh
```

### Python module not found

Make sure the working directory is correct:
```bash
ls ~/.idle_slayer_cheat/
# Should show: cheats.json, is_engine/
```

## How Cheats Map to Mods

Only these 7 cheats are currently implemented:

| UI Cheat | Mod Name | What It Does |
|----------|----------|--------------|
| AutoFarm Coins / Slayer | auto_farm | Jump → Move → Attack loop |
| Auto Ascend | auto_boost | Press B for boost |
| Auto Minions | minion_collect | Click minion icon every 30s |
| Rage Automation | auto_rage | Press R for rage |
| Quest Router | quest_complete | Click quest button and press return |
| Bonus Stages | bonus_complete | Press spacebar in bonus stages |

The other 11 cheats don't have mods yet - enabling them won't do anything.

## Files

- `Sources/` - Swift UI app
- `is_engine/` - Python automation backend
  - `launcher.py` - Entry point, loads config
  - `mods_automation.py` - All 7 mods and main loop
- `setup.sh` - Installation script
- `requirements.txt` - Python dependencies

## Running from Command Line

For debugging:
```bash
cd ~/.idle_slayer_cheat
python3 -m is_engine.launcher
```

Watch the output to see which mods are loading and if there are errors.
