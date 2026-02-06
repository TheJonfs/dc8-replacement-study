"""NASA DC-8-72 (N817NA) aircraft data.

Source: Provided in study problem statement (CLAUDE.md).
This is the NASA-modified configuration with CFM56-2-C1 engines and
science laboratory customizations. NOT a stock DC-8.

Engine: CFM International CFM56-2-C1
  - Four engines, wing-mounted
  - Sea level static thrust: ~22,000 lbf per engine (88,000 lbf total)
  - Cruise TSFC: ~0.65 lb/(lbf·hr) at typical cruise conditions
  - TSFC sources: Jane's Aero Engines, ICAO Engine Emissions Databank

Geometry sources: DC-8 type certificate, aviation reference documents.
"""

AIRCRAFT = {
    "name": "DC-8-72 (NASA)",
    "designation": "DC-8",

    # --- Weights (all in lb) ---
    "OEW": 157_000,          # Operating Empty Weight (NASA modified config)
    "MTOW": 325_000,         # Maximum Takeoff Weight
    "MZFW": 209_000,         # Maximum Zero Fuel Weight
    "max_payload": 52_000,   # MZFW - OEW
    "max_fuel": 147_255,     # Maximum fuel weight

    # Weight cross-checks:
    #   OEW + max_payload = 157000 + 52000 = 209000 = MZFW ✓
    #   OEW + max_fuel = 157000 + 147255 = 304255 < MTOW ✓
    #   MTOW - OEW - max_fuel = 325000 - 157000 - 147255 = 20745 lb payload at max fuel

    # --- Range-Payload Calibration Points ---
    # These are the primary calibration targets for the performance model.
    "range_payload_points": [
        # (payload_lb, fuel_lb, range_nmi)
        # Point 1: Max payload, fuel to MTOW
        #   fuel = MTOW - OEW - max_payload = 325000 - 157000 - 52000 = 116000 lb
        (52_000, 116_000, 2_750),
        # Point 2: Max fuel, payload to MTOW
        #   payload = MTOW - OEW - max_fuel = 325000 - 157000 - 147255 = 20745 lb
        (20_745, 147_255, 5_400),
        # Point 3: Max fuel, zero payload (ferry)
        (0, 147_255, 6_400),
    ],

    # --- Geometry ---
    "wing_area_ft2": 2868.0,      # ft² (from DC-8 type certificate)
    "wingspan_ft": 148.4,          # ft (with CFM56 engine pods)
    "aspect_ratio": 7.68,          # wingspan² / wing_area
    "fuselage_length_ft": 187.4,   # ft (overall length)
    "fuselage_interior_width_ft": 11.6,  # ft (interior cabin width, approximate)

    # --- Propulsion ---
    "n_engines": 4,
    "engine_type": "CFM56-2-C1",
    "thrust_per_engine_slst_lbf": 22_000,  # sea level static thrust, lbf
    "total_thrust_slst_lbf": 88_000,
    "tsfc_cruise_ref": 0.65,   # lb/(lbf·hr) at cruise conditions (~35,000 ft, M0.80)
    # Note: This is an initial estimate. Will be refined during calibration.
    # CFM56-2 series TSFC data from ICAO emissions databank and Jane's:
    #   SFC at takeoff: ~0.37 lb/(lbf·hr)  [lower because of higher thrust/lower SFC at max power]
    #   SFC at cruise: ~0.60-0.68 lb/(lbf·hr) [partial throttle at altitude]
    # The CFM56-2 is an older variant; the -5 and -7 series are more efficient.

    # --- Performance ---
    "cruise_mach": 0.80,
    "service_ceiling_ft": 42_000,
    "max_cruise_alt_ft": 41_000,   # typical max initial cruise altitude

    # --- Notes ---
    "notes": [
        "NASA-modified configuration — weights differ from commercial DC-8-72",
        "Re-engined from JT3D to CFM56-2-C1 turbofans",
        "Science laboratory interior — no standard passenger configuration",
        "T-tail configuration",
        "Four wing-mounted engines",
    ],
}
