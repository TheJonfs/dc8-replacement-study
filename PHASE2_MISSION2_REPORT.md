# Phase 2: Mission 2 — Vertical Atmospheric Sampling (NZCH → SCCI)

## Mission Definition

| Parameter | Value |
|---|---|
| Route | Christchurch, New Zealand (NZCH) to Punta Arenas, Chile (SCCI) |
| Distance | 4,200 nmi |
| Payload | 52,000 lb |
| Profile | Repeating sawtooth climb-descend cycles for vertical atmospheric column sampling |
| Cycle bottom altitude | 5,000 ft |
| Ceiling criterion | ROC < 100 ft/min (standard service ceiling) |
| Fuel budget | Explicit reserves only (no f_oh) — per PHASE2_STEP1_RECONCILIATION.md |

## Summary of Results

### Assessed Outcomes

| Aircraft | Status | Confidence | n_ac | Cycles | Peak Ceiling (ft) | Cost | $/klb·nm | Notes |
|---|---|---|---|---|---|---|---|---|
| **DC-8** | **PASS** | **Low** | 1 | 22 | 42,000 | $95,224 | $0.4360 | Completes with fuel to spare; ceiling airframe-limited |
| **767-200ER** | **PASS** | **High** | 1 | 20 | 43,100 | $132,985 | $0.6089 | Reliable result; best single-aircraft option after DC-8 on cost |
| **777-200LR** | **PASS** | **Low** | 1 | 19 | 43,100 | $267,037 | $1.2227 | Completes but at twice the 767's cost |
| GV | PASS | Medium | 9 | 17 | 51,000 | $269,828† | $1.2355† | Highest ceiling; operationally impractical fleet |
| A330-200 | FAIL (-15 nm) | Low | 1 | 20 | 41,100 | $181,926 | $0.8330 | Marginally short; fuel exhausted on cycle 20 |
| P-8 | FAIL | Low | 3 | 0 | 5,000 | $84,744† | $0.3880† | Cannot climb — drag exceeds thrust at all altitudes |

†Fleet aggregate (cost and $/klb·nm are for the full fleet of n_ac aircraft)

### Key Takeaways

**Three aircraft pass as single-ship solutions: DC-8, 767-200ER, and 777-200LR.** The DC-8 is the cheapest ($0.44/klb·nm) but its result is low-confidence due to extreme TSFC calibration compensation (k_adj=0.605). The 767-200ER is the only high-confidence pass ($0.61/klb·nm). The 777-200LR passes but costs twice as much ($1.22/klb·nm).

**Progressive ceiling increase does not manifest.** This was the mission's key scientific metric — as fuel burns off, lighter aircraft should reach higher altitudes. In practice, all aircraft hit their published service ceiling limit on every cycle rather than being thrust-limited. The ceilings are flat: the DC-8 achieves 42,000 ft on cycle 1 and cycle 22 identically. This means the aircraft are structurally or aerodynamically ceiling-limited at these payload/weight combinations, not thrust-limited. While physically correct behavior for these heavy-payload missions, it means the progressive altitude improvement that scientists value most would not materialize.

**The GV reaches the highest ceiling (51,000 ft) but requires 9 aircraft.** At 5,778 lb payload per aircraft, the 9-ship fleet costs $269,828 aggregate and is operationally impractical.

**The A330-200 fails by only 15 nm** — essentially marginal. It runs out of fuel during cycle 20. However, the A330's calibration is low-quality (CD0=0.033, e=2.165, f_oh=0.000), so this marginal result could go either way in reality.

**The P-8 cannot climb at all.** Its calibrated CD0 of 0.060 produces drag that exceeds available thrust even at 5,000 ft. This is an unphysical calibration artifact — the real P-8 can obviously climb — but the model cannot produce any useful Mission 2 results for this aircraft.

## Detailed Observations

### Feasible Aircraft

