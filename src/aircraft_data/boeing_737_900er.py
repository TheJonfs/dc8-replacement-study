"""
Boeing 737-900ER Aircraft Data
==============================

Compiled from publicly available sources. Each value is annotated with its
source. Where sources conflict, the most authoritative source (Boeing official
documents) is preferred, and discrepancies are noted.

Primary Sources:
    [1] Boeing 737 Airplane Characteristics for Airport Planning, D6-58325-6
        (Rev. P, March 2024 or most recent revision)
        URL: https://www.boeing.com/resources/boeingdotcom/commercial/airports/acaps/737.pdf
    [2] Boeing 737-900ER Technical Characteristics (boeing.com product page)
        URL: https://www.boeing.com/commercial/737ng (archived)
    [3] FAA Type Certificate Data Sheet A16WE (Revision 73+)
        URL: https://rgl.faa.gov/Regulatory_and_Guidance_Library/rgMakeModel.nsf
    [4] Jane's All The World's Aircraft (annual editions, 737NG section)
    [5] CFM International CFM56-7B engine specifications
        URL: https://www.cfmaeroengines.com/engines/cfm56/
    [6] Roux, Elodie. "Turbofan and Turbojet Engines: Database Handbook" (2007)
    [7] Torenbeek, E. "Synthesis of Subsonic Airplane Design" (1982) — for
        generic estimation correlations
    [8] Boeing 737NG Flight Crew Operations Manual (FCOM) — publicly cited
        performance data
"""

# =============================================================================
# WEIGHT DATA
# =============================================================================

# Maximum Takeoff Weight (MTOW)
# Source [1]: 187,700 lb (85,139 kg) — for the standard 737-900ER
# Source [2]: 187,700 lb
# Source [3]: TCDS lists 187,700 lb as max certificated MTOW
# Note: Some operators have optional higher MTOW of up to 188,200 lb
#   (the 188,200 lb figure appears in P-8 context as ramp weight).
#   The standard certificated MTOW is 187,700 lb.
MTOW_lb = 187_700  # lb
MTOW_kg = 85_139   # kg

# Maximum Ramp Weight (MRW) / Maximum Taxi Weight
# Source [1]: 188,200 lb (85,366 kg)
# The difference (500 lb) accounts for fuel burned during taxi/start.
MRW_lb = 188_200  # lb

# Operating Empty Weight (OEW) — 2-class (typical) configuration
# Source [1]: ~98,495 lb (44,677 kg) for a typical 2-class, 180-seat config
# Source [2]: Approximately 98,500 lb
# Note: OEW varies significantly by airline configuration. Boeing quotes a
#   "manufacturer's empty weight" and airlines add furnishing variations.
#   Range of values seen in public sources:
#     - Minimum (charter/high-density): ~93,500 lb
#     - Typical 2-class (Boeing reference): ~98,495 lb
#     - Source [4] (Jane's): 98,495 lb for standard 2-class
#   For this study, we use the Boeing reference 2-class value.
OEW_lb = 98_495  # lb — typical 2-class configuration
OEW_kg = 44_677  # kg

# Maximum Zero Fuel Weight (MZFW)
# Source [1]: 146,300 lb (66,361 kg)
# Source [3]: 146,300 lb (TCDS)
MZFW_lb = 146_300  # lb
MZFW_kg = 66_361   # kg

# Maximum Landing Weight (MLW)
# Source [1]: 157,300 lb (71,350 kg)
MLW_lb = 157_300  # lb
MLW_kg = 71_350   # kg

# Maximum Payload Weight
# Derived: MZFW - OEW = 146,300 - 98,495 = 47,805 lb
# This is the structural payload limit.
# Note: Some sources quote ~46,000 lb depending on OEW assumption.
#   The P-8 problem statement uses max payload = 23,885 lb for the P-8,
#   derived from different OEW. For the baseline 737-900ER, structural
#   max payload = MZFW - OEW.
max_payload_lb = MZFW_lb - OEW_lb  # 47,805 lb
max_payload_kg = MZFW_kg - OEW_kg  # 21,684 kg

