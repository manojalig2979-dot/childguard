"""
ChildGuard AI - Windows Desktop Standalone Executable Builder
Packages desktop_agent.py and safesearch_enforcer.py into a single .exe
using PyInstaller.
"""

import sys
import subprocess
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_SCRIPT = os.path.join(SCRIPT_DIR, "desktop_agent.py")
OUTPUT_NAME = "ChildGuardDesktopAgent"

def main():
    print("\n=======================================================")
    print("   CHILDGUARD AI: WINDOWS DESKTOP .EXE PACKAGER        ")
    print("=======================================================")

    # Check if pyinstaller is installed
    try:
        import PyInstaller
        print("[+] PyInstaller is installed.")
    except ImportError:
        print("[*] Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name", OUTPUT_NAME,
        "--paths", SCRIPT_DIR,
        TARGET_SCRIPT
    ]

    print(f"[*] Building standalone executable '{OUTPUT_NAME}.exe'...")
    print(f"[*] Command: {' '.join(cmd)}\n")

    res = subprocess.call(cmd, cwd=SCRIPT_DIR)
    if res == 0:
        print("\n=======================================================")
        print(f"[+] Build Successful! Standalone agent located at:")
        print(f"    {os.path.join(SCRIPT_DIR, 'dist', OUTPUT_NAME, OUTPUT_NAME + '.exe')}")
        print("=======================================================\n")
    else:
        print(f"\n[!] Build failed with exit code: {res}")

if __name__ == "__main__":
    main()
