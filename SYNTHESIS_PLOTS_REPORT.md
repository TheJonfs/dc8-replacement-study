# Synthesis Plots Report — Deliverables 3 and 5

## Overview

This report documents the generation of the remaining CLAUDE.md plot deliverables: weight breakdown stacked bar charts (Deliverable 3) and speed/altitude profile plots (Deliverable 5). All data is drawn from the same calibrated mission simulations used in the Phase 2 mission reports.

All plots are reproducible via:
```
python3 -m src.analysis.run_synthesis_plots
```

New source files:
- `src/plotting/weight_breakdown.py` — stacked bar chart generation
- `src/plotting/mission_profiles.py` — altitude/Mach/ceiling progression plots
- `src/analysis/run_synthesis_plots.py` — driver script

---

## Deliverable 3: Weight Breakdown Stacked Bar Charts

Three plots, one per mission. Each shows the six study aircraft side by side with stacked bars decomposed into OEW, payload, mission fuel, and reserve fuel. For the GV and P-8, additional hatched bars show fleet aggregate values.

### Output Files
| File | Mission |
|---|---|
| `outputs/plots/weight_breakdown_m1.png` | Mission 1: Engine-Out Transport |
| `outputs/plots/weight_breakdown_m2.png` | Mission 2: Vertical Sampling |
| `outputs/plots/weight_breakdown_m3.png` | Mission 3: Low-Altitude Smoke Survey |

### Design Decisions

**Fuel decomposition:** Total loaded fuel is split into "mission fuel" (fuel consumed or allocated for the flight) and "reserve fuel." The exact meaning of each varies by mission:
- **Mission 1:** Uses the f_oh hybrid fuel budget. `reserve_fuel_lb` is unburned cruise fuel after the full range is exhausted (not a pre-allocated reserve). Mission fuel = total fuel - reserve.
- **Missions 2-3:** Use explicit reserves (5% contingency + 200 nm alternate + 30 min hold). Mission fuel = total fuel - pre-computed reserves.

**Fleet aggregate bars:** Displayed with diagonal hatch patterns and labeled with fleet size (e.g., "GV (8x fleet)"). All weights are multiplied by n_aircraft. This makes the aggregate resource commitment immediately visible — the GV 9x fleet for Mission 2 has an aggregate takeoff weight of 814k lb, dwarfing any single aircraft.

**Total weight annotation:** Each bar is topped with the total weight in thousands of pounds, making cross-aircraft comparison quick.

### Key Observations

**Mission 1:** The 767 and A330 bars are similar height (~387k and 534k lb), but the 767 allocates a much larger fraction to mission fuel (range capability). The GV fleet aggregate (724k lb) and 777 (691k lb) represent enormous fuel commitments.

**Mission 2:** Similar pattern to Mission 1 since both are max-fuel range missions. The GV 9x fleet (814k lb aggregate) and P-8 3x fleet (545k lb) highlight the impracticality of using small aircraft for heavy payload missions.

**Mission 3:** Dramatically different from Missions 1-2 due to mission-sized fuel loading. The DC-8 loads only 44k lb of fuel (vs. 147k lb capacity); the 767 loads 96k lb (vs. 162k lb capacity). This is the iterative fuel sizing working as intended — aircraft are not penalized for having large tanks they don't need to fill.

---

## Deliverable 5: Speed and Altitude Profiles

Four plots covering Missions 1 and 2.

### Output Files
| File | Content |
|---|---|
| `outputs/plots/profile_m1_altitude.png` | Mission 1: Altitude vs. distance (engine-out) |
| `outputs/plots/profile_m1_mach.png` | Mission 1: Mach number vs. distance |
| `outputs/plots/profile_m2_altitude.png` | Mission 2: Altitude vs. distance (sawtooth) |
| `outputs/plots/profile_m2_ceiling.png` | Mission 2: Progressive ceiling vs. cycle number |

### Mission 1: Altitude Profile

The altitude plot is the most informative Mission 1 visualization. It shows:

1. **Pre-failure cruise (0–2,525 nm):** All aircraft cruise at 33–45k ft with gradual step-climbs as fuel burns off. The GV cruises highest (43–46k ft), consistent with its high-altitude design. The 767 starts at ~35k ft and climbs to ~38k by midpoint.

2. **Engine failure discontinuity (2,525 nm):** A sharp altitude drop occurs for aircraft with unphysical CD0 calibrations (P-8, A330, 777), which drop to the 10,000 ft floor. This is the model artifact documented in the Mission 1 report — with CD0 = 0.04–0.06, drag exceeds the reduced thrust available on n-1 engines at all altitudes above 10,000 ft. The DC-8, GV, and 767 (which have physical CD0 values) show more moderate altitude adjustments.

3. **Post-failure continuation:** The 767 continues cruising at 33–38k ft all the way past 5,050 nm with substantial range surplus. The DC-8 and GV run out of fuel before reaching destination. The P-8/A330/777 at 10,000 ft burn fuel much faster and also fall short (P-8, A330) or barely make it (777).

**Interpretation note:** The 10,000 ft floor for the P-8/A330/777 is an artifact of unphysical calibrations, not a prediction that these aircraft couldn't maintain altitude on one engine. In reality, all these aircraft are certified for single-engine flight at reasonable altitudes. The model simply can't produce trustworthy engine-out results for aircraft with CD0 > 0.03.

### Mission 1: Mach Profile

Mach is constant throughout the mission for each aircraft (the model holds cruise Mach constant and adjusts altitude). This plot shows the different operating points:
- 777-200LR: Mach 0.84 (fastest)
- DC-8 / A330-200: Mach 0.82
- GV: Mach 0.82 (but overlaps DC-8/A330 on the plot)
- 767-200ER: Mach 0.80
- P-8: Mach 0.785