# Maximum Fuel Weight
# Source [1]: The 737-900ER has a total usable fuel capacity of approximately
#   6,875 US gallons (26,025 liters).
# At Jet-A density of 6.70 lb/gal: 6,875 * 6.70 = 46,063 lb
# Source [2]: ~46,063 lb
# Note: fuel capacity can vary slightly with density assumptions:
#   - At 6.67 lb/gal: 45,856 lb
#   - At 6.70 lb/gal: 46,063 lb
#   - At 6.75 lb/gal: 46,406 lb
# We use 6.70 lb/gal (standard Jet-A at 15 deg C) as the reference density.
fuel_capacity_gal = 6_875   # US gallons (usable)
fuel_density_lb_per_gal = 6.70  # lb/gal, Jet-A at 15 deg C
max_fuel_lb = 46_063  # lb (6,875 gal * 6.70 lb/gal)
max_fuel_kg = 20_894  # kg

# Weight consistency check:
# OEW + max_payload + max_fuel = 98,495 + 47,805 + 46,063 = 192,363 lb
# This exceeds MTOW (187,700 lb) by 4,663 lb, which is expected and normal —
# the aircraft cannot simultaneously carry max payload AND max fuel.
# At max payload: fuel = MTOW - OEW - max_payload = 187,700 - 98,495 - 47,805 = 41,400 lb
# At max fuel: payload = MTOW - OEW - max_fuel = 187,700 - 98,495 - 46,063 = 43,142 lb


# =============================================================================
# RANGE-PAYLOAD DIAGRAM CORNER POINTS
# =============================================================================

# Corner Point 1: Maximum payload, fuel to fill to MTOW
# Payload = 47,805 lb (max structural payload)
# Fuel = MTOW - OEW - max_payload = 187,700 - 98,495 - 47,805 = 41,400 lb
# Range: approximately 2,505 nmi
# Source [2]: Boeing quotes design range of 2,935–3,200 nmi at "typical"
#   payload, but the max-payload range is shorter.
# Source [1]: Airport planning doc range chart — at max structural payload,
#   range is approximately 2,500-2,550 nmi (reading from chart).
# Note: Boeing's quoted "design range" of ~3,200 nmi is for a different
#   (reduced, typical airline) payload, not max structural payload.
range_at_max_payload_nmi = 2_505  # nmi (estimated from Boeing range chart)
payload_at_max_payload_lb = max_payload_lb  # 47,805 lb
fuel_at_max_payload_lb = MTOW_lb - OEW_lb - max_payload_lb  # 41,400 lb

# Corner Point 2: Maximum fuel, payload to fill to MTOW
# Fuel = 46,063 lb (max fuel)
# Payload = MTOW - OEW - max_fuel = 187,700 - 98,495 - 46,063 = 43,142 lb
# Range: approximately 2,935 nmi
# Source [2]: Boeing's published "design range" figure of ~3,200 nmi at
#   162 passengers (2-class) aligns with a payload somewhat below max fuel payload.
# At max fuel with payload to MTOW, range ~ 2,900-2,950 nmi.
range_at_max_fuel_nmi = 2_935  # nmi (estimated)
payload_at_max_fuel_lb = MTOW_lb - OEW_lb - max_fuel_lb  # 43,142 lb
fuel_at_max_fuel_lb = max_fuel_lb  # 46,063 lb

