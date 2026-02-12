"""Fuel cost comparison bar chart (Deliverable 4).

Produces a grouped bar chart showing $/klb-nm for each aircraft across
all three missions. Aircraft that fail a mission are shown with a
gray hatched bar labeled "FAIL" instead of a cost value.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os

from src.plotting.range_payload import AIRCRAFT_COLORS

STUDY_ORDER = ["DC-8", "GV", "P-8", "767-200ER", "A330-200", "777-200LR"]

# Mission 1 statuses from the reviewed analysis (STATUS.md).
# The model produces cost numbers even for infeasible aircraft, but
# reporting costs for failed missions is misleading. These overrides
# ensure we only show costs for aircraft that can complete the mission.
#
# PASS: model confirms feasibility with adequate confidence
# LIKELY_PASS: model suggests feasibility but calibration is low confidence
# UNCERTAIN: calibration too poor to assess
# FAIL: model confirms infeasibility
MISSION1_STATUS = {
    "DC-8":      "FAIL",
    "GV":        "FAIL",
    "P-8":       "FAIL",
    "767-200ER": "PASS",
    "A330-200":  "UNCERTAIN",
    "777-200LR": "LIKELY_PASS",
}


def _get_cost_metric(result):
    """Extract the $/klb-nm cost metric from a mission result.

    Uses fleet aggregate if n_aircraft > 1, otherwise per-aircraft.
    """
    if result["aggregate"]:
        return result["aggregate"]["fuel_cost_per_1000lb_nm"]
    pa = result["per_aircraft"]
    if pa is None:
        return None
    return pa["fuel_cost_per_1000lb_nm"]


def plot_fuel_cost_comparison(m1_results, m2_results, m3_results, output_path):
    """Plot grouped bar chart of fuel cost ($/klb-nm) across all missions.

    Aircraft that fail a mission get a gray hatched bar with "FAIL" label.
    Aircraft with UNCERTAIN status get a lighter bar with "?" label.

    Args:
        m1_results: Mission 1 results dict
        m2_results: Mission 2 results dict
        m3_results: Mission 3 results dict
        output_path: Full path for the output PNG file

    Returns:
        Output file path.
    """
    missions = ["Mission 1\nEngine-Out", "Mission 2\nSampling", "Mission 3\nSmoke Survey"]
    n_missions = len(missions)
    n_aircraft = len(STUDY_ORDER)

    bar_width = 0.12
    x = np.arange(n_missions)

    fig, ax = plt.subplots(figsize=(14, 7))

    for i, d in enumerate(STUDY_ORDER):
        color = AIRCRAFT_COLORS.get(d, "#333333")
        offset = (i - n_aircraft / 2 + 0.5) * bar_width

        costs = []
        statuses = []

        # Mission 1: use reviewed status overrides
        m1_status = MISSION1_STATUS.get(d, "FAIL")
        m1_cost = _get_cost_metric(m1_results[d])
        if m1_status in ("PASS", "LIKELY_PASS") and m1_cost is not None:
            costs.append(m1_cost)
            statuses.append(m1_status)
        else:
            costs.append(0)
            statuses.append(m1_status)

        # Missions 2-3: use model feasibility directly
        for m_results in [m2_results, m3_results]:
            r = m_results[d]
            if r["feasible"]:
                cost = _get_cost_metric(r)
                costs.append(cost if cost is not None else 0)
                statuses.append("PASS")
            else:
                costs.append(0)
                statuses.append("FAIL")

        # Draw bars for each mission
        for j in range(n_missions):
            bar_x = x[j] + offset
            status = statuses[j]
            cost = costs[j]

            if status in ("PASS", "LIKELY_PASS"):
                bar = ax.bar(bar_x, cost, bar_width * 0.9, color=color,
                             edgecolor='white', linewidth=0.5, alpha=0.85)
                # Fleet size annotation
                n_ac = m1_results[d]["n_aircraft"] if j == 0 else \
                       m2_results[d]["n_aircraft"] if j == 1 else \
                       m3_results[d]["n_aircraft"]
                label_text = f"${cost:.2f}"
                if n_ac > 1:
                    label_text += f"\n({n_ac}x)"
                ax.text(bar_x, cost + 0.02, label_text,
                        ha='center', va='bottom', fontsize=6.5,
                        fontweight='bold')
            elif status == "UNCERTAIN":
                # Light bar with question mark
                bar = ax.bar(bar_x, 0.15, bar_width * 0.9, color=color,
                             edgecolor='gray', linewidth=0.8, alpha=0.25,
                             hatch='...')
                ax.text(bar_x, 0.17, "?",
                        ha='center', va='bottom', fontsize=7,
                        color='gray', fontweight='bold')
            else:
                # FAIL — gray hatched stub
                bar = ax.bar(bar_x, 0.15, bar_width * 0.9, color='#cccccc',
                             edgecolor='gray', linewidth=0.8, alpha=0.5,
                             hatch='///')
                ax.text(bar_x, 0.17, "FAIL",
                        ha='center', va='bottom', fontsize=6,
                        color='#888888', fontweight='bold')

    # Custom legend (one entry per aircraft)
    handles = []
    for d in STUDY_ORDER:
        color = AIRCRAFT_COLORS.get(d, "#333333")
        patch = plt.Rectangle((0, 0), 1, 1, fc=color, ec='white', alpha=0.85)
        handles.append(patch)
    ax.legend(handles, STUDY_ORDER, fontsize=9, loc='upper left',
              ncol=2)

    ax.set_xlabel("Mission", fontsize=12)
    ax.set_ylabel("Fuel Cost ($ per 1,000 lb payload per nm)", fontsize=12)
    ax.set_title("Fuel Cost Efficiency Comparison Across Missions", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(missions, fontsize=10)
    ax.grid(True, alpha=0.2, axis='y')
    ax.set_ylim(0, None)

    # Note about failed missions and DC-8 reliability
    fig.text(0.5, -0.03,
             "FAIL = aircraft cannot complete mission as defined. "
             "? = calibration too poor to assess. "
             "DC-8 costs unreliable (k_adj=0.605). "
             "Fleet sizes shown where n > 1.",
             ha='center', fontsize=8, style='italic', color='#555555')

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {output_path}")
    return output_path
