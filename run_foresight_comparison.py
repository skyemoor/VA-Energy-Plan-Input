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
import demand_basis                                                       # noqa: E402
import driver as drv                                                      # noqa: E402
import lp_model as lp                                                     # noqa: E402
import multi_period_problem as mp                                         # noqa: E402
import paths                                                              # noqa: E402
from levelised_cost import (BUILD_RESULT_KEYS, build_salvage_credit,       # noqa: E402
                            undepreciated_value)

CHECKPOINTS = (2030, 2035, 2040, 2045)

SCENARIOS = {'1': cs.Scenario1WithReserveMargin, '3': cs.Scenario3WithReserveMargin}

#: Technical life per build variable position, for the salvage credit. Storage and solar take
#: CRF_LIFE_YEARS; there is no gas build variable, so no CCGT_LIFE_YEARS entry is needed.
_LIFE_BY_BUILD_VAR = [assumptions.CRF_LIFE_YEARS] * 8


def load_year(year, needs_distributed):
    """Weather, demand and any distributed inputs for one year.

    DEMAND COMES FROM demand_basis.VirginiaOnlyLoad, NOT the cached intermediate. The two are
    byte-identical where both exist -- verified 2026-09-14 at 2030 and 2045 -- because the
    intermediate is produced by run_all from exactly this call. But the cache exists only for
    CHECKPOINT years, while the source works for any year in 2026-2045, so reading the cache made
    this runner silently checkpoint-only and put a second demand path in the repository for no gain.

    The distributed inputs stay on the cache: they are genuinely derived artefacts of run_all's
    scenario3_inputs stage, not a cache of something callable.
    """
    weather = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    demand = demand_basis.VirginiaOnlyLoad(year).hourly_mw()
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
    """Residual value per MW of each build variable, at the 2045 horizon, **on an ANNUITY basis**.

    THE BASIS MATTERS AND I GOT IT WRONG FIRST TIME. build_problem charges build variables as
    `CRF * capex * 1000` -- an ANNUAL cost in $/MW-yr, not the capital outlay. Crediting salvage
    as raw undepreciated CAPITAL against an annuity-based objective made it swamp the cost: a live
    2030 run reported $6.50B of salvage against a $4.13B objective, larger than the entire year.

    Multiplying by CRF puts the credit on the same basis as the charge. What it then represents is
    the ANNUAL payment stream avoided for the years beyond the horizon -- which is the right
    quantity when every other term in the objective is also an annual figure.

    Straight-line on remaining technical life, per the EC's present-value convention and NREL's ATB
    note that "a technical life that is longer than the cost recovery period means residual value
    may be left after costs have been recovered". Nothing strands: solar and storage built at any
    checkpoint still operate past 2045. Gas WOULD strand at 100% compliance, but there is no gas
    build variable.
    """
    import lp_model as lp
    return [undepreciated_value(capex, year, CHECKPOINTS[-1], life,
                                strands_at_horizon=False) * lp.CRF
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
        # Pairs each per-MW credit with its OWN build variable. _build_value returns the four
        # utility build quantities in the same order as _capex_by_build_var's first four entries;
        # a mismatch here would credit solar salvage against storage MW without raising.
        drv.set_year_capex(year)
        salvage, _ = build_salvage_credit(result, year, CHECKPOINTS[-1])
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


#: Re-exported from levelised_cost (Rule 6.1), which owns the canonical ordering. A local copy
#: existed here until 2026-09-14 and would have been free to drift from the one build_salvage_credit
#: actually uses -- the pairing is positional, so a divergence would credit solar salvage against
#: storage MW without raising.
_BUILD_RESULT_KEYS = list(BUILD_RESULT_KEYS)


def _assert_build_ordering():
    """Rule 4: cross-check the two positional lists that must stay aligned.

    _capex_by_build_var returns [solar $/MW, NA power $/MW, NA energy $/MWh, FE energy $/MWh] and
    _BUILD_RESULT_KEYS must name the same four quantities in the same order. Checked by magnitude,
    which is the only signal available: solar capex per MW is ~30x storage ENERGY capex per MWh, so
    a swap shows up immediately.
    """
    import lp_model as lp
    drv.set_year_capex(2045)
    capex = _capex_by_build_var(2045)
    if not capex[0] > capex[2] * 5:
        raise AssertionError(
            f'build ordering looks wrong: position 0 ({capex[0]:,.0f}) should be solar $/MW and '
            f'position 2 ({capex[2]:,.0f}) storage energy $/MWh, which differ by an order of '
            'magnitude. Check _capex_by_build_var against _BUILD_RESULT_KEYS.')
    if list(BUILD_RESULT_KEYS) != ['S_mw', 'PNA_mw', 'ENA_mwh', 'EFE_mwh']:
        raise AssertionError(
            f'levelised_cost.BUILD_RESULT_KEYS reordered to {BUILD_RESULT_KEYS}; _capex_by_build_var '
            'must be reordered to match, or salvage is credited against the wrong quantities.')
    return True



def run_perfect_foresight(klass, needs_distributed, verbose=True):
    """All four checkpoints in one simultaneous LP."""
    problems, demands = [], []
    for year in CHECKPOINTS:
        solver, demand, w = _solver(klass, year, needs_distributed)
        solver.verify_input_data()
        drv.set_year_capex(year)
        prior_kwargs = solver._prior_kwargs()
        dist_kwargs = solver._distributed_kwargs() if hasattr(solver, '_distributed_kwargs') else {}
        gas_kwargs = solver._gas_merit_order_kwargs()
        hook = solver._chain_hooks(solver._post_build_hook(),
                                   solver._all_hours_reserve_hook(0.177))

        # BUILT THROUGH run_solve(build_only=True), NOT build_problem DIRECTLY.
        #
        # An earlier version called build_problem and applied the hooks itself. That skipped every
        # post-build step run_solve performs -- the capacity cap, the VCEA storage floors, and
        # min_na_duration_hr=6.0 -- and produced 41,718 MWh of unserved energy at 2030 where the
        # myopic solve had none. Without the duration floor the LP builds cheap power-only storage
        # that cannot sustain a multi-hour evening.
        #
        # PRIOR_* IS DELIBERATELY NOT PASSED. Continuity between periods is what the linking rows
        # do; passing prior floors as well would impose the myopic chain's own answer on the
        # foresight solve and defeat the comparison.
        problem = drv.run_solve(
            year, drv.gas_target_share(year), demand,
            lp.exist_solar_mw(year) * w['solar'], w['solar'], w['wind'], w['nuclear'],
            capacity_cap_mw=solver.apply_gas_cap(), build_only=True, post_build_hook=hook,
            slcr_curt_cost=solver.curtailment_cost_mwh(), **dist_kwargs, **gas_kwargs)
        problems.append(problem)
        demands.append(float(demand.sum()))

    salvage = [salvage_credit_per_mw(y, _capex_by_build_var(y)) for y in CHECKPOINTS]
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
    # APPENDIX P.2 §11 -- the myopic side verifies through solve_with_reserve_margin, and this
    # side had nothing. Without it the comparison would hold the two to different standards, which
    # is the failure the comparison exists to avoid. Raises rather than reporting a flag.
    verification = mp.verify_solution(assembled, res.x)
    builds = mp.builds_by_period(assembled, res.x)
    if verbose:
        print(f'  solved in {(time.time() - t0)/60:.1f} min, objective '
              f'${res.fun/1e9:,.2f}B (already discounted)', flush=True)
        for y, b in zip(CHECKPOINTS, builds):
            print(f'  {y}  solar {b["utility_solar_mw"]:>11,.0f} MW   '
                  f'NA {b["sodium_ion_power_mw"]:>10,.0f} MW   '
                  f'FE {b["iron_air_energy_mwh"]/1e6:>7.2f} TWh', flush=True)
    return {'objective_usd': float(res.fun), 'builds': builds, 'demands_mwh': demands,
            'verification': verification, 'seconds': round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--scenario', default='1', choices=sorted(SCENARIOS))
    ap.add_argument('--myopic-from', default=None,
                    help='reuse a saved run_scenario1.py result instead of re-solving the myopic '
                         'side (~19 min). The saved run must use the same checkpoints and IRM.')
    ap.add_argument('--out', default='results')
    args = ap.parse_args()
    klass = SCENARIOS[args.scenario]
    needs_dist = args.scenario == '3'
    _assert_build_ordering()

    print(f'Foresight comparison, scenario {args.scenario}. '
          'Five solves total; the foresight one is ~4x the size of a checkpoint.', flush=True)
    if args.myopic_from:
        # A MISSING FILE HERE IS THE EXPECTED FIRST-RUN STATE, not an error worth a traceback:
        # run_scenario1.py writes it, and --myopic-from is the natural thing to reach for before
        # noticing that. Say what to run.
        if not os.path.exists(args.myopic_from):
            raise SystemExit(
                f'{args.myopic_from} does not exist yet. It is written by:\n\n'
                f'    python3 run_scenario1.py\n\n'
                'which solves the myopic chain (~19 min). Run that first, then this with '
                '--myopic-from. Omit --myopic-from to solve both sides in one go.')
        try:
            with open(args.myopic_from) as f:
                saved = json.load(f)
        except json.JSONDecodeError as exc:
            raise SystemExit(
                f'{args.myopic_from} is not valid JSON ({exc}). If run_scenario1.py was '
                'interrupted mid-write, delete the file and re-run it.')
        if 'checkpoints' not in saved:
            raise SystemExit(
                f'{args.myopic_from} has no "checkpoints" key -- it does not look like a '
                'run_scenario1.py result. Check the path.')
        myopic = saved['checkpoints']
        if [r['year'] for r in myopic] != list(CHECKPOINTS):
            raise SystemExit(
                f'{args.myopic_from} covers {[r["year"] for r in myopic]}, not {list(CHECKPOINTS)}. '
                'The two sides must use the same checkpoints or the comparison is not like-for-like.')
        print(f'\n=== MYOPIC: reusing {args.myopic_from} ===', flush=True)
        for r in myopic:
            print(f'  {r["year"]}  solar {r["solar_mw_total"]:>11,.0f} MW   '
                  f'obj ${r["obj_usd"]/1e9:>6.2f}B   salvage ${r["salvage_usd"]/1e9:>5.2f}B',
                  flush=True)
    else:
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
