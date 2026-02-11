"""Mission simulation models for DC-8 replacement study.

Implements the three science missions from CLAUDE.md:
  Mission 1: Long-range transport with engine-out (SCEL -> KPMD)
  Mission 2: Vertical atmospheric sampling (NZCH -> SCCI)  [not yet implemented]
  Mission 3: Low-altitude smoke survey                      [not yet implemented]

Each mission function takes an aircraft data dict and calibration result dict,
and returns a detailed result dict including fuel breakdown, go/no-go status,
segment data for plotting, and fleet sizing for small aircraft.

Fuel budget approach (from PHASE2_STEP1_RECONCILIATION.md):
  Mission 1: f_oh hybrid (non_cruise_fuel = f_oh * W_tow)
  Mission 2: Explicit reserves only (no f_oh)
  Mission 3: Explicit reserves only (no f_oh)
"""

import math
from src.models import performance, aerodynamics
from src.models.calibration import CLIMB_DISTANCE_NM, DESCENT_DISTANCE_NM
from src.utils import fuel_cost


def _find_fuel_at_distance(segments, target_range_nm):
    """Find fuel burned and weight when cumulative range reaches a target distance.

    Scans through step_cruise_range segment data to find where cumulative
    range crosses the target. Interpolates within the crossing step.

    Args:
        segments: List of segment dicts from step_cruise_range, each with
                  cumulative_range_nm, cumulative_fuel_lb, W_start_lb,
                  W_end_lb, range_nm
        target_range_nm: Distance at which to stop

    Returns:
        dict with:
            fuel_burned_lb: Total fuel consumed to reach target distance
            weight_lb: Aircraft weight at target distance
            segments: List of segments up to target (last one truncated)
            reached: True if target was reached, False if fuel exhausted first
    """
    if not segments:
        return {"fuel_burned_lb": 0, "weight_lb": 0, "segments": [], "reached": False}

    truncated = []

    for i, s in enumerate(segments):
        if s["cumulative_range_nm"] >= target_range_nm:
            # This step crosses the target — interpolate
            prev_cum_range = segments[i - 1]["cumulative_range_nm"] if i > 0 else 0.0
            prev_cum_fuel = segments[i - 1]["cumulative_fuel_lb"] if i > 0 else 0.0

            range_into_step = target_range_nm - prev_cum_range
            frac = range_into_step / s["range_nm"] if s["range_nm"] > 0 else 1.0
            frac = min(max(frac, 0.0), 1.0)

            step_fuel = s["W_start_lb"] - s["W_end_lb"]
            interpolated_fuel = step_fuel * frac

            fuel_burned = prev_cum_fuel + interpolated_fuel
            weight = s["W_start_lb"] - interpolated_fuel

            # Add truncated step for plotting continuity
            partial = dict(s)
            partial["range_nm"] = s["range_nm"] * frac
            partial["cumulative_range_nm"] = target_range_nm
            partial["cumulative_fuel_lb"] = fuel_burned
            partial["W_end_lb"] = weight
            truncated.append(partial)

            return {
                "fuel_burned_lb": fuel_burned,
                "weight_lb": weight,
                "segments": truncated,
                "reached": True,
            }

        truncated.append(dict(s))

    # Exhausted all fuel before reaching target
    last = segments[-1]
    return {
        "fuel_burned_lb": last["cumulative_fuel_lb"],
        "weight_lb": last["W_end_lb"],
        "segments": truncated,
        "reached": False,
    }


def _determine_infeasibility(total_range, required_range, reserve):
    """Return a human-readable reason for mission infeasibility."""
    reasons = []
    if total_range < required_range:
        shortfall = required_range - total_range
        reasons.append(
            f"Range shortfall: {shortfall:,.0f} nm "
            f"({total_range:,.0f} of {required_range:,.0f} nm)"
        )
    if reserve < 0:
        reasons.append(f"Negative reserve fuel: {reserve:,.0f} lb")
    return "; ".join(reasons) if reasons else "Unknown"


