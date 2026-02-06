"""
Gulfstream G-V (Gulfstream V) Aircraft Specifications
======================================================

Data compiled from the following public sources:
1. Gulfstream G-V Airport Planning Manual (Gulfstream Aerospace Corporation)
2. FAA Type Certificate Data Sheet A12EA (Rev 23)
3. Gulfstream G-V Airplane Flight Manual (AFM) - published performance summaries
4. Jane's All the World's Aircraft (various editions, 1997-2005)
5. Rolls-Royce BR710 engine data from EASA Type Certificate Data Sheet E.012
6. Aviation Week & Space Technology fleet data and specifications
7. Gulfstream G-V marketing/specification brochures (public)

Notes on the G-V vs G550:
- The G-V (Model GV, serial numbers 501-638) was produced from 1995-2003
- The G550 is the successor with enhanced avionics (PlaneView) but very similar
  airframe and engine. The G550 has the same MTOW, OEW, and fuel capacity.
- For this study we use G-V specifications. Where sources give G550 data,
  it is noted and the GV-specific value is used where it differs.

All weights are in pounds (lb). All distances are in nautical miles (nmi).
All speeds are in knots or Mach number as noted.
"""

# =============================================================================
# 1. WEIGHT SPECIFICATIONS
# =============================================================================

# Maximum Takeoff Weight (MTOW)
# Source: FAA TCDS A12EA, Gulfstream APM
# Consistent across all sources
MTOW_lb = 90_500  # lb

# Maximum Landing Weight (MLW)
# Source: FAA TCDS A12EA, Gulfstream APM
MLW_lb = 75_300  # lb

# Maximum Zero Fuel Weight (MZFW)
# Source: FAA TCDS A12EA, Gulfstream APM
MZFW_lb = 54_000  # lb

# Operating Empty Weight (OEW)
# Source: Gulfstream spec sheet, Jane's
# Note: OEW varies with interior configuration. Gulfstream quotes a
# "typical" or "basic" OEW. Values in the literature range from ~46,000
# to ~48,800 lb depending on configuration.
#
# - Gulfstream published "basic operating weight": 48,200 lb (typical
#   executive interior with full crew provisions)
# - Jane's All the World's Aircraft lists approximately 46,800-48,200 lb
# - Some sources list ~46,000 lb for a lighter configuration
#
# For this study, we use the commonly cited typical OEW:
OEW_lb = 48_200  # lb (typical executive configuration)
# Conservative / lighter OEW for reference:
OEW_lb_min = 46_000  # lb (minimal interior, sometimes cited)

# Maximum Payload Weight
# Derived from: MZFW - OEW
# Using typical OEW: 54,000 - 48,200 = 5,800 lb
# Using lighter OEW: 54,000 - 46,000 = 8,000 lb
MAX_PAYLOAD_lb = 5_800  # lb (with typical OEW of 48,200 lb)
# Note: The structural payload limit is constrained by MZFW
# Some sources cite max payload as 6,200 lb with a slightly different OEW

# Maximum Fuel Weight
# Source: Gulfstream APM, spec sheets
# Total fuel capacity: approximately 41,300 lb
# Some sources cite 41,300 lb; others cite 41,580 lb
# The fuel capacity in volume is approximately 6,104 US gallons
#
# Values found:
# - Gulfstream spec sheet: 41,300 lb (6,104 gal)
# - Some references: 41,580 lb
# - Jane's: 41,300 lb
#
# Using the most commonly cited value:
MAX_FUEL_lb = 41_300  # lb
FUEL_CAPACITY_gal = 6_104  # US gallons
# Note: Jet-A density ~6.77 lb/gal -> 6,104 gal * 6.77 = 41,324 lb (consistent)

# Maximum Ramp Weight
# Source: Gulfstream APM
MAX_RAMP_WEIGHT_lb = 91_000  # lb (MTOW + taxi fuel allowance)

# Weight cross-check:
# OEW + MAX_PAYLOAD + fuel_to_MTOW = MTOW
# 48,200 + 5,800 + fuel = 90,500 -> fuel = 36,500 lb (partial fuel at max payload)
# OEW + payload + MAX_FUEL = MTOW
# 48,200 + payload + 41,300 = 90,500 -> payload = 1,000 lb (payload at max fuel)
# OEW + 0 + MAX_FUEL = 48,200 + 41,300 = 89,500 lb (ferry, below MTOW)

