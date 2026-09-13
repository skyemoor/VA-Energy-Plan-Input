"""
scenario2_all_hours_reserve.py

All-hours reserve margin for Scenario 2, written for Scenario 2's own problem structure.

WHY THIS IS SEPARATE FROM all_hours_reserve.py

The general version cannot be applied here, and forcing it would be worse than complex -- it would
be SILENTLY WRONG. Three structural mismatches:

    all_hours_reserve assumes          build_scenario2_problem has
    ------------------------------     ------------------------------------------------
    build variables at columns 0-7     NO BUILD BLOCK AT ALL -- 14 x T variables, all hourly
    a 21-key hourly IDX with dist_*    a 14-key IDX with no distributed segment
    problem['BUILD_SCALE']             no such key

Indexing build variables at columns 0-7 on a problem whose column 0 is hour 0's gas dispatch would
not raise. It would run, and produce a constraint tying reserve to arbitrary hourly variables --
arithmetic that looks plausible and means nothing. That is the failure mode this file exists to
avoid.

WHAT MAKES SCENARIO 2's VERSION SIMPLER

Everything is pinned. There is no build to size against the margin, so the constraint does not ask
"build enough to hold reserve" -- it asks "hold reserve out of the fixed fleet you have". That makes
it a dispatch constraint rather than a sizing one, and removes every build-variable term.

If the fixed fleet cannot hold the margin, the LP becomes infeasible. THAT IS A FINDING, not an
error: it would mean the statutory build cannot meet Virginia's reserve requirement at any dispatch,
which is precisely the kind of thing this baseline exists to reveal.

ON STRICTNESS, stated because it is a real qualification

This applies the INSTALLED RESERVE MARGIN at every hour. IRM is a PLANNING standard -- one-day-in-
ten-years LOLE, evaluated at peak -- not an hourly operating requirement. Holding it in all 8,760
hours is stricter than PJM requires of anyone. It is defensible as a conservative reliability floor,
but it must be labelled as MORE CONSERVATIVE THAN PJM rather than as "the PJM reserve margin".
"""
import numpy as np
from scipy import sparse

import assumptions


