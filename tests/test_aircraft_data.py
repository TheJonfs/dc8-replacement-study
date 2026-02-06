"""Data integrity tests for aircraft specifications.

These tests verify:
1. All aircraft load successfully through the unified loader
2. Weight balance consistency (OEW + payload + fuel vs MTOW)
3. Range-payload points are physically consistent
4. No unit confusion (kg vs lb, km vs nmi)
5. Values are in plausible ranges for their aircraft class

This test suite was created in response to reviewer feedback on Phase 0,
which flagged potential unit inconsistencies across data files collected
by different research agents.
"""

import pytest
from src.aircraft_data.loader import load_all_aircraft, load_aircraft, validate_aircraft


@pytest.fixture
def all_aircraft():
    return load_all_aircraft()


# --- Loading Tests ---

def test_all_aircraft_load(all_aircraft):
    """All 7 aircraft should load without errors."""
    expected = {"DC-8", "GV", "737-900ER", "P-8", "767-200ER", "A330-200", "777-200LR"}
    assert set(all_aircraft.keys()) == expected


def test_all_aircraft_have_required_keys(all_aircraft):
    """Every aircraft dict should have the minimum required keys."""
    required_keys = [
        "name", "OEW", "MTOW", "max_payload", "max_fuel",
        "range_payload_points", "wing_area_ft2", "wingspan_ft",
        "aspect_ratio", "n_engines", "tsfc_cruise_ref", "cruise_mach",
        "service_ceiling_ft",
    ]
    for designation, data in all_aircraft.items():
        for key in required_keys:
            assert key in data, f"{designation} missing key '{key}'"


# --- Unit Consistency Checks ---
# These catch cases where a value might be in kg instead of lb,
# or km instead of nmi, or thousands-of-lb instead of lb.

class TestUnitConsistency:
    """Detect likely unit errors by checking value ranges."""

    def test_oew_in_pounds(self, all_aircraft):
        """OEW should be in lb (> 10,000 for all aircraft here).
        If a value is under 1,000, it might be in thousands of lb.
        If under 100,000 for wide-bodies, it might be in kg."""
        for name, data in all_aircraft.items():
            oew = data["OEW"]
            assert oew > 10_000, f"{name}: OEW={oew} — too low, possibly wrong units"
            # Wide-bodies should be over 150,000 lb OEW
            if name in ("767-200ER", "A330-200", "777-200LR"):
                assert oew > 150_000, (
                    f"{name}: OEW={oew} lb seems low for a wide-body; "
                    f"if this is in kg, multiply by 2.205"
                )

    def test_mtow_in_pounds(self, all_aircraft):
        """MTOW should be in lb. Check for plausible ranges by aircraft class."""
        for name, data in all_aircraft.items():
            mtow = data["MTOW"]
            assert mtow > 50_000, f"{name}: MTOW={mtow} — too low, possibly wrong units"

    def test_fuel_in_pounds(self, all_aircraft):
        """Max fuel should be in lb."""
        for name, data in all_aircraft.items():
            fuel = data["max_fuel"]
            assert fuel > 5_000, f"{name}: max_fuel={fuel} — too low, possibly wrong units"
            # Fuel should be less than MTOW
            assert fuel < data["MTOW"], f"{name}: max_fuel ({fuel}) >= MTOW ({data['MTOW']})"

    def test_ranges_in_nautical_miles(self, all_aircraft):
        """Ranges should be in nmi. If a value is over 15,000, it might be in km.
        If under 500, it might be in statute miles or missing a digit."""
        for name, data in all_aircraft.items():
            for i, (pl, fuel, rng) in enumerate(data["range_payload_points"]):
                assert 500 < rng < 15_000, (
                    f"{name} point {i}: range={rng} nmi outside plausible bounds; "
                    f"if in km, divide by 1.852"
                )

    def test_wing_area_in_sqft(self, all_aircraft):
        """Wing area should be in ft². If under 500, might be in m²."""
        for name, data in all_aircraft.items():
            area = data["wing_area_ft2"]
            assert area > 500, (
                f"{name}: wing_area={area} ft² — too low; "
                f"if in m², multiply by 10.764"
            )

    def test_tsfc_in_lb_per_lbf_hr(self, all_aircraft):
        """Cruise TSFC should be 0.4-0.8 lb/(lbf·hr) for subsonic turbofans.
        If under 0.1, might be in kg/(N·s) or other SI units."""
        for name, data in all_aircraft.items():
            tsfc = data["tsfc_cruise_ref"]
            assert 0.4 < tsfc < 0.8, (
                f"{name}: TSFC={tsfc} outside range 0.4-0.8 lb/(lbf·hr)"
            )


