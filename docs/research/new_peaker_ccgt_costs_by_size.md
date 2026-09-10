# New Gas Peaker/CCGT Plant Costs, by Size Tier

Compiled for scoping potential new turbine purchases if Schedule A/B's
existing-fleet capacity proves insufficient to meet gas dispatch needs in
Scenario 1/3/1B/3B/3C. Organized by size tier so specific figures can be
mixed and matched to whatever shortfall size is identified.

## LEADING ASSUMPTION for addressing identified shortfalls (overhaul/retain, not new-build)

**Before defaulting to new construction, first check whether any plant
already scheduled to retire before the shortfall year can instead be
overhauled or simply retained past its formula-predicted retirement.**
This was tested directly against Scenario 1's 2035 shortfall (~1,720-1,777
MW) and found substantially cheaper than new-build:

| Path | PV, full 2026-2045 window |
|---|---|
| No action (over-comply via extra solar/storage) | $92,742.7M |
| New-build (~1,777 MW simple-cycle, per the standing rule below) | $89,525.9M |
| **Overhaul/retain existing near-EOL plants** | **$88,048.8M** |

**Specific finding for the 2035 case**: Tenaska Virginia (975 MW, formula
retirement 2034) and Ladysmith (782 MW, formula retirement 2031) --
combined 1,757 MW, closely matching the shortfall -- retained instead of
retired on schedule:
- Tenaska Virginia: within its own mid-life overhaul window (EOH=87,028,
  in the 48,000-100,000 range) -- genuine overhaul candidate, estimated
  ~$22.5M (midpoint of the \$15-30M CCGT comprehensive-overhaul range)
- Ladysmith: EOH=16,718, well BELOW typical overhaul thresholds --
  working assumption is this plant needs NO capital work at all to keep
  running past 2031; its formula retirement is likely simply premature
  given how lightly it has actually been used, not a scheduled
  overhaul-or-retire decision point
- Combined capital cost: ~$22.5M (vs. $1,936.3M for equivalent new-build
  capacity) -- even recovered over the same accelerated 10-year stranded
  basis, the annual fixed-cost burden ($2.84M/year) is trivial compared
  to new-build ($268.3M/year)

**THIS IS AN ASSUMPTION, explicitly flagged as such, not a confirmed
plan**:
- The $22.5M Tenaska Virginia overhaul cost is a midpoint estimate, not a
  plant-specific quote -- real cost depends on turbine model and actual
  scope of work needed
- Ladysmith's "no capital work needed" conclusion is an inference from
  its low EOH figure, not a confirmed engineering assessment
- Tenaska Virginia is THIRD-PARTY OWNED (Tenaska, not Dominion) --
  retaining it past its expected retirement would require a negotiated
  agreement with its owner, a real practical complication the cost math
  alone doesn't capture
- This specific pairing (Tenaska Virginia + Ladysmith) was identified for
  the 2035 shortfall specifically -- if shortfalls are found at other
  checkpoints in other scenarios, the same overhaul-first check should be
  applied there too, using whichever plants happen to be near their own
  formula-retirement dates at that point, not assumed to be this same pair

**Practical rule going forward**: when a checkpoint re-solve reveals a
capacity shortfall, first check Schedule A/B for any plant with a
formula-retirement date at or before that checkpoint year. If retaining
it (with or without an overhaul, depending on its own EOH position)
covers all or part of the shortfall, prefer that path and use new-build
(below) only for whatever capacity gap remains.

## STANDING RULE for new-build, when overhaul/retain isn't sufficient (user decision)

For Scenario 1, 1B, 3, 3B, and 3C specifically (NOT Scenario 2, which
retains its own established CCGT-based new-build methodology): any new
gas capacity needed to fill a shortfall against Schedule A/B, beyond what
overhaul/retention of near-EOL plants can cover, is modeled as
SIMPLE-CYCLE COMBUSTION TURBINES ONLY, using one or a combination of
these three specific units:

| Unit | Rated capacity | Total cost | $/kW | Fixed O&M |
|---|---|---|---|---|
| Aeroderivative | 105 MW (rounds to 100 MW) | $123.5M | $1,175/kW | $16.30/kW-yr |
| F-Class | 237 MW (rounds to 250 MW) | $165.8M | $713/kW | $7.00/kW-yr |
| H-Class | 418 MW (rounds to 430 MW) | $453.2M | $1,084/kW | $13.10/kW-yr |

**Rationale**: existing CCGT capacity is already substantial across these
scenarios; most anticipated shortfalls are likely short-duration (a few
hours at a time) gap-filling needs, exactly the duty profile simple-cycle
peakers are designed for. Heavy cycling (frequent starts/stops) sharply
shortens CCGT lifespan specifically (see
`Gas_turbine_lifespans_reference.md`) -- using CCGT to fill small,
intermittent gaps would reproduce the same wear pattern this project has
spent considerable effort identifying and correcting for in the existing
fleet. Simple-cycle units are the physically and economically appropriate
choice for this role.

These three units can be combined as needed to approximate whatever
specific shortfall size a checkpoint re-solve reveals (e.g., one F-Class
unit for a ~240 MW gap; an Aeroderivative + F-Class pairing for a gap in
the 300-350 MW range).

## Important context: costs have risen sharply and recently

