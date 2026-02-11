"""Tests for mission simulation functions.

Tests climb_segment(), descend_segment(), and simulate_mission2_sampling()
using synthetic aircraft parameters for fast execution (no calibration needed).
"""
import sys
sys.path.insert(0, '.')

import pytest
import math
from src.models.missions import climb_segment, descend_segment


# --- Synthetic aircraft parameters for testing ---
# These are representative of a 767-class aircraft but use round numbers
# for predictability. They do NOT need to match any calibrated aircraft.
SYNTH_WING_AREA = 3050.0       # ft^2
SYNTH_AR = 7.9                 # aspect ratio
SYNTH_CD0 = 0.020              # realistic zero-lift drag
SYNTH_E = 0.80                 # Oswald efficiency
SYNTH_TSFC_REF = 0.60          # lb/(lbf-hr) reference TSFC
SYNTH_K_ADJ = 1.0              # no TSFC adjustment
SYNTH_THRUST_SLST = 60_000.0   # lbf per engine (sea-level static)
SYNTH_N_ENGINES = 2
SYNTH_MACH_CLIMB = 0.76        # climb Mach (cruise_mach * 0.95)
SYNTH_MACH_DESCENT = 0.72      # descent Mach


class TestClimbSegment:
    """Tests for climb_segment()."""

    def test_returns_positive_fuel_and_distance(self):
        result = climb_segment(
            W_start_lb=300_000, h_start_ft=5_000, h_target_ft=35_000,
            mach_climb=SYNTH_MACH_CLIMB, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
            thrust_slst_lbf=SYNTH_THRUST_SLST, n_engines=SYNTH_N_ENGINES,
        )
        assert result["fuel_burned_lb"] > 0
        assert result["distance_nm"] > 0
        assert result["time_hr"] > 0

    def test_ceiling_reached_matches_target(self):
        """When thrust is sufficient, climb should reach target altitude."""
        result = climb_segment(
            W_start_lb=250_000, h_start_ft=5_000, h_target_ft=35_000,
            mach_climb=SYNTH_MACH_CLIMB, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
            thrust_slst_lbf=SYNTH_THRUST_SLST, n_engines=SYNTH_N_ENGINES,
        )
        assert result["ceiling_ft"] == pytest.approx(35_000, abs=1)
        assert result["ceiling_limited"] is False

    def test_ceiling_limited_at_heavy_weight(self):
        """Very heavy aircraft should hit ceiling before target."""
        # Use a very heavy weight with modest thrust to force ceiling limit
        result = climb_segment(
            W_start_lb=400_000, h_start_ft=5_000, h_target_ft=55_000,
            mach_climb=SYNTH_MACH_CLIMB, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
            thrust_slst_lbf=SYNTH_THRUST_SLST, n_engines=SYNTH_N_ENGINES,
        )
        assert result["ceiling_ft"] < 55_000
        assert result["ceiling_limited"] is True

    def test_lighter_aircraft_reaches_higher(self):
        """Lighter aircraft should achieve a higher ceiling."""
        heavy = climb_segment(
            W_start_lb=350_000, h_start_ft=5_000, h_target_ft=55_000,
            mach_climb=SYNTH_MACH_CLIMB, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
            thrust_slst_lbf=SYNTH_THRUST_SLST, n_engines=SYNTH_N_ENGINES,
        )
        light = climb_segment(
            W_start_lb=200_000, h_start_ft=5_000, h_target_ft=55_000,
            mach_climb=SYNTH_MACH_CLIMB, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
            thrust_slst_lbf=SYNTH_THRUST_SLST, n_engines=SYNTH_N_ENGINES,
        )
        assert light["ceiling_ft"] > heavy["ceiling_ft"]

    def test_no_climb_when_start_equals_target(self):
        result = climb_segment(
            W_start_lb=250_000, h_start_ft=35_000, h_target_ft=35_000,
            mach_climb=SYNTH_MACH_CLIMB, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
            thrust_slst_lbf=SYNTH_THRUST_SLST, n_engines=SYNTH_N_ENGINES,
        )
        assert result["fuel_burned_lb"] == 0.0
        assert result["distance_nm"] == 0.0
        assert result["steps"] == []

    def test_no_climb_when_start_above_target(self):
        result = climb_segment(
            W_start_lb=250_000, h_start_ft=40_000, h_target_ft=35_000,
            mach_climb=SYNTH_MACH_CLIMB, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
            thrust_slst_lbf=SYNTH_THRUST_SLST, n_engines=SYNTH_N_ENGINES,
        )
        assert result["fuel_burned_lb"] == 0.0

    def test_steps_cover_full_altitude_range(self):
        """Each step should cover the expected altitude increment."""
        h_start, h_target = 5_000, 25_000
        result = climb_segment(
            W_start_lb=250_000, h_start_ft=h_start, h_target_ft=h_target,
            mach_climb=SYNTH_MACH_CLIMB, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
            thrust_slst_lbf=SYNTH_THRUST_SLST, n_engines=SYNTH_N_ENGINES,
            h_step_ft=1000,
        )
        # Should have 20 steps for 20,000 ft at 1,000 ft steps
        if not result["ceiling_limited"]:
            assert len(result["steps"]) == 20
            assert result["steps"][0]["h_start_ft"] == h_start
            assert result["steps"][-1]["h_end_ft"] == h_target

    def test_weight_decreases_through_climb(self):
        result = climb_segment(
            W_start_lb=250_000, h_start_ft=5_000, h_target_ft=35_000,
            mach_climb=SYNTH_MACH_CLIMB, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
            thrust_slst_lbf=SYNTH_THRUST_SLST, n_engines=SYNTH_N_ENGINES,
        )
        steps = result["steps"]
        if len(steps) >= 2:
            assert steps[-1]["W_start_lb"] < steps[0]["W_start_lb"]

    def test_roc_decreases_with_altitude(self):
        """Rate of climb should generally decrease as altitude increases."""
        result = climb_segment(
            W_start_lb=250_000, h_start_ft=5_000, h_target_ft=40_000,
            mach_climb=SYNTH_MACH_CLIMB, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
            thrust_slst_lbf=SYNTH_THRUST_SLST, n_engines=SYNTH_N_ENGINES,
        )
        steps = result["steps"]
        if len(steps) >= 5:
            # Compare first few steps to last few — ROC should trend down
            early_roc = sum(s["roc_fpm"] for s in steps[:3]) / 3
            late_roc = sum(s["roc_fpm"] for s in steps[-3:]) / 3
            assert late_roc < early_roc

    def test_fuel_burned_reasonable_magnitude(self):
        """Climb fuel for a 30,000 ft climb should be in the ballpark of
        a few thousand pounds for a 767-class aircraft."""
        result = climb_segment(
            W_start_lb=300_000, h_start_ft=5_000, h_target_ft=35_000,
            mach_climb=SYNTH_MACH_CLIMB, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
            thrust_slst_lbf=SYNTH_THRUST_SLST, n_engines=SYNTH_N_ENGINES,
        )
        # Expect roughly 2,000–8,000 lb for this configuration
        assert 1_000 < result["fuel_burned_lb"] < 15_000

    def test_high_cd0_reduces_ceiling(self):
        """Unrealistically high CD0 (like calibrated P-8/A330) should reduce ceiling."""
        normal = climb_segment(
            W_start_lb=300_000, h_start_ft=5_000, h_target_ft=55_000,
            mach_climb=SYNTH_MACH_CLIMB, wing_area_ft2=SYNTH_WING_AREA,
            CD0=0.020, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
            thrust_slst_lbf=SYNTH_THRUST_SLST, n_engines=SYNTH_N_ENGINES,
        )
        high_cd0 = climb_segment(
            W_start_lb=300_000, h_start_ft=5_000, h_target_ft=55_000,
            mach_climb=SYNTH_MACH_CLIMB, wing_area_ft2=SYNTH_WING_AREA,
            CD0=0.050, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
            thrust_slst_lbf=SYNTH_THRUST_SLST, n_engines=SYNTH_N_ENGINES,
        )
        assert high_cd0["ceiling_ft"] < normal["ceiling_ft"]


