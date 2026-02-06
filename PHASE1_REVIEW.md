# Phase 1 Review Document: Core Performance Model & Calibration

## Purpose of This Review

This document is written for an independent reviewer (another Claude instance) to evaluate the Phase 1 work on the DC-8 Replacement Aircraft Performance Study. The reviewer should assess whether the modeling approach, calibration results, and identified limitations are sound enough to proceed to Phase 2 (mission analysis).

**What we want from the reviewer:**
1. Are there methodological errors or oversights?
2. Are the calibration results trustworthy enough to use for mission analysis?
3. Are there risks we haven't identified that could invalidate the Phase 2 work?
4. Any suggestions for Phase 2 approach?

---

## Project Context

We are replicating a published NASA study evaluating candidate replacement aircraft for the DC-8-72 Flying Laboratory. The study compares seven aircraft across three science missions. We know from the published abstract that the **767-200ER and P-8** are the top contenders — this serves as a high-level validation target.

We do **not** have access to NASA's Flight Optimization System (FLOPS), so we built physics-based models from first principles. The human collaborator is a space scientist (not an aircraft engineer), so this review serves as expert-level scrutiny that neither author can provide.

---

## What Was Built in Phase 1

### Model Architecture

Four modules, each building on the previous:

1. **Atmosphere** (`atmosphere.py`): ISA model, sea level to 65,000 ft. Troposphere + lower stratosphere. 18 tests verified against published ISA tables.

2. **Aerodynamics** (`aerodynamics.py`): Parabolic drag polar, CD = CD0 + CL²/(π·AR·e). Computes CL from weight/q/S, L/D, max L/D, engine-out drag increment (+10%).

3. **Propulsion** (`propulsion.py`): TSFC = TSFC_ref × f_alt(h) × f_mach(M) × k_adj, where:
   - f_alt = sqrt(theta/theta_ref), standard for high-bypass turbofans
   - f_mach = 1 + 0.3 × (M - M_ref), linear correction
   - k_adj = calibration multiplier
   - Thrust lapse: T_avail = T_SLS × (ρ/ρ0)^0.75

4. **Performance** (`performance.py`):
   - Breguet range equation: R = (V/TSFC) × (L/D) × ln(Wi/Wf)
   - Step-cruise: divides mission into N segments, recomputes optimal altitude at each step
   - Also contains climb/descent fuel estimation functions for future mission analysis

5. **Calibration** (`calibration.py`): Fits 4 parameters per aircraft to match published range-payload data. This is the most important module and the focus of this review.

### Calibration Approach

For each aircraft, we have 2-3 published range-payload "corner points" (max payload, max fuel, ferry). We fit four parameters:

| Parameter | Meaning | Bounds |
|-----------|---------|--------|
| CD0 | Zero-lift drag coefficient | 0.015 – 0.040 |
| e | Oswald span efficiency | 0.65 – 0.90 |
| k_adj | TSFC multiplier | 0.80 – 1.20 |
| f_oh | Non-cruise fuel overhead fraction | 0.05 – 0.25 |

**Optimization method:** SciPy `differential_evolution` (global) followed by `Nelder-Mead` (local refinement).

**The critical modeling choice: the non-cruise fuel overhead model.**

Published range-payload data includes all non-cruise fuel (taxi, takeoff, climb, descent, reserves). The calibration function computes range as:

```
cruise_fuel = total_fuel - f_oh × W_takeoff
range = step_cruise_breguet(cruise_fuel, ...) + 200 nm (climb credit) + 120 nm (descent credit)
```

The `f_oh × W_tow` term is critical. Without it, the Breguet equation cannot produce the observed range ratios between calibration points. Here is why:

Consider the DC-8 with these two points:
- Point 1: 52,000 lb payload, 116,000 lb fuel → 2,750 nmi
- Point 2: 20,745 lb payload, 147,255 lb fuel → 5,400 nmi

The range ratio is 5,400/2,750 = 1.96. In a pure Breguet model, range scales as ln(Wi/Wf). For Point 1, Wi/Wf = 325,000/209,000 = 1.555. For Point 2, Wi/Wf = 325,000/177,745 = 1.828. The ratio of ln values is ln(1.828)/ln(1.555) = 1.37.

