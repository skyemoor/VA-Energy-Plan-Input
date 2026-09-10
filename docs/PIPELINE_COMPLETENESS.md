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
| ~~`assumptions`~~ | `checkpoint_solver.py` | **RESTORED 2026-09-10.** See "What restoring it found" below. |
| `compute_scenario2_gas_replacement` | `checkpoint_solver.py` | `Scenario2Solver.get_existing_new_mw()` cannot run — blocks the social-cost/RGGI mixin for the Statutory Floor. |
| `compute_tier123_final` | `checkpoint_solver.py` | Blocks Tier 1/2/3 social cost calculation for every scenario. |
| `compute_scenario2_costs` | (not imported in-repo; referenced in docs) | The Statutory Floor capital cost pipeline. Calls `lp_model.ccgt_capex_kw()`, which nothing else in the repository calls. |
| ~~`dlc_assumptions`~~ | `scenario3_build.py` | **RESTORED 2026-09-10**, then renamed `dlc_derived_assumptions` once its primitive inputs moved to `assumptions.py` and only the derivation chain remained. |
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

---

## What restoring `assumptions.py` found (2026-09-10)

Restoring the module and comparing it value-by-value against `lp_model.py` — which legitimately
holds its own copies, needing them at import time for objective construction — found **24 shared
constants in agreement and one divergent**:

| Constant | `assumptions.py` | `lp_model.py` |
|---|---:|---:|
| `RESILIENCE_TILT_PCT` | **0.0** | **0.03** |

`lp_model.py` is the current one: it reinstated 0.03 on 2026-09-04 after the RBD trial (Internal
Debugging Log #20.6) concluded, with a full rationale, and applies it to `IRON_AIR_ENERGY_MWH`'s
objective coefficient. `assumptions.py` still carried the older held-at-zero value and its note
"see lp_model.py's own fuller note if reinstating."

**Solved results were never wrong**, because the LP reads `lp_model.py`'s copy. But any caller
importing `assumptions.RESILIENCE_TILT_PCT` would have silently received 0.0 — for six days. This
is precisely the divergence Rule 6.2 exists to catch, and the same class of defect as Debugging
Log #49, which cost a full Scenario 2 re-run across three gas cases with and without RGGI.

**Fixed two ways**: `assumptions.py` synchronized to 0.03 with a change note, and a runtime
cross-check (`_assert_consistent_with_lp_model()`) added at the foot of the module covering all 25
shared scalars. It raises at import rather than warning, because a divergence means some caller is
already receiving a wrong number and which caller is not knowable from that module. Verified to
fire on an injected mismatch, not merely present.

## Test suite: `conftest.py` added

`tests/test_provenance.py` could not be collected — it was written while `provenance.py` sat in
the same working directory and lacked the `sys.path.insert` preamble the other test modules carry.
A `conftest.py` now handles this for the whole directory, which is the correct scope; the per-file
inserts were working only for the files that remembered them.

The six test suites written this session (95 tests) now pass together. The pre-existing suites
still cannot be collected: they need the feature modules listed above, which remain absent.

---

## Test organization (2026-09-10)

Test files were consolidated from 36 to 29. The reduction was the smaller outcome; the larger one
was that the suite had never been run whole, and on a clean checkout reported 20 collection errors
and 21 failures of which exactly **two** meant anything was actually wrong.

**By class hierarchy**, where a hierarchy genuinely exists:

| Suite | Replaced |
|---|---|
| `test_capacity_accreditation.py` | `test_storage_accreditation`, `test_scenario2_reserve_margin` |
| `test_cost_derivation.py` | `test_peaker_capex`, and the cost half of the large C&I suite |
| `test_demand_basis.py` | `test_virginia_only_demand` |

**By county**, where one does not:

`test_{arlington,fairfax,loudoun,prince_william}_siting.py` each merge that county's rooftop and
parking suites. They were NOT parameterized into one shared suite, which was the first proposal.
The counties publish different source data and therefore test different logic -- Arlington checks
building-type eligibility against GIS footprints, Loudoun checks address parsing and unique-building
counting from business-account records. A parameterized suite would assert a commonality that does
not exist. What genuinely is shared stays tested once in `test_rooftop_solar_estimation_base.py`.

**Not consolidated:** the NSRDB / solar-profile / streak-finder suites. They form a real dependency
chain and could be merged, but all their tests currently skip for want of source data, so merging
them would be unverifiable churn.

---

## County siting modules restored (2026-09-10)

All nine restored: `rooftop_solar_estimation_base` plus the eight county modules (rooftop and
parking for Arlington, Fairfax, Loudoun and Prince William). The base class was the single
blocker -- four county modules subclass it, so its absence kept all of them uncollectable.

**Test count went from 212 passing to 301.** The four-county NoVA siting assessment is now
reproducible from the repository rather than quoted from a document.

### A defect the restoration exposed

With the modules present, the merged Arlington suite failed five tests with `KeyError: 'CM_Type'`.
Cause: both source files defined `PROJECT_CSV_PATH`, and the parking definition -- appearing later
in the merged file -- silently overrode the rooftop one, so every rooftop test was reading the
parking CSV.

The merge had checked for CLASS name collisions and found one (`TestRealDataCrossCheck`, since
renamed), but not module-level CONSTANT collisions. Python shadows silently, so nothing warned,
and the merged files could not be run at the time to catch it.

Fixed by section-scoping (`ROOFTOP_PROJECT_CSV_PATH` / `PARKING_PROJECT_CSV_PATH`) rather than by
renaming just the one that broke, and `test_run_all_stages.py` now asserts that no merged suite
defines any top-level name twice.
