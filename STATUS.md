# DC-8 Replacement Study — Handoff Status

## What This File Is

This document prepares a new Claude thread to continue the DC-8 Replacement Aircraft Performance Study. Read CLAUDE.md for the full problem statement. Read ASSUMPTIONS_LOG.md for all modeling assumptions. This file focuses on what was built, how it works, what to watch out for, and what to do next.

---

## Project State: Mission 1 Complete, Ready for Mission 2

### Phase Summary
- **Phases 0–1 (complete):** Core performance model, calibration system, range-payload diagrams.
- **Phase 2 Step 1 (complete):** Path A/B reconciliation — determined per-mission fuel budgeting approach.
- **Phase 2 Mission 1 (complete):** Engine-out transport analysis (SCEL→KPMD). 767-200ER is the sole confirmed PASS.
- **Phase 2 Mission 2 (next):** Vertical atmospheric sampling (NZCH→SCCI). Plan reviewed and ready for implementation.

### Key Documents for the Next Thread
- **`CLAUDE.md`** — Full problem statement (authoritative requirements)
- **`PHASE2_MISSION2_PLAN.md`** — Implementation plan for Mission 2 (reviewed, ready to execute)
- **`PHASE2_MISSION1_REPORT.md`** — Mission 1 results and methodology
- **`PHASE2_STEP1_RECONCILIATION.md`** — Fuel budgeting approach (f_oh for Mission 1, explicit reserves for Missions 2/3)
- **`ASSUMPTIONS_LOG.md`** — All modeling assumptions

### Test Status
74 tests, all passing. Run with: `python3 -m pytest tests/ -v`
Note: calibration quality tests take ~12 minutes (differential evolution).

---

## Repository Map

```
CLAUDE.md                        # Problem statement (read this first)
ASSUMPTIONS_LOG.md               # All modeling assumptions with rationale and impact
PHASE2_MISSION2_PLAN.md          # ★ IMPLEMENTATION PLAN for Mission 2 (read before coding)
PHASE2_MISSION1_REPORT.md        # Mission 1 results, methodology, confidence assessment
PHASE2_STEP1_RECONCILIATION.md   # Path A/B reconciliation and per-mission fuel budgeting
STUDY_PLAN.md                    # Original phasing (outdated for phases 0-1; use CLAUDE.md)
PROGRESS_REPORT.md               # Phase 0+1 progress report
PHASE1_REVIEW.md                 # Phase 1 review document
PHASE1_REVIEW_RESPONSE.md        # Response to Phase 1 review

src/
    utils.py                 # Unit conversions, fuel_cost()
    aircraft_data/
        loader.py            # Unified data loader → standardized dicts
        dc8_72.py, gulfstream_gv.py, boeing_737_900er.py, boeing_p8.py,
        boeing_767_200er.py, a330_200.py, boeing_777_200lr.py
    models/
        atmosphere.py        # ISA model (sea level to 65,000 ft)
        aerodynamics.py      # Parabolic drag polar, L/D, engine-out drag
        propulsion.py        # TSFC model, thrust lapse, thrust_available_cruise()
        performance.py       # Breguet range, step-cruise, climb/descent/reserves (~700 lines)
        calibration.py       # Parameter fitting + calibration range (Path A)
        missions.py          # ★ Mission simulation (Mission 1 complete, Mission 2/3 stubs)
    analysis/
        __init__.py
        run_calibration.py   # Calibrate all aircraft, save JSON
        run_plots.py         # Generate all range-payload plots
        run_missions.py      # ★ Mission analysis driver (Mission 1 complete)
        reconcile_paths.py   # Path A/B comparison tool
    plotting/
        range_payload.py     # Range-payload diagram generation

tests/
    test_atmosphere.py       # 18 tests
    test_aircraft_data.py    # 23 tests
    test_performance.py      # 33 tests (includes slow calibration quality tests)

outputs/
    plots/                   # Range-payload diagrams
    calibration_results.json # Cached calibration parameters
```

---

## How the Performance Model Works

### Loading Aircraft Data
```python
from src.aircraft_data.loader import load_all_aircraft
all_ac = load_all_aircraft()  # dict keyed by designation
ac = all_ac["767-200ER"]      # standardized dict with keys: OEW, MTOW, max_fuel, etc.
```

The loader normalizes 7 different file formats into a standard dict. Key fields:
- `OEW`, `MTOW`, `MZFW`, `max_payload`, `max_fuel` — weights in lb
- `range_payload_points` — list of `(payload_lb, fuel_lb, range_nmi)` tuples
- `wing_area_ft2`, `aspect_ratio`, `cruise_mach`, `tsfc_cruise_ref`, etc.