So the Breguet equation can only produce a 37% range increase between these points, but we need a 96% increase. The aerodynamic efficiency parameter (V × L/D) varies only ±5% across the typical CL range, nowhere near enough to close the gap.

The overhead model resolves this: at Point 1 (W_tow = 325,000 lb), overhead = 0.26 × 325,000 = 84,500 lb, leaving only 31,500 lb cruise fuel from 116,000 total. At Point 2 (W_tow = 325,000 lb), overhead is the same 84,500 lb, but there's 147,255 lb total fuel, leaving 62,755 lb for cruise — a 2:1 ratio of available cruise fuel, which with Breguet produces the observed 2:1 range ratio.

**Trade-off:** Because f_oh absorbs non-cruise fuel effects, the remaining parameters (CD0, e, k_adj) become "effective" values that compensate for the simplified model. They should not be interpreted as physically meaningful individual quantities. The combined 4-parameter model matches observed performance; the individual parameters do not necessarily represent real aerodynamic or propulsive characteristics.

---

## Calibration Results

| Aircraft | CD0 | e | k_adj | f_oh | L/D_max | RMS Error | Status |
|----------|------|-------|-------|------|---------|-----------|--------|
| DC-8 | 0.0141 | 0.968 | 0.605 | 0.260 | 20.4 | 0.5% | ✓ |
| G-V | 0.0150 | 0.745 | 0.801 | 0.131 | 17.3 | 1.2% | ✓ |
| 737-900ER | 0.0355 | 1.223 | 0.757 | 0.062 | 16.7 | 0.7% | ✓ |
| 767-200ER | 0.0153 | 0.947 | 0.756 | 0.157 | 19.7 | 0.2% | ✓ |
| A330-200 | 0.0334 | 2.165 | 1.021 | 0.000 | 22.6 | 3.0% | ✓ |
| 777-200LR | 0.0410 | 1.811 | 0.556 | 0.080 | 18.3 | 6.5% | ⚠ |
| P-8 | 0.0597 | 0.975 | 0.339 | 0.180 | 11.5 | 0.0% | ✓ (derived) |

### What the reviewer should notice about these parameters:

**Parameters outside physical bounds:**
- 737-900ER: e = 1.223 (physically impossible; Oswald efficiency cannot exceed 1.0)
- A330-200: e = 2.165 (far outside physical bounds)
- 777-200LR: e = 1.811 (far outside physical bounds)
- DC-8: k_adj = 0.605 (implies TSFC is 40% lower than published — very implausible on its own)
- A330-200: f_oh = 0.000 (zero non-cruise overhead — clearly unphysical)
- P-8: CD0 = 0.0597 (very high for a transport aircraft)

**We acknowledged this in the design:** the bounds in the code (e: 0.65–0.90) are the initial bounds for `differential_evolution`, but the subsequent `Nelder-Mead` refinement is unconstrained and can (and does) move parameters outside these bounds. This is by design — we prioritized matching the range-payload data over maintaining physically realistic individual parameters.

**The question for the reviewer:** Is this acceptable for comparative mission analysis, or does the unphysical parameter space undermine the model's ability to extrapolate to off-design conditions (engine-out, low altitude, repeated climbs)?

### Fit quality by aircraft

**Excellent fits (< 2% RMS): DC-8, G-V, 737-900ER, 767-200ER**
These four aircraft have well-behaved calibrations where the model curve passes through or very close to all published data points. These are the aircraft most relevant to the study conclusion.

**Acceptable fit (3% RMS): A330-200**
The A330 required e = 2.165 and f_oh = 0.000, both unphysical. The middle calibration point (max fuel range) shows a ~3-4% error. This may indicate the A330's actual performance curve has a shape that the 4-parameter model cannot capture well.

**Marginal fit (6.5% RMS): 777-200LR**
The worst calibration. Both the max-payload point and the max-fuel point show ~8% individual errors. The 777's extreme range (10,800 nmi ferry) stresses the simplified model. Parameters are also unphysical (e = 1.811, k_adj = 0.556).

