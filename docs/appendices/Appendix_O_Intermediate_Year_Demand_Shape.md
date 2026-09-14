## Appendix O — Intermediate-Year Demand Shape: Data-Center-Driven Flattening Methodology

### O.1 The Problem

This project's only real, sourced hourly load *shape* (as opposed to annual
total) comes from a Dominion-provided stakeholder hourly file that, on the
user checking their own records against stakeholder correspondence, turned
out to be **2023 IRP vintage**, not 2024 as originally labeled (the March
2024 date is when Dominion's answers arrived, not the IRP year the questions
were about -- see Activity Tracker item 54's seventh addendum for the full
correction).

Using that single, fixed shape unmodified for every intermediate year (2026-
2045) would miss something real and quantifiable: data centers run a
near-constant 24x7x365 load profile ("data centers have a constant 24x7x365
energy profile," Dominion Energy Virginia, 2025 IRP Update, p. 18), and their
share of Virginia electricity sales has grown substantially and is projected
to keep growing throughout this project's full modeling horizon. A load
curve with a large and growing flat, always-on component should itself get
flatter over time -- not just larger. A static 2023 shape scaled up to 2045's
annual total would understate how flat 2045's real hourly curve would
actually be, with direct consequences for this project's storage-sizing and
dispatch-timing conclusions in the later checkpoints specifically.

### O.2 Data Source: Commercial Share as a Data-Center Proxy

Dominion does not publish data-center load as its own separate line in
either IRP filing consulted for this project -- the closest available proxy
is the **Commercial** rate class, which the Company's own 2025 IRP Update
confirms is where data centers are concentrated ("the Company also has a
high concentration of data centers among its commercial customers... data
centers are extremely energy intensive").

Two sourced tables, both **Virginia-only** (not combined VA+NC DOM LSE --
see the correction note in O.5 below):

- **2018/2019 baseline** (pre-boom reference point, not itself used in the
  flattening formula, retained for historical context): Dominion Energy
  Virginia, "2018 Integrated Resource Plan" (filed May 1, 2018), Appendix
  2B. Commercial share: 39.8% (2018), 41.9% (2019). Citation C074.
- **2020-2045** (the series actually used): Dominion Energy Virginia, "2025
  Integrated Resource Plan Update" (Oct 15, 2025), Appendix 2B-2 -- the same
  table already cited for this project's Virginia-only demand totals
  (Activity Tracker item 54, Appendix M.9, citation C071), reused here for a
  second purpose. Commercial share: 49.3% (2023) rising to 73.6% (2045).

### O.3 Methodology

**Decomposition**: each year's hourly demand is modeled as a blend of two
components -- a "traditional" component following the base 2023 shape
(genuine daily/seasonal peakiness), and a "data-center-like" component,
perfectly flat across all hours in the year.

**Blend weight (alpha)**: the *incremental* commercial share above the base
shape's own 2023 vintage, not the full commercial share -- the base shape
already implicitly reflects however flat or peaky 2023's actual load mix
was, so using the full share would double-count that already-present
portion. `alpha(year) = max(0, commercial_share(year) - commercial_share(2023))`.

**Formula**:
```
demand(t) = ANNUAL_TOTAL(year) x [(1-alpha) x s_base(t) + alpha x (1/N)]
```
where `s_base` is the base shape normalized to sum to 1.0, `N` is the number
of hours in the year, and `ANNUAL_TOTAL(year)` is that year's real,
Virginia-only Appendix 2B-2 total -- so the annual total is always exactly
correct regardless of alpha; only the hour-to-hour distribution shifts.

**Alpha values at the four solved checkpoints:**

| Year | Commercial share | Alpha |
|---|---|---|
| 2030 | 59.1% | 0.098 |
| 2035 | 66.1% | 0.167 |
| 2040 | 70.5% | 0.212 |
| 2045 | 73.6% | 0.243 |

For the 15 unsolved intermediate years, alpha is computed directly from that
year's own real commercial-share value (all years 2018-2045 are individually
sourced from the same two tables, not interpolated a second time on top of
an already-derived quantity).

### O.4 Verification Against Real Data

Tested directly against the user's uploaded file's actual 2024 hourly
values (the file's earliest available year, used as the closest proxy for
the underlying 2023 vintage -- the file itself contains no true 2023 row).
Unflattened peak/average ratio: 1.534. After blending:

| Year | Peak/Average ratio | Change |
|---|---|---|
| 2030 | 1.482 | −3.4% |
| 2035 | 1.444 | −5.9% |
| 2040 | 1.421 | −7.4% |
| 2045 | 1.404 | −8.5% |

A real, measurable flattening effect -- meaningful but not extreme, consistent
with even 2045 still being roughly three-quarters traditional-shaped load.

### O.5 Correction Log (kept for transparency, per this project's established convention)

An earlier draft of `demand_shape_interpolation.py` mislabeled the 2025 IRP
Update source as **Appendix 2B-1** ("Total (DOM LSE) Sales," the combined
VA+NC table) rather than **Appendix 2B-2** (Virginia-only). Caught and fixed
same session, before this methodology was finalized, by directly
re-extracting both tables from the raw filing text and cross-verifying via
an independent row-sum check (Appendix 2B-1's own stated total, 82,157 GWh
at 2015, matches summing its own Residential + Commercial + Industrial +
Public Authority + Street/Traffic + Sales-for-Resale columns to within
rounding -- confirming which numeric block genuinely belongs to which
appendix).

**Practical impact of the error was small**: the true combined-table
commercial share runs about 1.0-1.4 percentage points lower than the
Virginia-only share used, fairly consistently across years -- and because
alpha is a *difference* from the 2023 baseline, this mostly cancels out
rather than compounding. The numbers actually used in the formula above were
never wrong; only their citation was. The corrected labeling (Virginia-only)
is, if anything, the more appropriate one for this project given its
established Virginia-only principle (Activity Tracker item 54) -- so this
correction improves consistency rather than requiring a substantive change.

### O.6 Limitations (disclosed explicitly, not discovered later)

1. **Commercial share is a proxy, not a direct data-center measurement.**
   The Commercial rate class includes real non-data-center load (offices,
   retail) without a flat 24x7 profile. This likely means alpha
   *understates* the true data-center-driven flattening effect, not
   overstates it -- ordinary commercial load dilutes the proxy downward.
2. **The linear blend formula is a reasonable, simple choice, not a
   uniquely-derived one.** No attempt was made to fit a more complex
   functional form given the sourcing available.
3. **No sourced basis exists beyond 2045** for either commercial-share
   table -- this methodology should not be extended past that year without
   new sourcing.
4. **`BASE_SHAPE_YEAR` (2024, the uploaded file's earliest row) is a proxy**
   for the true 2023 IRP vintage -- the file itself contains no actual 2023
   row to use directly.

---
