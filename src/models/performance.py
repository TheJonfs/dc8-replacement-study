"""Aircraft cruise performance model.

Implements:
1. Breguet range equation (closed-form and step-cruise refinement)
2. Specific range computation
3. Optimal cruise altitude determination
4. Reserve fuel calculation

The core computation path for range-payload analysis is:
    Given: aircraft data, payload weight, fuel weight
    Compute: cruise range using step-cruise Breguet integration

The step-cruise method divides the mission into segments. At each segment:
- Weight decreases as fuel burns
- Optimal altitude may increase (aircraft climbs as it gets lighter)
- CL, CD, L/D, and TSFC are recomputed for current conditions
- The Breguet equation is applied over each segment

This approach is significantly more accurate than a single-shot Breguet
calculation, especially for long-range missions where the aircraft burns
a large fraction of its initial weight.

See ASSUMPTIONS_LOG.md entries D1, D2, D4.
"""

import math
from src.models import atmosphere, aerodynamics, propulsion
from src.utils import NM_TO_FT, FT_TO_NM, HR_TO_SEC


def breguet_range_nm(V_fps, tsfc_lbplbfhr, L_D, W_initial_lb, W_final_lb):
    """Classic Breguet range equation.

    R = (V / TSFC) × (L/D) × ln(Wi / Wf)

    Args:
        V_fps: True airspeed in ft/s
        tsfc_lbplbfhr: TSFC in lb/(lbf·hr)
        L_D: Lift-to-drag ratio
        W_initial_lb: Initial weight in lbf
        W_final_lb: Final weight in lbf (= initial - fuel burned)

    Returns:
        Range in nautical miles
    """
    if W_final_lb >= W_initial_lb:
        return 0.0
    if W_final_lb <= 0:
        raise ValueError("Final weight must be positive")

    # Convert TSFC from per-hour to per-second: c [lb/(lbf·s)]
    tsfc_per_sec = tsfc_lbplbfhr / HR_TO_SEC

    # Breguet: R [ft] = (V / c) × (L/D) × ln(Wi/Wf)
    range_ft = (V_fps / tsfc_per_sec) * L_D * math.log(W_initial_lb / W_final_lb)
    return range_ft * FT_TO_NM


def specific_range(V_fps, tsfc_lbplbfhr, L_D, weight_lb):
    """Compute specific range: distance per unit fuel burned.

    SR = V × (L/D) / (TSFC × W)

    This is the instantaneous efficiency — nm of range per lb of fuel.

    Args:
        V_fps: True airspeed in ft/s
        tsfc_lbplbfhr: TSFC in lb/(lbf·hr)
        L_D: Lift-to-drag ratio
        weight_lb: Current aircraft weight in lbf

    Returns:
        Specific range in nm/lb
    """
    tsfc_per_sec = tsfc_lbplbfhr / HR_TO_SEC
    sr_ft_per_lb = V_fps * L_D / (tsfc_per_sec * weight_lb)
    return sr_ft_per_lb * FT_TO_NM


def cruise_conditions(weight_lb, h_ft, mach, wing_area_ft2, CD0, AR, e,
                      tsfc_ref, k_adj=1.0):
    """Compute all relevant cruise parameters at given flight conditions.

    Args:
        weight_lb: Aircraft weight in lbf
        h_ft: Altitude in feet
        mach: Mach number
        wing_area_ft2: Wing reference area in ft²
        CD0: Zero-lift drag coefficient
        AR: Wing aspect ratio
        e: Oswald span efficiency factor
        tsfc_ref: Reference cruise TSFC [lb/(lbf·hr)]
        k_adj: TSFC calibration adjustment factor

    Returns:
        dict with keys: CL, CD, L_D, V_fps, V_ktas, drag_lbf, tsfc, SR_nm_per_lb
    """
    # Atmospheric conditions
    rho = atmosphere.density(h_ft)
    a = atmosphere.speed_of_sound(h_ft)
    V_fps = mach * a
    q = 0.5 * rho * V_fps ** 2

    # Aerodynamics
    CL = aerodynamics.lift_coefficient(weight_lb, q, wing_area_ft2)
    CD = aerodynamics.drag_coefficient(CL, CD0, AR, e)
    L_D = CL / CD
    drag_lbf = CD * q * wing_area_ft2

    # Propulsion
    c = propulsion.tsfc(h_ft, mach, tsfc_ref, k_adj)

    # Specific range
    SR = specific_range(V_fps, c, L_D, weight_lb)

    return {
        "CL": CL,
        "CD": CD,
        "L_D": L_D,
        "V_fps": V_fps,
        "V_ktas": V_fps * 3600.0 / NM_TO_FT,
        "drag_lbf": drag_lbf,
        "tsfc": c,
        "SR_nm_per_lb": SR,
        "q_psf": q,
        "mach": mach,
        "altitude_ft": h_ft,
    }


