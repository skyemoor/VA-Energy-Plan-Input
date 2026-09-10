"""
fairfax_parking_lot_sqft.py

Estimates aggregate parking lot square footage in Fairfax County from the county's own
"Driveways and Parking Lots" GIS dataset (Department of Information Technology GIS Division),
provided directly by the user as
FairfaxCounty_Driveways_and_Parking_Lots_387463314629760591.csv.

UNLIKE Loudoun's Road Casings extract (which mixed roads, driveways, and parking lots together
under one "RD_TYPE" code, requiring a filter step), Fairfax's export is already pre-filtered to
parking lots only -- confirmed directly (see _validate_all_paved_parking_lot below), not assumed:
every one of 23,651 rows has "Type" == "PAVED PARKING LOT". No separate paved/unpaved split is
needed for the same reason -- every row is already paved by definition.

Real, surveyed county geometry -- each polygon has a directly-measured area (Shape__Area, DOUBLE
underscore -- a different field name than Loudoun's single-underscore "Shape_Area", confirmed
directly from the real CSV's own column header via inspection, not assumed to match). Units
confirmed empirically as sq ft (not sq meters): the max polygon (700,289) is ~16.1 acres, plausible
for a large mall's combined parking field; under sq-meters that same value would be ~173 acres for
one polygon, implausible.

Podium/multi-component building issue (found in Fairfax's own Buildings layer) does NOT apply
here: Building Identification Number uniqueness was verified in the Buildings dataset specifically
because that schema explicitly supports stacked, same-ID components (podium buildings). This
parking-lot dataset's OBJECTID and GlobalID were both confirmed unique across all 23,651 rows when
first inspected -- no comparable multi-polygon-per-lot grouping field exists in this schema, and no
evidence of the same pattern was found here.
"""
import pandas as pd
from dataclasses import dataclass

SQFT_PER_ACRE = 43_560

# Same threshold as Loudoun's own MIN_QUALIFYING_LOT_SQFT, per direct user instruction ("use at
# least the amount we filtered for Loudoun") -- not re-derived from Fairfax's own data
# independently.
MIN_QUALIFYING_LOT_SQFT = 6_000

PAVED_PARKING_LOT_TYPE = "PAVED PARKING LOT"


@dataclass
class FairfaxParkingLotTotals:
    """Mirrors loudoun_parking_lot_sqft.py's own ParkingLotTotals shape
    where the concepts genuinely carry over (total/filtered sqft and row
    counts), but does NOT carry Loudoun's paved-only or paved-and-size-
    filtered variants -- those don't apply here, since every row in this
    dataset is already confirmed paved by its own Type field."""
    total_rows: int
    unfiltered_sqft: float
    min_size_filtered_sqft: float
    min_size_filtered_rows: int

    def as_acres(self, sqft: float) -> float:
        return sqft / SQFT_PER_ACRE


def _validate_all_paved_parking_lot(df: pd.DataFrame) -> None:
    """Confirms the loaded data is genuinely all 'PAVED PARKING LOT' as
    directly observed when this dataset was first inspected, rather than
    assuming it still holds on every load."""
    unexpected_types = set(df["Type"].unique()) - {PAVED_PARKING_LOT_TYPE}
    if unexpected_types:
        raise ValueError(
            f"Expected all rows to be '{PAVED_PARKING_LOT_TYPE}', but found unexpected "
            f"Type values: {unexpected_types}. Do not silently include these -- they are "
            f"not confirmed to be parking lots."
        )


def load_fairfax_parking_lots(path: str) -> pd.DataFrame:
    """Loads Fairfax's Driveways and Parking Lots extract and confirms it
    is genuinely all 'PAVED PARKING LOT' as observed, rather than
    assuming it still holds."""
    df = pd.read_csv(path)
    _validate_all_paved_parking_lot(df)
    return df


def compute_totals(df: pd.DataFrame, min_qualifying_sqft: float = MIN_QUALIFYING_LOT_SQFT) -> FairfaxParkingLotTotals:
    above_min = df[df["Shape__Area"] >= min_qualifying_sqft]
    return FairfaxParkingLotTotals(
        total_rows=len(df),
        unfiltered_sqft=df["Shape__Area"].sum(),
        min_size_filtered_sqft=above_min["Shape__Area"].sum(),
        min_size_filtered_rows=len(above_min),
    )