WEIGHT_CROSSCHECK = {
    "max_payload_case": {
        "oew": OEW_lb,
        "payload": MAX_PAYLOAD_lb,
        "fuel": MTOW_lb - OEW_lb - MAX_PAYLOAD_lb,  # 36,500 lb
        "total": MTOW_lb,
    },
    "max_fuel_case": {
        "oew": OEW_lb,
        "payload": MTOW_lb - OEW_lb - MAX_FUEL_lb,  # 1,000 lb
        "fuel": MAX_FUEL_lb,
        "total": MTOW_lb,
    },
    "ferry_case": {
        "oew": OEW_lb,
        "payload": 0,
        "fuel": MAX_FUEL_lb,
        "total": OEW_lb + MAX_FUEL_lb,  # 89,500 lb (below MTOW)
    },
}


# =============================================================================
# 2. RANGE-PAYLOAD DATA (for calibration)
# =============================================================================

# Published range specifications:
# Source: Gulfstream spec sheets, Jane's, aviation databases
#
# The G-V's headline range figure varies by source and assumptions:
# - Gulfstream marketing: 5,800 nmi (at Mach 0.80, 8 passengers, NBAA IFR reserves)
# - Some sources: 6,500 nmi (at long-range cruise Mach ~0.80)
# - Jane's: range with 8 passengers: 5,800 nmi; max fuel range: ~6,500 nmi
# - Ferry range: approximately 6,750 nmi
#
# NBAA IFR reserves = 200 nmi alternate + 30 min hold (industry standard for
# business aviation range comparisons)
#
# Range-payload corner points (estimated from published data):
#
# Corner Point 1: Maximum payload, fuel to fill to MTOW
#   Payload: 5,800 lb
#   Fuel: MTOW - OEW - payload = 90,500 - 48,200 - 5,800 = 36,500 lb
#   Range: ~5,150 nmi (with NBAA IFR reserves)
#   Note: This is less than the headline 5,800 nmi because fuel is limited
#
# Corner Point 2: Maximum fuel, payload to fill to MTOW
#   Fuel: 41,300 lb
#   Payload: MTOW - OEW - fuel = 90,500 - 48,200 - 41,300 = 1,000 lb
#   Range: ~6,200 nmi (with NBAA IFR reserves)
#
# Corner Point 3: Maximum fuel, zero payload (ferry)
#   Fuel: 41,300 lb
#   Payload: 0 lb
#   Takeoff weight: 48,200 + 41,300 = 89,500 lb
#   Range: ~6,500 nmi (with NBAA IFR reserves)
#
# The "8 passengers, 5,800 nmi" headline figure:
#   8 passengers ~ 8 * 200 lb = 1,600 lb
#   Fuel: 90,500 - 48,200 - 1,600 = 40,700 lb
#   This yields approximately 5,800 nmi (Gulfstream published figure)

# Range-payload corner points for model calibration
# These are the three standard points that define the range-payload envelope
RANGE_PAYLOAD_POINTS = {
    "max_payload": {
        "payload_lb": 5_800,
        "fuel_lb": 36_500,       # MTOW - OEW - max_payload
        "takeoff_weight_lb": MTOW_lb,
        "range_nmi": 5_150,      # estimated
        "notes": "Max payload, fuel to fill to MTOW. Range estimated from "
                 "published data interpolation.",
    },
    "max_fuel": {
        "payload_lb": 1_000,
        "fuel_lb": MAX_FUEL_lb,  # 41,300
        "takeoff_weight_lb": MTOW_lb,
        "range_nmi": 6_200,      # estimated
        "notes": "Max fuel with payload to fill to MTOW.",
    },
    "ferry": {
        "payload_lb": 0,
        "fuel_lb": MAX_FUEL_lb,  # 41,300
        "takeoff_weight_lb": 89_500,  # OEW + max fuel
        "range_nmi": 6_500,
        "notes": "Ferry mission: max fuel, zero payload. Below MTOW.",
    },
}

