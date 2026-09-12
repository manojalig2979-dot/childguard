#!/usr/bin/env python3
"""
ChildGuard AI - Full Parent Desktop Command Center & Surveillance Station
Engineered by NDTechHub (A Part of NavDiva Group)

Comprehensive monitoring application for parents to supervise:
1. Live GPS Location, Movement Radar & Polygonal Geofences
2. Social Media & Chat Inspector (WhatsApp, Instagram, Snapchat, YouTube Shorts)
3. Active Windows & Android Application Usage + Process Watchdog
4. AI Behavioral Wellness & Weekly Safety Scorecard
5. Emergency Distress SOS & Remote Lockdown Controls
"""

import sys
import os
import time
import math
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# Theme Palette (Modern Dark Studio & High-Tech Accents)
COLOR_BG = "#080c14"
COLOR_HEADER = "#0d1322"
COLOR_CARD = "#121a2d"
COLOR_CARD_HOVER = "#18233c"
COLOR_BORDER = "#1f2e4d"
COLOR_TEXT = "#f8fafc"
COLOR_TEXT_MUTED = "#94a3b8"
COLOR_PRIMARY = "#3b82f6"
COLOR_CYAN = "#06b6d4"
COLOR_SUCCESS = "#10b981"
COLOR_WARNING = "#f59e0b"
COLOR_DANGER = "#ef4444"
COLOR_PURPLE = "#a855f7"

