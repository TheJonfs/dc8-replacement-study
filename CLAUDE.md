# DC-8 Replacement Aircraft Performance Study

## Problem Statement

NASA's Airborne Science Program (ASP) operates a DC-8-72 Flying Laboratory (N817NA) as its premier platform for large-scale atmospheric science campaigns. The aircraft was manufactured in 1969 and, despite modifications including re-engining with CFM56-2-C1 turbofans, faces growing age-related operational challenges: shortage of trained flight crew, diminishing spare parts, lack of suitable ground handling equipment at destination airports, high fuel costs, and few remaining flight simulators.

This project asks: **given a set of candidate replacement aircraft, how do they compare to the DC-8 in their ability to perform representative airborne science missions, as measured by range-payload capability, mission fuel consumption, and cost efficiency?**

## Objective

Build aircraft performance models from publicly available specifications, calibrate them against published range-payload data, and then use those models to evaluate each candidate aircraft's performance on three specific airborne science missions. Produce comparative analyses including range-payload diagrams, mission weight breakdowns, and fuel cost metrics.

## Candidate Aircraft

The following six aircraft are to be modeled and compared:

1. **Douglas DC-8-72 (NASA N817NA modified)** — the baseline
2. **Gulfstream G-V**
3. **Boeing P-8 Poseidon** (military variant derived from 737-900ER)
4. **Boeing 767-200ER**
5. **Airbus A330-200**
6. **Boeing 777-200LR**

## Aircraft Data

### Publicly Available Data (retrieve independently)
For the G-V, 737-900ER, 767-200ER, A330-200, and 777-200LR, retrieve the following from manufacturer airport planning documents, spec sheets, or equivalent public sources:
- Maximum Takeoff Weight (MTOW)
- Operating Empty Weight (OEW)
- Maximum payload weight
- Maximum fuel weight
- Maximum range at various payload conditions
- Range-payload diagram data (three corner points: max payload with partial fuel, max fuel with partial payload, max fuel with zero payload)
- Basic dimensions (wingspan, fuselage length, fuselage interior width)

### Provided Data: NASA DC-8-72 (N817NA Modified Configuration)
This is not a stock DC-8. The following weights reflect the NASA-modified configuration with CFM56-2-C1 engines and science laboratory customizations:

| Parameter | Value |
|---|---|
| Operating Empty Weight (OEW) | 157,000 lb |
| Maximum Payload Weight | 52,000 lb |
| Maximum Fuel Weight | 147,255 lb |
| Maximum Takeoff Weight (MTOW) | 325,000 lb |
| Maximum Zero Fuel Weight (ZFW) | 209,000 lb |

Range-payload calibration reference points:
- At max payload (52,000 lb) with fuel to MTOW: range ~2,750 nmi
- At max fuel (147,255 lb) with payload to MTOW: range ~5,400 nmi
- At max fuel (147,255 lb) with zero payload (ferry): range ~6,400 nmi

### Provided Data: Boeing P-8 Poseidon Derivation
The P-8's detailed performance specifications are not publicly available. The P-8 is derived from the Boeing 737-900ER airframe with the following modifications:
- **Wing:** Higher aspect ratio wing with swept wing tips (raked wingtips) to reduce induced drag
- **Empty weight reduction:** Removal of ~7,500 lb of passenger furnishings from the 737-900ER baseline, yielding an OEW of approximately 90,995 lb
- **Maximum payload:** 23,885 lb
- **Maximum fuel weight:** 73,320 lb (significantly increased from the ~46,063 lb 737-900ER capacity via auxiliary fuel tanks)
- **Maximum ramp weight:** 188,200 lb

First calibrate a 737-900ER model, then transition it to a P-8 model using these modifications.

## Science Mission Requirements

### Context from ASP Scientists and Personnel
The following requirements and constraints were gathered from interviews with DC-8 operators and science users. These inform the qualitative evaluation context and some quantitative mission parameters:

**Performance priorities:**
- Flying higher is the single most desirable capability improvement. Scientists strongly support a platform capable of DC-8-type measurements at altitudes up to 50,000 ft. The current DC-8 rarely reaches 40,000 ft until late in a flight when fuel has burned off, due to weight constraints.
- Off-design operations throughout the flight envelope are required, including low-altitude (1,000–1,500 ft AGL) endurance missions and vertical profiling with repeated climb-descend segments.
- Good performance throughout the flight envelope is preferred over optimal performance in narrow bands.
- The DC-8's speed is valued for flying away from its own exhaust plume to avoid contaminating atmospheric samples.

**Payload and configuration:**
- For large campaigns, maximum payload weight is less constraining than available floor space and emergency exit access.
- ASP policy requires the DC-8 be loaded with the fullest possible complement of payloads and investigative teams for each campaign.
- Scientific payloads on the DC-8 tend to be heavy, large, and less refined but more technologically advanced than payloads on smaller ASP platforms.
- Standard equipment rack maximum height: 54 in. (limited by overhead bins on DC-8).
- Some instruments exceed 2,000 lb individually.

**Engine-out considerations:**
- Scientists expressed concern about twin-engine reliability vs. the DC-8's four engines.
- One perspective: losing one of four engines allows most experiments to continue on remaining engine power.
- Counter-perspective: any engine loss should cease all experimentation and focus on safe return.
- This motivates analyzing a long-range mission with engine failure at the midpoint.

