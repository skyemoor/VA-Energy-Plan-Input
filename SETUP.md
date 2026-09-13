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

## Solving a checkpoint

`solve_checkpoint.py` runs one scenario checkpoint and saves the hourly supply-demand shadow
prices — the measurement that shows whether the model produces intraday price structure.

```bash
# the 2045 measurement (issue #1)
python3 solve_checkpoint.py --year 2045 --scenario 3 --merit-order

# without the merit order, for comparison
python3 solve_checkpoint.py --year 2045 --scenario 3
```

**Prerequisites.** Source CSVs are gitignored (re-downloadable) and intermediates are gitignored
(rebuildable), so a fresh clone has neither:

1. Put `DOMLSEHourlyLoadProjections2024through2048.csv` and
   `PJMMidAtlAPSrt_hrl_lmpsAug2025aug2026.csv` in `data/source/`
2. `python3 run_all.py` — builds all intermediates, a few minutes
3. Then solve

`solve_checkpoint.py` checks its inputs first and names the exact `run_all.py` command to rebuild
anything missing, rather than failing partway through with a `KeyError`.

**Expect it to take a while.** A checkpoint is **up to four LP solves** — `converge_frac` iterates
up to three times searching for the gas fraction that hits the target share, then solves once more
at the converged value. At 2030 those run 77–137 s each; 2045 is larger. A large gap at `iter0` is
normal and shrinks each iteration.

**Options.** `--scenario {1,1B,2,3}`, `--capacity-basis {nameplate,net_summer,net_winter}`
(default `net_summer`; net winter is 11.4% higher and the DOM zone now peaks in winter — see
`assumptions.GAS_SEASONAL_BASIS_NOTE`), and `--verbose`.

**`--verbose` is worth using on a long run.** It echoes the inputs before solving — demand peak and
mean, solar and wind CF, nuclear, distributed CF, exogenous price, gas target share — so a wrong
input is visible in the first second rather than after twenty minutes. At the end it prints a
**dual profile**: percentiles from p0 to p100, the share of hours priced at or above each merit-order
rung, and the share above $200 and $1,000/MWh.

That profile is the actual finding. A count of unique values says the dual is not flat; the
percentiles say whether it has a realistic *shape* — real Virginia nodes show most hours in a narrow
band with a small number of extreme hours, and a dual that is merely stepped between four rung
prices would look very different from one with genuine scarcity tails.

**Outputs** land in `results/`:

| file | contents |
|---|---|
| `duals_{scenario}_{year}_{merit\|flat}.npy` | 8,760 hourly shadow prices, $/MWh |
| `solve_{scenario}_{year}_{merit\|flat}.json` | build MW, converged frac, dual summary |
| `hourly_{scenario}_{year}_{merit\|flat}.csv` | **8,760-row dispatch stack** — the View 1 chart |

**The hourly CSV matches the `View1_*` sheets in the tracker workbook**: demand, solar potential,
wind, nuclear, curtailment (negative), unserved, and per-technology discharge / charging (negative)
/ state of charge in MWh and %, plus gas and the hourly dual. Suppress with `--no-hourly` if the
~1 MB file is unwanted.

**It also prints a curtailment check**, which exists because the dual profile alone could not answer
the obvious question it raised — *if a third of hours sit at the curtailment floor, what serves the
evening?* Duals say what a marginal MWh is worth; they say nothing about what physically
dispatched. The check reports how many hours curtail, what share of those are in daylight
(anything curtailing at night is a defect), total curtailed TWh, and whether storage actually
reaches full state of charge — curtailing while storage has headroom would be a real problem rather
than an artifact of scale.

The JSON's `dual_unique_values` is the headline number. **Before the merit order, 2030 gave 1
unique value across all 8,760 hours.** With it, 40. If a run reports 1, the script warns — that
means the model has returned to a single effective price and no intraday result from it is usable.

## Comparing pathways (overnight)

```bash
nohup python3 run_pathway_comparison.py --scenario 3 --merit-order > pathway.log 2>&1 &
tail -f pathway.log
```

Runs **both** pathways in one call and reports the comparison:

| | |
|---|---|
| **A — myopic chain** | 2030 → 2035 → 2040 → 2045, each carrying the prior build forward as a floor |
| **B — target-first** | 2045 standalone, no prior build |

**Five checkpoint solves, 60–90 minutes.** See
`docs/methodology/Experiment_Pathway_Foresight.md` for why this is an open question rather than a
settled choice.

**Built for unattended running:**

- **Results are written after every checkpoint**, not at the end — a run that fails on the last
  solve keeps the first four. Progress lands in `results/pathway_progress_{scenario}.json` and is
  renamed to `pathway_comparison_{scenario}.json` on completion.
- **A failed pathway does not kill the other.** If the chain fails at 2040, the target-first solve
  still runs and both partial results are reported with the traceback recorded.
- **Every line is timestamped and flushed**, so `tail -f` shows where a stalled run stopped.

**It uses the reserve-margin solver variants** (`Scenario1WithReserveMargin`,
`Scenario3WithReserveMargin`) and warns for any scenario lacking one. `solve_checkpoint.py` uses the
plain classes and therefore applies **no reserve margin** — which is how a full 2045 run was made
without one on 2026-09-12.

**What to look for in the output:**

| | meaning |
|---|---|
| `final systems agree` | the literature predicts a similar 2045 system with differing pathways — this tests it |
| build deltas marked `MATERIAL` | above 2%; below that is rounding |
| `myopia penalty` | our **endpoint annual** cost gap, read against the literature's **cumulative NPC** range of 14–23%. **Not directly comparable** — the output says so |
| `iron-air deferral` | whether the chain builds the whole long-duration fleet in the final checkpoint, which would be implausible against any real deployment rate |
