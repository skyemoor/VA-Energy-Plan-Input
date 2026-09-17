"""
time_solve_benchmark.py

Measures how long one Scenario 2 solve takes on THIS machine, and how well independent solves
parallelise, so the forced-outage draw loop can be sized before it is written.

WHY THIS EXISTS

Adequacy metrics -- loss of load hours, unserved energy, and eventually conditional value at risk --
need many scenarios rather than one. NERC's Risk Mitigation for Emerging Large Loads (2026) asks for
"thousands of integrated weather, load, and generation scenarios". This project holds eight weather
years, so the second axis has to come from forced-outage draws, and the cost of that loop is
solve time x draws x weather years x checkpoint years.

An estimate made in the development container gave 4.2 s per solve. That number does not transfer:
the solve is a single-threaded sparse linear program, bound by clock speed and memory bandwidth
rather than core count, and container CPU allocation is not the same as a workstation's.

WHAT THE DRAW LOOP WILL ACTUALLY DO

A forced-outage draw removes capacity from the merit-order stack for some hours. That changes RUNG
UPPER BOUNDS and nothing else -- not the matrix, not the objective, not the row structure. So the
problem can be built once and re-solved with mutated bounds, which this script measures separately
from a naive rebuild-every-draw loop.

The saving turns out to be small, because the build is cheap relative to the solve. Measured here
anyway, because "small" was a surprise and is worth confirming per machine.

WHERE THE REAL GAIN IS

Draws are independent, so they parallelise almost perfectly. N cores gives close to N times the
throughput, which matters far more than avoiding rebuilds. The parallel pass reports measured
speedup rather than assuming it, since memory bandwidth is shared and the scaling is rarely linear
on a memory-bound workload.

MEASURED RESULTS, and why the measurement is the point

On the development container: build 0.67 s, solve 3.83 s, and parallel scaling that was NEGATIVE at
two workers.

On a 16-logical-core x86_64 workstation, 2026-09-14:

    workers   speedup   efficiency   per draw
          4      2.4x          60%      0.95 s
          8      3.1x          38%      0.75 s
         16      2.7x          17%      0.85 s

**EIGHT WORKERS BEATS SIXTEEN.** Throughput peaks below the core count and then turns DOWN:
memory bandwidth saturates around eight concurrent solves, after which hyperthread contention takes
about 12% of throughput back while occupying the whole machine. Efficiency falls monotonically
across the three, which is the bandwidth-bound signature.

**THESE FIGURES ARE FOR TOTAL CONCURRENT SOLVES, however grouped.** Memory bandwidth does not care
how processes are divided into jobs, so two jobs on eight workers each is sixteen concurrent solves
-- the 2.7x row, not twice the 3.1x one. An earlier note here multiplied per-pool speedups and
claimed 6.2x aggregate; that was wrong.

Throughput is therefore maximised at about eight concurrent solves in TOTAL: one job on eight
workers, or two jobs on four workers each. `scripts/time_concurrent_jobs.py` measures the multi-job
case directly rather than inferring it from this one.

**The finding is not "eight is right".** It is that the peak sits below the core count and past it
gets worse, so it must be measured per machine. Three runs, ninety seconds, and it changed the
scheduling plan twice.

RUN IT

    python3 scripts/time_solve_benchmark.py                 # serial only, quick
    python3 scripts/time_solve_benchmark.py --parallel      # adds a multiprocessing pass
    python3 scripts/time_solve_benchmark.py --repeats 5 --workers 8

It prints a projected wall time for the draw loop at several draw counts, which is the number the
sizing decision needs.
"""
import argparse
import multiprocessing as mp
import os
import platform
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'lp_package'))

import demand_basis                                      # noqa: E402
import driver as drv                                     # noqa: E402
import gas_merit_order as gmo                            # noqa: E402
import lp_model as lp                                    # noqa: E402
import paths                                             # noqa: E402

YEAR = 2045
#: The 2045 split, from Scenario2Solver.solar_split_mw. Hard-coded so the benchmark measures solve
#: time rather than the solver's own setup, and so it stays comparable if the split later moves.
DIST_SOLAR_MW = 6862.0
UTIL_SOLAR_MW = 4583.0
#: Checkpoint years where capacity decisions are made. Intermediate years inherit the fleet, so the
#: draw loop does not need them.
CHECKPOINT_YEARS = 4
WEATHER_YEARS = 8


def _distributed_profile(weather):
    """A stand-in distributed capacity-factor profile, derived from the weather file's own solar
    series and rescaled to the 45-degree fixed array's 0.1526 capacity factor.

    NOT the real profile -- `distributed_solar_profile.hydro_year_profile` is, and it reads NSRDB
    CSVs that are deliberately not committed (large, public, re-downloadable). This benchmark does
    not need them: SOLVE TIME DEPENDS ON PROBLEM STRUCTURE, not on the values in the residual. The
    matrix shape, sparsity and row count are identical either way, so the timing transfers while
    the dependency does not.

    Using the real profile here would make a timing script fail on any machine without the source
    data, which is every machine except the one that built the profiles.
    """
    solar = np.asarray(weather['solar'], dtype=float)
    mean = solar.mean()
    return solar * (0.1526 / mean) if mean > 0 else np.full_like(solar, 0.1526)