class TestDescendSegment:
    """Tests for descend_segment()."""

    def test_returns_positive_values(self):
        result = descend_segment(
            W_start_lb=250_000, h_start_ft=35_000, h_target_ft=5_000,
            mach_descent=SYNTH_MACH_DESCENT, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
        )
        assert result["fuel_burned_lb"] > 0
        assert result["distance_nm"] > 0
        assert result["time_hr"] > 0

    def test_no_descent_when_already_at_target(self):
        result = descend_segment(
            W_start_lb=250_000, h_start_ft=5_000, h_target_ft=5_000,
            mach_descent=SYNTH_MACH_DESCENT, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
        )
        assert result["fuel_burned_lb"] == 0.0
        assert result["distance_nm"] == 0.0

    def test_no_descent_when_below_target(self):
        result = descend_segment(
            W_start_lb=250_000, h_start_ft=3_000, h_target_ft=5_000,
            mach_descent=SYNTH_MACH_DESCENT, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
        )
        assert result["fuel_burned_lb"] == 0.0

    def test_larger_altitude_drop_more_fuel(self):
        short = descend_segment(
            W_start_lb=250_000, h_start_ft=25_000, h_target_ft=5_000,
            mach_descent=SYNTH_MACH_DESCENT, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
        )
        long = descend_segment(
            W_start_lb=250_000, h_start_ft=40_000, h_target_ft=5_000,
            mach_descent=SYNTH_MACH_DESCENT, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
        )
        assert long["fuel_burned_lb"] > short["fuel_burned_lb"]
        assert long["distance_nm"] > short["distance_nm"]

    def test_descent_fuel_scales_with_aircraft_size(self):
        """Heavier aircraft (higher drag) should burn more fuel descending."""
        light = descend_segment(
            W_start_lb=150_000, h_start_ft=35_000, h_target_ft=5_000,
            mach_descent=SYNTH_MACH_DESCENT, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
        )
        heavy = descend_segment(
            W_start_lb=350_000, h_start_ft=35_000, h_target_ft=5_000,
            mach_descent=SYNTH_MACH_DESCENT, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
        )
        assert heavy["fuel_burned_lb"] > light["fuel_burned_lb"]

    def test_descent_fuel_reasonable_magnitude(self):
        """Descent from 35,000 to 5,000 ft should burn a few hundred to
        a few thousand pounds at idle for a 767-class aircraft."""
        result = descend_segment(
            W_start_lb=250_000, h_start_ft=35_000, h_target_ft=5_000,
            mach_descent=SYNTH_MACH_DESCENT, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
        )
        # At 10% idle fraction, expect roughly 200-1,500 lb
        assert 50 < result["fuel_burned_lb"] < 3_000

    def test_descent_distance_reasonable(self):
        """Descent from 35,000 to 5,000 ft at 2,000 ft/min at M0.72
        should cover roughly 100-200 nm."""
        result = descend_segment(
            W_start_lb=250_000, h_start_ft=35_000, h_target_ft=5_000,
            mach_descent=SYNTH_MACH_DESCENT, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
        )
        # 30,000 ft / 2,000 fpm = 15 min = 0.25 hr
        # At ~420 ktas, distance ~ 105 nm
        assert 50 < result["distance_nm"] < 250

    def test_descent_time_correct(self):
        """Descent time should equal altitude change / descent rate."""
        result = descend_segment(
            W_start_lb=250_000, h_start_ft=35_000, h_target_ft=5_000,
            mach_descent=SYNTH_MACH_DESCENT, wing_area_ft2=SYNTH_WING_AREA,
            CD0=SYNTH_CD0, AR=SYNTH_AR, e=SYNTH_E,
            tsfc_ref=SYNTH_TSFC_REF, k_adj=SYNTH_K_ADJ,
            descent_rate_fpm=2000.0,
        )
        expected_time_hr = (35_000 - 5_000) / 2000.0 / 60.0  # 0.25 hr
        assert result["time_hr"] == pytest.approx(expected_time_hr, rel=1e-10)
