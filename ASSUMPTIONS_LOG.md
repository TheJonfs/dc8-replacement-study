# Assumptions Log

This document records every significant modeling assumption, simplification, and data choice made during the study. Each entry includes the rationale and an assessment of the impact on results. This is intended to enable a domain expert to understand where our analysis departs from higher-fidelity methods (e.g., NASA FLOPS) and to judge the reliability of our conclusions accordingly.

---

## Notation
- **Impact: Low** — Unlikely to change relative aircraft rankings or absolute results by more than a few percent
- **Impact: Medium** — Could affect absolute numbers by 5-15% but relative rankings likely preserved
- **Impact: High** — Could meaningfully affect both absolute numbers and potentially relative rankings

---

## A. Atmospheric Modeling

### A1. International Standard Atmosphere (ISA)
**Assumption:** All performance calculations use ISA conditions (sea level: 15°C, 1013.25 hPa). No hot-day, cold-day, or non-standard atmosphere modeling.

**Rationale:** ISA is the standard basis for aircraft performance comparison. Published range-payload data is referenced to ISA. Using ISA ensures our calibration conditions match the data we're calibrating against.

**Impact: Low.** All aircraft are compared under the same conditions, so relative rankings are unaffected. Real-world performance would vary with actual atmospheric conditions, but this is standard practice.

### A2. No Wind Modeling
**Assumption:** All missions assume zero wind (no headwind, tailwind, or crosswind).

**Rationale:** Wind conditions are route-specific and time-dependent. The original study likely also used still-air conditions for comparison purposes (standard practice for aircraft performance analysis).

**Impact: Low** for comparative purposes (all aircraft face same conditions). Could be **Medium** for absolute feasibility of marginal missions (e.g., Mission 1 with headwind could fail for some aircraft that barely succeed in still air).

---

## B. Aerodynamic Modeling

### B1. Parabolic Drag Polar
**Assumption:** Aircraft drag is modeled as CD = CD0 + K·CL², where K = 1/(π·AR·e). This is the standard "clean configuration" parabolic drag polar.

**Rationale:** This is the standard conceptual design approximation. It captures the two dominant drag components (parasite drag and lift-induced drag) and is sufficient for cruise performance estimation.

**What we miss:**
- Compressibility drag rise near the drag-divergence Mach number
- Reynolds number effects with altitude
- Configuration-dependent drag (flaps, slats, gear)
- Trim drag
- Interference drag details

**Mitigation:** We calibrate CD0 and e against published range-payload data, so the effective drag polar absorbs some of these effects at cruise conditions.

**Impact: Low** for cruise performance (calibrated out). **Medium** for off-design conditions (low altitude in Mission 3, climb/descent in Mission 2) where the drag polar may be less representative.

### B2. Oswald Efficiency Factor Estimation
**Assumption:** Oswald efficiency factor (e) is treated as a calibration parameter, initialized from empirical correlations for transport aircraft (typically 0.75-0.85) and adjusted to match range-payload data.

**Rationale:** Oswald efficiency is not published for these aircraft. It depends on detailed wing design, fuselage interference, and other factors. Calibrating it against known performance is the standard approach when detailed aerodynamic data is unavailable.

**Impact: Low** in cruise (calibrated). The calibrated value lumps together all lift-dependent drag effects, which is acceptable for cruise but may be less accurate for flight conditions far from the calibration point.

### B3. No Compressibility Drag Rise Model
**Assumption:** We do not model the transonic drag rise that occurs as aircraft approach their drag-divergence Mach number (typically Mdd ≈ Mcruise + 0.02 to 0.05).

**Rationale:** Modeling compressibility drag requires knowledge of the wing's critical Mach number and drag rise characteristics, which are proprietary. Since we operate near or at design cruise Mach, and the drag polar is calibrated at cruise conditions, this effect is partially absorbed into the calibrated CD0.

**What we miss:** If an aircraft is forced to fly faster or slower than its design Mach (e.g., in Mission 1 engine-out where speed changes), the drag model may be less accurate.

**Impact: Low** for normal cruise. **Medium** for off-design speed conditions.

### B4. Engine-Out Asymmetric Drag Increment
**Assumption:** Single engine failure adds a drag increment of approximately 10% to the total aircraft drag. This accounts for: rudder deflection to counteract yaw, slight sideslip angle, windmilling drag of the failed engine.

