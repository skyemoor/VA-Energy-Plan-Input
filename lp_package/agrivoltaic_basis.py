"""
agrivoltaic_basis.py

Agrivoltaic siting share, land-use footprint, and farm lease income for the modeled solar buildout.

BASIS ADOPTED 2026-09-11: **85% of TOTAL solar capacity** is sited in agrivoltaic arrangements
under utility or PPA ownership.

This supersedes, for allocation purposes, the nested formulation in `scenario3_build.py`
(`agrivoltaic_share_of_nonurban = 0.90` applied to an 80% utility share, giving 72% of total). The
two are not contradictory — they answer the same question at different points in the chain — but
85% of total is the figure this analysis now carries, and mixing the two would produce a 13-point
discrepancy in every derived acreage and income figure.

WHY THE SHARE MOVED, AND WHY IT IS STATED RATHER THAN BUILT UP

The earlier 80/10/10 split implied a distributed resource of roughly 20% of total solar. Bottom-up
siting assessment across eight Virginia jurisdictions could not support that: the DOM zone
distributed cap stands at 7,440 MW against a 2045 solar build of ~173,780 MW, i.e. about 4.3%. The
gap is not a modeling artifact — the 2045 solve pins distributed at the cap, and the D3 constraint
had to be relaxed from equality to inequality because as an equality it capped total solar and
forced unserved energy.

Continuing to build the distributed share bottom-up was discontinued on 2026-09-11 (see
`docs/methodology/Parking_Reference_Basis_Working_Notes.md` §14): four of eight jurisdictions
publish parking geometry at all, source vintages span nineteen years which undermines
cross-jurisdiction comparison, and the effort was consuming disproportionate time for diminishing
returns.

So 85% is a **stated allocation assumption**, not a bottom-up result. It is defensible as such —
the residual 15% comfortably accommodates the assessed distributed resource plus non-agrivoltaic
utility-scale siting — but it must be presented as an assumption, and `share_is_assumed()` returns
that statement so a caller cannot omit it by forgetting.

WHAT THE SHARE DOES AND DOES NOT DETERMINE

A real distinction carried over from `docs/appendices/Appendix_Agrivoltaics.md`: **lease income
applies to all utility-scale solar regardless of agrivoltaic status**, because a landowner is paid
for hosting the array either way. What the agrivoltaic share determines is whether the landowner
ADDITIONALLY retains agricultural production on that same land. For the 85%, both; for
conventional utility-scale siting, lease income only, with the land presumed converted.

THE ARGUMENT THAT DOES NOT DEPEND ON YIELD

Crop yield under panels is genuinely contested and varies by crop, and no Virginia-specific field
trial was identified — the evidence base is Delaware's Eastern Shore and other out-of-state work.
The income-stability argument does not rest on yield at all:

    A contracted per-acre lease payment is a hedge against drought, hail and commodity price risk
    that dryland row-crop farming does not have. The revenue is contractually independent of that
    year's harvest outcome, so the argument holds even for crops with weak or negative yield
    evidence.

For an NSPM secondary-benefit case this is the stronger claim, because it is about income VARIANCE
rather than income LEVEL, and variance reduction is what mitigates farm failure. `lease_income()`
therefore reports the lease component separately from any production value.

SOURCED INPUTS (see the appendix for full citations)
  land use, single-axis tracking      4-6 acres/MW
  storage add-on at project targets   0.10-0.24 acres/MW of solar
  firmed solar-plus-storage           4.1-6.2 acres/MW
  Virginia lease rates                $1,200-2,500/acre/year
  national comparison                 $500-700/acre/year
"""
from dataclasses import dataclass

#: 85% of TOTAL solar capacity. A stated allocation assumption -- see module docstring.
AGRIVOLTAIC_SHARE_OF_TOTAL_SOLAR = 0.85

#: Acres per MW, single-axis tracking. Project-established, stable across revisions.
ACRES_PER_MW_LOW = 4.0
ACRES_PER_MW_HIGH = 6.0