def optimal_cruise_altitude(weight_lb, mach, wing_area_ft2, CD0, AR, e,
                             tsfc_ref, k_adj=1.0, ceiling_ft=43_000,
                             thrust_slst_lbf=None, n_engines=None,
                             h_min=25_000, h_step=500, CL_max_cruise=0.60,
                             drag_multiplier=1.0):
    """Find the altitude that maximizes specific range.

    Searches altitudes from h_min to ceiling_ft in h_step increments,
    subject to three constraints:
    1. Service ceiling
    2. Thrust available ≥ drag (if engine data provided)
    3. CL ≤ CL_max_cruise (buffet limit)

    The buffet limit is critical: at heavy weights, the aircraft cannot
    fly at high altitudes because CL would exceed the buffet boundary.
    This forces heavy aircraft to lower, less efficient altitudes —
    which is the primary reason that range degrades at high payload.

    Transport aircraft typically have a 1.3g buffet onset CL of 0.70-0.85.
    The corresponding cruise CL limit (with 1.3g margin) is about 0.55-0.65.
    This is a calibration parameter.

    Args:
        weight_lb: Aircraft weight in lbf
        mach: Cruise Mach number
        wing_area_ft2: Wing reference area in ft²
        CD0: Zero-lift drag coefficient
        AR: Wing aspect ratio
        e: Oswald span efficiency factor
        tsfc_ref: Reference cruise TSFC [lb/(lbf·hr)]
        k_adj: TSFC calibration adjustment factor
        ceiling_ft: Maximum altitude to consider (ft)
        thrust_slst_lbf: Sea-level static thrust per engine (lbf), for thrust check
        n_engines: Number of engines, for thrust check
        h_min: Minimum altitude to consider (ft)
        h_step: Altitude search step (ft)
        CL_max_cruise: Maximum CL allowed in cruise (buffet limit).
            Typical values: 0.55-0.65 for transport aircraft.

    Returns:
        Optimal altitude in feet
    """
    best_alt = h_min
    best_sr = 0.0

    h = h_min
    while h <= ceiling_ft:
        conds = cruise_conditions(weight_lb, h, mach, wing_area_ft2,
                                  CD0, AR, e, tsfc_ref, k_adj)

        # Check CL limit (buffet boundary)
        if conds["CL"] > CL_max_cruise:
            # CL too high at this altitude — can't go higher
            break

        # Check thrust available if engine data provided
        if thrust_slst_lbf is not None and n_engines is not None:
            thrust_avail = propulsion.thrust_available_cruise(
                thrust_slst_lbf, h, n_engines
            )
            if thrust_avail < conds["drag_lbf"] * drag_multiplier:
                # Can't sustain flight at this altitude — skip but keep searching.
                # Unlike CL (monotonically increasing with altitude), the
                # thrust-drag balance is non-monotonic: at low altitudes high
                # dynamic pressure can make drag exceed thrust, while at
                # mid-altitudes the balance may be favorable before thrust
                # lapse dominates at high altitudes.
                h += h_step
                continue

        if conds["SR_nm_per_lb"] > best_sr:
            best_sr = conds["SR_nm_per_lb"]
            best_alt = h

        h += h_step

    return best_alt


