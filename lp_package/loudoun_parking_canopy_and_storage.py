"""
loudoun_parking_canopy_and_storage.py

Sizes solar canopy MW/MWh and battery storage space over a county's filtered parking-lot
population. Structured for reuse across multiple counties: CountyParkingData is the only class
tied to a specific data source/format (Loudoun's Road Casing GIS extract, via the classmethod
below); SolarCanopyDesign, BatteryStorageDesign, and ParkingCanopyAssessment are county-agnostic
and take a CountyParkingData instance as input, so a second county needs only its own
CountyParkingData-producing classmethod, not changes to the engineering classes themselves.

KEY CONCEPTUAL POINT, per direct user correction: the solar canopy structure spans the full
parking-lot footprint regardless of what sits underneath any given section of it -- a battery
enclosure occupies the same footprint under the canopy a parked car would, so it does not reduce
canopy MW/MWh generation. Battery footprint is therefore NEVER subtracted from the solar
calculation. The only real consequence of siting batteries under the canopy is fewer available
vehicle parking SPACES -- an operational/owner-facing concern, reported separately, not an input
to the energy analysis. This is enforced structurally: SolarCanopyDesign.compute_mw takes only
parking_sqft, with no storage-related parameter that could accidentally net out battery area.

PARAMETER SOURCING (direct user decisions this round):
- Solar canopy density: 2.0-2.5 kW/space (SurgePV's own real-layout worked example: "a 100-space
  lot in a double-row W-frame layout typically supports 200-250 kW DC" -- see
  SolarCanopyDesign's own docstring for the full citation and why this exceeds the simpler,
  more conservative "800 W/space" planning-estimate figure that source also gives).
- Battery duration: 4 hours BY DEFAULT, kept as an overridable dataclass field rather than a
  module constant specifically because future counties (or future scenarios for this same
  county) may reasonably need a different duration -- matches VA_SLCOE_Model.xlsx row 61's
  "4-Hour Storage" PJM BRA capacity-market class benchmark, but is not hardcoded to it.
- Battery footprint: lower end of both ranges researched, per direct user instruction ("go with
  the lower sqft per MWh due to advances in recent years for both metrics") -- 600 sqft/MWh for
  the total developed site footprint (the figure used for sizing; already includes IFC setbacks,
  foundations, access, and PCS/inverters, so no separate setback calculation is layered on top,
  to avoid double-counting), and 25 sqft/MWh for the pure equipment footprint (a reference figure
  only, showing how compact the bare hardware is -- not used in any sizing calculation).
"""
from dataclasses import dataclass
from typing import Tuple
import sys

from loudoun_parking_lot_sqft import compute_totals, load_road_casing_type2

sys.path.insert(0, "/home/claude/work/lp_package/fairfax_parking_lot_solar")
import fairfax_parking_lot_sqft as _fairfax_parking_lot_sqft  # noqa: E402

sys.path.insert(0, "/home/claude/work/lp_package/arlington_parking_lot_solar")
import arlington_parking_lot_sqft as _arlington_parking_lot_sqft  # noqa: E402