#: Storage land-use add-on per MW of solar, at this project's own VCEA-target sodium-ion and
#: iron-air mix. Sodium-ion uses a lithium-ion proxy (no chemistry-specific figure found); iron-air
#: has a primary Form Energy figure of ~0.5 acre/MW at its least dense configuration.
STORAGE_ACRES_PER_MW_SOLAR_LOW = 0.10
STORAGE_ACRES_PER_MW_SOLAR_HIGH = 0.24

#: Virginia lease rates, $/acre/year. Substantially above the $500-700 national average.
VA_LEASE_RATE_LOW = 1_200.0
VA_LEASE_RATE_HIGH = 2_500.0
NATIONAL_LEASE_RATE_LOW = 500.0
NATIONAL_LEASE_RATE_HIGH = 700.0


def share_is_assumed() -> str:
    """The statement that must accompany any figure derived from the 85% share.

    Returned as a value rather than left in documentation so a caller building a table or report
    attaches it programmatically and cannot omit it by forgetting -- the same pattern used for
    parking_ratio_basis.basis_warning().
    """
    return (
        f'The {AGRIVOLTAIC_SHARE_OF_TOTAL_SOLAR:.0%} agrivoltaic share is a STATED ALLOCATION '
        'ASSUMPTION about how future buildout could be sited, not a description of current '
        'practice and not a bottom-up siting result. NREL counts 13 existing agrivoltaic projects '
        'in Virginia, so the present-day share is far below this. Bottom-up assessment of the '
        'distributed alternative was discontinued after eight jurisdictions because only four '
        'publish parking geometry and source vintages span nineteen years. Every acreage and '
        'income figure derived from this share inherits that assumption.')


@dataclass(frozen=True)
class AgrivoltaicFootprint:
    total_solar_mw: float
    agrivoltaic_mw: float
    non_agrivoltaic_mw: float
    solar_acres_low: float
    solar_acres_high: float
    firmed_acres_low: float
    firmed_acres_high: float
    agrivoltaic_acres_low: float
    agrivoltaic_acres_high: float
    assumption: str


def footprint(total_solar_mw: float,
              agrivoltaic_share: float = AGRIVOLTAIC_SHARE_OF_TOTAL_SOLAR) -> AgrivoltaicFootprint:
    """Land footprint for a given solar build, and the agrivoltaic portion of it.

    'Firmed' acreage includes the storage add-on, which is real but modest -- roughly 2.5-4% more
    land than solar alone. Reported separately rather than folded in, because a reader comparing
    against another study's acres/MW figure needs to know whether storage is inside it.
    """
    if total_solar_mw is None or total_solar_mw <= 0:
        raise ValueError(f"total_solar_mw must be positive, got {total_solar_mw!r}")
    if not 0.0 <= agrivoltaic_share <= 1.0:
        raise ValueError(f"agrivoltaic_share must be a fraction in [0,1], got {agrivoltaic_share!r}")

    agri_mw = total_solar_mw * agrivoltaic_share
    firmed_low = ACRES_PER_MW_LOW + STORAGE_ACRES_PER_MW_SOLAR_LOW
    firmed_high = ACRES_PER_MW_HIGH + STORAGE_ACRES_PER_MW_SOLAR_HIGH
    return AgrivoltaicFootprint(
        total_solar_mw=total_solar_mw,
        agrivoltaic_mw=agri_mw,
        non_agrivoltaic_mw=total_solar_mw - agri_mw,
        solar_acres_low=total_solar_mw * ACRES_PER_MW_LOW,
        solar_acres_high=total_solar_mw * ACRES_PER_MW_HIGH,
        firmed_acres_low=total_solar_mw * firmed_low,
        firmed_acres_high=total_solar_mw * firmed_high,
        agrivoltaic_acres_low=agri_mw * firmed_low,
        agrivoltaic_acres_high=agri_mw * firmed_high,
        assumption=share_is_assumed())


@dataclass(frozen=True)
class LeaseIncome:
    acres_low: float
    acres_high: float
    annual_income_low: float
    annual_income_high: float
    rate_low: float
    rate_high: float
    applies_to: str
    income_stability_note: str
    assumption: str


