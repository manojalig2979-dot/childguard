#!/usr/bin/env python3
"""
ChildGuard AI - Live Interactive Android Child Agent Terminal Daemon (Option 1)
Emulates the native Android agent subsystems:
- ChildGuardService.kt (Persistent Foreground Daemon)
- LocationTracker.kt (Adaptive GPS provider)
- NotificationMonitorService.kt (Chat & SMS Threat Sniffer)
- GuardDeviceAdminReceiver.kt (Anti-Uninstall & Remote Lock Enforcement)
- SocialFeedInspectorService.kt (Hardware Volume SOS Trigger)
"""

import sys
import time
import json
import re
import threading
from typing import Dict, Any

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ANSI Color Codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

DEVICE_ID = "child_dev_99182"
CHILD_NAME = "Aarav"
PARENT_PIN = "1234"

# State
state = {
    "latitude": 28.6145,
    "longitude": 77.2120,
    "speed": 0.8,
    "battery": 88,
    "is_locked": False,
    "auto_beacon": False,
    "recent_alerts": [],
    "stop_requested": False
}

# Regex Threat Patterns from NotificationMonitorService.kt
THREAT_PATTERNS = [
    re.compile(r"\b(suicide|kill yourself|hurt you|die|hate you)\b", re.IGNORECASE),
    re.compile(r"\b(meet alone|secret place|send photo|nude|don't tell)\b", re.IGNORECASE)
]

def emit_location_ping(reason: str = "Periodic Tracker Ping"):
    payload = {
        "device_id": DEVICE_ID,
        "latitude": state["latitude"],
        "longitude": state["longitude"],
        "speed": state["speed"],
        "battery": state["battery"],
        "timestamp": int(time.time() * 1000)
    }
    print(f"\n{CYAN}[LocationTracker] Emitted GPS Telemetry ({reason}):{RESET}")
    print(f"  Lat: {state['latitude']:.4f}° N, Lon: {state['longitude']:.4f}° E | Speed: {state['speed']} m/s | Battery: {state['battery']}%")

def inspect_incoming_notification(app_pkg: str, sender: str, message: str):
    print(f"\n{YELLOW}[NotificationMonitorService] Inspecting preview from {app_pkg} ({sender})...{RESET}")
    print(f"  Snippet: \"{message}\"")

    detected = False
    for pattern in THREAT_PATTERNS:
        match = pattern.search(message)
        if match:
            detected = True
            alert = {
                "type": "CHAT_SECURITY_ALARM",
                "severity": "HIGH",
                "app_package": app_pkg,
                "sender": sender,
                "snippet": message[:100],
                "trigger": f"Threat keyword detected: '{match.group(0)}'",
                "timestamp": int(time.time() * 1000)
            }
            state["recent_alerts"].append(alert)
            print(f"{BOLD}{RED}[ALERT DISPATCHED] CHAT_SECURITY_ALARM triggered!{RESET}")
            print(f"  {RED}Matched:{RESET} '{match.group(0)}' in {app_pkg}")
            print(f"  {RED}Payload queued for MQTT upload (QoS 1) to Parent Controller.{RESET}")
            break

    if not detected:
        print(f"  {GREEN}[CLEAR]{RESET} No threat patterns found. Message allowed without alarm.")

def trigger_hardware_sos():
    print(f"\n{BOLD}{RED}[SocialFeedInspectorService] Physical Volume Down Triple-Tap Intercepted!{RESET}")
    print(f"  {YELLOW}[Haptic Feedback]{RESET} Delivered 120ms stealth vibration to child.")
    alert = {
        "type": "EMERGENCY_SOS_ALARM",
        "severity": "CRITICAL",
        "trigger": "HARDWARE_TRIPLE_VOLUME_TAP",
        "snippet": "EMERGENCY: Silent panic signal triggered via physical button sequence!",
        "latitude": state["latitude"],
        "longitude": state["longitude"],
        "speed": state["speed"],
        "battery_percent": state["battery"],
        "timestamp": int(time.time() * 1000)
    }
    state["recent_alerts"].append(alert)
    print(f"{BOLD}{RED}[CRITICAL ALARM DISPATCHED] EMERGENCY_SOS_ALARM sent to parent app!{RESET}")
    print(f"  Coordinates: {state['latitude']:.4f}° N, {state['longitude']:.4f}° E | Battery: {state['battery']}%")

def handle_remote_lock():
    state["is_locked"] = True
    print(f"\n{BOLD}{RED}======================================================={RESET}")
    print(f"{BOLD}{RED} [DeviceAdminReceiver] EMERGENCY DEVICE LOCK ENGAGED!  {RESET}")
    print(f"{BOLD}{RED}======================================================={RESET}")
    print(f"  The device screen has been shut down via DevicePolicyManager.")
    print(f"  Device is locked. Requires Parent Master PIN ({PARENT_PIN}) to resume.\n")

def unlock_device(pin: str):
    if pin.strip() == PARENT_PIN:
        state["is_locked"] = False
        print(f"\n{GREEN}[DeviceAdminReceiver] Master PIN Verified! Device Unlocked.{RESET}")
    else:
        print(f"\n{RED}[DeviceAdminReceiver] Invalid PIN. Device remains locked.{RESET}")

def background_beacon_worker():
    while not state["stop_requested"]:
        if state["auto_beacon"] and not state["is_locked"]:
            # Slight random walk
            state["latitude"] += 0.0001
            state["longitude"] += 0.0001
            emit_location_ping("Continuous GPS Beacon")
        time.sleep(6)

