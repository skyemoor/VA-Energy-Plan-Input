"""
fairfax_ci_rooftop_solar_estimate.py

Estimates aggregate rooftop solar MW and annual MWh potential across Fairfax County C&I
buildings, using the 4,510 buildings (>=600 sq ft, Commercial/Industrial/Hotel/Health, deduped by
max footprint per unique Building Identification Number) identified directly from Fairfax
County's own "Buildings" GIS layer as the population.

WHY THIS MODULE'S APPROACH DIFFERS FROM loudoun_ci_rooftop_solar_estimate.py, AND WHY THAT'S THE
RIGHT CALL (Rule 1: reuse what's genuinely shared, don't force a shared shape onto genuinely
different inputs):

Loudoun's source data was business-license records with NO roof-area field at all -- only a
street address per business account, requiring (a) address-based deduplication down to a building
count, then (b) a flat per-building kW figure taken directly from a small real NVRC Solar Map
sample, since there was no building-specific area to size against.

Fairfax's source data is the opposite: a direct building-footprint inventory that already gives a
real Shape__Area (sq ft) for every individual building -- no address deduplication is needed (the
dedup problem here was the different, geometry-driven "podium/multi-component building" issue,
already solved upstream via max(Shape__Area) per unique Building Identification Number before this
module's input is produced), and no separately-sourced building count is needed either. What's
still needed is a way to convert a KNOWN footprint area into kW -- i.e. a DENSITY rate (kW per sq
ft), not a flat per-building figure.

REUSED, NOT DUPLICATED (Rule 6): NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR and HOURS_PER_YEAR are
imported directly from loudoun_ci_rooftop_solar_estimate.py -- same constant, same source
(VA_SLCOE_Model.xlsx row 13), not re-defined under a new name.

REUSED VIA A SHARED CLASS HIERARCHY, PER DIRECT USER REQUEST: the mean-based/median-based totals +
MWh conversion logic (previously duplicated arithmetic in this module, identical in shape to
Loudoun's own) now lives once in rooftop_solar_estimation_base.py's BaseRooftopSolarEstimator,
via the scale_per_unit_value_to_total_mw hook this module implements below
(_FairfaxRooftopEstimator) -- see that module's own docstring for the side-by-side comparison
showing why this is genuinely shared logic, not two independently-similar implementations.

REUSED, NOT RE-GATHERED: the density rate itself is derived from the SAME 8 real NVRC Solar Map
data points already established in loudoun_ci_rooftop_solar_estimate.py's own
NVRC_SAMPLE_KW_DATA_POINTS (imported directly, not re-typed), paired here with each point's own
roof sq ft (from loudoun_test_batch_results.md -- captured when the sample was originally gathered,
but not previously extracted into code since Loudoun's own use case only needed the flat kW
values, not a rate). This is the same underlying real-world sample, applied in the form Fairfax's
different data shape actually needs -- not a new, separately-invented density assumption.

CARRIED FORWARD, PER RULE 2: the same stated limitations that apply to the source NVRC sample in
Loudoun's module apply equally here, since it is the identical sample -- n=8, geographically
narrow (Sterling/Leesburg/Ashburn only, none from Fairfax itself), and reflecting a mid-2010s
imagery vintage. Applying it to Fairfax buildings is a real, additional extrapolation beyond what
Loudoun's own module already carries, since none of the 8 sample points are themselves Fairfax
buildings -- stated here explicitly, not hidden.

Run tests with: python3 -m pytest test_fairfax_ci_rooftop_solar_estimate.py -v
"""
import sys
from dataclasses import dataclass
from typing import List, Tuple

sys.path.insert(0, "/home/claude/work/lp_package/loudoun_ci_rooftop_solar")
sys.path.insert(0, "/home/claude/work/lp_package/rooftop_solar_common")
from loudoun_ci_rooftop_solar_estimate import (  # noqa: E402
    HOURS_PER_YEAR,
    NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR,
    NVRC_SAMPLE_KW_DATA_POINTS,
)
from rooftop_solar_estimation_base import BaseRooftopSolarEstimator, compute_descriptive_stats  # noqa: E402

# ============================================================================
# Real NVRC Solar Map roof sq ft for the SAME 8 data points as
# NVRC_SAMPLE_KW_DATA_POINTS (imported above) -- source: loudoun_test_batch_results.md.
# Order matches NVRC_SAMPLE_KW_DATA_POINTS exactly; paired below via zip(), not
# re-typed as a separate, disconnected list of kW values.
# ============================================================================
NVRC_SAMPLE_ROOF_SQFT_DATA_POINTS = [
    20_922.30,  # 21335 Signal Hill Plz, Sterling
    2_462.01,   # 19 E Market St, Leesburg
    29_787.94,  # 21631 Ridgetop Cir, Sterling
    5_604.48,   # 21370 Potomac View Rd, Sterling
    20_575.50,  # 20365 Exchange St, Ashburn (One Loudoun)
    19_812.31,  # 20405 Exchange St, Ashburn (One Loudoun)
    22_929.52,  # 22405 Enterprise St, Sterling
    2_225.08,   # 44375 Apache Cir, Ashburn
]


