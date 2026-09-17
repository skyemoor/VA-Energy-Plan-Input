"""
sweep_scenario2_gas_sizing.py

Finds the minimum whole number of combined-cycle reference units Scenario 2 needs in each year of
2026-2045, and writes the measured trajectory for `assumptions.SCENARIO2_NEW_CCGT_UNITS_BY_YEAR`.

WHY A PER-YEAR SWEEP, AND NOT FOUR CHECKPOINTS

THE REQUIREMENT IS NOT MONOTONIC. Spot measurements give 2031 needing 500 MW, 2033 needing none,
2035 needing 500 MW and 2037 needing 2,000 -- because the statutory solar build ramps to 16,100 MW
by 2035 while demand grows steadily, so the residual DIPS in years when solar arrives faster than
load.

A four-checkpoint table with zeros at 2030 and 2035 therefore missed 2031 entirely, and the runner
failed there on 4,022.9 MWh unserved. Interpolating between measured points failed again at 2036.
Rule 9's own invariant check caught both, which is the system working -- but it means the trajectory
has to be measured year by year rather than inferred.

**Capacity persists**, so what is BUILT in a year is the running maximum of the requirement up to
it. This script reports both: the per-year requirement, and the build that follows from it.

WHAT IT DOES NOT DO

It finds the ADEQUACY FLOOR -- the smallest build at which unserved energy reaches zero. That is not
the same as the cost optimum: at 2045 adequacy gives about 5,000 MW while cost gives 6,500, because
the extra capacity pays for itself in fuel saved on the existing fleet. The floor is the constraint;
the optimum sits above it and is set separately (Scenario 2 working document, section 9).

So the trajectory this produces is a LOWER BOUND on what a least-cost plan builds, and the terminal
year's entry should be the cost figure rather than this script's.

RUNNING IT

    python3 scripts/sweep_scenario2_gas_sizing.py
    python3 scripts/sweep_scenario2_gas_sizing.py --workers 2 --jobs 4
    python3 scripts/sweep_scenario2_gas_sizing.py --years 2036 2037 --max-units 8

Solves are independent, so they parallelise. On a 16-logical-core workstation, throughput peaks at
about EIGHT concurrent solves in total and turns down past it; four jobs of two workers measured
best (see scripts/time_concurrent_jobs.py). Twenty years at up to eight units each is at most 160
solves, a few minutes at that configuration.

Writes results/scenario2_gas_sizing.json and prints a table ready to paste into assumptions.py.
"""
import argparse
import json
import multiprocessing as mp
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, 'lp_package'))

import assumptions                                       # noqa: E402
import checkpoint_solver as checkpoint                    # noqa: E402
import demand_basis                                       # noqa: E402
import driver                                             # noqa: E402
import lp_model as lp                                     # noqa: E402
import paths                                              # noqa: E402

DEFAULT_YEARS = tuple(range(2026, 2046))
#: Above this the search stops and reports failure rather than continuing indefinitely. Eight units
#: is 8,664 MW, comfortably beyond the 6,498 MW the 2045 cost optimum builds.
DEFAULT_MAX_UNITS = 8
#: MWh. Below this a year counts as served; linear-programming solutions carry small residuals.
UNSERVED_TOLERANCE_MWH = 1.0


def _unserved_mwh(year, units):
    """Total unserved energy with `units` reference units of new combined cycle available."""
    weather = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    demand = demand_basis.VirginiaOnlyGeneration(year).hourly_mw()
    driver.set_year_capex(year)
    solver = checkpoint.Scenario2Solver(
        year=year, demand=demand,
        exist_solar=lp.exist_solar_mw(year) * weather['solar'], solar_cf=weather['solar'],
        wind_cf=weather['wind'], nuclear=weather['nuclear'], vcea_solar_mw=16_100.0)
    cap_mw = (driver.gas_baseline_mw(year, solver.gas_retirement_schedule())
              + assumptions.GAS_NEW_BUILD_POOL_MW
              + units * assumptions.CCGT_REFERENCE_UNIT_MW)
    # RULE 9'S INVARIANT CHECK RAISES ON UNSERVED ENERGY, which is correct for a scenario asked to
    # serve its load and wrong for this sweep: measuring the shortfall at an inadequate capacity is
    # the whole point. Catching it is not bypassing the check -- an undersized trial is EXPECTED to
    # fail, and the failure is the measurement.
    try:
        result = solver.solve(gas_price_mwh=lp.gas_cost_mwh(year, heat_rate=lp.CCGT_HEAT_RATE),
                              ccgt_mw=cap_mw)
    except ValueError as invariant_failure:
        message = str(invariant_failure)
        if 'unserved energy' not in message:
            raise
        # The check reports the figure it rejected; parse rather than re-solve.
        import re
        found = re.search(r'has ([\d,.]+) MWh unserved', message)
        if not found:
            raise
        return float(found.group(1).replace(',', ''))

    idx = result['problem']['IDX']
    vars_per_hour = result['problem']['hv_params'][1]
    return float(sum(result['raw'].x[t * vars_per_hour + idx['unserved']]
                     for t in range(len(demand))))


