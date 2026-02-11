# Phase 2: Mission 3 — Low-Altitude Smoke Survey

## Mission Definition

| Parameter | Value |
|---|---|
| Region | Central United States (Arkansas-Missouri area) |
| Duration | 8 hours |
| Payload | 30,000 lb |
| Altitude | 1,500 ft AGL |
| Speed | 250 KTAS (Mach 0.38) |
| Profile | Extended low-altitude endurance for forest fire particulate sampling |
| Fuel budget | Explicit reserves only (no f_oh) — per PHASE2_STEP1_RECONCILIATION.md |
| Fuel loading | Mission-sized (iterative sizing for 8 hr + reserves) — see ASSUMPTIONS_LOG.md F3 |

## Summary of Results

### Assessed Outcomes

| Aircraft | Status | Confidence | n_ac | Fuel Loaded (lb) | Fuel Burned (lb) | Avg FF (lb/hr) | Cost | $/klb·nm | Notes |
|---|---|---|---|---|---|---|---|---|---|
| **DC-8** | **PASS** | **Low** | 1 | 44,496 | 36,233 | 4,529 | $36,527 | $0.61 | Burn rate artificially low (k_adj=0.605); cheapest but unreliable |
| **767-200ER** | **PASS** | **High** | 1 | 96,124 | 78,921 | 9,865 | $78,907 | $1.32 | Best single-aircraft solution; realistic burn rate |
| P-8 | PASS | Low | 2 | 37,321 ea | 30,244 ea | 3,780 ea | $61,273† | $1.02† | Cheapest fleet aggregate; CD0=0.060 distorts burn rate |
| GV | PASS | Medium | 6 | 23,393 ea | 18,938 ea | 2,367 ea | $115,218† | $1.92† | 6-aircraft fleet; lowest per-aircraft burn but fleet impractical |
| A330-200 | PASS | Low | 1 | 166,342 | 133,649 | 16,706 | $136,549 | $2.28 | Highest burn rate; CD0=0.033 distorts drag |
| 777-200LR | PASS | Low | 1 | 128,747 | 102,996 | 12,874 | $105,688 | $1.76 | Mission-sized fuel dramatically reduces cost vs. max-fuel loading |

†Fleet aggregate

### Key Takeaways

**All six aircraft pass Mission 3.** This is the least discriminating mission: 30,000 lb payload is moderate, 8 hours of endurance is well within all aircraft's fuel capacity, and there is no engine-out condition or altitude challenge. The differentiator is cost efficiency.

**Mission-sized fuel loading is critical to fair comparison.** This mission is time-constrained (8 hours), not range-constrained. Loading maximum fuel — as was done in the initial analysis — inflated costs for aircraft with large tanks (especially the 777, which would load 325,300 lb but burn only ~103,000 lb). With iterative mission-sized fuel loading, each aircraft loads only enough fuel for the 8-hour endurance plus reserves plus a 5% margin. This changed the rankings dramatically: the 777 dropped from $4.45/klb·nm (most expensive) to $1.76/klb·nm (mid-pack). See ASSUMPTIONS_LOG.md entry F3.

**The DC-8 appears cheapest but the result is unreliable.** At $0.61/klb·nm and 4,529 lb/hr average fuel flow, the DC-8 looks like the clear winner. However, this is a direct consequence of k_adj=0.605 — the calibrated TSFC is ~40% below the reference value, producing artificially low fuel burn. Published DC-8 cruise fuel flow is ~10,000–13,000 lb/hr. The DC-8's real Mission 3 cost would likely be 2–3× higher than modeled.

**The 767-200ER is the best single-aircraft solution with reliable numbers.** At $1.32/klb·nm and 9,865 lb/hr, the 767 has trustworthy absolute numbers. Its calibration is the most physically grounded (CD0=0.018, k_adj=0.951, RMS 0.0%), making it the most reliable result in the study.

**The P-8 fleet (2 aircraft) is the cheapest aggregate at $1.02/klb·nm**, but this is distorted by the unphysical CD0=0.060 which inflates drag. The P-8's real fuel burn would likely be lower than modeled, which would make it even cheaper — but the absolute numbers should not be trusted.

**Large aircraft benefit from mission-sized fuel loading.** The 777 and A330 are the biggest beneficiaries: with max fuel, the 777 was the most expensive option ($4.45/klb·nm); with mission-sized fuel, it drops to $1.76/klb·nm. The A330 drops from $3.25 to $2.28. These aircraft have the largest fuel tanks and therefore gained the most from not filling them unnecessarily.

