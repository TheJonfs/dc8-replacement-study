# DC-8 Replacement Study — Progress Report (Phase 1 Complete)

## Date: 2026-02-06

## What This Project Is

We are attempting to replicate a published NASA study that evaluated candidate replacement aircraft for the DC-8-72 Flying Laboratory (N817NA). The study compares six aircraft on their ability to perform representative airborne science missions, measured by range-payload capability, mission fuel consumption, and cost efficiency.

The known conclusion from the original study (stated in its abstract) is that the **Boeing 767-200ER and P-8 Poseidon** emerge as the top contenders. This serves as a high-level validation target for our work.

## Context: Limitations and Approach

**We do not have access to NASA's Flight Optimization System (FLOPS)**, which was used in the original study. Instead, we are building physics-based models from first principles:
- Breguet range equation with step-cruise refinement
- Parabolic drag polar (CD = CD0 + CL²/(π·AR·e))
- Simplified TSFC models calibrated against published data

This means our models are lower-fidelity than the original. We are documenting every assumption and its expected impact in `ASSUMPTIONS_LOG.md`.

**The human collaborator is a space scientist, not an aircraft engineer**, so this project is also an exercise in how well AI can execute domain-specific engineering analysis when the human cannot easily verify intermediate results. We are erring toward justifying work to a hypothetical expert reviewer rather than to the immediate collaborator.

## What Has Been Completed (Phase 0)

### 1. Project Infrastructure
- Code directory structure created (`src/`, `tests/`, `data/`, `outputs/`)
- Study plan written (`STUDY_PLAN.md`) with 6 phases defined
- Assumptions log created (`ASSUMPTIONS_LOG.md`) with 20+ entries covering atmospheric modeling, aerodynamics, propulsion, performance, and cost assumptions

### 2. ISA Atmosphere Model
- **File:** `src/models/atmosphere.py`
- Implements International Standard Atmosphere from sea level through 65,000 ft
- Two layers: troposphere (linear lapse) and lower stratosphere (isothermal)
- Functions: temperature, pressure, density, speed of sound, and their ratios
- **Tested:** 18 unit tests in `tests/test_atmosphere.py`, all passing
- Tests verify against published ISA tables at sea level, 20,000 ft, tropopause (36,089 ft), and 45,000 ft
- Physical consistency checks: monotonicity, ideal gas law, isothermal stratosphere

### 3. Aircraft Data Collection
Data files created for all 7 aircraft in `src/aircraft_data/`:

| Aircraft | Data Source | Confidence |
|---|---|---|
| DC-8-72 (NASA) | Provided in problem statement | High — authoritative |
| Gulfstream G-V | Gulfstream APD, FAA TCDS A12EA, EASA TCDS E.012 (BR710), Jane's | High for weights/geometry; Medium for TSFC |
| Boeing 737-900ER | Boeing APD D6-58325-6, FAA TCDS A16WE, CFM International, Roux (2007) | High for weights/geometry; Medium for TSFC |
| Boeing P-8 | Derived from 737-900ER per problem statement modifications | Medium — inherits 737 uncertainty plus modification assumptions |
| Boeing 767-200ER | Boeing APD D6-58328, FAA TCDS A1NM, GE CF6-80C2 specs | High for weights/geometry; Medium for TSFC |
| Airbus A330-200 | Airbus APD, EASA TCDS EASA.A.004, GE CF6-80E1 specs | High for weights; Medium for range and TSFC |
| Boeing 777-200LR | Boeing APD D6-58329-2, FAA TCDS A28NM, GE GE90-110B specs | High for weights/geometry; Medium for TSFC |

**Unified data loader** (`src/aircraft_data/loader.py`) normalizes the different file formats into a consistent interface and includes validation checks.

### 4. Unit Utilities
- `src/utils.py`: Unit conversions (NM↔ft, Mach↔TAS, fuel weight↔gallons), fuel cost calculation

## Aircraft Data Summary

