# Session handoff — 2026-09-14

**Head:** `a400946` · **Tag:** `pre-lp-restructure` · **1,386 tests · 18 audit checks · 4 LP
fingerprints identical to baseline**

Read this, then `docs/Common_Reference.md` section 4 if you are picking up the LP restructuring, or
`docs/Scenario_Completion_Dashboard.md` for anything else.

---

## Where things stand

**Scenario 2 is complete, steps 1–11.** Everything else waits on Scenario 1.

| | 2026 | 2035 | 2045 |
|---|---:|---:|---:|
| clean share | 47.4% | 45.7% | **31.6%** |
| annualised cost | $2.4B | $6.1B | **$10.9B** |

**SLCOE $36.35/MWh** with terminal value, **band $29.59–$37.02** across three gas cases.
**Societal $122.33/MWh.** Central capex basis, design weather year.

---

## The one thing in flight

**`build_problem` is being restructured** and is roughly one-third done. Rule 15 sets a complexity
limit of 15; it measures **67** across 830 lines with 30 `if` statements, and one scenario's logic
scattered over five separate LP layers.

**Done:** the fingerprint harness, two row builders (`emit_energy_balance_rows`,
`emit_bath_state_of_charge_rows`, five call sites), `LpSegmentSpec`, `apply_segment_spec`, and the
base-class hook returning an empty spec.

**Next, and this is the risky step:** populate Scenario 3's spec, then replace the five
`enable_distributed_segment` sites with spec consumption. **That flag is still under its old name in
the code** — `enable_additional_distributed_segment` was agreed as the better name and never
applied, so grep for the old one (18 occurrences in `lp_model.py`). Renaming it is part of the next
step, not something already done. **The figures can move here if
anything is wrong**, where every step so far has been pure addition.

**Before touching it:**

    python3 scripts/capture_lp_baseline.py     # must report 4 problems IDENTICAL

**And note the gap:** Scenario 3 has never been solved on the current model, so its fingerprint is a
shape check rather than a verified result. If the extraction perturbs it subtly, nothing catches
that until Scenario 3 actually runs. The other three are protected by fingerprints *and*
baseline-locked tests.

**To abandon:** `git checkout pre-lp-restructure`.

---

## What the session changed, and why each mattered

**Scenario 2's gas fleet was unbounded.** `solve()` defaulted to a 200,000 MW ceiling, so the
published run dispatched gas that does not exist and reported zero unserved energy, while a bounded
run showed 30.05 TWh at 2045. Every downstream figure rested on the wrong specification. Fixed on
the existing `apply_gas_cap` hook.

**The merit-order stack had never run.** Ported, tested and committed a session earlier — and
`Scenario2Solver.solve` never passed the kwargs, so every reported figure burned 132 TWh at a flat
6.40 heat rate. **Audit check 18 now catches this class**: import is not invocation.

**The gas-price flag was inert for the same reason.** The rungs carry their own cost coefficients and
hard-coded the Deloitte path. Caught because an EIA run returned a figure *identical to the cent* —
had it come back at $34 it would have been accepted.

**Checkpoint sizing failed twice.** The new-gas requirement is **not monotonic**: 2031 needs a unit,
2032 and 2033 need none, 2034 needs one again, because statutory solar outpaces load growth for two
years. Rule 9's invariant check caught both failures. Now measured year by year.

**Thermal cycling is priced, not forbidden.** `MAX_ANNUAL_STARTS` was nearly made a hard invariant;
it is a screening-curve device, not a dispatch constraint, and `ccgt_legacy` sits at 89% of it — one
derating change from blocking every run. **$645M/yr at 2045, 6% of total**, which also settles the
mixed-integer question: nobody should build 52,560 binaries for 6%.

---

## Three findings a reader should not lose

**The two statutory solar requirements work against each other.** § 56-585.5(D)(2)'s one-time
16,100 MW capacity target and § 56-585.5(C)(2)'s growing annual energy obligation from ≤1 MW
resources. By 2045 the carve-out is 60% of new build, and fixed-tilt delivers ~4.4 TWh less than the
tracking it displaces.

**The mandated storage is insufficient, not idle.** Against the real fleet it discharges 13 TWh and
18 TWh still goes unserved. An earlier reading had it sitting unused; that was wrong.

**Roughly 70% of Scenario 2's new gas is the no-imports boundary.** 6,547 MW with no imports, about
2,000 MW at Virginia's actual 20% share. **Neither end is the answer** — a flat demand reduction is
more generous than imports, which are shaped, but in a scarcity year PJM may be tight exactly when
Virginia is. Reported as a range throughout.

---

## What the observed fleet data settled

EIA plant-level generation for Virginia's gas fleet, capacity-weighted by merit-order rung,
2022–2024: **66.8% / 47.8% / 7.0%**, tracking modelled heat rates 6.40 / 7.55 / 11.00 exactly. That
confirms the rung structure from *outside* the model.

**A proposal to cap capacity factor at observed levels was considered and rejected.** Capacity
factor is a dispatch *outcome* carrying three confounds that would not transfer to 2045: regional
supply, merchant-versus-rate-base ownership, and market conditions that swung `ccgt_fleet` from
41.3% to 56.1% in three years. Availability stays the constraint; the observed figures are a
benchmark.

---

## Open items, in the order they block things

1. **Wire the carve-out into Scenarios 1, 1B and 3** — Scenario 2's implementation is the model, and
   the restructuring puts it in the core rather than per-scenario.