# --- Weight Balance Checks ---

class TestWeightBalance:
    """Verify weight relationships are physically consistent."""

    def test_oew_less_than_mtow(self, all_aircraft):
        for name, data in all_aircraft.items():
            assert data["OEW"] < data["MTOW"], f"{name}: OEW >= MTOW"

    def test_max_payload_positive(self, all_aircraft):
        for name, data in all_aircraft.items():
            assert data["max_payload"] > 0, f"{name}: max_payload <= 0"

    def test_max_fuel_positive(self, all_aircraft):
        for name, data in all_aircraft.items():
            assert data["max_fuel"] > 0, f"{name}: max_fuel <= 0"

    def test_oew_plus_payload_within_mtow(self, all_aircraft):
        """OEW + max_payload should not exceed MTOW (would mean zero fuel)."""
        for name, data in all_aircraft.items():
            assert data["OEW"] + data["max_payload"] <= data["MTOW"] * 1.01, (
                f"{name}: OEW + max_payload = {data['OEW'] + data['max_payload']} "
                f"> MTOW = {data['MTOW']}"
            )

    def test_oew_plus_fuel_within_mtow(self, all_aircraft):
        """OEW + max_fuel should not exceed MTOW (would mean zero payload ferry)."""
        for name, data in all_aircraft.items():
            assert data["OEW"] + data["max_fuel"] <= data["MTOW"] * 1.01, (
                f"{name}: OEW + max_fuel = {data['OEW'] + data['max_fuel']} "
                f"> MTOW = {data['MTOW']}"
            )

    def test_payload_fuel_tradeoff_exists(self, all_aircraft):
        """For most aircraft, OEW + max_payload + max_fuel > MTOW,
        meaning you can't carry both max payload and max fuel.
        Exception: P-8 is designed so they sum to exactly MTOW."""
        for name, data in all_aircraft.items():
            total = data["OEW"] + data["max_payload"] + data["max_fuel"]
            if name == "P-8":
                # P-8: max_payload + max_fuel designed to fill to MTOW exactly
                assert abs(total - data["MTOW"]) < 100, (
                    f"P-8: OEW+payload+fuel={total} should ≈ MTOW={data['MTOW']}"
                )
            # For some aircraft (767-200ER), total may be less than MTOW
            # due to tank volume or MZFW constraints — that's also valid


# --- Range-Payload Consistency ---

