# Phase 2: Mission 2 — Implementation Plan

## Mission Definition

| Parameter | Value |
|---|---|
| Route | Christchurch, New Zealand (NZCH) to Punta Arenas, Chile (SCCI) |
| Distance | ~4,200 nmi |
| Payload | 52,000 lb |
| Profile | Multiple repeating climb-descend segments for vertical atmospheric sampling |
| Key feature | Progressive altitude capability increase as fuel burns off |
| Fuel budget | Explicit reserves only (no f_oh) — per PHASE2_STEP1_RECONCILIATION.md |

## What Makes Mission 2 Different from Mission 1

Mission 1 is a standard transport profile (cruise with engine-out perturbation). Mission 2 is fundamentally different:

- **No sustained cruise.** The aircraft repeatedly climbs to its ceiling, samples the vertical atmospheric column, then descends to low altitude — the entire mission is climb-descend cycles.
- **No f_oh.** Because there is no cruise phase analogous to the calibration regime, the f_oh overhead factor does not apply. Fuel budget uses `compute_reserve_fuel()` for explicit reserves.
- **Altitude is the deliverable, not range.** The mission's scientific value comes from *how high* each sampling cycle reaches. Range (4,200 nmi) is a constraint to satisfy, not an objective to maximize.
- **Progressive ceiling increase.** As the aircraft burns fuel, it gets lighter, and can climb higher. This is the core metric to track — the altitude envelope over the course of the mission.

## Approach: Sawtooth Profile Model

Model the mission as a series of **sawtooth cycles**: climb to ceiling → descend to sampling bottom → repeat. Each cycle:

1. **Climb phase:** From sampling bottom altitude to the weight-limited ceiling. Uses the energy method: thrust required = drag + weight × sin(γ). Fuel burn, distance, and time computed by integrating in altitude steps.

2. **Descent phase:** From ceiling back to sampling bottom. Near-idle thrust, fuel burn scaled to aircraft size (see Descent Model below). Distance computed from descent rate and TAS.

3. **Low-altitude transit (optional):** Brief level segment at bottom altitude between descent endpoint and next climb start. May be negligible or zero.

The mission continues cycling until one of:
- Total distance covered ≥ 4,200 nmi (success — mission complete with reserve fuel check)
- Available fuel exhausted before reaching 4,200 nmi (failure)
- Aircraft too heavy to climb above descent target altitude (pathological — unlikely)

### Key Output Per Cycle
- Maximum altitude achieved (ceiling)
- Fuel burned (climb + descent)
- Distance covered (climb + descent)
- Aircraft weight at start/end

### Key Output For Mission
- Number of complete cycles
- Altitude envelope: ceiling vs. cycle number (or vs. distance)
- Total fuel burned
- Reserve fuel remaining
- Go/no-go determination

## Fuel Budget

```
total_fuel = min(MTOW - OEW - payload, max_fuel)
reserve_fuel = compute_reserve_fuel(total_fuel, ac, CD0, e, k_adj)
mission_fuel = total_fuel - reserve_fuel
```

No f_oh deduction. All of `mission_fuel` is available for climb-descend cycles.

## New Functions to Build

### 1. `climb_segment(W_start_lb, h_start_ft, h_target_ft, mach_climb, ac, CD0, AR, e, tsfc_ref, k_adj)`

Compute fuel, distance, and time for a climb between two altitudes. Uses an altitude-stepping integration (e.g., 1,000 ft steps) rather than the single-point average in the existing `estimate_climb_fuel()`. At each step:
- Compute drag at current altitude/weight/Mach
- Compute thrust available
- Compute excess thrust → rate of climb
- If excess thrust ≤ 0, the aircraft has reached its ceiling — stop
- Compute fuel flow = thrust_required × TSFC
- Compute time for this altitude step = Δh / ROC
- Compute distance = V_TAS × time
- Update weight: W -= fuel_flow × time

Returns: fuel_burned_lb, distance_nm, time_hr, ceiling_ft (actual ceiling achieved), segments list for plotting.

**Key design choice:** Use constant Mach during climb (cruise_mach × 0.95 or similar). This is a simplification — real climbs use constant IAS below transition altitude then constant Mach above — but it's consistent with how the rest of the model works and avoids introducing a new Mach schedule. Document as assumption.

