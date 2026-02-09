# Phase 2: Mission 1 — Long-Range Transport with Engine-Out

## Mission Definition

| Parameter | Value |
|---|---|
| Route | Santiago, Chile (SCEL) to Palmdale, CA (KPMD) |
| Distance | 5,050 nmi |
| Payload | 46,000 lb |
| Engine failure | At mission midpoint (2,525 nm from departure) |
| Fuel budget | f_oh hybrid (non_cruise_fuel = f_oh × W_tow) |

## Summary of Results

| Aircraft | Status | n_ac | Payload (lb) | Fuel (lb) | Range (nm) | Surplus (nm) | Cost | $/klb·nm |
|---|---|---|---|---|---|---|---|---|
| **767-200ER** | **PASS** | 1 | 46,000 | 162,000 | 6,252 | +1,202 | $132,985 | $0.5725 |
| **777-200LR** | **PASS** | 1 | 46,000 | 325,300 | 6,217 | +1,167 | $267,037 | $1.1495 |
| GV | FAIL | 8 | 5,750 ea | 36,550 ea | 4,853 | -197 | $240,030† | $1.0333† |
| A330-200 | FAIL | 1 | 46,000 | 221,619 | 4,633 | -417 | $181,926 | $0.7832 |
| P-8 | FAIL | 2 | 23,000 ea | 73,320 ea | 3,765 | -1,285 | $120,376† | $0.5182† |
| DC-8 | FAIL | 1 | 46,000 | 122,000 | 3,187 | -1,863 | $100,149 | $0.4311 |

†Fleet aggregate (cost and $/klb·nm are for the full fleet of n_ac aircraft)

**Only the 767-200ER and 777-200LR complete the mission.** The 767 is the clear winner on cost efficiency ($0.57/klb·nm vs. $1.15 for the 777). The 767 also carries less than half the fuel (162,000 lb vs. 325,300 lb).

## Methodology

### Two-Segment Cruise Model

The engine-out mission is modeled as two consecutive cruise segments:

1. **Segment 1 (0 → 2,525 nm): Normal cruise**, all engines, no drag penalty. The step-cruise integrator runs at full resolution, then `_find_fuel_at_distance()` interpolates to find the exact fuel burn and aircraft weight at the midpoint distance minus climb credit (2,525 - 200 = 2,325 nm of cruise).

2. **Segment 2 (2,525 → end of fuel): Engine-out cruise**, n_engines - 1, +10% drag multiplier. The altitude optimizer naturally finds a lower ceiling due to reduced thrust available. The segment runs until all remaining cruise fuel is exhausted.

**Total mission range** = climb credit (200 nm) + segment 1 cruise range + segment 2 cruise range + descent credit (120 nm).

### Fuel Budget (f_oh Hybrid)

Per the confirmed Phase 2 approach (see PHASE2_STEP1_RECONCILIATION.md):
- Total fuel = min(MTOW - OEW - payload, max_fuel)
- Non-cruise overhead = f_oh × W_tow (absorbs taxi, climb, descent, reserves, and calibration residuals)
- Cruise fuel = total fuel - non-cruise overhead

### Fleet Sizing

Aircraft that cannot carry 46,000 lb payload (GV max payload = 5,750 lb, P-8 max payload = 23,885 lb) are modeled as a fleet. Payload is divided evenly across n = ceil(46,000 / max_payload) aircraft. Cost metrics are aggregated.

### Engine-Out Drag Bug Fix

A bug was found and fixed in `optimal_cruise_altitude()`: the thrust-available check was comparing against un-adjusted drag, so during engine-out segments the altitude optimizer could select altitudes where thrust was sufficient for normal drag but not for the 10%-higher engine-out drag. The fix passes the `drag_multiplier` through from `step_cruise_range()` to the altitude check. Default value is 1.0, so the fix is fully backward-compatible (all existing calibration and Phase 1 tests pass without change).

## Detailed Observations

### Feasible Aircraft

