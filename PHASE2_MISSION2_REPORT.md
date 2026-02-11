# Phase 2: Mission 2 — Vertical Atmospheric Sampling (Revised)

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

| Aircraft | Status | Confidence | n_ac | Cycles | Init→Peak Ceil (ft) | Cost | $/klb·nm | Notes |
|---|---|---|---|---|---|---|---|---|
| **DC-8** | **PASS** | **Low** | 1 | 21 | 42,000→42,000 | $95,224 | $0.4360 | Flat ceiling — 4 engines provide ample thrust at all weights |
| **767-200ER** | **PASS** | **High** | 1 | 18 | 41,000→43,100 | $132,985 | $0.6089 | Progressive ceiling (+2,100 ft); best single-aircraft option |
| **777-200LR** | **PASS** | **Low** | 1 | 17 | 43,100→43,100 | $267,037 | $1.2227 | Flat ceiling at hard cap — massive thrust overcomes weight |
| GV | PASS | Medium | 9 | 16 | 44,000→47,000 | $269,828† | $1.2355† | Best progressive ceiling (+3,000 ft); fleet impractical |
| A330-200 | PASS (marginal) | Low | 1 | 19 | 41,100→41,100 | $177,001 | $0.8104 | Barely passes (+49 nm); flat ceiling; low-confidence calibration |
| P-8 | PASS | Low | 3 | 14 | 38,000→40,000 | $180,564† | $0.8268† | Progressive ceiling (+2,000 ft); low-confidence due to CD0=0.060 |

†Fleet aggregate (cost and $/klb·nm are for the full fleet of n_ac aircraft)

### Key Takeaways

**All six aircraft pass Mission 2.** This mission is less demanding than Mission 1: shorter distance (4,200 vs. 5,050 nm), no engine-out, and explicit reserves instead of the f_oh hybrid. The A330 is the most marginal at +49 nm surplus.

**Progressive ceiling increase manifests for four aircraft.** After incorporating reviewer feedback on the thrust model (see Changes Since Initial Report), the model now correctly shows weight-dependent ceilings:
- **GV:** 44,000 → 47,000 ft (+3,000 ft over 16 cycles) — highest progression
- **767-200ER:** 41,000 → 43,100 ft (+2,100 ft over 18 cycles) — reaches hard cap by cycle 13
- **P-8:** 38,000 → 40,000 ft (+2,000 ft over 14 cycles)
- **DC-8 and 777-200LR:** Flat ceilings — both have enough thrust to reach the hard cap at all weights. The DC-8's 4 engines and the 777's massive engines provide sufficient excess thrust even at MTOW.
- **A330-200:** Flat at 41,100 ft — the unphysical calibration (CD0=0.033) distorts thrust margins

**The 767-200ER is the best single-aircraft solution.** It combines progressive ceiling increase (41,000→43,100 ft) with moderate cost ($0.61/klb·nm) and high model confidence. The GV reaches higher (47,000 ft) but requires 9 aircraft.

**The DC-8 is the cheapest but its ceiling doesn't increase.** At $0.44/klb·nm the DC-8 has the lowest cost, but its 4-engine configuration has so much excess thrust that the ceiling is flat at 42,000 ft throughout. The DC-8 result is low-confidence due to k_adj=0.605 (TSFC ~40% below reference).

**Scientists' top priority — "flying higher" — favors the GV and 767-200ER.** The GV reaches the highest altitudes (47,000 ft) and shows the most ceiling progression, but requires a 9-aircraft fleet. The 767-200ER is the only single-aircraft solution that offers meaningful progressive ceiling increase with high model confidence.

## Changes Since Initial Report

This is a revised report incorporating reviewer feedback from the first submission. One critical change was made:

### Two-Regime Thrust Lapse Model (Reviewer Critical Feedback)

The initial report showed flat ceilings for all aircraft on every cycle — the reviewer correctly identified this as physically implausible. The root cause was the thrust model: `T = T_SLS × σ^0.75` overpredicted thrust above the tropopause, allowing even MTOW-weight aircraft to reach the published service ceiling.

**Fix:** Implemented a two-regime thrust lapse model (see ASSUMPTIONS_LOG.md entry C3):
- Below tropopause (≤36,089 ft): `T = T_SLS × σ^0.75` (unchanged)
- Above tropopause (>36,089 ft): `T = T_trop × (σ/σ_trop)^2.0` (steeper lapse)

The hard service ceiling cap remains as a structural/pressurization limit. The climb target is set above the hard cap (+5,000 ft) so that `climb_segment()` finds the thrust-limited ceiling via ROC < 100 ft/min. The result is then capped: `cycle_ceiling = min(thrust_ceiling, hard_ceiling)`.

