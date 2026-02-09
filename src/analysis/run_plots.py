"""Generate all range-payload diagrams.

Produces individual range-payload plots for each aircraft and a combined
overlay plot comparing all candidates. Uses Path A (calibration range)
for curve generation.

Usage:
    python3 -m src.analysis.run_plots

Outputs:
    outputs/plots/rp_dc8.png
    outputs/plots/rp_gv.png
    outputs/plots/rp_737900er.png
    outputs/plots/rp_p8.png
    outputs/plots/rp_767200er.png
    outputs/plots/rp_a330200.png
    outputs/plots/rp_777200lr.png
    outputs/plots/rp_overlay_all.png
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.analysis.run_calibration import run_all_calibrations
from src.plotting.range_payload import plot_individual_rp, plot_overlay_rp

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'outputs', 'plots')

# All aircraft to plot (includes 737-900ER for context)
PLOT_ORDER = ["DC-8", "GV", "737-900ER", "P-8", "767-200ER", "A330-200", "777-200LR"]


def run_all_plots(all_ac=None, calibrations=None):
    """Generate all range-payload plots.

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

    # Individual plots
    print("\nGenerating individual range-payload plots...")
    for designation in PLOT_ORDER:
        if designation in calibrations:
            path = plot_individual_rp(
                all_ac[designation], calibrations[designation],
                output_dir=OUTPUT_DIR
            )
            output_paths.append(path)

    # Overlay plot
    print("\nGenerating overlay plot...")
    path = plot_overlay_rp(all_ac, calibrations, output_dir=OUTPUT_DIR)
    output_paths.append(path)

    print(f"\nGenerated {len(output_paths)} plots in {OUTPUT_DIR}")
    return output_paths


if __name__ == "__main__":
    run_all_plots()
