# Scenario 2 — Statutory Minimums

*Draft section for the Virginia Energy Plan Input whitepaper. Figures are modelled output, not
estimates. Every number traces to `results/scenario2_slcoe_central.json` and the audit in
`docs/methodology/Scenario2_Runnability_Audit.md`.*

---

## What Scenario 2 is

Build only what the Code names. § 56-585.5(D)(2) and (E) require 16,100 MW of solar, 16,000 MW of
short-duration storage and 4,000 MW of long-duration storage. Scenario 2 builds that and nothing
more, meeting the remaining demand with gas.

It is the reference case: not a proposal, but the answer to *what happens if Virginia does exactly
what the statute requires and no more*.

## The headline

**Compliance falls even as the statutory build is completed.**

| | 2026 | 2030 | 2035 | 2040 | 2045 |
|---|---:|---:|---:|---:|---:|
| clean share | 47.4% | **48.6%** | 46.1% | 35.7% | **32.5%** |
| peak gas, MW | 13,141 | 14,948 | 18,457 | 22,926 | 22,480 |
| **annualised cost, $B/yr** | **1.88** | **3.27** | **5.72** | **8.58** | **9.98** |
| cost per MWh served | 18.39 | 27.73 | 38.44 | 45.53 | 49.38 |

Clean share **rises** to a peak near 2030 as the statutory solar comes online, then **falls to 32.5%
by 2045**. The turning point is where the fixed 16,100 MW target stops keeping pace with demand,
which grows 72% across the window — from 102.3 TWh in 2026 to 202.2 TWh in 2045.

**Annualised cost rises 5.3-fold while compliance falls by a third.** Cost per megawatt-hour served
climbs from $18.39 to $49.38.

**Storage moves energy. It does not create it.** A fixed solar target against rising demand can only
lose ground, however much storage is paired with it.

## Cost

Twenty annual solves, levelised at a 4.5% weighted average cost of capital from a 2026 base year.

| | $/MWh |
|---|---:|
| **System levelised cost, with terminal value** | **31.81** |
| without terminal value | 36.41 |

The capex sensitivity band is narrow, because **most of this scenario's cost is fuel, not capital**.
Gas capital-cost uncertainty barely moves the result; gas *price* is the sensitivity that matters,
and it is treated separately.

### Societal cost

| | PV | $/MWh |
|---|---:|---:|
| Virginia social cost of carbon (CO₂ only, statutory) | $147.09B | 74.37 |
| Social cost of greenhouse gases (CO₂ + CH₄ + N₂O) | $161.95B | **81.88** |
| Health impacts (PM, SO₂, NOₓ) | $10.96B | 5.54 |
| **Total societal levelised cost** | | **119.24** |

**The climate externality is roughly 2.4 times the direct cost.** Virginia Code § 56-598(2)(d)
requires the social cost of carbon as a component of generation operating costs; the CO₂-only
statutory figure and the broader multi-gas total are reported separately because they are different
quantities, per § 56-585.1(A)(6).

Air-toxics costs are disclosed but not monetised: no sufficiently robust dollar-per-ton figure
exists, and inventing one would create false precision rather than insight.

## The statutory obligations work against each other

The Code sets two solar requirements that pull apart over time.

**§ 56-585.5(D)(2)** requires 16,100 MW of solar or onshore wind by 31 December 2035 — a one-time
capacity target with a deadline.

**§ 56-585.5(C)(2)**, as raised by the Distributed Generation Expansion Act (HB 628 / SB 175, 2026),
requires **4.5% of the RPS obligation for 2026–2030 and 5% for 2031–2045** to come from resources of
1 MW or less. That is an annual *energy* obligation, and it grows: the RPS percentage climbs to 100%
by 2045 and energy sold roughly doubles.

| year | RPS share | distributed required | utility-scale remainder |
|---|---:|---:|---:|
| 2030 | 41% | 1,432 MW | 3,655 MW |
| 2035 | 59% | 2,856 MW | 8,589 MW |
| 2040 | 79% | 4,924 MW | 6,522 MW |
| **2045** | **100%** | **6,862 MW** | **4,583 MW** |

