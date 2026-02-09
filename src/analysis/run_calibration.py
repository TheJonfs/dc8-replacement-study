"""Run calibration for all aircraft and save results.

Calibrates all 7 aircraft models (6 candidates + 737-900ER intermediate)
against published range-payload data using differential evolution + Nelder-Mead
optimization. The P-8 is derived from the calibrated 737-900ER model.

Usage:
    python3 -m src.analysis.run_calibration

Outputs:
    - Calibration reports printed to stdout
    - outputs/calibration_results.json

The run_all_calibrations() function is also importable by other scripts
(run_plots.py, run_missions.py) to avoid re-running calibration.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.aircraft_data.loader import load_all_aircraft
from src.models.calibration import (
    calibrate_aircraft,
    calibrate_p8_from_737,
    print_calibration_report,
)

# Order in which aircraft are calibrated
CALIBRATION_ORDER = ["DC-8", "GV", "737-900ER", "767-200ER", "A330-200", "777-200LR"]

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'outputs')


def run_all_calibrations(verbose=True):
    """Run calibration for all aircraft.

    Args:
        verbose: If True, print calibration reports to stdout.

    Returns:
        Tuple of (all_aircraft_data, all_calibrations) where:
            all_aircraft_data: dict keyed by designation -> normalized aircraft dict
            all_calibrations: dict keyed by designation -> calibration result dict
    """
    all_ac = load_all_aircraft()
    calibrations = {}

    for designation in CALIBRATION_ORDER:
        if verbose:
            print(f"Calibrating {designation}...")
        calibrations[designation] = calibrate_aircraft(all_ac[designation])
        if verbose:
            print_calibration_report(calibrations[designation])

    # P-8 derived from 737-900ER
    if verbose:
        print("Deriving P-8 from 737-900ER...")
    calibrations["P-8"] = calibrate_p8_from_737(
        calibrations["737-900ER"], all_ac["P-8"], all_ac["737-900ER"]
    )
    if verbose:
        print_calibration_report(calibrations["P-8"])

    return all_ac, calibrations


def save_calibration_results(calibrations, output_dir=None):
    """Save calibration results to JSON.

    Args:
        calibrations: dict keyed by designation -> calibration result dict
        output_dir: Directory for output file. Defaults to outputs/.
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, 'calibration_results.json')

    # Convert to JSON-serializable format
    serializable = {}
    for designation, cal in calibrations.items():
        entry = {
            "aircraft_name": cal["aircraft_name"],
            "CD0": float(cal["CD0"]),
            "e": float(cal["e"]),
            "k_adj": float(cal["k_adj"]),
            "f_oh": float(cal["f_oh"]),
            "rms_error": float(cal["rms_error"]),
            "L_D_max": float(cal["L_D_max"]),
            "converged": bool(cal["converged"]),
        }
        if "derived_from" in cal:
            entry["derived_from"] = cal["derived_from"]
        serializable[designation] = entry

    with open(filepath, 'w') as f:
        json.dump(serializable, f, indent=2)

    print(f"Saved calibration results to {filepath}")


def print_summary_table(calibrations):
    """Print a compact summary table of all calibrations."""
    print(f"\n{'='*90}")
    print("Calibration Summary")
    print(f"{'='*90}")
    print(f"{'Aircraft':<14} {'CD0':>8} {'e':>8} {'k_adj':>8} {'f_oh':>8} "
          f"{'L/D_max':>8} {'RMS':>8} {'Status':<12}")
    print(f"{'-'*14} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*12}")

    for designation in CALIBRATION_ORDER + ["P-8"]:
        cal = calibrations[designation]
        status = "CONVERGED" if cal["converged"] else "PARTIAL"
        print(f"{designation:<14} {cal['CD0']:>8.4f} {cal['e']:>8.3f} "
              f"{cal['k_adj']:>8.3f} {cal['f_oh']:>8.3f} "
              f"{cal['L_D_max']:>8.1f} {cal['rms_error']*100:>7.1f}% "
              f"{status:<12}")
    print()


if __name__ == "__main__":
    all_ac, calibrations = run_all_calibrations(verbose=True)
    print_summary_table(calibrations)
    save_calibration_results(calibrations)