**Impact on calibration:** All calibration RMS errors remain unchanged. Thrust is used only as a go/no-go viability check in the cruise altitude optimizer, and at calibration-relevant altitudes (35,000–39,000 ft, mostly below the tropopause), thrust still far exceeds drag.

**Impact on Mission 1:** Small (~5%) reduction in the 767-200ER's range surplus (1,134 nm vs. 1,202 nm previously) due to slightly lower engine-out cruise altitudes above the tropopause. No status changes.

### Reviewer Answers Incorporated

**Q2 (A330 assessment):** The A330 now passes (marginally, +49 nm) with the two-regime thrust model. Even if it had remained infeasible, the reviewer guidance was to label it "UNCERTAIN" rather than "FAIL" given the 0.4% margin and poor calibration quality.

**Q3 (P-8 assessment):** The P-8 now passes with the two-regime thrust model (14 cycles, 38,000→40,000 ft progressive ceiling). However, this result is low-confidence because the P-8's calibrated CD0=0.060 is unphysical. The real P-8 can unquestionably climb; the model's ceiling predictions should not be taken at face value.

## Detailed Observations

### Progressive Ceiling Progression (Core Scientific Output)

The progressive ceiling table shows the altitude capability at each cycle:

| Cycle | DC-8 | GV | P-8 | 767-200ER | A330 | 777-200LR |
|---|---|---|---|---|---|---|
| 1 | 42,000 | 44,000 | 38,000 | 41,000 | 41,100 | 43,100 |
| 4 | 42,000 | 45,000 | 38,000 | 42,000 | 41,100 | 43,100 |
| 8 | 42,000 | 46,000 | 39,000 | 43,000 | 41,100 | 43,100 |
| 12 | 42,000 | 47,000 | 40,000 | 43,000 | 41,100 | 43,100 |
| 16 | 42,000 | 47,000 | — | 43,100 | 41,100 | 43,100 |

Aircraft fall into three categories:

1. **Progressive ceiling (thrust-limited at heavy weight):** GV, 767-200ER, P-8. These aircraft cannot reach the published ceiling at MTOW. As fuel burns off, the ceiling rises 1,000 ft every few cycles until it converges on the hard cap. This is the physically correct and scientifically valuable behavior.

2. **Flat ceiling at hard cap (thrust-sufficient):** DC-8, 777-200LR. These have enough excess thrust to reach the published ceiling even at MTOW. The DC-8 benefits from 4 engines (total SLS thrust ~88,000 lbf); the 777 benefits from massive engines (2 × 110,100 lbf SLS). Their ceilings are structurally/pressurization-limited, not thrust-limited.

3. **Flat ceiling (calibration artifact):** A330. The calibrated CD0=0.033 (unphysical) distorts the thrust-drag balance. The A330's real ceiling behavior is unknown.

### Individual Aircraft

**DC-8** — PASS, 21 cycles, 42,000 ft flat, $95,224.
- Fuel burned: 60,896 lb of 106,197 lb available. 45,301 lb remaining.
- The DC-8's 4-engine configuration provides redundant thrust for climbing. At 325,000 lb MTOW with 4× CFM56-2-C1 engines, excess thrust at 42,000 ft is still substantial.
- Low-confidence: k_adj=0.605, f_oh=0.260 (not used here, but indicates heavy calibration compensation).

**767-200ER** — PASS, 18 cycles, 41,000→43,100 ft, $132,985. **Best single-aircraft solution.**
- Fuel burned: 112,101 lb of 145,761 lb available. 33,660 lb remaining.
- Ceiling progression: 41,000 ft (cycles 1–3) → 42,000 ft (cycles 4–7) → 43,000 ft (cycles 8–12) → 43,100 ft (cycles 13–18).
- This 2,100 ft progression is physically meaningful — the 767 starts thrust-limited and progressively reaches the hard cap as it lightens. The step pattern reflects the 1,000 ft integration resolution.
- **High-confidence result.** CD0=0.018, k_adj=0.951, RMS 0.0%.

**GV** — PASS (9 aircraft), 16 cycles, 44,000→47,000 ft, $269,828 fleet. **Best altitude capability.**
- Each aircraft: fuel burned 23,959 lb of 32,408 lb available. 8,449 lb remaining.
- Best ceiling progression: 44,000 → 45,000 → 46,000 → 47,000 ft (+3,000 ft over 16 cycles).
- The GV's published ceiling (51,000 ft) is the highest in the study. The two-regime thrust model limits it to 47,000 ft at the lightest cycle weights — plausible for the BR710 engines at these altitudes.
- Fleet of 9 aircraft is operationally impractical, but the altitude performance demonstrates the value of a lighter, higher-ceiling platform.

