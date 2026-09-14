## Appendix N — Scenario 1B

Scenario 1B: identical to Scenario 1 (utility solar, colocated firming
storage, PJM market arbitrage) for 2026-2044, full VCEA/RPS compliance
throughout that period. Diverges only at 2045+, where up to 5% gas is
permitted instead of chasing VCEA's ~100% mandate — testing whether a
small, deliberate compliance exception avoids the expensive marginal
clean-capacity buildout Scenario 1's own 2045 checkpoint required.

### N.1 Existing Fleet Capacity Bound, and Its Reconciliation

Scenario 1's 2045 checkpoint solves respect a hard gas capacity bound of
`schedule_b_baseline_mw(2045)` (1,860 MW, the VCEA-driven Schedule B
step-down — Chesterfield, Doswell, Possum Point only) plus the 2,862 MW
peaker pool (`driver.py`'s `POOL`) — 4,722 MW total. An initial check
this session found this bound might be stale, based on a generation-data
note ("zero output since Dec 2024, cause unconfirmed") for all 8 pool
plants. Direct verification against each owner's own current site —
Dominion (for Remington, Gordonsville, Elizabeth River, Darbytown,
Gravel Neck), ODEC (for Marsh Run, Louisa), and Middle River Power (for
Wolf Hills) — confirmed all 8 plants are still listed as active
facilities (C098-C100). The 4,722 MW bound
stands as originally established; no adjustment needed for Scenario 1B
specifically (this same correction was separately, and more
consequentially, applied to Scenario 2's Appendix C.10, Activity Tracker
item 75).

### N.2 Capacity Sweep: Finding the Cost-Minimizing New-Build Size

**A methodological pitfall, caught and corrected**: an initial approach
solved the 2045 checkpoint with the gas capacity bound removed entirely,
treating the LP's own chosen peak (17,704 MW) as the required new-build
size (12,982 MW beyond the existing fleet). This significantly
overstated the true requirement — the uncapped LP has no capex penalty
for gas within its own objective (only marginal fuel cost), so it had no
reason to economize on capacity once given free rein.

**Corrected approach**: swept multiple capacity caps, computing true
total system cost (LP objective + externally-priced new-build capex) at
each:

| Total gas capacity | New build | @ $1,200/kW | @ $2,000/kW | @ $2,500/kW | @ $3,000/kW |
|---|---|---|---|---|---|
| 4,722 MW (existing only) | 0 | $10,065.2M | $10,065.2M | $10,065.2M | $10,065.2M |
| 6,000 MW | 1,278 MW | $9,406.5M | **$9,469.3M** | **$9,508.5M** | **$9,547.7M** |
| 7,000 MW | 2,278 MW | **$9,362.2M** | $9,474.0M | $9,544.0M | $9,613.9M |
| 8,000 MW | 3,278 MW | $9,416.2M | $9,577.2M | $9,677.8M | $9,778.5M |
| 12,000 MW | 7,278 MW | $9,722.8M | $10,080.3M | $10,303.7M | $10,527.1M |
| 17,704 MW | 12,982 MW | $10,182.9M | $10,820.5M | $11,219.0M | $11,617.5M |

The cost-minimizing point holds remarkably stable at **6,000-7,000 MW
total (1,278-2,278 MW new)** across the full $1,200-3,000/kW capex range
tested — not sensitive to exactly where within that band the true
current simple-cycle rate falls. **Locked in: 6,000 MW total capacity
(1,278 MW new simple-cycle CT), $2,000/kW central capex assumption**
(the midpoint of the tested range, consistent with this project's own
Wood Mackenzie-sourced equipment-to-full-project-cost ratio for CCGT,
C.6, extended here to simple-cycle by the same underlying supply-chain
logic, C101).

> **INDEPENDENTLY CONFIRMED 2026-09-14.** `driver.select_overhaul_retain()` — a youngest-first
> retain/overhaul selector written for a different purpose and never called until now — reproduces
> this figure by a completely different route:
>
> ```
> 6,000 MW target − 1,860 Schedule B survivors − 2,862 MW POOL = 1,278 MW residual
> N.2's capacity sweep, above:                                   1,278 MW new CT
> ```
>
> Two pieces of work that never met, agreeing exactly.
>
> **It also surfaces a discreteness gap the sweep could not see.** F-Class units are 237 MW, so a
> 1,278 MW residual takes **six of them — 1,422 MW**, overshooting by 144. The sweep treated
> capacity as continuous. Both figures are now reported by `run_scenario1b.py`: **1,278 MW** for the
> cost comparison, **1,422 MW** for what could actually be procured.
>
> The four plants flagged `needs_overhaul` — Gordonsville (1994), Elizabeth River (1992), Darbytown
> (1990), Gravel Neck (1989) — are all at or beyond nominal CT life by 2045 and need capital work
> rather than simple retention.

### N.3 Turbine Procurement Lead Time: Feasibility Check

Confirmed current gas turbine lead times (C102-C105): 5-7 years for
heavy-duty CCGT frames (GE Vernova, Siemens, Mitsubishi all report
multi-year backlogs into 2029-2031), but materially shorter — 2-4 years
— for simple-cycle units specifically, the relevant case for this
scenario's new-build.

**Timing check**: exactly 4 years separate today (August 2026) from the
2030-equivalent question that matters here — the 2045 checkpoint itself
is 19 years out, comfortably beyond any lead-time constraint. (The
tighter, genuinely constrained case was Scenario 2's 2030 checkpoint,
addressed separately in Appendix C.11 — not a live issue for Scenario
1B, whose only new-build lands at 2045.)

> ## CORRECTION 2026-09-14 — N.4 was solved at the wrong capacity
>
> **N.2 locked in 6,000 MW total (1,278 MW new simple-cycle CT). N.4 then solved 2045 at 4,722 MW**
> — N.2's own *"existing only"* row, which its table shows costing **$10,065.2M against $9,469.3M**
> at 6,000 MW. N.4 solved the configuration N.2 explicitly rejected.
>
> **The arithmetic closes exactly:** 4,722 (existing + standing pool) + 1,278 (new CT) = 6,000.
>
> **It was never implemented in code either.** `Scenario1BSolver` inherited `apply_gas_cap()`
> unchanged, so the 1,278 MW appeared nowhere. Fixed 2026-09-14:
> `SCENARIO_1B_GAS_CAPACITY_MW = 6,000` with an override on the subclass.
>
> **What this invalidates below:** the **1.63%** gas share, and the conclusion that *"the 5%
> statutory ceiling is, in practice, largely moot... the binding constraint is physical fleet
> capacity, not the RPS percentage."* Both were measured without the capacity the sweep selected,
> and are artifacts of the omission rather than results about the scenario. **Re-measurement
> needed.**
>
> **Also fixed:** there was no `Scenario1BWithReserveMargin`, so 1B solved with **no reserve margin
> at all** while Scenarios 1 and 3 carried the all-hours constraint — holding it to a looser
> reliability standard than the scenarios it is compared against.
>
> **And 2044 must be a checkpoint for this scenario.** 2044's RPS is 5% gas, which *is* 1B's 2045
> target, so its 2045 build should equal its 2044 build. Linking 2045 back to 2040 is what produced
> the *"physically nonsensical, wildly oversized 2045 buildout"* N.4 itself records correcting.

### N.4 Full SLCOE/NPV Build

**Fully rebuilt this session, replacing an earlier attempt that
overshot** — flagged directly by the user before being propagated
further. The first attempt linked Scenario 1B's own 2045 checkpoint
back to Scenario 1's own 2040 (skipping the shared 2041-2044 window
entirely) and computed the resulting "fresh increment" via simple
subtraction — a formula that produced a physically nonsensical, wildly
oversized 2045 buildout, since 2041-2044 are genuinely identical
between the two scenarios (same RPS target every year through 2044) and
should not have been bypassed.