# Additional published range reference points
RANGE_REFERENCE_POINTS = {
    "8_pax_nbaa_ifr": {
        "payload_lb": 1_600,     # 8 pax @ 200 lb each
        "range_nmi": 5_800,
        "mach": 0.80,
        "notes": "Gulfstream published headline figure. 8 passengers, "
                 "Mach 0.80, NBAA IFR reserves.",
        "source": "Gulfstream G-V specification sheet",
    },
    "high_speed_cruise": {
        "payload_lb": 1_600,     # 8 pax
        "range_nmi": 5_000,      # reduced at higher speed
        "mach": 0.85,
        "notes": "Approximate range at high-speed cruise. Range trades "
                 "significantly with cruise speed above Mach 0.80.",
    },
}


# =============================================================================
# 3. WING AND AERODYNAMIC DATA
# =============================================================================

# Wing geometry
# Source: Gulfstream APM, Jane's, FAA TCDS
WING_SPAN_ft = 93.5         # ft (93 ft 6 in)
WING_SPAN_m = 28.50         # m
WING_AREA_sqft = 1_137.0    # sq ft
# Note: Some sources cite wing area as 1,137 sq ft, others as 1,137.4 sq ft
# Jane's: 105.6 m^2 = 1,137 sq ft (consistent)
WING_AREA_sqm = 105.6       # m^2

# Aspect ratio
# AR = span^2 / area = 93.5^2 / 1,137 = 8,742.25 / 1,137 = 7.69
ASPECT_RATIO = 7.69

# Wing sweep (quarter-chord)
WING_SWEEP_deg = 33.47      # degrees at quarter-chord
# Source: Jane's, Gulfstream documents
# Note: Some sources round to 33.5 degrees

# Mean aerodynamic chord
MAC_ft = 13.1                # ft (approximate, derived from wing geometry)

# Estimated Oswald efficiency factor (for initial drag polar estimation)
# Not published; will be calibrated. Initial estimate based on:
# - Moderate aspect ratio (7.69)
# - Swept wing (33.5 deg)
# - Clean design
# Typical range for business jets: 0.75-0.82
OSWALD_EFFICIENCY_INITIAL = 0.78  # initial estimate, to be calibrated

# Estimated zero-lift drag coefficient
# Not published; will be calibrated. Initial estimate:
# Business jets typically have CD0 ~ 0.018-0.024
# G-V is a very clean design
CD0_INITIAL = 0.020  # initial estimate, to be calibrated

# Estimated maximum L/D
# For a well-designed business jet: 16-18
# Gulfstream has cited L/D values in the 17-18 range for the GV
LD_MAX_ESTIMATED = 17.5  # approximate


# =============================================================================
# 4. ENGINE SPECIFICATIONS
# =============================================================================

# Engine: Rolls-Royce BR710-A1-10 (also designated BR710-48)
# Number of engines: 2
# Source: EASA TCDS E.012, Rolls-Royce data, Jane's Aero Engines

ENGINE_TYPE = "Rolls-Royce BR710-A1-10"
ENGINE_COUNT = 2

# Sea-level static thrust (uninstalled)
# Source: EASA TCDS E.012, Rolls-Royce
# Takeoff thrust rating: 14,750 lbf per engine
# Some sources cite 14,750 lbf; the BR710-A1-10 variant is rated at this level
# The later BR710-C4-11 (used on G550 and some late G-V) is rated at 15,385 lbf
SLS_THRUST_per_engine_lbf = 14_750  # lbf (sea-level static, takeoff rating)
SLS_THRUST_total_lbf = 14_750 * 2   # 29,500 lbf total

# Maximum continuous thrust
# Typically ~90-95% of takeoff thrust for civil turbofans
MCT_per_engine_lbf = 13_790  # lbf (approximate, ~93.5% of takeoff)

# Thrust-Specific Fuel Consumption (TSFC)
# Source: Various published references, Rolls-Royce data
#
# SLS TSFC (takeoff conditions):
# The BR710 is a medium-bypass-ratio turbofan (BPR ~4.2)
# Typical SLS TSFC for this class: 0.36-0.40 lb/(lbf*hr)
TSFC_SLS = 0.384  # lb/(lbf*hr) at sea level static
# Source: Published BR710 specifications

