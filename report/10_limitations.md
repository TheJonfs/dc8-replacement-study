# 10. Model Limitations and Confidence Assessment

## 10.1 Model Architecture Limitations

### 10.1.1 Four-Parameter Calibration

The performance model uses four free parameters ($C_{D_0}$, $e$, $k_{\text{adj}}$, $f_{oh}$) calibrated against three range-payload corner points. With four parameters and three constraints, the system is underdetermined, allowing non-unique solutions. This manifests as compensating parameter combinations: for example, the DC-8's low $k_{\text{adj}}$ (0.605) is compensated by its high $f_{oh}$ (0.260), producing correct range-payload predictions from individually unphysical parameters.

The practical consequence is that the calibrated parameters cannot be interpreted individually as physical properties of the aircraft. The $C_{D_0}$ does not necessarily represent the true zero-lift drag; rather, it represents the value that, combined with the other three parameters, reproduces the published range-payload data. This limits the model's ability to predict performance at conditions far from the calibration points.

### 10.1.2 Drag Model Simplicity

The parabolic drag polar $C_D = C_{D_0} + C_L^2/(\pi \cdot AR \cdot e)$ does not capture:

- **Compressibility drag rise** near the drag-divergence Mach number
- **Reynolds number effects** at varying altitudes and speeds
- **Configuration-dependent drag** (landing gear, flaps, speed brakes)
- **Store drag** from externally mounted instruments and pods

These omissions have low impact at design cruise conditions (the calibration regime) but can introduce errors at off-design conditions such as the low-speed, low-altitude flight of Mission 3 or the high-altitude ceiling operations of Mission 2.

### 10.1.3 Propulsion Model Simplicity

The TSFC model uses a single altitude-dependent correction and a multiplicative calibration factor. It does not capture:

- **Part-power effects**: TSFC varies with throttle setting, and most cruise segments operate well below maximum thrust.
- **Mach-dependent TSFC**: The model's Mach dependence is limited.
- **Installation effects**: Inlet pressure recovery, exhaust interference, and bleed air extraction affect installed TSFC.

The two-regime thrust lapse model (Section 3.3.2) captures the first-order altitude dependence but uses fixed exponents (0.75 below tropopause, 2.0 above) that may not accurately represent all engine types.

### 10.1.4 Non-Cruise Overhead Fraction

The $f_{oh}$ model bundles all non-cruise fuel consumption into a single fraction of takeoff weight. This approach cannot distinguish between:

- Taxi and takeoff fuel
- Climb fuel (which varies with cruise altitude)
- Descent and approach fuel
- Contingency reserves

For Mission 1, this means reserves are implicit rather than explicit. For Missions 2 and 3, explicit reserve calculations are used instead.

## 10.2 Per-Aircraft Confidence

### 10.2.1 Boeing 767-200ER --- High Confidence

The 767 calibration produces physically reasonable parameters across all four dimensions. The RMS range error is machine-precision zero. Mission results are quantitatively reliable.

**Remaining uncertainty**: The model has not been validated against actual 767 mission data. Published range-payload data may not perfectly represent the specific -200ER variant and engine combination modeled. The mission profiles (engine-out, sawtooth climb, low-altitude endurance) are far from the calibration conditions (optimized cruise).

### 10.2.2 Gulfstream G-V --- Medium Confidence

The G-V calibration is mostly physical, with a moderately low $k_{\text{adj}} = 0.801$ and elevated $f_{oh} = 0.131$. Results are directionally reliable but absolute fuel consumption may carry 15-20% uncertainty.

**Key uncertainty**: The G-V's fleet sizing (6-9 aircraft) amplifies any per-aircraft error by the fleet multiplier. A 20% error in per-aircraft fuel consumption becomes a 20% error in aggregate fleet cost.

### 10.2.3 Douglas DC-8-72 --- Low Confidence

The $k_{\text{adj}} = 0.605$ implies the model consumes fuel at approximately 60% of the rate indicated by published TSFC. This is compensated by $f_{oh} = 0.260$ (26% of takeoff weight allocated to non-cruise overhead). The combined effect reproduces range-payload data but the individual parameters are unphysical.

