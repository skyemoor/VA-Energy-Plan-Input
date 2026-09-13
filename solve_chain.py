#!/usr/bin/env python3
"""
solve_chain.py

Solves all four checkpoints in sequence, chaining each build forward as the next one's floor.

    python3 solve_chain.py --scenario 3 --merit-order

WHY THIS EXISTS -- and what solve_checkpoint.py cannot do

`solve_checkpoint.py` solves ONE checkpoint with `prior_result = None`, so `_prior_kwargs()`
returns all zeros and the checkpoint builds its entire fleet from scratch in that year. That is not
the scenario. The scenarios are cumulative: 2030's build is a floor under 2035's, aged forward by
`solar_degradation_factor`, and so on to 2045.

An unlinked 2045 solve is a different and easier problem -- free to build less, because nothing
carries over -- and `_verify_monotonicity()` silently passes, because there is no prior to compare
against.

IT ALSO USES THE RESERVE-MARGIN VARIANT. `Scenario3Solver` does not include `ReserveMarginMixin`;
`Scenario3WithReserveMargin` does. A solve through the plain class carries NO reserve margin, which
is the one adequacy constraint this project does model. Both gaps were found in an audit on
2026-09-12, after a full 2045 run had already been made and analysed through the unlinked,
unreserved path.

THIS IS A MYOPIC PATHWAY, AND THAT IS A CHOICE. Each checkpoint minimises cost for its own year:
2030 solves against gas_target_share = 0.59 and has no knowledge that 2045 requires zero gas. In
the literature's taxonomy this is Case 3a -- myopic foresight with goals imposed exogenously via an
annual trajectory. The alternative, solving 2045 first as a target, is Case 1 (snapshot year).

The literature consistently finds myopia costs more: 23% higher cumulative net present cost in one
European study, 14-61% in a sector-coupled review. But it also finds that intertemporal and myopic
models reach a SIMILAR FINAL SYSTEM while differing in pathway and cumulative cost -- so the 2045
build may come out close either way.

See docs/methodology/Experiment_Pathway_Foresight.md. The comparison is an open experiment, not a
settled question, and the whitepaper should state which pathway it prices.

COST: four checkpoints, each up to four LP solves plus a dual extraction. Expect 45-60 minutes.
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

CHECKPOINTS = (2030, 2035, 2040, 2045)

#: Reserve-margin variants where they exist. Using the plain class silently drops the IRM
#: constraint, which is how a full 2045 run was made without one.
SCENARIOS = {
    '1': cs.Scenario1WithReserveMargin,
    '1B': cs.Scenario1BSolver,
    '2': cs.Scenario2Solver,
    '3': cs.Scenario3WithReserveMargin,
}
NEEDS_DISTRIBUTED = {'3'}


def load_year(year, needs_distributed):
    missing = []
    weather = paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz')
    if not os.path.exists(weather):
        missing.append(f'{weather}  (weather year)')
    demand_path = paths.intermediate(f'demand_{year}fy_va_only.npy')
    if not os.path.exists(demand_path):
        missing.append(f'{demand_path}  -- rebuild: python3 run_all.py --only demand')
    dist = {}
    if needs_distributed:
        for name in ('dist_solar_cf_designyear.npy', f'dist_exog_price_{year}.npy'):
            p = paths.intermediate(name)
            if not os.path.exists(p):
                missing.append(f'{p}  -- rebuild: python3 run_all.py --only scenario3_inputs')
            else:
                dist[name] = np.load(p)
    if missing:
        raise SystemExit('Missing inputs:\n  ' + '\n  '.join(missing))
    w = np.load(weather)
    return w, np.load(demand_path), dist


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--scenario', default='3', choices=sorted(SCENARIOS))
    ap.add_argument('--merit-order', action='store_true')
    ap.add_argument('--capacity-basis', default='net_summer',
                    choices=['nameplate', 'net_summer', 'net_winter'])
    ap.add_argument('--irm', type=float, default=0.177, help='PJM installed reserve margin')
    ap.add_argument('--out', default='results')
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()

    needs_dist = args.scenario in NEEDS_DISTRIBUTED
    cls = SCENARIOS[args.scenario]
    stack = GasMeritOrder(capacity_basis=args.capacity_basis) if args.merit_order else None

    print(f'Scenario {args.scenario} chain: {" -> ".join(str(y) for y in CHECKPOINTS)}')
    print(f'Solver class: {cls.__name__}'
          + ('  (reserve margin applied)' if 'ReserveMargin' in cls.__name__
             else '  WARNING: no reserve-margin variant for this scenario'))
    print(f'Merit order: {"ON (" + args.capacity_basis + ")" if stack else "OFF"}')
    print('Each checkpoint chains forward as the next one\'s floor. Expect 45-60 minutes.\n')

    prior = None
    chain = []
    t_start = time.time()

    for year in CHECKPOINTS:
        w, demand, dist = load_year(year, needs_dist)
        exist_solar = lp.exist_solar_mw(year) * w['solar']
        kwargs = dict(year=year, gas_target_share=drv.gas_target_share(year), demand=demand,
                      exist_solar=exist_solar, solar_cf=w['solar'], wind_cf=w['wind'],
                      nuclear=w['nuclear'])
        if needs_dist:
            kwargs['distributed_solar_cf'] = dist['dist_solar_cf_designyear.npy']
            kwargs['distributed_exogenous_price_mwh'] = dist[f'dist_exog_price_{year}.npy']

        solver = cls(**kwargs)
        solver.prior_result = prior            # THE CHAIN. None for 2030, then each prior result.
        if stack is not None:
            solver.gas_merit_order = stack

        pk = solver._prior_kwargs()
        print(f'[{year}] prior solar floor {pk["prior_solar_mw"]:>12,.1f} MW   '
              f'NA power {pk["prior_na_power_mw"]:>10,.1f} MW')

        t0 = time.time()
        if hasattr(solver, 'solve_with_reserve_margin'):
            result = solver.solve_with_reserve_margin(IRM=args.irm)
        else:
            result = solver.converge_and_solve()
        elapsed = time.time() - t0

        result = dict(result)
        result['year'] = year                  # _prior_kwargs() reads this off the prior result
        row = {'year': year,
               'solar_mw': float(result.get('S_mw', 0.0)),
               'solar_mw_total': float(result.get('S_mw_total', result.get('S_mw', 0.0))),
               'na_power_mw': float(result.get('PNA_mw', 0.0)),
               'na_energy_mwh': float(result.get('ENA_mwh', 0.0)),
               'ironair_energy_mwh': float(result.get('EFE_mwh', 0.0)),
               'converged_frac': float(getattr(solver, 'converged_frac', 0.0)),
               'elapsed_seconds': round(elapsed, 1)}
        for k in ('dist_S_mw', 'dist_S_mw_total'):
            if k in result:
                row[k] = float(result[k])
        chain.append(row)
        print(f'       solar {row["solar_mw_total"]:>12,.1f} MW   '
              f'NA {row["na_power_mw"]:>10,.1f} MW   FE {row["ironair_energy_mwh"]/1000:>9,.1f} GWh   '
              f'({elapsed/60:.1f} min)\n')
        prior = result

    # Monotonicity across the chain -- the check _verify_monotonicity cannot make when each
    # checkpoint is solved unlinked, because there is no prior to compare against.
    print('Chain monotonicity (each build >= the prior checkpoint):')
    ok = True
    for a, b in zip(chain, chain[1:]):
        for key in ('solar_mw_total', 'na_power_mw', 'na_energy_mwh', 'ironair_energy_mwh'):
            if b[key] < a[key] - 1e-6:
                print(f'  FAIL {a["year"]}->{b["year"]}  {key}: {a[key]:,.1f} -> {b[key]:,.1f}')
                ok = False
    print('  all non-decreasing' if ok else '  MONOTONICITY VIOLATED -- builds shrink across the chain')

    os.makedirs(args.out, exist_ok=True)
    tag = f'{args.scenario}' + ('_merit' if args.merit_order else '_flat')
    summary = {'scenario': args.scenario, 'merit_order': args.merit_order,
               'capacity_basis': args.capacity_basis, 'irm': args.irm,
               'solver_class': cls.__name__, 'reserve_margin_applied': 'ReserveMargin' in cls.__name__,
               'monotonic': ok, 'total_minutes': round((time.time() - t_start) / 60, 1),
               'checkpoints': chain}
    with open(os.path.join(args.out, f'chain_{tag}.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    print(f'\nDone in {summary["total_minutes"]:.1f} min. Wrote results/chain_{tag}.json')
    print('For hourly dispatch and duals at one checkpoint, run solve_checkpoint.py -- but note '
          'it solves UNLINKED,\nso its build will differ from this chain. See its docstring.')


if __name__ == '__main__':
    main()
