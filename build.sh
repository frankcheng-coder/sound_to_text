#!/bin/bash
#
# Build Sound to Text as a macOS .app bundle.
#
# This creates a native .app that wraps the Python project.
# The app uses the project's virtual environment and source code in-place.
#
# Usage:
#   ./build.sh
#
# Prerequisites:
#   - Python 3.12 virtual environment at .venv/
#   - All dependencies installed (pip install -r requirements.txt)
#
# Output:
#   dist/Sound to Text.app
#
set -euo pipefail
cd "$(dirname "$0")"

PROJECT_DIR="$(pwd)"
VENV="$PROJECT_DIR/.venv"
PYTHON="$VENV/bin/python"
APP_NAME="Sound to Text"
APP_PATH="dist/${APP_NAME}.app"
CONTENTS="$APP_PATH/Contents"
MACOS="$CONTENTS/MacOS"
RESOURCES="$CONTENTS/Resources"

# Verify venv exists
if [ ! -f "$PYTHON" ]; then
    echo "ERROR: Virtual environment not found at .venv/"
    echo "Create one first:  python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Clean previous build
echo "Cleaning previous build..."
rm -rf "$APP_PATH"
mkdir -p "$MACOS" "$RESOURCES"

# --- Info.plist ---
echo "Writing Info.plist..."
cat > "$CONTENTS/Info.plist" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Sound to Text</string>
    <key>CFBundleDisplayName</key>
    <string>Sound to Text</string>
    <key>CFBundleIdentifier</key>
    <string>com.soundtotext.app</string>
    <key>CFBundleVersion</key>
    <string>1.0.0</string>
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    <key>CFBundleExecutable</key>
    <string>SoundToText</string>
    <key>CFBundleIconFile</key>
    <string>SoundToText</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleSignature</key>
    <string>????</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSMinimumSystemVersion</key>
    <string>12.0</string>
    <key>LSEnvironment</key>
    <dict>
        <key>LANG</key>
        <string>en_US.UTF-8</string>
    </dict>
</dict>
</plist>
PLIST

# --- Icon ---
if [ -f "assets/SoundToText.icns" ]; then
    echo "Copying app icon..."
    cp "assets/SoundToText.icns" "$RESOURCES/SoundToText.icns"
else
    echo "WARNING: No icon found at assets/SoundToText.icns — app will use default icon."
fi

# --- Launcher script ---
echo "Writing launcher..."
cat > "$MACOS/SoundToText" << LAUNCHER
#!/bin/bash
# Sound to Text launcher — resolves the project directory and runs main.py
PROJECT_DIR="$PROJECT_DIR"
cd "\$PROJECT_DIR"
exec "\$PROJECT_DIR/.venv/bin/python" "\$PROJECT_DIR/main.py" "\$@"
LAUNCHER
chmod +x "$MACOS/SoundToText"

# --- Verify ---
if [ -d "$APP_PATH" ]; then
    echo ""
    echo "Build successful!"
    echo "  App:  $APP_PATH"
    echo "  Size: $(du -sh "$APP_PATH" | cut -f1)"
    echo ""
    echo "To run:    open \"$APP_PATH\""
    echo "To install: cp -R \"$APP_PATH\" /Applications/"
else
    echo "ERROR: Build failed."
    exit 1
fi