**By 2045 the distributed carve-out takes 60% of new solar build.** Because sub-1 MW resources are
fixed-tilt rather than tracking — a 15.3% capacity factor against 22.5% — the same nameplate
delivers roughly **4.4 TWh less** energy. Compliance falls further than the capacity figures alone
suggest.

**This analysis assumes total solar stops at 16,100 MW.** The Code does not say whether the growing
energy obligation is built on top of the capacity target or absorbed within it. Since this scenario
models a utility that does not pursue the RPS, and whose stated plan builds 16,100 MW of solar, the
cap is assumed to hold and the mix re-weights inside it.

## The finding that was not expected

**The mandated storage cannot close the gap, and it is working hard trying.**

With gas bounded by the real fleet — 12,216 MW available at 2045 — sodium-ion storage discharges
**13.04 TWh across 2,666 hours**, and **17.96 TWh of demand still goes unserved** over 3,294 hours,
peaking at 10,263 MW.

The mechanism is scarcity rather than arbitrage. With gas capped, the alternative to discharging is
unserved load, so storage runs whenever it holds charge. It needs no price spread to do so.

**So the statutory storage mandate is not mismatched to the system. It is insufficient for it.**

### Closing that gap

The shortfall is **1,233 separate blocks, median 2 hours, longest 27** — uniformly peaking duty,
with an implied capacity factor of 20.0%. Nothing in that profile clears a combined-cycle unit's
six-hour minimum run time at any output level.

Costed across capital, fuel, start-up and maintenance, **combustion turbine capacity beats combined
cycle by $1,365M/yr** — on capital, maintenance, capacity factor and duty shape alike. Only fuel
efficiency favours combined cycle, and at a 20% capacity factor there are too few running hours to
recover its higher capital.

### An honest limit on these figures

Two modelling boundaries push the same way:

● **Imports are excluded, and it accounts for most of the new gas.** Virginia sits inside PJM and
  imports roughly 20% of its energy. The hourly price data to value that exists; the hourly *volume*
  data does not, and inventing it would mean inventing the quantity that matters most.

  **Measured:** new combined-cycle capacity needed to serve the load falls from **6,547 MW with no
  imports to 2,000 MW at a 20% allowance** — so roughly **70% of the new gas this scenario builds is
  a consequence of the boundary, not of the statute.** The response is non-linear, the first 10%
  removing 1,547 MW and the second 3,000, as the peak comes off the steep part of the load duration
  curve.

  **Neither end is the answer.** A flat demand reduction is more generous than imports, which are
  dispatchable and shaped, so 2,000 MW is a lower bound; but in a scarcity year PJM may be tight
  exactly when Virginia is, and imports may not arrive when the capacity is most needed. The honest
  statement is the range: **the statutory minimum requires 6,547 MW of new gas in a self-sufficient
  Virginia, or roughly 2,000 MW if imports continue at current levels.**

● **Gas price is flat within each year.** Real PJM Mid-Atlantic prices show a **$45.92 spread**
  between overnight ($41.75/MWh) and evening peak ($87.67/MWh). Without that spread, storage can
  absorb surplus but never arbitrage, so its measured utilisation is a floor rather than an
  estimate.

**This is screening-level analysis**, which is what a capacity-expansion question of this kind
warrants at this stage. A procurement decision would require production-cost validation with unit
commitment, forced outages and transmission — a separate tool at a later stage. Full method,
formulas and limitations: Appendix Q.
## On the prior draft text

The existing whitepaper section for Scenario 2 predates the modelling and the gas-fleet rebuild. Its
figures — 13.1 CCGT units at 15.8 GW, a 65% average capacity factor, operational cost rising from
$48/MWh to over $112/MWh — do not derive from this model and are **superseded, not reconciled**.

**`docs/methodology/Gas_Consolidated_Reference.md` is the fleet reference**, rebuilt against
Dominion's 2024 Annual Report. Gas capacity in Scenario 2 is an **output** of the statutory build,
not an input: 22,479 MW at the 2045 peak.

The prior draft's gas-price trajectory — $3.50/MMBtu in 2026 rising to $11.50 by 2050 on
Marcellus/Utica depletion — describes a **single path** where this work treats gas price as a
sensitivity band (Deloitte MEDIUM and HIGH, EIA). That band has not yet been run.
