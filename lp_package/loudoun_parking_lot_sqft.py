"""
loudoun_parking_lot_sqft.py

Estimates aggregate parking lot square footage in Loudoun County from the county's own "Road
Casings" GIS dataset (Office of Mapping and Geographic Information, most recently updated 2023-24),
filtered to RD_TYPE=2 (parking lots) and provided directly by the user as
Loudoun_Road_Casing_type_2.xlsx.

This is REAL, surveyed county geometry -- each polygon has a directly-measured area (Shape_Area,
in square feet, confirmed by the underlying Virginia State Plane North coordinate system's US
survey foot units), not an inferred or estimated figure. This is a materially better data vintage
than the NVRC rooftop dataset used elsewhere in this project: 96%+ of rows were last updated in
2022 or later (77% in 2024 alone), versus the NVRC rooftop data's ~2016 evaluation date.

TWO REAL DATA-QUALITY QUESTIONS surfaced by direct inspection, neither silently resolved here:

1. SMALL FRAGMENTS: nearly half of all 11,317 polygons (5,572) are smaller than what the county's
   own data dictionary defines as a qualifying "Type 2" feature (commercial parking over 200 ft
   long / 20+ spaces, which implies roughly 6,000+ sqft at a standard ~300 sqft/space planning
   figure including drive aisles). These smaller polygons only account for ~4.8% of total area,
   so their inclusion/exclusion doesn't swing the headline number much -- but their prevalence
   suggests many real parking lots are digitized as multiple adjacent polygon fragments (islands,
   different paving dates, etc.) rather than one polygon per physical lot, which matters for
   understanding what "11,317 rows" actually represents (not 11,317 distinct physical lots).

2. LARGE-POLYGON CONCENTRATION, UNVERIFIED: the largest single polygon alone is 92.8 acres
   (1.64% of the entire county total from one row), and the 38 largest polygons combined (0.34%
   of all rows) account for 13.3% of the total. This dataset has no address, parcel ID, or
   location field to cross-reference against -- unlike the NVRC rooftop sample earlier in this
   project, where a real merge artifact (multiple buildings combined into one reported area) was
   caught specifically BECAUSE an address was available to check against Street View. That same
   verification is not possible here with the fields provided. These large polygons are neither
   confirmed genuine nor confirmed artifacts -- flagged, not resolved.

Because of these open questions, this module does NOT hardcode a single "correct" filter.
compute_totals() returns multiple totals side by side (unfiltered, paved-only, size-filtered,
and combinations) so the choice of which to use as the headline figure is a visible, deliberate
decision, not buried in the code.
"""
import pandas as pd
from dataclasses import dataclass
from typing import Optional

SQFT_PER_ACRE = 43_560

# The county's own data-dictionary definition of a qualifying Type 2 (parking lot) feature is
# "over 200 ft long, for 20 spaces or more." At a standard ~300 sqft/space planning figure
# (including a pro-rated share of drive aisles -- the same convention used in the companion
# parking-ratio ordinance approach), 20 spaces implies roughly 6,000 sqft. This threshold is used
# to separate likely-genuine qualifying lots from smaller fragments/slivers, but is a planning
# approximation, not a value taken directly from the county's own data.
MIN_QUALIFYING_LOT_SQFT = 6_000

PAVED_SURFACE_CODE = "P"
UNPAVED_SURFACE_CODE = "N"


@dataclass
class ParkingLotTotals:
    """Every filtering choice's resulting total recorded explicitly and
    separately, per this project's standing practice of not collapsing
    genuinely different, real options into one number when a design
    decision (here: which rows to trust) hasn't been made yet."""
    total_rows: int
    unfiltered_sqft: float
    paved_only_sqft: float
    paved_only_rows: int
    min_size_filtered_sqft: float
    min_size_filtered_rows: int
    min_size_and_paved_sqft: float
    min_size_and_paved_rows: int
    largest_single_polygon_sqft: float
    top_38_polygons_sqft: float  # the "500,000+ sqft" cohort found in the real data
    small_fragment_sqft: float  # rows below MIN_QUALIFYING_LOT_SQFT
    small_fragment_rows: int

    def as_acres(self, sqft: float) -> float:
        return sqft / SQFT_PER_ACRE


def _validate_all_type_2(df: pd.DataFrame) -> None:
    """Confirms the loaded data is actually pre-filtered to RD_TYPE=2 as
    the filename claims, rather than assuming it. Separated from
    load_road_casing_type2 so this check is independently testable without
    writing a temp file."""
    unexpected_types = set(df["RD_TYPE"].unique()) - {2}
    if unexpected_types:
        raise ValueError(
            f"Expected all rows to be RD_TYPE=2 (parking lots), but found "
            f"unexpected type codes: {unexpected_types}. Do not silently "
            f"include these -- they are not confirmed to be parking lots."
        )


def load_road_casing_type2(path: str) -> pd.DataFrame:
    """Loads the county's Road Casing Type 2 (parking lot) extract and
    confirms it's actually pre-filtered to RD_TYPE=2 as the filename
    claims, rather than assuming it."""
    df = pd.read_excel(path)
    _validate_all_type_2(df)
    return df


def compute_totals(df: pd.DataFrame, min_qualifying_sqft: float = MIN_QUALIFYING_LOT_SQFT) -> ParkingLotTotals:
    paved = df[df["RD_SURFACE"] == PAVED_SURFACE_CODE]
    above_min = df[df["Shape_Area"] >= min_qualifying_sqft]
    above_min_paved = df[(df["Shape_Area"] >= min_qualifying_sqft) & (df["RD_SURFACE"] == PAVED_SURFACE_CODE)]
    below_min = df[df["Shape_Area"] < min_qualifying_sqft]

    return ParkingLotTotals(
        total_rows=len(df),
        unfiltered_sqft=df["Shape_Area"].sum(),
        paved_only_sqft=paved["Shape_Area"].sum(),
        paved_only_rows=len(paved),
        min_size_filtered_sqft=above_min["Shape_Area"].sum(),
        min_size_filtered_rows=len(above_min),
        min_size_and_paved_sqft=above_min_paved["Shape_Area"].sum(),
        min_size_and_paved_rows=len(above_min_paved),
        largest_single_polygon_sqft=df["Shape_Area"].max(),
        top_38_polygons_sqft=df.nlargest(38, "Shape_Area")["Shape_Area"].sum(),
        small_fragment_sqft=below_min["Shape_Area"].sum(),
        small_fragment_rows=len(below_min),
    )