**P-8** — PASS (3 aircraft), 14 cycles, 38,000→40,000 ft, $180,564 fleet.
- Each aircraft: fuel burned 43,239 lb of 66,077 lb available. 22,838 lb remaining.
- Progressive ceiling: 38,000 ft (cycles 1–5) → 39,000 ft (cycles 6–11) → 40,000 ft (cycles 12–14).
- **Low-confidence.** Calibrated CD0=0.060 is 3–4× physical reality. The P-8's ceiling of 38,000–40,000 ft is artificially low — the real P-8 (published ceiling 41,000 ft) would reach higher. However, the qualitative behavior (progressive increase) is plausible.

**A330-200** — PASS (marginal, +49 nm), 19 cycles, 41,100 ft flat, $177,001.
- Fuel burned: 184,733 lb of 187,358 lb available. Only 2,625 lb remaining.
- This is the most marginal result — essentially on the knife-edge of feasibility.
- Flat ceiling reflects calibration artifact (CD0=0.033, e=2.165).
- **Low-confidence.** The A330 could pass or fail in reality; the model cannot determine this with the current calibration quality.

**777-200LR** — PASS, 17 cycles, 43,100 ft flat, $267,037.
- Fuel burned: 142,963 lb of 295,387 lb available. 152,425 lb remaining — largest margin.
- Flat ceiling: the 777's massive engines (2 × 110,100 lbf SLS) provide ample thrust at all weights.
- Cost of $267,037 ($1.22/klb·nm) is the highest single-aircraft cost — the 777 is oversized for this mission.
- **Low-confidence** (CD0=0.041, did not converge), but the 777 passes so comfortably that the true answer is almost certainly PASS.

## Methodology

### Two-Regime Thrust Lapse Model

The thrust model now uses two regimes (see ASSUMPTIONS_LOG.md entry C3):
- **Below tropopause (≤36,089 ft):** `T = T_SLS × σ^0.75` — standard high-bypass turbofan lapse
- **Above tropopause (>36,089 ft):** `T = T_trop × (σ/σ_trop)^2.0` — steeper lapse reflecting accelerated thrust decay in the isothermal stratosphere

This is implemented in `propulsion.thrust_available_cruise()`. Continuity at the tropopause is guaranteed by construction.

### Sawtooth Cycle Model

Each cycle consists of two phases:

1. **Climb phase (altitude-stepping integration):** Starting at 5,000 ft, the model integrates in 1,000 ft altitude steps toward `hard_ceiling + 5,000 ft`. At each step:
   - Compute drag from the parabolic polar (CD = CD0 + CL²/πARe)
   - Compute available thrust from `thrust_available_cruise()` with two-regime lapse
   - Compute excess thrust → rate of climb: ROC = V × (T_excess / W)
   - Stop if ROC < 100 ft/min (thrust-limited ceiling) or T_excess ≤ 0
   - Apply hard ceiling cap: `cycle_ceiling = min(thrust_ceiling, hard_ceiling)`
   - If climb exceeds hard ceiling, truncate fuel/distance/time using per-step data

2. **Descent phase (bulk calculation):** From `cycle_ceiling` back to 5,000 ft at 2,000 ft/min:
   - Time = Δh / 2,000 ft/min
   - Fuel = 10% of cruise fuel flow at mid-descent altitude × time
   - Distance = TAS at mid-descent altitude × time

### Fuel Budget (Explicit Reserves, No f_oh)

Per the Phase 2 reconciliation decision, Mission 2 does not use the f_oh overhead fraction:

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

1. **Two-regime thrust lapse (exp_strato=2.0).** Per reviewer feedback. The exponent 2.0 was selected to produce physically plausible weight-dependent ceilings. Below the tropopause, the original 0.75 exponent is preserved to maintain calibration consistency.

2. **Hard ceiling cap retained.** Published service ceilings reflect structural/pressurization limits beyond thrust. The hard cap prevents the model from producing altitudes above the published ceiling even at light weights.

3. **Climb target = hard_ceiling + 5,000 ft.** The climb segment targets above the hard cap so the ROC criterion determines the thrust-limited ceiling. Results are truncated at the hard cap afterward.

4. **Cycle bottom altitude = 5,000 ft.** Per reviewer guidance.

5. **Constant Mach climb at 95% cruise Mach.** A simplification consistent with the rest of the model.

