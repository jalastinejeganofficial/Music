# 🪟 Music Player for Windows

Native desktop software for Windows 10 & Windows 11 (64-bit).

---

### 🚀 How to Run the App (No Installation Needed)

1. Open folder: **`dist\Music\`**
2. Double-click **`Music.exe`**.
3. The app launches immediately in its own native desktop window with:
   - Full dark theme
   - Real-time music search & playback
   - Spotify playlist importer
   - Bottom audio player controls & volume
   - Offline & online stream playback
   - No command prompt or console window required!

---

### 📦 Distributing to Other Windows Laptops

You can share **`dist\Music-Windows-x64.zip`**:
- Anyone on Windows 10 or 11 can unzip it and double-click `Music.exe` to run.
- **Does NOT require Python** to be installed on their laptop! Everything (Python runtime, WebView2 wrapper, FastAPI server, UI assets) is self-contained.

---

### 🛠️ How to Rebuild on Windows

To rebuild anytime:
```cmd
packaging\windows\build_windows.bat
```
Or run directly:
```cmd
pyinstaller --noconfirm --clean Music.spec
python packaging\windows\create_portable_zip.py
```
