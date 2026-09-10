"""
arlington_parking_lot_sqft.py

Estimates aggregate parking lot square footage in Arlington County from the county's own "Pave
Parking Lot Polygons" GIS dataset (Arlington County GIS Mapping Center / Department of
Environmental Services), provided directly by the user as Arlington_Pave_Parking_Lot_Polygons.csv.

UNLIKE Loudoun's Road Casings extract (RD_TYPE mixing roads/driveways/parking lots) and even
Fairfax's Driveways and Parking Lots extract (a "Type" field, uniformly "PAVED PARKING LOT" but
present), this dataset has NO type/category field at all -- confirmed directly by inspection, not
assumed. The dataset's own name ("Pave Parking Lot Polygons," Arlington's own authoritative layer
name, not a generic export label) is trusted as the basis for treating every row as a genuine
parking lot, since there is no competing field to validate against the way there was for the other
two counties.

Real, surveyed county geometry -- each polygon has a directly-measured area (SHAPE_Area, single
underscore, matching Arlington's own Building Height Polygons convention and Loudoun's
Shape_Area -- NOT Fairfax's double-underscore Shape__Area, confirmed directly from the real CSV's
own column header, not assumed to match either prior convention). Units confirmed empirically as
sq ft: the max polygon (1,044,828.7) is ~24.0 acres, plausible for a large parking structure/lot;
under sq-meters that same value would be ~258 acres for one polygon, implausible.

ONE HONEST, UNRESOLVED LIMITATION: GeoSyncDate is a single, uniform timestamp across all 2,783
rows (the same date, to the second, for every record) -- this looks like an extraction/sync
timestamp (when this particular CSV export was generated), not a per-row survey/update vintage the
way Fairfax's Source field was (which gave genuine per-record imagery-vintage information). There
is no reliable way to assess this dataset's actual underlying data-collection age from the fields
provided -- flagged here explicitly, not silently assumed to be either current or stale.

SNOW_OWNER/SNOW_PRIORITY are present but NOT used for filtering: these describe which county
department (or "UNK" for unknown/non-county, 92.7% of rows) is responsible for snow removal at
each lot -- operational metadata about winter maintenance responsibility, not a genuine parking-lot
type/validity classification. A lot being "UNK"-owned for snow purposes does not mean it is not a
real parking lot.
"""
import pandas as pd
from dataclasses import dataclass

SQFT_PER_ACRE = 43_560

# Same threshold as Loudoun's and Fairfax's own, per direct user instruction ("use at least the
# amount we filtered for Loudoun") -- not re-derived from Arlington's own data independently.
MIN_QUALIFYING_LOT_SQFT = 6_000


@dataclass
class ArlingtonParkingLotTotals:
    """Mirrors loudoun_parking_lot_sqft.py's and fairfax_parking_lot_sqft.py's
    own totals shape where the concepts genuinely carry over (total/
    filtered sqft and row counts) -- no paved-only variant here either,
    for the same reason as Fairfax: there's no type field to split on,
    and the dataset's own name already asserts every row is a paved
    parking lot."""
    total_rows: int
    unfiltered_sqft: float
    min_size_filtered_sqft: float
    min_size_filtered_rows: int

    def as_acres(self, sqft: float) -> float:
        return sqft / SQFT_PER_ACRE


def _validate_expected_columns(df: pd.DataFrame) -> None:
    """No type/category field exists in this dataset to validate rows
    against (unlike Loudoun's RD_TYPE or Fairfax's Type) -- confirmed
    directly by inspection, not an oversight. The check available here is
    structural: confirm the columns this loader depends on actually
    exist, rather than silently producing wrong numbers from a KeyError
    somewhere downstream if the schema ever changes."""
    required = {"OBJECTID", "SHAPE_Area"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"Expected columns {required} in Arlington parking lot extract, but missing: "
            f"{missing}. Do not silently proceed with a different schema than expected."
        )


def load_arlington_parking_lots(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    _validate_expected_columns(df)
    return df


def compute_totals(df: pd.DataFrame, min_qualifying_sqft: float = MIN_QUALIFYING_LOT_SQFT) -> ArlingtonParkingLotTotals:
    above_min = df[df["SHAPE_Area"] >= min_qualifying_sqft]
    return ArlingtonParkingLotTotals(
        total_rows=len(df),
        unfiltered_sqft=df["SHAPE_Area"].sum(),
        min_size_filtered_sqft=above_min["SHAPE_Area"].sum(),
        min_size_filtered_rows=len(above_min),
    )
