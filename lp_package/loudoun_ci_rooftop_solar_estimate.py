"""
loudoun_ci_rooftop_solar_estimate.py

Estimates aggregate rooftop solar MW and annual MWh potential across Loudoun County C&I
buildings, using the 14,303 not-hard-excluded records from address_classifier.py's full-county
run (loudoun_full_classified.csv) as the building population, and real NVRC Solar Map data points
(gathered directly from the live map earlier this session, see loudoun_test_batch_results.md) to
size a per-building capacity.

METHODOLOGY, and why each step is shaped the way it is:

1. DEDUPLICATION BY BUILDING, NOT BY BUSINESS ACCOUNT. The 14,303 records are business accounts,
   not buildings -- multiple tenants at the same street address (different suites) share one roof,
   and a real, larger pattern was found directly in this data: many records share the EXACT SAME
   address including suite number (e.g. one suite appearing 33 times), consistent with shared/
   virtual-office registrations rather than one business per suite. Counting every business record
   as its own roof would badly overcount. Deduplication runs in two passes for this reason: first
   by the exact, full address (catches the same-suite-many-businesses case), then by the
   suite-stripped address (catches the different-suites-one-building case).

2. PER-BUILDING kW FROM REAL NVRC DATA, NOT AN INVENTED DENSITY ASSUMPTION. The 8 cleanly-usable
   NVRC Solar Map data points gathered earlier this session (loudoun_test_batch_results.md) give
   roof sqft, usable %, AND kW directly for each real building -- kW is used directly rather than
   re-deriving it from a separately-assumed W/sqft density, since the NVRC platform's own kW figure
   is already the more authoritative number for these specific, real buildings.

3. SMALL SAMPLE, GEOGRAPHICALLY NARROW -- STATED, NOT HIDDEN. n=8, and all 8 are in Sterling,
   Leesburg, or Ashburn -- none from Round Hill, Hamilton, Middleburg, Purcellville, or the
   county's more rural/historic communities, which plausibly have a different building-size profile
   (e.g. Middleburg's historic downtown likely skews smaller). Both mean and median per-building kW
   are computed and carried through, since the sample's wide range (9.72-226.09 kW, ~23x spread)
   means the two can differ substantially, and neither should be presented as the only answer.

4. CAPACITY FACTOR REUSES THE PROJECT'S OWN, ALREADY-SOURCED FIGURE. 20% (VA_SLCOE_Model.xlsx,
   "Assumptions & Sources" row 13, "NEM distributed solar capacity factor" -- NREL PVWatts typical
   range for mid-Atlantic fixed-tilt systems), not the 24% utility-scale figure (row 23) or any
   newly-invented number, per this project's own single-source-of-truth convention.

5. RESULT IS A CONSERVATIVE LOWER BOUND, PER THE PROJECT'S OWN ALREADY-ESTABLISHED POSITION
   (VA_SLCOE_Model.xlsx rows 126-127). The NVRC dataset's own ~2016 LiDAR vintage means post-2016
   construction is underrepresented in the source data both for the 8-point sample AND for the
   14,303-record building population being sized -- this estimate inherits that same limitation,
   not a new one introduced here.

Run tests with: python3 -m pytest test_loudoun_ci_rooftop_solar_estimate.py -v
"""
import csv
import re
import sys
from dataclasses import dataclass
from statistics import mean, median
from typing import List

sys.path.insert(0, "/home/claude/work/lp_package/rooftop_solar_common")
from rooftop_solar_estimation_base import BaseRooftopSolarEstimator, compute_descriptive_stats  # noqa: E402

# ============================================================================
# SECTION 1: Real NVRC Solar Map data points, gathered directly from the live
# map earlier this session (loudoun_test_batch_results.md). This is the full
# set of "cleanly usable" results -- excludes 22611 Markey Ct (flagged
# unreliable, multi-building merge) and 42340 Soave Dr (valid data, wrong
# structure type -- a parking garage, not a C&I rooftop), per that file's own
# documented findings.
# ============================================================================

NVRC_SAMPLE_KW_DATA_POINTS = [
    132.41,  # 21335 Signal Hill Plz, Sterling
    9.72,    # 19 E Market St, Leesburg
    195.62,  # 21631 Ridgetop Cir, Sterling
    44.26,   # 21370 Potomac View Rd, Sterling
    171.63,  # 20365 Exchange St, Ashburn (One Loudoun)
    133.85,  # 20405 Exchange St, Ashburn (One Loudoun)
    226.09,  # 22405 Enterprise St, Sterling
    10.31,   # 44375 Apache Cir, Ashburn
]
# Source: loudoun_test_batch_results.md. All 8 are in Sterling, Leesburg, or
# Ashburn specifically -- a real, stated limitation on how far this sample's
# average should be trusted to generalize across the whole county. See
# module docstring point 3.

