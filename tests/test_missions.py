"""Tests for mission simulation functions.

Tests climb_segment(), descend_segment(), simulate_mission2_sampling(),
and simulate_mission3_low_altitude() using synthetic aircraft parameters
for fast execution (no calibration needed).
"""
import sys
sys.path.insert(0, '.')

import pytest
import math
from src.models.missions import (
    climb_segment, descend_segment,
    simulate_mission2_sampling, simulate_mission3_low_altitude,
)


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


# --- Synthetic aircraft dict and calibration for Mission 2 testing ---
# This mimics the structure produced by loader.py + calibrate_aircraft()

def _make_synth_aircraft(designation="SYNTH-767", oew=180_000, mtow=395_000,
                          max_fuel=160_000, max_payload=80_000,
                          n_engines=2, cruise_mach=0.80):
    """Create a synthetic aircraft dict for testing."""
    return {
        "designation": designation,
        "name": f"Synthetic {designation}",
        "OEW": oew,
        "MTOW": mtow,
        "MZFW": oew + max_payload,
        "max_payload": max_payload,
        "max_fuel": max_fuel,
        "wing_area_ft2": SYNTH_WING_AREA,
        "wingspan_ft": 156.0,
        "aspect_ratio": SYNTH_AR,
        "n_engines": n_engines,
        "cruise_mach": cruise_mach,
        "tsfc_cruise_ref": SYNTH_TSFC_REF,
        "thrust_per_engine_slst_lbf": SYNTH_THRUST_SLST,
        "service_ceiling_ft": 43_000,
    }


def _make_synth_calibration():
    """Create a synthetic calibration result dict for testing."""
    return {
        "CD0": SYNTH_CD0,
        "e": SYNTH_E,
        "k_adj": SYNTH_K_ADJ,
        "f_oh": 0.05,
    }