### Calibration (What Was Done in Phase 1)
```python
from src.models.calibration import calibrate_aircraft, calibrate_p8_from_737
cal = calibrate_aircraft(all_ac["DC-8"])
# Returns dict: CD0, e, k_adj, f_oh, rms_error, L_D_max, point_errors, ...
```

Each aircraft has 4 calibrated parameters:
- **CD0** — zero-lift drag coefficient
- **e** — Oswald span efficiency
- **k_adj** — TSFC multiplier (scales the reference cruise TSFC)
- **f_oh** — non-cruise fuel overhead fraction (`overhead = f_oh × W_tow`)

### Current Calibration Results

| Aircraft | CD0 | e | k_adj | f_oh | L/D_max | RMS | Fuel Burn Check |
|---|---|---|---|---|---|---|---|
| DC-8 | 0.0141 | 0.968 | 0.605 | 0.260 | 20.4 | 0.5% | ✗ low by 50% |
| G-V | 0.0150 | 0.745 | 0.801 | 0.131 | 17.3 | 1.2% | ✓ |
| 737-900ER | 0.0355 | 1.223 | 0.757 | 0.062 | 16.7 | 0.7% | ✓ |
| **767-200ER** | **0.0177** | **0.732** | **0.951** | **0.030** | **16.1** | **0.0%** | **✓** |
| A330-200 | 0.0334 | 2.165 | 1.021 | 0.000 | 22.6 | 3.0% | ✗ high by 40% |
| 777-200LR | 0.0410 | 1.811 | 0.556 | 0.080 | 18.3 | 6.5% | ✓ |
| P-8 | 0.0597 | 0.975 | 0.339 | 0.180 | 11.5 | 0.0% | ⚠ low by 25% |

"Fuel Burn Check" compares computed cruise fuel burn (lb/hr) at FL350/mid-weight against published operator data.

### Confidence Tiers for Mission Analysis (Updated from Mission 1 findings)

1. **High confidence:** 767-200ER (CD0=0.018 physical, k_adj=0.969, RMS 0.0%), GV (CD0=0.015, physical)
2. **Lower confidence:** 777-200LR (CD0=0.041 unphysical, but range-payload matches), P-8 (CD0=0.060, derived model)
3. **Low confidence:** DC-8 (k_adj=0.605, f_oh=0.26 — strong compensation), A330-200 (e=2.165, f_oh=0.000 — unphysical)

**Key finding from Mission 1:** Aircraft with high calibrated CD0 (P-8, A330, 777) have drag that exceeds single-engine thrust at all altitudes — an unphysical artifact. This is most severe for engine-out (Mission 1 only) but also affects climb ceiling (Mission 2) and low-altitude fuel burn (Mission 3) to a lesser degree. See PHASE2_MISSION1_REPORT.md "Confidence Framework for Missions 2 and 3" for details.

---

## Critical Architecture Detail: Two Range Computation Paths

This is the most important thing to understand before Phase 2.

### Path A: Calibration Range (used in Phase 1)
**Module:** `calibration.compute_calibration_range()`
**How it works:**
```
cruise_fuel = total_fuel - f_oh × W_tow
range = step_cruise_breguet(cruise_fuel) + 200 nm (climb) + 120 nm (descent)
```
**Status:** Validated — this is what was calibrated against published data.

### Path B: Mission Range (intended for Phase 2)
**Module:** `performance.compute_range_for_payload()`
**How it works:**
```
climb_fuel = energy_method_estimate(W, h_cruise)
descent_credit = glide_distance(h_cruise)
reserve_fuel = 5% contingency + 200nm alternate + 30min hold
cruise_fuel = total_fuel - climb_fuel - reserve_fuel
range = step_cruise_breguet(cruise_fuel) + climb_distance + descent_credit
```
**Status:** Code exists but has NEVER been validated against published data or compared to Path A.

### The Risk
The calibrated parameters (CD0, e, k_adj) were fitted using Path A. If Path B gives different ranges at the same conditions, then using the Path A parameters with Path B code will produce wrong results.

### Recommended First Step for Phase 2
Before running any missions, run Path B at each aircraft's calibration conditions and compare to published ranges. If they agree within ~5%, proceed. If they diverge, either:
- (a) Recalibrate using Path B as the objective function, or
- (b) Adjust Path B's sub-models (climb fuel, reserves) to be consistent with Path A's overhead

The reviewer agreed this is the right approach.

---

