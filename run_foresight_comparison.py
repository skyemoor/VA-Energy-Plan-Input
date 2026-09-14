#!/usr/bin/env python3
"""
run_foresight_comparison.py

Solves the same scenario two ways and reports the myopia penalty.

    python3 run_foresight_comparison.py --scenario 1

    MYOPIC (Case 3a)            four checkpoints solved in sequence, each carrying the prior
                                build forward as a floor. Each optimises for its own year and its
                                own gas target, knowing nothing of later ones.

    PERFECT FORESIGHT (Case 2)  all four checkpoints in ONE simultaneous LP, linked by
                                build[a] <= build[a+1]. The optimiser sees every year's
                                constraints at once and chooses the whole trajectory together.

THE COMPARISON IS THE DISCOUNTED TOTAL, not the endpoint build. The literature's own finding is
that "intertemporal and myopic models lead to a SIMILAR FINAL ENERGY SYSTEM. However, the
transformation pathways differ" -- so comparing 2045 builds may show nothing while the pathways
diverge substantially. Myopia penalties reported elsewhere: 23% cumulative NPC (European study),
14% rising to 61% in a sector-coupled review, GBP 100-500bn in UCL's UK work.

SALVAGE VALUE IS APPLIED TO BOTH SIDES, by project decision 2026-09-14. If it were in one and not
the other, the comparison would measure salvage treatment rather than foresight. Under perfect
foresight it sits INSIDE the objective, where it shapes what gets built -- the literature is
explicit that omitting it penalises late-horizon investment. Under the myopic chain the same credit
is applied to the same builds at the same discount, so the two totals are comparable.

WHAT THIS CANNOT SHOW. The myopic side is four checkpoints, not twenty years; both sides use the
same checkpoint set, so the comparison is like-for-like, but neither is an SLCOE over the full
stream. Intermediate years would change both totals in the same direction and are a separate run.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lp_package'))

import numpy as np                                                        # noqa: E402
from scipy.optimize import linprog                                        # noqa: E402

import assumptions                                                        # noqa: E402
import checkpoint_solver as cs                                            # noqa: E402
import driver as drv                                                      # noqa: E402
import lp_model as lp                                                     # noqa: E402
import multi_period_problem as mp                                         # noqa: E402
import paths                                                              # noqa: E402
from levelised_cost import undepreciated_value                            # noqa: E402

CHECKPOINTS = (2030, 2035, 2040, 2045)

SCENARIOS = {'1': cs.Scenario1WithReserveMargin, '3': cs.Scenario3WithReserveMargin}

#: Technical life per build variable position, for the salvage credit. Storage and solar take
#: CRF_LIFE_YEARS; there is no gas build variable, so no CCGT_LIFE_YEARS entry is needed.
_LIFE_BY_BUILD_VAR = [assumptions.CRF_LIFE_YEARS] * 8


def load_year(year, needs_distributed):
    weather = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    demand = np.load(paths.intermediate(f'demand_{year}fy_va_only.npy'))
    dist = {}
    if needs_distributed:
        for name in ('dist_solar_cf_designyear.npy', f'dist_exog_price_{year}.npy'):
            dist[name] = np.load(paths.intermediate(name))
    return weather, demand, dist


def _solver(klass, year, needs_distributed):
    w, demand, dist = load_year(year, needs_distributed)
    kwargs = dict(year=year, gas_target_share=drv.gas_target_share(year), demand=demand,
                  exist_solar=lp.exist_solar_mw(year) * w['solar'], solar_cf=w['solar'],
                  wind_cf=w['wind'], nuclear=w['nuclear'])
    if needs_distributed:
        kwargs['distributed_solar_cf'] = dist['dist_solar_cf_designyear.npy']
        kwargs['distributed_exogenous_price_mwh'] = dist[f'dist_exog_price_{year}.npy']
    return klass(**kwargs), demand, w


def salvage_credit_per_mw(year, capex_by_build_var):
    """Residual value per MW of each build variable, at the 2045 horizon.

    Straight-line on remaining technical life, per the EC's present-value convention and NREL's
    ATB note that "a technical life that is longer than the cost recovery period means residual
    value may be left after costs have been recovered". Nothing here strands: solar and storage
    built at any checkpoint still operate past 2045.
    """
    return [undepreciated_value(capex, year, CHECKPOINTS[-1], life, strands_at_horizon=False)
            for capex, life in zip(capex_by_build_var, _LIFE_BY_BUILD_VAR)]


def _capex_by_build_var(year):
    """Per-MW (or per-MWh) capital cost of each build variable at `year`'s parameters."""
    drv.set_year_capex(year)
    return [lp.SOLAR_CAPEX * 1000, lp.NA_POWER_CAPEX * 1000, lp.NA_ENERGY_CAPEX * 1000,
            lp.FE_ENERGY_CAPEX * 1000, lp.SOLAR_CAPEX * 1000, lp.NA_POWER_CAPEX * 1000,
            lp.NA_ENERGY_CAPEX * 1000, lp.FE_ENERGY_CAPEX * 1000]