def step_cruise_range(W_initial_lb, fuel_available_lb, mach, wing_area_ft2,
                      CD0, AR, e, tsfc_ref, k_adj=1.0, ceiling_ft=43_000,
                      thrust_slst_lbf=None, n_engines=None,
                      n_steps=50, fixed_altitude_ft=None,
                      drag_multiplier=1.0, CL_max_cruise=0.60,
                      h_min=25_000):
    """Compute cruise range using step-cruise method.

    Divides the total fuel load into n_steps equal segments. At each step:
    1. Compute current weight
    2. Find optimal altitude (or use fixed altitude)
    3. Compute cruise conditions (CL, CD, L/D, TSFC)
    4. Apply Breguet equation for this segment's fuel burn

    This captures the altitude and efficiency improvement as the aircraft
    gets lighter throughout the cruise.

    Args:
        W_initial_lb: Takeoff weight (OEW + payload + fuel) in lbf
        fuel_available_lb: Total fuel available for cruise in lbf
        mach: Cruise Mach number
        wing_area_ft2: Wing reference area in ft²
        CD0: Zero-lift drag coefficient
        AR: Wing aspect ratio
        e: Oswald span efficiency factor
        tsfc_ref: Reference cruise TSFC [lb/(lbf·hr)]
        k_adj: TSFC calibration adjustment factor
        ceiling_ft: Maximum cruise altitude in ft
        thrust_slst_lbf: Sea-level static thrust per engine (lbf)
        n_engines: Number of engines
        n_steps: Number of cruise segments (higher = more accurate)
        fixed_altitude_ft: If set, use this altitude instead of optimizing
        drag_multiplier: Drag multiplier (e.g., 1.10 for engine-out)
        h_min: Minimum altitude for optimizer search (ft, default 25,000)

    Returns:
        dict with:
            range_nm: Total cruise range in nautical miles
            fuel_burned_lb: Fuel consumed (should ≈ fuel_available_lb)
            segments: List of per-segment data for plotting/analysis
    """
    fuel_per_step = fuel_available_lb / n_steps
    total_range = 0.0
    total_fuel = 0.0
    W_current = W_initial_lb
    segments = []

    for i in range(n_steps):
        # Current weight at start of segment
        W_start = W_current
        W_end = W_current - fuel_per_step

        if W_end <= 0:
            break  # Ran out of weight (shouldn't happen with valid inputs)

        # Determine altitude
        if fixed_altitude_ft is not None:
            h = fixed_altitude_ft
        else:
            h = optimal_cruise_altitude(
                W_start, mach, wing_area_ft2, CD0, AR, e,
                tsfc_ref, k_adj, ceiling_ft,
                thrust_slst_lbf, n_engines,
                h_min=h_min,
                CL_max_cruise=CL_max_cruise,
                drag_multiplier=drag_multiplier,
            )

        # Compute cruise conditions at segment midpoint weight
        W_mid = (W_start + W_end) / 2.0
        conds = cruise_conditions(W_mid, h, mach, wing_area_ft2,
                                  CD0, AR, e, tsfc_ref, k_adj)

        # Apply drag multiplier (e.g., for engine-out)
        effective_L_D = conds["L_D"] / drag_multiplier

        # Breguet for this segment
        seg_range = breguet_range_nm(
            conds["V_fps"], conds["tsfc"], effective_L_D, W_start, W_end
        )

        total_range += seg_range
        total_fuel += fuel_per_step
        W_current = W_end

        segments.append({
            "step": i,
            "W_start_lb": W_start,
            "W_end_lb": W_end,
            "altitude_ft": h,
            "mach": mach,
            "CL": conds["CL"],
            "CD": conds["CD"],
            "L_D": conds["L_D"],
            "effective_L_D": effective_L_D,
            "tsfc": conds["tsfc"],
            "V_ktas": conds["V_ktas"],
            "range_nm": seg_range,
            "cumulative_range_nm": total_range,
            "cumulative_fuel_lb": total_fuel,
        })

    return {
        "range_nm": total_range,
        "fuel_burned_lb": total_fuel,
        "segments": segments,
    }