## The Six Study Candidates (Not Seven)

The 737-900ER is a modeling intermediate used to derive the P-8. It should appear in range-payload diagrams for context but should NOT appear in Phase 2 mission analysis. The six study candidates are:

1. **DC-8-72** — baseline
2. **Gulfstream G-V**
3. **Boeing P-8 Poseidon**
4. **Boeing 767-200ER**
5. **Airbus A330-200**
6. **Boeing 777-200LR**

---

## What the Next Thread Needs to Do

### Immediate Task: Implement Mission 2

Read **`PHASE2_MISSION2_PLAN.md`** for the full implementation plan. Summary:

- **Mission:** Vertical atmospheric sampling, NZCH→SCCI, 4,200 nmi, 52,000 lb payload
- **Profile:** Sawtooth climb-descend cycles. Climb to ceiling, descend to 5,000 ft, repeat.
- **Key feature:** Progressive altitude increase as fuel burns off (lighter → higher ceiling)
- **Fuel budget:** Explicit reserves only (no f_oh) — use `compute_reserve_fuel()` directly
- **New functions needed:**
  1. `climb_segment()` — altitude-stepping integration (1,000 ft steps), energy method
  2. `descend_segment()` — 2,000 ft/min descent, fuel scaled to aircraft size (not fixed 300 lb)
  3. `simulate_mission2_sampling()` — top-level mission orchestrator
- **Add to `run_missions.py`:** `run_mission2()` parallel to existing `run_mission1()`

### After Mission 2: Mission 3, then Comparative Analysis

**Mission 3: Low-Altitude Smoke Survey** (not yet planned in detail)
- 8 hours, 30,000 lb payload, ~1,500 ft AGL endurance
- Fuel budget: explicit reserves only (no f_oh)

**Comparative analysis** (after all 3 missions):
- Weight breakdown stacked bars
- Speed/altitude profile plots
- Fuel cost metrics ($/klb·nm)
- Combined comparison across all missions

### Fuel Cost Assumptions
From ASSUMPTIONS_LOG.md (G1): Jet-A at $5.50/gal (~$0.82/lb at 6.7 lb/gal).

---

## Known Limitations the Next Thread Should Be Aware Of

1. **Path A/B reconciliation is resolved.** Mission 1 uses f_oh (Path A-style). Missions 2 and 3 use explicit reserves only (no f_oh). See PHASE2_STEP1_RECONCILIATION.md for full rationale.

2. **The altitude optimizer's thrust check uses `continue` (not `break`).** This was changed in Mission 1 to handle non-monotonic thrust-drag balance at low altitudes. The optimizer searches the full altitude range from h_min to ceiling. For Mission 2 climb modeling, you should use the same approach: thrust-drag balance is non-monotonic, so don't assume "if thrust fails at h, it fails at h+1."

3. **Three aircraft have unphysical calibrated CD0 values (P-8: 0.060, A330: 0.033, 777: 0.041).** These are 2–4× physical reality. For Mission 1 engine-out, this made single-engine flight impossible at all altitudes. For Mission 2, these will distort climb ceilings (predicting lower ceilings than reality). Flag results for these aircraft as lower confidence.

4. **The DC-8's calibration produces unrealistic cruise-vs-overhead split** (k_adj=0.605, f_oh=0.260). For Missions 2/3 which don't use f_oh, the DC-8's cruise fuel burn rate will be ~40% too low. Results should be flagged as low confidence for absolute numbers.

5. **The existing `estimate_climb_fuel()` is too simple for Mission 2.** It uses a single-point average at h/2 altitude with fixed 1,500 ft/min ROC. Mission 2 needs altitude-stepping integration where ROC varies with weight, altitude, and thrust. Build a new `climb_segment()` function per PHASE2_MISSION2_PLAN.md.

6. **Descent fuel model needs scaling for Mission 2.** The fixed ~300 lb per descent is adequate for Mission 1 (single descent) but compounds over 8–12 cycles in Mission 2. Scale descent fuel to aircraft size using `idle_fraction × cruise_fuel_flow × descent_time`.

---

## Analysis Driver Scripts

All outputs are reproducible from scripts in `src/analysis/`. No ad-hoc or interactive invocation needed.

### Running the scripts

```bash
# Calibrate all aircraft, print reports, save JSON (~12 min)
python3 -m src.analysis.run_calibration

# Generate all range-payload plots (~12 min, includes calibration)
python3 -m src.analysis.run_plots

# Mission analysis (~8 min, includes calibration)
# Currently runs Mission 1 only; add Mission 2 here
python3 -m src.analysis.run_missions
```

