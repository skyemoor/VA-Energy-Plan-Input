# Scenario 1B — 95% Clean, 5% Gas from 2045

**The working document for Scenario 1B.** As Scenario 1, except gas may supply 5% of the statutory
base from 2045. Tests whether a small gas allowance materially eases the build.

Status lives in `Scenario_Completion_Dashboard.md`, which carries the full routing table for every
kind of writing — what changed, LP issues, error patterns, source detail, citations and open
problems each have their own home.

---

## Index

| # | topic | covers |
|---|---|---|
| 1 | Result | SLCOE — **not started**; social cost per checkpoint only |
| 2 | The 5% ceiling | why it cannot be reached, and what that means |
| 3 | Gas capacity | the 6,000 MW cap, the retain/overhaul pool, and the new-build residual |
| 4 | Checkpoint structure | why 2044 is a checkpoint and 2045 builds nothing |

**Detailed methodology is Appendix N**, which carries the capacity sweep and its table.

---

## 1. Result

**SLCOE not started** — there is no twenty-year annual runner for Scenario 1B.
`run_scenario1_annual.py` is Scenario 1 specific and would need the five-checkpoint set and 1B's own
2045 capacity.

Social and health cost exist per checkpoint only.

---

## 2. The 5% ceiling cannot be reached

**Gas reaches 4.27% of the statutory base and saturates.** The convergence search leaves the
achieved share unchanged at 0.0427 across a tripling of the allowance.

**The binding constraint is physical fleet capacity, not the RPS percentage** — Appendix N.4's
original conclusion, surviving the capacity correction at 4.27% rather than the 1.63% it was first
measured at.

On the model's own clean-share axis, which counts nuclear as clean, the same dispatch is 3.66% of
total demand. The two differ because the statute excludes nuclear from the compliance base; 4.27% is
the figure a ceiling applies to.

---

## 3. Gas capacity

**6,000 MW at 2045**: 1,860 MW of Schedule B survivors, 2,862 MW retained from the overhaul pool,
and **1,278 MW of new simple-cycle CT** — the residual the capacity sweep selected, independently
reproduced by `select_overhaul_retain`.

Discreteness costs 144 MW: six F-class units at 237 MW give 1,422 MW against the 1,278 MW the
continuous solve wanted.

---

## 4. Checkpoint structure

**2044 is a checkpoint because it carries the same 5% target as 2045.** Its build therefore covers
2045, and 2045 builds nothing — confirmed by `solar_mw_new = 0`.

The cumulative fleet falls 626 MW between the two years, which is exactly the 0.5%/yr degradation of
the carried-forward build, not a reduction in capacity.