**Rationale:** Published literature cites engine-out drag increments in the range of 5-20% depending on aircraft configuration. 10% is a mid-range estimate. The actual value depends on engine location (wing-mounted vs. fuselage-mounted), rudder authority, and speed.

**What we miss:** The drag increment varies with speed and should be higher at low speeds. For twin-engine aircraft, the yaw moment from losing one engine is larger (engines further from centerline on many designs, and 50% vs 25% thrust loss), potentially making the drag increment proportionally larger.

**Mitigation:** We will run sensitivity analysis at 5% and 15% to bound the effect.

**Impact: Medium.** This directly affects Mission 1 engine-out feasibility and fuel burn. However, it affects all aircraft similarly (as a percentage), so relative rankings may be less sensitive than absolute fuel numbers.

---

## C. Propulsion Modeling

### C1. Simplified TSFC Model
**Assumption:** Thrust-specific fuel consumption is modeled as:
TSFC(h, M) = TSFC_ref × f(h) × g(M)
where f(h) captures altitude variation and g(M) captures Mach variation. The reference TSFC is a published or estimated cruise value.

**Rationale:** Real engine performance is described by complex "engine decks" that are proprietary. Our simplified model captures the two dominant trends: TSFC improves with altitude (up to the tropopause) due to lower ambient temperature improving thermal efficiency, and TSFC increases with Mach number.

**What we miss:**
- Throttle setting effects (TSFC varies with thrust level)
- Detailed inlet recovery effects
- Engine deterioration with age
- Bleed air extraction effects
- The specific shape of the TSFC map for each engine

**Mitigation:** The reference TSFC is adjusted during calibration to match range-payload data, so cruise conditions are reasonably well-captured.

**Impact: Medium.** This is our single largest source of uncertainty. TSFC directly multiplies into fuel burn. Errors of 5-10% in TSFC translate directly to 5-10% errors in fuel burn. However, since we calibrate against range-payload data, cruise TSFC is constrained. Off-design TSFC (low altitude, off-optimum thrust) carries more uncertainty.

### C2. Engine-Out Thrust Assumptions
**Assumption:** When one engine fails, the remaining engines operate at maximum continuous thrust (MCT). For twin-engine aircraft, this is 100% of one engine's max continuous rating. For quad-engine aircraft (DC-8), this is 100% of three engines' max continuous rating.

**Rationale:** Standard operating procedure after engine failure is to advance remaining engines to MCT. MCT is slightly below maximum takeoff thrust and can be sustained indefinitely.

**Impact: Low.** This is standard practice and well-defined.

### C3. Two-Regime Thrust Lapse Model
**Assumption:** Available thrust lapse with altitude uses two regimes:
- Below tropopause (≤36,089 ft): `T = T_SLS × (ρ/ρ₀)^0.75` (standard high-bypass turbofan model)
- Above tropopause (>36,089 ft): `T = T_trop × (ρ/ρ_trop)^2.0` (steeper lapse)

The two regimes are continuous at the tropopause by construction.

**Rationale:** The original single-regime model (`σ^0.75` everywhere) overpredicted thrust above the tropopause, causing all aircraft to reach their published service ceiling on every Mission 2 climb cycle regardless of weight. This prevented the progressive ceiling increase that is the core scientific metric of Mission 2.

In reality, high-bypass turbofan engines lose thrust faster in the isothermal stratosphere than the simple density-ratio model predicts. Above the tropopause, compressor efficiency degrades at very low inlet density, the engine may operate near maximum RPM limits, and bleed/accessory power becomes a larger fraction of available thrust.

The steeper exponent (2.0) was selected to produce physically plausible weight-dependent ceilings: at MTOW, the thrust-limited ceiling is below the published service ceiling, and as fuel burns off, the ceiling rises toward the published limit. The published service ceiling remains as a hard structural/pressurization cap.

**Validation:** At light operating weights (OEW + minimal payload + reserves), the model ceiling approximately matches or slightly exceeds the published ceiling for aircraft with physical calibrations (767-200ER, GV), which is the expected behavior since published ceilings are demonstrated at typical operating weights.

