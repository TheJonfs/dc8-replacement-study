# Phase 2: Mission 1 — Long-Range Transport with Engine-Out (Revised)

## Mission Definition

| Parameter | Value |
|---|---|
| Route | Santiago, Chile (SCEL) to Palmdale, CA (KPMD) |
| Distance | 5,050 nmi |
| Payload | 46,000 lb |
| Engine failure | At mission midpoint (2,525 nm from departure) |
| Fuel budget | f_oh hybrid (non_cruise_fuel = f_oh × W_tow) |

## Summary of Results

### Assessed Outcomes

Engine-out results are only reliable for aircraft with physically-grounded calibrations (DC-8, GV, 767-200ER). For the P-8, A330, and 777, the calibrated CD0 makes single-engine flight impossible at all altitudes in the model — an unphysical artifact. Their engine-out status is assessed using engineering judgment rather than model output alone (see Altitude Investigation below).

| Aircraft | Status | Confidence | n_ac | Fuel@Dest (lb) | Cost | $/klb·nm | Notes |
|---|---|---|---|---|---|---|---|
| **767-200ER** | **PASS** | **High** | 1 | 25,732 | $132,985 | $0.5725 | Engine-out modeled; result reliable |
| 777-200LR | LIKELY PASS | Low | 1 | — | $267,037 | $1.1495 | Engine-out not reliably modeled (CD0 artifact); passes on range-payload envelope alone |
| GV | FAIL (-195 nm) | Medium | 8 | — | $240,030† | $1.0333† | Engine-out modeled; result plausible |
| A330-200 | UNCERTAIN | Low | 1 | — | $181,926 | $0.7832 | Engine-out not reliably modeled; normal-cruise calibration also poor |
| P-8 | FAIL | Low | 2 | — | $120,376† | $0.5182† | Engine-out not reliably modeled; also range-limited |
| DC-8 | FAIL (-1,863 nm) | Low | 1 | — | $100,149 | $0.4311 | Engine-out modeled (3/4 engines); range-limited regardless |

†Fleet aggregate (cost and $/klb·nm are for the full fleet of n_ac aircraft)

### Raw Model Output

For reference, the raw model results before engineering assessment:

| Aircraft | Range (nm) | Surplus (nm) | Payload (lb) | Fuel (lb) | EO Altitude |
|---|---|---|---|---|---|
| 767-200ER | 6,252 | +1,202 | 46,000 | 162,000 | 33,000–43,000 ft |
| 777-200LR | 4,622 | -428 | 46,000 | 325,300 | 10,000 ft (floor) |
| GV | 4,855 | -195 | 5,750 ea | 36,550 ea | 40,000–45,000 ft |
| A330-200 | 3,741 | -1,309 | 46,000 | 221,619 | 10,000 ft (floor) |
| P-8 | 3,276 | -1,774 | 23,000 ea | 73,320 ea | 10,000 ft (floor) |
| DC-8 | 3,187 | -1,863 | 46,000 | 122,000 | 39,500–40,000 ft |

### Key Takeaways

**The 767-200ER is the only aircraft that demonstrably passes** with high model confidence. It has the best cost efficiency ($0.57/klb·nm) and arrives with 25,732 lb of cruise fuel remaining at 5,050 nm.

**The 777-200LR likely passes in reality** — its range-payload diagram shows it can carry 46,000 lb well beyond 5,050 nm under normal cruise, and ETOPS-330 certification means the real aircraft can sustain single-engine cruise at reasonable altitudes. However, even if it passes, it costs twice as much as the 767 ($1.15 vs. $0.57/klb·nm).

**The A330-200 result is unreliable in either direction** — both its engine-out and normal-cruise calibrations are poor (f_oh=0.000, e=2.165).

**The DC-8 cannot complete this mission** at 46,000 lb payload, confirming the need for replacement on long-range missions. This mission was selected specifically because it stresses the DC-8's capability.

## Changes Since Initial Report

This is a revised report incorporating reviewer feedback from the first submission. Three changes were made:

### 1. Fuel-at-Destination Metric (Reviewer Q1: "Yes, add this")

For feasible aircraft, the model now computes cruise fuel remaining at exactly 5,050 nm using `_find_fuel_at_distance()`. The 767-200ER arrives with **25,732 lb** of cruise fuel — in addition to the reserves embedded in f_oh. This gives a meaningful operational metric: the fuel state at destination.

### 2. Lower Engine-Out Altitude Floor (Reviewer Q2: "Yes, lower it")

The altitude search floor for engine-out segments was lowered from 25,000 ft to 10,000 ft. This exposed two issues:

