"""Boeing P-8 Poseidon aircraft data.

Derived from the Boeing 737-900ER with modifications per the study
problem statement (CLAUDE.md). The P-8's detailed performance specs
are not publicly available, so this model is constructed by modifying
a calibrated 737-900ER baseline.

Source: CLAUDE.md problem statement for P-8-specific modifications.
Base aircraft data: boeing_737_900er.py

Modifications from 737-900ER baseline:
    1. Wing: Higher aspect ratio with raked wingtips (swept wing tips)
       to reduce induced drag. Modeled as Oswald efficiency improvement.
    2. OEW: Reduced by ~7,500 lb from removal of passenger furnishings.
       P-8 OEW = 737-900ER OEW - 7,500 = 98,495 - 7,500 = 90,995 lb.
    3. Max payload: 23,885 lb (per problem statement).
    4. Max fuel: 73,320 lb (significantly increased from 737-900ER's
       ~46,063 lb via auxiliary fuel tanks).
    5. Max ramp weight: 188,200 lb.

See ASSUMPTIONS_LOG.md entry E2 for uncertainty discussion.
"""

# Import base aircraft data for reference
# (The performance model will use this to derive P-8 from calibrated 737-900ER)

AIRCRAFT = {
    "name": "Boeing P-8 Poseidon",
    "designation": "P-8",

    # --- Weights (all in lb) ---
    "OEW": 90_995,            # 737-900ER OEW (98,495) - 7,500 lb furnishings
    "MTOW": 188_200,          # Per problem statement (max ramp weight used as MTOW proxy)
    # Note: The problem statement gives "maximum ramp weight: 188,200 lb".
    # The actual MTOW would be slightly less (~187,700 lb, same as 737-900ER).
    # Using 188,200 as the operational max weight per problem statement.
    "MZFW": 146_300,          # Same structural limit as 737-900ER (assumed)
    # This may differ for the P-8 but is not publicly specified.
    "max_payload": 23_885,    # Per problem statement
    "max_fuel": 73_320,       # Per problem statement — aux fuel tanks added
    "max_ramp_weight": 188_200,  # Per problem statement

    # Weight cross-checks:
    #   OEW + max_payload = 90,995 + 23,885 = 114,880 lb
    #   OEW + max_fuel = 90,995 + 73,320 = 164,315 lb
    #   OEW + max_payload + max_fuel = 90,995 + 23,885 + 73,320 = 188,200 lb = MTOW ✓
    #   (The P-8 can carry max payload AND max fuel simultaneously — fills to MTOW exactly)
    #
    #   At max payload: fuel = MTOW - OEW - max_payload = 188,200 - 90,995 - 23,885 = 73,320 lb = max fuel
    #   At max fuel: payload = MTOW - OEW - max_fuel = 188,200 - 90,995 - 73,320 = 23,885 lb = max payload
    #   Ferry: TOW = OEW + max_fuel = 164,315 lb (below MTOW)

    # --- Range-Payload Calibration Points ---
    # These must be estimated after calibrating the 737-900ER model,
    # then applying the P-8 modifications. Initial estimates:
    "range_payload_points": [
        # Point A: Max payload + max fuel (both fit within MTOW)
        # payload = 23,885 lb, fuel = 73,320 lb, TOW = 188,200 lb
        (23_885, 73_320, 4_500),  # estimated — to be refined after calibration
        # Point B: Same as Point A for P-8 (max payload + max fuel = MTOW exactly)
        # Point C: Max fuel, zero payload (ferry)
        # fuel = 73,320 lb, TOW = 164,315 lb
        (0, 73_320, 5_800),  # estimated — to be refined after calibration
    ],
    # Note: Range estimates are preliminary. The P-8 model will be derived
    # from the calibrated 737-900ER by modifying weights and drag.

    # --- Geometry ---
    # Same wing planform as 737-900ER but with raked wingtips
    "wing_area_ft2": 1_344,       # same as 737-900ER
    "wingspan_ft": 117.42,         # geometric span same; raked tips extend beyond
    # The raked wingtips add effective span but the reference geometric span
    # used for AR calculation remains the same. The benefit is captured in
    # the Oswald efficiency factor.
    "aspect_ratio": 10.26,         # same reference geometry as 737-900ER
    "wing_sweep_deg": 25.02,
    "fuselage_length_ft": 138.17,  # same as 737-900ER
    "fuselage_interior_width_ft": 11.6,  # same structure

    # --- Propulsion ---
    "n_engines": 2,
    "engine_type": "CFM56-7B27",   # P-8 uses the higher-thrust variant
    "thrust_per_engine_slst_lbf": 27_300,  # higher thrust than standard 737-900ER
    "total_thrust_slst_lbf": 54_600,
    "tsfc_cruise_ref": 0.627,   # same engine family; slight difference from -7B26
    "bypass_ratio": 5.1,

    # --- Performance ---
    "cruise_mach": 0.785,          # same as 737-900ER
    "mmo": 0.82,
    "service_ceiling_ft": 41_000,  # same as 737-900ER

    # --- P-8-Specific Modeling Notes ---
    # Raked wingtip effect on Oswald efficiency:
    # The raked wingtips reduce induced drag. We model this as an increase
    # in the Oswald efficiency factor of approximately 0.02-0.03 above
    # the calibrated 737-900ER value.
    # See ASSUMPTIONS_LOG.md entry E2.
    "oswald_efficiency_delta": 0.025,  # added to 737-900ER calibrated value

    # --- Notes ---
    "notes": [
        "Derived from 737-900ER — not independently calibrated",
        "Passenger furnishings removed (-7,500 lb from OEW)",
        "Auxiliary fuel tanks added (fuel capacity: 46,063 → 73,320 lb)",
        "Raked wingtips for reduced induced drag",
        "Max payload + max fuel fills to MTOW exactly (unusual characteristic)",
        "Military variant — detailed specs are not publicly available",
        "Performance estimates carry higher uncertainty than other aircraft",
    ],
}