2. **Re-run Scenario 1**, then 1B and 3.
3. **The compliance sweep**, 75–100% — the whitepaper's primary axis, and nothing else is blocking
   it once Scenario 1 runs.
4. **Scenario 3's siting cap** (issue #14) blocks that scenario entirely.
5. **Forced-outage draws** for LOLE and CVaR — scoped, costed at 2.5 hours for 3,000 scenarios, not
   built.
6. **`PJMMap.webp` as the NSRDB data-root marker** — a map image standing in for solar data, which
   produced two misleading failures this session.

---

## Source data: the archive, and what supersedes what

**The repository deliberately excludes large source data** — `.gitignore` drops `*.csv` on the
grounds that it is public and re-downloadable. That is right for a public repo, but it left the
NSRDB irradiance, NOAA weather, PJM market, EIA fleet and GIS siting data with no version-controlled
home, accumulated across two machines with some of it possibly lost.

**`project_knowledge_base_2026-09-18.zip` consolidates it** — 180 files, 71 MB compressed, grouped
into twelve folders with a manifest giving each dataset's provenance and where to re-download it.
Will is uploading it to the project knowledge base, so it should be available in the next session as
it is today.

**What is NOT in it, because the repository has it:** all model code, tests, appendices, working
documents, the citation register, the tracker, session handoffs, and the derived weather years and
distributed solar profiles under `data/weather_years/`.

### Three documents in that archive are superseded and must be read as such

`documents/Virginia_Energy_Plan_Input.docx`, `documents/Executive_Legislative_Summary.md` and
`documents/Technical_Official_Summary.md` predate the current results by several corrections. Their
figures put Scenario 2's direct cost at **$43.77–$49.43/MWh** against the current **$29.59–$37.02**,
and Scenario 1 and 1B at values that predate the Bath County correction, the retirement schedules,
the distributed carve-out, the merit-order stack and the bounded gas fleet. One of them still leads
with a scenario-comparison table on levelised cost, which is the framing this project moved away
from — **the headline is the compliance curve, with annualised cost primary and levelised cost
informal.**

**Two things in them remain valuable.** The DER policy material in the `.docx` — aggregator market
access, distribution upgrades, DER caps, Direct Transfer Trip, near-term recommendations — is not
yet in the repository at all and is scheduled to become Appendix H. And the summaries' habit of
disclosing their own prior errors in the text is a posture worth keeping, and is carried into
`docs/whitepaper/Executive_Summary_Draft.md`.

---

## Things worth knowing that are easy to miss

**The measured parallel scaling is machine-specific and counterintuitive.** On a 16-core workstation
throughput peaks at **8 concurrent solves**, and 4 jobs × 2 workers beat 1 job × 8 by 12%. Going
past the peak makes things *worse*. `scripts/time_concurrent_jobs.py` measures it; I reasoned wrongly
about this twice before measuring.

**`gas_cost_mwh` returns $/MMBtu at `heat_rate=1.0`; the other price functions always return
$/MWh.** Mixing them gives a 6.4× error that looks plausible. Use `lp_model.gas_price_mwh`.

**Appendices are for end readers; working documents are for the collaboration.** Material migrates
one way, rewritten rather than copied, when a subject is finalised. `appendices/APPENDIX_ORDER.md`
holds the agreed sequence — sixteen entries in reader order, DER at H. **Fourteen exist as files**;
B is a working-notes document to be promoted and G is to be assembled from the Scenario 3 working
document.

**Two appendices carry superseded figures and say so at the top.** That is not drift; it is awaiting
migration.

---

## What the next session starts with

**The repository** — code, tests, appendices, working documents, registers, and the derived data
under `data/weather_years/`. Everything this session produced is committed.

**A source-data archive**, `project_knowledge_base_2026-09-18.zip`, 71 MB, to be uploaded to the
project knowledge base. 180 files in twelve folders with a manifest: NSRDB irradiance for six sites
2012–2020, PVWatts output runs, NOAA weather records, offshore wind, PJM market data, EIA fleet and
plant generation, GIS siting polygons, reference PDFs, and the standalone scripts. **The repository
deliberately excludes this** — `.gitignore` drops `*.csv` on the grounds that it is public and
re-downloadable — so the archive is its only consolidated home, and the manifest records where each
dataset came from in case any of it needs replacing.

**Three documents in that archive predate the current results and should not be read for figures.**
`Virginia_Energy_Plan_Input.docx`, `Executive_Legislative_Summary.md` and
`Technical_Official_Summary.md` were superseded several times over — the last of them reports
Scenario 2 at $43.77–$49.43/MWh against the current $29.59–$37.02, on a horizon to 2050 rather than
2045, before the bounded gas fleet, the carve-out, agrivoltaic siting, the merit order and thermal
cycling.

**They are worth keeping for one thing:** their DER policy material — aggregator market access,
distribution upgrades, DER caps, Direct Transfer Trip, and near-term recommendations — is not in the
repository and is the largest unversioned piece of the project. It is scheduled to become Appendix
H. `docs/whitepaper/Executive_Summary_Draft.md` supersedes the summary drafts for everything else.

---

## What I would do differently

**I reported figures three times before they were stable**, because each correction revealed the
next. A reader of the working documents will see SLCOE at $32.80, $31.81 and $36.35 in successive
entries. The build log explains each move, but the churn was avoidable had the bounded-fleet
question been asked first.

**And two defects hid behind plausible-looking results.** The merit order and the gas-price flag both
produced numbers that looked reasonable. What caught them was an *identical* figure and a call-graph
trace — not review of the output. **That is the argument for the structural audit being routine
rather than requested.**
