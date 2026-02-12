"""Speed and altitude profile plots (Deliverable 5).

Mission 1: Altitude vs. distance and Mach vs. distance, showing
the engine-out altitude drop for each aircraft.

Mission 2: Altitude vs. distance showing the sawtooth pattern with
progressive ceiling increase across all aircraft.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

from src.plotting.range_payload import AIRCRAFT_COLORS, AIRCRAFT_MARKERS

STUDY_ORDER = ["DC-8", "GV", "P-8", "767-200ER", "A330-200", "777-200LR"]


def plot_mission1_altitude(results, output_path):
    """Plot altitude vs. distance for Mission 1 (engine-out).

    Shows all aircraft on a single overlay. A vertical dashed line marks
    the engine failure point at 2,525 nm. The altitude drop after engine
    failure is the key feature.

    Args:
        results: dict keyed by designation -> mission 1 result dict
        output_path: Full path for the output PNG file

    Returns:
        Output file path.
    """
    fig, ax = plt.subplots(figsize=(14, 7))

    for d in STUDY_ORDER:
        r = results[d]
        pa = r["per_aircraft"]
        if pa is None:
            continue

        color = AIRCRAFT_COLORS.get(d, "#333333")

        # Collect distance and altitude from both segments
        distances = []
        altitudes = []

        # Segment 1 (normal cruise)
        seg1 = pa["segment1"]
        for s in seg1["segments"]:
            distances.append(s["cumulative_range_nm"])
            altitudes.append(s["altitude_ft"])

        # Segment 2 (engine-out)
        seg2 = pa["segment2"]
        for s in seg2["segments"]:
            distances.append(s["cumulative_range_nm"])
            altitudes.append(s["altitude_ft"])

        if distances:
            alt_kft = [a / 1000 for a in altitudes]
            ax.plot(distances, alt_kft, '-', color=color, linewidth=1.8,
                    label=d, alpha=0.9)

    # Engine failure marker
    ax.axvline(x=2525, color='red', linestyle='--', alpha=0.6, linewidth=1.5)
    ax.text(2525, ax.get_ylim()[1] * 0.02, "  Engine\n  Failure",
            color='red', fontsize=9, alpha=0.7, va='bottom')

    # Destination marker
    ax.axvline(x=5050, color='green', linestyle='--', alpha=0.4, linewidth=1)
    ax.text(5050, ax.get_ylim()[1] * 0.02, "  KPMD",
            color='green', fontsize=9, alpha=0.6, va='bottom')

    ax.set_xlabel("Distance from Departure (nm)", fontsize=12)
    ax.set_ylabel("Cruise Altitude (1,000 ft)", fontsize=12)
    ax.set_title("Mission 1: Altitude Profile — Engine-Out Transport (SCEL→KPMD)",
                 fontsize=13)
    ax.legend(fontsize=9, loc='lower left')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, None)
    ax.set_ylim(0, None)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {output_path}")
    return output_path


def plot_mission1_mach(results, output_path):
    """Plot Mach number vs. distance for Mission 1 (engine-out).

    Mach is constant per aircraft (cruise Mach) but differs between
    aircraft, so this shows the operating point comparison.

    Args:
        results: dict keyed by designation -> mission 1 result dict
        output_path: Full path for the output PNG file

    Returns:
        Output file path.
    """
    fig, ax = plt.subplots(figsize=(14, 5))

    for d in STUDY_ORDER:
        r = results[d]
        pa = r["per_aircraft"]
        if pa is None:
            continue

        color = AIRCRAFT_COLORS.get(d, "#333333")

        distances = []
        machs = []

        for seg_key in ["segment1", "segment2"]:
            seg = pa[seg_key]
            for s in seg["segments"]:
                distances.append(s["cumulative_range_nm"])
                machs.append(s["mach"])

        if distances:
            ax.plot(distances, machs, '-', color=color, linewidth=2,
                    label=d, alpha=0.9)

    # Engine failure marker
    ax.axvline(x=2525, color='red', linestyle='--', alpha=0.6, linewidth=1.5)
    ax.text(2525, ax.get_ylim()[0] + 0.001, "  Engine Failure",
            color='red', fontsize=9, alpha=0.7, va='bottom')

    ax.set_xlabel("Distance from Departure (nm)", fontsize=12)
    ax.set_ylabel("Mach Number", fontsize=12)
    ax.set_title("Mission 1: Mach Profile — Engine-Out Transport (SCEL→KPMD)",
                 fontsize=13)
    ax.legend(fontsize=9, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, None)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {output_path}")
    return output_path


def plot_mission2_altitude(results, output_path):
    """Plot altitude vs. distance for Mission 2 (vertical sampling).

    Shows the sawtooth climb-descend pattern for all aircraft overlaid.
    Progressive ceiling increase as fuel burns off is the key feature.

    Args:
        results: dict keyed by designation -> mission 2 result dict
        output_path: Full path for the output PNG file

    Returns:
        Output file path.
    """
    fig, ax = plt.subplots(figsize=(16, 8))

    for d in STUDY_ORDER:
        r = results[d]
        pa = r["per_aircraft"]
        if pa is None:
            continue

        color = AIRCRAFT_COLORS.get(d, "#333333")
        profile = pa["profile_points"]
        if not profile:
            continue

        distances = [p[0] for p in profile]
        altitudes = [p[1] / 1000 for p in profile]

        ax.plot(distances, altitudes, '-', color=color, linewidth=1.2,
                label=f"{d} (peak {pa['peak_ceiling_ft']/1000:.0f}k ft)",
                alpha=0.85)

    # Distance requirement
    ax.axvline(x=4200, color='green', linestyle='--', alpha=0.4, linewidth=1)
    ax.text(4200, 1, "  4,200 nm\n  required",
            color='green', fontsize=9, alpha=0.6, va='bottom')

    ax.set_xlabel("Distance from Departure (nm)", fontsize=12)
    ax.set_ylabel("Altitude (1,000 ft)", fontsize=12)
    ax.set_title("Mission 2: Altitude Profile — Vertical Atmospheric Sampling "
                 "(NZCH→SCCI)", fontsize=13)
    ax.legend(fontsize=9, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, None)
    ax.set_ylim(0, None)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {output_path}")
    return output_path


def plot_mission2_ceiling_progression(results, output_path):
    """Plot ceiling altitude vs. cycle number for Mission 2.

    Shows how each aircraft's achievable ceiling increases across
    successive climb-descend cycles as fuel burns off.

    Args:
        results: dict keyed by designation -> mission 2 result dict
        output_path: Full path for the output PNG file

    Returns:
        Output file path.
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    for d in STUDY_ORDER:
        r = results[d]
        pa = r["per_aircraft"]
        if pa is None:
            continue

        cycles = pa["cycles"]
        if not cycles:
            continue

        color = AIRCRAFT_COLORS.get(d, "#333333")
        marker = AIRCRAFT_MARKERS.get(d, "o")

        cycle_nums = [c["cycle"] for c in cycles]
        ceilings = [c["ceiling_ft"] / 1000 for c in cycles]

        ax.plot(cycle_nums, ceilings, '-', color=color, marker=marker,
                markersize=5, linewidth=1.5,
                label=f"{d} ({ceilings[0]:.0f}→{ceilings[-1]:.0f}k ft)",
                alpha=0.85)

    ax.set_xlabel("Cycle Number", fontsize=12)
    ax.set_ylabel("Ceiling Altitude (1,000 ft)", fontsize=12)
    ax.set_title("Mission 2: Progressive Ceiling — Altitude Capability vs. "
                 "Cycle Number", fontsize=13)
    ax.legend(fontsize=9, loc='best')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(bottom=35)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {output_path}")
    return output_path