**Ceiling definition:** The altitude where rate of climb drops below 100 ft/min (standard service ceiling) or where thrust_available ≤ drag × 1.0. Either is acceptable; the 100 ft/min ROC threshold is more physically meaningful.

### 2. `descend_segment(W_start_lb, h_start_ft, h_target_ft, mach_descent, ac, CD0, AR, e, tsfc_ref, k_adj)`

Compute fuel, distance, and time for an idle descent. Simpler than climb but non-trivial for Mission 2 because descent is roughly half of every cycle:
- Assume constant descent rate (e.g., 2,000 ft/min)
- Compute time = (h_start - h_target) / descent_rate
- **Fuel burn scaled to aircraft size:** `descent_fuel = idle_fraction × cruise_fuel_flow × descent_time`, where `idle_fraction` ≈ 0.10–0.15 of cruise thrust fuel flow. Compute `cruise_fuel_flow` from `cruise_conditions()` at a representative mid-descent altitude. This replaces the fixed 300 lb assumption from Mission 1 — over 8–12 cycles, the difference between 300 lb and 1,000+ lb per descent for large aircraft is 10,000–15,000 lb total, which is not negligible.
- Distance = V_TAS_avg × time (significant: a descent from 40,000 ft to 5,000 ft at 2,000 ft/min covers ~135 nmi)

Returns: fuel_burned_lb, distance_nm, time_hr.

### 3. `simulate_mission2_sampling(ac, cal, payload_lb=52_000, distance_nm=4_200, n_altitude_steps=20)`

Top-level Mission 2 simulator. Algorithm:

```
1. Fleet sizing (GV, P-8 can't carry 52,000 lb)
2. Fuel budget: total_fuel, reserve_fuel, mission_fuel
3. Initialize: W = OEW + payload + total_fuel, fuel_remaining = mission_fuel, distance_covered = 0
4. cycle_results = []
5. While fuel_remaining > 0 and distance_covered < distance_nm:
     a. climb_result = climb_segment(W, h_low, h_ceiling, ...)
     b. ceiling = climb_result.ceiling_ft
     c. descent_result = descend_segment(W - climb_fuel, ceiling, h_low, ...)
     d. Update: W -= (climb_fuel + descent_fuel), fuel_remaining -= same, distance_covered += distances
     e. Record cycle: {cycle_num, ceiling_ft, fuel_burned, distance, start_weight, end_weight}
     f. If distance_covered >= distance_nm after climb but before descent, handle partial cycle
6. feasible = distance_covered >= distance_nm and fuel_remaining >= 0
7. Return mission result dict
```

### 4. Update `run_missions.py`

Add `run_mission2()` function parallel to `run_mission1()`, with:
- Per-aircraft detailed output (weight breakdown, cycle summary, altitude progression)
- Summary table across all aircraft
- Altitude vs. distance profile data for plotting

## Existing Building Blocks to Reuse

| Function | Use in Mission 2 |
|---|---|
| `compute_reserve_fuel()` | Explicit reserve calculation — direct reuse |
| `cruise_conditions()` | Drag, L/D, TSFC at each altitude step during climb |
| `propulsion.thrust_available_cruise()` | Available thrust at each altitude during climb |
| `propulsion.tsfc()` | Fuel consumption rate at each altitude |
| `atmosphere.*` | ISA properties at all altitudes |
| `_find_fuel_at_distance()` | Could reuse for partial-cycle handling at mission end |
| Fleet sizing logic from Mission 1 | Same pattern for GV/P-8 |

## What Does NOT Need to Be Built

- **No new calibration.** Same calibrated parameters (CD0, e, k_adj) used as Mission 1.
- **No new drag model.** Existing parabolic polar with calibrated parameters.
- **No engine-out.** Mission 2 is all-engines throughout.
- **No f_oh computation.** Explicitly excluded by the reconciliation decision.

## Parameters and Assumptions