**Derived (P-8):**
The P-8 is derived from the 737-900ER calibration with a +0.025 Oswald efficiency increment for raked wingtips. It has only 2 preliminary calibration points (both estimates, not published data), and the Nelder-Mead refinement from the 737 starting point found parameters that match perfectly. The P-8's parameters (CD0 = 0.0597, k_adj = 0.339) are the most extreme in the table, reflecting the challenge of extrapolating the 737 model to an aircraft with very different fuel capacity.

---

## Range-Payload Diagrams

The overlay plot (`rp_overlay_all.png`, included with this review) shows all seven aircraft on one diagram with mission requirement lines overlaid. Individual aircraft plots are also available.

**Key observations from the overlay:**
1. The DC-8 (red) falls well short of Mission 1's 5,050 nmi requirement at 46,000 lb payload — this is expected and matches the study's premise that the DC-8 needs replacement for long-range missions.
2. The 767-200ER (blue) comfortably covers both Mission 1 and Mission 2 requirements with payload to spare.
3. The 737-900ER (orange) and P-8 (green) have limited payload capacity but reasonable range for the lighter-payload missions.
4. The A330 and 777 are vastly oversized for these missions.
5. The G-V is far too small for the payload requirements (5,800 lb max vs. 46,000-52,000 lb needed).

---

## Data Sources and Confidence

| Aircraft | Calibration Point Source | Confidence |
|----------|-------------------------|------------|
| DC-8-72 | Problem statement (NASA) | **High** — authoritative |
| G-V | Gulfstream APD + FAA TCDS + Jane's | **High** |
| 737-900ER | Boeing APD D6-58325-6 + FAA TCDS | **High** for max-payload; **Medium** for ferry (estimated) |
| 767-200ER | Boeing APD D6-58328 + FAA TCDS | **High** |
| A330-200 | Airbus APD + EASA TCDS | **High** for max-payload; **Medium** for ferry (estimated) |
| 777-200LR | Boeing APD D6-58329-2 + FAA TCDS | **High** |
| P-8 | Problem statement + derived from 737 | **Low** — points are estimates, not published data |

---

## Known Issues and Risks for Phase 2

### 1. Off-Design Extrapolation Risk (HIGH)
The calibration matches cruise performance. Phase 2 missions involve:
- **Mission 1 engine-out:** Reduced speed, increased drag, lower altitude. The drag model (parabolic polar with unphysical e) may not extrapolate well. The 10% drag increment for engine-out is assumed constant with speed/configuration.
- **Mission 2 repeated climbs:** The climb fuel estimation uses an energy method with a fixed 1,500 ft/min ROC assumption. For repeated climb-descend cycles, errors compound over each cycle.
- **Mission 3 low-altitude endurance:** At 1,500 ft, the air density is ~96% of sea level. The TSFC model was calibrated at 35,000 ft — the altitude correction (sqrt(theta)) extrapolation to low altitude gives a TSFC penalty of ~15-20%. Whether this is accurate is uncertain.

### 2. The f_oh Overhead in Mission Analysis
For calibration, f_oh captures non-cruise fuel as a fraction of TOW. But for mission analysis, we need to explicitly model climb fuel, descent fuel, and reserves — we can't just subtract f_oh × W_tow because the missions have non-standard profiles. The `performance.py` module has separate climb/descent/reserve functions for this purpose, but **these functions were not used or validated during calibration**. They are independent models that may produce different fuel allocations than what f_oh implies.

This is an architectural inconsistency: the calibration module uses `compute_calibration_range()` (with f_oh), while mission analysis will use `compute_range_for_payload()` (with explicit climb/descent/reserve). The two approaches may give different absolute ranges for the same aircraft at the same conditions.

**Mitigation option:** Use the calibrated CD0, e, k_adj values in the mission analysis code, but be aware that absolute range numbers may differ from the calibration-derived values.