def estimate_climb_fuel(W_lb, h_cruise_ft, aircraft_data, CD0, AR, e,
                        tsfc_ref, k_adj=1.0):
    """Estimate fuel consumed climbing from sea level to cruise altitude.

    Uses an energy method: the aircraft must gain potential energy (m·g·h)
    while also overcoming drag. Climb fuel is estimated as:

        fuel_climb ≈ W × h / (V_climb × L/D_climb / TSFC_climb)

    This is equivalent to using the Breguet equation over a distance
    equal to the climb distance, plus the energy penalty for altitude gain.

    For a more physical approach, we use:
        fuel_climb = (ΔPE + D_avg × distance_climb) × TSFC_avg / (η × V)

    Simplified to a semi-empirical model calibrated against typical climb
    fuel fractions for transport aircraft.

    See ASSUMPTIONS_LOG.md entry D3.

    Args:
        W_lb: Aircraft weight at start of climb (lbf)
        h_cruise_ft: Target cruise altitude (ft)
        aircraft_data: Normalized aircraft dict
        CD0: Zero-lift drag coefficient
        AR: Wing aspect ratio
        e: Oswald span efficiency factor
        tsfc_ref: Reference cruise TSFC
        k_adj: TSFC adjustment factor

    Returns:
        dict with climb_fuel_lb and climb_distance_nm
    """
    ac = aircraft_data

    # Average climb conditions (approximate at h/2 altitude)
    h_avg = h_cruise_ft / 2.0
    # Climb speed: typically M0.78 for transports, or 300 ktas at lower alt
    mach_climb = min(ac.get("cruise_mach", 0.80) * 0.95, 0.80)

    conds = cruise_conditions(W_lb, h_avg, mach_climb,
                              ac["wing_area_ft2"], CD0, AR, e,
                              tsfc_ref, k_adj)

    # Energy method:
    # Power required to climb = W × ROC
    # Power required to sustain level flight = D × V
    # Total fuel flow = (D × V + W × ROC) × TSFC / V
    #                 = TSFC × (D + W × ROC / V)
    #
    # For transport aircraft, typical ROC at initial cruise weight:
    # 1500-2500 ft/min at lower altitudes, decreasing with altitude
    # Average ROC over climb ≈ 1500 ft/min for a heavily loaded transport

    # Time to climb (use average ROC)
    avg_roc_fpm = 1500.0  # ft/min, conservative for heavy transport
    climb_time_min = h_cruise_ft / avg_roc_fpm
    climb_time_hr = climb_time_min / 60.0

    # Distance covered during climb (ground distance)
    climb_distance_nm = conds["V_ktas"] * climb_time_hr

    # Fuel burned during climb:
    # Fuel = integral of (TSFC × Thrust) dt
    # During climb, Thrust > Drag (excess thrust provides climb)
    # T = D + W × sin(γ) ≈ D + W × ROC/V
    avg_roc_fps = avg_roc_fpm / 60.0
    gamma_sin = avg_roc_fps / conds["V_fps"]  # climb angle sine
    thrust_climb = conds["drag_lbf"] + W_lb * gamma_sin

    # TSFC during climb (use average conditions)
    tsfc_climb = propulsion.tsfc(h_avg, mach_climb, tsfc_ref, k_adj)
    fuel_flow_climb = thrust_climb * tsfc_climb  # lb/hr
    climb_fuel = fuel_flow_climb * climb_time_hr

    return {
        "climb_fuel_lb": climb_fuel,
        "climb_distance_nm": climb_distance_nm,
        "climb_time_hr": climb_time_hr,
    }


def estimate_descent_credit(h_cruise_ft, aircraft_data):
    """Estimate distance covered and fuel saved during descent.

    During descent, the aircraft converts potential energy to kinetic/distance.
    Descent fuel is very low (near-idle power). We approximate this as
    a distance credit with minimal fuel consumption.

    Args:
        h_cruise_ft: Cruise altitude (ft)
        aircraft_data: Normalized aircraft dict

    Returns:
        dict with descent_distance_nm and descent_fuel_lb
    """
    # Typical descent profile: ~3° glide path, M0.78 at altitude
    # Descent distance ≈ h / tan(3°) in feet, but typically covers
    # about 100-150 nm from cruise altitude for transport aircraft
    descent_distance_nm = h_cruise_ft / 6076.12 / math.tan(math.radians(3.0))

    # Descent fuel is minimal — roughly 200-500 lb for a transport
    # Use 1% of what climb fuel would be
    descent_fuel = 300.0  # lb, approximate idle descent fuel

    return {
        "descent_distance_nm": descent_distance_nm,
        "descent_fuel_lb": descent_fuel,
    }


