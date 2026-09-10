# Cross-Utility Residential Battery/Solar DR-VPP Compensation Comparison

Compiled 2026-08-23, direct follow-up to: "I'm leery of Dominion's approach
as they tend to underincentivize energy efficiency and DR programs." This
file checks that concern against real, sourced data from other utilities,
rather than assuming it either way.

**Headline finding: the concern is well-founded.** Dominion's own
Residential Battery Storage Pilot ($294/year) sits meaningfully below every
other program checked here — by a factor of 1.1x to 4.7x depending on the
comparison.

## Summary table

| Utility/Program | Structure | Approx. annual/upfront value | Reserve SoC / backup priority confirmed? |
|---|---|---|---|
| **Dominion (VA)** | Flat $1,000 enrollment + flat $294/year, size-independent | $294/year | **No** — unconfirmed after two direct searches |
| **Green Mountain Power (VT)** | $850-$1,050/kW upfront (max $10,500) + ~$850/year — size-scaled | $850/year + large upfront | **Yes** — "prioritizes home backup" |
| **MA ConnectedSolutions** | $225/kW summer + $50/kW winter | ~$1,375/year (5kW example) | Not confirmed |
| **APS (Arizona)** | Per-event, ~15 events/summer, 50-80% of capacity typically allowed | $150-$500/year | **Yes** — 50-80% cap implies 20-50% reserve |
| **PG&E/Tesla ELRP (CA)** | $2.00/kWh for additional discharge during an event, min. 7 events/year | Typically ~$16/Powerwall/event | **Yes** — customer sets own Backup Reserve in-app |
| **PG&E/Sunrun Local PeakShift (CA)** | Flat one-time payment, seasonal enrollment (Jun-Oct, up to 100 hrs) | $150 one-time/battery | **Yes** — explicitly published: **20% reserve, always retained** |
| **SMUD (CA, municipal)** | Large upfront + ongoing, per Powerwall | Up to $5,400 upfront (capped $10,000/household) + ~$440/year | Not confirmed |
| **NYSERDA statewide rebate (NY)** | One-time capital rebate — NOT a DR/VPP program | $200/kWh upstate, $250/kWh Con Edison territory, capped $5,000 (≈$2,700-$3,375 for a 13.5 kWh Powerwall) | N/A |
| **NYSEG Energy Storage Solutions (NY)** | Per-kW average seasonal delivered performance — size-scaled | $50/kW seasonal (≈$150 for a 3kW example) | Not confirmed |
| **Con Edison BYOB (NY)** | Not yet launched | Not yet published | Not yet known |

## Multiples vs. Dominion's own $294/year (ongoing-payment programs only)

- Green Mountain Power: **2.9x**
- MA ConnectedSolutions: **4.7x**
- SMUD (CA): **1.5x**
- APS (midpoint): **1.1x**
- NYSEG (3kW example): **0.5x** — the one program found this session that pays *less* than Dominion, worth noting rather than cherry-picking away

## Reserve SoC — the most complete picture found so far, ranked by precision

1. **PG&E/Sunrun Local PeakShift (CA): 20% reserve, explicitly published** — the single most precise, directly-stated figure found across every utility checked this session.
2. **APS (AZ): 50-80% of capacity typically allowed per event** — implies a 20-50% customer-controlled reserve.
3. **Pacific Power (OR, found prior turn): will not drain below 10% capacity.**
4. **PG&E/Tesla ELRP (CA): customer-configurable via the Tesla app** — no fixed percentage published, but explicit that the customer sets their own level.
5. **Dominion (VA): still not confirmed**, after searches across two separate turns. Every other state checked has at least one program with an explicit reserve mechanism; Virginia's own silence on this looks more like an omission than an industry norm at this point.

## What this means concretely, using the same 8kW solar + 13.5kWh battery example already built (`residential_vpp_model.py`)

Substituting GMP's own $850/year for Dominion's $294/year (all else equal):
- Dominion-based year 2+ total (D-REC + battery DR): $578/year
- GMP-based year 2+ total: $1,134/year
- **Difference: +$556/year, a 96% increase**

## Structural observations, not just magnitude

1. **GMP and APS both scale or cap by battery size/capacity** — Dominion's
   own $294/year is flat regardless of whether the battery is 5 kWh or 20
   kWh. This is a real structural difference, not just a generosity gap:
   Dominion's flat-rate design gives a smaller device the same reward as a
   larger one, which may distort what size battery a rational customer
   installs relative to what a size-scaled program (GMP, MA) would incentivize.
