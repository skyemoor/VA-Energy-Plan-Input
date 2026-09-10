# DERA / VPP / WMA — Consolidated Working Notes

*Assembled 2026-08-27, direct user request: "let's assemble DERA/VPP/WMA working notes into 1
file." This file consolidates prior, scattered research (Scenario3_Scope_and_Gaps.md's own D.1-D.3
sections, Dominion_VPP_Pilot_Research.md, ThirdParty_VPP_DERA_Compensation_Benchmarks.md, and the
sourced constants already built into `citizen_ev_v2g_feature.py` / `ev_charger_rewards_feature.py`)
into a single reference, plus new research (the NYISO vs. PJM structural comparison below). The
original source files remain on disk, unmodified — this file is the new primary reference for this
topic area going forward; the originals remain the deep-dive source for their own specific material
where this summary points to them rather than repeating them in full.*

---

## 1. Core concepts and definitions

- **WMA** — Wholesale Market Access. The ability for a distributed energy resource (DER) or
  aggregation of DERs to sell products (capacity, energy, ancillary services) directly into an
  RTO/ISO's own wholesale market, rather than only through a retail utility program.
- **DERA** — DER Aggregator. A third-party (or, in some markets, self-designated) entity that
  bundles multiple individual DERs into a single "market unit" large enough to meet an RTO/ISO's
  own minimum participation threshold.
- **VPP** — Virtual Power Plant. The broader concept of coordinating many small, distributed
  resources (batteries, EVs, smart thermostats, flexible loads) to behave, from the grid's own
  perspective, like a single dispatchable power plant.
- **FERC Order 2222** (Sept. 2020) — the federal directive requiring every RTO/ISO to establish
  rules allowing DER aggregations to participate in wholesale markets. Both PJM and NYISO are
  implementing this same federal order, but — as Section 4 below shows directly — with materially
  different rules, timelines, and current operational status.

---

## 2. Dominion's own VPP Pilot filing — the Virginia-specific source

**Docket PUR-2025-00211**, Company Exhibit, Witness CSY (Courtney S. Young), Schedule 1, filed
December 2025. Direct PDF:
https://cdn-dominionenergy-prd-001.azureedge.net/-/media/content/save-energy/global/pdfs/virginia/vpp-pilot-young-testimoy-schedule-1.pdf

Full program table (Appendix C's own official numbering — corrected 2026-08-27 after an earlier
mislabeling; see `Dominion_VPP_Pilot_Research.md` for the full correction record):

| # | Program | Status | Incentive | Cost recovery |
|---|---|---|---|---|
| 1 | Residential Smart Thermostat Reward | Existing (DSM-XIII) | $25 one-time + $25/yr | DSM Rider C1A |
| 2 | Residential EV Charger Rewards (Peak Shaving) | Existing (DSM-VIII) | $40/yr | DSM Rider C1A |
| 3 | Residential Peak Time Rebate | Existing (DSM-XII) | up to $28/yr | DSM Rider C1A |
| 4 | Non-Residential Curtailment | Existing (DSM-XIII) | $36/kW/yr (~$26,250/yr avg) | DSM Rider C1A |
| **5** | **BYOD Aggregator Access Pilot** | New (DSM-XIV) | **pay-for-performance, rate NOT disclosed** | DSM Rider C1A |
| 6 | Residential Battery Storage Pilot (DR) | New (DSM-XIV) | $1,000 one-time + $294/yr | DSM Rider C1A |
| 7 | Residential IAQ Battery Storage Purchase Pilot | New (DSM-XIV) | free 13.5 kWh Powerwall 3 | DSM Rider C1A |
| 8 | Residential IAQ Battery Storage Pilot (DR) | New (DSM-XIV) | ~$183/yr avg | DSM Rider C1A |
| **9** | **Residential Managed Charging Pilot (TOU + non-TOU)** | New (DSM-XIV) | $40+$10/mo (non-TOU) / $20+$5/mo (TOU) | DSM Rider C1A |
| 10 | Non-Residential HVAC (Small/Medium Business) | New (DSM-XIV) | $75 one-time + $40/yr | DSM Rider C1A |

**Two programs matter most for Scenario 3's own D.2 work, and are genuinely different from each
other**:

- **#5, BYOD Aggregator Access Pilot** — device-agnostic (EVs, batteries, thermostats), the ONLY
  program in this filing structured around aggregator/DERA participation. This is the path
  `CitizenEVV2G` is built on. Rate undisclosed as of this research.