## Detailed Observations

### Low-Altitude Aerodynamics

At 1,500 ft and 250 KTAS, the aerodynamic conditions are very different from cruise. Note that with mission-sized fuel loading, the takeoff weights — and therefore CL values — are lower than they would be at max fuel:

| Aircraft | TOW (lb) | CL | CD | L/D | CD0 (cal) | CD0/CD ratio |
|---|---|---|---|---|---|---|
| DC-8 | 231,496 | 0.399 | 0.023 | 17.6 | 0.0141 | 62% |
| GV | 76,593 | 0.333 | 0.021 | 15.8 | 0.0150 | 71% |
| P-8 | 143,316 | 0.527 | 0.071 | 7.4 | 0.0597 | 84% |
| 767-200ER | 305,204 | 0.494 | 0.032 | 15.6 | 0.0177 | 56% |
| A330-200 | 462,242 | 0.587 | 0.038 | 15.3 | 0.0334 | 87% |
| 777-200LR | 478,747 | 0.503 | 0.047 | 10.6 | 0.0410 | 87% |

**Key observations:**
- **CD0 dominates for aircraft with unphysical calibrations.** For the P-8, A330, and 777, CD0 accounts for 84–87% of total drag. Their fuel burn is driven almost entirely by the calibrated CD0, not by the payload or mission profile.
- **The 767's drag breakdown is the most physical.** CD0 accounts for only 56% of total drag, with induced drag (from CL=0.494) contributing the rest. This is consistent with a transport aircraft at low altitude.
- **The DC-8's L/D of 17.6 is unrealistically high** for low-altitude flight. This is driven by CD0=0.0141, which is too low for a 4-engine transport. Real L/D would be ~12–16.
- **Mission-sized fuel reduces CL values** compared to max-fuel loading, which reduces induced drag. This partially explains why the fuel savings from lighter loading are slightly better than linear — less weight means less drag, which means less fuel burn per hour.

### Individual Aircraft

**DC-8** — PASS, $36,527, 4,529 lb/hr.
- Loads 44,496 lb of fuel (of 147,255 lb max capacity — only 30% of tank).
- Burns 36,233 lb in 8 hours, covering ~2,000 nm.
- **Low-confidence.** The burn rate is ~40% below reality due to k_adj=0.605. If corrected to k_adj≈1.0, the burn rate would be ~7,500 lb/hr, fuel loaded would be ~73,000 lb, and cost would rise to ~$1.0/klb·nm. The DC-8 would still pass easily but at ~2× the modeled cost.

**767-200ER** — PASS, $78,907, 9,865 lb/hr. **Best single-aircraft solution.**
- Loads 96,124 lb of fuel (of 162,000 lb max capacity — 59% of tank).
- Burns 78,921 lb in 8 hours, covering ~2,000 nm.
- **High-confidence result.** CD0=0.018 is physical, k_adj=0.951 is near unity, and the L/D=15.6 at low altitude is realistic for a clean transport aircraft.

**P-8** — PASS (2 aircraft), $61,273 fleet, 3,780 lb/hr per aircraft.
- Each aircraft loads 37,321 lb of fuel (of 73,320 lb max — 51% of tank).
- Each burns 30,244 lb in 8 hours.
- **Low-confidence.** CD0=0.060 is the highest in the study, driving an L/D of only 7.4 at low altitude. Real P-8 drag would be much lower (CD0 ~0.020–0.025), so real fuel burn would be lower and cost would improve.
- Despite the inflated drag, the P-8 fleet is the cheapest aggregate option ($1.02/klb·nm), confirming the P-8 is genuinely competitive for this mission.

**GV** — PASS (6 aircraft), $115,218 fleet, 2,367 lb/hr per aircraft.
- Each aircraft loads 23,393 lb of fuel (of 41,300 lb max — 57% of tank).
- Each burns 18,938 lb in 8 hours.
- **Medium confidence.** The GV's calibration is reasonable (CD0=0.015 physical).
- 6-aircraft fleet is operationally impractical. At $1.92/klb·nm, it's mid-range on cost.
- The GV's strengths (high altitude, long range) are irrelevant for this mission.

