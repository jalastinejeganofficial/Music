# 🪟 Music Player - Windows Package Manager & Software Setup

Native desktop software for Windows 10 & Windows 11 (64-bit), bundling both the **FastAPI uvicorn backend** and **modern frontend web player** into a single native desktop window with automatic port management and zero terminal windows.

---

### 📦 Installation & Setup Options (Zero Python Required)

#### Option 1: Native Windows Installer (`Music.msi`) 🌟 (Recommended)
1. Double-click **`dist\Music.msi`** (or install via `msiexec /i dist\Music.msi`).
2. Windows Installer installs all software components natively to `%LOCALAPPDATA%\Programs\Music`.
3. Automatically places a permanent **Desktop Shortcut with custom Music icon** directly on your desktop.
4. Registers in Windows Start Menu and "Installed apps" for easy opening anytime.
5. Double-click the desktop icon anytime to immediately launch both backend & frontend together!

#### Option 2: Standalone Package Manager Installer (`MusicSetup.exe`)
1. Run **`dist\MusicSetup.exe`**.
2. Select options (Desktop Shortcut, Start Menu Shortcut, Auto-Launch).
3. Click **Install & Launch 🚀**.
4. The package manager installs all files into `%LOCALAPPDATA%\Programs\Music` and **automatically launches both frontend and backend software**.

#### Option 2: 1-Click Double-Click Setup (`setup.bat`)
Double-click **`setup.bat`** in the repository root or in `packaging\windows\setup.bat`.
It automatically runs the package manager, installs all components, creates shortcuts, and boots the application.

#### Option 3: PowerShell One-Liner Web Installer
Open PowerShell and run:
```powershell
irm https://raw.githubusercontent.com/jalastinejeganofficial/Music/main/packaging/windows/install.ps1 | iex
```
This downloads the latest release directly from GitHub, extracts it, creates desktop shortcuts, and launches the software automatically.

---

### 🚀 Direct Portable Run (No Install Required)

If you prefer not to install anything:
1. Open **`dist\Music\`**
2. Double-click **`Music.exe`**.
3. Both frontend and backend start up automatically in a native `#0a0a0a` dark-themed window with custom icons.

---

### 🛠️ Developer: How to Rebuild Package Manager & Executables

Run:
```cmd
packaging\windows\build_windows.bat
```
Or build the Package Manager Installer executable:
```cmd
pyinstaller --noconfirm --clean --onefile --noconsole --name MusicSetup --icon assets/icon.ico --add-data "assets;assets" packaging/windows/installer_app.py
```