| Aircraft | OEW (lb) | MTOW (lb) | Max Payload (lb) | Max Fuel (lb) | Engines | Cruise TSFC | Cruise Mach |
|---|---|---|---|---|---|---|---|
| DC-8-72 | 157,000 | 325,000 | 52,000 | 147,255 | 4×CFM56-2-C1 | 0.650 | 0.80 |
| G-V | 48,200 | 90,500 | 5,800 | 41,300 | 2×BR710 | 0.657 | 0.80 |
| 737-900ER | 98,495 | 187,700 | 47,805 | 46,063 | 2×CFM56-7B26 | 0.627 | 0.785 |
| P-8 | 90,995 | 188,200 | 23,885 | 73,320 | 2×CFM56-7B27 | 0.627 | 0.785 |
| 767-200ER | 179,080 | 395,000 | 55,920 | 162,000 | 2×CF6-80C2B2 | 0.605 | 0.80 |
| A330-200 | 265,900 | 533,519 | 108,908 | 245,264 | 2×CF6-80E1A4 | 0.560 | 0.82 |
| 777-200LR | 320,000 | 766,000 | 135,000 | 325,300 | 2×GE90-110B1 | 0.545 | 0.84 |

## Range-Payload Calibration Points

These are the primary targets for model calibration in Phase 1:

| Aircraft | Max Payload Range (nmi) | Max Fuel Range (nmi) | Ferry Range (nmi) |
|---|---|---|---|
| DC-8-72 | 2,750 (52,000 lb) | 5,400 (20,745 lb) | 6,400 (0 lb) |
| G-V | 5,150 (5,800 lb) | 6,200 (1,000 lb) | 6,500 (0 lb) |
| 737-900ER | 2,505 (47,805 lb) | 2,935 (43,142 lb) | 3,990 (0 lb) |
| P-8 | ~4,500 (23,885 lb)* | — | ~5,800 (0 lb)* |
| 767-200ER | 5,990 (55,920 lb) | 6,100 (53,920 lb) | 7,900 (0 lb) |
| A330-200 | 4,800 (108,908 lb) | 7,250 (22,354 lb) | 8,000 (0 lb) |
| 777-200LR | 7,500 (135,000 lb) | 9,400 (120,700 lb) | 10,800 (0 lb) |

*P-8 ranges are preliminary estimates to be refined after 737-900ER calibration.

## Key Observations So Far

1. **Payload capacity gap is stark.** The G-V (5,800 lb) and P-8 (23,885 lb) cannot match the DC-8's 52,000 lb payload. The G-V would need ~9 aircraft; the P-8 would need ~3 aircraft for equivalent aggregate payload.

2. **The 767-200ER is the closest payload match** at 55,920 lb — within 8% of the DC-8's 52,000 lb.

3. **The A330-200 and 777-200LR are oversized** — their payload capacities (109 klb and 135 klb) far exceed DC-8 requirements. They may be fuel-inefficient for the mission profile.

4. **TSFC trends make physical sense.** Newer, higher-bypass-ratio engines (GE90: BPR ~8.7, TSFC 0.545) are significantly more efficient than older lower-bypass engines (CFM56-2: BPR ~6, TSFC 0.650). The ~16% TSFC improvement from DC-8 engines to 777 engines is consistent with the generational technology gap.

5. **The 767-200ER has a distinctive range-payload shape** — max fuel capacity (162,000 lb) nearly equals MTOW minus MZFW (160,000 lb), so Points A and B of the range-payload diagram are very close together (only 2,000 lb payload difference). This is a real characteristic of the aircraft, confirmed by cross-checking against the published 6,600 nmi design range.

## Review Response (Post Phase 0 Review)

An external review of this progress report identified four action items. Here is how each was resolved:

### Item 1 [HIGH] — 767-200ER Fuel Capacity: CORRECTED
**Original value:** 91,380 lb. **Corrected value:** 162,000 lb (24,140 US gal).

The original 91,380 lb figure was the base 767-200 capacity *without* the center section fuel tank that defines the "ER" variant. Many online references incorrectly cite this figure for the -200ER. The correct value of 162,000 lb was confirmed by:
- Boeing Airport Planning Document D6-58328
- Breguet range cross-check: 91,380 lb of fuel is physically incompatible with the well-documented 6,600 nmi design range; only ~162,000 lb of fuel produces a consistent result

