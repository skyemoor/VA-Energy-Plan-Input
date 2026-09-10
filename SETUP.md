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
python3 run_all.py --verbose        show the modules' import-time capex banners
```

Stages whose outputs already exist are skipped, so an interrupted run resumes where it stopped
rather than starting over.

## Source data

Large public datasets are **not** committed — they are re-downloadable, and storing them would
bloat the repository without adding verifiability. Stages needing them are skipped with a message
naming the file.

Place them in `data/source/`. See `docs/DATA_SOURCES.md` for what each file is and where to get
it. The main one is Dominion's hourly load projection, which is accepted under any of these
filenames — this dataset circulates under several naming conventions and you do not need to
rename yours:

```
DOMLSEHourlyLoadProjections2024through2048.csv
DOM-LSE-HourlyLoadProjections-2024-through-2048.csv
DOM_LSE_HourlyLoadProjections_2024_through_2048.csv
```

The filename is checked first, then the columns. A file with an accepted name but a different
internal layout — a `_formatted` variant using `DateTime`/`MWh` rather than
`Year`/`Month`/`Day`/`1`–`24` — reports which columns are missing and which are present, rather
than failing obscurely.

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

A clean checkout gives **212 passed, 52 skipped, 0 failed**.

Skips are expected, not problems. Tests needing large source data (NSRDB irradiance, SAM exports)
or modules recorded as not-yet-restored in `docs/PIPELINE_COMPLETENESS.md` skip with a reason
naming what they need. Run `pytest -rs` to list them.

Suites whose modules are absent entirely are ignored at collection, determined by attempting the
import rather than from a maintained list — so a suite un-ignores itself the moment its module is
restored, instead of staying silently skipped.

**A failure means something is actually wrong.** That distinction is the point: a suite that
reports red on a clean checkout trains people to ignore it.

## If something fails

The pipeline reports the stage, the exception and a traceback rather than failing silently.
Common cases:

| Message | Meaning |
|---|---|
| `'scipy' not installed` | Run the pip command in step 2 |
| `SKIPPED -- source data not present` | Put the named file in `data/source/` and re-run |
| `SKIPPED -- needs output from: <stage>` | An upstream stage did not run; fix that one first |
| `source data file not found` | Same as above, with the search paths listed |

A blocked stage is not an error. Stages that do not depend on the missing input still run, so a
partial result set is produced rather than nothing. Re-running after adding the file executes only
the stages that were blocked — everything already built is skipped.

Nothing writes outside the repository directory.
