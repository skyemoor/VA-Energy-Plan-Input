# Weather-Year Robustness: Three Approaches, Approach 1's Extensions, and Findings

Built 2026-08-23, specifically to survive conversation compression without
information loss. This is the operational reference for continuing this
work -- exact file paths, function signatures, and numbers, not just a
summary. `/tmp/*.npz` files referenced below are ephemeral (this
environment's filesystem resets between sessions) -- if they're gone,
regenerate using the documented scripts/parameters, don't assume they
still exist. `/home/claude/work/lp_package/*.py` files are the persistent,
reusable code.

## Why this work exists

Scenario 1/1B/2's own build sizing has always used a single, established
weather year (2016-17, `hydro_year1_2016_17.npz`) for every checkpoint
solve. Entry #47 (prior session) established 2016-17 as the min-max-robust
choice among three tested years (2016-17/2013-14/2012-13) via cross-
testing -- a real, demonstrated result, not an assumption. This session's
work asks a further question: does a build sized against one weather year
generalize to *other* real weather years, tested individually and chained
together, and does it maintain genuine reserve adequacy throughout, not
just avoid unserved energy.

## The three approaches, explicitly defined (this distinction caused real confusion mid-session -- keep it precise)

**Approach 1: reserve-margin enforcement mechanism** -- how "does the
system have adequate margin" gets checked/enforced. Not about which
weather years or how many are tested; about *what the check itself
verifies* and *when*.
- 1a (superseded): single-hour check, existing project code
  (`driver.add_reserve_margin_constraint()`), only verifies the one,
  global peak-*net-load* hour.
- 1b (built this session): post-hoc, all-hours audit function
  (`verify_reserve_margin_all_hours.py`), checks every hour of an
  already-solved dispatch result.
- 1c (built this session, current standard): LP-integrated, all-hours
  constraint (`chained_dispatch_test.add_all_hours_reserve_margin_constraint()`),
  enforced *during* the solve itself, not just audited afterward.

**Approach 2: multi-year dispatch-only cross-testing** -- take an
ALREADY-FIXED build (S_mw/PNA_mw/ENA_mwh/EFE_mwh unchanged from the
original 2016-17-sized 2040 checkpoint) and test whether it holds up
against different weather-year sequences, chained end-to-end with
continuous SoC carry-over (not reset per year). This is what every test
this session has actually been -- including the "harsher ordering"
request. **Chaining more years together, or a harsher ordering, does NOT
make something approach 3** -- it's still approach 2 as long as the build
size itself is never re-solved.

**Approach 3: multi-year simultaneous build-sizing** -- NOT YET BUILT.
The build size itself (S_mw, PNA_mw, ENA_mwh, EFE_mwh) becomes a decision
variable solved simultaneously against multiple weather years at once, so
the resulting build is provably sufficient for all of them by
construction, rather than tested after the fact against a build sized for
only one year. This is the natural next step if approach 2 testing
reveals the current build is genuinely undersized -- not yet triggered,
since every approach-2 test so far has passed.

## Approach 1's extensions, in the order they were actually built

1. **SoC floors (heuristic, superseded as the primary mechanism)**:
   direct bounds on `nsoc`/`fsoc` in `build_dispatch_problem()`'s own
   `problem['bounds']`. User-specified: Na floor 20%, IA/Fe floor 0%
   (asymmetric by design -- Na is the fast-response, daily-cycling asset,
   IA is meant to be drawable to empty during genuine multi-day droughts).
   Worked empirically (zero unserved energy, all-hours reserve audit
   later showed it also incidentally resolved all 769 shortfall hours),
   but is NOT a provable guarantee -- just happened to be sufficient for
   this build/these years.

2. **Post-hoc all-hours audit** (`verify_reserve_margin_all_hours.py`,
   function `check_all_hours_reserve_margin()`): takes an already-solved
   dispatch result's actual hourly `nsoc`/`fsoc` arrays, computes
   `min(rated_power, actual_soc[t])` as the real available discharge at
   each hour (not assumed-full), sums against nuclear/gas_cap/wind/solar,
   checks `>= (1+IRM)*demand[t]` at every hour. This is what found the
   769-shortfall-hour result below. Does not modify the LP -- read-only
   verification of an already-solved result.

3. **LP-integrated all-hours constraint** (`chained_dispatch_test.py`,
   function `add_all_hours_reserve_margin_constraint()`): the real fix.
   Adds two new decision variables per hour (`na_reserve[t]`,
   `fe_reserve[t]`), zero cost, representing capacity held back
   specifically for the margin requirement:
   - `nd[t] + na_reserve[t] <= PNA_mw`
   - `na_reserve[t] <= nsoc[t]`
   - `fd[t] + fe_reserve[t] <= EFE_mwh/FE_DURATION`
   - `fe_reserve[t] <= fsoc[t]`
   - `nuclear[t] + gas_cap_mw + wind[t] + na_reserve[t] + fe_reserve[t] +
     solar_avail[t] >= (1+IRM)*demand[t]`
   Takes an already-built `build_dispatch_problem()` output and extends
   it (new columns via `sparse.hstack`, new rows via `sparse.vstack`) --
   does not rebuild from scratch. Validated: re-running the post-hoc
   audit against a solve using this constraint showed 7 "shortfall"
   hours, all at exactly -0.000000 MW (floating-point noise, not a real
   violation) -- confirmed by inspecting each to 10 decimal places.

4. **`init_na_frac`/`init_fe_frac` extension to `build_dispatch_problem()`**
   (`lp_model.py`): the function's own `init_soc_frac` was a single
   scalar applied uniformly to bath/Na/Fe. Extended with two new,
   optional parameters (default `None`, falling back to `init_soc_frac`
   -- zero behavior change for any existing caller that doesn't pass
   them). Needed because chaining a new weather sequence starting from a
   *prior* chain's own actual ending SoC requires different starting
   fractions for Na and Fe (they end at different values), which the
   single scalar couldn't express.

5. **`t_peak` → `t_peak_net_load` rename** (`checkpoint_solver.py`,
   `driver.py`): not a reserve-margin extension per se, but found and
   fixed in the course of this work. The ambiguous name directly caused
   a real analysis error mid-session (checking `argmax(demand)` instead
   of the actual saved peak-*net-load* hour). Renamed throughout both
   live modules; older one-off scripts
   (`solve_2030_reserve_margin_FINAL.py` etc.) left as historical
   artifacts, not maintained.

## Key findings, with data

### The eight hydro years, and two real data-quality corrections made along the way

| Hydro year | File | Status |
|---|---|---|
| 2012-13 | `hydro_year_2012_13.npz` | Validated -- correct parser confirmed |
| 2013-14 | `hydro_year_2013_14.npz` | Validated -- correct parser confirmed |
| 2014-15 | `hydro_year_2014_15.npz` | Built 2026-08-23 -- wind CF max=0.8176 (wake-loss ceiling confirmed) |
| 2015-16 | `hydro_year_2015_16.npz` | Built 2026-08-23 -- wind CF max=0.8176 (wake-loss ceiling confirmed) |
| 2016-17 | `hydro_year1_2016_17.npz` | Established standard (entry #47) |
| 2017-18 | `hydro_year_2017_18.npz` | Built this session -- see below |
| 2018-19 | `hydro_year_2018_19.npz` | Already existed, used as-is |
| 2019-20 | `hydro_year_2019_20.npz` | Already existed, used as-is |

**Full, consecutive 8-year set (2012-2020), no remaining gaps** -- the
raw-data gap at calendar-year 2015 that made 2014-15/2015-16
unassemblable is now closed (user provided 2015 solar and CVOW data
2026-08-23). Built via `build_hydro_2014_15_and_2015_16.py`, reusing the
already-validated `parse_cvow_cf_flat()`/`blended_solar_cf()`
(`build_hydro3_2012_13_2013_14.py`) for 2014/2015's own flat-format CVOW
and standard solar, and `parse_cvow_cf()` (`build_new_weather_years.py`)
for 2016's own matrix-format CVOW. One new, small gap found and closed
along the way: 2016's own raw solar data exists under the "insolation"
naming convention (same pattern as 2017's own files), not in
`build_new_weather_years.py`'s own `SOLAR_FILES` dictionary (which only
covers 2018-2020) -- added a dedicated `blended_solar_cf_2016()`
directly in the new script rather than modifying the existing,
already-validated module.

**Two real bugs found and fixed while assembling the original six-year
set** (both a matter of "verify format/units directly, never assume" --
entry #23's own established discipline, reapplied):
- `hydro_year2_2013_14.npz` and `hydro_year3_2012_13.npz` (a separate,
  "numbered" naming batch, bundled with a demand array of unverified
  provenance) were found to disagree with the validated parser on wind
  CF (0.4689 vs 0.4594 for 2012-13; 0.4582 vs 0.4490 for 2013-14).
  Freshly recomputing from raw source using the validated
  `parse_cvow_cf_flat()` (in `build_hydro3_2012_13_2013_14.py`) exactly
  reproduced the lower, "un-numbered" file's own values, confirmed via
  the independently-known ~0.8176 wake-loss ceiling matching exactly.
  The numbered files are unreliable; use the un-numbered pair.
- 2017's CVOW data was originally only available as
  `2017CVOWhourlyout.csv` -- a single, unlabeled `kWh` column with no
  timestamp, a third distinct format from the other two already-known
  CVOW layouts. A naive parse gave a nonsensical mean CF of 0.0004;
  the column header turned out to be mislabeled (values are actually
  MWh, not kWh) -- confirmed when the user later provided the genuine
  SAM output (`2017CVOWhourlymatrixkWhWake140mresults.csv`, standard
  367-column matrix format) and it matched the unit-corrected
  reconstruction hour-by-hour exactly (max diff 0.000000, correlation
  1.000000). `build_hydro_2017_18.py` now sources from the primary SAM
  file directly, with the reconstruction retained only as a documented
  cross-check, not the production path.

### "Worst year" splits three ways, none coincide -- the core empirical finding this whole session's work supports

All results below: Scenario 1's 2040 checkpoint build (S_mw=54,625.3,
PNA_mw=23,678.6, ENA_mwh=168,489.7, EFE_mwh=300,000.0), dispatch-only
(fixed build), demand held at 2040's own established level throughout.

| Year | Achieved gas share | Curtailment GWh | Winter GWh | Winter share |
|---|---|---|---|---|
| 2012-13 | 19.36% | 14,125 | 3,597 | 13.9% |
| 2013-14 | 19.33% | 11,479 | 3,963 | 15.4% |
| 2016-17 (established) | 19.89% | 14,270 | 4,406 | 16.6% |
| 2017-18 | 18.78% | 14,685 | 4,317 | 17.2% |
| **2018-19** | **22.64%** | 12,828 | 4,513 | **14.9% (lowest)** |
| **2019-20** | 21.02% | 15,971 | **5,041** | **18.0% (highest)** |

Statutory target: 21%.

- **2016-17 = reliability-sizing-worst** (entry #47's own min-max-robust
  finding, established prior session, not re-derived here).
- **2018-19 = compliance-percentage-worst** (only year clearly exceeding
  21%) -- **and its own elevated total is a summer/August phenomenon, not
  winter** -- has the *lowest* winter share of all six years. Verified
  directly via month-by-month gas dispatch: August alone accounts for
  +1,524 GWh vs. 2016-17; February actually runs the *opposite*
  direction (2016-17 needed more gas in February than 2018-19 did).
- **2019-20 = winter-specific-worst** (highest winter share AND highest
  absolute winter gas need) -- but is NOT the compliance-worst year
  overall.
- **No genuine multi-day cold-snap event appears in any of the six
  years** -- searched directly for sustained (48+ consecutive hour)
  above-90th-percentile winter net-load events; longest found across all
  six years is 20 hours. This is a real sample-size limitation (n=6,
  still small), not evidence PJM's own winter-risk framing doesn't apply
  to Virginia.

### 5-year compliance-averaging check (tests whether a CA-style multi-year RPS window would solve the variability problem)

All C(6,5)=6 possible 5-year averages, using the achieved shares above:

| Excluded year | 5-year average | vs. 21% cap |
|---|---|---|
| 2019-20 | 20.00% | under |
| 2018-19 | 19.68% | under |
| 2017-18 | 20.45% | under |
| 2016-17 | 20.23% | under |
| 2013-14 | 20.34% | under |
| 2012-13 | 20.33% | under |

**Every possible 5-year average stays under 21%**, even though 2 of 6
individual years exceed it. Direct, computed evidence (not a hypothetical)
that a CA-style multi-year averaging window (see
`CA_NY_PJM_Reliability_Compliance_Comparison_2026-08-23.md`) would have
resolved Virginia's own compliance-variability problem for this exact
build.

### Reserve-margin deep dive: `t_peak_net_load` verification and the real 769-hour finding

Once the naming/formula confusion was resolved (checking the FULL
formula -- nuclear + gas_cap + wind + PNA + solar -- not solar alone, and
using each year's own actual peak-net-load hour, not a shared one), the
existing 2040 build passes the single-hour IRM=17.7% check comfortably
for all four originally-tested years (+29% to +36% margin). This
single-hour check is NOT sufficient on its own, though:

**Post-hoc all-hours audit against the unconstrained 4-year chain
(2016-17→2017-18→2018-19→2019-20, demand fixed at 2040's level) found
769 shortfall hours out of 35,040 (2.2%)** -- every one of them
invisible to the single-hour check. Worst margin: -8,317.9 MW at hour
26,813 (2019-20, hour 533 within that year). Shortfalls cluster early in
the chain, driven by Na SoC hitting genuine 0%.

**The already-tested 20% Na floor, run through the same audit, resolved
all 769 hours to zero** -- a direct, empirically-confirmed link between
the SoC-floor work and the reserve-margin finding, though as noted above,
this is empirical, not a provable guarantee the way the LP-integrated
constraint (extension 3, above) is.

### Chained multi-year dispatch results (approach 2), all using the LP-integrated all-hours reserve constraint as of the most recent runs

**4-year chain, 2016-17→2017-18→2018-19→2019-20** (`/tmp/2040_4year_chain_allhours_reserve.npz`):
zero unserved energy, achieved_share=20.61%, reserve-margin audit clean
(7 hours at exactly -0.000000 MW). Solve time 32.2s for 35,040 hours,
560,640 variables, 175,201 constraint rows.

**3-year "harsh" chain, 2017-18→2018-19→2019-20, fresh start (50%)**
(`/tmp/2040_3year_harsh_chain.npz`): zero unserved, achieved_share=20.84%.
Every single year hits ~0% Fe SoC at some point (`min-in-year Fe` = -0.0%
for all three years) -- a harder stress pattern than the 4-year chain
showed. Reserve margin held (same 7-hour floating-point noise).

**Same 3-year chain, starting from 2016-17's own actual ending SoC**
(Na=30.0%, Fe=5.6%, via the new `init_na_frac`/`init_fe_frac` parameters)
(`/tmp/2040_3year_harsh_chain_from_201617_endpoint.npz`): zero unserved,
achieved_share=20.84%. Results barely moved from the fresh-start version
(18.90%/22.65%/20.97% vs. 18.76%/22.64%/21.13% per year) -- the build
had enough margin to absorb the extra initial deficit too. One honest
wrinkle: reported initial SoC came out to Na=27.3%/Fe=4.6%, not exactly
30.0%/5.6% -- the hour-0 constraint ties the *starting balance* to the
target value, but the solver can still charge/discharge at hour 0 itself
if economically useful, so the literal reported value can differ
slightly. Not a bug; an existing characteristic of the SoC formulation
used throughout this project, just not previously inspected this closely.
The chain's own *ending* SoC came out to exactly Na=30.0%/Fe=5.6%,
confirming the periodic boundary (start≈end) still holds precisely at
the far end.

## Open, not-yet-done items (needed to actually continue this work)

1. **Relaxed-ending-SoC run** -- proposed, not yet built. Every chain so
   far forces the final hour back to a specific SoC (the periodic
   boundary constraint `bsoc[T-1] == init_bath`, and equivalently for
   Na/Fe). This gives the LP perfect foresight of its own required
   endpoint, letting it plan a multi-year drawdown/recovery strategy a
   real operator wouldn't have visibility into. A run that removes this
   terminal constraint (letting the system end wherever it naturally
   would) would show whether the "zero unserved energy" results above
   are a genuine, sustainable finding or partly an artifact of known-
   endpoint optimization. Needs: modify `build_dispatch_problem()`'s own
   `bsoc[T-1]==init_bath`/`nsoc[T-1]==init_na`/`fsoc[T-1]==init_fe` rows
   to remove the equality (or convert to a much looser inequality/no
   constraint at all) for the specific chain length being tested.

2. **2015 data** -- CLOSED 2026-08-23. User provided raw solar
   (Albemarle/Chesapeake/King George) and CVOW wind data for calendar-
   year 2015; `hydro_year_2014_15.npz` and `hydro_year_2015_16.npz` both
   built and validated (wind CF max=0.8176 for both, matching the
   wake-loss ceiling). This closes the full 2012-2020 raw-data span --
   all 8 possible consecutive hydro years now exist, no remaining gaps.
   Next natural step: extend the chained-dispatch testing (approach 2)
   beyond the current 3-4 year chains to the full 8-year sequence, now
   that all the source data exists.

3. **Approach 3 (multi-year simultaneous build-sizing)** -- not started.
   Only worth building if approach 2 testing (once the relaxed-ending-SoC
   run and/or more years are tested) actually reveals the current,
   2016-17-sized build is undersized for a harder sequence. Every test so
   far has passed, so this hasn't been triggered yet -- don't build it
   speculatively.

4. **Whether the LP-integrated all-hours reserve constraint
   (`add_all_hours_reserve_margin_constraint()`) should replace the
   existing single-hour constraint (`driver.add_reserve_margin_constraint()`)
   in the STANDARD, single-year checkpoint-solving process** -- not just
   the chained-test infrastructure built this session. This would be a
   genuinely project-wide methodology change (affecting Scenario 1/1B/2's
   own established checkpoint solves, not just this robustness-testing
   work), and hasn't been proposed or decided yet. Worth raising
   explicitly before assuming it should happen.

5. **Cross-reference this document against
   `CA_NY_PJM_Reliability_Compliance_Comparison_2026-08-23.md`** -- the
   5-year compliance-averaging finding above directly supports that
   document's own California multi-year-compliance-period discussion;
   the two haven't been formally linked yet.
