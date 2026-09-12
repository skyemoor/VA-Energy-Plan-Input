#!/usr/bin/env python3
"""
solve_checkpoint.py

Solves one scenario checkpoint and saves the hourly supply-demand shadow prices.

WHY THIS EXISTS. The 2045 measurement -- does the hourly dual still have structure once the gas
merit order is active, in a year with ~42% surplus hours -- could not be completed in the session
environment. A checkpoint is UP TO FOUR LP SOLVES (converge_frac iterates up to three times before
the final solve), and at 2030 those ran 77-137 s each. This script exists so the solve can be run
where there is no per-command timeout.

    python3 solve_checkpoint.py --year 2045 --scenario 3 --merit-order

Outputs land in results/ and are what the analysis needs:
    duals_{scenario}_{year}.npy         8,760 hourly shadow prices, $/MWh
    solve_{scenario}_{year}.json        build MW, converged frac, dual summary

FIRST RUN takes a while and prints per-iteration progress. Nothing is wrong if iter0 shows a large
gap -- converge_frac is searching for the gas fraction that hits the target share, and the gap
shrinks each iteration.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lp_package'))

import numpy as np                                                        # noqa: E402

import checkpoint_solver as cs                                            # noqa: E402
import driver as drv                                                      # noqa: E402
import lp_model as lp                                                     # noqa: E402
import paths                                                              # noqa: E402
from gas_merit_order import GasMeritOrder                                 # noqa: E402

SCENARIOS = {'1': cs.Scenario1Solver, '1B': cs.Scenario1BSolver,
             '2': cs.Scenario2Solver, '3': cs.Scenario3Solver}


def load_inputs(year, needs_distributed):
    """Loads what the solve needs, failing with the rebuild command rather than a KeyError."""
    missing = []
    weather = paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz')
    if not os.path.exists(weather):
        missing.append(f'{weather}  (weather year)')
    demand_path = paths.intermediate(f'demand_{year}fy_va_only.npy')
    if not os.path.exists(demand_path):
        missing.append(f'{demand_path}  -- rebuild: python3 run_all.py --only demand')
    dist = {}
    if needs_distributed:
        for name, hint in ((f'dist_solar_cf_designyear.npy', 'scenario3_inputs'),
                           (f'dist_exog_price_{year}.npy', 'scenario3_inputs')):
            p = paths.intermediate(name)
            if not os.path.exists(p):
                missing.append(f'{p}  -- rebuild: python3 run_all.py --only {hint}')
            else:
                dist[name] = np.load(p)
    if missing:
        raise SystemExit('Missing inputs:\n  ' + '\n  '.join(missing))

    w = np.load(weather)
    return w, np.load(demand_path), dist


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--year', type=int, required=True, choices=[2030, 2035, 2040, 2045])
    ap.add_argument('--scenario', default='3', choices=sorted(SCENARIOS))
    ap.add_argument('--merit-order', action='store_true',
                    help='dispatch gas against the sourced merit order rather than one flat price')
    ap.add_argument('--capacity-basis', default='net_summer',
                    choices=['nameplate', 'net_summer', 'net_winter'],
                    help='rating basis for gas capacity (default net_summer; see '
                         'assumptions.GAS_SEASONAL_BASIS_NOTE -- net winter is 11.4%% higher and '
                         'the DOM zone now peaks in winter)')
    ap.add_argument('--out', default='results')
    args = ap.parse_args()

    needs_dist = args.scenario == '3'
    w, demand, dist = load_inputs(args.year, needs_dist)
    exist_solar = lp.exist_solar_mw(args.year) * w['solar']

    kwargs = dict(year=args.year, gas_target_share=drv.gas_target_share(args.year),
                  demand=demand, exist_solar=exist_solar, solar_cf=w['solar'],
                  wind_cf=w['wind'], nuclear=w['nuclear'])
    if needs_dist:
        kwargs['distributed_solar_cf'] = dist['dist_solar_cf_designyear.npy']
        kwargs['distributed_exogenous_price_mwh'] = dist[f'dist_exog_price_{args.year}.npy']

    solver = SCENARIOS[args.scenario](**kwargs)
    if args.merit_order:
        solver.gas_merit_order = GasMeritOrder(capacity_basis=args.capacity_basis)
        stack = solver.gas_merit_order.rungs(args.year)
        print(f'Merit order active ({args.capacity_basis}), {len(stack)} rungs:')
        for r in stack:
            print(f'    {r.name:<14}{r.nameplate_mw:>9,.1f} MW  '
                  f'${r.marginal_cost_mwh(args.year):>7.2f}/MWh')
    else:
        print('Merit order OFF -- one flat gas price (simple-cycle heat rate).')

    print(f'\nSolving scenario {args.scenario}, {args.year}. '
          'Up to four LP solves; expect several minutes per solve.\n')
    t0 = time.time()
    result = solver.converge_and_solve()
    elapsed = time.time() - t0

    os.makedirs(args.out, exist_ok=True)
    tag = f'{args.scenario}_{args.year}' + ('_merit' if args.merit_order else '_flat')

    summary = {'scenario': args.scenario, 'year': args.year,
               'merit_order': args.merit_order, 'capacity_basis': args.capacity_basis,
               'converged_frac': float(solver.converged_frac),
               'elapsed_seconds': round(elapsed, 1),
               'solar_mw': float(result.get('S_mw', 0.0)),
               'solar_mw_total': float(result.get('S_mw_total', 0.0))}
    for k in ('dist_S_mw', 'dist_S_mw_total', 'PNA_mw', 'ENA_mwh', 'EFE_mwh'):
        if k in result:
            summary[k] = float(result[k])

    # The duals are the point of the exercise. run_solve does not return the raw result, so they
    # are re-derived by one extra solve at the converged frac rather than by changing run_solve's
    # return contract, which every existing caller depends on.
    print('\nRe-solving at the converged fraction to extract shadow prices...')
    extra = dict(kwargs)
    for key in ('year', 'gas_target_share', 'demand', 'exist_solar', 'solar_cf', 'wind_cf',
                'nuclear', 'distributed_solar_cf', 'distributed_exogenous_price_mwh'):
        extra.pop(key, None)
    raw = drv.run_solve(
        args.year, solver.converged_frac, demand, exist_solar, w['solar'], w['wind'], w['nuclear'],
        return_raw_result=True,
        enable_distributed_segment=needs_dist,
        distributed_solar_cf=dist.get('dist_solar_cf_designyear.npy'),
        distributed_exogenous_price_mwh=dist.get(f'dist_exog_price_{args.year}.npy'),
        gas_merit_order=solver.gas_merit_order if args.merit_order else None,
        gas_merit_order_year=args.year if args.merit_order else None)
    res = raw['res']
    if getattr(res, 'eqlin', None) is not None:
        duals = np.asarray(res.eqlin.marginals, dtype=float)[:8760]
        np.save(os.path.join(args.out, f'duals_{tag}.npy'), duals)
        summary['dual_unique_values'] = int(len(np.unique(np.round(duals, 3))))
        summary['dual_min_mwh'] = float(duals.min())
        summary['dual_max_mwh'] = float(duals.max())
        summary['dual_std_mwh'] = float(duals.std())
        print(f'  duals: {summary["dual_unique_values"]} unique values, '
              f'${duals.min():,.2f} to ${duals.max():,.2f}, std {duals.std():,.2f}')
        if summary['dual_unique_values'] <= 1:
            print('  WARNING: the dual is FLAT. With the merit order active that should not '
                  'happen -- see docs/MODEL_WIDE_FINDINGS.md section 1.')
    else:
        print('  no equality marginals returned; duals not saved')

    with open(os.path.join(args.out, f'solve_{tag}.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    print(f'\nDone in {elapsed/60:.1f} min. Wrote results/solve_{tag}.json'
          + (f' and results/duals_{tag}.npy' if 'dual_unique_values' in summary else ''))


if __name__ == '__main__':
    main()
