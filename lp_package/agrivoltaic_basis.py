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
