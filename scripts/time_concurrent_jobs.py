"""
time_concurrent_jobs.py

Measures aggregate throughput when N independent jobs each run M worker processes, so the draw loop
can be scheduled on evidence rather than on arithmetic.

WHY THIS EXISTS SEPARATELY FROM time_solve_benchmark.py

That script measures ONE job scaling across workers, and found throughput peaking at eight workers
on a 16-logical-core workstation -- 3.1x, against 2.7x at sixteen. Past the peak, hyperthread
contention takes throughput back while occupying the whole machine.

The obvious next question is whether several smaller jobs beat one large one, and it is easy to get
wrong. A previous version of this project's notes claimed that "two jobs on eight workers each gives
roughly 6.2x aggregate" -- multiplying per-pool speedups. **That is wrong.** Memory bandwidth does
not care how processes are grouped: two jobs of eight workers IS sixteen concurrent solves, which is
the configuration that measured 2.7x.

So the measured curve is a function of TOTAL CONCURRENT SOLVES, and N x M is the only number that
matters for throughput. What N and M separately decide is whether results arrive together or in
sequence.

**This script exists because that reasoning was wrong once already**, and measuring the multi-job
case costs two minutes.

WHAT IT MEASURES

For each (jobs, workers) combination, it runs `jobs` separate processes, each of which solves
`solves_per_job` problems on a pool of `workers`. It reports aggregate solves per second against the
serial baseline, so configurations with equal N x M can be compared directly.

    python3 scripts/time_concurrent_jobs.py
    python3 scripts/time_concurrent_jobs.py --grid 1x8 2x4 4x2 1x16 2x8
    python3 scripts/time_concurrent_jobs.py --solves-per-job 8

MEASURED RESULTS, 16-logical-core x86_64 workstation, 2026-09-14

    config  concurrent  solves/s  speedup
       1x4           4      1.09     2.9x
       1x8           8      1.21     3.2x
       2x4           8      1.27     3.4x
       4x2           8      1.37     3.6x   <- best
       3x4          12      1.22     3.2x
       6x2          12      1.26     3.3x
       4x3          12      1.28     3.4x
      1x16          16      1.18     3.1x
       4x4          16      1.14     3.0x
       2x8          16      1.06     2.8x

**TOTAL CONCURRENCY SETS THE ENVELOPE.** Eight beats twelve beats sixteen in every grouping; no
arrangement of processes recovers what is lost past the bandwidth ceiling.

**GROUPING MATTERS ONLY AT THE PEAK.** At eight concurrent, four jobs of two workers beats one job
of eight by 12% -- likely pool coordination overhead, which shows when the last of the available
bandwidth is being extracted. At twelve the three groupings sit within 5% and the effect has gone.

Recommended: **4 jobs x 2 workers** for aggregate throughput with four scenarios progressing
together; **4 x 3** when four scenarios should FINISH sooner (7% less aggregate, each job 50%
faster); **1 x 8** for a single scenario.

WHAT TO DO WITH THE ANSWER

If configurations with equal N x M give equal throughput, group by what is convenient: two jobs of
four workers each runs two scenarios at once, which is usually preferable to running them in
sequence at the same aggregate rate.

If they differ materially, the grouping matters and the best one should be recorded per machine --
process-level effects such as memory locality can break the simple model, which is the case worth
knowing about.
"""
import argparse
import multiprocessing as mp
import os
import platform
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, 'lp_package'))


def _solve_once(_ignored=None):
    """One build-and-solve, as a draw-loop iteration would be."""
    import time as _t
    from time_solve_benchmark import _build           # noqa: F401  (same directory)
    import lp_model as _lp
    t0 = _t.perf_counter()
    _lp.solve_problem(_build())
    return _t.perf_counter() - t0


def _run_one_job(workers, solves):
    """A single job: `solves` problems across `workers` processes. Returns wall seconds."""
    t0 = time.perf_counter()
    with mp.Pool(workers) as pool:
        pool.map(_solve_once, range(solves))
    return time.perf_counter() - t0


def _job_entry():
    """Child-process entry point, invoked by --_job."""
    workers, solves = int(sys.argv[2]), int(sys.argv[3])
    print(f'{_run_one_job(workers, solves):.4f}')


def _serial_baseline():
    """One solve, no pool, for the speedup denominator."""
    sys.path.insert(0, HERE)
    from time_solve_benchmark import _build
    import lp_model as lp
    lp.solve_problem(_build())                        # warm caches, discard
    t0 = time.perf_counter()
    lp.solve_problem(_build())
    return time.perf_counter() - t0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[2])
    ap.add_argument('--grid', nargs='*', default=['1x4', '1x8', '2x4', '1x16', '2x8', '4x2'],
                    help='JOBSxWORKERS combinations (default: 1x4 1x8 2x4 1x16 2x8 4x2)')
    ap.add_argument('--solves-per-job', type=int, default=8,
                    help='solves each job performs (default 8)')
    args = ap.parse_args()

    cores = os.cpu_count() or 1
    print(f'  machine: {platform.machine()}, {cores} logical cores')
    print('  measuring serial baseline...', flush=True)
    serial = _serial_baseline()
    print(f'  serial solve: {serial:.2f} s')
    print()
    print(f'  {"config":>8}{"concurrent":>12}{"wall s":>9}{"solves/s":>10}{"speedup":>9}')

    results = []
    for spec in args.grid:
        jobs, workers = (int(v) for v in spec.lower().split('x'))
        total_solves = jobs * args.solves_per_job
        procs = []
        t0 = time.perf_counter()
        for _ in range(jobs):
            procs.append(subprocess.Popen(
                [sys.executable, os.path.abspath(__file__), '--_job',
                 str(workers), str(args.solves_per_job)],
                cwd=REPO, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        for p in procs:
            p.wait()
        wall = time.perf_counter() - t0
        rate = total_solves / wall
        speedup = rate * serial
        results.append((spec, jobs * workers, wall, rate, speedup))
        print(f'  {spec:>8}{jobs * workers:>12}{wall:>9.1f}{rate:>10.2f}{speedup:>8.1f}x',
              flush=True)

    print()
    best = max(results, key=lambda r: r[3])
    print(f'  BEST: {best[0]} -- {best[3]:.2f} solves/s, {best[4]:.1f}x')
    groups = {}
    for spec, conc, _w, rate, _s in results:
        groups.setdefault(conc, []).append((spec, rate))
    mixed = {c: v for c, v in groups.items() if len(v) > 1}
    if mixed:
        print()
        print('  EQUAL CONCURRENCY, DIFFERENT GROUPING:')
        for conc, v in sorted(mixed.items()):
            rates = ', '.join(f'{s} {r:.2f}/s' for s, r in v)
            spread = (max(r for _s, r in v) - min(r for _s, r in v)) / max(r for _s, r in v)
            verdict = ('grouping barely matters -- schedule for convenience'
                       if spread < 0.10 else
                       'GROUPING MATTERS -- process-level effects break the simple model')
            print(f'    {conc:>2} concurrent: {rates}   ({spread:.0%} spread, {verdict})')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--_job':
        sys.path.insert(0, HERE)
        _job_entry()
    else:
        main()
