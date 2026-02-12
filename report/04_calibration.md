# 4. Calibration Results

## 4.1 Calibration Procedure

Each aircraft model is calibrated by adjusting four parameters to minimize the root-mean-square error between predicted and published ranges at three corner points of the range-payload diagram:

1. **Maximum payload** with fuel to MTOW
2. **Maximum fuel** with payload to MTOW
3. **Maximum fuel** with zero payload (ferry)

The four calibration parameters are:

- **$C_{D_0}$** --- zero-lift drag coefficient
- **$e$** --- Oswald efficiency factor
- **$k_{\text{adj}}$** --- TSFC adjustment multiplier
- **$f_{oh}$** --- non-cruise fuel overhead fraction

Optimization uses differential evolution (a global optimizer) followed by Nelder-Mead refinement. The P-8 is not calibrated independently; it is derived from the calibrated 737-900ER model with modifications to OEW, fuel capacity, and Oswald efficiency reflecting the raked wingtip installation.

## 4.2 Results

| Aircraft | $C_{D_0}$ | $e$ | $k_{\text{adj}}$ | $f_{oh}$ | L/D max | RMS Error | Converged |
|---|---|---|---|---|---|---|---|
| DC-8-72 | 0.0141 | 0.968 | 0.605 | 0.260 | 20.4 | 0.5% | Yes |
| G-V | 0.0150 | 0.745 | 0.801 | 0.131 | 17.3 | 1.2% | Yes |
| 737-900ER | 0.0355 | 1.223 | 0.757 | 0.062 | 16.7 | 0.7% | Yes |
| P-8 | 0.0597 | 0.975 | 0.339 | 0.180 | 11.5 | 0.0% | Yes* |
| 767-200ER | 0.0177 | 0.732 | 0.951 | 0.030 | 16.1 | 0.0% | Yes |
| A330-200 | 0.0334 | 2.165 | 1.021 | 0.000 | 22.6 | 3.0% | Yes |
| 777-200LR | 0.0410 | 1.811 | 0.556 | 0.080 | 18.3 | 6.5% | No |

*Derived from 737-900ER; convergence refers to the parent model.

## 4.3 Confidence Assessment

The calibrated parameters fall into three confidence tiers:

### High Confidence: Boeing 767-200ER

All four parameters are physically reasonable. The zero-lift drag coefficient ($C_{D_0} = 0.0177$) is consistent with a clean widebody transport. The Oswald efficiency ($e = 0.732$) is within the expected range for a moderate aspect ratio wing. The TSFC adjustment ($k_{\text{adj}} = 0.951$) is close to unity, meaning the published TSFC closely predicts actual fuel consumption. The overhead fraction ($f_{oh} = 0.030$) is small, consistent with efficient climb and descent profiles. The RMS range error is effectively zero ($2 \times 10^{-12}$, i.e., machine precision). Mission results for the 767-200ER can be treated as quantitatively reliable.

### Medium Confidence: Gulfstream G-V

Parameters are generally physical. The $C_{D_0} = 0.0150$ is appropriate for a clean business jet. The Oswald efficiency ($e = 0.745$) is reasonable. The TSFC adjustment ($k_{\text{adj}} = 0.801$) indicates the model needs approximately 20% less fuel consumption than the published TSFC suggests, which is somewhat low but not unphysical --- it may absorb inaccuracies in the published TSFC value or reflect the G-V's efficient flight profile. The overhead fraction ($f_{oh} = 0.131$) is higher than expected but plausible for a business jet with steep climb profiles. The RMS error is 1.2%, acceptable for this analysis.

### Low Confidence: DC-8, P-8, A330-200, 777-200LR

These four aircraft exhibit at least one unphysical calibration parameter:

**DC-8-72**: The TSFC adjustment $k_{\text{adj}} = 0.605$ implies the model needs only 60% of the published fuel consumption rate. This produces fuel burn rates approximately 40% below reality. The likely cause is compensating interaction between $k_{\text{adj}}$ and the high overhead fraction $f_{oh} = 0.260$: the model allocates 26% of takeoff weight to non-cruise overhead and then uses an artificially low burn rate for the remaining cruise fuel. The individual parameters are not physically interpretable, though their combined effect reproduces the range-payload data accurately (RMS 0.5%).

**P-8 Poseidon**: The zero-lift drag coefficient $C_{D_0} = 0.0597$ is 3-4 times the expected value for a 737-derived airframe. This artifact propagates from the 737-900ER parent calibration ($C_{D_0} = 0.0355$, already high) and is amplified by the P-8 derivation process. The practical consequence is that engine-out performance cannot be reliably modeled: at $C_{D_0} = 0.06$, drag exceeds available thrust at all cruise altitudes when an engine fails.

**A330-200**: The Oswald efficiency $e = 2.165$ is unphysical --- values above 1.0 violate the theoretical upper bound for a planar wing. The overhead fraction $f_{oh} \approx 0$ is implausibly low. These artifacts likely arise from compensating errors in the calibration, possibly related to inaccuracies in the published A330-200 range data for the specific MTOW variant modeled. The 3.0% RMS error is the second-highest among all aircraft.

**777-200LR**: The Oswald efficiency $e = 1.811$ is unphysical. The TSFC adjustment $k_{\text{adj}} = 0.556$ implies only 56% of published fuel consumption. The $C_{D_0} = 0.041$ is approximately double the expected value. The calibration did not converge (RMS 6.5%, highest of all aircraft), suggesting the four-parameter model is insufficient to capture the 777-200LR's performance characteristics from the available range-payload data.

## 4.4 Range-Payload Diagrams

Range-payload diagrams for all six study aircraft are presented in Figure 1 (overlay) and Figures 2 through 7 (individual). Each diagram shows the three calibration corner points (markers) and the model-predicted range-payload curve. Good agreement between the markers and the curve indicates successful calibration; deviation (as seen for the A330-200 and 777-200LR) indicates the model does not fully capture the aircraft's performance characteristics.

<!-- Figure references for LaTeX conversion:
outputs/plots/rp_overlay_all.png   -> Figure 1: Range-payload overlay
outputs/plots/rp_dc8.png           -> Figure 2: DC-8-72
outputs/plots/rp_gv.png            -> Figure 3: G-V
outputs/plots/rp_p8.png            -> Figure 4: P-8
outputs/plots/rp_767200er.png      -> Figure 5: 767-200ER
outputs/plots/rp_a330200.png       -> Figure 6: A330-200
outputs/plots/rp_777200lr.png      -> Figure 7: 777-200LR
-->

## 4.5 Implications for Mission Analysis

The calibration quality directly determines the confidence level of mission results. The practical implication is:

- **767-200ER**: Absolute fuel burn numbers, costs, and range predictions are trustworthy.
- **G-V**: Results are directionally reliable; absolute numbers carry moderate uncertainty.
- **DC-8, P-8, A330-200, 777-200LR**: Useful for relative comparison and feasibility assessment (pass/fail), but absolute fuel consumption and cost numbers carry substantial uncertainty. The DC-8's fuel burn is systematically underestimated by approximately 40%.

This tiered confidence structure is carried through Sections 5-8, where results are presented with explicit confidence ratings.
