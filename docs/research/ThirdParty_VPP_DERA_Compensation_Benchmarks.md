# Third-Party VPP/DERA Compensation Benchmarks — Residential, C&I, Govt

*Compiled 2026-08-27, direct user request. Objective stated by the user: determine the optimum
IRR for (1) C&I/govt entities who may not clear the 100 kW WMA aggregation minimum on their own,
and (2) residential EV charger owners, if any positive IRR exists at all. This file is the
compensation-benchmark inventory; the IRR assessment itself follows the table, and is honest
about what is and is not computable from what's actually published.*

*Sourcing note: every figure below traces to a search performed 2026-08-27 (this session) unless
otherwise marked. Where a source is a third-party aggregator/press estimate rather than a utility-
or program-published figure, that is stated directly in the "Other/notes" column -- do not treat an
unmarked figure as more authoritative than a marked one without re-checking the original source.*

---

## RESIDENTIAL

### Home battery discharge

| Operator / Program | $/kW | $/kWh (ongoing, performance) | $/kWh (upfront, one-time) | Other initial $ | Other/notes |
|---|---|---|---|---|---|
| Tesla / PECO (PA) | $80/kW seasonal | -- | -- | -- | Pay-for-performance, published by Tesla |
| Tesla / APS (AZ) | $110/kW seasonal | -- | -- | -- | Published by Tesla |
| Tesla / TEP (AZ) | up to $120/kW/season | -- | -- | -- | Published by Tesla; summer + winter separately |
| Tesla / Entergy New Orleans (LA) | $125/kW, capped $600/yr | -- | -- | -- | Published by Tesla |
| Tesla / PSEG Long Island (NY) | $8/kW-month (May-Sept) | $0.25/kWh delivered | -- | -- | HYBRID structure -- one of only two hybrid programs found |
| Tesla / SECO Energy (FL) | $1/kW-installed/month | $0.30/kWh delivered | -- | -- | HYBRID structure -- the other of the two |
| Tesla / ConnectedSolutions (MA) | $275/kW | -- | -- | -- | Highest published fixed rate found |
| Tesla / ConnectedSolutions (RI) | $225/kW | -- | -- | -- | Published by Tesla |
| Generac / NYISO+PSEG-LI VPP | up to $125 (lump-sum, May-Oct season) | -- | -- | -- | Ceiling framed as a season total, not an explicit $/kW rate |
| Generac (via Enphase hardware) / PSEG-LI Battery Storage Rewards | -- | -- | **$250/kWh usable capacity** | capped $6,250/household | UPFRONT only, no ongoing component -- a genuinely different structure from the same utility's own Tesla-partnered program above |
| Octopus Energy (TX) | -- | -- | -- | -- | **50% off energy rate** -- not a $/kW or $/kWh figure at all; a bill-discount structure |
| NJ BPU pilot (PSE&G/JCP&L) | ~$100/kW summer capacity | -- | -- | -- | Pilot stage |
| Dominion #6 -- Residential Battery Storage Pilot (VA, general) | not device-specific | -- | -- | **$1,000 one-time enrollment** | + $294/yr ongoing (flat $, not $/kW -- no mandated device size in the filing) |
| Dominion #7 -- IAQ Battery Storage Purchase Pilot (VA) | -- | -- | -- | **free 13.5 kWh Tesla Powerwall 3** (~$20,000 value) | Income/age-qualifying only |
| Dominion #8 -- IAQ Battery Storage Pilot DR (VA, companion to #7) | ~$15.91/kW/yr *(implied -- see note)* | -- | -- | -- | ~$183/yr average; conversion uses Powerwall 3's own confirmed 11.5 kW US continuous rating, since #8's own customers already have that specific device via #7 |

### EV discharge (V2G) -- genuinely thinner than home battery

| Operator / Program | $/kW | $/kWh (ongoing) | $/kWh upfront | Other initial $ | Other/notes |
|---|---|---|---|---|---|
| Bidirectional Energy / CT Residential V2G Pilot | -- | -- | -- | up to $10,800 (CT) / $8,800 (CA) charger + install, via a parallel Wallbox pilot | **$1,350 over the one-year pilot** at full participation + up to $300/yr on a separate managed-charging tier. Kia EV9 only; capped at 63 participants |
| PG&E V2X pilots (CA) | -- | -- | -- | -- | $300-$800/yr, usage-dependent; no clean $/kW stated |
| Tesla Powershare / CenterPoint + Oncor (TX) | **not published by Tesla** | -- | -- | -- | Third-party estimate only: $200-$500/yr, based on ERCOT peak pricing -- explicitly not a Tesla-published figure |
| Maryland DRIVE Act pilots (BGE/Pepco/Delmarva) | **$300/kW-year** | -- | -- | -- | TARGETED, not yet live -- targeted summer 2027; residential-only, not C&I |
| MA ConnectedSolutions (EV-specific) | $275/kW (reported) | -- | -- | -- | Press-reported, NOT utility-confirmed; ~45 vehicles enrolled at launch |
| MassCEC V2X pilot | -- | -- | -- | full charger + install paid, participant keeps equipment | Different mechanism entirely -- capital subsidy, not a discharge rate |
| Dominion #5 -- BYOD Aggregator Access Pilot (VA) | **pay-for-performance, rate NOT disclosed** | -- | -- | -- | The path CitizenEVV2G is built on -- still no published figure as of this research |
| *(context, not citizen)* Dominion Electric School Bus Program | -- | -- | -- | -- | In-kind (free battery replenishment), not cash -- a genuinely different compensation *type* |