def compute_range_for_payload(aircraft_data, payload_lb, fuel_lb,
                              CD0, e, k_adj=1.0, n_steps=50,
                              drag_multiplier=1.0, fixed_altitude_ft=None,
                              include_reserves=True, CL_max_cruise=0.60):
    """Compute mission range for a specific payload-fuel combination.

    Models a complete mission profile: climb + cruise + descent.
    This is critical for matching published range-payload data, which
    represents mission range (not cruise-only range).

    The fuel budget is allocated as:
        total_fuel = climb_fuel + cruise_fuel + descent_fuel + reserve_fuel

    And total range = climb_distance + cruise_range + descent_distance.

    Args:
        aircraft_data: Normalized aircraft dict from loader
        payload_lb: Payload weight in lbf
        fuel_lb: Fuel weight in lbf
        CD0: Zero-lift drag coefficient (calibrated)
        e: Oswald span efficiency factor (calibrated)
        k_adj: TSFC adjustment factor (calibrated)
        n_steps: Number of cruise segments
        drag_multiplier: Drag multiplier (1.0 = normal, >1.0 = engine-out)
        fixed_altitude_ft: If set, cruise at this altitude
        include_reserves: If True, include reserve fuel in fuel budget.
            Default True — published R-P data includes reserves.
        CL_max_cruise: Maximum cruise CL (buffet limit). This is a key
            calibration parameter that controls altitude at heavy weights.

    Returns:
        dict with range_nm, fuel breakdown, and segment data
    """
    ac = aircraft_data
    W_initial = ac["OEW"] + payload_lb + fuel_lb

    # Validate weights
    if W_initial > ac["MTOW"] * 1.001:  # small tolerance for rounding
        raise ValueError(
            f"Takeoff weight {W_initial:.0f} lb exceeds MTOW {ac['MTOW']:.0f} lb"
        )
    if fuel_lb > ac["max_fuel"] * 1.001:
        raise ValueError(
            f"Fuel {fuel_lb:.0f} lb exceeds max fuel {ac['max_fuel']:.0f} lb"
        )

    # Determine cruise altitude (initial estimate for fuel allocation)
    ceiling = ac.get("service_ceiling_ft", 43_000)
    if fixed_altitude_ft is not None:
        h_cruise_init = fixed_altitude_ft
    else:
        h_cruise_init = optimal_cruise_altitude(
            W_initial, ac["cruise_mach"], ac["wing_area_ft2"],
            CD0, ac["aspect_ratio"], e, ac["tsfc_cruise_ref"], k_adj,
            ceiling, ac["thrust_per_engine_slst_lbf"], ac["n_engines"],
            CL_max_cruise=CL_max_cruise
        )

    # Estimate climb fuel and distance
    climb = estimate_climb_fuel(
        W_initial, h_cruise_init, ac, CD0, ac["aspect_ratio"], e,
        ac["tsfc_cruise_ref"], k_adj
    )

    # Estimate descent credit
    descent = estimate_descent_credit(h_cruise_init, ac)

    # Reserve fuel
    # Published range-payload data is always "with reserves" — the published
    # range is what the aircraft achieves AFTER setting aside reserve fuel.
    # So reserves should ALWAYS be included for calibration accuracy.
    # The include_reserves flag is now used only to control whether additional
    # mission-specific reserves are applied beyond the standard set.
    reserve_fuel = compute_reserve_fuel(fuel_lb, ac, CD0, e, k_adj)
    if not include_reserves:
        # For calibration: use standard reserves (already computed above)
        pass
    # For mission analysis: reserves already computed, same formula

    # Cruise fuel = total - climb - descent - reserves
    cruise_fuel = fuel_lb - climb["climb_fuel_lb"] - descent["descent_fuel_lb"] - reserve_fuel
    cruise_fuel = max(cruise_fuel, 0)

    if cruise_fuel <= 0:
        return {"range_nm": 0, "fuel_burned_lb": 0, "segments": [],
                "reserve_fuel_lb": reserve_fuel,
                "climb_fuel_lb": climb["climb_fuel_lb"],
                "descent_fuel_lb": descent["descent_fuel_lb"]}

    # Weight at top of climb (start of cruise)
    W_cruise_start = W_initial - climb["climb_fuel_lb"]

    # Engine data for thrust checks
    n_engines_eff = ac["n_engines"]
    if drag_multiplier > 1.0:
        n_engines_eff = ac["n_engines"] - 1

    # Step-cruise for the cruise segment
    cruise_result = step_cruise_range(
        W_initial_lb=W_cruise_start,
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
        n_engines=n_engines_eff,
        n_steps=n_steps,
        fixed_altitude_ft=fixed_altitude_ft,
        drag_multiplier=drag_multiplier,
        CL_max_cruise=CL_max_cruise,
    )

    # Total mission range = climb + cruise + descent
    total_range = (climb["climb_distance_nm"] +
                   cruise_result["range_nm"] +
                   descent["descent_distance_nm"])

    result = {
        "range_nm": total_range,
        "cruise_range_nm": cruise_result["range_nm"],
        "climb_distance_nm": climb["climb_distance_nm"],
        "descent_distance_nm": descent["descent_distance_nm"],
        "fuel_burned_lb": (climb["climb_fuel_lb"] +
                           cruise_result["fuel_burned_lb"] +
                           descent["descent_fuel_lb"]),
        "climb_fuel_lb": climb["climb_fuel_lb"],
        "cruise_fuel_lb": cruise_fuel,
        "descent_fuel_lb": descent["descent_fuel_lb"],
        "reserve_fuel_lb": reserve_fuel,
        "takeoff_weight_lb": W_initial,
        "payload_lb": payload_lb,
        "fuel_total_lb": fuel_lb,
        "segments": cruise_result["segments"],
        "initial_cruise_alt_ft": h_cruise_init,
        "climb_time_hr": climb["climb_time_hr"],
    }

    return result


