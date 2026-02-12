# 7. Mission 3: Low-Altitude Smoke Survey

## 7.1 Mission Definition

| Parameter | Value |
|---|---|
| Region | Central United States (Arkansas-Missouri area) |
| Duration | 8 hours |
| Payload | 30,000 lb |
| Altitude | 1,500 ft above ground level |
| Speed | 250 KTAS (Mach 0.38) |
| Fuel budget | Explicit reserves + iterative mission-sized loading |

This mission represents extended low-altitude operations for forest fire particulate sampling. Unlike Missions 1 and 2, the constraint is time rather than distance: the aircraft must sustain 8 hours of flight at low altitude with the specified payload. The slow speed (250 KTAS, well below cruise Mach for all candidates) and low altitude (1,500 ft, far below optimal cruise altitude) represent severely off-design operating conditions.

## 7.2 Mission-Sized Fuel Loading

A critical modeling decision for Mission 3 is fuel loading. If aircraft carry maximum fuel, the large-tank aircraft (777-200LR with 325,300 lb capacity, A330-200 with 245,264 lb) are heavily penalized: the extra fuel weight increases drag and fuel consumption, creating a self-reinforcing weight spiral.

The solution is iterative mission-sized fuel loading. Each aircraft loads only enough fuel for the 8-hour mission plus reserves:

| Aircraft | Max Fuel (lb) | Mission Fuel Loaded (lb) | Utilization |
|---|---|---|---|
| DC-8 | 147,255 | 44,496 | 30% |
| GV | 41,300 | 23,393 | 57% |
| P-8 | 73,320 | 37,321 | 51% |
| 767-200ER | 162,000 | 96,124 | 59% |
| A330-200 | 245,264 | 166,342 | 68% |
| 777-200LR | 325,300 | 128,747 | 40% |

All aircraft converged within 5-8 iterations of the fuel sizing algorithm (tolerance: 50 lb). The impact is dramatic for the 777-200LR: without mission-sized loading, its cost metric would be $4.45/klb-nm; with it, the cost drops to $1.76/klb-nm --- a 60% reduction.

## 7.3 Results

### 7.3.1 Feasibility Assessment

All six aircraft pass Mission 3. This is the least discriminating mission: the 30,000 lb payload and 8-hour endurance requirement are within the capability of all candidates.

| Aircraft | Confidence | n | Fuel Burned (lb) | Avg Flow (lb/hr) | Endurance (hr) |
|---|---|---|---|---|---|
| DC-8* | Low | 1 | 36,233 | 4,529 | 8.0 |
| GV | Medium | 6 | 18,938 ea | 2,367 ea | 8.0 |
| P-8 | Low | 2 | 30,244 ea | 3,780 ea | 8.0 |
| **767-200ER** | **High** | 1 | 78,921 | 9,865 | 8.0 |
| A330-200 | Low | 1 | 133,649 | 16,706 | 8.0 |
| 777-200LR | Low | 1 | 102,996 | 12,874 | 8.0 |

*DC-8 burn rate approximately 40% below reality due to $k_{\text{adj}} = 0.605$.

### 7.3.2 Weight Breakdown

Figure 14 shows the weight breakdown for Mission 3.

<!-- Figure reference: outputs/plots/weight_breakdown_m3.png -> Figure 14 -->

The mission-sized fuel loading is immediately visible: fuel fractions are much smaller relative to OEW than in Missions 1-2. The DC-8's fuel band (44,500 lb) is notably thin compared to its 147,255 lb capacity. The GV 6x fleet aggregate (460,000 lb) remains larger than the single 767 (305,000 lb) and A330 (462,000 lb), reinforcing the fleet weight penalty.

### 7.3.3 Low-Altitude Aerodynamics

Operating at 1,500 ft and Mach 0.38 places all aircraft far below their design cruise conditions. At these conditions, parasite drag ($C_{D_0}$) dominates:

| Aircraft | $C_L$ | $C_D$ | L/D | $C_{D_0}/C_D$ |
|---|---|---|---|---|
| DC-8 | 0.399 | 0.023 | 17.6 | 62% |
| GV | 0.333 | 0.021 | 15.8 | 71% |
| P-8 | 0.527 | 0.071 | 7.4 | 84% |
| 767-200ER | 0.494 | 0.032 | 15.6 | 56% |
| A330-200 | 0.587 | 0.038 | 15.3 | 87% |
| 777-200LR | 0.503 | 0.047 | 10.6 | 87% |

For aircraft with unphysical $C_{D_0}$ (P-8, A330, 777), the parasite drag fraction exceeds 84%, meaning their fuel burn is dominated by the calibration artifact rather than physics. The DC-8 and 767 have more balanced drag polars, with the 767 showing the lowest parasite drag fraction (56%) and a healthy L/D of 15.6.

## 7.4 Fuel Cost

| Aircraft | n | Total Fuel Cost | $/klb-nm |
|---|---|---|---|
| DC-8* | 1 | $36,527 | $0.61 |
| GV | 6 | $115,218 | $1.92 |
| P-8 | 2 | $61,273 | $1.02 |
| **767-200ER** | **1** | **$78,907** | **$1.32** |
| A330-200 | 1 | $136,549 | $2.28 |
| 777-200LR | 1 | $105,688 | $1.76 |

*DC-8 cost unreliable (approximately 40% underburn).

Mission 3 costs are higher per klb-nm than Missions 1-2 because low-altitude flight at slow speed is inherently less fuel-efficient than optimized high-altitude cruise. The 767 at $1.32/klb-nm is the best single-aircraft option with reliable numbers. The P-8 fleet at $1.02/klb-nm is competitive and demonstrates the P-8's strength on shorter, less demanding missions.

## 7.5 Implications

Mission 3 does not discriminate among candidates on feasibility --- all pass. The discrimination is on cost:

- The **767** has the best reliable single-aircraft cost efficiency.
- The **P-8 fleet** (2 aircraft) is cheaper per unit of science delivered, though at the cost of operating two platforms.
- The **A330** is the most expensive option ($2.28/klb-nm) due to its high OEW driving fuel consumption even with mission-sized loading.
- The **777** benefits substantially from mission-sized loading but remains more expensive than the 767.

The key takeaway for Mission 3 is that aircraft size does not determine cost efficiency in a simple way. The mission-sized fuel loading equalizes the playing field, and the dominant cost driver becomes the aircraft's OEW-to-payload ratio and aerodynamic efficiency at off-design conditions.
