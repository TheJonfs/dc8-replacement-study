# DC-8 Replacement Study — Handoff Status

## What This File Is

This document prepares a new Claude thread to continue the DC-8 Replacement Aircraft Performance Study. All three science missions are complete and reviewed. The next step is an integrated final synthesis: comparative plots, cross-mission analysis, and a final report.

Read CLAUDE.md for the full problem statement. Read ASSUMPTIONS_LOG.md for all modeling assumptions.

---

## Project State: All Missions Complete, Ready for Final Synthesis

### Phase Summary
- **Phases 0–1 (complete):** Core performance model, calibration system, range-payload diagrams.
- **Phase 2 Step 1 (complete):** Path A/B reconciliation — determined per-mission fuel budgeting approach.
- **Phase 2 Mission 1 (complete):** Engine-out transport (SCEL→KPMD, 5,050 nmi, 46,000 lb). Report reviewed.
- **Phase 2 Mission 2 (complete):** Vertical atmospheric sampling (NZCH→SCCI, 4,200 nmi, 52,000 lb). Report reviewed.
- **Phase 2 Mission 3 (complete):** Low-altitude smoke survey (Central US, 8 hr, 30,000 lb). Report reviewed.
- **Final synthesis (next):** Integrated analysis, comparative plots, final report.

### Key Documents
| Document | Purpose |
|---|---|
| `CLAUDE.md` | Authoritative problem statement and deliverables specification |
| `ASSUMPTIONS_LOG.md` | All modeling assumptions (Sections A–H) with rationale and impact |
| `PHASE2_MISSION1_REPORT.md` | Mission 1 results: 767 sole confirmed PASS |
| `PHASE2_MISSION2_REPORT.md` | Mission 2 results: all PASS, progressive ceiling analysis |
| `PHASE2_MISSION3_REPORT.md` | Mission 3 results: all PASS, mission-sized fuel loading |
| `PHASE2_STEP1_RECONCILIATION.md` | Fuel budgeting methodology (f_oh vs. explicit reserves) |

### Test Status
120 tests, all passing. Run with: `python3 -m pytest tests/ -v`

| Test file | Count | Coverage |
|---|---|---|
| `test_missions.py` | 43 | All three missions, fleet sizing, fuel sizing convergence |
| `test_performance.py` | 36 | Breguet, cruise conditions, reserves, calibration quality |
| `test_aircraft_data.py` | 23 | Data loading, unit consistency, required keys |
| `test_atmosphere.py` | 18 | ISA model validation |

Note: Calibration quality tests in `test_performance.py` take ~12 minutes (differential evolution optimizer).

---

## Cross-Mission Results Summary

This is the single most important table in the study.

### Mission 1: Engine-Out Transport (SCEL→KPMD, 5,050 nmi, 46,000 lb)

| Aircraft | Status | Confidence | n_ac | Cost | $/klb·nm |
|---|---|---|---|---|---|
| **767-200ER** | **PASS** | **High** | 1 | $132,985 | $0.57 |
| 777-200LR | LIKELY PASS | Low | 1 | $267,037 | $1.15 |
| GV | FAIL (-195 nm) | Medium | 8 | $240,030† | $1.03† |
| A330-200 | UNCERTAIN | Low | 1 | $181,926 | $0.78 |
| P-8 | FAIL | Low | 2 | $120,376† | $0.52† |
| DC-8 | FAIL (-1,863 nm) | Low | 1 | $100,149 | $0.43 |

Fuel budget: f_oh hybrid (non_cruise_fuel = f_oh × W_tow). Engine-out at midpoint (2,525 nm) with +10% drag and n-1 engines.

### Mission 2: Vertical Sampling (NZCH→SCCI, 4,200 nmi, 52,000 lb)

| Aircraft | Status | Confidence | n_ac | Cycles | Ceiling Range (ft) | Cost | $/klb·nm |
|---|---|---|---|---|---|---|---|
| DC-8 | PASS | Low | 1 | 21 | 42,000→42,000 | $95,224 | $0.44 |
| **767-200ER** | **PASS** | **High** | 1 | 18 | 41,000→43,100 | $132,985 | $0.61 |
| 777-200LR | PASS | Low | 1 | 17 | 43,100→43,100 | $267,037 | $1.22 |
| GV | PASS | Medium | 9 | 16 | 44,000→47,000 | $269,828† | $1.24† |
| A330-200 | PASS (marginal) | Low | 1 | 19 | 41,100→41,100 | $177,001 | $0.81 |
| P-8 | PASS | Low | 3 | 14 | 38,000→40,000 | $180,564† | $0.83† |

