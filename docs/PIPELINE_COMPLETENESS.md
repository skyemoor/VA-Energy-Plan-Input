# Pipeline Completeness Audit

*2026-09-10. Licensed [CC BY 4.0](../LICENSE-DOCS).*

Systematic check of what the modeling pipeline requires versus what the repository contains.
Prompted by three missing files found incidentally in one session (the seasonal shapes `.npz`,
`demand_shape_interpolation.py`, and `compute_scenario2_costs.py`), which suggested the gap was
systematic rather than incidental. It was.

## Missing Python modules

Imported by code in the repository but not present:

| Module | Imported by | Consequence |
|---|---|---|
| `assumptions` | `checkpoint_solver.py` | The centralized constants module built in Internal Debugging Log #49 specifically to prevent duplicate-constant bugs. Its absence is the most serious item here. |
| `compute_scenario2_gas_replacement` | `checkpoint_solver.py` | `Scenario2Solver.get_existing_new_mw()` cannot run — blocks the social-cost/RGGI mixin for the Statutory Floor. |
| `compute_tier123_final` | `checkpoint_solver.py` | Blocks Tier 1/2/3 social cost calculation for every scenario. |
| `compute_scenario2_costs` | (not imported in-repo; referenced in docs) | The Statutory Floor capital cost pipeline. Calls `lp_model.ccgt_capex_kw()`, which nothing else in the repository calls. |
| `dlc_assumptions` | `scenario3_build.py` | Direct load control assumptions for Distributed Build. |
| `VA_SLCOE_Model` | `loudoun_battery_dispatch.py` | Referenced in a docstring rather than a live import; low priority. |

**Net effect: no scenario's cost side can be run from a clean clone.** Dispatch runs; costing
does not. The README's claim that results are independently reproducible is currently true only
for the physical/dispatch results, not the cost results.

*(The audit script also flagged `a`, `this`, `scratch`, `gas_cost_mwh`,
`congestion_and_loss_shape_by_month_hour` and `pathlib` — these are false positives from prose in
docstrings and from same-module function references, not real imports.)*

## Missing data files

Referenced by path but absent. Two distinct categories:

**Source data, deliberately excluded** — the county insolation and CVOW CSVs used by
`scripts/build_hydro_*.py`, and `DOM-LSE-HourlyLoadProjections-...csv`. These are public and
re-downloadable; see `DATA_SOURCES.md`. Excluded by `.gitignore` on purpose. The build scripts
expect them in `/mnt/project/`, so a clean-clone user must retrieve them first.

**Derived intermediates written to `/tmp` or a working directory** — `chained_8yr_weather.npz`,
`dist_solar_cf_8yr_chained_REAL.npy`, `demand_2045fy.npy`, `exist_solar_2045.npy`,
`dist_price_2030fy.npy`, `sim_8yr_result.npz`. These are produced by one script and consumed by
another, but nothing in the repository records the production order, and the sandbox filesystem
resets between sessions. **This is the reproducibility gap that matters most**, and it is what
`run_all.py` (Stage 4 of the implementation plan) would fix: a single entry point that produces
intermediates in dependency order rather than relying on them surviving from a previous session.

Note also that `scripts/build_hydro_2016_17.py` writes `hydro_year1_2016_17_RECONSTRUCTED.npz`
while `scenario3_build.py` reads `hydro_year1_2016_17.npz` — different names for what should be
the same file.

## Costing class structure

**There is no capital-costing class.** `SocialCostRGGIMixin` exists and covers Tier 1/2 social
costs and RGGI compliance, built in response to Internal Debugging Log #51-53, where three
free-standing scripts independently reimplemented the same year-loop and present-value logic and
two shared an undiscovered bug. Capital costing has no equivalent and lives in free-standing
scripts.

**Recommendation:** a `CapitalCostMixin` alongside `SocialCostRGGIMixin`, following the same
pattern. Per Rule 1, the test is whether the underlying formula is shared: it is — annualized
capex via CRF, vintage tracking, terminal value — with only the technology mix differing by
scenario. That is precisely the mixin-with-scenario-hook shape `SocialCostRGGIMixin` already
uses, where `get_existing_new_mw()` is the scenario-specific hook.

The scenario-specific hook here would be technology selection, which is now documented in
`methodology/Gas_Technology_Selection_By_Scenario.md`: CCGT for the Statutory Floor, simple-cycle
peakers for the VCEA scenarios.

### Current state, stated precisely

`Scenario2Solver` exists and composes `SocialCostRGGIMixin`, so the Statutory Floor's **social and
RGGI** costs are computed inside the class hierarchy correctly. Its **capital** costs are not:
they live in `compute_scenario2_costs.py`, a free-standing script that is not in this repository.

That arrangement violates Rule 1.3 — "free-standing scripts are for orchestration and one-off
analysis, not for logic that will be called more than once across scenarios" — and capital costing
is called by every scenario. It is also the precise pattern that produced Internal Debugging Log
#49: `compute_scenario2_costs.py`'s own `ccgt_capex_rate()` used the stale $1,775/kW constant
while the correct $3,000/kW function sat unused in `lp_model.py`. A method on a shared mixin
cannot drift from the class hierarchy that way.

**The refactor is the right fix and does not require finding the original script.** A
`CapitalCostMixin` can be written against the documented behaviour (annualized capex via CRF,
vintage tracking, terminal value, with technology selection as the scenario hook) and locked to
the established figures with baseline tests, as `SocialCostRGGIMixin` was. Recovering the original
would make the refactor faster and would let the new implementation be checked against it, but is
not a prerequisite.

## Priority

1. **Restore the missing modules**, `assumptions.py` first — it is the anti-duplication mechanism
   and its absence risks recreating the exact class of bug it was built to prevent.
2. **Build `run_all.py`** so derived intermediates are produced in dependency order rather than
   assumed to exist.
3. **Then** refactor capital costing into a `CapitalCostMixin`.