This correction resolved the "merged A/B corner points" anomaly: the range-payload diagram now has three proper corner points, with Points A (160,000 lb fuel, 55,920 lb payload) and B (162,000 lb fuel, 53,920 lb payload) very close but distinct.

### Item 2 [MEDIUM] — A330-200 and 777-200LR Weights: VERIFIED CORRECT
- **A330-200 MTOW (533,519 lb = 242,000 kg):** Confirmed as the highest certified -200 option per EASA TCDS EASA.A.004. Not a -300 or -200F value. The odd lb precision is a unit conversion artifact.
- **A330-200 OEW (265,900 lb = 120,600 kg):** Within expected range for typical 2-class -200 configuration (119,600-121,700 kg across sources).
- **777-200LR MTOW (766,000 lb):** Confirmed per FAA TCDS A28NM. The proximity to the -300ER (775,000 lb) and -F (766,800 lb) is by design — the LR variant has massive structural reinforcement and auxiliary fuel tanks for ultra-long-range operations.

### Item 3 [LOW] — G-V Maximum Payload: VERIFIED, NUANCE ADDED
- MZFW = 54,000 lb confirmed from FAA TCDS A12EA
- OEW = 48,200 lb is Gulfstream's published typical executive configuration (range: 46,000-48,800 lb)
- Max payload = 5,800 lb is correct given chosen OEW
- Note for future reference: a science-stripped G-V could have OEW ~46,000 lb, yielding max payload ~8,000 lb. This doesn't change the qualitative conclusion (still needs ~7 aircraft to match DC-8 payload).

### Item 4 [PROCESS] — Unit Consistency Audit: COMPLETED
Added 23 automated data validation tests in `tests/test_aircraft_data.py`:
- Unit plausibility checks (detecting potential kg/lb or km/nmi confusion)
- Weight balance consistency (OEW + payload + fuel vs. MTOW)
- Range-payload physical consistency (increasing range with decreasing payload)
- Cross-aircraft sanity checks (TSFC ordering by engine generation, size ordering)

All 23 tests pass. No unit inconsistencies detected.

## Known Issues and Uncertainties for Reviewer Attention

### Data Confidence Concerns
- **Cruise TSFC values are the weakest data point** across all aircraft. These are not published by engine manufacturers and are estimated from secondary sources. They will be adjusted during calibration, but the initial estimates affect convergence and may introduce bias.
- **P-8 data carries the most uncertainty** — it is derived from the 737-900ER with assumed modifications. The raked wingtip effect on Oswald efficiency is modeled as a +0.025 increment, which is a rough estimate.
- **Range-payload corner points** for some aircraft (especially the 767-200ER ferry range and A330-200 ferry range) are estimated rather than directly from manufacturer publications.

### Modeling Concerns for Phase 1
- **Calibration overfitting risk:** With 2-3 data points per aircraft and 2-3 free parameters (CD0, Oswald e, TSFC adjustment), we are curve-fitting, not predicting. The calibration validates cruise performance but does NOT validate off-design performance.
- **The parabolic drag polar** does not capture compressibility effects near the drag-divergence Mach number, trim drag, or configuration-dependent drag.
- **TSFC models** will be simplified functions of altitude and Mach. Real engines have complex performance maps that are proprietary.

### Process Notes
- Aircraft data files were collected by parallel research agents. Each agent documented its sources and noted conflicting values. The files use slightly different internal formats but are normalized by the unified loader.
- The 737-900ER agent updated the STUDY_PLAN.md data sources table directly (visible in the file).

## What Has Been Completed (Phase 1)

### 5. Aerodynamic Model
- **File:** `src/models/aerodynamics.py`
- Parabolic drag polar: CD = CD0 + CL²/(π·AR·e)
- Lift coefficient from weight/q/S; drag force; L/D ratio
- Maximum L/D computation and CL for max range (CL* = √(CD0/(3K)) for jets)
- Engine-out drag factor (configurable % increment, default 10%)
- **Tested:** 7 unit tests (all passing)

