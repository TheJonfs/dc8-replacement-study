# DC-8 Replacement Aircraft Performance Study — Implementation Plan

## Document Purpose
This plan serves as a persistent reference across conversation threads. It captures the technical approach, phasing, verification strategy, known limitations, and decision log for the study. Update this document as the project evolves.

---

## Phase Overview

| Phase | Description | Key Output | Status |
|-------|-------------|------------|--------|
| 0 | Project setup and data collection | Aircraft data files, code scaffolding | Not started |
| 1 | Core performance model (single aircraft) | Calibrated DC-8 model, range-payload diagram | Not started |
| 2 | Extend model to all aircraft | 6 calibrated models, overlay range-payload diagram | Not started |
| 3 | Mission 1 — Long-range transport with engine-out | Mission results, speed/altitude profiles | Not started |
| 4 | Mission 2 — Vertical atmospheric sampling | Mission results, speed/altitude profiles | Not started |
| 5 | Mission 3 — Low-altitude smoke survey | Mission results, fuel burn comparison | Not started |
| 6 | Comparative analysis and deliverables | Weight breakdowns, fuel cost metrics, final plots | Not started |

---

## Phase 0: Project Setup and Data Collection

### 0a. Code Structure
```
src/
    aircraft_data/       # Per-aircraft YAML or Python data files with specs
    models/
        atmosphere.py    # ISA atmosphere model
        aerodynamics.py  # Drag polar estimation, L/D computation
        propulsion.py    # TSFC modeling by altitude/Mach/throttle
        performance.py   # Breguet range, cruise performance, climb/descent
        mission.py       # Mission simulation (integrates above)
    plotting/            # All matplotlib output generation
    utils.py             # Unit conversions, common helpers
data/
    published/           # Any reference data we retrieve (with source URLs)
outputs/
    plots/               # Generated figures
    results/             # Numerical results (CSV or similar)
tests/                   # Verification tests (see Verification Strategy below)
STUDY_PLAN.md            # This file
ASSUMPTIONS_LOG.md       # Running log of every modeling assumption and its justification
CLAUDE.md                # Problem statement and requirements
```

### 0b. Data Collection
For each of the 5 commercial aircraft (G-V, 737-900ER, 767-200ER, A330-200, 777-200LR), retrieve from public sources:
- MTOW, OEW, max payload, max fuel weight, MZFW
- Published range at various payload conditions (range-payload corner points)
- Wing area, wingspan, aspect ratio
- Engine type and count, sea-level static thrust, cruise TSFC
- Cruise Mach number, service ceiling
- Fuselage dimensions (length, interior width)

**DC-8 data** is provided in CLAUDE.md. **P-8 data** is derived from the 737-900ER with specified modifications.

**Source documentation:** Every retrieved value must be recorded with its source URL or document reference in the aircraft data file.

---

## Phase 1: Core Performance Model (DC-8)

### 1a. Atmosphere Model
- Implement International Standard Atmosphere (ISA) up to ~65,000 ft
- Properties needed: temperature, pressure, density as functions of altitude
- **Verification:** Compare against published ISA tables at standard altitudes (0, 11,000 m tropopause, 20,000 m)

### 1b. Aerodynamic Model
- Estimate zero-lift drag coefficient (CD0) from wetted area correlations or equivalent parasite area methods
- Model lift-dependent drag using parabolic drag polar: CD = CD0 + CL²/(π·AR·e)
  - AR = aspect ratio (known from geometry)
  - e = Oswald efficiency factor (estimated, typically 0.75-0.85 for transport aircraft)
- **Key uncertainty:** CD0 and e are not published. We estimate them and then *calibrate* to match known range-payload performance.
- **Verification:** After calibration, check that resulting L/D_max values are physically reasonable for the aircraft class (typically 15-19 for modern transports, 12-16 for older designs).

### 1c. Propulsion Model
- Model TSFC as a function of altitude and Mach number
- Baseline approach: use published sea-level and/or cruise TSFC values, then apply standard lapse models
  - TSFC generally decreases with altitude (colder, denser air at turbine inlet in relative terms) up to the tropopause, then roughly constant
  - TSFC increases modestly with Mach number
- For the DC-8's CFM56-2-C1 engines, publicly available TSFC data exists
- **Key uncertainty:** TSFC models are simplified. Real engine decks are proprietary.
- **Verification:** Check that cruise TSFC values fall in published ranges for the engine type