**Impact: Low** for calibration (verified: all calibration RMS errors unchanged, because thrust is used only as a go/no-go viability check in the altitude optimizer, and thrust still exceeds drag at all calibration-relevant cruise altitudes). **Medium** for Mission 2 ceiling progression (this is the primary intended effect). **Low** for Mission 1 (slight reduction in engine-out cruise altitude at the highest altitudes, resulting in ~5% change in range surplus for the 767-200ER — 1,134 nm vs. 1,202 nm previously).

---

## D. Performance Modeling

### D1. Breguet Range Equation as Baseline
**Assumption:** Cruise range is computed using the Breguet range equation, which assumes constant altitude, constant Mach number, and continuous weight decrease as fuel burns.

**Rationale:** Breguet is the standard analytical tool for cruise range estimation. It gives a closed-form solution that is within ~2% of a full trajectory integration for typical cruise profiles.

**Refinement:** We implement step-cruise (dividing the mission into segments and recomputing conditions at each step) to account for altitude changes as the aircraft gets lighter.

**Impact: Low** for cruise missions (well-established method). **Medium** for missions with significant non-cruise segments.

### D2. Step-Cruise Altitude Profile
**Assumption:** Aircraft fly a step-cruise profile, climbing in discrete altitude steps as weight decreases. We optimize altitude at each step for best specific range.

**Rationale:** Real transport aircraft fly step-climbs (ATC typically allows 2,000 ft or 4,000 ft steps). A continuously optimized altitude profile slightly overestimates performance vs. realistic step-climbs, but the difference is small (~1-2%).

**Impact: Low.**

### D3. Climb and Descent Fuel Estimation
**Assumption:** For Mission 2's repeated climb-descend segments, we model climb fuel burn using an energy method: fuel consumed = (change in potential energy + change in kinetic energy + drag work) / (engine efficiency × fuel energy density). Descents are modeled at near-idle thrust with excess energy recovered as distance.

**Rationale:** Full point-performance trajectory integration would require detailed engine thrust-available-vs-altitude curves that we don't have. The energy method captures the dominant physics (lifting the aircraft against gravity costs energy) without requiring detailed climb schedules.

**What we miss:** Optimal climb speed scheduling, exact engine thrust lapse with altitude, specific excess power details.

**Impact: Medium.** Mission 2 results are the most sensitive to this assumption, as the entire mission consists of climb-descend cycles. Absolute fuel numbers may be off by 10-20%, but relative comparisons between aircraft should be more reliable.

### D4. Reserve Fuel Policy
**Assumption:** Standard reserves defined as: 5% of trip fuel + fuel for 200 nmi alternate at cruise conditions + 30 minutes hold fuel at 1,500 ft.

**Rationale:** This approximates FAR Part 121 requirements for international operations. The actual NASA ASP reserve policy may differ, but this is a reasonable and conservative baseline for comparative purposes. The key requirement is that all aircraft are evaluated against the same standard.

**Note:** If the original study used a different reserve policy, our absolute feasibility determinations could differ. The comparative rankings should be unaffected since all aircraft face the same reserve requirement.

**Impact: Low** for comparative rankings. Could be **Medium** for marginal go/no-go determinations.

---

## E. Aircraft Data

### E1. Published Specifications as Ground Truth
**Assumption:** Manufacturer-published specifications (MTOW, OEW, fuel capacity, range) are used as ground truth for calibration.

**Rationale:** These are the best publicly available data. They represent certified, demonstrated performance.

**Caveat:** Published OEW may differ from airline-specific configurations. Published range values may use optimistic assumptions (e.g., long-range cruise Mach, optimum altitude, standard reserves). Our calibration procedure accounts for this by adjusting model parameters to match the published data, effectively adopting whatever assumptions are embedded in the published values.

**Impact: Low** for aircraft where good published data exists. **Medium** for the P-8, where we derive performance from the 737-900ER with modifications.

### E2. P-8 Derivation from 737-900ER
**Assumption:** The P-8 model is created by modifying a calibrated 737-900ER model: reducing OEW by 7,500 lb (furnishing removal), increasing fuel capacity to 73,320 lb, adjusting MTOW/ramp weight, and modestly improving Oswald efficiency (~0.02-0.03) for raked wingtips.

**Rationale:** Per the problem statement. The P-8's detailed performance data is not publicly available, so derivation from the base airframe is the only feasible approach.

