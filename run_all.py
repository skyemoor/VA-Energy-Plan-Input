#!/usr/bin/env python3
"""
run_all.py

Single entry point for the whole modeling pipeline. Run it with no arguments:

    python3 run_all.py

WHY THIS EXISTS (2026-09-10)

A dependency audit found the repository could not reproduce its own results from a clean clone,
despite the README saying it could. Scripts hardcoded absolute paths to three environment-specific
roots, several passed derived intermediates to each other through /tmp with no recorded production
order, and the development filesystem resets between sessions. Anyone cloning the repository --
including a future session of this project -- would have had to reconstruct the order by reading
each script.

WHAT IT DOES

  - Checks the environment FIRST and reports what is missing in plain language, rather than dying
    on an import traceback or an opaque numpy error several minutes in.
  - Runs stages in dependency order, producing each intermediate before anything needs it.
  - Prints progress as it goes, so a long run does not look frozen.
  - SKIPS stages whose outputs already exist, so an interrupted run resumes rather than restarting.
    Use --force to rebuild regardless.
  - Writes a run manifest per stage (lp_package/provenance.py) recording parameters, input file
    HASHES and runtime -- so a result can be traced to exactly what produced it.
  - Writes final outputs to results/.

DESIGN NOTE: stages declare their inputs and outputs as data, not as prose. That makes the
dependency graph checkable (--graph prints it) rather than something a reader has to infer, and it
is what allows both resume and the missing-input check to work without duplicating knowledge.
"""
import argparse
import os
import sys
import time
import traceback

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lp_package'))

# Silence the modules' import-time capex banners. They are useful when a modeler imports these
# interactively, but here they interleave with this script's own progress output -- appearing
# mid-stage and making a clean run look like something had gone wrong. Set before any project
# import so it takes effect regardless of import order. Use --verbose to see them.
if '--verbose' not in sys.argv:
    os.environ['VA_ENERGY_QUIET_IMPORT'] = '1'


# --- Environment check ------------------------------------------------------------------------
REQUIRED_PACKAGES = [
    ('numpy', 'numpy'),
    ('scipy', 'scipy'),
    ('pandas', 'pandas'),
    ('openpyxl', 'openpyxl'),
]


def check_environment():
    """Returns a list of human-readable problems. Empty list means good to go.

    Deliberately checks everything and reports all problems at once rather than failing on the
    first -- a user missing three packages should learn that in one run, not three.
    """
    problems = []
    if sys.version_info < (3, 9):
        problems.append(
            f"Python {sys.version_info.major}.{sys.version_info.minor} found; 3.9 or newer needed.")
    for module_name, pip_name in REQUIRED_PACKAGES:
        try:
            __import__(module_name)
        except ImportError:
            problems.append(f"'{module_name}' not installed.  Fix:  pip install {pip_name}")
    try:
        import scipy.optimize
        if not hasattr(scipy.optimize, 'linprog'):
            problems.append("scipy.optimize.linprog missing -- scipy install looks incomplete.")
    except ImportError:
        pass  # already reported above
    return problems


# --- Stage definitions ------------------------------------------------------------------------
# Each stage declares what it needs and what it produces, so the dependency graph is data rather
# than something a reader infers from import order.

class Stage:
    def __init__(self, name, description, outputs, function, source_files=(), inputs=()):
        self.name = name
        self.description = description
        self.outputs = list(outputs)          # paths, relative to repo root
        self.function = function
        self.source_files = list(source_files)  # large public data, not committed
        self.inputs = list(inputs)            # intermediates produced by earlier stages

    def outputs_exist(self):
        import paths
        return all(os.path.exists(os.path.join(paths.REPO_ROOT, o)) for o in self.outputs)

    def unmet_prerequisites(self, stages_by_name):
        """Names of declared input stages whose outputs are not on disk.

        Judged on DISK STATE, not on what ran in this invocation. An earlier version tracked the
        latter, which produced a false negative under --only: filtering the stage list meant the
        upstream stages never entered the loop, so they were recorded as not-run even when their
        outputs were sitting on disk from a previous run. Reported 2026-09-10 by
        `--only scenario2_capacity --force`.

        The `inputs` field was previously declared and never read -- a stage would run even when
        the stage that produces its inputs had skipped, then fail on a missing file. Found
        2026-09-10 by a user whose source data was absent: stage 1 skipped, stage 4 ran anyway and
        died. Declaring a dependency graph and then not consulting it is worse than not declaring
        one, because the docstring claims a check that is not happening.
        """
        unmet = []
        for name in self.inputs:
            upstream = stages_by_name.get(name)
            if upstream is None or not upstream.outputs_exist():
                unmet.append(name)
        return unmet

    def missing_sources(self):
        import paths
        missing = []
        for f in self.source_files:
            try:
                paths.source_file(f)
            except FileNotFoundError:
                missing.append(f)
        return missing


