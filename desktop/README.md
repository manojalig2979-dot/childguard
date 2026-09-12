# ChildGuard Windows Desktop Surveillance, Process Watchdog & SafeSearch Agent

The ChildGuard Windows Desktop Agent runs continuously as a background system guardian on supervised Windows computers. It enforces application blacklists, inspects active window titles, forces SafeSearch at the network layer, and executes instant remote workstation locks.

---

## Core Capabilities

### 1. Active Process Watchdog & Termination
- Uses native Win32 kernel APIs (`CreateToolhelp32Snapshot`, `Process32FirstW`, `Process32NextW`, `OpenProcess`, `TerminateProcess`).
- Continuously scans running processes every 3 seconds against blacklisted executables:
  - **Dark Web / Anonymizers**: `tor.exe`, `firefox-tor.exe`
  - **P2P Torrents**: `bittorrent.exe`, `utorrent.exe`, `qbittorrent.exe`, `deluge.exe`
  - **Memory/Game Hack Tools**: `cheatengine.exe`, `cheatengine-x86_64.exe`, `cheatengine-i386.exe`
  - **Packet Sniffers / Proxies**: `wireshark.exe`, `fiddler.exe`
  - **Gambling & Betting Clients**: `pokerstars.exe`, `bet365.exe`, `casinogame.exe`
- Immediately terminates unauthorized processes and dispatches a `PROCESS_VIOLATION_ALARM` (`CRITICAL` severity) to the parent controller over MQTT.

### 2. Network-Level SafeSearch & Domain Sinkhole Filter
- Enforces SafeSearch across all browsers (Chrome, Edge, Firefox, Brave) by routing major search engine queries to their official VIP IPs:
  - **Google**: `216.239.38.120` (`forcesafesearch.google.com`)
  - **YouTube**: `216.239.38.119` (`restrict.youtube.com`)
  - **Bing**: `204.79.197.220` (`strict.bing.com`)
  - **DuckDuckGo**: `52.142.124.215` (`safe.duckduckgo.com`)
- Sinks known high-risk adult, gambling, and piracy domains to loopback null route (`127.0.0.1`).
- Calls `dnsapi.DnsFlushResolverCache()` via Win32 API to apply rules immediately.
- Includes a background self-healing anti-tamper thread restoring rules if modified.

### 3. Window Title Inspector & Content Minimizer
- Periodically captures the active foreground window title via `user32.GetForegroundWindow` and `user32.GetWindowTextW`.
- Checks for restricted keywords (`gambling`, `casino`, `torrent`, `xxx`, `porn`, `dark web`, etc.).
- Instantly calls `ShowWindow(hwnd, SW_MINIMIZE)` to hide the prohibited feed and reports the violation.

### 4. Remote Workstation Lock
- Subscribes to parental remote commands (`devices/{DEVICE_ID}/commands`).
- Triggers immediate Windows lock screen session via `user32.LockWorkStation()` upon receiving `LOCK_DEVICE` or `LOCK_STATION`.

---

## Setup & Running

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Launch the agent (Run as Administrator for hosts file modification)
python desktop_agent.py
```
