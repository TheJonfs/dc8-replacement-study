"""Unit conversions and common utilities for aircraft performance modeling."""


# --- Physical Constants ---
G = 32.174  # gravitational acceleration, ft/s^2
R_AIR = 1716.49  # specific gas constant for air, ft·lbf/(slug·°R)
GAMMA = 1.4  # ratio of specific heats for air

# --- Conversion Factors ---
NM_TO_FT = 6076.12  # nautical miles to feet
FT_TO_NM = 1.0 / NM_TO_FT
FT_TO_M = 0.3048
M_TO_FT = 1.0 / FT_TO_M
KG_TO_LB = 2.20462
LB_TO_KG = 1.0 / KG_TO_LB
GAL_TO_LB_JETA = 6.7  # Jet-A density, lb per US gallon
LB_TO_GAL_JETA = 1.0 / GAL_TO_LB_JETA
LITER_TO_GAL = 0.264172
KT_TO_FPS = NM_TO_FT / 3600.0  # knots to feet per second
FPS_TO_KT = 1.0 / KT_TO_FPS
HR_TO_SEC = 3600.0
SEC_TO_HR = 1.0 / HR_TO_SEC


def nm_to_ft(nm):
    """Convert nautical miles to feet."""
    return nm * NM_TO_FT


def ft_to_nm(ft):
    """Convert feet to nautical miles."""
    return ft * FT_TO_NM


def mach_to_tas(mach, speed_of_sound_fps):
    """Convert Mach number to true airspeed in ft/s."""
    return mach * speed_of_sound_fps


def tas_to_mach(tas_fps, speed_of_sound_fps):
    """Convert true airspeed (ft/s) to Mach number."""
    return tas_fps / speed_of_sound_fps


def tas_fps_to_ktas(tas_fps):
    """Convert true airspeed from ft/s to knots."""
    return tas_fps * FPS_TO_KT


def ktas_to_tas_fps(ktas):
    """Convert true airspeed from knots to ft/s."""
    return ktas * KT_TO_FPS


def fuel_lb_to_gallons(fuel_lb):
    """Convert fuel weight in pounds to US gallons (Jet-A)."""
    return fuel_lb * LB_TO_GAL_JETA


def fuel_gallons_to_lb(gallons):
    """Convert fuel volume in US gallons to weight in pounds (Jet-A)."""
    return gallons * GAL_TO_LB_JETA


def fuel_cost(fuel_lb, price_per_gallon=5.50):
    """Calculate fuel cost from weight in pounds.

    Default price: $5.50/gallon Jet-A (mid-range 2024 estimate).
    See ASSUMPTIONS_LOG.md entry G1.
    """
    return fuel_lb_to_gallons(fuel_lb) * price_per_gallon
