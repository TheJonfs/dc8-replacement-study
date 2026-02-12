# Synthesis Plots Report — Deliverables 3, 4, and 5

## Overview

This report documents the generation of the remaining CLAUDE.md plot deliverables: weight breakdown stacked bar charts (Deliverable 3), fuel cost comparison chart and table (Deliverable 4), and speed/altitude profile plots (Deliverable 5). All data is drawn from the same calibrated mission simulations used in the Phase 2 mission reports.

All plots are reproducible via:
```
python3 -m src.analysis.run_synthesis_plots
```

Source files:
- `src/plotting/weight_breakdown.py` — stacked bar chart generation
- `src/plotting/mission_profiles.py` — altitude/Mach/ceiling progression plots
- `src/plotting/fuel_cost.py` — fuel cost grouped bar chart
- `src/analysis/run_synthesis_plots.py` — driver script

---

## Deliverable 3: Weight Breakdown Stacked Bar Charts

Three plots, one per mission. Each shows the six study aircraft side by side with stacked bars decomposed into OEW, payload, mission fuel, and reserve/remaining fuel. For the GV and P-8, additional hatched bars show fleet aggregate values.

### Output Files
| File | Mission |
|---|---|
| `outputs/plots/weight_breakdown_m1.png` | Mission 1: Engine-Out Transport |
| `outputs/plots/weight_breakdown_m2.png` | Mission 2: Vertical Sampling |
| `outputs/plots/weight_breakdown_m3.png` | Mission 3: Low-Altitude Smoke Survey |

### Design Decisions

**Fuel decomposition labels vary by mission** (per reviewer feedback):
- **Mission 1:** The top fuel band is labeled **"Remaining Fuel"** — unburned cruise fuel after the f_oh hybrid model allocates non-cruise overhead. This is not a pre-allocated reserve; it represents surplus range capability.
- **Missions 2-3:** The top fuel band is labeled **"Reserve Fuel"** — pre-allocated explicit reserves (5% contingency + 200 nm alternate + 30 min hold).

Each chart includes a one-line fuel budget note below the x-axis explaining the method used.

**Fleet aggregate bars:** Displayed with diagonal hatch patterns and labeled with fleet size (e.g., "GV (8x fleet)"). All weights are multiplied by n_aircraft.

**Total weight annotation:** Each bar is topped with the total weight in thousands of pounds.

### Key Observations

**Mission 1:** The 767 (387k lb) is the only aircraft with high-confidence feasibility. The GV 8x fleet aggregate (724k lb) is nearly double the 767, illustrating the resource penalty of fleet operations on a demanding mission.

**Mission 2:** The GV 9x fleet (814k lb aggregate) and P-8 3x fleet (545k lb) highlight the impracticality of using small aircraft for heavy payload missions. The 767 (393k lb) is the most efficient single-aircraft solution.

**Mission 3:** Dramatically different due to mission-sized fuel loading. The DC-8 loads only 44k lb of fuel (vs. 147k lb capacity); the 767 loads 96k lb (vs. 162k lb capacity). Aircraft are not penalized for having large tanks they don't need to fill.

---

## Deliverable 4: Fuel Cost Comparison

### Grouped Bar Chart

| File | Content |
|---|---|
| `outputs/plots/fuel_cost_comparison.png` | $/klb-nm across all missions, FAIL/? for infeasible aircraft |

The chart shows $/klb-nm for each aircraft grouped by mission. Key design decisions following reviewer feedback:

**Failed missions are shown as gray hatched stubs labeled "FAIL"** rather than reporting a cost value. The cost of an incomplete mission is not a meaningful comparison metric.

**UNCERTAIN status** (A330-200 on Mission 1) is shown as a dotted stub with "?" — calibration quality is too poor to assess feasibility, so neither PASS nor FAIL can be assigned.

**Fleet sizes** are annotated on multi-aircraft bars (e.g., "(9x)" for the GV fleet on Mission 2).

**Footnote** reminds the reader that DC-8 costs are unreliable due to k_adj=0.605.

### Consolidated Fuel Cost Table ($/klb-nm)

| Aircraft | n | Mission 1 | n | Mission 2 | n | Mission 3 |
|---|---|---|---|---|---|---|
| DC-8 | 1 | FAIL | 1 | $0.44* | 1 | $0.61* |
| GV | 8 | FAIL | 9 | $1.24† | 6 | $1.92† |
| P-8 | 2 | FAIL | 3 | $0.83† | 2 | $1.02† |
| **767-200ER** | **1** | **$0.57** | **1** | **$0.61** | **1** | **$1.32** |
| A330-200 | 1 | UNCERTAIN | 1 | $0.81 | 1 | $2.28 |
| 777-200LR | 1 | $1.15‡ | 1 | $1.22 | 1 | $1.76 |

