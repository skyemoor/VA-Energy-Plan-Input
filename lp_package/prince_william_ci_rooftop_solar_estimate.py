"""
prince_william_ci_rooftop_solar_estimate.py

Estimates aggregate rooftop solar MW and annual MWh potential across Prince William County C&I
buildings, using the user-provided PWCCommericialBuildings.xlsx (3,876 rows).

SOURCE DATA IS ALREADY PRE-FILTERED, UNLIKE FAIRFAX'S/ARLINGTON'S OWN "BUILDINGS" LAYERS: the full
Prince William County buildings GIS layer exceeded the upload size limit, so the user extracted only
StructureType=3 ("Commercial") rows before upload. Confirmed directly against the full StructureType
legend the user provided:
  1=Residence, 2=House Trailer, 3=Commercial, 4=Residential Outbuilding, 5=Tank, 6=Silo, 7=Tower,
  8=Pool, 9=Recreation Field, 10=Mixed Use
There is NO separate "Industrial" code anywhere in this 10-value legend -- industrial buildings are
almost certainly folded into "3=Commercial" rather than absent from the dataset entirely. This means
this module's population is likely BROADER in composition than Fairfax's/Arlington's own "Commercial
or Retail Facility"/"Commercial / Retail" categories alone (which explicitly exclude industrial,
counted as a separate tag there) -- it plausibly corresponds to "Commercial + Industrial" combined
for those two counties. There is no way to split industrial back out from this data, so this
composition difference is carried forward as a known limitation, not resolved here.

NO DEDUP CHECK POSSIBLE (an open limitation, not assumed away): unlike Fairfax's Building
Identification Number or Arlington's GIS_ID, this dataset has no parcel/building-grouping field at
all -- both OBJECTID and GlobalID are confirmed fully unique across all 3,876 rows (verified
directly, not assumed). This means there is no way to check for the same kind of podium/multi
-component-building issue found in Fairfax's data. Each row is treated as one distinct structure,
since there is no field available to test that assumption against.

The same >=600 sqft minimum-viable-rooftop-size threshold established for Fairfax's and Arlington's
buildings is applied here too, using ShapeSTArea as the footprint field (this dataset's own area
column, analogous to Fairfax's Shape__Area / Arlington's SHAPE_Area).

REUSED VIA THE SAME SHARED CLASS HIERARCHY AS FAIRFAX AND ARLINGTON (Rule 1): Prince William's
situation -- a known per-building footprint area, needing a kW/sqft density rate to convert to
installed capacity -- is structurally identical to those two counties (not Loudoun's flat-per
-building-count approach), so this module reuses BaseRooftopSolarEstimator and the same real
8-point NVRC density sample directly, rather than reimplementing the estimation logic a fourth time.

Run tests with: python3 -m pytest test_prince_william_ci_rooftop_solar_estimate.py -v
"""
import sys
from dataclasses import dataclass

import pandas as pd

sys.path.insert(0, "/home/claude/work/lp_package/loudoun_ci_rooftop_solar")
sys.path.insert(0, "/home/claude/work/lp_package/rooftop_solar_common")
sys.path.insert(0, "/home/claude/work/lp_package/fairfax_ci_rooftop_solar")
from loudoun_ci_rooftop_solar_estimate import (  # noqa: E402
    HOURS_PER_YEAR,
    NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR,
    NVRC_SAMPLE_KW_DATA_POINTS,
)
from fairfax_ci_rooftop_solar_estimate import (  # noqa: E402
    NVRC_SAMPLE_ROOF_SQFT_DATA_POINTS,
    PerSqftKwDensityStats,
    compute_kw_per_sqft_density_stats,
)
from rooftop_solar_estimation_base import BaseRooftopSolarEstimator  # noqa: E402

MIN_VIABLE_ROOFTOP_SQFT = 600  # same established building-rooftop minimum used for Fairfax/Arlington

COMMERCIAL_STRUCTURE_TYPE_CODE = 3  # confirmed against the user-provided full legend; kept as an
# explicit constant (rather than assumed always-true) in case a future, less-pre-filtered extract
# is used with this same module


def build_ci_eligible_population(buildings_df: pd.DataFrame) -> pd.DataFrame:
    """Applies the >=600 sqft minimum-viable-rooftop floor to the (already
    source-pre-filtered-to-Commercial) population. Also defensively
    re-confirms StructureType==3 rather than blindly trusting the input
    is pre-filtered exactly as described -- if a future extract includes
    other StructureType values, this keeps the population correct rather
    than silently including them."""
    commercial = buildings_df[buildings_df["StructureType"] == COMMERCIAL_STRUCTURE_TYPE_CODE]
    return commercial[commercial["ShapeSTArea"] >= MIN_VIABLE_ROOFTOP_SQFT]


class _PrinceWilliamRooftopEstimator(BaseRooftopSolarEstimator):
    """Same hook shape as Fairfax's and Arlington's own estimators: a
    kW/sqft density gets scaled to a total MW figure by multiplying
    against the total footprint sq ft."""

    def __init__(self, total_footprint_sqft: float):
        self.total_footprint_sqft = total_footprint_sqft

    def scale_per_unit_value_to_total_mw(self, per_unit_value: float) -> float:
        return self.total_footprint_sqft * per_unit_value / 1000


@dataclass
class PrinceWilliamCiRooftopSolarEstimate:
    n_buildings: int
    total_footprint_sqft: float
    density_stats: PerSqftKwDensityStats
    total_mw_mean_based: float
    total_mw_median_based: float
    total_mwh_per_year_mean_based: float
    total_mwh_per_year_median_based: float
    capacity_factor_used: float


def estimate_prince_william_ci_rooftop_solar(
    buildings_df: pd.DataFrame,
    capacity_factor: float = NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR,
) -> PrinceWilliamCiRooftopSolarEstimate:
    """Top-level estimate: builds the C&I-eligible population, applies
    both the mean- and median-based kW/sqft density (the same real
    8-point NVRC sample already used for Fairfax and Arlington) via the
    shared BaseRooftopSolarEstimator.compute_totals(). Mean-based is the
    statistically appropriate primary figure for an aggregate/sum
    estimate; median-based is a separate sensitivity check, not blended
    in (see rooftop_solar_estimation_base.py's RooftopSolarTotals
    docstring for the full reasoning)."""
    eligible = build_ci_eligible_population(buildings_df)
    n_buildings = len(eligible)
    total_footprint_sqft = eligible["ShapeSTArea"].sum()

    roof_sqft_and_kw_pairs = list(zip(NVRC_SAMPLE_ROOF_SQFT_DATA_POINTS, NVRC_SAMPLE_KW_DATA_POINTS))
    density_stats = compute_kw_per_sqft_density_stats(roof_sqft_and_kw_pairs)

    estimator = _PrinceWilliamRooftopEstimator(total_footprint_sqft)
    totals = estimator.compute_totals(
        mean_per_unit=density_stats.mean_kw_per_sqft, median_per_unit=density_stats.median_kw_per_sqft,
        capacity_factor=capacity_factor, hours_per_year=HOURS_PER_YEAR,
    )

    return PrinceWilliamCiRooftopSolarEstimate(
        n_buildings=n_buildings,
        total_footprint_sqft=total_footprint_sqft,
        density_stats=density_stats,
        total_mw_mean_based=totals.total_mw_mean_based,
        total_mw_median_based=totals.total_mw_median_based,
        total_mwh_per_year_mean_based=totals.total_mwh_per_year_mean_based,
        total_mwh_per_year_median_based=totals.total_mwh_per_year_median_based,
        capacity_factor_used=totals.capacity_factor_used,
    )
