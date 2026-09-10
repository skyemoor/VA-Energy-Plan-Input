# Virginia Clean Energy Compliance Pathways: Technical Summary

*A cost analysis prepared for Virginia Department of Energy staff, utility
modelers, and other technical stakeholders — working draft*

---

## 1. Purpose and scope

This analysis independently models the cost of Dominion Energy Virginia's
compliance with the Virginia Clean Economy Act (Va. Code §56-1706.1) and the
Renewable Portfolio Standard (§56-585.5), under demand levels roughly double
what either statute assumed at enactment in 2020. It compares three
compliance pathways on both a direct-financial and a full-societal-cost
basis, using an hourly linear-programming dispatch model built and
independently verified for this project.

This document summarizes methodology and results at a level intended for
technical review. Full model documentation, every sourced assumption, and
the complete record of corrections made during development live in the
accompanying appendices and internal debugging log.

## 2. Methodology overview

- **Model type**: hourly linear program, solving jointly for build-out and
  dispatch (Scenarios 1/1B) or dispatch alone against a statutorily fixed
  build (Scenario 2), across a single representative weather year
  (2016-17).
- **Demand basis**: Virginia-only DOM LSE sales, Appendix 2B-2 vintage,
  hourly-shaped using a data-center-driven flattening methodology (see
  Appendix O) to reflect the near-constant 24x7x365 load profile of the
  data-center share of load, which the project's only sourced hourly shape
  (a 2023 IRP vintage file) would otherwise understate for later years.
- **Time horizon**: 20 years, 2026-2045. Four checkpoint years (2030, 2035,
  2040, 2045) are solved as full build-and-dispatch optimizations; the
  remaining 16 years are solved as dispatch-only problems against builds
  interpolated between checkpoints, each independently constrained to its
  own year-exact statutory RPS share.
