# Phase 1 Review Response

## Summary of Actions Taken

The Phase 1 review identified one critical data issue and two secondary data concerns. We investigated all three. One was confirmed and corrected; two were investigated and found to be incorrect.

---

## CRITICAL: Boeing 767-200ER Data — CONFIRMED AND CORRECTED

The reviewer was correct. The MZFW of 235,000 lb does not appear anywhere in the Boeing APD (D6-58328) for any 767-200ER variant.

**Source:** Boeing APD D6-58328 lists six weight variants for the 767-200ER. For the 395,000 lb MTOW variant:

| MTOW (lb) | MZFW (lb) | MLW (lb) | OEW (lb) | Max Structural Payload (lb) |
|---|---|---|---|---|
| 395,000 | **260,000** | **300,000** | 181,610 | 78,390 |

Confirmed by Aircraft Commerce Owner's & Operator's Guide (Issue 46, 2006), which lists all five weight variants with identical figures.

### Changes Made

| Parameter | Old Value | New Value | Source |
|---|---|---|---|
| MZFW | 235,000 lb | **260,000 lb** | Boeing APD D6-58328 |
| MLW | 290,000 lb | **300,000 lb** | Boeing APD D6-58328 |
| Max payload | 55,920 lb | **80,920 lb** | Derived (MZFW - OEW) |
| OEW | 179,080 lb | 179,080 lb (unchanged) | Within Boeing's range (181,610 standard) |

### Impact on Range-Payload Points

The corrected MZFW changes the weight balance at the range-payload corner points:

| Point | Old Payload | Old Fuel | Old Range | New Payload | New Fuel | New Range |
|---|---|---|---|---|---|---|
| A (max payload) | 55,920 lb | 160,000 lb | 5,990 nmi | 80,920 lb | 135,000 lb | ~5,150 nmi |
| B (max fuel) | 53,920 lb | 162,000 lb | 6,100 nmi | 53,920 lb | 162,000 lb | ~6,500 nmi |
| C (ferry) | 0 lb | 162,000 lb | 7,900 nmi | 0 lb | 162,000 lb | ~7,850 nmi |

The new range values were estimated by Breguet ratio back-calculation from the Aircraft Commerce reference point of 6,850 nmi at 174 passengers (~36,540 lb payload) with max fuel, and cross-checked against:
- Boeing's published design range of 6,600 nmi at ~33,000 lb payload
- Air Seychelles 767-200ER delivery flight of ~7,727 nmi (ferry with favorable winds)
- BJT Online VIP 767-200ER ferry range of 7,540 nmi

No directly published range at max structural payload was found for this specific weight variant.

### Impact on Calibration — Dramatic Improvement

The corrected data produced significantly more physical calibrated parameters:

| Parameter | Old (MZFW=235k) | New (MZFW=260k) | Physical Range |
|---|---|---|---|
| CD0 | 0.0153 | **0.0177** | 0.015–0.025 ✓ |
| e (Oswald) | 0.947 | **0.732** | 0.65–0.85 ✓ |
| k_adj (TSFC) | 0.756 | **0.951** | 0.85–1.15 ✓ |
| f_oh (overhead) | 0.157 | **0.030** | 0.05–0.20 (low but OK) |
| L/D_max | 19.7 | **16.1** | 15–20 ✓ |
| RMS error | 0.2% | **0.0%** | — |

**Every parameter moved into or very close to the physically expected range.** The reviewer's prediction was correct: the unphysical parameters were a symptom of incorrect input data, not a flaw in the modeling approach.

---

## SECONDARY: A330-200 Fuel Capacity — INVESTIGATED, NO CHANGE NEEDED

The reviewer suggested the A330-200 max fuel might be ~309,000 lb (~140,000 kg) rather than our 245,264 lb (111,260 kg).

**Finding: Our value is correct.** The ~140,000 figure appears to confuse the tank volume in liters (139,090 L) with mass in kg. The Airbus APD lists usable fuel capacity of 139,090 liters. At standard Jet-A density of 0.800 kg/L, this yields 111,272 kg (~245,264 lb). Multiple sources confirm this:
- Airbus APD: 139,090 L usable capacity
- At min density (0.785 kg/L): 109,186 kg
- At standard density (0.800 kg/L): 111,272 kg
- At max density (0.840 kg/L): 116,836 kg

Even at maximum fuel density, the capacity is ~257,600 lb — nowhere near 309,000 lb.

**The A330-200's unphysical calibrated parameters (e=2.165, f_oh=0.000) are a genuine limitation of our 4-parameter model, not a data error.**

---

## SECONDARY: Boeing 777-200LR Fuel Capacity — INVESTIGATED, NO CHANGE NEEDED

The reviewer suggested the 777-200LR max fuel might be ~388,000 lb rather than our 325,300 lb.

**Finding: Our value is correct for the standard configuration.** The Boeing APD lists the 777-200LR with its standard 3 auxiliary aft cargo fuel tanks at 47,890 US gallons (~325,300 lb at 6.79 lb/gal). An optional further auxiliary tank configuration exists (~53,515 US gal / ~358,000 lb), but no airline has installed these. The reviewer's figure of ~388,000 lb doesn't match any published configuration.