*DC-8 costs unreliable (k_adj=0.605 produces ~40% underburn)
†Fleet aggregate cost (total fleet fuel cost / total payload / distance)
‡LIKELY PASS — model suggests feasibility but calibration is low confidence

**Key takeaway:** The 767 is the cheapest single-aircraft option with reliable numbers on every mission it passes ($0.57–$1.32/klb-nm). The P-8 fleet is competitive on Missions 2-3 ($0.83–$1.02) but cannot complete Mission 1.

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

The altitude plot shows all six aircraft on a single overlay with a vertical engine failure marker at 2,525 nm and a destination marker at KPMD (5,050 nm).

**Key features:**
1. **Pre-failure cruise (0–2,525 nm):** Aircraft cruise at 33–45k ft with gradual step-climbs as fuel burns off. The GV cruises highest (43–46k ft).
2. **Engine failure discontinuity (2,525 nm):** The 767, DC-8, and GV (physical CD0 values) show moderate altitude adjustments. The P-8, A330, and 777 (unphysical CD0) drop to the 10,000 ft floor.
3. **Post-failure continuation:** Only the 767 reaches and passes KPMD with surplus range.

**Calibration artifact annotation** (per reviewer feedback): The 10,000 ft floor for P-8, A330, and 777 is annotated directly on the plot with a text box stating "Calibration artifact — P-8, A330-200, 777-200LR drop to altitude floor due to unphysical CD₀ (see report)." The lines are preserved to show what the model produces, with honest annotation about what to trust.

### Mission 1: Mach Profile

Mach is constant throughout the mission for each aircraft (the model holds cruise Mach constant and adjusts altitude). The plot shows different operating points: 777 at Mach 0.84, DC-8/A330/GV at 0.82, 767 at 0.80, P-8 at 0.785.

### Mission 2: Sawtooth Altitude Profile

Overlay of all six aircraft's sawtooth patterns from 5,000 ft to their respective ceilings. The GV reaches highest (47k ft), the P-8 lowest (38–40k ft). The plot is dense by nature; the companion ceiling progression chart extracts the key metric more clearly.

### Mission 2: Progressive Ceiling Chart

The most scientifically significant plot in the study (per reviewer assessment). Shows each aircraft's achievable ceiling on each successive climb-descend cycle:

- **GV:** 44,000 → 47,000 ft (+3,000 ft progression)
- **767-200ER:** 41,000 → 43,000 ft (+2,000 ft)
- **P-8:** 38,000 → 40,000 ft (+2,000 ft)
- **DC-8, 777, A330:** Flat ceilings (calibration artifacts or excess thrust)

The progressive ceiling increase directly addresses the scientists' top priority: flying higher. The GV's 47,000 ft peak is the strongest argument for a fleet approach; the 767's 43,000 ft exceeds the DC-8's current capability.

---

## Changes from Reviewer Feedback

The following changes were made in response to expert review:

| Issue | Resolution |
|---|---|
| Fuel cost table included failed aircraft costs | Replaced with FAIL/UNCERTAIN status; costs only shown for aircraft that can complete the mission |
| Mission 1 "Reserve Fuel" label misleading | Relabeled to "Remaining Fuel" for Mission 1; "Reserve Fuel" retained for Missions 2-3 |
| 10,000 ft floor in altitude plot could be misread | Added annotation box identifying calibration artifact and affected aircraft |
| No fuel cost visualization | Added grouped bar chart with FAIL stubs, fleet size annotations, and footnotes |
| No fuel budget method indicated on weight charts | Added one-line italic note below each weight breakdown chart |

---

## Code Organization

```
src/plotting/
    range_payload.py      # Existing: R-P diagrams (Deliverable 1)
    weight_breakdown.py   # Stacked bar charts (Deliverable 3)
    fuel_cost.py          # Fuel cost grouped bars (Deliverable 4)
    mission_profiles.py   # Altitude/Mach/ceiling plots (Deliverable 5)

src/analysis/
    run_plots.py              # Existing: R-P plot driver
    run_synthesis_plots.py    # Deliverables 3+4+5 driver
```

All plots are generated from mission result dicts — no new calculations are performed. Aircraft colors and markers are shared from `range_payload.py` for visual consistency.