- **Discounting**: 4.5% real WACC, 2026 base year, applied consistently
  throughout — chosen specifically so general inflation does not need
  separate treatment, provided every cost stream stays on the same
  constant-dollar basis (verified this project's own inputs do).
- **Reserve margin**: PJM's 17.7% Installed Reserve Margin, applied against
  each year's own peak net-demand hour. For Scenarios 1/1B, enforced as a
  hard LP constraint on the optimizer's own build decision. Scenario 2 has
  no build variables (fully statutory), so reserve margin is instead
  checked against the fixed build — confirmed to pass at all four
  checkpoints with substantial margin (790-10,864 MW above target),
  requiring no adjustment.
- **Terminal value**: assets with useful lives extending past the 2045
  window boundary (25-year solar/storage, 30-year gas turbines) receive a
  credit for their own unrecovered capex fraction as of 2045, discounted
  back to 2026 — prevents the model from penalizing late-window investment
  in genuinely long-lived assets.

## 3. Scenario definitions

- **Scenario 1**: full VCEA/RPS compliance via solar and battery storage
  only (short-duration sodium-ion and long-duration iron-air), no new gas
  generation, reaching true 100% clean generation by 2045.
- **Scenario 1B**: identical to Scenario 1 through 2044 (both share the
  same year-exact RPS target every year); relaxes the 2045 target to allow
  up to 5% gas generation, per HB 895/SB 448.
- **Scenario 2**: builds only the minimum statutory solar and battery
  capacity named directly in the RPS text (§56-585.5(D)(2)/(E)(2)/(E)(4)):
  16,100 MW solar, 16 GW short-duration storage, 4 GW long-duration
  storage. Remaining generation need served by the existing gas fleet plus
  new-build combined-cycle gas turbines sized to cover each year's own
  worst-hour demand.

## 4. Results

### 4.1 Direct financial SLCOE (societal levelized cost of energy)

*(A note on Scenario 2's own figures below: an earlier draft of this table briefly showed lower
values for Scenario 2, close to or below Scenario 1's own. That was a real, confirmed accounting
error — a stale CCGT capex constant, 1.69x below this project's own correct, cross-validated
figure — found and fixed after this document was first drafted. See §5's own note on this.)*

| Scenario | SLCOE, no RGGI | SLCOE, with RGGI |
|---|---|---|
| 1 | $42.45/MWh | $46.22/MWh |
| 1B | $42.14/MWh | $45.94/MWh |
| 2 (Deloitte gas price case) | $48.99/MWh | $56.70/MWh |
| 2 (EIA gas price case) | $43.77/MWh | $51.48/MWh |
| 2 (Wood Mackenzie/Hughes gas price case) | $49.43/MWh | $57.15/MWh |

RGGI compliance cost uses RGGI's own published Cost Containment Reserve
trigger-price schedule ($18.22/ton 2026, escalating 7%/year from $19.50 in
2027) as a conservative reference point — RGGI's own actual market-clearing
price has run above this schedule since Virginia's July 2026 re-entry (most
recent auction: $35.00/ton), so these figures should be read as a plausible
lower bound, not a prediction.

### 4.2 Social cost figures (externality estimates, not billed costs)

| Scenario | Social Cost of Carbon (CO2 only, statutory) | Social Cost of GHG (CO2+CH4+N2O) | Health Impacts (PM2.5+SO2+NOx) |
|---|---|---|---|
| 1 | $39.84/MWh | $43.66/MWh | $3.19/MWh |
| 1B | $40.19/MWh | $44.05/MWh | $3.21/MWh |
| 2 | $66.16/MWh | $72.84/MWh | $4.72/MWh |

Social Cost of Carbon is reported separately from the broader Social Cost of
GHG per Va. Code §56-598(2)(d)/§56-585.1(A)(6), which directs the SCC to
consider a Virginia-specific rate; absent a Commission-set figure, this
analysis uses the EPA's own 2023 rate schedule as the best available proxy,
re-based from its native 2020$ to this project's 2026$ using a BLS-sourced
CPI deflator. Health Impacts uses EPA's own BenMAP benefit-per-ton figures,
similarly re-based from 2016$. Both figures here are unaffected by the CCGT
capex correction noted above or by RGGI, since they depend only on gas
dispatch volume, not on capex or on the RGGI carbon price.

### 4.3 Total societal cost (direct SLCOE + Social Cost of GHG + Health Impacts)

Shown both without and with RGGI folded into the direct-cost side — RGGI is
a real, currently-billed carbon-market cost, additive to (not a substitute
for) the Social Cost of GHG externality estimate, which represents the
broader, un-priced societal value of the same emissions rather than what a
generator is actually charged per ton:

| Scenario | Total societal, no RGGI | Total societal, with RGGI |
|---|---|---|
| 1 | $89.30/MWh | $93.07/MWh |
| 1B | $89.40/MWh | $93.20/MWh |
| 2 (Deloitte) | $126.55/MWh | $134.26/MWh |
| 2 (EIA) | $121.33/MWh | $129.04/MWh |
| 2 (Hughes) | $126.99/MWh | $134.71/MWh |

Tier 3 (air toxics — formaldehyde, benzene) is tracked and disclosed
qualitatively throughout the appendices but deliberately not monetized: no
sufficiently robust, defensible dollar-per-ton figure exists for these
effects at this project's level of sourcing.

## 5. Key methodological findings worth flagging to technical reviewers

- **Scenario 1B's own 5% gas allowance is largely moot in practice.** By
  2045, the physical gas fleet itself — sized down by the VCEA's own
  Schedule B retirement schedule — cannot generate more than about 1.6-4.3%
  of demand regardless of what the statute would permit. The binding
  constraint at 2045 is physical fleet capacity, not the RPS percentage.
- **Scenario 2's direct cost is now clearly above Scenario 1's under all
  three gas cases**, itself a correction to an earlier, briefly-reported
  finding in this same document that Scenario 2's direct cost sat close to
  or below Scenario 1's — that finding traced to a real, confirmed
  accounting error (§5's own next bullet), not a genuine result, and does
  not hold once corrected. The gap between the two scenarios' total
  societal cost is driven by both the direct-cost figure and the
  climate-cost figure now, not the climate figure carrying it alone.
- **A real CCGT capex accounting error was found and fixed this
  development cycle**, worth disclosing directly rather than only in the
  debugging log: two separate CCGT capital-cost definitions had coexisted
  in this project's own code — a stale $1,775/kW figure and a correct,
  later-built, cross-validated $3,000/kW figure (Wood Mackenzie, EPRI, and
  GridLab sourcing, independently corroborated) — and a downstream cost
  script was found to be silently using the stale one. Since CCGT capex is
  Scenario 2's single largest cost component, this was a material
  correction (1.69x on that line item), not a rounding fix, and every
  Scenario 2 figure in this document reflects the corrected value. In
  response, every sourced parameter this project uses was consolidated
  into a single, centralized module (`assumptions.py`) specifically to
  make this class of bug — two coexisting definitions for the same
  parameter — structurally harder to reintroduce going forward.
- **Simultaneous charge/discharge degeneracy**, a known, named problem in
  the battery-optimization literature ("SCD" / battery complementarity
  constraint), was found and resolved across multiple points in this
  model's development, using a combination of hard physical constraints
  and, where confirmed via direct KKT/reduced-cost verification to be
  genuine LP degeneracy (not a real cost preference), disclosed cycling-
  cost penalties. Full record in the internal debugging log.
- **Every reported figure in this document has been independently
  re-verified this development cycle** against corrected demand data, a
  storage-loss RPS-constraint splice, and (for Scenario 1/1B) an explicit
  reserve-margin constraint — none of which were present in this project's
  earlier draft passes. Figures from any version of this analysis prior to
  the current working session should not be treated as current.

## 6. Disclosed limitations and open items

- Scenario 3 (locally-sited solar with FERC 2222 market participation,
  agrivoltaics, retail rate design) is scoped but not yet built out.
- Land acreage requirements (battery storage, new gas capacity) are not
  yet fully sourced.
- Tier 3 air-toxics effects remain qualitative-only by design; see Appendix
  D for the full, disclosed reasoning.
- The existing/new-fleet split used for Scenario 2's NOx-blend calculation
  interpolates between four sourced checkpoints (Appendix C.10); the
  intermediate years' own split is not independently verified to the same
  precision as the checkpoints themselves.

## 7. Where to find more

- **Full methodology, all sourced assumptions, every rate and factor
  used**: Reorganized Appendices Draft (Appendices A-P).
- **Complete record of every correction, verification, and dead end
  encountered during model development**, including the reasoning behind
  each: Internal Debugging Log.
- **Reference literature consulted**: Appendix M.
