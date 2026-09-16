# Scenario completion dashboard

**Status only.** One row per step per scenario, its status, and what blocks it.

A step is **done** only when its result has been produced on current code, constants and scenario
definition — not when the code to produce it exists.

Narrative goes elsewhere:

| kind | where |
|---|---|
| scenario findings | `scenarios/<scenario>_Working_Document.md` |
| cross-cutting facts | `Common_Reference.md` |
| methodology spanning scenarios | the relevant appendix |
| **LP issues and their solutions** | **`Internal_Debugging_Log.md`** |
| recurring error patterns | `Common_Mistake_Log.md` |
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

| # | step | status | blockers |
|---|---|---|---|
| 1 | Solver wired and verified | **superseded** | step 3 |
| 2 | Statutory distributed carve-out | **done** | — |
| 3 | Agrivoltaic siting, applied evenly | **not started** | — |
| 4 | Merit-order stack in the solver | **done** | — |
| 5 | Gas capacity fit on the measured gap | **done** | — |
| 6 | Four-checkpoint pathway | **superseded** | step 3 |
| 7 | Twenty-year annual stream | **superseded** | step 3 |
| 8 | Annualised cost + capex band | **superseded** | step 3 |
| 9 | Social + health cost | **superseded** | step 3 |
| 10 | New gas capacity costed in | **not started** | step 3 |
| 11 | Gas price band (Deloitte MED/HIGH, EIA) | **not started** | — |
| 12 | Whitepaper section | **superseded** | step 3 |
| 13 | Unit commitment sensitivity | **blocked** | #17 |

---

## Scenario 1 — 100% Clean by 2045

Full VCEA and RPS compliance, firmed solar co-located with storage, no standalone storage.

| # | step | status | blockers |
|---|---|---|---|
| 1 | Solver wired, all-hours reserve applied | **superseded** | steps 7, 8 |
| 2 | Four-checkpoint pathway | **superseded** | #24, steps 7, 8 |
| 3 | Twenty-year annual stream | **ready** | step 2 |
| 4 | SLCOE | **not started** | step 3 |
| 5 | Social + health cost, all 20 years | **not started** | step 3 |
| 6 | Myopic vs perfect-foresight comparison | **blocked** | #22 |
| 7 | Statutory distributed carve-out | **not started** | profile built, not wired |
| 8 | Agrivoltaic siting, applied evenly | **not started** | — |
| 9 | Merit-order stack in the solver | **done** | — |
| 10 | Whitepaper section | **not started** | step 4 |

---

## Scenario 1B — 95% Clean, 5% Gas from 2045

As Scenario 1, except gas may supply 5% of the statutory base from 2045.

| # | step | status | blockers |
|---|---|---|---|
| 1 | Solver and reserve variant | **superseded** | steps 7, 8 |
| 2 | Capacity sweep result implemented (6,000 MW) | **re-check** | steps 7, 8 |
| 3 | Five-checkpoint pathway incl. 2044 | **superseded** | #24, steps 7, 8 |
| 4 | Twenty-year annual stream | **not started** | no runner |
| 5 | SLCOE | **not started** | step 4 |
| 6 | Social + health cost | **partial** | step 4 |
| 7 | Statutory distributed carve-out | **not started** | profile built, not wired |
| 8 | Agrivoltaic siting, applied evenly | **not started** | — |
| 9 | Whitepaper section | **not started** | step 5 |

---

## Scenario 3 — Distributed 80/10/10

As Scenario 1, with 10% rooftop, 10% parking canopy, and 80% remaining utility-scale of which 90%
agrivoltaic; FERC 2222 participation and hourly retail rates.

| # | step | status | blockers |
|---|---|---|---|
| 1 | Solver, reserve variant, distributed bounds | **superseded** | step 8 |
| 2 | Four-checkpoint pathway | **not started** | #14, #24 |
| 3 | Twenty-year annual stream | **not started** | step 2 |
| 4 | SLCOE | **not started** | step 3 |
| 5 | DER owner economics | **blocked** | #5, #15 |
| 6 | Transmission-deferral assessment | **not started** | #4 |
| 7 | Social + health cost | **not started** | step 3 |
| 8 | Statutory distributed carve-out | **not started** | profile built, not wired |
| 9 | Whitepaper section | **not started** | step 4 |

---

## Cross-scenario

| # | step | status | blockers |
|---|---|---|---|
| 1 | Compliance sweep, 30–100% | **not started** | S1 step 2 |
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