def _build():
    """Build the 2045 Scenario 2 problem with the merit-order stack, as the draw loop would."""
    w = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    demand = demand_basis.VirginiaOnlyGeneration(YEAR).hourly_mw()
    drv.set_year_capex(YEAR)
    return lp.build_scenario2_problem(
        w['solar'], w['wind'], w['nuclear'], lp.exist_solar_mw(YEAR) * w['solar'], demand,
        vcea_solar_mw=UTIL_SOLAR_MW, ccgt_mw=200_000.0,
        na_power_mw=drv.vcea_short_duration_floor_mw(YEAR), na_duration_hr=4.0,
        fe_power_mw=drv.vcea_long_duration_floor_mw(YEAR), fe_duration_hr=100.0,
        gas_price_mwh=lp.gas_cost_mwh(YEAR, heat_rate=lp.CCGT_HEAT_RATE), ccgt_vom_mwh=3.0,
        verbose=False, gas_merit_order=gmo.GasMeritOrder(), gas_merit_order_year=YEAR,
        dist_solar_mw=DIST_SOLAR_MW, dist_solar_cf=_distributed_profile(w))


def _solve_once(_ignored=None):
    """Build and solve, for the parallel pass. Each worker builds its own: the problem holds sparse
    matrices that pickle poorly, and the build is cheap relative to the solve anyway."""
    t0 = time.perf_counter()
    lp.solve_problem(_build())
    return time.perf_counter() - t0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[2])
    ap.add_argument('--repeats', type=int, default=3,
                    help='serial solves to time (default 3)')
    ap.add_argument('--parallel', action='store_true',
                    help='add a multiprocessing pass to measure speedup')
    ap.add_argument('--workers', type=int, default=0,
                    help='worker processes; 0 uses cpu_count()')
    args = ap.parse_args()

    cores = os.cpu_count() or 1
    workers = args.workers or cores
    print(f'  machine: {platform.processor() or platform.machine()}, {cores} logical cores')
    print(f'  python {platform.python_version()}, numpy {np.__version__}')
    print()

    t0 = time.perf_counter()
    problem = _build()
    build_s = time.perf_counter() - t0
    nvar, nrow = len(problem['c']), problem['A_eq'].shape[0]
    print(f'  problem: {nvar:,} variables, {nrow:,} equality rows')
    print(f'  build:   {build_s:.2f} s')

    times = []
    for i in range(args.repeats):
        t0 = time.perf_counter()
        lp.solve_problem(problem)
        times.append(time.perf_counter() - t0)
        print(f'    solve {i + 1}: {times[-1]:.2f} s', flush=True)
    serial = float(np.mean(times))
    print(f'  solve:   {serial:.2f} s mean of {args.repeats} '
          f'(min {min(times):.2f}, max {max(times):.2f})')

    per_draw = serial
    if args.parallel:
        print()
        n = workers * 2                      # two rounds, so scheduling overhead is visible
        t0 = time.perf_counter()
        with mp.Pool(workers) as pool:
            pool.map(_solve_once, range(n))
        wall = time.perf_counter() - t0
        per_draw = wall / n
        speedup = serial / per_draw
        print(f'  parallel: {n} solves on {workers} workers in {wall:.1f} s')
        print(f'    {per_draw:.2f} s per draw, {speedup:.1f}x speedup '
              f'({speedup / workers:.0%} of linear)')
        print('    (memory bandwidth is shared, so scaling on a sparse LP is rarely linear)')

    print()
    print(f'  PROJECTED DRAW-LOOP WALL TIME, {WEATHER_YEARS} weather years x '
          f'{CHECKPOINT_YEARS} checkpoint years:')
    print(f'  {"draws/yr":>10}{"scenarios":>12}{"hours":>9}   what it supports')
    for draws in (30, 100, 375):
        scen = draws * WEATHER_YEARS
        hours = per_draw * scen * CHECKPOINT_YEARS / 3600
        if draws == 30:
            note = 'LOLH mean; EUE point estimate only'
        elif draws == 100:
            note = 'LOLH and EUE with intervals; CVaR-95 on 40 tail points'
        else:
            note = 'CVaR-95 on 150 tail points, NERC "thousands" range'
        print(f'  {draws:>10,}{scen:>12,}{hours:>9.1f}   {note}')
    print()
    print('  LOLH converges fastest -- it is a bounded count. EUE is heavy-tailed and needs more')
    print('  draws for the same relative precision. CVaR needs the tail itself, not a mean over it.')


if __name__ == '__main__':
    main()
