#!/usr/bin/env python3
"""
ChildGuard AI - Unified Ecosystem Master Orchestrator
Launches the Web Command Center and Android Device Daemon side-by-side.
"""

import sys
import subprocess
import os
import time

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    print("\n=======================================================")
    print("        CHILDGUARD AI: UNIFIED ECOSYSTEM LAUNCHER      ")
    print("=======================================================")
    print("[1/2] Starting Web Command Center on http://localhost:8080...")

    # Start Web Dashboard in a separate process
    web_proc = subprocess.Popen([sys.executable, os.path.join(ROOT_DIR, "start_demo.py")])
    time.sleep(1.5)

    print("[2/2] Starting Interactive Android Child Agent Daemon...")
    print("=======================================================\n")

    try:
        # Run Android agent daemon in foreground console
        subprocess.run([sys.executable, os.path.join(ROOT_DIR, "simulator", "run_android_agent.py")])
    except KeyboardInterrupt:
        pass
    finally:
        print("\n[*] Stopping all ChildGuard processes...")
        web_proc.terminate()
        print("[*] ChildGuard Unified Ecosystem stopped cleanly.")

if __name__ == "__main__":
    main()
