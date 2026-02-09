"""Path A/B Reconciliation: Compare calibration and mission range computations.

Path A (calibration.compute_calibration_range):
    cruise_fuel = total_fuel - f_oh * W_tow
    range = step_cruise(cruise_fuel, W_tow) + 200nm (climb) + 120nm (descent)

Path B (performance.compute_range_for_payload):
    climb_fuel = energy_method(W_tow, h_cruise)
    descent_fuel = 300 lb (fixed)
    reserve_fuel = 5% contingency + 200nm alternate + 30min hold
    cruise_fuel = total_fuel - climb_fuel - descent_fuel - reserve_fuel
    range = step_cruise(cruise_fuel, W_cruise_start) + climb_dist + descent_dist

Key structural differences:
1. Fuel budget: Path A uses f_oh*W_tow overhead; Path B computes climb/descent/reserve explicitly
2. Cruise start weight: Path A starts cruise at W_tow; Path B starts at W_tow - climb_fuel
3. Climb/descent range: Path A uses fixed 200+120=320nm; Path B computes from physics
4. Reserves: Path A has no explicit reserves (absorbed into f_oh); Path B deducts reserves

For each aircraft at each calibration point, this script:
- Runs Path A with calibrated parameters
- Runs Path B with the same calibrated (CD0, e, k_adj) but NO f_oh
- Breaks down the fuel budget and range contributions
- Reports the discrepancy

Usage:
    python3 -m src.analysis.reconcile_paths
"""

import os
import sys
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.aircraft_data.loader import load_all_aircraft
from src.analysis.run_calibration import run_all_calibrations
from src.models.calibration import compute_calibration_range
from src.models.performance import (
    compute_range_for_payload,
    estimate_climb_fuel,
    estimate_descent_credit,
    compute_reserve_fuel,
    step_cruise_range,
    optimal_cruise_altitude,
)

# Study candidates only (not 737-900ER)
STUDY_CANDIDATES = ["DC-8", "GV", "P-8", "767-200ER", "A330-200", "777-200LR"]