### Script dependency chain

```
run_calibration.py
    └── run_all_calibrations() → (all_aircraft_data, all_calibrations)
            ├── Used by run_plots.py
            └── Used by run_missions.py (Phase 2)
```

`run_plots.py` and `run_missions.py` import `run_all_calibrations()` from `run_calibration` so calibration only runs once when scripts are called together.

---

## Function Map Across Modules

### Path A: Calibration Range (validated, used for range-payload diagrams)

```
calibration.calibrate_aircraft()
    └── calibration.calibration_error()
            └── calibration.compute_calibration_range()
                    ├── cruise_fuel = total_fuel - f_oh × W_tow
                    ├── performance.step_cruise_range()     ← shared core
                    └── + CLIMB_DISTANCE_NM + DESCENT_DISTANCE_NM (fixed credits)
```

### Path B: Mission Range (code exists, NOT YET VALIDATED)

```
performance.compute_range_for_payload()
    ├── performance.estimate_climb_fuel()    ← energy method
    ├── performance.estimate_descent_credit() ← 3° glide path
    ├── performance.compute_reserve_fuel()   ← 5% contingency + 200nm alt + 30min hold
    ├── performance.step_cruise_range()      ← shared core
    └── total = climb_distance + cruise_range + descent_distance
```

### Shared core (used by both paths)

```
performance.step_cruise_range()
    ├── performance.optimal_cruise_altitude()  ← SR-maximizing altitude search
    │       └── performance.cruise_conditions()
    ├── performance.cruise_conditions()        ← CL, CD, L/D, TSFC at given state
    │       ├── atmosphere.density(), atmosphere.speed_of_sound()
    │       ├── aerodynamics.lift_coefficient(), aerodynamics.drag_coefficient()
    │       └── propulsion.tsfc()
    └── performance.breguet_range_nm()         ← per-segment range
```

### Plotting (uses Path A only)

```
plotting.range_payload.generate_rp_curve()
    └── calibration.compute_calibration_range()  ← Path A

plotting.range_payload.plot_individual_rp()
    └── generate_rp_curve()

plotting.range_payload.plot_overlay_rp()
    └── generate_rp_curve() for each aircraft
```

### Key functions by module

| Module | Function | Purpose |
|---|---|---|
| `performance.py` | `breguet_range_nm()` | Classic Breguet range equation |
| `performance.py` | `cruise_conditions()` | All flight params at given state |
| `performance.py` | `optimal_cruise_altitude()` | SR-maximizing altitude search (supports drag_multiplier, h_min) |
| `performance.py` | `step_cruise_range()` | Multi-segment cruise integration (supports drag_multiplier, h_min) |
| `performance.py` | `estimate_climb_fuel()` | Energy-method climb fuel (simple, for reference) |
| `performance.py` | `compute_reserve_fuel()` | Reserve fuel budget — **use this for Missions 2/3** |
| `calibration.py` | `compute_calibration_range()` | Range via overhead model (Path A, validated) |
| `calibration.py` | `calibrate_aircraft()` | Fit CD0, e, k_adj, f_oh to data |
| `missions.py` | `simulate_mission1_engine_out()` | Mission 1 simulation (complete) |
| `missions.py` | `_find_fuel_at_distance()` | Interpolate fuel/weight at target distance |
| `analysis/run_calibration.py` | `run_all_calibrations()` | Returns (all_ac, calibrations) — import this |
| `analysis/run_missions.py` | `run_mission1()` | Mission 1 driver with formatted output |
| `plotting/range_payload.py` | `generate_rp_curve()` | Sweep payload, compute RP curve |
| `aircraft_data/loader.py` | `load_all_aircraft()` | Load all 7 aircraft as standardized dicts |
| `utils.py` | `fuel_cost()` | Fuel cost from weight ($5.50/gal default) |

---

## Process Notes

- The human collaborator is a space scientist, not an aircraft engineer.
- An independent Claude review thread provides feedback after each major step. After implementing Mission 2, write a report (PHASE2_MISSION2_REPORT.md) for the reviewer. The human will pass it to the review thread and bring back feedback.
- The known conclusion from the original NASA study is that the **767-200ER and P-8** are the top contenders. Mission 1 confirmed the 767 as the clear leader; Mission 2 will further test altitude capability.
- Use `python3` (not `python`) — the system doesn't have `python` on PATH.
- SciPy, NumPy, and Matplotlib are installed.
- The workflow for each mission: implement → run tests → run analysis → write report → commit/push → reviewer feedback → incorporate feedback → next mission.
