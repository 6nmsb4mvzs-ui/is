# Pixel Calibration Guide

The new AFK system uses **exact pixel detection** - it looks for specific RGB colors at specific screen coordinates to know what's happening in the game.

The coordinates and colors are estimates from analyzing the AutoIt script. **Your game may have different positions or colors** depending on resolution, UI scale, or updates.

## How to Calibrate

### Step 1: Find Exact Pixel Values

```bash
python3 -m is_engine.calibrate
```

This opens interactive mode. Instructions:
1. Start Idle Slayer, position the game window
2. Move your mouse to a UI element (e.g., the quest button)
3. Press Enter to capture the pixel color at cursor
4. It shows: Position (x, y) and Hex value like `0xCBCB4C`
5. Repeat for each UI element

### Step 2: Update afk_system.py

Open `is_engine/afk_system.py` and update the `GameState` class:

```python
class GameState:
    # Update these with YOUR captured values
    QUEST_AVAILABLE = Pixel(1130, 610, "0xCBCB4C", "quest_popup")
    MEGAHORDE = Pixel(385, 280, "0x140C1C", "megahorde_ready")
    # ... etc
```

### UI Elements to Calibrate

Find these in your game and capture their colors:

| Element | Current Value | Your Value |
|---------|---|---|
| Quest popup button | (1130, 610) = 0xCBCB4C | ? |
| Megahorde indicator | (385, 280) = 0x140C1C | ? |
| Silver box ready | (650, 36) = 0xCA9700 | ? |
| Minion ready | (99, 113) = 0xFFFF7A | ? |
| Chest hunt icon | (187, 296) = 0xFFBB31 | ? |
| Chest hunt ready | (187, 303) = 0xF68F37 | ? |
| Bonus stage | (660, 254) = 0xFFE737 | ? |
| Soul bonus | (625, 143) = 0xA86D0A | ? |
| Boss fight | (639, 224) = 0xFF878A | ? |

## Testing

Once you've updated the pixels, test with debug logging:

```bash
# In launcher.py, change:
system = AFKSystem(debug=True)
```

Run it and watch the logs - you should see which pixels are being detected.

## Why This Matters

- **Wrong coordinates**: System never detects game state
- **Wrong colors**: Tolerance mismatch means detection fails
- **Resolution**: UI may be at different coordinates on your screen

The calibration ensures the system "sees" what's actually on YOUR screen.