**Airframe preferences:**
- The DC-8's long narrow-body fuselage is preferred — scientists sit along the walls near instruments, and a wider central aisle would be wasted space.
- Military cargo aircraft would provide too much width, unusable overhead volume, and excess payload capacity.
- However, for larger campaigns, a wider fuselage might provide better payload configuration options and safety (emergency exit access).
- The DC-8 features the longest commercially manufactured narrow-body fuselage; scientists utilize that length for spatially separated simultaneous measurements.
- T-tail configurations obstruct sensor views of the upper hemisphere and interfere with solar flux measurements.
- A structurally over-designed fuselage amenable to cutouts and externally mounted equipment is strongly desired.

**Other factors:**
- At least one aft lavatory is non-negotiable (the forward lavatory is declared off-limits during sampling to avoid contaminating air samples measured downstream).
- Larger cargo doors would save days of instrument assembly/disassembly time.
- Wing hard points for externally mounted equipment and pods are desirable.

### Mission 1: Long-Range Transport with Engine-Out (SCEL-KPMD)
- **Route:** Santiago, Chile (SCEL) to Palmdale, CA (KPMD)
- **Distance:** 5,050 nmi
- **Payload:** 46,000 lb
- **Profile:** Nominal cruise transport mission
- **Special condition:** Model single engine failure occurring at the mission midpoint. Analyze the aircraft's ability to complete the mission on remaining engines without alternate landing sites. The aircraft should adjust speed and altitude appropriately following engine loss (accounting for differences between 2-engine and 4-engine configurations).

### Mission 2: Vertical Atmospheric Sampling (NZCH-SCCI)
- **Route:** Christchurch, New Zealand (NZCH) to Punta Arenas, Chile (SCCI)
- **Distance:** ~4,200 nmi
- **Payload:** 52,000 lb
- **Profile:** Multiple repeating, consecutive climb-descend segments for vertical atmospheric column sampling. As the aircraft burns fuel and gets lighter, it becomes capable of reaching higher sampling altitudes. Model the progressive altitude capability increase throughout the mission.

### Mission 3: Low-Altitude Smoke Survey
- **Region:** Central United States (Arkansas-Missouri area)
- **Duration:** 8 hours
- **Payload:** 30,000 lb
- **Altitude:** ~1,500 ft above ground level
- **Profile:** Extended low-altitude endurance mission for forest fire particulate sampling. The aircraft cruises at low altitude for the full mission duration.

## Deliverables

### 1. Range-Payload Diagrams
For each aircraft, produce a range-payload diagram calibrated against published data. Each diagram should show the three calibration corner points:
- Maximum payload, with fuel weight set to reach MTOW
- Maximum fuel, with payload weight set to reach MTOW
- Maximum fuel, zero payload (ferry mission)

Produce a combined overlay plot comparing all six aircraft.

### 2. Mission Performance Analysis
For each of the three science missions and each aircraft:
- Determine whether the aircraft can complete the mission as defined
- Calculate total mission fuel consumption
- Calculate reserve fuel remaining
- For aircraft that cannot carry the full payload (G-V and P-8), determine how many aircraft (n) would be needed to carry the equivalent aggregate payload, and calculate aggregate fuel consumption for the n-aircraft fleet

### 3. Weight Breakdown Comparison
For each mission, produce a stacked comparison showing each aircraft's:
- Operating Empty Weight
- Payload weight
- Mission fuel weight
- Reserve fuel weight
Show both individual aircraft values and aggregate values for the G-V and P-8 (where n > 1).

### 4. Fuel Cost Metrics
Calculate and compare:
- Total fuel cost per mission (assume a reasonable fuel price per pound or per gallon of Jet-A)
- **Fuel cost metric:** Estimated fuel cost to carry 1,000 lb of payload one nautical mile
- For the G-V and P-8, calculate both per-aircraft and n-aircraft aggregate costs

### 5. Speed and Altitude Profiles
For Mission 1 (engine-out) and Mission 2 (sampling), produce plots of:
- Aircraft speed (Mach number) vs. distance
- Altitude vs. distance
Show how each aircraft's optimal operating characteristics differ given their different aerodynamic and propulsive efficiencies, and how the engine-out condition affects performance differently for 2-engine vs. 4-engine configurations.

## Technical Approach Notes

- You will need to develop your own aircraft performance modeling methodology. The original study used NASA's Flight Optimization System (FLOPS), which is not available to you. You should build physics-based models from first principles (Breguet range equation, drag polar estimation, engine performance modeling, etc.) or use any other suitable publicly available methods.
- Calibrate your models against published range-payload data before applying them to the science missions. The calibration step is critical — the science missions involve off-nominal flight profiles (repeated climbs/descents, low-altitude cruise, engine-out) that are very different from standard transport operations.
- Document your modeling assumptions, data sources, and any simplifications made.
- Use Python for implementation. Organize the code for clarity and maintainability.
- Produce all plots using matplotlib or a comparable plotting library.

## Success Criteria

Results will be compared against the published study for:
- Qualitative agreement on which aircraft are most and least suitable as DC-8 replacements
- Reasonable quantitative agreement on range-payload diagrams, mission fuel consumption, and cost metrics
- Correct identification of the 767-200ER and P-8 as the top contenders (this general conclusion is stated in the study abstract, so it serves as a high-level check rather than a hint about methodology)
