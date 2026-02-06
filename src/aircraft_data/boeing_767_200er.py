"""
Boeing 767-200ER Aircraft Data
==============================

Data collected from publicly available sources for use in the DC-8 replacement
aircraft performance study. All values are for the 767-200ER (Extended Range)
variant unless otherwise noted.

Primary Sources:
    [1] Boeing 767 Airplane Characteristics for Airport Planning (D6-58328)
        https://www.boeing.com/resources/boeingdotcom/commercial/airports/acaps/767.pdf
    [2] FAA Type Certificate Data Sheet A1NM (Rev 72+)
        https://rgl.faa.gov/Regulatory_and_Guidance_Library/rgMakeModel.nsf/
    [3] Boeing 767 Wikipedia / standard aviation references
        https://en.wikipedia.org/wiki/Boeing_767
    [4] GE CF6-80A2 / CF6-80C2 engine specifications from GE Aviation
    [5] Jane's All the World's Aircraft (various editions)

Engine variant notes:
    The 767-200ER was offered with several engine options:
      - Pratt & Whitney JT9D-7R4D (48,000 lbf) -- early production
      - General Electric CF6-80A2 (50,000 lbf) -- common early option
      - Pratt & Whitney PW4052 (52,000 lbf) -- later production
      - General Electric CF6-80C2B2 (52,500 lbf) -- later production
    The CF6-80C2B2 and PW4052 are the most common on later-build ER variants
    and are the engines we model, as they represent the most capable configuration.

Weight reconciliation notes:
    MTOW - OEW = max available for fuel + payload = 395,000 - 179,080 = 215,920 lb
    MZFW - OEW = 235,000 - 179,080 = 55,920 lb (structural payload limit)
    At max structural payload (55,920 lb):
      fuel = MTOW - MZFW = 395,000 - 235,000 = 160,000 lb (MTOW limited, within tank cap.)
      TOW = MTOW = 395,000 lb
    At max fuel (162,000 lb):
      payload = MTOW - OEW - max_fuel = 395,000 - 179,080 - 162,000 = 53,920 lb
      This is below MZFW - OEW = 55,920, so MTOW is the binding constraint (not MZFW).
    At ferry (max fuel, zero payload):
      TOW = OEW + max_fuel = 179,080 + 162,000 = 341,080 lb

Fuel capacity derivation:
    The 767-200ER has wing tanks plus a center section (body) fuel tank added for
    the extended range capability. Boeing's Airport Planning Document (D6-58328)
    lists the total usable fuel capacity for the 767-200ER as approximately
    24,140 US gallons. At a standard Jet-A density of 6.7 lb/US gallon:
        24,140 gal * 6.7 lb/gal = 161,738 lb
    We round to 162,000 lb for the maximum fuel weight.

    CRITICAL NOTE: Many online references incorrectly cite the base 767-200
    fuel capacity (~16,700 US gallons / ~91,000 lb) for the 767-200ER. The ER
    variant has significantly more fuel capacity due to the center section tank.

    Cross-check with Breguet equation:
    At typical airline payload (33,000 lb) with max fuel, the published range is
    ~6,600 nmi. Using L/D ~ 17 and TSFC ~ 0.60 at M0.80/FL350:
      R = (V/TSFC) * (L/D) * ln(Wi/Wf)
      Wi = 179,080 + 33,000 + fuel, Wf = Wi - fuel_burned
    Working backwards: fuel ~ 150,000-160,000 lb required -- consistent with
    the ~162,000 lb capacity but NOT consistent with the ~91,000 lb figure.
"""

# =============================================================================
# WEIGHT DATA
# =============================================================================

