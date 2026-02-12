# 6. Mission 2: Vertical Atmospheric Sampling

## 6.1 Mission Definition

| Parameter | Value |
|---|---|
| Route | Christchurch, New Zealand (NZCH) to Punta Arenas, Chile (SCCI) |
| Distance | 4,200 nm |
| Payload | 52,000 lb |
| Profile | Repeating climb-descend cycles (5,000 ft to ceiling) |
| Fuel budget | Explicit reserves (5% + 200 nm alternate + 30 min hold) |

This mission exercises the aircraft's ability to perform vertical atmospheric column sampling --- a core DC-8 science capability. The aircraft repeatedly climbs from 5,000 ft to its thrust-limited ceiling and descends back, with each cycle sampling the full atmospheric column. As fuel burns off and the aircraft lightens, it becomes capable of reaching progressively higher altitudes on successive cycles.

This profile directly addresses the scientists' top priority: "flying higher is the single most desirable capability improvement."

## 6.2 Results

### 6.2.1 Feasibility Assessment

All six aircraft pass Mission 2:

| Aircraft | Confidence | n | Cycles | Init. Ceiling (ft) | Peak Ceiling (ft) | Progression |
|---|---|---|---|---|---|---|
| DC-8 | Low | 1 | 21 | 42,000 | 42,000 | Flat |
| GV | Medium | 9 | 16 | 44,000 | 47,000 | +3,000 ft |
| P-8 | Low | 3 | 14 | 38,000 | 40,000 | +2,000 ft |
| **767-200ER** | **High** | 1 | 18 | 41,000 | 43,100 | **+2,100 ft** |
| A330-200 | Low | 1 | 19 | 41,100 | 41,100 | Flat |
| 777-200LR | Low | 1 | 17 | 43,100 | 43,100 | Flat |

Mission 2 is less discriminating than Mission 1 --- all aircraft can complete it --- but the quality of the science output varies significantly.

### 6.2.2 Progressive Ceiling Analysis

The progressive ceiling chart (Figure 11) is the most scientifically significant visualization in this study. It shows how each aircraft's achievable ceiling evolves across successive climb-descend cycles.

<!-- Figure reference: outputs/plots/profile_m2_ceiling.png -> Figure 11 -->

Three aircraft exhibit meaningful progressive ceiling increase:

- **GV**: From 44,000 to 47,000 ft (+3,000 ft over 16 cycles). The GV reaches the highest altitude of any candidate, but requires a fleet of 9 aircraft.
- **767-200ER**: From 41,000 to 43,100 ft (+2,100 ft over 18 cycles). The 767 demonstrates progressive capability gain with high-confidence results.
- **P-8**: From 38,000 to 40,000 ft (+2,000 ft over 14 cycles). The P-8's ceiling is artificially depressed by its unphysical $C_{D_0}$; the real P-8 ceiling of 41,000 ft would likely show higher values.

Three aircraft show flat ceilings:

- **DC-8**: Flat at 42,000 ft across all 21 cycles. This is likely a calibration artifact: the $k_{\text{adj}} = 0.605$ produces ~40% underburn, so the aircraft does not get light enough fast enough for the ceiling to rise within the mission.
- **777-200LR**: Flat at 43,100 ft across 17 cycles. The 777 has so much thrust that its service ceiling (a structural/pressurization limit, not thrust-limited) governs from cycle 1.
- **A330-200**: Flat at 41,100 ft across 19 cycles. The unphysical $e = 2.165$ makes the drag model unreliable at altitude.

### 6.2.3 Altitude Profile

The sawtooth altitude profile (Figure 12) shows the raw climb-descend pattern for all six aircraft overlaid.

<!-- Figure reference: outputs/plots/profile_m2_altitude.png -> Figure 12 -->

The profile is visually dense because six overlaid sawtooth patterns create many intersections. The ceiling progression chart (Figure 11) extracts the key metric more clearly and should be preferred for decision-making.

### 6.2.4 Weight Breakdown

Figure 13 shows the weight breakdown for Mission 2.

<!-- Figure reference: outputs/plots/weight_breakdown_m2.png -> Figure 13 -->

The GV 9x fleet aggregate (814,000 lb) exceeds any single aircraft, illustrating the resource penalty of fleet operations. The P-8 3x fleet (545,000 lb) is comparable to the A330 (534,000 lb). The 767 (393,000 lb) is the lightest single-aircraft solution capable of carrying the full 52,000 lb payload.

## 6.3 Fuel Cost

| Aircraft | n | Total Fuel Cost | $/klb-nm |
|---|---|---|---|
| DC-8* | 1 | $95,224 | $0.44 |
| GV | 9 | $269,828 | $1.24 |
| P-8 | 3 | $180,564 | $0.83 |
| **767-200ER** | **1** | **$132,985** | **$0.61** |
| A330-200 | 1 | $177,001 | $0.81 |
| 777-200LR | 1 | $267,037 | $1.22 |

*DC-8 cost unreliable due to $k_{\text{adj}} = 0.605$ (approximately 40% underburn).

The 767 offers the best cost efficiency among aircraft with reliable calibrations ($0.61/klb-nm). The DC-8 appears cheapest ($0.44/klb-nm) but this figure is artificially low.

## 6.4 Scientific Value Assessment

From a science mission perspective, the key question is not just "can the aircraft complete the mission" but "how much useful data does it collect?" The relevant factors are:

1. **Peak altitude**: Higher ceilings sample more of the atmospheric column. The GV wins (47,000 ft), followed by the 767 and 777 (43,100 ft).
2. **Progressive ceiling**: Aircraft that reach higher altitudes on later cycles sample the upper atmosphere when instruments have been fully characterized during lower-altitude cycles. The GV, 767, and P-8 show this behavior.
3. **Number of cycles**: More cycles provide more vertical profiles. The DC-8 leads (21 cycles), followed by the A330 (19) and 767 (18).
4. **Single-aircraft operation**: All payloads on one aircraft allows coordinated measurements. Only the DC-8, 767, A330, and 777 can carry the full 52,000 lb.

The 767 provides the best combination: progressive ceiling (41,000 to 43,100 ft), adequate cycle count (18), single-aircraft payload capacity, and high-confidence model results.
