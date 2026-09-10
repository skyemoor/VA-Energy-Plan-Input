# Dominion Energy Virginia — VPP/DER Pilot Program Research

Working reference file, compiled 2026-08-23, separating out all Dominion-
specific pilot-program research from Scenario3_Scope_and_Gaps.md's own
§5.2.2 for easier standalone reference. Every figure here traces to a
specific, cited source — nothing is estimated or assumed unless
explicitly marked as such.

## 1. Legal framework — the Community Energy Act

**HB 2346 / SB 1100, enacted May 2, 2025, codified at Va. Code
§56-585.1:16.** Requires Dominion (a "Phase II Utility") to:

- Petition the SCC by **December 1, 2025** for approval of a VPP pilot
  program, up to **450 MW**, sited across multiple regions of Virginia.
  **Done** — filed as Docket **PUR-2025-00211**.
- Include at least **15 MW of residential battery storage incentives**
  within that pilot.
- Petition the SCC by **November 15, 2026** for a program tariff (or
  variations of one) allowing residential and C&I customers to enroll,
  **either directly or through an aggregator**. Dominion chose to file
  this simultaneously with the pilot petition (both are in the same
  December 2025 filing) rather than waiting for the November 2026
  deadline, to maximize testing time before the pilot's own July 1, 2028
  conclusion.
- The statute explicitly directs the SCC, post-pilot, to weigh "lessons
  learned" against **FERC Order 2222** implementation directly — the
  state and federal frameworks are designed to work together, not as
  competing or redundant pathways.

**Related, non-Dominion Virginia VPP legislation** (noted for
completeness, not pursued further since this project's own scope is
Dominion-specific): HB 1467 (Appalachian Power, same mandatory/SCC-
regulated structure) and HB 562 (electric cooperatives, permissive/
self-implementing, no SCC approval required, effective July 1, 2026).