def lease_income(footprint_result: AgrivoltaicFootprint,
                 agrivoltaic_only: bool = False) -> LeaseIncome:
    """Annual landowner lease income from hosting the array.

    `agrivoltaic_only` defaults to False deliberately. Lease income applies to ALL utility-scale
    solar regardless of agrivoltaic status -- a landowner is paid for hosting either way -- so
    restricting it to the agrivoltaic share would understate the income effect. Set True only when
    the question is specifically about land that ALSO retains agricultural production.

    Production value is NOT included and is not estimated here. Crop yield under panels is
    contested, varies by crop, and has no Virginia field-trial basis; adding a speculative
    production figure to a well-sourced lease figure would degrade the latter.
    """
    if agrivoltaic_only:
        lo, hi = footprint_result.agrivoltaic_acres_low, footprint_result.agrivoltaic_acres_high
        applies = (f'Agrivoltaic acreage only ({AGRIVOLTAIC_SHARE_OF_TOTAL_SOLAR:.0%} of build) -- '
                   'land that also retains agricultural production')
    else:
        lo, hi = footprint_result.firmed_acres_low, footprint_result.firmed_acres_high
        applies = ('All utility-scale acreage -- a landowner is paid for hosting the array '
                   'whether or not the siting is agrivoltaic')
    return LeaseIncome(
        acres_low=lo, acres_high=hi,
        annual_income_low=lo * VA_LEASE_RATE_LOW,
        annual_income_high=hi * VA_LEASE_RATE_HIGH,
        rate_low=VA_LEASE_RATE_LOW, rate_high=VA_LEASE_RATE_HIGH,
        applies_to=applies,
        income_stability_note=(
            'The NSPM-relevant benefit is income VARIANCE reduction, not income level. A '
            'contracted per-acre payment is a hedge against drought, hail and commodity price '
            'risk that dryland row-crop farming does not have, and is contractually independent '
            'of that year\'s harvest. This argument does not depend on agrivoltaic crop yields '
            'being neutral or positive, and therefore survives the contested and '
            'non-Virginia-specific state of the yield evidence.'),
        assumption=footprint_result.assumption)


# ============================================================================
# LOCAL REVENUE SHARE -- Va. Code § 58.1-2636
# ============================================================================
# The second rural economic-development channel, and the one aimed squarely at the constituency
# that has been REJECTING solar projects. Woods Rogers' account of the 2020 legislation is direct
# about the politics: rural localities "felt they were being forced to subsidize the economic
# development of the more affluent parts of the state", because low rural property values plus a
# machinery-and-tools exemption meant hosting a facility worth tens of millions brought little
# revenue. "The response of many rural localities was to reject a number of worthwhile projects."
#
# Revenue share was the legislature's answer: a locality may replace the M&T/real-estate treatment
# with a flat annual per-MW payment. Unlike lease income, which accrues to the landowner, this
# accrues to the COUNTY -- so it funds schools, roads and services for residents who host the
# infrastructure without owning the land.
#
# STATUTORY DETAIL, verified against the Code rather than assumed:
#   - up to $1,400/MW AC on solar generation capacity, AND a SEPARATE $1,400/MW AC on energy
#     storage capacity. Storage is easy to overlook and is material here: at 2045 the storage
#     fleet contributes roughly a third of the total.
#   - escalates 10% on 1 July 2026 and every five years thereafter, for projects approved on or
#     after 1 January 2021. Four escalations by 2045.
#   - does NOT apply to projects of 5 MW or less, nor to net-metered projects under §§ 56-594,
#     56-594.01, 56-594.02 or 56-594.2. Distributed rooftop and canopy are therefore largely
#     OUTSIDE this mechanism -- a real asymmetry between the utility-scale and distributed paths,
#     and a further reason the 85% utility/PPA framing carries the rural benefit case.
#   - it is a CEILING ("up to"), adopted by local ordinance. Not every locality has adopted one,
#     and some adopt below the maximum. Figures here assume adoption at the maximum and are
#     therefore an upper bound on this channel.
REVENUE_SHARE_BASE_RATE_PER_MW = 1_400.0
REVENUE_SHARE_FIRST_ESCALATION_YEAR = 2026
REVENUE_SHARE_ESCALATION_INTERVAL_YEARS = 5
REVENUE_SHARE_ESCALATION_RATE = 0.10
REVENUE_SHARE_MINIMUM_PROJECT_MW = 5.0


