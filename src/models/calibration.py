"""Calibration module for fitting aircraft performance parameters.

For each aircraft, we have 2-3 known range-payload points from published data.
We adjust four parameters to match these points:

    CD0         — zero-lift drag coefficient
    e           — Oswald span efficiency factor
    k_adj       — TSFC adjustment factor (multiplier on reference TSFC)
    f_oh        — non-cruise fuel overhead fraction (overhead = f_oh × W_tow)

The f_oh parameter captures ALL non-cruise fuel: taxi, takeoff, climb to
cruise altitude, descent, approach, and reserves. It is modeled as a fraction
of takeoff weight because heavier aircraft consume proportionally more fuel
during these phases. This is the key to matching the SHAPE of the range-payload
diagram: at max payload (high TOW, low fuel), the overhead consumes a much
larger fraction of available fuel than at lighter payload conditions.

KNOWN LIMITATION: With a simplified Breguet cruise model and parabolic drag
polar, we typically achieve 5-15% RMS range error across the three calibration
points. The systematic bias pattern is:
    - Overprediction at short-range / high-payload conditions (Point 1)
    - Underprediction at long-range / low-payload conditions (Points 2, 3)

This occurs because the simplified model cannot capture the full trajectory
effects (altitude-variable engine performance, compressibility drag, detailed
climb profiles) that a tool like NASA FLOPS would model. The relative
comparisons between aircraft remain valid because all aircraft experience
the same systematic bias.

See STUDY_PLAN.md Phase 1e and ASSUMPTIONS_LOG.md for details.
"""

import math
import numpy as np
from scipy.optimize import minimize, differential_evolution
from src.models import performance, aerodynamics


# --- Parameter bounds ---
CD0_BOUNDS = (0.015, 0.040)     # Zero-lift drag coefficient
E_BOUNDS = (0.65, 0.90)         # Oswald efficiency factor
K_ADJ_BOUNDS = (0.80, 1.20)    # TSFC adjustment factor
F_OH_BOUNDS = (0.05, 0.25)     # Non-cruise fuel overhead fraction

# Climb/descent distance credits (nm)
CLIMB_DISTANCE_NM = 200
DESCENT_DISTANCE_NM = 120


def compute_calibration_range(aircraft_data, payload_lb, fuel_lb,
                               CD0, e, k_adj, f_oh, n_steps=30):
    """Compute mission range for calibration purposes.

    Uses the overhead model: cruise_fuel = total_fuel - f_oh × W_tow.
    Adds climb and descent distance credits to cruise range.

    Args:
        aircraft_data: Normalized aircraft dict
        payload_lb: Payload weight in lbf
        fuel_lb: Fuel weight in lbf
        CD0, e, k_adj, f_oh: Calibration parameters
        n_steps: Number of cruise steps

    Returns:
        Predicted mission range in nautical miles, or 0 if infeasible
    """
    ac = aircraft_data
    W_tow = ac["OEW"] + payload_lb + fuel_lb

    # Non-cruise fuel overhead
    overhead = f_oh * W_tow
    cruise_fuel = fuel_lb - overhead
    if cruise_fuel <= 0:
        return 0.0

    # Step-cruise for the cruise segment
    ceiling = ac.get("service_ceiling_ft", 43_000)
    result = performance.step_cruise_range(
        W_initial_lb=W_tow,
        fuel_available_lb=cruise_fuel,
        mach=ac["cruise_mach"],
        wing_area_ft2=ac["wing_area_ft2"],
        CD0=CD0,
        AR=ac["aspect_ratio"],
        e=e,
        tsfc_ref=ac["tsfc_cruise_ref"],
        k_adj=k_adj,
        ceiling_ft=ceiling,
        thrust_slst_lbf=ac["thrust_per_engine_slst_lbf"],
        n_engines=ac["n_engines"],
        n_steps=n_steps,
    )

    total_range = result["range_nm"] + CLIMB_DISTANCE_NM + DESCENT_DISTANCE_NM
    return total_range


