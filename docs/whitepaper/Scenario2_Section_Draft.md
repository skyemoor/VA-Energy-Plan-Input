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
| clean share | 47.4% | **49.4%** | 47.3% | 37.3% | **34.7%** |
| peak gas, MW | 13,141 | 14,938 | 18,456 | 22,926 | 22,479 |
| cost, $B/yr | 1.88 | 3.38 | 5.94 | 8.93 | 10.46 |

Clean share **rises** to a peak near 2030–31 as the statutory solar comes online, then **falls to
34.7% by 2045**. The turning point is where the fixed 16,100 MW target stops keeping pace with
demand, which grows 72% across the window — from 102.3 TWh in 2026 to 202.2 TWh in 2045.

**Storage moves energy. It does not create it.** A fixed solar target against rising demand can only
lose ground, however much storage is paired with it.

## Cost

Twenty annual solves, levelised at a 4.5% weighted average cost of capital from a 2026 base year.

| | $/MWh |
|---|---:|
| **System levelised cost, with terminal value** | **32.80** |
| without terminal value | 37.86 |
| capex sensitivity band | 32.30 – 33.51 |

The band is narrow — 3.7% — because **most of this scenario's cost is fuel, not capital**. Gas
capital-cost uncertainty barely moves the result; gas *price* is the sensitivity that matters, and
it is treated separately.

### Societal cost

| | PV | $/MWh |
|---|---:|---:|
| Virginia social cost of carbon (CO₂ only, statutory) | $145.83B | 73.73 |
| Social cost of greenhouse gases (CO₂ + CH₄ + N₂O) | $160.57B | **81.18** |
| Health impacts (PM, SO₂, NOₓ) | $10.88B | 5.50 |
| **Total societal levelised cost** | | **119.48** |

**The climate externality is roughly 2.5 times the direct cost.** Virginia Code § 56-598(2)(d)
requires the social cost of carbon as a component of generation operating costs; the CO₂-only
statutory figure and the broader multi-gas total are reported separately because they are different
quantities, per § 56-585.1(A)(6).

Air-toxics costs are disclosed but not monetised: no sufficiently robust dollar-per-ton figure
exists, and inventing one would create false precision rather than insight.

## The finding that was not expected

**The mandated storage never operates.**

At 2045, across all 8,760 hours: **zero charge, zero discharge, zero curtailment** — sodium-ion,
iron-air and Bath County pumped storage alike.

There is nothing to store. Solar delivers 41.3 TWh against 202.2 TWh of demand, and solar plus
nuclear exceeds demand in **14 hours of 8,760**. With 16,100 MW of solar against a 29,000 MW peak,
every kilowatt-hour it produces is consumed as it is made. Charging would mean burning gas at midday
to discharge in the evening, losing a tenth of it to round-trip efficiency — strictly worse than
burning the same gas in the evening.

**The two statutory mandates are mismatched.** The Code pairs 20,000 MW of storage with a solar
target far too small to fill it. That storage is built, and carries roughly **$3.4B/yr of annualised
capital by 2045**, and never cycles.

### An honest limit on that claim

Two modelling boundaries push the same way, and the result cannot separate them from the mandate
mismatch:

● **Imports are excluded.** Virginia sits inside PJM and imports roughly 20% of its energy. The
  hourly price data to value that exists; the hourly *volume* data does not, and inventing it would
  mean inventing the quantity that matters most.

● **Gas price is flat within each year.** Real PJM Mid-Atlantic prices show a **$45.92 spread**
  between overnight ($41.75/MWh) and evening peak ($87.67/MWh) — against a sodium-ion cycling cost
  of $5.43/MWh. On that spread, storage is comfortably economic **with no surplus solar at all**.

A merit order alone would not produce that spread: combined-cycle gas is cheaper than combustion
turbines in every hour, so the differential arises from minimum run times and start costs — unit
commitment, which this model does not represent.

**The mandate-mismatch finding stands** on the energy balance, which no price shape alters. **The
stranded-capital figure does not stand alone** — a model with unit commitment would have that
storage earning against the spread, and these results cannot distinguish the two.

Both boundaries also mean **every scenario's cost is overstated**: a Virginia that can import builds
less. That is conservative for an argument that clean build-out is affordable, but it is not
neutral and should not be read as neutral.

---

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
