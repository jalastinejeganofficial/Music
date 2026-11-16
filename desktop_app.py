"""
Music Desktop Application Launcher.
Wraps the FastAPI server and modern frontend into a standalone native desktop window
powered by pywebview (Edge WebView2 on Windows, WebKitGTK on Linux, WebKit on macOS).
"""
import sys
import os
import time
import socket
import threading
import urllib.request
import webbrowser

# Resolve frozen PyInstaller base path
if getattr(sys, 'frozen', False):
    BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
    import uvicorn
    from server import app
    
    config = uvicorn.Config(
        app=app,
        host="127.0.0.1",
        port=port,
        log_level="error",
        access_log=False
    )
    server = uvicorn.Server(config)
    server_container['server'] = server
    server.run()

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

def main():
    port = find_free_port(5000)
    server_container = {}
    
    server_thread = threading.Thread(
        target=start_backend,
        args=(port, server_container),
        daemon=True
    )
    server_thread.start()
    
    # Wait until the backend is responding
    wait_for_server(port, timeout=8)
    app_url = f"http://127.0.0.1:{port}/"

    icon_path = os.path.join(BASE_DIR, 'assets', 'icon.png')
    if not os.path.exists(icon_path):
        icon_path = None

    try:
        import webview
        
        window = webview.create_window(
            title='Music',
            url=app_url,
            width=1240,
            height=820,
            min_size=(760, 560),
            background_color='#0a0a0a',
            text_select=False
        )
        
        # Start desktop window (blocks until user closes window)
        webview.start(icon=icon_path, debug=False)
        
    except Exception as e:
        print(f"[Desktop Launcher] pywebview notice ({e}). Opening in default browser...")
        webbrowser.open(app_url)
        # Keep server thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
    finally:
        if 'server' in server_container:
            server_container['server'].should_exit = True
        sys.exit(0)

if __name__ == '__main__':
    main()