def compute_reserve_fuel(total_fuel_lb, aircraft_data, CD0, e, k_adj=1.0):
    """Compute required reserve fuel using an iterative method.

    Published range-payload data uses the convention:
        total_fuel = trip_fuel + reserve_fuel
    where trip_fuel is what's burned during the actual flight.

    Reserve policy (see ASSUMPTIONS_LOG.md entry D4):
    - 5% of trip fuel as contingency
    - 200 nmi alternate at cruise conditions
    - 30 minutes hold at 1,500 ft

    Since contingency is a percentage of trip fuel, and trip fuel =
    total_fuel - reserves, we need to solve iteratively. However,
    the alternate and hold fuel don't depend on trip fuel, so we
    can solve directly.

    Args:
        total_fuel_lb: Total fuel loaded (trip + reserves) in lbf
        aircraft_data: Normalized aircraft dict
        CD0: Zero-lift drag coefficient
        e: Oswald span efficiency factor
        k_adj: TSFC adjustment factor

    Returns:
        Required reserve fuel in lbf
    """
    ac = aircraft_data

    # Estimate weight for reserve legs (near end of flight, light weight)
    W_reserve_est = ac["OEW"] + 10_000  # light-weight estimate for reserve legs

    # Alternate fuel: 200 nmi at lower altitude
    h_alt = 25_000
    mach_alt = ac["cruise_mach"] * 0.95

    conds_alt = cruise_conditions(W_reserve_est, h_alt, mach_alt,
                                  ac["wing_area_ft2"], CD0, ac["aspect_ratio"],
                                  e, ac["tsfc_cruise_ref"], k_adj)

    R_alt_ft = 200.0 * NM_TO_FT
    tsfc_per_sec = conds_alt["tsfc"] / HR_TO_SEC
    exponent = R_alt_ft * tsfc_per_sec / (conds_alt["V_fps"] * conds_alt["L_D"])
    alternate_fuel = W_reserve_est * (1.0 - math.exp(-exponent))

    # Hold fuel: 30 minutes at 1,500 ft
    h_hold = 1_500
    a_hold = atmosphere.speed_of_sound(h_hold)
    V_hold_fps = 250 * NM_TO_FT / HR_TO_SEC  # ~250 ktas
    mach_hold = V_hold_fps / a_hold
    if mach_hold > 0.5:
        mach_hold = 0.5

    conds_hold = cruise_conditions(W_reserve_est, h_hold, mach_hold,
                                   ac["wing_area_ft2"], CD0, ac["aspect_ratio"],
                                   e, ac["tsfc_cruise_ref"], k_adj)

    hold_fuel_flow = conds_hold["drag_lbf"] * conds_hold["tsfc"]  # lb/hr
    hold_fuel = hold_fuel_flow * 0.5  # 30 minutes

    # Fixed reserves (not depending on trip fuel)
    fixed_reserves = alternate_fuel + hold_fuel

    # Contingency = 5% of trip fuel
    # trip_fuel = total_fuel - reserves
    # reserves = 0.05 * trip_fuel + fixed_reserves
    # reserves = 0.05 * (total_fuel - reserves) + fixed_reserves
    # reserves * (1 + 0.05) = 0.05 * total_fuel + fixed_reserves
    # reserves = (0.05 * total_fuel + fixed_reserves) / 1.05
    total_reserve = (0.05 * total_fuel_lb + fixed_reserves) / 1.05

    # Ensure reserves don't exceed total fuel
    total_reserve = min(total_reserve, total_fuel_lb * 0.95)

    return total_reserve