The Mach plot is less informative than the altitude plot since the model doesn't vary speed. It does, however, confirm that the aircraft operate at different design points, which affects specific range and fuel efficiency.

### Mission 2: Sawtooth Altitude Profile

The overlay of all six aircraft's sawtooth climb-descend patterns from 5,000 ft to their respective ceilings. Key features:

- **GV reaches highest:** Peaks at 47,000 ft on later cycles, consistent with its high-altitude design and light weight per aircraft.
- **767 middle of pack:** 41,000–43,000 ft ceiling range, with visible progression.
- **P-8 lowest ceiling:** 38,000–40,000 ft range.
- **Cycle count varies:** GV completes 16 cycles (widest sawtooth), DC-8 completes 21 (narrowest).

The plot is dense because six sawtooth profiles overlap. The companion ceiling progression plot (below) extracts the key metric more clearly.

### Mission 2: Progressive Ceiling Chart

This is the most scientifically significant plot for Mission 2. It shows each aircraft's achievable ceiling altitude on each successive climb-descend cycle:

- **GV:** 44,000 → 47,000 ft (+3,000 ft progression over 16 cycles)
- **767-200ER:** 41,000 → 43,000 ft (+2,000 ft over 18 cycles)
- **P-8:** 38,000 → 40,000 ft (+2,000 ft over 14 cycles)
- **DC-8:** Flat at 42,000 ft (21 cycles) — likely calibration artifact (k_adj=0.605 means too little fuel burn, so the aircraft doesn't get light enough for the thrust-limited ceiling to rise)
- **777-200LR:** Flat at 43,100 ft (17 cycles) — so much thrust that the service ceiling (structural/pressurization cap) governs from cycle 1
- **A330-200:** Flat at 41,100 ft (19 cycles) — unphysical e=2.165 makes the drag model unreliable

The progressive ceiling increase directly addresses the scientists' top priority: "flying higher is the single most desirable capability improvement." The GV's 47,000 ft peak is the strongest argument for a small-aircraft fleet approach, while the 767's 43,000 ft demonstrates it can exceed the DC-8's current altitude capability.

---

## Consolidated Fuel Cost Table (Deliverable 4)

This data exists in the per-mission reports and is consolidated here for cross-mission comparison. No separate plot was produced — this is a table deliverable.

### Fuel Cost per 1,000 lb of Payload per Nautical Mile ($/klb-nm)

| Aircraft | n | Mission 1 | n | Mission 2 | n | Mission 3 |
|---|---|---|---|---|---|---|
| DC-8 | 1 | $0.43 | 1 | $0.44 | 1 | $0.61 |
| GV | 8 | $1.03† | 9 | $1.24† | 6 | $1.92† |
| P-8 | 2 | $0.52† | 3 | $0.83† | 2 | $1.02† |
| **767-200ER** | **1** | **$0.57** | **1** | **$0.61** | **1** | **$1.32** |
| A330-200 | 1 | $0.78 | 1 | $0.81 | 1 | $2.28 |
| 777-200LR | 1 | $1.15 | 1 | $1.22 | 1 | $1.76 |

†Fleet aggregate cost (total fleet fuel cost / total payload / distance)

**Notes:**
- DC-8 costs are unreliable (k_adj=0.605 produces ~40% underburn).
- Mission 1 costs include all loaded fuel (f_oh model); Missions 2-3 use explicit reserves + mission fuel.
- Mission 3 uses mission-sized fuel loading (iterative sizing for 8 hr + reserves).
- The 767 is consistently the cheapest single-aircraft option with reliable numbers across all three missions.
- The P-8 fleet is competitive on Missions 2-3 but fails Mission 1.

---

## Implementation Notes

### Data Flow
The synthesis plots draw from the same mission simulation functions used in the Phase 2 reports:
- `simulate_mission1_engine_out()` → segment-level step data
- `simulate_mission2_sampling()` → cycle details + profile_points
- `simulate_mission3_low_altitude()` → time-stepping endurance data

No new calculations are performed. The plotting code only extracts and visualizes data already computed in the mission result dicts.

### Code Organization
```
src/plotting/
    range_payload.py      # Existing: R-P diagrams (Deliverable 1)
    weight_breakdown.py   # New: stacked bar charts (Deliverable 3)
    mission_profiles.py   # New: altitude/Mach/ceiling plots (Deliverable 5)

src/analysis/
    run_plots.py              # Existing: R-P plot driver
    run_synthesis_plots.py    # New: Deliverable 3+5 driver
```

### Shared Constants
Aircraft colors and markers are defined in `range_payload.py` and imported by the new modules for visual consistency across all plots.

---

## Questions for Reviewer

1. **Mission 2 sawtooth overlay readability:** The 6-aircraft overlay is dense. Should we also produce individual sawtooth plots per aircraft, or is the overlay + ceiling progression chart sufficient?

2. **Weight breakdown fuel decomposition for Mission 1:** The f_oh model bundles taxi/climb/descent/reserves into a single overhead term, making the "reserve fuel" bar represent something different than for Missions 2-3. Should we add a note on the plot, use different labels, or is the current approach acceptable?

3. **Mission 1 altitude profile — 10,000 ft floor:** The drop to 10,000 ft for P-8/A330/777 is a model artifact. Should we annotate this on the plot, omit those aircraft from the altitude plot, or show them but note the artifact in the caption?

4. **Additional plots:** Are there any other visualizations that would strengthen the final report? Possibilities include:
   - Fuel cost bar chart (grouped by mission)
   - Mission 3 fuel flow vs. time (shows weight-dependent burn rate decrease)
   - Range-payload overlay with mission requirements highlighted (already exists but could be enhanced)
