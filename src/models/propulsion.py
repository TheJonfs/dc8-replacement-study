"""Propulsion model for turbofan engine performance.

Models Thrust-Specific Fuel Consumption (TSFC) as a function of altitude
and Mach number using a simplified parametric approach:

    TSFC(h, M) = TSFC_ref × f_altitude(h) × f_mach(M) × k_adj

where:
    TSFC_ref    = published or estimated cruise reference TSFC [lb/(lbf·hr)]
    f_altitude  = altitude correction factor (improves up to tropopause)
    f_mach      = Mach number correction factor
    k_adj       = calibration adjustment factor (fitted to match range-payload data)

The altitude correction models the thermodynamic benefit of colder air at
altitude. For turbofans, TSFC generally scales with the square root of the
temperature ratio (theta = T/T0), reflecting the Brayton cycle efficiency
improvement. Above the tropopause, temperature is constant (ISA), so TSFC
stabilizes.

The Mach correction captures the ram effect on inlet temperature and the
velocity-dependent momentum drag of the bypass stream.

See ASSUMPTIONS_LOG.md entries C1, C2, C3.

References:
    - Mattingly, "Elements of Propulsion" (theta^0.5 model)
    - Raymer, "Aircraft Design: A Conceptual Approach" (TSFC lapse models)
"""

import math
from src.models import atmosphere


# --- Reference conditions for TSFC_ref values ---
# Most published cruise TSFC values are quoted at approximately these conditions
TSFC_REF_ALT_FT = 35_000   # ft
TSFC_REF_MACH = 0.80       # Mach number

# --- Thrust lapse model constants ---
# Two-regime model: different exponents below and above the tropopause.
# Below tropopause: standard sigma^0.75 for high-bypass turbofans.
# Above tropopause: steeper lapse (sigma^2.0) because real engines lose
# thrust faster in the isothermal stratosphere than the simple density-ratio
# model predicts (compressor efficiency degrades, max RPM limits, etc.).
# See ASSUMPTIONS_LOG.md entry C3.
THRUST_LAPSE_EXPONENT_TROPO = 0.75
THRUST_LAPSE_EXPONENT_STRATO = 2.0


def altitude_factor(h_ft, ref_alt_ft=TSFC_REF_ALT_FT):
    """Altitude correction factor for TSFC.

    TSFC scales approximately as sqrt(theta) where theta = T(h)/T0.
    We normalize relative to the reference altitude condition so that
    f_altitude = 1.0 at the reference altitude.

    For turbofans at altitude, the improvement comes from:
    1. Lower ambient temperature improving thermal efficiency
    2. Lower air density reducing bypass drag

    The sqrt(theta) model is standard for high-bypass turbofans.

    Args:
        h_ft: Altitude in feet
        ref_alt_ft: Reference altitude where f=1.0 (default 35,000 ft)

    Returns:
        TSFC altitude correction factor (dimensionless)
    """
    theta = atmosphere.temperature_ratio(h_ft)
    theta_ref = atmosphere.temperature_ratio(ref_alt_ft)
    return math.sqrt(theta / theta_ref)


def mach_factor(mach, ref_mach=TSFC_REF_MACH):
    """Mach number correction factor for TSFC.

    TSFC increases with Mach number due to ram temperature rise
    at the compressor inlet. For modern high-bypass turbofans,
    the relationship is approximately linear over the typical
    cruise Mach range (0.7-0.87):

        f_mach ≈ 1 + k_mach * (M - M_ref)

    where k_mach is typically 0.2-0.5 for high-bypass turbofans.
    We use k_mach = 0.3 as a mid-range estimate.

    Args:
        mach: Operating Mach number
        ref_mach: Reference Mach number where f=1.0 (default 0.80)

    Returns:
        TSFC Mach correction factor (dimensionless)
    """
    K_MACH = 0.3  # Sensitivity of TSFC to Mach number
    return 1.0 + K_MACH * (mach - ref_mach)