def calibration_error(params, aircraft_data, calibration_points, n_steps=30):
    """Compute RMS relative range error for given parameters.

    Args:
        params: (CD0, e, k_adj, f_oh) tuple
        aircraft_data: Normalized aircraft dict
        calibration_points: List of (payload_lb, fuel_lb, range_nmi) tuples
        n_steps: Number of cruise segments

    Returns:
        RMS relative error (dimensionless, e.g., 0.05 = 5%)
    """
    CD0, e, k_adj, f_oh = params

    if CD0 <= 0 or e <= 0 or k_adj <= 0 or f_oh <= 0:
        return 1e6

    errors = []
    for payload, fuel, target_range in calibration_points:
        if target_range <= 0:
            continue

        try:
            predicted = compute_calibration_range(
                aircraft_data, payload, fuel, CD0, e, k_adj, f_oh,
                n_steps=n_steps
            )
            if predicted <= 0:
                errors.append(1.0)
            else:
                rel_error = (predicted - target_range) / target_range
                errors.append(rel_error ** 2)
        except Exception:
            errors.append(1.0)

    if not errors:
        return 1e6

    return math.sqrt(sum(errors) / len(errors))


def calibrate_aircraft(aircraft_data, method="two_stage"):
    """Calibrate CD0, e, k_adj, and f_oh for an aircraft.

    Two-stage approach:
    1. Global search with differential evolution
    2. Local refinement with Nelder-Mead

    Args:
        aircraft_data: Normalized aircraft dict
        method: "two_stage" (recommended), "global_only", or "local_only"

    Returns:
        dict with calibrated parameters and diagnostics
    """
    cal_points = aircraft_data["range_payload_points"]
    AR = aircraft_data["aspect_ratio"]

    if len(cal_points) < 2:
        raise ValueError(
            f"{aircraft_data['name']}: Need at least 2 calibration points, "
            f"got {len(cal_points)}"
        )

    bounds = [CD0_BOUNDS, E_BOUNDS, K_ADJ_BOUNDS, F_OH_BOUNDS]

    def objective(params):
        return calibration_error(params, aircraft_data, cal_points, n_steps=25)

    if method in ("two_stage", "global_only"):
        result_global = differential_evolution(
            objective,
            bounds=bounds,
            seed=42,
            maxiter=300,
            tol=1e-8,
            atol=1e-8,
            popsize=25,
            mutation=(0.5, 1.5),
            recombination=0.8,
        )
        x_best = result_global.x
        f_best = result_global.fun

        if method == "two_stage":
            result_local = minimize(
                objective,
                x0=x_best,
                method="Nelder-Mead",
                options={"maxiter": 5000, "xatol": 1e-10, "fatol": 1e-10},
            )
            if result_local.fun < f_best:
                x_best = result_local.x
                f_best = result_local.fun
    else:
        x0 = [0.025, 0.80, 1.0, 0.12]
        result_local = minimize(
            objective,
            x0=x0,
            method="Nelder-Mead",
            options={"maxiter": 10000, "xatol": 1e-10, "fatol": 1e-10},
        )
        x_best = result_local.x
        f_best = result_local.fun

    CD0_cal, e_cal, k_adj_cal, f_oh_cal = x_best

    # Detailed point-by-point results
    point_errors = _compute_point_errors(
        aircraft_data, cal_points, CD0_cal, e_cal, k_adj_cal, f_oh_cal
    )

    L_D_max, CL_star = aerodynamics.max_lift_to_drag(CD0_cal, AR, e_cal)

    # Convergence: 5% for 3+ points, 3% for 2 points
    threshold = 0.05 if len(cal_points) >= 3 else 0.03
    converged = f_best < threshold

    return {
        "CD0": CD0_cal,
        "e": e_cal,
        "k_adj": k_adj_cal,
        "f_oh": f_oh_cal,
        "rms_error": f_best,
        "point_errors": point_errors,
        "L_D_max": L_D_max,
        "CL_at_max_LD": CL_star,
        "converged": converged,
        "aircraft_name": aircraft_data["name"],
        "aircraft_designation": aircraft_data["designation"],
    }