**A330-200** — PASS, $136,549, 16,706 lb/hr.
- Loads 166,342 lb of fuel (of 245,264 lb max — 68% of tank).
- Burns 133,649 lb in 8 hours.
- Highest burn rate of all aircraft — 69% more than the 767 for the same payload.
- **Low-confidence.** CD0=0.033 and e=2.165 are both unphysical.
- The A330 is oversized for this mission (30,000 lb is well below its max payload of 108,908 lb).

**777-200LR** — PASS, $105,688, 12,874 lb/hr.
- Loads 128,747 lb of fuel (of 325,300 lb max — only 40% of tank).
- Burns 102,996 lb in 8 hours.
- **Low-confidence.** CD0=0.041 is unphysical.
- With mission-sized fuel loading, the 777 drops from the most expensive ($4.45/klb·nm with max fuel) to mid-range ($1.76/klb·nm). This demonstrates how much the max-fuel approach distorted the comparison — the 777 was penalized for having a large fuel tank, not for being fuel-inefficient.

## Methodology

### Time-Stepping Endurance Model

The mission is duration-based (8 hours) rather than distance-based. The model uses a time-stepping approach:

1. Compute Mach number for 250 KTAS at 1,500 ft: Mach ≈ 0.38
2. Divide 8 hours into 40 time steps (dt = 0.2 hr)
3. At each step:
   - Compute `cruise_conditions()` at current weight, h=1,500 ft, Mach=0.38
   - Fuel burn = drag × TSFC × dt
   - Distance = V_ktas × dt
   - Update weight
4. If fuel runs out before 8 hours → FAIL (none did)

This is simpler than the Breguet-based range computation because speed is fixed and altitude is fixed. The weight decrease as fuel burns off reduces drag slightly, improving efficiency over time.

### Iterative Mission-Sized Fuel Loading

Unlike Missions 1 and 2 (which are range-constrained and need maximum fuel), Mission 3 is time-constrained. Loading maximum fuel would inflate costs without operational benefit. The aircraft loads only enough fuel to complete the 8-hour endurance plus reserves.

The fuel load is computed iteratively because fuel weight affects drag, which affects burn rate:

1. **Initial estimate:** Compute burn rate at empty weight (OEW + payload, no fuel) → lower bound on fuel flow. Multiply by duration × 1.05 (5% margin).
2. **Iterate:**
   - Add reserve fuel to the mission fuel estimate → total fuel candidate
   - Cap at maximum fuel capacity
   - Simulate the 8-hour endurance at this fuel load → actual burn
   - If feasible: tighten estimate to actual burn × 1.05
   - If not feasible: scale up proportionally (duration / achieved endurance × margin)
3. **Converge** when successive total fuel values stabilize within 50 lb.
4. **Fallback:** If iteration does not converge in 20 rounds, use maximum fuel capacity.

All six aircraft converged within ~5–8 iterations. The 5% margin ensures a small operational buffer beyond the theoretical minimum.

### Fuel Budget (Explicit Reserves, No f_oh)

Per the Phase 2 reconciliation decision, Mission 3 does not use the f_oh overhead fraction:

```
reserve_fuel = compute_reserve_fuel(total_fuel, ac, CD0, e, k_adj)
mission_fuel = total_fuel - reserve_fuel
```

Reserves: 5% contingency + 200 nm alternate + 30 min hold at 1,500 ft.

### Fleet Sizing

Aircraft that cannot carry 30,000 lb payload are modeled as a fleet:
- GV: max payload 5,800 lb → 6 aircraft, 5,000 lb each
- P-8: max payload 23,885 lb → 2 aircraft, 15,000 lb each

### Fuel Cost

Cost is computed on total fuel loaded (fuel loaded must be purchased, regardless of what is burned). For the $/klb·nm metric, the denominator uses actual distance covered (~2,000 nm at 250 KTAS for 8 hours).

### Low-Altitude Speed

All aircraft fly at 250 KTAS (Mach ≈ 0.38 at 1,500 ft). This is below VMO for all study aircraft and consistent with the hold speed in the reserve fuel model. See ASSUMPTIONS_LOG.md entry F1.

## Key Modeling Choices and Limitations

### Choices

1. **Mission-sized fuel loading.** The most important modeling choice. For time-constrained missions, loading only the required fuel plus reserves produces a fair comparison. Without this, large-tanked aircraft (777, A330) are penalized for having capacity they don't need. See ASSUMPTIONS_LOG.md entry F3.

