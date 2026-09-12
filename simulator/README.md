# ChildGuard AI: End-to-End Simulation & Test Suite

The simulation suite (`e2e_simulation.py`) allows developers and stakeholders to validate the complete ChildGuard pipeline locally without requiring a physical Android device or external cloud services.

## What It Tests
1. **Safe Zone Telemetry**: Verifies that GPS breadcrumbs within authorized boundaries (School/Home) are logged without false alarms.
2. **Safe Zone Exit Detection**: Verifies that moving outside approved safe perimeters raises a `HIGH` severity `SAFE_ZONE_EXIT` alert.
3. **Danger Zone Penetration**: Verifies that entering hazardous areas (construction sites, industrial yards) triggers an immediate `CRITICAL` severity `DANGER_ZONE_BREACH` alarm.
4. **Chat Threat Sniffer**: Emulates incoming chat notifications (WhatsApp, Telegram, SMS) with predatory keywords and verifies that on-device classifiers trigger `CHAT_SECURITY_ALARM`.
5. **Emergency Remote Lock**: Simulates a parent dispatching a `LOCK_DEVICE` command and verifies immediate receipt and lock enforcement by the child device daemon.

## Running the Simulation

```bash
python simulator/e2e_simulation.py
```