def tsfc(h_ft, mach, tsfc_ref, k_adj=1.0, ref_alt_ft=TSFC_REF_ALT_FT,
         ref_mach=TSFC_REF_MACH):
    """Compute TSFC at given flight conditions.

    TSFC(h, M) = TSFC_ref × f_altitude(h) × f_mach(M) × k_adj

    Args:
        h_ft: Altitude in feet
        mach: Mach number
        tsfc_ref: Published/reference cruise TSFC [lb/(lbf·hr)]
        k_adj: Calibration adjustment factor (default 1.0)
        ref_alt_ft: Reference altitude for TSFC_ref (default 35,000 ft)
        ref_mach: Reference Mach for TSFC_ref (default 0.80)

    Returns:
        TSFC in lb/(lbf·hr)
    """
    f_alt = altitude_factor(h_ft, ref_alt_ft)
    f_mach = mach_factor(mach, ref_mach)
    return tsfc_ref * f_alt * f_mach * k_adj


def fuel_flow_rate(thrust_lbf, h_ft, mach, tsfc_ref, k_adj=1.0):
    """Compute fuel flow rate.

    fuel_flow = T × TSFC

    Args:
        thrust_lbf: Thrust per engine (or total) in lbf
        h_ft: Altitude in feet
        mach: Mach number
        tsfc_ref: Published/reference cruise TSFC [lb/(lbf·hr)]
        k_adj: Calibration adjustment factor

    Returns:
        Fuel flow rate in lb/hr
    """
    c = tsfc(h_ft, mach, tsfc_ref, k_adj)
    return thrust_lbf * c


def thrust_available_cruise(thrust_slst_lbf, h_ft, n_engines=1):
    """Estimate available cruise thrust at altitude.

    Two-regime thrust lapse model:
    - Below tropopause (≤36,089 ft): T = T_SLS × σ^0.75
      Standard high-bypass turbofan lapse.
    - Above tropopause (>36,089 ft): T = T_trop × (σ/σ_trop)^2.0
      Steeper lapse reflecting accelerated thrust decay in the isothermal
      stratosphere where real engines lose performance faster than the
      simple density-ratio model predicts.

    At the tropopause boundary, both regimes give the same thrust value
    (continuity guaranteed by construction).

    This is used for checking whether the aircraft can sustain flight
    at a given altitude and weight, NOT for fuel burn computation
    (which uses the Breguet equation directly).

    Args:
        thrust_slst_lbf: Sea-level static thrust per engine, lbf
        h_ft: Altitude in feet
        n_engines: Number of operating engines

    Returns:
        Total available thrust in lbf
    """
    sigma = atmosphere.density_ratio(h_ft)

    if h_ft <= atmosphere.H_TROPOPAUSE:
        thrust_per_engine = thrust_slst_lbf * (
            sigma ** THRUST_LAPSE_EXPONENT_TROPO
        )
    else:
        # Two-regime: steeper lapse above tropopause
        sigma_trop = atmosphere.density_ratio(atmosphere.H_TROPOPAUSE)
        thrust_at_trop = thrust_slst_lbf * (
            sigma_trop ** THRUST_LAPSE_EXPONENT_TROPO
        )
        sigma_ratio = sigma / sigma_trop
        thrust_per_engine = thrust_at_trop * (
            sigma_ratio ** THRUST_LAPSE_EXPONENT_STRATO
        )

    return thrust_per_engine * n_engines


def max_altitude_for_thrust(required_thrust_lbf, thrust_slst_lbf, n_engines):
    """Find the maximum altitude where thrust ≥ required thrust.

    Uses bisection search since the thrust lapse model doesn't have
    a clean inverse.

    Args:
        required_thrust_lbf: Required thrust in lbf
        thrust_slst_lbf: Sea-level static thrust per engine, lbf
        n_engines: Number of operating engines

    Returns:
        Maximum altitude in feet (capped at 55,000 ft)
    """
    h_low = 0
    h_high = 55_000  # reasonable upper bound for jet aircraft

    # Check if flight is possible at all
    thrust_at_ground = thrust_available_cruise(thrust_slst_lbf, 0, n_engines)
    if thrust_at_ground < required_thrust_lbf:
        return 0  # Can't even fly at sea level

    # Bisection
    for _ in range(50):  # converges well within 50 iterations
        h_mid = (h_low + h_high) / 2.0
        thrust_avail = thrust_available_cruise(thrust_slst_lbf, h_mid, n_engines)
        if thrust_avail >= required_thrust_lbf:
            h_low = h_mid
        else:
            h_high = h_mid

    return h_low


def engine_out_thrust_fraction(n_engines):
    """Fraction of total thrust remaining after single engine failure.

    Args:
        n_engines: Total number of engines

    Returns:
        Fraction of original total thrust available (e.g., 0.5 for twins)
    """
    return (n_engines - 1) / n_engines
