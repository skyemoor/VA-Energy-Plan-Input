#!/usr/bin/env python3
"""
run_scenario1.py

Solves Scenario 1 across its checkpoints and reports the build, cost, gas share and social cost.

    python3 run_scenario1.py

The myopic chain on its own, separated from run_foresight_comparison.py so the two halves can be
run independently -- the myopic side takes ~19 minutes and does not need repeating every time the
perfect-foresight solve is retried.

SCENARIO 1 is the 100% compliance endpoint: 100% clean generation by 2045, firmed solar colocated
with storage, no standalone storage. Four checkpoints, each carrying the prior build forward as a
floor. Scenario 1B, which diverges only at 2045, needs a fifth checkpoint at 2044 and has its own
runner.

WHAT THE OUTPUT SHOWS

The build trajectory is the finding, not just the endpoint. Measured 2026-09-14: 8,702 MW at 2030
rising to 156,737 MW at 2045, with 59% of the total arriving in the FINAL checkpoint -- more solar
built in 2045 alone than in the fifteen years before it combined. That is the delay-then-overbuild
pattern the myopic-foresight literature describes: each checkpoint builds only what its own gas
target requires, so 2030 at 59% gas allowed builds almost nothing and the 2045 zero-gas requirement
lands all at once.

Whether 92,544 MW in a five-year window is physically deliverable -- roughly 18.5 GW/year of solar
in one state -- is a question this model does not ask.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lp_package'))

import numpy as np                                                        # noqa: E402

import assumptions                                                        # noqa: E402
import checkpoint_solver as cs                                            # noqa: E402
import compute_tier123_final as tier123                                   # noqa: E402
import demand_basis                                                       # noqa: E402
import driver as drv                                                      # noqa: E402
import lp_model as lp                                                     # noqa: E402
import paths                                                              # noqa: E402
from levelised_cost import build_salvage_credit                           # noqa: E402

CHECKPOINTS = (2030, 2035, 2040, 2045)


def solve_checkpoint(year, weather, prior, irm):
    demand = demand_basis.VirginiaOnlyLoad(year).hourly_mw()
    solver = cs.Scenario1WithReserveMargin(
        year=year, gas_target_share=drv.gas_target_share(year), demand=demand,
        exist_solar=lp.exist_solar_mw(year) * weather['solar'], solar_cf=weather['solar'],
        wind_cf=weather['wind'], nuclear=weather['nuclear'])
    solver.prior_result = prior
    t0 = time.time()
    result = dict(solver.solve_with_reserve_margin(IRM=irm))
    result['year'] = year

    g_hourly = None
    gas_mwh = float(result.get('gas_mwh', 0.0))
    if 'hourly' in result and 'g' in result['hourly']:
        g_hourly = np.asarray(result['hourly']['g'], dtype=float)
        if not gas_mwh:
            gas_mwh = float(g_hourly.sum())

    # Tier 1 and 2 on the same per-year basis as the Scenario 2 and 1B runners, from THIS year's
    # actual hourly dispatch -- the NOx blend depends on the existing/new MW split at this level.
    tiers = {}
    if g_hourly is not None:
        t = tier123.compute_year(year, g_hourly, drv.schedule_b_baseline_mw(year),
                                 assumptions.GAS_NEW_BUILD_POOL_MW)
        tiers = {'virginia_scc_usd': float(t['social_cost_of_carbon']),
                 'social_cost_ghg_usd': float(t['social_cost_of_ghg']),
                 'health_impacts_usd': float(t['health_impacts_cost'])}

    # Salvage across ALL FOUR build assets, on an annuity basis, from the shared implementation.
    #
    # THIS CREDITED SOLAR ONLY until 2026-09-14, while run_foresight_comparison credited four build
    # variables. A comparison drawing its myopic side from a saved result here would have weighed a
    # solar-only salvage against a four-asset one -- worth 2.4x at 2030 ($0.326B against $0.779B),
    # biasing the myopia penalty by the whole difference. One implementation now, so the two cannot
    # diverge again.
    drv.set_year_capex(year)
    salvage, salvage_by_asset = build_salvage_credit(result, year, CHECKPOINTS[-1])

    row = {
        'year': year,
        'demand_mwh': float(demand.sum()),
        'gas_mwh': gas_mwh,
        'gas_share': gas_mwh / float(demand.sum()) if demand.sum() else 0.0,
        'gas_target_share': float(solver.gas_target_share),
        'gas_cap_mw': float(solver.apply_gas_cap()),
        'solar_mw_total': float(result.get('S_mw_total', result.get('S_mw', 0.0))),
        'solar_mw_new': float(result.get('S_mw', 0.0)),
        'na_power_mw': float(result.get('PNA_mw', 0.0)),
        'na_energy_mwh': float(result.get('ENA_mwh', 0.0)),
        'fe_energy_mwh': float(result.get('EFE_mwh', 0.0)),
        'curtailment_mwh': float(result.get('curt_mwh', 0.0)),
        'obj_usd': float(result['obj']),
        'salvage_usd': float(salvage),
        'salvage_by_asset_usd': {k: float(v) for k, v in salvage_by_asset.items()},
        'converged': bool(result.get('converged', False)),
        'convergence_gap': float(result.get('convergence_gap', 0.0)),
        'unserved_mwh': float(result.get('unserved_mwh', 0.0)),
        'seconds': round(time.time() - t0, 1),
    }
    row.update(tiers)
    return row, result


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--irm', type=float, default=0.177)
    ap.add_argument('--out', default='results')
    args = ap.parse_args()

    weather = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    print('Scenario 1: ' + ' -> '.join(str(y) for y in CHECKPOINTS), flush=True)
    print(f'\n{"year":<6}{"clean":>8}{"solar total":>13}{"new":>12}{"curt TWh":>10}'
          f'{"obj $B":>9}{"salvage $B":>12}', flush=True)

    prior, rows = None, []
    t_start = time.time()
    for year in CHECKPOINTS:
        row, result = solve_checkpoint(year, weather, prior, args.irm)
        rows.append(row)
        print(f'{year:<6}{1 - row["gas_share"]:>7.1%}{row["solar_mw_total"]:>13,.0f}'
              f'{row["solar_mw_new"]:>12,.0f}{row["curtailment_mwh"]/1e6:>10.1f}'
              f'{row["obj_usd"]/1e9:>9.2f}{row["salvage_usd"]/1e9:>12.2f}', flush=True)
        prior = result

    # THE BUILD TRAJECTORY IS THE FINDING. Each checkpoint builds only what its own gas target
    # requires, so the increments grow sharply toward the end.
    print('\nbuild trajectory:', flush=True)
    previous = 0.0
    for row in rows:
        increment = row['solar_mw_total'] - previous
        print(f'  {row["year"]}  cumulative {row["solar_mw_total"]:>11,.0f} MW   '
              f'increment {increment:>10,.0f} MW   '
              f'{increment / rows[-1]["solar_mw_total"]:>6.1%} of total', flush=True)
        previous = row['solar_mw_total']
    final_increment = rows[-1]['solar_mw_total'] - rows[-2]['solar_mw_total']
    if final_increment > rows[-2]['solar_mw_total']:
        print(f'  MORE IS BUILT IN {rows[-1]["year"]} ALONE ({final_increment:,.0f} MW) THAN IN '
              f'EVERY YEAR BEFORE IT COMBINED ({rows[-2]["solar_mw_total"]:,.0f} MW).', flush=True)
        print('  That is the delay-then-overbuild pattern: each checkpoint builds only what its '
              'own gas target needs.', flush=True)

    unconverged = [r['year'] for r in rows if not r['converged']]
    if unconverged:
        print(f'\nNOT CONVERGED at {unconverged} -- those builds miss their own gas target.',
              flush=True)

    final = rows[-1]
    if 'social_cost_ghg_usd' in final:
        print(f'\nsocial cost at {final["year"]}: SC-GHG '
              f'${final["social_cost_ghg_usd"]/1e9:.3f}B   Virginia SCC '
              f'${final["virginia_scc_usd"]/1e9:.3f}B   health '
              f'${final["health_impacts_usd"]/1e9:.3f}B', flush=True)

    print(f'\nDone in {(time.time() - t_start)/60:.1f} min', flush=True)
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, 'scenario1.json')
    with open(path, 'w') as f:
        json.dump({'checkpoints': rows, 'irm': args.irm}, f, indent=2)
    print(f'Wrote {path}  -- run_foresight_comparison.py --myopic-from {path} reuses it.',
          flush=True)


if __name__ == '__main__':
    main()
