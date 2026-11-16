# 🍏 Music Player for macOS

Supports both **Apple Silicon (M1/M2/M3/M4)** and **Intel** Macs running macOS Monterey, Ventura, Sonoma, and Sequoia.

---

### 📦 Option 1: Install from `.dmg`
1. Download **`Music-macOS.dmg`**.
2. Double-click the `.dmg` file to open it.
3. Drag **`Music.app`** into your **`Applications`** folder.
4. Launch **Music** from Spotlight (`Cmd + Space` -> `Music`) or Launchpad.

> **Note for unsigned Mac builds:**  
> If macOS displays *"Apple cannot check it for malicious software"*, open Terminal and run:  
> ```bash
> xattr -cr /Applications/Music.app
> ```  
> Or right-click `Music.app` in Finder and select **Open**.

---

### 📦 Option 2: Build from Source on macOS
```bash
# 1. Clone repository
git clone https://github.com/jalastinejeganofficial/Music.git
cd Music

# 2. Run build script
chmod +x packaging/macos/build_macos.sh
./packaging/macos/build_macos.sh
```
The output `Music.app` and `Music-macOS.dmg` will be ready in the `dist/` folder!