**Impact: Medium.** The P-8 model inherits any errors in the 737-900ER model and adds uncertainty from the modification assumptions (especially the raked wingtip drag improvement and the additional fuel tank weight/drag effects).

---

### E3. Non-Cruise Fuel Overhead Model
**Assumption:** Non-cruise fuel (taxi, takeoff, climb, descent, approach, and reserves) is modeled as a fraction of takeoff weight: `F_overhead = f_oh × W_tow`. The parameter f_oh is calibrated per aircraft alongside the aerodynamic parameters.

**Rationale:** Published range-payload data represents mission range including standard reserves and non-cruise phases. The Breguet range equation models only the cruise segment, so a separate model is needed for non-cruise fuel. The fractional-TOW model captures the physical reality that heavier aircraft burn proportionally more fuel during non-cruise phases (heavier means higher climb fuel, higher reserve fuel, etc.).

**Key insight:** Without this overhead model, a Breguet-based model cannot match the shape of published range-payload diagrams. At max payload (high TOW, low fuel), the overhead fraction of available fuel is much larger than at lighter payload conditions, which is the primary driver of the steep range reduction at high payload.

**What we miss:**
- Separate modeling of individual non-cruise phases (taxi, climb, descent, reserves)
- Route-specific effects (different climb profiles for different mission lengths)
- Weight-dependent reserve policies
- The individual calibrated parameters (CD0, e, k_adj) should not be interpreted as physically accurate values — they are effective values that work in combination with f_oh to reproduce the correct range-payload behavior

**Calibration results across aircraft:**
- f_oh ranges from ~0.06 (737-900ER) to ~0.26 (DC-8)
- The wide variation partly reflects different operational assumptions in the published data
- Individual aerodynamic parameters may be outside typical physical ranges because they compensate for the simplified overhead model

**Impact: Medium.** The overhead model introduces correlation between calibration parameters, making individual parameters less physically interpretable. However, the combined model matches published range-payload data typically within 1-5% RMS error, which is excellent for a simplified approach. For mission analysis, the calibrated model applies the same overhead consistently, so relative comparisons between aircraft remain valid.

## F. Mission-Specific Assumptions

### F1. Mission 3 Low-Altitude Speed
**Assumption:** All aircraft fly at 250 KTAS (Mach ≈ 0.38 at 1,500 ft) during Mission 3. This is a single speed for all aircraft types.

**Rationale:** At 1,500 ft, the air density is ~96% of sea level. Flying at normal cruise Mach (0.75–0.85) would produce TAS of 500–530 KTAS, which exceeds VMO for all study aircraft (~340–365 KCAS). A realistic low-altitude cruise speed is 250–300 KTAS. We use 250 KTAS as a conservative choice that is below all VMO limits and consistent with the hold speed assumption in the reserve fuel model.

**What we miss:**
- Aircraft-specific optimal endurance speeds (each aircraft has a different L/D profile vs. speed)
- Speed variations during the survey pattern (turns, course changes)
- The actual survey speed would depend on instrument requirements

**Impact: Medium.** Speed affects both fuel burn rate and distance covered. At 250 KTAS, the drag is dominated by CD0 (parasite drag) because CL is low in dense air. A faster speed would increase parasite drag quadratically while barely changing induced drag. All aircraft are compared at the same speed, so relative rankings are preserved.

### F2. Negligible Climb/Descent to Mission Altitude
**Assumption:** Climb from the departure airport to 1,500 ft AGL and descent back are ignored. All mission fuel is allocated to low-altitude endurance.

**Rationale:** 1,500 ft is essentially traffic pattern altitude. Climbing to 1,500 ft consumes ~50–100 lb of fuel and takes under 1 minute — negligible compared to 8 hours of endurance burning thousands of pounds per hour.

**Impact: Low.** The fuel consumed climbing to 1,500 ft is <0.1% of mission fuel for all aircraft.

---

## G. Cost Assumptions

### G1. Fuel Price
**Assumption:** Jet-A fuel cost of $5.50 per gallon (approximately $0.82 per pound, using Jet-A density of 6.7 lb/gal).

**Rationale:** This is a mid-range estimate for Jet-A fuel pricing. The exact value affects absolute costs but not relative comparisons between aircraft.

**Impact: Low** for relative comparisons (linear scaling). Absolute cost numbers will scale proportionally with actual fuel price.

---

*This document will be updated as additional assumptions are made during the study.*