Fuel budget: explicit reserves only (no f_oh). Sawtooth climb-descend cycles from 5,000 ft to thrust-limited ceiling.

### Mission 3: Low-Altitude Smoke Survey (8 hr, 30,000 lb, 1,500 ft)

| Aircraft | Status | Confidence | n_ac | Fuel Loaded (lb) | Fuel Burned (lb) | Cost | $/klb·nm |
|---|---|---|---|---|---|---|---|
| DC-8 | PASS | Low | 1 | 44,496 | 36,233 | $36,527 | $0.61 |
| **767-200ER** | **PASS** | **High** | 1 | 96,124 | 78,921 | $78,907 | $1.32 |
| P-8 | PASS | Low | 2 | 37,321 ea | 30,244 ea | $61,273† | $1.02† |
| GV | PASS | Medium | 6 | 23,393 ea | 18,938 ea | $115,218† | $1.92† |
| A330-200 | PASS | Low | 1 | 166,342 | 133,649 | $136,549 | $2.28 |
| 777-200LR | PASS | Low | 1 | 128,747 | 102,996 | $105,688 | $1.76 |

Fuel budget: explicit reserves only (no f_oh). Mission-sized fuel loading (iterative sizing for 8 hr + reserves).

†Fleet aggregate cost

### Overall Assessment

| Aircraft | M1 | M2 | M3 | Confidence | Summary |
|---|---|---|---|---|---|
| **767-200ER** | **PASS** | **PASS** | **PASS** | **High** | Only aircraft that passes all 3 with trustworthy numbers |
| P-8 | FAIL | PASS (3 ac) | PASS (2 ac) | Low | Cheapest fleet aggregate on M3; fails M1 |
| 777-200LR | LIKELY PASS | PASS | PASS | Low | Passes but always expensive |
| GV | FAIL | PASS (9 ac) | PASS (6 ac) | Medium | Best altitude capability; fleet impractical |
| A330-200 | UNCERTAIN | PASS (marginal) | PASS | Low | Calibration too poor to trust |
| DC-8 | FAIL | PASS | PASS | Low | k_adj=0.605 makes burn rates ~40% too low |

**The 767-200ER is the clear overall winner. The P-8 is the strongest fleet competitor.** This aligns with the success criteria in CLAUDE.md, which states the study should identify the 767 and P-8 as top contenders.

---

## Calibration Quality Summary

Each aircraft was calibrated against published range-payload data by optimizing 4 parameters: CD0 (zero-lift drag), e (Oswald efficiency), k_adj (TSFC multiplier), f_oh (fuel overhead fraction).

| Aircraft | CD0 | e | k_adj | f_oh | RMS | Confidence | Key Issue |
|---|---|---|---|---|---|---|---|
| **767-200ER** | 0.0177 | 0.698 | 0.951 | 0.030 | 0.0% | **High** | All parameters physical |
| GV | 0.0150 | 0.764 | 0.801 | 0.131 | 1.2% | Medium | k_adj slightly low |
| DC-8 | 0.0141 | 0.968 | 0.605 | 0.260 | 0.5% | Low | k_adj=0.605 → burn rate 40% too low; CD0 too low for 4-engine |
| 737-900ER | 0.0355 | 1.223 | 0.757 | 0.062 | 0.7% | — | P-8 baseline only |
| P-8 | 0.0597 | 0.975 | 0.339 | 0.180 | 0.0% | Low | CD0 2–3× physical; engine-out impossible |
| A330-200 | 0.0334 | 2.165 | 1.021 | 0.000 | 3.0% | Low | e=2.165 unphysical; f_oh=0.000 |
| 777-200LR | 0.0410 | 1.811 | 0.556 | 0.080 | 6.5% | Low | CD0 unphysical; highest RMS |

**Implication for final report:** Only the 767 results should be cited as reliable absolute numbers. All other aircraft results are useful for relative comparison and qualitative feasibility assessment, but not for precise fuel burn predictions.

---

## What Remains: CLAUDE.md Deliverables Checklist

### ✅ Deliverable 1: Range-Payload Diagrams
**Status: Complete.** Individual plots for all 7 aircraft (6 study + 737-900ER baseline) plus an overlay plot comparing all six.
- Files: `outputs/plots/rp_*.png`
- Generator: `python3 -m src.analysis.run_plots`

