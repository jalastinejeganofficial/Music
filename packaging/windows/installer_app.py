"""
Music Desktop - Automated Package Manager & Installer (GUI)
Installs Music, creates shortcuts, and launches the full-stack software automatically.
"""

import os
import sys
import time
import shutil
import zipfile
import urllib.request
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

REPO_SLUG = "jalastinejeganofficial/Music"
DOWNLOAD_URL = f"https://github.com/{REPO_SLUG}/releases/latest/download/Music-Windows-x64.zip"
DEFAULT_INSTALL_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Programs", "Music")

class MusicInstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Music - Setup & Package Manager")
        self.geometry("540x480")
        self.resizable(False, False)
        self.configure(bg="#121212")

        # Set window icon if available
        self._load_icon()

        self.install_dir = tk.StringVar(value=DEFAULT_INSTALL_DIR)
        self.create_desktop_shortcut = tk.BooleanVar(value=True)
        self.create_startmenu_shortcut = tk.BooleanVar(value=True)
        self.auto_launch = tk.BooleanVar(value=True)
        self.status_text = tk.StringVar(value="Click 'Install & Launch' to start.")

        self._setup_styles()
        self._build_ui()

    def _load_icon(self):
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "icon.ico")
        if not os.path.exists(icon_path):
            # Check PyInstaller frozen bundle
            base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_dir, "assets", "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

    def _setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        
        # Configure dark theme styles
        self.style.configure(".", background="#121212", foreground="#ffffff")
        self.style.configure("TProgressbar", thickness=14, troughcolor="#222222", background="#ff0033")
        self.style.configure("Dark.TCheckbutton", background="#121212", foreground="#e0e0e0", font=("Segoe UI", 9))
        self.style.map("Dark.TCheckbutton", background=[("active", "#121212")], foreground=[("active", "#ffffff")])

    def _build_ui(self):
        # Header Container
        header_frame = tk.Frame(self, bg="#1a1a1a", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_lbl = tk.Label(header_frame, text="🎵 Music Desktop", font=("Segoe UI", 16, "bold"), fg="#ffffff", bg="#1a1a1a")
        title_lbl.pack(anchor="w", padx=24, pady=(14, 2))

        sub_lbl = tk.Label(header_frame, text="Full-Stack Music Player • Automated Package Manager", font=("Segoe UI", 9), fg="#999999", bg="#1a1a1a")
        sub_lbl.pack(anchor="w", padx=24)

        # Body Frame
        body = tk.Frame(self, bg="#121212", padx=24, pady=18)
        body.pack(fill=tk.BOTH, expand=True)

        # Destination Folder Selector
        dest_lbl = tk.Label(body, text="Installation Location:", font=("Segoe UI", 9, "bold"), fg="#cccccc", bg="#121212")
        dest_lbl.pack(anchor="w", pady=(0, 4))

        path_frame = tk.Frame(body, bg="#121212")
        path_frame.pack(fill=tk.X, pady=(0, 16))

        path_entry = tk.Entry(path_frame, textvariable=self.install_dir, font=("Segoe UI", 9), bg="#1e1e1e", fg="#ffffff", insertbackground="#ffffff", relief=tk.FLAT, bd=6)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        browse_btn = tk.Button(path_frame, text="Browse...", font=("Segoe UI", 8), bg="#2a2a2a", fg="#ffffff", activebackground="#333333", activeforeground="#ffffff", relief=tk.FLAT, bd=5, command=self._browse_dir)
        browse_btn.pack(side=tk.LEFT, padx=(8, 0))

        # Shortcut & Launch Checkboxes
        cb_desk = ttk.Checkbutton(body, text="Create Desktop Shortcut", variable=self.create_desktop_shortcut, style="Dark.TCheckbutton")
        cb_desk.pack(anchor="w", pady=3)

        cb_start = ttk.Checkbutton(body, text="Create Start Menu Shortcut", variable=self.create_startmenu_shortcut, style="Dark.TCheckbutton")
        cb_start.pack(anchor="w", pady=3)

        cb_run = ttk.Checkbutton(body, text="Launch Music automatically when ready (Frontend + Backend)", variable=self.auto_launch, style="Dark.TCheckbutton")
        cb_run.pack(anchor="w", pady=3)

        # Status & Progress Section
        status_box = tk.Frame(body, bg="#181818", bd=1, relief=tk.SOLID, padx=12, pady=12)
        status_box.pack(fill=tk.X, pady=(18, 12))

        self.status_lbl = tk.Label(status_box, textvariable=self.status_text, font=("Segoe UI", 9), fg="#00e676", bg="#181818", anchor="w")
        self.status_lbl.pack(fill=tk.X, pady=(0, 8))

        self.progressbar = ttk.Progressbar(status_box, orient="horizontal", mode="determinate", style="TProgressbar")
        self.progressbar.pack(fill=tk.X)

        # Action Buttons Container
        btn_frame = tk.Frame(self, bg="#121212", padx=24, pady=16)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.install_btn = tk.Button(
            btn_frame,
            text="Install & Launch 🚀",
            font=("Segoe UI", 10, "bold"),
            bg="#ff0033",
            fg="#ffffff",
            activebackground="#ff3355",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=6,
            padx=16,
            command=self._start_install_thread
        )
        self.install_btn.pack(side=tk.RIGHT)

        close_btn = tk.Button(
            btn_frame,
            text="Exit",
            font=("Segoe UI", 9),
            bg="#252525",
            fg="#cccccc",
            activebackground="#333333",
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=5,
            padx=12,
            command=self.destroy
        )
        close_btn.pack(side=tk.RIGHT, padx=(0, 10))

    def _browse_dir(self):
        chosen = filedialog.askdirectory(initialdir=self.install_dir.get(), title="Select Install Folder")
        if chosen:
            self.install_dir.set(os.path.normpath(chosen))

    def _set_status(self, text, progress_pct=None):
        self.status_text.set(text)
        if progress_pct is not None:
            self.progressbar["value"] = progress_pct
        self.update_idletasks()

    def _start_install_thread(self):
        self.install_btn.config(state=tk.DISABLED, text="Installing...")
        threading.Thread(target=self._run_installation, daemon=True).start()

    def _find_local_zip(self):
        possible_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "Music-Windows-x64.zip"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "dist", "Music-Windows-x64.zip"),
            os.path.join(os.getcwd(), "dist", "Music-Windows-x64.zip"),
            os.path.join(os.getcwd(), "Music-Windows-x64.zip"),
            os.path.join(getattr(sys, '_MEIPASS', ''), "Music-Windows-x64.zip")
        ]
        for p in possible_paths:
            if p and os.path.exists(p) and os.path.isfile(p):
                return p
        return None

    def _run_installation(self):
        try:
            target_dir = os.path.normpath(self.install_dir.get())
            temp_zip = os.path.join(os.environ.get("TEMP", "C:\\Temp"), "Music-Windows-x64.zip")

            # Step 1: Obtain Package
            local_zip = self._find_local_zip()
            if local_zip:
                self._set_status(f"Found local package: {os.path.basename(local_zip)}", 15)
                shutil.copyfile(local_zip, temp_zip)
            else:
                self._set_status("Downloading latest package from GitHub...", 5)
                def hook(blocks, block_size, total_size):
                    if total_size > 0:
                        downloaded = blocks * block_size
                        pct = min(40, int(5 + (downloaded / total_size) * 35))
                        mb = downloaded / (1024 * 1024)
                        total_mb = total_size / (1024 * 1024)
                        self._set_status(f"Downloading: {mb:.1f} MB / {total_mb:.1f} MB ({int((downloaded/total_size)*100)}%)", pct)
                
                try:
                    urllib.request.urlretrieve(DOWNLOAD_URL, temp_zip, reporthook=hook)
                except Exception as e:
                    # Check for local dist/Music folder fallback
                    local_dist_music = os.path.join(os.getcwd(), "dist", "Music")
                    if os.path.exists(os.path.join(local_dist_music, "Music.exe")):
                        self._set_status("Using local dist/Music directory...", 35)
                        if os.path.exists(target_dir):
                            shutil.rmtree(target_dir, ignore_errors=True)
                        shutil.copytree(local_dist_music, target_dir)
                        temp_zip = None
                    else:
                        raise RuntimeError(f"Could not download package ({e}) and no local package was found.")

            # Step 2: Extract
            if temp_zip and os.path.exists(temp_zip):
                self._set_status("Extracting files to installation folder...", 45)
                extract_temp = os.path.join(os.environ.get("TEMP", "C:\\Temp"), f"MusicExtract_{int(time.time())}")
                if os.path.exists(extract_temp):
                    shutil.rmtree(extract_temp, ignore_errors=True)
                os.makedirs(extract_temp, exist_ok=True)

                with zipfile.ZipFile(temp_zip, 'r') as zf:
                    zf.extractall(extract_temp)

                # Kill any active Music process before overwriting
                subprocess.run(["taskkill", "/F", "/IM", "Music.exe"], capture_output=True)
                time.sleep(1)

                if os.path.exists(target_dir):
                    shutil.rmtree(target_dir, ignore_errors=True)
                os.makedirs(target_dir, exist_ok=True)

                # Determine root folder
                inner_music = os.path.join(extract_temp, "Music")
                src_dir = inner_music if os.path.exists(os.path.join(inner_music, "Music.exe")) else extract_temp
                
                for item in os.listdir(src_dir):
                    s = os.path.join(src_dir, item)
                    d = os.path.join(target_dir, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d)
                    else:
                        shutil.copy2(s, d)

                # Cleanup temp
                shutil.rmtree(extract_temp, ignore_errors=True)
                try:
                    os.remove(temp_zip)
                except Exception:
                    pass

            exe_path = os.path.join(target_dir, "Music.exe")
            if not os.path.exists(exe_path):
                raise FileNotFoundError(f"Installation failed: Music.exe not found in {target_dir}")

            self._set_status("Configuring shortcuts...", 80)

            # Step 3: Create Shortcuts
            if self.create_desktop_shortcut.get():
                desktop = self._get_special_folder("Desktop")
                if desktop:
                    self._create_shortcut(exe_path, os.path.join(desktop, "Music.lnk"), target_dir)

            if self.create_startmenu_shortcut.get():
                programs = self._get_special_folder("Programs")
                if programs:
                    self._create_shortcut(exe_path, os.path.join(programs, "Music.lnk"), target_dir)

            self._set_status("Installation complete!", 100)
            time.sleep(0.5)

            # Step 4: Automatically launch Frontend + Backend
            if self.auto_launch.get():
                self._set_status("🚀 Launching Music (Frontend + Backend)...", 100)
                subprocess.Popen([exe_path], cwd=target_dir)
                time.sleep(1.5)
                self.destroy()
            else:
                messagebox.showinfo("Success", f"Music has been successfully installed to:\n{target_dir}")
                self.install_btn.config(state=tk.NORMAL, text="Installed")

        except Exception as err:
            self._set_status(f"Error: {err}", 0)
            messagebox.showerror("Installation Error", str(err))
            self.install_btn.config(state=tk.NORMAL, text="Retry Install")

    def _get_special_folder(self, name):
        try:
            cmd = f"[Environment]::GetFolderPath('{name}')"
            res = subprocess.run(["powershell", "-NoProfile", "-Command", cmd], capture_output=True, text=True, check=True)
            return res.stdout.strip()
        except Exception:
            if name == "Desktop":
                return os.path.join(os.path.expanduser("~"), "Desktop")
            return None

    def _create_shortcut(self, target, lnk_path, working_dir):
        try:
            # Use PowerShell WScript.Shell with safe quoting
            ps_script = f"""
            $ws = New-Object -ComObject WScript.Shell
            $s = $ws.CreateShortcut('{lnk_path}')
            $s.TargetPath = '{target}'
            $s.WorkingDirectory = '{working_dir}'
            $s.IconLocation = '{target},0'
            $s.Description = 'Music Desktop Application'
            $s.Save()
            """
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, check=True)
        except Exception as e:
            print(f"Warning: shortcut creation failed for {lnk_path}: {e}")

if __name__ == "__main__":
    app = MusicInstallerApp()
    # Check if CLI auto-install flag passed
    if "--auto" in sys.argv:
        app.after(500, app._start_install_thread)
    app.mainloop()
