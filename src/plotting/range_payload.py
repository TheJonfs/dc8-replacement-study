"""Range-payload diagram generation.

Produces individual and overlay range-payload diagrams for all aircraft.
Shows calibration points overlaid on continuous curves.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import os

from src.models.calibration import compute_calibration_range


# Color scheme for aircraft
AIRCRAFT_COLORS = {
    "DC-8": "#d62728",       # red (baseline)
    "GV": "#9467bd",         # purple
    "737-900ER": "#ff7f0e",  # orange
    "P-8": "#2ca02c",        # green
    "767-200ER": "#1f77b4",  # blue
    "A330-200": "#8c564b",   # brown
    "777-200LR": "#17becf",  # cyan
}

AIRCRAFT_MARKERS = {
    "DC-8": "s",
    "GV": "^",
    "737-900ER": "D",
    "P-8": "o",
    "767-200ER": "v",
    "A330-200": "p",
    "777-200LR": "*",
}


def generate_rp_curve(aircraft_data, cal_result, n_points=40, n_steps=30):
    """Generate range-payload curve data points.

    Sweeps payload from max_payload to 0, computing range at each point.

    Returns:
        List of dicts with payload_lb, range_nm, fuel_lb, tow_lb
    """
    ac = aircraft_data
    CD0 = cal_result["CD0"]
    e = cal_result["e"]
    k_adj = cal_result["k_adj"]
    f_oh = cal_result["f_oh"]

    curve = []
    max_pl = ac["max_payload"]

    for i in range(n_points + 1):
        payload = max_pl * (1.0 - i / n_points)

        # Determine fuel (limited by tank capacity and MTOW)
        fuel_mtow_limit = ac["MTOW"] - ac["OEW"] - payload
        fuel = min(fuel_mtow_limit, ac["max_fuel"])
        fuel = max(fuel, 0)

        if fuel <= 0:
            curve.append({
                "payload_lb": payload,
                "range_nm": 0,
                "fuel_lb": 0,
                "tow_lb": ac["OEW"] + payload,
            })
            continue

        try:
            range_nm = compute_calibration_range(
                ac, payload, fuel, CD0, e, k_adj, f_oh, n_steps=n_steps
            )
        except Exception:
            range_nm = 0

        curve.append({
            "payload_lb": payload,
            "range_nm": range_nm,
            "fuel_lb": fuel,
            "tow_lb": ac["OEW"] + payload + fuel,
        })

    return curve


def plot_individual_rp(aircraft_data, cal_result, output_dir="outputs/plots"):
    """Plot range-payload diagram for a single aircraft with calibration points."""
    ac = aircraft_data
    designation = ac["designation"]

    curve = generate_rp_curve(ac, cal_result, n_points=50)
    payloads = [p["payload_lb"] / 1000 for p in curve]
    ranges = [p["range_nm"] for p in curve]

    fig, ax = plt.subplots(figsize=(10, 7))

    # Plot curve
    color = AIRCRAFT_COLORS.get(designation, "#333333")
    ax.plot(ranges, payloads, '-', color=color, linewidth=2, label="Model")

    # Plot calibration points
    cal_points = ac["range_payload_points"]
    cal_payloads = [p[0] / 1000 for p in cal_points]
    cal_ranges = [p[2] for p in cal_points]
    ax.plot(cal_ranges, cal_payloads, 'ko', markersize=10, zorder=5,
            label="Published data")

    # Also show predicted values at calibration points
    for pe in cal_result["point_errors"]:
        ax.plot(pe["predicted_range_nm"], pe["payload_lb"] / 1000,
                'rx', markersize=10, markeredgewidth=2, zorder=5)

    # Labels and formatting
    ax.set_xlabel("Range (nm)", fontsize=12)
    ax.set_ylabel("Payload (1000 lb)", fontsize=12)
    ax.set_title(f"Range-Payload Diagram: {ac['name']}", fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    # Add calibration info text
    rms = cal_result["rms_error"] * 100
    ax.text(0.98, 0.02,
            f"Calibration RMS: {rms:.1f}%\n"
            f"CD0={cal_result['CD0']:.4f}, e={cal_result['e']:.3f}\n"
            f"L/D_max={cal_result['L_D_max']:.1f}",
            transform=ax.transAxes, fontsize=8, verticalalignment='bottom',
            horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"rp_{designation.replace('-', '').replace(' ', '_').lower()}.png")
    fig.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {filepath}")
    return filepath


def plot_overlay_rp(all_aircraft_data, all_calibrations, output_dir="outputs/plots"):
    """Plot overlaid range-payload diagrams for all aircraft."""
    fig, ax = plt.subplots(figsize=(14, 9))

    for designation in ["DC-8", "GV", "737-900ER", "P-8",
                         "767-200ER", "A330-200", "777-200LR"]:
        if designation not in all_calibrations:
            continue

        ac = all_aircraft_data[designation]
        cal = all_calibrations[designation]

        curve = generate_rp_curve(ac, cal, n_points=50)
        payloads = [p["payload_lb"] / 1000 for p in curve]
        ranges = [p["range_nm"] for p in curve]

        color = AIRCRAFT_COLORS.get(designation, "#333333")
        marker = AIRCRAFT_MARKERS.get(designation, "o")

        ax.plot(ranges, payloads, '-', color=color, linewidth=2,
                label=designation)

        # Plot calibration points
        cal_points = ac["range_payload_points"]
        cal_payloads = [p[0] / 1000 for p in cal_points]
        cal_ranges = [p[2] for p in cal_points]
        ax.plot(cal_ranges, cal_payloads, marker, color=color,
                markersize=8, markeredgecolor='black', markeredgewidth=0.5,
                zorder=5)

    ax.set_xlabel("Range (nm)", fontsize=13)
    ax.set_ylabel("Payload (1000 lb)", fontsize=13)
    ax.set_title("Range-Payload Comparison: DC-8 Replacement Candidates",
                 fontsize=15)
    ax.legend(fontsize=10, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)

    # Add mission requirement lines
    missions = [
        (5050, 46, "M1: SCEL→KPMD"),
        (4200, 52, "M2: NZCH→SCCI"),
    ]
    for rng, pl, label in missions:
        ax.axvline(x=rng, color='gray', linestyle='--', alpha=0.5)
        ax.axhline(y=pl, color='gray', linestyle='--', alpha=0.5)
        ax.annotate(label, xy=(rng, pl), fontsize=8, alpha=0.7,
                    xytext=(10, 10), textcoords='offset points')

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, "rp_overlay_all.png")
    fig.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {filepath}")
    return filepath
