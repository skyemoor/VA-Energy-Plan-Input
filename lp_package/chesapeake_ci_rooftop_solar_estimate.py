"""
chesapeake_ci_rooftop_solar_estimate.py

Estimates aggregate rooftop solar MW and annual MWh potential across Chesapeake City C&I
buildings, from the city's own Building Outlines GIS layer.

WHY THIS IS THE CLEANEST CLASSIFICATION OF THE FIVE COUNTIES SO FAR

Chesapeake publishes a 14-value BUILDINGCLASS coded domain, obtained directly from its ArcGIS REST
endpoint rather than inferred:

    1 General/Residential   2 Government    3 Medical      4 Education     5 Transportation
    6 Commercial            7 Religious     8 Recreation   9 Cultural/Heritage
   10 Hospitality          11 Airport      12 Industrial  13 CommunityCenter  14 Apartment

That is a near-superset of Arlington's CM_Type scheme, and two of its additions make it strictly
better than what Arlington allowed.

**Industrial (12) exists as its own class.** Arlington had no industrial category at all. Prince
William's source folds industrial into "Commercial" -- its module records that there is no separate
industrial code anywhere in that 10-value legend. Fairfax counts them separately. Including
Industrial here therefore makes Chesapeake consistent with Fairfax and Prince William, and more
complete than Arlington, rather than introducing an inconsistency.

**Apartment (14) removes Arlington's weakest step.** Arlington had to apply a size heuristic --
"General / Residential" over 2,000 sqft assumed commercial, on the reasoning that large
residential structures are apartment or condo buildings, often company-owned and so more like a
commercial roof in decision-making terms. That judgment was applied to 9,956 buildings and is the
least defensible part of that module. Chesapeake states the category outright, so the heuristic is
not needed: Apartment is included directly and General/Residential is excluded entirely.

STATED CONSEQUENCE: Chesapeake and Arlington therefore use DIFFERENT rules. That is deliberate.
Using the best classification each dataset supports is preferable to degrading Chesapeake's to
match Arlington's limitation -- but the two are consequently not strictly like-for-like, and any
cross-county comparison should say so.

EXCLUSIONS follow Arlington's established precedent: Government (= "Government / Military"),
Education (avoiding double-count with the school-solar work), Transportation, Religious,
Recreation, Airport and CommunityCenter. Cultural/Heritage has no exact Arlington analogue; it is
excluded as the nearest match to "Community Center".

SOURCE DATA IS PRE-FILTERED AT EXTRACTION. The supplied file contains 5,838 rows across exactly
the five included classes -- the selection was made in the city's own map interface before export.
build_ci_eligible_population() therefore re-applies the class filter defensively rather than
trusting the extract, so a future, less-filtered export is handled correctly.

A NAME FIELD IS PRESENT, which no other county's extract provided ("Amazon Warehouse", "Parkview
Shopping Center", "Firestone"). It is not used in any calculation, but it makes the classification
spot-checkable against reality -- see this module's tests, which assert that a known warehouse
lands in Industrial rather than assuming the coded domain is applied correctly.

CLASSIFICATION IS INCONSISTENTLY APPLIED -- found 2026-09-11 using the NAME field, and not
detectable in any other county's extract. Chesapeake's 636,190 sqft Amazon distribution centre
(14.6 acres) is classified BUILDINGCLASS=6 Commercial, not 12 Industrial, though the schema has an
Industrial class. A published coded domain states what the codes MEAN; it does not guarantee how
consistently they were APPLIED.

  - The C&I TOTAL is unaffected: Commercial and Industrial are both included either way.
  - The PER-CLASS BREAKDOWN below is therefore indicative, not reliable. Its 32.0% Industrial
    share understates real industrial presence, and the split must NOT be used for anything
    load-shape dependent -- an industrial roof and a retail roof sit above very different
    consumption profiles.
  - The same inconsistency may exist in Fairfax, Arlington and Prince William and be
    undetectable there, since none of those extracts carry a name field.

REUSED VIA THE SAME SHARED CLASS HIERARCHY AS FAIRFAX, ARLINGTON AND PRINCE WILLIAM (Rule 1):
Chesapeake's situation -- a known per-building footprint area, needing a kW/sqft density rate -- is
structurally identical to those three, so this module reuses BaseRooftopSolarEstimator and the same
real 8-point NVRC density sample rather than reimplementing the estimation logic a fifth time.

CARRIED FORWARD: the NVRC sample's own stated limitations apply here as they do everywhere else it
is used -- n=8, all points in Sterling/Leesburg/Ashburn, none in Hampton Roads, mid-2010s imagery
vintage. Applying a Loudoun-derived density to Chesapeake buildings is a real extrapolation, stated
rather than hidden.

Run tests with: python3 -m pytest test_chesapeake_siting.py -v
"""
from dataclasses import dataclass

import pandas as pd

from loudoun_ci_rooftop_solar_estimate import (
    HOURS_PER_YEAR,
    NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR,
    NVRC_SAMPLE_KW_DATA_POINTS,
)
from fairfax_ci_rooftop_solar_estimate import (
    NVRC_SAMPLE_ROOF_SQFT_DATA_POINTS,
    PerSqftKwDensityStats,
    compute_kw_per_sqft_density_stats,
)
from rooftop_solar_estimation_base import BaseRooftopSolarEstimator

