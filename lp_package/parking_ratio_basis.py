"""
parking_ratio_basis.py

Parking-lot area estimated from C&I building footprint, typed by development pattern.

Replaces the per-capita approach in `population_extrapolation.py`, which is unsound — see that
module's own caution and `docs/methodology/Parking_Reference_Basis_Working_Notes.md`.

WHY C&I FOOTPRINT RATHER THAN POPULATION OR LAND AREA

Parking scales with commercial floorspace. It does not scale with residents: Richmond City and
Loudoun have nearly identical parking per resident (0.01203 against 0.01188 acres) despite being
opposite kinds of place, because a jurisdiction's commercial parking serves its economic catchment
rather than the people who sleep there. It does not scale with land area either: that conflates
undeveloped acreage, development intensity, and structured-versus-surface parking, which is the
comparison that wrongly condemned Fairfax's dataset as coverage-limited.

Footprint-to-footprint is physically causal, and it discriminates structured from surface parking —
the distinction that actually matters for canopy solar, since a multi-level deck yields only its
top level.

READ THIS BEFORE USING THE OUTPUT: THE BASIS IS TWO ANCHORS, ONE PER TYPE

Of six jurisdictions with any measurement, only TWO have BOTH a C&I footprint and a parking area:

    Fairfax     19,493,424 sqft C&I : 77,426,918 sqft parking = 3.97
    Arlington   55,038,330 sqft C&I : 47,300,701 sqft parking = 0.86

The others are blocked for structural reasons, not for want of effort:

    Loudoun         has parking; C&I source is business-licence records with NO area field
    Richmond City   has parking; its Structures layer carries NO building-use field
    Chesapeake      has C&I; publishes no parking layer at all
    Prince William  has C&I; publishes no parking layer at all

So each development type has exactly ONE anchor. There is no within-type variance to estimate from,
and the two anchors differ by 4.6x. This module therefore does NOT produce a confidence interval —
producing one would imply a sample that does not exist. It produces a point estimate per type with
the anchor named, and `basis_warning()` returns a statement that must accompany any figure derived
from it.

**Recommendation for the whitepaper: report measured jurisdictions and state that Virginia's GIS
coverage does not support statewide parking extrapolation.** Of eight jurisdictions checked, four
publish parking geometry and no suburban county outside Northern Virginia does. That is a property
of the data landscape, not of the search. A defensible "here is what four jurisdictions have, and
the data does not permit more" is stronger before a regulator than a wide extrapolated range that
invites exactly the challenge it cannot survive.

This module exists so that estimate CAN be produced where one is genuinely needed, with its
limitations attached, rather than being produced ad hoc without them.

NO SITE SURVEY WAS PERFORMED. Every figure here is an upper bound on the physical resource, not
deliverable capacity. Canopy output carries no shading deduction, while parking-lot tree canopy is
common and frequently mandated by local ordinance.
"""
from dataclasses import dataclass
from typing import Optional

SQFT_PER_ACRE = 43_560

#: Development patterns that produce materially different parking-to-floorspace ratios. Named for
#: the physical mechanism rather than for a political category: Chesapeake is legally an
#: independent city and functionally a surface-parked suburb; Stafford is legally a county and
#: functionally the same. The city/county distinction does not predict parking; development pattern
#: does.
SURFACE_PARKED = 'surface_parked'
STRUCTURED = 'structured'


@dataclass(frozen=True)
class ParkingRatioAnchor:
    """A jurisdiction with BOTH a measured C&I building footprint and a measured parking area.

    Only two exist. Each is the sole anchor for its development type.
    """
    name: str
    development_type: str
    ci_footprint_sqft: float
    parking_sqft: float
    parking_source: str
    ci_source: str

    @property
    def ratio(self) -> float:
        return self.parking_sqft / self.ci_footprint_sqft