# Cruise TSFC:
# At typical cruise conditions (FL410-FL510, Mach 0.80-0.85):
# Published cruise TSFC values for BR710: approximately 0.64-0.69 lb/(lbf*hr)
#
# Note: TSFC increases significantly from SLS to cruise conditions due to
# ram drag effects and off-design operation. For a BPR ~4.2 engine:
# - SLS TSFC: ~0.38 lb/(lbf*hr)
# - Cruise TSFC at M0.80, FL450: ~0.65-0.67 lb/(lbf*hr)
#
# Some references:
# - Jane's Aero Engines: cruise TSFC ~0.66 lb/(lbf*hr) at Mach 0.80
# - Industry references: 0.64-0.69 lb/(lbf*hr) range
TSFC_CRUISE = 0.657  # lb/(lbf*hr) at cruise (M0.80, ~FL450)
# This value will be refined during calibration

# Engine bypass ratio
BYPASS_RATIO = 4.2  # approximate
# Source: Rolls-Royce BR710 data

# Engine overall pressure ratio
OVERALL_PRESSURE_RATIO = 23.0  # approximate at takeoff
# Source: EASA TCDS, Rolls-Royce data

# Engine dry weight
ENGINE_DRY_WEIGHT_lb = 3_620  # lb per engine (approximate)
# Source: Jane's Aero Engines

# Engine dimensions (approximate)
ENGINE_FAN_DIAMETER_in = 48.2  # inches
ENGINE_LENGTH_in = 89.0        # inches


# =============================================================================
# 5. CRUISE PERFORMANCE
# =============================================================================

# Cruise speeds
# Source: Gulfstream spec sheet, Jane's
MACH_LONG_RANGE_CRUISE = 0.80   # Long-range cruise (maximum range speed)
MACH_NORMAL_CRUISE = 0.82       # Normal cruise
MACH_HIGH_SPEED_CRUISE = 0.85   # High-speed cruise
MACH_MAX_OPERATING = 0.885      # Mmo (maximum operating Mach number)
# Source: FAA TCDS A12EA: Mmo = 0.885

# Typical cruise altitude
# The G-V is designed for high-altitude cruise
CRUISE_ALTITUDE_TYPICAL_ft = 45_000   # ft (typical initial cruise)
CRUISE_ALTITUDE_MAX_ft = 51_000       # ft (maximum certified altitude)
# Note: The G-V was the first business jet certified to FL510

# Service ceiling
SERVICE_CEILING_ft = 51_000  # ft
# Source: FAA TCDS A12EA, Gulfstream spec sheet
# Note: This is an exceptionally high service ceiling. The G-V was specifically
# designed for high-altitude, long-range operations.

# Initial cruise altitude capability
# At MTOW (90,500 lb), the aircraft cannot immediately cruise at FL510.
# Typical initial cruise altitude at MTOW: FL410-FL430
# As fuel burns off, the aircraft step-climbs to higher altitudes
INITIAL_CRUISE_ALTITUDE_AT_MTOW_ft = 41_000  # approximate

# True airspeed at typical cruise
# At FL450, M0.80: TAS ~460 ktas
# At FL450, M0.85: TAS ~489 ktas
TAS_LRC_FL450_ktas = 460  # approximate, at LRC Mach 0.80
TAS_HSC_FL450_ktas = 489  # approximate, at HSC Mach 0.85


# =============================================================================
# 6. FUSELAGE AND EXTERNAL DIMENSIONS
# =============================================================================

# Overall dimensions
# Source: Gulfstream APM, spec sheet
OVERALL_LENGTH_ft = 96.42       # ft (96 ft 5 in)
OVERALL_LENGTH_m = 29.39        # m
OVERALL_HEIGHT_ft = 25.83       # ft (25 ft 10 in)
OVERALL_HEIGHT_m = 7.87         # m

# Fuselage dimensions
FUSELAGE_EXTERNAL_DIAMETER_ft = 7.83   # ft (approximate, ~94 inches)
FUSELAGE_EXTERNAL_WIDTH_in = 94.0      # inches (approximate)

# Cabin dimensions (interior)
# Source: Gulfstream spec sheet
CABIN_LENGTH_ft = 50.17         # ft (50 ft 2 in) - usable cabin length
CABIN_LENGTH_m = 15.29          # m
CABIN_WIDTH_ft = 7.33           # ft (7 ft 4 in) = 88 inches
CABIN_WIDTH_in = 88.0           # inches
CABIN_HEIGHT_ft = 6.17          # ft (6 ft 2 in) = 74 inches
CABIN_HEIGHT_in = 74.0          # inches

# Cabin volume
CABIN_VOLUME_cuft = 1_669       # cubic feet (approximate)

