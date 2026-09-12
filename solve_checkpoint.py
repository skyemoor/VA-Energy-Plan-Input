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
    ap.add_argument('--no-hourly', action='store_true',
                    help='skip the hourly dispatch CSV (it is ~1 MB and the default is to write it)')
    ap.add_argument('--verbose', action='store_true',
                    help='print problem size, per-iteration timing, and a dual profile at the end. '
                         'Useful on a long run to tell "still working" from "stuck".')
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

    if not args.verbose:
        # lp_model prints capex banners at import and on each build; quiet by default so the
        # convergence trace is readable, restored by --verbose.
        os.environ.setdefault('VA_ENERGY_QUIET_IMPORT', '1')

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

    if args.verbose:
        print(f'\nInputs:')
        print(f'    demand        {len(demand):,} h   peak {demand.max():>10,.0f} MW   '
              f'mean {demand.mean():>9,.0f} MW')
        print(f'    solar CF      mean {w["solar"].mean():.4f}   max {w["solar"].max():.4f}')
        print(f'    wind CF       mean {w["wind"].mean():.4f}   max {w["wind"].max():.4f}')
        print(f'    nuclear       mean {w["nuclear"].mean():>9,.0f} MW')
        print(f'    existing solar peak {exist_solar.max():>9,.0f} MW')
        if needs_dist:
            cf = dist['dist_solar_cf_designyear.npy']
            px = dist[f'dist_exog_price_{args.year}.npy']
            print(f'    distributed CF  mean {cf.mean():.4f}')
            print(f'    exogenous price mean ${px.mean():.2f}  max ${px.max():.2f}/MWh')
        print(f'    gas target share {drv.gas_target_share(args.year):.4f}')

    print(f'\nSolving scenario {args.scenario}, {args.year}. '
          'Up to four LP solves; expect several minutes per solve.')
    print('Each iteration line below is one completed solve -- if the gap stops shrinking across '
          'iterations,\nconverge_frac is not finding the gas fraction, which is a different problem '
          'from the solve being slow.\n')
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
    # MUST REPRODUCE THE SOLVER'S OWN CALL EXACTLY.
    #
    # BUG FIXED 2026-09-12: this previously called run_solve WITHOUT capacity_cap_mw and WITHOUT
    # the prior_* kwargs, making it an UNLINKED checkpoint with no prior-checkpoint build and no
    # gas cap -- a different optimisation from the one whose build figures were being reported
    # beside it. The duals and hourly dispatch described a problem that was not the scenario.
    #
    # It surfaced as a dispatch that could not balance: at night, supply of ~4,300 MW (wind plus
    # nuclear) against ~47,900 MW of demand, charging and curtailment, with zero unserved energy.
    # Physically impossible, and the signature of reading one problem's variables while comparing
    # against another problem's inputs.
    #
    # The kwargs are rebuilt from the solver's own accessors rather than reassembled by hand, so
    # this cannot drift from what converge_and_solve() ran.
    solve_kwargs = dict(solver._prior_kwargs())
    solve_kwargs.update(solver._gas_merit_order_kwargs())
    if needs_dist:
        solve_kwargs.update(solver._distributed_kwargs())
    raw = drv.run_solve(
        args.year, solver.converged_frac, demand, exist_solar, w['solar'], w['wind'], w['nuclear'],
        capacity_cap_mw=solver.apply_gas_cap(), return_hourly=True, return_raw_result=True,
        **solve_kwargs)

    # Rule 4: cross-verify against the solve whose results are being reported. A build that differs
    # means the two problems differ, and the duals do not describe the reported scenario.
    reported = float(result.get('S_mw', 0.0))
    rebuilt = float(raw.get('S_mw', 0.0))
    if reported > 0 and abs(rebuilt - reported) / reported > 1e-6:
        raise SystemExit(
            f'Re-solve does not reproduce the converged solve: solar {rebuilt:,.1f} MW vs '
            f'{reported:,.1f} MW. The duals and hourly dispatch would describe a different '
            'problem from the build figures. Not writing results.')
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
        if args.verbose:
            print('\n  Dual profile (the shape is the finding, not just the count):')
            for q in (0, 1, 5, 25, 50, 75, 95, 99, 100):
                print(f'    p{q:<3} ${np.percentile(duals, q):>10,.2f}/MWh')
            if args.merit_order:
                print('\n  Against the stack that produced it:')
                for r in solver.gas_merit_order.rungs(args.year):
                    share = float((duals >= r.marginal_cost_mwh(args.year) - 0.5).mean())
                    print(f'    {r.name:<14}${r.marginal_cost_mwh(args.year):>7.2f}/MWh   '
                          f'{share:>6.1%} of hours priced at or above it')
            above = float((duals > 200).mean())
            print(f'\n    hours above $200/MWh: {above:>6.2%}   '
                  f'above $1,000: {float((duals > 1000).mean()):.2%}')
        if summary['dual_unique_values'] <= 1:
            print('  WARNING: the dual is FLAT. With the merit order active that should not '
                  'happen -- see docs/MODEL_WIDE_FINDINGS.md section 1.')
    else:
        print('  no equality marginals returned; duals not saved')

    # ------------------------------------------------------------------
    # HOURLY DISPATCH -- the View 1 stack
    # ------------------------------------------------------------------
    # Added 2026-09-12 because the dual profile alone could not answer the obvious question it
    # raised: if 32.5% of hours sit at the curtailment floor, what serves the evening? Duals say
    # what a marginal MWh is worth; they say nothing about what physically dispatched. The columns
    # below match the View 1 sheets in the tracker workbook so the same chart can be rebuilt.
    if not args.no_hourly:
        x, IDX, BS = res.x, raw['problem']['IDX'], raw['problem']['BUILD_SCALE']
        T = raw['problem']['T']

        # build_problem exposes its variable layout as hv_params = (NVAR_BUILD, NVAR_PER_HOUR).
        # Variables are [build vars][T * NVAR_PER_HOUR], the k-th within hour t.
        hv_params = raw['problem'].get('hv_params')
        if hv_params is None:
            print('  hourly dispatch skipped: problem dict does not expose hv_params')
        else:
            nvar_build, nvar_per_hour = hv_params
            def col(t, key):
                return nvar_build + t * nvar_per_hour + IDX[key]

            def series(key, scale=1.0):
                return np.array([x[col(t, key)] for t in range(T)]) * scale

            solar_built = float(result.get('S_mw_total', result.get('S_mw', 0.0)))
            rows = {
                'Timestamp': np.arange(T),
                'Demand (MW)': demand[:T],
                'Solar potential (MW)': solar_built * w['solar'][:T] + exist_solar[:T],
                'Wind (MW)': lp.CVOW_MW * w['wind'][:T],
                'Nuclear (MW)': w['nuclear'][:T],
                'Curtailment (MW, neg)': -series('curtailed_generation_mw', BS),
                'Unserved (MW)': series('unserved_energy_mw', BS),
            }
            for label, key in (('Bath', 'bath'), ('NaIon', 'sodium_ion'), ('IronAir', 'iron_air')):
                for suffix, sign in (('discharge_mw', 1.0), ('charge_mw', -1.0)):
                    k = f'{key}_{suffix}'
                    if k in IDX:
                        nice = 'Discharge (MW)' if sign > 0 else 'Charging (MW, neg)'
                        rows[f'{label} {nice}'] = series(k, BS) * sign
                soc = f'{key}_state_of_charge_mwh'
                if soc in IDX:
                    v = series(soc, BS)
                    rows[f'{label} SoC (MWh)'] = v
                    if v.max() > 0:
                        rows[f'{label} SoC (%)'] = 100.0 * v / v.max()
            if 'gas_generation_mw' in IDX:
                rows['Gas (MW)'] = series('gas_generation_mw', BS)
            rows['Dual ($/MWh)'] = duals if 'duals' in locals() else np.zeros(T)

            import csv
            path = os.path.join(args.out, f'hourly_{tag}.csv')
            with open(path, 'w', newline='') as f:
                wtr = csv.writer(f)
                wtr.writerow(rows.keys())
                for t in range(T):
                    wtr.writerow([f'{v[t]:.4f}' if isinstance(v[t], float) else v[t]
                                  for v in rows.values()])
            print(f'  hourly dispatch -> {path}')

            # Answer the question the duals raised, in the run itself rather than by inference.
            curt = -rows['Curtailment (MW, neg)']
            sun = w['solar'][:T] > 0
            print(f'\n  Curtailment check:')
            print(f'    hours curtailing:            {int((curt > 1).sum()):>6,}')
            print(f'    of those, in daylight:       {int(((curt > 1) & sun).sum()):>6,}  '
                  f'({((curt > 1) & sun).sum() / max(1, (curt > 1).sum()):.1%})')
            print(f'    curtailed energy:            {curt.sum()/1e6:>6.1f} TWh')
            for label in ('NaIon', 'IronAir'):
                k = f'{label} SoC (%)'
                if k in rows:
                    v = rows[k]
                    print(f'    {label} SoC: min {v.min():.1f}%  max {v.max():.1f}%  '
                          f'hours at >99%: {int((v > 99).sum()):,}')

    with open(os.path.join(args.out, f'solve_{tag}.json'), 'w') as f:
        json.dump(summary, f, indent=2)
    print(f'\nDone in {elapsed/60:.1f} min. Wrote results/solve_{tag}.json'
          + (f' and results/duals_{tag}.npy' if 'dual_unique_values' in summary else ''))


if __name__ == '__main__':
    main()
