"""Tests for the ISA atmosphere model.

Verification approach: Compare computed values against published ISA tables
at standard reference altitudes. These are well-known values that serve as
our Tier 1 verification for the atmosphere module.

Reference: US Standard Atmosphere 1976, ICAO Doc 7488/3
"""

import math
import pytest
from src.models.atmosphere import (
    temperature, pressure, density, speed_of_sound,
    density_ratio, pressure_ratio, temperature_ratio,
    H_TROPOPAUSE, T0, P0, RHO0, A0,
)


# --- Sea Level Checks ---

def test_sea_level_temperature():
    assert abs(temperature(0) - 518.67) < 0.01  # 59°F = 518.67°R


def test_sea_level_pressure():
    assert abs(pressure(0) - 2116.22) < 0.1  # lbf/ft²


def test_sea_level_density():
    assert abs(density(0) - 0.002377) < 0.000001  # slug/ft³


def test_sea_level_speed_of_sound():
    assert abs(speed_of_sound(0) - 1116.45) < 0.5  # ft/s


# --- Tropopause Checks (36,089 ft = 11,000 m) ---

def test_tropopause_temperature():
    T_trop = temperature(H_TROPOPAUSE)
    # ISA tropopause: -56.5°C = 216.65 K = 389.97°R
    assert abs(T_trop - 389.97) < 0.5


def test_tropopause_pressure():
    P_trop = pressure(H_TROPOPAUSE)
    # ISA tropopause pressure: 22632 Pa = 472.68 lbf/ft²
    assert abs(P_trop - 472.68) < 2.0


def test_tropopause_density():
    rho_trop = density(H_TROPOPAUSE)
    # ISA tropopause density: 0.3639 kg/m³ = 0.000706 slug/ft³
    assert abs(rho_trop - 0.000706) < 0.00002


# --- Mid-Troposphere Check (20,000 ft ≈ 6,096 m) ---

def test_20000ft_temperature():
    T = temperature(20000)
    # 20,000 ft: T0 + lapse_rate * 20000 = 518.67 - 0.003566 * 20000 = 447.35°R
    # = 248.53 K = -24.6°C
    assert abs(T - 447.35) < 0.5


def test_20000ft_density_ratio():
    sigma = density_ratio(20000)
    # Published sigma at 20,000 ft ≈ 0.5328
    assert abs(sigma - 0.5328) < 0.01


# --- Stratosphere Check (45,000 ft ≈ 13,716 m) ---

def test_stratosphere_isothermal():
    """Temperature should be constant above tropopause."""
    T_trop = temperature(H_TROPOPAUSE)
    T_45k = temperature(45000)
    assert abs(T_45k - T_trop) < 0.01


def test_45000ft_pressure():
    P_45k = pressure(45000)
    # Approximate ISA pressure at 45,000 ft ≈ 308 lbf/ft² (from tables)
    # More precisely: ~4.36 psi = 308 lbf/ft² (approximately)
    # Let's use a wider tolerance here since this is interpolated from tables
    assert 280 < P_45k < 320


# --- Physical Consistency Checks ---

def test_temperature_decreases_in_troposphere():
    """Temperature should decrease with altitude in troposphere."""
    T_0 = temperature(0)
    T_10k = temperature(10000)
    T_20k = temperature(20000)
    T_30k = temperature(30000)
    assert T_0 > T_10k > T_20k > T_30k


def test_pressure_always_decreases():
    """Pressure should always decrease with altitude."""
    altitudes = [0, 10000, 20000, 30000, 40000, 50000, 60000]
    pressures = [pressure(h) for h in altitudes]
    for i in range(len(pressures) - 1):
        assert pressures[i] > pressures[i + 1]


def test_density_always_decreases():
    """Density should always decrease with altitude."""
    altitudes = [0, 10000, 20000, 30000, 40000, 50000, 60000]
    densities = [density(h) for h in altitudes]
    for i in range(len(densities) - 1):
        assert densities[i] > densities[i + 1]


def test_speed_of_sound_decreases_in_troposphere():
    """Speed of sound decreases with temperature (and thus altitude in troposphere)."""
    a_0 = speed_of_sound(0)
    a_20k = speed_of_sound(20000)
    a_trop = speed_of_sound(H_TROPOPAUSE)
    assert a_0 > a_20k > a_trop


def test_speed_of_sound_constant_in_stratosphere():
    """Speed of sound is constant in the isothermal stratosphere."""
    a_37k = speed_of_sound(37000)
    a_50k = speed_of_sound(50000)
    assert abs(a_37k - a_50k) < 0.1


def test_ideal_gas_consistency():
    """Verify P = rho * R * T at several altitudes."""
    R = 1716.49
    for h in [0, 10000, 20000, 36089, 45000, 60000]:
        P = pressure(h)
        rho = density(h)
        T = temperature(h)
        assert abs(P - rho * R * T) / P < 1e-10  # should be exact


def test_ratios_at_sea_level():
    """All ratios should be 1.0 at sea level.

    Note: density_ratio uses a rounded RHO0 constant (0.002377) while
    density(0) computes P0/(R*T0), giving a tiny discrepancy (~2e-6).
    This is acceptable — the rounded constant matches published tables.
    """
    assert abs(density_ratio(0) - 1.0) < 1e-4
    assert abs(pressure_ratio(0) - 1.0) < 1e-10
    assert abs(temperature_ratio(0) - 1.0) < 1e-10
