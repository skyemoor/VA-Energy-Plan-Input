#!/usr/bin/env python3
"""
run_pathway_comparison.py

Runs both pathways in one call and reports the comparison. Built for an unattended overnight run.

    nohup python3 run_pathway_comparison.py --scenario 3 --merit-order > pathway.log 2>&1 &

WHAT IT RUNS

    A  MYOPIC CHAIN     2030 -> 2035 -> 2040 -> 2045, each carrying the prior build forward as a
                        floor. Case 3a: myopic foresight, goals imposed via an annual trajectory.
    B  TARGET-FIRST     2045 standalone, no prior build. Case 1: snapshot year, no pathway.

Then `PathwayComparison` reports build deltas, the myopia penalty, and whether the chain defers
long-duration storage into the final checkpoint.

See docs/methodology/Experiment_Pathway_Foresight.md for why this is an open question rather than a
settled choice.

BUILT FOR UNATTENDED RUNNING, which drives three design choices:

  RESULTS ARE WRITTEN AFTER EVERY CHECKPOINT, not at the end. A five-checkpoint run that fails on
  the last one should not lose the first four. `results/pathway_progress.json` is rewritten each
  time, so a crashed run leaves everything it completed.

  A FAILED PATHWAY DOES NOT KILL THE OTHER. If the chain fails at 2040, the target-first solve
  still runs and both partial results are reported. Overnight time is expensive to waste.

  EVERY CHECKPOINT IS TIMESTAMPED AND FLUSHED. `print(..., flush=True)` throughout, because a
  buffered log tells you nothing about where an overnight run stalled.

RULE 1: this file is orchestration only. The comparison logic lives in
lp_package/pathway_comparison.py, because a second scenario will need it in the same form.

COST: five full checkpoint solves (four chained plus one standalone), each up to four LP solves.
Expect 60-90 minutes.
"""
import argparse
import json
import os
import sys
import time
import traceback
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lp_package'))

import numpy as np                                                        # noqa: E402

import checkpoint_solver as cs                                            # noqa: E402
import driver as drv                                                      # noqa: E402
import lp_model as lp                                                     # noqa: E402
import paths                                                              # noqa: E402
from gas_merit_order import GasMeritOrder                                 # noqa: E402
from pathway_comparison import PathwayComparison                          # noqa: E402

CHECKPOINTS = (2030, 2035, 2040, 2045)

#: Reserve-margin variants where they exist. Using a plain class silently drops the IRM constraint,
#: which is how a full 2045 run was made without one on 2026-09-12.
SCENARIOS = {'1': cs.Scenario1WithReserveMargin, '1B': cs.Scenario1BSolver,
             '2': cs.Scenario2Solver, '3': cs.Scenario3WithReserveMargin}
NEEDS_DISTRIBUTED = {'3'}


def log(msg):
    print(f'[{datetime.now():%H:%M:%S}] {msg}', flush=True)


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
    return np.load(weather), np.load(demand_path), dist


