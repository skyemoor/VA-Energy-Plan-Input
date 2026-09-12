# Gas Merit Order — heat rate tiers

> **Consolidated treatment: `Gas_Fleet_Working_Notes.md`** — heat rates, capacity per rung,
> cost structure, retirements, definitions and open items in one place. Read that first.

**Working note, 2026-09-11.**

## Why this exists

The LP dispatches gas at a **single marginal cost** (`GAS_COST_MWH`). Combined with unconstrained
storage arbitrage and no operating reserve, that is sufficient on its own to produce the perfectly
flat hourly energy-balance dual measured at 2030 ($54.70 in all 8,760 hours — see
`Scenario3_Technical_Notes.md`).

$54.70 ≈ $51.30 simple-cycle fuel + $3.00 VOM, so the marginal resource *is* simple-cycle gas. It
is simply priced identically in every hour. **A merit order gives the dual a ladder to climb.**

## Sourced tiers

**EIA Electric Power Annual, Table 8.2** — "Average Tested Heat Rates by Prime Mover and Energy
Source," Form EIA-860, capacity-weighted. 2024 natural gas:

| prime mover | Btu/kWh |
|---|---:|
| Combined Cycle | **7,548** |
| Gas Turbine | **10,999** |
| Steam Generator | **10,337** |
| Internal Combustion | 8,924 |

**CCGT by vintage** (EIA *Today in Energy* #61444, #60984):

| entry period | Btu/kWh |
|---|---:|
| 2014–2023 | < 7,000 |
| 2010–2022 | 6,960 (2022) |
| 2000–2009 | 7,479 (2022) |
| 1990–1999 | ~9,010 |

## The resulting stack

| tier | heat rate | 2030 fuel | 2045 fuel |
|---|---:|---:|---:|
| `ccgt_modern` | 6.400 | $34.56 | $44.32 |
| `ccgt_fleet` | 7.548 | $40.76 | $52.27 |
| `ccgt_legacy` | 9.010 | $48.65 | $62.39 |
| `ct_aeroderivative` | 9.500 | $51.30 | $65.79 |
| `ct_fleet` | 10.999 | $59.39 | $76.17 |
| **spread** | | **$24.83 (1.72×)** | **$31.85 (1.72×)** |

## A finding: our simple-cycle assumption is optimistic

`SIMPLE_CYCLE_HEAT_RATE = 9.5` is **14% better** than EIA's 2024 gas-turbine fleet average of
11.0. It describes a modern aeroderivative unit, not the fleet.

Where the question is *what the marginal peaking unit actually costs to run*, **11.0 is the better
figure**. Both are kept as separate tiers rather than one correcting the other, because they
describe genuinely different machines — but any result resting on 9.5 as "the" peaker cost is
understating marginal peaking cost by about 14%.

## What is still missing — capacity per rung

**A merit order needs MW at each tier to bind, not just prices.** The Virginia fleet split by
vintage and prime mover is not yet sourced, so these tiers **cannot yet be wired into the LP**.

The Dominion IRP PDFs in the project folder are **truncated and unreadable** — no `/Root` object,
confirmed with both `pypdf` and `pdfplumber`. Worth knowing independently, since other work may
depend on them. EIA-860 generator-level data is the likely alternative source.

`docs/methodology/VA_gas_capacity_schedules.md` already holds plant names, capacities and
retirement years (Brunswick, Greensville, Warren County, Bear Garden, Chesterfield, Doswell, Possum
Point), so mapping those to vintage and prime mover would close the gap without new plant research.

## Next

1. Source capacity per tier for the Virginia fleet
2. Wire the stack into the LP objective and dispatch
3. Re-extract hourly duals and compare against the Dominion Hub node graphics
