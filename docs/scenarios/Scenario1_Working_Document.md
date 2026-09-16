# Scenario 1 — 100% Clean by 2045

**The working document for Scenario 1.** Full VCEA and RPS compliance, firmed solar co-located with
storage, no standalone storage. The upper bound of the compliance axis.

Status lives in `Scenario_Completion_Dashboard.md`; LP issues and their solutions live in
`Internal_Debugging_Log.md`; recurring error patterns live in `Common_Mistake_Log.md`; open problems
live in GitHub issues. Cross-cutting facts that apply to every scenario live in
`Common_Reference.md`.

---

## Index

| # | topic | covers |
|---|---|---|
| 1 | Result | SLCOE, social and health cost — **pending re-run** |
| 2 | Build trajectory | when capacity arrives, and the delay-then-overbuild pattern |
| 3 | Curtailment | how much is spilled, and why |
| 4 | Foresight comparison | myopic against perfect foresight, and what myopia costs |
| 5 | Solver structure | reserve margin treatment, convergence, checkpoint chaining |

---

## 1. Result

**Pending re-run.** The prior four-checkpoint result predates Bath County's correction to Dominion's
1,808 MW share and the Schedule B retirement correction, both of which move every dispatch figure.

See the dashboard for what blocks it.

---

## 2. Build trajectory — delay, then overbuild

From the superseded run, to re-confirm:

| year | cumulative solar | new that step |
|---|---:|---:|
| 2030 | 8,702 MW | 8,702 |
| 2035 | 28,393 MW | 19,907 |
| 2040 | 64,114 MW | 36,424 |
| **2045** | **156,737 MW** | **92,622** |

**59.1% of the fleet arrives in the final checkpoint** — 92,622 MW at 2045 against 64,114 MW
cumulative through 2040.

That is a consequence of myopic optimisation: each checkpoint optimises against its own target, and
the early targets are weak. Whether a perfect-foresight planner would build earlier is what section
4 measures.

---

## 3. Curtailment

**142.1 TWh curtailed against 202.2 TWh served** at 2045 — the system generates roughly 344 TWh to
deliver 202.

---

## 4. Foresight comparison

**Blocked.** See issue #22: the perfect-foresight assembly produces unserved energy at 2030 that the
myopic solve does not, and the remaining difference is the salvage credit.

Measured so far: the assembly, the linking rows and the salvage credit are all clean at two periods.
The cause appears only at three or more.

---

## 5. Solver structure

`Scenario1WithReserveMargin` applies the installed reserve margin in **every hour**, not only at the
peak-net-demand hour. The peak-hour variant is retained for A/B comparison and is dormant.

Convergence uses a bracketed secant search on the gas fraction, falling back to bisection when a
secant step would leave the bracket.