def stage_demand_arrays():
    """Virginia-only hourly demand for each checkpoint fiscal year.

    Fiscal-year construction, leap handling and column validation live in
    demand_basis.VirginiaOnlyLoad, not here (Rule 1.3: scripts orchestrate, they do not own logic
    called more than once). This stage now only chooses the years and writes the files.
    """
    import numpy as np, paths
    from demand_basis import VirginiaOnlyLoad
    written = []
    for year in (2030, 2035, 2040, 2045):
        basis = VirginiaOnlyLoad(year)
        out = basis.hourly_mw()
        np.save(paths.intermediate(f'demand_{year}fy_va_only.npy'), out)
        written.append((year, out.sum() / 1e6, out.max()))
    return {'years': [int(w[0]) for w in written],
            'annual_twh': [round(float(w[1]), 1) for w in written],
            'peak_mw': [int(round(float(w[2]))) for w in written]}


def stage_existing_solar():
    """Existing solar generation profiles per checkpoint, from the design weather year."""
    import numpy as np, paths, lp_model as lp
    w = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    for year in (2030, 2035, 2040, 2045):
        np.save(paths.intermediate(f'exist_solar_{year}.npy'), lp.exist_solar_mw(year) * w['solar'])
    return {'years': [2030, 2035, 2040, 2045]}


def stage_chained_weather():
    """Chains the eight derived hydrological weather years into one continuous 70,080-hour series.

    Continuity across year boundaries is the point: it is what allowed the seasonal iron-air
    drawdown to be observed at all. Resetting storage state annually would have hidden it.
    """
    import numpy as np, paths
    order = ['hydro_year_2012_13.npz', 'hydro_year_2013_14.npz',
             'hydro_year_2014_15_RECONSTRUCTED.npz', 'hydro_year_2015_16_RECONSTRUCTED.npz',
             'hydro_year1_2016_17_RECONSTRUCTED.npz', 'hydro_year_2017_18_RECONSTRUCTED.npz',
             'hydro_year_2018_19.npz', 'hydro_year_2019_20.npz']
    parts = {'solar': [], 'wind': [], 'nuclear': [], 'exist_solar': []}
    for fn in order:
        d = np.load(paths.weather_year(fn))
        for k in parts:
            if k in d:
                parts[k].append(d[k][:8760])
    chained = {k: np.concatenate(v) for k, v in parts.items() if v}
    np.savez(paths.intermediate('chained_8yr_weather.npz'), **chained)
    return {'years_chained': len(order), 'hours': int(len(chained['solar']))}


