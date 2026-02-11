"""Mission simulation models for DC-8 replacement study.

Implements the three science missions from CLAUDE.md:
  Mission 1: Long-range transport with engine-out (SCEL -> KPMD)
  Mission 2: Vertical atmospheric sampling (NZCH -> SCCI)
  Mission 3: Low-altitude smoke survey (Central US)

Each mission function takes an aircraft data dict and calibration result dict,
and returns a detailed result dict including fuel breakdown, go/no-go status,
segment data for plotting, and fleet sizing for small aircraft.

Fuel budget approach (from PHASE2_STEP1_RECONCILIATION.md):
  Mission 1: f_oh hybrid (non_cruise_fuel = f_oh * W_tow)
  Mission 2: Explicit reserves only (no f_oh)
  Mission 3: Explicit reserves only (no f_oh)
"""

import math
from src.models import atmosphere, performance, aerodynamics, propulsion
from src.models.calibration import CLIMB_DISTANCE_NM, DESCENT_DISTANCE_NM
from src.utils import fuel_cost, NM_TO_FT, FT_TO_NM


def climb_segment(W_start_lb, h_start_ft, h_target_ft, mach_climb,
                   wing_area_ft2, CD0, AR, e, tsfc_ref, k_adj,
                   thrust_slst_lbf, n_engines, h_step_ft=1000,
                   roc_min_fpm=100.0):
    """Compute fuel, distance, and time for a climb between two altitudes.

    Uses altitude-stepping integration. At each step:
    - Compute drag at current altitude/weight/Mach
    - Compute thrust available
    - Compute excess thrust -> rate of climb
    - If ROC < roc_min_fpm, the aircraft has reached its service ceiling
    - Compute fuel flow, time for step, distance covered
    - Update weight

    Args:
        W_start_lb: Aircraft weight at start of climb (lbf)
        h_start_ft: Starting altitude (ft)
        h_target_ft: Target altitude (ft); climb stops earlier if ceiling reached
        mach_climb: Mach number during climb (constant Mach assumption)
        wing_area_ft2: Wing reference area (ft^2)
        CD0: Zero-lift drag coefficient (calibrated)
        AR: Wing aspect ratio
        e: Oswald span efficiency factor (calibrated)
        tsfc_ref: Reference cruise TSFC [lb/(lbf-hr)]
        k_adj: TSFC calibration adjustment factor
        thrust_slst_lbf: Sea-level static thrust per engine (lbf)
        n_engines: Number of operating engines
        h_step_ft: Altitude integration step size (ft, default 1000)
        roc_min_fpm: Minimum ROC for service ceiling definition (ft/min, default 100)

    Returns:
        dict with:
            fuel_burned_lb: Total fuel consumed during climb
            distance_nm: Horizontal distance covered during climb
            time_hr: Total climb time in hours
            ceiling_ft: Actual ceiling achieved (may be < h_target_ft)
            steps: List of per-step dicts for plotting/analysis
            ceiling_limited: True if climb stopped before h_target_ft
    """
    if h_start_ft >= h_target_ft:
        return {
            "fuel_burned_lb": 0.0,
            "distance_nm": 0.0,
            "time_hr": 0.0,
            "ceiling_ft": h_start_ft,
            "steps": [],
            "ceiling_limited": False,
        }

    total_fuel = 0.0
    total_distance_nm = 0.0
    total_time_hr = 0.0
    W_current = W_start_lb
    h_current = h_start_ft
    steps = []
    ceiling_limited = False

    while h_current < h_target_ft:
        # Altitude step (may be partial at the top)
        dh = min(h_step_ft, h_target_ft - h_current)
        h_mid = h_current + dh / 2.0

        # Atmospheric conditions at midpoint
        a_mid = atmosphere.speed_of_sound(h_mid)
        V_fps = mach_climb * a_mid
        rho_mid = atmosphere.density(h_mid)
        q_mid = 0.5 * rho_mid * V_fps ** 2

        # Aerodynamics at current weight and midpoint altitude
        CL = aerodynamics.lift_coefficient(W_current, q_mid, wing_area_ft2)
        CD = aerodynamics.drag_coefficient(CL, CD0, AR, e)
        drag_lbf = CD * q_mid * wing_area_ft2

        # Thrust available at midpoint altitude
        thrust_avail = propulsion.thrust_available_cruise(
            thrust_slst_lbf, h_mid, n_engines
        )

        # Excess thrust -> climb capability
        excess_thrust = thrust_avail - drag_lbf
        if excess_thrust <= 0:
            ceiling_limited = True
            break

        # Rate of climb: ROC = V * (T_excess / W)
        # sin(gamma) = T_excess / W, ROC = V * sin(gamma)
        sin_gamma = excess_thrust / W_current
        roc_fps = V_fps * sin_gamma
        roc_fpm = roc_fps * 60.0

        if roc_fpm < roc_min_fpm:
            ceiling_limited = True
            break

        # Time for this altitude step
        dt_sec = dh / roc_fps
        dt_hr = dt_sec / 3600.0

        # Fuel burn: thrust_required * TSFC * time
        # During climb, thrust ~ drag + W * sin(gamma) = thrust_avail
        # But we use a more accurate formulation: the engine produces
        # thrust equal to drag + climb component
        thrust_required = drag_lbf + W_current * sin_gamma
        tsfc_val = propulsion.tsfc(h_mid, mach_climb, tsfc_ref, k_adj)
        fuel_flow_lbhr = thrust_required * tsfc_val
        fuel_this_step = fuel_flow_lbhr * dt_hr

        # Horizontal distance
        cos_gamma = math.sqrt(1.0 - sin_gamma ** 2)
        horiz_fps = V_fps * cos_gamma
        dist_ft = horiz_fps * dt_sec
        dist_nm = dist_ft * FT_TO_NM

        # Record step
        steps.append({
            "h_start_ft": h_current,
            "h_end_ft": h_current + dh,
            "h_mid_ft": h_mid,
            "W_start_lb": W_current,
            "fuel_lb": fuel_this_step,
            "distance_nm": dist_nm,
            "time_hr": dt_hr,
            "roc_fpm": roc_fpm,
            "thrust_avail_lbf": thrust_avail,
            "drag_lbf": drag_lbf,
            "excess_thrust_lbf": excess_thrust,
            "mach": mach_climb,
            "CL": CL,
        })

        # Update state
        total_fuel += fuel_this_step
        total_distance_nm += dist_nm
        total_time_hr += dt_hr
        W_current -= fuel_this_step
        h_current += dh

    return {
        "fuel_burned_lb": total_fuel,
        "distance_nm": total_distance_nm,
        "time_hr": total_time_hr,
        "ceiling_ft": h_current,
        "steps": steps,
        "ceiling_limited": ceiling_limited,
    }