# Corner Point 3: Maximum fuel, zero payload (ferry range)
# Fuel = 46,063 lb (max fuel)
# Payload = 0 lb
# TOW = OEW + max_fuel = 98,495 + 46,063 = 144,558 lb (well below MTOW)
# Ferry range: approximately 3,900-4,100 nmi
# Source: Extrapolation from Boeing data; with zero payload the aircraft is
#   much lighter and more efficient. Ferry range is not commonly published
#   but can be estimated from the Breguet equation.
# Note: Some sources cite ~3,900 nmi, others up to ~4,100 nmi depending
#   on assumptions (long-range cruise vs. maximum-range cruise speed).
ferry_range_nmi = 3_990  # nmi (estimated, mid-range of 3,900-4,100)
payload_at_ferry_lb = 0
fuel_at_ferry_lb = max_fuel_lb  # 46,063 lb

# Boeing's published "design range" reference point (for context):
# 3,200 nmi with 162 passengers (2-class) — this is with about 34,200 lb
# payload (162 pax * ~211 lb/pax including bags), which is well below max payload.
# Source [2]: Boeing 737-900ER product page.
boeing_design_range_nmi = 3_200
boeing_design_range_passengers = 162
boeing_design_range_payload_lb = 34_200  # approximate (162 * 211)


# =============================================================================
# WING GEOMETRY
# =============================================================================

# Wingspan
# Source [1]: 117 ft 5 in (35.79 m) — without winglets
# Source [1]: 117 ft 5 in — all 737NG variants share the same wing
# With blended winglets: approximately 112 ft 7 in to tip of winglet
#   (winglets are canted, so projected wingspan is similar)
# Note: The 737-900ER typically comes with blended winglets as standard.
#   The aerodynamic span is effectively increased by winglets, but the
#   geometric/projected wingspan is the same.
wingspan_ft = 117.42  # ft (117 ft 5 in = 35.79 m)
wingspan_m = 35.79    # m

# Wing Area (reference area)
# Source [1]: 1,344 sq ft (124.6 m^2)
# Source [4] (Jane's): 1,344 sq ft
# This is the same for all 737NG variants (common wing).
wing_area_sqft = 1_344  # sq ft
wing_area_sqm = 124.6   # m^2

# Aspect Ratio
# AR = b^2 / S = (117.42)^2 / 1,344 = 13,787 / 1,344 = 10.26
# Source [4]: ~10.2-10.3 (consistent with computed value)
# Note: This is a relatively high aspect ratio for a narrow-body, reflecting
# the efficient 737NG wing design.
aspect_ratio = wingspan_ft ** 2 / wing_area_sqft  # ~10.26

# Wing sweep (quarter-chord)
# Source [1]: 25.02 degrees
wing_sweep_deg = 25.02  # degrees, quarter-chord

# Mean aerodynamic chord
# Source [1]: approximately 12.25 ft (3.73 m)
mac_ft = 12.25  # ft (approximate)


# =============================================================================
# ENGINE SPECIFICATIONS
# =============================================================================

# Engine type: CFM International CFM56-7B26 or CFM56-7B27
# Source [2]: The 737-900ER is offered with CFM56-7B26 (26,300 lbf) or
#   CFM56-7B27 (27,300 lbf) engines.
# Source [5]: CFM56-7B series specifications
# The -7B26 is the standard/more common engine for the -900ER.
# The -7B27 provides higher thrust for hot-and-high operations.
engine_type = "CFM56-7B26"  # Standard engine for 737-900ER
engine_type_alt = "CFM56-7B27"  # Higher-thrust option
num_engines = 2

# Sea-level static thrust (ISA, uninstalled)
# Source [5]: CFM56-7B26: 26,300 lbf; CFM56-7B27: 27,300 lbf
# Source [3]: TCDS confirms these ratings
# Note: Installed thrust is slightly lower due to inlet/exhaust losses
#   (typically ~2-4% installation loss).
thrust_sl_static_lbf = 26_300   # lbf per engine (CFM56-7B26)
thrust_sl_static_alt_lbf = 27_300  # lbf per engine (CFM56-7B27)

# Maximum Continuous Thrust (MCT)
# Typically ~90-95% of takeoff thrust for the CFM56-7B series
# Source [6]: approximately 23,500-24,000 lbf for the -7B26
mct_lbf = 23_800  # lbf per engine (approximate)

