# Appendix: PHIUS Core / HVAC Efficiency Standard Stock-Turnover Model

Built 2026-08-23. Projects Virginia's energy savings from (a) PHIUS Core envelope conservation on
new residential and school construction, and (b) progressively higher HVAC efficiency standards
(residential SEER2/HSPF2, school IEER) phased in via natural equipment replacement, from 2026
through 2045.

**Code location**: `/home/claude/work/lp_package/`
- `efficiency_assumptions.py` -- every sourced input parameter, single source of truth
- `building_stock_turnover_model.py` -- the simulation engine (`HVACEfficiencyStockModel`,
  `EfficiencyTier`, `StockTurnoverResult`, including `energy_saved_mwh()`)
- `test_building_stock_turnover_model.py` -- 30 tests, all passing
- `run_efficiency_projection.py` -- orchestration script producing the per-stream results (%
  and MWh) below
- `efficiency_projection_outputs/` -- generated CSVs and figure
- `build_scenario3_hourly_demand.py` -- applies the combined MWh reduction to this project's
  existing hourly demand checkpoints, producing Scenario 3's own hourly demand set
- `test_build_scenario3_hourly_demand.py` -- 7 tests, all passing
- `scenario3_hourly_outputs/` -- generated Scenario 3 `.npz`/`.csv` hourly demand files

**Internal debugging/design-decision log**: `Internal_Debugging_Log.md` entries #56-60.

---

## 1. Executive summary