# Maximum Takeoff Weight (MTOW)
# Source: [1] Boeing APD, [2] FAA TCDS A1NM
# The TCDS lists 395,000 lb for the 767-200ER (CF6-80C2B2 or PW4052 engines).
# Some earlier CF6-80A2 variants had lower MTOW.
# We use 395,000 lb as it represents the most capable and most common ER config.
MTOW_LB = 395_000  # lb
# Conflicting values:
#   351,000 lb -- early production 767-200ER (rarely referenced) [2]
#   387,000 lb -- production 767-200ER with CF6-80A2 engines [2]
#   395,000 lb -- later production with CF6-80C2B2 or PW4052 [1][2]
# Selected: 395,000 lb (most common ER configuration, matches Boeing APD)

# Maximum Ramp Weight (MRW) / Maximum Taxi Weight
# Source: [1] Boeing APD
MRW_LB = 396_000  # lb (MTOW + taxi fuel allowance, typically ~1,000 lb)

# Operating Empty Weight (OEW)
# Source: [1] Boeing APD, [3] various references
# OEW varies significantly by airline configuration. Boeing's standard OEW for
# the 767-200ER is approximately 179,080 lb in a typical two-class configuration.
OEW_LB = 179_080  # lb (Boeing standard, two-class ~216 passenger config)
# Conflicting values:
#   176,500 lb -- some references cite lighter configurations
#   179,080 lb -- Boeing standard two-class [1]
#   181,610 lb -- heavier configurations or with additional options
# Selected: 179,080 lb (Boeing's published standard for the ER variant)
# Note: For the NASA science mission study, interior furnishings would be
# removed (reducing OEW) but replaced with science equipment mounting
# structure. We use the standard OEW as a baseline.

# Maximum Zero Fuel Weight (MZFW)
# Source: [1] Boeing APD, [2] FAA TCDS
# This is the structural limit on combined OEW + payload (no fuel in wings).
MZFW_LB = 235_000  # lb
# Conflicting values: consistent across Boeing APD and TCDS for the ER variant

# Maximum Payload Weight
# Derived from MZFW - OEW (structural payload limit)
MAX_PAYLOAD_LB = MZFW_LB - OEW_LB  # = 55,920 lb
# Note: Some references cite lower max payload (~52,720 lb) for typical airline
# configurations where cargo hold volume limits payload. For the science mission
# study we use the structural limit since scientific payloads are dense.
# The actual structural payload capacity is slightly higher than MZFW - OEW
# because crew, oil, and operational items are counted in ZFW but not OEW.

# Maximum Landing Weight (MLW)
# Source: [1] Boeing APD, [2] FAA TCDS
MLW_LB = 290_000  # lb
# Conflicting values:
#   283,000 lb -- some references for earlier variants
#   290,000 lb -- standard for the 395,000 lb MTOW ER variant [1]

# Maximum Fuel Weight
# Source: [1] Boeing APD
# The 767-200ER has wing tanks plus a center section fuel tank.
# Total usable fuel capacity: approximately 24,140 US gallons.
# At standard Jet-A density of 6.7 lb/gal: 24,140 * 6.7 = 161,738 lb
MAX_FUEL_LB = 162_000  # lb (rounded from 161,738 lb)
FUEL_CAPACITY_GAL = 24_140  # US gallons (usable)
#
# IMPORTANT NOTE ON CONFLICTING VALUES:
#   ~91,000 lb (~13,600 gal) -- This is the base 767-200 capacity WITHOUT center
#       section tank. Many online references incorrectly cite this for the ER.
#   ~162,000 lb (~24,140 gal) -- This is the correct 767-200ER capacity WITH
#       the center section tank that defines the "ER" variant [1].
#   Cross-check: The 767-200ER's published design range of 6,600 nmi at typical
#       airline load is physically impossible with only 91,000 lb of fuel. The
#       Breguet equation requires ~150,000+ lb of fuel for this range, confirming
#       the higher fuel capacity figure.
# Selected: 162,000 lb (Boeing APD, confirmed by range cross-check)