# NEM distributed solar capacity factor -- VA_SLCOE_Model.xlsx, "Assumptions
# & Sources" tab, row 13. Distinct from the 24% utility-scale figure (row
# 23): rooftop systems are typically fixed-tilt, not tracking, and don't
# share utility-scale siting/orientation optimization.
NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR = 0.20

HOURS_PER_YEAR = 8_760

# Regex for suite/unit/floor designations, adapted from
# address_classifier.py's has_suite_indicator -- but used here to actually
# STRIP the matched text (for building-level deduplication), not just detect
# its presence.
_SUITE_PATTERN = re.compile(r"\b(ste|suite|unit|apt|fl|floor|bldg|building)\b\.?\s*[\w-]+\b", re.IGNORECASE)


def strip_suite_from_address(address: str) -> str:
    """Removes a suite/unit/floor designation from an address string, for
    building-level (not business-account-level) deduplication. E.g.
    '21631 RIDGETOP CIR STE 250' -> '21631 RIDGETOP CIR'."""
    stripped = _SUITE_PATTERN.sub("", address)
    return re.sub(r"\s+", " ", stripped).strip().rstrip(",")


@dataclass
class BuildingDedupResult:
    """Both dedup stages recorded explicitly and separately, not just the
    final count -- so the two distinct patterns behind the reduction (exact-
    address reuse vs. different-suite-same-building) stay visible rather
    than being collapsed into one opaque number."""
    total_records: int
    unique_exact_addresses: int  # after pass 1: dedup by full, exact address
    unique_buildings: int  # after pass 2: dedup by suite-stripped address


def count_unique_buildings(records: List[dict]) -> BuildingDedupResult:
    """Two-pass deduplication from business-account records to a unique-
    building count. Pass 1 (exact address) catches the same-suite-many-
    businesses pattern found directly in this data (e.g. one suite
    registered under 33 different business names); pass 2 (suite-stripped)
    catches the different-suites-one-building pattern. Records with an
    empty address (after any upstream corruption-recovery step) are
    excluded from the building count entirely -- there's no address text to
    deduplicate against, and counting them as a distinct "building" would
    silently fabricate buildings with no addressable evidence at all.
    """
    total = len(records)

    exact_addresses = set()
    for r in records:
        addr = r["address"].strip().upper()
        city = r["city"].strip().upper()
        if addr:
            exact_addresses.add((addr, city))

    buildings = set()
    for addr, city in exact_addresses:
        buildings.add((strip_suite_from_address(addr), city))

    return BuildingDedupResult(
        total_records=total,
        unique_exact_addresses=len(exact_addresses),
        unique_buildings=len(buildings),
    )


@dataclass
class PerBuildingKwStats:
    """The underlying n/mean/median/min/max computation is now genuinely
    shared (via compute_descriptive_stats, imported from
    rooftop_solar_estimation_base.py) -- see compute_per_building_kw_stats
    below, which builds this dataclass by delegating to that shared
    computation rather than reimplementing it. This dataclass itself
    stays separate from fairfax_ci_rooftop_solar_estimate.py's own
    PerSqftKwDensityStats: same shape, but genuinely different units/
    semantics (a flat per-building kW figure here, vs. a kW-per-sq-ft
    rate there), and collapsing them into one shared type would
    reintroduce a real clarity problem for no genuine reuse gain."""
    n: int
    mean_kw: float
    median_kw: float
    min_kw: float
    max_kw: float


def compute_per_building_kw_stats(sample_kw_data_points: List[float]) -> PerBuildingKwStats:
    stats = compute_descriptive_stats(sample_kw_data_points)
    return PerBuildingKwStats(n=stats.n, mean_kw=stats.mean, median_kw=stats.median,
                               min_kw=stats.min, max_kw=stats.max)


class _LoudounRooftopEstimator(BaseRooftopSolarEstimator):
    """This county's own scale_per_unit_value_to_total_mw hook: a flat
    per-building kW figure gets scaled to a total MW figure by
    multiplying against the deduplicated building COUNT (Loudoun's
    source data -- business-license records -- had no area field at all,
    unlike Fairfax's direct building-footprint inventory). See
    rooftop_solar_estimation_base.py's own module docstring for the
    side-by-side comparison against Fairfax's different hook."""

    def __init__(self, unique_buildings: int):
        self.unique_buildings = unique_buildings

    def scale_per_unit_value_to_total_mw(self, per_unit_value: float) -> float:
        return self.unique_buildings * per_unit_value / 1000