**Non-monotonic thrust-drag behavior.** The original optimizer used `break` when thrust was insufficient — it assumed "if thrust fails at altitude h, it fails at all h' > h." This is true for the CL buffet check (CL increases monotonically with altitude) but **not** for thrust vs. drag. At low altitudes, high dynamic pressure creates high drag even though thrust is also high. At mid-altitudes, the balance can be favorable before thrust lapse dominates at high altitudes. The fix: changed the thrust check from `break` to `continue`, allowing the optimizer to search through the full altitude range and find the true optimum.

**Unphysical calibrated drag for three aircraft.** With the floor lowered and the search corrected, the model revealed that for the P-8, A330, and 777, single-engine thrust is insufficient to sustain level flight at *any* altitude from 10,000 to 43,000 ft. This is a calibration artifact — their calibrated CD0 values (0.060, 0.033, and 0.041 respectively) are 2–4× higher than physical reality (~0.015–0.020 for transport aircraft), because the calibration optimizer pushed CD0 high to compensate for other model errors.

### 3. Mach Reduction Note (Reviewer additional note)

Added as a known simplification in the Limitations section. Standard engine-out procedure involves decelerating ~0.02–0.05 Mach below normal cruise, but this is a secondary effect compared to the altitude change.

## Altitude Investigation Detail

The engine-out thrust margin diagnostic at the weight where each aircraft experiences engine failure:

| Aircraft | n_eng EO | CD0 (cal) | Thrust@25k | Drag×1.1@25k | Margin@25k | EO Altitude |
|---|---|---|---|---|---|---|
| DC-8 | 3 | 0.014 | 36,147 | 19,663 | **+16,484** | 39,500–40,000 ft |
| GV | 1 | 0.015 | 8,078 | 7,531 | **+548** | 40,000–45,000 ft |
| 767-200ER | 1 | 0.018 | 28,753 | 26,746 | **+2,008** | 33,000–43,000 ft |
| P-8 | 1 | 0.060 | 14,952 | 31,977 | **-17,025** | 10,000 ft (floor) |
| A330-200 | 1 | 0.033 | 39,433 | 55,092 | **-15,659** | 10,000 ft (floor) |
| 777-200LR | 1 | 0.041 | 60,300 | 86,444 | **-26,145** | 10,000 ft (floor) |

Aircraft with positive margins find their optimal engine-out altitude through the normal search process. Aircraft with negative margins at all altitudes default to h_min (10,000 ft), where drag is even higher due to dense air — this penalizes their range significantly.

**Physical reality check:** All ETOPS-certified twin-engine aircraft must demonstrate single-engine cruise capability. The P-8, A330, and 777 can unquestionably fly on one engine in reality. The model's failure to reproduce this is a direct consequence of the calibration absorbing errors into CD0, producing effective drag coefficients far above physical values.

**Impact on the 777 result:** With h_min=25,000 ft (original), the 777 passed with +1,167 nm surplus. With h_min=10,000 ft and thrust insufficient everywhere, the optimizer falls to 10,000 ft, where fuel burn roughly doubles, and the 777 fails by -428 nm. The true answer is somewhere in between — the 777 *probably* passes this mission in reality, but the model cannot reliably determine this.

## Detailed Observations

### The Sole Feasible Aircraft

**767-200ER** — Clear Mission 1 winner.
- Lowest f_oh (0.030), so 97% of fuel goes to cruise
- Normal cruise at 35,000–39,000 ft; engine-out cruise at 33,000–43,000 ft
- The engine-out altitude *increases* over the segment as fuel burns off — the single CF6-80C2 has enough thrust to sustain and climb as weight decreases
- 1,202 nm range surplus + 25,732 lb fuel at destination = substantial safety margin
- Lowest cost per payload-distance of all aircraft ($0.57/klb·nm)
- **Highest confidence result** in the study (calibrated CD0=0.018 is physical, RMS 0.0%)

### Infeasible Aircraft

**777-200LR** — Fails by 428 nm, but result is uncertain.
- Normal cruise at 35,000–37,000 ft; engine-out forced to 10,000 ft (thrust insufficient at all altitudes due to calibrated CD0=0.041)
- Burns 192,897 lb in the engine-out segment at 10,000 ft — roughly twice what it would burn at 25,000+ ft
- At 325,300 lb fuel load, the 777 should have ample range on paper, but the model's drag overprediction consumes it
- **This is the most important uncertain result in Mission 1.** The real 777 likely passes, making the choice between 767 and 777 a cost/efficiency question rather than a feasibility one
- Even if it passes, cost efficiency ($1.15/klb·nm) is twice the 767's

**GV** — Closest to feasibility (-195 nm shortfall).
- Requires 8 aircraft to carry 46,000 lb (max payload 5,750 lb each)
- Excellent aerodynamic efficiency: cruises at 43,000–46,000 ft on 2 engines, drops to 40,000–45,000 ft on 1 engine
- The altitude drop on engine-out is small (~3,000 ft) because the GV is light enough that a single BR710 sustains near-cruise altitude
- Fleet aggregate cost of $240,030 makes it the most expensive option
- Per reviewer guidance: the 8-aircraft fleet is operationally impractical regardless of marginal range feasibility