# =============================================================================
# RANGE-PAYLOAD DIAGRAM CORNER POINTS
# =============================================================================
# Standard three-corner-point range-payload diagram:
#
# Point A: Maximum payload, fuel to fill to MTOW
#   Payload = MZFW - OEW = 55,920 lb (structural limit)
#   Fuel = MTOW - MZFW = 395,000 - 235,000 = 160,000 lb
#   TOW = MTOW = 395,000 lb
#   Note: fuel (160,000) < max fuel (162,000), so fuel is MTOW-limited, not tank-limited.
#
# Point B: Maximum fuel, payload to fill to MTOW
#   Fuel = 162,000 lb (max fuel)
#   Payload = MTOW - OEW - max_fuel = 395,000 - 179,080 - 162,000 = 53,920 lb
#   Check MZFW: OEW + 53,920 = 233,000 < 235,000 MZFW -- OK
#   TOW = MTOW = 395,000 lb
#   Note: Points A and B are close together (payload drops from 55,920 to 53,920,
#   fuel increases from 160,000 to 162,000) because max fuel nearly fills
#   the MTOW - MZFW gap.
#
# Point C: Ferry -- maximum fuel, zero payload
#   Fuel = 162,000 lb
#   Payload = 0 lb
#   TOW = OEW + max_fuel = 179,080 + 162,000 = 341,080 lb

# Published range data (Source: [1] Boeing APD, [3] various references):
RANGE_MAX_PAYLOAD_NMI = 5_990  # nmi at max structural payload (55,920 lb)
# At max payload: fuel = 160,000 lb (MTOW limited), TOW = 395,000 lb

RANGE_MAX_FUEL_NMI = 6_100  # nmi at max fuel with reduced payload (53,920 lb)
# At max fuel: payload slightly reduced, TOW = 395,000 lb
# Points A and B are very close in both payload and range because the
# fuel increase (2,000 lb) is small relative to total fuel.

RANGE_DESIGN_NMI = 6_600  # nmi at typical airline load (~33,000 lb payload)
# This is Boeing's commonly quoted "design range" figure for the 767-200ER.

RANGE_FERRY_NMI = 7_900  # nmi at max fuel, zero payload
# Ferry range with max fuel (162,000 lb), zero payload
# TOW = OEW + fuel = 179,080 + 162,000 = 341,080 lb

# For the range-payload diagram calibration, we define three well-separated points:
RANGE_PAYLOAD_POINTS = {
    "point_A": {
        "description": "Max structural payload, fuel to MTOW",
        "payload_lb": 55_920,
        "fuel_lb": 160_000,  # MTOW - MZFW
        "tow_lb": 395_000,
        "range_nmi": 5_990,
        "notes": "MTOW-limited; fuel slightly below max tank capacity"
    },
    "point_B": {
        "description": "Max fuel, payload to MTOW",
        "payload_lb": 53_920,  # MTOW - OEW - max_fuel
        "fuel_lb": 162_000,
        "tow_lb": 395_000,
        "range_nmi": 6_100,
        "notes": "Max fuel with reduced payload; very close to Point A"
    },
    "point_C": {
        "description": "Ferry range -- max fuel, zero payload",
        "payload_lb": 0,
        "fuel_lb": 162_000,
        "tow_lb": 341_080,  # OEW + max fuel
        "range_nmi": 7_900,
        "notes": "Maximum ferry range"
    },
}

# Additional published range reference points for calibration:
RANGE_ADDITIONAL_POINTS = {
    "typical_airline": {
        "description": "Typical two-class airline load (~216 pax, ~33,000 lb payload)",
        "payload_lb": 33_000,
        "fuel_lb": 162_000,  # max fuel (below MTOW with this payload)
        "tow_lb": 374_080,  # OEW + 33,000 + 162,000
        "range_nmi": 6_600,
        "notes": "Boeing's commonly published design range figure"
    },
}


# =============================================================================
# GEOMETRY / DIMENSIONS
# =============================================================================