def _compute_point_errors(aircraft_data, cal_points, CD0, e, k_adj, f_oh):
    """Compute per-point calibration errors with detailed breakdown."""
    point_errors = []
    for payload, fuel, target_range in cal_points:
        try:
            ac = aircraft_data
            W_tow = ac["OEW"] + payload + fuel
            overhead = f_oh * W_tow
            cruise_fuel = fuel - overhead

            predicted = compute_calibration_range(
                aircraft_data, payload, fuel, CD0, e, k_adj, f_oh,
                n_steps=50
            )
            pct_err = (predicted - target_range) / target_range * 100

            # Get cruise segment details
            cruise_result = performance.step_cruise_range(
                W_initial_lb=W_tow,
                fuel_available_lb=max(cruise_fuel, 0),
                mach=ac["cruise_mach"],
                wing_area_ft2=ac["wing_area_ft2"],
                CD0=CD0, AR=ac["aspect_ratio"], e=e,
                tsfc_ref=ac["tsfc_cruise_ref"], k_adj=k_adj,
                ceiling_ft=ac.get("service_ceiling_ft", 43000),
                thrust_slst_lbf=ac["thrust_per_engine_slst_lbf"],
                n_engines=ac["n_engines"],
                n_steps=50,
            )
            # Get initial cruise altitude from first segment
            init_alt = (cruise_result["segments"][0]["altitude_ft"]
                        if cruise_result["segments"] else 0)

            point_errors.append({
                "payload_lb": payload,
                "fuel_lb": fuel,
                "target_range_nm": target_range,
                "predicted_range_nm": predicted,
                "error_pct": pct_err,
                "overhead_fuel_lb": overhead,
                "cruise_fuel_lb": max(cruise_fuel, 0),
                "initial_cruise_alt_ft": init_alt,
            })
        except Exception as ex:
            point_errors.append({
                "payload_lb": payload,
                "fuel_lb": fuel,
                "target_range_nm": target_range,
                "predicted_range_nm": 0,
                "error_pct": -100,
                "error_msg": str(ex),
            })
    return point_errors


def calibrate_p8_from_737(cal_737, aircraft_data_p8, aircraft_data_737):
    """Derive P-8 calibration from calibrated 737-900ER model.

    Modifications from 737-900ER:
    - Raked wingtips: Oswald efficiency +0.025
    - Same basic CD0, k_adj, and f_oh

    If P-8 calibration points exist, refine parameters locally.
    """
    CD0_p8 = cal_737["CD0"]
    e_p8 = min(cal_737["e"] + 0.025, 0.90)
    k_adj_p8 = cal_737["k_adj"]
    f_oh_p8 = cal_737["f_oh"]

    cal_points = aircraft_data_p8.get("range_payload_points", [])
    if len(cal_points) >= 2:
        def objective(params):
            return calibration_error(params, aircraft_data_p8, cal_points, n_steps=25)

        result = minimize(
            objective,
            x0=[CD0_p8, e_p8, k_adj_p8, f_oh_p8],
            method="Nelder-Mead",
            options={"maxiter": 5000, "xatol": 1e-10, "fatol": 1e-10},
        )
        CD0_p8, e_p8, k_adj_p8, f_oh_p8 = result.x
        rms_err = result.fun
    else:
        rms_err = float('nan')

    AR = aircraft_data_p8["aspect_ratio"]
    L_D_max, CL_star = aerodynamics.max_lift_to_drag(CD0_p8, AR, e_p8)

    point_errors = _compute_point_errors(
        aircraft_data_p8, cal_points, CD0_p8, e_p8, k_adj_p8, f_oh_p8
    )

    return {
        "CD0": CD0_p8,
        "e": e_p8,
        "k_adj": k_adj_p8,
        "f_oh": f_oh_p8,
        "rms_error": rms_err,
        "point_errors": point_errors,
        "L_D_max": L_D_max,
        "CL_at_max_LD": CL_star,
        "converged": rms_err < 0.10 if not math.isnan(rms_err) else True,
        "aircraft_name": aircraft_data_p8["name"],
        "aircraft_designation": "P-8",
        "derived_from": "737-900ER",
        "oswald_delta": 0.025,
    }


