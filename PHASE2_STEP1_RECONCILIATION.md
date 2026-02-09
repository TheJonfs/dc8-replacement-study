# Phase 2 Step 1: Path A/B Reconciliation

## Summary

Path A (calibration) and Path B (mission) produce **dramatically different ranges** when given the same aircraft, payload, fuel, and calibrated aerodynamic/propulsion parameters (CD0, e, k_adj). The discrepancies range from -27% to +239%, depending on the aircraft. **Path B cannot be used with Path A's calibrated parameters without modification.**

The root cause is clear: Path A's `f_oh` parameter absorbs all non-cruise fuel into a single overhead fraction, while Path B computes climb fuel, descent fuel, and reserves explicitly. For aircraft where `f_oh` is large (DC-8: 26%, P-8: 18%, GV: 13%), Path B's explicit deductions are much smaller than Path A's overhead, leaving far more fuel for cruise and producing grossly inflated ranges. For aircraft where `f_oh` is near zero (A330: 0%, 767: 3%), Path B deducts realistic reserves that Path A doesn't account for, producing shorter ranges.

## What Was Done

Ran both paths at every calibration point for all six study candidates using the Phase 1 calibrated parameters. The script `src/analysis/reconcile_paths.py` breaks down:
- **Fuel budget:** How each path splits total fuel into cruise vs. non-cruise
- **Range components:** Climb distance, cruise range, descent distance
- **Discrepancies:** Absolute and percentage differences

## Results Summary

| Aircraft | Path A→Target | Path B→Target | A-B Range Gap | f_oh | Path B Deductions | Overhead Diff |
|---|---|---|---|---|---|---|
| **DC-8** | ~0.5% | +115–239% | +6,500–7,300 nm | 0.260 | 15,400–16,900 lb | -62,000–-69,000 lb |
| **GV** | ~1% | +21–27% | +1,400–1,500 nm | 0.131 | 7,100–7,400 lb | -4,400–-4,700 lb |
| **P-8** | ~0.2% | +47–67% | +2,800–3,000 nm | 0.180 | 11,400–11,500 lb | -18,000–-22,500 lb |
| **767-200ER** | 0.0% | -9 to -10% | -500–-800 nm | 0.030 | 25,200–26,500 lb | +13,500–+16,100 lb |
| **A330-200** | -1 to +4% | -16 to -28% | -1,300–-1,500 nm | 0.000 | 44,600–48,700 lb | +44,600–+48,600 lb |
| **777-200LR** | -8 to +8% | +1 to +19% | +500–+800 nm | 0.080 | 44,300–45,100 lb | -6,700–-17,100 lb |

## Root Cause Analysis

### The two paths model the same physics differently

**Path A** (calibration):
```
non_cruise_fuel = f_oh × W_tow          (single calibrated parameter)
cruise_fuel = total_fuel - non_cruise_fuel
range = step_cruise(cruise_fuel, W_tow) + 200nm + 120nm
```

**Path B** (mission):
```
climb_fuel = energy_method(W_tow, h_cruise)    (~3,500–19,000 lb)
descent_fuel = 300 lb                           (fixed constant)
reserve_fuel = 5% contingency + 200nm alt + 30min hold   (~4,000–30,000 lb)
cruise_fuel = total_fuel - climb_fuel - descent_fuel - reserve_fuel
range = step_cruise(cruise_fuel, W_tow - climb_fuel) + climb_dist + descent_dist
```

### Why they diverge

1. **f_oh absorbed the calibration residuals.** During Phase 1 calibration, f_oh was a free parameter that compensated for all modeling errors — not just non-cruise fuel. For the DC-8 (k_adj=0.605), the model's cruise TSFC is ~40% too low, so it needs f_oh=0.26 to remove enough fuel from cruise to avoid overpredicting range. The 26% "overhead" doesn't represent real non-cruise fuel — it's a correction term.

2. **Path B's explicit deductions are physically based but uncalibrated.** The climb fuel model uses a 1,500 ft/min average ROC energy method, which produces reasonable values (3,500–19,000 lb depending on aircraft size). The reserve model uses standard ICAO-type rules. But these were never tuned to match the data, and they don't compensate for the same modeling errors that f_oh does.

3. **Path B also has a second-order effect: cruise starts at lighter weight.** Path A starts `step_cruise_range` at `W_tow` (full takeoff weight). Path B starts at `W_tow - climb_fuel`. This means Path B's cruise operates at a lighter weight, which slightly increases L/D and range per unit fuel. This is physically more correct but contributes to the divergence.

### The three regimes