@dataclass
class PerSqftKwDensityStats:
    """Analogous in shape to loudoun_ci_rooftop_solar_estimate.py's own
    PerBuildingKwStats, but deliberately a SEPARATE dataclass rather than a
    reused/relabeled one: the units and semantics genuinely differ (a rate,
    kW per sq ft of roof footprint, vs. a flat per-building kW figure), and
    reusing a dataclass whose field names say "_kw" to actually mean
    "_kw_per_sqft" would be a real clarity violation, not a legitimate
    reuse. The underlying n/mean/median/min/max computation IS now
    genuinely shared (via compute_descriptive_stats, imported from
    rooftop_solar_estimation_base.py) -- see
    compute_kw_per_sqft_density_stats below, which builds this dataclass
    by delegating to that shared computation rather than reimplementing
    it."""
    n: int
    mean_kw_per_sqft: float
    median_kw_per_sqft: float
    min_kw_per_sqft: float
    max_kw_per_sqft: float


def compute_kw_per_sqft_density_stats(
    roof_sqft_and_kw_pairs: List[Tuple[float, float]]
) -> PerSqftKwDensityStats:
    """Derives kW/sq ft density rates from paired (roof_sqft, kW) data
    points -- one ratio per point, then descriptive stats over those
    ratios (delegating the actual mean/median/min/max computation to the
    shared compute_descriptive_stats, not reimplementing it here). Used
    with the real NVRC sample (roof sq ft paired with kW for the same 8
    real buildings), not an invented density assumption."""
    ratios = [kw / roof_sqft for roof_sqft, kw in roof_sqft_and_kw_pairs]
    stats = compute_descriptive_stats(ratios)
    return PerSqftKwDensityStats(
        n=stats.n, mean_kw_per_sqft=stats.mean, median_kw_per_sqft=stats.median,
        min_kw_per_sqft=stats.min, max_kw_per_sqft=stats.max,
    )


class _FairfaxRooftopEstimator(BaseRooftopSolarEstimator):
    """This county's own scale_per_unit_value_to_total_mw hook: a
    kW/sqft density gets scaled to a total MW figure by multiplying
    against the total footprint sq ft (known directly from Fairfax's own
    building-footprint GIS inventory). See
    rooftop_solar_estimation_base.py's own module docstring for the
    side-by-side comparison against Loudoun's different hook (building
    count, not footprint area)."""

    def __init__(self, total_footprint_sqft: float):
        self.total_footprint_sqft = total_footprint_sqft

    def scale_per_unit_value_to_total_mw(self, per_unit_value: float) -> float:
        return self.total_footprint_sqft * per_unit_value / 1000


@dataclass
class FairfaxCiRooftopSolarEstimate:
    n_buildings: int
    total_footprint_sqft: float
    density_stats: PerSqftKwDensityStats
    total_mw_mean_based: float
    total_mw_median_based: float
    total_mwh_per_year_mean_based: float
    total_mwh_per_year_median_based: float
    capacity_factor_used: float

    # NOTE: earlier versions of this module also exposed a
    # total_mw_combined / total_mwh_per_year_combined property, computed
    # by simply averaging the mean-based and median-based totals. Removed
    # after direct user challenge -- see RooftopSolarTotals' own
    # docstring (rooftop_solar_estimation_base.py) for the full
    # statistical reasoning: averaging a correct estimator (mean, for an
    # aggregate/sum) with a biased one (median, under a skewed sample)
    # produces an undefined number, not a more careful one. The
    # mean-based total is the primary, recommended figure; the
    # median-based total is a separate, explicitly-labeled sensitivity
    # check.


def estimate_fairfax_ci_rooftop_solar(
    total_footprint_sqft: float,
    n_buildings: int,
    roof_sqft_and_kw_pairs: List[Tuple[float, float]] = None,
    capacity_factor: float = NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR,
) -> FairfaxCiRooftopSolarEstimate:
    """Top-level estimate: applies both the mean- and median-based kW/sqft
    density (from the real NVRC sample) to the known total footprint sq
    ft, via the shared BaseRooftopSolarEstimator.compute_totals() (not
    reimplemented here). Both totals are returned, but they are NOT
    combined/averaged (see FairfaxCiRooftopSolarEstimate's own docstring
    note for why) -- the mean-based total is the statistically
    appropriate primary figure for an aggregate/sum estimate; the
    median-based total is a separate sensitivity check, not a blend
    input."""
    if roof_sqft_and_kw_pairs is None:
        roof_sqft_and_kw_pairs = list(zip(NVRC_SAMPLE_ROOF_SQFT_DATA_POINTS, NVRC_SAMPLE_KW_DATA_POINTS))

    density_stats = compute_kw_per_sqft_density_stats(roof_sqft_and_kw_pairs)

    estimator = _FairfaxRooftopEstimator(total_footprint_sqft)
    totals = estimator.compute_totals(
        mean_per_unit=density_stats.mean_kw_per_sqft, median_per_unit=density_stats.median_kw_per_sqft,
        capacity_factor=capacity_factor, hours_per_year=HOURS_PER_YEAR,
    )

    return FairfaxCiRooftopSolarEstimate(
        n_buildings=n_buildings,
        total_footprint_sqft=total_footprint_sqft,
        density_stats=density_stats,
        total_mw_mean_based=totals.total_mw_mean_based,
        total_mw_median_based=totals.total_mw_median_based,
        total_mwh_per_year_mean_based=totals.total_mwh_per_year_mean_based,
        total_mwh_per_year_median_based=totals.total_mwh_per_year_median_based,
        capacity_factor_used=totals.capacity_factor_used,
    )