# Wing
# Source: [1] Boeing APD, [3]
WING_SPAN_FT = 156.08  # ft (47.57 m)
# Consistent across sources [1][3]

WING_AREA_SQFT = 3_050  # sq ft (283.3 m^2)
# Conflicting values:
#   3,050 sq ft -- most common figure [1][3]
#   3,130 sq ft -- some references (may include different measurement conventions)
# Selected: 3,050 sq ft (Boeing APD)

ASPECT_RATIO = WING_SPAN_FT**2 / WING_AREA_SQFT  # = 7.99
# Cross-check: commonly cited as ~8.0, which matches

WING_SWEEP_DEG = 31.5  # degrees (quarter-chord sweep)
# Source: [1] Boeing APD

# Fuselage
# Source: [1] Boeing APD
FUSELAGE_LENGTH_FT = 159.17  # ft (48.51 m) -- overall aircraft length
# Some references cite fuselage-only length differently; this is overall

FUSELAGE_OUTER_DIAMETER_FT = 16.42  # ft (5.03 m) -- external diameter
# Consistent across sources

FUSELAGE_INTERIOR_WIDTH_FT = 15.5  # ft (4.72 m) -- interior cabin width
# Conflicting values:
#   15.5 ft / 4.72 m -- commonly cited [1]
#   15.0 ft -- some references (may measure at floor vs. max width)
# The 767 has a distinctive wide-body fuselage with 2-3-2 economy seating.
CABIN_WIDTH_IN = 186  # inches (~15.5 ft)
# Wider than a narrow-body (DC-8 ~139 in, 737 ~139 in) but narrower than
# full wide-bodies (A330 ~222 in, 777 ~231 in). Sometimes called "semi-wide-body."

# Tail height
TAIL_HEIGHT_FT = 52.0  # ft (15.85 m) -- from ground to top of vertical stabilizer

# Number of engines
N_ENGINES = 2


# =============================================================================
# ENGINE DATA
# =============================================================================

# Primary engine option modeled: General Electric CF6-80C2B2
# Alternative: Pratt & Whitney PW4052 (very similar thrust class)
# Source: [4] GE Aviation specifications, [5] Jane's

ENGINE_TYPE = "GE CF6-80C2B2"
ENGINE_TYPE_ALT = "PW4052"

# Sea-level static thrust (uninstalled)
# Source: [4]
SLS_THRUST_PER_ENGINE_LBF = 52_500  # lbf per engine (CF6-80C2B2)
SLS_THRUST_TOTAL_LBF = SLS_THRUST_PER_ENGINE_LBF * N_ENGINES  # = 105,000 lbf
# Conflicting values:
#   48,000 lbf -- JT9D-7R4D (earlier engine option, not modeled)
#   50,000 lbf -- CF6-80A2 (earlier GE option)
#   52,000 lbf -- PW4052
#   52,500 lbf -- CF6-80C2B2 [4]
# Selected: 52,500 lbf (CF6-80C2B2, matches the 395,000 lb MTOW variant)

# Cruise TSFC
# Source: [4], [5], various engine performance references
# The CF6-80C2 family has cruise TSFC in the range of 0.58-0.64 lb/(lbf*hr)
# at typical cruise conditions (M0.80, 35,000 ft).
CRUISE_TSFC_LB_LBF_HR = 0.605  # lb/(lbf*hr) at M0.80, FL350
# Conflicting values:
#   0.58 lb/(lbf*hr) -- optimistic, best-point cruise TSFC
#   0.60-0.61 lb/(lbf*hr) -- typical mid-cruise TSFC [4][5]
#   0.64 lb/(lbf*hr) -- higher values at off-design conditions
# Selected: 0.605 lb/(lbf*hr) as a representative mid-cruise value
# Note: This is an initial estimate and WILL be adjusted during calibration
# to match the published range-payload data.