def reconcile_single_point(ac, cal, payload_lb, fuel_lb, target_range_nm):
    """Compare Path A and Path B for a single calibration point.

    Returns dict with detailed breakdown of both paths.
    """
    CD0 = cal["CD0"]
    e = cal["e"]
    k_adj = cal["k_adj"]
    f_oh = cal["f_oh"]

    W_tow = ac["OEW"] + payload_lb + fuel_lb

    # === PATH A ===
    range_a = compute_calibration_range(ac, payload_lb, fuel_lb, CD0, e, k_adj, f_oh, n_steps=50)
    overhead_a = f_oh * W_tow
    cruise_fuel_a = fuel_lb - overhead_a
    climb_dist_a = 200.0
    descent_dist_a = 120.0

    # Get the cruise-only range from Path A (total - climb - descent credits)
    cruise_range_a = range_a - climb_dist_a - descent_dist_a

    # === PATH B ===
    ceiling = ac.get("service_ceiling_ft", 43_000)

    # Step 1: Determine cruise altitude (same as Path B does internally)
    h_cruise = optimal_cruise_altitude(
        W_tow, ac["cruise_mach"], ac["wing_area_ft2"],
        CD0, ac["aspect_ratio"], e, ac["tsfc_cruise_ref"], k_adj,
        ceiling, ac["thrust_per_engine_slst_lbf"], ac["n_engines"],
    )

    # Step 2: Climb fuel and distance
    climb = estimate_climb_fuel(W_tow, h_cruise, ac, CD0, ac["aspect_ratio"], e,
                                ac["tsfc_cruise_ref"], k_adj)

    # Step 3: Descent credit
    descent = estimate_descent_credit(h_cruise, ac)

    # Step 4: Reserve fuel
    reserve = compute_reserve_fuel(fuel_lb, ac, CD0, e, k_adj)

    # Step 5: Cruise fuel
    cruise_fuel_b = fuel_lb - climb["climb_fuel_lb"] - descent["descent_fuel_lb"] - reserve
    cruise_fuel_b_clamped = max(cruise_fuel_b, 0)

    # Step 6: Full Path B range
    try:
        result_b = compute_range_for_payload(ac, payload_lb, fuel_lb, CD0, e, k_adj, n_steps=50)
        range_b = result_b["range_nm"]
        cruise_range_b = result_b["cruise_range_nm"]
        climb_dist_b = result_b["climb_distance_nm"]
        descent_dist_b = result_b["descent_distance_nm"]
    except Exception as ex:
        range_b = 0
        cruise_range_b = 0
        climb_dist_b = climb["climb_distance_nm"]
        descent_dist_b = descent["descent_distance_nm"]

    # === COMPARISON ===
    # How does Path A's overhead compare to Path B's explicit deductions?
    total_deductions_b = climb["climb_fuel_lb"] + descent["descent_fuel_lb"] + reserve

    return {
        "designation": ac["designation"],
        "payload_lb": payload_lb,
        "fuel_lb": fuel_lb,
        "W_tow": W_tow,
        "target_range_nm": target_range_nm,
        # Path A
        "range_a": range_a,
        "overhead_a": overhead_a,
        "cruise_fuel_a": cruise_fuel_a,
        "cruise_range_a": cruise_range_a,
        "climb_dist_a": climb_dist_a,
        "descent_dist_a": descent_dist_a,
        # Path B
        "range_b": range_b,
        "climb_fuel_b": climb["climb_fuel_lb"],
        "descent_fuel_b": descent["descent_fuel_lb"],
        "reserve_fuel_b": reserve,
        "total_deductions_b": total_deductions_b,
        "cruise_fuel_b": cruise_fuel_b_clamped,
        "cruise_range_b": cruise_range_b,
        "climb_dist_b": climb_dist_b,
        "descent_dist_b": descent_dist_b,
        "h_cruise_b": h_cruise,
        # Discrepancies
        "range_error_ab": range_b - range_a,
        "range_error_ab_pct": (range_b - range_a) / range_a * 100 if range_a > 0 else float('nan'),
        "fuel_overhead_diff": total_deductions_b - overhead_a,
        "cruise_fuel_diff": cruise_fuel_b_clamped - cruise_fuel_a,
    }