### ✅ Deliverable 2: Mission Performance Analysis
**Status: Complete (data computed, not yet in final report format).**
All three missions simulated for all six aircraft. Feasibility, fuel consumption, reserves, fleet sizing, and aggregate fuel consumption computed and reported in per-mission reports.

### ⬜ Deliverable 3: Weight Breakdown Comparison
**Status: Not yet produced.**
CLAUDE.md requires: "For each mission, produce a stacked comparison showing each aircraft's OEW, payload, mission fuel, and reserve fuel. Show both individual aircraft values and aggregate values for the G-V and P-8 (where n > 1)."
- The data exists in the mission result dicts (each `per_aircraft` dict contains `oew_lb`, `payload_lb`, `total_fuel_lb`, `reserve_fuel_lb`, `fuel_burned_lb`).
- Need to produce stacked bar charts (3 plots, one per mission).
- For Mission 1: the fuel breakdown is `non_cruise_fuel` + `cruise_fuel` (f_oh model).
- For Missions 2-3: the fuel breakdown is `mission_fuel` + `reserve_fuel`.

### ⬜ Deliverable 4: Fuel Cost Metrics
**Status: Computed in mission reports, not yet in consolidated comparison format.**
Per-mission tables exist in the individual reports. Need a consolidated cross-mission comparison table and possibly a bar chart.

### ⬜ Deliverable 5: Speed and Altitude Profiles
**Status: Not yet produced.**
CLAUDE.md requires: "For Mission 1 (engine-out) and Mission 2 (sampling), produce plots of aircraft speed (Mach) vs. distance and altitude vs. distance."
- Mission 1 data: each result dict has `per_aircraft.segment1.segments` and `per_aircraft.segment2.segments`, each with per-step `cumulative_range_nm`, Mach, and altitude data.
- Mission 2 data: each result dict has `per_aircraft.cycles` and `per_aircraft.profile_points` (list of `(distance_nm, altitude_ft)` tuples for the sawtooth pattern).
- Mission 1 Mach is constant (cruise Mach) but altitude changes at engine-out. The key thing to show is how 2-engine aircraft drop to a lower altitude after losing an engine (but our model keeps constant Mach and lets altitude adjust).
- Mission 2 shows the sawtooth altitude pattern with progressive ceiling increase.

### ⬜ Final Synthesis Report
**Status: Not yet written.**
The reviewer recommended this should pull together:
1. The cross-mission comparison table (already drafted in Mission 3 report)
2. Calibration quality summary and its impact on which results to trust
3. The qualitative factors from the scientist interviews (CLAUDE.md) that the quantitative model doesn't capture: fuselage configuration, payload flexibility, engine redundancy, altitude capability, cargo door size, T-tail concerns
4. An honest assessment of what the model can and cannot tell us

---

## Repository Map

```
CLAUDE.md                        # Problem statement (read this first)
ASSUMPTIONS_LOG.md               # All modeling assumptions (Sections A-H)
STATUS.md                        # This file — handoff status

PHASE2_MISSION1_REPORT.md        # Mission 1 results and methodology
PHASE2_MISSION2_REPORT.md        # Mission 2 results and methodology
PHASE2_MISSION3_REPORT.md        # Mission 3 results and methodology
PHASE2_STEP1_RECONCILIATION.md   # Path A/B fuel budgeting reconciliation
PHASE2_MISSION2_PLAN.md          # Mission 2 implementation plan (historical)

STUDY_PLAN.md                    # Original phasing plan (historical)
PROGRESS_REPORT.md               # Phase 0+1 progress report (historical)
PHASE1_REVIEW.md                 # Phase 1 review document (historical)
PHASE1_REVIEW_RESPONSE.md        # Response to Phase 1 review (historical)

src/
    utils.py                     # Unit conversions, fuel_cost() [$5.50/gal]
    aircraft_data/
        loader.py                # Unified data loader → standardized dicts
        dc8_72.py                # NASA DC-8-72 (N817NA modified)
        gulfstream_gv.py         # Gulfstream G-V
        boeing_737_900er.py      # 737-900ER (P-8 baseline, not a study candidate)
        boeing_p8.py             # P-8 Poseidon (derived from 737-900ER)
        boeing_767_200er.py      # Boeing 767-200ER
        a330_200.py              # Airbus A330-200
        boeing_777_200lr.py      # Boeing 777-200LR
    models/
        atmosphere.py            # ISA model (sea level to 65,000 ft)
        aerodynamics.py          # Parabolic drag polar, engine-out drag factor
        propulsion.py            # TSFC model, thrust lapse, two-regime thrust model
        performance.py           # Breguet range, step-cruise, climb/descent/reserves
        calibration.py           # 4-parameter fitting against range-payload data
        missions.py              # All three mission simulations
    analysis/
        run_calibration.py       # Calibrate all aircraft, save JSON, print reports
        run_plots.py             # Generate all range-payload plots
        run_missions.py          # Run all three missions, print formatted results
        reconcile_paths.py       # Path A/B comparison tool (historical)
    plotting/
        range_payload.py         # Range-payload diagram generation

tests/
    test_atmosphere.py           # 18 tests — ISA model
    test_aircraft_data.py        # 23 tests — data loading, consistency
    test_performance.py          # 36 tests — performance model + calibration quality
    test_missions.py             # 43 tests — all three missions

outputs/
    plots/                       # Range-payload diagrams (7 individual + 1 overlay)
    calibration_results.json     # Cached calibration parameters
```

