"""Unified aircraft data loader.

Normalizes the different data file formats into a consistent dictionary
structure for use by the performance model. Each aircraft gets a dict with
standardized keys regardless of how the underlying data file was structured.

Standard keys:
    name            str     Human-readable name
    designation     str     Short code (e.g., "DC-8", "GV", "P-8")
    OEW             float   Operating Empty Weight, lb
    MTOW            float   Maximum Takeoff Weight, lb
    MZFW            float   Maximum Zero Fuel Weight, lb
    max_payload     float   Maximum payload weight, lb
    max_fuel        float   Maximum fuel weight, lb
    range_payload_points  list of (payload_lb, fuel_lb, range_nmi) tuples
        The standard 2-3 corner points of the range-payload diagram.
    wing_area_ft2   float   Reference wing area, ft²
    wingspan_ft     float   Wingspan, ft
    aspect_ratio    float   Wing aspect ratio
    n_engines       int     Number of engines
    engine_type     str     Engine designation
    thrust_per_engine_slst_lbf  float  Sea level static thrust per engine, lbf
    tsfc_cruise_ref float   Reference cruise TSFC, lb/(lbf·hr)
    cruise_mach     float   Typical cruise Mach number
    service_ceiling_ft float Service ceiling, ft
    fuselage_length_ft float Overall fuselage/aircraft length, ft
    fuselage_interior_width_ft float Interior cabin width, ft
"""


def _load_dc8():
    from src.aircraft_data.dc8_72 import AIRCRAFT
    return AIRCRAFT


def _load_gv():
    from src.aircraft_data.gulfstream_gv import GV_SPECS
    s = GV_SPECS
    return {
        "name": s["name"],
        "designation": s["designation"],
        "OEW": s["OEW_lb"],
        "MTOW": s["MTOW_lb"],
        "MZFW": s["MZFW_lb"],
        "max_payload": s["max_payload_lb"],
        "max_fuel": s["max_fuel_lb"],
        "range_payload_points": [
            (s["range_payload_points"]["max_payload"]["payload_lb"],
             s["range_payload_points"]["max_payload"]["fuel_lb"],
             s["range_payload_points"]["max_payload"]["range_nmi"]),
            (s["range_payload_points"]["max_fuel"]["payload_lb"],
             s["range_payload_points"]["max_fuel"]["fuel_lb"],
             s["range_payload_points"]["max_fuel"]["range_nmi"]),
            (s["range_payload_points"]["ferry"]["payload_lb"],
             s["range_payload_points"]["ferry"]["fuel_lb"],
             s["range_payload_points"]["ferry"]["range_nmi"]),
        ],
        "wing_area_ft2": s["wing_area_sqft"],
        "wingspan_ft": s["wing_span_ft"],
        "aspect_ratio": s["aspect_ratio"],
        "n_engines": s["engine_count"],
        "engine_type": s["engine_type"],
        "thrust_per_engine_slst_lbf": s["sls_thrust_per_engine_lbf"],
        "total_thrust_slst_lbf": s["sls_thrust_total_lbf"],
        "tsfc_cruise_ref": s["tsfc_cruise"],
        "cruise_mach": s["mach_lrc"],
        "service_ceiling_ft": s["service_ceiling_ft"],
        "fuselage_length_ft": s["overall_length_ft"],
        "fuselage_interior_width_ft": s["cabin_width_in"] / 12.0,
    }


