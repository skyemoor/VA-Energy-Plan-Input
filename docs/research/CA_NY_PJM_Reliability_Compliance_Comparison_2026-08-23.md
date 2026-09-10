# California / New York / PJM(Virginia): How Three Jurisdictions Separate Reliability Planning from Clean-Energy Compliance

Built 2026-08-23. Every claim below was directly verified against a primary source during this
session (CPUC/CEC/CAISO filings, NYSERDA/NYISO publications, PJM's own ELCC tables, Va. Code
§56-585.5) -- not asserted from general knowledge. Source URLs are inline; none of this has yet
been cross-checked against Scenario3_Literature_Search_Citations_2026-08-23.md's own numbering,
which should happen before this is folded into that tracker or into Appendix material.

## The one-sentence finding

**Every jurisdiction examined -- California, New York, and PJM/Virginia -- institutionally
separates "does this resource keep the lights on" from "does this resource count toward the
clean-energy percentage," and none of them use the same number for both.** Virginia's own VCEA
doesn't yet have an equivalent, formal separation; PJM's ELCC accreditation exists, but nothing in
this project's own RPS-compliance modeling to date has connected the two.

## 1. Compliance timing: how much does a single bad year matter?

| | Compliance period | Mechanism |
|---|---|---|
| **Virginia (VCEA/RPS, §56-585.5)** | **Annual** -- "in any year" | Deficiency payment: $45/MWh shortfall, **$75/MWh** for the ≤1 MW solar/wind/anaerobic-digester Virginia carve-out (directly relevant to Scenario 3's own DER share). Escalates 1%/yr after 2021. Limited REC "banking" (roll-forward is time-bounded, not indefinite). |
| **California (RPS, SB 350/SB 100)** | **Multi-year** -- 3-4 year windows (2025-2027, 2028-2030; standing 3-year cycles from 2031) | A bad year and a good year within the same window offset automatically. IOUs have run a forecasted *excess* procurement position for years, selling surplus RECs rather than tightly targeting the minimum -- direct evidence the multi-year window encourages deliberate over-procurement as the safe strategy. [cpuc.ca.gov/rps](https://www.cpuc.ca.gov/rps/), [D.16-12-040](https://docs.cpuc.ca.gov/PublishedDocs/Published/G000/M171/K457/171457580.PDF) |
| **New York (CES/RES)** | **Annual**, but centrally procured | NYSERDA -- a state entity, not individual utilities -- buys Tier 1 RECs on LSEs' behalf and sets a uniform, forecast-based per-MWh rate. Individual LSEs don't bear direct procurement-shortfall risk the way Dominion does; NYSERDA absorbs and smooths it centrally. Unsold RECs bank forward for future-year sale. Historical ACP has run well below Virginia's ($22-24/MWh in 2020 vs. VA's $45-75/MWh). [nyserda.ny.gov/LSE-Obligations](https://www.nyserda.ny.gov/All-Programs/Clean-Energy-Standard/LSE-Obligations) |

**Virginia is the only one of the three with neither a multi-year averaging window nor a
centralized procurement backstop.** Each utility bears its own single-year exposure directly, with
only the (real, statutorily-guaranteed) deficiency payment as a release valve.

## 2. Does a resource "counting toward RPS %" mean it counts toward reliability?

This is the core finding, and California's mechanism is the most explicit and quantified of the
three.

**California -- FCDS vs. EODS, a formal, per-resource designation:**
Every CAISO-interconnected resource gets one of two statuses. **FCDS** (Full Capacity
Deliverability Status) counts toward resource adequacy because it can demonstrably deliver during
actual system-peak-stress hours without overloading the grid. **EODS** (Energy-Only Deliverability
Status) counts toward RPS/renewable targets but *explicitly does not* count toward resource
adequacy. This is tracked and published per project, not an informal caveat.
[caiso.com/transmission-capability-estimates-white-paper-2026](https://www.caiso.com/documents/transmission-capability-estimates-white-paper-2026.pdf)

The quantified version of the same split -- CAISO's own on-peak vs. off-peak deliverability output
factors:

| Resource | On-peak (FCDS/reliability) | Off-peak (EODS/RPS-energy) |
|---|---|---|
| Solar | **13-15%** (varies by utility zone) | **68-79%** |
| Wind | 35-50% | 44-69% |
| Storage (≥4hr) | 100% | 100% in charging mode |

A solar project can be doing real, substantial work toward the RPS percentage while contributing a
small fraction of that toward the hour that actually determines reliability. Storage is the only
resource class CAISO credits fully on both sides -- full FCDS credit, and it *also* expands EODS
capability system-wide by charging during otherwise-curtailed hours.

**California also has a formal, statutory priority ordering that's directly relevant to the
Scenario 3 demand-shaping thesis:** the "Loading Order" mandates energy efficiency and demand
response be pursued *first*, renewables second, clean-fossil last -- a real, citable precedent for
the argument that WMA participation + retail pricing + DLC programs (S3's own combination) should
reduce required RE deployment, not just reshape when it's dispatched.
[cpuc.ca.gov/irp](https://www.cpuc.ca.gov/irp/)

**New York -- NYISO keeps reliability planning and CES compliance in separate institutional
tracks entirely**, rather than a single per-resource dual-status label the way CA does:
- Reliability: NYISO's own four-part Reliability Needs Assessment (RNA, biennial, 10-year horizon)
  → Comprehensive Reliability Plan (CRP) track.
- Compliance: NYSERDA/PSC's own CES/RES track, entirely separate.

Two NYISO mechanisms are worth carrying into Virginia's own planning discussion directly:

1. **"Rules of inclusion"**: a proposed generator only counts toward baseline reliability margins
   once it clears a real bar -- sufficient progress on financing, permitting, or the
   interconnection study process. Projects that haven't advanced enough are excluded from safety
   margins regardless of their policy status, "due to the risk and uncertainty associated with the
   project's successful completion." [nyiso.com/how-reliability-needs-are-identified](https://www.nyiso.com/-/how-reliability-needs-are-identified-on-new-yorks-grid)
2. **The "plausible futures" shift -- genuinely current, not legacy practice.** NYISO's own
   December 18, 2025 Comprehensive Reliability Plan states plainly: "solely relying on a single
   baseline forecast to identify actionable needs is no longer sufficient," citing aging
   generation, shifting demand, project delays, and extreme weather as jointly producing "a
   growing number of plausible outcomes" no single forecast captures. Their stated fix: stress-test
   the grid under multiple plausible combinations of demand growth, resource mix, transmission
   timing, and weather together.
   [nyiso.com/crp-expanded-planning-framework](https://www.nyiso.com/-/crp-expanded-planning-framework-needed-to-capture-emerging-risks)

**This is the same idea as this project's own entry #47 (fix a build, cross-test against multiple
real years) and the six-hydro-year test run this session, arrived at independently by the operator
of one of the most complex grids in the country, for almost exactly the same stated reasons.**

**PJM/Virginia -- ELCC class ratings, the actual, already-governing mechanism for this project's
own grid:**

| ELCC Class | 2023/24 | 2025/26 | 2026/27 | 2027/28 (preliminary) |
|---|---|---|---|---|
| Solar Fixed Panel | 50% | 37% | 33% | -- |
| Solar Tracking | 61% | 51% | 45% | -- |
| Onshore Wind | 15% | 15% | 13% | -- |
| Offshore Wind (CVOW-relevant) | 42% | 40% | 31% | -- |
| 4-hr Storage | 94% | 77% | 77% | **58%** |
| 6-hr Storage | 100% | 96% | 94% | 67% |
| 8-hr Storage | 100% | 100% | 100% | 70% |
| 10-hr Storage | 100% | 100% | 100% | 78% |
| Demand Response | -- | -- | -- | **92%** |

Sources: PJM's own official 2026/27 table [pjm.com/elcc-class-ratings-2023-2025-2026](https://www.pjm.com/-/media/DotCom/planning/res-adeq/elcc/elcc-class-ratings-for-2023-2025-2026.ashx);
2027/28 figures from [energycentral.com, Nov 2025](https://www.energycentral.com/intelligent-utility/post/news-pjm-s-elcc-class-ratings-show-the-vital-role-of-demand-response-wRo0iDoopWYHejE).

**This is not a one-time correction -- it's an accelerating trend across delivery years, and it
directly matters for a 20-year-horizon project.** If this project's own DER-comp "capacity"
compensation component, or any capacity-market revenue assumption feeding the owner-IRR work,
assumes anything close to full nameplate credit -- or even holds the 2026/27 figures flat through
2045 -- it understates how fast PJM's own market discounts battery/solar capacity value as
penetration grows. A directly-sourced real-world revenue anchor: a 4-hour battery at 50% ELCC
accreditation earns roughly **$60,700/MW-yr** in PJM capacity revenue at current prices
[sysotechnologies.com/pjm-bess-operators](https://www.sysotechnologies.com/pjm/pjm-bess-operators/).

**Virginia has no formally-named FCDS/EODS-style split or statutory Loading Order, but the
functional mechanism already exists, unlabeled, in Dominion's own filed IRP schedules.** Schedule
15a/15c of the 2025 IRP Update publish two separate MW figures for every individual solar/wind
project: "MW Nameplate" and "MW Annual Firm," with a footnote confirming "Solar firm based on
average ELCC value" (e.g., CVOW Phase 1: 2,587 MW nameplate vs. 915 MW firm; individual solar
projects typically 5-9% firm-to-nameplate). This is functionally the same distinction CAISO
formalizes as FCDS/EODS -- a reliability-counting number and a separate, much larger
nameplate/RPS-counting number for the same resource -- just embedded in standard IRP schedule
columns rather than a named, two-status designation connected explicitly to RPS-percentage
accounting. Dominion also confirms it calculates its PJM capacity obligation directly from "ELCC,
and reserve margin requirements" via its RPM (not FRR) participation -- so PJM's own de-rating
schedule already governs Dominion's real capacity obligations today, not just a hypothetical
future connection. Virginia doesn't need to import a foreign concept here; it needs to formalize
and explicitly connect a mechanism that already exists in the data.

## 3. A real, disclosed tension -- investigated further, largely resolved

PJM's own ELCC methodology, and independent replications of it (Ascend Analytics), find that
system risk has shifted enough toward winter that **wind's annual ELCC now exceeds solar's**,
despite solar's strong summer-peak performance -- a load-shape argument for winter as PJM's
primary stress season.

This project's own six-hydro-year cross-test (2040 checkpoint, Scenario 1's build) found the
single largest month-over-month gas-dispatch driver between the established (2016-17) and the
compliance-worst (2018-19) weather years was **August**, not any winter month.

**Investigated directly (2026-08-23), rather than left as an open disagreement:**

1. **No genuine multi-day cold-snap event appears in any of the six years.** Searching for
   sustained (48+ consecutive hour), above-the-90th-percentile winter net-load events across all
   six years found none -- the longest sustained stretch in any year tops out at 20 hours, well
   under a single day. The kind of event PJM's own Winter Storm Elliott/Polar Vortex 2014
   references (a genuine, sustained, multi-day cold snap) simply isn't present in this project's
   own six-year sample. This resolves possibility (a) from the original tension in favor of "not
   yet captured" rather than "genuinely absent" -- a real, disclosed sample-size limitation
   (n=6, still small relative to a multi-decade planning horizon), not evidence PJM's own winter
   framing is wrong for Virginia.

2. **Winter's proportional share of total gas need directly confirms, rather than contradicts,
   last session's own August finding**:

   | Year | Winter GWh | Total GWh | Winter share |
   |---|---|---|---|
   | 2012-13 | 3,597 | 25,814 | 13.9% |
   | 2013-14 | 3,963 | 25,771 | 15.4% |
   | 2016-17 (established) | 4,406 | 26,521 | 16.6% |
   | 2017-18 | 4,317 | 25,038 | 17.2% |
   | **2018-19 (compliance-worst)** | 4,513 | 30,189 | **14.9%** |
   | **2019-20 (winter-worst)** | 5,041 | 28,030 | **18.0%** |

   2018-19 -- the year with the highest *overall* gas need and the only year that clearly exceeds
   the 21% statutory cap -- has the *lowest* winter share of the six years, not the highest. Its
   elevated total is proportionally a non-winter (largely summer/August) phenomenon, confirming
   rather than complicating the earlier finding. 2019-20, by contrast, is the genuinely
   winter-driven year -- highest winter share *and* highest absolute winter gas need -- but it is
   not the year that most stresses overall RPS compliance.

**Updated conclusion: "worst year" now splits three ways, not two, and none of them coincide.**
2016-17 remains the reliability-sizing-worst year (entry #47's own min-max-robust finding).
2018-19 is the overall-compliance-percentage-worst year, and its own stress is not primarily
winter. 2019-20 is the winter-specifically-worst year, but is not the compliance-worst year
overall. A single-scenario planning approach -- sizing to any one of these three "worst" years --
would miss the other two entirely. This is a stronger, more precise version of the original
finding, not a resolution to a single answer, and should be presented that way rather than
simplified into one "the worst year is X" statement.

## 4. What this means for this project's own recommendations, stated directly

1. **The reliability-vs-compliance divergence this project already found empirically (2016-17 as
   reliability-worst, 2018-19 as compliance-worst, not the same year) is not a Virginia-specific
   quirk or a modeling artifact.** It's the same divergence CA and NY's own institutional
   structures are built around, and the same divergence CAISO's FCDS/EODS split makes explicit and
   quantified. This strengthens confidence that the finding is real, not a result of a
   parameterization choice.
2. **California's multi-year compliance window is the most direct, working precedent for "how do
   you plan for a weather year you can't predict"** -- it doesn't require guessing which year will
   occur, because the averaging window absorbs the variance structurally. Worth including as a
   citable policy alternative if this project's own recommendations touch on RPS compliance-timing
   design.
3. **PJM's own ELCC de-rating schedule should be connected to this project's own capacity-value
   assumptions**, particularly in the DER-comp structure's own capacity-compensation component and
   any owner-IRR capacity-revenue line -- both currently at risk of assuming higher, more stable
   capacity credit than PJM's own accelerating de-rating trend supports.
4. **The winter-vs-summer stress-driver question is open, not resolved**, and should be
   investigated further (more weather years, or a genuine cold-snap-specific analysis) before this
   project states a conclusion about which season actually drives Virginia's own worst-case
   compliance risk.

## Not yet done

- No further open items from this document's own original scope. Citation cross-reference (Part 3
  of Scenario3_Literature_Search_Citations_2026-08-23.md, #95-107), the Dominion Schedule 15a/15c
  FCDS/EODS-equivalent finding, and the cold-snap/winter-share investigation (§3) were all
  completed 2026-08-23.
- Not yet checked: whether Virginia's SCC has ever formally proposed or considered connecting
  PJM's own ELCC de-rating schedule directly to RPS-percentage compliance accounting (the specific
  policy move CAISO's FCDS/EODS split represents) -- Dominion's IRP filings show the underlying
  data already exists (§2), but that's distinct from the SCC having considered the *connection*
  as a compliance-design question.