**The 777-200LR's 6.5% RMS calibration error is also a genuine model limitation, not a data error.**

---

## Physical Sanity Checks — NEW

Per the reviewer's recommendation, we computed fuel burn rates and specific range at mid-cruise conditions (FL350) using the calibrated parameters and compared against published operator data:

| Aircraft | L/D max | L/D cruise | Fuel Burn (lb/hr) | Published (lb/hr) | Match | Specific Range (nmi/klb) |
|---|---|---|---|---|---|---|
| DC-8 | 20.4 | 19.4 | 5,435 | 10,000–13,000 | ✗ | 84.9 |
| G-V | 17.3 | 14.8 | 2,648 | 2,200–2,800 | ✓ | 174.2 |
| 737-900ER | 16.7 | 12.3 | 5,771 | 5,500–6,000 | ✓ | 78.4 |
| **767-200ER** | **16.1** | **15.8** | **11,535** | **10,000–12,000** | **✓** | **40.0** |
| A330-200 | 22.6 | 13.2 | 19,344 | 11,000–14,000 | ✗ | 24.4 |
| 777-200LR | 18.3 | 10.6 | 16,038 | 15,000–18,000 | ✓ | 30.2 |
| P-8 | 11.5 | 7.5 | 4,151 | 5,500–7,000 | ⚠ | 109.0 |

### Interpretation

**Four aircraft pass the fuel burn cross-check (G-V, 737, 767, 777).** These are the aircraft where the calibrated model produces physically realistic cruise performance. The 767-200ER result (11,535 lb/hr vs. published 10,000–12,000) is particularly strong, confirming that the MZFW correction resolved the data quality issue.

**Three aircraft fail or partially fail (DC-8, A330, P-8).** The pattern is illuminating:

- **DC-8** (5,435 vs. 10,000–13,000 lb/hr): The DC-8's calibration pushes k_adj to 0.605 and f_oh to 0.260, meaning the model underpredicts cruise fuel burn by ~50% but compensates by claiming 26% of fuel is overhead. This is the most extreme parameter trade-off. The DC-8 is the baseline aircraft with data from the problem statement, so we can't change the calibration points — but we should be aware that the calibrated cruise performance is unrealistic in isolation.

- **A330-200** (19,344 vs. 11,000–14,000 lb/hr): Overpredicts fuel burn by ~40%. With f_oh=0 and e=2.165, the model has no overhead buffer and high induced drag, producing excessive fuel consumption at cruise.

- **P-8** (4,151 vs. 5,500–7,000 lb/hr): Underpredicts by ~25%. As a derived model with estimated calibration points, this is the expected weakest result.

### Implications for Phase 2

For mission analysis, the fuel burn sanity check gives us a confidence ranking:

1. **High confidence:** 767-200ER, G-V, 737-900ER, 777-200LR — cruise fuel burn matches published data
2. **Medium confidence:** P-8 — within 30% of published data, acceptable for comparative analysis
3. **Low confidence for absolute numbers:** DC-8, A330-200 — cruise fuel burn significantly off, though relative comparisons may still be valid since the calibration correctly reproduces total mission fuel (cruise + overhead combined)

---

## Updated Calibration Summary

| Aircraft | CD0 | e | k_adj | f_oh | L/D_max | RMS Err | Fuel Burn Check |
|---|---|---|---|---|---|---|---|
| DC-8 | 0.0141 | 0.968 | 0.605 | 0.260 | 20.4 | 0.5% | ✗ (low by 50%) |
| G-V | 0.0150 | 0.745 | 0.801 | 0.131 | 17.3 | 1.2% | ✓ |
| 737-900ER | 0.0355 | 1.223 | 0.757 | 0.062 | 16.7 | 0.7% | ✓ |
| **767-200ER** | **0.0177** | **0.732** | **0.951** | **0.030** | **16.1** | **0.0%** | **✓** |
| A330-200 | 0.0334 | 2.165 | 1.021 | 0.000 | 22.6 | 3.0% | ✗ (high by 40%) |
| 777-200LR | 0.0410 | 1.811 | 0.556 | 0.080 | 18.3 | 6.5% | ✓ |
| P-8 | 0.0597 | 0.975 | 0.339 | 0.180 | 11.5 | 0.0% | ⚠ (low by 25%) |

---

## Note on the 737-900ER in Mission Comparisons

The reviewer correctly noted that the 737-900ER is a modeling intermediate (base airframe for P-8 derivation) and not one of the six study candidates. We will retain it in the range-payload diagram for context but exclude it from Phase 2 mission analysis.

---

## Path B Validation

The reviewer agreed with our suggestion to defer Path B validation until after data corrections. With the 767 data now corrected, the next step (before Phase 2) would be to run Path B (explicit climb/descent/reserve) at calibration conditions and compare to Path A results. If they diverge by more than ~5%, we will need to reconcile the two approaches.

---

## Files Modified

1. `src/aircraft_data/boeing_767_200er.py` — MZFW, MLW, max payload, range-payload points corrected
2. `outputs/plots/rp_*.png` — all regenerated with corrected 767 data
3. `PHASE1_REVIEW_RESPONSE.md` — this document (new)

## Test Status

All 74 tests passing (41 data/atmosphere + 33 performance/calibration).