@dataclass
class LoudounCiRooftopSolarEstimate:
    dedup: BuildingDedupResult
    kw_stats: PerBuildingKwStats
    total_mw_mean_based: float
    total_mw_median_based: float
    total_mwh_per_year_mean_based: float
    total_mwh_per_year_median_based: float
    capacity_factor_used: float

    # NOTE: earlier versions of this module exposed a total_mw_combined /
    # total_mwh_per_year_combined property, computed by simply averaging
    # the mean-based and median-based totals. Removed after direct user
    # challenge -- see RooftopSolarTotals' own docstring
    # (rooftop_solar_estimation_base.py) for the full statistical
    # reasoning: averaging a correct estimator (mean, for an
    # aggregate/sum) with a biased one (median, under a skewed sample --
    # this sample's raw kW values span ~23x min-to-max) produces an
    # undefined number, not a more careful one. The mean-based total is
    # the primary, recommended figure; the median-based total is a
    # separate, explicitly-labeled sensitivity check.


def estimate_loudoun_ci_rooftop_solar(
    records: List[dict],
    sample_kw_data_points: List[float] = None,
    capacity_factor: float = NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR,
) -> LoudounCiRooftopSolarEstimate:
    """Top-level estimate: deduplicates records to a building count,
    applies both the mean and median per-building kW from the real NVRC
    sample via the shared BaseRooftopSolarEstimator.compute_totals() (not
    reimplemented here). Both totals are returned, but they are NOT
    combined/averaged (see LoudounCiRooftopSolarEstimate's own docstring
    note for why) -- the mean-based total is the statistically
    appropriate primary figure for an aggregate/sum estimate; the
    median-based total is a separate sensitivity check, not a blend
    input."""
    if sample_kw_data_points is None:
        sample_kw_data_points = NVRC_SAMPLE_KW_DATA_POINTS

    dedup = count_unique_buildings(records)
    kw_stats = compute_per_building_kw_stats(sample_kw_data_points)

    estimator = _LoudounRooftopEstimator(dedup.unique_buildings)
    totals = estimator.compute_totals(
        mean_per_unit=kw_stats.mean_kw, median_per_unit=kw_stats.median_kw,
        capacity_factor=capacity_factor, hours_per_year=HOURS_PER_YEAR,
    )

    return LoudounCiRooftopSolarEstimate(
        dedup=dedup,
        kw_stats=kw_stats,
        total_mw_mean_based=totals.total_mw_mean_based,
        total_mw_median_based=totals.total_mw_median_based,
        total_mwh_per_year_mean_based=totals.total_mwh_per_year_mean_based,
        total_mwh_per_year_median_based=totals.total_mwh_per_year_median_based,
        capacity_factor_used=totals.capacity_factor_used,
    )


def load_not_hard_excluded_records(csv_path: str) -> List[dict]:
    """Loads only the not-hard-excluded rows from the full classified CSV --
    the population this module sizes solar against, per direct user
    instruction to use "the ones that have not been excluded.\""""
    records = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["hard_excluded"].strip().upper() == "FALSE":
                records.append(row)
    return records


def build_unique_building_list(records: List[dict]) -> List[dict]:
    """Returns one row per unique building (suite-stripped address + city),
    each annotated with how many business-account records share it -- the
    concrete, inspectable data behind count_unique_buildings' summary count,
    not just the aggregate number."""
    exact_groups = {}  # (address, city) -> list of original records
    for r in records:
        addr = r["address"].strip().upper()
        city = r["city"].strip().upper()
        if not addr:
            continue
        exact_groups.setdefault((addr, city), []).append(r)

    building_groups = {}  # (base_address, city) -> list of (exact_address, record_count)
    for (addr, city), recs in exact_groups.items():
        building_key = (strip_suite_from_address(addr), city)
        building_groups.setdefault(building_key, []).append((addr, recs[0]["state"], len(recs)))

    rows = []
    for (base_address, city), exact_entries in building_groups.items():
        state = exact_entries[0][1]  # state is consistent for a given city in practice
        rows.append({
            "base_address": base_address,
            "city": city,
            "state": state,
            "unique_suites_at_this_building": len(exact_entries),
            "total_business_records_at_this_building": sum(count for _, _, count in exact_entries),
        })
    return rows