**DC-8** — Lowest cost, lowest confidence.
- 22 sawtooth cycles, covering 4,200 nmi
- Ceiling locked at 42,000 ft (published service ceiling) on every cycle
- Mission fuel: 53,939 lb of 73,982 lb available after reserves
- The DC-8's low cost reflects its calibrated parameters: k_adj=0.605 means TSFC is ~40% below reference, producing artificially low fuel burn. The absolute cost numbers should not be taken at face value
- Despite calibration concerns, the DC-8 completing this mission is qualitatively plausible — it carries 52,000 lb (its max payload) and has 4 engines providing ample climb thrust

**767-200ER** — Best single-aircraft result with high confidence.
- 20 sawtooth cycles, covering 4,200 nmi
- Ceiling locked at 43,100 ft (published service ceiling) on every cycle
- Mission fuel: 98,625 lb of 117,597 lb available after reserves
- Calibrated parameters are physical: CD0=0.018, e=0.732, k_adj=0.951, RMS 0.0%
- Cost of $132,985 ($0.61/klb·nm) is moderate and reliable
- Carries the full 52,000 lb payload with 110,228 lb fuel remaining capacity to MTOW

**777-200LR** — Passes but expensive.
- 19 sawtooth cycles, covering 4,200 nmi
- Ceiling locked at 43,100 ft (published service ceiling) on every cycle
- Mission fuel: 203,729 lb of 244,474 lb available after reserves
- The 777 burns roughly 2× the fuel of the 767 per cycle due to its much higher weight (MTOW 766,000 lb vs. 395,000 lb)
- Cost of $267,037 ($1.22/klb·nm) is the highest of any single-aircraft solution
- Calibrated CD0=0.041 is unphysical — low-confidence result despite passing

### Infeasible Aircraft

**GV** — Passes individually but infeasible as a fleet.
- Requires 9 aircraft to carry 52,000 lb (max payload 5,750 lb each → 5,778 lb share)
- Each aircraft completes 17 cycles reaching 51,000 ft — the highest ceiling in the study
- The GV's light weight and high service ceiling (51,000 ft) make it aerodynamically excellent for this profile
- Fleet aggregate cost $269,828 ($1.24/klb·nm)
- Per reviewer precedent from Mission 1: 9-aircraft coordination is operationally impractical

**A330-200** — Marginally fails (-15 nm).
- 20 cycles completed before fuel exhaustion
- Ceiling at 41,100 ft — slightly lower than the 767 and 777 due to lower published service ceiling
- Falls 15 nm short of 4,200 nm — just 0.4% of mission distance
- Calibration quality is poor: e=2.165 (Oswald efficiency >1) and f_oh=0.000 are both unphysical
- The true answer could easily be pass or fail; the margin is within model uncertainty

**P-8** — Complete failure.
- Requires 3 aircraft to carry 52,000 lb (max payload 23,885 lb each)
- 0 cycles completed — the climb_segment function returns immediately because drag exceeds thrust at 5,000 ft
- Calibrated CD0=0.060 is 3–4× higher than physical reality (~0.015–0.020)
- A zero-progress guard in the simulator correctly detects this pathological case and terminates cleanly
- The P-8 result is entirely unreliable for Mission 2

## Methodology

### Sawtooth Cycle Model

Each cycle consists of two phases:

1. **Climb phase (altitude-stepping integration):** Starting at 5,000 ft, the model integrates in 1,000 ft altitude steps up to the aircraft's service ceiling. At each step:
   - Compute drag from the parabolic polar (CD = CD0 + CL²/πARe)
   - Compute available thrust from `thrust_available_cruise()` with density-ratio lapse
   - Compute excess thrust → rate of climb: ROC = V × (T_excess / W)
   - Stop if ROC < 100 ft/min (service ceiling reached) or T_excess ≤ 0
   - Compute fuel flow = thrust_required × TSFC, horizontal distance = V·cos(γ)·dt

2. **Descent phase (bulk calculation):** From the ceiling back to 5,000 ft at 2,000 ft/min:
   - Time = Δh / 2,000 ft/min
   - Fuel = 10% of cruise fuel flow at mid-descent altitude × time
   - Distance = TAS at mid-descent altitude × time