# Baggage compartment
BAGGAGE_VOLUME_cuft = 226       # cubic feet (external aft baggage)

# Door dimensions
MAIN_DOOR_HEIGHT_in = 69.0      # inches (approximate)
MAIN_DOOR_WIDTH_in = 32.0       # inches (approximate)


# =============================================================================
# 7. SOURCE CITATIONS AND CONFIDENCE NOTES
# =============================================================================

SOURCES = {
    "faa_tcds": {
        "document": "FAA Type Certificate Data Sheet A12EA",
        "url": "https://rgl.faa.gov/Regulatory_and_Guidance_Library/rgMakeModel.nsf/",
        "parameters": ["MTOW", "MLW", "Mmo", "service_ceiling", "engine_rating"],
        "confidence": "HIGH - Primary regulatory document",
    },
    "gulfstream_apm": {
        "document": "Gulfstream G-V Airport Planning Manual",
        "url": "https://www.gulfstream.com/en/aircraft-performance/airport-planning",
        "parameters": ["MTOW", "MLW", "MZFW", "dimensions", "wing_area", "wingspan"],
        "confidence": "HIGH - Manufacturer planning document",
    },
    "gulfstream_spec": {
        "document": "Gulfstream G-V Specifications (marketing/public)",
        "url": "https://www.gulfstream.com/en/aircraft/gulfstream-gv",
        "parameters": ["range", "speed", "cabin_dimensions", "OEW", "fuel_capacity"],
        "confidence": "HIGH for dimensions and speeds; MEDIUM for range (marketing "
                      "figures may use favorable assumptions)",
    },
    "janes": {
        "document": "Jane's All the World's Aircraft (various editions)",
        "parameters": ["OEW", "wing_area", "engine_specs", "performance_data"],
        "confidence": "HIGH - Independent reference; cross-checks manufacturer data",
    },
    "easa_tcds_engine": {
        "document": "EASA Type Certificate Data Sheet E.012 (BR710)",
        "url": "https://www.easa.europa.eu/en/document-library/type-certificates",
        "parameters": ["engine_thrust", "TSFC_SLS", "bypass_ratio", "OPR"],
        "confidence": "HIGH - Primary regulatory document for engine",
    },
    "rr_br710_data": {
        "document": "Rolls-Royce BR710 engine specifications (public)",
        "parameters": ["cruise_TSFC", "engine_weight", "dimensions"],
        "confidence": "MEDIUM-HIGH for cruise TSFC (published values are approximate; "
                      "exact cruise TSFC depends on installation and conditions)",
    },
}


# =============================================================================
# 8. CONFLICTING VALUES AND RESOLUTION
# =============================================================================

CONFLICTS = {
    "OEW": {
        "values_found": {
            "46,000 lb": "Some aviation databases (lighter/stripped config)",
            "46,800 lb": "Jane's (may be manufacturer empty weight, not OEW)",
            "48,200 lb": "Gulfstream spec sheet (typical executive interior)",
            "48,800 lb": "Some references (heavier interior options)",
        },
        "selected": "48,200 lb",
        "rationale": "Gulfstream's own published figure for typical executive "
                     "configuration. This is the most commonly cited value and "
                     "represents the standard production configuration. The range "
                     "reflects different interior fitouts.",
    },
    "max_fuel_weight": {
        "values_found": {
            "41,300 lb": "Most sources (Gulfstream spec, Jane's)",
            "41,580 lb": "Some aviation databases",
        },
        "selected": "41,300 lb",
        "rationale": "Most commonly cited value; consistent with published fuel "
                     "capacity in gallons (6,104 gal * 6.77 lb/gal = 41,324 lb).",
    },
    "range_8pax": {
        "values_found": {
            "5,800 nmi": "Gulfstream marketing, most sources (M0.80, NBAA IFR)",
            "6,500 nmi": "Some references (may be max fuel, reduced payload)",
            "6,750 nmi": "Some references (may be ferry range, no reserves)",
        },
        "selected": "5,800 nmi for 8-pax; ~6,500 nmi for ferry",
        "rationale": "5,800 nmi is the well-established headline figure at Mach "
                     "0.80 with NBAA IFR reserves and 8 passengers. Higher figures "
                     "correspond to lighter payloads or reduced reserves.",
    },
    "wing_area": {
        "values_found": {
            "1,137 sq ft": "Most sources",
            "1,137.4 sq ft": "Some detailed references",
            "105.6 m^2": "Jane's (= 1,136.8 sq ft, effectively the same)",
        },
        "selected": "1,137 sq ft",
        "rationale": "Consistent across sources within rounding.",
    },
    "sls_thrust": {
        "values_found": {
            "14,750 lbf": "EASA TCDS for BR710-A1-10 variant",
            "15,385 lbf": "BR710-C4-11 variant (G550 and late G-V production)",
        },
        "selected": "14,750 lbf",
        "rationale": "The BR710-A1-10 is the original G-V engine variant. The "
                     "higher-thrust C4-11 was introduced with the G550. We use "
                     "the A1-10 rating as specified in the problem statement.",
    },
    "cruise_tsfc": {
        "values_found": {
            "0.64 lb/(lbf*hr)": "Lower end of published estimates",
            "0.657 lb/(lbf*hr)": "Mid-range estimate from engine references",
            "0.69 lb/(lbf*hr)": "Upper end of published estimates",
        },
        "selected": "0.657 lb/(lbf*hr)",
        "rationale": "Mid-range value. Will be refined during model calibration "
                     "against range-payload data. The calibration process will "
                     "adjust this to match observed performance.",
    },
}


