# Scenario completion dashboard

**Status only.** One row per step per scenario, its status, and what blocks it.

**Steps run in dependency order: no step blocks a lower-numbered one.** Inputs first, then the
result chain, then reporting. Renumbered 2026-09-14, so step numbers cited in older build-log
entries may not match.

A step is **done** only when its result has been produced on current code, constants and scenario
definition — not when the code to produce it exists.

Narrative goes elsewhere:

| kind | where |
|---|---|
| scenario findings | `scenarios/<scenario>_Working_Document.md` |
| cross-cutting facts | `Common_Reference.md` |
| methodology spanning scenarios | the relevant appendix |
| what changed, when | `build.log` |
| **LP issues and their solutions** | **`Internal_Debugging_Log.md`** |
| recurring error patterns | `Common_Mistake_Log.md` |
| source detail behind an assumption | `Data_Sourcing_Log.md` |
| citations | `registers/Master_Citations.xlsx` |
| open problems | GitHub issues |

---

## Legend

● **done** — result produced on current code, constants and scenario definition
● **re-check** — result may still hold, but an input to it has changed
● **ready** — code complete and audited, not yet run
● **superseded** — result exists but its specification has changed
● **blocked** — cannot proceed until the listed issues are resolved
● **not started**

---

## Scenario 2 — Statutory Minimums

Build only the 16,100 MW solar and 20,000 MW storage the Code names; meet the rest with gas.

**Steps 7–10 ran on the unbounded gas path**, which dispatches capacity the fleet does not have and
so reports zero unserved energy; the bounded run shows 30.05 TWh at 2045. They are superseded until
step 6 reconciles the two.

*Renumbered 2026-09-14 so no step blocks a lower-numbered one: inputs (1–6), then the result chain
(7–10), then reporting (11–13). What was step 10 — pinning and costing new gas — is now step 6.*

| # | step | status | blockers |
|---|---|---|---|
| 1 | Solver wired and verified | **done** | — |
| 2 | Statutory distributed carve-out | **done** | — |
| 3 | Agrivoltaic siting, applied evenly | **done** | — |
| 4 | Merit-order stack in the solver | **done** | — |
| 5 | Gas capacity fit on the measured gap | **done** | — |
| 6 | New gas capacity pinned and costed; bounded and published runs reconciled | **in process** | — |
| 7 | Four-checkpoint pathway | **superseded** | 6 |
| 8 | Twenty-year annual stream | **superseded** | 7 |
| 9 | Annualised cost + capex band | **superseded** | 8 |
| 10 | Social + health cost | **superseded** | 8 |
| 11 | Gas price band (Deloitte MED/HIGH, EIA) | **not started** | 9 |
| 12 | Whitepaper section | **superseded** | 9, 10 |
| 13 | Unit commitment sensitivity | **blocked** | #17 |

---

## Scenario 1 — 100% Clean by 2045

Full VCEA and RPS compliance, firmed solar co-located with storage, no standalone storage.

| # | step | status | blockers |
|---|---|---|---|
| 1 | Statutory distributed carve-out | **not started** | profile built, not wired |
| 2 | Agrivoltaic siting, applied evenly | **not started** | — |
| 3 | Merit-order stack in the solver | **done** | — |
| 4 | Solver wired, all-hours reserve applied | **superseded** | 1, 2 |
| 5 | Four-checkpoint pathway | **superseded** | #24, 4 |
| 6 | Twenty-year annual stream | **ready** | 5 |
| 7 | Annualised cost | **not started** | 6 |
| 8 | Social + health cost, all 20 years | **not started** | 6 |
| 9 | Myopic vs perfect-foresight comparison | **blocked** | #22 |
| 10 | New-gas technology confirmed by measurement | **not started** | 5 |
| 11 | Whitepaper section | **not started** | 7 |

---

## Scenario 1B — 95% Clean, 5% Gas from 2045

As Scenario 1, except gas may supply 5% of the statutory base from 2045.

| # | step | status | blockers |
|---|---|---|---|
| 1 | Statutory distributed carve-out | **not started** | profile built, not wired |
| 2 | Agrivoltaic siting, applied evenly | **not started** | — |
| 3 | Solver and reserve variant | **superseded** | 1, 2 |
| 4 | Capacity sweep result implemented (6,000 MW) | **re-check** | 1, 2 |
| 5 | Five-checkpoint pathway incl. 2044 | **superseded** | #24, 3 |
| 6 | Twenty-year annual stream | **not started** | no runner; 5 |
| 7 | New-gas technology confirmed by measurement | **not started** | 5 |
| 8 | Annualised cost | **not started** | 6 |
| 9 | Social + health cost | **partial** | 6 |
| 10 | Whitepaper section | **not started** | 8 |

---

## Scenario 3 — Distributed 80/10/10

As Scenario 1, with 10% rooftop, 10% parking canopy, and 80% remaining utility-scale of which 90%
agrivoltaic; FERC 2222 participation and hourly retail rates.

| # | step | status | blockers |
|---|---|---|---|
| 1 | Siting cap re-derived on floor area | **blocked** | #14 |
| 2 | Statutory distributed carve-out | **not started** | profile built, not wired |
| 3 | Solver, reserve variant, distributed bounds | **superseded** | 1, 2 |
| 4 | Merit-order stack in the solver | **not started** | 3 |
| 5 | Four-checkpoint pathway | **not started** | #24, 3 |
| 6 | Twenty-year annual stream | **not started** | 5 |
| 7 | New-gas technology confirmed by measurement | **not started** | 5 |
| 8 | Annualised cost | **not started** | 6 |
| 9 | Social + health cost | **not started** | 6 |
| 10 | DER owner economics | **blocked** | #5, #15 |
| 11 | Transmission-deferral assessment | **not started** | #4 |
| 12 | Whitepaper section | **not started** | 8 |

---

## Cross-scenario

| # | step | status | blockers |
|---|---|---|---|
| 1 | Compliance sweep, 30–100% | **not started** | S1 step 5 |
| 2 | Gas price band across the sweep | **not started** | step 1 |
| 3 | Siting overlay (utility / 20% distributed / 85% agrivoltaic) | **not started** | #14, S3 |
| 4 | Data-centre demand axis | **not started** | deferred by decision |
| 5 | Final chart: annualised cost vs compliance level | **not started** | steps 1–4 |

---

## Blocking issues

| # | title | blocks |
|---|---|---|
| **#24** | `checkpoint_solver` parallel constructions | S1 2, S1B 3, S3 2 |
| **#14** | Distributed siting cap on a discredited basis | S3 2, cross 3 |
| **#22** | Perfect-foresight salvage and unserved energy | S1 6 |
| #17 | Merit order solve time | S2 13 |
| #5, #15 | DER foresight and revenue stack | S3 5 |
| #4 | Nodal prices | S3 6 |
| #3 | No import capability | caveats all; blocks none |
