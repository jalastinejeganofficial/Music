# 🐧 Music Player for Linux

### 📦 Option 1: Run Pre-built AppImage (Easiest, No Install Required)
The AppImage runs out of the box on **Ubuntu, Debian, Fedora, Arch, Manjaro, Linux Mint, Pop!_OS**, and all modern Linux distros:

```bash
chmod +x Music-x86_64.AppImage
./Music-x86_64.AppImage
```

---

### 📦 Option 2: Build from Source on Linux

1. **Install WebKit & Python dependencies:**
   - **Ubuntu / Debian / Mint:**
     ```bash
     sudo apt update
     sudo apt install -y python3-pip libwebkit2gtk-4.1-0 python3-gi gir1.2-webkit2-4.1
     ```
   - **Fedora / RHEL:**
     ```bash
     sudo dnf install -y python3-pip webkit2gtk4.1
     ```
   - **Arch Linux / Manjaro:**
     ```bash
     sudo pacman -S python-pip webkit2gtk-4.1
     ```

2. **Run the build script:**
   ```bash
   chmod +x packaging/linux/build_linux.sh
   ./packaging/linux/build_linux.sh
   ```

3. **Install application to system launcher:**
   ```bash
   sudo mkdir -p /opt/music
   sudo cp -r dist/Music/* /opt/music/
   sudo cp packaging/linux/music.desktop /usr/share/applications/
   sudo update-desktop-database
   ```
   Now **Music** appears in your application menu with the app icon!
