#!/usr/bin/env bash
# Build Script for Linux (Ubuntu, Debian, Fedora, Arch)
# Generates standalone native Linux binary using PyInstaller

set -e

echo "=== Building Music for Linux ==="

# 1. Install system webview dependencies (WebKitGTK)
if command -v apt-get &> /dev/null; then
    echo "Detected Debian/Ubuntu. Ensuring webkit2gtk is installed..."
    sudo apt-get update -y && sudo apt-get install -y libwebkit2gtk-4.0-37 libwebkit2gtk-4.1-0 python3-gi python3-gi-cairo gir1.2-webkit2-4.0 || true
elif command -v dnf &> /dev/null; then
    echo "Detected Fedora/RHEL. Ensuring webkit2gtk is installed..."
    sudo dnf install -y webkit2gtk4.1 || true
elif command -v pacman &> /dev/null; then
    echo "Detected Arch Linux. Ensuring webkit2gtk is installed..."
    sudo pacman -Sy --noconfirm webkit2gtk-4.1 || true
fi

# 2. Install python build dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller pywebview

# 3. Build standalone Linux binary
echo "Running PyInstaller for Linux..."
pyinstaller --noconfirm --clean Music.spec

echo "=== Build Complete! ==="
echo "Binary location: dist/Music/Music"
echo "To run: ./dist/Music/Music"
