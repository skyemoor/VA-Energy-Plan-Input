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
    'cotton': 91_073,
}
# These five are the COMPLETE 'Top Crops in Acres' list the state profile publishes -- there is no
# top ten. They total 2,369,156 acres, 82% of the 2,884,293-acre cropland base, so the unlisted
# remainder is about 515,000 acres.

#: Crop SALES by category ($1,000). Acreage is NOT published for these groupings, so they cannot be
#: added to the acreage table above. Carried because the compatibility gradient does not track
#: acreage: vegetables have the STRONGEST evidence in the entire agrivoltaics literature (tomatoes
#: and peppers good-to-improved across four independent studies; lettuce well, with one trial
#: finding shading reduced bitterness), and Virginia's Eastern Shore tomato industry sits squarely
#: in that category -- but at $134.6M of sales it is a small share of crop value and an unknown,
#: probably small, share of acreage.
VA_CROP_SALES_BY_CATEGORY_THOUSANDS = {
    'grains_oilseeds_dry_beans_peas': 843_372,
    'nursery_greenhouse_floriculture_sod': 398_562,
    'other_crops_and_hay': 184_958,
    'fruits_tree_nuts_berries': 144_372,
    'vegetables_melons_potatoes': 134_618,
    'cotton_and_cottonseed': 81_153,
    'tobacco': 69_566,
    'christmas_trees_woody_crops': 25_583,
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


# ============================================================================
# LIVESTOCK INVENTORY AND THE GRAZING CAPACITY CONSTRAINT
# ============================================================================
# 2022 Census of Agriculture, Virginia, inventory at 31 December 2022.
#
# THE CONSTRAINT THE COMPATIBILITY ARGUMENT CONCEALS
#
# Sheep grazing is repeatedly described -- correctly -- as the most mature agrivoltaic practice.
# But Virginia's ENTIRE sheep flock is 82,208 head, and the American Solar Grazing Association's
# 2024 census counted roughly 113,000 sheep across 500+ US solar sites. The national solar-grazing
# flock is already larger than every sheep in Virginia.
#
# At conventional solar-grazing stocking rates of 2-6 head per acre, covering even the LOW end of
# the agrivoltaic requirement (605,626 acres) would need 1.2M to 3.6M sheep -- 15x to 44x the
# state's whole flock. Sheep grazing therefore CANNOT manage this acreage, however well suited it
# is per-acre.
#
# Cattle are the more plausible route at scale. Virginia has 1,273,665 head, and at roughly 1-2
# acres per animal unit the agrivoltaic acreage could carry a substantial fraction of the existing
# herd. Cattle agrivoltaics is less mature than sheep but no longer speculative -- the University
# of Minnesota research dairy has grazed under an elevated array since 2020 (AIP Conference
# Proceedings, 2022), finding shade improved comfort during heat events with an associated
# milk-production benefit, and Cornell and The Nature Conservancy are running a 2026 study on
# barriers to scaling it. It does require taller, more expensive racking than sheep.
#
# WHY THIS MATTERS FOR THE CASE: 'sheep graze under panels' is true and is the strongest per-acre
# evidence available, but it is not a scalable answer at Virginia's buildout. Presenting it as one
# invites a straightforward rebuttal from anyone who looks up the state's flock size. The honest
# framing is that forage LAND is abundant (3.03M acres) while grazing LIVESTOCK to use it is not,
# so hay and haylage production -- which needs no animals at all -- carries more of the load than
# the grazing literature alone would suggest.
VA_LIVESTOCK_INVENTORY = {
    'cattle_and_calves': 1_273_665,
    'sheep_and_lambs': 82_208,
    'goats': 40_952,
    'horses_and_ponies': 55_258,
}

#: Conventional solar-grazing stocking, head per acre. A range, not a point: it varies with forage
#: productivity, rotation and panel spacing.
SOLAR_GRAZING_SHEEP_PER_ACRE = (2.0, 6.0)

#: American Solar Grazing Association 2024 census -- the national solar-grazing flock.
NATIONAL_SOLAR_GRAZING_SHEEP = 113_000


@dataclass(frozen=True)
class GrazingCapacity:
    agrivoltaic_acres: float
    sheep_needed_low: float
    sheep_needed_high: float
    va_sheep_inventory: int
    multiple_of_state_flock_low: float
    multiple_of_state_flock_high: float
    sheep_can_cover: bool
    finding: str


def grazing_capacity(agrivoltaic_acres: float) -> GrazingCapacity:
    """Whether Virginia's sheep flock could actually graze the agrivoltaic acreage.

    Exists because the answer is no, by more than an order of magnitude, and the agrivoltaic
    literature's emphasis on sheep makes that easy to miss.
    """
    lo_rate, hi_rate = SOLAR_GRAZING_SHEEP_PER_ACRE
    flock = VA_LIVESTOCK_INVENTORY['sheep_and_lambs']
    need_lo, need_hi = agrivoltaic_acres * lo_rate, agrivoltaic_acres * hi_rate
    return GrazingCapacity(
        agrivoltaic_acres=agrivoltaic_acres,
        sheep_needed_low=need_lo, sheep_needed_high=need_hi,
        va_sheep_inventory=flock,
        multiple_of_state_flock_low=need_lo / flock,
        multiple_of_state_flock_high=need_hi / flock,
        sheep_can_cover=need_lo <= flock,
        finding=(
            f"Virginia's entire sheep flock is {flock:,} head -- fewer than the ~"
            f"{NATIONAL_SOLAR_GRAZING_SHEEP:,} already grazing US solar sites nationally. Covering "
            f"{agrivoltaic_acres:,.0f} acres at {lo_rate:g}-{hi_rate:g} head/acre needs "
            f"{need_lo/1e6:.1f}M-{need_hi/1e6:.1f}M sheep, {need_lo/flock:.0f}x-{need_hi/flock:.0f}x "
            f"the state flock. Sheep grazing is the strongest PER-ACRE evidence available and is "
            f"not a scalable answer at this buildout. Cattle "
            f"({VA_LIVESTOCK_INVENTORY['cattle_and_calves']:,} head) are more plausible at scale "
            f"but need taller, costlier racking. Hay and haylage production, which needs no "
            f"animals at all, therefore carries more of the load than the grazing literature "
            f"alone would suggest."))


# ============================================================================
# FSA CROP ACREAGE, 2026 -- a second, independent and much finer source
# ============================================================================
# Source: USDA Farm Service Agency, "Crop Acreage Data", 2026 Virginia rows (August 2026 release),
# obtained through FSA's FOIA electronic reading room. Acres reported BY PRODUCERS to FSA, by
# county, crop, crop type, intended use and irrigation practice: 4,384 rows, 98 counties, 121
# distinct crops, 3,014,135 planted acres.
#
# WHY THIS IS BETTER THAN THE CENSUS SUMMARY FOR THIS PURPOSE
#   - 121 crops against the state profile's top-five list
#   - 2026 against the Census's 2022, and annual rather than five-yearly
#   - county resolution, so siting can eventually be matched to where crops actually are
#   - intended use is recorded, which matters: forage-intended acreage is identifiable directly
#     rather than inferred
#
# WHAT IT IS NOT. FSA counts PLANTED acres reported by participating producers. It therefore
# EXCLUDES pastureland entirely -- 1,915,266 acres in the Census -- because pasture is not a
# planted crop, and it excludes producers who do not report to FSA. The two sources are
# complementary, not alternatives, and must not be summed carelessly:
#
#     FSA planted acres          3,014,135   (crops, 2026, excludes pasture)
#     Census cropland            2,884,293   (2022)
#     Census pastureland         1,915,266   (2022, absent from FSA)
#
# THE FORAGE FINDING SURVIVES AND STRENGTHENS. MIXED FORAGE alone is 1,373,771 acres -- 45.6% of
# all planted acres in Virginia and the single largest crop in the state by a wide margin, ahead of
# soybeans (584,642) and corn (418,778) combined. Adding grass, sorghum forage, alfalfa, millet and
# clover gives 1,440,010 acres of forage, 47.8% of planted acreage.
#
# Combined with Census pastureland the compatible base is 3,355,276 acres, and the agrivoltaic
# requirement is 18-27% of it -- comfortably within, and a slightly better ratio than the Census
# alone gave (20.0-30.4%).
#
# COVER CROP -- TWO CORRECTIONS, 2026-09-11.
# FULL ACCOUNT: docs/methodology/Cover_Crops_and_Agrivoltaics.md. Summarised below. An earlier version of this module excluded cover crop
# acreage on the grounds that it is "not a cash crop" and "unaddressed in the agrivoltaic
# literature reviewed". Both halves of that were wrong in ways that matter.
#
# CORRECTION 1: COVER CROP ACREAGE IS NOT A SEPARATE LAND BASE. Cover crops are grown BETWEEN cash
# crops on the SAME ground -- to fix nitrogen, suppress weeds, prevent erosion and rebuild soil
# after a growing season, or through a fallow year to prevent soil exhaustion. So FSA's 3,014,135
# "planted acres" DOUBLE-COUNTS land carrying both a cover crop and a cash crop in the same year.
# It is not a unique-area figure and must not be treated as one.
#
# That is visible in the numbers: FSA planted acres (3,014,135) exceed the Census cropland base
# (2,884,293), and removing cover crop (302,940) puts the remainder BELOW it. Virginia's own
# use-value methodology makes the same point from the other direction -- SLEAC treats winter
# annuals as "always followed by a summer crop" and subtracts double-cropped acreage explicitly to
# avoid exactly this error.
#
# Consequence: the "47.8% of planted acreage" forage share is computed against a double-counted
# denominator. The compatible-base finding is unaffected, because that is computed against FSA
# forage plus CENSUS pastureland, neither of which is a planted-acres percentage.
#
# CORRECTION 2: COVER CROPS ARE PLAUSIBLY MORE AGRIVOLTAIC-COMPATIBLE THAN CASH CROPS, NOT LESS.
# SARE's "Managing Cover Crops Profitably" (3rd ed.) states directly that "many cover crops offer
# harvest possibilities as forage, grazing or seed that work well in systems with multiple crop
# enterprises and livestock", and its own illustration caption notes that winter wheat as a cover
# "grows well in fall, then provides forage and protects soil over winter". The species involved --
# rye, ryegrass, clover, hairy vetch, sorghum-sudangrass, winter wheat -- are largely the same
# forage species already in the strong-evidence group.
#
# Three reasons the fit is better than for a cash crop:
#   - the objective is soil health and nitrogen fixation, not yield maximization, so a shading
#     penalty that would be disqualifying for corn is largely immaterial
#   - solar sites require vegetation management regardless; a cover crop serves that purpose while
#     also delivering its agronomic benefits
#   - during a cover or fallow period the land is already earning no cash-crop income, so the
#     opportunity cost of hosting an array in that window is close to zero
#
# TWO COVER CROP PURPOSES THAT AGRIVOLTAICS DIRECTLY SERVES (University of Georgia Sustainable
# Agriculture, Farm Management: Cover Crops). UGA's list of why farmers plant cover crops includes,
# verbatim, "to extend the grazing season" and "to provide habitat and nectar for beneficial
# insects". Both are things a solar array improves rather than impedes:
#
#   GRAZING SEASON EXTENSION -- panel shade reduces heat stress on both sward and livestock, which
#   is the mechanism behind the University of Minnesota dairy finding. A cover crop planted for
#   grazing extension under an array compounds two effects aimed at the same outcome.
#
#   POLLINATOR HABITAT -- listed in this analysis's own NSPM channel table as an identified but
#   unquantified rural benefit. Cover cropping under panels is a route to it that requires no
#   additional land and no separate program, since the planting is happening anyway.
#
# UGA also confirms the mechanics underlying Correction 1 directly: cover crop selection depends on
# "your planting window (the time between cash crops)", and cover crops are "planted primarily for
# their agro-ecosystem benefits rather than for harvest" -- between cash crops, on the same ground,
# with yield not the objective.
#
# SPECIES OVERLAP WITH THE FORAGE GROUP IS SUBSTANTIAL, which is why the compatibility conclusion
# transfers. UGA's regionally-appropriate list -- cereal rye, oats, annual ryegrass, triticale,
# wheat, crimson/balansa clover, hairy and common vetch, Austrian winter peas for fall/winter;
# sorghum, sorghum-sudangrass, pearl and browntop millet, cowpeas, sunn hemp for spring/summer --
# is largely cool- and warm-season forage species. Sorghum-sudangrass and millet appear in BOTH
# this list and the FSA forage group used above, so the two categories overlap in the data as well
# as in agronomy.
#
# VIRGINIA-SPECIFIC: TWO EXISTING POLICY MECHANISMS ALREADY ATTACH TO THIS
# Source: Virginia Department of Conservation and Recreation, "Cover crops: a win for farmers and
# the environment" (September 2024), originally published in the Small Farm Outreach Program
# quarterly of Cooperative Extension at Virginia State University.
#
# 1. VACS COST-SHARE ALREADY FUNDS IT. The Virginia Agricultural Best Management Practices
#    Cost-Share Program, administered by DCR and delivered through local Soil and Water
#    Conservation Districts, "can decrease the cost of planting cover crops on your farm" and
#    covers "over 70 other conservation practices". This is the same shape of finding as
#    § 45.2-1702 energy performance contracting elsewhere in this analysis: a funding mechanism
#    that ALREADY EXISTS, requiring no new legislation and no new appropriation. Cover cropping
#    under an array is the same practice VACS already cost-shares.
#
# 2. CHESAPEAKE BAY NUTRIENT REDUCTION. DCR states cover crops reduce "nonpoint source pollution by
#    slowing runoff and absorbing excess nitrogen that otherwise would leach into the water table",
#    and can "potentially reduce the need for synthetic fertilizer". Virginia carries binding
#    nutrient-reduction obligations under the Chesapeake Bay TMDL, and cover crops are an
#    established BMP against them.
#
#    This is the most POLICY-RELEVANT non-energy impact identified for the rural case, because it
#    is a quantified obligation Virginia is already required to meet at cost. An agrivoltaic array
#    whose vegetation management is a cover crop delivers nutrient reduction on land that would
#    otherwise need a separate BMP to achieve it. NOT quantified here -- doing so needs
#    Bay-model nutrient-reduction efficiencies per acre and is out of scope -- but it is named in
#    the NSPM channel table as identified-and-unquantified rather than omitted.
#
# 3. THIRD INDEPENDENT CONFIRMATION OF THE DOUBLE-COUNT. DCR: cover crops are "non-cash crops
#    planted between primary crops". That is now attested by SLEAC (winter annuals always followed
#    by a summer crop), UGA (selection depends on the window between cash crops) and Virginia's own
#    conservation agency. The FSA planted-acres figure is not a unique-area figure.
#
# 4. EQUITY DIMENSION. The DCR piece was published through Virginia State University's Small Farm
#    Outreach Program, which serves "small, limited-resource, socially disadvantaged and veteran
#    farmers and ranchers". The farms for which a contracted lease payment most changes the
#    survival calculus are the ones with the least capacity to absorb a bad year -- the same
#    population. Relevant to NSPM treatment of distributional impacts, and not developed here.
#
# NOT ADDED TO THE COMPATIBLE BASE, deliberately. Because of Correction 1 the acreage largely
# overlaps land already counted, so adding it would double-count. It is recorded here because it
# strengthens the QUALITATIVE case -- 302,940 acres of Virginia cropland are already being managed
# for soil health rather than yield in any given year, on species that graze well -- without
# changing any quantity.
FSA_2026_TOP_CROPS_PLANTED_ACRES = {
    'mixed_forage': 1_373_771,
    'soybeans': 584_642,
    'corn': 418_778,
    'cover_crop': 302_940,
    'wheat': 73_643,
    'cotton_upland': 73_417,
    'grass': 45_947,
    'peanuts': 29_526,
    'rye': 15_687,
    'barley': 14_536,
    'tobacco_flue_cured': 12_643,
    'sorghum': 11_188,
    'triticale': 10_402,
    'sorghum_forage': 8_014,
    'alfalfa': 6_918,
}
FSA_2026_TOTAL_PLANTED_ACRES = 3_014_135
FSA_2026_COUNTIES = 98
FSA_2026_DISTINCT_CROPS = 121

#: Crops in the FSA data whose agrivoltaic evidence is strong -- forage and grazing swards. Cover
#: crop is deliberately absent despite being plausibly MORE compatible than cash crops: its acreage
#: overlaps land already counted, so including it would double-count. See the cover crop note above.
FSA_FORAGE_CROPS = ('mixed_forage', 'grass', 'sorghum_forage', 'alfalfa')
FSA_FORAGE_ACRES = 1_440_010          # includes millet and clover, not listed individually above

FSA_SOURCE_CAVEAT = (
    'FSA PLANTED ACRES DOUBLE-COUNT double-cropped land: cover crops (302,940 acres) are grown '
    'between cash crops on the same ground, so 3,014,135 is not a unique-area figure. SLEAC makes '
    'the same correction explicitly, treating winter annuals as always followed by a summer crop. '
    'FSA counts PLANTED acres reported by participating producers. It excludes pastureland '
    'entirely (1,915,266 acres in the 2022 Census) because pasture is not a planted crop, and '
    'excludes producers who do not report to FSA. Do not sum FSA planted acres with Census '
    'cropland -- they overlap. Do combine FSA forage with Census pastureland, which are disjoint.')


# ============================================================================
# MOUNTING CONFIGURATION -- AND A PROBLEM WITH THE ACRES/MW ASSUMPTION
# ============================================================================
# Added 2026-09-11. Revises two things recorded earlier in this module.
#
# REVISION 1: THE CORN EVIDENCE IS NO LONGER "ALMOST NONEXISTENT"
#
# This module and the agrivoltaics appendix both state that real-world field data on corn and
# soybeans is "almost nonexistent". For corn specifically that is now out of date:
#
#   Colorado State University, northern Colorado, 2024 season. Vertical bifacial panels in
#   NORTH-SOUTH oriented rows, corn planted between them. Treatments: centre, east (morning
#   light/afternoon shade), west (morning shade/afternoon light), and unshaded control, three
#   replicates. "Results showed no significant differences in silage or grain yields across
#   treatments (p > 0.05), indicating this vertical PV system did not negatively impact crop
#   productivity." (AgriVoltaics Conference Proceedings, "Impacts of a Vertical Bifacial
#   Agrivoltaics System on Field Corn in Northern Colorado, USA: Performance of Silage Corn in the
#   Establishment Year".)
#
#   Also: Sekiyama & Nagashima, "Solar sharing for both food and clean energy production:
#   Performance of agrivoltaic systems for corn, a typical shade-intolerant crop", Environments
#   6(6):65, 2019.
#
# STATED LIMITS: ONE season, the ESTABLISHMENT year, ONE site in a semi-arid continental climate
# unlike Virginia's humid subtropical. A null result at p > 0.05 with three replicates is weak
# evidence of no effect rather than strong evidence of equivalence. But "no significant difference"
# from a real field trial is a materially different position from "almost nonexistent data", and
# the earlier characterisation should not be repeated unqualified.
#
# THE CONFIGURATION MATTERS MORE THAN THE CROP. The result is specific to VERTICAL BIFACIAL panels
# in N-S rows, which shade a given plant only in the morning or only in the afternoon rather than
# through the midday peak. It does not transfer to conventional tilted arrays.
#
# REVISION 2 -- AND THIS IS A PROBLEM: 4-6 ACRES/MW IS THE WRONG BASIS FOR AGRIVOLTAICS
#
# ACRES_PER_MW_LOW/HIGH above are for standard single-axis tracking. Agrivoltaic configurations are
# materially less land-efficient, in both of the two viable designs:
#
#   VERTICAL BIFACIAL -- no LCOE penalty, but low energy density. A Jordan pilot comparing a
#   10-degree tilted array against a vertical east-west "fence" found the vertical system produced
#   1,288 kWh/kWp against the tilted system's 1,962 -- about 35% less per kWp -- and delivered
#   "energy yield equivalent to about 33% of the land area at the tested configuration". Crucially
#   it achieved this "without increasing the LCOE", whereas the elevated tilted configuration
#   "increases the levelized cost of electricity by roughly 88% compared to a conventional
#   ground-mounted system due to elevated structural costs".
#
#   ROW SPACING COMPOUNDS IT. A University of Turku study of vertical bifacial systems found row
#   spacing must be 11.3-13.7 m to retain 90% of reference-field agricultural yield. Wide spacing
#   is what makes the crop yield null results possible, and it directly reduces MW per acre.
#
# So the two designs trade against each other: elevated tilted keeps energy density but adds ~88%
# to LCOE; vertical bifacial keeps LCOE but needs substantially more land per MW. NEITHER matches
# the 4-6 acres/MW figure used for the footprint above, which is a standard-tracking number.
#
# CONSEQUENCE, stated rather than patched: the acreage figures in footprint() are a LOWER BOUND for
# agrivoltaic siting. The land-use fit (20-30% of forage land) and the farmland-share figures
# (7.9-12.0%) are correspondingly optimistic. Quantifying the correction needs an agrivoltaic-
# specific acres/MW figure, which this analysis does not yet have -- see AGRIVOLTAIC_ACRES_PER_MW_
# IS_UNRESOLVED. Substituting a guess would be worse than carrying the gap explicitly.
# ============================================================================
# THE STRONGEST CORN EVIDENCE: PURDUE FARM-SCALE TRIAL AND VALIDATED MODEL
# ============================================================================
# Gupta, Gruss, Cammarano, Tuinstra, Gitau, Agrawal et al., "Optimizing corn agrivoltaic farming
# through farm-scale experimentation and modeling", Cell Reports Sustainability 1, 100148, 26 July
# 2024. Open access.
#
# This supersedes the "almost nonexistent corn data" position entirely. It is farm-scale rather
# than plot-scale, uses EAST-WEST SUN-TRACKING panels rather than fixed vertical, and pairs the
# field trial with a crop model calibrated on the unshaded control and then validated against the
# shaded region -- which is what makes the configuration exploration credible.
#
# MEASURED YIELDS
#     without-PV (adjoining farm area)   10,955 kg/ha
#     between PV panels                  10,182 kg/ha      = 93.0% of unshaded, a 7.1% reduction
#
# MODEL VALIDATION (the reason the rest is usable)
#     APSIM calibrated on unshaded        10,856 kg/ha  vs 10,955 measured
#     APSIM + shadow model, PV region     10,102 kg/ha  vs 10,182 measured
# Both within ~1% of measurement. The model was calibrated ONLY on unshaded data, so agreement in
# the shaded region is genuine validation rather than fitting.
#
# THE HEADLINE MECHANISM: yield is governed by SPATIOTEMPORAL SHADOW DISTRIBUTION, not total
# radiation alone. Two configurations delivering identical total light to a plant produce different
# yields depending on WHEN the shadow falls. That is what makes active optimisation possible, and
# it is why results do not transfer between mounting configurations -- the CSU vertical-bifacial
# null and this 7.1% tracking-panel reduction are not in conflict; they are different shadow
# regimes.
#
# THREE DESIGN FINDINGS THAT BEAR DIRECTLY ON THIS PROJECT'S ACRES/MW GAP
#
#   1. TRACKER HEIGHT barely matters. "Average corn yield is a weak function of the tracker height
#      up to 2.44 m", though row-to-row variability rises as height falls. So the expensive part of
#      elevated racking buys little yield -- relevant against the ~88% LCOE premium recorded above
#      for elevated tilted configurations.
#
#   2. WIDER ROW SPACING DOES NOT HELP beyond a point. "Increasing the distance between the
#      adjacent PV rows beyond the 9.1 m, while keeping the total power over the entire land
#      constant, does not lead to an increase in corn yield based on the total land area."
#      This CONTRADICTS the intuition behind the University of Turku vertical-bifacial finding of
#      11.3-13.7 m spacing, and the difference is again configuration: tracking panels redistribute
#      shadow over the day in a way fixed vertical panels do not. 9.1 m is a materially tighter
#      spacing and therefore a materially better acres/MW than the vertical route.
#
#   3. ANTI-TRACKING GIVES LITTLE. Anti-tracking from 2 PM to 6 PM produced the greatest yield
#      gain, "however, this increase in corn yield of 5.6% is quite modest and should be weighed
#      against a substantial decline in solar power." Sacrificing generation to recover yield is a
#      poor trade at these magnitudes -- which matters for a scenario whose purpose is energy.
#
# WHAT IT DOES NOT RESOLVE. The paper does not state acres/MW or MW/ha directly, so the gap flagged
# in AGRIVOLTAIC_ACRES_PER_MW_IS_UNRESOLVED remains open -- but 9.1 m row spacing at constant total
# power is a far more favourable anchor than the vertical route's 11.3-13.7 m, and suggests the
# tracking configuration is the one to cost. Site is Indiana (Purdue), humid continental -- closer
# to Virginia than northern Colorado's semi-arid climate, though still not a match.
CORN_PURDUE_TRIAL = {
    'unshaded_yield_kg_per_ha': 10_955,
    'pv_region_yield_kg_per_ha': 10_182,
    'apsim_unshaded_modelled_kg_per_ha': 10_856,
    'apsim_pv_region_modelled_kg_per_ha': 10_102,
    'configuration': 'east-west sun-tracking',
    'row_spacing_beyond_which_no_yield_gain_m': 9.1,
    'tracker_height_yield_insensitive_up_to_m': 2.44,
    'anti_tracking_max_yield_gain_fraction': 0.056,
    'citation': ('Gupta et al., "Optimizing corn agrivoltaic farming through farm-scale '
                 'experimentation and modeling", Cell Reports Sustainability 1, 100148, 2024'),
}


def corn_yield_ratio_under_tracking_pv() -> float:
    """Measured PV-region corn yield as a fraction of the adjoining unshaded farm area.

    A single site-season, so not a general coefficient -- but it is farm-scale, measured rather
    than modelled, and paired with an independently validated model, which makes it the best corn
    figure this analysis holds.
    """
    t = CORN_PURDUE_TRIAL
    return t['pv_region_yield_kg_per_ha'] / t['unshaded_yield_kg_per_ha']


CORN_VERTICAL_BIFACIAL_EVIDENCE = (
    'Colorado State University, northern Colorado, 2024: vertical bifacial panels in north-south '
    'rows, field corn planted between. No significant differences in silage or grain yields across '
    'centre/east/west/control treatments (p > 0.05). One season, establishment year, one '
    'semi-arid site. Revises but does not overturn the "almost nonexistent corn data" position, '
    'and is specific to VERTICAL configurations -- it does not transfer to tilted arrays.')

VERTICAL_BIFACIAL_SPECIFIC_YIELD_KWH_PER_KWP = 1_288      # Jordan pilot, vertical east-west
TILTED_BIFACIAL_SPECIFIC_YIELD_KWH_PER_KWP = 1_962        # same pilot, 10-degree south-facing
ELEVATED_TILTED_LCOE_PREMIUM_FRACTION = 0.88              # vs conventional ground-mount
VERTICAL_BIFACIAL_ROW_SPACING_M_FOR_90PCT_YIELD = (11.3, 13.7)   # University of Turku

AGRIVOLTAIC_ACRES_PER_MW_IS_UNRESOLVED = (
    'ACRES_PER_MW_LOW/HIGH (4-6) are STANDARD SINGLE-AXIS TRACKING figures. Both viable '
    'agrivoltaic configurations are less land-efficient: vertical bifacial yields ~35% less per '
    'kWp and needs 11.3-13.7 m row spacing to retain 90% of crop yield, while elevated tilted '
    'racking preserves energy density but adds ~88% to LCOE. Every acreage figure derived from '
    '4-6 acres/MW is therefore a LOWER BOUND for agrivoltaic siting, and the land-use fit and '
    'farmland-share percentages are correspondingly optimistic. An agrivoltaic-specific acres/MW '
    'figure is needed and is not yet held; a guess would be worse than carrying the gap.')