# SFC at sea level static conditions (for reference/takeoff modeling)
SLS_TSFC_LB_LBF_HR = 0.37  # lb/(lbf*hr) at sea level static (approximate)

# Bypass ratio
BYPASS_RATIO = 5.15  # CF6-80C2B2
# The CF6-80C2 is a high-bypass turbofan (BPR ~5.0-5.3)

# Overall pressure ratio
OPR = 30.4  # CF6-80C2B2 (approximate)


# =============================================================================
# CRUISE PERFORMANCE
# =============================================================================

# Cruise Mach number
# Source: [1] Boeing APD, [3]
CRUISE_MACH = 0.80  # typical long-range cruise Mach
# The 767-200ER has:
#   Long-range cruise (LRC) Mach: ~0.80
#   High-speed cruise Mach: ~0.82
#   Maximum operating Mach (Mmo): 0.86
MMO = 0.86  # Maximum operating Mach number [2]

# Cruise speed
CRUISE_TAS_KT = 460  # kt TAS at typical cruise altitude (~M0.80 at FL350)
# This varies with altitude and temperature; approximate value

# Service ceiling
SERVICE_CEILING_FT = 43_100  # ft
# Source: [1] Boeing APD
# Conflicting values:
#   43,100 ft -- most common figure [1]
#   42,000 ft -- some references (may be for max weight)
# Note: Certified service ceiling. Actual achievable cruise altitude
# depends heavily on aircraft weight.

# Initial cruise altitude (at or near MTOW)
INITIAL_CRUISE_ALT_FT = 33_000  # ft (approximate, weight-dependent)
# At heavy weights near MTOW, the 767-200ER typically cruises at FL310-FL350.
# At lighter weights (mid-mission), it can step-climb to FL370-FL410.


# =============================================================================
# SUMMARY DICT FOR PROGRAMMATIC ACCESS
# =============================================================================

AIRCRAFT_DATA = {
    "name": "Boeing 767-200ER",
    "designation": "767-200ER",

    # Weights (lb)
    "mtow_lb": MTOW_LB,
    "mrw_lb": MRW_LB,
    "oew_lb": OEW_LB,
    "mzfw_lb": MZFW_LB,
    "mlw_lb": MLW_LB,
    "max_payload_lb": MAX_PAYLOAD_LB,
    "max_fuel_lb": MAX_FUEL_LB,
    "fuel_capacity_gal": FUEL_CAPACITY_GAL,

    # Geometry
    "wing_span_ft": WING_SPAN_FT,
    "wing_area_sqft": WING_AREA_SQFT,
    "aspect_ratio": ASPECT_RATIO,
    "wing_sweep_deg": WING_SWEEP_DEG,
    "fuselage_length_ft": FUSELAGE_LENGTH_FT,
    "fuselage_outer_diameter_ft": FUSELAGE_OUTER_DIAMETER_FT,
    "fuselage_interior_width_ft": FUSELAGE_INTERIOR_WIDTH_FT,
    "cabin_width_in": CABIN_WIDTH_IN,
    "tail_height_ft": TAIL_HEIGHT_FT,

    # Engines
    "n_engines": N_ENGINES,
    "engine_type": ENGINE_TYPE,
    "sls_thrust_per_engine_lbf": SLS_THRUST_PER_ENGINE_LBF,
    "sls_thrust_total_lbf": SLS_THRUST_TOTAL_LBF,
    "cruise_tsfc_lb_lbf_hr": CRUISE_TSFC_LB_LBF_HR,
    "bypass_ratio": BYPASS_RATIO,

    # Performance
    "cruise_mach": CRUISE_MACH,
    "mmo": MMO,
    "service_ceiling_ft": SERVICE_CEILING_FT,

    # Range-payload calibration points
    "range_payload_points": RANGE_PAYLOAD_POINTS,
    "range_additional_points": RANGE_ADDITIONAL_POINTS,
}