**Prior, separate, now-closed program — HB 2789 (2019), the "Income and
Age Qualifying Solar Program"**: a three-year pilot (SCC rules 2021,
installations began Oct. 2021, concluded/closed to new applications
December 2024) offering **free weatherization services and solar panel
installation** (no cost to the customer) to income- and age-qualifying
Virginians, with a 25-year panel maintenance/repair warranty included.
**This program was NOT structured around D-REC remuneration or any
ongoing payment stream** — the incentive was the free capital
installation itself. (A qualifying customer's resulting solar system
would presumably still be eligible to sell D-RECs on Virginia's general
market like any other solar owner, since nothing in the program design
excludes this — but that was not the program's own built-in mechanism.)
Directly relevant here because the VPP Pilot's own Residential IAQ
Battery Storage Purchase Pilot specifically targets customers who already
went through this prior solar program — confirming Dominion's pattern of
free-upfront-hardware incentives (not ongoing payments) specifically for
its income/age-qualifying tier, distinct from its general-population
pay-for-performance approach.

## 2. Dominion's own VPP Pilot filing (PUR-2025-00211) — full program table

**CORRECTED 2026-08-27**: the numbering below was originally taken from
this filing's own informal Table 1 summary ordering (Section 4.3.3),
which does NOT match the filing's own official, numbered tariff
language (Appendix C, "III. Program Eligibility and Incentives") —
verified directly by fetching the source PDF. Appendix C is the
authoritative numbering; corrected below. Two real errors found: (1)
BYOD is officially **#5**, not #11; (2) "Residential Managed EV
Charging" is a single, official **#9** covering both TOU and non-TOU
variants together, not two separate #8/#9 entries — the real #8 is a
different, unrelated program (Residential IAQ Battery Storage Pilot,
Demand Response).

Source: Company Exhibit, Witness CSY (Courtney S. Young), Schedule 1
("Virtual Power Plant Pilot"), filed with the December 2025 VPP Pilot
petition, Docket PUR-2025-00211. Direct PDF:
https://cdn-dominionenergy-prd-001.azureedge.net/-/media/content/save-energy/global/pdfs/virginia/vpp-pilot-young-testimoy-schedule-1.pdf
All figures below are as stated in that filing's own Appendix C.

| # | Program | Status | Incentive | Eligibility | Cost recovery |
|---|---|---|---|---|---|
| 1 | Residential Smart Thermostat Reward | Existing (DSM-XIII) | $25 one-time + $25/year | Any residential rate schedule | DSM Rider C1A |
| 2 | Residential EV Charger Rewards (Peak Shaving) | Existing (DSM-VIII) | $40/year | Residential, existing L2 charger | DSM Rider C1A |
| 3 | Residential Peak Time Rebate | Existing (DSM-XII) | Up to $28/year (10 events) | Residential, AMI meter, not otherwise DR-enrolled | DSM Rider C1A |
| 4 | Non-Residential Curtailment | Existing (DSM-XIII) | ~$26,250/year average | Non-residential, DSM Rider payers, not on Schedule 10 | DSM Rider C1A |
| 5 | **BYOD (Bring Your Own Device) Aggregator Access Pilot** | New (DSM-XIV) | **Pay-for-performance, "varies across residential, commercial, industrial, and vendor-managed segments" — exact rate NOT disclosed in this filing** | Res./C&I/industrial via an approved aggregator, OR up to 1,000 customers directly with Dominion as pilot aggregator | DSM Rider C1A |
| 6 | **Residential Battery Storage Pilot (DR)** | New (DSM-XIV) | **$1,000 one-time enrollment + $294/year** | Residential, existing qualifying battery, **standalone OR paired with solar**; NEM customers eligible but no duplicate export-energy incentive | DSM Rider C1A |
| 7 | Residential IAQ Battery Storage Purchase Pilot | New (DSM-XIV) | Free 13.5 kWh Tesla Powerwall 3 (~$20,000 value) | Income ≤80% AMI (or 60% state median) or age 60+ with income ≤120% state median; targets prior HB 2789 solar-pilot participants | DSM Rider C1A |
| 8 | Residential IAQ Battery Storage Pilot (DR, companion to #7) | New (DSM-XIV) | ~$183/year average | Same IAQ eligibility as #7; must participate in DR/grid events | DSM Rider C1A |
| 9 | **Residential Managed Charging Pilot for TOU rate and non-TOU rate customers** | New (DSM-XIV) | Non-TOU: $40 enrollment + $10/month. TOU: $20 enrollment + $5/month | Residential, TOU or non-TOU rate schedule, L1/L2 charger, telematics-compatible | DSM Rider C1A |
| 10 | Non-Residential HVAC (Small/Medium Business) | New (DSM-XIV) | $75 one-time + $40/year | Non-residential, ≤400 kW demand | DSM Rider C1A |
| — | Electric School Bus Program | Existing | N/A (V2G capability, not direct payment) | VA public school districts | Base rates |
| — | Non-Wires Alternative BESS Pilot | Existing (GT Plan) | N/A (utility-owned, front-of-meter) | Not applicable — utility asset | Rider DIST |

## 3. The BYOD program — why it matters most for this project

- **Device-agnostic**: thermostats, batteries, EVs, behavioral measures,
  and more are eligible. **Fossil-fuel-based distributed generation is
  explicitly excluded** — the filing does not explicitly list solar as
  eligible or ineligible, but the fossil-fuel-specific carve-out implies
  non-fossil distributed generation (solar) is not excluded by the same
  logic.
- **This is Dominion's own single largest projected VPP component**:
  the filing's own Figure 7 (tentative capacity growth to 2030) shows
  **200 MW** of the ~466 MW total pathway coming from BYOD Aggregator
  Access — nearly half of the entire program, and larger than every
  other individual program combined except the Residential Battery
  Storage Pilot (88 MW). This is a real, Dominion-sourced confirmation
  that the third-party-aggregator pathway (where Voltus and similar
  platforms would plug in) is expected to carry the bulk of total VPP
  capacity.
- **The real, disclosed gap**: the actual $/kW or $/MWh BYOD rate is not
  published in this filing. The statutory tariff deadline is November
  15, 2026 — this December 2025 filing pre-dates final rate-setting.
  Whether a rate schedule has since been published has not yet been
  checked.

## 4. General third-party aggregator context (Voltus and peers) — for bounding, not substituting

- **Voltus**: pure-play DER aggregation platform, owns no generation.
  Revenue-shares wholesale capacity/energy/ancillary-services payments
  with enrolled customers ("Voltus earns money for the capacity or
  energy provided... and shares it with you and your customers").
  Reported 2025 PJM-wide: $240M paid to customers across 8.1 GW of
  aggregated flexible capacity. **Exact revenue-share percentage not
  publicly disclosed** (varies by OEM/hardware-partner contract — B2B2C
  model with partners like Resideo/Honeywell).
- **Academic literature on aggregator business models** documents two
  common structures: (1) aggregator retains a flat ~20% of the
  customer's own total value created, or (2) aggregator passes through
  100% of value but charges a separate flat platform fee instead.
- **Useful only as a bounding heuristic** if Dominion's own BYOD rate
  remains unpublished — not a substitute for the real, Dominion-specific
  figure once available.

## 5. Real, direct-quoted confirmation of the NEM/wholesale double-compensation rule

Dominion's own Residential Battery Storage Pilot eligibility language:
**"net metering customers may participate but will not receive duplicate
incentives for exported energy."** This is Dominion's own tariff
directly enforcing, at the program level, the same FERC-level NEM-
vs-wholesale double-compensation prohibition already researched this
session from PJM/FERC compliance orders (Internal research, same
session) — confirming it is not just a PJM/FERC abstraction but an
actual, applied Dominion program rule.

## 6. Open question — reserve state-of-charge / backup-power carve-out

**Direct user question (2026-08-23)**: most people who buy solar+battery
do so specifically to have backup power during grid outages, meaning
they would likely only want to discharge down to some preset SoC value
during a grid event, reserving the remainder for their own outage
protection. Does Dominion's Residential Battery Storage Pilot have any
such provision?

**Status: not found, after two direct searches — genuinely unresolved,
not assumed either way.** The publicly available VPP Pilot filing
(Company Exhibit, Witness CSY, Schedule 1) does not specify a minimum
reserve SoC, a discharge floor, or any backup-power carve-out for the
Residential Battery Storage Pilot. This level of operational detail may
exist in the underlying DSM-XIV filing itself (referenced by, but not
reproduced within, the VPP Pilot exhibit) or in program-specific terms
and conditions not yet published or located.

**A relevant, though non-Dominion, precedent found earlier this
session**: Pacific Power's Oregon battery-incentive program explicitly
states the utility "will not drain batteries below 10% capacity" — a
real, operative example of exactly the kind of floor the user is asking
about, in a comparable (though different-utility, different-state)
context. Useful as a plausibility anchor for what such a provision might
look like if Dominion's own program has one, not as evidence Dominion's
own program does.

**Why this matters, stated directly rather than left implicit**: if
Dominion's program has no such floor, this is a real, material barrier
to participation for exactly the customer segment most likely to invest
in solar+battery in the first place (backup-power-motivated buyers) —
and could mean the program's own advertised/modeled available discharge
capacity overstates what customers would actually be willing to commit
in practice. If Scenario 3's own DER-comp modeling assumes full,
unreserved discharge availability from residential batteries, that
assumption should be flagged as unverified against Dominion's own actual
program terms, not treated as confirmed.

**Not yet done**: locating and reviewing the actual DSM-XIV filing
directly (rather than the VPP Pilot exhibit's own summary of it), which
may contain this operational detail.

## 7. Provenance note

All figures in this file are sourced directly from: (a) Dominion's own
December 2025 VPP Pilot filing exhibit (Witness CSY, Schedule 1),
fetched directly from Dominion's own CDN-hosted PDF; (b) direct web
search results for HB 2789/Income and Age Qualifying Solar Program
reporting (Canary Media, Dominion's own program page); (c) direct web
search for Order 841/Pacific Power precedent (already documented
separately in this session's own Order 2222/841 research). Nothing here
is estimated unless explicitly marked as such (see §4).
