"""Run mission analysis for all aircraft across three science missions.

Phase 2 implementation:
- Mission 1: Long-range transport with engine-out (SCEL->KPMD)
- Mission 2: Vertical atmospheric sampling (NZCH->SCCI)
- Mission 3: Low-altitude smoke survey                    [not yet implemented]

Usage:
    python3 -m src.analysis.run_missions

Outputs:
    Mission performance tables printed to stdout.
    Segment data available in returned result dicts for plotting.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.aircraft_data.loader import load_all_aircraft
from src.analysis.run_calibration import run_all_calibrations
from src.models.missions import simulate_mission1_engine_out, simulate_mission2_sampling
from src.utils import fuel_cost

# The six study candidates (not seven — 737-900ER is excluded)
STUDY_CANDIDATES = ["DC-8", "GV", "P-8", "767-200ER", "A330-200", "777-200LR"]


def run_mission1(all_ac, calibrations, verbose=True):
    """Run Mission 1 (engine-out) for all study candidates.

    Args:
        all_ac: Aircraft data dict from load_all_aircraft()
        calibrations: Calibration results dict from run_all_calibrations()
        verbose: Print results to stdout

    Returns:
        dict keyed by designation -> mission result dict
    """
    results = {}
    for designation in STUDY_CANDIDATES:
        ac = all_ac[designation]
        cal = calibrations[designation]
        result = simulate_mission1_engine_out(ac, cal)
        results[designation] = result
        if verbose:
            _print_mission1_result(result)

    if verbose:
        _print_mission1_summary(results)

    return results


def _print_mission1_result(result):
    """Print detailed Mission 1 result for a single aircraft."""
    d = result["designation"]
    name = result["aircraft_name"]
    status = "FEASIBLE" if result["feasible"] else "INFEASIBLE"

    print(f"\n{'='*80}")
    print(f"  Mission 1: {name} ({d})")
    print(f"  Status: {status}")
    if result["infeasible_reason"]:
        print(f"  Reason: {result['infeasible_reason']}")
    print(f"{'='*80}")

    if result["n_aircraft"] > 1:
        print(f"  Fleet: {result['n_aircraft']} aircraft "
              f"(max payload {result['payload_actual_lb']:,.0f} lb each, "
              f"{result['payload_requested_lb']:,.0f} lb total)")

    pa = result["per_aircraft"]
    if pa is None:
        return

    print(f"\n  Weight Breakdown:")
    print(f"    OEW:              {pa['oew_lb']:>12,.0f} lb")
    print(f"    Payload:          {pa['payload_lb']:>12,.0f} lb")
    print(f"    Fuel loaded:      {pa['total_fuel_lb']:>12,.0f} lb")
    print(f"    Takeoff weight:   {pa['takeoff_weight_lb']:>12,.0f} lb")

    print(f"\n  Fuel Budget:")
    print(f"    Non-cruise (f_oh):{pa['non_cruise_fuel_lb']:>12,.0f} lb")
    print(f"    Cruise fuel:      {pa['cruise_fuel_lb']:>12,.0f} lb")

    s1 = pa["segment1"]
    s2 = pa["segment2"]

    print(f"\n  Segment 1 — Normal Cruise ({s1['n_engines']} engines):")
    print(f"    Range:            {s1['range_nm']:>12,.0f} nm")
    print(f"    Fuel burned:      {s1['fuel_burned_lb']:>12,.0f} lb")
    print(f"    Weight at start:  {s1['weight_at_start_lb']:>12,.0f} lb")
    print(f"    Weight at end:    {s1['weight_at_end_lb']:>12,.0f} lb")
    if s1["segments"]:
        alts1 = [s["altitude_ft"] for s in s1["segments"]]
        print(f"    Altitude range:   {min(alts1):>8,.0f} – {max(alts1):,.0f} ft")

    print(f"\n  Segment 2 — Engine-Out Cruise ({s2['n_engines']} engines, "
          f"+{(s2['drag_multiplier']-1)*100:.0f}% drag):")
    print(f"    Range:            {s2['range_nm']:>12,.0f} nm")
    print(f"    Fuel burned:      {s2['fuel_burned_lb']:>12,.0f} lb")
    print(f"    Weight at start:  {s2['weight_at_start_lb']:>12,.0f} lb")
    print(f"    Weight at end:    {s2['weight_at_end_lb']:>12,.0f} lb")
    if s2["segments"]:
        alts2 = [s["altitude_ft"] for s in s2["segments"]]
        print(f"    Altitude range:   {min(alts2):>8,.0f} – {max(alts2):,.0f} ft")

    print(f"\n  Mission Totals:")
    print(f"    Cruise range:     {pa['cruise_range_nm']:>12,.0f} nm")
    print(f"    + climb credit:   {pa['climb_credit_nm']:>12,.0f} nm")
    print(f"    + descent credit: {pa['descent_credit_nm']:>12,.0f} nm")
    print(f"    Total range:      {pa['total_range_nm']:>12,.0f} nm")
    print(f"    Required:         {5050:>12,.0f} nm")
    print(f"    Surplus/deficit:  {pa['range_surplus_nm']:>+12,.0f} nm")
    print(f"    Fuel burned:      {pa['total_fuel_burned_lb']:>12,.0f} lb")
    print(f"    Reserve remaining:{pa['reserve_fuel_lb']:>12,.0f} lb")
    if pa.get("fuel_at_destination_lb") is not None:
        print(f"    Fuel at dest:     {pa['fuel_at_destination_lb']:>12,.0f} lb")
    print(f"    Fuel cost:        ${pa['fuel_cost_usd']:>11,.0f}")
    print(f"    Cost/1000lb·nm:   ${pa['fuel_cost_per_1000lb_nm']:>11.4f}")

    if result["aggregate"]:
        agg = result["aggregate"]
        print(f"\n  Fleet Aggregate ({agg['n_aircraft']} aircraft):")
        print(f"    Total payload:    {agg['total_payload_lb']:>12,.0f} lb")
        print(f"    Total fuel:       {agg['total_fuel_lb']:>12,.0f} lb")
        print(f"    Total fuel cost:  ${agg['total_fuel_cost_usd']:>11,.0f}")
        print(f"    Cost/1000lb·nm:   ${agg['fuel_cost_per_1000lb_nm']:>11.4f}")


def _print_mission1_summary(results):
    """Print compact comparison table for Mission 1 across all aircraft."""
    print(f"\n\n{'='*120}")
    print("MISSION 1 SUMMARY: Long-Range Transport with Engine-Out (SCEL→KPMD, 5,050 nm, 46,000 lb)")
    print(f"{'='*120}")
    print(f"{'Aircraft':<12} {'Status':<10} {'n_ac':>4} {'Payload':>10} {'Fuel':>10} "
          f"{'Range':>8} {'Surplus':>8} {'Fuel@Dest':>10} "
          f"{'Cost':>10} {'$/klb·nm':>10}")
    print(f"{'-'*12} {'-'*10} {'-'*4} {'-'*10} {'-'*10} "
          f"{'-'*8} {'-'*8} {'-'*10} "
          f"{'-'*10} {'-'*10}")

    for d in STUDY_CANDIDATES:
        r = results[d]
        status = "OK" if r["feasible"] else "FAIL"
        pa = r["per_aircraft"]

        if pa is None:
            print(f"{d:<12} {status:<10} {r['n_aircraft']:>4} "
                  f"{'—':>10} {'—':>10} {'—':>8} {'—':>8} {'—':>10} {'—':>10} {'—':>10}")
            continue

        # Use aggregate cost metric if fleet > 1
        if r["aggregate"]:
            cost_display = r["aggregate"]["total_fuel_cost_usd"]
            metric_display = r["aggregate"]["fuel_cost_per_1000lb_nm"]
        else:
            cost_display = pa["fuel_cost_usd"]
            metric_display = pa["fuel_cost_per_1000lb_nm"]

        fad = pa.get("fuel_at_destination_lb")
        fad_str = f"{fad:>10,.0f}" if fad is not None else f"{'—':>10}"

        print(f"{d:<12} {status:<10} {r['n_aircraft']:>4} "
              f"{pa['payload_lb']:>10,.0f} {pa['total_fuel_lb']:>10,.0f} "
              f"{pa['total_range_nm']:>8,.0f} {pa['range_surplus_nm']:>+8,.0f} "
              f"{fad_str} "
              f"${cost_display:>9,.0f} ${metric_display:>9.4f}")

    print(f"\nNotes:")
    print(f"  - Payload column shows per-aircraft payload (may be < 46,000 lb for fleet operations)")
    print(f"  - Cost and $/klb·nm show fleet aggregate for multi-aircraft entries")
    print(f"  - Fuel@Dest = cruise fuel remaining at 5,050 nm (feasible aircraft only)")
    print(f"  - DC-8 and A330 fuel metrics are low-confidence (see PHASE2_STEP1_RECONCILIATION.md)")
    print()


def run_mission2(all_ac, calibrations, verbose=True):
    """Run Mission 2 (vertical sampling) for all study candidates.

    Args:
        all_ac: Aircraft data dict from load_all_aircraft()
        calibrations: Calibration results dict from run_all_calibrations()
        verbose: Print results to stdout

    Returns:
        dict keyed by designation -> mission result dict
    """
    results = {}
    for designation in STUDY_CANDIDATES:
        ac = all_ac[designation]
        cal = calibrations[designation]
        result = simulate_mission2_sampling(ac, cal)
        results[designation] = result
        if verbose:
            _print_mission2_result(result)

    if verbose:
        _print_mission2_summary(results)
        _print_mission2_ceiling_table(results)

    return results


def _print_mission2_result(result):
    """Print detailed Mission 2 result for a single aircraft."""
    d = result["designation"]
    name = result["aircraft_name"]
    status = "FEASIBLE" if result["feasible"] else "INFEASIBLE"

    print(f"\n{'='*80}")
    print(f"  Mission 2: {name} ({d})")
    print(f"  Status: {status}")
    if result["infeasible_reason"]:
        print(f"  Reason: {result['infeasible_reason']}")
    print(f"{'='*80}")

    if result["n_aircraft"] > 1:
        print(f"  Fleet: {result['n_aircraft']} aircraft "
              f"(max payload {result['payload_actual_lb']:,.0f} lb each, "
              f"{result['payload_requested_lb']:,.0f} lb total)")

    pa = result["per_aircraft"]
    if pa is None:
        return

    print(f"\n  Weight Breakdown:")
    print(f"    OEW:              {pa['oew_lb']:>12,.0f} lb")
    print(f"    Payload:          {pa['payload_lb']:>12,.0f} lb")
    print(f"    Fuel loaded:      {pa['total_fuel_lb']:>12,.0f} lb")
    print(f"    Takeoff weight:   {pa['takeoff_weight_lb']:>12,.0f} lb")

    print(f"\n  Fuel Budget (explicit reserves, no f_oh):")
    print(f"    Reserve fuel:     {pa['reserve_fuel_lb']:>12,.0f} lb")
    print(f"    Mission fuel:     {pa['mission_fuel_lb']:>12,.0f} lb")

    print(f"\n  Mission Results:")
    print(f"    Distance covered: {pa['distance_covered_nm']:>12,.0f} nm (of 4,200 nm)")
    print(f"    Total time:       {pa['total_time_hr']:>12.1f} hr")
    print(f"    Cycles completed: {pa['n_cycles']:>12d}")
    print(f"    Fuel burned:      {pa['fuel_burned_lb']:>12,.0f} lb")
    print(f"    Fuel remaining:   {pa['fuel_remaining_lb']:>12,.0f} lb")

    print(f"\n  Altitude Performance:")
    print(f"    Initial ceiling:  {pa['initial_ceiling_ft']:>12,.0f} ft")
    print(f"    Peak ceiling:     {pa['peak_ceiling_ft']:>12,.0f} ft")
    print(f"    Final ceiling:    {pa['final_ceiling_ft']:>12,.0f} ft")

    # Cycle detail table
    cycles = pa["cycles"]
    if cycles:
        print(f"\n  Cycle Details:")
        print(f"    {'#':>3} {'Ceiling':>10} {'Climb Fuel':>12} {'Desc Fuel':>12} "
              f"{'Cycle Dist':>12} {'Cycle Time':>10} {'W_end':>12} {'Partial':>8}")
        print(f"    {'-'*3} {'-'*10} {'-'*12} {'-'*12} "
              f"{'-'*12} {'-'*10} {'-'*12} {'-'*8}")
        for c in cycles:
            partial_str = "YES" if c.get("partial", False) else ""
            print(f"    {c['cycle']:>3d} {c['ceiling_ft']:>10,.0f} "
                  f"{c['climb_fuel_lb']:>12,.0f} {c['descent_fuel_lb']:>12,.0f} "
                  f"{c['total_distance_nm']:>12,.1f} {c['total_time_hr']:>10.2f} "
                  f"{c['weight_end_lb']:>12,.0f} {partial_str:>8}")

    print(f"\n  Cost:")
    print(f"    Fuel cost:        ${pa['fuel_cost_usd']:>11,.0f}")
    print(f"    Cost/1000lb·nm:   ${pa['fuel_cost_per_1000lb_nm']:>11.4f}")

    if result["aggregate"]:
        agg = result["aggregate"]
        print(f"\n  Fleet Aggregate ({agg['n_aircraft']} aircraft):")
        print(f"    Total payload:    {agg['total_payload_lb']:>12,.0f} lb")
        print(f"    Total fuel:       {agg['total_fuel_lb']:>12,.0f} lb")
        print(f"    Total fuel cost:  ${agg['total_fuel_cost_usd']:>11,.0f}")
        print(f"    Cost/1000lb·nm:   ${agg['fuel_cost_per_1000lb_nm']:>11.4f}")


def _print_mission2_summary(results):
    """Print compact comparison table for Mission 2 across all aircraft."""
    print(f"\n\n{'='*130}")
    print("MISSION 2 SUMMARY: Vertical Atmospheric Sampling (NZCH→SCCI, 4,200 nm, 52,000 lb)")
    print(f"{'='*130}")
    print(f"{'Aircraft':<12} {'Status':<8} {'n_ac':>4} {'Payload':>10} {'Fuel':>10} "
          f"{'Distance':>10} {'Cycles':>7} {'Init Ceil':>10} {'Peak Ceil':>10} "
          f"{'Cost':>10} {'$/klb·nm':>10}")
    print(f"{'-'*12} {'-'*8} {'-'*4} {'-'*10} {'-'*10} "
          f"{'-'*10} {'-'*7} {'-'*10} {'-'*10} "
          f"{'-'*10} {'-'*10}")

    for d in STUDY_CANDIDATES:
        r = results[d]
        status = "OK" if r["feasible"] else "FAIL"
        pa = r["per_aircraft"]

        if pa is None:
            print(f"{d:<12} {status:<8} {r['n_aircraft']:>4} "
                  f"{'—':>10} {'—':>10} {'—':>10} {'—':>7} "
                  f"{'—':>10} {'—':>10} {'—':>10} {'—':>10}")
            continue

        # Use aggregate cost metric if fleet > 1
        if r["aggregate"]:
            cost_display = r["aggregate"]["total_fuel_cost_usd"]
            metric_display = r["aggregate"]["fuel_cost_per_1000lb_nm"]
        else:
            cost_display = pa["fuel_cost_usd"]
            metric_display = pa["fuel_cost_per_1000lb_nm"]

        print(f"{d:<12} {status:<8} {r['n_aircraft']:>4} "
              f"{pa['payload_lb']:>10,.0f} {pa['total_fuel_lb']:>10,.0f} "
              f"{pa['distance_covered_nm']:>10,.0f} {pa['n_cycles']:>7d} "
              f"{pa['initial_ceiling_ft']:>10,.0f} {pa['peak_ceiling_ft']:>10,.0f} "
              f"${cost_display:>9,.0f} ${metric_display:>9.4f}")

    print(f"\nNotes:")
    print(f"  - Payload column shows per-aircraft payload (may be < 52,000 lb for fleet operations)")
    print(f"  - Cost and $/klb·nm show fleet aggregate for multi-aircraft entries")
    print(f"  - Init Ceil = ceiling on first cycle; Peak Ceil = highest ceiling achieved")
    print(f"  - Cycle bottom altitude: 5,000 ft; ceiling limited by thrust vs. drag")
    print(f"  - P-8 and A330 calibrations have unphysical CD0 — ceilings are lower confidence")
    print()


def _print_mission2_ceiling_table(results):
    """Print progressive ceiling table showing altitude vs. cycle for all aircraft."""
    print(f"\n{'='*100}")
    print("PROGRESSIVE CEILING TABLE (ft) — Mission 2")
    print(f"{'='*100}")

    # Find max cycles across all aircraft
    max_n = 0
    for d in STUDY_CANDIDATES:
        pa = results[d].get("per_aircraft")
        if pa and pa["cycles"]:
            max_n = max(max_n, len(pa["cycles"]))

    if max_n == 0:
        print("  No aircraft completed any cycles.")
        return

    # Header
    header = f"{'Cycle':>6}"
    for d in STUDY_CANDIDATES:
        header += f"  {d:>12}"
    print(header)
    print(f"{'-'*6}" + f"  {'-'*12}" * len(STUDY_CANDIDATES))

    # Data rows
    for i in range(max_n):
        row = f"{i+1:>6}"
        for d in STUDY_CANDIDATES:
            pa = results[d].get("per_aircraft")
            if pa and pa["cycles"] and i < len(pa["cycles"]):
                ceil = pa["cycles"][i]["ceiling_ft"]
                row += f"  {ceil:>12,.0f}"
            else:
                row += f"  {'—':>12}"
        print(row)

    print()


if __name__ == "__main__":
    print("Running calibrations (this may take several minutes)...")
    all_ac, calibrations = run_all_calibrations(verbose=False)

    print("\n" + "=" * 80)
    print("MISSION 1: Long-Range Transport with Engine-Out (SCEL → KPMD)")
    print("=" * 80)
    mission1_results = run_mission1(all_ac, calibrations, verbose=True)

    print("\n" + "=" * 80)
    print("MISSION 2: Vertical Atmospheric Sampling (NZCH → SCCI)")
    print("=" * 80)
    mission2_results = run_mission2(all_ac, calibrations, verbose=True)
