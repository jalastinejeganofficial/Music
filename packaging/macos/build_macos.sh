#!/usr/bin/env bash
# macOS Build Script
# Builds native Music.app bundle and drag-and-drop .dmg for macOS (Apple Silicon M1/M2/M3/M4 & Intel)

set -e

echo "=== Building Music for macOS ==="

# 1. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller pywebview pyobjc-framework-WebKit

# 2. Convert PNG to ICNS if needed
if [ ! -f "assets/icon.icns" ] && command -v sips &> /dev/null; then
    echo "Generating icon.icns from assets/icon.png..."
    mkdir -p icon.iconset
    sips -z 16 16     assets/icon.png --out icon.iconset/icon_16x16.png
    sips -z 32 32     assets/icon.png --out icon.iconset/icon_16x16@2x.png
    sips -z 32 32     assets/icon.png --out icon.iconset/icon_32x32.png
    sips -z 64 64     assets/icon.png --out icon.iconset/icon_32x32@2x.png
    sips -z 128 128   assets/icon.png --out icon.iconset/icon_128x128.png
    sips -z 256 256   assets/icon.png --out icon.iconset/icon_128x128@2x.png
    sips -z 256 256   assets/icon.png --out icon.iconset/icon_256x256.png
    sips -z 512 512   assets/icon.png --out icon.iconset/icon_256x256@2x.png
    sips -z 512 512   assets/icon.png --out icon.iconset/icon_512x512.png
    iconutil -c icns icon.iconset -o assets/icon.icns
    rm -rf icon.iconset
fi

# 3. Build standalone .app bundle
pyinstaller --noconfirm --clean \
    --windowed \
    --name="Music" \
    --icon="assets/icon.png" \
    --add-data="static:static" \
    --add-data="assets:assets" \
    --hidden-import="uvicorn" \
    --hidden-import="uvicorn.logging" \
    --hidden-import="uvicorn.loops" \
    --hidden-import="uvicorn.protocols" \
    --hidden-import="fastapi" \
    --hidden-import="yt_dlp" \
    --hidden-import="webview" \
    desktop_app.py

echo "=== Music.app bundle created in dist/Music.app ==="

# 4. Create DMG installer if create-dmg or hdiutil is present
if command -v hdiutil &> /dev/null; then
    echo "Creating Music.dmg installer..."
    hdiutil create -volname "Music" -srcfolder "dist/Music.app" -ov -format UDZO "dist/Music-macOS.dmg"
    echo "=== DMG Created: dist/Music-macOS.dmg ==="
fi