def run_myopic(klass, needs_distributed, verbose=True):
    """Four checkpoints in sequence, each carrying the prior build forward."""
    prior, rows = None, []
    for year in CHECKPOINTS:
        solver, demand, _ = _solver(klass, year, needs_distributed)
        solver.prior_result = prior
        t0 = time.time()
        result = solver.solve_with_reserve_margin(IRM=0.177)
        result = dict(result)
        result['year'] = year
        salvage = sum(salvage_credit_per_mw(year, _capex_by_build_var(year))[k]
                      * _build_value(result, k) for k in range(4))
        rows.append({'year': year, 'obj_usd': float(result['obj']),
                     'solar_mw': float(result.get('S_mw_total', result.get('S_mw', 0.0))),
                     'na_power_mw': float(result.get('PNA_mw', 0.0)),
                     'fe_energy_mwh': float(result.get('EFE_mwh', 0.0)),
                     'demand_mwh': float(demand.sum()),
                     'salvage_usd': float(salvage),
                     'seconds': round(time.time() - t0, 1)})
        if verbose:
            r = rows[-1]
            print(f'  {year}  solar {r["solar_mw"]:>11,.0f} MW   obj ${r["obj_usd"]/1e9:>6.2f}B   '
                  f'salvage ${r["salvage_usd"]/1e9:>5.2f}B   ({r["seconds"]/60:.1f} min)', flush=True)
        prior = result
    return rows


def _build_value(result, position):
    """Build variable value by position, from a solved checkpoint result."""
    keys = ['S_mw', 'PNA_mw', 'ENA_mwh', 'EFE_mwh']
    return float(result.get(keys[position], 0.0)) if position < len(keys) else 0.0


