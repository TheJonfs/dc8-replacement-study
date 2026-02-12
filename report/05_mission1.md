# 5. Mission 1: Long-Range Transport with Engine-Out

## 5.1 Mission Definition

| Parameter | Value |
|---|---|
| Route | Santiago, Chile (SCEL) to Palmdale, CA (KPMD) |
| Distance | 5,050 nm |
| Payload | 46,000 lb |
| Profile | Nominal cruise with engine failure at midpoint |
| Engine failure | Single engine loss at 2,525 nm |

This mission is the most demanding in the study. It combines a long range requirement (5,050 nm) with a heavy payload (46,000 lb) and the additional challenge of completing the second half of the mission on reduced thrust. The mission directly addresses the engine-out concern raised by scientists: can the aircraft safely complete a long over-water transit after losing an engine at the worst possible point?

The fuel budget uses the $f_{oh}$ hybrid model, in which non-cruise fuel overhead (taxi, climb, descent, reserves) is captured by the calibrated overhead fraction.

## 5.2 Results

### 5.2.1 Feasibility Assessment

| Aircraft | Status | Confidence | n | Fuel at Dest. (lb) | Range Achieved (nm) |
|---|---|---|---|---|---|
| **767-200ER** | **PASS** | **High** | 1 | 25,732 | >5,050 |
| 777-200LR | LIKELY PASS | Low | 1 | --- | >5,050* |
| A330-200 | UNCERTAIN | Low | 1 | --- | --- |
| GV | FAIL | Medium | 8 | --- | 4,855 |
| P-8 | FAIL | Low | 2 | --- | 3,276 |
| DC-8-72 | FAIL | Low | 1 | --- | 3,187 |

*Model suggests feasibility but calibration artifacts ($C_{D_0} = 0.041$) make the engine-out segment unreliable.

The **767-200ER is the only aircraft that demonstrably passes** Mission 1 with high model confidence. It arrives at KPMD with 25,732 lb of cruise fuel remaining --- a substantial margin that provides additional reserves or diversion capability.

The 777-200LR is assessed as LIKELY PASS: the model produces a feasible result, but the unphysical calibration parameters (particularly the inflated $C_{D_0}$) make the engine-out altitude and fuel consumption predictions unreliable. In reality, the 777's massive GE90 engines likely provide adequate single-engine performance for this mission, but the model cannot confirm this with confidence.

The DC-8 fails by 1,863 nm, confirming the motivation for this study: the current platform cannot complete demanding long-range missions with engine contingencies.

### 5.2.2 Weight Breakdown

The weight breakdown for Mission 1 is shown in Figure 8.

<!-- Figure reference: outputs/plots/weight_breakdown_m1.png -> Figure 8 -->

Key observations:
- The 767-200ER (387,000 lb takeoff weight) carries 46,000 lb of payload and 162,000 lb of fuel while remaining within its 395,000 lb MTOW.
- The GV requires 8 aircraft at 91,000 lb each, with an aggregate fleet weight of 724,000 lb --- nearly double the single 767.
- The 777-200LR's 691,000 lb takeoff weight reflects its much higher OEW (320,000 lb), which imposes a fuel consumption penalty even though the aircraft has ample range capability.

### 5.2.3 Altitude and Speed Profiles

Figure 9 shows the altitude profile for all six aircraft. Figure 10 shows the Mach profile.

<!-- Figure references:
outputs/plots/profile_m1_altitude.png -> Figure 9
outputs/plots/profile_m1_mach.png     -> Figure 10
-->

The altitude profile reveals the engine-out discontinuity at 2,525 nm:

- **767-200ER**: Cruises at 35,000--38,000 ft pre-failure. After engine loss, descends to approximately 33,000 ft and gradually climbs back to 38,000 ft as fuel burns off. Crosses KPMD at 5,050 nm with ample range remaining.
- **GV**: Cruises highest pre-failure (43,000--46,000 ft, exploiting its high service ceiling). After engine loss, descends to approximately 37,000 ft. However, it exhausts fuel before reaching KPMD.
- **DC-8**: The four-engine configuration loses only 25% of thrust (versus 50% for twin-engine aircraft), resulting in a more modest altitude drop. However, its total fuel load is insufficient for the 5,050 nm distance.
- **P-8, A330-200, 777-200LR**: These aircraft drop to the 10,000 ft altitude floor after engine failure. This is a calibration artifact: their unphysical $C_{D_0}$ values (0.034--0.060) produce drag that exceeds available thrust on one engine at all cruise altitudes. Real aircraft of these types are ETOPS-certified for extended single-engine flight at normal altitudes.

The Mach profile shows constant cruise Mach for each aircraft (the model optimizes altitude rather than speed): 777-200LR at Mach 0.84, DC-8/A330/GV at 0.82, 767 at 0.80, and P-8 at 0.785.

## 5.3 Fuel Cost

| Aircraft | Status | n | Total Fuel Cost | $/klb-nm |
|---|---|---|---|---|
| **767-200ER** | **PASS** | 1 | $132,985 | **$0.57** |
| 777-200LR | LIKELY PASS | 1 | $267,037 | $1.15 |
| DC-8 | FAIL | 1 | --- | --- |
| GV | FAIL | 8 | --- | --- |
| P-8 | FAIL | 2 | --- | --- |
| A330-200 | UNCERTAIN | 1 | --- | --- |

Cost metrics are reported only for aircraft that can complete the mission. The 767's $0.57/klb-nm is the benchmark; the 777's $1.15/klb-nm is approximately double, reflecting its higher OEW and fuel consumption.

## 5.4 Engine-Out: Two-Engine vs. Four-Engine

Mission 1 was designed to probe the engine redundancy concern raised by scientists. The results illuminate the trade-off:

- The DC-8 retains 75% of thrust after losing one of four engines, experiencing only a modest altitude drop. However, it fails the mission on range --- it simply cannot carry enough fuel.
- The 767 loses 50% of thrust but maintains cruise altitude above 33,000 ft and completes the mission with substantial reserves. Its higher fuel capacity and more efficient engines compensate for the greater thrust loss.

The conclusion is that for this mission profile, fuel capacity and engine efficiency matter more than engine count. A twin-engine aircraft with adequate range capability outperforms a four-engine aircraft with insufficient fuel capacity, even in an engine-out scenario.