**A330-200** — Falls 1,309 nm short; result is low-confidence.
- f_oh calibrated to 0.000, meaning ALL fuel is allocated to cruise
- Calibrated CD0=0.033 and e=2.165 (Oswald efficiency >1) are both unphysical
- Engine-out forced to 10,000 ft (thrust insufficient at all altitudes), burning 131,870 lb in the engine-out segment alone
- Even if the A330 marginally passed with a better calibration, it would be oversized and cost-inefficient for this mission

**P-8** — Falls 1,774 nm short.
- Requires 2 aircraft for the 46,000 lb payload (max payload 23,885 lb)
- Calibrated CD0=0.060 is the highest of all aircraft — engine-out at 10,000 ft burns fuel rapidly
- The P-8's strengths (modern airframe, reinforced structure, mission systems) are better suited to shorter-range missions

**DC-8** — Falls 1,863 nm short; expected result.
- Highest f_oh (0.260) removes 84,582 lb of the 122,000 lb fuel load as overhead, leaving only 37,418 lb for cruise
- Engine-out on 3 of 4 engines barely affects altitude (39,500–40,000 ft) — the four-engine configuration provides thrust redundancy that twins cannot match. The DC-8 has a thrust margin of +16,484 lb on three engines at 25,000 ft, while the 767 has only +2,008 lb on one engine. This is exactly the concern raised by scientists in the requirements interviews about twin-engine replacements, and the model captures it correctly despite the DC-8's other calibration issues.
- This mission was selected specifically because it stresses the DC-8's capability; the DC-8 failing reinforces the case for replacement
- Result is **low-confidence** for absolute numbers due to extreme calibration compensation (k_adj=0.605), but the engine-out qualitative behavior is trustworthy

## Methodology

### Two-Segment Cruise Model

1. **Segment 1 (0 → 2,525 nm): Normal cruise**, all engines, no drag penalty. The step-cruise integrator runs at full resolution, then `_find_fuel_at_distance()` interpolates to find the exact fuel burn and aircraft weight at the midpoint.

2. **Segment 2 (2,525 → end of fuel): Engine-out cruise**, n_engines - 1, +10% drag multiplier, altitude optimizer searches from 10,000 ft with non-breaking thrust check. The segment runs until all remaining cruise fuel is exhausted.

**Total mission range** = climb credit (200 nm) + segment 1 cruise + segment 2 cruise + descent credit (120 nm).

**Fuel at destination** (feasible aircraft only): For aircraft whose total range exceeds 5,050 nm, `_find_fuel_at_distance()` is applied to the combined segment data to find cruise fuel burned at exactly 5,050 nm. Remaining cruise fuel = total cruise fuel - fuel burned at destination.

### Fuel Budget (f_oh Hybrid)

Per the confirmed Phase 2 approach (see PHASE2_STEP1_RECONCILIATION.md):
- Total fuel = min(MTOW - OEW - payload, max_fuel)
- Non-cruise overhead = f_oh × W_tow (absorbs taxi, climb, descent, reserves, and calibration residuals)
- Cruise fuel = total fuel - non-cruise overhead

### Fleet Sizing

Aircraft that cannot carry 46,000 lb payload (GV max payload = 5,750 lb, P-8 max payload = 23,885 lb) are modeled as a fleet. Payload is divided evenly across n = ceil(46,000 / max_payload) aircraft. Cost metrics are aggregated.

## Key Modeling Choices and Limitations

### Choices

1. **Climb/descent distance credits.** Uses the Path A convention of 200 nm climb credit + 120 nm descent credit, imported from `calibration.py`. This maintains consistency with the calibrated model.

2. **Fuel cost basis.** Cost is computed on total fuel loaded, since all fuel must be purchased regardless of how it's consumed. Fuel price is $5.50/gal Jet-A.

3. **Reserve interpretation.** In the f_oh model, reserves are embedded in the overhead fraction. For feasible aircraft, both "Fuel@Dest" (cruise fuel remaining at 5,050 nm) and range surplus are reported as complementary safety metrics.

### Limitations

1. **f_oh absorbs calibration residuals**, not just physical non-cruise fuel. This is well-documented (see PHASE2_STEP1_RECONCILIATION.md) and is the reason the DC-8 and A330 results are flagged as low-confidence.

2. **Engine-out drag increment is fixed at +10%** regardless of aircraft type. In reality, the increment depends on nacelle drag, rudder deflection, and other airframe-specific factors.

3. **Mach number is held constant after engine failure.** Standard engine-out procedure involves decelerating 0.02–0.05 Mach below normal cruise to the best-range speed for the degraded configuration. This is a secondary effect compared to the altitude change, but would slightly improve engine-out range for all aircraft. Noted as a known simplification per reviewer feedback.

