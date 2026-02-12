# 8. Cross-Mission Synthesis

## 8.1 Feasibility Summary

| Aircraft | Mission 1 | Mission 2 | Mission 3 |
|---|---|---|---|
| DC-8-72 | FAIL | PASS | PASS |
| GV | FAIL | PASS | PASS |
| P-8 | FAIL | PASS | PASS |
| **767-200ER** | **PASS** | **PASS** | **PASS** |
| A330-200 | UNCERTAIN | PASS (marginal) | PASS |
| 777-200LR | LIKELY PASS | PASS | PASS |

The 767-200ER is the only aircraft that passes all three missions with high model confidence. The 777-200LR likely passes all three but its model confidence is low. The DC-8, GV, and P-8 all fail Mission 1, confirming that the demanding engine-out transport scenario is the most discriminating test.

## 8.2 Fuel Cost Efficiency Comparison

Figure 15 shows the fuel cost comparison across all three missions.

<!-- Figure reference: outputs/plots/fuel_cost_comparison.png -> Figure 15 -->

### 8.2.1 Consolidated Cost Table ($/klb-nm)

| Aircraft | n | Mission 1 | n | Mission 2 | n | Mission 3 |
|---|---|---|---|---|---|---|
| DC-8 | 1 | FAIL | 1 | $0.44* | 1 | $0.61* |
| GV | 8 | FAIL | 9 | $1.24 | 6 | $1.92 |
| P-8 | 2 | FAIL | 3 | $0.83 | 2 | $1.02 |
| **767-200ER** | **1** | **$0.57** | **1** | **$0.61** | **1** | **$1.32** |
| A330-200 | 1 | UNCERTAIN | 1 | $0.81 | 1 | $2.28 |
| 777-200LR | 1 | $1.15** | 1 | $1.22 | 1 | $1.76 |

*DC-8 costs unreliable ($k_{\text{adj}} = 0.605$, approximately 40% underburn). **LIKELY PASS; low confidence.

The 767 is consistently the cheapest single-aircraft option with reliable numbers: $0.57--$1.32/klb-nm across all missions. Its cost range spans a factor of 2.3x from the most efficient mission (Mission 1) to the least efficient (Mission 3), reflecting the transition from near-optimal cruise to severely off-design low-altitude conditions.

The P-8 fleet offers competitive costs on Missions 2 and 3 ($0.83 and $1.02/klb-nm respectively) but cannot address Mission 1. The GV fleet is the most expensive option on every mission it can complete.

### 8.2.2 Cost Drivers

Three factors drive the cost differences:

1. **OEW-to-payload ratio**: The weight the aircraft carries for its own structure relative to the science payload. The 767 carries 179,080 lb of structure for up to 80,920 lb of payload (ratio 2.2:1). The 777 carries 320,000 lb for up to 135,000 lb (2.4:1). The A330 carries 265,900 lb for up to 108,908 lb (2.4:1). Lower ratios mean less fuel consumed hauling structure.

2. **Aerodynamic efficiency**: The aircraft's L/D ratio at mission conditions. At cruise altitude, the 767 achieves L/D of approximately 16.1. At low altitude (Mission 3), L/D drops to 15.6 for the 767 but only 7.4 for the P-8 (driven by its unphysical $C_{D_0}$).

3. **Engine efficiency**: The TSFC at operating conditions. The 767's CF6-80C2B2 engines with $k_{\text{adj}} = 0.951$ indicate that the published TSFC is a good predictor of actual consumption. Aircraft with low $k_{\text{adj}}$ values (DC-8 at 0.605, P-8 at 0.339) have artificially low fuel consumption in the model.

## 8.3 Fleet vs. Single-Aircraft Operations

The GV and P-8 require multi-aircraft fleets for missions with payloads exceeding their individual capacity:

| Mission | GV Fleet | P-8 Fleet | 767 Single |
|---|---|---|---|
| Mission 1 (46,000 lb) | 8 aircraft (FAIL) | 2 aircraft (FAIL) | 1 aircraft (PASS) |
| Mission 2 (52,000 lb) | 9 aircraft | 3 aircraft | 1 aircraft |
| Mission 3 (30,000 lb) | 6 aircraft | 2 aircraft | 1 aircraft |

Fleet operations impose costs beyond fuel:
- **Coordination complexity**: Multiple aircraft must be scheduled, maintained, and crewed simultaneously.
- **Aggregate weight penalty**: OEW is multiplied by fleet size. The GV 9x fleet aggregate OEW (433,800 lb) exceeds the 777's single-aircraft OEW (320,000 lb).
- **Scientific coordination**: Measurements from multiple aircraft must be temporally and spatially coordinated, adding data processing complexity.
- **Infrastructure**: Each aircraft requires ground handling, maintenance, and crew accommodations.

The P-8 fleet (2-3 aircraft) is more operationally feasible than the GV fleet (6-9 aircraft), but both impose substantially more logistical overhead than a single-aircraft solution.

## 8.4 Aircraft Ranking

Based on the quantitative analysis, the candidates rank as follows:

1. **Boeing 767-200ER**: Only aircraft passing all missions with high confidence. Best single-aircraft cost efficiency on reliable numbers. Adequate altitude capability (43,100 ft peak).

2. **Boeing P-8 Poseidon**: Competitive fleet-based costs on Missions 2-3. Fails Mission 1. Fleet size (2-3 aircraft) is operationally feasible.

3. **Boeing 777-200LR**: Likely passes all missions but at approximately double the 767's cost. Massive capability exceeds mission requirements. Low model confidence.

4. **Airbus A330-200**: High OEW drives highest Mission 3 cost ($2.28/klb-nm). Uncertain Mission 1 status. Low model confidence.

5. **Gulfstream G-V**: Highest altitude capability (47,000 ft) but fleet sizes of 6-9 aircraft are operationally impractical for routine campaign use.

6. **Douglas DC-8-72**: Fails Mission 1. Cost numbers unreliable. Confirms replacement need.