# =============================================================================
# 9. SUMMARY DICTIONARY (for programmatic access)
# =============================================================================

GV_SPECS = {
    "name": "Gulfstream G-V",
    "designation": "GV",

    # Weights (lb)
    "MTOW_lb": MTOW_lb,
    "MLW_lb": MLW_lb,
    "MZFW_lb": MZFW_lb,
    "OEW_lb": OEW_lb,
    "max_payload_lb": MAX_PAYLOAD_lb,
    "max_fuel_lb": MAX_FUEL_lb,
    "max_ramp_weight_lb": MAX_RAMP_WEIGHT_lb,

    # Range-payload corner points
    "range_payload_points": RANGE_PAYLOAD_POINTS,
    "range_references": RANGE_REFERENCE_POINTS,

    # Wing / aerodynamics
    "wing_span_ft": WING_SPAN_ft,
    "wing_area_sqft": WING_AREA_sqft,
    "aspect_ratio": ASPECT_RATIO,
    "wing_sweep_deg": WING_SWEEP_deg,
    "oswald_efficiency_initial": OSWALD_EFFICIENCY_INITIAL,
    "cd0_initial": CD0_INITIAL,
    "ld_max_estimated": LD_MAX_ESTIMATED,

    # Engines
    "engine_type": ENGINE_TYPE,
    "engine_count": ENGINE_COUNT,
    "sls_thrust_per_engine_lbf": SLS_THRUST_per_engine_lbf,
    "sls_thrust_total_lbf": SLS_THRUST_total_lbf,
    "mct_per_engine_lbf": MCT_per_engine_lbf,
    "tsfc_sls": TSFC_SLS,
    "tsfc_cruise": TSFC_CRUISE,
    "bypass_ratio": BYPASS_RATIO,
    "overall_pressure_ratio": OVERALL_PRESSURE_RATIO,
    "engine_dry_weight_lb": ENGINE_DRY_WEIGHT_lb,

    # Cruise performance
    "mach_lrc": MACH_LONG_RANGE_CRUISE,
    "mach_normal_cruise": MACH_NORMAL_CRUISE,
    "mach_hsc": MACH_HIGH_SPEED_CRUISE,
    "mmo": MACH_MAX_OPERATING,
    "service_ceiling_ft": SERVICE_CEILING_ft,
    "cruise_altitude_typical_ft": CRUISE_ALTITUDE_TYPICAL_ft,
    "initial_cruise_alt_mtow_ft": INITIAL_CRUISE_ALTITUDE_AT_MTOW_ft,

    # Fuselage dimensions
    "overall_length_ft": OVERALL_LENGTH_ft,
    "overall_height_ft": OVERALL_HEIGHT_ft,
    "cabin_length_ft": CABIN_LENGTH_ft,
    "cabin_width_in": CABIN_WIDTH_in,
    "cabin_height_in": CABIN_HEIGHT_in,
    "fuselage_external_width_in": FUSELAGE_EXTERNAL_WIDTH_in,

    # Fuel capacity
    "fuel_capacity_gal": FUEL_CAPACITY_gal,
}