- **#9, Residential Managed Charging Pilot** — direct-with-Dominion enrollment (same DSM Rider C1A
  structure as the existing DLC programs), **no aggregator/DERA involvement, no WMA application**
  — checked directly against the filing's own program description (2026-08-27): no mention of
  aggregators anywhere in its eligibility or incentive language. A real, disclosed "third wrinkle"
  in the EV participation landscape — neither the existing DLC path (#2) nor the BYOD/V2G path
  (#5) — not yet scoped into this project's own code.

---

## 3. This project's own built classes (`lp_package/`)

- **`EVChargerRewards`** (`dlc_analysis/ev_charger_rewards_feature.py`) — wraps Dominion's #2.
  Implied rate $11.40/kW-yr. Territory-wide ceiling (50/50 split with CitizenEVV2G): **~179.5 MW**.
- **`CitizenEVV2G`** (`citizen_ev_v2g_analysis/citizen_ev_v2g_feature.py`) — wraps Dominion's #5
  (BYOD). `current_compensation_usd()` correctly returns `None` (concept applies, rate unpublished).
  Per-vehicle discharge rate: F-150 Lightning's own confirmed 9.6 kW (hardware-rate-binding, not
  energy-limited — verified directly, not assumed). Territory-wide ceiling (50/50 split):
  **~490.6 MW** — higher than EVChargerRewards' own ceiling despite the identical population split,
  purely because 9.6 kW (hardware discharge capability) is a much larger per-vehicle figure than
  3.51 kW (expected DLC curtailment). A real, disclosed asymmetry, not an error.
- **Mutual exclusivity**: a given vehicle's capacity counts toward #2 OR #5, never both — declared
  explicitly in code (`MUTUALLY_EXCLUSIVE_WITH`), following the same convention already established
  in `large_ci_curtailment_assumptions.py`.
- **WMA eligibility constants** (both from PJM's own primary tariff text, confirmed directly):
  `WMA_AGGREGATION_MINIMUM_KW = 100`, `WMA_AGGREGATION_MAXIMUM_PER_COMPONENT_MW = 5`,
  `WMA_OPERATIONAL_DATE_ENERGY_ANCILLARY = "2028-02-01"`,
  `WMA_OPERATIONAL_DATE_CAPACITY = "2028/2029 Base Residual Auction"`.

---

## 4. NYISO vs. PJM — structural comparison, direct user request 2026-08-27

*The user's own research on NYISO (with citations) was verified directly against a third-party
source before being used here; PJM's own equivalent requirements were researched fresh, dimension
by dimension, so this is a genuinely fair, like-for-like comparison rather than one side
pre-researched and the other assumed. This table went through two real rounds of correction
before reaching the version below — full history (what was originally found, what was
incomplete, and why) is preserved in `Internal_Debugging_Log.md` entries #119-121, not repeated
here; this version states only the final, current understanding directly in each row.*

| Dimension | NYISO | PJM | Notes |
|---|---|---|---|
| **Minimum aggregation size** | ≥100 kW | ≥100 kW | Identical |
| **Maximum per component/asset** | not found stated as a ceiling | ≤5 MW per "Component DER" | PJM confirms a ceiling; no equivalent NYISO ceiling found |
| **Minimum per individual asset (floor)** | ≥10 kW per asset within an aggregation (user-provided, verified) | not found | PJM's own sources describe only the aggregation-level 100 kW floor, no stated per-component floor |
| **Dispatch/response time, new Order 2222 DER Aggregator model** | **5-minute** real-time electronic dispatch (confirmed via a second, independent source) | not found as an explicit "X-minute" figure for the DER Aggregator model specifically | A real, disclosed gap for PJM's own newer model |
| **Telemetry interval, DER Aggregator model specifically** | **1-second** telemetry via direct communication pathway | not found at this specificity for the DER Aggregator model itself | Genuine gap — the PJM figure below is from a related but distinct manual, not confirmed identical |
| **Telemetry interval, PJM's legacy generator/direct-participant path** | n/a | **2-second "fast scan" rate** for real-time generation telemetry; 2-10 second real-time data collection generally (PJM Manual 14D, "Generator Operational Requirements") | Manual 14D governs the traditional Generation Owner interconnection path (≥1 MW) — the closest real, sourced PJM telemetry figure found, not proven identical to the newer DER Aggregator model's own requirements |
| **Physical telemetry medium — is a specific technology (e.g. fiber) mandated?** | not researched at this level of detail | **No fiber-specific mandate found.** PJMnet (PJM's own private WAN carrying ICCP data) is specified in terms of *reliability/redundancy* ("redundant data links to guarantee uninterrupted data transmission"), not a named physical medium. A real market of third-party "PJMnet-as-a-service" vendors exists to handle the integration/validation burden — suggesting the practical barrier is setup complexity, not medium restriction. Whether cellular/5G specifically qualifies was not directly confirmed either way | **Direct comparison to the real Dominion NEM/DTT precedent, per user request**: Dominion's own Direct Transfer Trip requirement for net-metered school interconnections originally forced dark fiber specifically (Alexandria City Public Schools' own $1.4M cost, $150-250K/mile) — but the SCC's Nov. 2023 ruling forced Dominion to also offer a cellular-based DTT alternative "at the customer's election." PJM's own requirement, as documented, appears structured more like the post-ruling Dominion outcome (reliability-based, not medium-locked) than the original, successfully-challenged fiber-only DTT policy — but this is an inference from what's documented, not a confirmed PJM statement that cellular qualifies |
| **Single-node requirement for energy market participation** | not found as a distinct requirement | Aggregations of energy resources must be at a single PJM pricing node (p-node) to bid into the real-time wholesale energy market; capacity/ancillary services can be aggregated across nodes | A real, PJM-specific structural constraint |
| **Credit/collateral** | required (per user's own sourced research) | required — PJM's own Attachment Q: collateral, corporate guaranty, minimum corporate debt rating of "A"/"A2" for guaranty-based participants | Both systems impose real, substantial credit barriers — a SHARED barrier, not NYISO-specific |
| **Self-aggregation under the new Order 2222 DER Aggregator model** | legally possible — a C&I owner can become its own "Market Participant" (user's own sourced finding, confirmed) | **Confirmed legally possible.** PJM's own compliance filing explicitly includes "the concept of single-resource aggregations in the definition of DER... giving the opportunity for an individual resource to serve as its own aggregator" (Lexology, citing PJM's own filing directly) | Both systems permit self-aggregation under their respective new DER models |
| **Self-aggregation under PJM's legacy Curtailment Service Provider (CSP) model** | not applicable — CSP is a PJM-specific mechanism, no NYISO equivalent researched | **Confirmed possible.** Self-registration as one's own CSP is explicit ("Register as your own CSP. Full control, but you handle compliance, training (PJM LMS), and settlements") — verified via PJM's own live, active CSP listing page | **This is the single most important finding in this table** — see the bottom line below |
| **Operational status, as of this session (Aug. 2026)** | Operational today — real, registered participants (Voltus, CPower, etc.) already active | **The new Order 2222 DER Aggregator model is not yet operational** (Feb. 1, 2028 targeted for energy/A/S; 2028/2029 BRA for capacity). **But the legacy CSP/Emergency Load Response model is operational today**, is reported as "remain[ing] dominant through 2027," and already allows self-registration without a third-party DERA | Two genuinely different PJM mechanisms with two different timelines — both matter, and conflating them was this table's own original error, now corrected throughout |

### The bottom line

**PJM's own newer, Order-2222-branded DER Aggregator model — the mechanism this project's own D.2
work and `CitizenEVV2G`/BYOD framing depend on — is not operational until 2028, and NYISO's own
equivalent model is operational today.** That comparison is real and correct.

**But it is not the whole picture for a Virginia C&I/govt entity asking "can I access PJM's
wholesale market at all today, without a third-party DERA."** The honest answer to that broader
question is **yes, via PJM's legacy CSP/Emergency Load Response mechanism** — a real, live, already-
operational path, self-registrable, that predates Order 2222 entirely and is expected to remain the
dominant C&I mechanism through 2027. The two mechanisms are genuinely different (CSP is a legacy
demand-response registration; "DER Aggregator"/"single-resource aggregation" is the new,
technology-agnostic, Order-2222-specific model this project's own BYOD work depends on) — a
whitepaper reader building a near-term C&I business case should be pointed toward the CSP path;
one thinking about the technology-agnostic, multi-resource-type future model should understand
that path specifically isn't live until 2028.

**A real, disclosed gap that remains**: the CSP path's own detailed credit/collateral, telemetry,
and settlement requirements were not independently re-verified with the same rigor as the DER
Aggregator model's own requirements above. The third-party $240,294/yr example figure (a specific
2 MW PPL facility, 2026/2027 delivery year) is from a consulting/marketing site (kilowattlogic.com),
not a PJM-published figure — illustrative, not authoritative.

---

## 5. Third-party VPP/DERA compensation benchmarks

*Full table (residential, C&I/govt, with $/kW, $/kWh, upfront, and other-compensation columns) is
maintained in the dedicated file `ThirdParty_VPP_DERA_Compensation_Benchmarks.md` — not duplicated
here in full, to avoid two copies of the same figures drifting out of sync (Rule 6). Headline
findings, safe to state without re-deriving them:*

- **No C&I aggregator checked (CPower, Voltus, Enersponse, NuEnergen) publishes a rate.** All
  require a direct sales conversation. Voltus publishes "up to" market-ceiling figures only,
  explicitly labeled "gross and approximate."
- **No company publishes a separate government rate** distinct from general C&I — government
  customers (Westchester County, CA state agencies) participate under the same undisclosed,
  negotiated structure.
- **Residential compensation structures are genuinely varied**, not just "fixed $/kW": flat $/kW
  seasonal (most common), hybrid $/kW + $/kWh (PSEG, SECO — the two exceptions the user identified),
  upfront $/kWh-of-capacity (PSEG/Enphase), and percentage-off-bill (Octopus Energy) all appear in
  the market.
- **EV discharge compensation is genuinely thinner than home battery compensation** across every
  operator checked — most EV-specific programs are still pilots (CT: 63-participant cap; MA: ~45
  vehicles enrolled at launch) or have no published rate at all (Tesla Powershare/TX).

### IRR assessment — full reasoning in the dedicated file; headline conclusions here

- **C&I/govt below 100 kW**: not computable from published data. No aggregator publishes a rate;
  Voltus's own ceiling figures are explicitly not point estimates.
- **Residential EV charger, existing DLC (#2)**: not a meaningful IRR question in the traditional
  sense — near-zero incremental capex (customer already owns the charger).
- **Residential EV charger, BYOD/V2G (#5)**: not computable at all — the compensation rate is
  unpublished, so any IRR numerator is unknown, not merely uncertain.

---

## 6. Value stacking / double-compensation — can a C&I owner get paid for both utility DLC and PJM WMA from the same asset? Direct user request 2026-08-27

*Motivated by a specific IRR-building question: can a C&I building's BEMS both (a) cover the
building's own load during a DLC event and (b) separately sell surplus power to the grid, without
double payment?*

### The governing federal principle

FERC's own Order 2222 double-counting rule is narrower than a blanket prohibition: RTOs/ISOs may
limit wholesale participation only where "a DER aggregation is receiving compensation for the same
services as part of another program" (LBNL, "State regulatory opportunities to advance DER
aggregations in wholesale markets"). The restriction is meant to be **narrowly designed** around
genuinely overlapping products — not a bar on any resource touching more than one program.

### A real, PJM-confirmed example that "stacking" genuinely works

PJM's own Inside Lines blog describes the Village of Minster, Ohio using solar-plus-storage to
**reduce peak demand (deferring equipment upgrades) while simultaneously selling grid support
services into PJM's frequency response market** — the same asset, two genuinely different products,
concurrently. This is a real, utility-scale precedent for the shape of the user's own question, even
though the specific products differ (peak-shaving + ancillary services, not retail DLC + energy
export).

### Dominion's own #4 (Non-Residential Curtailment) tariff language — verified directly, and broader than this project's own code

Direct quote, Dominion's own program page (`dominionenergy.com/virginia/save-energy/targeted-sector-programs`):

> "Customers who participate in the program may not simultaneously participate in any other load
> curtailment programs or tariffs offered by Dominion Energy Virginia, PJM Interconnection LLC, or
> any other party."

**This is broader than what `large_ci_curtailment_assumptions.py`'s own `MUTUALLY_EXCLUSIVE_WITH`
constant currently captures** — that constant lists three specific items (Schedule 10, the
Distributed Generation program, "PJM Interconnection demand response/peak-shaving programs"), but
the real tariff language sweeps in "any other load curtailment programs or tariffs... or any other
party." **Code comment update needed** — flagged here, not yet made in the code itself pending
direction on whether to expand the constant's own list or add an explanatory comment about the
broader tariff language.

**A real, plausible, but genuinely untested textual distinction**: "load curtailment" means reducing
consumption — not selling surplus generation. Exporting excess battery/solar output to the wholesale
market is a different action from curtailing load. This is a real argument, not a settled one — "or
tariffs... or any other party" is broad enough that a regulator or Dominion could reasonably read the
exclusion to cover any form of reduced net grid draw, including export. Testing this would require
either a direct clarification from Dominion/the SCC or litigating the question — not resolved by this
research.

### Is legislation required to fix this? No — a real, disclosed finding, not assumed

Checked directly rather than assumed: Dominion's Non-Residential Curtailment Program was authorized
under **§ 56-585.1's general DSM-program authority** (confirmed via the Company's own DSM Phase XIII
application notice, citing § 56-585.1 A 5). The exclusivity language itself is **Dominion's own
program design choice**, filed as part of that application and SCC-approved — it is not written into
Virginia Code. The same LBNL report confirms directly: state regulators (the SCC) **do** have
jurisdiction over retail-program eligibility rules, even though they lack jurisdiction over
wholesale market participation itself. This means the SCC already has the authority to require
narrower exclusivity language — through a future DSM application cycle or a dedicated proceeding —
**without new legislation**.

### Conceptual statutory language — offered as a secondary, "belt-and-suspenders" option, not because it's required

Since a statutory fix would be more durable than relying on a contestable textual argument or a
discretionary SCC proceeding, and since the whitepaper's own legislative readers may want a direct
option:

> **Conceptual new section, Code of Virginia, Title 56, Chapter 23** *(following the existing
> precedent of standalone numbered sections like § 56-585.1:6)*
>
> **§ 56-585.1:__. Limitation on utility demand-side management program exclusivity provisions.**
>
> A. No rate schedule, tariff, or program terms and conditions for a demand-side management program
> approved pursuant to § 56-585.1 shall prohibit a customer from concurrently (i) participating in
> such demand-side management program and (ii) separately transacting in wholesale energy, capacity,
> or ancillary services markets operated by a regional transmission organization or independent
> system operator, provided that such concurrent participation does not result in compensation for
> the same increment of demand reduction, generation, or storage discharge under both the
> demand-side management program and the wholesale market transaction.
>
> B. Nothing in this section shall be construed to require a utility or the Commission to permit
> compensation for the same megawatt or megawatt-hour of curtailed load, exported energy, or
> dispatched capacity under more than one program or tariff.
>
> C. The Commission may adopt rules to implement this section, including rules establishing
> metering, telemetry, or reporting requirements necessary to verify that concurrent participation
> under subsection A does not result in duplicate compensation.

**This is illustrative/conceptual only, not real bill language** — drafted to mirror FERC Order
2222's own "narrowly designed restrictions" standard rather than invent new principles, so it
doesn't override Dominion's legitimate anti-double-counting purpose, only requires the restriction
to be drawn around the actual overlapping product rather than a blanket "any other program"
exclusion.

---

## 7. Open items carried forward

- **D.3 (compensation structure) remains formally open** for the general case — resolved only for
  Citizen EV V2G's own specific pathway (BYOD/#5), not as a category-wide policy.
- **Dominion's own #9 (Managed Charging)** remains unscoped in code — confirmed to have no WMA
  application, but not yet built as its own feature/class.
- **Municipal transit bus V2G** remains deliberately held (direct user decision), not part of this
  file's own scope.
- **A defensible IRR estimate for the BYOD path** would require either (a) an actual DERA quote
  (outside a research pass's own scope), or (b) an explicitly-labeled sensitivity range built from
  the closest genuine analogs (MA's $275/kW, MD's targeted $300/kW) — flagged as available but not
  yet built, pending direction.
- **Whether PJM has a self-aggregation path** (analogous to NYISO's "Market Participant"
  designation) — RESOLVED, same day: yes, via two distinct mechanisms — "single-resource
  aggregations" under the new Order 2222 DER Aggregator model (confirmed via PJM's own compliance
  filing), and self-registration as one's own Curtailment Service Provider under the older, already-
  operational legacy model. The CSP path is the more immediately actionable finding, since it's
  live today rather than pending until 2028.
- **The CSP path's own detailed requirements** (credit, telemetry, settlement specifics) were not
  independently verified with the same rigor as the DER Aggregator model's own requirements in
  Section 4 — worth a dedicated pass if the whitepaper's own C&I recommendations come to depend on
  the CSP pathway specifically, given it may now be the more practically relevant near-term option
  for Virginia C&I/govt entities than the Order-2222-branded model this project has otherwise
  focused on.
- **Code update needed, not yet made**: `large_ci_curtailment_assumptions.py`'s own
  `MUTUALLY_EXCLUSIVE_WITH` constant lists three specific items, but Dominion's own real tariff
  language (Section 6) is broader — "any other load curtailment programs or tariffs... or any other
  party." The constant should either be expanded or given an explanatory comment pointing to the
  real, broader tariff language, so the code doesn't understate the actual restriction. Flagged here
  pending direction on which approach to take.
- **Whether "load curtailment" textually excludes energy-market export/arbitrage** (Section 6's own
  central open question) remains untested — would need either a direct clarification from
  Dominion/the SCC or a real test case, not resolvable through further research alone.