### 3. Calibration Bounds Were Not Enforced
The code specifies physical bounds (e.g., e: 0.65–0.90) for `differential_evolution`, but `Nelder-Mead` is unconstrained. Several aircraft have parameters far outside physical bounds. If the mission analysis code makes assumptions that depend on parameters being physical (e.g., checking CL at max L/D), it might behave unexpectedly.

### 4. 777-200LR Results May Be Unreliable
At 6.5% RMS calibration error, mission analysis results for the 777 should be treated as approximate. However, the 777 is massively oversized for these missions, so its absolute numbers matter less than the qualitative conclusion that it's overkill.

---

## Architectural Note: Two Range Computation Paths

This is worth highlighting because it could cause confusion:

**Path A (calibration):** `calibration.compute_calibration_range()`
- Used for: fitting parameters to published data, generating range-payload diagrams
- Model: cruise_fuel = total_fuel - f_oh × W_tow; step-cruise Breguet; +200 nm climb credit, +120 nm descent credit
- Validated: Yes, against published data (that's what calibration is)

**Path B (mission analysis):** `performance.compute_range_for_payload()`
- Used for: Phase 2 mission analysis (planned, not yet used)
- Model: explicit climb fuel (energy method), explicit descent credit (3° glide), explicit reserves (5% contingency + 200 nm alternate + 30 min hold), then step-cruise Breguet for remaining fuel
- Validated: No — this code exists but has never been compared against Path A or against published data

**Risk:** If Path B gives substantially different ranges than Path A for the same conditions, the calibrated parameters (which were fitted to match data via Path A) may produce incorrect results when used with Path B.

**Suggested mitigation for Phase 2:** Before running missions, run Path B at calibration conditions and compare to published data. If discrepancies are large, either (a) recalibrate using Path B, or (b) adjust Path B's sub-models to be consistent with Path A.

---

## Test Summary

74 tests total, all passing:
- 18 atmosphere tests (ISA tables)
- 23 aircraft data validation tests (weight balance, unit consistency, cross-aircraft sanity)
- 7 aerodynamics tests (drag polar, max L/D, engine-out)
- 7 propulsion tests (TSFC corrections, thrust lapse)
- 8 performance tests (Breguet equation, step-cruise)
- 4 calibration range tests (physical behavior)
- 7 calibration quality tests (verify each aircraft RMS < threshold)

---

## Questions for the Reviewer

1. **Is the non-cruise fuel overhead model (f_oh × W_tow) a reasonable approach**, or is there a better way to bridge the gap between Breguet cruise range and published mission range?

2. **Do the unphysical calibrated parameters** (e > 1.0, etc.) pose a real risk for off-design mission analysis, or is it acceptable to treat the 4-parameter set as an opaque calibration that works as a unit?

3. **Should we recalibrate using the explicit climb/descent/reserve model** (Path B) before running Phase 2 missions, to ensure consistency? This would be significant work (re-running the optimizer with a different objective function).

4. **Are there physical sanity checks** we should add before proceeding — e.g., verifying that the model produces reasonable fuel burn rates (lb/hr), reasonable cruise altitudes, or reasonable specific range values?

5. **For the P-8 derivation,** is the +0.025 Oswald efficiency increment for raked wingtips reasonable? The literature suggests raked wingtips provide 2-4% fuel burn reduction, which corresponds to a ~0.02-0.04 improvement in effective span efficiency.

---

## Files Included with This Review

1. **This document** (`PHASE1_REVIEW.md`)
2. **Overlay range-payload diagram** (`outputs/plots/rp_overlay_all.png`) — shows all aircraft curves with calibration points and mission requirement lines
3. **Individual range-payload diagrams** (`outputs/plots/rp_*.png`) — one per aircraft, showing model vs. published data in detail
4. **Assumptions log** (`ASSUMPTIONS_LOG.md`) — all modeling assumptions with rationale and impact assessment

For code review, the key files are:
- `src/models/calibration.py` — the calibration approach (418 lines)
- `src/models/performance.py` — Breguet + step-cruise + climb/descent models (~620 lines)
- `src/models/aerodynamics.py` — drag polar (~200 lines)
- `src/models/propulsion.py` — TSFC model (~200 lines)