def print_dashboard():
    print(f"\n{BOLD}{CYAN}==================================================================={RESET}")
    print(f"{BOLD}{CYAN}      CHILDGUARD ANDROID AGENT DAEMON (DEVICE SIMULATOR)           {RESET}")
    print(f"{BOLD}{CYAN}==================================================================={RESET}")
    print(f"Target Child: {BOLD}{CHILD_NAME}{RESET} | Device UID: {BOLD}{DEVICE_ID}{RESET}")
    
    lock_status = f"{RED}LOCKED (Screen Off){RESET}" if state["is_locked"] else f"{GREEN}ACTIVE (Protected){RESET}"
    beacon_status = f"{GREEN}ON{RESET}" if state["auto_beacon"] else f"{YELLOW}OFF{RESET}"
    
    print(f"Daemon Status: {lock_status} | Continuous Beacon: {beacon_status}")
    print(f"Coordinates  : {state['latitude']:.4f}° N, {state['longitude']:.4f}° E | Speed: {state['speed']} m/s | Battery: {state['battery']}%")
    print(f"Alerts Sent  : {len(state['recent_alerts'])} events recorded")
    print(f"{CYAN}-------------------------------------------------------------------{RESET}")
    print(f"  {BOLD}[1]{RESET} Jump to School Campus Safe Zone    (Lat: 28.6145, Lon: 77.2120)")
    print(f"  {BOLD}[2]{RESET} Jump Outside Safe Zone Perimeter   (Lat: 28.6190, Lon: 77.2180)")
    print(f"  {BOLD}[3]{RESET} Jump into Industrial Danger Zone   (Lat: 28.6120, Lon: 77.2340)")
    print(f"  {BOLD}[4]{RESET} Inject Simulated Chat Notification (WhatsApp / SMS)")
    print(f"  {BOLD}[5]{RESET} Trigger Physical Button SOS Panic  (Triple Volume Down)")
    print(f"  {BOLD}[6]{RESET} Simulate Parent Emergency Lock Command")
    print(f"  {BOLD}[7]{RESET} Unlock Device with Master Parent PIN")
    print(f"  {BOLD}[8]{RESET} Toggle Continuous GPS Beacon (Every 6s)")
    print(f"  {BOLD}[q]{RESET} Quit Daemon")
    print(f"{CYAN}==================================================================={RESET}")

def main():
    beacon_thread = threading.Thread(target=background_beacon_worker, daemon=True)
    beacon_thread.start()

    print(f"{GREEN}[ChildGuardService] Sticky Foreground Daemon Initialized.{RESET}")
    print(f"{GREEN}[LocationTracker] FusedLocationProviderClient active.{RESET}")
    print(f"{GREEN}[NotificationMonitorService] NotificationListenerService active.{RESET}")
    print(f"{GREEN}[GuardDeviceAdminReceiver] Device Administrator policy registered.{RESET}")

    while True:
        print_dashboard()
        try:
            choice = input(f"\n{BOLD}Select an action [1-8, q]: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == '1':
            state["latitude"] = 28.6145
            state["longitude"] = 77.2120
            state["speed"] = 0.5
            emit_location_ping("School Campus (Inside Safe Zone)")

        elif choice == '2':
            state["latitude"] = 28.6190
            state["longitude"] = 77.2180
            state["speed"] = 1.9
            emit_location_ping("Outside Safe Zone Perimeter (Transit)")

        elif choice == '3':
            state["latitude"] = 28.6120
            state["longitude"] = 77.2340
            state["speed"] = 2.4
            emit_location_ping("Industrial Construction Site (DANGER ZONE)")

        elif choice == '4':
            print("\nSelect message preset or type custom:")
            print("  a. Predatory Chat: 'meet alone at the secret place don't tell your parents'")
            print("  b. Harassment Chat: 'everyone hates you die'")
            print("  c. Normal Safe Chat: 'hey did you finish the math homework?'")
            print("  d. Type custom text...")
            sub = input("Choose [a, b, c, d]: ").strip().lower()

            if sub == 'a':
                inspect_incoming_notification("com.whatsapp", "+91 98765 00001", "Hey, meet alone at the secret place after class, don't tell your parents.")
            elif sub == 'b':
                inspect_incoming_notification("org.telegram.messenger", "Anonymous", "Everyone hates you die.")
            elif sub == 'c':
                inspect_incoming_notification("com.whatsapp", "Classmate Rohan", "Hey did you finish the math homework?")
            elif sub == 'd':
                custom_text = input("Enter notification text to test: ").strip()
                inspect_incoming_notification("com.whatsapp", "Test Sender", custom_text)

        elif choice == '5':
            trigger_hardware_sos()

        elif choice == '6':
            handle_remote_lock()

        elif choice == '7':
            pin = input("Enter Parent Master PIN to unlock (default: 1234): ")
            unlock_device(pin)

        elif choice == '8':
            state["auto_beacon"] = not state["auto_beacon"]
            status_text = "ENABLED" if state["auto_beacon"] else "DISABLED"
            print(f"\n{YELLOW}[LocationTracker] Continuous GPS Beacon is now {status_text}.{RESET}")

        elif choice.lower() == 'q':
            state["stop_requested"] = True
            print("\n[ChildGuardService] Shutting down Android agent daemon. Goodbye!")
            break

        time.sleep(0.5)

if __name__ == "__main__":
    main()