@dataclass
class CountyParkingData:
    """The one class tied to a specific county/data source. A second
    county needs its own classmethod like from_road_casing_extract below,
    producing this same CountyParkingData shape -- the engineering classes
    that consume it (SolarCanopyDesign, BatteryStorageDesign,
    ParkingCanopyAssessment) never need to change."""
    county_name: str
    filtered_parking_sqft: float
    source_description: str

    @classmethod
    def from_road_casing_extract(cls, path: str, county_name: str,
                                  min_qualifying_sqft: float = 6_000) -> "CountyParkingData":
        """Loudoun-specific: wraps the existing, already-tested
        load_road_casing_type2()/compute_totals() from
        loudoun_parking_lot_sqft.py rather than duplicating that logic.
        Uses the size-filtered-only total (>=6,000 sqft, NOT the paved-only
        or unfiltered variants) -- the 'filtered sites' choice made
        earlier in this project's work, after direct inspection found
        unpaved lots skew larger/more commercial-looking than paved ones,
        making a paved-only filter likely to undercount real parking area
        rather than safely exclude noise."""
        df = load_road_casing_type2(path)
        totals = compute_totals(df, min_qualifying_sqft=min_qualifying_sqft)
        return cls(
            county_name=county_name,
            filtered_parking_sqft=totals.min_size_filtered_sqft,
            source_description=(
                f"{path}, RD_TYPE=2 (parking lots), filtered to >= "
                f"{min_qualifying_sqft:,.0f} sqft (n={totals.min_size_filtered_rows})"
            ),
        )


    @classmethod
    def from_fairfax_parking_extract(cls, path: str, county_name: str = "Fairfax",
                                      min_qualifying_sqft: float = 6_000) -> "CountyParkingData":
        """Fairfax-specific: wraps the already-tested
        load_fairfax_parking_lots()/compute_totals() from
        fairfax_parking_lot_sqft.py rather than duplicating that logic --
        exactly the extension this class's own docstring anticipated
        ("a second county needs only its own CountyParkingData-producing
        classmethod, not changes to the engineering classes themselves").
        Unlike Loudoun's extract (which mixed roads/driveways/parking
        lots under one RD_TYPE code, requiring a type filter), Fairfax's
        own export is already pre-filtered to parking lots only, so this
        classmethod only needs the size threshold -- no separate type or
        paved-surface filter."""
        df = _fairfax_parking_lot_sqft.load_fairfax_parking_lots(path)
        totals = _fairfax_parking_lot_sqft.compute_totals(df, min_qualifying_sqft=min_qualifying_sqft)
        return cls(
            county_name=county_name,
            filtered_parking_sqft=totals.min_size_filtered_sqft,
            source_description=(
                f"{path}, Type='PAVED PARKING LOT' (already pre-filtered at source), "
                f"filtered to >= {min_qualifying_sqft:,.0f} sqft (n={totals.min_size_filtered_rows})"
            ),
        )


    @classmethod
    def from_arlington_parking_extract(cls, path: str, county_name: str = "Arlington",
                                        min_qualifying_sqft: float = 6_000) -> "CountyParkingData":
        """Arlington-specific: wraps the already-tested
        load_arlington_parking_lots()/compute_totals() from
        arlington_parking_lot_sqft.py rather than duplicating that logic
        -- the third county to use this class's own anticipated extension
        pattern. Arlington's own export has no type/category field at all
        (unlike both Loudoun's RD_TYPE and Fairfax's Type), so this
        classmethod, like Fairfax's, only needs the size threshold."""
        df = _arlington_parking_lot_sqft.load_arlington_parking_lots(path)
        totals = _arlington_parking_lot_sqft.compute_totals(df, min_qualifying_sqft=min_qualifying_sqft)
        return cls(
            county_name=county_name,
            filtered_parking_sqft=totals.min_size_filtered_sqft,
            source_description=(
                f"{path}, Arlington's own 'Pave Parking Lot Polygons' layer (no type field; "
                f"trusted by the dataset's own name), filtered to >= {min_qualifying_sqft:,.0f} "
                f"sqft (n={totals.min_size_filtered_rows})"
            ),
        )


@dataclass
class SolarCanopyDesign:
    """County-agnostic canopy sizing parameters. All fields are instance-
    level with defaults, not module constants, so a different county or
    scenario can override them without subclassing or editing this file.

    Density sourcing: SurgePV, 'Solar Carport Design Guide 2026'
    (surgepv.com/blog/solar-carport-design-guide). That source gives TWO
    figures: a conservative planning estimate ('1 parking space ~= 800 W
    DC') and a real-layout worked example ('a 100-space lot in a
    double-row W-frame layout typically supports 200-250 kW DC... the 800
    W figure is a planning estimate; the actual layout is always denser,'
    since continuous panel rows spanning multiple stalls are more
    space-efficient than one discrete panel pair per stall). Per direct
    user decision, this module uses only the real-layout figure
    (2.0-2.5 kW/space, the 200-250 kW / 100 spaces range) -- the more
    conservative 800 W/space figure is not carried in this version.
    """
    kw_per_space_low: float = 2.0
    kw_per_space_high: float = 2.5
    # Sqft per parking space INCLUDING a pro-rated share of drive-aisle/
    # circulation area -- reused from loudoun_parking_lot_sqft.py's
    # MIN_QUALIFYING_LOT_SQFT basis (20 spaces x ~300 sqft/space = ~6,000
    # sqft, the county's own implied "20+ space" qualifying threshold),
    # rather than introducing a second, inconsistent figure in this project.
    sqft_per_space: float = 300

    def compute_mw(self, parking_sqft: float) -> Tuple[float, float]:
        """Returns (mw_low, mw_high). Takes ONLY parking_sqft -- no
        storage-related parameter -- so battery siting can never
        accidentally net out of this calculation. See module docstring's
        'KEY CONCEPTUAL POINT.'"""
        implied_spaces = parking_sqft / self.sqft_per_space
        mw_low = implied_spaces * self.kw_per_space_low / 1_000
        mw_high = implied_spaces * self.kw_per_space_high / 1_000
        return mw_low, mw_high