#: Chesapeake's own coded-value domain, read from its ArcGIS REST endpoint -- not inferred from
#: another county's numbering. That distinction matters: Richmond's Structures SubType 3 was
#: assumed C&I because Prince William's StructureType=3 is Commercial, and turned out to be
#: accessory structures with a 200 sqft median.
BUILDING_CLASS_LEGEND = {
    1: 'General/Residential', 2: 'Government', 3: 'Medical', 4: 'Education',
    5: 'Transportation', 6: 'Commercial', 7: 'Religious', 8: 'Recreation',
    9: 'Cultural/Heritage', 10: 'Hospitality', 11: 'Airport', 12: 'Industrial',
    13: 'CommunityCenter', 14: 'Apartment',
}

#: See module docstring for the rationale on each. Industrial and Apartment are the two that
#: differ from Arlington's own included set.
CI_ELIGIBLE_BUILDING_CLASSES = [3, 6, 10, 12, 14]

MIN_VIABLE_ROOFTOP_SQFT = 600  # same floor used for Fairfax, Arlington and Prince William

AREA_COLUMN = 'SHAPESTArea'    # a third naming convention: not Shape__Area, not SHAPE_Area


def build_ci_eligible_population(buildings_df: pd.DataFrame) -> pd.DataFrame:
    """Applies the class filter and the >=600 sqft minimum-viable-rooftop floor.

    Re-applies the class filter defensively even though the supplied extract is already
    pre-filtered at source -- Rule 5: a future, less-filtered export must be handled correctly
    rather than silently including classes this module excludes.
    """
    if AREA_COLUMN not in buildings_df.columns:
        raise ValueError(
            f"expected column {AREA_COLUMN!r} in the Chesapeake extract; found "
            f"{list(buildings_df.columns)}. Chesapeake uses SHAPESTArea, distinct from Fairfax's "
            f"Shape__Area and Arlington's SHAPE_Area -- do not assume the convention.")
    eligible = buildings_df[buildings_df['BUILDINGCLASS'].isin(CI_ELIGIBLE_BUILDING_CLASSES)]
    return eligible[eligible[AREA_COLUMN] >= MIN_VIABLE_ROOFTOP_SQFT]


class _ChesapeakeRooftopEstimator(BaseRooftopSolarEstimator):
    """Same hook shape as Fairfax's, Arlington's and Prince William's: a kW/sqft density scaled to
    total MW by the total footprint area."""

    def __init__(self, total_footprint_sqft: float):
        self.total_footprint_sqft = total_footprint_sqft

    def scale_per_unit_value_to_total_mw(self, per_unit_value: float) -> float:
        return self.total_footprint_sqft * per_unit_value / 1000


@dataclass
class ChesapeakeCiRooftopSolarEstimate:
    n_buildings: int
    total_footprint_sqft: float
    density_stats: PerSqftKwDensityStats
    total_mw_mean_based: float
    total_mw_median_based: float
    total_mwh_per_year_mean_based: float
    total_mwh_per_year_median_based: float
    capacity_factor_used: float
    buildings_by_class: dict


def estimate_chesapeake_ci_rooftop_solar(
    buildings_df: pd.DataFrame,
    capacity_factor: float = NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR,
) -> ChesapeakeCiRooftopSolarEstimate:
    """Top-level estimate. Mean-based is the statistically appropriate primary figure for an
    aggregate; median-based is a separate sensitivity check, never blended -- see
    rooftop_solar_estimation_base.RooftopSolarTotals for the full reasoning.

    Also returns a per-class breakdown, which no other county's estimate does. Chesapeake is the
    first extract with a rich enough legend to make one meaningful, and it matters here because
    Industrial and Apartment are included on this project's own judgment rather than on
    established precedent -- so their contribution should be visible rather than buried in a total
    someone would have to take on trust.
    """
    eligible = build_ci_eligible_population(buildings_df)
    n_buildings = len(eligible)
    total_footprint_sqft = eligible[AREA_COLUMN].sum()

    density_stats = compute_kw_per_sqft_density_stats(
        list(zip(NVRC_SAMPLE_ROOF_SQFT_DATA_POINTS, NVRC_SAMPLE_KW_DATA_POINTS)))

    totals = _ChesapeakeRooftopEstimator(total_footprint_sqft).compute_totals(
        mean_per_unit=density_stats.mean_kw_per_sqft,
        median_per_unit=density_stats.median_kw_per_sqft,
        capacity_factor=capacity_factor, hours_per_year=HOURS_PER_YEAR,
    )

    by_class = {}
    for code, grp in eligible.groupby('BUILDINGCLASS'):
        by_class[BUILDING_CLASS_LEGEND.get(code, f'code {code}')] = {
            'buildings': len(grp),
            'footprint_sqft': float(grp[AREA_COLUMN].sum()),
            'share_of_footprint': float(grp[AREA_COLUMN].sum() / total_footprint_sqft),
        }

    return ChesapeakeCiRooftopSolarEstimate(
        n_buildings=n_buildings,
        total_footprint_sqft=total_footprint_sqft,
        density_stats=density_stats,
        total_mw_mean_based=totals.total_mw_mean_based,
        total_mw_median_based=totals.total_mw_median_based,
        total_mwh_per_year_mean_based=totals.total_mwh_per_year_mean_based,
        total_mwh_per_year_median_based=totals.total_mwh_per_year_median_based,
        capacity_factor_used=totals.capacity_factor_used,
        buildings_by_class=by_class,
    )