Per GridLab's September 2025 market survey (the most rigorous, recent
source found): combustion turbine (simple-cycle) costs for plants placed
in service in 2023 averaged **$562/kW**; by 2025, costs range
**$728-$1,544/kW** — roughly a 2-3x increase in just two years. CCGT
costs show the same pattern: plants completing 2026-2027 were reported at
$1,116-$1,427/kW, while the most recent CCGT projects are "routinely
reporting costs of $2,000/kW." **Any cost figure used in modeling should
be treated as reflecting this elevated, still-rising market, not
historical averages** — a project quoted at pre-2023 prices would
meaningfully understate current cost.

## Small tier (20-50 MW) — fast-deployment, aeroderivative

- **GE TM2500 mobile aeroderivative** (30 MW package): $950-1,250/kW EPC,
  commissioned in 120-180 days from deposit. Designed for fast-track
  captive/bridge power. (USP&E Global, 2026)
- **General small-project range (25-50 MW)**: $1,400-2,000/kW — smaller
  projects carry a real cost-per-kW premium versus larger ones due to
  reduced economies of scale. (USP&E Global, 2026)
- Illustrative project cost at 30 MW, midpoint ~$1,100/kW: **~$33M**

## Medium tier (100-250 MW) — the classic "single new peaker" scale

- **Aeroderivative 100 MW simple-cycle genset**: twin gas turbine unit
  rated 105 MW, 41.5% efficiency, **$123.5M total ($1,175/kW installed)**,
  $16.30/kW fixed O&M. (Gas Turbine World 2024 Handbook)
- **F-Class 240 MW simple-cycle genset**: single F-Class unit rated
  237 MW, 38.2% efficiency, **$165.8M total ($713/kW installed)**,
  $7.00/kW fixed O&M. (Gas Turbine World 2024 Handbook)
- Note the efficiency-of-scale effect here: the larger 237 MW unit has a
  LOWER per-kW cost ($713) than the smaller 105 MW unit ($1,175), despite
  being a newer technology class -- consistent with the broader "size
  matters" pattern found elsewhere in this research

## Large tier (400-600 MW) — combined-cycle territory

- **H-Class 430 MW single-shaft combined cycle**: rated 418 MW, 58.9%
  efficiency, **$453.2M total ($1,084/kW installed)**, $13.10/kW fixed
  O&M. (Gas Turbine World 2024 Handbook)
- **600 MW combined-cycle plant** (generic mid-range scenario): HRSGs,
  advanced turbines, moderate interconnection work. **$700-900M total
  ($1,170-1,500/kW)**. (LatestCost, 2026)
- **550 MW combined-cycle** (generic build-cost estimate): **$1.8M/MW,
  ~$990M total** — notably higher per-kW than the ranges above, likely
  reflecting the most recent, elevated 2026 cost environment described
  above. (Design Transition Studio, 2026)

## Very large tier (1,000+ MW)

- **H-Class 1,100 MW multi-shaft combined cycle**: rated 1,083 MW, 59.4%
  efficiency, **$958M total ($950/kW installed)**, $12.20/kW fixed O&M.
  (Gas Turbine World 2024 Handbook)
- **1,000+ MW ultra-efficient CCGT** (premium scenario): high-grade
  turbines, low-emission systems, complex site work. **$1.2-1.6B total
  ($1,200-1,600/kW)**. (LatestCost, 2026)
- For direct comparison: this project's own established figure for CCGT
  is **$2,400/kW** (used throughout Scenario 2's CCGT sizing) --
  meaningfully higher than most figures in this table, consistent with
  reflecting the most current, elevated market rather than 2023-2024
  price levels.

## Simple-cycle (300 MW) — filling the gap between medium and large

- **300 MW simple-cycle plant** (basic scenario): standard emissions
  controls, standard interconnection. **$310-360M total
  ($1,033-1,200/kW)**. (LatestCost, 2026)

## General O&M reference (across sizes)

Typical ongoing O&M for an installed gas plant: **$25-50/kW-year**, plus
fuel — broadly consistent with (though somewhat higher than) the specific
fixed-O&M figures listed per genset above.

## Quick-reference summary table

| Size | Technology | Total cost | $/kW | Source |
|---|---|---|---|---|
| 30 MW | Aeroderivative, mobile | ~$33M (est.) | $950-1,250 | USP&E, 2026 |
| 105 MW | Aeroderivative, simple-cycle | $123.5M | $1,175 | Gas Turbine World |
| 237 MW | F-Class, simple-cycle | $165.8M | $713 | Gas Turbine World |
| 300 MW | Simple-cycle | $310-360M | $1,033-1,200 | LatestCost |
| 418 MW | H-Class, combined-cycle | $453.2M | $1,084 | Gas Turbine World |
| 550 MW | Combined-cycle | ~$990M | $1,800 | Design Transition Studio |
| 600 MW | Combined-cycle | $700-900M | $1,170-1,500 | LatestCost |
| 1,083 MW | H-Class, combined-cycle | $958M | $950 | Gas Turbine World |
| 1,000+ MW | Premium CCGT | $1.2-1.6B | $1,200-1,600 | LatestCost |

## Caveats

- Costs vary regionally by roughly ±15-30% versus national benchmarks;
  Virginia-specific figures were not separately sourced here
- "Prime mover" equipment typically represents only 30-50% of total
  installed cost — balance of plant (transformers, switchgear,
  interconnection, fuel infrastructure, civil works) accounts for the
  rest; buyers benchmarking on equipment price alone can underestimate
  installed cost by 40-80%
- Given the sharp, recent cost escalation noted above, figures toward the
  higher end of each range (or this project's own $2,400/kW CCGT figure)
  are likely more representative of actual, current procurement
  conditions than the lower ends of these ranges
- These are overnight capital costs (excluding financing/inflation during
  construction) — actual project costs including financing would be
  higher