class TestMission2Sampling:
    """Tests for simulate_mission2_sampling()."""

    def test_basic_feasibility(self):
        """A well-configured aircraft should complete the mission."""
        ac = _make_synth_aircraft()
        cal = _make_synth_calibration()
        result = simulate_mission2_sampling(ac, cal, payload_lb=52_000,
                                             distance_nm=4_200)
        # With 163,000 lb fuel (395k - 180k - 52k), mission should be feasible
        assert result["feasible"] is True
        pa = result["per_aircraft"]
        assert pa["distance_covered_nm"] >= 4_200
        assert pa["n_cycles"] >= 1

    def test_returns_expected_keys(self):
        ac = _make_synth_aircraft()
        cal = _make_synth_calibration()
        result = simulate_mission2_sampling(ac, cal)
        assert "feasible" in result
        assert "per_aircraft" in result
        assert "designation" in result
        assert "n_aircraft" in result
        pa = result["per_aircraft"]
        assert "cycles" in pa
        assert "profile_points" in pa
        assert "peak_ceiling_ft" in pa
        assert "fuel_cost_usd" in pa

    def test_ceiling_increases_with_cycles(self):
        """As fuel burns off, ceiling should increase (progressive ceiling).

        With the two-regime thrust model, heavy aircraft are thrust-limited
        below the published ceiling. As fuel burns, they get lighter and
        can reach higher. This is the core scientific output of Mission 2.
        """
        ac = _make_synth_aircraft()
        cal = _make_synth_calibration()
        result = simulate_mission2_sampling(ac, cal, payload_lb=52_000,
                                             distance_nm=4_200)
        pa = result["per_aircraft"]
        cycles = pa["cycles"]
        if len(cycles) >= 3:
            # Compare first and last full cycle ceilings — should show increase
            full_cycles = [c for c in cycles if not c.get("partial", False)]
            if len(full_cycles) >= 2:
                assert full_cycles[-1]["ceiling_ft"] >= full_cycles[0]["ceiling_ft"]

    def test_fleet_sizing_small_aircraft(self):
        """Aircraft with small max_payload should trigger fleet sizing."""
        ac = _make_synth_aircraft(designation="SMALL", max_payload=10_000)
        cal = _make_synth_calibration()
        result = simulate_mission2_sampling(ac, cal, payload_lb=52_000)
        assert result["n_aircraft"] == math.ceil(52_000 / 10_000)
        assert result["payload_actual_lb"] < 52_000

    def test_fleet_aggregate_computed(self):
        """Multi-aircraft fleet should have aggregate cost data."""
        ac = _make_synth_aircraft(designation="SMALL", max_payload=10_000)
        cal = _make_synth_calibration()
        result = simulate_mission2_sampling(ac, cal, payload_lb=52_000)
        if result["feasible"] or result["per_aircraft"] is not None:
            assert result["aggregate"] is not None
            assert result["aggregate"]["n_aircraft"] > 1

    def test_infeasible_when_payload_exceeds_capacity(self):
        """An aircraft that can't carry payload within MTOW should be infeasible."""
        # OEW + payload > MTOW, no room for fuel
        ac = _make_synth_aircraft(oew=350_000, mtow=395_000, max_payload=80_000)
        cal = _make_synth_calibration()
        result = simulate_mission2_sampling(ac, cal, payload_lb=52_000)
        # fuel_available = min(395k - 350k - 52k, max_fuel) = min(-7k, ...) < 0
        assert result["feasible"] is False

    def test_weight_decreases_across_cycles(self):
        """Aircraft weight should decrease as fuel is burned."""
        ac = _make_synth_aircraft()
        cal = _make_synth_calibration()
        result = simulate_mission2_sampling(ac, cal, payload_lb=52_000,
                                             distance_nm=4_200)
        pa = result["per_aircraft"]
        cycles = pa["cycles"]
        if len(cycles) >= 2:
            assert cycles[-1]["weight_end_lb"] < cycles[0]["weight_start_lb"]

    def test_profile_points_monotonic_distance(self):
        """Profile distance coordinates should be monotonically increasing."""
        ac = _make_synth_aircraft()
        cal = _make_synth_calibration()
        result = simulate_mission2_sampling(ac, cal, payload_lb=52_000,
                                             distance_nm=4_200)
        pa = result["per_aircraft"]
        points = pa["profile_points"]
        if len(points) >= 2:
            distances = [p[0] for p in points]
            for i in range(1, len(distances)):
                assert distances[i] >= distances[i - 1]

    def test_profile_shows_sawtooth(self):
        """Profile altitude should oscillate between h_low and ceiling."""
        ac = _make_synth_aircraft()
        cal = _make_synth_calibration()
        result = simulate_mission2_sampling(ac, cal, payload_lb=52_000,
                                             distance_nm=4_200, h_low_ft=5_000)
        pa = result["per_aircraft"]
        points = pa["profile_points"]
        if len(points) >= 3:
            altitudes = [p[1] for p in points]
            # Should have both low (5,000 ft) and high (>20,000 ft) altitudes
            assert min(altitudes) == 5_000
            assert max(altitudes) > 20_000

    def test_fuel_accounting_consistent(self):
        """Total fuel burned + remaining should equal mission fuel budget."""
        ac = _make_synth_aircraft()
        cal = _make_synth_calibration()
        result = simulate_mission2_sampling(ac, cal, payload_lb=52_000,
                                             distance_nm=4_200)
        pa = result["per_aircraft"]
        # fuel_burned + fuel_remaining should equal mission_fuel
        total = pa["fuel_burned_lb"] + pa["fuel_remaining_lb"]
        assert total == pytest.approx(pa["mission_fuel_lb"], rel=0.01)

    def test_short_distance_fewer_cycles(self):
        """A shorter mission should require fewer cycles."""
        ac = _make_synth_aircraft()
        cal = _make_synth_calibration()
        short = simulate_mission2_sampling(ac, cal, payload_lb=52_000,
                                            distance_nm=1_000)
        long = simulate_mission2_sampling(ac, cal, payload_lb=52_000,
                                           distance_nm=4_200)
        assert short["per_aircraft"]["n_cycles"] <= long["per_aircraft"]["n_cycles"]

    def test_no_foh_used(self):
        """Mission 2 should not use f_oh — fuel budget is explicit reserves only."""
        ac = _make_synth_aircraft()
        # Use a large f_oh to verify it's NOT being used
        cal = _make_synth_calibration()
        cal["f_oh"] = 0.30  # would remove 30% of MTOW as overhead if used
        result = simulate_mission2_sampling(ac, cal, payload_lb=52_000,
                                             distance_nm=4_200)
        pa = result["per_aircraft"]
        # mission_fuel should be total_fuel minus reserves (not minus f_oh * MTOW)
        # If f_oh were used, mission_fuel would be much smaller
        assert pa["mission_fuel_lb"] > pa["total_fuel_lb"] * 0.5

    def test_ceiling_capped_at_service_ceiling(self):
        """Cycle ceiling should never exceed the published service ceiling,
        even when the aircraft is light enough to climb higher."""
        # Use a light aircraft with modest ceiling — should be capped
        ac = _make_synth_aircraft(oew=150_000, mtow=395_000,
                                   max_payload=80_000, max_fuel=160_000)
        ac["service_ceiling_ft"] = 40_000  # low ceiling for easy testing
        cal = _make_synth_calibration()
        result = simulate_mission2_sampling(ac, cal, payload_lb=30_000,
                                             distance_nm=2_000)
        pa = result["per_aircraft"]
        for c in pa["cycles"]:
            assert c["ceiling_ft"] <= 40_000, (
                f"Cycle {c['cycle']} ceiling {c['ceiling_ft']} exceeds "
                f"service ceiling 40,000 ft"
            )

    def test_progressive_ceiling_strict(self):
        """With heavy payload and enough fuel, early cycles should have lower
        ceilings than later cycles when the aircraft is thrust-limited."""
        # Use a heavy configuration so the aircraft starts thrust-limited
        ac = _make_synth_aircraft(oew=180_000, mtow=395_000,
                                   max_payload=80_000, max_fuel=160_000)
        ac["service_ceiling_ft"] = 50_000  # high cap so thrust limits first
        cal = _make_synth_calibration()
        result = simulate_mission2_sampling(ac, cal, payload_lb=52_000,
                                             distance_nm=4_200)
        pa = result["per_aircraft"]
        full_cycles = [c for c in pa["cycles"] if not c.get("partial", False)]
        if len(full_cycles) >= 5:
            # With a high service ceiling and heavy weight, early ceilings
            # should be thrust-limited and later ceilings should be higher
            assert full_cycles[-1]["ceiling_ft"] > full_cycles[0]["ceiling_ft"], (
                f"Last cycle ceiling ({full_cycles[-1]['ceiling_ft']}) should "
                f"exceed first ({full_cycles[0]['ceiling_ft']})"
            )

    def test_zero_progress_breaks_loop(self):
        """Aircraft that can't climb above h_low should not loop forever."""
        # Use extremely high CD0 so drag exceeds thrust at all altitudes
        ac = _make_synth_aircraft()
        cal = _make_synth_calibration()
        cal["CD0"] = 0.20  # absurdly high — no climb possible
        result = simulate_mission2_sampling(ac, cal, payload_lb=52_000,
                                             distance_nm=4_200)
        assert result["feasible"] is False
        pa = result["per_aircraft"]
        # Should have 0 cycles (broke out immediately), not 50
        assert pa["n_cycles"] == 0