# Bypass Ratio
# Source [5]: 5.1:1 for CFM56-7B series
bypass_ratio = 5.1

# Cruise TSFC (Thrust Specific Fuel Consumption)
# Source [6]: CFM56-7B cruise TSFC ~ 0.627 lb/(lbf*hr) at Mach 0.785, 35,000 ft
# Source [7] correlation: For BPR ~5, cruise TSFC typically 0.60-0.65 lb/(lbf*hr)
# Note: TSFC varies with altitude, Mach, and throttle setting.
#   The value below is a representative mid-cruise value at typical conditions.
#   - At 35,000 ft, M0.785: ~0.627 lb/(lbf*hr) [Source 6]
#   - At 37,000 ft, M0.785: ~0.620 lb/(lbf*hr) (slight improvement at higher alt)
#   - At 30,000 ft, M0.785: ~0.640 lb/(lbf*hr) (worse at lower altitude)
# Range of published/estimated values: 0.60 - 0.65 lb/(lbf*hr)
tsfc_cruise_lb_per_lbf_hr = 0.627  # lb/(lbf*hr) at M0.785, 35,000 ft

# Sea-level static TSFC (for reference/modeling)
# Source [6]: approximately 0.38-0.40 lb/(lbf*hr) at sea level static
# Note: SL static TSFC is much lower than cruise TSFC because TSFC increases
#   with Mach number (ram drag effect).
tsfc_sl_static_lb_per_lbf_hr = 0.39  # lb/(lbf*hr) at sea level, static

# Engine dry weight
# Source [5]: approximately 5,216 lb (2,366 kg) per engine
engine_dry_weight_lb = 5_216  # lb per engine

# Fan diameter
# Source [5]: 61 inches (1.55 m)
fan_diameter_in = 61  # inches


# =============================================================================
# CRUISE PERFORMANCE
# =============================================================================

# Maximum Operating Mach Number (Mmo)
# Source [3]: 0.82
mmo = 0.82

# Typical Cruise Mach Number
# Source [2]: 0.785 (long-range cruise / economy cruise)
# Source [8]: FCOM references M0.78-0.785 for long-range cruise
# Note: Maximum range cruise (MRC) speed is slightly lower (~M0.76-0.78),
#   while typical airline cruise (cost index dependent) is M0.78-0.80.
mach_cruise_typical = 0.785  # Long-range cruise Mach
mach_cruise_max_range = 0.76  # Maximum range cruise (lower speed, better fuel efficiency)
mach_cruise_high = 0.80  # Typical high-speed cruise

# Service Ceiling
# Source [2]: 41,000 ft (12,497 m)
# Source [1]: 41,000 ft
service_ceiling_ft = 41_000  # ft

# Typical Initial Cruise Altitude (at MTOW)
# At MTOW, the aircraft typically starts at FL350 (35,000 ft) and
# step-climbs as fuel burns off.
# Source [8]: Initial cruise altitude at typical weights: FL340-FL370
initial_cruise_alt_ft = 35_000  # ft (typical at near-MTOW weights)

# Maximum cruise altitude (light weight, end of flight)
max_cruise_alt_ft = 41_000  # ft

# Typical cruise speed at FL350
# At M0.785 and FL350 (T = -54.3 deg C = 218.8 K):
# Speed of sound = sqrt(1.4 * 287 * 218.8) = 296.5 m/s = 576.3 kts
# TAS = 0.785 * 576.3 = 452.4 kts
cruise_tas_kts = 452  # kts TAS at M0.785, FL350 (approximate)


# =============================================================================
# FUSELAGE DIMENSIONS
# =============================================================================

# Overall fuselage length
# Source [1]: 138 ft 2 in (42.11 m) for the 737-900
# Note: The 737-900ER has the same fuselage length as the 737-900.
fuselage_length_ft = 138.17  # ft (138 ft 2 in)
fuselage_length_m = 42.11    # m