### 1d. Breguet Range Equation Implementation
- Classic form: R = (V / TSFC) · (L/D) · ln(W_initial / W_final)
- This assumes constant altitude, constant speed cruise — a simplification
- For more accuracy, implement step-cruise: divide the mission into segments, recompute optimal altitude and L/D at each step as weight decreases
- **Verification:**
  - Reproduce DC-8 range-payload corner points within target tolerance
  - Energy audit: fuel energy expended ≈ drag force × distance (integrated)

### 1e. Calibration Procedure
- **Inputs:** Known range-payload corner points (3 points for DC-8)
- **Free parameters:** CD0, Oswald efficiency (e), cruise TSFC adjustment factor
- **Method:** Minimize error between predicted and known range at each corner point
- **Acceptance criterion:** Match all three corner points within 5% range error (aspirational; document actual achieved accuracy)
- **Overfitting risk:** With 3 data points and 2-3 free parameters, we are fitting rather than predicting. The calibration tells us "the model can reproduce cruise performance" but does NOT validate off-design performance (low altitude, engine-out, climb/descent cycles). This limitation must be prominently documented.

### 1f. Range-Payload Diagram
- Generate continuous curve from max-payload to zero-payload
- Overlay the three calibration points
- Label axes, include aircraft name and key specs

---

## Phase 2: Extend to All Aircraft

- Repeat Phase 1 process for G-V, 737-900ER, 767-200ER, A330-200, 777-200LR
- Derive P-8 model from calibrated 737-900ER model using the specified modifications
  - Reduce OEW by 7,500 lb
  - Increase fuel capacity to 73,320 lb
  - Increase max ramp weight to 188,200 lb
  - Adjust drag polar for raked wingtip effect (modest Oswald efficiency improvement)
- Produce overlay range-payload diagram for all 6 aircraft
- **Verification:** Each aircraft's calibration error documented; cross-check L/D and TSFC values against published ranges

---

## Phase 3: Mission 1 — Long-Range Transport with Engine-Out (SCEL to KPMD)

### Mission Parameters
- Distance: 5,050 nmi
- Payload: 46,000 lb
- Profile: Cruise to midpoint, then engine failure

### Modeling Approach
- **Normal cruise (first half):** Step-cruise at optimal altitude/Mach
- **Engine-out (second half):**
  - For twin-engine aircraft: lose 50% thrust → must descend to altitude where remaining thrust matches drag at reduced speed
  - For quad-engine aircraft (DC-8): lose 25% thrust → less severe but still significant
  - Asymmetric thrust creates yaw → additional drag from rudder deflection and sideslip (model as an incremental drag term, ~5-15% drag increase — this is an estimate we should document)
  - Reduce speed to best range speed for the degraded configuration
  - Compute new optimal altitude (likely significantly lower)
- **Feasibility check:** Can the aircraft complete the remaining 2,525 nmi on reduced thrust with fuel remaining at midpoint?
- **Reserve fuel:** Calculate fuel remaining at destination; compare against standard reserves (typically 5% of trip fuel + 200 nmi alternate + 30 min hold, but we should define and document our reserve policy)

### Outputs
- Go/no-go for each aircraft
- Fuel consumed (total and per-segment)
- Speed and altitude profiles vs. distance
- Reserve fuel remaining

---

## Phase 4: Mission 2 — Vertical Atmospheric Sampling (NZCH to SCCI)

### Mission Parameters
- Distance: ~4,200 nmi
- Payload: 52,000 lb
- Profile: Repeated climb-descend segments

### Modeling Approach
- This is the most computationally involved mission
- Divide into segments; at each segment:
  - Compute current weight (fuel burned so far)
  - Determine maximum achievable altitude at current weight (service ceiling or thrust-limited ceiling)
  - Model climb from low altitude to ceiling: fuel burn = f(climb rate, altitude gain, weight)
  - Model descent: near-idle thrust, trading altitude for distance
  - As fuel burns off, ceiling increases → later segments reach higher altitudes
- **Key modeling challenge:** Climb and descent performance requires more than Breguet. Need rate-of-climb model: ROC = (T - D) · V / W
- **Simplification:** We may approximate climb fuel burn using an energy method rather than integrating the full trajectory
- **Verification:** Check that computed ceilings match published service ceilings for near-empty weights