---

## How the Performance Model Works

### Loading Aircraft Data
```python
from src.aircraft_data.loader import load_all_aircraft
all_ac = load_all_aircraft()  # dict keyed by designation
ac = all_ac["767-200ER"]      # standardized dict
```

Key fields: `OEW`, `MTOW`, `MZFW`, `max_payload`, `max_fuel`, `wing_area_ft2`, `aspect_ratio`, `cruise_mach`, `tsfc_cruise_ref`, `thrust_per_engine_slst_lbf`, `n_engines`, `service_ceiling_ft`, `range_payload_points`.

### Calibration
```python
from src.models.calibration import calibrate_aircraft
cal = calibrate_aircraft(ac)
# Returns: CD0, e, k_adj, f_oh, rms_error, L_D_max, point_errors, ...
```

### Running All Missions
```python
from src.analysis.run_calibration import run_all_calibrations
from src.models.missions import (
    simulate_mission1_engine_out,
    simulate_mission2_sampling,
    simulate_mission3_low_altitude,
)

all_ac, calibrations = run_all_calibrations()  # ~12 min
for designation in STUDY_ORDER:
    ac = all_ac[designation]
    cal = calibrations[designation]
    m1 = simulate_mission1_engine_out(ac, cal)
    m2 = simulate_mission2_sampling(ac, cal)
    m3 = simulate_mission3_low_altitude(ac, cal)
```

Or use the analysis driver: `python3 -m src.analysis.run_missions`

### Mission Result Dict Structure

All three mission functions return:
```python
{
    "feasible": bool,
    "infeasible_reason": str or None,
    "aircraft_name": str,
    "designation": str,
    "payload_requested_lb": float,
    "payload_actual_lb": float,
    "n_aircraft": int,
    "per_aircraft": { ... },   # detailed per-aircraft results
    "aggregate": { ... },       # fleet aggregate (or None if n=1)
}
```

**Mission 1 per_aircraft** has: `segment1`, `segment2` (each with `.segments` list for plotting), `total_range_nm`, `total_fuel_burned_lb`, `reserve_fuel_lb`, `fuel_at_destination_lb`, `fuel_cost_usd`, `fuel_cost_per_1000lb_nm`.

**Mission 2 per_aircraft** has: `cycles` (list of per-cycle dicts with ceiling, fuel, distance), `profile_points` (list of `(distance_nm, altitude_ft)` for sawtooth plot), `peak_ceiling_ft`, `initial_ceiling_ft`, `final_ceiling_ft`, `fuel_cost_usd`, `fuel_cost_per_1000lb_nm`.

**Mission 3 per_aircraft** has: `steps` (list of per-step dicts), `endurance_hr`, `distance_covered_nm`, `avg_fuel_flow_lbhr`, `max_fuel_available_lb`, `fuel_sizing_converged`, `fuel_cost_usd`, `fuel_cost_per_1000lb_nm`.

---

## Key Architecture Details

### Fuel Budgeting Varies by Mission
| Mission | Approach | Function |
|---|---|---|
| Mission 1 | f_oh hybrid: `non_cruise = f_oh × W_tow` | Built into `simulate_mission1_engine_out()` |
| Mission 2 | Explicit reserves only (no f_oh) | Uses `compute_reserve_fuel()` directly |
| Mission 3 | Explicit reserves + iterative fuel sizing | Uses `compute_reserve_fuel()` + convergence loop |