def print_calibration_report(cal_result):
    """Print a formatted calibration report."""
    cr = cal_result
    status = "✓ CONVERGED" if cr["converged"] else "⚠ PARTIAL"

    print(f"\n{'='*72}")
    print(f"Calibration Report: {cr['aircraft_name']}")
    print(f"{'='*72}")
    print(f"Status: {status}  (RMS error: {cr['rms_error']*100:.2f}%)")
    print(f"\nCalibrated Parameters:")
    print(f"  CD0          = {cr['CD0']:.6f}")
    print(f"  e (Oswald)   = {cr['e']:.4f}")
    print(f"  k_adj (TSFC) = {cr['k_adj']:.4f}")
    print(f"  f_oh (ovhd)  = {cr['f_oh']:.4f}  "
          f"({cr['f_oh']*100:.1f}% of TOW is non-cruise fuel)")
    print(f"  (L/D)_max    = {cr['L_D_max']:.2f}  at CL = {cr['CL_at_max_LD']:.4f}")

    if "derived_from" in cr:
        print(f"\n  (Derived from {cr['derived_from']}, "
              f"Oswald delta = +{cr['oswald_delta']:.3f})")

    print(f"\nCalibration Point Results:")
    print(f"  {'Payload':>10} {'Fuel':>10} {'Target':>8} "
          f"{'Predicted':>10} {'Error':>8} {'Overhead':>10} {'Cruise F':>10} "
          f"{'Alt':>8}")
    print(f"  {'(lb)':>10} {'(lb)':>10} {'(nm)':>8} "
          f"{'(nm)':>10} {'':>8} {'(lb)':>10} {'(lb)':>10} {'(ft)':>8}")
    print(f"  {'-'*94}")
    for pe in cr["point_errors"]:
        oh = pe.get("overhead_fuel_lb", 0)
        cf = pe.get("cruise_fuel_lb", 0)
        alt = pe.get("initial_cruise_alt_ft", 0)
        print(f"  {pe['payload_lb']:>10,.0f} {pe['fuel_lb']:>10,.0f} "
              f"{pe['target_range_nm']:>8,.0f} "
              f"{pe['predicted_range_nm']:>10,.0f} "
              f"{pe['error_pct']:>+7.2f}% "
              f"{oh:>10,.0f} {cf:>10,.0f} {alt:>8,.0f}")
    print()

    _sanity_check(cr)


def _sanity_check(cal_result):
    """Run physical sanity checks on calibration results."""
    cr = cal_result
    issues = []

    if cr["L_D_max"] < 10:
        issues.append(f"WARNING: L/D_max = {cr['L_D_max']:.1f} is unusually low")
    elif cr["L_D_max"] > 22:
        issues.append(f"WARNING: L/D_max = {cr['L_D_max']:.1f} is unusually high")

    if cr["CD0"] < 0.015:
        issues.append(f"WARNING: CD0 = {cr['CD0']:.5f} below typical range")
    elif cr["CD0"] > 0.035:
        issues.append(f"WARNING: CD0 = {cr['CD0']:.5f} above typical range")

    if cr["e"] < 0.65:
        issues.append(f"WARNING: e = {cr['e']:.3f} below typical range")

    if abs(cr["k_adj"] - 1.0) > 0.15:
        issues.append(
            f"NOTE: k_adj = {cr['k_adj']:.3f} differs from 1.0 by "
            f"{abs(cr['k_adj']-1.0)*100:.1f}%"
        )

    if cr["f_oh"] > 0.20:
        issues.append(f"NOTE: f_oh = {cr['f_oh']:.3f} is high (>20% overhead)")
    elif cr["f_oh"] < 0.06:
        issues.append(f"NOTE: f_oh = {cr['f_oh']:.3f} is low (<6% overhead)")

    if issues:
        print("Sanity Checks:")
        for issue in issues:
            print(f"  {issue}")
        print()
    else:
        print("Sanity Checks: All passed ✓\n")
