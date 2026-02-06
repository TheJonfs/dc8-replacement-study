"""Tests for the performance model modules.

Tests aerodynamics, propulsion, and performance computation.
"""
import sys
sys.path.insert(0, '.')

import pytest
import math
from src.models import atmosphere, aerodynamics, propulsion, performance
from src.models.calibration import compute_calibration_range


class TestAerodynamics:
    """Tests for the aerodynamic model."""

    def test_lift_coefficient_positive(self):
        CL = aerodynamics.lift_coefficient(200000, 250.0, 2000.0)
        assert CL > 0

    def test_lift_coefficient_scales_with_weight(self):
        CL1 = aerodynamics.lift_coefficient(100000, 250.0, 2000.0)
        CL2 = aerodynamics.lift_coefficient(200000, 250.0, 2000.0)
        assert CL2 == pytest.approx(2 * CL1, rel=1e-10)

    def test_drag_coefficient_positive(self):
        CD = aerodynamics.drag_coefficient(0.5, 0.025, 8.0, 0.80)
        assert CD > 0.025  # must exceed CD0

    def test_drag_polar_parabolic(self):
        CD0 = 0.025
        AR = 8.0
        e = 0.80
        K = aerodynamics.induced_drag_factor(AR, e)
        CL = 0.5
        expected = CD0 + K * CL**2
        actual = aerodynamics.drag_coefficient(CL, CD0, AR, e)
        assert actual == pytest.approx(expected, rel=1e-10)

    def test_max_ld_physical_range(self):
        """Max L/D should be 10-22 for transport aircraft parameters."""
        for CD0, AR, e in [(0.020, 8.0, 0.80), (0.030, 9.5, 0.85),
                           (0.025, 7.5, 0.75)]:
            LD_max, CL_star = aerodynamics.max_lift_to_drag(CD0, AR, e)
            assert 10 < LD_max < 22, f"L/D_max={LD_max} for CD0={CD0}, AR={AR}, e={e}"
            assert CL_star > 0

    def test_max_ld_occurs_at_correct_cl(self):
        CD0 = 0.025
        AR = 8.0
        e = 0.80
        LD_max, CL_star = aerodynamics.max_lift_to_drag(CD0, AR, e)
        # Check that this is actually the maximum
        for delta in [-0.1, -0.01, 0.01, 0.1]:
            CL_test = CL_star + delta
            if CL_test > 0:
                LD_test = aerodynamics.lift_to_drag_ratio(CL_test, CD0, AR, e)
                assert LD_test <= LD_max + 1e-10

    def test_engine_out_drag_factor(self):
        factor = aerodynamics.engine_out_drag_factor(2, 10.0)
        assert factor == pytest.approx(1.10, rel=1e-10)

        factor4 = aerodynamics.engine_out_drag_factor(4, 10.0)
        assert factor4 == pytest.approx(1.10, rel=1e-10)


class TestPropulsion:
    """Tests for the propulsion model."""

    def test_altitude_factor_sea_level_higher_than_cruise(self):
        """TSFC should be worse (higher) at sea level than at cruise altitude."""
        f_sl = propulsion.altitude_factor(0, 35000)
        f_cruise = propulsion.altitude_factor(35000, 35000)
        assert f_sl > f_cruise

    def test_altitude_factor_unity_at_reference(self):
        f = propulsion.altitude_factor(35000, 35000)
        assert f == pytest.approx(1.0, rel=1e-10)

    def test_mach_factor_unity_at_reference(self):
        f = propulsion.mach_factor(0.80, 0.80)
        assert f == pytest.approx(1.0, rel=1e-10)

    def test_mach_factor_increases_with_mach(self):
        f_low = propulsion.mach_factor(0.75, 0.80)
        f_high = propulsion.mach_factor(0.85, 0.80)
        assert f_high > f_low

    def test_tsfc_at_reference_conditions(self):
        """TSFC at reference conditions should equal tsfc_ref × k_adj."""
        tsfc_ref = 0.65
        k_adj = 1.0
        c = propulsion.tsfc(35000, 0.80, tsfc_ref, k_adj)
        assert c == pytest.approx(tsfc_ref, rel=1e-3)

    def test_thrust_available_decreases_with_altitude(self):
        t_low = propulsion.thrust_available_cruise(22000, 10000, 4)
        t_high = propulsion.thrust_available_cruise(22000, 40000, 4)
        assert t_high < t_low

    def test_engine_out_thrust_fraction(self):
        assert propulsion.engine_out_thrust_fraction(2) == pytest.approx(0.5)
        assert propulsion.engine_out_thrust_fraction(4) == pytest.approx(0.75)