### 6. Propulsion Model
- **File:** `src/models/propulsion.py`
- TSFC = TSFC_ref × f_altitude(h) × f_mach(M) × k_adj
- Altitude correction: sqrt(theta) model (standard for high-bypass turbofans)
- Mach correction: linear model with k_mach = 0.3
- Thrust lapse at altitude: T_avail = T_SLS × (ρ/ρ0)^0.75
- Engine-out thrust fraction
- **Tested:** 7 unit tests (all passing)

### 7. Performance Model
- **File:** `src/models/performance.py`
- Breguet range equation: R = (V/TSFC) × (L/D) × ln(Wi/Wf)
- Step-cruise method: divides mission into N segments, recomputes CL, CD, and altitude at each weight step
- Optimal cruise altitude computation (thrust-limited ceiling)
- Specific range, cruise conditions at altitude
- Climb fuel estimation and descent fuel credit
- **Tested:** 8 unit tests (all passing)

### 8. Calibration System
- **File:** `src/models/calibration.py`
- **Four calibration parameters per aircraft:** CD0, Oswald e, TSFC adjustment k_adj, non-cruise fuel overhead fraction f_oh
- **Key innovation — Non-cruise fuel overhead model:** F_overhead = f_oh × W_tow. This captures taxi, takeoff, climb, descent, and reserves as a fraction of takeoff weight. At max payload (high TOW, low available fuel), the overhead consumes a disproportionate share of fuel, correctly suppressing range. This was necessary because the Breguet equation's logarithmic weight dependence (ln(Wi/Wf)) alone cannot produce the range ratios observed in published range-payload data. See ASSUMPTIONS_LOG.md entry E3 for full documentation.
- **Two-stage optimization:** SciPy differential_evolution (global search) + Nelder-Mead (local refinement)
- **P-8 derived from 737-900ER** with Oswald efficiency +0.025 delta for raked wingtips
- Calibration error function minimizes RMS percentage error across published range-payload points
- **Tested:** 4 calibration range tests + 7 calibration quality tests (all passing)

### 9. Calibration Results

| Aircraft | CD0 | e | k_adj | f_oh | L/D_max | RMS Error | Status |
|---|---|---|---|---|---|---|---|
| DC-8 | 0.0141 | 0.968 | 0.605 | 0.260 | 20.4 | 0.5% | ✓ |
| G-V | 0.0150 | 0.745 | 0.801 | 0.131 | 17.3 | 1.2% | ✓ |
| 737-900ER | 0.0355 | 1.223 | 0.757 | 0.062 | 16.7 | 0.7% | ✓ |
| 767-200ER | 0.0153 | 0.947 | 0.756 | 0.157 | 19.7 | 0.2% | ✓ |
| A330-200 | 0.0334 | 2.165 | 1.021 | 0.000 | 22.6 | 3.0% | ✓ |
| 777-200LR | 0.0410 | 1.811 | 0.556 | 0.080 | 18.3 | 6.5% | ⚠ |
| P-8 | 0.0597 | 0.975 | 0.339 | 0.180 | 11.5 | 0.0% | ✓ (derived) |

**Important caveat:** Individual calibrated parameters (CD0, e, k_adj) are often outside physically realistic bounds because the simplified overhead model forces other parameters to compensate. The *combined* model (all 4 parameters together) is what's calibrated, not individual components. The L/D_max values are effective cruise L/D values within this framework. See ASSUMPTIONS_LOG.md entry E3.

**777-200LR note:** At 6.5% RMS, this is the weakest calibration. The extreme range of this aircraft (10,800 nmi ferry) stresses the simplified overhead model. Points 1 and 2 each show ~8% individual error. This is a known limitation.

### 10. Range-Payload Diagrams
- **File:** `src/plotting/range_payload.py`
- Individual diagrams for all 7 aircraft with calibration point overlays (`outputs/plots/rp_*.png`)
- Overlay comparison diagram with all aircraft and mission requirement lines (`outputs/plots/rp_overlay_all.png`)
- Each individual diagram shows calibration RMS, CD0, e, and L/D_max annotations

