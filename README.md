# ChildGuard AI: Intelligent Real-Time Parental Supervision & Child Safety Platform
> **An NDTechHub Innovation • A Part of NavDiva Group**

<div align="center">

[![CI Ecosystem Pipeline](https://github.com/manojalig2979-dot/childguard/actions/workflows/ci.yml/badge.svg)](https://github.com/manojalig2979-dot/childguard/actions/workflows/ci.yml)
[![Build Android APK](https://github.com/manojalig2979-dot/childguard/actions/workflows/build_apk.yml/badge.svg)](https://github.com/manojalig2979-dot/childguard/actions/workflows/build_apk.yml)
[![Build Flutter Parent APK](https://github.com/manojalig2979-dot/childguard/actions/workflows/build_parent_apk.yml/badge.svg)](https://github.com/manojalig2979-dot/childguard/actions/workflows/build_parent_apk.yml)
[![Deploy Web Command Center](https://github.com/manojalig2979-dot/childguard/actions/workflows/deploy_pages.yml/badge.svg)](https://github.com/manojalig2979-dot/childguard/actions/workflows/deploy_pages.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**[🌐 Live Web Showcase](https://manojalig2979-dot.github.io/childguard/)** • **[📱 Download Child APK](https://manojalig2979-dot.github.io/childguard/downloads/app-debug.apk)** • **[📲 Parent App APK](https://github.com/manojalig2979-dot/childguard/actions/workflows/build_parent_apk.yml)** • **[📦 GitHub Repository](https://github.com/manojalig2979-dot/childguard.git)**

</div>

---

ChildGuard is an end-to-end multi-platform parental protection and digital safety ecosystem engineered by **NDTechHub** (part of **NavDiva Group**). Operating on an **Edge-AI + Cloud Ingestion** architecture compliant with the **India Digital Personal Data Protection (DPDP) Act 2023** and **Google Play Families Policy**.

---

## 🏛️ Ecosystem Architecture

```
                                  ┌────────────────────────┐
                                  │   Parent Controller    │
                                  │   (Flutter Mobile)     │
                                  └──────────┬─────────────┘
                                             │ TLS 1.3
                                             ▼
┌─────────────────────────┐       ┌────────────────────────┐       ┌─────────────────────────┐
│  Android Child Agent    │◄─────►│    EMQX MQTT Broker    │◄─────►│  Go Telemetry Ingestor  │
│  (Kotlin Daemon & ACC)  │ TLS   │  (Port 1883 / 8883)    │  TLS  └────────────┬────────────┘
└─────────────────────────┘       └────────────────────────┘                    │
                                             ▲                                  ▼
┌─────────────────────────┐                  │                     ┌─────────────────────────┐
│  Windows Desktop Agent  │──────────────────┘                     │   PostgreSQL + PostGIS  │
│  (Win32 Process Watcher)│                                        │   Spatial Database      │
└─────────────────────────┘                                        └─────────────────────────┘
```

---

## 📦 Directory Structure

| Directory | Tech Stack | Description |
|---|---|---|
| [`android/`](android/) | Kotlin, Android SDK, Room, SQLCipher | Background daemon, device admin anti-tamper, adaptive location tracking, notification sniffer, social feed auto-skip accessibility service, and hardware Volume Down SOS trigger. |
| [`cloud/`](cloud/) | Docker Compose, PostGIS, Go (Golang) | Infrastructure services: PostGIS spatial database schema (`schema.sql`), test seed data (`seed.sql`), and Go MQTT telemetry & alert ingestion pipeline. |
| [`desktop/`](desktop/) | Python 3, Win32 Ctypes, Paho MQTT | Windows active window title inspector, prohibited process terminator (`TerminateProcess`), network-level SafeSearch VIP router, and remote lock. |
| [`parent_app/`](parent_app/) | Flutter / Dart | Real-time monitoring dashboard with interactive OpenStreetMap canvas, live animated child pin, geofence polygons, and AI Safety Report card. |
| [`web/`](web/) | HTML5, CSS3, Vanilla JS, Leaflet | Zero-dependency live web visualizer with interactive scenario triggers. |
| [`simulator/`](simulator/) | Python 3 | 6-scenario automated test suite (`e2e_simulation.py`) and live interactive Android terminal daemon emulator (`run_android_agent.py`). |
| [`.github/`](.github/) | GitHub Actions | Workflows for automated CI, cloud Android APK build, and GitHub Pages live deployment. |

---

## 🚀 Quickstart Guide

### 1. Interactive Web Command Center (Instant)
Test the entire system in your browser without any setup:
```bash
python start_demo.py
# or double-click start_demo.bat
```
👉 Or view online at: **[https://manojalig2979-dot.github.io/childguard/](https://manojalig2979-dot.github.io/childguard/)**

### 2. Live Android Child Agent Emulator (No Android Studio needed)
Test the Android daemon, GPS routes, chat threat sniffer, and SOS sequence in your terminal:
```bash
python simulator/run_android_agent.py
# or double-click run_android_agent.bat
```

### 3. Run Automated 6-Scenario Test Suite
```bash
python simulator/e2e_simulation.py
```

### 4. Windows Desktop Agent
Launch the active process watchdog, window minimizer, and SafeSearch enforcer:
```bash
cd desktop
pip install -r requirements.txt
python desktop_agent.py
```

### 5. Cloud Backend & PostGIS (Docker)
```bash
cd cloud
docker-compose up -d
cd ingestor
go run main.go
```

### 6. Parent Controller (Flutter Mobile)
```bash
cd parent_app
flutter pub get
flutter run
```

---

## 🔒 Compliance & Privacy Standards
- **India DPDP Act (2023) Section 9**: Explicit parental consent verified prior to telemetry activation.
- **Privacy by Design**: Chat texts and keystrokes are evaluated exclusively on-device; only flagged safety triggers with contextual snippets are transmitted over TLS 1.3.
- **Automated Data Minimization**: Geolocation breadcrumbs older than 30 days are automatically purged via scheduled PostGIS routines.

---

## 🏢 Organization & Attribution
**ChildGuard AI** is researched, engineered, and maintained by **NDTechHub**, a technology and artificial intelligence division of **NavDiva Group**.

- **Official Git Repository**: [https://github.com/manojalig2979-dot/childguard.git](https://github.com/manojalig2979-dot/childguard.git)
- **Live Showcase & Download Center**: [https://manojalig2979-dot.github.io/childguard/](https://manojalig2979-dot.github.io/childguard/)
- **Parent Company**: **NavDiva Group**
- **Technology Division**: **NDTechHub**
- **License**: MIT Open Source License