@dataclass
class BatteryStorageDesign:
    """County-agnostic battery sizing parameters, all overridable
    per-instance. duration_hours is deliberately a dataclass field with a
    default (4.0), not a module constant -- per direct user correction --
    since a future county or scenario may need a different duration
    without editing this class.

    Footprint sourcing: two genuinely different metrics researched and
    refined by the user beyond the module's earlier draft --
    'pure equipment footprint' (bare container dimensions, no clearance:
    ~25-160 sqft/MWh, driven by rapidly-improving container energy
    density) vs. 'total developed site footprint' (~600-1,000 sqft/MWh,
    already including IFC-mandated setbacks, foundations, access, and
    PCS/inverters). Per direct user instruction ("go with the lower sqft
    per MWh... for both metrics"), this module uses the lower end of each
    range: 600 sqft/MWh for sizing, 25 sqft/MWh carried only as a
    reference figure. No separate setback calculation is layered on top
    of the 600 sqft/MWh figure, since IFC setbacks are already included in
    it -- doing so would double-count.
    """
    duration_hours: float = 4.0
    sqft_per_mwh: float = 600  # total developed site footprint -- used for sizing
    equipment_only_sqft_per_mwh: float = 25  # reference only, not used in sizing

    def compute_storage(self, solar_mw: float, sqft_per_space: float) -> "StorageResult":
        """Sizes storage at a 1:1 MW pairing with the given solar MW (the
        'firmed solar' convention, per direct user confirmation), for
        self.duration_hours. sqft_per_space is passed in explicitly
        (rather than duplicated as a field on this class) so this class
        doesn't need to know about SolarCanopyDesign directly -- the
        caller (ParkingCanopyAssessment) wires the two together, keeping
        both design classes independently reusable. Returns spaces
        displaced as a clearly-separate, owner-facing figure -- NEVER
        subtracted from any solar MW/MWh number."""
        mwh = solar_mw * self.duration_hours
        footprint_sqft = mwh * self.sqft_per_mwh
        equipment_only_sqft = mwh * self.equipment_only_sqft_per_mwh
        spaces_displaced = footprint_sqft / sqft_per_space
        return StorageResult(
            solar_mw=solar_mw,
            duration_hours=self.duration_hours,
            mwh=mwh,
            footprint_sqft=footprint_sqft,
            equipment_only_sqft=equipment_only_sqft,
            spaces_displaced=spaces_displaced,
        )


@dataclass
class StorageResult:
    solar_mw: float
    duration_hours: float
    mwh: float
    footprint_sqft: float
    equipment_only_sqft: float
    spaces_displaced: float


@dataclass
class ParkingCanopyAssessmentResult:
    county_name: str
    parking_sqft: float
    mw_low: float
    mw_high: float
    storage_low: StorageResult   # paired with mw_low
    storage_high: StorageResult  # paired with mw_high


@dataclass
class ParkingCanopyAssessment:
    """Orchestrates a full county assessment: wires a CountyParkingData's
    sqft total through a SolarCanopyDesign (for MW) and a
    BatteryStorageDesign (for storage MWh/footprint), producing both the
    low and high solar-density scenarios end to end. Neither design class
    is required to know about the other -- this class does the wiring."""
    county_data: CountyParkingData
    solar_design: SolarCanopyDesign = None
    storage_design: BatteryStorageDesign = None

    def __post_init__(self):
        if self.solar_design is None:
            self.solar_design = SolarCanopyDesign()
        if self.storage_design is None:
            self.storage_design = BatteryStorageDesign()

    def run(self) -> ParkingCanopyAssessmentResult:
        mw_low, mw_high = self.solar_design.compute_mw(self.county_data.filtered_parking_sqft)
        storage_low = self.storage_design.compute_storage(mw_low, self.solar_design.sqft_per_space)
        storage_high = self.storage_design.compute_storage(mw_high, self.solar_design.sqft_per_space)
        return ParkingCanopyAssessmentResult(
            county_name=self.county_data.county_name,
            parking_sqft=self.county_data.filtered_parking_sqft,
            mw_low=mw_low,
            mw_high=mw_high,
            storage_low=storage_low,
            storage_high=storage_high,
        )