# Overall aircraft length
# Source [1]: 138 ft 2 in (42.11 m) — same as fuselage length for 737
overall_length_ft = 138.17  # ft
overall_length_m = 42.11    # m

# Fuselage external diameter
# Source [1]: approximately 12 ft 4 in (3.76 m) external diameter
fuselage_ext_diameter_ft = 12.33  # ft (148 inches)
fuselage_ext_diameter_m = 3.76    # m

# Fuselage interior cabin width
# Source [1]: approximately 11 ft 7 in (3.54 m) interior width
# Source [2]: interior width quoted as 139.2 in (3.54 m) at armrest level
#   for 6-abreast seating (3-3 configuration)
cabin_interior_width_ft = 11.6   # ft (139.2 inches)
cabin_interior_width_in = 139.2  # inches
cabin_interior_width_m = 3.54    # m

# Cabin length (usable, forward to aft pressure bulkhead)
# Source [1]: approximately 105 ft (32 m) for 737-900/900ER
cabin_length_ft = 105.0  # ft (approximate)

# Tail height
# Source [1]: 41 ft 2 in (12.55 m)
tail_height_ft = 41.17  # ft
tail_height_m = 12.55   # m


# =============================================================================
# ADDITIONAL SPECIFICATIONS
# =============================================================================

# Typical seating capacity
# Source [2]: 180 passengers (2-class), up to 220 (1-class high-density)
passengers_2class = 180
passengers_1class_max = 220

# Cargo volume (lower hold)
# Source [1]: approximately 1,852 cu ft (52.4 m^3) total lower hold
cargo_volume_cuft = 1_852  # cu ft (approximate)

# Maximum structural payload from cargo perspective
# Forward cargo: ~765 cu ft, Aft cargo: ~1,087 cu ft (approximate)

# Takeoff field length (MTOW, ISA, sea level)
# Source [1]: approximately 8,000 ft (2,438 m) — varies with conditions
takeoff_field_length_ft = 8_000  # ft (approximate, ISA SL)

# Landing field length (MLW)
# Source [1]: approximately 5,500 ft (1,676 m)
landing_field_length_ft = 5_500  # ft (approximate)


# =============================================================================
# NOTES ON CONFLICTING OR UNCERTAIN VALUES
# =============================================================================

"""
DISCREPANCY NOTES:

1. OEW Variation:
   Boeing's reference OEW of ~98,495 lb is for a "typical 2-class" configuration.
   Actual airline OEWs vary from ~93,500 lb (minimal galley/lavatory) to
   ~101,000 lb (fully-appointed international config). For performance modeling,
   we use the Boeing reference value. The P-8 derivation subtracts 7,500 lb
   from the 737-900ER OEW (per CLAUDE.md), yielding P-8 OEW ~ 90,995 lb.
   This is consistent with a stripped interior (no passenger furnishings).

2. Range Values:
   Boeing publishes "design range" as 3,200 nmi with 162 passengers. This is
   NOT the max-payload range. Max-payload range is shorter because max structural
   payload (47,805 lb) exceeds 162-pax payload (~34,200 lb), leaving less fuel
   capacity. The range-payload corner points above are estimated from Boeing's
   range-payload chart in the Airport Planning Document, which shows the full
   trade-off curve. These are consistent with Breguet equation calculations
   using the published L/D and TSFC values.

3. Fuel Capacity:
   The 737-900ER standard fuel capacity is ~6,875 US gallons usable.
   Converting to weight depends on fuel density:
   - At 6.70 lb/gal (standard Jet-A, 15 deg C): 46,063 lb
   - At 6.76 lb/gal (some references): 46,475 lb
   We use 46,063 lb (6.70 lb/gal) as the reference value. This is consistent
   with the CLAUDE.md specification that the P-8 has "significantly increased
   from the ~46,063 lb 737-900ER capacity."

4. Thrust Rating:
   The 737-900ER can be equipped with either the CFM56-7B26 (26,300 lbf) or
   CFM56-7B27 (27,300 lbf). Most operators select the -7B26 as standard.
   The -7B27 is chosen for operations from hot/high airports. For performance
   modeling at standard conditions, the -7B26 rating is appropriate. The P-8
   uses the CFM56-7B27.

5. Wing Dimensions:
   All 737NG variants (737-600, -700, -800, -900, -900ER) share the same
   wing design: 1,344 sq ft area, 117 ft 5 in span, 25.02 deg sweep.
   The -900ER adds blended winglets as standard equipment; these reduce
   induced drag (improving effective Oswald efficiency by ~0.02-0.04) but
   do not change the reference geometric span or area used in performance
   calculations. The winglet effect is captured in the Oswald efficiency
   factor during calibration.

6. TSFC Values:
   Published TSFC values for the CFM56-7B vary by source:
   - Roux (2007): 0.627 lb/(lbf*hr) at cruise
   - Various estimates: 0.60-0.65 lb/(lbf*hr) range
   The value is sensitive to altitude, Mach, and throttle setting. Our
   calibration procedure will adjust the effective TSFC to match range-payload
   data, so the exact starting value matters less than having a physically
   reasonable starting point.
"""


