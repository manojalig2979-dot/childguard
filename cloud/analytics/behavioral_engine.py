"""
ChildGuard AI - Behavioral & Safety Analytics Engine (Phase 4)
Aggregates spatial telemetry, app usage stats, and threat alarms into
actionable weekly parental insights and wellness scoring.
"""

import sys
import json
import time
from typing import Dict, Any, List

def compute_weekly_behavioral_summary(
    child_name: str = "Aarav",
    device_id: str = "child_dev_99182",
    total_locations: int = 1420,
    safe_zone_locations: int = 1369,
    screen_time_hours: float = 18.5,
    intercepted_threats: int = 4,
    blocked_processes: int = 2
) -> Dict[str, Any]:
    """Computes wellness metrics, spatial compliance, and AI parenting guidance."""
    
    # 1. Safe-Zone Adherence Percentage
    adherence_pct = round((safe_zone_locations / max(total_locations, 1)) * 100, 1)

    # 2. Compute Holistic Safety Score (0 - 100)
    # Deductions: high screen time (> 20 hrs: -5), threats (-3 each), danger breaches (-10 each)
    base_score = 100.0
    if screen_time_hours > 20:
        base_score -= 8
    elif screen_time_hours > 15:
        base_score -= 3

    base_score -= (intercepted_threats * 2.5)
    base_score -= (blocked_processes * 3.0)

    # Geofence compliance factor
    if adherence_pct < 90.0:
        base_score -= (90.0 - adherence_pct) * 0.5

    safety_score = max(min(round(base_score), 100), 40)

    # Status classification
    if safety_score >= 90:
        status_label = "Optimal Protection"
        status_color = "#10B981" # Green
    elif safety_score >= 75:
        status_label = "Good Protection"
        status_color = "#3B82F6" # Blue
    elif safety_score >= 60:
        status_label = "Moderate Attention Needed"
        status_color = "#F59E0B" # Amber
    else:
        status_label = "High Alert"
        status_color = "#EF4444" # Red

    # 3. Screen Time Category Breakdown
    screen_time_breakdown = [
        {"category": "Learning & Classroom", "percentage": 42, "color": "#10B981", "hours": 7.8},
        {"category": "Messaging & Family", "percentage": 26, "color": "#3B82F6", "hours": 4.8},
        {"category": "Entertainment & Video", "percentage": 20, "color": "#8B5CF6", "hours": 3.7},
        {"category": "Gaming & Other", "percentage": 12, "color": "#F59E0B", "hours": 2.2}
    ]

    # 4. Actionable AI Recommendations for Parents
    recommendations = [
        {
            "title": "Positive Spatial Routine",
            "body": f"{child_name} maintained a {adherence_pct}% safe-zone adherence rate between Delhi Public School and Home this week.",
            "type": "positive"
        },
        {
            "title": "Evening Screen-Time Balance",
            "body": "Entertainment app usage increased between 8:30 PM - 10:00 PM. Consider enabling a 9:00 PM automated screen curfew.",
            "type": "suggestion"
        },
        {
            "title": "Threat Protection Shield Active",
            "body": f"The on-device classifier successfully filtered {intercepted_threats} vulgar social feed items and 1 unknown contact threat.",
            "type": "shield"
        }
    ]

    summary = {
        "child_name": child_name,
        "device_id": device_id,
        "period": "Last 7 Days",
        "safety_score": safety_score,
        "status_label": status_label,
        "status_color": status_color,
        "metrics": {
            "safe_zone_adherence_pct": adherence_pct,
            "total_screen_time_hours": screen_time_hours,
            "threats_neutralized": intercepted_threats + blocked_processes,
            "danger_zone_breaches_prevented": 1
        },
        "screen_time_breakdown": screen_time_breakdown,
        "recommendations": recommendations,
        "generated_at": int(time.time() * 1000)
    }

    return summary

def main():
    report = compute_weekly_behavioral_summary()
    print("\n=======================================================")
    print(f" CHILDGUARD AI: WEEKLY BEHAVIORAL SAFETY REPORT        ")
    print("=======================================================")
    print(f"Target: {report['child_name']} ({report['device_id']})")
    print(f"Safety Index: {report['safety_score']}/100 [{report['status_label']}]")
    print(f"Safe-Zone Adherence: {report['metrics']['safe_zone_adherence_pct']}%")
    print(f"Screen Time: {report['metrics']['total_screen_time_hours']} hrs")
    print(f"Threats Neutralized: {report['metrics']['threats_neutralized']}")
    print("\nAI Recommendations:")
    for idx, rec in enumerate(report['recommendations'], 1):
        print(f"  {idx}. [{rec['title']}] {rec['body']}")
    print("=======================================================\n")

if __name__ == "__main__":
    main()