def run_perfect_foresight(klass, needs_distributed, verbose=True):
    """All four checkpoints in one simultaneous LP."""
    problems, demands = [], []
    for year in CHECKPOINTS:
        solver, demand, _ = _solver(klass, year, needs_distributed)
        solver.verify_input_data()
        drv.set_year_capex(year)
        prior_kwargs = solver._prior_kwargs()
        dist_kwargs = solver._distributed_kwargs() if hasattr(solver, '_distributed_kwargs') else {}
        w = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
        problem = lp.build_problem(
            w['solar'], w['wind'], w['nuclear'], lp.exist_solar_mw(year) * w['solar'], demand,
            drv.gas_target_share(year), verbose=False, **dist_kwargs)
        # Per-period constraints run BEFORE assembly -- the assembler knows nothing about what
        # they mean. Reserve margin and any scenario bounds apply here.
        hook = solver._chain_hooks(solver._post_build_hook(),
                                   solver._all_hours_reserve_hook(0.177))
        if hook is not None:
            problem = hook(problem)
        problem = drv.apply_slcr_constraint(problem, drv.gas_target_share(year),
                                            curt_cost=solver.curtailment_cost_mwh())
        problems.append(problem)
        demands.append(float(demand.sum()))

    salvage = [sum(salvage_credit_per_mw(y, _capex_by_build_var(y))[:4]) / 4 for y in CHECKPOINTS]
    assembled = mp.assemble(problems, CHECKPOINTS, salvage_usd_by_period=salvage)
    if verbose:
        print(f'  assembled {len(assembled["c"]):,} vars, {assembled["A_ub"].shape[0]:,} ub rows, '
              f'{assembled["link_rows"]} linking rows -- solving', flush=True)
    t0 = time.time()
    res = linprog(assembled['c'], A_ub=assembled['A_ub'], b_ub=assembled['b_ub'],
                  A_eq=assembled['A_eq'], b_eq=assembled['b_eq'],
                  bounds=assembled['bounds'], method='highs')
    if not res.success:
        raise RuntimeError(f'perfect-foresight solve failed: status {res.status}, {res.message}')
    builds = mp.builds_by_period(assembled, res.x)
    if verbose:
        print(f'  solved in {(time.time() - t0)/60:.1f} min, objective '
              f'${res.fun/1e9:,.2f}B (already discounted)', flush=True)
        for y, b in zip(CHECKPOINTS, builds):
            print(f'  {y}  solar {b["utility_solar_mw"]:>11,.0f} MW   '
                  f'NA {b["sodium_ion_power_mw"]:>10,.0f} MW   '
                  f'FE {b["iron_air_energy_mwh"]/1e6:>7.2f} TWh', flush=True)
    return {'objective_usd': float(res.fun), 'builds': builds, 'demands_mwh': demands,
            'seconds': round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--scenario', default='1', choices=sorted(SCENARIOS))
    ap.add_argument('--out', default='results')
    args = ap.parse_args()
    klass = SCENARIOS[args.scenario]
    needs_dist = args.scenario == '3'

    print(f'Foresight comparison, scenario {args.scenario}. '
          'Five solves total; the foresight one is ~4x the size of a checkpoint.', flush=True)
    print('\n=== MYOPIC (Case 3a): four checkpoints in sequence ===', flush=True)
    myopic = run_myopic(klass, needs_dist)

    wacc, base = assumptions.WACC, assumptions.BASE_YEAR
    def df(y):
        return 1.0 / (1.0 + wacc) ** (y - base)
    myopic_pv = sum((r['obj_usd'] - r['salvage_usd']) * df(r['year']) for r in myopic)
    pv_demand = sum(r['demand_mwh'] * df(r['year']) for r in myopic)

    print('\n=== PERFECT FORESIGHT (Case 2): one simultaneous solve ===', flush=True)
    foresight = run_perfect_foresight(klass, needs_dist)

    penalty = (myopic_pv - foresight['objective_usd']) / abs(foresight['objective_usd'])
    print('\n=== COMPARISON ===', flush=True)
    print(f'  myopic PV (net of salvage)   ${myopic_pv/1e9:>9,.2f}B', flush=True)
    print(f'  perfect foresight PV         ${foresight["objective_usd"]/1e9:>9,.2f}B', flush=True)
    print(f'  MYOPIA PENALTY               {penalty:>9.1%}', flush=True)
    print(f'  published range              14%-23% cumulative NPC', flush=True)
    print(f'  per MWh (PV demand {pv_demand/1e6:,.0f} TWh): '
          f'${myopic_pv/pv_demand:.2f} vs ${foresight["objective_usd"]/pv_demand:.2f}', flush=True)
    if penalty < 0:
        print('  NEGATIVE PENALTY -- myopic cheaper than foresight inverts the literature and is '
              'not possible if both solve the same feasible set. Check before reporting.',
              flush=True)

    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, f'foresight_comparison_{args.scenario}.json')
    with open(path, 'w') as f:
        json.dump({'scenario': args.scenario, 'myopic': myopic, 'perfect_foresight': foresight,
                   'myopic_pv_usd': myopic_pv, 'pv_demand_mwh': pv_demand,
                   'myopia_penalty': penalty, 'wacc': wacc, 'base_year': base}, f, indent=2)
    print(f'\nWrote {path}', flush=True)


if __name__ == '__main__':
    main()
