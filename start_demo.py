#!/usr/bin/env python3
"""
ChildGuard AI - One-Click Web Demo Launcher
Starts a local web server and automatically opens the interactive
ChildGuard Command Center in your default web browser.
"""

import os
import sys
import http.server
import socketserver
import webbrowser
import threading
import time

PORT = 8080
DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def log_message(self, format, *args):
        # Suppress verbose asset request logging in console
        pass

def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("\n=======================================================")
    print("      CHILDGUARD AI: WEB COMMAND CENTER LAUNCHER       ")
    print("=======================================================")
    print(f"[*] Serving web dashboard from: {DIRECTORY}")
    print(f"[*] Local URL: http://localhost:{PORT}")
    print("[*] Opening default web browser automatically...")

    def open_browser():
        time.sleep(1.0)
        webbrowser.open(f"http://localhost:{PORT}")

    threading.Thread(target=open_browser, daemon=True).start()

    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print("[+] Server active! Press Ctrl+C at any time to exit.")
            print("=======================================================\n")
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e) or getattr(e, 'winerror', 0) == 10048:
            print(f"[!] Port {PORT} is already in use. Opening browser to existing instance...")
            webbrowser.open(f"http://localhost:{PORT}")
        else:
            print(f"[!] Server error: {e}")
    except KeyboardInterrupt:
        print("\n[*] Shutting down ChildGuard demo server. Goodbye!")

if __name__ == "__main__":
    main()
