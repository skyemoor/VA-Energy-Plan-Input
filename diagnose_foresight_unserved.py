#!/usr/bin/env python3
"""
diagnose_foresight_unserved.py

Finds WHERE the perfect-foresight assembly starts producing unserved energy, by solving it at
2, 3 and 4 periods and reporting the distribution per period.

    python3 diagnose_foresight_unserved.py

WHY THIS EXISTS. The four-period assembly reports unserved energy at 2030 that the myopic solve
does not produce, and three successive guesses at the cause each moved the number a little without
removing it -- 41,718 -> 39,682 -> 38,965 MWh. A number that shrinks under unrelated changes is a
sign of guessing, not of progress.

WHAT IS ALREADY RULED OUT, measured at TWO periods (2030 + 2035), which gives EXACTLY 0.0 MWh:

    the block-diagonal assembly        not the cause
    the 24 linking rows                not the cause
    the salvage credit                 not the cause
    the build_only problem itself      not the cause -- a single period solves clean

So the cause appears only at three or more periods. The candidates this distinguishes:

    SCALE. 876,032 variables against 438,016. If unserved is spread thinly across many hours at
    small magnitudes, it is solver feasibility tolerance rather than a modelling error, and the
    verification threshold -- currently 1e-3 MWh against an annual demand of 117,899,892 MWh, or
    one part in 10^11 -- is simply tighter than any LP guarantees.

    STRUCTURE. If unserved is concentrated in a few hours at large magnitudes, something in the
    2040 or 2045 block is making 2030 infeasible-but-for-unserved through the linking.

Report the output; do not act on it until the two are told apart.
"""
import sys
import time

sys.path.insert(0, 'lp_package')

import numpy as np
from scipy.optimize import linprog

import checkpoint_solver as cs
import demand_basis as db
import driver as drv
import lp_model as lp
import multi_period_problem as mp
import paths

ALL = (2030, 2035, 2040, 2045)


def build(year, weather):
    d = db.VirginiaOnlyLoad(year).hourly_mw()
    s = cs.Scenario1WithReserveMargin(
        year=year, gas_target_share=drv.gas_target_share(year), demand=d,
        exist_solar=lp.exist_solar_mw(year) * weather['solar'], solar_cf=weather['solar'],
        wind_cf=weather['wind'], nuclear=weather['nuclear'])
    drv.set_year_capex(year)
    hook = s._chain_hooks(s._post_build_hook(), s._all_hours_reserve_hook(0.177))
    p = drv.run_solve(year, drv.gas_target_share(year), d,
                      lp.exist_solar_mw(year) * weather['solar'], weather['solar'],
                      weather['wind'], weather['nuclear'], capacity_cap_mw=s.apply_gas_cap(),
                      build_only=True, post_build_hook=hook,
                      slcr_curt_cost=s.curtailment_cost_mwh())
    return p, d


def main():
    w = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    cache = {y: build(y, w) for y in ALL}

    for n in (2, 3, 4):
        years = ALL[:n]
        probs = [cache[y][0] for y in years]
        a = mp.assemble(probs, years)
        print(f'\n=== {n} periods: {years} -- {len(a["c"]):,} vars ===', flush=True)
        t0 = time.time()
        r = linprog(a['c'], A_ub=a['A_ub'], b_ub=a['b_ub'], A_eq=a['A_eq'], b_eq=a['b_eq'],
                    bounds=a['bounds'], method='highs')
        print(f'  status {r.status} in {(time.time() - t0) / 60:.1f} min', flush=True)
        if r.x is None:
            continue
        for i, y in enumerate(years):
            nb, nph = a['hv_params_by_period'][i]
            off = a['offsets'][i]
            T = cache[y][1].shape[0]
            u = np.array([r.x[off + nb + t * nph + a['IDX']['unserved']] for t in range(T)])
            total = u.sum()
            if total <= 1e-9:
                print(f'  {y}: clean', flush=True)
                continue
            # THE DISTINCTION THAT MATTERS: spread thin is tolerance, concentrated is structural.
            print(f'  {y}: {total:,.1f} MWh over {int((u > 1e-9).sum()):,} hours   '
                  f'max {u.max():,.2f} MW   '
                  f'>1 MW in {int((u > 1).sum()):,} h   >100 MW in {int((u > 100).sum()):,} h',
                  flush=True)
            share = total / cache[y][1].sum()
            print(f'       = {share:.3e} of that year\'s demand  '
                  f'({"looks like solver tolerance" if u.max() < 1.0 else "CONCENTRATED -- structural"})',
                  flush=True)


if __name__ == '__main__':
    main()