def descend_segment(W_start_lb, h_start_ft, h_target_ft, mach_descent,
                     wing_area_ft2, CD0, AR, e, tsfc_ref, k_adj,
                     descent_rate_fpm=2000.0, idle_fraction=0.10):
    """Compute fuel, distance, and time for an idle descent.

    Fuel burn is scaled to aircraft size using idle_fraction of cruise
    fuel flow at a representative mid-descent altitude, rather than
    the fixed 300 lb used in Mission 1.

    Args:
        W_start_lb: Aircraft weight at start of descent (lbf)
        h_start_ft: Starting altitude (ft)
        h_target_ft: Target altitude (ft)
        mach_descent: Mach number during descent
        wing_area_ft2: Wing reference area (ft^2)
        CD0: Zero-lift drag coefficient (calibrated)
        AR: Wing aspect ratio
        e: Oswald span efficiency factor (calibrated)
        tsfc_ref: Reference cruise TSFC [lb/(lbf-hr)]
        k_adj: TSFC calibration adjustment factor
        descent_rate_fpm: Descent rate in ft/min (default 2000)
        idle_fraction: Fraction of cruise fuel flow during idle descent
                       (default 0.10, i.e. 10% of cruise thrust fuel flow)

    Returns:
        dict with:
            fuel_burned_lb: Fuel consumed during descent
            distance_nm: Horizontal distance covered during descent
            time_hr: Descent time in hours
    """
    if h_start_ft <= h_target_ft:
        return {"fuel_burned_lb": 0.0, "distance_nm": 0.0, "time_hr": 0.0}

    delta_h = h_start_ft - h_target_ft

    # Time to descend
    time_min = delta_h / descent_rate_fpm
    time_hr = time_min / 60.0

    # Compute cruise fuel flow at mid-descent altitude for scaling
    h_mid = (h_start_ft + h_target_ft) / 2.0
    conds = performance.cruise_conditions(
        W_start_lb, h_mid, mach_descent, wing_area_ft2,
        CD0, AR, e, tsfc_ref, k_adj
    )
    cruise_fuel_flow_lbhr = conds["drag_lbf"] * conds["tsfc"]

    # Idle descent fuel = idle_fraction * cruise_fuel_flow * time
    descent_fuel = idle_fraction * cruise_fuel_flow_lbhr * time_hr

    # Horizontal distance: TAS at mid-descent altitude * time
    a_mid = atmosphere.speed_of_sound(h_mid)
    V_fps = mach_descent * a_mid
    V_ktas = V_fps * 3600.0 / NM_TO_FT
    distance_nm = V_ktas * time_hr

    return {
        "fuel_burned_lb": descent_fuel,
        "distance_nm": distance_nm,
        "time_hr": time_hr,
    }


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