def stage_scenario2_capacity():
    """Statutory Floor gas capacity under both standards, all checkpoints."""
    import numpy as np, paths, driver as drv, lp_model as lp
    from scenario2_reserve_margin import compare_capacity_standards
    w = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    rows = []
    for year in (2030, 2035, 2040, 2045):
        demand = np.load(paths.intermediate(f'demand_{year}fy_va_only.npy'))
        exist = np.load(paths.intermediate(f'exist_solar_{year}.npy'))
        solar = 16100.0 if year >= 2035 else 16100.0 * (year - 2026) / 9
        r = compare_capacity_standards(
            demand, w['nuclear'], exist, w['solar'], w['wind'], solar,
            drv.vcea_short_duration_floor_mw(year), drv.vcea_long_duration_floor_mw(year),
            bath_county_mw=lp.BATH_MW)
        r['year'] = year
        rows.append(r)
    import csv
    out = paths.result('scenario2_capacity_standards.csv')
    with open(out, 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
    return {'checkpoints': [r['year'] for r in rows],
            'reserve_margin_gas_mw': [int(round(float(r['reserve_margin_gas_mw_storage_credited']))) for r in rows]}


def stage_dsm_incentive_comparison():
    """Avoided-cost comparison for the DSM incentive section, on current peaker costs."""
    import csv, paths
    import large_ci_curtailment_derived as derived
    rows = [dict(derived.avoided_generation_capacity_cost_comparison(c), case=c)
            for c in ('low', 'central', 'high')]
    out = paths.result('dsm_avoided_cost_comparison.csv')
    keys = [k for k in rows[1] if not k.endswith('note')]
    with open(out, 'w', newline='') as fh:
        wr = csv.DictWriter(fh, fieldnames=keys, extrasaction='ignore')
        wr.writeheader()
        wr.writerows(rows)
    central = rows[1]
    return {'central_aeroderivative_pct': central['aeroderivative_incentive_as_pct_of_avoided_cost'],
            'central_fclass_pct': central['fclass_incentive_as_pct_of_avoided_cost']}


STAGES = [
    Stage('demand', 'Virginia-only hourly demand per checkpoint',
          ['data/intermediates/demand_2030fy_va_only.npy',
           'data/intermediates/demand_2035fy_va_only.npy',
           'data/intermediates/demand_2040fy_va_only.npy',
           'data/intermediates/demand_2045fy_va_only.npy'],
          stage_demand_arrays,
          source_files=['DOMLSEHourlyLoadProjections2024through2048.csv']),

    Stage('existing_solar', 'Existing solar profiles per checkpoint',
          [f'data/intermediates/exist_solar_{y}.npy' for y in (2030, 2035, 2040, 2045)],
          stage_existing_solar),

    Stage('chained_weather', 'Eight weather years chained continuously (70,080 h)',
          ['data/intermediates/chained_8yr_weather.npz'],
          stage_chained_weather),

    Stage('scenario2_capacity', 'Statutory Floor gas capacity, both standards',
          ['results/scenario2_capacity_standards.csv'],
          stage_scenario2_capacity,
          inputs=['demand', 'existing_solar']),

    Stage('dsm_incentives', 'DSM avoided-cost comparison on current peaker costs',
          ['results/dsm_avoided_cost_comparison.csv'],
          stage_dsm_incentive_comparison),
]


def print_graph():
    print("\nPipeline stages, in dependency order:\n")
    for i, s in enumerate(STAGES, 1):
        dep = f"  (needs: {', '.join(s.inputs)})" if s.inputs else ""
        src = f"  [source data: {', '.join(s.source_files)}]" if s.source_files else ""
        print(f"  {i}. {s.name:<20} {s.description}{dep}")
        if src:
            print(f"     {src.strip()}")
        for o in s.outputs:
            print(f"       -> {o}")
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--force', action='store_true',
                    help='rebuild every stage even if its outputs already exist')
    ap.add_argument('--graph', action='store_true', help='print the stage graph and exit')
    ap.add_argument('--only', metavar='STAGE', help='run one named stage only')
    ap.add_argument('--verbose', action='store_true',
                    help="show the modules' import-time capex banners (suppressed by default)")
    args = ap.parse_args()

    if args.graph:
        print_graph()
        return 0

    print("=" * 72)
    print("Virginia Energy Plan modeling pipeline")
    print("=" * 72)

    problems = check_environment()
    if problems:
        print("\nEnvironment problems found -- nothing was run:\n")
        for p in problems:
            print(f"  * {p}")
        print("\nSee SETUP.md for full setup instructions.\n")
        return 1
    print(f"Environment OK  (Python {sys.version_info.major}.{sys.version_info.minor})")

    import paths
    from provenance import RunManifest
    paths.ensure_directories()
    print(f"Repository root: {paths.REPO_ROOT}\n")

    stages = [s for s in STAGES if not args.only or s.name == args.only]
    if args.only and not stages:
        print(f"No stage named '{args.only}'. Known stages: {', '.join(s.name for s in STAGES)}")
        return 1

    ran = already_built = blocked = failed = 0
    all_stages_by_name = {s.name: s for s in STAGES}   # full set, not the --only filtered view
    for i, stage in enumerate(stages, 1):
        label = f"[{i}/{len(stages)}] {stage.name}"

        unmet = stage.unmet_prerequisites(all_stages_by_name)
        if unmet:
            print(f"{label}: SKIPPED -- missing outputs from: {', '.join(unmet)}")
            print(f"           Run those stages first:  python3 run_all.py --only {unmet[0]}")
            blocked += 1
            continue

        missing = stage.missing_sources()
        if missing:
            print(f"{label}: SKIPPED -- source data not present: {', '.join(missing)}")
            print(f"           See docs/DATA_SOURCES.md; place files in {paths.SOURCE_DATA}")
            blocked += 1
            continue

        if stage.outputs_exist() and not args.force:
            print(f"{label}: already built (use --force to rebuild)")
            already_built += 1
            continue

        print(f"{label}: {stage.description}")
        started = time.time()
        try:
            summary = stage.function()
        except Exception as exc:
            elapsed = time.time() - started
            print(f"FAILED after {elapsed:.0f}s")
            print(f"           {type(exc).__name__}: {exc}")
            traceback.print_exc()
            failed += 1
            continue   # later independent stages may still succeed; dependants will skip cleanly
        elapsed = time.time() - started
        print(f"           done ({elapsed:.0f}s)")
        if summary:
            for k, v in summary.items():
                print(f"           {k}: {v}")

        RunManifest(
            record_id=f'stage-{stage.name}',
            description=stage.description,
            parameters={'stage': stage.name, 'outputs': stage.outputs},
            input_file_paths=[os.path.join(paths.REPO_ROOT, o) for o in stage.outputs],
            build_results=summary or {},
            runtime_seconds=round(elapsed, 1),
        ).write_json(paths.manifest(f'{stage.name}.json'))
        ran += 1

    print("\n" + "=" * 72)
    parts = [f"{ran} run"]
    if already_built:
        parts.append(f"{already_built} already built")
    if blocked:
        parts.append(f"{blocked} blocked")
    if failed:
        parts.append(f"{failed} failed")
    print("Complete: " + ", ".join(parts))
    if blocked:
        print("\nBlocked stages were missing either their source data or an upstream stage's")
        print("outputs. Each line above says which. For source data, place the named file in")
        print(f"{paths.SOURCE_DATA} (see docs/DATA_SOURCES.md); for upstream outputs, run that")
        print("stage first, or run the whole pipeline with no --only filter.")
    print(f"Results:   {paths.RESULTS}")
    print(f"Manifests: {paths.MANIFESTS}")
    print("=" * 72 + "\n")
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
