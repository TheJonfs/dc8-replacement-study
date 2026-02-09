# DC-8 Replacement Study — Handoff Status

## What This File Is

This document prepares a new Claude thread to continue the DC-8 Replacement Aircraft Performance Study from where the previous threads left off. Phases 0 and 1 are complete and reviewed. Phase 2 (mission analysis) is next.

Read CLAUDE.md for the full problem statement. Read STUDY_PLAN.md for the original phasing. Read ASSUMPTIONS_LOG.md for all modeling assumptions. This file focuses on what was built, how it works, what to watch out for, and what to do next.

---

## Project State: Phase 1 Complete, Ready for Phase 2

### Git History
```
f66728d  Fix 767-200ER MZFW (235k→260k lb) and respond to Phase 1 review
eff1c90  Add Phase 1 review document for independent evaluation
ad2bf60  Phase 1: core performance model, calibration system, and range-payload diagrams
9ac6f5c  Address Phase 0 review feedback: correct 767-200ER fuel capacity, add data validation tests
db07593  Phase 0: atmosphere model, aircraft data collection, and project scaffolding
9eaeac2  Initial commit: project structure and problem statement
60af776  Initial commit
```

### Test Status
74 tests, all passing. Run with: `python3 -m pytest tests/ -v`
Note: the calibration quality tests (`test_performance.py::TestCalibrationQuality`) take ~12 minutes because they run differential evolution for each aircraft.

---

## Repository Map

```
CLAUDE.md                    # Problem statement (read this first)
STUDY_PLAN.md                # Original 6-phase plan (phases 0-1 are outdated; 3-6 still relevant)
ASSUMPTIONS_LOG.md           # All modeling assumptions with rationale and impact
PROGRESS_REPORT.md           # Detailed Phase 0+1 progress report
PHASE1_REVIEW.md             # Review document sent for independent evaluation
PHASE1_REVIEW_RESPONSE.md    # Response to review feedback (767 fix, A330/777 verification)

src/
    utils.py                 # Unit conversions (NM_TO_FT, FT_TO_NM, HR_TO_SEC, fuel cost)
    aircraft_data/
        loader.py            # Unified data loader — normalizes all aircraft into standard dict
        dc8_72.py            # NASA DC-8 data (from problem statement)
        gulfstream_gv.py     # G-V data
        boeing_737_900er.py  # 737-900ER data (modeling intermediate, not a study candidate)
        boeing_p8.py         # P-8 Poseidon (derived from 737-900ER)
        boeing_767_200er.py  # 767-200ER data (corrected twice: fuel in Phase 0, MZFW in Phase 1)
        a330_200.py          # A330-200 data
        boeing_777_200lr.py  # 777-200LR data
    models/
        atmosphere.py        # ISA model (sea level to 65,000 ft)
        aerodynamics.py      # Parabolic drag polar, L/D, engine-out drag
        propulsion.py        # TSFC model with altitude/Mach corrections, thrust lapse
        performance.py       # Breguet range, step-cruise, climb/descent fuel (694 lines)
        calibration.py       # Parameter fitting + calibration range computation (417 lines)
    plotting/
        range_payload.py     # Range-payload diagram generation

tests/
    test_atmosphere.py       # 18 tests: ISA tables verification
    test_aircraft_data.py    # 23 tests: weight balance, unit consistency, cross-aircraft sanity
    test_performance.py      # 33 tests: aero, propulsion, Breguet, calibration quality

outputs/plots/
    rp_dc8.png ... rp_p8.png    # Individual range-payload diagrams (7 aircraft)
    rp_overlay_all.png           # Combined overlay with mission requirement lines
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

### Confidence Tiers for Mission Analysis
1. **High confidence:** 767-200ER (physical parameters, fuel burn matches), G-V, 737-900ER, 777-200LR
2. **Medium confidence:** P-8 (derived model, within 30%)
3. **Low confidence for absolute numbers:** DC-8 (k_adj=0.605 implies cruise TSFC ~40% below reality; f_oh=0.26 compensates), A330-200 (e=2.165, f_oh=0.000 — both unphysical)

The combined models match range-payload data well for all aircraft. The issue is that for DC-8 and A330, the cruise-vs-overhead split is unrealistic, which matters when modeling off-design conditions.

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

## What Phase 2 Needs to Do

### Three Science Missions

**Mission 1: Long-Range Transport with Engine-Out (SCEL→KPMD)**
- Distance: 5,050 nmi
- Payload: 46,000 lb
- Single engine failure at mission midpoint
- Need: speed/altitude profiles showing engine-out effects
- Key modeling: engine-out drag increment (+10%), thrust reduction (50% for twins, 25% for DC-8), speed/altitude adjustment after failure
- For twins: losing 1 of 2 engines. For DC-8: losing 1 of 4.

**Mission 2: Vertical Atmospheric Sampling (NZCH→SCCI)**
- Distance: ~4,200 nmi
- Payload: 52,000 lb
- Repeated climb-descend segments for atmospheric column sampling
- As aircraft gets lighter (fuel burn), it can reach higher altitudes
- Need: altitude capability progression throughout mission, speed/altitude profiles

**Mission 3: Low-Altitude Smoke Survey**
- Region: Central US (Arkansas-Missouri)
- Duration: 8 hours
- Payload: 30,000 lb
- Altitude: ~1,500 ft AGL
- Extended low-altitude endurance — very different from cruise optimization

### For Each Mission, Each Aircraft

Determine:
- Can the aircraft complete the mission? (fuel feasibility)
- Total mission fuel consumption
- Reserve fuel remaining
- For G-V and P-8: how many aircraft (n) needed for equivalent aggregate payload? Aggregate fuel?

### For G-V and P-8
These aircraft cannot carry the full mission payloads (G-V max ~5,800 lb; P-8 max ~23,885 lb). Calculate how many aircraft are needed to carry the aggregate payload, and compute per-aircraft and aggregate fuel/cost.

### Deliverables from Phase 2+
1. **Mission performance table** — go/no-go, fuel burn, reserves for each aircraft × mission
2. **Weight breakdown stacked bars** — OEW / payload / fuel / reserves for each combination
3. **Speed and altitude profiles** — Mach and altitude vs. distance for Missions 1 and 2
4. **Fuel cost metrics** — total cost per mission, cost per 1000 lb·nmi
5. **Combined comparison** — aggregate fuel for G-V fleet and P-8 fleet vs. single larger aircraft

### Fuel Cost Assumptions
From ASSUMPTIONS_LOG.md (G1): Jet-A at $5.50/gal (~$0.82/lb at 6.7 lb/gal).

---

## Known Limitations the Next Thread Should Be Aware Of

1. **performance.py is large (694 lines) and has accumulated code from multiple iterations.** It contains functions from early attempts at climb/descent modeling that were partially superseded by the f_oh overhead approach. The `compute_range_for_payload()` function uses the earlier explicit climb/descent/reserve model (Path B), while calibration uses `calibration.compute_calibration_range()` (Path A). Both use the same underlying `step_cruise_range()` function.

2. **The Nelder-Mead refinement in calibration is unconstrained.** Several aircraft have parameters outside the initial differential_evolution bounds (e.g., 737-900ER e=1.223, A330 e=2.165). This was intentional — we prioritized matching the data over physical bounds. But it means the models may behave unexpectedly at conditions far from calibration.

3. **The DC-8's calibration is problematic for cruise fuel burn analysis.** Its k_adj=0.605 means the model thinks the DC-8's engines are 40% more efficient than published. The f_oh=0.26 compensates by claiming 26% of fuel is overhead. For mission analysis that separates cruise from non-cruise, this split will produce unrealistic cruise fuel burn rates. Consider whether to use the f_oh overhead model for DC-8 missions or recalibrate with constrained parameters.

4. **The P-8's calibration points are estimates, not published data.** Its parameters (CD0=0.0597, k_adj=0.339) are the most extreme. Results should be treated as lowest-confidence.

5. **The 767-200ER range-payload corner points (5,150 / 6,500 / 7,850 nmi) are Breguet-estimated, not directly from Boeing charts.** We derived them from the Aircraft Commerce 6,850 nmi reference point and cross-checked against delivery flight records and design range. They produced a perfect calibration fit, which is encouraging, but they haven't been independently verified against the Boeing APD's range-payload chart.

6. **The STUDY_PLAN.md phase table is outdated.** Phase 0 and 1 descriptions don't reflect what was actually done (e.g., Phase 1 was supposed to be DC-8 only, but we calibrated all aircraft). Phases 3-6 in the original plan correspond roughly to what CLAUDE.md calls Phase 2 deliverables. Use CLAUDE.md as the authoritative requirements document.

---

## Analysis Driver Scripts

All outputs are reproducible from scripts in `src/analysis/`. No ad-hoc or interactive invocation needed.

### Running the scripts

```bash
# Calibrate all aircraft, print reports, save JSON (~12 min)
python3 -m src.analysis.run_calibration

