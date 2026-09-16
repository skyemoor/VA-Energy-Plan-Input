#!/usr/bin/env python3
"""
run_scenario2_slcoe.py

Solves every year 2026-2045 and levelises the result into a single SLCOE for Scenario 2 -- the
whitepaper's baseline, Dominion's approach of building only the solar and storage the Code names.

    python3 run_scenario2_slcoe.py

WHY EVERY YEAR RATHER THAN THE FOUR CHECKPOINTS

A levelised cost needs the whole stream. Averaging 2030/2035/2040/2045 weights each equally,
ignores discounting, and misses that demand grows 72% across the horizon so later years carry far
more MWh. LevelisedCost.verify_complete() refuses a partial stream for exactly that reason.

Twenty dispatch-only solves is under two minutes: build_scenario2_problem has no build variables,
so each year is ~5 s.

WHAT THIS RUNNER DOES NOT NEED, and the reason is worth stating

No demand interpolation. Dominion's own hourly projections cover 2026-2045 with no gaps and carry a
different shape per year that ALREADY flattens as data-centre load grows -- load factor 0.652 in
2024 rising to 0.794 by 2045. demand_shape_interpolation was built to age a single fixed shape
forward and would, applied here, make the shape LESS flat than the source already is. See its own
docstring banner.

No build interpolation either. Scenario 2's build is STATUTORY, so every year's pins come straight
from the Code via drv.vcea_*_floor_mw(year) and assumptions.vcea_new_solar_mw(year). Scenarios 1
and 3 will need build interpolation between checkpoints; this one does not.

TERMINAL VALUE is computed per asset from its build year and technical life, using the EC's
present-value-of-post-horizon-cash-flows convention: an asset that will never run again is worth
nothing whatever its book age. Scenario 2's gas DOES run at 2045, so unlike the 100%-compliance
case it carries real residual value.
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
import demand_basis                                                       # noqa: E402
import driver as drv                                                      # noqa: E402
import lp_model as lp                                                     # noqa: E402
import paths                                                              # noqa: E402
import compute_tier123_final as tier123                                   # noqa: E402
from levelised_cost import LevelisedCost, undepreciated_value             # noqa: E402

FIRST_YEAR, FINAL_YEAR = 2026, 2045

#: Technical lives for the terminal-value calculation. Solar and storage take CRF_LIFE_YEARS (25);
#: gas takes its own CCGT_LIFE_YEARS (30). Named here rather than inline so a reader can see which
#: life drives which credit.
ASSET_LIVES = {'solar': assumptions.CRF_LIFE_YEARS,
               'storage_na': assumptions.CRF_LIFE_YEARS,
               'storage_fe': assumptions.CRF_LIFE_YEARS,
               'gas': assumptions.CCGT_LIFE_YEARS}


def solve_year(year, weather, capex_basis):
    """One year: statutory pins, dispatch-only solve, full lifecycle cost."""
    demand = demand_basis.VirginiaOnlyGeneration(year).hourly_mw()
    solver = cs.Scenario2Solver(
        year=year, demand=demand, exist_solar=lp.exist_solar_mw(year) * weather['solar'],
        solar_cf=weather['solar'], wind_cf=weather['wind'], nuclear=weather['nuclear'],
        vcea_solar_mw=16_100.0)
    result = solver.solve(gas_price_mwh=lp.gas_cost_mwh(year, heat_rate=lp.CCGT_HEAT_RATE))
    if not result['success']:
        raise RuntimeError(f'{year}: solve failed with status {result["status"]}')

    problem = result['problem']
    x, IDX = result['raw'].x, problem['IDX']
    # SIMULTANEOUS CHARGE/DISCHARGE, all three storage types. Appendix P.2 #11 requires this
    # alongside the unserved check, and it was MISSING here until 2026-09-14: Scenario2Solver.solve
    # does not call verify_result, and this runner only checked unserved energy -- so twenty years
    # were levelised with no degeneracy check at all.
    #
    # The results were clean when finally measured (zero hours at 2026 and 2045), but that was luck
    # rather than verification, and Scenario 2 is exactly where it matters: build_scenario2_problem
    # lacks the SLCR splice and cycling costs that make simultaneous dispatch unattractive in
    # build_problem, which is why it needs its own Bath discharge token in the first place.
    # VARIABLES PER HOUR FROM THE PROBLEM, not a literal. This file used a hardcoded 14 at four
    # sites; build_scenario2_problem happens to have 14, but a literal that must match a structure
    # defined elsewhere is the shape that produced the merit-order and curtailment divergences.
    nph = problem['hv_params'][1]
    for charge_key, discharge_key, label in (('nc', 'nd', 'Na'), ('fc', 'fd', 'iron-air'),
                                             ('bc', 'bd', 'Bath')):
        if charge_key not in IDX or discharge_key not in IDX:
            continue
        ch = np.array([x[t * nph + IDX[charge_key]] for t in range(len(demand))])
        di = np.array([x[t * nph + IDX[discharge_key]] for t in range(len(demand))])
        n = int(np.sum((ch > 1e-6) & (di > 1e-6)))
        if n:
            raise RuntimeError(
                f'{year}: {n} hours of simultaneous charge/discharge for {label} storage. '
                'Appendix P.2 #11 requires zero before a solve is presented as final.')

    unserved = sum(x[t * nph + IDX['unserved']] for t in range(len(demand)))
    if unserved > 1.0:
        # Appendix P.2 #11: verification before any solve is presented as final.
        raise RuntimeError(
            f'{year}: {unserved:,.1f} MWh unserved. At $100,000/MWh this dominates the objective, '
            'and a year with unserved energy has failed verification -- its cost is not meaningful.')

    cost = solver.lifecycle_cost(ccgt_capex_basis=capex_basis)
    gas_mwh = sum(x[t * nph + IDX['g']] for t in range(len(demand)))

    # TIER 1 AND 2, per Appendix P.2 #9 -- which requires them "across all 20 years of a
    # scenario-solve, not from a subset of checkpoint years", the same full-window rule as #1.
    # Computed from THIS year's actual hourly gas dispatch, not from an annual total, because the
    # NOx blend depends on the existing/new MW split at this year's own dispatch level.
    g_hourly = np.array([x[t * nph + IDX['g']] for t in range(len(demand))])
    # SCHEDULE A, from the solver's own declaration. This read schedule_b_baseline_mw until
    # 2026-09-14 -- the VCEA-driven schedule, whose premise is that plants retire FOR LACK OF
    # MARKET. Scenario 2 runs gas at a 68% capacity factor supplying 132 TWh, so they do not.
    existing_mw = drv.gas_baseline_mw(year, solver.gas_retirement_schedule())
    new_mw = assumptions.GAS_NEW_BUILD_POOL_MW
    tiers = tier123.compute_year(year, g_hourly, existing_mw, new_mw)
    return {
        'year': year,
        'demand_mwh': float(demand.sum()),
        'gas_mwh': float(gas_mwh),
        # BOTH BASES, as the Scenario 1 and 1B runners report. gas_share_statutory is
        # gas / (demand - nuclear), the § 56-585.5(A) base that EXCLUDES nuclear and that any
        # compliance ceiling applies to; clean_share counts nuclear as clean and is the
        # whitepaper's own compliance axis. They differ by 14 points at 2030.
        'clean_share': float(1.0 - gas_mwh / demand.sum()),
        'gas_share_of_demand': float(gas_mwh / demand.sum()),
        'gas_share_statutory': float(gas_mwh / (demand - weather['nuclear']).sum()),
        'peak_gas_mw': float(max(x[t * nph + IDX['g']] for t in range(len(demand)))),
        'new_solar_mw': float(result['vcea_new_build_mw']),
        'na_power_mw': float(result['na_power_mw']),
        'fe_power_mw': float(result['fe_power_mw']),
        'objective_usd': float(result['obj']),
        'total_annual_usd': float(cost.total_annual_usd),
        'annualised_capital_usd': float(cost.annualised_capital_usd),
        'fixed_om_usd': float(cost.fixed_om_usd),
        # Tier 1 reported as TWO figures per Va. Code §56-598(2)(d) / §56-585.1(A)(6): the
        # statutory CO2-only concept and the broader multi-gas total are different quantities and
        # must not be combined into one.
        'virginia_scc_usd': float(tiers['social_cost_of_carbon']),
        'social_cost_ghg_usd': float(tiers['social_cost_of_ghg']),
        'health_impacts_usd': float(tiers['health_impacts_cost']),
        'co2_tons': float(tiers['co2_tons']),
        'nox_tons': float(tiers['nox_tons']),
    }, cost


def terminal_values(stream, final_cost, capex_basis):
    """Residual value of each asset class at the horizon.

    BUILD YEAR IS TAKEN AS THE YEAR THE CAPACITY FIRST APPEARS in the stream, not the final year.
    Using the final year would credit every asset with its full life remaining and inflate the
    credit enormously -- solar reaching its statutory level in 2035 has 15 of its 25 years gone by
    2045, not zero.
    """
    first_seen = {}
    for row in stream:
        for key, field in (('solar', 'new_solar_mw'), ('storage_na', 'na_power_mw'),
                           ('storage_fe', 'fe_power_mw'), ('gas', 'peak_gas_mw')):
            if row[field] > 0 and key not in first_seen:
                first_seen[key] = row['year']

    capex_by_asset = {a.name: a for a in final_cost.assets}
    out = {}
    for key, life in ASSET_LIVES.items():
        if key not in first_seen:
            out[key] = 0.0
            continue
        # Sum the capital actually charged for this asset class across the lifecycle breakdown.
        capital = sum(a.new_mw * 1000.0 * a.capex_usd_per_kw
                      for name, a in capex_by_asset.items() if name.startswith(key.split('_')[0]))
        out[key] = undepreciated_value(capital, first_seen[key], FINAL_YEAR, life,
                                       # Scenario 2's gas RUNS at 2045 -- unlike the 100%
                                       # compliance case, it is not stranded and keeps its value.
                                       strands_at_horizon=False)
    return out, first_seen


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--capex-basis', default='central', choices=['low', 'central', 'high'])
    ap.add_argument('--out', default='results')
    args = ap.parse_args()

    weather = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    print(f'Scenario 2 SLCOE: solving {FIRST_YEAR}-{FINAL_YEAR}, capex basis {args.capex_basis}',
          flush=True)
    print(f'{"year":<6}{"clean":>8}{"gas peak":>11}{"total $B":>11}{"$/MWh":>9}', flush=True)

    t0 = time.time()
    stream, final_cost = [], None
    for year in range(FIRST_YEAR, FINAL_YEAR + 1):
        row, cost = solve_year(year, weather, args.capex_basis)
        stream.append(row)
        final_cost = cost
        print(f'{year:<6}{row["clean_share"]:>7.1%}{row["peak_gas_mw"]:>11,.0f}'
              f'{row["total_annual_usd"] / 1e9:>11.2f}'
              f'{row["total_annual_usd"] / row["demand_mwh"]:>9.2f}', flush=True)

    lc = LevelisedCost()
    for row in stream:
        lc.add_year(row['year'], row['total_annual_usd'], row['demand_mwh'])
    lc.verify_complete()

    tv, first_seen = terminal_values(stream, final_cost, args.capex_basis)
    for asset, value in tv.items():
        lc.add_terminal_value(asset, value,
                              note=f'first built {first_seen.get(asset, "n/a")}, '
                                   f'life {ASSET_LIVES[asset]} yr')

    # Tier 1/2 levelised on the same PV basis as the financial figure -- same discount rate, same
    # base year, same 20 years -- so the per-MWh numbers are directly addable into a total
    # societal SLCOE. Appendix D: "the genuine, full-20-year total for each scenario, not derived
    # from the four-checkpoint table".
    pv_demand = sum(r['demand_mwh'] * lc.discount_factor(r['year']) for r in stream)
    tiers_pv = {}
    for key, label in (('virginia_scc_usd', 'Virginia SCC (CO2 only, statutory)'),
                       ('social_cost_ghg_usd', 'Social cost of GHG (CO2+CH4+N2O)'),
                       ('health_impacts_usd', 'Health impacts (PM, SO2, NOx)')):
        pv = sum(r[key] * lc.discount_factor(r['year']) for r in stream)
        tiers_pv[key] = {'pv_usd': pv, 'per_mwh': pv / pv_demand, 'label': label}

    summary = lc.summary()
    summary['tiers'] = tiers_pv
    print(f'\nPV cost      ${summary["pv_cost_usd"] / 1e9:>10,.2f}B', flush=True)
    print(f'PV demand     {summary["pv_demand_mwh"] / 1e6:>10,.1f} TWh', flush=True)
    print(f'PV terminal  ${summary["pv_terminal_value_usd"] / 1e9:>10,.2f}B', flush=True)
    print(f'\nSLCOE without terminal value  ${summary["slcoe_without_terminal_value"]:>7.2f}/MWh')
    print(f'SLCOE with terminal value     ${summary["slcoe_with_terminal_value"]:>7.2f}/MWh')
    print('\nTier 1 and 2, levelised on the same PV basis (Appendix P.2 #9, Appendix D):')
    for v in tiers_pv.values():
        print(f'  {v["label"]:<38}${v["pv_usd"] / 1e9:>8,.3f}B   ${v["per_mwh"]:>6.2f}/MWh')
    societal = (summary['slcoe_with_terminal_value']
                + tiers_pv['social_cost_ghg_usd']['per_mwh']
                + tiers_pv['health_impacts_usd']['per_mwh'])
    print(f'  {"TOTAL SOCIETAL SLCOE":<38}{"":>9}   ${societal:>6.2f}/MWh')
    print('  (direct SLCOE + SC-GHG + health; Tier 3 excluded from the dollar total by design;')
    print('   the broader SC-GHG used here, not the narrower CO2-only Virginia SCC)')
    summary['total_societal_slcoe'] = societal

    print(f'\nclean share {stream[0]["clean_share"]:.1%} ({FIRST_YEAR}) '
          f'-> {stream[-1]["clean_share"]:.1%} ({FINAL_YEAR})')
    print(f'Done in {(time.time() - t0) / 60:.1f} min')

    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, f'scenario2_slcoe_{args.capex_basis}.json')
    with open(path, 'w') as f:
        json.dump({'capex_basis': args.capex_basis, 'stream': stream,
                   'levelised': summary, 'first_built': first_seen}, f, indent=2)
    print(f'Wrote {path}')


if __name__ == '__main__':
    main()