#: Both anchors use UNFILTERED parking area. For Fairfax that is required, not optional: it
#: fragments lots (median paved polygon 308 sqft, one parking space), so a minimum-size threshold
#: discards real parking rather than excluding noise. Arlington is reported unfiltered for
#: consistency with it.
ANCHORS = {
    SURFACE_PARKED: ParkingRatioAnchor(
        name='Fairfax County',
        development_type=SURFACE_PARKED,
        ci_footprint_sqft=19_493_424.0,
        parking_sqft=77_426_918.0,
        parking_source=('GIS_MINOR_TRANSPORTATION_AREAS, PAVED PARKING LOT (23,651) plus '
                        'UNPAVED PARKING LOT (851), unfiltered'),
        ci_source='Fairfax Buildings GIS layer, 4,510 C&I buildings >=600 sqft'),
    STRUCTURED: ParkingRatioAnchor(
        name='Arlington County',
        development_type=STRUCTURED,
        ci_footprint_sqft=55_038_330.0,
        parking_sqft=47_300_701.0,
        parking_source='Pave Parking Lot Polygons, unfiltered',
        ci_source='Arlington Buildings GIS layer, CM_Type C&I classification'),
}


def basis_warning() -> str:
    """The statement that must accompany any figure derived from this module.

    Returned as a value rather than left in documentation so a caller producing a table or report
    can attach it programmatically and cannot omit it by forgetting.
    """
    return (
        'Estimated from a single anchor per development type: Fairfax County (ratio 3.97) for '
        'surface-parked jurisdictions and Arlington County (ratio 0.86) for structured ones. '
        'These are the only two Virginia jurisdictions with both a measured C&I building '
        'footprint and a measured parking area. With one anchor per type there is no within-type '
        'variance, so no confidence interval is offered and none should be inferred. The two '
        'anchors differ by 4.6x, so classification of a jurisdiction into the wrong type is the '
        'dominant source of error. No site survey was performed; figures are upper bounds on the '
        'physical resource, with no shading deduction.')


def ratio_for_type(development_type: str) -> float:
    if development_type not in ANCHORS:
        raise ValueError(
            f"unknown development type {development_type!r}; expected one of "
            f"{sorted(ANCHORS)}. There is no default -- the two ratios differ by 4.6x, so "
            f"guessing a type would dominate the error in any figure produced.")
    return ANCHORS[development_type].ratio


@dataclass(frozen=True)
class ParkingEstimate:
    jurisdiction: str
    development_type: str
    anchor_used: str
    ci_footprint_sqft: float
    ratio_applied: float
    estimated_parking_sqft: float
    estimated_parking_acres: float
    warning: str
    is_measured: bool


def estimate_parking_from_ci(jurisdiction: str, ci_footprint_sqft: float,
                             development_type: str) -> ParkingEstimate:
    """Estimates parking area from a MEASURED C&I footprint. Requires an explicit development type
    -- see ratio_for_type() for why there is no default."""
    if ci_footprint_sqft is None or ci_footprint_sqft <= 0:
        raise ValueError(
            f"ci_footprint_sqft must be positive, got {ci_footprint_sqft!r}. This method estimates "
            "parking FROM a measured commercial footprint; it cannot estimate both.")
    ratio = ratio_for_type(development_type)
    sqft = ci_footprint_sqft * ratio
    return ParkingEstimate(
        jurisdiction=jurisdiction, development_type=development_type,
        anchor_used=ANCHORS[development_type].name,
        ci_footprint_sqft=ci_footprint_sqft, ratio_applied=ratio,
        estimated_parking_sqft=sqft, estimated_parking_acres=sqft / SQFT_PER_ACRE,
        warning=basis_warning(), is_measured=False)


def measured(jurisdiction: str, parking_sqft: float,
             ci_footprint_sqft: Optional[float] = None,
             development_type: Optional[str] = None) -> ParkingEstimate:
    """Wraps a jurisdiction's own MEASURED parking area in the same result shape.

    Exists so a report can mix measured and estimated jurisdictions without the distinction
    getting lost in a table -- `is_measured` is the field that keeps them separable, and Rule 5
    favours making that explicit over letting a reader assume.
    """
    return ParkingEstimate(
        jurisdiction=jurisdiction, development_type=development_type or 'measured',
        anchor_used='none -- measured directly',
        ci_footprint_sqft=ci_footprint_sqft or 0.0,
        ratio_applied=(parking_sqft / ci_footprint_sqft) if ci_footprint_sqft else 0.0,
        estimated_parking_sqft=parking_sqft,
        estimated_parking_acres=parking_sqft / SQFT_PER_ACRE,
        warning='Measured directly from published GIS geometry; no extrapolation applied. '
                'No site survey was performed, so this remains an upper bound on the physical '
                'resource with no shading deduction.',
        is_measured=True)
