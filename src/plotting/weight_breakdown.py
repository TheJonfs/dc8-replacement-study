"""Weight breakdown stacked bar charts (Deliverable 3).

For each mission, produces a stacked bar chart showing each aircraft's:
- Operating Empty Weight (OEW)
- Payload weight
- Mission fuel weight (fuel burned)
- Reserve fuel weight

For the GV and P-8, additional bars show fleet aggregate values
where n_aircraft > 1.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

from src.plotting.range_payload import AIRCRAFT_COLORS

# Study candidates in display order
STUDY_ORDER = ["DC-8", "GV", "P-8", "767-200ER", "A330-200", "777-200LR"]


def _build_bar_data(results):
    """Extract weight breakdown data from mission results.

    Returns a list of dicts, one per bar to display. Aircraft with
    n_aircraft > 1 get two entries: one per-aircraft and one aggregate.
    """
    bars = []
    for d in STUDY_ORDER:
        r = results[d]
        pa = r["per_aircraft"]
        if pa is None:
            continue

        n_ac = r["n_aircraft"]
        oew = pa["oew_lb"]
        payload = pa["payload_lb"]
        total_fuel = pa["total_fuel_lb"]

        # Fuel breakdown: reserve vs. mission fuel burned
        # Mission 1 uses f_oh model; missions 2-3 use explicit reserves
        if "reserve_fuel_lb" in pa and pa["reserve_fuel_lb"] > 0:
            reserve = pa["reserve_fuel_lb"]
        elif "fuel_at_destination_lb" in pa and pa["fuel_at_destination_lb"] is not None:
            # Mission 1 feasible aircraft: fuel at dest includes reserves
            reserve = pa["fuel_at_destination_lb"]
        else:
            # Fallback: total fuel minus burned
            reserve = max(total_fuel - pa.get("total_fuel_burned_lb",
                          pa.get("fuel_burned_lb", 0)), 0)

        fuel_burned = pa.get("total_fuel_burned_lb",
                             pa.get("fuel_burned_lb", 0))

        # For mission 1, non_cruise_fuel is overhead (taxi, climb, etc.)
        # We show it as part of mission fuel for simplicity
        non_cruise = pa.get("non_cruise_fuel_lb", 0)

        # Total fuel = burned + reserve (+ non_cruise for M1)
        # But total_fuel_lb is the actual fuel loaded, so:
        # mission_component = total_fuel - reserve
        mission_fuel_display = total_fuel - reserve

        bars.append({
            "label": d,
            "oew": oew,
            "payload": payload,
            "mission_fuel": mission_fuel_display,
            "reserve_fuel": reserve,
            "total": oew + payload + total_fuel,
            "is_aggregate": False,
            "n_aircraft": n_ac,
            "color": AIRCRAFT_COLORS.get(d, "#333333"),
        })

        # Fleet aggregate bar
        if n_ac > 1:
            bars.append({
                "label": f"{d}\n({n_ac}x fleet)",
                "oew": oew * n_ac,
                "payload": payload * n_ac,
                "mission_fuel": mission_fuel_display * n_ac,
                "reserve_fuel": reserve * n_ac,
                "total": (oew + payload + total_fuel) * n_ac,
                "is_aggregate": True,
                "n_aircraft": n_ac,
                "color": AIRCRAFT_COLORS.get(d, "#333333"),
            })

    return bars


def plot_weight_breakdown(results, mission_title, output_path):
    """Plot stacked weight breakdown bar chart for one mission.

    Args:
        results: dict keyed by designation -> mission result dict
        mission_title: Title string for the plot
        output_path: Full path for the output PNG file

    Returns:
        Output file path.
    """
    bars = _build_bar_data(results)
    if not bars:
        return None

    n_bars = len(bars)
    fig, ax = plt.subplots(figsize=(max(10, n_bars * 1.4), 8))

    x = np.arange(n_bars)
    width = 0.7

    labels = [b["label"] for b in bars]
    oew = np.array([b["oew"] for b in bars]) / 1000
    payload = np.array([b["payload"] for b in bars]) / 1000
    mission_fuel = np.array([b["mission_fuel"] for b in bars]) / 1000
    reserve_fuel = np.array([b["reserve_fuel"] for b in bars]) / 1000

    # Stacked bars
    p1 = ax.bar(x, oew, width, label="OEW", color="#7f7f7f", edgecolor="white")
    p2 = ax.bar(x, payload, width, bottom=oew,
                label="Payload", color="#2ca02c", edgecolor="white")
    p3 = ax.bar(x, mission_fuel, width, bottom=oew + payload,
                label="Mission Fuel", color="#ff7f0e", edgecolor="white")
    p4 = ax.bar(x, reserve_fuel, width, bottom=oew + payload + mission_fuel,
                label="Reserve Fuel", color="#d62728", edgecolor="white",
                alpha=0.7)

    # Hatch pattern for aggregate bars
    for i, b in enumerate(bars):
        if b["is_aggregate"]:
            for p in [p1, p2, p3, p4]:
                p[i].set_hatch("//")
                p[i].set_edgecolor("black")
                p[i].set_linewidth(0.5)

    # Total weight annotation on top of each bar
    totals = oew + payload + mission_fuel + reserve_fuel
    for i, total in enumerate(totals):
        ax.text(i, total + max(totals) * 0.01,
                f"{total:.0f}k",
                ha='center', va='bottom', fontsize=8, fontweight='bold')

    ax.set_xlabel("Aircraft", fontsize=12)
    ax.set_ylabel("Weight (1,000 lb)", fontsize=12)
    ax.set_title(f"Weight Breakdown: {mission_title}", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.legend(fontsize=10, loc='upper left')
    ax.grid(True, alpha=0.2, axis='y')
    ax.set_ylim(0, max(totals) * 1.12)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {output_path}")
    return output_path
