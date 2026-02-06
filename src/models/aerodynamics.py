"""Aerodynamic model for aircraft performance estimation.

Implements a parabolic drag polar:
    CD = CD0 + CL² / (π · AR · e)

where:
    CD0 = zero-lift drag coefficient (parasite drag)
    AR  = wing aspect ratio
    e   = Oswald span efficiency factor
    CL  = lift coefficient

The key insight is that CD0 and e are *calibration parameters* — we don't know
them from public data, so we fit them to match published range-payload
performance. This means the model absorbs compressibility effects, trim drag,
and other contributions into the effective CD0 and e values at cruise.

See ASSUMPTIONS_LOG.md entries B1, B2, B3.
"""

import math


def lift_coefficient(weight_lb, dynamic_pressure_psf, wing_area_ft2):
    """Compute lift coefficient in steady level flight (L = W).

    Args:
        weight_lb: Aircraft weight in lbf (= lift in level flight)
        dynamic_pressure_psf: Dynamic pressure q in lbf/ft²
        wing_area_ft2: Reference wing area in ft²

    Returns:
        CL (dimensionless)
    """
    if dynamic_pressure_psf <= 0 or wing_area_ft2 <= 0:
        raise ValueError("Dynamic pressure and wing area must be positive")
    return weight_lb / (dynamic_pressure_psf * wing_area_ft2)


def drag_coefficient(CL, CD0, AR, e):
    """Compute drag coefficient using parabolic drag polar.

    CD = CD0 + CL² / (π · AR · e)

    Args:
        CL: Lift coefficient
        CD0: Zero-lift drag coefficient
        AR: Wing aspect ratio
        e: Oswald span efficiency factor

    Returns:
        CD (dimensionless)
    """
    K = induced_drag_factor(AR, e)
    return CD0 + K * CL ** 2


def induced_drag_factor(AR, e):
    """Compute the induced drag factor K = 1 / (π · AR · e).

    Args:
        AR: Wing aspect ratio
        e: Oswald span efficiency factor

    Returns:
        K (dimensionless)
    """
    return 1.0 / (math.pi * AR * e)


def drag_force(weight_lb, dynamic_pressure_psf, wing_area_ft2, CD0, AR, e):
    """Compute total aerodynamic drag in level flight.

    D = CD · q · S

    Args:
        weight_lb: Aircraft weight in lbf
        dynamic_pressure_psf: Dynamic pressure q in lbf/ft²
        wing_area_ft2: Reference wing area S in ft²
        CD0: Zero-lift drag coefficient
        AR: Wing aspect ratio
        e: Oswald span efficiency factor

    Returns:
        Drag force in lbf
    """
    CL = lift_coefficient(weight_lb, dynamic_pressure_psf, wing_area_ft2)
    CD = drag_coefficient(CL, CD0, AR, e)
    return CD * dynamic_pressure_psf * wing_area_ft2


def lift_to_drag_ratio(CL, CD0, AR, e):
    """Compute L/D ratio.

    Args:
        CL: Lift coefficient
        CD0: Zero-lift drag coefficient
        AR: Wing aspect ratio
        e: Oswald span efficiency factor

    Returns:
        L/D ratio (dimensionless)
    """
    CD = drag_coefficient(CL, CD0, AR, e)
    if CD <= 0:
        raise ValueError("CD must be positive")
    return CL / CD


def max_lift_to_drag(CD0, AR, e):
    """Compute maximum L/D ratio and the CL at which it occurs.

    For a parabolic drag polar, (L/D)_max occurs at CL* = sqrt(CD0 / K):
        (L/D)_max = 1 / (2 * sqrt(CD0 * K))

    Args:
        CD0: Zero-lift drag coefficient
        AR: Wing aspect ratio
        e: Oswald span efficiency factor

    Returns:
        Tuple of (L_D_max, CL_star):
            L_D_max: Maximum lift-to-drag ratio
            CL_star: CL at which L/D is maximized
    """
    K = induced_drag_factor(AR, e)
    CL_star = math.sqrt(CD0 / K)
    L_D_max = 1.0 / (2.0 * math.sqrt(CD0 * K))
    return L_D_max, CL_star


def cl_for_max_range(CD0, AR, e):
    """Compute CL for maximum specific range (best nm per lb fuel).

    For jet aircraft, max range occurs at max CL/CD (i.e., max L/D) for
    Breguet range equation with V·L/D dependency. Actually, for the standard
    Breguet equation R = (V/TSFC)·(L/D)·ln(Wi/Wf), the integrand is
    V·(L/D) which maximizes at CL = sqrt(CD0/(3K)), giving:
        (CL/CD)_range = max of CL^0.5 / CD

    However, with the full Breguet formulation R = (V/c)·(L/D)·ln(Wi/Wf),
    since V = sqrt(2W/(rho·S·CL)), the range parameter is actually:
        V · L/D = sqrt(2W/(rho·S)) · CL^0.5 / CD

    This maximizes at CL = sqrt(CD0 / (3K)), NOT at max L/D.

    Args:
        CD0: Zero-lift drag coefficient
        AR: Wing aspect ratio
        e: Oswald span efficiency factor

    Returns:
        CL for maximum range (jet aircraft)
    """
    K = induced_drag_factor(AR, e)
    return math.sqrt(CD0 / (3.0 * K))


def speed_for_cl(CL, weight_lb, density_slugft3, wing_area_ft2):
    """Compute true airspeed for a given CL in level flight.

    From L = W = 0.5 · ρ · V² · S · CL, solve for V.

    Args:
        CL: Lift coefficient (must be > 0)
        weight_lb: Aircraft weight in lbf
        density_slugft3: Air density in slug/ft³
        wing_area_ft2: Wing reference area in ft²

    Returns:
        True airspeed in ft/s
    """
    if CL <= 0:
        raise ValueError("CL must be positive")
    return math.sqrt(2.0 * weight_lb / (density_slugft3 * wing_area_ft2 * CL))


def engine_out_drag_factor(n_engines, drag_increment_pct=10.0):
    """Compute drag multiplier for single engine failure.

    Engine-out creates asymmetric drag from:
    - Rudder deflection to counteract yaw
    - Slight sideslip angle
    - Windmilling drag of failed engine

    See ASSUMPTIONS_LOG.md entry B4.

    Args:
        n_engines: Total number of engines
        drag_increment_pct: Percentage drag increase (default 10%)

    Returns:
        Drag multiplier (e.g., 1.10 for 10% increase)
    """
    # For twin-engine aircraft, losing one of two engines creates a larger
    # yaw moment arm relative to available correction authority, so the
    # drag penalty could be slightly higher. We use a uniform increment
    # as a simplification (documented in assumptions).
    return 1.0 + drag_increment_pct / 100.0