The mission accumulates distance and fuel burn across cycles until either 4,200 nm is covered (pass) or fuel is exhausted (fail).

### Fuel Budget (Explicit Reserves, No f_oh)

Per the Phase 2 reconciliation decision, Mission 2 does not use the f_oh overhead fraction. The sawtooth profile has no sustained cruise analogous to the calibration regime, so f_oh would inappropriately remove fuel:

```
total_fuel = min(MTOW - OEW - payload, max_fuel)
reserve_fuel = compute_reserve_fuel(total_fuel, ac, CD0, e, k_adj)
mission_fuel = total_fuel - reserve_fuel
```

Reserve fuel uses the standard 3-component policy: 200 nm alternate + 30 min hold + 5% contingency.

### Fleet Sizing

Aircraft that cannot carry 52,000 lb payload are modeled as a fleet:
- GV: max payload 5,750 lb → ceil(52,000 / 5,750) = 9 aircraft, 5,778 lb each
- P-8: max payload 23,885 lb → ceil(52,000 / 23,885) = 3 aircraft, 17,333 lb each

### Fuel Cost

Cost is computed on total fuel loaded (all fuel must be purchased). Fuel price: $5.50/gal Jet-A.

## Key Modeling Choices and Limitations

### Choices

1. **Cycle bottom altitude = 5,000 ft.** Per reviewer guidance, 5,000 ft is representative for atmospheric column sampling. The 1,500 ft figure applies to Mission 3 (smoke survey), not Mission 2.

2. **Constant Mach climb at 95% cruise Mach.** A simplification — real climbs use constant IAS below the transition altitude then constant Mach above. Consistent with the rest of the model.

3. **Descent at 90% cruise Mach, 2,000 ft/min.** Standard transport idle descent parameters.

4. **Idle descent fuel = 10% of cruise fuel flow.** Scaled to aircraft size, replacing the fixed 300 lb from Mission 1. This properly accounts for large aircraft (A330, 777) having idle flows of 1,000–2,000 lb per descent.

5. **No level cruise segments between cycles.** The model transitions directly from descent bottom to the next climb. Any low-altitude transit would add fuel burn and distance, slightly improving feasibility for marginal aircraft.

### Limitations

1. **Ceilings are flat — no progressive increase.** All aircraft hit their published service ceiling on every cycle. The model caps altitude at the published ceiling, so even as weight decreases, the maximum altitude doesn't change. To observe thrust-limited progressive ceiling increases, the aircraft would need to be operating at weights where thrust limits the ceiling below the published value. At 52,000 lb payload, all aircraft are heavy enough that thrust reaches the published ceiling with margin to spare on every cycle.

2. **Published service ceilings may not be applicable during sawtooth operations.** The published ceiling is a certification limit for sustained flight. During sampling climbs, the aircraft might briefly exceed this altitude. The model conservatively enforces the published ceiling as a hard limit.

3. **Calibrated CD0 makes P-8 results useless for Mission 2.** The P-8's calibrated CD0=0.060 produces drag exceeding thrust at all altitudes, making climb impossible. The real P-8 can unquestionably climb; the model failure is a direct consequence of the calibration pushing CD0 to an unphysically high value to compensate for other model errors.

4. **Climb integration step size (1,000 ft).** Adequate for the long climbs in Mission 2 (35,000+ ft of altitude gain per cycle), but not rigorously validated against finer step sizes. The effect on total fuel burn is expected to be small (sub-1%).

5. **No wind effects.** The 4,200 nm distance is treated as still-air. Prevailing westerlies on the NZCH→SCCI route would provide a tailwind, potentially reducing fuel burn and improving feasibility for marginal cases like the A330.

## Confidence Assessment