# Generate all range-payload plots (~12 min, includes calibration)
python3 -m src.analysis.run_plots

# Mission analysis (Phase 2 — stub, not yet implemented)
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
| `performance.py` | `specific_range()` | Instantaneous nm/lb efficiency |
| `performance.py` | `cruise_conditions()` | All flight params at given state |
| `performance.py` | `optimal_cruise_altitude()` | SR-maximizing altitude search |
| `performance.py` | `step_cruise_range()` | Multi-segment cruise integration |
| `performance.py` | `estimate_climb_fuel()` | Energy-method climb fuel (Path B) |
| `performance.py` | `estimate_descent_credit()` | Glide distance credit (Path B) |
| `performance.py` | `compute_reserve_fuel()` | Reserve fuel budget (Path B) |
| `performance.py` | `compute_range_for_payload()` | Full mission range (Path B) |
| `calibration.py` | `compute_calibration_range()` | Mission range via overhead model (Path A) |
| `calibration.py` | `calibrate_aircraft()` | Fit CD0, e, k_adj, f_oh to data |
| `calibration.py` | `calibrate_p8_from_737()` | Derive P-8 from 737-900ER |
| `plotting/range_payload.py` | `generate_rp_curve()` | Sweep payload, compute RP curve |
| `plotting/range_payload.py` | `plot_individual_rp()` | Single aircraft RP diagram |
| `plotting/range_payload.py` | `plot_overlay_rp()` | All aircraft overlay RP diagram |
| `aircraft_data/loader.py` | `load_all_aircraft()` | Load all 7 aircraft as standardized dicts |
| `utils.py` | `fuel_cost()` | Fuel cost from weight ($5.50/gal default) |

---

## Process Notes

- The human collaborator is a space scientist, not an aircraft engineer. The project instruction is to "err on the side of being able to justify to yourself (or perhaps to another Claude instance reviewing your work)."
- An independent Claude thread reviews progress reports and provides feedback. Reviews have caught two real data errors (767-200ER fuel capacity in Phase 0, MZFW in Phase 1) and also made two incorrect claims (A330 and 777 fuel capacities). The review process is valuable but claims need independent verification.
- The known conclusion from the original NASA study is that the **767-200ER and P-8** are the top contenders. This serves as a high-level validation target.
- Use `python3` (not `python`) — the system doesn't have `python` on PATH.
- SciPy, NumPy, and Matplotlib are installed.
