"""
demand_shape_interpolation.py

Builds the hourly demand array for any year 2026-2045 (not just the four solved
checkpoints), for use in the intermediate-year dispatch-only re-solves.

METHODOLOGY NOTE FOR FUTURE READERS -- full narrative version, with the reasoning
trail and sourcing, lives in Reorganized_Appendices_Draft.md, Appendix O. This
docstring is the code-side half of that pair (see this project's standing
convention: appendix and code should each be readable on their own, with each
pointing to the other). Read Appendix O first if this is your first time here --
it explains WHY this exists, not just what it does.

THE PROBLEM THIS SOLVES: this project's only real, sourced hourly load SHAPE
(as opposed to annual total) comes from a stakeholder-obtained hourly file that
turned out, on the user checking their own records, to be 2023 IRP vintage (not
2024 as originally labeled -- the 2024 date is when Dominion's answers arrived,
not the IRP year they answered). A single fixed shape scaled to different
annual totals would miss something real: data centers run a near-constant
24x7x365 load profile (Dominion's own language, 2025 IRP Update p.18), and
their share of Virginia-only DOM LSE sales has grown enormously and continues
to grow through this project's full 2030-2045 horizon -- so the TRUE hourly
shape should genuinely flatten over time, not just scale up. Using a static
2023 shape for 2045 would understate how flat 2045's real load curve would be.

THE FIX: blend the base (2023) shape toward a perfectly flat shape, by an
amount (alpha) tied to how much data-center-like load has been added since
2023, sourced from Dominion's own two IRP filings (see COMMERCIAL_SHARE_PCT
below). This is a proxy, not a direct data-center measurement -- flagged
explicitly, see LIMITATIONS at the bottom of this file.
"""

import numpy as np
import pandas as pd
import os

# ---------------------------------------------------------------------------
# SOURCE DATA 1: Commercial share of Virginia-only DOM LSE sales, by year.
# CORRECTED (2026-08-20): both tables below are VIRGINIA-ONLY, not combined
# VA+NC DOM LSE -- an earlier draft of this module mislabeled the 2025-update
# source as Appendix 2B-1 (Total/combined). Verified directly against the raw
# filing text: the values actually match Appendix 2B-2 (Virginia-specific),
# confirmed via an independent row-sum cross-check against 2B-1's own real
# total column. Practical impact of the mislabeling was small (~1-1.4
# percentage points, mostly cancels out in alpha since alpha is a difference
# from the 2023 baseline) -- but worth being precise about, and the corrected
# labeling is actually the MORE appropriate one for this project given its
# established Virginia-only principle (Activity Tracker item 54).
#
# Appendix O, source table 1 (2018-2019): Dominion Energy Virginia, "2018
# Integrated Resource Plan" (filed May 1, 2018), Appendix 2B: "Virginia Sales
# by Customer Class (DOM LSE) (GWh)" -- Virginia-only (confirmed by the same
# filing's separate Appendix 2C for North Carolina). Pre-data-center-boom
# baseline.
# Appendix O, source table 2 (2020-2045): Dominion Energy Virginia, "2025
# Integrated Resource Plan Update" (Oct 15, 2025), Appendix 2B-2: "Virginia
# Sales (GWh) by Customer Class" -- the SAME table already cited elsewhere in
# this project (Activity Tracker item 54, Appendix M.9, citation C071) for
# the Virginia-only demand SCALE; now also the source for this SHARE.
# Values below are (Commercial GWh, Total GWh) as filed; share is computed,
# not itself a filed figure.
# Tracker Citations: C074 (2018 IRP Appendix 2B); C071 (already-existing
# citation, 2025 IRP Update Appendix 2B-2, reused here for a second purpose).
# ---------------------------------------------------------------------------
_COMMERCIAL_AND_TOTAL_GWH = {
    2018: (32752, 82254), 2019: (34091, 81317), 2020: (30681, 76176),
    2021: (34239, 80897), 2022: (38781, 85864), 2023: (42438, 86006),
    2024: (44961, 90495), 2025: (48828, 95246), 2026: (50193, 95805),
    2027: (53369, 98862), 2028: (57103, 102289), 2029: (61162, 106249),
    2030: (65542, 110864), 2031: (70146, 115684), 2032: (75179, 120920),
    2033: (80054, 125938), 2034: (85057, 131176), 2035: (90294, 136645),
    2036: (96032, 142549), 2037: (101188, 148004), 2038: (106220, 153370),
    2039: (110060, 157486), 2040: (114338, 162077), 2041: (118430, 166548),
    2042: (122951, 171265), 2043: (127603, 176399), 2044: (132713, 181729),
    2045: (137237, 186462),
}

