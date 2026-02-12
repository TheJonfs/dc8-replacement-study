# 3. Performance Modeling Methodology

This section describes the physics-based models used to predict aircraft performance across the three science missions. The approach builds from fundamental atmospheric, aerodynamic, and propulsion models, integrates them through range and endurance equations, and calibrates the combined system against published range-payload data.

## 3.1 Atmospheric Model

All calculations use the International Standard Atmosphere (ISA) model from sea level to 65,000 ft. The ISA defines temperature, pressure, and density as functions of altitude in two regimes:

- **Troposphere** (0 to 36,089 ft): Temperature decreases linearly at 3.566 degrees F per 1,000 ft from a sea level value of 518.67 degrees R.
- **Stratosphere** (36,089 to 65,000 ft): Temperature is constant at 389.97 degrees R; pressure and density decrease exponentially.

From temperature and pressure, the model computes air density (used in lift and drag calculations) and speed of sound (used to convert between Mach number and true airspeed). Wind effects are not modeled; all ranges and endurances assume zero-wind conditions.

## 3.2 Aerodynamic Model

Aircraft drag is modeled using the parabolic drag polar:

$$C_D = C_{D_0} + \frac{C_L^2}{\pi \cdot AR \cdot e}$$

where:
- $C_{D_0}$ is the zero-lift drag coefficient (parasite drag from skin friction, form drag, and interference)
- $C_L$ is the lift coefficient, determined by the requirement that lift equals weight in steady cruise
- $AR$ is the wing aspect ratio (known from published geometry)
- $e$ is the Oswald efficiency factor (a calibration parameter capturing the deviation from ideal elliptical lift distribution)

The lift coefficient in cruise at altitude $h$ and Mach number $M$ is:

$$C_L = \frac{W}{q \cdot S}$$

where $W$ is aircraft weight, $S$ is wing reference area, and $q = \frac{1}{2} \rho V^2$ is dynamic pressure.

For engine-out conditions (Mission 1, second segment), the drag coefficient is increased by 10% to account for asymmetric thrust, rudder deflection, and sideslip:

$$C_{D,\text{eng-out}} = 1.10 \cdot C_D$$

The drag polar does not model compressibility drag rise near the drag divergence Mach number. This simplification has low impact because all aircraft cruise at or below their design cruise Mach, but it means the model cannot reliably predict performance at off-design speeds.

## 3.3 Propulsion Model

### 3.3.1 Thrust Specific Fuel Consumption

Thrust specific fuel consumption (TSFC) varies with altitude and Mach number. The model uses an altitude-adjusted reference TSFC:

$$TSFC(h) = TSFC_{\text{ref}} \cdot k_{\text{adj}} \cdot \left(\frac{\rho(h)}{\rho_0}\right)^{-0.1}$$

where $TSFC_{\text{ref}}$ is the manufacturer-published cruise TSFC, $k_{\text{adj}}$ is a calibration factor, and the density ratio term captures the altitude dependence of fuel consumption in turbofan engines (TSFC generally increases modestly with altitude).

### 3.3.2 Thrust Lapse Model

Available thrust decreases with altitude as air density decreases. The model uses a two-regime lapse rate:

**Below the tropopause** (h < 36,089 ft):
$$T = T_{SLS} \cdot \sigma^{0.75}$$

**Above the tropopause** (h >= 36,089 ft):
$$T = T_{\text{trop}} \cdot \left(\frac{\sigma}{\sigma_{\text{trop}}}\right)^{2.0}$$

where $\sigma = \rho / \rho_0$ is the density ratio and $T_{SLS}$ is sea-level static thrust.

The steeper lapse above the tropopause reflects the isothermal stratosphere where engine performance degrades more rapidly. This two-regime model is critical for Mission 2's progressive ceiling behavior: as fuel burns off and the aircraft lightens, thrust-limited ceilings increase in discrete steps that match the integration resolution.

### 3.3.3 Engine-Out Thrust

For the engine-out segment of Mission 1, available thrust is reduced to $(n-1)/n$ of the all-engines value, where $n$ is the number of engines. This means 2-engine aircraft lose 50% of thrust while the 4-engine DC-8 loses only 25%. The remaining engines operate at maximum continuous thrust.

## 3.4 Range Computation

### 3.4.1 Breguet Range Equation

The fundamental range prediction uses the Breguet range equation for constant-Mach, constant-altitude cruise:

$$R = \frac{V}{TSFC} \cdot \frac{L}{D} \cdot \ln\left(\frac{W_i}{W_f}\right)$$

where $V$ is true airspeed, $L/D$ is lift-to-drag ratio, $W_i$ is initial weight, and $W_f$ is final weight.

### 3.4.2 Step-Cruise Integration

Because optimal altitude increases as fuel burns off and the aircraft lightens, the model divides each cruise segment into discrete steps. At each step:

1. Compute optimal altitude for current weight (the altitude maximizing $L/D$ or specific range)
2. Cap altitude at the aircraft's thrust-limited ceiling (where available thrust equals drag at that altitude)
3. Compute range for the fuel burned in this step using Breguet
4. Update weight and advance to the next step

This step-cruise approach produces realistic altitude profiles that step upward during long cruise segments. The step size is 500 lb of fuel, providing altitude resolution of approximately 1,000 ft.

### 3.4.3 Non-Cruise Fuel Overhead

Fuel consumed during taxi, takeoff, climb, descent, and approach is not modeled explicitly. Instead, a fraction $f_{oh}$ of the takeoff weight is allocated as non-cruise overhead:

$$W_{\text{non-cruise}} = f_{oh} \cdot W_{\text{takeoff}}$$

This overhead is subtracted from the total fuel load before cruise range is computed. The overhead fraction $f_{oh}$ is a calibration parameter.

## 3.5 Reserve Fuel Policy

Two reserve fuel policies are used depending on mission type:

**Missions 2 and 3 (explicit reserves):**
- 5% of trip fuel as contingency
- 200 nm alternate airport capability
- 30 minutes holding fuel at destination altitude

**Mission 1 (f_oh model):**
Reserves are implicitly included in the non-cruise fuel overhead fraction $f_{oh}$. The fuel remaining after the full range is exhausted represents unburned cruise fuel, not a pre-allocated reserve.

## 3.6 Mission-Specific Models

### 3.6.1 Mission 1: Engine-Out Transport

The mission is modeled as two consecutive cruise segments:

1. **Normal cruise** (0 to 2,525 nm): All engines operating, step-cruise altitude optimization.
2. **Engine-out cruise** (2,525 nm to fuel exhaustion): One engine failed, remaining engines at maximum continuous thrust, +10% drag penalty. The aircraft descends to its new thrust-limited ceiling and continues cruise.

A fuel-at-distance interpolation determines the exact fuel state at the engine failure point (2,525 nm) and at the destination (5,050 nm). Aircraft that exhaust fuel before 5,050 nm are classified as infeasible.

### 3.6.2 Mission 2: Vertical Atmospheric Sampling

The mission is modeled as a series of repeating climb-descend cycles:

1. **Climb** from 5,000 ft to the aircraft's current thrust-limited ceiling, using an energy-method climb model that computes fuel, distance, and time as functions of rate-of-climb, which itself depends on excess thrust.
2. **Descend** from ceiling back to 5,000 ft with reduced fuel consumption.
3. **Repeat** until total distance reaches 4,200 nm.

The aircraft's ceiling is recomputed at the start of each climb cycle based on current weight. As fuel burns off, the ceiling increases --- this progressive ceiling behavior is the key scientific output of Mission 2.

### 3.6.3 Mission 3: Low-Altitude Smoke Survey

The mission is modeled as an 8-hour endurance cruise at 1,500 ft altitude and 250 KTAS (Mach 0.38). A time-stepping integration (30-minute intervals) computes fuel consumption from the instantaneous drag and TSFC at each step.

Because the mission is time-constrained rather than range-constrained, the aircraft loads only enough fuel for the 8-hour mission plus reserves. This fuel load is computed iteratively:

1. Estimate initial fuel requirement from clean-aircraft burn rate
2. Compute takeoff weight (OEW + payload + fuel estimate)
3. Simulate 8-hour endurance at that takeoff weight
4. Compute required reserves for the fuel burned
5. Iterate until fuel estimate converges within 50 lb
6. Add 5% operational margin

This iterative sizing is critical for fair comparison: without it, large aircraft with high fuel capacity (777-200LR, A330-200) would be penalized for carrying fuel they do not need.

## 3.7 Fleet Sizing

For aircraft whose maximum payload is less than the mission-required payload (G-V and P-8), the model determines the minimum number of aircraft $n$ needed to carry the aggregate payload:

$$n = \left\lceil \frac{W_{\text{payload,required}}}{W_{\text{payload,max}}} \right\rceil$$

Each aircraft in the fleet carries $W_{\text{payload,required}} / n$ pounds of payload, and aggregate fuel consumption and cost are computed as $n$ times the per-aircraft values.

## 3.8 Cost Metric

Fuel cost is computed at $5.50 per gallon of Jet-A fuel (6.7 lb per gallon). The primary cost metric is:

$$\text{Cost efficiency} = \frac{\text{Total fuel cost}}{\text{Payload weight} \times \text{Distance}} \quad \left[\frac{\$}{\text{klb} \cdot \text{nm}}\right]$$

This metric normalizes cost by both payload carried and distance traveled, enabling comparison across missions with different payload and range requirements. For multi-aircraft fleets, the aggregate cost, payload, and distance are used.