def revenue_share_rate_per_mw(year: int) -> float:
    """Statutory maximum revenue share rate in a given year, with § 58.1-2636(A)(2) escalation."""
    if year < REVENUE_SHARE_FIRST_ESCALATION_YEAR:
        return REVENUE_SHARE_BASE_RATE_PER_MW
    steps = (year - REVENUE_SHARE_FIRST_ESCALATION_YEAR) // REVENUE_SHARE_ESCALATION_INTERVAL_YEARS + 1
    return REVENUE_SHARE_BASE_RATE_PER_MW * (1 + REVENUE_SHARE_ESCALATION_RATE) ** steps


@dataclass(frozen=True)
class RevenueShare:
    year: int
    rate_per_mw: float
    solar_mw: float
    storage_mw: float
    solar_revenue: float
    storage_revenue: float
    total_revenue: float
    caveat: str


def revenue_share(year: int, solar_mw: float, storage_mw: float = 0.0) -> RevenueShare:
    """Annual local revenue share at the statutory maximum.

    `storage_mw` defaults to 0.0 but should almost always be supplied: § 58.1-2636(A)(1)(ii)
    assesses storage capacity separately from generation, and at 2045 storage is roughly a third
    of the total. Defaulting it to zero silently understates the rural benefit by that much, so
    the omission is recorded in the returned caveat rather than passing unnoticed.
    """
    rate = revenue_share_rate_per_mw(year)
    solar_rev, storage_rev = solar_mw * rate, storage_mw * rate
    caveat = (
        f'Assumes local adoption at the statutory MAXIMUM of ${rate:,.2f}/MW AC (§ 58.1-2636 is a '
        f'ceiling adopted by ordinance; not every locality has adopted one, and some adopt below '
        f'the maximum), so this is an upper bound on this channel. Projects of '
        f'{REVENUE_SHARE_MINIMUM_PROJECT_MW:,.0f} MW or less and net-metered projects are exempt, '
        f'so distributed rooftop and canopy are largely outside this mechanism. Nameplate is '
        f'measured in AC; if the modeled build is expressed in DC these figures are '
        f'correspondingly high.')
    if storage_mw == 0.0:
        caveat += (' NOTE: storage_mw was not supplied. Storage is separately assessable and is '
                   'roughly a third of the 2045 total, so this figure understates accordingly.')
    return RevenueShare(
        year=year, rate_per_mw=rate, solar_mw=solar_mw, storage_mw=storage_mw,
        solar_revenue=solar_rev, storage_revenue=storage_rev,
        total_revenue=solar_rev + storage_rev, caveat=caveat)