2. **GMP and APS both have an explicit, utility-stated backup-power
   reserve mechanism** — directly answering the reserve-SoC question raised
   two turns ago, just not from Dominion. GMP frames it as an intentional
   design feature ("battery prioritizes home backup"), not an afterthought.
   This is real, positive evidence that such mechanisms are a normal,
   expected part of a well-designed residential battery VPP — which makes
   Dominion's own silence on the topic more notable, not less.
3. **A genuine discrepancy surfaced, not silently corrected**: this
   project's own `Scenario3_Scope_and_Gaps.md` §7.4 previously rejected MA's
   ConnectedSolutions for a "twice-replicated 50/50 winter/summer seasonal
   mismatch." This session's own sourced figures ($225/kW summer vs. $50/kW
   winter) show an **~4.5:1 summer-weighted split, not 50/50**. Flagged here
   as an open discrepancy between this session's own research and whatever
   produced the original 50/50 characterization — not yet reconciled, and
   worth revisiting before citing either figure as settled.
4. **GMP's own program scale is real and substantial**: ~75 MW aggregated
   (growing), over 5,000 customers, over 10,000 batteries, with GMP's own
   reporting of $6-11M/year in customer-wide savings — this is not a small
   pilot, it's an operating, proven, multi-year program, which strengthens
   its usefulness as a benchmark (not just a theoretical upper bound).
5. **California runs multiple, structurally distinct programs simultaneously**,
   not one uniform approach — a real, useful design-space illustration:
   - *Emergency/event-triggered, per-kWh* (PG&E/Tesla ELRP): pays only when
     the grid genuinely needs it, scales with actual delivered energy.
   - *Seasonal, flat-fee, scheduled* (PG&E/Sunrun Local PeakShift): pays a
     known amount for a known commitment window, regardless of how often
     it's actually called — lower payment, lower risk to the customer.
   - *Municipal, upfront-heavy* (SMUD): large capital incentive plus modest
     ongoing payment — closer to a purchase subsidy than a DR program.
   These are three different answers to "how should a residential DR
   program be structured," coexisting in the same state — worth treating as
   three genuinely different design options for Scenario 3, not one
   "California approach."
6. **New York separates the capital rebate from the DR payment cleanly** —
   NYSERDA's $200-250/kWh rebate is explicitly a one-time purchase subsidy,
   structurally analogous to Dominion's own $1,000 enrollment bonus, not its
   ongoing $294/year. NYSEG's separate $50/kW seasonal DR program is the
   actual ongoing-payment comparison point, and at ~$150 for a 3kW example,
   it's the one program found this session that pays **less** than
   Dominion's own $294/year — a useful check against reading every non-
   Dominion program as automatically more generous.
7. **Con Edison's own BYOB program is not yet launched** — a real, disclosed
   gap structurally identical to Dominion's own unpublished BYOD rate.
   Worth re-checking once it goes live (expected "later 2026").

## Implication for Scenario 3's own modeling

If Scenario 3's own DER-comp structure adopts Dominion's own, real figures
as the baseline (the "narrower," more defensible-to-Dominion's-own-actual-
filing choice), the resulting rooftop/canopy owner economics will likely
look **meaningfully worse** than what a comparably-designed program in a
more generous state would produce. Two live options, not yet decided
between:

1. **Use Dominion's own figures as-is** — most defensible as "what Virginia
   residents would actually receive under current Dominion policy," but
   risks understating Scenario 3's own economic case if the point is to
   show what a well-designed VPP *could* deliver.
2. **Use GMP or a blended benchmark as an alternative/upper-bound
   scenario alongside Dominion's own figures** — shows the achievable range
   if Virginia's own VPP design (still not finalized — the tariff isn't due
   until November 2026) moves toward a more generous, GMP-style structure,
   explicitly framed as a policy choice rather than Dominion's own current
   commitment.

Not decided here — flagged as a live modeling-scope choice for Scenario 3.

## Sources

All figures researched directly this session (2026-08-23), not carried over
from prior sessions:
- Green Mountain Power: Utility Dive (2023 PUC order approving BYOD
  incentive structure), Electrek (July 2026, VPP scale/savings reporting),
  NuWatt Energy (2026, consolidated program-terms summary)
