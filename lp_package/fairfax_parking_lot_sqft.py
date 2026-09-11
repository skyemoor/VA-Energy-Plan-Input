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

CORRECTED 2026-09-11 -- TWO ERRORS, BOTH MATERIAL. See
docs/methodology/Parking_Reference_Basis_Working_Notes.md for the full account.

ERROR 1: THE EXTRACT WAS MISSING UNPAVED PARKING LOTS. Fairfax's parent feature class
(GIS_MINOR_TRANSPORTATION_AREAS) carries eight coded values, TWO of which are parking:
PAVED PARKING LOT and UNPAVED PARKING LOT. The original extract contained only the first. The
other six -- private roads, driveways and shared drives -- are correctly excluded.

Unpaved adds 851 polygons and 100 acres, 6.0% of the paved total. Smaller than Loudoun's 14.8%,
which is consistent: Loudoun's unpaved lots are engineered permeable-pavement facilities at rural
commercial sites, a pattern with less scope in Fairfax. But the DIRECTION holds -- unpaved lots
here are again substantially LARGER than paved (median 1,759 against 308 sqft), confirming they
are real facilities rather than informal gravel, exactly as Loudoun's own inspection found.

ERROR 2: THE 6,000 SQFT THRESHOLD DOES NOT TRANSFER TO THIS DATASET. It was adopted on the direct
instruction "use at least the amount we filtered for Loudoun", and Loudoun's own module derived it
from that county's data-dictionary definition of a qualifying Type 2 feature ("over 200 ft long,
for 20 spaces or more", ~300 sqft/space including aisles).

Fairfax's median PAVED PARKING LOT polygon is 308 sqft -- one parking space. These are FRAGMENTS:
pieces of real lots split by islands, aisles, or repaving dates. Loudoun's module anticipated
exactly this ("many real parking lots are digitized as multiple adjacent polygon fragments...
rather than one polygon per physical lot"), but the consequence was not carried across. Fragments
sum to real lot area, so filtering them out discards genuine parking rather than excluding noise.

The correct Fairfax figure is the UNFILTERED total across both parking types:

    paved     23,651 polygons   1,677 acres
    unpaved      851 polygons     100 acres
    TOTAL     24,502 polygons   1,777 acres      (against 1,298 previously reported)

compute_totals() still returns the size-filtered variants, since a caller may legitimately want
them and Rule 8 favours exposing the choice over burying it -- but min_size_filtered_sqft is NOT
the right figure for this county, and total_parking_sqft() below is.

NO SITE SURVEY WAS PERFORMED. The canopy figures derived from this county's parking area assume
unobstructed solar access, with no shading deduction. Mature tree canopy in parking lots is common
and frequently mandated -- many Virginia jurisdictions impose parking-lot canopy requirements to
reduce heat island effect -- and a lot meeting a 10% canopy standard carries real generation loss
at exactly the perimeter and island locations where trees are placed. These figures are upper
bounds on the physical resource, not deliverable capacity.

WHY THE EARLIER "FAIRFAX IS COVERAGE-LIMITED" DIAGNOSIS WAS WRONG. Fairfax was briefly judged
unusable because it reported 0.65% of land area as parking against Richmond's 7.82% and
Arlington's 6.08%. Land area turned out to be the wrong normalizer: it conflates undeveloped land,
development intensity, and structured-versus-surface parking into one number, and those vary
enormously between Loudoun's farmland, Fairfax's suburbs and Arlington's urban core.

Normalized against C&I BUILDING FOOTPRINT -- the thing parking actually scales with -- Fairfax
looks entirely normal and Arlington is the outlier:

    Fairfax    19.5M sqft C&I : 73.1M sqft parking = 3.75x   surface-parked suburb
    Arlington  55.0M sqft C&I : 44.1M sqft parking = 0.80x   structured, transit-served

3.75x is the expected range for surface-parked suburban development. 0.80x is the signature of a
jurisdiction that parks vertically -- Rosslyn-Ballston and Crystal City. Fairfax's data is sound;
the comparison that condemned it was not.
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


UNPAVED_PARKING_LOT_TYPE = "UNPAVED PARKING LOT"


def load_fairfax_unpaved_parking_lots(path: str) -> pd.DataFrame:
    """Loads the UNPAVED PARKING LOT extract, confirming its Type as the paved loader does.

    A separate loader rather than a parameter on the existing one: these arrive as two distinct
    exports from Fairfax's portal, and keeping them separate makes it visible when one is missing
    -- which is how the original omission went unnoticed.
    """
    df = pd.read_csv(path)
    unexpected = set(df["Type"].unique()) - {UNPAVED_PARKING_LOT_TYPE}
    if unexpected:
        raise ValueError(
            f"Expected all rows to be '{UNPAVED_PARKING_LOT_TYPE}', found: {unexpected}. "
            f"Do not silently include these.")
    return df


def total_parking_sqft(paved_df: pd.DataFrame, unpaved_df: pd.DataFrame = None) -> dict:
    """The figure this county should be cited on: UNFILTERED area across both parking types.

    No size threshold, deliberately -- Fairfax fragments its lots (median paved polygon 308 sqft,
    one parking space), so a minimum-size filter discards real parking area rather than excluding
    noise. See this module's docstring, ERROR 2.

    unpaved_df is optional but its omission is RECORDED in the return value rather than silently
    defaulting to zero, since omitting it is precisely the error this correction fixes.
    """
    paved_sqft = float(paved_df["Shape__Area"].sum())
    unpaved_sqft = float(unpaved_df["Shape__Area"].sum()) if unpaved_df is not None else 0.0
    return {
        "paved_rows": len(paved_df),
        "paved_sqft": paved_sqft,
        "unpaved_rows": len(unpaved_df) if unpaved_df is not None else 0,
        "unpaved_sqft": unpaved_sqft,
        "unpaved_included": unpaved_df is not None,
        "total_sqft": paved_sqft + unpaved_sqft,
        "total_acres": (paved_sqft + unpaved_sqft) / SQFT_PER_ACRE,
        "size_filtered": False,
        "note": ("Unfiltered by design -- Fairfax fragments lots, so a minimum-size threshold "
                 "discards real parking area. See module docstring ERROR 2."),
    }