# ============================================================================
# CROP NET RETURNS -- Virginia Tech / SLEAC, the statutory basis
# ============================================================================
# Source: "Methods and Procedures: Determining the Use Value of Agricultural and Horticultural
# Land in Virginia", VCE publication 446-011 (AAEC-215P), Friedel and Kayser, Virginia Tech, last
# reviewed August 2025. These are the figures the State Land Evaluation Advisory Council uses to
# set agricultural use-value assessments under Va. Code § 58.1-3239 -- the numbers Virginia's own
# tax system runs on, not advocacy estimates. That provenance is the point: a farm-income
# comparison built on them is very hard to dispute.
#
# Figures below are the Prince Edward County composite farm for tax year 2020, the publication's
# own worked example. Net returns are seven-year OLYMPIC averages (highest and lowest dropped)
# over variable AND fixed costs, with federal program payments added where applicable.
#
# THE COMPARISON THIS ENABLES
#
# The composite farm's weighted average net return is $17.69/acre/year. Virginia solar lease
# rates run $1,200-2,500/acre/year. The lease is therefore 68x to 141x the return from farming
# the same ground -- and 6x to 13x even against soybeans, the composite farm's best performer.
#
# This reframes the agrivoltaic argument substantially. The question is not whether panel shading
# costs a farmer some fraction of yield; at these ratios, a farmer could lose the ENTIRE crop and
# still be far ahead. What agrivoltaics adds on top of that is the option to keep farming at all,
# and the food-production and land-preservation benefits that follow.
#
# THE VARIANCE ARGUMENT, IN THE SOURCE'S OWN DATA
#
# The publication's corn table for Prince Edward shows net returns by year:
#     2012  +$156.45     2013  -$52.39     2014  -$65.55     2015  +$27.09
#     2016   +$38.28     2017 -$112.44     2018  -$65.47
# FOUR OF SEVEN YEARS NEGATIVE. The methodology floors negatives at zero before averaging, so the
# published $76.27 corn figure is itself generous relative to what a farmer actually experienced.
#
# That is the income-variance case in Virginia's own official data, and it is why a contracted
# lease payment is a hedge rather than merely a supplement.
#
# CAVEATS, stated
#   - Prince Edward is the publication's worked EXAMPLE, not a Virginia average. Backing net
#     returns out of published use-values (net return = use-value x capitalization rate) across
#     other jurisdictions gives roughly $20/acre (Prince Edward) to $88/acre (Dinwiddie Piedmont).
#     Even at the high end the lease is 14-28x.
#   - Use-value is NOT annual net return. Use-value = net return / capitalization rate, so the
#     published per-acre use-values (e.g. $350-$1,530 for average cropland) are LAND VALUES and
#     must not be compared directly against an annual lease rate.
#   - Livestock is excluded from use-value entirely: the statute assesses "what is produced on the
#     land and not ... livestock, buildings, or other improvements". Grazing operations are
#     therefore not represented by these figures.
#   - TY2020 vintage; enterprise budgets lag the tax year by two years, so the underlying data is
#     DY2012-DY2018.
SLEAC_NET_RETURN_PER_ACRE = {
    'soybeans': 197.83,
    'alfalfa': 98.73,
    'corn': 76.27,
    'pasture': 3.69,
    'hay': 0.32,
}
SLEAC_COMPOSITE_FARM_NET_RETURN_PER_ACRE = 17.69
SLEAC_SOURCE = ('Virginia Tech / SLEAC, VCE 446-011 (AAEC-215P), Prince Edward County composite '
                'farm, tax year 2020 -- the statutory basis for agricultural use-value assessment '
                'under Va. Code § 58.1-3239')

#: Cross-jurisdiction range, derived as use-value x capitalization rate from the publication's own
#: Table B-1a. Wider than the Prince Edward example alone and used for the conservative comparison.
SLEAC_NET_RETURN_RANGE_ACROSS_JURISDICTIONS = (20.0, 88.0)


@dataclass(frozen=True)
class LeaseVersusFarmIncome:
    crop: str
    farm_net_return_per_acre: float
    lease_rate_low: float
    lease_rate_high: float
    multiple_low: float
    multiple_high: float
    source: str
    interpretation: str


def lease_versus_farm_income(crop: str = 'composite') -> LeaseVersusFarmIncome:
    """Solar lease income against the SLEAC net return for a given crop.

    'composite' is the default and the most representative single figure -- the weighted average
    across the composite farm, which is what the use-value assessment itself capitalizes.
    """
    if crop == 'composite':
        net = SLEAC_COMPOSITE_FARM_NET_RETURN_PER_ACRE
    elif crop in SLEAC_NET_RETURN_PER_ACRE:
        net = SLEAC_NET_RETURN_PER_ACRE[crop]
    else:
        raise ValueError(
            f"no SLEAC net return for {crop!r}; available: 'composite' plus "
            f"{sorted(SLEAC_NET_RETURN_PER_ACRE)}. Do not substitute a figure from another state "
            "-- the value of this comparison is that it rests on Virginia's own statutory "
            "assessment methodology.")
    return LeaseVersusFarmIncome(
        crop=crop, farm_net_return_per_acre=net,
        lease_rate_low=VA_LEASE_RATE_LOW, lease_rate_high=VA_LEASE_RATE_HIGH,
        multiple_low=VA_LEASE_RATE_LOW / net, multiple_high=VA_LEASE_RATE_HIGH / net,
        source=SLEAC_SOURCE,
        interpretation=(
            'At these ratios the yield question is secondary: a farmer could lose the entire crop '
            'and remain far ahead on lease income alone. What agrivoltaics adds is the option to '
            'keep farming at all, with the food-production and land-preservation benefits that '
            'follow. Note also that SLEAC floors negative annual net returns at zero before '
            'averaging, so published figures are generous relative to what farmers experienced -- '
            'Prince Edward corn was NEGATIVE in four of the seven years averaged.'))