def _smallest_adequate(args):
    """Fewest units at which `year` serves its load. Returns (year, units, unserved_at_that_size)."""
    year, max_units = args
    for units in range(max_units + 1):
        unserved = _unserved_mwh(year, units)
        if unserved < UNSERVED_TOLERANCE_MWH:
            return year, units, unserved
    return year, None, unserved


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[2])
    parser.add_argument('--years', nargs='*', type=int, default=list(DEFAULT_YEARS))
    parser.add_argument('--max-units', type=int, default=DEFAULT_MAX_UNITS)
    parser.add_argument('--workers', type=int, default=2,
                        help='worker processes (default 2; see time_concurrent_jobs.py)')
    args = parser.parse_args()

    print(f'  reference unit: {assumptions.CCGT_REFERENCE_UNIT_MW:,.0f} MW')
    print(f'  sweeping {len(args.years)} years, up to {args.max_units} units, '
          f'{args.workers} workers', flush=True)

    started = time.perf_counter()
    work = [(year, args.max_units) for year in args.years]
    if args.workers > 1:
        with mp.Pool(args.workers) as pool:
            found = pool.map(_smallest_adequate, work)
    else:
        found = [_smallest_adequate(item) for item in work]
    elapsed = time.perf_counter() - started

    found.sort()
    failed = [year for year, units, _ in found if units is None]
    print(f'  swept in {elapsed / 60:.1f} min')
    print()
    print(f'  {"year":<6}{"units required":>16}{"MW":>10}{"units built":>13}{"MW built":>11}')
    built_so_far = 0
    trajectory = {}
    for year, units, _unserved in found:
        if units is None:
            print(f'  {year:<6}{"NOT ADEQUATE":>16}{"":>10}{"":>13}{"":>11}')
            continue
        built_so_far = max(built_so_far, units)      # capacity persists
        trajectory[year] = built_so_far
        print(f'  {year:<6}{units:>16}{units * assumptions.CCGT_REFERENCE_UNIT_MW:>10,.0f}'
              f'{built_so_far:>13}{built_so_far * assumptions.CCGT_REFERENCE_UNIT_MW:>11,.0f}')

    if failed:
        print()
        print(f'  NOT ADEQUATE at {args.max_units} units: {failed}. Re-run those years with a '
              '--max-units high enough to bracket them; do not assume the table is complete.')

    results_dir = os.path.join(REPO, 'results')
    os.makedirs(results_dir, exist_ok=True)
    out_path = os.path.join(results_dir, 'scenario2_gas_sizing.json')
    with open(out_path, 'w') as handle:
        json.dump({
            'reference_unit_mw': assumptions.CCGT_REFERENCE_UNIT_MW,
            'basis': ('adequacy floor: smallest build at which unserved energy reaches zero. NOT '
                      'the cost optimum, which sits above it -- at 2045 adequacy gives about 5,000 '
                      'MW against a 6,500 MW cost optimum.'),
            'units_required_by_year': {str(y): u for y, u, _ in found if u is not None},
            'units_built_by_year': {str(y): u for y, u in trajectory.items()},
            'not_adequate_at_max_units': failed,
        }, handle, indent=2)
    print()
    print(f'  wrote {out_path}')
    print()
    print('  paste into assumptions.SCENARIO2_NEW_CCGT_UNITS_BY_YEAR:')
    years = sorted(trajectory)
    for start in range(0, len(years), 5):
        row = years[start:start + 5]
        print('    ' + ', '.join(f'{y}: {trajectory[y]}' for y in row) + ',')
    print()
    print('  NOTE: this is the ADEQUACY FLOOR. The terminal year should carry the COST optimum')
    print('  instead -- 6 units at 2045 -- since the extra capacity pays for itself in fuel saved.')


if __name__ == '__main__':
    main()