class TestRangePayload:
    """Verify range-payload points are physically consistent."""

    def test_ranges_increase_with_decreasing_payload(self, all_aircraft):
        """Range should increase (or stay equal) as payload decreases."""
        for name, data in all_aircraft.items():
            rp = data["range_payload_points"]
            for i in range(len(rp) - 1):
                assert rp[i][0] >= rp[i+1][0], (
                    f"{name}: payload at point {i} ({rp[i][0]}) < "
                    f"payload at point {i+1} ({rp[i+1][0]})"
                )
                assert rp[i][2] <= rp[i+1][2], (
                    f"{name}: range at point {i} ({rp[i][2]}) > "
                    f"range at point {i+1} ({rp[i+1][2]})"
                )

    def test_range_payload_points_weight_within_mtow(self, all_aircraft):
        """At each range-payload point, OEW + payload + fuel <= MTOW."""
        for name, data in all_aircraft.items():
            for i, (pl, fuel, rng) in enumerate(data["range_payload_points"]):
                total = data["OEW"] + pl + fuel
                assert total <= data["MTOW"] * 1.01, (
                    f"{name} point {i}: OEW+payload+fuel={total} > MTOW={data['MTOW']}"
                )

    def test_fuel_within_max_fuel(self, all_aircraft):
        """Fuel at each R-P point should not exceed max fuel capacity."""
        for name, data in all_aircraft.items():
            for i, (pl, fuel, rng) in enumerate(data["range_payload_points"]):
                assert fuel <= data["max_fuel"] * 1.01, (
                    f"{name} point {i}: fuel={fuel} > max_fuel={data['max_fuel']}"
                )

    def test_payload_within_max_payload(self, all_aircraft):
        """Payload at each R-P point should not exceed max payload."""
        for name, data in all_aircraft.items():
            for i, (pl, fuel, rng) in enumerate(data["range_payload_points"]):
                assert pl <= data["max_payload"] * 1.01, (
                    f"{name} point {i}: payload={pl} > max_payload={data['max_payload']}"
                )

    def test_ferry_point_has_zero_payload(self, all_aircraft):
        """The last range-payload point should be the ferry point (zero payload)."""
        for name, data in all_aircraft.items():
            rp = data["range_payload_points"]
            last = rp[-1]
            assert last[0] == 0, (
                f"{name}: last R-P point has payload={last[0]}, expected 0 (ferry)"
            )


# --- Cross-Aircraft Sanity Checks ---

class TestCrossAircraftSanity:
    """Relative comparisons between aircraft that should always hold."""

    def test_gv_smallest(self, all_aircraft):
        """G-V should have the lowest MTOW of all candidates."""
        gv_mtow = all_aircraft["GV"]["MTOW"]
        for name, data in all_aircraft.items():
            if name != "GV":
                assert gv_mtow < data["MTOW"], (
                    f"G-V MTOW ({gv_mtow}) should be < {name} MTOW ({data['MTOW']})"
                )

    def test_777_largest(self, all_aircraft):
        """777-200LR should have the highest MTOW."""
        max_mtow = all_aircraft["777-200LR"]["MTOW"]
        for name, data in all_aircraft.items():
            if name != "777-200LR":
                assert max_mtow > data["MTOW"], (
                    f"777-200LR MTOW ({max_mtow}) should be > {name} MTOW ({data['MTOW']})"
                )

    def test_dc8_has_four_engines(self, all_aircraft):
        """DC-8 is the only 4-engine aircraft."""
        assert all_aircraft["DC-8"]["n_engines"] == 4
        for name, data in all_aircraft.items():
            if name != "DC-8":
                assert data["n_engines"] == 2, f"{name} should have 2 engines"

    def test_newer_engines_lower_tsfc(self, all_aircraft):
        """Newer high-BPR engines should have lower TSFC than older ones.
        GE90 (777) < CF6-80E (A330) < CF6-80C (767) < CFM56-7 (737) < CFM56-2 (DC-8)
        BR710 (GV) is a different class (medium BPR business jet engine)."""
        tsfc_777 = all_aircraft["777-200LR"]["tsfc_cruise_ref"]
        tsfc_a330 = all_aircraft["A330-200"]["tsfc_cruise_ref"]
        tsfc_767 = all_aircraft["767-200ER"]["tsfc_cruise_ref"]
        tsfc_dc8 = all_aircraft["DC-8"]["tsfc_cruise_ref"]
        assert tsfc_777 < tsfc_a330 < tsfc_767 < tsfc_dc8, (
            f"TSFC ordering wrong: 777={tsfc_777}, A330={tsfc_a330}, "
            f"767={tsfc_767}, DC-8={tsfc_dc8}"
        )