# ============================================================================
# VIRGINIA LAND IN FARMS BY USE -- 2022 Census of Agriculture
# ============================================================================
# Source: USDA NASS, 2022 Census of Agriculture, Virginia state profile (cp99051). 38,995 farms,
# average 187 acres, $5.49B market value of products sold.
#
# THE FINDING THIS ENABLES, and it reframes the land-use objection
#
# Against ALL land in farms the agrivoltaic requirement is 8.3-12.6%. Against CROPLAND ALONE it is
# 21-32% -- a far harder number, and the one an opponent would reach for.
#
# But agrivoltaic compatibility is not uniform across uses, and the evidence runs in exactly the
# opposite direction to the acreage pressure:
#
#   PASTURELAND is the most mature agrivoltaic practice there is. The American Solar Grazing
#   Association's 2024 census counted ~113,000 sheep across 500+ US solar sites, and cattle
#   compatibility is peer-reviewed (University of Minnesota research dairy, AIP Conference
#   Proceedings 2022, finding shade improved cattle comfort during heat events with an associated
#   milk-production benefit).
#
#   HAY AND FORAGE are well-supported -- the University of Illinois research plot grows switchgrass
#   and orchardgrass successfully alongside solar.
#
#   CORN AND SOYBEANS, Virginia's two largest row crops, carry the WEAKEST evidence: current
#   varieties are bred for full sun, and the peer-reviewed literature describes real-world
#   agrivoltaic field data on these specific crops as "almost nonexistent".
#
# Pasture (1,915,266 acres) plus forage hay/haylage (1,117,726) gives 3,032,992 acres. The entire
# agrivoltaic requirement of 605,626-921,733 acres is 20.0-30.4% of that -- so it fits within forage
# land alone, WITHOUT TOUCHING corn, soybeans, cotton, peanuts or tobacco.
#
# Forage land exceeds the weak-evidence row crops (soybeans 610,605 + corn 384,337 + wheat 165,415
# = 1,160,357 acres) by 2.6x, so the compatible base is not merely sufficient but comfortably so.
#
# AND THE ECONOMICS ALIGN WITH THE COMPATIBILITY. SLEAC net returns are $3.69/acre for pasture and
# $0.32/acre for hay -- the two lowest of any use. Solar lease income is therefore most
# transformative precisely where agrivoltaic compatibility is strongest and where the opportunity
# cost of hosting is lowest. That is not a coincidence to gloss over; it is the core of the case.
#
VA_LAND_IN_FARMS_BY_USE_ACRES = {
    'cropland': 2_884_293,
    'pastureland': 1_915_266,
    'woodland': 2_053_786,
    'other': 456_342,
}
VA_TOTAL_LAND_IN_FARMS_ACRES = sum(VA_LAND_IN_FARMS_BY_USE_ACRES.values())   # 7,309,687
VA_FARMS_COUNT = 38_995
VA_AG_PRODUCTS_SOLD_USD = 5_491_996_000