def add_scenario2_all_hours_reserve(problem, nuclear, wind_cf, exist_solar, solar_cf,
                                     vcea_solar_mw, na_power_mw, fe_power_mw, gas_ceiling_mw,
                                     demand, irm=0.177):
    """Requires (1 + irm) x demand of AVAILABLE capacity in every hour, not just at peak.

    "Available" means what could actually be delivered, which for storage is
    `min(rated_power, state_of_charge)` -- not rated power assumed full. A post-hoc audit using the
    assumed-full convention once reported zero unserved energy while 769 hours were in fact short
    of margin, which is the distinction this enforces.

    Adds two variables per hour (sodium and iron-air reserve headroom) and five rows:
      nd[t] + na_reserve[t] <= na_power_mw          headroom is capacity not already discharging
      na_reserve[t] <= nsoc[t]                      and cannot exceed stored energy
      fd[t] + fe_reserve[t] <= fe_power_mw
      fe_reserve[t] <= fsoc[t]
      firm + reserve >= (1 + irm) * demand[t]       the margin itself

    Gas enters at its CEILING rather than its dispatch: reserve margin is about capacity available
    to be called, and gas not currently running is still available. Using actual dispatch would
    conflate energy with capacity.
    """
    IDX = problem['IDX']
    NB, NPH = problem['hv_params']
    T = len(demand)
    if NB != 0:
        raise ValueError(
            f'build_scenario2_problem is expected to have no build block, but hv_params reports '
            f'NVAR_BUILD={NB}. This function indexes hourly variables directly and would be wrong '
            'if a build block existed -- use all_hours_reserve.py for problems that have one.')
    for required in ('nd', 'nsoc', 'fd', 'fsoc'):
        if required not in IDX:
            raise ValueError(
                f'IDX is missing {required!r}; this does not look like a Scenario 2 problem. '
                'Applying this constraint to another problem shape would index the wrong columns '
                'without raising.')

    def hv(t, k):
        return t * NPH + IDX[k]

    n_old = len(problem['c'])
    def reserve_var(t, which):          # which: 0 = sodium, 1 = iron-air
        return n_old + t * 2 + which

    n_new = n_old + T * 2
    rows, cols, data, rhs = [], [], [], []
    row = 0
    for t in range(T):
        nar, fer = reserve_var(t, 0), reserve_var(t, 1)

        rows += [row, row]; cols += [hv(t, 'nd'), nar]; data += [1.0, 1.0]
        rhs.append(na_power_mw); row += 1
        rows += [row, row]; cols += [nar, hv(t, 'nsoc')]; data += [1.0, -1.0]
        rhs.append(0.0); row += 1

        rows += [row, row]; cols += [hv(t, 'fd'), fer]; data += [1.0, 1.0]
        rhs.append(fe_power_mw); row += 1
        rows += [row, row]; cols += [fer, hv(t, 'fsoc')]; data += [1.0, -1.0]
        rhs.append(0.0); row += 1

        # Margin, in <= form:  -na_reserve - fe_reserve <= firm[t] - (1 + irm) * demand[t]
        # Everything on the right is FIXED in this scenario -- no build variables appear, which is
        # what makes Scenario 2's version simple.
        firm = (nuclear[t] + gas_ceiling_mw + assumptions.CVOW_MW * wind_cf[t]
                + exist_solar[t] + vcea_solar_mw * solar_cf[t])
        rows += [row, row]; cols += [nar, fer]; data += [-1.0, -1.0]
        rhs.append(firm - (1.0 + irm) * demand[t]); row += 1

    A_new = sparse.coo_matrix((data, (rows, cols)), shape=(row, n_new)).tocsr()
    pad_ub = sparse.csr_matrix((problem['A_ub'].shape[0], T * 2))
    pad_eq = sparse.csr_matrix((problem['A_eq'].shape[0], T * 2))

    out = dict(problem)
    out['c'] = np.concatenate([problem['c'], np.zeros(T * 2)])
    out['A_ub'] = sparse.vstack(
        [sparse.hstack([problem['A_ub'], pad_ub], format='csr'), A_new], format='csr')
    out['b_ub'] = np.concatenate([problem['b_ub'], rhs])
    out['A_eq'] = sparse.hstack([problem['A_eq'], pad_eq], format='csr')
    out['bounds'] = list(problem['bounds']) + [(0, None)] * (T * 2)
    out['reserve_var_base_index'] = n_old
    out['reserve_irm'] = irm
    return out


def margin_shortfall_hours(problem, x, nuclear, wind_cf, exist_solar, solar_cf, vcea_solar_mw,
                           na_power_mw, fe_power_mw, gas_ceiling_mw, demand, irm=0.177):
    """Hours where available capacity falls short of (1 + irm) x demand, given a solved dispatch.

    A READ-ONLY CROSS-CHECK (Rule 4), not a substitute for the constraint. Run against a solve that
    had the constraint applied it should return zero; against one that did not, it reports how far
    short the unconstrained dispatch actually was. Storage contributes min(rated_power, soc[t]) --
    the same "actually available" standard, not rated power assumed full.
    """
    IDX = problem['IDX']
    _, NPH = problem['hv_params']
    short = []
    for t in range(len(demand)):
        nsoc = x[t * NPH + IDX['nsoc']]
        fsoc = x[t * NPH + IDX['fsoc']]
        avail = (nuclear[t] + gas_ceiling_mw + assumptions.CVOW_MW * wind_cf[t] + exist_solar[t]
                 + vcea_solar_mw * solar_cf[t]
                 + min(na_power_mw, nsoc) + min(fe_power_mw, fsoc))
        need = (1.0 + irm) * demand[t]
        if avail < need:
            short.append((t, need - avail))
    return short