**High f_oh aircraft (DC-8, P-8, GV):** f_oh removes far more fuel from cruise than Path B's explicit climb+descent+reserves. Path B has much more cruise fuel available → wildly overpredicts range. The DC-8 is the extreme case: Path A removes 84,600 lb as overhead; Path B removes only 15,400 lb. The remaining 69,000 lb of "extra" cruise fuel produces +6,500 nm of phantom range.

**Near-zero f_oh aircraft (A330, 767):** f_oh removes little or nothing from cruise, but Path B still deducts realistic climb fuel (~10,000–19,000 lb) and reserves (~15,000–30,000 lb). Path B has less cruise fuel → underpredicts range. The A330 is the extreme case: f_oh=0.000 means Path A uses ALL fuel for cruise, but Path B deducts ~45,000–49,000 lb for climb/descent/reserves.

**Moderate f_oh aircraft (777):** The two overhead models happen to be closer in magnitude, so the gap is smaller (+5–10%), but still significant.

## Implications for Phase 2

### Path B cannot be used as-is

Using Path B with Path A's calibrated parameters would produce meaningless mission results. The DC-8 would appear to fly 13,000 nm on fuel that actually gets it 6,400 nm. The 767 would appear to fly 10% shorter than its published capability.

### Initial recommendation (pre-review)

The initial recommendation was to use f_oh for the fuel budget across all missions ("hybrid approach"), with mission-specific adjustments layered on top.

### Reviewer feedback: f_oh is profile-dependent

The reviewer identified a critical flaw: **f_oh was calibrated against standard transport profiles** (climb to cruise, long cruise, descend). It should only be used for missions that resemble that profile. The three science missions have fundamentally different profiles:

- **Mission 1 (engine-out):** Close enough to a transport profile. f_oh is appropriate.
- **Mission 2 (climb-descend):** Entirely non-cruise. The cruise/non-cruise distinction that f_oh captures doesn't apply. Using f_oh would remove fuel that should be available for climb-descend cycles — especially destructive for high-f_oh aircraft (DC-8: 84,600 lb removed from 116,000 lb total).
- **Mission 3 (low-altitude endurance):** Negligible climb (1,500 ft vs. FL350). Effectively all cruise at radically different conditions. f_oh's transport-sized overhead is inappropriate.

### Confirmed approach for Phase 2

| Mission | Fuel Budget Method | Physics Parameters |
|---|---|---|
| **1 (engine-out)** | f_oh overhead (hybrid) | CD0, e, k_adj + engine-out adjustments |
| **2 (climb-descend)** | Explicit reserves only; no f_oh | CD0, e, k_adj for each climb/descend segment |
| **3 (low-altitude)** | Explicit reserves only; no f_oh | CD0, e, k_adj at 1,500 ft conditions |

**For Missions 2 and 3:**
1. Compute reserve fuel explicitly using the standard reserve policy (5% contingency + 200nm alternate + 30min hold), using `performance.compute_reserve_fuel()` as-is (standard FL250/250kt assumptions for alternate — this is an operational convention, not a physics model)
2. Allocate all remaining fuel (total minus reserves) to the mission profile
3. Use calibrated CD0, e, k_adj for the physics of each flight segment
4. No f_oh deduction

**For Mission 1:**
1. Use f_oh × W_tow as non-cruise fuel overhead
2. Model engine-out perturbation (drag increment, thrust reduction, speed/altitude adjustment) on top of the calibrated cruise model

### Known fuel burn rate limitations

The DC-8's calibrated k_adj=0.605 produces cruise fuel burn ~50% below published rates (~5,400 lb/hr vs. 10,000–13,000 lb/hr published). The A330's calibrated model overpredicts fuel burn by ~40%. These errors are masked in Mission 1 by f_oh compensation, but will directly affect Mission 3 results where fuel burn rate is the primary output.

**Mitigation:** Flag DC-8 and A330 Mission 3 results as low-confidence. Consider a sensitivity case using published TSFC values alongside calibrated model results.

### Alternative: Constrained recalibration (lower priority)

If more accurate cruise fuel burn rates are needed, a constrained recalibration could be attempted:
- Bound k_adj to [0.85, 1.15] (forcing TSFC close to published values)
- Bound f_oh to [0.02, 0.12] (forcing overhead to physical range)
- Accept higher RMS range-payload error (~5–15% vs. current 0–6%)

This remains a lower-priority sensitivity analysis, not the primary approach.

## Reproduction

```bash
python3 -m src.analysis.reconcile_paths
```

This runs the full reconciliation analysis and prints the detailed comparison tables shown above. Runtime ~12 minutes (dominated by calibration).
