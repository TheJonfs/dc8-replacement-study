"""Boeing 777-200LR aircraft data.

Sources:
    [1] Boeing 777 Airplane Characteristics for Airport Planning (D6-58329-2)
        https://www.boeing.com/resources/boeingdotcom/commercial/airports/acaps/777_200LR.pdf
    [2] FAA Type Certificate Data Sheet A28NM
        https://rgl.faa.gov (search TCDS A28NM)
    [3] Boeing Commercial Airplanes 777 specifications page
        https://www.boeing.com/commercial/777
    [4] GE Aviation GE90 engine specifications
        https://www.geaviation.com/commercial/engines/ge90-engine
    [5] FAA Type Certificate Data Sheet E00049EN (GE90 engine family)
    [6] Jane's All the World's Aircraft

The 777-200LR (Long Range) is the ultra-long-range variant of the 777-200.
It features raked wingtips and three auxiliary fuel tanks in the aft cargo
hold, giving it the longest range of any commercial aircraft when introduced.

Weight notes:
    MTOW - OEW = 766,000 - 320,000 = 446,000 lb available for fuel + payload
    MZFW - OEW = 455,000 - 320,000 = 135,000 lb max structural payload
    At max payload: fuel = MTOW - MZFW = 766,000 - 455,000 = 311,000 lb (< max fuel)
    At max fuel: payload = MTOW - OEW - max_fuel = 766,000 - 320,000 - 325,300 = 120,700 lb
    Ferry: TOW = OEW + max_fuel = 320,000 + 325,300 = 645,300 lb (below MTOW)
"""

AIRCRAFT = {
    "name": "Boeing 777-200LR",
    "designation": "777-200LR",

    # --- Weights (all in lb) ---
    "OEW": 320_000,            # Typical 3-class configuration [1][3]
    # OEW range: 318,000-326,000 lb depending on configuration.
    # Using 320,000 as a commonly cited typical value.
    "MTOW": 766_000,           # [1][2] — certified value
    "MZFW": 455_000,           # [1][2] — certified value
    "MLW": 492_000,            # [1][2]
    "max_payload": 135_000,    # MZFW - OEW = 455,000 - 320,000
    "max_fuel": 325_300,       # [1] — includes 3 aux aft cargo tanks
    # Fuel capacity: ~47,890 US gal. At 6.79 lb/gal = 325,271 lb ≈ 325,300 lb.
    # Some sources cite ~320,860 lb; we use the higher figure representing
    # full auxiliary tank installation.
    "max_ramp_weight": 767_000,  # [1]

    # --- Range-Payload Calibration Points ---
    "range_payload_points": [
        # Point A: Max payload, fuel to MTOW
        # payload = 135,000 lb, fuel = MTOW - MZFW = 311,000 lb (below max fuel capacity)
        (135_000, 311_000, 7_500),
        # Point B: Max fuel, payload to MTOW
        # fuel = 325,300 lb, payload = MTOW - OEW - max_fuel = 120,700 lb
        (120_700, 325_300, 9_400),
        # Point C: Max fuel, zero payload (ferry)
        # TOW = OEW + max_fuel = 645,300 lb
        (0, 325_300, 10_800),
    ],
    # Boeing published reference: 8,555 nmi with 301 pax (~63,210 lb payload)
    # at max fuel (325,300 lb), TOW = 708,510 lb (below MTOW)
    "range_reference_points": [
        {"payload_lb": 63_210, "fuel_lb": 325_300, "range_nmi": 8_555,
         "notes": "Boeing published headline: 301 pax, 3-class, max fuel"},
    ],

    # --- Geometry ---
    "wing_area_ft2": 4_702,       # [1]
    "wingspan_ft": 212.58,         # [1] — includes raked wingtips
    "aspect_ratio": 9.61,          # wingspan^2 / wing_area = 212.58^2 / 4702
    "wing_sweep_deg": 31.6,        # quarter-chord [1]
    "fuselage_length_ft": 209.08,  # overall length [1]
    "fuselage_outer_diameter_ft": 20.33,  # [1]
    "fuselage_interior_width_ft": 19.25,  # cabin width [1]
    "cabin_width_in": 231,         # inches, approximate

    # --- Propulsion ---
    "n_engines": 2,
    "engine_type": "GE90-110B1",
    "thrust_per_engine_slst_lbf": 110_100,  # [4][5] sea level static takeoff
    "total_thrust_slst_lbf": 220_200,
    "tsfc_cruise_ref": 0.545,   # lb/(lbf·hr) estimated at M0.84, FL350-FL390
    # TSFC range from sources: 0.52-0.56. Using 0.545 as central estimate.
    # This will be calibrated against range-payload data.
    # The GE90-110B is a very high bypass ratio engine (BPR ~8.4-9.0),
    # giving it excellent cruise fuel efficiency.
    "bypass_ratio": 8.7,         # [4]
    "fan_diameter_in": 128,      # [4]

    # --- Performance ---
    "cruise_mach": 0.84,          # [3] typical long-range cruise
    "mmo": 0.89,                  # [2] maximum operating Mach
    "service_ceiling_ft": 43_100, # [1]
    "max_cruise_alt_ft": 43_000,

    # --- Notes ---
    "notes": [
        "Ultra-long-range variant with raked wingtips",
        "3 auxiliary fuel tanks in aft cargo hold (unique to LR variant)",
        "World-record distance flight: HKG-LHR eastbound, 11,664 nmi (Nov 2005)",
        "Largest twin-engine thrust: 220,200 lbf total",
        "Twin-aisle wide-body — 9/10-abreast economy seating",
        "Conventional low-tail configuration (not T-tail)",
    ],
}
