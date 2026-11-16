#!/usr/bin/env bash
# AppImage Packaging Script for Linux
# Builds a portable single-file .AppImage that runs on ANY Linux distribution without installation

set -e

echo "=== Creating Music AppImage ==="

APP_DIR="AppDir"
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/usr/bin"
mkdir -p "$APP_DIR/usr/share/applications"
mkdir -p "$APP_DIR/usr/share/icons/hicolor/512x512/apps"

# Copy binary & assets
cp -r dist/Music/* "$APP_DIR/usr/bin/"
cp packaging/linux/music.desktop "$APP_DIR/usr/share/applications/music.desktop"
cp packaging/linux/music.desktop "$APP_DIR/music.desktop"
cp assets/icon.png "$APP_DIR/usr/share/icons/hicolor/512x512/apps/music.png"
cp assets/icon.png "$APP_DIR/music.png"
cp assets/icon.png "$APP_DIR/.DirIcon"

# AppRun script
cat << 'EOF' > "$APP_DIR/AppRun"
#!/bin/sh
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/Music" "$@"
EOF
chmod +x "$APP_DIR/AppRun"

# Download appimagetool if missing
if [ ! -f "appimagetool" ]; then
    echo "Downloading appimagetool..."
    wget -q -O appimagetool https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage
    chmod +x appimagetool
fi

# Build AppImage
./appimagetool "$APP_DIR" "dist/Music-x86_64.AppImage"

echo "=== AppImage Created: dist/Music-x86_64.AppImage ==="
