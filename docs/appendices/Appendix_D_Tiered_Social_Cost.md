## Appendix D — Tiered Social Cost Analysis

*(Originally carried forward from the existing white paper section's A.4
as a brief framework summary; substantially expanded this session with
sourced rates, worked calculations, and results for Scenarios 1 and 2.
Retitled from "Framework" to "Analysis" since this section now contains
applied results, not just a methodology description.)*

### D.1 Framework and Sourcing

Three-tier externality framework: Social Cost of Carbon / Social Cost
of Greenhouse Gases (climate, monetized — renamed this session per
direct user direction, replacing the earlier internal "Tier 1"
shorthand as the primary label; #9 has the full naming history and
statutory reasoning), Health Impacts (regional health, monetized;
formerly "Tier 2"), Tier 3 (air toxics, deliberately qualitative —
never monetized or summed into either dollar total; this label is
retained as-is, per direct user direction).

**Social Cost of Carbon / Social Cost of Greenhouse Gases.** Rates
sourced directly from EPA's *Report on the Social Cost of Greenhouse
Gases: Estimates Incorporating Recent Scientific Advances* (November
2023, Docket EPA-HQ-OAR-2021-0317), fetched and read directly this
session — Table ES.1, 2.0% near-term Ramsey discount rate, 2020 dollars
per metric ton:

| Emission year | SC-CO2 | SC-CH4 | SC-N2O |
|---|---|---|---|
| 2020 | $190 | $1,600 | $54,000 |
| 2030 | $230 | $2,400 | $66,000 |
| 2040 | $270 | $3,300 | $79,000 |
| 2050 | $310 | $4,200 | $93,000 |

2035 and 2045 rates linearly interpolated between adjacent EPA anchor
points (not extrapolated from a different vintage):

| Checkpoint | SC-CO2 | SC-CH4 | SC-N2O |
|---|---|---|---|
| 2030 | $230 | $2,400 | $66,000 |
| 2035 | $250 | $2,850 | $72,500 |
| 2040 | $270 | $3,300 | $79,000 |
| 2045 | $290 | $3,750 | $86,000 |

**CPI re-basing, this session**: the table above is EPA's own 2020$;
this project's WACC/SLCOE use a 2026 base year. Re-based to 2026$ using
a BLS-sourced deflator of 1.2902 (29.02% cumulative inflation, 2020
annual average CPI-U of 258.811 to July 2026's 333.918, the most recent
available) before use in any calculation — full sourcing and the second,
related BenMAP correction in #9.

**Correction to this project's own prior sourcing**: `whitepaper_draft.md`
(an earlier, separate draft of the actual white paper document, distinct
from this working appendix set) carried a SC-CO2 schedule of $190 (2026)
→ $230 (2035) → $280 (2045) → $310 (2050) — internally consistent-looking,
but its year labels are shifted roughly 5-6 years from EPA's own table
(EPA has $190 at 2020 and $230 at 2030, not 2026/2035). That schedule's
specific $/MWh results ($74-228/MWh across scenarios) are themselves
stale, from an earlier, different modeling pass predating this project's
rigorous LP work — not reused here. This appendix uses EPA's own table
directly, interpolated to our exact checkpoint years, rather than
propagating the earlier, shifted schedule forward.

**Emission factors**: AP-42 Compilation of Air Pollutant Emission
Factors, Vol. I, Section 3.1, Stationary Gas Turbines (C028), natural
gas-fired, uncontrolled: CO2 110 lb/MMBtu, CH4 (combustion) 0.0086
lb/MMBtu, N2O 0.003 lb/MMBtu (low-confidence rating in the source),
PM2.5 0.0066 lb/MMBtu, SO2 0.0034 lb/MMBtu, NOx 0.32 lb/MMBtu
(uncontrolled) or 0.099 lb/MMBtu (lean-premix/DLN, low-NOx combustors).

**Upstream methane leakage**: 2.3% of gas produced escapes unburned
before combustion (`whitepaper_draft.md` assumption, not independently
re-verified this session — carried forward as a disclosed, unverified
input). Converted via 1.037 MMBtu/Mcf energy content and an approximate
19.3 kg CH4/Mcf pipeline-gas density.