def _load_737():
    from src.aircraft_data import boeing_737_900er as b
    return {
        "name": "Boeing 737-900ER",
        "designation": "737-900ER",
        "OEW": b.OEW_lb,
        "MTOW": b.MTOW_lb,
        "MZFW": b.MZFW_lb,
        "max_payload": b.max_payload_lb,
        "max_fuel": b.max_fuel_lb,
        "range_payload_points": [
            (b.payload_at_max_payload_lb, b.fuel_at_max_payload_lb, b.range_at_max_payload_nmi),
            (b.payload_at_max_fuel_lb, b.fuel_at_max_fuel_lb, b.range_at_max_fuel_nmi),
            (b.payload_at_ferry_lb, b.fuel_at_ferry_lb, b.ferry_range_nmi),
        ],
        "wing_area_ft2": b.wing_area_sqft,
        "wingspan_ft": b.wingspan_ft,
        "aspect_ratio": b.aspect_ratio,
        "n_engines": b.num_engines,
        "engine_type": b.engine_type,
        "thrust_per_engine_slst_lbf": b.thrust_sl_static_lbf,
        "total_thrust_slst_lbf": b.thrust_sl_static_lbf * b.num_engines,
        "tsfc_cruise_ref": b.tsfc_cruise_lb_per_lbf_hr,
        "cruise_mach": b.mach_cruise_typical,
        "service_ceiling_ft": b.service_ceiling_ft,
        "fuselage_length_ft": b.overall_length_ft,
        "fuselage_interior_width_ft": b.cabin_interior_width_ft,
    }


def _load_767():
    from src.aircraft_data.boeing_767_200er import AIRCRAFT_DATA
    d = AIRCRAFT_DATA
    rp = d["range_payload_points"]
    return {
        "name": d["name"],
        "designation": d["designation"],
        "OEW": d["oew_lb"],
        "MTOW": d["mtow_lb"],
        "MZFW": d["mzfw_lb"],
        "max_payload": d["max_payload_lb"],
        "max_fuel": d["max_fuel_lb"],
        "range_payload_points": [
            (rp["point_A"]["payload_lb"], rp["point_A"]["fuel_lb"], rp["point_A"]["range_nmi"]),
            (rp["point_B"]["payload_lb"], rp["point_B"]["fuel_lb"], rp["point_B"]["range_nmi"]),
            (rp["point_C"]["payload_lb"], rp["point_C"]["fuel_lb"], rp["point_C"]["range_nmi"]),
        ],
        "wing_area_ft2": d["wing_area_sqft"],
        "wingspan_ft": d["wing_span_ft"],
        "aspect_ratio": d["aspect_ratio"],
        "n_engines": d["n_engines"],
        "engine_type": d["engine_type"],
        "thrust_per_engine_slst_lbf": d["sls_thrust_per_engine_lbf"],
        "total_thrust_slst_lbf": d["sls_thrust_total_lbf"],
        "tsfc_cruise_ref": d["cruise_tsfc_lb_lbf_hr"],
        "cruise_mach": d["cruise_mach"],
        "service_ceiling_ft": d["service_ceiling_ft"],
        "fuselage_length_ft": d["fuselage_length_ft"],
        "fuselage_interior_width_ft": d["fuselage_interior_width_ft"],
    }


def _load_a330():
    from src.aircraft_data import a330_200 as a
    return {
        "name": "Airbus A330-200",
        "designation": "A330-200",
        "OEW": a.OEW_LB,
        "MTOW": a.MTOW_LB,
        "MZFW": a.MZFW_LB,
        "max_payload": a.MAX_PAYLOAD_LB,
        "max_fuel": a.MAX_FUEL_LB,
        "range_payload_points": [
            (int(a.PAYLOAD_AT_MAX_PAYLOAD_KG * 2.20462),
             int(a.FUEL_AT_MAX_PAYLOAD_KG * 2.20462),
             a.RANGE_MAX_PAYLOAD_NMI),
            (int(a.PAYLOAD_AT_MAX_FUEL_KG * 2.20462),
             int(a.FUEL_AT_MAX_FUEL_KG * 2.20462),
             a.RANGE_MAX_FUEL_NMI),
            (0,
             int(a.FUEL_AT_FERRY_KG * 2.20462),
             a.RANGE_FERRY_NMI),
        ],
        "wing_area_ft2": a.WING_AREA_FT2,
        "wingspan_ft": a.WINGSPAN_FT,
        "aspect_ratio": a.ASPECT_RATIO,
        "n_engines": a.ENGINE_COUNT,
        "engine_type": a.ENGINE_TYPE,
        "thrust_per_engine_slst_lbf": a.THRUST_SLS_PER_ENGINE_LBF,
        "total_thrust_slst_lbf": a.THRUST_SLS_TOTAL_LBF,
        "tsfc_cruise_ref": a.CRUISE_TSFC_LB_LBF_HR,
        "cruise_mach": a.CRUISE_MACH_TYPICAL,
        "service_ceiling_ft": a.SERVICE_CEILING_FT,
        "fuselage_length_ft": a.OVERALL_LENGTH_FT,
        "fuselage_interior_width_ft": a.CABIN_WIDTH_FT,
    }