**767-200ER** — Best overall Mission 1 performer.
- Lowest f_oh of the feasible aircraft (0.030), so 97% of fuel goes to cruise
- Normal cruise at 35,000–39,000 ft; engine-out cruise at 33,000–43,000 ft
- The engine-out altitude *increases* over the segment as fuel burns off and the aircraft gets lighter — the single GE CF6-80C2 engine has enough thrust to climb as weight decreases
- 1,202 nm range surplus provides substantial safety margin
- Lowest cost per payload-distance of all aircraft ($0.57/klb·nm)

**777-200LR** — Completes mission but at much higher cost.
- Higher f_oh (0.080), removing 55,431 lb as overhead
- Normal cruise at 35,000–37,000 ft; engine-out cruise stuck at 25,000 ft
- The single GE90-115B engine cannot push the 614,327 lb aircraft above 25,000 ft with +10% drag. This is thrust-limited, not buffet-limited — the 777 is simply too heavy
- Engine-out altitude remains at 25,000 ft for the entire segment (the aircraft never gets light enough to climb)
- 325,300 lb fuel load is double the 767's, yielding fuel cost of $267,037 vs. $133,000
- Cost efficiency ($1.15/klb·nm) is the worst among all aircraft, even worse than the 8-aircraft GV fleet

### Infeasible Aircraft

**GV** — Closest to feasibility (-197 nm shortfall).
- Requires 8 aircraft to carry 46,000 lb (max payload 5,750 lb each)
- Excellent aerodynamic efficiency: cruises at 43,000–46,000 ft on 2 engines, drops to 40,000–45,000 ft on 1 engine
- The altitude drop on engine-out is relatively small (~3,000 ft) because the GV is light enough that a single Rolls-Royce BR710 can sustain near-cruise altitude
- Fleet aggregate cost of $240,030 makes it the most expensive option
- With 197 nm less range, could potentially complete the mission with slightly reduced payload

**A330-200** — Falls 417 nm short.
- f_oh calibrated to 0.000, meaning ALL fuel is allocated to cruise — no overhead at all. This is a known calibration edge case (see PHASE2_STEP1_RECONCILIATION.md)
- Despite burning all 221,619 lb as cruise fuel, range still falls short
- Engine-out segment stuck at 25,000 ft (thrust-limited with single Trent 772B engine at 443,770 lb weight)
- The A330 result is flagged as **low-confidence** — the calibrated model has an unphysical f_oh=0 and e=2.165 (Oswald efficiency >1, which is physically impossible but compensates for other model errors)

**P-8** — Falls 1,285 nm short.
- Requires 2 aircraft for the 46,000 lb payload (max payload 23,885 lb)
- High f_oh (0.180) removes 33,810 lb as overhead, leaving only 39,510 lb for cruise
- Engine-out segment stuck at 25,000 ft (single CFM56-7B engine cannot sustain higher altitude at 164,451 lb)
- Fleet cost of $120,376 is moderate, but the mission is clearly infeasible

**DC-8** — Worst performer (-1,863 nm shortfall).
- Highest f_oh (0.260) removes 84,582 lb of the 122,000 lb fuel load as overhead, leaving only 37,418 lb for cruise
- This is the most extreme manifestation of the calibration compensation issue: k_adj=0.605 makes the cruise model burn ~40% less fuel than reality, so f_oh must remove proportionally more fuel to match published range
- Engine-out segment on 3 engines achieves 39,500–40,000 ft (the 4-engine configuration gives it more thrust redundancy, so the altitude drop is small)
- Only burns 542 nm in engine-out before exhausting cruise fuel — the aircraft simply doesn't have enough cruise fuel
- Result is flagged as **low-confidence** due to extreme calibration parameters

## Key Modeling Choices and Limitations

### Choices

1. **Mach number held constant after engine failure.** The aircraft maintains its nominal cruise Mach in the engine-out segment. In practice, a Mach reduction of 2–5% might occur, but modeling this would require a speed optimization loop that doesn't exist in the current framework. The altitude optimizer handles the primary thrust constraint.

2. **Climb/descent distance credits.** Uses the Path A convention of 200 nm climb credit + 120 nm descent credit, imported from `calibration.py`. This maintains consistency with the calibrated model — the same assumptions used to fit the parameters are used to compute the mission.

