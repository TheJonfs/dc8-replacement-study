# DC-8 Replacement Aircraft Performance Study — Report Sections

This directory contains the final report as a series of modular markdown files, numbered for assembly order. Each file corresponds to a section of the report and is sized for manageable editing context.

## Section Map

| File | Section | Figures Referenced |
|---|---|---|
| `00_abstract.md` | Abstract | --- |
| `01_introduction.md` | 1. Introduction | --- |
| `02_aircraft.md` | 2. Candidate Aircraft | --- |
| `03_methodology.md` | 3. Performance Modeling Methodology | --- |
| `04_calibration.md` | 4. Calibration Results | Figs 1-7 (range-payload diagrams) |
| `05_mission1.md` | 5. Mission 1: Engine-Out Transport | Figs 8-10 (weight, altitude, Mach) |
| `06_mission2.md` | 6. Mission 2: Vertical Sampling | Figs 11-13 (ceiling, sawtooth, weight) |
| `07_mission3.md` | 7. Mission 3: Low-Altitude Survey | Fig 14 (weight) |
| `08_synthesis.md` | 8. Cross-Mission Synthesis | Fig 15 (fuel cost) |
| `09_qualitative.md` | 9. Qualitative Factors | --- |
| `10_limitations.md` | 10. Model Limitations and Confidence | --- |
| `11_conclusions.md` | 11. Conclusions and Recommendations | --- |

## Figure Map

| Figure | Source File | Section |
|---|---|---|
| Fig 1 | `outputs/plots/rp_overlay_all.png` | 4 (Calibration) |
| Figs 2-7 | `outputs/plots/rp_*.png` | 4 (Calibration) |
| Fig 8 | `outputs/plots/weight_breakdown_m1.png` | 5 (Mission 1) |
| Fig 9 | `outputs/plots/profile_m1_altitude.png` | 5 (Mission 1) |
| Fig 10 | `outputs/plots/profile_m1_mach.png` | 5 (Mission 1) |
| Fig 11 | `outputs/plots/profile_m2_ceiling.png` | 6 (Mission 2) |
| Fig 12 | `outputs/plots/profile_m2_altitude.png` | 6 (Mission 2) |
| Fig 13 | `outputs/plots/weight_breakdown_m2.png` | 6 (Mission 2) |
| Fig 14 | `outputs/plots/weight_breakdown_m3.png` | 7 (Mission 3) |
| Fig 15 | `outputs/plots/fuel_cost_comparison.png` | 8 (Synthesis) |

## LaTeX Conversion Notes

- Each markdown file maps to one `\section{}` or `\chapter{}` in LaTeX
- Tables use standard markdown format; convert to `tabular` environments
- Figure references are marked with HTML comments: `<!-- Figure reference: path -> Figure N -->`
- Math expressions use `$$...$$` (display) and `$...$` (inline) LaTeX notation
- The `---` used in aircraft names (e.g., "767-200ER") should not be converted to em-dashes
