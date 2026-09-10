# Gas Technology Selection by Scenario

*2026-09-10. Licensed [CC BY 4.0](../../LICENSE-DOCS).*

Which gas technology a scenario should build is **scenario-dependent**, because the marginal unit
does completely different work depending on how much clean generation surrounds it. Applying one
project-wide default produces the wrong capital cost in one direction or the other.

## The rule

| Scenario | Gas role | Technology | Capex basis |
|---|---|---|---|
| **Statutory Floor** (`S2`) | Bulk energy supply | **CCGT** | `lp_model.ccgt_capex_kw()`, $3,000/kW |
| **Build to Zero** (`S1`), **2045 Gas Exception** (`S1B`), **Distributed Build** (`S3`) | Residual gap-filling | **Simple-cycle peaker** | **MISSING — see gap below** |

## Evidence for the Statutory Floor being CCGT

Measured from the no-foresight dispatch across eight weather years
(`scripts/` gas capacity-factor analysis, Virginia-only load basis):

| Year | Gas MW | Fleet capacity factor | Hours running |
|---|---:|---:|---:|
| 2030 | 14,923 | 42.5% | 92.8% |
| 2035 | 18,861 | 42.3% | 82.3% |
| 2040 | 23,331 | 53.4% | 96.3% |
| 2045 | 24,382 | **57.6%** | **98.8%** |

At 42–58% capacity factor and online 82–99% of hours, this is baseload-adjacent duty. CCGT is
correct: lower heat rate and lower fuel cost per MWh, and the cycling-wear concern that motivates
the peaker rule does not apply to a unit that essentially never stops.

### A superficially contrary result, and why it is wrong

Computing the capacity factor of the *top 2,503 MW slice* of the output stack gives 0.03–0.07% —
roughly thirty hours a year, which looks like pure peaking duty and suggests simple-cycle.

**That reading is an artifact of the calculation.** Taking the top slice of the output stack
implicitly assumes the incremental unit dispatches last. A new CCGT does not enter the merit order
at the bottom: at roughly 6,400 Btu/kWh against older simple-cycle units above 10,000, it enters
near the top and runs baseload, displacing *existing* less-efficient units into the peaking role.
An operations team adding capacity to a fleet already running 98.8% of hours builds the unit that
runs hard, not one sized for thirty hours a year.

So the incremental capacity for the Statutory Floor is CCGT, and the 2,503 MW eight-weather-year
uplift at 2045 costs approximately **$7.5 billion** at $3,000/kW.

## Why the VCEA scenarios differ

In Build to Zero and Distributed Build, gas is a small residual covering short gaps in a mostly
clean system. There the fleet genuinely is not running continuously, cycling wear is the binding
constraint on lifespan (see `Gas_turbine_lifespans_reference.md`), and simple-cycle is correct —
which is the rationale the standing rule in `new_peaker_ccgt_costs_by_size.md` already gives.

## Open gap: no simple-cycle capex exists in the code

A 2026-09-10 audit found:

- `lp_model.ccgt_capex_kw()` — $3,000/kW, cross-verified against Wood Mackenzie, EPRI and GridLab.
  Correct and current. **Note it is full installed project cost, not turbine equipment only** —
  the two differ by roughly 4x and are easy to conflate.
- `lp_model.CCGT_CAPEX_KW` — the stale $1,775/kW Lazard midpoint that Internal Debugging Log #49
  found in use while the correct function sat unused beside it. **Nothing references it now**;
  renamed 2026-09-10 to `CCGT_CAPEX_KW_DO_NOT_USE_SUPERSEDED` so misuse is self-evident (Rule 12.3).
- **No simple-cycle / peaker capex constant or function exists anywhere in the package.**

The unit costs in `new_peaker_ccgt_costs_by_size.md` ($713/kW F-Class, $1,175/kW aeroderivative,
$1,084/kW H-Class) predate the 2025–2026 price surge that moved the CCGT figure from $1,775 to
$3,000/kW. That same document cites GridLab's September 2025 survey showing simple-cycle costs
rising from $562/kW (2023) to $728–1,544/kW (2025). Using the older per-unit figures would
understate VCEA-scenario gas capital cost substantially.

**A current simple-cycle installed cost, sourced the way `ccgt_capex_kw()` was, is required before
the VCEA scenarios' gas capital cost can be considered defensible.** Flagged rather than
interpolated.

## Second gap: the cost pipeline is not in the repository

`compute_scenario2_costs.py` — the caller of `ccgt_capex_kw()` — is not present. The Statutory
Floor's cost side therefore cannot be run from a clean clone, only its dispatch side.