# Base-shape vintage: the uploaded hourly file's underlying forecast is 2023
# IRP-vintage (see Appendix O for the full correction history on this point).
# The file's own earliest data row is labeled 2024 (closest available proxy
# for the 2023 IRP's own assumptions -- there is no 2023 row in the file
# itself). This is the reference point alpha is measured FROM: any commercial-
# share growth beyond this baseline is treated as new, incremental,
# data-center-driven flattening not already present in the base shape.
BASE_SHAPE_YEAR = 2024
_ALPHA_BASELINE_YEAR = 2023  # commercial share reference point, per above


def commercial_share_pct(year):
    """Sourced (not interpolated) commercial share of Virginia-only DOM LSE
    sales for a given year, 2018-2045. Raises KeyError outside that range --
    deliberate, since this project has no sourced basis to extrapolate this
    specific series beyond 2045."""
    return 100.0 * _COMMERCIAL_AND_TOTAL_GWH[year][0] / _COMMERCIAL_AND_TOTAL_GWH[year][1]


def data_center_flattening_alpha(year):
    """Incremental data-center-like blend weight for `year`, relative to the
    base shape's own 2023 vintage. See Appendix O for full derivation.
    Floored at 0 (years at or below the 2023 baseline get no flattening
    adjustment, not a negative one -- would imply un-flattening, which this
    project has no basis to model)."""
    share_now = commercial_share_pct(year)
    share_baseline = commercial_share_pct(_ALPHA_BASELINE_YEAR)
    return max(0.0, (share_now - share_baseline) / 100.0)


def _load_base_shape():
    """Loads and normalizes the base (2023-vintage) hourly shape from the
    user-uploaded stakeholder file, using its earliest available year
    (2024) as the closest proxy. Returns an array summing to exactly 1.0."""
    path = '/mnt/user-data/uploads/DOM-LSE-HourlyLoadProjections-2024-through-2048_formatted.csv'
    df = pd.read_csv(path)
    base = df[df['Year'] == BASE_SHAPE_YEAR].sort_values('DateTime')
    mwh = base['MWh'].values.astype(float)
    return mwh / mwh.sum()


_BASE_SHAPE_NORMALIZED = None  # lazy-loaded, cached module-level


def flattened_hourly_demand(year, annual_total_gwh):
    """Returns an hourly demand array (MW) for `year`, blending the base 2023
    shape toward flat by data_center_flattening_alpha(year), then scaled to
    exactly match annual_total_gwh (intended to be that year's real,
    Virginia-only Appendix 2B-2 total -- NOT looked up internally, passed in
    explicitly, so this function has no silent dependency on which demand
    vintage/geography the caller has decided to use elsewhere in this
    project -- see Activity Tracker item 54 for why that decision is kept
    separate and explicit rather than hardcoded here).

    Formula (Appendix O): demand(t) = annual_total * [(1-a)*s_base(t) + a*(1/N)]
    where N = len(s_base), a = data_center_flattening_alpha(year).
    """
    global _BASE_SHAPE_NORMALIZED
    if _BASE_SHAPE_NORMALIZED is None:
        _BASE_SHAPE_NORMALIZED = _load_base_shape()

    s_base = _BASE_SHAPE_NORMALIZED
    n_hours = len(s_base)
    s_flat = np.full(n_hours, 1.0 / n_hours)

    alpha = data_center_flattening_alpha(year)
    s_blend = (1 - alpha) * s_base + alpha * s_flat

    annual_total_mwh = annual_total_gwh * 1000.0
    return s_blend * annual_total_mwh  # hourly MWh == hourly MW (1-hour steps)


# ---------------------------------------------------------------------------
# LIMITATIONS (full versions of each also in Appendix O -- kept in sync,
# not duplicated verbatim, per this project's aligned-documentation standard)
# ---------------------------------------------------------------------------
# 1. Commercial share is a PROXY for data-center share, not a direct
#    measurement. The Commercial rate class includes real non-data-center
#    load (offices, retail) that does not have a flat 24x7 profile. This
#    likely means true alpha is somewhat UNDERSTATED, not overstated, since
#    ordinary commercial load dilutes the proxy downward.
# 2. The linear blend formula is a reasonable, simple way to model
#    flattening, not a uniquely-derived one -- no attempt was made to fit a
#    more complex functional form given the sourcing available.
# 3. This series has no sourced basis beyond 2045 -- do not extend
#    commercial_share_pct() or this module past that year without new
#    sourcing.
# 4. BASE_SHAPE_YEAR (2024, the file's earliest row) is a proxy for the true
#    2023 IRP vintage -- the file itself contains no actual 2023 row.
