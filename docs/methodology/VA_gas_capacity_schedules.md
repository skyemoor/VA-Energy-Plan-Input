# Virginia Existing Gas Fleet -- Time-Varying Capacity Schedules

> **Consolidated treatment: `Gas_Fleet_Working_Notes.md`** — this document remains authoritative
> for retirement schedules; the working notes carry heat rates, merit order, capacity per rung and
> definitions. Read that before using any gas assumption.

Two DISTINCT schedules, for two genuinely different purposes. Do not use
interchangeably. This version adds Chesterfield's corrected, gas-only EOH
figure and walks back the "confirmed retired" language for seven plants
after independent verification came back inconclusive.

## ASSUMPTION UPDATE: Tenaska Virginia and Ladysmith retained past formula retirement (for Scenario 1/3/1B/3B/3C shortfall purposes)

Tested directly against Scenario 1's 2035 checkpoint shortfall and found
substantially cheaper than new-build (see `new_peaker_ccgt_costs_by_size.md`
for full detail and caveats). **This is an assumption, not a confirmed
plan** -- Tenaska Virginia's overhaul cost is a midpoint estimate, not a
plant-specific quote; Ladysmith's "no capital work needed" conclusion is
inferred from its low EOH, not a confirmed engineering assessment; and
Tenaska Virginia's third-party (Tenaska) ownership means retention would
require a negotiated agreement, not just a Dominion capital decision.

**Effect on the schedules below**: Tenaska Virginia (975 MW) and Ladysmith
(782 MW) are now assumed RETAINED past their formula-retirement dates
(2034 and 2031 respectively) for the specific purpose of addressing
identified capacity shortfalls in Scenario 1/3/1B/3B/3C -- NOT
automatically extended to their full physical life indefinitely. This
assumption should be re-examined if a shortfall large enough to require
their retention doesn't actually arise at a given checkpoint, or if a
shortfall at a LATER checkpoint would need them retained even longer than
currently assumed.

## Chesterfield's EOH, now correctly computed (gas-only data)

Coal Units 5&6 retired May 31, 2023 -- data from June 2023 onward is
confirmed gas-only (Units 7&8 only). Over this clean 36-month window
(Jun 2023-May 2026): **16,487 EOH**, at a 62.7% average capacity factor,
against the corrected 386 MW gas-only capacity.

Extrapolating this rate backward (implied ~5,496 EOH/year) suggests a
full-history cumulative EOH somewhere in the range of 137,000-198,000
depending on the assumed start year (2001 data-window limit vs. 1990 true
commissioning) -- both figures place Chesterfield well above the
48,000-100,000 mid-life window, consistent with the earlier (invalid)
calculation's conclusion even though the specific number has changed.
**This extrapolation should be treated as directional, not precise**: it
assumes the gas units' utilization rate has been roughly constant
throughout their history, which is unlikely -- Units 7&8 plausibly ran
less while the coal units still provided most of the site's baseload,
then increased utilization after coal retired to help compensate for the
lost capacity. The true historical average could be meaningfully lower
than 62.7%.

## Independent verification of the "seven plants, Dec 2024" pattern: INCONCLUSIVE

A working search for direct news/regulatory confirmation of retirement
for Gordonsville, Gravel Neck, Darbytown, Elizabeth River, Remington,
Marsh Run, and Louisa did NOT find clear confirmation. What it did find:
third-party databases (gridinfo.com, Global Energy Monitor) that draw on
the same underlying EIA data and share the identical Dec 2024 cutoff --
not independent confirmation. Global Energy Monitor's own Gordonsville
page (updated January 2026) still lists the plant's status as
"operating... with multiple units, some of which are not currently
operating" -- ambiguous, but does not say retired.

**Revised characterization**: these seven plants show generation data at
zero since Dec 2024, with the underlying cause UNCONFIRMED -- could be
retirement, reserve/standby status, or a data-reporting gap specific to
smaller plants (all seven larger CCGT-style plants continue reporting
cleanly through May 2026, which argues against a uniform reporting lag,
but does not rule out a lag specific to this plant class). Treated
CONSERVATIVELY as unavailable capacity in the schedule below (same
practical effect as retirement for our purposes), but this is now
explicitly flagged as an assumption under genuine uncertainty, not a
confirmed fact.

## CERC approval status, corrected again

Per Virginia Mercury (most recent, most direct source found): the SCC
approved CERC in November 2025; advocacy groups petitioned for
reconsideration (this appears to be the source of the earlier "suspended"
report); the SCC **declined to reconsider, reasserting its original
approval**. Advocacy groups are now pursuing a separate air-permit appeal.
**Current status: approved**, though still facing an ongoing legal
challenge on a different track. Also note: this more recent source cites
944 MW (not 1,000 MW) and states the plant is expected to run "about 33%
of the time." Still excluded from the capacity schedules below, since
commercial operation (~2029) falls partway through our analysis window
and hasn't been incorporated as a time-varying addition yet.

## Data collection status: COMPLETE

All 10 peaker/mixed-type plants now have direct generation-data
confirmation (Wolf Hills was the last, uploaded and processed most
recently). 8 of these 10 plants show the identical "zero output since
Dec 2024" pattern (cause unconfirmed, see note above) -- only Ladysmith
and Possum Point continue reporting cleanly through May 2026.

## Schedule A: Physical/data-driven retirement (for Scenario 3C specifically)

| Year | Total capacity (MW) | Notes |
|---|---|---|
| 2026-2040 | 9,362 | All confirmed/presumed-operating plants; Tenaska Virginia and Ladysmith now assumed RETAINED (see assumption note above) rather than retiring on their formula dates (2034, 2031) |
| 2041-2043 | 8,740 | Bear Garden retires (2041) |
| 2044-2045 | 7,391 | Warren County retires (2044) |

## Schedule B: VCEA-driven retirement (for Scenario 1/3's own 2045 checkpoint context)

| Year | Total capacity (MW), VCEA-consistent world | Notes |
|---|---|---|
| 2026-2044 | Same as Schedule A | VCEA doesn't bind until the 100% terminal year itself |
| 2045 | 1,860 (Chesterfield + Doswell + Possum Point) | Brunswick County + Potomac Energy Center + Greensville (3,774 MW combined) retire for lack of market |

## Important caveats

- 30-year CCGT / 30-45yr CT lifespan assumptions are user-selected
  starting points, not engineering certainties
- Chesterfield's full-history EOH is an extrapolation from a confirmed
  36-month gas-only window, not a direct historical measurement -- treat
  as directional (well above the mid-life window) rather than precise
- The "seven plants, zero output since Dec 2024" finding is NOW EXPLICITLY
  UNCONFIRMED as to cause -- treated conservatively (excluded from
  capacity) but should not be cited elsewhere as "confirmed retired"
- CERC's approval status has been revised twice in this project (approved
  -> reported as suspended -> reasserted as approved) -- worth a final
  re-check before this is used in any downstream calculation, given the
  history of this specific status changing
- Wolf Hills has no generation data uploaded -- still relies on the
  30-year formula alone
- Marsh Run, Louisa (ODEC-owned), Potomac Energy Center (Blackstone-owned),
  Wolf Hills (Middle River Power II-owned), and Doswell (LS Power
  Group-owned) are included per the physical-grid-contribution principle
  where still applicable
