# Cross-State Commercial/C&I Curtailment Incentive Comparison

Compiled 2026-08-24, direct follow-up to entry #82's own avoided-cost finding for A.2 (extended,
Large C&I): Dominion's $36/kW/yr incentive captures only ~41-71% of avoided generation-capacity
cost, benchmarked against this project's own peaker-cost figures. This file checks that theoretical
finding against a second, independent kind of evidence — what other, comparable states/utilities
actually pay for similar commercial curtailment programs — rather than relying on the avoided-cost
comparison alone. States checked, per direct user request: NY, CA, MA, NJ, WA, HI.

**Headline finding: the concern is well-founded, and more consistently than the earlier residential-
battery comparison (`Cross_Utility_VPP_Compensation_Comparison.md`) found.** Every single commercial
curtailment program sourced this session, across five of the six states checked, pays more per kW
than Dominion's $36/kW/yr — not one counter-example, unlike the residential-battery comparison,
which found NYSEG's own program paying less than Dominion in that context.

## Summary table

| State/Utility | Program | Structure | $/kW-yr (or seasonal, noted) | Multiple vs. Dominion's $36 |
|---|---|---|---|---|
| **Dominion (VA)** | Non-Residential Curtailment Program | Flat, annual, no backup gen | $36/kW/yr | 1.00x (baseline) |
| NY — NYSEG | Commercial System Relief Program (CSRP) | Reservation ($4.10-4.35/kW-mo) + $0.50/kWh performance, additive | $49.20-52.20/kW/yr (capacity component only) | 1.37-1.45x |
| NY — Con Edison | Smart Usage Rewards (CSRP/DLRP/Term-DLM) | $18-25/kW-month by network tier, + $1/kWh performance | $216-300/kW/yr | 6.00-8.33x |
| CA — PG&E | BIP / Capacity Bidding Program | Monthly incentive, size/commitment-scaled | $50-200/kW/yr | 1.39-5.56x |
| MA — Eversource/National Grid | ConnectedSolutions (standard) | Seasonal (Jun-Sep), $/kW averaged across event hours | $200/kW **for the ~4-month season**, not annualized | 5.56x (season vs. Dominion's full year — not a clean annual comparison, see caveat below) |
| MA — Eversource | ConnectedSolutions+ (Boston pilot) | Enhanced, localized, seasonal | $250/kW seasonal | 6.94x (same seasonal caveat) |
| MA — Eversource | ConnectedSolutions+ (SE Massachusetts pilot) | Enhanced, extended season (summer + shoulder months) | $275/kW summer + $100/kW shoulder = $375/kW across extended season | 10.42x (same seasonal caveat, though season is longer than the standard program) |
| NJ | — | No clean, current utility-level $/kW figure found | Not sourced — see structural note below | N/A |
| WA — Puget Sound Energy | Flex C&I / Business Demand Response | Capacity + performance, annual cap | Up to $130/kW/yr | 3.61x |
| HI — Hawaiian Electric | Controlled Demand Incentive | Flat, monthly, regardless of event occurrence | $60/kW/yr | 1.67x |
| HI — Hawaiian Electric | Fast Demand Response | Performance-based bill credit, 50kW minimum | $120/kW/yr (at 50kW minimum enrollment) | 3.33x |

## Multiples vs. Dominion's own $36/kW/yr, ranked

- NY (NYSEG CSRP, lower tier): **1.37x**
- CA (PG&E, low end): **1.39x**
- NY (NYSEG CSRP, higher tier): **1.45x**
- HI (Controlled Demand Incentive — the single most structurally comparable program, same flat/
  regardless-of-event-occurrence design as Dominion's own): **1.67x**
- HI (Fast DR): **3.33x**
- WA (PSE Flex C&I): **3.61x**
- CA (PG&E, high end): **5.56x**
- MA (ConnectedSolutions, standard — seasonal caveat applies): **5.56x**
- NY (Con Edison, low end): **6.00x**
- MA (ConnectedSolutions+, Boston — seasonal caveat applies): **6.94x**
- NY (Con Edison, high end): **8.33x**
- MA (ConnectedSolutions+, SE Massachusetts — seasonal caveat applies): **10.42x**

**Even the single lowest figure found (NYSEG's own lower tier, 1.37x) still pays more than
Dominion.** No program found this session, across any of the five states with clean data, pays at or
below Dominion's own rate — a materially different (more one-sided) result than the earlier
residential-battery comparison, where NYSEG's own 3kW example paid *less* than Dominion's $294/year.

## Caveats — real structural differences, not glossed over

1. **Seasonal vs. annual programs are not directly comparable without adjustment.** Dominion's
   $36/kW/yr is a full-year figure. Massachusetts's ConnectedSolutions programs are seasonal-only
   (roughly June-September for the standard program, with the SE Massachusetts pilot extending into
   shoulder months) — a $200/kW *seasonal* payment is not the same claim as a $200/kW *annual*
   payment, even though both numbers use the same units. The multiples shown above for MA programs
   should be read as "seasonal payment vs. Dominion's full-year payment," not as a clean apples-to-
   apples annual comparison — included because even a partial-year MA payment still exceeds
   Dominion's full-year one, which is itself a meaningful finding, not because the comparison is
   methodologically clean.
2. **Capacity-only vs. capacity+performance structures differ.** Several programs (NYSEG, Con
   Edison, Hawaiian Electric's Fast DR/Energy Reduction Incentive) split compensation into a flat
   reservation/capacity payment plus a separate, additive per-event performance payment tied to
   actual delivered kWh during events. The $/kW-yr figures in the table above generally capture only
   the capacity/reservation component where a clean separation was sourced — meaning actual total
   compensation for a participant who performs well during called events would run *higher* than the
   figures shown, not lower. This means the multiples above are likely conservative (understating the
   true gap), not overstated.
3. **Eligibility thresholds vary and aren't a perfectly matched customer segment across every
   program.** Dominion's own program uses a 100 kW typical threshold; Hawaiian Electric's Fast DR and
   Con Edison's aggregator minimum both use 50 kW; PG&E's cited range applies to ">100 kW
   curtailable." Close enough to treat as a reasonable comparison set, but not a perfectly uniform
   customer segment across all seven jurisdictions.
4. **New Jersey did not yield a clean, current utility-level $/kW figure**, despite a dedicated
   search. This appears to be a genuine structural difference, not a gap in searching: New Jersey's
   commercial DR landscape leans more heavily on direct participation in PJM's own wholesale
   Emergency Load Response Program via curtailment service providers/aggregators (Enel, CPower,
   Voltus, etc.), where compensation is more market-driven/variable rather than a fixed, published
   utility tariff rate the way NY/CA/MA/WA/HI each have. Worth noting as a real difference in program
   *design philosophy* across states — some states run a distinct, utility-administered tariff with a
   published rate; New Jersey appears to rely more on direct wholesale-market pass-through — not
   simply an unsourced data point.

## Structural observations, not just magnitude

1. **Hawaiian Electric's Controlled Demand Incentive is the single most structurally comparable
   program to Dominion's own** — both are flat, monthly-equivalent payments made regardless of
   whether an event actually occurs, unlike the reservation+performance-split programs found
   elsewhere. Even on this closest-structural-match comparison, Hawaii still pays 1.67x Dominion's
   rate — suggesting the gap isn't primarily an artifact of comparing structurally different program
   designs against each other.
2. **The reservation-plus-performance split (NY, HI's Fast DR/Energy Reduction Incentive) is a
   materially different design than Dominion's own flat annual rate.** This structure rewards
   customers more when they actually deliver during real events, and less when they don't — arguably
   a more precisely avoided-cost-aligned design than a flat rate, since it ties more of the payment
   to genuine delivered value rather than mere enrollment. Worth flagging as a candidate structural
   alternative for Scenario 3's own future LP formulation, not just a candidate for a higher flat
   rate.
3. **California runs a genuinely wide range ($50-200/kW/yr) depending on commitment level and
   program**, consistent with the same multi-program-design pattern already observed in the
   residential-battery comparison (`Cross_Utility_VPP_Compensation_Comparison.md`) — California
   appears to consistently offer commercial/industrial customers several structurally distinct
   options rather than one uniform rate, a pattern now confirmed across both residential and
   commercial contexts in that state specifically.
4. **Massachusetts's tiered/localized pilot structure (ConnectedSolutions vs. ConnectedSolutions+)
   is a real, deliberate design choice, not just a blanket statewide rate** — the "+" pilots pay
   substantially more ($250-375/kW) specifically in areas with documented local grid constraints or
   excess solar, a targeted-locational-value approach conceptually similar to this project's own
   Scenario 3 Part D locational/FERC 2222 framing, worth keeping in mind as a possible design
   reference point.
5. **This is a second, independent line of evidence pointing the same direction as entry #82's own
   theoretical avoided-cost comparison, not a restatement of it.** Entry #82 asked "what should
   Dominion's rate be, based on what it avoids spending" and found a gap. This file asks "what do
   comparable utilities actually pay in practice" and finds the same conclusion via entirely
   different data (real, current, other-state tariff filings and program pages, not a cost-model
   calculation) — the two lines of evidence corroborate each other without being the same argument
   made twice.

## Relationship to entry #82's avoided-cost finding

Entry #82 found Dominion's $36/kW/yr captures only ~41-71% of avoided generation-capacity cost using
this project's own peaker-cost benchmarks. This file's own empirical finding is directionally
consistent and, if anything, more stark: every comparable program found pays at least 1.37x
Dominion's rate, with most paying 3-10x. Neither file alone would be as strong as the two together —
a theoretical avoided-cost gap could in principle reflect a modeling choice specific to this project
(e.g., an unusually expensive peaker benchmark), while a real-world multi-state pattern could in
principle reflect other states simply overpaying. Having both a theoretical, cost-based argument and
an empirical, comparative one pointing the same direction is meaningfully stronger evidence than
either alone.

## State coverage tracker — for future evidence/strategy searches (added 2026-08-24, direct user request)

The six states checked above (NY, CA, MA, NJ, WA, HI) were the user's own initial list. For best
evidentiary coverage going forward, the user pointed to CESA's own "Table of 100% Clean Energy
States" (https://www.cesa.org/projects/100-clean-energy-collaborative/guide/table-of-100-clean-energy-states/,
fetched directly, last modified 2026-08-12) as the source pool for future comparison states — the
rationale being that states with their own ambitious 100%-clean-energy mandates (comparable in
spirit to Virginia's own VCEA/RPS) are the most likely to have well-developed, comparable DR/EE
incentive programs worth checking against Dominion's own, not an arbitrary state list.

**26 jurisdictions total on CESA's list.** Virginia itself is excluded from the tracking below (it
is this project's own subject, not a comparison point). Of the remaining 25, six have already been
checked for commercial curtailment specifically (this file, entry #84):

| Status | Jurisdictions |
|---|---|
| **Checked (commercial curtailment, entry #84)** | New York, California, Massachusetts, New Jersey, Washington, Hawaii |
| **Not yet checked — available for future evidence/strategy searches** | Colorado, Connecticut, District of Columbia, Louisiana, Maine, Michigan, Nevada, New Mexico, Puerto Rico, Rhode Island, Wisconsin, Oregon, Illinois, North Carolina, Nebraska, Maryland, Minnesota, Delaware, Vermont |

**19 jurisdictions remain available**, not yet checked for commercial curtailment or any other
comparative purpose this project might need (residential DR, efficiency incentives, VPP
compensation, rate design, or any other future cross-state evidentiary question — this list is a
general-purpose source pool per the user's own framing, "for when we do future evidence or strategy
searches," not scoped narrowly to commercial curtailment alone). When picking up cross-state
comparison work in a future session, check this table first rather than re-searching a state already
covered, and update this table directly when new states are added to whatever the comparison is at
that time.

**A few of the 19 worth flagging directly, not left as an undifferentiated list**: North Carolina and
Maryland are Virginia's own immediate neighbors and both PJM-territory states (like Virginia
itself), likely offering the most directly comparable grid/market context of anything on this list.
Puerto Rico's own 100% mandate is real but its grid is physically islanded and structurally
dissimilar to PJM-integrated states — worth treating any Puerto Rico comparison as a genuinely
different context, not a peer comparison the way the PJM-adjacent states would be. Nebraska is the
only state served solely by publicly-owned utilities (per CESA's own note), a structurally distinct
utility-ownership model from Dominion's own investor-owned structure — a real caveat to carry into
any future Nebraska-specific comparison, not a reason to exclude it.