6. **Idle descent fuel = 10% of cruise fuel flow.** Scaled to aircraft size.

### Limitations

1. **Stratospheric thrust exponent is approximate.** The value 2.0 produces physically plausible results but is not derived from engine-specific data. Different engine types would have different stratospheric thrust lapse characteristics.

2. **1,000 ft step size discretizes the ceiling.** The progressive ceiling appears as 1,000 ft jumps (e.g., 41,000 → 42,000 → 43,000) rather than continuous. Finer step sizes would smooth the progression but increase computation time. The scientific interpretation is the same.

3. **Calibrated CD0 still distorts P-8 and A330 ceilings.** The P-8 (CD0=0.060) starts at 38,000 ft — lower than the published 41,000 ft ceiling. The A330 (CD0=0.033) shows no progression despite having physical characteristics similar to the 767. These are calibration artifacts, not physical results.

4. **No wind effects.** The 4,200 nm distance assumes still air.

5. **A330 margin is within model uncertainty.** The A330 passes by only 49 nm (1.2% of mission distance) with a calibration that has e=2.165 and f_oh=0.000, both unphysical. This result should be treated as UNCERTAIN.

## Confidence Assessment

| Aircraft | Confidence | Notes |
|---|---|---|
| 767-200ER | **High** | CD0=0.018 physical, k_adj=0.951, RMS 0.0%. Ceiling progression (41k→43.1k ft) is reliable. |
| GV | **Medium** | CD0=0.015 physical. Ceiling progression (44k→47k ft) plausible. Fleet impractical. |
| DC-8 | **Low** | k_adj=0.605 (TSFC ~40% low). Flat ceiling (42k ft) physically correct for 4-engine config. |
| 777-200LR | **Low** | CD0=0.041 unphysical. Flat ceiling correct (massive engines). Passes comfortably. |
| P-8 | **Low** | CD0=0.060 unphysical. Progression (38k→40k ft) direction correct but absolute values too low. |
| A330-200 | **Low** | CD0=0.033, e=2.165 unphysical. Marginal pass (+49 nm) within model error — true answer uncertain. |

## Comparison with Mission 1

| Aircraft | Mission 1 | Mission 2 | Cost Change | Notes |
|---|---|---|---|---|
| DC-8 | FAIL (-1,863 nm) | PASS | — | Shorter distance, no engine-out, explicit reserves vs f_oh |
| 767-200ER | PASS (+1,134 nm) | PASS | $133k → $133k | Comparable cost; ceiling progression is the new information |
| 777-200LR | LIKELY PASS | PASS | $267k → $267k | Passes comfortably; high cost persists |
| GV | FAIL (-373 nm) | PASS (9 ac) | $240k → $270k† | Higher fleet count (8→9) due to heavier payload (52k vs 46k lb) |
| A330-200 | UNCERTAIN | PASS (marginal) | — | Both missions marginal; low-confidence calibration |
| P-8 | FAIL | PASS (3 ac) | $120k → $181k† | Now climbs with two-regime thrust model; still low-confidence |

†Fleet aggregate costs

**Key pattern:** The DC-8 flips from FAIL (Mission 1) to PASS (Mission 2). This is primarily because Mission 2 is 850 nm shorter, has no engine-out degradation, and uses explicit reserves instead of the f_oh hybrid (the DC-8's f_oh=0.260 removes 26% of fuel as overhead in Mission 1, while explicit reserves remove far less). However, the DC-8's pass is low-confidence.

## Reproduction

```bash
python3 -m src.analysis.run_missions
```

Runtime: ~15 minutes (dominated by calibration). Prints detailed per-aircraft results, summary table, and progressive ceiling table for both Mission 1 and Mission 2.

## Files Changed (Cumulative)

| File | Change |
|---|---|
| `src/models/propulsion.py` | Two-regime thrust lapse model: `σ^0.75` below tropopause, `σ^2.0` above |
| `src/models/missions.py` | `climb_segment()`, `descend_segment()`, `simulate_mission2_sampling()` with ceiling cap logic and zero-progress guard |
| `src/analysis/run_missions.py` | `run_mission2()` and output functions; `__main__` runs both missions |
| `tests/test_missions.py` | 34 tests: climb_segment (11), descend_segment (8), Mission 2 orchestrator (15 incl. progressive ceiling + ceiling cap) |
| `tests/test_performance.py` | 3 new tests: thrust continuity, steeper above tropopause, unchanged below |
| `ASSUMPTIONS_LOG.md` | Added C3: Two-Regime Thrust Lapse Model |