See `PHASE2_STEP1_RECONCILIATION.md` for the rationale.

### Two-Regime Thrust Model
Implemented in `propulsion.thrust_available_cruise()`. Below 36,089 ft uses a steeper lapse than above. This was needed for Mission 2 to produce physically correct progressive ceiling increase (lighter aircraft reaching higher as fuel burns off).

### Mission-Sized Fuel Loading (Mission 3 Only)
Mission 3 is time-constrained, not range-constrained. Aircraft load only enough fuel for 8 hours + reserves, computed iteratively (fuel weight affects drag affects burn rate). See `ASSUMPTIONS_LOG.md` entry F3. Convergence: 50 lb tolerance, 5% operational margin, max 20 iterations.

### The Six Study Candidates (Not Seven)
The 737-900ER appears in range-payload diagrams as context for the P-8 derivation but is NOT a study candidate. The six candidates are: DC-8, GV, P-8, 767-200ER, A330-200, 777-200LR.

Study order in code:
```python
STUDY_ORDER = ["DC-8", "GV", "P-8", "767-200ER", "A330-200", "777-200LR"]
```

---

## Guidance from Reviewer for Final Synthesis

The expert reviewer (a separate Claude thread providing independent feedback) made these recommendations for the final report:

1. **The cross-mission comparison table is the most important output.** Build the final report around it.

2. **The 767+P-8 conclusion must be well-supported.** CLAUDE.md's success criteria state these should emerge as top contenders. The data supports this: the 767 is the only single-aircraft that passes all missions with high confidence; the P-8 fleet is cost-competitive on Missions 2–3.

3. **Include qualitative factors from scientist interviews** that the quantitative model can't capture:
   - Fuselage: DC-8's long narrow body preferred; wide-bodies have wasted central space
   - Altitude: flying higher is the #1 desired improvement; GV reaches 47,000 ft
   - Engine redundancy: 4 engines vs. 2 engines debate
   - Payload config: floor space and emergency exit access more constraining than weight
   - Equipment: wing hard points, large cargo doors, no T-tail (solar flux measurement)
   - Structural: over-designed fuselage amenable to cutouts desired

4. **Be honest about model limitations.** Only the 767 has trustworthy absolute numbers. Other aircraft are useful for relative comparison and qualitative feasibility.

5. **The progressive ceiling table (Mission 2) and iterative fuel sizing (Mission 3) are genuine contributions** beyond straightforward analysis — highlight them.

---

## What the Next Thread Needs to Do

### 1. Produce Remaining Plots (Deliverables 3 and 5)

**Weight breakdown stacked bars (Deliverable 3):** Three plots (one per mission). Each plot shows 6 aircraft side by side with stacked bars: OEW, payload, mission fuel, reserve fuel. GV and P-8 get additional bars showing fleet aggregate. Use matplotlib.

**Speed/altitude profiles (Deliverable 5):** Two sets of plots.
- Mission 1: Altitude vs. distance showing engine-out altitude drop. Mach vs. distance (likely constant but shows the operating point).
- Mission 2: Altitude vs. distance showing sawtooth pattern with progressive ceiling. One line per aircraft on an overlay plot.

### 2. Consolidate Fuel Cost Metrics (Deliverable 4)

A single cross-mission comparison table with $/klb·nm for all aircraft across all three missions. The data exists in the per-mission reports; pull it into one place.

### 3. Write Final Synthesis Report

Pull together:
- Cross-mission comparison (quantitative)
- Calibration quality impact assessment
- Qualitative factors from scientist interviews
- Model limitations and confidence assessment
- Recommendation: 767-200ER as primary candidate, P-8 as fleet alternative

### 4. Workflow

The human collaborator follows a review cycle: implement → push → reviewer feedback → incorporate → next step. For the final synthesis, the deliverable is likely a single comprehensive report (`FINAL_REPORT.md` or similar) plus the supporting plots.

---

## Process Notes

- The human collaborator is a space scientist, not an aircraft engineer.
- An independent Claude review thread provides feedback after each major step.
- Use `python3` (not `python`) — the system doesn't have `python` on PATH.
- SciPy, NumPy, and Matplotlib are installed.
- All outputs should be reproducible from analysis scripts. No ad-hoc computation.
- Calibration runs take ~12 minutes (differential evolution). The `run_all_calibrations()` function caches results across scripts in a single session.
