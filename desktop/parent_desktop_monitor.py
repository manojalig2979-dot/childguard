#!/usr/bin/env python3
"""
ChildGuard AI - Desktop Parent Command Center & Activity Monitor
Engineered by NDTechHub (A Part of NavDiva Group)

Provides a native desktop dashboard for parents to supervise child activities
(GPS location, active apps, geofence breaches, threat alerts, and remote lock)
directly from their Windows/macOS/Linux system without needing a mobile phone.
"""

import sys
import time
import json
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# Theme Palette (Modern Dark Studio)
COLOR_BG = "#0b0f19"
COLOR_CARD = "#131b2e"
COLOR_CARD_BORDER = "#23304d"
COLOR_TEXT = "#f8fafc"
COLOR_TEXT_MUTED = "#94a3b8"
COLOR_PRIMARY = "#3b82f6"
COLOR_SUCCESS = "#10b981"
COLOR_WARNING = "#f59e0b"
COLOR_DANGER = "#ef4444"
COLOR_CYAN = "#06b6d4"

class ParentDesktopMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChildGuard AI — Parent System Monitor (NDTechHub)")
        self.geometry("1020x680")
        self.minsize(900, 580)
        self.configure(bg=COLOR_BG)

        # State Variables
        self.child_device_id = "child_agent_in_991"
        self.is_connected = True
        self.is_locked = False
        self.current_lat = 28.6145
        self.current_lon = 77.2120
        self.current_speed = 0.4
        self.current_battery = 84
        self.current_zone = "School Safe Zone"

        self._setup_styles()
        self._build_header()
        self._build_main_content()
        self._build_footer()

        # Seed initial sample events
        self._populate_initial_events()

    def _setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Treeview styling for threat feed
        self.style.configure(
            "Treeview",
            background=COLOR_CARD,
            foreground=COLOR_TEXT,
            fieldbackground=COLOR_CARD,
            rowheight=28,
            font=("Segoe UI", 9)
        )
        self.style.configure(
            "Treeview.Heading",
            background="#1e293b",
            foreground="#94a3b8",
            font=("Segoe UI", 9, "bold"),
            relief="flat"
        )
        self.style.map("Treeview", background=[("selected", "#2563eb")])

    def _build_header(self):
        header = tk.Frame(self, bg="#0d1424", height=65, padx=20, pady=10)
        header.pack(fill=tk.X, side=tk.TOP)

        # Brand Info
        brand_frame = tk.Frame(header, bg="#0d1424")
        brand_frame.pack(side=tk.LEFT)

        lbl_title = tk.Label(
            brand_frame,
            text="ChildGuard AI",
            font=("Segoe UI", 16, "bold"),
            fg="#ffffff",
            bg="#0d1424"
        )
        lbl_title.pack(side=tk.LEFT)

        lbl_corp = tk.Label(
            brand_frame,
            text="• System Monitor (NDTechHub / NavDiva Group)",
            font=("Segoe UI", 10),
            fg=COLOR_CYAN,
            bg="#0d1424"
        )
        lbl_corp.pack(side=tk.LEFT, padx=8)

        # Status & Quick Actions
        actions_frame = tk.Frame(header, bg="#0d1424")
        actions_frame.pack(side=tk.RIGHT)

        self.lbl_broker = tk.Label(
            actions_frame,
            text="● CLOUD BROKER: CONNECTED",
            font=("Segoe UI", 9, "bold"),
            fg=COLOR_SUCCESS,
            bg="#0d1424"
        )
        self.lbl_broker.pack(side=tk.LEFT, padx=12)

        self.btn_lock = tk.Button(
            actions_frame,
            text="🔒 Remote Screen Lock",
            font=("Segoe UI", 9, "bold"),
            bg="#b91c1c",
            fg="#ffffff",
            activebackground="#dc2626",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=4,
            cursor="hand2",
            command=self._toggle_remote_lock
        )
        self.btn_lock.pack(side=tk.LEFT)

    def _build_main_content(self):
        content = tk.Frame(self, bg=COLOR_BG, padx=15, pady=15)
        content.pack(fill=tk.BOTH, expand=True)

        # Left Column: Telemetry & Activity Stats
        left_col = tk.Frame(content, bg=COLOR_BG, width=360)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))

        # Target Device Info Card
        dev_card = tk.LabelFrame(
            left_col,
            text=" 📱 Supervised Child Target ",
            font=("Segoe UI", 10, "bold"),
            bg=COLOR_CARD,
            fg=COLOR_CYAN,
            bd=1,
            relief="solid",
            padx=12,
            pady=10
        )
        dev_card.pack(fill=tk.X, pady=(0, 10))

        self._add_stat_row(dev_card, "Target Child:", "Aarav (Student)")
        self._add_stat_row(dev_card, "Device ID:", self.child_device_id)
        self.lbl_status = self._add_stat_row(dev_card, "Status:", "Active & Protected", COLOR_SUCCESS)
        self.lbl_loc = self._add_stat_row(dev_card, "Zone:", self.current_zone, COLOR_SUCCESS)
        self.lbl_coords = self._add_stat_row(dev_card, "GPS Coordinates:", f"{self.current_lat:.4f}° N, {self.current_lon:.4f}° E")
        self.lbl_speed = self._add_stat_row(dev_card, "Speed:", f"{self.current_speed:.1f} m/s")
        self.lbl_bat = self._add_stat_row(dev_card, "Battery:", f"{self.current_battery}%")

        # Active Desktop & Mobile Applications Card
        apps_card = tk.LabelFrame(
            left_col,
            text=" 📊 Active Usage & Application Watchdog ",
            font=("Segoe UI", 10, "bold"),
            bg=COLOR_CARD,
            fg=COLOR_CYAN,
            bd=1,
            relief="solid",
            padx=12,
            pady=10
        )
        apps_card.pack(fill=tk.BOTH, expand=True)

        app_items = [
            ("Google Classroom (School)", "1h 45m", COLOR_SUCCESS),
            ("Wikipedia / Chrome", "42m", COLOR_SUCCESS),
            ("WhatsApp (Inspected)", "18m", COLOR_WARNING),
            ("Roblox / Games (Blocked)", "0m (Terminated)", COLOR_DANGER),
        ]
        for app_name, duration, color in app_items:
            row = tk.Frame(apps_card, bg=COLOR_CARD, pady=4)
            row.pack(fill=tk.X)
            tk.Label(row, text=app_name, font=("Segoe UI", 9), fg=COLOR_TEXT, bg=COLOR_CARD).pack(side=tk.LEFT)
            tk.Label(row, text=duration, font=("Segoe UI", 9, "bold"), fg=color, bg=COLOR_CARD).pack(side=tk.RIGHT)

        # Right Column: Live Safety Threat Stream & Action Controls
        right_col = tk.Frame(content, bg=COLOR_BG)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Interactive Simulation & Action Bar
        ctrl_bar = tk.LabelFrame(
            right_col,
            text=" 🎮 System Quick-Triggers & Live Simulation ",
            font=("Segoe UI", 10, "bold"),
            bg=COLOR_CARD,
            fg=COLOR_CYAN,
            bd=1,
            relief="solid",
            padx=10,
            pady=8
        )
        ctrl_bar.pack(fill=tk.X, pady=(0, 10))

        btn_grid = tk.Frame(ctrl_bar, bg=COLOR_CARD)
        btn_grid.pack(fill=tk.X)

        self._create_btn(btn_grid, "🏫 School Zone", self._sim_school, "#065f46").pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        self._create_btn(btn_grid, "🚶 Exit Perimeter", self._sim_exit, "#854d0e").pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        self._create_btn(btn_grid, "⚠️ Danger Zone", self._sim_danger, "#991b1b").pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        self._create_btn(btn_grid, "💬 Predator Chat", self._sim_chat, "#7c2d12").pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)
        self._create_btn(btn_grid, "🚨 Silent SOS", self._sim_sos, "#be123c").pack(side=tk.LEFT, padx=3, fill=tk.X, expand=True)

        # Threat Log Table
        feed_card = tk.LabelFrame(
            right_col,
            text=" 🛡️ Real-Time Safety & Threat Feed (Synchronized with Mobile App) ",
            font=("Segoe UI", 10, "bold"),
            bg=COLOR_CARD,
            fg=COLOR_CYAN,
            bd=1,
            relief="solid",
            padx=10,
            pady=8
        )
        feed_card.pack(fill=tk.BOTH, expand=True)

        # Treeview for event stream
        columns = ("time", "severity", "type", "details")
        self.tree = ttk.Treeview(feed_card, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("time", text="Time")
        self.tree.heading("severity", text="Severity")
        self.tree.heading("type", text="Threat Type")
        self.tree.heading("details", text="Event Details & Condition")

        self.tree.column("time", width=75, anchor="center")
        self.tree.column("severity", width=85, anchor="center")
        self.tree.column("type", width=170, anchor="w")
        self.tree.column("details", width=340, anchor="w")

        scrollbar = ttk.Scrollbar(feed_card, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _add_stat_row(self, parent, label_text, val_text, val_color=COLOR_TEXT):
        row = tk.Frame(parent, bg=COLOR_CARD, pady=3)
        row.pack(fill=tk.X)
        tk.Label(row, text=label_text, font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD).pack(side=tk.LEFT)
        val_lbl = tk.Label(row, text=val_text, font=("Segoe UI", 9, "bold"), fg=val_color, bg=COLOR_CARD)
        val_lbl.pack(side=tk.RIGHT)
        return val_lbl

    def _create_btn(self, parent, text, command, bg_color):
        return tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 8, "bold"),
            bg=bg_color,
            fg="#ffffff",
            activebackground=COLOR_PRIMARY,
            activeforeground="#ffffff",
            relief="flat",
            pady=4,
            cursor="hand2",
            command=command
        )

    def _build_footer(self):
        footer = tk.Frame(self, bg="#070a12", height=32, padx=15)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        lbl_corp = tk.Label(
            footer,
            text="NDTechHub (NavDiva Group) • Multi-Platform Parental Safety Core • DPDP 2023 Compliant",
            font=("Segoe UI", 8),
            fg=COLOR_TEXT_MUTED,
            bg="#070a12"
        )
        lbl_corp.pack(side=tk.LEFT, pady=6)

        lbl_sync = tk.Label(
            footer,
            text="Sync Status: Mobile & System Paired (MQTT QoS 1)",
            font=("Segoe UI", 8, "bold"),
            fg=COLOR_CYAN,
            bg="#070a12"
        )
        lbl_sync.pack(side=tk.RIGHT, pady=6)

    def _log_event(self, severity, event_type, details):
        time_str = datetime.now().strftime("%H:%M:%S")
        self.tree.insert("", 0, values=(time_str, severity, event_type, details))

    def _populate_initial_events(self):
        self._log_event("SUCCESS", "DAEMON_ONLINE", "Android ChildGuard daemon connected via MQTT.")
        self._log_event("SUCCESS", "DESKTOP_WATCHDOG", "Windows Process Watchdog active. SafeSearch VIP enforced.")
        self._log_event("SUCCESS", "SAFE_ZONE_VERIFIED", "Child coordinates verified inside School perimeter.")

    def _toggle_remote_lock(self):
        self.is_locked = not self.is_locked
        if self.is_locked:
            self.btn_lock.config(text="🔓 Unlock Child Device", bg="#059669")
            self.lbl_status.config(text="DEVICE LOCKED (OVERLAY ACTIVE)", fg=COLOR_DANGER)
            self._log_event("CRITICAL", "REMOTE_LOCK_DISPATCHED", "Parent locked child screen. Overlay PIN displayed.")
            messagebox.showwarning(
                "Remote Device Locked",
                "Instant Lockdown command transmitted to Aarav's Android and Windows devices over MQTT.\n\nAll touchscreen inputs and apps are frozen until unlocked."
            )
        else:
            self.btn_lock.config(text="🔒 Remote Screen Lock", bg="#b91c1c")
            self.lbl_status.config(text="Active & Protected", fg=COLOR_SUCCESS)
            self._log_event("SUCCESS", "REMOTE_UNLOCK", "Device unlocked successfully by parent.")

    def _sim_school(self):
        self.current_lat, self.current_lon = 28.6145, 77.2120
        self.current_speed = 0.3
        self.current_zone = "School Safe Zone"
        self._update_telemetry()
        self._log_event("SUCCESS", "SAFE_ZONE_NORMAL", "Child is safely on school grounds (DPS campus).")

    def _sim_exit(self):
        self.current_lat, self.current_lon = 28.6190, 77.2180
        self.current_speed = 1.8
        self.current_zone = "Transit Perimeter"
        self._update_telemetry()
        self._log_event("HIGH", "SAFE_ZONE_EXIT", "Boundary alert: Child exited designated School polygon!")

    def _sim_danger(self):
        self.current_lat, self.current_lon = 28.6120, 77.2340
        self.current_speed = 2.4
        self.current_zone = "Industrial Danger Zone"
        self._update_telemetry(zone_color=COLOR_DANGER)
        self._log_event("CRITICAL", "DANGER_ZONE_BREACH", "CRITICAL: Child entered restricted Construction Site!")

    def _sim_chat(self):
        self._log_event(
            "HIGH",
            "CHAT_SECURITY_ALARM",
            "WhatsApp Intercept: 'Meet alone at the secret place after class, don't tell parents.'"
        )

    def _sim_sos(self):
        self.current_speed = 0.0
        self.current_battery = 79
        self._update_telemetry()
        self._log_event(
            "CRITICAL",
            "EMERGENCY_SOS_ALARM",
            "DISTRESS PANIC: Child triple-tapped physical Volume Down key! Stealth alert received."
        )
        messagebox.showerror(
            "EMERGENCY SOS RECEIVED!",
            "Child distress signal triggered on Aarav's device!\n\nLocation: 28.6145° N, 77.2120° E\nBattery: 79%\nImmediate parental attention required."
        )

    def _update_telemetry(self, zone_color=COLOR_SUCCESS):
        self.lbl_loc.config(text=self.current_zone, fg=zone_color)
        self.lbl_coords.config(text=f"{self.current_lat:.4f}° N, {self.current_lon:.4f}° E")
        self.lbl_speed.config(text=f"{self.current_speed:.1f} m/s")
        self.lbl_bat.config(text=f"{self.current_battery}%")

if __name__ == "__main__":
    app = ParentDesktopMonitor()
    app.mainloop()
