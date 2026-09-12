# ChildGuard Parent Controller Application (Flutter / Dart)

The ChildGuard Parent App provides a real-time command center for parents to supervise minor activity, view live GPS breadcrumbs, inspect safety alarms (predatory contacts, self-harm, cyberbullying), and trigger emergency remote device lock.

## Features
- **Live GPS Breadcrumb Tracking**: Displays coordinates, speed, and device connectivity in real time.
- **Safety Threat Feed**: Incoming threat warnings intercepted by the child's on-device classifiers with contextual snippets.
- **Remote Lock Action**: Sends an instant MQTT command to lock the child's phone or computer screen remotely.

## Getting Started

```bash
# 1. Fetch Flutter dependencies
flutter pub get

# 2. Run in debug mode on connected device or simulator
flutter run
```