**Impact**: DC-8 fuel costs are systematically underestimated by approximately 40%. The DC-8's apparent cost advantage ($0.44/klb-nm on Mission 2, $0.61/klb-nm on Mission 3) is an artifact of the low $k_{\text{adj}}$. Real costs would be 50-70% higher, likely placing the DC-8 above the 767 in cost.

### 10.2.4 Boeing P-8 Poseidon --- Low Confidence

The $C_{D_0} = 0.0597$ is 3-4 times the expected value for a 737-derived airframe. This artifact propagates from the 737-900ER parent calibration and is amplified by the derivation process. The $k_{\text{adj}} = 0.339$ compensates, producing correct range-payload predictions from individually extreme parameters.

**Impact**: Engine-out performance is not reliable (drag exceeds single-engine thrust at cruise altitudes). The P-8's low ceiling in Mission 2 (38,000-40,000 ft vs. published 41,000 ft) reflects the inflated $C_{D_0}$. Fuel consumption at low altitude (Mission 3) is CD0-dominated and therefore unreliable in absolute terms, though the relative ranking may still be approximately correct.

### 10.2.5 Airbus A330-200 --- Low Confidence

The Oswald efficiency $e = 2.165$ exceeds the theoretical maximum of 1.0 for a planar wing. The overhead fraction $f_{oh} \approx 0$ is implausibly low. The RMS error of 3.0% is the second-highest.

**Impact**: The A330's marginal Mission 2 pass (by only 49 nm) is within the model's uncertainty band. The absolute fuel consumption values carry substantial uncertainty. The A330 may be better or worse than the model suggests; the data does not support confident quantitative claims.

### 10.2.6 Boeing 777-200LR --- Low Confidence

The calibration did not converge (RMS 6.5%). The Oswald efficiency $e = 1.811$ is unphysical. The $C_{D_0} = 0.041$ is approximately double the expected value.

**Impact**: The 777 likely passes all missions (its enormous fuel capacity and thrust provide large margins), but the model cannot confirm this with confidence. Cost estimates ($1.15-$1.76/klb-nm) are approximate.

## 10.3 Mission-Specific Confidence

| Factor | Mission 1 | Mission 2 | Mission 3 |
|---|---|---|---|
| Distance from calibration conditions | High (long-range cruise is near calibration) | Medium (climb/descend cycles at varying altitudes) | High (1,500 ft, Mach 0.38 is far from calibration) |
| Engine-out modeling | Critical (determines pass/fail) | Not applicable | Not applicable |
| Fleet sizing sensitivity | Medium (GV 8x amplifies errors) | Medium (GV 9x, P-8 3x) | Low (GV 6x, P-8 2x) |
| Fuel budget method | f_oh (implicit reserves) | Explicit reserves | Mission-sized + explicit reserves |
| Discriminating power | High (only 1-2 aircraft pass) | Low (all pass) | None (all pass) |

Mission 1 results carry the most weight for the replacement decision because it is the only discriminating mission, but it is also the mission most affected by engine-out modeling uncertainties. The high confidence of the 767 calibration partially mitigates this: we can be confident in the 767's pass even though we cannot be confident in the other aircraft's failures.

## 10.4 What the Model Can and Cannot Tell Us

**The model can reliably determine:**
- The 767-200ER passes all three missions
- The DC-8, GV, and P-8 cannot complete Mission 1
- The 767 is the most cost-efficient single-aircraft option among candidates with reliable calibrations
- Progressive ceiling increase occurs for lighter-fuel-burn aircraft on Mission 2
- Mission-sized fuel loading is critical for fair Mission 3 comparison

**The model cannot reliably determine:**
- Whether the 777-200LR or A330-200 can complete Mission 1 (engine-out modeling unreliable)
- Absolute fuel costs for the DC-8, P-8, A330, or 777 (unphysical calibration parameters)
- Whether the P-8's real Mission 2 ceiling exceeds 41,000 ft (CD0 artifact depresses ceiling)
- The DC-8's true operating cost relative to replacement candidates