Three parallel efficiency standards were modeled: residential cooling (SEER2), residential heating
(HSPF2), and school HVAC (IEER), each stepping up from a current baseline to a 2028 standard and
then a 2035 standard, phased in as equipment reaches natural end-of-life -- residential equipment
assumed at a 14-year average lifespan (DOE/AHRI's own rulemaking figure), school HVAC assumed at a
21.3-year average lifespan (ASHRAE's own live Service Life Database, actually-replaced "Packaged DX
unit, rooftop" equipment -- a genuinely different, longer figure, not the same rate reused across
streams; see Section 3) -- or as new construction enters the stock (new construction gets both the
higher HVAC standard AND PHIUS Core's own envelope conservation reduction; replacement-only units
get the HVAC standard alone, since PHIUS is a building-envelope standard that does not retroactively
apply when only the HVAC equipment is swapped).

**Headline results** (energy savings %, relative to a counterfactual where the same, growing stock
remained entirely at today's baseline efficiency -- i.e. this isolates the standards' own effect
from the separate effect of stock growth):

| Stream | 2028 | 2035 | 2040 | 2045 |
|---|---|---|---|---|
| Residential Cooling (SEER2 + PHIUS) | 2.1% | 14.5% | 23.9% | 30.5% |
| Residential Heating (HSPF2 only*) | 1.4% | 9.9% | 19.4% | 25.6% |
| School HVAC (IEER + PHIUS) | 1.8% | 13.2% | 22.5% | 29.8% |

*PHIUS's own combined heating+cooling reduction figure is attributed entirely to the Cooling row in
this table for reporting purposes -- see Section 4 for why, and do not sum the Cooling and Heating
rows together.

Full year-by-year figures, and the underlying stock composition each year, are in the CSVs and
figure referenced above.

**MWh headline results** (absolute energy savings, additive across residential streams -- see
Section 8 below for sourcing and Section 4 for why school combines heating+cooling into one figure):

| Stream | 2028 | 2035 | 2040 | 2045 |
|---|---|---|---|---|
| Residential Cooling | 165,263 MWh | 1,214,211 MWh | 2,108,291 MWh | 2,815,909 MWh |
| Residential Heating | 81,649 MWh | 639,325 MWh | 1,315,541 MWh | 1,820,708 MWh |
| School HVAC | 2,554 MWh | 19,216 MWh | 33,634 MWh | 45,531 MWh |

---

## 2. Methodology

This model follows a four-phase structure, adapted from a draft methodology the user supplied at
the start of this build -- with the phase structure kept, but the actual calculations corrected
where the draft's own approach was found to contain material errors (see Section 5).

### Phase 1: Establish the baseline

Each stream starts from a defined stock size and a defined baseline efficiency rating at simulation
start (2026):

- **Residential** (cooling and heating share the same physical stock): 2,444,031 units (Dominion's
  own 2018 IRP Appendix 2E, 2026 projection row -- Dominion service territory, not statewide
  Virginia; see Section 6 for the scope caveat).
- **School**: 1,812 buildings (VDOE 2024-25 data, via USSchoolIndex.org).

### Phase 2: Model stock turnover

Two inflows add fresh units to whichever efficiency tier is currently active each year:

1. **Replacement**: existing stock turns over at a stream-specific rate, not a single shared
   figure. Residential (cooling and heating): 1/14 = ~7.1%/yr, DOE/AHRI's own 14-year average
   heat-pump lifespan assumption (used directly in federal rulemaking cost-benefit analyses).
   School: 1/21.3 = ~4.7%/yr, ASHRAE's own live Service Life and Maintenance Cost Database figure
   for "Packaged DX unit, rooftop" equipment specifically -- see Section 3 for the full sourcing
   and its small-sample caveat.
2. **New construction**: residential adds 27,500 units/yr (midpoint of Virginia DHCD's own
   25,000-30,000/yr range); schools add 9 buildings/yr (VDOE's own 2024-25 actual count).

New-construction units, and only new-construction units, also receive PHIUS Core's own 51.1%
heating+cooling energy reduction (see Section 4 for the derivation of this figure).

### Phase 3: Apply the efficiency differential formula

For a rated-value standard (SEER2, HSPF2, IEER), the energy-use reduction from switching a unit
from a baseline rating to a new rating, to deliver the same thermal output, is:

```
Energy Savings (%) = (1 - Baseline_Rating / New_Rating) x 100
```

This is not an approximation -- it follows directly from the definition of these ratings as
BTU-output-per-watt-hour-input ratios. For the one target that is not a rated value (school's 2035
"~50% below conventional baseline" DOE Technology Challenge target), the reduction is used directly
as stated, with no conversion needed.

### Phase 4: Aggregate stock-weighted savings

Each simulated year, every stock pool (six per stream: legacy/2028-tier/2035-tier, crossed with
whether PHIUS applies) is multiplied by its own energy-use fraction and summed, producing a
stock-weighted aggregate energy-use index for that year. Comparing this to what the SAME stock size
would use if it had remained entirely legacy-tier, no-PHIUS gives the reported savings percentage.

---

## 3. Sourced assumptions

| Parameter | Value | Source | Confidence |
|---|---|---|---|
| Residential heat pump lifespan | 14.0 years | DOE/AHRI TSD rulemaking assumption (via EGIA Contractor University) | Confirmed |
| Residential annual replacement rate | 7.14%/yr | Derived: 1/14 | Derived |
| School HVAC ("Packaged DX unit, rooftop") lifespan | 21.3 years (mean age at actual replacement) | ASHRAE's own live Service Life and Maintenance Cost Database (costdatabase.ashrae.org), queried 2026-08-23 | Confirmed, empirical, small sample (n=5 replacement events) |
| School annual replacement rate | 4.69%/yr | Derived: 1/21.3 | Derived |
| Residential cooling baseline | 14.3 SEER2 | DOE Southeast-region minimum, VA explicitly named | Confirmed |
| Residential cooling 2028 target | 18.0 SEER2 | Project policy decision | Decision |
| Residential cooling 2035 target | 22.0 SEER2 | Project policy decision | Decision |
| Residential heating baseline | 7.5 HSPF2 | Federal minimum, national (not region-differentiated) | Confirmed |
| Residential heating 2028 target | 9.0 HSPF2 | Project policy decision | Decision |
| Residential heating 2035 target | 12.0 HSPF2 | Project policy decision | Decision |
| School HVAC baseline | 13.9-14.5 IEER (midpoint 14.2 used) | DOE commercial HVAC efficiency standards summary | Confirmed, range |
| School HVAC 2028 target | 20.8 IEER | DOE High Performance RTU Challenge; already-certified products (Daikin Rebel, Carrier WeatherExpert) | Confirmed, demonstrated |
| School HVAC 2035 target | ~50% below conventional RTU baseline | DOE Commercial Building HVAC Technology Challenge (Better Buildings Accelerator); Carrier's 10-14 ton unit completed DOE lab validation Sept. 2025 | Confirmed, dated program target |
| PHIUS Core heating+cooling reduction | 51.1% (vs. Virginia's actual 2021 IECC baseline) | Derived: Emu Report's 55.7% (vs. 2018 IECC) rebased using DOE's own 9.38% 2018-to-2021-IECC improvement figure | Derived, two-source chain |
| Residential starting stock (2026) | 2,444,031 | Dominion 2018 IRP Appendix 2E | Confirmed, Dominion territory only |
| Residential new construction | 27,500/yr (midpoint of 25,000-30,000) | Virginia DHCD HB854 Housing Study | Confirmed, range |
| School starting stock (2026) | 1,812 | VDOE 2024-25 data (via USSchoolIndex.org) | Confirmed |
| School new construction | 9/yr | VDOE 2024-25 Annual Cost Data Report (actual) | Confirmed, single-year |
| School renovation projects | 46/yr | VDOE 2024-25 Annual Cost Data Report (actual) | Confirmed, single-year; NOT fed into simulation (see Section 6) |

"Decision" rows are this project's own chosen policy targets, not external facts -- kept as
overridable constructor parameters in the code (`efficiency_assumptions.py`), not hardcoded
literals, per Software_Engineering_Standards.md Rule 8.

---

## 4. The PHIUS-attribution-to-one-stream decision

PHIUS Core's own 51.1% reduction figure was measured, in its original source (the Emu Report), as a
single, combined heating+cooling site-energy figure -- there is no sourced way to split it separately
between the residential cooling and residential heating streams without introducing a new, unsourced
assumption (e.g., "60% of PHIUS's benefit is heating, 40% cooling"). This model resolves that by
attributing the full PHIUS reduction to the Cooling stream's own reporting only, with an explicit
warning (both in code comments and in the console output of `run_efficiency_projection.py`) that the
Cooling and Heating rows must not be summed. The SEER2/HSPF2 equipment-only contribution IS additive
and separable between the two streams; only the PHIUS envelope contribution is not, since it was
never measured as two separate figures in the first place. This is a reporting-attribution choice,
not a claim that heating-side envelope improvements contribute zero real-world benefit.

---

## 5. School HVAC replacement rate: full derivation

The original model (Internal_Debugging_Log.md #56) applied the residential 14-year/7.1%-per-year
figure uniformly to all three streams, flagged explicitly at the time as an unverified
simplification. Direct user follow-up questions led to sourcing a school-specific figure instead.

**Search path**: a static citation (2003 ASHRAE Applications Handbook, Chapter 36: "15 years as the
estimated service life for rooftop air conditioners," cross-confirmed by a second source citing the
same figure) was found first and considered, but a live, empirical, continuously-updated alternative
was located and preferred: ASHRAE's own public **Service Life and Maintenance Cost Database**
(costdatabase.ashrae.org), which as of the query date (2026-08-23) contains 38,946 individual
equipment service-life records across 345 real buildings.

**Locating the right equipment category**: the database's "Cooling" and "Heating" system-type
categories are predominantly central-plant equipment (chillers, boilers, geothermal heat
exchangers) -- not the packaged rooftop units schools actually use. The correct category, "Packaged
DX unit, rooftop," is filed under the database's own "Air Distribution" system type instead
(confirmed by reviewing the database's full HVAC Equipment List before querying).

**The two figures the database reports for this equipment type, and why 21.3 (not 15.6) was chosen**:

| Metric | n | Mean | Median |
|---|---|---|---|
| Currently-in-service units (still running, not yet replaced) | 215 | 15.6 yrs | 16.0 yrs |
| Actually-replaced units (real replacement events) | 5 | **21.3 yrs** | 22.0 yrs |

The "currently in service" figure is a *lower bound* on true lifespan, not a lifespan measurement
itself -- it is simply the current age of units that have not yet failed, and will keep aging before
eventual replacement. The "actually replaced" figure measures the exact quantity this model's
replacement-rate mechanism requires: age at the point a unit was actually swapped out. Per direct
user instruction, 21.3 years (the actually-replaced mean) was adopted.

**The honest caveat, stated plainly rather than buried**: only 5 replacement events are recorded for
this equipment type in the entire database. This is real, empirical data -- not a marketing estimate
or a single old handbook citation -- but a sample of 5 carries meaningful sampling uncertainty that a
larger sample would narrow. If ASHRAE's database accumulates more replacement records in the future
(it is continuously updated by reporting buildings), this figure should be re-queried and, if it has
shifted materially, updated here with a new debugging-log entry documenting the change.

**Resulting rate**: `1 / 21.3 = 4.69%/yr`, applied to the school HVAC stream only
(`ea.ANNUAL_SCHOOL_HVAC_REPLACEMENT_RATE`), distinct from and slower than the residential
`ea.ANNUAL_HVAC_REPLACEMENT_RATE` (7.14%/yr, unchanged). See `Internal_Debugging_Log.md` #58 for the
full session record, and `test_building_stock_turnover_model.py`'s own
`test_school_hvac_replacement_rate_is_distinct_from_and_slower_than_residential` for the regression
guard against these two constants ever being accidentally conflated in a future edit.

---

## 6. Corrections made to the user-provided draft methodology

The user's own initial draft (a four-phase structure with an embedded Python simulation) was
reviewed before this model was built, and four material issues were identified and corrected:

1. **Internally inconsistent SEER baseline.** The draft's 2028 calculation used both 14.3 SEER2 and
   15 (old-SEER) baselines; its 2035 calculation silently used only the old-SEER figure, producing a
   ~3.2-percentage-point understatement once SEER2 was confirmed as the standard to use throughout
   (31.8% stated vs. 35.0% correct).
2. **The draft's own simulation used `seer_legacy = 14.5`**, matching neither its stated legal
   minimum (14.3 SEER2) nor its stated "operating stock average" claim (12-13 SEER, itself never
   independently sourced) -- and Phase 1 of the draft explicitly argued the operating average should
   be *lower* than the legal minimum, which its own simulation value contradicted.
3. **No separate new-construction stream** -- the draft's simulation held total stock fixed at
   1,000,000 units for the full 20-year run, silently omitting the additive new-construction growth
   already established elsewhere in this project's own work.
4. **No PHIUS integration, and no school/IEER stream at all.**

All four are corrected in the model this appendix documents; see `Internal_Debugging_Log.md` #56
for the full review detail.

---

## 8. Converting the relative efficiency index into actual MWh

Everything above (Sections 1-7) describes a RELATIVE, unit-weighted efficiency index -- `total_stock
- energy_use_index` gives a savings figure in "units," not energy, under the implicit assumption
that every unit in a stream consumes the same average baseline energy. Converting this into actual
MWh requires a per-unit annual kWh figure, one that did not exist anywhere in this model until
directly requested.

**Residential (EIA 2020 RECS, Table CE5.3a, South Atlantic division -- confirmed to include
Virginia)**: these are CONDITIONAL averages -- kWh per household that actually uses electricity for
the given end use, not blended across all households regardless of fuel type. The correct
denominator, since this model's residential streams represent electric-HVAC households specifically.

| End use | kWh/household/yr |
|---|---|
| Space heating | 2,401 |
| Air conditioning | 3,112 |

**School (EIA 2018 CBECS, two-table derivation)**: Table C14 gives Education buildings' total
electricity (293,000 kWh/building/yr, all end uses). Table E3 gives Education's own
electricity-specific end-use split (heating 5.7% of total, cooling 20.6%). Applying E3's shares to
C14's total gives the per-building figures below. Cross-checked (Rule 4) by confirming the two
tables imply a consistent underlying building population (~437,000 electricity-using education
buildings nationally -- plausible given CBECS's Education category is broader than K-12 alone).
**Unlike the residential figures, this is a national average, not Virginia-specific** -- CBECS's
Table E3 does not cross-tabulate building type and census division simultaneously the way RECS does.

| End use | kWh/building/yr |
|---|---|
| Space heating | ~16,760 |
| Cooling | ~60,360 |

**Two sources were tried and rejected before finding the CBECS Table E3 breakdown**: (1) Dominion's
own 2018 IRP Figure 5.5.1 ("Residential Energy Intensities") was found to be genuinely corrupted in
the source PDF's own text extraction -- numbers misaligned with their own row/column labels,
confirmed directly via `pdftotext` extraction and grep, not assumed -- and was abandoned rather than
force-fit into the model. (2) A nationally-reported 42%/11% heating/cooling share for education
buildings was correctly flagged, before use, as likely an all-fuels (not electricity-only) share,
which would have overstated the true electric-heating portion specifically, since schools commonly
use gas heat -- superseded once Table E3's own electricity-specific figures were located.

**New method**: `StockTurnoverResult.energy_saved_mwh(per_unit_kwh_baseline)`, computing
`[total_stock - energy_use_index] * per_unit_kwh_baseline / 1000`. School HVAC uses the SUM of the
school heating and cooling figures (77,120 kWh/building/yr combined), not either alone, since the
school stream's own IEER-based index represents a single combined-function RTU, not separately-
tracked heating/cooling pools the way the residential streams are. Residential Cooling and
Residential Heating MWh figures ARE additive between the two streams (unlike the % figures, which
would double-count PHIUS if summed -- see Section 4); each has its own, separately-sourced per-unit
figure and its own SEER2/HSPF2 savings.

See `Internal_Debugging_Log.md` #59 for the full session record.

---

## 9. Scenario 3 hourly demand set

Direct user request: apply the efficiency model's own combined MWh reductions to this project's
existing hourly demand data, producing a distinct Scenario 3 hourly demand set -- not a temperature-
based hourly reshaping (an earlier, unrequested direction this session began pursuing and was
directly corrected out of; see `Internal_Debugging_Log.md` #60 for that record in full).

**Method** (`build_scenario3_hourly_demand.py`): for each of this project's own existing demand
checkpoints (`checkpoint_YYYY_demand_v2.npz` -- 2030, 2035, 2040, and 2045_46, matched to the
efficiency model's own 2030/2035/2040/2045), the combined MWh reduction (summed across all three
streams) is divided by that checkpoint's own real annual total to produce a single scale factor,
applied identically to every one of the 8,760 hours in that year's array.

**Results**:

| Checkpoint | Original annual MWh | Combined efficiency MWh saved | Scale factor | Scenario 3 annual MWh |
|---|---|---|---|---|
| 2030 | 110,864,000 | 709,709 | 0.993598 | 110,154,291 |
| 2035 | 136,645,000 | 1,872,752 | 0.986295 | 134,772,248 |
| 2040 | 162,077,000 | 3,457,465 | 0.978668 | 158,619,535 |
| 2045_46 | 186,462,000 | 4,682,148 | 0.974890 | 181,779,852 |

Outputs (both `.npz`, matching this project's existing checkpoint convention, and `.csv`, matching
the `VA_YYYY_ScenarioN_hourly_*.csv` convention already used for Scenario 1) are written to
`lp_package/scenario3_hourly_outputs/`, each CSV carrying both the original and Scenario-3-adjusted
arrays side by side.

A safety guard (`build_scenario3_checkpoint()`) raises `ValueError` if the combined reduction would
ever meet or exceed a checkpoint's own original annual total -- which would produce zero or negative
demand -- rather than silently clipping to zero.

**LIMITATION, stated explicitly**: this is a UNIFORM annual scale factor, identical across all 8,760
hours. It does NOT capture PHIUS/HVAC efficiency's own disproportionate reduction of peak heating/
cooling-driven hours specifically -- an envelope upgrade cuts a cold January evening's heating load
by more than an already-low April night's load. This was the explicit, direct build instruction; an
hourly-shape-aware refinement remains available as genuine follow-up work if later requested, not
something this build silently assumes is equivalent to the simpler uniform-scaling approach actually
used.

**Scope note**: this covers only the efficiency-driven demand-reduction layer of Scenario 3.
Scenario 3's other, originally-defined elements (rooftop/parking-canopy solar with FERC 2222
participation, agrivoltaic siting, retail day-ahead/real-time pricing) remain entirely separate,
not-yet-integrated work.

---

## 10. Limitations and open items (efficiency-standard model itself)

- **Geographic scope mismatch**: the residential new-construction rate (25,000-30,000/yr) is
  Virginia-statewide (DHCD); the residential starting stock (2,444,031) is Dominion service
  territory only. Judged an acceptable simplification (Dominion serves ~85-90% of Virginia) rather
  than a blocking issue, but not reconciled to a single consistent geography.
- **School renovation figure (46/yr) not used in the simulation.** Deliberately excluded to avoid
  double-counting against the natural replacement mechanism already driving the model. As a
  cross-check, now recalculated with the school-specific 4.69%/yr rate (Section 5): 1,812 schools x
  4.69%/yr implies ~85 school-buildings/yr reaching HVAC end-of-life -- still meaningfully larger
  than the 46/yr VDOE renovation-project count, though closer than the original, residential-rate-
  based estimate of ~129/yr. This gap remains an unresolved sanity-check discrepancy, not
  investigated further this session (possible explanations include: not every school building has
  independently-tracked HVAC replacement each cycle, or VDOE's renovation-project count undercounts
  routine swaps that don't rise to a formally tracked "project").
- **Uniform replacement rate WITHIN each stream's own three tiers.** The model now uses two
  genuinely distinct rates ACROSS streams (residential 7.14%/yr vs. school 4.69%/yr, Section 5), but
  still applies one single rate uniformly across the legacy/2028-tier/2035-tier pools WITHIN each
  stream. No data was available to support the alternative hypothesis (e.g. newer, higher-efficiency
  equipment failing at a different rate than older equipment within the same stream).
- **Linear (not Weibull) retirement curve**: equipment is assumed to reach end-of-life at a fixed
  rate rather than following a distribution around the average. This does not change the long-run
  (2035/2045) cumulative penetration figures, since both approaches converge to the same steady-
  state replacement rate, but would slightly change the year-to-year transition shape.
- **Commercial buildings remain entirely unmodeled**, per the project's own explicit "requires
  information" scoping decision made earlier in this work.
- **Not yet integrated into the hourly demand model.** This is a standalone, annual-resolution
  demand-reduction projection. Feeding these results into `checkpoint_solver.py`'s own hourly demand
  curves (including PHIUS's own disproportionate peak-load-reduction effect, since envelope/HVAC
  improvements cut peak heating/cooling demand harder than baseload) is explicit follow-up work, not
  yet started.
