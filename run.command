#!/bin/bash
# Double-click this file to build and install Idle Slayer Cheat.app
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
APP_NAME="Idle Slayer Cheat"
APP_DIR="$HOME/Applications/${APP_NAME}.app"

echo "⚔️  IDLE SLAYER CHEAT ENGINE"
echo "============================"
echo ""

# Xcode CLI tools
if ! xcode-select -p &>/dev/null; then
    echo "📦 Installing Xcode Command Line Tools (one-time)..."
    xcode-select --install
    echo "Please re-run this script after installation completes."
    read -n1 -rsp "Press any key to close..."
    exit 0
fi

echo "✅ Xcode tools found"

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 not found"
    exit 1
fi

echo "✅ Python 3 found"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
for pkg in pyautogui pynput pillow numpy; do
    python3 -m pip install "$pkg" --user --quiet 2>/dev/null || \
    python3 -m pip install "$pkg" --break-system-packages --quiet 2>/dev/null || true
done
echo "✅ Python packages ready"

# Copy engine files
if [ -d "$SCRIPT_DIR/is_engine" ]; then
    echo "📂 Setting up engine..."
    mkdir -p "$HOME/.idle_slayer_cheat"
    cp -r "$SCRIPT_DIR/is_engine" "$HOME/.idle_slayer_cheat/"
    echo "✅ Engine files copied"
fi

# Build Swift app
echo "🔨 Building app..."
cd "$SCRIPT_DIR"

if ! swift build -c release --quiet 2>&1; then
    echo ""
    echo "Build failed. Retrying with verbose output..."
    swift build -c release
    read -n1 -rsp "Press any key to close..."
    exit 1
fi

echo "✅ App built"

# Create app bundle
echo "📦 Creating app bundle..."
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

# Copy executable
cp .build/release/IdleSlayerCheat "$APP_DIR/Contents/MacOS/IdleSlayerCheat"
chmod +x "$APP_DIR/Contents/MacOS/IdleSlayerCheat"

# Create Info.plist
cat > "$APP_DIR/Contents/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Idle Slayer Cheat</string>
    <key>CFBundleDisplayName</key>
    <string>Idle Slayer Cheat</string>
    <key>CFBundleIdentifier</key>
    <string>com.idle.slayer.cheat</string>
    <key>CFBundleVersion</key>
    <string>2.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0.0</string>
    <key>CFBundleExecutable</key>
    <string>IdleSlayerCheat</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>13.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
PLIST

# Update Spotlight and icon cache
/usr/bin/mdimport "$APP_DIR" 2>/dev/null || true
/usr/bin/touch "$APP_DIR"

echo "✅ App created: $APP_DIR"
echo ""
echo "🎮 Ready to use!"
echo "   Open: ~/Applications/Idle Slayer Cheat.app"
echo ""
echo "💡 How to use:"
echo "   1. Launch the app from Applications"
echo "   2. Toggle cheats ON/OFF"
echo "   3. Click START to run"
echo "   4. Cheats run in background"
echo ""

# Launch app
open "$APP_DIR"

# Close this terminal window
osascript -e 'tell application "Terminal" to close front window' 2>/dev/null &
exit 0