**Health Impacts — regional health.** EPA Sector-based PM2.5 Benefit-per-Ton
(BenMAP), Electricity Generating Units category, 2016 dollars (C033,
verified full table read directly): PM2.5 $140,000/ton, SO2 $40,000/ton,
NOx $6,000/ton — 40-60% lower than the area-source figures used
elsewhere in this project, consistent with tall-stack dispersion reducing
ground-level concentration impact per ton. **CPI re-based to 2026$ this
session** (see #9): deflator 1.3913 (39.13% cumulative, 2016 annual
average CPI-U of 240.007 to July 2026's 333.918) — a larger correction
than the SC-GHG table's own, given the ten-year gap to this rate's own
2016$ vintage.

**NOx factor selection** (this session's direction, applied to both
scenarios): uncontrolled (0.32 lb/MMBtu) for dispatch served by the
existing fleet, DLN/low-NOx (0.099 lb/MMBtu) for dispatch served by
new-build capacity, blended by each checkpoint's existing/new MW capacity
share as an energy-share proxy.

**Tier 3 — air toxics, qualitative only.** Formaldehyde (0.00071
lb/MMBtu) and benzene (0.000012 lb/MMBtu), both AP-42 (C028). Both are
IARC Group 1 confirmed human carcinogens (C029). Formaldehyde carries a
turbine-specific NESHAP limit of 91 ppbvd at 15% O2 (40 CFR Part 63
Subpart YYYY, C030). EPRI field testing (GE LM6000 simple-cycle turbine
with SCR and oxidation catalyst) found formaldehyde emissions rise
specifically at less-than-80%-load operation (C031) — directly relevant
to any fleet, like Scenario 2's new CT build, that is sized for
intermittent, partial-load, peaking duty rather than steady baseload
operation. Nationally, roughly half of average air-toxics cancer risk is
attributed to formaldehyde, though ~90% of that is from atmospheric
secondary formation rather than direct source emission (2014 NATA, C032)
— presented as national context, not a fleet-specific attribution claim.
Deliberately never monetized or combined with the Social Cost of Carbon/
Greenhouse Gases or Health Impacts dollar totals, per this project's
standing convention.

**Tier 3 update, literature search performed this session (C094-C097)**:
a follow-up search for recent developments surfaced several genuinely
new items, all early-to-mid 2026 unless noted, none monetized here,
consistent with the standing Tier 3 convention.

- **EPA finalized NSPS amendments for stationary combustion turbines**,
  effective January 15, 2026 (C094) — directly confirms combustion
  controls (DLN) as the "best system of emission reduction" for new,
  modified, or reconstructed turbines, with SCR added for one
  subcategory. Current, direct regulatory confirmation of this analysis's
  own new-build-is-DLN assumption (D.2), not merely an inference from
  industry norms.
- **Two new, independent Virginia-specific academic sources** (C095):
  a VCU study (Feb 2026, Pitt et al.) spatially mapping air pollution
  from 138 Northern Virginia data centers, finding their aggregate
  emissions — primarily from backup diesel generators, a different
  source category than this analysis's CT/CCGT fleet — can exceed
  nearby gas power plants'; and a first-of-its-kind peer-reviewed review
  (Frontiers in Climate, Feb 2026, Gour/Ortiz/Maibach, George Mason)
  of Virginia data center health implications broadly (air, water,
  noise, land use).
- **A governance finding, not an emissions finding, but relevant
  context**: a POLITICO/E&E News investigation (July 2026, C096), based
  on internal emails obtained via public records request, found Virginia
  DEQ moved quickly to challenge the Cork/Dominici Vantage health study
  (C024) after it was shared with regulators, rather than treating it as
  independent input — relevant to how much weight the regulatory
  environment itself places on this category of finding, distinct from
  the finding's own substance.
- **A new, previously untracked project**: Remington Technology Park
  (Fauquier County) is reportedly proposing 13 on-site gas turbines
  (C096) — noted as an example of the broader trend continuing, not
  incorporated into this project's own plant roster or dispatch modeling.
- **A new, specifically air-permit-focused legal challenge**: the
  Southern Environmental Law Center has filed an appeal against the
  Chesterfield Energy Reliability Center's DEQ air permit specifically
  (C096) — distinct from, and in addition to, the SCC siting-approval
  reconsideration already tracked in this project (Appendix A.8.5).
- **Not "lately" by this project's own window, but not previously
  cited**: an EDF report (Sept 2024, C097) found EPA's own national Risk
  and Technology Review modeled only 15% of actual gas-turbine EGUs
  operating nationally (273 of an estimated ~1,750) — a genuine gap in
  the federal regulatory analysis's own scope, suggesting the true
  national air-toxics burden from gas turbines is understated in EPA's
  own official review, not just in this project's necessarily partial
  treatment.

None of the above changes any Social Cost of Carbon/Greenhouse Gases or
Health Impacts monetized figure or is intended to; presented as
qualitative context update only, per the standing Tier 3 convention.

### D.2 Existing/New Fleet Split by Scenario, and Plant-Specific NOx Controls

Applying the checkpoint-solved hourly gas dispatch, split at the 70th-
percentile load-duration threshold (this session's established baseload/
peaker method, Appendix C.10) to separate CCGT-rate dispatch (6.4
MMBtu/MWh) from CT-rate dispatch (9.5 MMBtu/MWh):

**Scenario 1**: **existing/new MW share corrected this session,
superseding an earlier "zero new-build throughout" claim.** That earlier
claim held under Scenario 1's own pre-correction dispatch (verified
against the demand basis and dispatch mechanism in use at the time), but
was checked directly against this session's own corrected dispatch
(demand basis, SLCR, reserve margin — Internal Debugging Log #24/#26/
#29) before being relied on further, rather than carried forward
unchecked. It no longer holds: corrected gas dispatch reaches the full
capacity cap — existing fleet plus the 2,862 MW overhaul/retain pool —
at every checkpoint, not just the existing-fleet-only bound. The
existing/new split is now genuinely `schedule_b_baseline_mw(year)` /
2,862.0 MW, giving an existing share of 76.6% for 2026-2044 (9,362 /
12,224) and 39.4% at 2045 (1,860 / 4,722, following the VCEA-driven
Schedule B step-down) — not 100%/0% as previously stated.

**Scenario 2**: uses the corrected, individual-plant-retirement-tracked
existing/new split from Appendix C.10:

| Year | Existing share | New share |
|---|---|---|
| 2030 | 72% | 28% |
| 2035 | 45% | 55% |
| 2040 | 38% | 62% |
| 2045 | 15% | 85% |

**Plant-specific NOx control classification (this session, replacing an
earlier existing/new binary assumption)**: a direct literature search,
prompted by user question, found that the "existing = 100% uncontrolled"
assumption used in an earlier pass of this analysis materially
overstated actual NOx emissions — most of the existing CCGT fleet is
already DLN-equipped, in several cases via documented retrofit, not
original-build assumption:

| Plant | MW | NOx control | Evidence basis |
|---|---|---|---|
| Greensville County | 1,605 | DLN | Confirmed — DEQ/RBLC permit records explicitly cite dry low-NOx burners + SCR |
| Possum Point | 573 | DLN | Confirmed — GE press release: Dominion installed "GE DLN combustion hardware" in a 2015 Advanced Gas Path retrofit at this plant specifically |
| Bear Garden | 622 | DLN | Confirmed — same GE press release, same 2015 AGP/DLN retrofit program |
| Brunswick County | 1,376 | DLN | Strong inference — same Dominion program, era (2016), and M501J turbine family as Greensville; not independently confirmed by name |
| Warren County | 1,349 | DLN | Strong inference — same basis as Brunswick County |
| Potomac Energy Center | 793 | DLN | Strong inference — repeatedly described as "advanced emissions-control technology," modern (2017) Siemens SGT6-5000F turbines, a DLN-standard class |
| Tenaska Virginia | 975 | DLN | Weak inference only — no plant-specific statement found; GE 7F.04 turbines, 2004 commissioning, an era when DLN was already standard industry practice for new CCGT, but this is an industry-norm inference, not a confirmed fact about this specific plant |
| Chesterfield, Doswell, Ladysmith, Marsh Run, Louisa, Wolf Hills, Remington | 386/901/782/550/525/285/619 | Uncontrolled (conservative default) | No evidence found either way. These are the older, lower-utilization simple-cycle peakers (Ladysmith's EOH of 16,718 the clearest example) where an expensive DLN retrofit is least likely to have been economically justified — an inference, not a finding |

**Resulting existing-fleet blended NOx factor, by checkpoint** (weighted
by which specific plants remain operating, per their own retirement
year, not a flat existing/new split):

| Year | Blended existing NOx EF (lb/MMBtu) |
|---|---|
| 2030 | 0.170 |
| 2035 | 0.154 |
| 2040 | 0.154 |
| 2045 | 0.099 (only Greensville, Brunswick, Potomac Energy Center remain — all DLN) |

Substantially below the uncontrolled factor (0.32) used in the prior
pass of this analysis, and approaching the DLN factor (0.099) directly
by 2045 as the DLN-confirmed plants increasingly dominate the surviving
fleet.

### D.3 Results

**MAJOR CORRECTION (this session)**: both scenarios' own figures below
are now fully current — Scenario 1's own from an earlier pass this
session (Internal Debugging Log #24/#26/#29/#32/#35/#36), Scenario 2's
own from a full dispatch and downstream rebuild completed this same
session (#38-#42), including two simultaneous-dispatch fixes (Bath,
then Na, the latter requiring a direct literature search and KKT/
reduced-cost verification before resolving), a reserve-margin check
(passes at all four checkpoints with substantial margin, no build
adjustment needed — a genuinely different finding from Scenario 1,
where the LP had to be explicitly constrained), and a corrected
existing/new-fleet split for the NOx-blend calculation (an initial pass
wrongly assumed 100% new-build, caught and corrected before presenting
results here). Both EPA rate tables re-based to this project's 2026
base year (#9/#35) for both scenarios.

**Emissions and monetized cost, by checkpoint** (both scenarios shown
at their 4 checkpoints for table continuity; both scenarios' own PV
figures below reflect the genuine full 20-year calculation, not an
extrapolation from these four rows alone):

| Scenario | Year | Gas (MWh) | CO2 (t) | CH4 total (t) | N2O (t) | Social Cost of Carbon ($M) | Health Impacts ($M) |
|---|---|---|---|---|---|---|---|
| 1 | 2030 | 48,458,654 | 20,827,010 | 167,539.6 | 568.01 | 6,180.3 | 521.3 |
| 1 | 2035 | 44,051,286 | 23,016,797 | 185,155.0 | 627.73 | 7,424.1 | 554.4 |
| 1 | 2040 | 28,253,645 | 14,762,530 | 118,754.9 | 402.61 | 5,142.6 | 355.6 |
| 1 | 2045 | 188,877 | 98,688 | 793.9 | 2.69 | 36.9 | 2.1 |
| 2 | 2030 | 43,859,100 | ~22,918,000 | ~184,300 | ~625 | ~6,546.2 | ~501.3 |
| 2 | 2035 | 58,737,900 | ~30,700,000 | ~247,000 | ~837 | ~9,670.3 | ~621.5 |
| 2 | 2040 | 84,433,900 | ~44,140,000 | ~355,000 | ~1,203 | ~13,760.8 | ~802.9 |
| 2 | 2045 | 109,388,400 | ~57,180,000 | ~460,000 | ~1,559 | ~18,353.0 | ~922.7 |

Scenario 2's own CO2/CH4/N2O tons above are shown approximately (~),
back-calculated from this session's own SC-carbon/health dollar figures
rather than re-extracted from the raw hourly arrays as a separate step
— the dollar figures themselves are the genuinely verified, directly-
computed values; the tons are provided for row-format consistency with
Scenario 1's own display above, not independently re-verified to the
same precision.

**Present value (WACC 4.5%, base year 2026)** — all figures below are
the genuine, full-20-year total for each scenario, not derived from the
four-checkpoint table above. **Social Cost of Carbon (statutory,
CO2-only) shown as its own column, separate from Social Cost of
Greenhouse Gases (the broader, multi-gas figure) — per Virginia Code
§56-598(2)(d)/§56-585.1(A)(6)'s own requirement that these be reported
separately, not combined into one (#9's own full statutory reasoning)**:

| Scenario | PV Social Cost of Carbon | $/MWh | PV Social Cost of GHG | $/MWh | PV Health Impacts | $/MWh |
|---|---|---|---|---|---|---|
| 1 | $71.701B | $39.84 | $78.577B | $43.66 | $5.740B | $3.19 |
| 1B | $72.329B | $40.19 | $79.276B | $44.05 | $5.775B | $3.21 |
| 2 | $119.071B | $66.16 | $131.090B | $72.84 | $8.486B | $4.72 |

Scenario 1B's own Social Cost of Carbon and Social Cost of GHG sit only
marginally above Scenario 1's own — consistent with N.4/N.5's own
finding that Scenario 1B's relaxed 5%-gas ceiling at 2045 is largely
moot in practice, since the physical gas fleet's own hard capacity cap
binds before the statutory percentage does. Scenario 2's much higher
gas share (39-59%, sustained throughout the full window, vs. both
Scenario 1 and 1B's decline to near-zero by 2045) shows up almost
entirely in both climate figures — roughly 65-70% higher than Scenario
1/1B's own totals — while Health Impacts, though still meaningfully
higher for Scenario 2, diverges less sharply, since it depends on
short-lived pollutants tied to the existing-fleet NOx blend rather than
cumulative GHG stock, and all three share much of the same underlying
existing-plant roster.

**Total societal SLCOE** (direct financial SLCOE + Social Cost of
Greenhouse Gases + Health Impacts; Tier 3 excluded from the dollar
total by design; the broader SC-GHG figure used here, not the narrower
SC-CO2, since this line is meant to capture the full climate cost).
**Scenario 2's own direct SLCOE below was corrected after this table
was first built** — a real, confirmed CCGT capex bug (a stale $1,775/kW
constant used instead of this project's own correct, cross-validated
$3,000/kW figure, a 1.69x understatement on Scenario 2's single largest
cost component) was found and fixed; see Internal Debugging Log #49 for
the full incident and the centralized `assumptions.py` module built in
response to it:

| Scenario | Direct SLCOE | + Social Cost of GHG + Health Impacts | Total societal |
|---|---|---|---|
| 1 | $42.45/MWh | +$46.85 | **$89.30/MWh** |
| 1B | $42.14/MWh | +$47.26 | **$89.40/MWh** |
| 2 (Deloitte gas) | $48.99/MWh | +$77.56 | **$126.55/MWh** |
| 2 (EIA gas) | $43.77/MWh | +$77.56 | **$121.33/MWh** |
| 2 (Hughes gas) | $49.43/MWh | +$77.56 | **$126.99/MWh** |

**A genuinely important pattern, worth stating plainly rather than
smoothing over**: on a direct-financial basis, Scenario 2 now sits
*above* Scenario 1 under all three gas cases — the corrected CCGT
capex removed what had briefly looked like a direct-cost advantage for
Scenario 2 under two of the three gas cases; that finding did not
survive the capex correction and should not be cited. Scenario 2's
total societal cost remains substantially *higher* than Scenario 1's
(or 1B's) under all three gas cases — now $121-127/MWh vs.
$89.30-89.40/MWh, a wider gap than previously reported, not a
narrower one — driven by both the direct-cost gap (now real, not
narrowed) and the climate-cost gap (unchanged) working in the same
direction, rather than partially offsetting as the pre-correction
figures suggested. Scenario 1 and Scenario 1B remain essentially tied
on a total-societal basis (within $0.10/MWh), consistent with N.5's own
finding — unaffected by the Scenario 2 correction, since neither uses
CCGT capex at all. **Scenario 1's own total-societal advantage over
Scenario 2 is real, now fully verified on all sides including this
correction, and larger than this project's own most recent prior
estimate, not smaller.** The underlying reason has not changed from
this project's own original characterization: Scenario 2 sustains
substantial gas generation throughout the full 20-year window by
statutory design, while Scenario 1 (and, in practice, 1B too)
approaches true zero by 2045 — both the direct-cost and climate-cost
gaps between Scenario 1/1B and Scenario 2 are real and now consistently
point the same direction.

**Total societal SLCOE, with RGGI folded into the direct-cost side**
(new, this session — closes the open item tracked in Appendix P.4/entry
#43, where RGGI had been built into each scenario's own direct SLCOE
but never carried through into a distinct total-societal-with-RGGI
figure). RGGI is a real, currently-billed carbon-market cost, additive
to — not a substitute for — the Social Cost of GHG externality
estimate above, which represents the broader, un-priced societal value
of the same emissions rather than what a generator is actually charged
per ton; the two are shown combined here for a genuinely complete
"most costs accounted for" figure, not because either alone was
insufficient on its own terms:

| Scenario | Direct SLCOE (w/ RGGI) | + Social Cost of GHG + Health Impacts | Total societal (w/ RGGI) |
|---|---|---|---|
| 1 | $46.22/MWh | +$46.85 | **$93.07/MWh** |
| 1B | $45.94/MWh | +$47.26 | **$93.20/MWh** |
| 2 (Deloitte gas) | $56.70/MWh | +$77.56 | **$134.26/MWh** |
| 2 (EIA gas) | $51.48/MWh | +$77.56 | **$129.04/MWh** |
| 2 (Hughes gas) | $57.15/MWh | +$77.56 | **$134.71/MWh** |

The ordering and the size of the gap between Scenario 1/1B and Scenario
2 are essentially unchanged by including RGGI — RGGI adds roughly
$3.8-4.5/MWh to every scenario's own total (proportional to each
scenario's own gas volume, largest in absolute terms for Scenario 2)
without altering which pathway costs more or by roughly how much.

### D.4 Disclosed Gaps and Limitations

- **Scenario 2's own approximate CO2/CH4/N2O tons in D.3's own table**
  (back-calculated from the SC-carbon/health dollar figures, not
  independently re-extracted from the raw hourly arrays to the same
  precision as Scenario 1's own row): a minor, disclosed precision gap,
  not a gap in the dollar figures themselves, which are the genuinely
  verified values.
- **Plant-specific NOx classification confidence varies** (D.2): direct
  evidence exists for Greensville County and Possum Point/Bear Garden
  (the latter two via a specifically-named 2015 retrofit program);
  Brunswick County, Warren County, and Potomac Energy Center rest on
  strong circumstantial inference (same era, vendor, or program) rather
  than plant-specific confirmation; Tenaska Virginia rests on weak,
  industry-norm inference only. The uncontrolled classification for the
  older peaker fleet (Chesterfield, Doswell, Ladysmith, Marsh Run,
  Louisa, Wolf Hills) is an absence-of-evidence default, not a confirmed
  finding — a genuine retrofit at any of these plants would lower the
  Health Impacts figure further.

- **"Density/frequency sensitivity" for Health Impacts**: referenced in
  this section's original brief summary, but the specific adjustment
  formula was not recoverable from any source located this session,
  despite a direct literature search. The general concept (benefit-per-
  ton varies meaningfully by source location and population density) is
  well-established in the literature (e.g. the EGU-specific vs.
  area-source distinction already embedded in C033's own figures), but
  this analysis uses EPA's flat, national EGU rates rather than a
  location-adjusted version. A genuine limitation, not a judgment call.
- **Upstream CH4 leakage (2.3%)** is carried forward from
  `whitepaper_draft.md` without independent re-verification this
  session.
- **NOx existing/new blending** uses MW capacity share as a proxy for
  energy-dispatch share, not a true hourly-resolved attribution (the LP's
  gas dispatch variable does not itself distinguish which physical unit
  serves a given hour).
- **N2O** is now fully sourced (this session, resolving a prior gap) —
  no remaining omission on this point.
- Tier 3 remains deliberately unmonetized; the qualitative findings in
  D.1 should not be read as implying any specific dollar magnitude.

---