---

## C&I / GOVT

*No company found publishes a separate government rate distinct from its general C&I offering --
NuEnergen and Enersponse both name government/institutional customers (Westchester County, City of
White Plains, California state agencies) explicitly, but under the same undisclosed, negotiated
structure as any other C&I customer. Government is therefore folded into this single section, not
given its own subheading, since no real rate distinction exists to document.*

| Aggregator | $/kW | $/kWh | $/kWh upfront | Other initial $ | Other/notes |
|---|---|---|---|---|---|
| CPower Energy | **not published** | -- | -- | -- | Own site language: "often guarantees a fixed payment per kW" -- describes the *structure*, never a number. $1.2B paid to customers since 2015 (aggregate, not a rate) |
| Voltus | **not published** | -- | -- | -- | Publishes market-CEILING figures only: "up to $450,000/MW-yr" (NYISO), "up to $470,000/MW-yr" (ISO-NE) -- explicitly labeled "gross and approximate... more precise estimates by speaking to a team member" |
| Enersponse | **not published** | -- | -- | -- | Generic "financial incentives" language only; works with CA state agencies at no cost to the agency, incentive value undisclosed |
| NuEnergen | **not published** | -- | -- | -- | Generic "revenue"/"cash income" language only; works with Westchester County govt customers under the same undisclosed structure |
| Dominion #4 -- Non-Residential Curtailment (VA, existing) | **$36/kW/yr** | -- | -- | -- | ~$26,250/yr average per participant reported separately -- cross-checks to an implied ~729 kW average enrolled size (26,250 / 36), a useful internal consistency check, not a second data point |

---

## The structural finding that matters most for the IRR objective

**Dominion's own #4 (Non-Residential Curtailment) and #5 (BYOD) both require >=100 kW.** A
sub-100kW Virginia C&I or government entity cannot access either program directly on its own -- the
only path is third-party aggregation. And **none of the four C&I aggregators checked (CPower,
Voltus, Enersponse, NuEnergen) publish a rate** -- every one requires a direct sales conversation
for an actual number.

---

## IRR assessment -- honest about what is and isn't computable

### C&I/govt below 100 kW

**Not computable from published data.** There is no public $/kW or $/kWh figure for the only
realistic pathway (third-party aggregation) -- Voltus's own "up to $450,000/MW-yr" ceiling is
explicitly not a rate, and using it as an IRR input would silently convert a marketing ceiling into
a false point estimate. The honest options going forward: (1) treat Voltus's own ceiling as an
explicit, labeled UPPER BOUND for a best-case sensitivity run, not an expected value; or (2) treat
this segment's own IRR as genuinely unknown pending an actual aggregator quote, which is outside
what a research pass can produce. Recommend NOT computing a false-precision IRR number here without
first deciding which of these two framings the whitepaper should use.

### Residential EV charger -- the question has two genuinely different answers depending on path

**Existing DLC (Dominion #2, EVChargerRewards)**: near-zero incremental capex, since the program
assumes the customer already owns a Level 2 charger for their own charging needs -- enrolling adds
no new hardware cost, only the $40/yr incentive. A traditional IRR calculation is not meaningful
here in the usual sense (there's no real "investment" being returned on) -- framing it as "$40/yr
against ~$0 incremental cost" is closer to the honest description than a computed IRR percentage
would be.

**BYOD/V2G path (Dominion #5, CitizenEVV2G)**: **not computable at all** -- the compensation rate is
unpublished, so the numerator of any IRR calculation is genuinely unknown, not just uncertain. Real
hardware costs exist and are sourced (V2H/V2G install ranges $3,950-$20,000 depending on vehicle and
charger, already on record in `citizen_ev_v2g_feature.py`'s own research), but pairing a real cost
against an unknown revenue stream produces a number with no real meaning, not a conservative
estimate.

**A real option worth flagging**: if the whitepaper needs a placeholder IRR for the BYOD path
specifically, the most defensible approach is a labeled sensitivity range using the closest genuine
analogs found this session -- Massachusetts's own $275/kW (press-reported) and Maryland's targeted
$300/kW (not yet live) -- explicitly stated as "what a mature-market rate might look like," not
"Dominion's own rate." This has not been built; flagging it as a real, available next step rather
than doing it unprompted.
