"""International Standard Atmosphere (ISA) model.

Implements the ISA from sea level through the stratosphere (~65,000 ft).
Reference: ICAO Standard Atmosphere (Doc 7488/3), US Standard Atmosphere 1976.

Layers modeled:
  - Troposphere: 0 to 36,089 ft (0 to 11,000 m) — linear temperature lapse
  - Lower stratosphere: 36,089 to 65,617 ft (11,000 to 20,000 m) — isothermal

See ASSUMPTIONS_LOG.md entry A1.
"""

import math


# --- ISA Sea Level Constants ---
T0 = 518.67      # sea level temperature, °R (= 288.15 K = 15°C)
P0 = 2116.22     # sea level pressure, lbf/ft² (= 101325 Pa)
RHO0 = 0.002377  # sea level density, slug/ft³ (= 1.225 kg/m³)
A0 = 1116.45      # sea level speed of sound, ft/s (= 340.3 m/s)

# --- Layer Boundaries ---
H_TROPOPAUSE = 36089.24  # tropopause altitude, ft (= 11,000 m)
H_STRATO2 = 65616.80     # top of lower stratosphere, ft (= 20,000 m)

# --- Temperature Lapse Rate ---
LAPSE_RATE = -0.003566  # °R per ft in troposphere (= -6.5°C per km = -0.0065 K/m)

# --- Gas Constants ---
GAMMA = 1.4
R = 1716.49  # ft·lbf/(slug·°R), specific gas constant for dry air
G = 32.174   # ft/s², standard gravitational acceleration


def temperature(h_ft):
    """ISA temperature at geometric altitude.

    Args:
        h_ft: Altitude in feet (0 to ~65,000 ft)

    Returns:
        Temperature in degrees Rankine (°R)
    """
    if h_ft <= H_TROPOPAUSE:
        return T0 + LAPSE_RATE * h_ft
    elif h_ft <= H_STRATO2:
        # Isothermal layer — temperature is constant at tropopause value
        return T0 + LAPSE_RATE * H_TROPOPAUSE
    else:
        # Above our modeled range — extrapolate isothermal (conservative)
        return T0 + LAPSE_RATE * H_TROPOPAUSE


def pressure(h_ft):
    """ISA pressure at geometric altitude.

    Args:
        h_ft: Altitude in feet

    Returns:
        Pressure in lbf/ft²
    """
    if h_ft <= H_TROPOPAUSE:
        # Troposphere: P = P0 * (T/T0)^(g/(L*R))
        T = temperature(h_ft)
        exponent = -G / (LAPSE_RATE * R)
        return P0 * (T / T0) ** exponent
    else:
        # Stratosphere (isothermal): P = P_trop * exp(-g*(h-h_trop)/(R*T_trop))
        P_trop = pressure(H_TROPOPAUSE)
        T_trop = temperature(H_TROPOPAUSE)
        return P_trop * math.exp(-G * (h_ft - H_TROPOPAUSE) / (R * T_trop))


def density(h_ft):
    """ISA air density at geometric altitude.

    Uses ideal gas law: rho = P / (R * T)

    Args:
        h_ft: Altitude in feet

    Returns:
        Density in slug/ft³
    """
    return pressure(h_ft) / (R * temperature(h_ft))


def speed_of_sound(h_ft):
    """Speed of sound at altitude.

    a = sqrt(gamma * R * T)

    Args:
        h_ft: Altitude in feet

    Returns:
        Speed of sound in ft/s
    """
    return math.sqrt(GAMMA * R * temperature(h_ft))


def density_ratio(h_ft):
    """Ratio of density at altitude to sea level density (sigma)."""
    return density(h_ft) / RHO0


def pressure_ratio(h_ft):
    """Ratio of pressure at altitude to sea level pressure (delta)."""
    return pressure(h_ft) / P0


def temperature_ratio(h_ft):
    """Ratio of temperature at altitude to sea level temperature (theta)."""
    return temperature(h_ft) / T0


def dynamic_pressure(h_ft, velocity_fps):
    """Dynamic pressure q = 0.5 * rho * V^2.

    Args:
        h_ft: Altitude in feet
        velocity_fps: True airspeed in ft/s

    Returns:
        Dynamic pressure in lbf/ft²
    """
    return 0.5 * density(h_ft) * velocity_fps ** 2