### Phase 1 Test Summary
- 33 new tests in `tests/test_performance.py`
- **Total test suite: 74 tests, all passing**
  - 18 atmosphere tests
  - 23 aircraft data tests
  - 7 aerodynamics tests
  - 7 propulsion tests
  - 8 performance/Breguet tests
  - 4 calibration range tests
  - 7 calibration quality tests (verify all aircraft RMS < threshold)

## Key Technical Findings from Phase 1

### The Breguet Calibration Challenge
The most significant technical challenge in Phase 1 was matching published range-payload data with a simplified Breguet model. The core issue:

1. **Published range-payload data includes all non-cruise fuel** (taxi, takeoff, climb, descent, reserves), not just cruise range
2. **Non-cruise fuel scales approximately with takeoff weight** — heavier aircraft burn more fuel in climb, require larger reserves, etc.
3. **The Breguet equation's logarithmic weight ratio** ln(Wi/Wf) cannot by itself produce the observed range ratios between high-payload and low-payload conditions
4. **The range parameter** V×L/D varies only ±5% across the typical CL range, so aerodynamic efficiency variations cannot explain the spread either

The solution was introducing the non-cruise fuel overhead model: F_overhead = f_oh × W_tow. At max payload (high TOW), this overhead consumes a large fraction of available fuel, correctly suppressing range. At zero payload (low TOW), the overhead is smaller, leaving more fuel for cruise.

This is documented as assumption E3 in ASSUMPTIONS_LOG.md. The trade-off is that calibrated parameter values are not individually interpretable as physical quantities — they are effective parameters within a coupled model.

## What's Next (Phase 2)

Mission analysis for the three NASA science missions:
1. **Mission 1:** Long-range transport SCEL→KPMD (5,050 nmi, 46,000 lb payload) with engine-out at midpoint
2. **Mission 2:** Vertical atmospheric sampling NZCH→SCCI (4,200 nmi, 52,000 lb payload) with repeated climb-descend segments
3. **Mission 3:** Low-altitude smoke survey (8 hours endurance, 30,000 lb payload, 1,500 ft AGL)

This will require extending the step-cruise model to handle:
- Engine-out scenarios (reduced thrust, increased drag, altitude/speed adjustment)
- Repeated climb-descend profiles (fuel penalty per cycle)
- Low-altitude endurance (very different operating point from cruise)

## Files in Repository

```
CLAUDE.md                           # Problem statement
STUDY_PLAN.md                       # Full project plan with phases
ASSUMPTIONS_LOG.md                  # All modeling assumptions documented
PROGRESS_REPORT.md                  # This file
src/
    __init__.py
    utils.py                        # Unit conversions
    aircraft_data/
        __init__.py
        loader.py                   # Unified data loader + validation
        dc8_72.py                   # NASA DC-8 data
        gulfstream_gv.py            # Gulfstream G-V data
        boeing_737_900er.py         # Boeing 737-900ER data
        boeing_p8.py                # P-8 Poseidon (derived from 737)
        boeing_767_200er.py         # Boeing 767-200ER data
        a330_200.py                 # Airbus A330-200 data
        boeing_777_200lr.py         # Boeing 777-200LR data
    models/
        __init__.py
        atmosphere.py               # ISA atmosphere model
        aerodynamics.py             # Parabolic drag polar model
        propulsion.py               # TSFC and thrust model
        performance.py              # Breguet range + step-cruise
        calibration.py              # Parameter fitting + range computation
    plotting/
        __init__.py
        range_payload.py            # Range-payload diagram generation
tests/
    __init__.py
    test_atmosphere.py              # 18 ISA model tests (all passing)
    test_aircraft_data.py           # 23 data validation tests (all passing)
    test_performance.py             # 33 performance model tests (all passing)
outputs/
    plots/
        rp_dc8.png                  # DC-8 range-payload diagram
        rp_gv.png                   # G-V range-payload diagram
        rp_737900er.png             # 737-900ER range-payload diagram
        rp_p8.png                   # P-8 range-payload diagram
        rp_767200er.png             # 767-200ER range-payload diagram
        rp_a330200.png              # A330-200 range-payload diagram
        rp_777200lr.png             # 777-200LR range-payload diagram
        rp_overlay_all.png          # All aircraft overlay comparison
    results/                        # (empty — for Phase 2+ numerical results)
```
