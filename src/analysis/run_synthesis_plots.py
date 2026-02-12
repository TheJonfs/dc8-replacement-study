"""Generate all synthesis plots (Deliverables 3 and 5).

Produces:
  - Weight breakdown stacked bars for all three missions (Deliverable 3)
  - Altitude and Mach profiles for Missions 1 and 2 (Deliverable 5)

Requires calibration (~12 min) and mission simulation to produce the
data needed for plotting.

Usage:
    python3 -m src.analysis.run_synthesis_plots

Outputs:
    outputs/plots/weight_breakdown_m1.png
    outputs/plots/weight_breakdown_m2.png
    outputs/plots/weight_breakdown_m3.png
    outputs/plots/profile_m1_altitude.png
    outputs/plots/profile_m1_mach.png
    outputs/plots/profile_m2_altitude.png
    outputs/plots/profile_m2_ceiling.png
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.analysis.run_calibration import run_all_calibrations
from src.analysis.run_missions import run_mission1, run_mission2, run_mission3
from src.plotting.weight_breakdown import plot_weight_breakdown
from src.plotting.mission_profiles import (
    plot_mission1_altitude,
    plot_mission1_mach,
    plot_mission2_altitude,
    plot_mission2_ceiling_progression,
)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'outputs', 'plots')


def run_all_synthesis_plots(all_ac=None, calibrations=None):
    """Generate all synthesis plots.

    Args:
        all_ac: Aircraft data dict (if None, runs calibration first).
        calibrations: Calibration results dict (if None, runs calibration first).

    Returns:
        List of output file paths.
    """
    if all_ac is None or calibrations is None:
        print("Running calibrations (this may take several minutes)...")
        all_ac, calibrations = run_all_calibrations(verbose=False)

    output_paths = []

    # --- Run all missions (quiet mode) ---
    print("\nRunning Mission 1 (engine-out)...")
    m1_results = run_mission1(all_ac, calibrations, verbose=False)

    print("Running Mission 2 (vertical sampling)...")
    m2_results = run_mission2(all_ac, calibrations, verbose=False)

    print("Running Mission 3 (low-altitude endurance)...")
    m3_results = run_mission3(all_ac, calibrations, verbose=False)

    # --- Deliverable 3: Weight Breakdown Stacked Bars ---
    print("\nGenerating weight breakdown plots (Deliverable 3)...")

    path = plot_weight_breakdown(
        m1_results,
        "Mission 1 — Engine-Out Transport (SCEL→KPMD, 5,050 nm, 46,000 lb)",
        os.path.join(OUTPUT_DIR, "weight_breakdown_m1.png"),
    )
    output_paths.append(path)

    path = plot_weight_breakdown(
        m2_results,
        "Mission 2 — Vertical Sampling (NZCH→SCCI, 4,200 nm, 52,000 lb)",
        os.path.join(OUTPUT_DIR, "weight_breakdown_m2.png"),
    )
    output_paths.append(path)

    path = plot_weight_breakdown(
        m3_results,
        "Mission 3 — Low-Altitude Smoke Survey (8 hr, 30,000 lb, 1,500 ft)",
        os.path.join(OUTPUT_DIR, "weight_breakdown_m3.png"),
    )
    output_paths.append(path)

    # --- Deliverable 5: Speed and Altitude Profiles ---
    print("\nGenerating speed/altitude profile plots (Deliverable 5)...")

    path = plot_mission1_altitude(
        m1_results,
        os.path.join(OUTPUT_DIR, "profile_m1_altitude.png"),
    )
    output_paths.append(path)

    path = plot_mission1_mach(
        m1_results,
        os.path.join(OUTPUT_DIR, "profile_m1_mach.png"),
    )
    output_paths.append(path)

    path = plot_mission2_altitude(
        m2_results,
        os.path.join(OUTPUT_DIR, "profile_m2_altitude.png"),
    )
    output_paths.append(path)

    path = plot_mission2_ceiling_progression(
        m2_results,
        os.path.join(OUTPUT_DIR, "profile_m2_ceiling.png"),
    )
    output_paths.append(path)

    print(f"\nGenerated {len(output_paths)} synthesis plots in {OUTPUT_DIR}")
    return output_paths


if __name__ == "__main__":
    run_all_synthesis_plots()
