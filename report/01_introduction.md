# 1. Introduction

## 1.1 Background

NASA's Airborne Science Program (ASP) operates a fleet of research aircraft supporting atmospheric science, Earth observation, and instrument development campaigns worldwide. The DC-8-72 Flying Laboratory (N817NA) serves as the program's premier large platform, carrying heavy science payloads (up to 52,000 lb) with teams of investigators on missions spanning continents and oceans. Originally manufactured in 1969, the aircraft was re-engined with CFM56-2-C1 turbofans and extensively modified with a laboratory interior, structural reinforcements for external sensor mounts, and fuselage cutouts for atmospheric sampling instruments.

Despite these modifications, the DC-8 faces growing operational challenges driven by its age:

- **Crew availability**: The pool of pilots trained and current on the DC-8 type is shrinking, with few opportunities for new qualification as the fleet population dwindles.
- **Spare parts**: Original equipment components are increasingly difficult to source, with some requiring custom fabrication.
- **Ground support**: Airport handling equipment compatible with the DC-8's configuration is no longer standard at many destination airports.
- **Operating costs**: The CFM56-2-C1 engines, while a significant improvement over the original JT3D turbofans, are less fuel-efficient than current-generation powerplants.
- **Training infrastructure**: Flight simulator availability for the DC-8 type is extremely limited.

These factors motivate a systematic evaluation of potential replacement aircraft.

## 1.2 Objective

This study asks: given a set of candidate replacement aircraft spanning a range of sizes and configurations, how do they compare to the DC-8 in their ability to perform representative airborne science missions?

The evaluation is quantitative, based on physics-based aircraft performance models calibrated against publicly available specifications. Three metrics drive the comparison:

1. **Feasibility**: Can the aircraft complete the mission as defined (range, payload, altitude, duration)?
2. **Fuel consumption**: How much fuel does the mission require, and what reserves remain?
3. **Cost efficiency**: What is the fuel cost per unit of science payload transported per unit distance?

The study also considers qualitative factors drawn from interviews with ASP scientists and flight operations personnel --- preferences regarding altitude capability, fuselage configuration, engine redundancy, and payload flexibility --- that a purely numerical analysis cannot capture.

## 1.3 Scope

The study models six aircraft: the DC-8-72 baseline and five candidates. Three science missions are defined to exercise different regions of the flight envelope: long-range transport with an engine failure, vertical atmospheric profiling with repeated climb-descend cycles, and extended low-altitude endurance. The performance models are built from first principles (Breguet range equation, parabolic drag polar, altitude-dependent thrust and fuel consumption models) and calibrated against published range-payload corner points before being applied to the science missions.

The study does not address structural modification feasibility, certification requirements, acquisition cost, or fleet transition logistics. These are important considerations for a replacement decision but fall outside the scope of a performance comparison study.

## 1.4 Report Organization

This report is organized as follows. Section 2 describes the six aircraft and their key specifications. Section 3 presents the performance modeling methodology, including the atmosphere model, aerodynamic and propulsion models, and the calibration procedure. Section 4 reports calibration results and assesses model confidence for each aircraft. Sections 5 through 7 present results for the three science missions. Section 8 provides a cross-mission synthesis with consolidated cost comparisons. Section 9 discusses qualitative factors from the scientist and operator interviews. Section 10 assesses model limitations and their impact on conclusions. Section 11 presents conclusions and recommendations.
