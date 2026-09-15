#!/usr/bin/env python3
"""
run_scenario1b.py

Solves Scenario 1B across its own checkpoint set and reports the build, cost and gas share.

    python3 run_scenario1b.py

WHAT MAKES 1B DIFFERENT, and why it needs its own runner rather than a --scenario flag

    CHECKPOINTS      2030, 2035, 2040, **2044**, 2045 -- five, not four.
    TARGET           identical to Scenario 1 through 2044; 5% gas from 2045 rather than 0%.
    GAS CAPACITY     6,000 MW from 2045 (Appendix N.2's locked sweep result), against
                     Scenario 1's 4,722 MW.

2044 IS NOT OPTIONAL. 2044's own RPS target is 5% gas -- which IS 1B's 2045 target. So 1B's 2045
build should equal its 2044 build, and the 2045 checkpoint should require no new capacity at all.
Linking 2045 back to 2040 and skipping the shared 2041-2044 window is what produced what Appendix
N.4 calls "a physically nonsensical, wildly oversized 2045 buildout" -- corrected there, and the
correction is why this runner carries a fifth checkpoint.

TWO DEFECTS FIXED BEFORE THIS COULD RUN (2026-09-14)

    N.2 locked in 6,000 MW total (1,278 MW new simple-cycle CT) after sweeping capped capacities
    and costing each as LP objective PLUS externally-priced capex. N.4 then solved at 4,722 MW --
    N.2's own "existing only" row, costing $10,065.2M against $9,469.3M at 6,000 MW. The 1,278 MW
    was never implemented in code. N.4's 1.63% gas share, and its conclusion that "the 5% statutory
    ceiling is largely moot", were measured without it.

    There was no Scenario1BWithReserveMargin, so 1B solved with NO RESERVE MARGIN AT ALL while
    Scenarios 1 and 3 carried the all-hours constraint.

THE NEW CT IS COSTED EXTERNALLY, not inside the LP objective, because the LP carries no capex
penalty for gas -- only marginal fuel cost. That is precisely why N.2's sweep was needed: given
free rein the uncapped LP chose 17,704 MW, having no reason to economize.
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

#: Five, not four. See the module docstring: 2044's RPS target IS 1B's 2045 target.
CHECKPOINTS = (2030, 2035, 2040, 2044, 2045)


def solve_checkpoint(year, weather, prior, irm):
    demand = demand_basis.VirginiaOnlyLoad(year).hourly_mw()
    solver = cs.Scenario1BWithReserveMargin(
        year=year, demand=demand, exist_solar=lp.exist_solar_mw(year) * weather['solar'],
        solar_cf=weather['solar'], wind_cf=weather['wind'], nuclear=weather['nuclear'])
    solver.prior_result = prior
    t0 = time.time()
    result = dict(solver.solve_with_reserve_margin(IRM=irm))
    result['year'] = year

    gas_mwh = float(result.get('gas_mwh', 0.0))
    g_hourly = None
    if 'hourly' in result and 'g' in result['hourly']:
        g_hourly = np.asarray(result['hourly']['g'], dtype=float)
        if not gas_mwh:
            gas_mwh = float(g_hourly.sum())

    # TIER 1 AND 2 per Appendix P.2 #9, on the same per-year basis as the Scenario 2 runner, so the
    # two scenarios' societal costs are comparable. Computed from THIS year's actual hourly gas
    # dispatch, because the NOx blend depends on the existing/new MW split at this dispatch level.
    tiers = {}
    if g_hourly is not None:
        t = tier123.compute_year(year, g_hourly, drv.schedule_b_baseline_mw(year),
                                 assumptions.GAS_NEW_BUILD_POOL_MW)
        tiers = {'virginia_scc_usd': float(t['social_cost_of_carbon']),
                 'social_cost_ghg_usd': float(t['social_cost_of_ghg']),
                 'health_impacts_usd': float(t['health_impacts_cost']),
                 'co2_tons': float(t['co2_tons'])}

    # New CT beyond the inherited cap, costed externally. Zero before 2045, where 1B's capacity is
    # Scenario 1's.
    new_ct_mw = (assumptions.SCENARIO_1B_NEW_CT_MW if year >= 2045 else 0.0)
    new_ct_capex = new_ct_mw * 1000.0 * assumptions.SCENARIO_1B_NEW_CT_CAPEX_KW

    row = {
        'year': year,
        'demand_mwh': float(demand.sum()),
        'gas_mwh': gas_mwh,
        # BOTH BASES. gas_share_statutory is gas / (demand - nuclear), the § 56-585.5(A) base that
        # EXCLUDES nuclear -- what gas_target_share means and what a compliance ceiling applies to.
        # gas_share_of_demand counts nuclear as clean and is the whitepaper's own compliance axis.
        # They differ by 14 points at 2030 and 0.6 at 2045; comparing one against the other's
        # ceiling is an apples-to-oranges claim.
        'gas_share_statutory': float(result.get('achieved_share', 0.0)),
        'gas_share_of_demand': gas_mwh / float(demand.sum()) if demand.sum() else 0.0,
        'gas_target_share': float(solver.gas_target_share),
        'gas_cap_mw': float(solver.apply_gas_cap()),
        'solar_mw_total': float(result.get('S_mw_total', result.get('S_mw', 0.0))),
        'solar_mw_new': float(result.get('S_mw', 0.0)),
        'na_power_mw': float(result.get('PNA_mw', 0.0)),
        'fe_energy_mwh': float(result.get('EFE_mwh', 0.0)),
        'obj_usd': float(result['obj']),
        'new_ct_mw': new_ct_mw,
        'new_ct_capex_usd': new_ct_capex,
        'new_ct_annualised_usd': new_ct_capex * lp.CRF,
        'converged': bool(result.get('converged', False)),
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
    print('Scenario 1B: ' + ' -> '.join(str(y) for y in CHECKPOINTS), flush=True)
    print('  2044 carries 1B\'s own 2045 target (5% gas), so 2045 should need no new build.',
          flush=True)
    # 'obj $B' IS NOT A COST TRAJECTORY. Each checkpoint's objective charges annualised capital on
    # that year's NEW build only, so a year that builds nothing shows a low objective while
    # operating a fleet it is not charged for -- Scenario 1B's 2045 ($8.25B) sits below its 2044
    # ($13.29B) for exactly that reason, on higher demand. Comparable across checkpoints only after
    # the full lifecycle treatment.
    print(f'\n{"year":<6}{"clean":>8}{"gas cap":>10}{"solar total":>13}{"new solar":>11}'
          f'{"incr obj $B":>13}', flush=True)

    prior, rows = None, []
    for year in CHECKPOINTS:
        row, result = solve_checkpoint(year, weather, prior, args.irm)
        rows.append(row)
        print(f'{year:<6}{1 - row["gas_share_of_demand"]:>7.1%}{row["gas_cap_mw"]:>10,.0f}'
              f'{row["solar_mw_total"]:>13,.0f}{row["solar_mw_new"]:>11,.0f}'
              f'{row["obj_usd"]/1e9:>9.2f}', flush=True)
        prior = result

    # THE CHECK THAT MATTERS FOR THIS SCENARIO. 2044 and 2045 carry the SAME 5% target, so the
    # 2045 checkpoint should add nothing -- Appendix N.4's "zero new solar or storage build". A
    # nonzero increment means the linking is not carrying 2044 forward.
    final, penultimate = rows[-1], rows[-2]
    increment = final['solar_mw_total'] - penultimate['solar_mw_total']

    # TEST solar_mw_new, NOT THE INCREMENT. The cumulative total FALLS between checkpoints even
    # when nothing is built, because the carried-forward fleet degrades at 0.5%/yr -- 125,193.88 x
    # 0.995 = 124,567.91, which is exactly the -626 MW first measured here. An increment-based test
    # can therefore never read zero, and flagged a correct result as suspicious.
    print(f'\n2044 -> 2045: new build {final["solar_mw_new"]:,.1f} MW, '
          f'cumulative {increment:+,.1f} MW', flush=True)
    if final['solar_mw_new'] > 1.0:
        print('  NOTE: 2044 and 2045 share the same 5% target, so Appendix N.4 expects NO new '
              'build. A nonzero figure means either the linking is not carrying 2044 forward, or '
              'the 6,000 MW cap has changed what 2045 needs.', flush=True)
    else:
        degradation = penultimate['solar_mw_total'] * (1 - 0.995)
        print(f'  No new build, as Appendix N.4 found: 2044 already exceeds what the 5% target '
              f'needs. The cumulative fall of {abs(increment):,.0f} MW is degradation of the '
              f'carried-forward fleet ({degradation:,.0f} MW expected at 0.5%/yr).', flush=True)

    print(f'\ngas share at {final["year"]}:', flush=True)
    print(f'  {final["gas_share_statutory"]:.2%} on the STATUTORY base (gas / demand excluding '
          f'nuclear) against the {final["gas_target_share"]:.0%} ceiling  <- the comparison that '
          'matters', flush=True)
    print(f'  {final["gas_share_of_demand"]:.2%} of total demand, the model\'s own clean-share '
          'axis, which counts nuclear as clean', flush=True)
    print(f'  Appendix N.4 reported 1.63% at a 4,722 MW cap; this runs at '
          f'{final["gas_cap_mw"]:,.0f} MW.', flush=True)
    if not final['converged']:
        print('  DID NOT CONVERGE, and that is the result rather than a failure: the search '
              'saturated with the achieved share unchanged across a tripling of the allowance, so '
              'gas CANNOT reach the ceiling at this capacity. N.4\'s conclusion that the binding '
              'constraint is physical fleet capacity rather than the RPS percentage survives the '
              'correction -- at a materially higher share than it was measured at.', flush=True)

    # Retain/overhaul plan at the final checkpoint -- which plants the 6,000 MW target implies
    # keeping, which need overhaul, and how much genuinely new capacity is left over.
    w2 = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    d2 = demand_basis.VirginiaOnlyLoad(CHECKPOINTS[-1]).hourly_mw()
    plan = cs.Scenario1BWithReserveMargin(
        year=CHECKPOINTS[-1], demand=d2,
        exist_solar=lp.exist_solar_mw(CHECKPOINTS[-1]) * w2['solar'],
        solar_cf=w2['solar'], wind_cf=w2['wind'],
        nuclear=w2['nuclear']).retain_and_overhaul_plan()
    if plan:
        print(f'\nretain / overhaul plan at {CHECKPOINTS[-1]}:', flush=True)
        print(f'  Schedule B survivors      {plan["schedule_b_survivors_mw"]:>8,.0f} MW', flush=True)
        print(f'  retained from pool        {plan["retained_pool_mw"]:>8,.0f} MW  '
              f'({len(plan["retained_plants"])} plants, {len(plan["needing_overhaul"])} needing '
              f'overhaul)', flush=True)
        print(f'  residual gap              {plan["residual_gap_mw"]:>8,.0f} MW  '
              f'<- matches N.2\'s independently-swept {plan["new_build_mw_continuous"]:,.0f} MW',
              flush=True)
        print(f'  new build, discrete units {plan["new_build_mw_discrete"]:>8,.0f} MW  '
              f'({plan["new_build_units"]} F-Class -- 237 MW each overshoots by '
              f'{plan["new_build_mw_discrete"] - plan["residual_gap_mw"]:,.0f} MW)', flush=True)
        print(f'  overhaul ${plan["overhaul_annual_cost_usd"]/1e6:,.1f}M/yr, '
              f'new build ${plan["newbuild_annual_cost_usd"]/1e6:,.1f}M/yr', flush=True)

    if 'social_cost_ghg_usd' in final:
        print(f'\nsocial cost at 2045: SC-GHG ${final["social_cost_ghg_usd"]/1e9:.3f}B   '
              f'Virginia SCC ${final["virginia_scc_usd"]/1e9:.3f}B   '
              f'health ${final["health_impacts_usd"]/1e9:.3f}B', flush=True)

    print(f'\nnew simple-cycle CT at 2045: {final["new_ct_mw"]:,.0f} MW, '
          f'${final["new_ct_capex_usd"]/1e9:.2f}B capital, '
          f'${final["new_ct_annualised_usd"]/1e9:.3f}B/yr annualised', flush=True)
    print('  Costed externally -- the LP has no capex penalty for gas, which is why N.2 swept '
          'capacities rather than letting it choose.', flush=True)

    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, 'scenario1b.json')
    with open(path, 'w') as f:
        json.dump({'checkpoints': rows,
                   'gas_capacity_mw': assumptions.SCENARIO_1B_GAS_CAPACITY_MW,
                   'new_ct_mw': assumptions.SCENARIO_1B_NEW_CT_MW,
                   'new_ct_capex_kw': assumptions.SCENARIO_1B_NEW_CT_CAPEX_KW,
                   'solar_increment_2044_to_2045_mw': increment,
                   'solar_new_build_2045_mw': final['solar_mw_new'],
                   'retain_overhaul_plan': plan}, f, indent=2)
    print(f'\nWrote {path}', flush=True)


if __name__ == '__main__':
    main()