4. **Calibrated CD0 makes engine-out unreliable for three aircraft.** The P-8 (CD0=0.060), A330 (CD0=0.033), and 777 (CD0=0.041) have calibrated drag coefficients that make single-engine flight impossible at all altitudes in the model. This is unphysical — real twin-engine aircraft must demonstrate engine-out cruise capability for certification. The model's engine-out results for these three aircraft should be treated as lower bounds on actual capability.

5. **No diversion modeling.** The mission tests whether the aircraft can fly the full 5,050 nm. It does not model alternate airports, holding fuel, or regulatory reserves beyond what's captured in f_oh.

## Confidence Assessment

### Mission 1 Confidence

| Aircraft | Confidence | Notes |
|---|---|---|
| 767-200ER | **High** | CD0=0.018 physical, f_oh=0.030, k_adj=0.969, RMS 0.0%. Engine-out altitude realistic (33k–43k ft). |
| GV | **Medium** | f_oh=0.131 somewhat high. Engine-out altitude realistic (40k–45k ft). |
| 777-200LR | **Low** | CD0=0.041 unphysical. Engine-out forced to 10k ft floor. Assessed as LIKELY PASS based on range-payload envelope and ETOPS certification. |
| P-8 | **Low** | CD0=0.060 unphysical. Engine-out forced to 10k ft floor. Also range-limited. |
| A330-200 | **Low** | CD0=0.033, e>1, f_oh=0.000 all unphysical. Engine-out and normal-cruise calibrations both poor. |
| DC-8 | **Low** | k_adj=0.605 (TSFC ~40% low), f_oh=0.260. Engine-out qualitative behavior trustworthy (3/4 engines). |

### Confidence Framework for Missions 2 and 3

Per reviewer guidance, the calibration quality concern is **primarily specific to engine-out** but has secondary effects on all-engines operations:

- **Engine-out (Mission 1 only):** The unphysical CD0 values make thrust-drag balance unresolvable. This is the most severe impact — the model produces physically impossible results (unable to sustain level flight).
- **Climb-descend (Mission 2):** Climb rate and altitude ceiling depend on specific excess power (thrust minus drag). Unphysical CD0 will distort the altitude achieved at the top of each climb cycle, though the effect is moderated by full thrust being available.
- **Low-altitude endurance (Mission 3):** Fuel burn rate at 1,500 ft depends directly on the drag model. Unphysical CD0 produces incorrect absolute fuel burn rates.
- **Normal cruise (all missions):** During cruise with all engines, thrust far exceeds drag (typical T/D ratio 1.5–3×), so the altitude optimizer finds reasonable altitudes. The calibration works as a system (CD0, e, k_adj, f_oh together match published data) even though individual parameters are non-physical.

**Recommendation adopted:** Flag P-8, A330, and 777 as lower confidence across all missions. Flag DC-8 as lower confidence due to TSFC/f_oh compensation. The **high-confidence results across all missions are the 767-200ER and GV** — the two most important aircraft for the study's conclusions.

## Resolved Questions

The following questions were raised in the initial report and resolved through reviewer feedback:

1. **Reserve reporting (Q1):** Fuel-at-destination metric added. The 767 arrives with 25,732 lb cruise fuel at 5,050 nm.
2. **777 altitude floor (Q2):** Floor lowered to 10,000 ft, revealing unphysical calibrated drag. Adopted option (c): engine-out results only reliable for physically-grounded calibrations. Status labels (LIKELY PASS, UNCERTAIN) used for affected aircraft.
3. **A330 flagging (Q3):** "Low-confidence" note is sufficient. A330 not a leading candidate regardless.
4. **GV near-feasibility (Q4):** Not worth quantifying. 8-aircraft fleet is operationally impractical regardless.
5. **Mach reduction:** Noted as known simplification; secondary to altitude change.

## Reproduction

```bash
python3 -m src.analysis.run_missions
```

Runtime: ~8 minutes (dominated by calibration). Prints detailed per-aircraft results and summary table.

## Files Changed (Cumulative)

| File | Change |
|---|---|
| `src/models/performance.py` | (1) Added `drag_multiplier` to `optimal_cruise_altitude()` thrust check; (2) Added `h_min` parameter to `step_cruise_range()` forwarded to altitude optimizer; (3) Changed thrust check from `break` to `continue` to handle non-monotonic thrust-drag regime |
| `src/models/missions.py` | **New file.** `simulate_mission1_engine_out()` with fuel-at-destination calculation, `_find_fuel_at_distance()`, `_determine_infeasibility()`, `_infeasible_result()` |
| `src/analysis/run_missions.py` | Updated from stub to functional Mission 1 driver; displays fuel-at-destination for feasible aircraft |