class TestPerformance:
    """Tests for the cruise performance model."""

    def test_breguet_positive_range(self):
        """Breguet range should be positive for valid inputs."""
        R = performance.breguet_range_nm(
            V_fps=778.0, tsfc_lbplbfhr=0.65,
            L_D=14.0, W_initial_lb=300000, W_final_lb=200000
        )
        assert R > 0

    def test_breguet_zero_for_no_fuel(self):
        R = performance.breguet_range_nm(
            V_fps=778.0, tsfc_lbplbfhr=0.65,
            L_D=14.0, W_initial_lb=300000, W_final_lb=300000
        )
        assert R == 0

    def test_breguet_increases_with_fuel(self):
        """More fuel = more range."""
        R1 = performance.breguet_range_nm(778, 0.65, 14, 300000, 250000)
        R2 = performance.breguet_range_nm(778, 0.65, 14, 300000, 200000)
        assert R2 > R1

    def test_breguet_increases_with_ld(self):
        """Higher L/D = more range."""
        R1 = performance.breguet_range_nm(778, 0.65, 12, 300000, 200000)
        R2 = performance.breguet_range_nm(778, 0.65, 16, 300000, 200000)
        assert R2 > R1

    def test_breguet_increases_with_lower_tsfc(self):
        """Lower TSFC = more range."""
        R1 = performance.breguet_range_nm(778, 0.70, 14, 300000, 200000)
        R2 = performance.breguet_range_nm(778, 0.55, 14, 300000, 200000)
        assert R2 > R1

    def test_step_cruise_positive_range(self):
        result = performance.step_cruise_range(
            W_initial_lb=300000,
            fuel_available_lb=100000,
            mach=0.80,
            wing_area_ft2=2800,
            CD0=0.025,
            AR=8.0,
            e=0.80,
            tsfc_ref=0.65,
            n_steps=20,
        )
        assert result["range_nm"] > 0
        assert result["fuel_burned_lb"] == pytest.approx(100000, rel=1e-6)

    def test_step_cruise_more_fuel_more_range(self):
        kwargs = dict(
            W_initial_lb=300000, mach=0.80, wing_area_ft2=2800,
            CD0=0.025, AR=8.0, e=0.80, tsfc_ref=0.65, n_steps=20,
        )
        r1 = performance.step_cruise_range(fuel_available_lb=50000, **kwargs)
        r2 = performance.step_cruise_range(fuel_available_lb=100000, **kwargs)
        assert r2["range_nm"] > r1["range_nm"]

    def test_step_cruise_lighter_aircraft_more_efficient(self):
        """Same fuel, lighter aircraft should go further."""
        kwargs = dict(
            fuel_available_lb=80000, mach=0.80, wing_area_ft2=2800,
            CD0=0.025, AR=8.0, e=0.80, tsfc_ref=0.65, n_steps=20,
        )
        r_heavy = performance.step_cruise_range(W_initial_lb=300000, **kwargs)
        r_light = performance.step_cruise_range(W_initial_lb=250000, **kwargs)
        assert r_light["range_nm"] > r_heavy["range_nm"]


class TestCalibrationRange:
    """Tests for the calibration range computation."""

    def test_positive_range(self):
        from src.aircraft_data.loader import load_aircraft
        dc8 = load_aircraft("DC-8")
        r = compute_calibration_range(dc8, 52000, 116000, 0.025, 0.80, 1.0, 0.12)
        assert r > 0

    def test_more_fuel_more_range(self):
        from src.aircraft_data.loader import load_aircraft
        dc8 = load_aircraft("DC-8")
        r1 = compute_calibration_range(dc8, 20000, 80000, 0.025, 0.80, 1.0, 0.12)
        r2 = compute_calibration_range(dc8, 20000, 120000, 0.025, 0.80, 1.0, 0.12)
        assert r2 > r1

    def test_overhead_reduces_range(self):
        from src.aircraft_data.loader import load_aircraft
        dc8 = load_aircraft("DC-8")
        r_low = compute_calibration_range(dc8, 20000, 100000, 0.025, 0.80, 1.0, 0.05)
        r_high = compute_calibration_range(dc8, 20000, 100000, 0.025, 0.80, 1.0, 0.20)
        assert r_low > r_high

    def test_zero_range_if_overhead_exceeds_fuel(self):
        from src.aircraft_data.loader import load_aircraft
        dc8 = load_aircraft("DC-8")
        r = compute_calibration_range(dc8, 50000, 10000, 0.025, 0.80, 1.0, 0.50)
        assert r == 0  # overhead > fuel


class TestCalibrationQuality:
    """Test that calibrated models match published data."""

    @pytest.fixture(scope="class")
    def calibrations(self):
        from src.aircraft_data.loader import load_all_aircraft
        from src.models.calibration import calibrate_aircraft, calibrate_p8_from_737
        all_ac = load_all_aircraft()
        cals = {}
        for des in ["DC-8", "GV", "737-900ER", "767-200ER", "A330-200", "777-200LR"]:
            cals[des] = calibrate_aircraft(all_ac[des])
        cals["P-8"] = calibrate_p8_from_737(cals["737-900ER"], all_ac["P-8"], all_ac["737-900ER"])
        return cals

    def test_dc8_rms_below_5pct(self, calibrations):
        assert calibrations["DC-8"]["rms_error"] < 0.05

    def test_gv_rms_below_5pct(self, calibrations):
        assert calibrations["GV"]["rms_error"] < 0.05

    def test_737_rms_below_5pct(self, calibrations):
        assert calibrations["737-900ER"]["rms_error"] < 0.05

    def test_767_rms_below_5pct(self, calibrations):
        assert calibrations["767-200ER"]["rms_error"] < 0.05

    def test_a330_rms_below_5pct(self, calibrations):
        assert calibrations["A330-200"]["rms_error"] < 0.05

    def test_777_rms_below_10pct(self, calibrations):
        # 777-200LR has larger error due to extreme range
        assert calibrations["777-200LR"]["rms_error"] < 0.10

    def test_all_ld_max_positive(self, calibrations):
        for des, cal in calibrations.items():
            assert cal["L_D_max"] > 0, f"{des}: L/D_max should be positive"