def print_reconciliation_report(results):
    """Print a detailed reconciliation report."""
    current_ac = None

    for r in results:
        if r["designation"] != current_ac:
            current_ac = r["designation"]
            print(f"\n{'='*100}")
            print(f"  {current_ac}")
            print(f"{'='*100}")

        print(f"\n  Payload: {r['payload_lb']:,.0f} lb  |  Fuel: {r['fuel_lb']:,.0f} lb  |  "
              f"TOW: {r['W_tow']:,.0f} lb  |  Target: {r['target_range_nm']:,.0f} nm")
        print(f"  {'-'*90}")

        # Fuel budget comparison
        print(f"  {'Fuel Budget':<30} {'Path A':>15} {'Path B':>15} {'Difference':>15}")
        print(f"  {'-'*75}")
        print(f"  {'Total fuel':<30} {r['fuel_lb']:>15,.0f} {r['fuel_lb']:>15,.0f} {'—':>15}")
        print(f"  {'Overhead / climb fuel':<30} {r['overhead_a']:>15,.0f} "
              f"{r['climb_fuel_b']:>15,.0f} {r['climb_fuel_b']-r['overhead_a']:>+15,.0f}")
        print(f"  {'(descent fuel)':<30} {'(in overhead)':>15} "
              f"{r['descent_fuel_b']:>15,.0f}")
        print(f"  {'(reserve fuel)':<30} {'(in overhead)':>15} "
              f"{r['reserve_fuel_b']:>15,.0f}")
        print(f"  {'Total non-cruise':<30} {r['overhead_a']:>15,.0f} "
              f"{r['total_deductions_b']:>15,.0f} {r['fuel_overhead_diff']:>+15,.0f}")
        print(f"  {'Cruise fuel':<30} {r['cruise_fuel_a']:>15,.0f} "
              f"{r['cruise_fuel_b']:>15,.0f} {r['cruise_fuel_diff']:>+15,.0f}")

        # Range comparison
        print(f"\n  {'Range Components':<30} {'Path A':>15} {'Path B':>15} {'Difference':>15}")
        print(f"  {'-'*75}")
        print(f"  {'Climb distance (nm)':<30} {r['climb_dist_a']:>15.0f} "
              f"{r['climb_dist_b']:>15.0f} {r['climb_dist_b']-r['climb_dist_a']:>+15.0f}")
        print(f"  {'Cruise range (nm)':<30} {r['cruise_range_a']:>15.0f} "
              f"{r['cruise_range_b']:>15.0f} {r['cruise_range_b']-r['cruise_range_a']:>+15.0f}")
        print(f"  {'Descent distance (nm)':<30} {r['descent_dist_a']:>15.0f} "
              f"{r['descent_dist_b']:>15.0f} {r['descent_dist_b']-r['descent_dist_a']:>+15.0f}")
        print(f"  {'TOTAL RANGE (nm)':<30} {r['range_a']:>15.0f} "
              f"{r['range_b']:>15.0f} {r['range_error_ab']:>+15.0f}")
        pct = r['range_error_ab_pct']
        pct_str = f"{pct:+.1f}%" if not math.isnan(pct) else "N/A"
        target_err_a = (r['range_a'] - r['target_range_nm']) / r['target_range_nm'] * 100
        target_err_b = (r['range_b'] - r['target_range_nm']) / r['target_range_nm'] * 100
        print(f"  {'Relative to Path A':<30} {'—':>15} {pct_str:>15}")
        print(f"  {'Error vs target':<30} {target_err_a:>+14.1f}% {target_err_b:>+14.1f}%")


def print_summary_table(results):
    """Print a compact summary comparing both paths across all points."""
    print(f"\n\n{'='*110}")
    print("RECONCILIATION SUMMARY")
    print(f"{'='*110}")
    print(f"{'Aircraft':<12} {'Payload':>10} {'Fuel':>10} {'Target':>8} "
          f"{'Path A':>8} {'Path B':>8} {'A-B':>8} {'A-B %':>8} "
          f"{'OH_A':>10} {'Ded_B':>10} {'OH diff':>10}")
    print(f"{'-'*12} {'-'*10} {'-'*10} {'-'*8} "
          f"{'-'*8} {'-'*8} {'-'*8} {'-'*8} "
          f"{'-'*10} {'-'*10} {'-'*10}")

    for r in results:
        pct = r['range_error_ab_pct']
        pct_str = f"{pct:+.1f}%" if not math.isnan(pct) else "N/A"
        print(f"{r['designation']:<12} {r['payload_lb']:>10,.0f} {r['fuel_lb']:>10,.0f} "
              f"{r['target_range_nm']:>8,.0f} "
              f"{r['range_a']:>8,.0f} {r['range_b']:>8,.0f} "
              f"{r['range_error_ab']:>+8,.0f} {pct_str:>8} "
              f"{r['overhead_a']:>10,.0f} {r['total_deductions_b']:>10,.0f} "
              f"{r['fuel_overhead_diff']:>+10,.0f}")

    print()


def run_reconciliation(verbose=True):
    """Run full Path A/B reconciliation.

    Returns list of per-point result dicts.
    """
    if verbose:
        print("Running calibrations...")
    all_ac, calibrations = run_all_calibrations(verbose=False)

    results = []
    for designation in STUDY_CANDIDATES:
        ac = all_ac[designation]
        cal = calibrations[designation]

        for payload, fuel, target_range in ac["range_payload_points"]:
            r = reconcile_single_point(ac, cal, payload, fuel, target_range)
            results.append(r)

    if verbose:
        print_reconciliation_report(results)
        print_summary_table(results)

    return results


if __name__ == "__main__":
    run_reconciliation(verbose=True)