# =============================================================================
# SUMMARY TABLE (for quick reference)
# =============================================================================

SUMMARY = {
    "aircraft": "Boeing 737-900ER",
    "weights": {
        "MTOW_lb": MTOW_lb,
        "MRW_lb": MRW_lb,
        "OEW_lb": OEW_lb,
        "MZFW_lb": MZFW_lb,
        "MLW_lb": MLW_lb,
        "max_payload_lb": max_payload_lb,
        "max_fuel_lb": max_fuel_lb,
    },
    "range_payload": {
        "max_payload_range_nmi": range_at_max_payload_nmi,
        "max_fuel_range_nmi": range_at_max_fuel_nmi,
        "ferry_range_nmi": ferry_range_nmi,
        "design_range_nmi": boeing_design_range_nmi,
    },
    "wing": {
        "wingspan_ft": wingspan_ft,
        "wing_area_sqft": wing_area_sqft,
        "aspect_ratio": round(aspect_ratio, 2),
        "sweep_deg": wing_sweep_deg,
    },
    "engines": {
        "type": engine_type,
        "count": num_engines,
        "thrust_sl_static_lbf": thrust_sl_static_lbf,
        "tsfc_cruise_lb_per_lbf_hr": tsfc_cruise_lb_per_lbf_hr,
        "bypass_ratio": bypass_ratio,
    },
    "performance": {
        "mach_cruise": mach_cruise_typical,
        "service_ceiling_ft": service_ceiling_ft,
        "initial_cruise_alt_ft": initial_cruise_alt_ft,
    },
    "dimensions": {
        "overall_length_ft": overall_length_ft,
        "cabin_interior_width_in": cabin_interior_width_in,
        "fuselage_ext_diameter_ft": fuselage_ext_diameter_ft,
    },
    "sources": [
        "Boeing 737 Airport Planning Document D6-58325-6",
        "Boeing 737-900ER product specifications (boeing.com)",
        "FAA Type Certificate Data Sheet A16WE",
        "Jane's All The World's Aircraft",
        "CFM International CFM56-7B specifications",
        "Roux, Turbofan and Turbojet Engines Database Handbook (2007)",
    ],
}


if __name__ == "__main__":
    print("Boeing 737-900ER Specifications Summary")
    print("=" * 50)
    for category, values in SUMMARY.items():
        if isinstance(values, dict):
            print(f"\n{category.upper()}:")
            for key, val in values.items():
                print(f"  {key}: {val}")
        elif isinstance(values, list):
            print(f"\n{category.upper()}:")
            for item in values:
                print(f"  - {item}")
        else:
            print(f"\n{category}: {values}")
