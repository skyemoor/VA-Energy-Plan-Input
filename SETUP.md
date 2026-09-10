# Setup

Everything here runs on public data with four standard Python packages. No solver licence, no
compilation, no configuration files to edit.

## 1. Install Python 3.9 or newer

**Linux (Debian/Ubuntu)**
```
sudo apt update && sudo apt install python3 python3-pip
```

**macOS** — `brew install python3`, or download from python.org

**Windows** — download from python.org and tick "Add Python to PATH" during install

Check it:
```
python3 --version
```

## 2. Install the four packages

```
pip install numpy scipy pandas openpyxl
```

That is the complete dependency list. **HiGHS, the linear solver this project uses, ships inside
SciPy** — `scipy.optimize.linprog(..., method='highs-ds')` is what the code calls, so installing
SciPy installs the solver. There is nothing separate to obtain or licence.

Optional, only for re-deriving solar capacity factors from raw NSRDB files:
```
pip install NREL-PySAM
```

## 3. Clone and run

```
git clone https://github.com/skyemoor/VA-Energy-Plan-Input.git
cd VA-Energy-Plan-Input
python3 run_all.py
```

The pipeline checks your environment first and reports anything missing in plain language before
running. Outputs land in `results/`.

## Useful flags

```
python3 run_all.py --graph          show the stage graph and exit, run nothing
python3 run_all.py --only demand    run one named stage
python3 run_all.py --force          rebuild everything, ignoring existing outputs
```

Stages whose outputs already exist are skipped, so an interrupted run resumes where it stopped
rather than starting over.

## Source data

Large public datasets are **not** committed — they are re-downloadable, and storing them would
bloat the repository without adding verifiability. Stages needing them are skipped with a message
naming the file.

Place them in `data/source/`. See `docs/DATA_SOURCES.md` for what each file is and where to get
it. The main one is Dominion's hourly load projection,
`DOMLSEHourlyLoadProjections2024through2048.csv`.

Derived weather years **are** committed (`data/weather_years/`) — small, and expensive to rebuild.

## What you get

| Location | Contents |
|---|---|
| `results/` | Final outputs, CSV |
| `results/manifests/` | One JSON per stage: parameters, input file hashes, runtime |
| `data/intermediates/` | Derived arrays passed between stages (rebuildable; not committed) |

**Start with `registers/Provenance_Register.xlsx`** before citing any figure. Every result carries
a status — `current`, `provisional`, or `superseded` — and most 2045 figures are provisional,
resting on stated limitations documented there.

## Running the tests

```
cd tests && python3 -m pytest -q
```

Some pre-existing suites cannot yet be collected because they need feature modules absent from the
repository — see `docs/PIPELINE_COMPLETENESS.md`. The suites covering the current modeling
package all pass.

## If something fails

The pipeline reports the stage, the exception and a traceback rather than failing silently.
Common cases:

| Message | Meaning |
|---|---|
| `'scipy' not installed` | Run the pip command in step 2 |
| `SKIPPED -- source data not present` | Put the named file in `data/source/` |
| `source data file not found` | Same, with the search paths listed |

Nothing writes outside the repository directory.