def simulate_mission1_engine_out(ac, cal, payload_lb=46_000, distance_nm=5050,
                                  failure_point_nm=2525, n_steps_per_segment=50):
    """Simulate Mission 1: Long-range transport with single engine failure.

    Route: Santiago, Chile (SCEL) to Palmdale, CA (KPMD)
    Distance: 5,050 nmi, Payload: 46,000 lb
    Single engine failure at mission midpoint (2,525 nm)

    Two-segment cruise model:
      Segment 1 (0 to 2,525 nm): Normal cruise, all engines
      Segment 2 (2,525 to 5,050 nm): Engine-out with +10% drag, n_engines-1

    Fuel budget: f_oh hybrid (non_cruise_fuel = f_oh * W_tow).
    Climb/descent distance credits: 200 nm + 120 nm (Path A convention).

    For aircraft that cannot carry the full payload (GV, P-8),
    computes fleet sizing and aggregate costs.

    Args:
        ac: Normalized aircraft data dict from loader
        cal: Calibration result dict (CD0, e, k_adj, f_oh, etc.)
        payload_lb: Required total payload in lbf (default 46,000)
        distance_nm: Total mission distance in nmi (default 5,050)
        failure_point_nm: Distance at engine failure in nmi (default 2,525)
        n_steps_per_segment: Cruise integration steps per segment

    Returns:
        dict with feasibility, per-aircraft results, fleet aggregate, and
        segment data for speed/altitude profile plotting.
    """
    designation = ac["designation"]

    # --- Step 1: Fleet sizing ---
    actual_payload = min(payload_lb, ac["max_payload"])
    if actual_payload < payload_lb:
        n_aircraft = math.ceil(payload_lb / ac["max_payload"])
        actual_payload = payload_lb / n_aircraft
    else:
        n_aircraft = 1

    # --- Step 2: Fuel available ---
    fuel_available = min(ac["MTOW"] - ac["OEW"] - actual_payload, ac["max_fuel"])
    if fuel_available <= 0:
        return _infeasible_result(ac, cal, payload_lb, actual_payload, n_aircraft,
                                  "Cannot carry payload within MTOW")

    W_tow = ac["OEW"] + actual_payload + fuel_available

    # --- Step 3: Fuel budget (f_oh hybrid) ---
    f_oh = cal["f_oh"]
    non_cruise_fuel = f_oh * W_tow
    cruise_fuel = fuel_available - non_cruise_fuel
    if cruise_fuel <= 0:
        return _infeasible_result(ac, cal, payload_lb, actual_payload, n_aircraft,
                                  "No cruise fuel after f_oh overhead deduction")

    # Calibrated parameters
    CD0 = cal["CD0"]
    e = cal["e"]
    k_adj = cal["k_adj"]
    ceiling = ac.get("service_ceiling_ft", 43_000)
    mach = ac["cruise_mach"]

    # --- Step 4: Segment 1 — Normal cruise ---
    # Run with all cruise fuel to find where 2,525 nm is reached.
    # Account for climb credit: the failure_point_nm is measured from takeoff,
    # and the first 200 nm are climb credit, so the cruise distance to the
    # failure point is failure_point_nm - CLIMB_DISTANCE_NM.
    cruise_to_failure = failure_point_nm - CLIMB_DISTANCE_NM
    if cruise_to_failure <= 0:
        # Failure occurs during climb — treat entire mission as engine-out
        cruise_to_failure = 0

    seg1_full = performance.step_cruise_range(
        W_initial_lb=W_tow,
        fuel_available_lb=cruise_fuel,
        mach=mach,
        wing_area_ft2=ac["wing_area_ft2"],
        CD0=CD0,
        AR=ac["aspect_ratio"],
        e=e,
        tsfc_ref=ac["tsfc_cruise_ref"],
        k_adj=k_adj,
        ceiling_ft=ceiling,
        thrust_slst_lbf=ac["thrust_per_engine_slst_lbf"],
        n_engines=ac["n_engines"],
        n_steps=n_steps_per_segment * 2,  # fine resolution for interpolation
        drag_multiplier=1.0,
    )

    # Find where cumulative cruise range hits the failure point
    seg1_split = _find_fuel_at_distance(seg1_full["segments"], cruise_to_failure)

    seg1_fuel_burned = seg1_split["fuel_burned_lb"]
    seg1_range = seg1_split["segments"][-1]["cumulative_range_nm"] if seg1_split["segments"] else 0.0
    seg1_segments = seg1_split["segments"]

    # --- Step 5: Weight and remaining fuel at failure ---
    W_at_failure = W_tow - seg1_fuel_burned
    remaining_cruise_fuel = cruise_fuel - seg1_fuel_burned

    # --- Step 6: Segment 2 — Engine-out cruise ---
    drag_mult = aerodynamics.engine_out_drag_factor(ac["n_engines"])
    n_engines_eo = ac["n_engines"] - 1

    if remaining_cruise_fuel > 0:
        seg2_result = performance.step_cruise_range(
            W_initial_lb=W_at_failure,
            fuel_available_lb=remaining_cruise_fuel,
            mach=mach,
            wing_area_ft2=ac["wing_area_ft2"],
            CD0=CD0,
            AR=ac["aspect_ratio"],
            e=e,
            tsfc_ref=ac["tsfc_cruise_ref"],
            k_adj=k_adj,
            ceiling_ft=ceiling,
            thrust_slst_lbf=ac["thrust_per_engine_slst_lbf"],
            n_engines=n_engines_eo,
            n_steps=n_steps_per_segment,
            drag_multiplier=drag_mult,
            h_min=10_000,  # lower floor to find true engine-out ceiling
        )
        seg2_range = seg2_result["range_nm"]
        seg2_fuel_burned = seg2_result["fuel_burned_lb"]
        seg2_segments = seg2_result["segments"]
    else:
        seg2_range = 0.0
        seg2_fuel_burned = 0.0
        seg2_segments = []

    # --- Step 7: Total range and feasibility ---
    total_cruise_range = seg1_range + seg2_range
    total_range = total_cruise_range + CLIMB_DISTANCE_NM + DESCENT_DISTANCE_NM
    total_fuel_burned = seg1_fuel_burned + seg2_fuel_burned
    reserve_remaining = cruise_fuel - total_fuel_burned

    feasible = total_range >= distance_nm and reserve_remaining >= -50  # small tolerance

    # --- Step 7b: Fuel remaining at destination (for feasible aircraft) ---
    # If the aircraft can reach the required distance, calculate how much
    # cruise fuel remains unburned at exactly the mission distance.
    # This gives pilots a meaningful "fuel on board at destination" metric.
    fuel_at_destination_lb = None
    if feasible:
        required_cruise_distance = distance_nm - CLIMB_DISTANCE_NM - DESCENT_DISTANCE_NM
        # Combine seg1 + seg2 segments with continuous cumulative tracking
        # seg1 segments have raw cumulative_range_nm; seg2 segments need offset
        combined_for_fad = []
        for s in seg1_segments:
            combined_for_fad.append(dict(s))
        seg1_total_fuel = seg1_fuel_burned
        seg1_total_range_val = seg1_range
        for s in seg2_segments:
            entry = dict(s)
            entry["cumulative_range_nm"] = seg1_total_range_val + s["cumulative_range_nm"]
            entry["cumulative_fuel_lb"] = seg1_total_fuel + s["cumulative_fuel_lb"]
            combined_for_fad.append(entry)
        fad_result = _find_fuel_at_distance(combined_for_fad, required_cruise_distance)
        if fad_result["reached"]:
            fuel_at_destination_lb = cruise_fuel - fad_result["fuel_burned_lb"]

    # --- Step 8: Offset segment data for continuous distance axis ---
    # Segment 1: offset by climb credit
    for s in seg1_segments:
        s["cumulative_range_nm"] += CLIMB_DISTANCE_NM

    # Segment 2: offset by climb credit + segment 1 range
    seg2_offset = CLIMB_DISTANCE_NM + seg1_range
    for s in seg2_segments:
        s["cumulative_range_nm"] += seg2_offset

    # --- Step 9: Fuel cost metrics ---
    total_fuel_cost = fuel_cost(fuel_available)
    fuel_cost_metric = (
        total_fuel_cost / (actual_payload / 1000.0 * distance_nm)
        if actual_payload > 0 and distance_nm > 0 else float('inf')
    )

    # --- Step 10: Assemble result ---
    per_aircraft = {
        "takeoff_weight_lb": W_tow,
        "oew_lb": ac["OEW"],
        "payload_lb": actual_payload,
        "total_fuel_lb": fuel_available,
        "non_cruise_fuel_lb": non_cruise_fuel,
        "cruise_fuel_lb": cruise_fuel,
        "segment1": {
            "label": "Normal cruise",
            "range_nm": seg1_range,
            "fuel_burned_lb": seg1_fuel_burned,
            "n_engines": ac["n_engines"],
            "drag_multiplier": 1.0,
            "mach": mach,
            "weight_at_start_lb": W_tow,
            "weight_at_end_lb": W_at_failure,
            "segments": seg1_segments,
        },
        "segment2": {
            "label": "Engine-out cruise",
            "range_nm": seg2_range,
            "fuel_burned_lb": seg2_fuel_burned,
            "n_engines": n_engines_eo,
            "drag_multiplier": drag_mult,
            "mach": mach,
            "weight_at_start_lb": W_at_failure,
            "weight_at_end_lb": W_at_failure - seg2_fuel_burned,
            "segments": seg2_segments,
        },
        "climb_credit_nm": CLIMB_DISTANCE_NM,
        "descent_credit_nm": DESCENT_DISTANCE_NM,
        "total_range_nm": total_range,
        "cruise_range_nm": total_cruise_range,
        "range_surplus_nm": total_range - distance_nm,
        "total_fuel_burned_lb": total_fuel_burned,
        "reserve_fuel_lb": max(reserve_remaining, 0),
        "fuel_at_destination_lb": fuel_at_destination_lb,
        "fuel_cost_usd": total_fuel_cost,
        "fuel_cost_per_1000lb_nm": fuel_cost_metric,
    }

    # --- Step 11: Fleet aggregate ---
    if n_aircraft > 1:
        fleet_fuel_cost = n_aircraft * total_fuel_cost
        aggregate = {
            "n_aircraft": n_aircraft,
            "total_payload_lb": n_aircraft * actual_payload,
            "total_fuel_lb": n_aircraft * fuel_available,
            "total_fuel_burned_lb": n_aircraft * total_fuel_burned,
            "total_fuel_cost_usd": fleet_fuel_cost,
            "fuel_cost_per_1000lb_nm": (
                fleet_fuel_cost / (payload_lb / 1000.0 * distance_nm)
                if payload_lb > 0 else float('inf')
            ),
        }
    else:
        aggregate = None

    return {
        "feasible": feasible,
        "infeasible_reason": (
            None if feasible else
            _determine_infeasibility(total_range, distance_nm, reserve_remaining)
        ),
        "aircraft_name": ac.get("name", designation),
        "designation": designation,
        "payload_requested_lb": payload_lb,
        "payload_actual_lb": actual_payload,
        "n_aircraft": n_aircraft,
        "per_aircraft": per_aircraft,
        "aggregate": aggregate,
    }


def _infeasible_result(ac, cal, payload_requested, payload_actual, n_aircraft, reason):
    """Build a minimal result dict for an aircraft that can't attempt the mission."""
    return {
        "feasible": False,
        "infeasible_reason": reason,
        "aircraft_name": ac.get("name", ac["designation"]),
        "designation": ac["designation"],
        "payload_requested_lb": payload_requested,
        "payload_actual_lb": payload_actual,
        "n_aircraft": n_aircraft,
        "per_aircraft": None,
        "aggregate": None,
    }