class TestMission3LowAltitude:
    """Tests for simulate_mission3_low_altitude()."""

    def test_basic_feasibility(self):
        """A well-configured aircraft should complete 8 hours at low altitude."""
        ac = _make_synth_aircraft()
        cal = _make_synth_calibration()
        result = simulate_mission3_low_altitude(ac, cal, payload_lb=30_000,
                                                 duration_hr=8.0)
        assert result["feasible"] is True
        pa = result["per_aircraft"]
        assert pa["endurance_hr"] >= 8.0 - 0.01
        assert pa["distance_covered_nm"] > 0
        assert pa["fuel_burned_lb"] > 0

    def test_returns_expected_keys(self):
        ac = _make_synth_aircraft()
        cal = _make_synth_calibration()
        result = simulate_mission3_low_altitude(ac, cal)
        assert "feasible" in result
        assert "per_aircraft" in result
        pa = result["per_aircraft"]
        expected_keys = [
            "takeoff_weight_lb", "oew_lb", "payload_lb",
            "total_fuel_lb", "reserve_fuel_lb", "mission_fuel_lb",
            "fuel_burned_lb", "fuel_remaining_lb",
            "endurance_hr", "distance_covered_nm",
            "altitude_ft", "mach", "V_ktas",
            "avg_fuel_flow_lbhr", "steps",
            "fuel_cost_usd", "fuel_cost_per_1000lb_nm",
        ]
        for key in expected_keys:
            assert key in pa, f"Missing key: {key}"

    def test_fleet_sizing_for_small_aircraft(self):
        """Aircraft with max payload < 30,000 lb need a fleet."""
        ac = _make_synth_aircraft(max_payload=10_000)
        cal = _make_synth_calibration()
        result = simulate_mission3_low_altitude(ac, cal, payload_lb=30_000)
        assert result["n_aircraft"] == 3
        assert result["payload_actual_lb"] == pytest.approx(10_000, abs=1)
        assert result["aggregate"] is not None
        assert result["aggregate"]["n_aircraft"] == 3

    def test_fuel_increases_with_duration(self):
        """Longer endurance requires more fuel."""
        ac = _make_synth_aircraft()
        cal = _make_synth_calibration()
        r4 = simulate_mission3_low_altitude(ac, cal, duration_hr=4.0)
        r8 = simulate_mission3_low_altitude(ac, cal, duration_hr=8.0)
        assert (r8["per_aircraft"]["fuel_burned_lb"]
                > r4["per_aircraft"]["fuel_burned_lb"])

    def test_distance_positive_and_reasonable(self):
        """Should cover significant distance in 8 hours at 250 KTAS."""
        ac = _make_synth_aircraft()
        cal = _make_synth_calibration()
        result = simulate_mission3_low_altitude(ac, cal, duration_hr=8.0)
        pa = result["per_aircraft"]
        # At 250 KTAS for 8 hours, distance should be ~2,000 nm
        assert pa["distance_covered_nm"] > 1_500
        assert pa["distance_covered_nm"] < 2_500

    def test_endurance_decreases_with_payload(self):
        """Heavier payload means less fuel, shorter endurance (or more burned)."""
        ac = _make_synth_aircraft()
        cal = _make_synth_calibration()
        # Very light payload — lots of fuel
        r_light = simulate_mission3_low_altitude(ac, cal, payload_lb=10_000,
                                                   duration_hr=8.0)
        # Heavy payload — less fuel available
        r_heavy = simulate_mission3_low_altitude(ac, cal, payload_lb=70_000,
                                                   duration_hr=8.0)
        # Light aircraft should burn less fuel per hour
        assert (r_light["per_aircraft"]["avg_fuel_flow_lbhr"]
                < r_heavy["per_aircraft"]["avg_fuel_flow_lbhr"])

    def test_altitude_is_mission_altitude(self):
        """All steps should be at the mission altitude."""
        ac = _make_synth_aircraft()
        cal = _make_synth_calibration()
        result = simulate_mission3_low_altitude(ac, cal, h_mission_ft=1_500)
        pa = result["per_aircraft"]
        for step in pa["steps"]:
            assert step["altitude_ft"] == 1_500

    def test_infeasible_when_fuel_limited(self):
        """Aircraft with very little fuel should not endure 8 hours."""
        ac = _make_synth_aircraft(max_fuel=5_000)
        cal = _make_synth_calibration()
        result = simulate_mission3_low_altitude(ac, cal, payload_lb=30_000,
                                                 duration_hr=8.0)
        assert result["feasible"] is False
        pa = result["per_aircraft"]
        assert pa["endurance_hr"] < 8.0