**The fix — and a real, separate bug it surfaced.** The physically
correct approach links 2045 to 2044 (not 2040) through this project's
own `run_solve()`/`prior_*` linking mechanism, which enforces
monotonicity as a genuine LP bound rather than a post-hoc subtraction
that can go negative. Testing this directly surfaced a real, previously
unnoticed bug: `run_solve()`'s own VCEA-storage-floor logic was
unconditionally overwriting whatever lower bound `build_problem()` had
already set from the prior checkpoint, rather than combining the two.
This never affected any of this session's own regular Scenario 1
checkpoints (their own RPS-driven build always exceeded the VCEA floor
anyway, confirmed by re-solving Scenario 1's own established 2045
checkpoint under both the old and fixed logic and getting a
byte-identical result) — but it was a real bug for Scenario 1B's own,
relaxed 2045 target, where the VCEA floor sits below what 2044 has
already built. Fixed: both storage floors now take the max of the VCEA
statutory floor and whatever the linking mechanism already requires,
rather than silently discarding the higher of the two.

> **SUPERSEDED 2026-09-14 — the paragraphs below were measured at 4,722 MW, not the 6,000 MW
> N.2 locked in.** The 1.63% gas share and the conclusion that the 5% ceiling is "largely moot"
> are artifacts of the omitted 1,278 MW of new CT. Re-measurement pending; see the correction
> above N.4.