### Outputs
- Altitude envelope vs. distance (showing progressive increase)
- Fuel consumed per segment
- Maximum altitude achieved
- Speed profile

---

## Phase 5: Mission 3 — Low-Altitude Smoke Survey

### Mission Parameters
- Duration: 8 hours
- Payload: 30,000 lb
- Altitude: ~1,500 ft AGL (assume flat terrain, ~1,500 ft MSL)
- Region: Central US (no significant terrain concerns)

### Modeling Approach
- Low-altitude cruise is very different from high-altitude:
  - Air density much higher → more drag at a given TAS
  - Optimal speed is lower
  - TSFC may be different (engines at very different operating point)
  - True airspeed will be lower, so distance covered in 8 hours is less (but that's not the constraint here — duration is)
- Compute fuel flow rate at 1,500 ft, required payload, and optimal low-altitude cruise speed
- Total fuel = fuel flow rate × 8 hours (+ reserves)
- **Feasibility check:** Can the aircraft carry enough fuel for 8 hours at 1,500 ft plus reserves, given MTOW constraint?

### Outputs
- Fuel consumed
- Total distance covered (informational)
- Feasibility determination
- Fuel remaining / reserves

---

## Phase 6: Comparative Analysis and Deliverables

### Weight Breakdown Charts
- Stacked bar charts per mission showing OEW, payload, fuel, reserve fuel
- For G-V and P-8: show single-aircraft and n-aircraft aggregate

### Fuel Cost Metrics
- Assume Jet-A price (document assumed price; ~$5-6/gallon is a reasonable 2024 range, or ~$0.75-0.90/lb)
- Total fuel cost per mission per aircraft
- Fuel cost per 1,000 lb of payload per nautical mile
- Aggregate costs for multi-aircraft G-V/P-8 operations

### Fleet Size Computation
- For G-V and P-8 on missions where they can't carry full payload:
  - n = ceil(required_payload / aircraft_max_payload)
  - Aggregate fuel = n × single-aircraft fuel
  - Aggregate cost = n × single-aircraft cost

### Final Comparison Summary
- Tabular comparison across all metrics
- Discussion of which aircraft best replicate DC-8 capability
- Note where our results agree/disagree with the known conclusion (767-200ER and P-8 as top contenders)

---

## Verification Strategy

### Tier 1: Unit Tests (Automated)
- Atmosphere model matches ISA tables
- Weight balance: OEW + payload + fuel = takeoff weight (always)
- Fuel burn is positive and monotonically depletes fuel
- Range increases as payload decreases (for fixed MTOW)
- No aircraft exceeds MTOW, MZFW, or max fuel limits

### Tier 2: Calibration Validation
- Each aircraft's model reproduces its published range-payload corner points
- Document calibration error for each point (absolute and percentage)
- L/D_max values are physically reasonable for aircraft class
- Cruise TSFC values are within published ranges

### Tier 3: Physical Sanity Checks
- Larger aircraft burn more total fuel but may be more efficient per payload-mile
- Engine-out impact is proportionally worse for twin-engine aircraft
- Low-altitude fuel burn is substantially higher than cruise-altitude fuel burn
- G-V and P-8 require multiple airframes for full DC-8 payload
- Ferry range > max-payload range (always)

### Tier 4: Sensitivity Analysis
- For key uncertain parameters (CD0, Oswald e, TSFC), vary by ±10% and report range spread
- Identify which parameters the results are most sensitive to
- Report confidence bounds on mission fuel estimates

### Tier 5: External Cross-Reference
- Where possible, compare computed fuel burn rates against published operator data
- Compare computed L/D values against published estimates for similar aircraft
- Spot-check any available mission-specific performance data

---

## Known Limitations and Honest Uncertainties

### Limitations of our approach vs. the original study (which used FLOPS)
1. **No access to proprietary engine decks.** Our TSFC models are simplified curve fits. Real engines have complex performance maps. This is our single largest source of uncertainty.
2. **Simplified drag model.** A parabolic drag polar with fixed Oswald efficiency is a textbook approximation. Real aircraft have compressibility drag rise near Mach limits, Reynolds number effects, and configuration-dependent drag (flaps, gear, etc.).
3. **No Mach-dependent drag rise modeling.** We should add a simple wave drag correction for flight near the drag-divergence Mach number, but it will be approximate.
4. **Climb/descent modeling is approximate.** Breguet applies to cruise. For climb and descent segments (Mission 2 especially), we use energy methods that are less accurate.
5. **Engine-out asymmetric drag is estimated.** The yaw drag increment from engine failure is typically determined from flight test data we don't have.
6. **No wind modeling.** All missions assume zero wind. Real missions would be planned with forecast winds.
7. **Calibration overfitting risk.** With ~3 data points per aircraft and 2-3 free parameters, we are curve-fitting, not predicting. The calibration validates cruise performance but gives limited confidence for off-design conditions.

### What this means for results
- Range-payload diagrams should be quite good (directly calibrated)
- Cruise mission fuel burn (Mission 1 normal segment, Mission 3) should be reasonable
- Engine-out performance (Mission 1 second half) has moderate uncertainty due to asymmetric drag estimates
- Climb-descent cycling (Mission 2) has the highest uncertainty — this is furthest from the calibrated cruise condition
- Relative rankings between aircraft are likely more reliable than absolute numbers

---

## Decision Log

Record every significant modeling decision here with date and rationale.

| Date | Decision | Rationale | Alternatives Considered |
|------|----------|-----------|------------------------|
| 2026-02-06 | Use Breguet range equation with step-cruise refinement | Standard approach for conceptual-level analysis; matches available data fidelity | Full trajectory integration (more complex, not warranted by input data quality) |
| 2026-02-06 | Calibrate CD0 and Oswald e to match range-payload data | These parameters are not directly available; calibration anchors model to reality | Use generic textbook values (less accurate for specific aircraft) |
| 2026-02-06 | Model engine-out drag increment as 5-15% increase | Standard rule-of-thumb range; exact value requires flight test data | Ignore asymmetric drag (unrealistic); CFD (not feasible) |
| | | | |

---

## Data Sources Log

Record all external data sources used.

| Aircraft | Parameter | Value | Source | Date Retrieved |
|----------|-----------|-------|--------|----------------|
| DC-8-72 | All weights | Per CLAUDE.md | Provided in problem statement | N/A |
| 737-900ER | MTOW | 187,700 lb | Boeing Airport Planning D6-58325-6; TCDS A16WE | 2026-02-06 |
| 737-900ER | OEW (2-class) | 98,495 lb | Boeing Airport Planning D6-58325-6; Jane's | 2026-02-06 |
| 737-900ER | MZFW | 146,300 lb | Boeing Airport Planning D6-58325-6; TCDS A16WE | 2026-02-06 |
| 737-900ER | MLW | 157,300 lb | Boeing Airport Planning D6-58325-6 | 2026-02-06 |
| 737-900ER | Max fuel | 46,063 lb (6,875 gal) | Boeing Airport Planning D6-58325-6 | 2026-02-06 |
| 737-900ER | Wing area | 1,344 sq ft | Boeing Airport Planning D6-58325-6 | 2026-02-06 |
| 737-900ER | Wingspan | 117.42 ft | Boeing Airport Planning D6-58325-6 | 2026-02-06 |
| 737-900ER | Engines | 2x CFM56-7B26 (26,300 lbf) | CFM International; TCDS A16WE | 2026-02-06 |
| 737-900ER | Cruise TSFC | 0.627 lb/(lbf*hr) | Roux (2007) engine database | 2026-02-06 |
| 737-900ER | Design range | 3,200 nmi / 162 pax | Boeing product specifications | 2026-02-06 |
| 737-900ER | Service ceiling | 41,000 ft | Boeing product specifications | 2026-02-06 |
| 737-900ER | Cruise Mach | 0.785 | Boeing product specifications | 2026-02-06 |
| | | | | |

---

## Open Questions

1. What reserve fuel policy should we use? Options: FAR 91 (VFR/IFR domestic), FAR 121 (airline operations), or a custom policy matching NASA ASP practice. **Proposed default:** 5% of trip fuel + 200 nmi alternate at cruise speed + 30 min hold fuel.
2. For Mission 2 climb-descend profile, what altitude band should the sampling cover? The problem says "vertical atmospheric column sampling" but doesn't specify a minimum altitude. **Proposed default:** Descend to ~10,000 ft, climb to maximum achievable ceiling.
3. Should we model the P-8's raked wingtips as an Oswald efficiency improvement, an aspect ratio improvement, or both? **Proposed:** Small Oswald efficiency increase (~0.02-0.03) to account for reduced induced drag.
