import sys
import time
import ctypes
from ctypes import wintypes
import json
import threading
import paho.mqtt.client as mqtt
from safesearch_enforcer import SafeSearchEnforcer

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Prohibited Window Keywords
RESTRICTED_KEYWORDS = [
    "gambling", "casino", "torrent", "free movie", "xxx", "porn",
    "betting", "poker", "dark web", "hack tool"
]

# Blacklisted Executable Filenames (Case-insensitive)
BLACK_LISTED_PROCESSES = {
    "tor.exe",
    "firefox-tor.exe",
    "bittorrent.exe",
    "utorrent.exe",
    "qbittorrent.exe",
    "deluge.exe",
    "cheatengine.exe",
    "cheatengine-x86_64.exe",
    "cheatengine-i386.exe",
    "wireshark.exe",
    "fiddler.exe",
    "pokerstars.exe",
    "bet365.exe",
    "casinogame.exe"
}

BROKER_ADDRESS = "broker.childguard.internal"
PORT = 8883
DEVICE_ID = "desktop_pc_agent_001"

# Win32 Process Snapshot Structures & Constants
TH32CS_SNAPPROCESS = 0x00000002
PROCESS_TERMINATE = 0x0001
SW_MINIMIZE = 6

class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.WCHAR * 260)
    ]

# Active Window Title Inspector
def get_foreground_window_title():
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return ""
    length = user32.GetWindowTextLengthW(hwnd)
    if length <= 0:
        return ""
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value

# Win32 Process Termination Helper
def terminate_process_by_pid(pid, proc_name):
    h_process = kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
    if not h_process:
        return False
    try:
        success = kernel32.TerminateProcess(h_process, 1)
        return bool(success)
    finally:
        kernel32.CloseHandle(h_process)

# Enumerate and kill blacklisted running processes
def scan_and_terminate_blacklisted_processes(client):
    h_snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if h_snapshot == wintypes.HANDLE(-1).value or h_snapshot == -1:
        return

    pe32 = PROCESSENTRY32W()
    pe32.dwSize = ctypes.sizeof(PROCESSENTRY32W)

    if not kernel32.Process32FirstW(h_snapshot, ctypes.byref(pe32)):
        kernel32.CloseHandle(h_snapshot)
        return

    terminated_any = False
    try:
        while True:
            exe_name = pe32.szExeFile.lower()
            if exe_name in BLACK_LISTED_PROCESSES:
                pid = pe32.th32ProcessID
                killed = terminate_process_by_pid(pid, exe_name)
                if killed:
                    print(f"[WATCHDOG] Terminated prohibited process: {exe_name} (PID: {pid})")
                    terminated_any = True
                    dispatch_process_alert(client, exe_name, pid)

            if not kernel32.Process32NextW(h_snapshot, ctypes.byref(pe32)):
                break
    finally:
        kernel32.CloseHandle(h_snapshot)

    return terminated_any

def dispatch_process_alert(client, proc_name, pid):
    alert_payload = {
        "type": "PROCESS_VIOLATION_ALARM",
        "severity": "CRITICAL",
        "process_name": proc_name,
        "pid": pid,
        "trigger": "BLACK_LISTED_PROCESS",
        "snippet": f"Prohibited executable '{proc_name}' was detected and terminated.",
        "timestamp": int(time.time() * 1000)
    }
    try:
        client.publish(f"devices/{DEVICE_ID}/alerts/safety", json.dumps(alert_payload), qos=1)
    except Exception as ex:
        print(f"[Alert Dispatch Error] {ex}")

# MQTT Event Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"[Desktop Agent] Connected to broker with result code: {rc}")
    client.subscribe(f"devices/{DEVICE_ID}/commands")

def on_message(client, userdata, msg):
    try:
        command = json.loads(msg.payload.decode())
        action = command.get("action")
        if action in ("LOCK_STATION", "LOCK_DEVICE"):
            print("[Desktop Agent] Received emergency lock command. Locking workstation now...")
            user32.LockWorkStation()
    except Exception as e:
        print(f"Command execution error: {e}")

def main():
    client = mqtt.Client(client_id=DEVICE_ID)
    client.on_connect = on_connect
    client.on_message = on_message

    # Initialize SafeSearch & DNS Loopback Enforcer
    dns_enforcer = SafeSearchEnforcer()
    dns_enforcer.apply_rules()
    dns_enforcer.start_watchdog(interval_seconds=30)

    try:
        client.connect(BROKER_ADDRESS, PORT, 60)
        client.loop_start()
    except Exception as ex:
        print(f"Warning: Cloud connection offline, running locally: {ex}")

    print("[ChildGuard Desktop] Daemon active.")
    print(f"[ChildGuard Desktop] Monitoring window titles & watching for {len(BLACK_LISTED_PROCESSES)} blacklisted executables...")
    print("[ChildGuard Desktop] SafeSearch & DNS Loopback Filter active.")

    last_reported_title = ""
    last_process_scan_time = 0

    while True:
        try:
            now = time.time()

            # 1. Periodic Process Scanner (Every 3 seconds)
            if now - last_process_scan_time >= 3.0:
                scan_and_terminate_blacklisted_processes(client)
                last_process_scan_time = now

            # 2. Active Foreground Window Title Inspector
            current_title = get_foreground_window_title().strip()
            if current_title and current_title != last_reported_title:
                last_reported_title = current_title
                lower_title = current_title.lower()

                for kw in RESTRICTED_KEYWORDS:
                    if kw in lower_title:
                        print(f"[WINDOW VIOLATION] Restricted keyword detected: '{kw}' in title: '{current_title}'")
                        alert_payload = {
                            "type": "DESKTOP_VIOLATION_ALARM",
                            "severity": "HIGH",
                            "window_title": current_title,
                            "trigger": f"Keyword: {kw}",
                            "snippet": f"Restricted window title intercepted: '{current_title[:60]}'",
                            "timestamp": int(time.time() * 1000)
                        }
                        try:
                            client.publish(f"devices/{DEVICE_ID}/alerts/safety", json.dumps(alert_payload), qos=1)
                        except Exception as ex:
                            print(f"[Alert Publish Error] {ex}")

                        # Minimize the restricted window immediately
                        hwnd = user32.GetForegroundWindow()
                        if hwnd:
                            user32.ShowWindow(hwnd, SW_MINIMIZE)
                        break

            time.sleep(1.0)
        except KeyboardInterrupt:
            print("\n[ChildGuard Desktop] Stopping agent...")
            break
        except Exception as err:
            print(f"[Error in main loop] {err}")
            time.sleep(2.0)

    client.loop_stop()

if __name__ == "__main__":
    main()
