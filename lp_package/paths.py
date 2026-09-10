"""
paths.py

Single source of truth for every filesystem location this project reads or writes.

WHY (2026-09-10)

A dependency audit of `scripts/` found absolute paths to three different roots hardcoded across
the scripts -- `/tmp`, `/home/claude/work`, and `/mnt/user-data/uploads` -- none of which exist on
a user's own machine. Several scripts also passed derived intermediates to each other through
`/tmp` with no recorded production order, on a filesystem that resets between sessions. The
practical effect was that the repository could not reproduce its own results from a clean clone,
despite the README saying it could.

Rule 6 applies to paths as much as to constants: a path used in more than one place belongs in one
place. Everything here resolves relative to the repository root, so a clone works wherever it
lands.

LAYOUT

    data/weather_years/     derived hourly weather years (committed -- small, expensive to rebuild)
    data/intermediates/     derived arrays produced by one stage and consumed by another
                            (NOT committed -- reproducible from source by running run_all.py)
    data/source/            large public source data (NOT committed -- see docs/DATA_SOURCES.md)
    results/                final outputs intended to be read by a person
    results/manifests/      one run manifest per stage, recording inputs, parameters and versions

The `data/source/` convention is new here. Scripts previously expected source CSVs in
`/mnt/project/`, which is specific to the environment this project was developed in. That path is
still checked first so existing setups keep working, with `data/source/` as the portable fallback.
"""
import os


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LP_PACKAGE = os.path.join(REPO_ROOT, 'lp_package')
SCRIPTS = os.path.join(REPO_ROOT, 'scripts')
DOCS = os.path.join(REPO_ROOT, 'docs')

DATA = os.path.join(REPO_ROOT, 'data')
WEATHER_YEARS = os.path.join(DATA, 'weather_years')
INTERMEDIATES = os.path.join(DATA, 'intermediates')
SOURCE_DATA = os.path.join(DATA, 'source')

RESULTS = os.path.join(REPO_ROOT, 'results')
HOURLY_DISPATCH = os.path.join(RESULTS, 'hourly_dispatch')
MANIFESTS = os.path.join(RESULTS, 'manifests')

REGISTERS = os.path.join(REPO_ROOT, 'registers')

# Development-environment source location, checked before the portable one so existing setups
# continue to work unchanged.
_LEGACY_SOURCE_DATA = '/mnt/project'


def ensure_directories():
    """Creates the writable directories if absent. Safe to call repeatedly."""
    for d in (INTERMEDIATES, RESULTS, HOURLY_DISPATCH, MANIFESTS):
        os.makedirs(d, exist_ok=True)


# Known filename variants for the same underlying dataset. This project has repeatedly received
# the same file under different naming conventions -- nsrdb_data.py already carries equivalent
# handling for two NSRDB conventions. Requiring users to rename a file they legitimately have is a
# poor trade against a few lines of alias resolution.
#
# CAUTION: an alias means "same dataset, different filename", NOT "same layout". The
# `_formatted` variant referenced by demand_shape_interpolation.py carries DateTime/MWh columns
# rather than Year/Month/Day/1-24, so callers must still verify the columns they need are present
# -- see require_columns() below.
SOURCE_FILE_ALIASES = {
    'DOMLSEHourlyLoadProjections2024through2048.csv': [
        'DOM-LSE-HourlyLoadProjections-2024-through-2048.csv',
        'DOM_LSE_HourlyLoadProjections_2024_through_2048.csv',
        'DOMLSEHourlyLoadProjections2024through2048.csv',
    ],
}


def require_columns(dataframe, columns, filename):
    """Rule 5: fail with the actual column list rather than a KeyError several frames deep.

    Filename aliasing resolves WHERE a file is, not WHAT is in it. A variant of the same dataset
    can carry a different layout, so anything resolved by alias should pass through here before
    use.
    """
    missing = [c for c in columns if c not in dataframe.columns]
    if missing:
        raise ValueError(
            f"{filename} is missing expected column(s): {missing}\n"
            f"  Columns present: {list(dataframe.columns)[:12]}"
            f"{' ...' if len(dataframe.columns) > 12 else ''}\n"
            f"  This file may be a differently-formatted variant of the same dataset. "
            f"See docs/DATA_SOURCES.md.")
    return dataframe


def source_file(filename):
    """Absolute path to a large source data file, checking the development location first.

    Rule 5: raises with actionable guidance rather than returning a path that does not exist, so a
    missing input fails at the point it is needed with an explanation, not later with an opaque
    numpy error.
    """
    candidates = SOURCE_FILE_ALIASES.get(filename, [filename])
    if filename not in candidates:
        candidates = [filename] + candidates
    for root in (_LEGACY_SOURCE_DATA, SOURCE_DATA):
        for name in candidates:
            candidate = os.path.join(root, name)
            if os.path.exists(candidate):
                return candidate
    tried = '\n    '.join(candidates)
    raise FileNotFoundError(
        f"source data file not found: {filename}\n"
        f"  Looked in: {_LEGACY_SOURCE_DATA} and {SOURCE_DATA}\n"
        f"  Accepted filenames (any one of these works):\n    {tried}\n"
        f"  Large source data is not committed to this repository -- it is public and "
        f"re-downloadable.\n"
        f"  See docs/DATA_SOURCES.md for what this file is and where to obtain it, then place it "
        f"in:\n    {SOURCE_DATA}")


def weather_year(filename):
    return os.path.join(WEATHER_YEARS, filename)


def intermediate(filename):
    return os.path.join(INTERMEDIATES, filename)


def result(filename):
    return os.path.join(RESULTS, filename)


def manifest(filename):
    return os.path.join(MANIFESTS, filename)
