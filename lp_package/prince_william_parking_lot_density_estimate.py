"""
prince_william_parking_lot_density_estimate.py

Estimates Prince William County's qualifying parking-lot square footage via a per-capita density
extrapolation from Loudoun's and Fairfax's own real, GIS-verified figures -- used only because
direct Prince William County GIS extraction (the TYPE_CODE field) returned zero results despite
repeated attempts. NOT real data -- an explicitly-labeled estimate, to be replaced the moment real
Prince William parking-lot GIS data becomes available.

METHOD CHOSEN PER DIRECT USER DECISION: Loudoun-anchored per-capita density, not the per-land-area
method or a Fairfax anchor. Rationale given directly: Prince William is more distant from DC than
Fairfax, implying less structured/garage parking (which DC-proximity land values push developers
toward) and more surface-lot parking -- similar to Loudoun's own development pattern rather than
Fairfax's more urbanized one. This is a real, substantive difference in the two source counties'
own per-capita densities (Loudoun 0.011877 acres/capita vs. Fairfax's 0.001112 acres/capita, a
10.7x gap) -- not a minor rounding difference, so which anchor is chosen materially changes the
result. The Fairfax-anchored figure is retained as an explicit sensitivity check, not blended in,
consistent with how every other genuine range in this project has been handled (mean/median,
low/high canopy density, etc.).

Populations used (2025 estimates, both verified directly against Census/Wikipedia sourcing in
chat): Loudoun 449,749; Fairfax 1,167,873; Prince William 502,966.

Run tests with: python3 -m pytest test_prince_william_parking_lot_density_estimate.py -v
"""
import sys
from dataclasses import dataclass

sys.path.insert(0, "/home/claude/work/lp_package/loudoun_ci_rooftop_solar")
sys.path.insert(0, "/home/claude/work/lp_package/loudoun_parking_lot_solar")
from loudoun_ci_rooftop_solar_estimate import HOURS_PER_YEAR, NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR  # noqa: E402
from loudoun_parking_canopy_and_storage import CountyParkingData, ParkingCanopyAssessment  # noqa: E402

SQFT_PER_ACRE = 43_560

# Real, established source-county figures (both cross-checked directly against their own real GIS
# extracts elsewhere in this project -- not re-derived here)
LOUDOUN_QUALIFYING_PARKING_ACRES = 5_341.6
LOUDOUN_POPULATION_2025 = 449_749
FAIRFAX_QUALIFYING_PARKING_ACRES = 1_298.2
FAIRFAX_POPULATION_2025 = 1_167_873

PRINCE_WILLIAM_POPULATION_2025 = 502_966


def compute_per_capita_density(qualifying_acres: float, population: float) -> float:
    """Acres of qualifying parking per capita -- the shared computation
    underlying both the Loudoun-anchored and Fairfax-anchored estimates
    below."""
    return qualifying_acres / population


def estimate_prince_william_parking_acres(
    anchor_acres_per_capita: float, prince_william_population: float = PRINCE_WILLIAM_POPULATION_2025
) -> float:
    return anchor_acres_per_capita * prince_william_population


def build_estimated_county_parking_data(estimated_acres: float, anchor_label: str) -> CountyParkingData:
    """Constructs a CountyParkingData object directly (not via a
    from_..._extract() classmethod, since there is no real file to load
    for this estimate) -- reusing the existing, already-tested
    engineering classes (SolarCanopyDesign/BatteryStorageDesign/
    ParkingCanopyAssessment) unchanged, the same way every real county's
    own classmethod does."""
    return CountyParkingData(
        county_name=f"Prince William (ESTIMATED -- {anchor_label} per-capita anchor)",
        filtered_parking_sqft=estimated_acres * SQFT_PER_ACRE,
        source_description=(
            f"NOT real GIS data. Estimated via {anchor_label}'s own real per-capita parking "
            f"density x Prince William's 2025 population estimate ({PRINCE_WILLIAM_POPULATION_2025:,}), "
            f"since direct Prince William County GIS extraction (TYPE_CODE field) returned zero "
            f"results. Rationale for the {anchor_label} anchor choice: Prince William's greater "
            f"distance from DC vs. Fairfax implies less structured/garage parking and more "
            f"surface-lot parking, more similar to Loudoun's own development pattern."
        ),
    )


@dataclass
class PrinceWilliamParkingEstimate:
    anchor_label: str
    estimated_acres: float
    mw_low: float
    mw_high: float
    storage_mwh_low: float
    storage_mwh_high: float
    annual_mwh_low: float
    annual_mwh_high: float


def run_prince_william_parking_estimate(
    anchor_acres_per_capita: float, anchor_label: str,
    capacity_factor: float = NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR,
) -> PrinceWilliamParkingEstimate:
    """Full pipeline: per-capita density -> estimated acres -> the same,
    unchanged ParkingCanopyAssessment engineering already used for
    Loudoun/Fairfax/Arlington's own real data -> annual MWh via the
    same, already-established 20% capacity factor."""
    estimated_acres = estimate_prince_william_parking_acres(anchor_acres_per_capita)
    county_data = build_estimated_county_parking_data(estimated_acres, anchor_label)
    result = ParkingCanopyAssessment(county_data=county_data).run()

    annual_mwh_low = result.mw_low * HOURS_PER_YEAR * capacity_factor
    annual_mwh_high = result.mw_high * HOURS_PER_YEAR * capacity_factor

    return PrinceWilliamParkingEstimate(
        anchor_label=anchor_label,
        estimated_acres=estimated_acres,
        mw_low=result.mw_low, mw_high=result.mw_high,
        storage_mwh_low=result.storage_low.mwh, storage_mwh_high=result.storage_high.mwh,
        annual_mwh_low=annual_mwh_low, annual_mwh_high=annual_mwh_high,
    )