2. **Fixed speed (250 KTAS).** A single speed for all aircraft simplifies comparison. In reality, each aircraft has a different optimal endurance speed. The effect on relative rankings is small because all aircraft share the same speed assumption.

3. **No climb/descent modeling.** At 1,500 ft, climb fuel is negligible (~50–100 lb). See ASSUMPTIONS_LOG.md entry F2.

4. **No wind effects.** Still-air assumption, same as Missions 1 and 2.

5. **No survey pattern modeling.** The mission assumes straight-and-level flight. Real smoke surveys involve track patterns with turns, which would increase fuel burn slightly.

### Limitations

1. **DC-8 fuel burn is ~40% low.** The k_adj=0.605 calibration directly scales cruise TSFC. At low altitude where TSFC is already higher than cruise, the underestimate is even more pronounced. DC-8 absolute numbers should be approximately doubled for reality.

2. **Unphysical CD0 dominates drag for P-8, A330, 777.** At low altitude, CD0 drives 84–87% of total drag for these aircraft. Their fuel burn numbers are unreliable in absolute terms, though relative ordering (A330 > 777 > P-8) may be preserved since the inflated CD0 tracks with wing area.

3. **All aircraft fly at the same speed.** In reality, optimal endurance speed varies by aircraft. Lighter aircraft (GV) would fly slower for best endurance; heavier aircraft might fly slightly faster. The equal-speed assumption slightly disadvantages lighter aircraft and slightly advantages heavier ones.

## Confidence Assessment

| Aircraft | Confidence | Notes |
|---|---|---|
| 767-200ER | **High** | CD0=0.018, k_adj=0.951. L/D=15.6 and 9,865 lb/hr burn rate are realistic. |
| GV | **Medium** | CD0=0.015 physical. Per-aircraft burn (2,367 lb/hr) plausible. Fleet of 6 impractical. |
| DC-8 | **Low** | k_adj=0.605 → burn rate ~40% too low. Real cost likely 2–3× higher. |
| P-8 | **Low** | CD0=0.060 → burn rate too high. Real cost likely lower (better for P-8). |
| A330-200 | **Low** | CD0=0.033, e=2.165. Drag and burn rate distorted. |
| 777-200LR | **Low** | CD0=0.041. Burn rate distorted. |

## Comparison Across All Three Missions

| Aircraft | Mission 1 | Mission 2 | Mission 3 | Best For |
|---|---|---|---|---|
| **DC-8** | FAIL | PASS | PASS | Cheapest (but low-confidence) |
| **767-200ER** | **PASS** | **PASS** | **PASS** | All-around best; only one with high confidence across all missions |
| 777-200LR | LIKELY PASS | PASS | PASS | Nothing — expensive across all missions |
| GV | FAIL | PASS (9 ac) | PASS (6 ac) | High-altitude capability (Mission 2) |
| A330-200 | UNCERTAIN | PASS (marginal) | PASS | Nothing — calibration too poor to trust |
| P-8 | FAIL | PASS (3 ac) | PASS (2 ac) | Cost-competitive fleet ops (Missions 2, 3) |

**The 767-200ER is the clear overall winner.** It is the only aircraft that:
- Passes all three missions with high model confidence
- Has physically grounded calibration parameters
- Costs less than all competitors per payload-distance unit (except the DC-8, whose numbers are unreliable)

**The P-8 is the strongest fleet competitor.** Despite needing multiple aircraft, the P-8 fleet's aggregate cost is the lowest on Mission 3 ($1.02/klb·nm) and competitive on Mission 2.

## Reproduction

```bash
python3 -m src.analysis.run_missions
```

Runtime: ~15 minutes (dominated by calibration). Prints detailed per-aircraft results and summary tables for all three missions.

## Files Changed

| File | Change |
|---|---|
| `src/models/missions.py` | Added `simulate_mission3_low_altitude()` with iterative fuel sizing and `_run_endurance()` helper |
| `src/analysis/run_missions.py` | Added `run_mission3()`, `_print_mission3_result()`, `_print_mission3_summary()`, updated `__main__` |
| `tests/test_missions.py` | Added 9 tests for Mission 3 including fuel sizing validation (total: 43 mission tests) |
| `ASSUMPTIONS_LOG.md` | Added F1 (low-altitude speed), F2 (negligible climb/descent), F3 (mission-sized fuel loading) |