def solve_one(cls, year, stack, needs_dist, prior_result, irm):
    """One checkpoint. `prior_result=None` gives an unlinked solve; anything else chains."""
    w, demand, dist = load_year(year, needs_dist)
    exist_solar = lp.exist_solar_mw(year) * w['solar']
    kwargs = dict(year=year, gas_target_share=drv.gas_target_share(year), demand=demand,
                  exist_solar=exist_solar, solar_cf=w['solar'], wind_cf=w['wind'],
                  nuclear=w['nuclear'])
    if needs_dist:
        kwargs['distributed_solar_cf'] = dist['dist_solar_cf_designyear.npy']
        kwargs['distributed_exogenous_price_mwh'] = dist[f'dist_exog_price_{year}.npy']

    solver = cls(**kwargs)
    solver.prior_result = prior_result
    if stack is not None:
        solver.gas_merit_order = stack

    t0 = time.time()
    if hasattr(solver, 'solve_with_reserve_margin'):
        result = solver.solve_with_reserve_margin(IRM=irm)
    else:
        result = solver.converge_and_solve()
    result = dict(result)
    result['year'] = year                       # _prior_kwargs() reads this off the prior result

    row = {'year': year, 'elapsed_seconds': round(time.time() - t0, 1),
           'converged_frac': float(getattr(solver, 'converged_frac', 0.0))}
    for out_key, res_key in (('solar_mw_total', 'S_mw_total'), ('solar_mw', 'S_mw'),
                             ('na_power_mw', 'PNA_mw'), ('na_energy_mwh', 'ENA_mwh'),
                             ('ironair_energy_mwh', 'EFE_mwh'),
                             ('dist_solar_mw_total', 'dist_S_mw_total'),
                             ('annual_cost_usd', 'obj')):
        if res_key in result:
            row[out_key] = float(result[res_key])
    row.setdefault('solar_mw_total', row.get('solar_mw', 0.0))
    return row, result


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--scenario', default='3', choices=sorted(SCENARIOS))
    ap.add_argument('--merit-order', action='store_true')
    ap.add_argument('--capacity-basis', default='net_summer',
                    choices=['nameplate', 'net_summer', 'net_winter'])
    ap.add_argument('--irm', type=float, default=0.177)
    ap.add_argument('--out', default='results')
    args = ap.parse_args()

    needs_dist = args.scenario in NEEDS_DISTRIBUTED
    cls = SCENARIOS[args.scenario]
    stack = GasMeritOrder(capacity_basis=args.capacity_basis) if args.merit_order else None
    os.makedirs(args.out, exist_ok=True)
    progress_path = os.path.join(args.out, f'pathway_progress_{args.scenario}.json')

    log(f'Pathway comparison, scenario {args.scenario}')
    log(f'  solver: {cls.__name__}'
        + ('  (reserve margin applied)' if 'ReserveMargin' in cls.__name__
           else '  WARNING: no reserve-margin variant exists for this scenario'))
    log(f'  merit order: {"ON (" + args.capacity_basis + ")" if stack else "OFF"}')
    log('  A = myopic chain 2030->2045   B = target-first 2045 standalone')
    log('  Five checkpoint solves total; expect 60-90 minutes.')

    state = {'scenario': args.scenario, 'merit_order': args.merit_order,
             'capacity_basis': args.capacity_basis, 'irm': args.irm,
             'solver_class': cls.__name__,
             'reserve_margin_applied': 'ReserveMargin' in cls.__name__,
             'started': datetime.now().isoformat(timespec='seconds'),
             'chain': [], 'target_first': None, 'errors': []}

    def save():
        with open(progress_path, 'w') as f:
            json.dump(state, f, indent=2)

    # -- A: myopic chain ---------------------------------------------------
    log('')
    log('=== A: MYOPIC CHAIN ===')
    prior = None
    for year in CHECKPOINTS:
        try:
            row, result = solve_one(cls, year, stack, needs_dist, prior, args.irm)
            state['chain'].append(row)
            save()                                    # after EVERY checkpoint, not at the end
            log(f'  {year}: solar {row["solar_mw_total"]:>12,.1f} MW  '
                f'NA {row.get("na_power_mw", 0):>10,.1f} MW  '
                f'FE {row.get("ironair_energy_mwh", 0)/1000:>9,.1f} GWh  '
                f'({row["elapsed_seconds"]/60:.1f} min)')
            prior = result
        except Exception as exc:                                          # noqa: BLE001
            state['errors'].append({'pathway': 'chain', 'year': year,
                                    'error': f'{type(exc).__name__}: {exc}',
                                    'traceback': traceback.format_exc()})
            save()
            log(f'  {year}: FAILED -- {type(exc).__name__}: {exc}')
            log('  Chain cannot continue past a failed checkpoint (later ones depend on it).')
            break

    # -- B: target-first ---------------------------------------------------
    # Runs even if the chain failed. Overnight time is too expensive to waste on one bad branch.
    log('')
    log('=== B: TARGET-FIRST (2045 standalone) ===')
    try:
        row, _ = solve_one(cls, 2045, stack, needs_dist, None, args.irm)
        state['target_first'] = row
        save()
        log(f'  2045: solar {row["solar_mw_total"]:>12,.1f} MW  '
            f'NA {row.get("na_power_mw", 0):>10,.1f} MW  '
            f'FE {row.get("ironair_energy_mwh", 0)/1000:>9,.1f} GWh  '
            f'({row["elapsed_seconds"]/60:.1f} min)')
    except Exception as exc:                                              # noqa: BLE001
        state['errors'].append({'pathway': 'target_first', 'year': 2045,
                                'error': f'{type(exc).__name__}: {exc}',
                                'traceback': traceback.format_exc()})
        save()
        log(f'  2045: FAILED -- {type(exc).__name__}: {exc}')

    # -- comparison --------------------------------------------------------
    log('')
    log('=== COMPARISON ===')
    if state['target_first'] is None or not any(c['year'] == 2045 for c in state['chain']):
        log('  Cannot compare: one pathway did not reach 2045. Partial results are in')
        log(f'  {progress_path} and the errors are recorded there.')
    else:
        cmp = PathwayComparison(state['chain'], state['target_first'])
        s = cmp.summary()
        log(f'  final systems agree: {s["final_systems_agree"]}')
        for d in s['build_deltas']:
            frac = 'n/a' if d['fraction'] is None else f'{d["fraction"]:+.1%}'
            flag = '  <-- MATERIAL' if d['material'] else ''
            log(f'    {d["name"]:<22}myopic {d["myopic"]:>13,.1f}   '
                f'target-first {d["target_first"]:>13,.1f}   {frac:>8}{flag}')
        log(f'  {s["penalty_reading"]}')
        ia = s['iron_air']
        log(f'  iron-air deferral: {ia["deferred"]}')
        log(f'    {ia["note"]}')
        state['comparison'] = s
        save()

    state['finished'] = datetime.now().isoformat(timespec='seconds')
    save()
    final = os.path.join(args.out, f'pathway_comparison_{args.scenario}.json')
    os.replace(progress_path, final)
    log('')
    log(f'Wrote {final}')
    if state['errors']:
        log(f'{len(state["errors"])} checkpoint(s) FAILED -- see the errors array in that file.')


if __name__ == '__main__':
    main()