def _load_777():
    from src.aircraft_data.boeing_777_200lr import AIRCRAFT
    return AIRCRAFT


def _load_p8():
    from src.aircraft_data.boeing_p8 import AIRCRAFT
    return AIRCRAFT


# Registry of all aircraft
_LOADERS = {
    "DC-8": _load_dc8,
    "GV": _load_gv,
    "737-900ER": _load_737,
    "767-200ER": _load_767,
    "A330-200": _load_a330,
    "777-200LR": _load_777,
    "P-8": _load_p8,
}


def load_aircraft(designation):
    """Load normalized aircraft data by designation.

    Args:
        designation: One of "DC-8", "GV", "737-900ER", "767-200ER",
                     "A330-200", "777-200LR", "P-8"

    Returns:
        dict with standardized keys (see module docstring)
    """
    if designation not in _LOADERS:
        raise ValueError(
            f"Unknown aircraft '{designation}'. "
            f"Available: {list(_LOADERS.keys())}"
        )
    return _LOADERS[designation]()


def load_all_aircraft():
    """Load all aircraft data as a dict keyed by designation."""
    return {name: loader() for name, loader in _LOADERS.items()}


def validate_aircraft(data):
    """Run basic consistency checks on aircraft data.

    Returns list of (level, message) tuples where level is 'ERROR' or 'WARNING'.
    """
    issues = []
    name = data.get("name", "unknown")

    # Weight checks
    oew = data.get("OEW", 0)
    mtow = data.get("MTOW", 0)
    mzfw = data.get("MZFW", 0)
    max_payload = data.get("max_payload", 0)
    max_fuel = data.get("max_fuel", 0)

    if oew <= 0:
        issues.append(("ERROR", f"{name}: OEW must be positive"))
    if mtow <= 0:
        issues.append(("ERROR", f"{name}: MTOW must be positive"))
    if oew >= mtow:
        issues.append(("ERROR", f"{name}: OEW ({oew}) >= MTOW ({mtow})"))

    # MZFW check
    if mzfw > 0:
        expected_payload = mzfw - oew
        if abs(expected_payload - max_payload) > 5000:
            issues.append(("WARNING",
                f"{name}: max_payload ({max_payload}) differs from "
                f"MZFW-OEW ({expected_payload}) by {abs(expected_payload - max_payload)} lb"))

    # Can't carry max payload AND max fuel simultaneously (unless designed that way)
    total = oew + max_payload + max_fuel
    if total > mtow * 1.01:  # 1% tolerance
        pass  # This is normal — just means there's a trade-off

    # Range-payload points should have decreasing payload and increasing range
    rp = data.get("range_payload_points", [])
    if len(rp) >= 2:
        for i in range(len(rp) - 1):
            if rp[i][2] >= rp[i+1][2]:
                issues.append(("WARNING",
                    f"{name}: Range-payload point {i} range ({rp[i][2]}) >= "
                    f"point {i+1} range ({rp[i+1][2]}) — expected increasing range"))

    # Physical reasonableness
    ar = data.get("aspect_ratio", 0)
    if ar > 0 and (ar < 5 or ar > 15):
        issues.append(("WARNING",
            f"{name}: Aspect ratio {ar} outside typical range 5-15"))

    tsfc = data.get("tsfc_cruise_ref", 0)
    if tsfc > 0 and (tsfc < 0.4 or tsfc > 0.8):
        issues.append(("WARNING",
            f"{name}: Cruise TSFC {tsfc} outside typical range 0.4-0.8"))

    return issues