class FullParentDesktopMonitor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ChildGuard AI — Full Parent Supervision Station (NDTechHub)")
        self.geometry("1160x780")
        self.minsize(1040, 680)
        self.configure(bg=COLOR_BG)

        # Child Target State
        self.child_name = "Aarav"
        self.device_id = "child_agent_in_991"
        self.is_locked = False
        self.lat = 28.6145
        self.lon = 77.2120
        self.speed = 0.4
        self.battery = 84
        self.current_zone = "School Safe Zone (DPS Campus)"
        self.radar_angle = 0
        self.child_canvas_x = 240
        self.child_canvas_y = 190

        self._setup_styles()
        self._build_header()
        self._build_notebook()
        self._build_footer()

        # Start animation loop for the live radar
        self._animate_radar()

    def _setup_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Custom Notebook Tabs
        self.style.configure(
            "TNotebook",
            background=COLOR_BG,
            borderwidth=0
        )
        self.style.configure(
            "TNotebook.Tab",
            background="#0d1424",
            foreground=COLOR_TEXT_MUTED,
            font=("Segoe UI", 10, "bold"),
            padding=[16, 8],
            borderwidth=0
        )
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", COLOR_PRIMARY), ("active", "#1e293b")],
            foreground=[("selected", "#ffffff"), ("active", "#ffffff")]
        )

        # Treeview Styles
        self.style.configure(
            "Treeview",
            background=COLOR_CARD,
            foreground=COLOR_TEXT,
            fieldbackground=COLOR_CARD,
            rowheight=30,
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
        header = tk.Frame(self, bg=COLOR_HEADER, height=72, padx=22, pady=12)
        header.pack(fill=tk.X, side=tk.TOP)

        # Brand Info
        brand_frame = tk.Frame(header, bg=COLOR_HEADER)
        brand_frame.pack(side=tk.LEFT)

        lbl_icon = tk.Label(
            brand_frame,
            text="🛡️",
            font=("Segoe UI", 18),
            bg=COLOR_HEADER
        )
        lbl_icon.pack(side=tk.LEFT, padx=(0, 10))

        title_box = tk.Frame(brand_frame, bg=COLOR_HEADER)
        title_box.pack(side=tk.LEFT)

        lbl_title = tk.Label(
            title_box,
            text="ChildGuard AI",
            font=("Segoe UI", 15, "bold"),
            fg="#ffffff",
            bg=COLOR_HEADER
        )
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(
            title_box,
            text="Central Parental Command & Surveillance Workstation • NDTechHub (NavDiva Group)",
            font=("Segoe UI", 8),
            fg=COLOR_CYAN,
            bg=COLOR_HEADER
        )
        lbl_sub.pack(anchor="w")

        # Telemetry Quick-Bar & Actions
        right_box = tk.Frame(header, bg=COLOR_HEADER)
        right_box.pack(side=tk.RIGHT)

        self.lbl_target = tk.Label(
            right_box,
            text=f"Target: {self.child_name} ({self.device_id})",
            font=("Segoe UI", 9, "bold"),
            fg="#ffffff",
            bg="#162035",
            padx=10,
            pady=4,
            relief="solid",
            bd=1
        )
        self.lbl_target.pack(side=tk.LEFT, padx=8)

        self.lbl_cloud_status = tk.Label(
            right_box,
            text="● CLOUD SYNC: 42ms",
            font=("Segoe UI", 9, "bold"),
            fg=COLOR_SUCCESS,
            bg=COLOR_HEADER
        )
        self.lbl_cloud_status.pack(side=tk.LEFT, padx=10)

        self.btn_emergency_lock = tk.Button(
            right_box,
            text="🔒 Remote Screen Lock",
            font=("Segoe UI", 9, "bold"),
            bg="#dc2626",
            fg="#ffffff",
            activebackground="#b91c1c",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self._toggle_lock
        )
        self.btn_emergency_lock.pack(side=tk.LEFT, padx=5)

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)

        # 5 Core Supervision Tabs
        self.tab_map = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_social = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_apps = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_ai = tk.Frame(self.notebook, bg=COLOR_BG)
        self.tab_emergency = tk.Frame(self.notebook, bg=COLOR_BG)

        self.notebook.add(self.tab_map, text="  📍 Live Location & Geofencing  ")
        self.notebook.add(self.tab_social, text="  💬 Social Media & Chat Inspector  ")
        self.notebook.add(self.tab_apps, text="  📊 App Usage & PC Watchdog  ")
        self.notebook.add(self.tab_ai, text="  🧠 AI Safety Scorecard  ")
        self.notebook.add(self.tab_emergency, text="  🚨 SOS Panic & Remote Controls  ")

        self._init_tab_map()
        self._init_tab_social()
        self._init_tab_apps()
        self._init_tab_ai()
        self._init_tab_emergency()

    # =========================================================================
    # TAB 1: LIVE LOCATION & GEOFENCING RADAR
    # =========================================================================
    def _init_tab_map(self):
        container = tk.Frame(self.tab_map, bg=COLOR_BG, padx=10, pady=10)
        container.pack(fill=tk.BOTH, expand=True)

        # Left Canvas Map (Spatial Tracking)
        left_box = tk.Frame(container, bg=COLOR_CARD, bd=1, relief="solid")
        left_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        map_hdr = tk.Frame(left_box, bg="#162238", padx=12, pady=8)
        map_hdr.pack(fill=tk.X)

        tk.Label(
            map_hdr,
            text="🗺️ High-Resolution Spatial Geofence Canvas (PostGIS ST_Contains Engine)",
            font=("Segoe UI", 10, "bold"),
            fg="#ffffff",
            bg="#162238"
        ).pack(side=tk.LEFT)

        self.lbl_canvas_coords = tk.Label(
            map_hdr,
            text=f"{self.lat:.4f}° N, {self.lon:.4f}° E • ±3m accuracy",
            font=("Segoe UI", 9, "bold"),
            fg=COLOR_CYAN,
            bg="#162238"
        )
        self.lbl_canvas_coords.pack(side=tk.RIGHT)

        # Visual Radar Map Canvas
        self.canvas = tk.Canvas(left_box, bg="#070c16", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self._draw_map_zones()

        # Legend Bar
        legend = tk.Frame(left_box, bg="#0d1424", padx=12, pady=6)
        legend.pack(fill=tk.X)

        self._add_legend_item(legend, "#10b981", "School Safe Perimeter")
        self._add_legend_item(legend, "#3b82f6", "Home Safe Perimeter")
        self._add_legend_item(legend, "#ef4444", "Industrial Danger Zone")
        self._add_legend_item(legend, "#06b6d4", "Live Child GPS Pin")

        # Right Telemetry Deck & Scenario Triggers
        right_box = tk.Frame(container, bg=COLOR_BG, width=340)
        right_box.pack(side=tk.RIGHT, fill=tk.BOTH)

        # Telemetry Card
        telem_card = tk.LabelFrame(
            right_box,
            text=" 📡 Live Telemetry & Fused Sensor Metrics ",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_CARD,
            fg=COLOR_CYAN,
            bd=1,
            relief="solid",
            padx=12,
            pady=10
        )
        telem_card.pack(fill=tk.X, pady=(0, 10))

        self.val_zone = self._add_stat(telem_card, "Current Location:", self.current_zone, COLOR_SUCCESS)
        self.val_speed = self._add_stat(telem_card, "Velocity / Movement:", f"{self.speed} m/s (Walking)")
        self.val_battery = self._add_stat(telem_card, "Battery & Health:", f"{self.battery}% (Good)")
        self.val_signal = self._add_stat(telem_card, "Network Cell/WiFi:", "Airtel 5G (Excellent)")
        self.val_admin = self._add_stat(telem_card, "Anti-Uninstall Shield:", "ACTIVE (Device Admin Locked)", COLOR_SUCCESS)

        # Simulation Trigger Buttons
        sim_card = tk.LabelFrame(
            right_box,
            text=" 🎯 Scenario Simulation & Field Testing ",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_CARD,
            fg=COLOR_CYAN,
            bd=1,
            relief="solid",
            padx=10,
            pady=10
        )
        sim_card.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            sim_card,
            text="Click below to test real-time perimeter alarms:",
            font=("Segoe UI", 8),
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD
        ).pack(anchor="w", pady=(0, 6))

        self._btn(sim_card, "🏫 Teleport: Inside School Zone (Safe)", self._go_school, "#065f46").pack(fill=tk.X, pady=3)
        self._btn(sim_card, "🚶 Simulate: Exit School Perimeter (Warning)", self._go_exit, "#854d0e").pack(fill=tk.X, pady=3)
        self._btn(sim_card, "⚠️ Simulate: Danger Zone Breach (Critical)", self._go_danger, "#991b1b").pack(fill=tk.X, pady=3)
        self._btn(sim_card, "🏡 Teleport: Home Safe Zone (Safe)", self._go_home, "#1e40af").pack(fill=tk.X, pady=3)

    def _draw_map_zones(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 600
        h = self.canvas.winfo_height() or 400

        # Draw dark grid coordinates
        for x in range(0, w, 50):
            self.canvas.create_line(x, 0, x, h, fill="#111c30", width=1)
        for y in range(0, h, 50):
            self.canvas.create_line(0, y, w, y, fill="#111c30", width=1)

        # 1. School Zone Polygon (Green)
        self.canvas.create_polygon(
            150, 110, 320, 110, 320, 270, 150, 270,
            fill="#064e3b", outline="#10b981", width=2
        )
        self.canvas.create_text(235, 130, text="🏫 Delhi Public School (Safe Zone)", fill="#34d399", font=("Segoe UI", 9, "bold"))

        # 2. Home Zone Polygon (Blue)
        self.canvas.create_polygon(
            380, 50, 520, 50, 520, 180, 380, 180,
            fill="#1e3a8a", outline="#3b82f6", width=2
        )
        self.canvas.create_text(450, 70, text="🏡 Home Perimeter", fill="#93c5fd", font=("Segoe UI", 9, "bold"))

        # 3. Danger Zone Polygon (Red Dashed)
        self.canvas.create_polygon(
            390, 230, 560, 230, 560, 360, 390, 360,
            fill="#450a0a", outline="#ef4444", width=2, dash=(6, 4)
        )
        self.canvas.create_text(475, 250, text="⚠️ Industrial Construction Site (Danger Zone)", fill="#fca5a5", font=("Segoe UI", 9, "bold"))

        # 4. Animated Child Marker
        x, y = self.child_canvas_x, self.child_canvas_y
        self.canvas.create_oval(x-18, y-18, x+18, y+18, outline=COLOR_CYAN, width=1, tags="radar_ring")
        self.canvas.create_oval(x-9, y-9, x+9, y+9, fill=COLOR_CYAN, outline="#ffffff", width=2, tags="child_pin")
        self.canvas.create_text(x, y-24, text=f"{self.child_name} (Active)", fill="#ffffff", font=("Segoe UI", 9, "bold"), tags="child_lbl")

    def _animate_radar(self):
        self.radar_angle = (self.radar_angle + 6) % 360
        rad = math.radians(self.radar_angle)
        r = 30

        # Animate glowing beacon sweep
        x, y = self.child_canvas_x, self.child_canvas_y
        px = x + r * math.cos(rad)
        py = y + r * math.sin(rad)

        self.canvas.delete("radar_beam")
        self.canvas.create_line(x, y, px, py, fill="#38bdf8", width=2, tags="radar_beam")
        self.after(50, self._animate_radar)

    def _add_legend_item(self, parent, color, text):
        box = tk.Frame(parent, bg="#0d1424")
        box.pack(side=tk.LEFT, padx=12)
        dot = tk.Label(box, text="■", fg=color, bg="#0d1424", font=("Segoe UI", 12))
        dot.pack(side=tk.LEFT)
        lbl = tk.Label(box, text=text, fg=COLOR_TEXT_MUTED, bg="#0d1424", font=("Segoe UI", 8))
        lbl.pack(side=tk.LEFT, padx=4)

    # =========================================================================
    # TAB 2: SOCIAL MEDIA & CHAT PREDATOR INSPECTOR
    # =========================================================================
    def _init_tab_social(self):
        container = tk.Frame(self.tab_social, bg=COLOR_BG, padx=12, pady=12)
        container.pack(fill=tk.BOTH, expand=True)

        top_info = tk.Frame(container, bg="#162238", padx=14, pady=8, bd=1, relief="solid")
        top_info.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            top_info,
            text="💬 On-Device Notification Sniffer & Accessibility Content Inspector",
            font=("Segoe UI", 10, "bold"),
            fg="#ffffff",
            bg="#162238"
        ).pack(side=tk.LEFT)

        tk.Label(
            top_info,
            text="Privacy Standard: DPDP 2023 Compliant (Evaluated On-Device • Encrypted Alerts)",
            font=("Segoe UI", 8),
            fg=COLOR_SUCCESS,
            bg="#162238"
        ).pack(side=tk.RIGHT)

        # 4 Social Channels Grid
        grid_frame = tk.Frame(container, bg=COLOR_BG)
        grid_frame.pack(fill=tk.BOTH, expand=True)

        # Channel 1: WhatsApp Predator Sniffer
        c1 = self._make_channel_card(grid_frame, "📱 WhatsApp Messenger", "Active Sniffer", COLOR_SUCCESS)
        c1.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self._add_threat_entry(
            c1,
            "CRITICAL THREAT INTERCEPTED",
            "Unknown Contact (+91 99999 12345)",
            "\"Hey, meet alone at the secret place after class, don't tell your parents.\"",
            "Keywords: [meet alone, secret place, don't tell]",
            COLOR_DANGER
        )
        self._add_threat_entry(
            c1,
            "SAFE CONVERSATION",
            "Mom (+91 98111 55555)",
            "\"I will pick you up at 3:30 PM from school gate.\"",
            "Normal family chat • Confidence: 99.8%",
            COLOR_SUCCESS
        )

        # Channel 2: Instagram Direct & Follower Scanner
        c2 = self._make_channel_card(grid_frame, "📷 Instagram Direct", "Active Filter", COLOR_PURPLE)
        c2.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)
        self._add_threat_entry(
            c2,
            "SUSPICIOUS FOLLOWER REQUEST",
            "Account: @stranger_club_x9",
            "Adult account attempted to send direct message to Aarav.",
            "Blocked automatically by ChildGuard Protection",
            COLOR_WARNING
        )
        self._add_threat_entry(
            c2,
            "CYBERBULLYING SCANNER",
            "Classmate Group Chat",
            "\"Let's study together for Monday's math exam.\"",
            "No harmful or toxic speech detected",
            COLOR_SUCCESS
        )

        # Channel 3: Snapchat & Disappearing Messages
        c3 = self._make_channel_card(grid_frame, "👻 Snapchat Sentinel", "Active Monitor", COLOR_WARNING)
        c3.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        self._add_threat_entry(
            c3,
            "GHOST MODE ENFORCED",
            "Snap Map Location Sharing",
            "External location broadcasting was restricted to preserve child anonymity.",
            "Rule: LocationPrivacyEnforced == TRUE",
            COLOR_CYAN
        )
        self._add_threat_entry(
            c3,
            "IMAGE VAULT PROTECTION",
            "Incoming Snap Intercept",
            "Safe image classification verified. No explicit content detected.",
            "Local neural scanner pass rate: 100%",
            COLOR_SUCCESS
        )

        # Channel 4: YouTube Shorts & Reels Auto-Skipper
        c4 = self._make_channel_card(grid_frame, "🎬 YouTube Shorts / Reels", "Auto-Skip Engine", "#e11d48")
        c4.grid(row=1, column=1, sticky="nsew", padx=6, pady=6)
        self._add_threat_entry(
            c4,
            "INAPPROPRIATE REEL AUTO-SKIPPED",
            "Accessibility Service Action",
            "Detected adult/violent video content on YouTube Shorts. Swiped next in 120ms.",
            "Category: Violence/Explicit • Confidence: 97.4%",
            COLOR_DANGER
        )
        self._add_threat_entry(
            c4,
            "EDUCATIONAL FEED",
            "Channel: Khan Academy Physics",
            "Whitelisted learning video. Allowed without screen timeout restriction.",
            "Category: Productive Learning",
            COLOR_SUCCESS
        )

        grid_frame.columnconfigure(0, weight=1)
        grid_frame.columnconfigure(1, weight=1)
        grid_frame.rowconfigure(0, weight=1)
        grid_frame.rowconfigure(1, weight=1)

    def _make_channel_card(self, parent, title, status_text, status_color):
        card = tk.LabelFrame(
            parent,
            text=f" {title} [{status_text}] ",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_CARD,
            fg=status_color,
            bd=1,
            relief="solid",
            padx=10,
            pady=8
        )
        return card

    def _add_threat_entry(self, parent, badge, sender, msg, rule, color):
        frame = tk.Frame(parent, bg="#0d1424", bd=1, relief="solid", padx=8, pady=6)
        frame.pack(fill=tk.X, pady=4)

        top = tk.Frame(frame, bg="#0d1424")
        top.pack(fill=tk.X)
        tk.Label(top, text=badge, font=("Segoe UI", 8, "bold"), fg=color, bg="#0d1424").pack(side=tk.LEFT)
        tk.Label(top, text=sender, font=("Segoe UI", 8), fg=COLOR_TEXT_MUTED, bg="#0d1424").pack(side=tk.RIGHT)

        tk.Label(frame, text=msg, font=("Segoe UI", 8, "italic"), fg="#ffffff", bg="#0d1424", wraplength=480, justify="left").pack(anchor="w", pady=2)
        tk.Label(frame, text=rule, font=("Consolas", 7), fg=COLOR_CYAN, bg="#0d1424").pack(anchor="w")

    # =========================================================================
    # TAB 3: ACTIVE APPS & WINDOWS DESKTOP WATCHDOG
    # =========================================================================
    def _init_tab_apps(self):
        container = tk.Frame(self.tab_apps, bg=COLOR_BG, padx=12, pady=12)
        container.pack(fill=tk.BOTH, expand=True)

        # Top App Watchdog Summary
        top_bar = tk.Frame(container, bg="#162238", padx=14, pady=8, bd=1, relief="solid")
        top_bar.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            top_bar,
            text="🖥️ Windows PC & Mobile Application Watchdog (Native Win32 TerminateProcess Hook)",
            font=("Segoe UI", 10, "bold"),
            fg="#ffffff",
            bg="#162238"
        ).pack(side=tk.LEFT)

        tk.Label(
            top_bar,
            text="SafeSearch VIP Routing: ACTIVE • Loopback Sinkhole (127.0.0.1): 10,480 Domains",
            font=("Segoe UI", 8, "bold"),
            fg=COLOR_CYAN,
            bg="#162238"
        ).pack(side=tk.RIGHT)

        # Split into Apps Table and Process Log
        split_frame = tk.Frame(container, bg=COLOR_BG)
        split_frame.pack(fill=tk.BOTH, expand=True)

        # Left: Application Screen Time Breakdown
        app_box = tk.LabelFrame(
            split_frame,
            text=" 📊 Daily Application Usage Breakdown ",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_CARD,
            fg=COLOR_CYAN,
            bd=1,
            relief="solid",
            padx=10,
            pady=8
        )
        app_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        apps = [
            ("Google Classroom (Assignments)", "2 hrs 15 mins", "62%", COLOR_SUCCESS),
            ("Chrome (Wikipedia & Chemistry)", "1 hr 10 mins", "24%", COLOR_SUCCESS),
            ("WhatsApp (Approved Family Contacts)", "25 mins", "8%", COLOR_WARNING),
            ("YouTube (Educational Videos)", "20 mins", "6%", COLOR_WARNING),
            ("Roblox / Minecraft (Games)", "0 mins (BLOCKED)", "0%", COLOR_DANGER),
            ("Steam Client", "0 mins (BLOCKED)", "0%", COLOR_DANGER),
        ]

        for name, duration, pct, color in apps:
            row = tk.Frame(app_box, bg="#0d1424", padx=8, pady=6)
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=name, font=("Segoe UI", 9, "bold"), fg="#ffffff", bg="#0d1424").pack(side=tk.LEFT)
            tk.Label(row, text=f"{duration} ({pct})", font=("Segoe UI", 9, "bold"), fg=color, bg="#0d1424").pack(side=tk.RIGHT)

        # Right: Real-Time Process Watchdog Logs
        proc_box = tk.LabelFrame(
            split_frame,
            text=" 🛡️ Real-Time Process Watchdog Action Log ",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_CARD,
            fg=COLOR_CYAN,
            bd=1,
            relief="solid",
            padx=10,
            pady=8
        )
        proc_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        cols = ("time", "action", "process", "detail")
        self.proc_tree = ttk.Treeview(proc_box, columns=cols, show="headings")
        self.proc_tree.heading("time", text="Time")
        self.proc_tree.heading("action", text="Action")
        self.proc_tree.heading("process", text="Process Name")
        self.proc_tree.heading("detail", text="Enforcement Details")

        self.proc_tree.column("time", width=75, anchor="center")
        self.proc_tree.column("action", width=95, anchor="center")
        self.proc_tree.column("process", width=110, anchor="w")
        self.proc_tree.column("detail", width=220, anchor="w")

        self.proc_tree.pack(fill=tk.BOTH, expand=True)

        self._add_proc_log("15:42:10", "TERMINATED", "RobloxPlayerBeta.exe", "Killed by Win32 TerminateProcess API")
        self._add_proc_log("15:40:05", "REDIRECTED", "google.com/search", "Enforced forcesafesearch.google.com VIP")
        self._add_proc_log("15:38:22", "SINKHOLED", "adult-gambling-site.com", "Resolved to loopback null 127.0.0.1")
        self._add_proc_log("15:35:10", "ALLOWED", "Code.exe (VS Code)", "Whitelisted educational software")
        self._add_proc_log("15:30:00", "ACTIVE", "chrome.exe", "Foreground Window: Google Classroom")

    def _add_proc_log(self, t, act, proc, det):
        self.proc_tree.insert("", "end", values=(t, act, proc, det))

    # =========================================================================
    # TAB 4: AI BEHAVIORAL WELLNESS & SAFETY SCORECARD
    # =========================================================================
    def _init_tab_ai(self):
        container = tk.Frame(self.tab_ai, bg=COLOR_BG, padx=14, pady=14)
        container.pack(fill=tk.BOTH, expand=True)

        # Header
        top = tk.Frame(container, bg="#162238", padx=14, pady=8, bd=1, relief="solid")
        top.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            top,
            text="🧠 Autonomous Behavioral Safety Engine & Digital Wellness Report",
            font=("Segoe UI", 10, "bold"),
            fg="#ffffff",
            bg="#162238"
        ).pack(side=tk.LEFT)

        tk.Label(
            top,
            text="Analysis Window: Past 7 Days (Updated 10m ago)",
            font=("Segoe UI", 8),
            fg=COLOR_CYAN,
            bg="#162238"
        ).pack(side=tk.RIGHT)

        # Cards Grid
        deck = tk.Frame(container, bg=COLOR_BG)
        deck.pack(fill=tk.BOTH, expand=True)

        # 1. Big Score Card
        score_card = tk.LabelFrame(
            deck,
            text=" Overall Safety Score ",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_CARD,
            fg=COLOR_CYAN,
            bd=1,
            relief="solid",
            padx=14,
            pady=14
        )
        score_card.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        tk.Label(score_card, text="94 / 100", font=("Segoe UI", 36, "bold"), fg=COLOR_SUCCESS, bg=COLOR_CARD).pack(pady=(10, 2))
        tk.Label(score_card, text="STATUS: EXCELLENT SAFETY COMPLIANCE", font=("Segoe UI", 10, "bold"), fg=COLOR_SUCCESS, bg=COLOR_CARD).pack()
        tk.Label(score_card, text="Aarav's activity reflects healthy learning habits, zero dangerous route deviations, and 100% adherence to study curfews.", font=("Segoe UI", 8), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD, wraplength=220, justify="center").pack(pady=10)

        # 2. Risk Metrics
        metrics_card = tk.LabelFrame(
            deck,
            text=" Behavioral Metric Breakdown ",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_CARD,
            fg=COLOR_CYAN,
            bd=1,
            relief="solid",
            padx=14,
            pady=10
        )
        metrics_card.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)

        m_items = [
            ("Geographic Adherence (Safe Routes):", "98.5% Safe", COLOR_SUCCESS),
            ("Predator & Stranger Exposure Risk:", "0.2% (1 Blocked Intercept)", COLOR_SUCCESS),
            ("Sleep & Bedtime Curfew Adherence:", "100% (No screens after 10 PM)", COLOR_SUCCESS),
            ("Gaming / Distraction Ratio:", "4.2% (Strictly within 30m limit)", COLOR_SUCCESS),
            ("Device Admin Anti-Tamper State:", "0 Bypass Attempts Detected", COLOR_SUCCESS)
        ]
        for label, val, c in m_items:
            r = tk.Frame(metrics_card, bg=COLOR_CARD, pady=4)
            r.pack(fill=tk.X)
            tk.Label(r, text=label, font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD).pack(side=tk.LEFT)
            tk.Label(r, text=val, font=("Segoe UI", 9, "bold"), fg=c, bg=COLOR_CARD).pack(side=tk.RIGHT)

        # 3. AI Safety Recommendations
        rec_card = tk.LabelFrame(
            deck,
            text=" 💡 AI Safety Recommendations & Action Items ",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_CARD,
            fg=COLOR_CYAN,
            bd=1,
            relief="solid",
            padx=14,
            pady=10
        )
        rec_card.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=6, pady=6)

        recs = [
            ("✅ Stranger Chat Defense:", "The predator sniffer successfully intercepted an unverified contact attempting to arrange a secret meetup. The phone number (+91 99999 12345) has been added to the parental blocklist."),
            ("✅ School Transit Precision:", "ChildGuard observed normal transit arrival at Delhi Public School at 07:48 AM, with no boundary exits during school hours."),
            ("💡 Guidance for Parents:", "Aarav is showing strong interest in computer science and mathematics tutorials. Consider extending weekend screen privileges for coding practice.")
        ]

        for title, desc in recs:
            b = tk.Frame(rec_card, bg="#0d1424", padx=10, pady=6, bd=1, relief="solid")
            b.pack(fill=tk.X, pady=3)
            tk.Label(b, text=title, font=("Segoe UI", 9, "bold"), fg=COLOR_CYAN, bg="#0d1424").pack(anchor="w")
            tk.Label(b, text=desc, font=("Segoe UI", 8), fg=COLOR_TEXT, bg="#0d1424", wraplength=950, justify="left").pack(anchor="w", pady=2)

        deck.columnconfigure(0, weight=1)
        deck.columnconfigure(1, weight=2)
        deck.rowconfigure(0, weight=1)
        deck.rowconfigure(1, weight=1)

    # =========================================================================
    # TAB 5: SOS PANIC & REMOTE CONTROLS
    # =========================================================================
    def _init_tab_emergency(self):
        container = tk.Frame(self.tab_emergency, bg=COLOR_BG, padx=14, pady=14)
        container.pack(fill=tk.BOTH, expand=True)

        top = tk.Frame(container, bg="#450a0a", padx=14, pady=8, bd=1, relief="solid")
        top.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            top,
            text="🚨 Emergency Command Center: Physical SOS Sequence & Remote Actions",
            font=("Segoe UI", 10, "bold"),
            fg="#ffffff",
            bg="#450a0a"
        ).pack(side=tk.LEFT)

        tk.Label(
            top,
            text="Encrypted Protocol: MQTT QoS 1 Instant Delivery (< 800ms)",
            font=("Segoe UI", 8),
            fg="#fca5a5",
            bg="#450a0a"
        ).pack(side=tk.RIGHT)

        # Control Panel & SOS Log
        deck = tk.Frame(container, bg=COLOR_BG)
        deck.pack(fill=tk.BOTH, expand=True)

        # Buttons Card
        btn_card = tk.LabelFrame(
            deck,
            text=" Emergency Remote Controls ",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_CARD,
            fg=COLOR_DANGER,
            bd=1,
            relief="solid",
            padx=14,
            pady=14
        )
        btn_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        tk.Label(
            btn_card,
            text="Instant actions to secure your child immediately:",
            font=("Segoe UI", 9),
            fg=COLOR_TEXT_MUTED,
            bg=COLOR_CARD
        ).pack(anchor="w", pady=(0, 10))

        self._btn(btn_card, "🔒 Freeze & Lock Child Device (PIN Required)", self._toggle_lock, "#991b1b").pack(fill=tk.X, pady=6)
        self._btn(btn_card, "📢 Sound Emergency Siren on Child Phone", self._sound_siren, "#b45309").pack(fill=tk.X, pady=6)
        self._btn(btn_card, "📍 Force High-Precision GPS Refresh", self._force_gps, "#0369a1").pack(fill=tk.X, pady=6)
        self._btn(btn_card, "🚨 Simulate Child Silent Volume SOS Trigger", self._sim_sos, "#be123c").pack(fill=tk.X, pady=6)

        # SOS History
        log_card = tk.LabelFrame(
            deck,
            text=" Hardware Volume Down SOS Emergency History ",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_CARD,
            fg=COLOR_CYAN,
            bd=1,
            relief="solid",
            padx=12,
            pady=12
        )
        log_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        cols = ("time", "trigger", "gps", "battery", "status")
        self.sos_tree = ttk.Treeview(log_card, columns=cols, show="headings")
        self.sos_tree.heading("time", text="Time")
        self.sos_tree.heading("trigger", text="Trigger Key")
        self.sos_tree.heading("gps", text="GPS Coordinates")
        self.sos_tree.heading("battery", text="Battery")
        self.sos_tree.heading("status", text="Response Status")

        self.sos_tree.column("time", width=75, anchor="center")
        self.sos_tree.column("trigger", width=140, anchor="w")
        self.sos_tree.column("gps", width=140, anchor="w")
        self.sos_tree.column("battery", width=65, anchor="center")
        self.sos_tree.column("status", width=120, anchor="w")

        self.sos_tree.pack(fill=tk.BOTH, expand=True)

        self._add_sos_entry("16:02:11", "TRIPLE_VOLUME_DOWN", "28.6145, 77.2120", "80%", "Parent Notified")
        self._add_sos_entry("Yesterday", "TEST_SEQUENCE_OK", "28.6220, 77.2230", "92%", "Verified Safe")

    def _add_sos_entry(self, t, trig, gps, bat, stat):
        self.sos_tree.insert("", "end", values=(t, trig, gps, bat, stat))

    # =========================================================================
    # FOOTER & ACTIONS
    # =========================================================================
    def _build_footer(self):
        footer = tk.Frame(self, bg="#070a12", height=34, padx=18)
        footer.pack(fill=tk.X, side=tk.BOTTOM)

        lbl_corp = tk.Label(
            footer,
            text="NDTechHub (NavDiva Group) • Multi-Platform Parental Safety Core • DPDP 2023 Compliant",
            font=("Segoe UI", 8),
            fg=COLOR_TEXT_MUTED,
            bg="#070a12"
        )
        lbl_corp.pack(side=tk.LEFT, pady=7)

        lbl_sync = tk.Label(
            footer,
            text="Dual-Sync: Mobile & Desktop Concurrently Active (MQTT QoS 1)",
            font=("Segoe UI", 8, "bold"),
            fg=COLOR_CYAN,
            bg="#070a12"
        )
        lbl_sync.pack(side=tk.RIGHT, pady=7)

    def _add_stat(self, parent, label, val, color=COLOR_TEXT):
        row = tk.Frame(parent, bg=COLOR_CARD, pady=3)
        row.pack(fill=tk.X)
        tk.Label(row, text=label, font=("Segoe UI", 9), fg=COLOR_TEXT_MUTED, bg=COLOR_CARD).pack(side=tk.LEFT)
        v = tk.Label(row, text=val, font=("Segoe UI", 9, "bold"), fg=color, bg=COLOR_CARD)
        v.pack(side=tk.RIGHT)
        return v

    def _btn(self, parent, text, cmd, bg_color):
        return tk.Button(
            parent,
            text=text,
            font=("Segoe UI", 8, "bold"),
            bg=bg_color,
            fg="#ffffff",
            activebackground=COLOR_PRIMARY,
            activeforeground="#ffffff",
            relief="flat",
            pady=5,
            cursor="hand2",
            command=cmd
        )

    # =========================================================================
    # EVENT HANDLERS & SIMULATIONS
    # =========================================================================
    def _toggle_lock(self):
        self.is_locked = not self.is_locked
        if self.is_locked:
            self.btn_emergency_lock.config(text="🔓 Unlock Child Device", bg="#059669")
            messagebox.showwarning(
                "Remote Device Locked",
                f"Emergency Remote Lockdown command transmitted to {self.child_name}'s Android phone and Windows PC.\n\nAll touchscreen and keyboard inputs are frozen with full-screen security PIN overlay."
            )
        else:
            self.btn_emergency_lock.config(text="🔒 Remote Screen Lock", bg="#dc2626")
            messagebox.showinfo("Remote Unlock", f"{self.child_name}'s device has been unlocked.")

    def _sound_siren(self):
        messagebox.showinfo("Emergency Siren Triggered", f"High-decibel alert tone dispatched to {self.child_name}'s phone to help locate them in crowds or emergencies.")

    def _force_gps(self):
        messagebox.showinfo("GPS Refreshed", f"High-precision Fused Location ping sent. Coordinates updated: {self.lat:.4f}° N, {self.lon:.4f}° E.")

    def _sim_sos(self):
        time_str = datetime.now().strftime("%H:%M:%S")
        self._add_sos_entry(time_str, "HARDWARE_VOL_DOWN", f"{self.lat:.4f}, {self.lon:.4f}", f"{self.battery}%", "ALARM DISPATCHED")
        messagebox.showerror(
            "CRITICAL DISTRESS SOS ALARM!",
            f"PANIC SEQUENCE DETECTED!\n\nChild: {self.child_name}\nTrigger: Rapid Triple-Tap on Volume Down Button\nCoordinates: {self.lat:.4f}° N, {self.lon:.4f}° E\nBattery: {self.battery}%\n\nImmediate attention required!"
        )

    def _go_school(self):
        self.lat, self.lon = 28.6145, 77.2120
        self.child_canvas_x, self.child_canvas_y = 235, 190
        self.current_zone = "School Safe Zone (DPS Campus)"
        self.val_zone.config(text=self.current_zone, fg=COLOR_SUCCESS)
        self.lbl_canvas_coords.config(text=f"{self.lat:.4f}° N, {self.lon:.4f}° E • ±3m accuracy")
        self._draw_map_zones()

    def _go_exit(self):
        self.lat, self.lon = 28.6190, 77.2180
        self.child_canvas_x, self.child_canvas_y = 350, 140
        self.current_zone = "Perimeter Transit (Exited School)"
        self.val_zone.config(text=self.current_zone, fg=COLOR_WARNING)
        self.lbl_canvas_coords.config(text=f"{self.lat:.4f}° N, {self.lon:.4f}° E • Outside Safe Perimeters")
        self._draw_map_zones()
        messagebox.showwarning("Perimeter Breach Warning", f"ChildGuard Alert: {self.child_name} has exited the designated School Safe Zone boundaries.")

    def _go_danger(self):
        self.lat, self.lon = 28.6120, 77.2340
        self.child_canvas_x, self.child_canvas_y = 475, 295
        self.current_zone = "Industrial Construction Site (DANGER ZONE)"
        self.val_zone.config(text=self.current_zone, fg=COLOR_DANGER)
        self.lbl_canvas_coords.config(text=f"{self.lat:.4f}° N, {self.lon:.4f}° E • CRITICAL BREACH")
        self._draw_map_zones()
        messagebox.showerror("CRITICAL GEOFENCE BREACH!", f"EMERGENCY ALARM: {self.child_name} has entered a PROHIBITED Danger Zone (Industrial Construction Site)!")

    def _go_home(self):
        self.lat, self.lon = 28.6220, 77.2230
        self.child_canvas_x, self.child_canvas_y = 450, 115
        self.current_zone = "Home Safe Zone"
        self.val_zone.config(text=self.current_zone, fg=COLOR_PRIMARY)
        self.lbl_canvas_coords.config(text=f"{self.lat:.4f}° N, {self.lon:.4f}° E • Home Protected")
        self._draw_map_zones()

if __name__ == "__main__":
    app = FullParentDesktopMonitor()
    app.mainloop()