| Aircraft | Confidence | Notes |
|---|---|---|
| 767-200ER | **High** | CD0=0.018 physical, k_adj=0.951, RMS 0.0%. Climb dynamics reliable. |
| GV | **Medium** | CD0=0.015 physical. f_oh=0.131 (not used in Mission 2). k_adj=0.801 moderate. |
| DC-8 | **Low** | k_adj=0.605 (TSFC ~40% below reference). f_oh=0.260 (not used, but indicates calibration compensation). Qualitatively plausible. |
| 777-200LR | **Low** | CD0=0.041 unphysical. Did not converge during calibration. Passes on fuel volume alone. |
| A330-200 | **Low** | CD0=0.033, e=2.165, f_oh=0.000 all unphysical. Marginal result within model error. |
| P-8 | **None** | CD0=0.060 makes climb impossible. No useful Mission 2 data. |

The confidence assessment is consistent with Mission 1: the **767-200ER and GV have the only physically grounded calibrations**. The other four aircraft have at least one calibrated parameter far from physical reality.

## Comparison with Mission 1

| Aircraft | Mission 1 | Mission 2 | Cost Change | Notes |
|---|---|---|---|---|
| DC-8 | FAIL (-1,863 nm) | PASS | — | Mission 2 is shorter (4,200 vs 5,050 nm) and has no engine-out |
| 767-200ER | PASS (+1,202 nm) | PASS | $133k → $133k | Comparable cost; Mission 2 has explicit reserves vs f_oh |
| 777-200LR | LIKELY PASS | PASS | $267k → $267k | Same fuel load; high cost per payload-distance persists |
| GV | FAIL (-195 nm) | PASS (9 ac) | $240k → $270k† | Higher fleet count (8→9) because heavier payload (52k vs 46k lb) |
| A330-200 | UNCERTAIN | FAIL (-15 nm) | — | Marginally infeasible in both missions |
| P-8 | FAIL | FAIL (0 cycles) | — | Unphysical calibration prevents any useful analysis |

†Fleet aggregate costs

**Key pattern:** The DC-8 flips from FAIL (Mission 1) to PASS (Mission 2). This is primarily because Mission 2 is 850 nm shorter, has no engine-out degradation, and uses explicit reserves instead of the f_oh hybrid (the DC-8's f_oh=0.260 removes 26% of fuel as overhead in Mission 1, while explicit reserves remove far less). However, the DC-8's pass is low-confidence.

## Open Questions for Reviewer

1. **Flat ceilings:** The progressive ceiling increase — the core scientific metric for this mission — does not appear because all aircraft are airframe-ceiling-limited rather than thrust-limited at 52,000 lb payload. Should we also model a reduced payload scenario (e.g., 30,000 lb) to demonstrate the thrust-limited regime where progressive ceiling increase would actually manifest? Alternatively, should we raise or remove the published ceiling cap and let the model find the true thrust-limited ceiling at each weight?

2. **A330 marginal result (-15 nm):** The A330 fails by 0.4% of mission distance with a low-quality calibration. Should this be assessed as "UNCERTAIN" rather than "FAIL," similar to how the 777 was assessed as "LIKELY PASS" in Mission 1?

3. **P-8 assessment:** The P-8 produces zero useful data for Mission 2. Should the report carry forward any qualitative assessment (e.g., based on the 737-900ER's known climb capabilities), or simply note the model limitation and move on?

## Reproduction

```bash
python3 -m src.analysis.run_missions
```

Runtime: ~11 minutes (dominated by calibration). Prints detailed per-aircraft results, summary table, and progressive ceiling table for both Mission 1 and Mission 2.

## Files Changed (Cumulative from Mission 1)

| File | Change |
|---|---|
| `src/models/missions.py` | Added `climb_segment()`, `descend_segment()`, `simulate_mission2_sampling()` with zero-progress guard |
| `src/analysis/run_missions.py` | Added `run_mission2()`, `_print_mission2_result()`, `_print_mission2_summary()`, `_print_mission2_ceiling_table()`; updated `__main__` for both missions |
| `tests/test_missions.py` | New file: 32 tests covering climb_segment (11), descend_segment (8), and Mission 2 orchestrator (13) |