# Top crops in acres, 2022 Census of Agriculture, Virginia state profile. Pastureland is reported
# separately under land-in-farms-by-use above and is NOT a crop, so it is not listed here.
#
# CORRECTED 2026-09-11: an earlier version carried VA_HAY_ACRES_APPROX = 870,000, DERIVED from
# NASS production tonnage at an assumed ~2.5 tons/acre because the Census figure had not been
# located. The Census reports 1,117,726 acres of forage (hay/haylage) -- the derivation was 22%
# LOW. It has been replaced, and the derived constant removed rather than left available to be
# picked up by mistake.
#
# The correction moves the forage finding in the favourable direction: the agrivoltaic requirement
# is 20.0-30.4% of forage land rather than the 21.7-33.1% previously reported.
VA_TOP_CROPS_ACRES = {
    'forage_hay_haylage': 1_117_726,
    'soybeans': 610_605,
    'corn_for_grain': 384_337,
    'wheat_for_grain': 165_415,
}

#: Cotton, peanuts, tobacco, vegetables and orchards are not captured in the state profile's
#: truncated top-crops list. They are collectively small relative to the four above, but the list
#: is INCOMPLETE and should not be summed as though it were total cropland.
VA_TOP_CROPS_IS_PARTIAL = (
    "VA_TOP_CROPS_ACRES is the state profile's top-crops list and does NOT include cotton, "
    'peanuts, tobacco, vegetables or orchards. Do not sum it as total cropland -- use '
    "VA_LAND_IN_FARMS_BY_USE_ACRES['cropland'] for that.")

#: Row crops carrying the WEAKEST agrivoltaic evidence -- current varieties are bred for full sun,
#: and the literature describes real-world field data on them as "almost nonexistent". Named so
#: the contrast against forage is explicit rather than implied.
WEAK_EVIDENCE_ROW_CROPS = ('soybeans', 'corn_for_grain')

#: Uses where agrivoltaic compatibility evidence is strongest. Deliberately excludes cropland as a
#: whole: within cropland, hay and winter wheat are well-supported while corn and soybeans are not,
#: and treating cropland as uniformly compatible would overstate the case.
FORAGE_COMPATIBLE_USES = ('pastureland', 'hay')


@dataclass(frozen=True)
class LandUseFit:
    agrivoltaic_acres_low: float
    agrivoltaic_acres_high: float
    share_of_all_farmland: tuple
    share_of_cropland: tuple
    share_of_forage_land: tuple
    forage_acres: float
    fits_within_forage: bool
    finding: str
    caveat: str


def land_use_fit(footprint_result: AgrivoltaicFootprint) -> LandUseFit:
    """Where the agrivoltaic acreage would have to land, against Virginia's actual land in farms.

    Reports the share against THREE bases rather than one, because the choice of denominator is
    the whole argument: all farmland flatters the case, cropland alone damns it, and forage land
    is the one that matches where the compatibility evidence actually is.
    """
    lo, hi = footprint_result.agrivoltaic_acres_low, footprint_result.agrivoltaic_acres_high
    total = VA_TOTAL_LAND_IN_FARMS_ACRES
    crop = VA_LAND_IN_FARMS_BY_USE_ACRES['cropland']
    forage = (VA_LAND_IN_FARMS_BY_USE_ACRES['pastureland']
              + VA_TOP_CROPS_ACRES['forage_hay_haylage'])
    return LandUseFit(
        agrivoltaic_acres_low=lo, agrivoltaic_acres_high=hi,
        share_of_all_farmland=(lo / total, hi / total),
        share_of_cropland=(lo / crop, hi / crop),
        share_of_forage_land=(lo / forage, hi / forage),
        forage_acres=forage,
        fits_within_forage=hi <= forage,
        finding=(
            'The requirement fits within pasture and hay land alone -- 20-30% of it -- without '
            'touching corn, soybeans, cotton, peanuts or tobacco. That matters because agrivoltaic '
            'compatibility is strongest on exactly those forage uses (sheep grazing is the most '
            'mature practice in the field) and weakest on the row crops, where the literature '
            'describes real-world data as almost nonexistent. The economics align the same way: '
            'pasture and hay carry the LOWEST SLEAC net returns of any use ($3.69 and $0.32/acre), '
            'so lease income is most transformative precisely where compatibility is best and the '
            'opportunity cost of hosting is lowest.'),
        caveat=VA_TOP_CROPS_IS_PARTIAL)
