# Changelog

## v2.4.0 - AppleScript Automation
- **FIXED:** Replaced unreliable pynput with native macOS AppleScript
- **NEW:** Built-in auto-updater that checks GitHub releases
- **NEW:** Updates tab in app for one-click installation
- **NEW:** Proper state persistence between sessions
- **FIX:** Toggle cheats work reliably now
- **FIX:** Tab switching no longer steals focus
- **FIX:** Removed pynput dependency - no accessibility permission issues
- **NEW:** Global ⌘+M hotkey support for showing/hiding menu

## How It Works Now

### Installation
1. Download the latest app from GitHub releases
2. Double-click to run the installer
3. App installs to ~/Applications/Idle_Slayer_Cheat.app

### Auto-Updates
1. App checks GitHub on startup
2. If update available, shows in Updates tab
3. Click "INSTALL" to download and install
4. App automatically relaunches with new version

### Development Workflow
1. Make changes
2. Test locally: `swift build && swift run`
3. Commit and push to main: `git add . && git commit && git push origin main`
4. Create release: `git tag -a vX.Y.Z && git push origin vX.Y.Z`
5. GitHub Actions automatically builds and uploads to releases
6. Users see update immediately in their running app

### Using the Cheats
1. Toggle cheats ON (green)
2. Press START
3. Cheats run in background using AppleScript automation
4. Idle Slayer stays in foreground
5. Press ⌘+M to show/hide menu from anywhere

## Architecture

```
Swift UI (macOS native window)
    ↓
CheatManager (state, toggle, sync)
    ↓
UpdateManager (check GitHub, download, install, relaunch)
    ↓
Python Engine (cheats loop)
    ↓
AppleScript (keyboard/mouse automation)
```

## Future Changes

Whenever you make changes:
```bash
# Make changes
cd is

# Commit
git add .
git commit -m "Your message"
git push origin main

# When ready to release
git tag -a vX.Y.Z -m "Release notes"
git push origin vX.Y.Z
```

GitHub Actions will automatically build and upload the release.
Users will see the update the next time they run the app.