3. **Fuel cost basis.** Cost is computed on total fuel loaded (not just fuel burned), since all fuel must be purchased regardless of whether it's consumed in cruise or lost to overhead. Fuel price is $5.50/gal Jet-A.

4. **Reserve interpretation.** In the f_oh model, reserves are embedded in the overhead fraction — they are not computed separately. The "Reserve remaining" column shows cruise fuel not burned (always 0 here because `step_cruise_range` exhausts all cruise fuel to determine maximum range). For feasible aircraft, the range surplus (1,200+ nm) represents the safety margin — this fuel would go unburned in an actual mission.

### Limitations

1. **f_oh absorbs calibration residuals**, not just physical non-cruise fuel. This is well-documented (see PHASE2_STEP1_RECONCILIATION.md) and is the reason the DC-8 and A330 results are flagged as low-confidence.

2. **Engine-out drag increment is fixed at +10%** regardless of aircraft type. In reality, the increment depends on the ratio of engine nacelle drag to total drag, rudder deflection required, and other factors specific to each airframe.

3. **No diversion modeling.** The mission tests whether the aircraft can fly the full 5,050 nm distance. It does not model alternate airports, holding fuel, or regulatory reserve requirements beyond what's captured in f_oh.

4. **Step-cruise altitude changes are instantaneous.** The model recomputes optimal altitude at each integration step as weight decreases; actual step-climbs involve ATC coordination and fuel cost for the climb.

## Confidence Assessment

| Aircraft | Confidence | Notes |
|---|---|---|
| 767-200ER | **High** | f_oh=0.030 is physical, k_adj=0.969, RMS error 0.0% |
| 777-200LR | **Medium** | f_oh=0.080 is reasonable, but RMS error 6.5% |
| GV | **Medium** | f_oh=0.131 is somewhat high; model may overallocate to overhead |
| P-8 | **Low-Medium** | Derived from 737-900ER, extreme parameters (f_oh=0.180) |
| A330-200 | **Low** | f_oh=0.000, e>1 unphysical; known calibration edge case |
| DC-8 | **Low** | k_adj=0.605 (TSFC ~40% low), f_oh=0.260; strong compensation effects |

## Questions for Reviewer

1. **Reserve reporting:** The f_oh model doesn't produce an explicit reserve figure. For feasible aircraft, the range surplus (1,200+ nm for 767/777) is the meaningful safety metric. Should I add a "fuel remaining at mission distance" calculation by running `_find_fuel_at_distance` up to the required 5,050 nm, so we can report both total capability and the actual fuel state at destination?

2. **777 engine-out altitude ceiling:** The 777 spends its entire engine-out segment at 25,000 ft (the model's minimum search altitude). Is this a concern? The aircraft is 614,000 lb with one engine — physically this seems right, but the 25,000 ft floor is a hard-coded parameter (`h_min=25_000` in `optimal_cruise_altitude`). Should we lower it to see if the 777 would actually be thrust-limited below 25,000 ft?

3. **A330 confidence:** With f_oh=0.000 and Oswald efficiency >1, the A330 calibration is clearly non-physical. The Mission 1 result (FAIL by 417 nm) may be unreliable in either direction. Should we flag it differently than the other infeasible results, or is the current "low-confidence" note sufficient?

4. **GV near-feasibility:** The GV fleet of 8 aircraft misses by only 197 nm. A modest payload reduction (~15%) would likely make it feasible. Is this worth quantifying for the report, or do we treat the 46,000 lb payload requirement as absolute?

## Reproduction

```bash
python3 -m src.analysis.run_missions
```

Runtime: ~8 minutes (dominated by calibration). Prints detailed per-aircraft results and summary table.

## Files Changed

| File | Change |
|---|---|
| `src/models/performance.py` | Added `drag_multiplier` parameter to `optimal_cruise_altitude()` and passed through from `step_cruise_range()` |
| `src/models/missions.py` | **New file.** `simulate_mission1_engine_out()`, `_find_fuel_at_distance()`, `_determine_infeasibility()`, `_infeasible_result()` |
| `src/analysis/run_missions.py` | Updated from stub to functional Mission 1 driver with formatted output |
