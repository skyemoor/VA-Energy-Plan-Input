"""
arlington_ci_rooftop_solar_estimate.py

Estimates aggregate rooftop solar MW and annual MWh potential across Arlington County C&I
buildings, using Arlington's own "Buildings" GIS layer (Arlington_Buildings.csv, 49,064 rows).

WHY THIS MODULE'S CLASSIFICATION LOGIC DIFFERS FROM BOTH LOUDOUN'S AND FAIRFAX'S OWN MODULES, AND
WHY THAT'S THE RIGHT CALL (Rule 1: reuse what's genuinely shared, don't force a shared shape onto
genuinely different inputs):

Arlington's "CM_Type" field (its own "Community Maps Type"-style classification, directly parallel
to Fairfax's own naming) severely under-tags commercial buildings: only 164 of 49,064 rows (0.33%)
are tagged "Commercial / Retail" -- confirmed directly against the real data, not taken on faith --
an implausibly low figure for a dense, highly-commercialized jurisdiction like Arlington. Per
direct user instruction, this is supplemented with a size heuristic: any "General / Residential"-
tagged building over 2,000 sq ft is assumed commercial (rationale given directly by the user: large
"residential"-classified structures in this context are likely apartment/condo buildings, which are
often company-owned rental properties -- more like a commercial building's roof in terms of
decision-making/economics than a single-family home's roof).

CATEGORY DECISIONS, PER DIRECT USER INSTRUCTION AND ESTABLISHED PRECEDENT:
- Directly included (already tagged C&I-relevant, no size heuristic needed): "Commercial / Retail",
  "Medical", "Hotel" -- the latter two follow the same precedent as Fairfax's own "Health or
  Medical Facility" and "Hotel / Motel" categories.
- Included via the size heuristic: "General / Residential" rows > 2,000 sqft.
- Excluded per DIRECT user instruction this round: "Religious", "Government / Military".
- Excluded per the SAME precedent already established for Fairfax (not re-stated by the user this
  round, but consistent with how analogous categories were handled there): "Education" (to avoid
  double-counting with the separate school-solar module), "Community Center", "Transportation",
  "Recreation", "Airport" (non-C&I in the conventional sense -- "Airport" in particular is a single
  762,694 sqft row, almost certainly Reagan National's own terminal, federally-operated
  infrastructure, not a conventional C&I rooftop-solar candidate).

POdium/multi-part dedup (Rule 1, reusing the same underlying concern as Fairfax's max(Shape__Area)
per Building Identification Number approach): GIS_ID was checked directly for duplicates within the
C&I-eligible population specifically -- ZERO found (0 of 10,120 eligible rows share a GIS_ID with
another eligible row), so no dedup step is applied here. This is a real, checked finding, not an
assumption that Arlington's data doesn't have the same multi-part-building issue Fairfax's did (the
dataset's own description uses the same "a building may be made up of many parts" language) -- it
simply doesn't manifest within this specific eligible subset.

The same >=600 sqft minimum-viable-rooftop-size threshold established for Fairfax's buildings
(distinct from the >=6,000 sqft parking-lot threshold) is applied here too, after the
classification step above -- confirmed to do real work: 10 of the 164 explicit "Commercial /
Retail" rows fall under 600 sqft, while every "General / Residential" row that clears the 2,000
sqft heuristic automatically clears 600 sqft too.

REUSED VIA THE SAME SHARED CLASS HIERARCHY AS FAIRFAX (Rule 1): Arlington's situation -- a known
per-building footprint area, needing a kW/sqft density rate to convert to installed capacity -- is
structurally identical to Fairfax's (not Loudoun's flat-per-building-count approach), so this
module reuses BaseRooftopSolarEstimator and the same real 8-point NVRC density sample directly,
rather than reimplementing the estimation logic a third time.

Run tests with: python3 -m pytest test_arlington_ci_rooftop_solar_estimate.py -v
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

# ============================================================================
# Category classification constants -- see module docstring for full sourcing/rationale.
# ============================================================================
DIRECTLY_INCLUDED_CM_TYPES = ["Commercial / Retail", "Medical", "Hotel"]
RESIDENTIAL_CM_TYPE = "General / Residential"
RESIDENTIAL_TO_COMMERCIAL_SQFT_THRESHOLD = 2_000  # direct user decision this round

MIN_VIABLE_ROOFTOP_SQFT = 600  # same established building-rooftop minimum used for Fairfax


def build_ci_eligible_population(buildings_df: pd.DataFrame) -> pd.DataFrame:
    """Applies the full classification: directly-included CM_Types, plus
    General/Residential rows clearing the size heuristic, then the
    >=600 sqft minimum-viable-rooftop floor on the combined set.
    Returns the filtered, still-row-level DataFrame (not yet summed) so
    callers can inspect the population directly before aggregating."""
    directly_included = buildings_df[buildings_df["CM_Type"].isin(DIRECTLY_INCLUDED_CM_TYPES)]
    resi_over_threshold = buildings_df[
        (buildings_df["CM_Type"] == RESIDENTIAL_CM_TYPE)
        & (buildings_df["SHAPE_Area"] > RESIDENTIAL_TO_COMMERCIAL_SQFT_THRESHOLD)
    ]
    combined = pd.concat([directly_included, resi_over_threshold])
    return combined[combined["SHAPE_Area"] >= MIN_VIABLE_ROOFTOP_SQFT]


def build_school_education_population(buildings_df: pd.DataFrame) -> pd.DataFrame:
    """Returns all rows tagged CM_Type='Education' in Arlington's own
    Buildings GIS layer -- the real, measured footprint for every
    identifiable education-related building (schools, plus a handful of
    related facilities sharing the same CM_Type tag, e.g. the David M
    Brown Planetarium and a few administrative/secondary-program
    buildings). NOT narrowed by school type (ES/MS/HS) -- per direct user
    instruction, this population feeds a single, aggregate MW/MWh figure
    rather than a per-type breakdown. Includes Bishop O'Connell High
    School (a private/parochial school, not APS) and the small number of
    non-comprehensive/administrative entries flagged in chat when the
    per-type breakdown was computed -- not excluded here, since the
    question this function answers is "how much rooftop solar potential
    exists across Arlington's identifiable education-related buildings,"
    not "how much exists at APS-owned comprehensive schools specifically."
    Callers wanting a narrower population should filter buildings_df
    themselves before calling."""
    return buildings_df[buildings_df["CM_Type"] == "Education"]


def estimate_arlington_school_rooftop_solar(
    buildings_df: pd.DataFrame,
    capacity_factor: float = NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR,
) -> "ArlingtonCiRooftopSolarEstimate":
    """Same estimation approach as estimate_arlington_ci_rooftop_solar
    (same shared BaseRooftopSolarEstimator hook, same real 8-point NVRC
    density sample), applied to the school-education population instead
    of the C&I-eligible one. Returns the SAME ArlingtonCiRooftopSolarEstimate
    shape -- the fields (n_buildings, total_footprint_sqft, density_stats,
    mean/median MW+MWh) are genuinely identical in meaning here, just
    describing a different underlying building population, so reusing the
    one dataclass is a real reuse (Rule 1), not a naming mismatch the way
    PerBuildingKwStats vs. PerSqftKwDensityStats would have been."""
    eligible = build_school_education_population(buildings_df)
    n_buildings = len(eligible)
    total_footprint_sqft = eligible["SHAPE_Area"].sum()

    roof_sqft_and_kw_pairs = list(zip(NVRC_SAMPLE_ROOF_SQFT_DATA_POINTS, NVRC_SAMPLE_KW_DATA_POINTS))
    density_stats = compute_kw_per_sqft_density_stats(roof_sqft_and_kw_pairs)

    estimator = _ArlingtonRooftopEstimator(total_footprint_sqft)
    totals = estimator.compute_totals(
        mean_per_unit=density_stats.mean_kw_per_sqft, median_per_unit=density_stats.median_kw_per_sqft,
        capacity_factor=capacity_factor, hours_per_year=HOURS_PER_YEAR,
    )

    return ArlingtonCiRooftopSolarEstimate(
        n_buildings=n_buildings,
        total_footprint_sqft=total_footprint_sqft,
        density_stats=density_stats,
        total_mw_mean_based=totals.total_mw_mean_based,
        total_mw_median_based=totals.total_mw_median_based,
        total_mwh_per_year_mean_based=totals.total_mwh_per_year_mean_based,
        total_mwh_per_year_median_based=totals.total_mwh_per_year_median_based,
        capacity_factor_used=totals.capacity_factor_used,
    )


class _ArlingtonRooftopEstimator(BaseRooftopSolarEstimator):
    """Same hook shape as Fairfax's own _FairfaxRooftopEstimator: a
    kW/sqft density gets scaled to a total MW figure by multiplying
    against the total footprint sq ft. Shared by both
    estimate_arlington_ci_rooftop_solar and
    estimate_arlington_school_rooftop_solar -- the scaling relationship
    is identical regardless of which building population is being
    converted."""

    def __init__(self, total_footprint_sqft: float):
        self.total_footprint_sqft = total_footprint_sqft

    def scale_per_unit_value_to_total_mw(self, per_unit_value: float) -> float:
        return self.total_footprint_sqft * per_unit_value / 1000


@dataclass
class ArlingtonCiRooftopSolarEstimate:
    n_buildings: int
    total_footprint_sqft: float
    density_stats: PerSqftKwDensityStats
    total_mw_mean_based: float
    total_mw_median_based: float
    total_mwh_per_year_mean_based: float
    total_mwh_per_year_median_based: float
    capacity_factor_used: float


def estimate_arlington_ci_rooftop_solar(
    buildings_df: pd.DataFrame,
    capacity_factor: float = NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR,
) -> ArlingtonCiRooftopSolarEstimate:
    """Top-level estimate: builds the C&I-eligible population, applies
    both the mean- and median-based kW/sqft density (the same real
    8-point NVRC sample already used for Fairfax) via the shared
    BaseRooftopSolarEstimator.compute_totals(). Mean-based is the
    statistically appropriate primary figure for an aggregate/sum
    estimate; median-based is a separate sensitivity check, not blended
    in (see rooftop_solar_estimation_base.py's RooftopSolarTotals
    docstring for the full reasoning, established after direct user
    challenge on the Fairfax module)."""
    eligible = build_ci_eligible_population(buildings_df)
    n_buildings = len(eligible)
    total_footprint_sqft = eligible["SHAPE_Area"].sum()

    roof_sqft_and_kw_pairs = list(zip(NVRC_SAMPLE_ROOF_SQFT_DATA_POINTS, NVRC_SAMPLE_KW_DATA_POINTS))
    density_stats = compute_kw_per_sqft_density_stats(roof_sqft_and_kw_pairs)

    estimator = _ArlingtonRooftopEstimator(total_footprint_sqft)
    totals = estimator.compute_totals(
        mean_per_unit=density_stats.mean_kw_per_sqft, median_per_unit=density_stats.median_kw_per_sqft,
        capacity_factor=capacity_factor, hours_per_year=HOURS_PER_YEAR,
    )

    return ArlingtonCiRooftopSolarEstimate(
        n_buildings=n_buildings,
        total_footprint_sqft=total_footprint_sqft,
        density_stats=density_stats,
        total_mw_mean_based=totals.total_mw_mean_based,
        total_mw_median_based=totals.total_mw_median_based,
        total_mwh_per_year_mean_based=totals.total_mwh_per_year_mean_based,
        total_mwh_per_year_median_based=totals.total_mwh_per_year_median_based,
        capacity_factor_used=totals.capacity_factor_used,
    )