| Parameter | Value | Rationale |
|---|---|---|
| Low altitude (cycle bottom) | 5,000 ft | Reviewer guidance: 1,500 ft is for Mission 3 (smoke survey), not Mission 2 (column sampling). 5,000 ft is representative of atmospheric profiling operations — the lowest altitudes are sampled on initial descent and final approach, not every cycle. Higher bottom altitude also conserves fuel and increases cycle count. |
| Climb Mach | cruise_mach × 0.95 | Standard transport climb approximation |
| Descent rate | 2,000 ft/min | Typical transport idle descent |
| Descent fuel burn | Scaled to aircraft size | `idle_fraction × cruise_fuel_flow × descent_time` with idle_fraction ≈ 0.10–0.15. Per reviewer: fixed 300 lb is too low for large aircraft (A330, 777) where idle flow is 1,000–2,000 lb per descent. Over 8–12 cycles this compounds to 10,000–15,000 lb. |
| Ceiling criterion | ROC < 100 ft/min | Standard service ceiling definition |
| Altitude integration step | 1,000 ft | Balance between accuracy and speed |
| Distance goal | 4,200 nmi | Route NZCH→SCCI |

## Expected Results (Pre-Analysis Intuition)

- **DC-8:** At 52,000 lb payload (max payload), fuel is constrained. Initial ceiling probably 35,000–37,000 ft, rising as fuel burns off. The 4-engine configuration provides better climb capability. Should complete 4,200 nmi but with limited margin.
- **767-200ER:** Can carry 52,000 lb with substantial fuel. Should reach higher altitudes as it gets lighter. Likely completes mission.
- **777-200LR:** Massive fuel capacity but very heavy — initial ceiling may be lower than the 767's despite more thrust, because of the much higher weight. Will burn a lot more fuel per cycle.
- **GV:** Max payload 5,750 lb → needs 10 aircraft. Reaches very high altitudes (natural ceiling 51,000 ft), but the fleet coordination is operationally impractical.
- **P-8:** Max payload ~23,885 lb → needs 3 aircraft. Limited ceiling due to 737-derived airframe.
- **A330:** Can carry payload but calibration quality is low. Results will be flagged accordingly.

The scientists' top priority is "flying higher" — this mission directly tests which aircraft can reach the highest sampling altitudes. The GV excels at altitude but fails on payload. The 767 is likely the best combination of ceiling + payload + fuel.

## Reviewer Feedback (Incorporated)

Two substantive items from the reviewer have been incorporated into this plan:

1. **Cycle bottom altitude raised from 1,500 ft to 5,000 ft.** The 1,500 ft figure applies to Mission 3 (low-altitude smoke survey), not Mission 2. For vertical atmospheric column sampling, a higher bottom (~5,000 ft) is more operationally representative, conserves fuel, and increases the achievable number of sampling cycles. The lowest altitudes are sampled during initial descent and final approach, not on every cycle.

2. **Descent fuel model scaled to aircraft size.** The fixed 300 lb per descent (from Mission 1's simple descent credit) is inadequate for Mission 2, where descent is ~50% of every cycle and compounds over 8–12 cycles. Descent fuel is now computed as `idle_fraction × cruise_fuel_flow × descent_time`, which properly accounts for larger aircraft having higher idle fuel flows (1,000–2,000 lb per descent for A330/777 vs. 300 lb for GV).

## Risk Areas

1. **Climb fuel integration accuracy.** The 1,000 ft step size should be adequate, but worth checking sensitivity.
2. **Calibrated CD0 affecting climb ceiling.** The same unphysical CD0 values (P-8, A330, 777) that caused engine-out issues will reduce climb performance. With all engines, thrust margins are larger, so the effect is moderated — but ceiling predictions for these aircraft should still be flagged as lower confidence.
3. **Descent distance is a major fraction of total mission distance.** A descent from 40,000 ft to 5,000 ft at 2,000 ft/min at Mach 0.80 covers ~135 nmi. Over 8–12 cycles, 1,000–1,600 nmi of the 4,200 nmi budget is consumed during descents alone. Climb distances are similar. Accurate horizontal distance tracking in both climb and descent is essential.

## Deliverables

1. Mission 2 results for all 6 aircraft
2. Altitude-vs-distance sawtooth profile plots
3. Progressive ceiling table (ceiling at cycle 1, 2, 3, ...)
4. Weight breakdown and fuel cost comparison
5. Report for reviewer (PHASE2_MISSION2_REPORT.md)
