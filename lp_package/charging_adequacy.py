"""
charging_adequacy.py

Adds a CHARGING-ADEQUACY constraint to an already-built lp.build_problem() output:

    sum_t charge[t]  >=  N_cycles_per_year  x  energy_capacity

i.e. the clean fleet must actually generate enough surplus to CYCLE the storage it builds.

WHY (this session, 2026-09-09): the 8-year continuous dispatch test found Na-ion sitting empty
85.3% of all hours and, decisively, that the existing 4,000 MW fleet ALREADY captures 75.4% of every
MWh of clean surplus that physically exists across all 8 years (16.0M MWh available, 12.1M captured).
Even capturing 100% of the remainder would close only ~55% of the 6.44M MWh unserved gap. The LP's
own positive reduced cost on the Na-ion floor ($4,543/MW -- it would build LESS if allowed) was
therefore CORRECT, not an artifact: at 2030's 54.8% clean-energy penetration there is genuinely
almost nothing to store. Storage and solar are not substitutes competing on marginal cost (which is
how the unmodified objective treats them) but COMPLEMENTS with a threshold -- surplus is convex in
clean build (measured this session: 1.5x clean generation yields 8x the annual surplus). This
constraint makes that complementarity explicit, so the LP can no longer select the cheap
gas + minimum-mandated-storage corner without also building the generation to fill that storage.

Linear in the existing decision variables (both sides), so no MILP penalty -- drops into the current
formulation directly.

PER-TECHNOLOGY CYCLE REQUIREMENTS (not a single pooled N -- that would be actively wrong): iron-air's
own demonstrated cycle life is ~1,000 cycles total (FE_CYCLE_LIFE in lp_model.py, cited C122 in
Master_Citations.xlsx), which over a ~25-year life is ~40 cycles/year. Requiring it to cycle at a
Na-ion-like daily rate would force it to consume its entire rated life in under three years. Na-ion,
by contrast, is a daily-cycling asset (CATL Tener, C119: 15,000 cycles over 25-30 years, i.e.
500-600/yr available), so a few-hundred-cycles/year requirement sits well inside its design envelope.

KNOWN LIMITATION, stated rather than hidden: this constrains total CHARGING, which the LP could in
principle satisfy by charging from gas rather than from clean surplus. Gas-charging is economically
unattractive (fuel cost plus round-trip losses versus simply running gas directly when needed) and is
separately capped by the RPS constraint's own gas-energy limit, so the risk is believed low -- but it
is not structurally prevented here. Any run using this constraint should check gas dispatch against
the unconstrained baseline; a large gas increase would indicate this loophole is being exercised.
"""
import numpy as np
from scipy import sparse
import assumptions

# Disclosed modeling choices, not researched constants -- see module docstring for the reasoning and
# the cited lifetime figures each is derived from.
# Rule 6: sourced from assumptions.py's STORAGE CYCLING REQUIREMENTS block, where the reasoning
# for the per-technology split is recorded alongside the values.
DEFAULT_NA_CYCLES_PER_YEAR = assumptions.NA_CYCLES_PER_YEAR_REQUIREMENT
DEFAULT_FE_CYCLES_PER_YEAR = assumptions.FE_CYCLES_PER_YEAR_REQUIREMENT


def add_charging_adequacy_constraint(problem, na_cycles_per_year=DEFAULT_NA_CYCLES_PER_YEAR,
                                      fe_cycles_per_year=DEFAULT_FE_CYCLES_PER_YEAR,
                                      include_distributed=True):
    IDX = problem['IDX']
    NB, NPH = problem['hv_params']
    T = problem['T']
    BUILD_SCALE = problem.get('BUILD_SCALE', 1.0)
    NVAR = NB + T * NPH

    def hv(t, k):
        return NB + t * NPH + k

    SODIUM_ION_ENERGY_MWH, IRON_AIR_ENERGY_MWH = 2, 3
    DISTRIBUTED_SODIUM_ION_ENERGY_MWH, DISTRIBUTED_IRON_AIR_ENERGY_MWH = 6, 7

    # Scale the annual cycle requirement to however many hours are actually being solved, so a
    # partial-year window isn't held to a full year's charging requirement.
    year_fraction = T / 8760.0

    specs = [
        (SODIUM_ION_ENERGY_MWH, 'nc', na_cycles_per_year),
        (IRON_AIR_ENERGY_MWH, 'fc', fe_cycles_per_year),
    ]
    if include_distributed:
        specs += [
            (DISTRIBUTED_SODIUM_ION_ENERGY_MWH, 'dist_na_charge_mw', na_cycles_per_year),
            (DISTRIBUTED_IRON_AIR_ENERGY_MWH, 'dist_fe_charge_mw', fe_cycles_per_year),
        ]

    rows, cols, data, rhs = [], [], [], []
    row = 0
    for energy_var, charge_key, cycles in specs:
        # N*year_fraction*BUILD_SCALE*energy_var - sum_t charge[t] <= 0
        rows.append(row); cols.append(energy_var)
        data.append(cycles * year_fraction * BUILD_SCALE)
        for t in range(T):
            rows.append(row); cols.append(hv(t, IDX[charge_key])); data.append(-1.0)
        rhs.append(0.0)
        row += 1

    A_new = sparse.coo_matrix((data, (rows, cols)), shape=(row, NVAR)).tocsr()
    new_problem = dict(problem)
    new_problem['A_ub'] = sparse.vstack([problem['A_ub'], A_new], format='csr')
    new_problem['b_ub'] = np.concatenate([problem['b_ub'], rhs])
    return new_problem
