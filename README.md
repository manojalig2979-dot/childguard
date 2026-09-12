# ChildGuard AI: Intelligent Real-time Parental Supervision & Child Safety Platform

ChildGuard is a multi-platform parental protection ecosystem operating on a privacy-first **Edge-AI + Cloud Ingestion** architecture compliant with the **India Digital Personal Data Protection (DPDP) Act 2023** and **Google Play Families Policy**.

---

## Ecosystem Architecture

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

## Directory Structure

| Directory | Platform / Tech Stack | Description |
|---|---|---|
| [`android/`](file:///f:/ChildGuard/android) | Kotlin, Android SDK, Room, SQLCipher | Background daemon, device admin anti-tamper, adaptive location tracking, notification sniffer, social feed auto-skip accessibility service. |
| [`cloud/`](file:///f:/ChildGuard/cloud) | Docker Compose, PostGIS, Go (Golang) | Infrastructure services: PostGIS spatial database schema and Go MQTT telemetry & alert ingestion pipeline. |
| [`desktop/`](file:///f:/ChildGuard/desktop) | Python 3, Win32 Ctypes, Paho MQTT | Windows active window title inspector, restricted app minimizer, and remote workstation lock. |
| [`parent_app/`](file:///f:/ChildGuard/parent_app) | Flutter / Dart | Real-time monitoring dashboard with live GPS tracking, safety threat feed, and one-tap emergency remote device lock. |

---

## Quickstart Guide

### 1. Cloud Backend & Broker
Spin up PostGIS and EMQX MQTT broker using Docker Compose:
```bash
cd cloud
docker-compose up -d
```
Run the Go telemetry ingestor:
```bash
cd cloud/ingestor
go mod download
go run main.go
```

### 2. Android Child Agent
Open the `android/` directory in Android Studio:
```bash
cd android
./gradlew assembleDebug
```
Deploy the APK to the child's device and grant required permissions:
- Device Administrator (`com.childguard.agent.receivers.GuardDeviceAdminReceiver`)
- Accessibility Service (`com.childguard.agent.services.SocialFeedInspectorService`)
- Notification Listener Service (`com.childguard.agent.services.NotificationMonitorService`)
- Usage Access & Background Location

### 3. Windows Desktop Agent
Install dependencies and launch the background watcher on the target PC:
```bash
cd desktop
pip install -r requirements.txt
python desktop_agent.py
```

### 4. Parent Controller App
Run the Flutter dashboard on iOS/Android:
```bash
cd parent_app
flutter pub get
flutter run
```

---

## Compliance & Privacy Standards
- **India DPDP Act (2023) Section 9**: Verifiable parental consent enforced prior to device telemetry activation.
- **Privacy by Design**: Chat transcripts and keystrokes are processed strictly on-device; only flagged safety triggers with contextual snippets are transmitted over TLS 1.3.
- **Retention Limitation**: Geolocation breadcrumbs are purged automatically after 30 days.