def simulate_mission2_sampling(ac, cal, payload_lb=52_000, distance_nm=4_200,
                                h_low_ft=5_000, max_cycles=50):
    """Simulate Mission 2: Vertical atmospheric sampling (NZCH -> SCCI).

    Route: Christchurch, NZ (NZCH) to Punta Arenas, Chile (SCCI)
    Distance: ~4,200 nmi, Payload: 52,000 lb
    Profile: Repeating sawtooth climb-descend cycles.

    The aircraft repeatedly climbs from h_low_ft to its weight-limited
    ceiling, then descends back to h_low_ft. As fuel burns off, the
    aircraft gets lighter and can reach higher altitudes on each successive
    cycle. The mission continues until total distance >= distance_nm
    or fuel is exhausted.

    Fuel budget: Explicit reserves only (no f_oh) — per
    PHASE2_STEP1_RECONCILIATION.md.

    For aircraft that cannot carry the full payload (GV, P-8), computes
    fleet sizing and aggregate costs.

    Args:
        ac: Normalized aircraft data dict from loader
        cal: Calibration result dict (CD0, e, k_adj, etc.)
        payload_lb: Required total payload in lbf (default 52,000)
        distance_nm: Total mission distance in nmi (default 4,200)
        h_low_ft: Bottom altitude for sawtooth cycles (ft, default 5,000)
        max_cycles: Safety limit on cycle count (default 50)

    Returns:
        dict with feasibility, per-aircraft results, fleet aggregate,
        cycle details, and altitude profile data.
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

    # --- Step 3: Fuel budget (explicit reserves, no f_oh) ---
    CD0 = cal["CD0"]
    e = cal["e"]
    k_adj = cal["k_adj"]

    reserve_fuel = performance.compute_reserve_fuel(
        fuel_available, ac, CD0, e, k_adj
    )
    mission_fuel = fuel_available - reserve_fuel
    if mission_fuel <= 0:
        return _infeasible_result(ac, cal, payload_lb, actual_payload, n_aircraft,
                                  "No mission fuel after reserve deduction")

    # --- Step 4: Mission parameters ---
    # The hard ceiling is a structural/pressurization limit that the aircraft
    # must not exceed. The climb target is set higher so that climb_segment()
    # finds the thrust-limited ceiling via the ROC < 100 ft/min criterion.
    # At heavy weights, the thrust-limited ceiling will be below the hard cap,
    # producing the progressive ceiling increase that is the key scientific
    # output of this mission. At lighter weights, the thrust-limited ceiling
    # exceeds the hard cap, so the cap governs.
    hard_ceiling = ac.get("service_ceiling_ft", 43_000)
    climb_ceiling = hard_ceiling + 5_000
    mach = ac["cruise_mach"]
    mach_climb = mach * 0.95
    mach_descent = mach * 0.90

    # --- Step 5: Sawtooth cycle simulation ---
    W_current = W_tow
    fuel_remaining = mission_fuel
    distance_covered = 0.0
    total_time_hr = 0.0
    cycles = []

    for cycle_num in range(1, max_cycles + 1):
        if fuel_remaining <= 0 or distance_covered >= distance_nm:
            break

        cycle_start_weight = W_current
        cycle_fuel = 0.0
        cycle_distance = 0.0
        cycle_time = 0.0

        # --- Climb phase ---
        climb_result = climb_segment(
            W_start_lb=W_current,
            h_start_ft=h_low_ft,
            h_target_ft=climb_ceiling,
            mach_climb=mach_climb,
            wing_area_ft2=ac["wing_area_ft2"],
            CD0=CD0, AR=ac["aspect_ratio"], e=e,
            tsfc_ref=ac["tsfc_cruise_ref"], k_adj=k_adj,
            thrust_slst_lbf=ac["thrust_per_engine_slst_lbf"],
            n_engines=ac["n_engines"],
        )

        # Apply hard ceiling cap (structural/pressurization limit).
        # The thrust-limited ceiling from climb_segment may be below or
        # above the hard cap. If below, the aircraft is thrust-limited
        # (heavy weight) — use the climb result as-is. If above, truncate
        # fuel/distance/time to the hard ceiling using the per-step data.
        raw_ceiling = climb_result["ceiling_ft"]
        if raw_ceiling <= hard_ceiling:
            # Thrust-limited: use climb result as-is
            climb_fuel = climb_result["fuel_burned_lb"]
            climb_dist = climb_result["distance_nm"]
            climb_time = climb_result["time_hr"]
            cycle_ceiling = raw_ceiling
        else:
            # Climbed past the hard cap — truncate at hard_ceiling
            cycle_ceiling = hard_ceiling
            climb_fuel = 0.0
            climb_dist = 0.0
            climb_time = 0.0
            for step in climb_result["steps"]:
                if step["h_end_ft"] <= hard_ceiling:
                    climb_fuel += step["fuel_lb"]
                    climb_dist += step["distance_nm"]
                    climb_time += step["time_hr"]
                else:
                    # Partial step crossing the hard ceiling
                    if step["h_start_ft"] < hard_ceiling:
                        frac = ((hard_ceiling - step["h_start_ft"])
                                / (step["h_end_ft"] - step["h_start_ft"]))
                        climb_fuel += step["fuel_lb"] * frac
                        climb_dist += step["distance_nm"] * frac
                        climb_time += step["time_hr"] * frac
                    break

        # Zero-progress guard: if the aircraft can't climb above h_low
        # (e.g., because calibrated CD0 is so high that drag exceeds
        # thrust at all altitudes), the cycle produces zero distance
        # and zero fuel burn. Break to avoid an infinite loop.
        if climb_dist <= 0 and climb_fuel <= 0:
            break

        # Check if climb exceeds remaining fuel
        if climb_fuel > fuel_remaining:
            # Partial climb — estimate fraction completed
            frac = fuel_remaining / climb_fuel if climb_fuel > 0 else 0
            climb_fuel = fuel_remaining
            climb_dist *= frac
            climb_time *= frac
            cycle_ceiling = h_low_ft + (cycle_ceiling - h_low_ft) * frac

            cycle_fuel += climb_fuel
            cycle_distance += climb_dist
            cycle_time += climb_time
            W_current -= climb_fuel
            fuel_remaining = 0

            cycles.append({
                "cycle": cycle_num,
                "ceiling_ft": cycle_ceiling,
                "climb_fuel_lb": climb_fuel,
                "climb_distance_nm": climb_dist,
                "climb_time_hr": climb_time,
                "descent_fuel_lb": 0.0,
                "descent_distance_nm": 0.0,
                "descent_time_hr": 0.0,
                "total_fuel_lb": cycle_fuel,
                "total_distance_nm": cycle_distance,
                "total_time_hr": cycle_time,
                "weight_start_lb": cycle_start_weight,
                "weight_end_lb": W_current,
                "partial": True,
            })
            distance_covered += cycle_distance
            total_time_hr += cycle_time
            break

        # Full climb completed
        W_current -= climb_fuel
        fuel_remaining -= climb_fuel
        cycle_fuel += climb_fuel
        cycle_distance += climb_dist
        cycle_time += climb_time

        # Check if distance goal reached during climb
        if distance_covered + cycle_distance >= distance_nm:
            cycles.append({
                "cycle": cycle_num,
                "ceiling_ft": cycle_ceiling,
                "climb_fuel_lb": climb_fuel,
                "climb_distance_nm": climb_dist,
                "climb_time_hr": climb_time,
                "descent_fuel_lb": 0.0,
                "descent_distance_nm": 0.0,
                "descent_time_hr": 0.0,
                "total_fuel_lb": cycle_fuel,
                "total_distance_nm": cycle_distance,
                "total_time_hr": cycle_time,
                "weight_start_lb": cycle_start_weight,
                "weight_end_lb": W_current,
                "partial": True,
            })
            distance_covered += cycle_distance
            total_time_hr += cycle_time
            break

        # --- Descent phase ---
        descent_result = descend_segment(
            W_start_lb=W_current,
            h_start_ft=cycle_ceiling,
            h_target_ft=h_low_ft,
            mach_descent=mach_descent,
            wing_area_ft2=ac["wing_area_ft2"],
            CD0=CD0, AR=ac["aspect_ratio"], e=e,
            tsfc_ref=ac["tsfc_cruise_ref"], k_adj=k_adj,
        )

        descent_fuel = descent_result["fuel_burned_lb"]
        descent_dist = descent_result["distance_nm"]
        descent_time = descent_result["time_hr"]

        # Check if descent exceeds remaining fuel
        if descent_fuel > fuel_remaining:
            frac = fuel_remaining / descent_fuel if descent_fuel > 0 else 0
            descent_fuel = fuel_remaining
            descent_dist *= frac
            descent_time *= frac
            fuel_remaining = 0
        else:
            fuel_remaining -= descent_fuel

        W_current -= descent_fuel
        cycle_fuel += descent_fuel
        cycle_distance += descent_dist
        cycle_time += descent_time

        cycles.append({
            "cycle": cycle_num,
            "ceiling_ft": cycle_ceiling,
            "climb_fuel_lb": climb_fuel,
            "climb_distance_nm": climb_dist,
            "climb_time_hr": climb_time,
            "descent_fuel_lb": descent_fuel,
            "descent_distance_nm": descent_dist,
            "descent_time_hr": descent_time,
            "total_fuel_lb": cycle_fuel,
            "total_distance_nm": cycle_distance,
            "total_time_hr": cycle_time,
            "weight_start_lb": cycle_start_weight,
            "weight_end_lb": W_current,
            "partial": False,
        })
        distance_covered += cycle_distance
        total_time_hr += cycle_time

    # --- Step 6: Feasibility ---
    total_fuel_burned = mission_fuel - fuel_remaining
    feasible = distance_covered >= distance_nm and fuel_remaining >= -50

    # --- Step 7: Fuel cost metrics ---
    total_fuel_cost = fuel_cost(fuel_available)
    fuel_cost_metric = (
        total_fuel_cost / (actual_payload / 1000.0 * distance_nm)
        if actual_payload > 0 and distance_nm > 0 else float('inf')
    )

    # --- Step 8: Build altitude profile for plotting ---
    # Construct a list of (distance_nm, altitude_ft) points for the sawtooth
    profile_points = []
    cum_dist = 0.0
    for c in cycles:
        # Start of climb (at h_low)
        profile_points.append((cum_dist, h_low_ft))
        # Top of climb (at ceiling)
        cum_dist += c["climb_distance_nm"]
        profile_points.append((cum_dist, c["ceiling_ft"]))
        # Bottom of descent (at h_low), if descent occurred
        if c["descent_distance_nm"] > 0:
            cum_dist += c["descent_distance_nm"]
            profile_points.append((cum_dist, h_low_ft))

    # --- Step 9: Assemble per-aircraft result ---
    per_aircraft = {
        "takeoff_weight_lb": W_tow,
        "oew_lb": ac["OEW"],
        "payload_lb": actual_payload,
        "total_fuel_lb": fuel_available,
        "reserve_fuel_lb": reserve_fuel,
        "mission_fuel_lb": mission_fuel,
        "fuel_burned_lb": total_fuel_burned,
        "fuel_remaining_lb": max(fuel_remaining, 0),
        "distance_covered_nm": distance_covered,
        "total_time_hr": total_time_hr,
        "n_cycles": len(cycles),
        "cycles": cycles,
        "profile_points": profile_points,
        "peak_ceiling_ft": max(c["ceiling_ft"] for c in cycles) if cycles else 0,
        "initial_ceiling_ft": cycles[0]["ceiling_ft"] if cycles else 0,
        "final_ceiling_ft": cycles[-1]["ceiling_ft"] if cycles else 0,
        "fuel_cost_usd": total_fuel_cost,
        "fuel_cost_per_1000lb_nm": fuel_cost_metric,
    }

    # --- Step 10: Fleet aggregate ---
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
            _determine_infeasibility(distance_covered, distance_nm, fuel_remaining)
        ),
        "aircraft_name": ac.get("name", designation),
        "designation": designation,
        "payload_requested_lb": payload_lb,
        "payload_actual_lb": actual_payload,
        "n_aircraft": n_aircraft,
        "per_aircraft": per_aircraft,
        "aggregate": aggregate,
    }


# --- Low-altitude speed constant ---
# 250 KTAS is used for low-altitude endurance missions.
# At 1,500 ft, this corresponds to Mach ≈ 0.38.
# See ASSUMPTIONS_LOG.md entry F1.
LOW_ALT_KTAS = 250.0

# Convergence parameters for iterative fuel sizing
_FUEL_ITER_MAX = 20        # max iterations
_FUEL_ITER_TOL_LB = 50.0   # convergence tolerance in lb
_FUEL_MARGIN_FACTOR = 1.05  # 5% margin on mission fuel for safety


def _run_endurance(W_tow, mission_fuel, h_ft, mach, ac, CD0, AR, e,
                   tsfc_ref, k_adj, duration_hr, n_steps):
    """Run time-stepping endurance simulation at fixed altitude.

    This is the inner loop of Mission 3, extracted so it can be called
    repeatedly during iterative fuel sizing.

    Args:
        W_tow: Takeoff weight (OEW + payload + fuel) in lbf
        mission_fuel: Fuel available for mission (total - reserves) in lbf
        h_ft: Mission altitude in ft
        mach: Mission Mach number
        ac: Aircraft data dict (for wing_area_ft2)
        CD0, AR, e: Aerodynamic parameters
        tsfc_ref, k_adj: TSFC parameters
        duration_hr: Target duration in hours
        n_steps: Number of time integration steps

    Returns:
        dict with fuel_burned_lb, distance_nm, endurance_hr, steps list,
        avg_fuel_flow_lbhr, fuel_remaining_lb
    """
    dt_hr = duration_hr / n_steps
    W_current = W_tow
    fuel_remaining = mission_fuel
    total_fuel_burned = 0.0
    total_distance_nm = 0.0
    actual_endurance_hr = 0.0
    steps = []

    for step_num in range(n_steps):
        conds = performance.cruise_conditions(
            W_current, h_ft, mach,
            ac["wing_area_ft2"], CD0, AR, e, tsfc_ref, k_adj
        )

        fuel_flow_lbhr = conds["drag_lbf"] * conds["tsfc"]
        fuel_this_step = fuel_flow_lbhr * dt_hr

        # Fuel exhaustion — partial step
        if fuel_this_step > fuel_remaining:
            partial_dt_hr = (fuel_remaining / fuel_flow_lbhr
                             if fuel_flow_lbhr > 0 else 0)
            partial_dist_nm = conds["V_ktas"] * partial_dt_hr
            steps.append({
                "step": step_num,
                "time_start_hr": actual_endurance_hr,
                "time_end_hr": actual_endurance_hr + partial_dt_hr,
                "W_start_lb": W_current,
                "W_end_lb": W_current - fuel_remaining,
                "fuel_burned_lb": fuel_remaining,
                "distance_nm": partial_dist_nm,
                "fuel_flow_lbhr": fuel_flow_lbhr,
                "altitude_ft": h_ft,
                "mach": mach,
                "V_ktas": conds["V_ktas"],
                "CL": conds["CL"],
                "CD": conds["CD"],
                "L_D": conds["L_D"],
            })
            total_fuel_burned += fuel_remaining
            total_distance_nm += partial_dist_nm
            actual_endurance_hr += partial_dt_hr
            fuel_remaining = 0.0
            break

        # Full step
        dist_this_step = conds["V_ktas"] * dt_hr
        steps.append({
            "step": step_num,
            "time_start_hr": actual_endurance_hr,
            "time_end_hr": actual_endurance_hr + dt_hr,
            "W_start_lb": W_current,
            "W_end_lb": W_current - fuel_this_step,
            "fuel_burned_lb": fuel_this_step,
            "distance_nm": dist_this_step,
            "fuel_flow_lbhr": fuel_flow_lbhr,
            "altitude_ft": h_ft,
            "mach": mach,
            "V_ktas": conds["V_ktas"],
            "CL": conds["CL"],
            "CD": conds["CD"],
            "L_D": conds["L_D"],
        })
        total_fuel_burned += fuel_this_step
        total_distance_nm += dist_this_step
        actual_endurance_hr += dt_hr
        W_current -= fuel_this_step
        fuel_remaining -= fuel_this_step

    return {
        "fuel_burned_lb": total_fuel_burned,
        "distance_nm": total_distance_nm,
        "endurance_hr": actual_endurance_hr,
        "steps": steps,
        "fuel_remaining_lb": max(fuel_remaining, 0),
        "avg_fuel_flow_lbhr": (total_fuel_burned / actual_endurance_hr
                               if actual_endurance_hr > 0 else 0),
    }


def simulate_mission3_low_altitude(ac, cal, payload_lb=30_000,
                                    duration_hr=8.0, h_mission_ft=1_500,
                                    n_steps=40):
    """Simulate Mission 3: Low-altitude smoke survey endurance mission.

    Region: Central United States (Arkansas-Missouri area)
    Duration: 8 hours, Payload: 30,000 lb, Altitude: ~1,500 ft AGL
    Profile: Extended low-altitude cruise for forest fire particulate sampling.

    The aircraft cruises at fixed low altitude for the full mission duration.
    The primary question is whether the aircraft has enough fuel for 8 hours
    of low-altitude endurance. Distance covered is an output, not a target.

    Fuel loading is mission-sized: the aircraft loads only enough fuel to
    complete the 8-hour endurance plus reserves, not maximum fuel. This is
    computed iteratively because fuel weight affects drag which affects burn
    rate. See ASSUMPTIONS_LOG.md entry F3.

    Low-altitude cruise uses a reduced speed (250 KTAS / Mach ≈ 0.38) to
    stay within structural speed limits (VMO). Climb/descent to 1,500 ft is
    negligible and ignored.

    Fuel budget: Explicit reserves only (no f_oh) — per
    PHASE2_STEP1_RECONCILIATION.md.

    For aircraft that cannot carry the full payload (GV, P-8), computes
    fleet sizing and aggregate costs.

    Args:
        ac: Normalized aircraft data dict from loader
        cal: Calibration result dict (CD0, e, k_adj, etc.)
        payload_lb: Required total payload in lbf (default 30,000)
        duration_hr: Mission duration in hours (default 8.0)
        h_mission_ft: Mission altitude in ft AGL (default 1,500)
        n_steps: Number of time integration steps (default 40)

    Returns:
        dict with feasibility, per-aircraft results, fleet aggregate,
        and time-series data for plotting.
    """
    designation = ac["designation"]

    # --- Step 1: Fleet sizing ---
    actual_payload = min(payload_lb, ac["max_payload"])
    if actual_payload < payload_lb:
        n_aircraft = math.ceil(payload_lb / ac["max_payload"])
        actual_payload = payload_lb / n_aircraft
    else:
        n_aircraft = 1

    # --- Step 2: Maximum fuel capacity check ---
    max_fuel_available = min(
        ac["MTOW"] - ac["OEW"] - actual_payload, ac["max_fuel"]
    )
    if max_fuel_available <= 0:
        return _infeasible_result(ac, cal, payload_lb, actual_payload,
                                  n_aircraft,
                                  "Cannot carry payload within MTOW")

    # --- Step 3: Calibration parameters ---
    CD0 = cal["CD0"]
    e_oswald = cal["e"]
    k_adj = cal["k_adj"]

    # --- Step 4: Mission parameters ---
    a_mission = atmosphere.speed_of_sound(h_mission_ft)
    V_mission_fps = LOW_ALT_KTAS * NM_TO_FT / 3600.0
    mach_mission = V_mission_fps / a_mission

    # --- Step 5: Iterative fuel sizing ---
    # Goal: find the minimum fuel load that satisfies 8-hour endurance + reserves.
    #
    # The iteration is needed because fuel weight affects drag, which affects
    # burn rate, which affects how much fuel is needed. We converge on the
    # total fuel loaded.
    #
    # Algorithm:
    # 1. Estimate burn rate at light weight (no fuel) → initial mission fuel
    # 2. Add reserves → total fuel candidate
    # 3. Simulate at that fuel load → actual burn
    # 4. If feasible: next estimate = actual burn (+ margin)
    #    If not feasible: scale up proportionally
    # 5. Converge when successive total fuel values stabilize

    W_empty_with_payload = ac["OEW"] + actual_payload

    # Initial estimate: burn rate at empty weight (lower bound on actual burn)
    conds_light = performance.cruise_conditions(
        W_empty_with_payload, h_mission_ft, mach_mission,
        ac["wing_area_ft2"], CD0, ac["aspect_ratio"], e_oswald,
        ac["tsfc_cruise_ref"], k_adj
    )
    initial_burn_rate = conds_light["drag_lbf"] * conds_light["tsfc"]
    mission_fuel_est = initial_burn_rate * duration_hr * _FUEL_MARGIN_FACTOR

    converged = False
    prev_total_fuel = 0.0

    for iteration in range(_FUEL_ITER_MAX):
        # Build total fuel = mission estimate + reserves
        # First get a reserve estimate for this fuel level
        reserve_fuel = performance.compute_reserve_fuel(
            mission_fuel_est * 1.2,  # rough total for reserve calc
            ac, CD0, e_oswald, k_adj
        )
        total_fuel_candidate = mission_fuel_est + reserve_fuel

        # Cap at max fuel capacity
        total_fuel_candidate = min(total_fuel_candidate, max_fuel_available)

        # Recompute reserves properly for the capped total
        reserve_fuel = performance.compute_reserve_fuel(
            total_fuel_candidate, ac, CD0, e_oswald, k_adj
        )
        mission_fuel_candidate = total_fuel_candidate - reserve_fuel
        if mission_fuel_candidate <= 0:
            return _infeasible_result(
                ac, cal, payload_lb, actual_payload, n_aircraft,
                "No mission fuel after reserve deduction"
            )

        # Check convergence: has total fuel stabilized?
        if abs(total_fuel_candidate - prev_total_fuel) < _FUEL_ITER_TOL_LB:
            # Run one final simulation at this fuel load
            W_tow_candidate = W_empty_with_payload + total_fuel_candidate
            sim = _run_endurance(
                W_tow_candidate, mission_fuel_candidate,
                h_mission_ft, mach_mission, ac, CD0, ac["aspect_ratio"],
                e_oswald, ac["tsfc_cruise_ref"], k_adj, duration_hr, n_steps
            )
            converged = True
            break

        prev_total_fuel = total_fuel_candidate

        # Simulate endurance at this fuel load
        W_tow_candidate = W_empty_with_payload + total_fuel_candidate
        sim = _run_endurance(
            W_tow_candidate, mission_fuel_candidate,
            h_mission_ft, mach_mission, ac, CD0, ac["aspect_ratio"],
            e_oswald, ac["tsfc_cruise_ref"], k_adj, duration_hr, n_steps
        )

        actual_burn = sim["fuel_burned_lb"]

        if sim["endurance_hr"] >= duration_hr - 0.01:
            # Feasible — tighten estimate to actual burn + small margin
            mission_fuel_est = actual_burn * _FUEL_MARGIN_FACTOR
        else:
            # Not enough fuel — scale up
            if actual_burn > 0 and sim["endurance_hr"] > 0:
                scale = duration_hr / sim["endurance_hr"]
                mission_fuel_est = actual_burn * scale * _FUEL_MARGIN_FACTOR
            else:
                mission_fuel_est *= 2.0

        # Safety: don't exceed max capacity
        reserve_check = performance.compute_reserve_fuel(
            max_fuel_available, ac, CD0, e_oswald, k_adj
        )
        max_mission_fuel = max_fuel_available - reserve_check
        if mission_fuel_est > max_mission_fuel:
            mission_fuel_est = max_mission_fuel

    # If not converged, use max fuel as fallback
    if not converged:
        total_fuel_candidate = max_fuel_available
        reserve_fuel = performance.compute_reserve_fuel(
            total_fuel_candidate, ac, CD0, e_oswald, k_adj
        )
        mission_fuel_candidate = total_fuel_candidate - reserve_fuel
        W_tow_candidate = W_empty_with_payload + total_fuel_candidate
        sim = _run_endurance(
            W_tow_candidate, mission_fuel_candidate,
            h_mission_ft, mach_mission, ac, CD0, ac["aspect_ratio"],
            e_oswald, ac["tsfc_cruise_ref"], k_adj, duration_hr, n_steps
        )

    # Final values
    fuel_loaded = total_fuel_candidate
    W_tow = W_tow_candidate
    mission_fuel = mission_fuel_candidate

    total_fuel_burned = sim["fuel_burned_lb"]
    total_distance_nm = sim["distance_nm"]
    actual_endurance_hr = sim["endurance_hr"]
    steps = sim["steps"]
    fuel_remaining = sim["fuel_remaining_lb"]

    # --- Step 6: Feasibility ---
    feasible = actual_endurance_hr >= duration_hr - 0.01

    # --- Step 7: Fuel cost metrics ---
    # Cost is on fuel loaded (all fuel must be purchased)
    total_fuel_cost = fuel_cost(fuel_loaded)
    fuel_cost_metric = (
        total_fuel_cost / (actual_payload / 1000.0 * total_distance_nm)
        if actual_payload > 0 and total_distance_nm > 0 else float('inf')
    )

    # --- Step 8: Assemble per-aircraft result ---
    per_aircraft = {
        "takeoff_weight_lb": W_tow,
        "oew_lb": ac["OEW"],
        "payload_lb": actual_payload,
        "total_fuel_lb": fuel_loaded,
        "reserve_fuel_lb": reserve_fuel,
        "mission_fuel_lb": mission_fuel,
        "fuel_burned_lb": total_fuel_burned,
        "fuel_remaining_lb": fuel_remaining,
        "endurance_hr": actual_endurance_hr,
        "distance_covered_nm": total_distance_nm,
        "altitude_ft": h_mission_ft,
        "mach": mach_mission,
        "V_ktas": LOW_ALT_KTAS,
        "avg_fuel_flow_lbhr": sim["avg_fuel_flow_lbhr"],
        "steps": steps,
        "fuel_cost_usd": total_fuel_cost,
        "fuel_cost_per_1000lb_nm": fuel_cost_metric,
        "max_fuel_available_lb": max_fuel_available,
        "fuel_sizing_converged": converged,
    }

    # --- Step 9: Fleet aggregate ---
    if n_aircraft > 1:
        fleet_fuel_cost = n_aircraft * total_fuel_cost
        aggregate = {
            "n_aircraft": n_aircraft,
            "total_payload_lb": n_aircraft * actual_payload,
            "total_fuel_lb": n_aircraft * fuel_loaded,
            "total_fuel_burned_lb": n_aircraft * total_fuel_burned,
            "total_fuel_cost_usd": fleet_fuel_cost,
            "fuel_cost_per_1000lb_nm": (
                fleet_fuel_cost / (payload_lb / 1000.0 * total_distance_nm)
                if payload_lb > 0 and total_distance_nm > 0 else float('inf')
            ),
        }
    else:
        aggregate = None

    return {
        "feasible": feasible,
        "infeasible_reason": (
            None if feasible else
            f"Fuel exhausted after {actual_endurance_hr:.1f} hr "
            f"(required {duration_hr:.1f} hr)"
        ),
        "aircraft_name": ac.get("name", designation),
        "designation": designation,
        "payload_requested_lb": payload_lb,
        "payload_actual_lb": actual_payload,
        "n_aircraft": n_aircraft,
        "per_aircraft": per_aircraft,
        "aggregate": aggregate,
    }