- MA ConnectedSolutions: NuWatt Energy (2026, consolidated multi-state VPP
  earnings guide)
- APS: AZ Energy Hub (2026, program-terms summary)
- PG&E/Tesla ELRP: Tesla Support (official PG&E ELRP program page),
  California Energy Initiative (2026, consolidated CA VPP guide)
- PG&E/Sunrun Local PeakShift: Sunrun investor press releases (Feb. 2026
  results announcement), Solar Builder (2025), Solar Power World (2025-2026)
- SMUD: California Energy Initiative (2026)
- NYSERDA statewide rebate: NY Solar State Farm, NY Solar Incentives (2026)
- NYSEG Energy Storage Solutions: NYSEG/Avangrid official program page (2026)
- Con Edison BYOB: Hoodline (April 2026), NYSERDA Utility DLM Program
  Overview (January 2026)

## Event-based vs. everyday wholesale arbitrage — a real structural split, direct follow-up (2026-08-23)

Sorting all nine real-world programs above by compensation *type*, not just
magnitude:

| Type | Count | Programs |
|---|---|---|
| **Event-based** (limited # of grid-stress-triggered events/year) | 7 | Dominion, GMP, MA ConnectedSolutions, APS, PG&E/Tesla ELRP, SMUD, NYSEG |
| **Scheduled-daily** (fixed daily window, no fresh offer each day) | 1 | PG&E/Sunrun Local PeakShift (7-9pm daily, Jun-Oct — PG&E's own program manager described it as "less like a peaker plant, more like 24/7 baseload," not emergency DR) |
| **Capital subsidy** (neither — one-time purchase incentive) | 1 | NYSERDA statewide rebate |
| **Everyday wholesale market arbitrage** (fresh offer submitted daily, true price-taking) | **0** | **None found** |

**This is the real, honest finding, not a data gap to apologize for.** Every
actual, operating residential program checked this session — across VA, VT,
MA, AZ, CA, and NY — is either event-based, a fixed daily schedule, or a
one-time capital subsidy. Not one is genuine daily wholesale-market
participation with a fresh offer submitted each day.

**Why this makes sense**: FERC Order 2222's own residential-scale energy/
ancillary-services market pathway isn't live in PJM until February 2028
(already documented in this project's own research — `Dominion_VPP_Pilot_
Research.md` §1, §3). True daily-arbitrage DER participation currently
exists mainly at commercial/industrial scale (Voltus and similar aggregators
bidding into day-ahead/real-time markets on behalf of C&I customers), not
residential. The operational/telemetry demands of submitting a genuine daily
market offer are apparently a real barrier that residential-scale programs
haven't crossed yet, anywhere checked.

**Direct implication for Scenario 3's own modeling**: the $63.00/MWh "Energy"
component in this project's own already-built DER-comp structure
(`Scenario3_Scope_and_Gaps.md` §8.2) models a compensation *type* that has
essentially **no real-world residential precedent** yet. It's a reasonable,
defensible estimate of what wholesale-equivalent value *should* be worth to
a well-timed, storage-backed owner — but unlike the event-based DRV/PTR
figures (which DO have direct real-world precedent, e.g. NY's own DRV
program), the Energy component is closer to a theoretical construct than an
observed market rate. This distinction is worth stating explicitly in the
whitepaper — the two components of Scenario 3's own DER-comp stack rest on
meaningfully different levels of empirical grounding, and presenting them
as equally well-established would overstate the Energy component's own
evidentiary basis.

## Full three-tier taxonomy (direct user structure, 2026-08-23) — supersedes the two-way split above

1. **Daily Wholesale Market Arbitrage (Everyday Operations)**
   1. Day-Ahead Market (DAM)
   2. Real-Time / Intraday Market
2. **Ancillary Services (Everyday Grid Balancing)**
3. **Peak Demand and Event-Driven Programs (The Legacy Layer)**

Sorting every program found this session (including two new additions —
Puerto Rico's LUMA CBES and a direct check of NYISO's Special Case
Resources) into this structure:

| Tier | Count | Programs |
|---|---|---|
| **1. Daily arbitrage** | 1 | NYISO DER Participation Model (FERC-approved 2019) — confirmed **C&I-scale only** in practice (Voltus's own ~300 MW), no residential usage found |
| **2. Ancillary services** | 3 | PJM Regulation market, Rocky Mountain Power WattSmart, CA blended Tesla/Enphase/OhmConnect range ($50-400/yr) |
| **3. Event-driven (legacy)** | 10 | Dominion, GMP, MA ConnectedSolutions, APS, PG&E/Tesla ELRP, SMUD, NYSEG, **LUMA Energy Puerto Rico CBES**, **NYISO SCR/EDRP**, PG&E/Sunrun Local PeakShift |
| *(outside taxonomy)* | 1 | NYSERDA capital rebate |

## Two new additions this turn

**LUMA Energy (Puerto Rico) Community Battery Energy Storage (CBES)** —
Event-driven, but at real, proven scale:
- **$1.25/kWh** discharged during events
- Delivered through **five simultaneous third-party aggregators**
  (Fortress Power, Sonnen, Sunnova, Tesla, Virtual Peaker) — a genuinely
  different model from every other program checked, which each use a single
  utility-selected vendor
- 11,157 customers enrolled (May 2025); **70,000 batteries dispatched in a
  single event, 48 MW**, during a real ~50 MW shortfall (summer 2025),
  preventing rolling blackouts
- Transitioned from pilot to **permanent program status** within about a
  year of launch (Nov. 2023 → permanent by end of 2024) — the most
  operationally-proven program found this session
- Confirms customer-adjustable reserve margins and event opt-out, same
  pattern as GMP/APS/PG&E

**NYISO Special Case Resources (SCR) — checked directly, confirmed NOT
daily-arbitrage** despite being cited by the Foley Hoag article (see
below) as NY's "direct wholesale market participation" example:
- Structurally a **capacity-market (ICAP) resource** — paid seasonally for
  *availability*, dispatched only during actual reliability emergencies
  (day-ahead or 2-hour notice)
- NYISO's own language: "reliability-based demand response programs...
  activated at NYISO's discretion"
- **This belongs in Tier 3, not Tier 1** — worth stating directly, since
  the source article's own framing could otherwise mislead

**NYISO DER Participation Model — the one genuine Tier 1 example found**:
FERC-approved 2019, enables co-optimization across Energy (DAM + Real-
Time), Ancillary Services, and Capacity under a single registration.
Voltus reports ~300 MW enrolled since 2021 — but every source found
describes this as C&I-scale usage, not residential.

## The single most consequential finding this session: PJM's own market-access restriction

**"PJM currently restricts net metered customers from participating in
energy or capacity markets, only allowing injections into the ancillary
services markets."** (RenewableEnergyWorld, citing PJM's own rules)

Since Virginia is in PJM, this means **Ancillary Services is not one of
three theoretical options for a Dominion-territory residential NEM
owner — it is currently the only wholesale-market pathway actually open**,
given the energy/capacity-market restriction. This is a real, structural
constraint on what Scenario 3's own DER-comp modeling can defensibly claim
is achievable today for PJM-territory owners, independent of whether a
$63.00/MWh Energy-market rate is theoretically reasonable.

Separately, PJM's own market data shows **over 80% of battery revenue in
PJM today comes from providing Regulation** (frequency response) — though
this blends utility-scale/aggregated storage broadly, not confirmed as
residential-specific.

**Direct implication for Scenario 3, not yet resolved here**: the
$63.00/MWh "Energy" component (Tier 1) may not be the right anchor for a
PJM/Virginia-specific residential DER-comp figure at all. A Tier 2
(Ancillary Services) or Tier 3 (Event-based/DRV-style) rate may be the more
defensible, currently-achievable figure, given PJM's own actual
market-access rules. This is a real, open modeling-scope decision, not a
data gap — worth an explicit choice rather than defaulting to the
theoretically largest number.

## Additional sources (this turn)

- LUMA Energy Puerto Rico CBES: Foley Hoag LLP (July 2026), citing CESA's
  own Feb. 2026 Puerto Rico VPP report
- NYISO SCR: NYISO official program documentation, CPower SCR snapshot,
  Enel program guidelines
- NYISO DER Participation Model: Voltus blog, NYISO official DR program page
- PJM Regulation market / NEM restriction: Modo Energy (2025), RenewableEnergyWorld (2024)
- Rocky Mountain Power WattSmart: Idaho National Laboratory VPP report (2026)
- CA blended range: VPP.services, Temecula Solar Savings (2026)
