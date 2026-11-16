"""
Music Desktop Application Launcher.
Wraps the FastAPI server and modern frontend into a standalone native desktop window.
On Windows: Launches directly via Edge/Chromium App Mode (no address bar, no browser tabs,
standalone native dark-themed window) - 100% reliable without .NET CLR crashes.
"""
import sys
import os
import time

# --- CRITICAL FIX FOR WINDOWS GUI / NOCONSOLE MODE ---
# In windowed PyInstaller executables (console=False), sys.stdout, stderr, stdin are None.
# Uvicorn's logging formatter calls sys.stdout.isatty(), crashing if streams are None.
class DummyStream:
    def write(self, s):
        pass
    def flush(self):
        pass
    def isatty(self):
        return False

if sys.stdout is None:
    sys.stdout = DummyStream()
if sys.stderr is None:
    sys.stderr = DummyStream()
if sys.stdin is None:
    sys.stdin = DummyStream()

import socket
import threading
import urllib.request
import subprocess
import shutil
import webbrowser
import traceback

# Setup persistent runtime logger in user AppData
LOG_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Programs", "Music")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "desktop_runtime.log")

def log(msg):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

log("=== Music Desktop Launcher Starting ===")

# Resolve frozen PyInstaller base path
if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

log(f"Base Directory: {BASE_DIR}")

def find_free_port(start_port=5000):
    for p in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', p))
                return p
        except OSError:
            continue
    return start_port

def start_backend(port, server_container):
    try:
        import uvicorn
        from server import app
        
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=port,
            log_config=None,
            log_level="critical",
            access_log=False
        )
        server = uvicorn.Server(config)
        server_container['server'] = server
        log(f"Backend uvicorn starting on port {port}...")
        server.run()
    except Exception as e:
        log(f"FATAL: Backend failed to start: {e}\n{traceback.format_exc()}")

def wait_for_server(port, timeout=10):
    start = time.time()
    url = f"http://127.0.0.1:{port}/"
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=0.5) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(0.1)
    return False

def launch_native_window(app_url):
    """
    Launches an isolated native desktop application window.
    Runs in dedicated App Mode: no address bar, no tabs, standalone window.
    """
    profile_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "MusicApp_Profile")
    os.makedirs(profile_dir, exist_ok=True)
    
    app_args = [
        f"--app={app_url}",
        f"--user-data-dir={profile_dir}",
        "--window-size=1240,820",
        "--hide-scrollbars=false",
        "--enable-features=OverlayScrollbar"
    ]

    # Windows candidate executables
    candidate_browsers = [
        # Microsoft Edge (Standard on every Windows 10/11 system)
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        # Google Chrome
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        # Brave
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        # Linux/macOS equivalents
        "google-chrome", "chromium-browser", "chromium", "microsoft-edge"
    ]

    for browser in candidate_browsers:
        if os.path.exists(browser) or (sys.platform != "win32" and shutil.which(browser)):
            try:
                log(f"Launching standalone app window via: {browser}")
                proc = subprocess.Popen([browser] + app_args)
                return proc
            except Exception as e:
                log(f"Failed to launch {browser}: {e}")

    # Fallback to default browser
    log("Falling back to system default browser.")
    webbrowser.open(app_url)
    return None

def main():
    port = find_free_port(5000)
    server_container = {}
    
    log(f"Binding backend to port {port}...")
    server_thread = threading.Thread(
        target=start_backend,
        args=(port, server_container),
        daemon=True
    )
    server_thread.start()
    
    # Wait until the backend is responding
    server_ready = wait_for_server(port, timeout=8)
    log(f"Backend readiness: {server_ready}")
    app_url = f"http://127.0.0.1:{port}/"

    # Launch native desktop window
    window_proc = launch_native_window(app_url)

    if window_proc:
        log(f"Window process running (PID: {window_proc.pid}). Waiting for user to close...")
        try:
            window_proc.wait()
            log("Window closed by user.")
        except Exception as e:
            log(f"Wait error: {e}")
    else:
        # If opened in default browser, keep backend alive
        log("Running in background browser mode. Waiting...")
        try:
            while True:
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            pass

    log("Cleaning up backend server...")
    if 'server' in server_container:
        server_container['server'].should_exit = True
    log("Music Desktop Exiting.")
    sys.exit(0)

if __name__ == '__main__':
    main()
