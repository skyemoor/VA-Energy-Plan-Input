#!/usr/bin/env python3
"""
run_scenario1_annual.py

Fills in the sixteen non-checkpoint years of Scenario 1, so the SLCOE covers all twenty.

    python3 run_scenario1_annual.py

Reads the four solved checkpoints from results/scenario1.json, interpolates the build between them,
and solves each remaining year DISPATCH-ONLY at that fixed build.

WHY INTERPOLATE RATHER THAN SOLVE EVERY YEAR FULLY

Solving all twenty with build variables would be maximally MYOPIC: each year would optimise against
its own gas target alone, and the early years' targets are weak (71% gas allowed at 2026), so almost
nothing would be built until late. The checkpoints carry the foresight; the intermediate years
inherit it. That is why a year like 2044 UNDER-shoots its own gas allowance -- it holds a build
sized for the steeper trajectory ahead of it.

It is also 3-4 hours against roughly 8 minutes.

2026 IS A ZERO-BUILD VIRTUAL CHECKPOINT. The first real checkpoint is 2030, so 2026-2029 have no
earlier pair to interpolate between. Anchoring at zero build in 2026 gives them one, and matches the
fact that Scenario 1's build genuinely starts from the existing fleet.

RESERVE MARGIN IS APPLIED, NOT JUST CHECKED. With the build pinned, the all-hours margin is a
constraint the year either satisfies or does not -- so an inadequate interpolated build surfaces as
INFEASIBILITY, which is the signal wanted, rather than as silently-accepted unserved energy. An
infeasible year is a real possibility and is reported as a finding about the interpolation, not
worked around.

THE SAME CONSTRAINT FUNCTION as the checkpoints use, not a dispatch-specific copy: Appendix P.2 §14.
build_dispatch_problem fixes capacity (NVAR_BUILD = 0), so capacities are passed through
fixed_capacity_mw and the constraint puts them on the right-hand side instead of treating them as
columns.
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lp_package'))

import numpy as np                                                        # noqa: E402

import all_hours_reserve as ahr                                           # noqa: E402
import assumptions                                                        # noqa: E402
import checkpoint_solver as cs                                            # noqa: E402
import compute_tier123_final as tier123                                   # noqa: E402
import demand_basis                                                       # noqa: E402
import driver as drv                                                      # noqa: E402
import lp_model as lp                                                     # noqa: E402
import paths                                                              # noqa: E402
from levelised_cost import LevelisedCost, build_salvage_credit            # noqa: E402

FIRST_YEAR, FINAL_YEAR = 2026, 2045

#: The build quantities carried between years, and the result keys they come from.
BUILD_KEYS = ('solar_mw_total', 'na_power_mw', 'na_energy_mwh', 'fe_energy_mwh')


def interpolate_build(year, anchors):
    """Linear interpolation between the nearest checkpoint pair.

    `anchors` maps year -> build dict, including the 2026 zero-build virtual checkpoint.

    A CHECKPOINT YEAR RETURNS ITS OWN SOLVED BUILD unchanged, so the twenty-year stream agrees with
    the four-year one exactly at the years both cover -- which is what makes them comparable.
    """
    years = sorted(anchors)
    if year in anchors:
        return dict(anchors[year])
    lo = max(y for y in years if y < year)
    hi = min(y for y in years if y > year)
    w = (year - lo) / (hi - lo)
    return {k: anchors[lo][k] + w * (anchors[hi][k] - anchors[lo][k]) for k in BUILD_KEYS}


def solve_year(year, weather, build, irm):
    """One dispatch-only solve at a fixed build, with the all-hours reserve margin applied."""
    demand = demand_basis.VirginiaOnlyLoad(year).hourly_mw()
    exist_solar = lp.exist_solar_mw(year) * weather['solar']
    drv.set_year_capex(year)

    gas_cap = drv.schedule_b_baseline_mw(year) + assumptions.GAS_NEW_BUILD_POOL_MW
    problem = lp.build_dispatch_problem(
        weather['solar'], weather['wind'], weather['nuclear'], exist_solar, demand,
        drv.gas_target_share(year), S_mw=build['solar_mw_total'], PNA_mw=build['na_power_mw'],
        ENA_mwh=build['na_energy_mwh'], EFE_mwh=build['fe_energy_mwh'], verbose=False)
    problem = ahr.add_all_hours_reserve_margin_constraint(
        problem, weather['nuclear'], weather['wind'], exist_solar, weather['solar'],
        np.zeros(len(demand)), gas_cap, demand, IRM=irm,
        fixed_capacity_mw={'utility_solar_mw': build['solar_mw_total'],
                           'sodium_ion_power_mw': build['na_power_mw'],
                           'iron_air_energy_mwh': build['fe_energy_mwh']})

    t0 = time.time()
    res = lp.solve_problem(problem)
    if res.status == 2:
        raise RuntimeError(
            f'{year}: INFEASIBLE. With the build pinned, that means the interpolated build cannot '
            f'hold the {irm:.1%} reserve margin in every hour -- a finding about the interpolation, '
            'not a solver failure. Report which year and by how much; do not relax the constraint.')
    if not res.success:
        raise RuntimeError(f'{year}: solve failed with status {res.status}: {res.message}')

    IDX, T = problem['IDX'], problem['T']
    nb, nph = problem['hv_params']

    def hourly(key):
        return np.array([res.x[nb + t * nph + IDX[key]] for t in range(T)])

    unserved = float(hourly('unserved').sum())
    if unserved > 1.0:
        raise RuntimeError(
            f'{year}: {unserved:,.1f} MWh unserved. At the penalty price this dominates the '
            'objective, and Appendix P.2 §11 requires zero before a solve is presented as final.')
    for charge, discharge, label in (('nc', 'nd', 'Na'), ('fc', 'fd', 'iron-air'),
                                     ('bc', 'bd', 'Bath')):
        n = int(np.sum((hourly(charge) > 1e-6) & (hourly(discharge) > 1e-6)))
        if n:
            raise RuntimeError(f'{year}: {n} hours of simultaneous charge/discharge for {label}.')

    gas = hourly('g')
    tiers = tier123.compute_year(year, gas, drv.schedule_b_baseline_mw(year),
                                 assumptions.GAS_NEW_BUILD_POOL_MW)
    nonnuclear = float((demand - weather['nuclear']).sum())
    return {
        'year': year,
        'interpolated': True,
        'demand_mwh': float(demand.sum()),
        'gas_mwh': float(gas.sum()),
        # BOTH BASES. gas_share_statutory is gas / (demand - nuclear), the § 56-585.5(A) base that
        # EXCLUDES nuclear and that the RPS target is defined on; gas_share_of_demand counts
        # nuclear as clean and is the whitepaper's compliance axis.
        'gas_share_statutory': float(gas.sum() / nonnuclear),
        'gas_share_of_demand': float(gas.sum() / demand.sum()),
        'gas_target_share': float(drv.gas_target_share(year)),
        'gas_cap_mw': float(gas_cap),
        'peak_gas_mw': float(gas.max()),
        'solar_mw_total': float(build['solar_mw_total']),
        'na_power_mw': float(build['na_power_mw']),
        'na_energy_mwh': float(build['na_energy_mwh']),
        'fe_energy_mwh': float(build['fe_energy_mwh']),
        'curtailment_mwh': float(hourly('curt').sum()),
        'unserved_mwh': unserved,
        'obj_usd': float(res.fun),
        'virginia_scc_usd': float(tiers['social_cost_of_carbon']),
        'social_cost_ghg_usd': float(tiers['social_cost_of_ghg']),
        'health_impacts_usd': float(tiers['health_impacts_cost']),
        'seconds': round(time.time() - t0, 1),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--checkpoints', default='results/scenario1.json',
                    help='the four solved checkpoints to interpolate between')
    ap.add_argument('--irm', type=float, default=0.177)
    ap.add_argument('--out', default='results')
    args = ap.parse_args()

    if not os.path.exists(args.checkpoints):
        raise SystemExit(
            f'{args.checkpoints} does not exist yet. It is written by:\n\n'
            f'    python3 run_scenario1.py\n\n'
            'which solves the four checkpoints (~26 min). Run that first.')
    with open(args.checkpoints) as f:
        saved = json.load(f)
    solved = {r['year']: r for r in saved['checkpoints']}
    if args.irm != saved.get('irm', args.irm):
        raise SystemExit(
            f'--irm {args.irm} against {saved["irm"]} in {args.checkpoints}. The interpolated years '
            'must hold the same margin as the checkpoints they interpolate between.')

    # 2026 ZERO-BUILD VIRTUAL CHECKPOINT -- see the module docstring. Without it 2026-2029 have no
    # earlier anchor and would have to extrapolate backwards from 2030.
    anchors = {FIRST_YEAR: {k: 0.0 for k in BUILD_KEYS}}
    anchors.update({y: {k: r[k] for k in BUILD_KEYS} for y, r in solved.items()})

    weather = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    print(f'Scenario 1 annual stream {FIRST_YEAR}-{FINAL_YEAR}', flush=True)
    print(f'  checkpoints from {args.checkpoints}: {sorted(solved)}', flush=True)
    print(f'  {FIRST_YEAR} anchored at zero build; {len(range(FIRST_YEAR, FINAL_YEAR + 1)) - len(solved)}'
          ' years interpolated and dispatch-solved\n', flush=True)
    print(f'{"year":<6}{"":>3}{"clean":>8}{"statutory":>11}{"solar":>12}{"curt TWh":>10}'
          f'{"obj $B":>9}', flush=True)

    t_start = time.time()
    stream = []
    for year in range(FIRST_YEAR, FINAL_YEAR + 1):
        if year in solved:
            row = dict(solved[year])
            row['interpolated'] = False
            mark = ' *'
        else:
            row = solve_year(year, weather, interpolate_build(year, anchors), args.irm)
            mark = '  '
        stream.append(row)
        print(f'{year:<6}{mark:>3}{1 - row["gas_share_of_demand"]:>7.1%}'
              f'{row["gas_share_statutory"]:>10.1%} {row["solar_mw_total"]:>11,.0f}'
              f'{row.get("curtailment_mwh", 0.0) / 1e6:>10.1f}{row["obj_usd"] / 1e9:>9.2f}',
              flush=True)
    print('  * = solved checkpoint, not interpolated', flush=True)

    # Levelise. Salvage is credited on the CHECKPOINT builds only: an interpolated year holds
    # capacity built at a checkpoint, so crediting it again would count the same asset repeatedly.
    lc = LevelisedCost()
    for row in stream:
        lc.add_year(row['year'], row['obj_usd'], row['demand_mwh'])
    lc.verify_complete()
    for year, r in solved.items():
        drv.set_year_capex(year)
        credit, _ = build_salvage_credit(
            {'S_mw': r['solar_mw_new'], 'PNA_mw': r['na_power_mw'],
             'ENA_mwh': r['na_energy_mwh'], 'EFE_mwh': r['fe_energy_mwh']}, year, FINAL_YEAR)
        lc.add_terminal_value(f'checkpoint_{year}', credit, note='build vintage of that checkpoint')

    summary = lc.summary()
    pv_demand = summary['pv_demand_mwh']
    tiers_pv = {}
    for key, label in (('virginia_scc_usd', 'Virginia SCC (CO2 only, statutory)'),
                       ('social_cost_ghg_usd', 'Social cost of GHG (CO2+CH4+N2O)'),
                       ('health_impacts_usd', 'Health impacts (PM, SO2, NOx)')):
        pv = sum(r.get(key, 0.0) * lc.discount_factor(r['year']) for r in stream)
        tiers_pv[key] = {'pv_usd': pv, 'per_mwh': pv / pv_demand, 'label': label}
    summary['tiers'] = tiers_pv

    print(f'\nPV cost      ${summary["pv_cost_usd"] / 1e9:>10,.2f}B', flush=True)
    print(f'PV demand     {pv_demand / 1e6:>10,.1f} TWh', flush=True)
    print(f'\nSLCOE without terminal value  ${summary["slcoe_without_terminal_value"]:>7.2f}/MWh')
    print(f'SLCOE with terminal value     ${summary["slcoe_with_terminal_value"]:>7.2f}/MWh')
    print('\nTier 1 and 2, levelised on the same PV basis:', flush=True)
    for v in tiers_pv.values():
        print(f'  {v["label"]:<38}${v["pv_usd"] / 1e9:>8,.3f}B   ${v["per_mwh"]:>6.2f}/MWh')
    societal = (summary['slcoe_with_terminal_value']
                + tiers_pv['social_cost_ghg_usd']['per_mwh']
                + tiers_pv['health_impacts_usd']['per_mwh'])
    summary['total_societal_slcoe'] = societal
    print(f'  {"TOTAL SOCIETAL SLCOE":<38}{"":>9}   ${societal:>6.2f}/MWh')

    print('\nDECOMMISSIONING AND SCRAP ARE BOTH OMITTED. Schedule B retires 7,502 MW of gas at 2045;')
    print('  a retired thermal plant has no residual generating value, and what remains is scrap')
    print('  metal against demolition, abatement, remediation and disconnection -- typically a net')
    print('  liability. Neither side is costed here for want of sourced figures. The omissions')
    print('  partly offset, and booking the liability would make the gas-heavier scenarios look')
    print('  worse, not better, so the omission is conservative in the direction that matters.')

    print(f'\nDone in {(time.time() - t_start) / 60:.1f} min', flush=True)
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, 'scenario1_annual.json')
    with open(path, 'w') as f:
        json.dump({'stream': stream, 'levelised': summary, 'irm': args.irm,
                   'checkpoints_from': args.checkpoints}, f, indent=2)
    print(f'Wrote {path}', flush=True)


if __name__ == '__main__':
    main()
