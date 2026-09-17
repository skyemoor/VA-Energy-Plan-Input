# Appendix — Scenario 2 Methodology

**Extracted 2026-09-14 from `Reorganized_Appendices_Draft.md`, where it existed only inside a 4,682-line composite file.** That draft also carried stale copies of five appendices that have their own authoritative files; this one had no standalone version at all, which made it invisible to the index, untestable, and impossible to revise without editing a file about something else.

Lettering is deliberately omitted here. The scheme is being reworked into reader order (methods, scenarios, topics, reference) and a letter baked into the filename now would be wrong twice.

> **FIGURES SUPERSEDED 2026-09-14.** Every cost in this appendix predates the bounded gas fleet,
> the C.2 distributed carve-out, agrivoltaic siting, the merit-order stack and thermal cycling cost.
> Scenario 2's current result is **$36.35/MWh levelised, $10.86B annualised at 2045, 31.6% clean
> share**, with a gas-price band of $29.59–$37.02. See
> `docs/scenarios/Scenario2_Working_Document.md`, which is authoritative.
>
> **The METHOD text here is still useful** and is why this was extracted rather than deleted — it
> documents how the scenario was constructed, and much of that construction still stands. Read it
> for approach, not for numbers.

---

### C.1 Structural Difference from Scenarios 1/3
Solar and storage are fixed inputs (linear buildout to VCEA statutory
minimums — 16,100 MW solar/wind by 2035 per Va. Code SS56-585.5(D)(2), then
flat; 16,000 MW short-duration and 4,000 MW long-duration storage [CORRECTED
2026-08-16, was misquoted as 3,480 MW -- verified directly against the
statute text, SS56-585.5(E)(4): "4,000 megawatts of long-duration energy
storage capacity," half by Dec. 31, 2035, remainder by Dec. 31, 2045], ramping
linearly to 2045 per Va. HB895/SB448), not LP-optimized decision variables.
Only dispatch is optimized against fixed capacities.

### C.2 CCGT Sizing
Sized directly to cover each checkpoint's worst single hourly gap, crediting
storage with zero contribution — a deliberately conservative simplification
in place of a full joint optimization of CCGT size with storage
pre-positioning, which was set aside to conserve session scope.

### C.2.1 Correction: Per-Checkpoint Statutory Minimums (was: one flat figure applied to every year)

**Code location**: `lp_package/solve_scenario2.py`.

**The error, caught before completing the very first solve**: the initial
2030 run used a single, flat set of targets for every checkpoint — 16,200
MW solar, 16,000 MW Na-power, 4,000 MW iron-air — treating the *2035/2045
end-state* targets as if they applied to 2030 as well. Va. Code
§56-585.5's actual text, fetched and read in full directly
(law.lis.virginia.gov), specifies a genuinely phased schedule, not a flat
one:

**Solar/onshore wind (D.2, cumulative, Phase II Utility)**: 2024: 3,000 MW
&rarr; 2027: +3,000 (6,000 cum.) &rarr; **2030: +4,000 (10,000 cum.)** &rarr;
2035: +6,100 (16,100 cum., the full target) &rarr; no further mandated
increase through 2045.

**Short-duration storage (E.2)**: **2030: 4,000 MW** &rarr; 2045: 16,000 MW
(full target). No intermediate milestone specified.

**Long-duration storage (E.4, per 2026 Acts cc.694/695)**: 2035: 2,000 MW
(half) &rarr; 2045: 4,000 MW (full). **No 2030 milestone exists at all** —
nothing is statutorily required that early.

**Corrected 2030 inputs**: solar 10,000 MW (not 16,200), Na-power 4,000 MW
(not 16,000), iron-air 0 MW (not 4,000) — all three were wrong in the same
direction, each one a checkpoint too early relative to its actual
milestone.

**Genuine, unresolved ambiguity for 2035/2040, flagged rather than
assumed**: the statute gives no explicit milestone for Na-power between
2030 and 2045, nor for iron-air between 2035 and 2045. `solve_scenario2.py`
currently placeholders both at their nearer end-state value (2035/2040
Na-power = the full 2045 figure; 2040 iron-air = the 2035 figure) pending
an explicit decision — not run yet, deliberately, until that choice is
made rather than assumed silently.

**Corrected 2030 result** (Deloitte gas): CCGT sized at 14,852 MW (worst-
hour, zero-storage-credit) — unchanged from the pre-correction run,
because the worst hour is an overnight/near-zero-solar hour where fleet
size doesn't matter. Gas share 39.2% (up from an incorrect 28.9%),
curtailment 138.8 GWh (up from an incorrect zero) — smaller storage means
less capacity to absorb surplus even though the surplus itself also
shrank. Zero unserved energy — reliability maintained under the corrected,
smaller fleet.

### C.3 The Export Correction
An earlier version of this formulation carried over Scenario 1/3's export
mechanism without reconsidering fit. Diagnosis: CCGT was being dispatched as
a merchant generator purely for arbitrage (identical export revenue
regardless of demand or clean capacity was the tell); confirmed via zero
curtailment even with export disabled, ruling out genuine overgeneration.
Export removed entirely; gas dispatch dropped 40-53% as a result.

### C.4 Gas-Price Tier Mechanics
Because storage carries zero marginal cost in this formulation and export is
disabled, total dispatch VOLUME (aggregate gas GWh, curtailment GWh) is
mathematically invariant to the specific gas price — only cost changes.
**Correction to this section's original phrasing, verified directly rather
than assumed**: this invariance holds for the aggregate totals only, not
the specific hour-by-hour dispatch pattern. Directly tested (2030,
Deloitte vs. EIA pricing): total gas GWh matched to floating-point noise
(~1e-11), but 275 of 8,760 individual hours showed real differences up to
7,000 MW — LP degeneracy, not an error: with storage's marginal cost at
zero, multiple hour-by-hour dispatch patterns are equally optimal, and the
solver can land on a different one depending on the exact price value
passed in, even though the aggregate volume (and therefore total cost) is
identical either way. Safe to reuse the Base (Deloitte) tier's total
gas/curtailment volumes, repriced rather than re-solved, for cost/SLCOE
purposes specifically — not safe to assume the Low/High tiers' hourly
dispatch arrays are identical to Base's if hour-by-hour detail is ever
needed for its own sake.

### C.5 Full Four-Checkpoint, Three-Gas-Tier Results

**Code location**: `lp_package/solve_scenario2.py` (dispatch solves, one per
checkpoint) plus the repricing calculation described in C.4 (three gas
tiers computed from each checkpoint's single solved dispatch).

**Build inputs by checkpoint**, per the corrected statutory schedule (C.2.1):

| Year | Solar (MW) | Na-power (MW) | Iron-air (MW) | CCGT (MW, worst-hour sized) |
|---|---|---|---|---|
| 2030 | 10,000 | 4,000 | 0 | 14,852 |
| 2035 | 16,100 | 8,000 | 2,000 | 18,556 |
| 2040 | 16,100 | 12,000 | 3,000 | 22,231 |
| 2045 | 16,100 | 16,000 | 4,000 | 25,763 |

**Dispatch outcome, all four checkpoints, zero unserved energy throughout
(reliability maintained at every point)**:

| Year | Gas share | Curtailment (GWh) |
|---|---|---|
| 2030 | 39.2% | 138.8 |
| 2035 | 42.1% | 7.5 |
| 2040 | 51.0% | 0.0 |
| 2045 | 57.4% | 0.0 |

**A genuinely illustrative, expected pattern — the opposite direction from
Scenario 1, worth stating plainly rather than just tabulating**: gas share
*rises* over time under Scenario 2, while it falls sharply under Scenario
1 (59%&rarr;41%&rarr;21%&rarr;0.1% at the same four checkpoints, per A.16's
underlying data). This is exactly what "minimal compliance" should
produce: solar is statutorily flat at 16,100 MW from 2035 onward with no
further mandated increase, while demand keeps growing — a fixed clean
fleet inevitably covers a shrinking share of a growing load. Curtailment
falls to zero by 2040 for the same reason (a modest, no-longer-growing
solar fleet increasingly gets fully absorbed by growing demand, rather
than producing surplus) — a sharp, illustrative contrast with Scenario
1's 142,266 GWh of curtailment at 2045 from continuous, RPS-driven
overbuild. This contrast is precisely the comparison this project's
Scenario 1 vs. Scenario 2 structure is designed to surface.

**Gas fuel cost by checkpoint and tier** (repriced from each checkpoint's
single solved dispatch volume per C.4, not independently re-solved):

| Year | Deloitte ($M) | EIA ($M) | Hughes ($M) |
|---|---|---|---|
| 2030 | 1,631.9 | 1,187.0 | 1,317.0 |
| 2035 | 2,336.3 | 1,645.8 | 2,186.3 |
| 2040 | 3,605.4 | 2,468.6 | 3,951.9 |
| 2045 | 5,064.2 | 3,454.6 | 6,468.8 |

**Status**: gas fuel cost complete for all four checkpoints across all
three established tiers. Not yet built out: annualized capex/O&M for the
fixed solar/storage/CCGT fleet (the Scenario 1 equivalent of A.16/A.17),
curtailment/reliability findings beyond the summary table above, or a
combined Scenario 2 SLCOE/NPV figure comparable to Scenario 1's A.21.

### C.6 CCGT Capex/O&M

**Code location**: `lp_model.py`, `ccgt_capex_kw()`; `lp_package/
compute_ccgt_vintage_and_terminal.py`.

**CORRECTION (2026-08-20), prompted directly by user-flagged recent
market news**: this section originally sourced CCGT capex from Lazard's
LCOE+ v19.0 (already in this project's knowledge base) — "Gas Combined
Cycle" line, capital cost $1,450-$2,100/kW, midpoint $1,775/kW. Per direct
user instruction ("gas turbine prices have soared recently... Lazard very
likely pulled from older data"), this capex figure is now updated —
Lazard's own facility life (30 years) and fixed O&M ($10.00-$25.50/kW-yr,
midpoint $17.75/kW-yr) are RETAINED unchanged, since neither is addressed
or contradicted by the new turbine-price research, which speaks to capex
specifically.

**New capex sourcing, cross-verified across multiple independent outlets
(Bloomberg, Utility Dive, Power-Eng, APPA, Latitude Media), not resting on
one article**: gas turbine equipment and installed-project prices have
risen sharply, driven by data-center-led demand outpacing global
manufacturing capacity (110 GW of orders against 60-70 GW/yr of capacity,
per Wood Mackenzie's April 2026 report). Two scopes matter and are easy
to conflate: turbine-*equipment-only* cost (Wood Mackenzie: reaching
$600/kW by end-2027, a 195% increase since 2019) versus *full installed
project* cost (EPRI, the most recent directly-stated figure: ~$2,000/kW
to ~$3,000/kW in the six months to March 2026). These reconcile, not
conflict — turbines are 20-30% of total project cost per Wood Mackenzie's
own report, so $600/kW of equipment implies roughly $2,000-3,000/kW of
full project cost by 2027 — the same level EPRI's data shows the market
already reaching by its own more recent snapshot. A third, independent
source (GridLab/Energy Futures Group/Halcyon, Sept 2025) corroborates the
same order-of-magnitude rise, from pre-surge ($1,116-1,427/kW) to
2030-31-vintage projects ("routinely" $2,000/kW+).

**Updated methodology, `ccgt_capex_kw()`**: flat $3,000/kW for all years,
anchored to EPRI's most recent full-project figure — a 69% increase over
the superseded $1,775/kW Lazard midpoint. Not extrapolated further in
either direction beyond available sourcing. Wood Mackenzie's own report
explicitly diagnoses the current spike as a temporary manufacturing-
capacity shortfall, not a permanent structural driver, with all three
major OEMs (GE Vernova, Siemens Energy, Mitsubishi) actively expanding
capacity — no sourced basis to assume continued escalation once that
constraint eases, and this project's checkpoints (earliest: 2030) all
fall after Wood Mackenzie's own "supply crunch through 2027" window.

**A genuine, disclosed distinction from solar/storage, unchanged from the
original sourcing**: CCGT retains its own directly-sourced 30-year
facility life (Lazard), not this project's generic 25-year figure used
for solar/storage — its own CRF, not folded into the same bucket.

### C.7 Full Vintage-Tracked Capex/O&M, All Four Checkpoints

**Code location**: `lp_package/compute_ccgt_vintage_and_terminal.py`
(CCGT, updated this section) plus the pre-existing solar/Na-power/energy-
cycling components (unchanged). Same methodology as A.16/A.17: solar and
Na-power CRF-annualized with vintage-rate-locking; Na-energy and iron-air
cycling-cost-based (A.17's double-counting correction applies here too).

**Verified, not assumed**: CCGT vintage decomposition sums back to the
reported cumulative totals exactly at every checkpoint (e.g. 2045: 14,852.3
+ 3,704.0 + 3,674.5 + 3,531.9 = 25,762.8, matching the solved total to the
displayed precision).

**Updated result** ($M) — CCGT column reflects the new capex sourcing (C.6):

| Year | Solar | Na-power | CCGT | Na-energy | Iron-air | Total |
|---|---|---|---|---|---|---|
| 2030 | 1,175.7 | 18.2 | 2,999.0 | 37.5 | 0.0 | 4,230.4 |
| 2035 | 1,849.7 | 33.6 | 3,747.0 | 35.5 | 19.8 | 5,685.6 |
| 2040 | 1,845.5 | 46.6 | 4,489.0 | 16.2 | 0.4 | 6,397.7 |
| 2045 | 1,839.2 | 57.6 | 5,202.1 | 3.4 | 0.0 | 7,102.3 |

(Superseded totals, pre-turbine-price-correction: 3,113.5 / 4,290.0 /
4,725.9 / 5,164.8 — retained here for the correction trail, not for use.)

CCGT was already the largest single cost component before this
correction; it is now even more dominant, at roughly 2.7x total fuel cost
(nominal, EIA tier) across the four checkpoints combined — a direct,
sourced consequence of the current gas-turbine market, not an assumption.

### C.8 Terminal Value

Same treatment as A.19 — solar, Na-power, and CCGT all have real
remaining life beyond 2045 (CCGT's own 30-year life especially), so their
capex is credited back proportionally to what remains unrecovered at the
window's end, discounted to 2026.

**Updated result**: solar $3.273B, Na-power $0.191B, **CCGT $15.871B**
(up from a superseded $9.390B — the higher capex base means more absolute
dollars remain unrecovered at every vintage, even though the *fraction*
recovered by 2045 is similar to before). **Total terminal value: $19.335B**
(up from a superseded $12.854B).

### C.9 Final Scenario 2 SLCOE and NPV, All Three Gas Tiers

**Code location**: assembly combining C.7 (capex/O&M, updated), C.5 (gas
fuel cost by tier, unchanged), and C.8 (terminal value, updated) — same
discounting methodology as A.21 (4.5% real WACC, 2026 base year). No
export revenue term (C.3).

**Updated result, with terminal value included**:

| Gas tier | PV cost, no TV ($B) | PV cost, with TV ($B) | SLCOE, no TV | **SLCOE, with TV** |
|---|---|---|---|---|
| Deloitte | 20.987 | 1.652 | $59.42/MWh | **$4.68/MWh** |
| EIA | 18.838 | **-0.497** | $53.33/MWh | **-$1.41/MWh** |
| Hughes | 21.418 | 2.083 | $60.63/MWh | **$5.90/MWh** |

**A genuinely important, counterintuitive result, flagged directly rather
than smoothed over**: the EIA tier's SLCOE comes out *negative*. Verified
this is not a calculation error, not an artifact — CCGT capex is now
substantially higher than gas fuel cost (roughly 2.7x, nominal, for this
tier), and a large share of that capex remains genuinely unrecovered at
the 2045 window boundary given the fleet keeps growing throughout the
period. For the tier with the lowest fuel cost specifically, the capex-
only terminal value credit legitimately exceeds the tier's entire
combined (capex+fuel) present-value cost. This is a real mathematical
consequence of the methodology, not a sign it's broken — but it does
expose a genuine limitation worth stating plainly: **the terminal-value
approach works best when the analysis window captures a reasonable share
of each asset's lifetime cost.** When capex is this large relative to a
20-year window against a 30-year asset life, with heavy back-loading of
new build toward the window's end, the credited remaining value can swing
results into ranges that are difficult to interpret as a straightforward
per-MWh cost — a negative SLCOE does not mean Scenario 2's EIA-tier gas
is "free" or profitable; it means most of this scenario's CCGT capital
commitment sits beyond this project's 2026-2045 analysis horizon, and the
accounting convention that credits that back can dominate the visible
window's own numbers when capex is this concentrated. Retained and
reported honestly rather than adjusted to look more conventional.

**Comparison against Scenario 1, still directionally valid despite the
above**: even before terminal value, Scenario 2's SLCOE ($53-61/MWh, no
TV) now runs noticeably *higher* than the pre-correction figure
($43-50/MWh) and closer to (Deloitte/Hughes) or above (via EIA's
volatility) Scenario 1's own $54.59/MWh no-TV figure (A.18) — the
turbine-price correction has materially narrowed, and in places reversed,
what looked like a clear cost advantage for the minimal-compliance
approach before this correction. This itself is a legitimate, important
finding: Scenario 2's apparent cost advantage over Scenario 1 was
partly an artifact of understated CCGT capex, not fully a reflection of
its lighter clean-buildout obligation.

**Status**: Scenario 2's SLCOE/NPV now reflects current, cross-verified
turbine market pricing. Remaining, parallel to Scenario 1's own open
items: extending to 2026-2029, and reconciling this comparison further
once Appendix D's social-cost framework is applied to both scenarios
side by side. The negative-SLCOE finding for the EIA tier specifically
may also warrant a methodological discussion with the user about whether
terminal value should be capped, floored, or otherwise treated
differently when it approaches or exceeds total PV cost for a given tier
— not yet resolved, flagged here for follow-up.

### C.10 Realistic Gas Fleet Replacement: Existing Fleet Retirement + Type-Matched New Build

**SECOND CORRECTION (later session, direct owner-website verification)**: this section's
existing-fleet roster originally excluded Gordonsville and Gravel Neck entirely, and
marked Marsh Run, Louisa, Wolf Hills, Remington as "already effectively offline" and
Elizabeth River as "already retired" — all based on a generation-data note ("zero
output since Dec 2024, cause unconfirmed") that was over-interpreted as evidence of
retirement. Direct verification against each owner's own current site (Dominion's
power-stations page, ODEC's generation-facilities page, Middle River Power's own
site) confirmed all seven of these plants are still listed as active, operating
facilities — none show any indication of retirement. Corrected to the same
"confirmed still operating → retained through the full window" treatment already
used for Ladysmith/Tenaska/Chesterfield/Possum Point/Doswell; Gordonsville and Gravel
Neck added back to the roster. Existing fleet available, by type, corrected:

| Year | Existing CT (MW) | Existing CCGT (MW) | Total (MW) | (superseded total) |
|---|---|---|---|---|
| 2030 | 4,094.5 | 7,961.5 | 12,056.0 | 10,722.0 |
| 2035 | 4,094.5 | 6,986.5 | 11,081.0 | 8,387.0 |
| 2040 | 4,094.5 | 6,986.5 | 11,081.0 | 8,387.0 |
| 2045 | 0.0 | 3,774.0 | 3,774.0 | 3,774.0 |

2045 is unchanged — VCEA's 100% mandate excludes all gas capacity at that checkpoint
regardless of confirmed-operating status, so this correction only affects 2030-2040.

**New-build need, re-corrected**:

| Year | New CCGT (cumulative) | New CT (cumulative) | Fresh new CT | (superseded fresh) |
|---|---|---|---|---|
| 2030 | 0 | 2,796 | 2,796 | 4,130 |
| 2035 | 0 | 7,475 | 4,679 | 6,039 |
| 2040 | 0 | 11,150 | 3,675 | 0 |
| 2045 | 6,021 | 15,968 | 4,818 (CT) + 6,021 (CCGT) | 2,124 |

**Vintage-tracked annualized cost, re-corrected**:

| Year | Corrected | (superseded) |
|---|---|---|
| 2030 | $142.0M | $209.7M |
| 2035 | $379.5M | $516.3M |
| 2040 | $566.1M | $702.9M |
| 2045 | $2,026.5M | $2,026.5M (unchanged) |

**Terminal value**: gas fleet $10.500B (was $10.045B). **Total terminal value:
$13.964B** (was $13.509B) — terminal value rose slightly even as absolute capex fell,
because less early-build/more late-build (as a share of the smaller total) shifts
more of the capital toward less-recovered vintages, the same dynamic flagged in the
first C.10 correction.

**Final, re-corrected SLCOE and NPV**:

| Gas tier | PV cost, no TV ($B) | PV cost, with TV ($B) | SLCOE, no TV | **SLCOE, with TV** |
|---|---|---|---|---|
| Deloitte | 14.609 | 0.645 | $41.36/MWh | **$1.83/MWh** |
| EIA | 11.887 | **-2.077** | $33.65/MWh | **-$5.88/MWh** |
| Hughes | 15.053 | 1.089 | $42.61/MWh | **$3.08/MWh** |

The EIA tier's negative SLCOE is now more negative than before this correction
(-$5.88/MWh vs. a superseded -$3.96/MWh) — same underlying dynamic as flagged
previously, not resolved by this correction.

**Still outstanding**: the plant-specific NOx classification in Appendix D.2
(`PLANT_NOX_CLASS`) uses the same, now-corrected retirement years for these plants
in its own roster and has not yet been re-verified against this update — a small,
likely immaterial follow-up, since the classification (DLN vs. uncontrolled) for
each plant is unaffected by its retirement year, only which checkpoints it
contributes to.

CORRECTION, caught while building a visualization of this section's own
data (2026-08-20)**: as originally written, this section's new-CT sizing
(`new_ct = max(0, peaker_need - existing_CT)`) only credited existing CT
capacity toward the peaking need, ignoring that existing CCGT's own
excess above the baseload level is physically available to cover peaking
hours too — CCGT capacity doesn't stop existing just because it exceeds
the sustained-need calculation. At every checkpoint except 2045, existing
CCGT substantially exceeds its own baseload requirement (by 5,868 MW at
2030, for example) — capacity this methodology was wrongly leaving idle
in the peaking calculation. Fixed: new CT is now sized against the
remaining gap after ALL existing capacity (both types) plus any new CCGT
already decided, not existing CT alone. Verified directly, not assumed:
existing + new now sums to exactly the required peak at every checkpoint
(e.g. 2030: 7,744+0+2,978+4,130 = 14,852, matching peak exactly). All
figures below are the corrected values; the immediately-superseded
(buggy) figures are noted inline for the correction trail.

**Code location**: `lp_package/compute_scenario2_gas_replacement.py`. A
substantial further correction, prompted directly by user observation:
C.6-C.9 as written treated Scenario 2's *entire* required gas capacity as
brand-new CCGT build at every checkpoint, with no reference whatsoever to
the gas capacity Dominion already owns today. This section replaces that
with a physically grounded alternative.

**The user's key observation, which reshaped this methodology**: CCGT
plants are designed for sustained, near-continuous operation — cycling
them (frequent starts/stops) incurs substantially higher O&M costs. CT
(simple-cycle) units, by contrast, are specifically designed for flexible
cycling and handle it well. The right replacement principle is therefore
not "match whatever technology the retiring plant happened to be," but
"size CCGT to the sustained/baseload portion of actual need, and CT to
the intermittent/peaking remainder" — regardless of the retiring unit's
own original type.

**Baseload/peaker split, empirically derived, not assumed**: using each
checkpoint's own already-solved hourly gas dispatch, a load-duration curve
was computed directly. The split uses the 70th-percentile threshold (the
MW level sustained for at least 70% of hours) as the CCGT-sized
"baseload floor," with everything above that (the steep, brief tail) as
the CT-sized peaking need — chosen because this is visibly where each
checkpoint's own curve transitions from a gradual slope to a steep drop
toward zero. Confirmed genuinely different in shape by checkpoint, not
just in level: 2030/2035 show steep curves (near-zero by 75-80% of
hours, overwhelmingly peaker-shaped need); 2040/2045 show much flatter
curves (still 2,461-5,944 MW even at 80% of hours) — the gas fleet
increasingly behaves like real baseload as demand outgrows the
statutorily-flat solar fleet, consistent with C.5's rising-gas-share
finding.

| Year | Baseload (70th pct, MW) | Peak (MW) | Peaker need (MW) |
|---|---|---|---|
| 2030 | 1,875 | 14,852 | 12,977 |
| 2035 | 1,721 | 18,556 | 16,835 |
| 2040 | 6,153 | 22,231 | 16,078 |
| 2045 | 9,795 | 25,763 | 15,968 |

**Existing fleet, full roster (not just `driver.py`'s smaller 8-plant
overhaul/retain pool, which only covers Scenario 1's own retirement-
candidate peakers) classified CT vs. CCGT** — trusting each plant's
detailed notes over its terse type code where they conflict (the type
code reads "CT" for several plants the notes explicitly describe as
combined-cycle, e.g. Greensville County, Brunswick County). Retirement
timing uses confirmed-actual operating status where it contradicts the
30-year formula date (Chesterfield, Doswell, Possum Point, Ladysmith are
all directly confirmed via generation data to still be operating well
past their formula retirement year) — assumed to continue operating
through this project's full window absent a specific confirmed
retirement event, consistent with how this project treats these same
plants everywhere else. Doswell's mixed-type site (901 MW) split 50/50
CT/CCGT — a disclosed placeholder, not sourced data.

| Year | Existing CT available (MW) | Existing CCGT available (MW) |
|---|---|---|
| 2030 | 2,978.5 | 7,743.5 |
| 2035 | 1,618.5 | 6,768.5 |
| 2040 | 1,618.5 | 6,768.5 |
| 2045 | 0.0 | 3,774.0 |

**New-build need, by type, net of existing fleet — CORRECTED (see
correction note at the top of this section)**: CCGT sized to whatever
baseload need exceeds existing CCGT availability; CT sized to whatever
of the total peak remains after ALL existing capacity (both types) plus
any new CCGT, not existing CT alone.

| Year | New CCGT (cumulative, MW) | New CT (cumulative, MW) | (superseded, buggy New CT) |
|---|---|---|---|
| 2030 | 0 | 4,130 | 9,999 |
| 2035 | 0 | 10,169 | 15,217 |
| 2040 | 0 | 13,844 | 14,459 |
| 2045 | 6,021 | 15,968 | 15,968 |

**A genuine, worth-noting quirk, still present after the correction**:
cumulative new-CT need grows more slowly than total capacity — e.g.
2035-to-2040 (10,169 to 13,844 MW) despite the checkpoint's much larger
total capacity growth. This reflects the baseload threshold itself
growing substantially over this span (1,721 to 6,153 MW), reclassifying
capacity that would have counted as "peaking" earlier into "baseload"
later. Where this pattern actually goes slightly negative (not the case
here after the fix, but preserved as a documented edge case), the
vintage-decomposition logic floors the resulting fresh-increment at zero
rather than modeling an impossible "un-build" of already-installed
capacity.

**CT capex sourcing**: F-Class ($713/kW, $7.00/kW-yr fixed O&M) — this
project's own already-established default for new-build simple-cycle
capacity (`driver.py`'s `select_overhaul_retain()`, `NEWBUILD_UNITS[0]`,
chosen there as the cheapest of three reference units). Same 30-year
life as CCGT (`Gas_turbine_lifespans_reference.md`: CCGT 25-30yr, CT
peakers 30-45yr — using the shared, lower end of both ranges for
consistency), same CRF, own vintage-tracking and terminal-value treatment
identical in structure to CCGT's (C.6/C.8).

**Vintage-tracked annualized capex+O&M, corrected result — the scale of
the reduction is substantial, not marginal**:

| Year | Original (100% new CCGT) | Corrected (existing fleet + type-matched, bug-fixed) |
|---|---|---|
| 2030 | $2,999.0M | **$209.7M** |
| 2035 | $3,747.0M | **$516.3M** |
| 2040 | $4,489.0M | **$702.9M** |
| 2045 | $5,202.1M | **$2,026.5M** |

The reduction is large because the existing fleet (~10,700 MW combined
CT+CCGT at 2030) already covers most of the requirement, and because the
baseload/peaker split routes nearly all new-build toward the far cheaper
CT rate ($713/kW) rather than CCGT's ($3,000/kW) — the earlier C.6-C.9
figures implicitly assumed all new capacity was CCGT-grade, which this
correction shows was not warranted by the actual dispatch shape.

**Gas fuel cost, also corrected to reflect the CCGT/CT split** (same
per-hour split: dispatch up to the baseload level valued at CCGT's 6.4
MMBtu/MWh heat rate, dispatch above it at CT's 9.5 MMBtu/MWh rate — a
~48% higher fuel burn per MWh for the peaking portion, not previously
captured when all dispatch was priced at the CCGT rate; unaffected by the
new-build-sizing bug fix above, since fuel cost is computed directly from
the solved hourly dispatch, not from the new-build totals):

| Year | Deloitte ($M) | EIA ($M) | Hughes ($M) |
|---|---|---|---|
| 2030 | 2,155.7 | 1,555.6 | 1,730.9 |
| 2035 | 3,185.0 | 2,223.6 | 2,976.2 |
| 2040 | 4,401.4 | 2,995.0 | 4,830.1 |
| 2045 | 5,844.1 | 3,969.8 | 7,479.6 |

**Terminal value**: solar $3.273B, Na-power $0.191B, gas fleet (CCGT+CT
combined) $10.045B. **Total terminal value: $13.509B.**

**Final, corrected SLCOE and NPV, all three gas tiers**:

| Gas tier | PV cost, no TV ($B) | PV cost, with TV ($B) | SLCOE, no TV | **SLCOE, with TV** |
|---|---|---|---|---|
| Deloitte | 14.832 | 1.323 | $41.99/MWh | **$3.74/MWh** |
| EIA | 12.110 | **-1.399** | $34.28/MWh | **-$3.96/MWh** |
| Hughes | 15.275 | 1.766 | $43.24/MWh | **$5.00/MWh** |

**The EIA tier's SLCOE remains negative, and is now somewhat more
negative than before the bug fix** (-$3.96/MWh vs. the immediately-prior,
buggy -$1.16/MWh) — the same underlying dynamic flagged in C.9 still
applies: a meaningful share of this scenario's gas-fleet capital
commitment sits beyond the 2045 window boundary, and correcting the
new-build sizing shifted more of that commitment toward later, less-
recovered vintages rather than resolving the underlying tension. This
reinforces, rather than resolves, C.9's flagged open question about
whether terminal value needs different treatment when it approaches or
exceeds a tier's total PV cost.

**Status**: this is Scenario 2's most physically-realistic gas-cost
methodology to date, now also verified internally consistent (existing +
new capacity sums exactly to each checkpoint's required peak). Superseded
figures retained throughout this section and C.6-C.9 for the full
correction trail, not for use. Same remaining open items as C.9:
2026-2029 extension, and the EIA-tier negative-SLCOE methodological
question.

---

### C.11 Turbine Procurement Lead Time: Feasibility Check on 2030's New-Build

Prompted directly by user question: given confirmed current gas turbine lead times
(C.6-adjacent research, this session — 5-7 years for heavy-duty CCGT frames, 2-4
years for simple-cycle units specifically, the relevant case here), is the corrected
2030 new-build requirement (2,796 MW fresh, C.10) actually achievable in time?

**Timing check**: exactly 4 years separate today (August 2026) from the 2030
checkpoint. At the confirmed simple-cycle lead-time range (2-4 years), turbines
ordered starting now would be ready anywhere from 2028 (fast end) to exactly 2030
(slow end) — tight, with no margin for delay, but not infeasible on its face. This
is a materially different conclusion than for the original, larger 4,130 MW figure
(pre-C.10-correction), which would have required orders placed essentially before
this project's own analysis began.

**Resolved as feasible**, on two grounds: (1) the timing arithmetic itself is
consistent with a 2030 in-service date if procurement starts promptly, and (2)
real-world precedent — Dominion has already demonstrated willingness and ability to
place large new simple-cycle turbine orders on a comparable timeline, via the
Chesterfield Energy Reliability Center (944 MW, 4-unit simple-cycle, SCC-approved
November 2025, per this project's own earlier tracking, A.8.5) — user-reported
turbine ordering activity for that project predates the SCC approval by a year or
more, consistent with normal parallel permitting/procurement practice. CERC itself
is a separate, specific project and is not counted toward this analysis's own
modeled 2,796 MW requirement — it is cited here only as evidence that turbine
procurement on this scale and timeline is something Dominion has actually done, not
a hypothetical capability.

**Disclosed caveat**: this conclusion assumes procurement begins essentially
immediately and experiences no material slippage (permitting, interconnection
queue, or further supply-chain tightening) — a real risk given the tightness of the
margin, not a certainty. No quantitative adjustment made to Scenario 2's SLCOE/NPV
on this basis; C.10's figures stand as the final result for this checkpoint.

### C.12 Full 20-Year Extension — Correcting a Major, Previously Undisclosed Gap

**The gap**: every Scenario 2 SLCOE/NPV figure through C.11 was built from
the 4 checkpoints (2030/2035/2040/2045) only — discrete years, individually
discounted, with **no dispatch or build-out information for the other 15
of 20 modeled years**. This was not previously flagged as a limitation in
this appendix. It surfaced only when directly asked how yearly gas
consumption and new-turbine timing between checkpoints had been captured
— they hadn't been, at all, for Scenario 2 (unlike Scenario 1, which
genuinely solved all 12 intermediate years).

**Corrected**: solved all 12 intermediate years (2031-2034, 2036-2039,
2041-2044) plus 2026-2029, using `solve_scenario2_year()` (already
year-parameterized, unmodified) with the VCEA statutory solar/storage
targets linearly interpolated between their own defined milestones —
solar flat after 2035 (no further statutory milestone), Na-power
interpolated 2030-2045, iron-air interpolated 2035-2045 (zero before,
consistent with the existing checkpoint treatment). 2026-2029 uses the
statute's own earlier milestones (2024: 3,000 MW, 2027: 6,000 MW
cumulative, Va. Code §56-585.5 D.2) rather than extrapolating backward
from 2030 alone. All 20 years connect smoothly — no discontinuities at
the original checkpoint boundaries (e.g., 2034's 17,770 MW peak leads
into 2035's 18,556 MW checkpoint; 2044's 25,082 MW leads into 2045's
25,763 MW).

C.10's existing-fleet-crediting and baseload/peaker-split methodology
(including the CCGT-excess-covers-peaking correction) was then applied
to all 20 years, not just 4 — every year independently verified
(existing + new sums exactly to that year's own peak, all 20/20 years).

**Result — a complete reversal of the prior conclusion**:

| Gas tier | 4-checkpoint approximation (superseded) | Full 20-year (corrected) |
|---|---|---|
| Deloitte | $1.83/MWh | **$35.54/MWh** |
| EIA | **-$5.88/MWh** | **$29.01/MWh** |
| Hughes | $3.08/MWh | **$35.91/MWh** |

**Mechanism**: the 4-checkpoint approximation counted cost at only 4
discrete years while still crediting the *full* 30-year terminal value
against that badly undercounted total. The EIA tier's negative SLCOE —
raised and investigated repeatedly across this session as a genuine,
if uncomfortable, finding — turns out to have been entirely an artifact
of this undercounting, not a real result. With the full 20-year cost
stream properly captured (16 additional years of real gas capex and
fuel cost that Scenario 2 actually incurs), the EIA tier is an ordinary
positive number.

**Terminal value, corrected to include solar/Na-power** (previously gas
only): gas $9.676B, solar $2.219B, Na-power $0.172B — **total $12.067B**
(down from a superseded, gas-only $13.964B, since properly distributing
capex across the full 20-year vintage stream — rather than concentrating
it artificially at 4 points — reduces how much sits in the
highly-creditable late-vintage position).

**Downstream implications, not yet resolved**: every comparison built on
the superseded 4-checkpoint Scenario 2 figures is now invalid, including
Scenario 1B vs. Scenario 2 framing (Appendix N) and the Social Cost of
Carbon/Greenhouse Gases and Health Impacts work (Appendix D), which drew
on the same 4-checkpoint dispatch data. Both are flagged for a follow-up
correction pass, deliberately not done in the same turn as this one per
direct user direction (pause, document, come back).

Scripts: `solve_scenario2_intermediate_years.py`,
`solve_scenario2_2026_2029.py`,
`compute_scenario2_gas_replacement_20yr.py`,
`compute_scenario2_20yr_full_slcoe.py`.

### C.13 Solar Degradation — a Gap Present Since Scenario 2's First Solve

**The gap**: Scenario 1/1B's solar is vintage-tracked and properly
degraded (0.5%/yr, `solar_degradation_factor()`) throughout this
project. Scenario 2's statutory VCEA solar target (`vcea_solar_mw`) was
used directly, undegraded, in every dispatch solve built this session —
only its small pre-2026 legacy baseline (`exist_solar`) was ever
degraded. Confirmed directly in code:
`solar_degradation_factor()` is referenced only within `lp_model.py`'s
own LP problem-builder and `exist_solar_mw()` — never in `driver.py` or
`solve_scenario2.py`. Flagged by direct user question ("would be quite
obvious to a modeler").

**Fix**: vintage-decomposed the statutory nameplate solar schedule into
yearly fresh increments — critically, using the SIMPLE year-over-year
difference in the statutory MW figure itself (not Scenario 1's
degradation-backed-out approach), since VCEA's targets are raw,
undegraded cumulative nameplate build requirements by construction, not
LP-derived totals that already implicitly reflect degradation the way
Scenario 1's do. Each vintage then degraded forward to compute each
year's effective (as opposed to nameplate) capacity, used in place of
the raw statutory figure for dispatch and worst-hour CCGT sizing;
nameplate MW is unchanged and still used for capex accounting (VCEA
compliance is a nameplate-installed requirement, not an effective-output
one).

| Year | Nameplate (MW) | Effective (MW) | Shortfall |
|---|---|---|---|
| 2030 | 10,000 | 9,865.9 | 1.3% |
| 2035 | 16,100 | 15,661.0 | 2.7% |
| 2040 | 16,100 | 15,273.3 | 5.1% |
| 2045 | 16,100 | 14,895.3 | 7.5% |

**Result — a small, genuine correction, not a dramatic one**: the
worst-hour CCGT-sizing calculation (`peak_g`) is completely unaffected
at every year — the worst hour is an overnight/zero-solar hour, so
`vcea_solar_mw * solar_cf` is zero at that hour regardless of which MW
figure is used, meaning capacity requirements and the resulting capex
stream are essentially unchanged. Annual gas *generation* (all other
hours, where solar is actually producing) rises modestly at every year
(e.g. 2045: 107,020→109,359 GWh; gas share 57.5%→58.7%), since less
actual solar output means slightly more must come from gas across the
year.

| | Superseded (undegraded) | Corrected (degraded) |
|---|---|---|
| Deloitte SLCOE | $35.54/MWh | $35.50/MWh |
| EIA SLCOE | $29.01/MWh | $28.96/MWh |
| Hughes SLCOE | $35.91/MWh | $35.87/MWh |
| Social Cost of Carbon | $57.12/MWh | $57.25/MWh |
| Health Impacts | $3.52/MWh | $3.52/MWh |

All 20 years of dispatch re-solved and all downstream figures (gas
capex, terminal value, SLCOE, Social Cost of Carbon/Health Impacts)
recomputed against the corrected data — not a partial patch. Terminal
value: gas $9.676B→$10.060B, total $12.067B→$12.451B.

Scripts: `fix_scenario2_solar_degradation.py`,
`resolve_scenario2_20yr_degraded_solar.py` (re-solves all 20 years),
plus re-runs of `compute_scenario2_gas_replacement_20yr.py`,
`compute_scenario2_20yr_full_slcoe.py`, and
`compute_scenario2_tier12_20yr.py` against the corrected dispatch data.
