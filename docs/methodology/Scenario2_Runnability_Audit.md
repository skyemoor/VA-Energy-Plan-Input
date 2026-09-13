# Scenario 2 runnability audit

**2026-09-13.** Scenario 2 is the whitepaper's **baseline** — Dominion's approach of building only
the solar and storage assets named in the Code. Before it can be plotted as the reference point on
the compliance sweep, it has to run. This records what was found tracing it.

---

## It uses a different solve path entirely

`Scenario2Solver.solve()` calls **`lp.build_scenario2_problem()`**, not `build_problem()`. It does
not use `converge_frac`, `apply_gas_cap()` or `capacity_cap_mw`.

**Gas is unbounded, and that is correct for this scenario.** The build is pinned to the statutory
solar and storage; gas fills whatever remains. That *is* Dominion's approach, and the resulting gas
share is the output we want.

**Consequence worth stating:** the two-gas-limits problem recorded in `Gas_Fleet_Working_Notes.md`
does **not** apply to Scenario 2. That cap governs Scenarios 1, 1B and 3.

---

## Three blockers

### 1. `peak_gas_mw` comes from a lost temp file

`get_existing_new_mw()` back-computes new build from `self.peak_gas_mw`, documented as coming from
*"Scenario 2's own already-solved 20-year gas capex schedule"* at
**`/tmp/scenario2_20yr_gas_capex.npz`**.

**That is a temp file.** It does not exist in any clone and did not survive any session. Whatever
was solved for is gone.

Scoped: this path is needed **only** for the social-cost/RGGI mixin. A plain cost run may not touch
it, and the constructor raises a clear error if it is called without the value rather than
substituting a default.

### 2. `compute_scenario2_gas_replacement` is not restored

`get_existing_new_mw()` imports it for `existing_fleet_mw_by_type()`. It is on the outstanding
restore list from earlier sessions, alongside `compute_tier123_final.py` and
`compute_scenario2_costs.py`.

### 3. Whether storage is pinned is unverified

`build_scenario2_problem()` takes `vcea_solar_mw`. The baseline definition requires **16,100 MW
solar, 16 GW short-duration storage, 4 GW long-duration** — all three pinned.

**Whether the storage figures are pinned or left free has not been checked.** If storage is free,
the LP optimises it and the run is not Dominion's approach — it is a partially-optimised hybrid,
and the baseline point would be wrong in the favourable direction.

---

## Why this matters for the sweep

The whole comparison rests on Scenario 2 being **genuinely** the statutory build. If any of its
three components is optimised rather than pinned, the reference point moves toward the curve and
the gap the whitepaper reports shrinks for the wrong reason.

**This is the next thing to trace**, and it gates step 3 of the sweep sequence.

---

## Related

- `Scenario_Restructuring_Compliance_Sweep.md` — why Scenario 2 is the reference
- `Gas_Fleet_Working_Notes.md` — the gas cap that does *not* apply here
- `SCENARIO_NAMES.md`, `Internal_Debugging_Log.md` #53 — prior Scenario 2 work