**Result: Scenario 1B's own 2045 checkpoint requires ZERO new solar or
storage build.** 2044's own, already-built capacity already exceeds
what the relaxed, 5%-gas target needs — the LP correctly chooses to add
nothing further. Gas dispatch still pins the physical gas-fleet
capacity cap exactly (4,722 MW, the same cap Scenario 1 itself is bound
by) — but only reaches 1.63% of 2045 demand, not the full 5% the
statute would allow, because the physical fleet itself (sized down by
the VCEA's own Schedule B retirement schedule) simply cannot generate
more than that by this point in the window. **The 5% statutory ceiling
is, in practice, largely moot for Scenario 1B at 2045** — the binding
constraint is physical fleet capacity, not the RPS percentage.

**2045 dispatch cost, from the corrected hourly arrays**:

| Component | Scenario 1 | Scenario 1B |
|---|---|---|
| Na cycling | $359.2M | $347.3M |
| FE cycling | $84.5M | $84.1M |
| Gas fuel | $12.4M | $200.2M |
| Export revenue | $335.5M | $292.6M |
| Gas share of demand | 0.10% | 1.63% |

**Full 20-year result:**

| | Scenario 1 | Scenario 1B |
|---|---|---|
| PV net cost, no TV | $131.845B | $121.950B |
| Terminal value credit | $55.456B | $46.112B |
| **PV net cost, with TV** | **$76.389B** | **$75.839B** |
| **SLCOE (with TV)** | **$42.45/MWh** | **$42.14/MWh** |

**A materially different, more physically coherent conclusion than the
original, pre-session finding** ("Scenario 1B is more expensive... the
terminal-value convention penalizes Scenario 1B for building less at
2045"). That earlier finding was itself an artifact of comparing
different-vintage, uncorrected dispatch data — not a robust structural
feature of the methodology. On today's corrected basis, Scenario 1B's
own terminal value is smaller (2045 contributes nothing new to credit
back), but its own PV cost before terminal value is smaller too, by a
comparable amount — the two effects largely offset, landing the two
scenarios within $0.31/MWh of each other. The underlying reason both
figures converge is the same one identified above: since the physical
gas fleet's own hard cap binds before the RPS percentage ceiling does,
Scenario 1B's own relaxation barely changes what actually gets built or
dispatched relative to Scenario 1.

### N.5 Social Cost of Carbon/Greenhouse Gases, Health Impacts, and Total Societal SLCOE

**Fully rebuilt this session, on the same corrected 2045 basis as N.4.**
2026-2044 reused directly from Scenario 1's own already-corrected
figures (#9/D.3) — genuinely identical by construction, not an
approximation. Only 2045 differs, computed from the corrected,
zero-new-build hourly result described in N.4.

| | Scenario 1, 2045 (corrected) | Scenario 1B, 2045 (corrected) |
|---|---|---|
| Gas (MWh) | 188,877 | 3,043,582 |
| Social Cost of Carbon | $36.9M | $595.0M |
| Health Impacts | $2.1M | $33.3M |

**Full PV-weighted, total societal SLCOE:**

| | Direct SLCOE | Social Cost of GHG | Health Impacts | **Total societal** |
|---|---|---|---|---|
| Scenario 1 | $42.45/MWh | $43.66/MWh | $3.19/MWh | **$89.30/MWh** |
| Scenario 1B | $42.14/MWh | $43.81/MWh | $3.20/MWh | **$89.15/MWh** |

**Conclusion, genuinely different from every earlier version of this
comparison**: Scenario 1B and Scenario 1 now land within $0.15/MWh of
each other on total societal cost — essentially tied, not a clear
advantage in either direction. This supersedes both the original,
pre-session finding (Scenario 1B clearly more expensive) and this
session's own earlier, since-corrected intermediate figure ($90.49/MWh,
built on the since-fixed monotonicity bug). Relaxing VCEA compliance to
allow 5% gas at 2045 does not meaningfully change total cost either
way, under this project's own methodology — because the physical gas
fleet's own capacity, not the statutory percentage, is what actually
constrains Scenario 1B's own dispatch at that point.



**Code location**: `lp_package/demand_shape_interpolation.py` (full module, not just
one function). This section and that file are a matched pair per this
project's standing documentation convention -- each is written to be readable
on its own, and each points back to the other.
