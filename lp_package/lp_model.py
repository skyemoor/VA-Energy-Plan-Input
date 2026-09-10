import numpy as np
import pandas as pd
from scipy import sparse
from scipy.optimize import linprog

# ---------------- Financial / technology parameters ----------------
WACC = 0.045
CRF = WACC*(1+WACC)**25 / ((1+WACC)**25 - 1)

# NEW (Scenario 2 capex build-out): CCGT-specific CRF, distinct from the 25-year CRF above used for
# solar/storage. Lazard's LCOE+ v19.0 (already in this project's knowledge base) sources CCGT's own
# facility life directly at 30 years -- using the same 25-year figure for CCGT would misrepresent an
# asset this project has actual sourced data for. Same WACC (4.5%), different amortization horizon.
CCGT_LIFE_YEARS = 30
CCGT_CRF = WACC*(1+WACC)**CCGT_LIFE_YEARS / ((1+WACC)**CCGT_LIFE_YEARS - 1)

# NEW (Scenario 2 capex build-out): CCGT capital and fixed O&M cost, sourced directly from Lazard's
# LCOE+ v19.0 "Gas Combined Cycle" line (already in this project's knowledge base, not independently
# re-sourced) -- capital cost $1,450-$2,100/kW, fixed O&M $10.00-$25.50/kW-yr; midpoint used as the
# point estimate, consistent with how this project has generally handled other Lazard-sourced ranges.
# Lazard also flags a separate "illustrative high case" of $2,400-$2,600/kW for post-2028-COD CCGT
# projects reflecting current market tightness -- noted for context, not adopted as the base figure.
CCGT_CAPEX_KW = (1450.0 + 2100.0) / 2.0   # = $1,775/kW
CCGT_FOM_KW_YR = (10.00 + 25.50) / 2.0    # = $17.75/kW-yr

BUILD_YEAR = 2044.5  # midpoint of the 2-year build window, used for cost-curve lookup

def solar_capex(y):
    return 1474 * (1-0.015)**(y-2026)

def ccgt_capex_kw(y):
    """
    NEW (Scenario 2 CCGT capex, established per direct user request 2026-08-20). Full installed
    project cost ($/kW), NOT turbine-equipment-only cost -- an important scope distinction, since
    the two differ by roughly 4x in the sourced data and are easy to conflate.

    SOURCING, cross-verified across multiple independent outlets, not resting on one article:
    - Wood Mackenzie ("The U.S. gas turbine market: navigating manufacturing scarcity and demand
      growth," April 2026, reported by Bloomberg/Utility Dive/Power-Eng/APPA independently):
      turbine-EQUIPMENT-only cost reaching $600/kW by end-2027, a 195% increase since 2019. Wood
      Mackenzie's own report states turbines are "20-30% of project costs for combined cycle
      projects" -- converting the equipment figure to full-installed terms: $600/0.20 to $600/0.30
      = roughly $2,000-3,000/kW by 2027.
    - EPRI (via Utility Dive, March 2026): average FULL-PROJECT gas turbine prices rose from
      roughly $2,000/kW to $3,000/kW in just the prior six months (~Sept 2025 to ~March 2026) --
      the most recent, directly-stated full-project figure, and it already lands at the same level
      Wood Mackenzie's converted turbine-only projection reaches by 2027. Read together, this
      suggests the market may already be near its near-term plateau as of this project's own 2026
      baseline year, not still climbing toward a later peak.
    - GridLab/Energy Futures Group/Component Reliability Consultants/Halcyon (Sept 2025, via
      Latitude Media): pre-surge/near-term cost $1,116-1,427/kW, 2030-2031-vintage projects
      "routinely" $2,000/kW or more -- corroborates the same magnitude of increase, from a
      different, independent methodology.

    METHODOLOGY: flat $3,000/kW for all years, anchored to EPRI's most recent, directly-stated
    full-project figure. NOT extrapolated further upward or downward beyond this point --
    disclosed limitation, not an oversight. The Wood Mackenzie report explicitly diagnoses the
    current spike as a temporary manufacturing-capacity shortfall (110 GW of global orders against
    60-70 GW/yr of capacity), not a permanent structural cost driver, with OEMs (GE Vernova,
    Siemens Energy, Mitsubishi) actively expanding capacity -- there is no sourced basis in this
    project's research to assume either continued escalation or reversion once that capacity
    constraint eases, and this project's own checkpoints (earliest: 2030) all fall after Wood
    Mackenzie's own explicitly-described "supply crunch through 2027" window.
    """
    return 3000.0

def na_capex_kwh_6hr_ref(y):
    """RENAMED (was na_capex_kwh_4hr_ref -- mislabeled): per the Assumptions & Sources tab
    (row 33), the prior session deliberately settled on a 6-hour reference for sodium-ion as
    the best fit across a number of scenario runs, not 4-hour. The $97.50/kWh (2026) figure
    itself is unchanged; only its duration label was corrected."""
    return 97.50 * (43.40/97.50)**((y-2026)/24)

# ---- ASSUMPTION, flagged explicitly ----
# Power/energy cost decomposition for sodium-ion, derived from NREL's 2025 utility-scale
# lithium-ion bottom-up cost model (Cole, Ramasamy, Turan, "Cost Projections for Utility-Scale
# Battery Storage: 2025 Update," NREL/TP-6A40-93281, June 2025), Figure 2 regression:
#   Total System Cost ($/kW) = $240.8/kWh * Duration(hr) + $379.16/kW   (2024$, R^2=0.9999)
# No sodium-ion-specific power/energy cost breakdown is publicly documented at this level of
# detail, so as a reasonable proxy this applies NREL's lithium-ion PROPORTIONAL power/energy
# cost SHARE (not the absolute $ figures) to this model's own sodium-ion reference price. At
# the 6-hr reference (CORRECTED from an earlier, mislabeled 4-hr basis -- see na_capex_kwh_6hr_ref):
# energy share = (240.8*6)/(240.8*6+379.16) = 79.21%, power share = 20.79%.
# This is an assumption, not a sourced sodium-ion-specific figure -- flagged for review.
_NREL_ENERGY_SHARE_6HR = (240.8*6)/(240.8*6+379.16)   # 0.79210
_NREL_POWER_SHARE_6HR = 379.16/(240.8*6+379.16)       # 0.20790

def na_power_energy_split(y):
    """Returns (energy_$_per_kWh, power_$_per_kW), both duration-independent unit rates, derived
    by applying the NREL lithium-ion power/energy share (see note above) to this model's own
    sodium-ion 6-hr reference price at year y. CORRECTED from an earlier 4-hr-basis version --
    both the constants and this function's own math were updated together with the rename."""
    ref = na_capex_kwh_6hr_ref(y)
    energy_per_kwh = _NREL_ENERGY_SHARE_6HR * ref
    power_per_kw = _NREL_POWER_SHARE_6HR * 6.0 * ref
    return energy_per_kwh, power_per_kw

def fe_capex_kwh(y):
    return 52.50 * 0.25**((y-2026)/24)

SOLAR_CAPEX = solar_capex(BUILD_YEAR)          # $/kW-AC
NA_REF_KWH = na_capex_kwh_6hr_ref(BUILD_YEAR)  # $/kWh at 6-hr reference (corrected from 4-hr label)
# decompose 6-hr-reference $/kWh into power ($/kW) and energy ($/kWh) via na_power_energy_split(),
# replacing the earlier ad-hoc 25%/75% placeholder split with the NREL-share-derived figures.
NA_POWER_CAPEX, NA_ENERGY_CAPEX = na_power_energy_split(BUILD_YEAR)
FE_ENERGY_CAPEX = fe_capex_kwh(BUILD_YEAR)     # $/kWh (source already quotes at 100-hr duration)

SOLAR_OM = 24.0       # $/kW-yr -- NREL ATB 2022 base year, comprehensive scope (land lease, property tax, insurance, asset mgmt, security included per NREL's own 2021 ATB documentation); see Assumptions tab for full Lazard/LBNL/NREL reconciliation
STOR_FOM_PCT = 0.025  # %/yr of capex. Applies uniformly to Na-ion and iron-air (see c[ENA_]/c[EFE_]
                        # in build_problem()). For iron-air specifically, this is a STATED, DISCLOSED
                        # ASSUMPTION, not an independently-verified figure -- see the full rationale
                        # and citations at FE_CYCLE_LIFE below.

BATH_MW = 3000.0
BATH_MWH = 24000.0
BATH_RTE_CHARGE = 0.80
NA_RTE_CHARGE = 0.90
NA_CYCLE_LIFE = 15000  # default/fallback; driver.set_year_capex() overrides per checkpoint year
                        # (10,000 pre-2035, 15,000 2035+, per project direction 2026-08-16)
FE_CYCLE_LIFE = 1000   # Form Energy-specific published figure ("maintained over 80% capacity after
                        # more than 1,000 cycles"), held constant across all years -- no established
                        # improvement trajectory the way Na-ion has one. VERIFIED (2026-09-09,
                        # Master_Citations.xlsx C122): independently confirmed via a third-party
                        # comparative LDES technology review, not just Form Energy's own claim. Prior
                        # to this verification, this figure had no citation anywhere in this project's
                        # own record (checked Master_Citations.xlsx, Data_Sourcing_Log.md, Internal_
                        # Debugging_Log.md directly -- none referenced it). Historical context (C123,
                        # ARPA-E 2012 peer review): 1,000-2,000 cycles was already iron-air's state of
                        # the art over a decade ago, against a still-unmet 5,000-cycle field target
                        # (C121) -- this is Form Energy's real, demonstrated figure, not a target.
                        #
                        # STOR_FOM_PCT (2.5%/yr, defined above) applied to iron-air rests on a STATED
                        # ASSUMPTION, decided directly (2026-09-09): that this rate is adequate given
                        # electrode-level renewal, not full-hardware replacement, at this 1,000-cycle
                        # figure. Two things this assumption depends on, disclosed rather than silently
                        # bundled in:
                        #   1. General iron-air/metal-air patent literature supports designs where the
                        #      electrode(s) -- not the full cell housing/air-handling/power electronics
                        #      -- are the serviceable, periodically-renewed component (e.g. US 9,972,874,
                        #      an extractible/replaceable air electrode; a separate metal-air patent
                        #      describing an explicit two-tier strategy: electrode-only replacement
                        #      first, full cell-unit replacement only once degradation products have
                        #      accumulated too much for that alone). NOT CONFIRMED as Form Energy's own
                        #      specific product design -- their public materials (formenergy.com/about,
                        #      multiple project-announcement press releases, checked directly) do not
                        #      publish a calendar-life, renewal-cost, or serviceability figure. This is
                        #      a real, disclosed gap, not resolved by the general literature.
                        #   2. A 10,000-cycle figure (Fraunhofer ELuStat) was considered and explicitly
                        #      NOT used here -- it describes general iron ELECTRODE MATERIAL durability,
                        #      not Form Energy's own iron-AIR SYSTEM, and is 10x this project's own
                        #      FE_CYCLE_LIFE. Using it would have put two inconsistent cycle-life figures
                        #      for the same hardware into this project at once (one driving the cycling
                        #      cost below, a different one justifying this O&M rate) -- caught directly
                        #      rather than written in silently.
                        # If Form Energy's own serviceability model is ever found (an investor
                        # presentation, a utility RFP response, an actual teardown/service document),
                        # this assumption should be re-checked against it, not assumed settled.
FE_DOD = 1.0            # iron-air gets no DoD restriction -- see na_cycling_cost/fe_cycling_cost note
                        # in build_problem() for the sourcing behind this asymmetry
NA_DOD_FLOOR = 0.20     # sodium-ion: standard industry convention -- "80% DoD" means discharging FROM
                        # 100% down to a 20% floor, not to 0%. PROMOTED to module level (this session):
                        # previously defined only locally inside build_problem(), which meant
                        # build_dispatch_problem()'s own cycling-cost fix (added this session, Internal
                        # Debugging Log #30) had no access to it -- NameError caught directly when first
                        # tested, not silently worked around.
RESILIENCE_TILT_PCT = 0.03  # REINSTATED (2026-09-04): RBD trial (Internal Debugging Log #20.6)
                        # concluded, removing the reason this was held at 0.0. A deliberate, disclosed
                        # policy preference for long-duration storage (iron-air) within the near-cost-flat region
                        # confirmed this session between Na-ion and iron-air build sizes (forcing +5,000 MW
                        # Na cost only ~$5M/year net, against a ~$21B total -- genuine near-indifference,
                        # not a numerical artifact, confirmed via a 100,000x scaling improvement that
                        # changed nothing).
                        # Everything below documents the original 3% figure's own rationale, unchanged.
                        # land-use calculations, etc.). Rationale: iron-air's 100-hour duration provides
                        # genuine multi-day resilience Na-ion cannot structurally match, directly relevant
                        # given this project's own chronological-persistence methodology is built specifically
                        # to protect against sustained, multi-day events -- a criterion this project's own LP
                        # does not otherwise price, since it optimizes cost alone. A starting magnitude, not a
                        # researched figure -- sized to reliably break the tie within the confirmed-flat range
                        # without exceeding it. Explicitly does NOT apply to Na-ion's real grid-services/fast-
                        # response value (frequency regulation, etc.), which this project's LP also does not
                        # price and which argues in the opposite direction -- a disclosed, one-directional
                        # policy choice, not a claim that iron-air is unambiguously superior.
def iron_air_rte(year):
    """Linear round-trip-efficiency improvement: 45% (2026) -> 80% (2033), held flat after."""
    if year <= 2026:
        return 0.45
    if year >= 2033:
        return 0.80
    return 0.45 + (0.80-0.45)*(year-2026)/(2033-2026)

FE_RTE_CHARGE = iron_air_rte(2044.5)  # = 0.80: both 2044 and 2045 fall past the 2033 ramp
                                        # completion, so this dispatch window uses the flat
                                        # terminal 80% value, not an in-progress ramp value.
FE_DURATION = 100.0

SIMPLE_CYCLE_HEAT_RATE = 9.5  # MMBtu/MWh HHV, GE 7F.05 simple-cycle spec (8,580-8,610 Btu/kWh LHV,
                               # x1.108 LHV->HHV) -- Scenario 1/3/1B/3B/3C fleet, per standing
                               # simple-cycle-only convention
CCGT_HEAT_RATE = 6.4          # MMBtu/MWh HHV, GE 7F.05 combined-cycle spec (5,660 Btu/kWh LHV,
                               # x1.108) -- confirms the pre-existing constant is correct for
                               # Scenario 2, which is genuinely CCGT-based

def gas_cost_mwh(year, heat_rate=None):
    """
    CORRECTED (was: flat GAS_COST_MWH = 48.0 constant). Time-varying Deloitte-derived fuel
    cost, matching the same trajectory Scenario 2 uses -- confirmed via user instruction that
    all scenarios run gas through 2045, so gas price assumptions should apply consistently
    across all of them, not just Scenario 2. Piecewise-linear interpolation between Deloitte's
    own $/MMBtu data points ($3.70 2026, $5.40 2030, $6.35 2040, $7.50 2050 extrapolated -- see
    Assumptions tab).

    CORRECTED (2026-08-16, was a bug): heat_rate now defaults to None and must be supplied by
    the caller -- there is NO single correct default, since Scenario 2 is CCGT (CCGT_HEAT_RATE,
    6.4 MMBtu/MWh, confirmed against GE 7F.05 combined-cycle spec) while Scenario 1/3/1B/3B/3C
    are simple-cycle only per the standing convention (SIMPLE_CYCLE_HEAT_RATE, 9.5 MMBtu/MWh,
    confirmed against GE 7F.05 simple-cycle spec). The prior flat 6.4 default silently applied
    the CCGT rate to the simple-cycle-only scenarios too, understating their fuel cost by ~48%
    in every checkpoint solved before this fix (see Activity Tracker item 49; Citations C034).
    Does NOT include CCGT VOM ($3.00/MWh in Scenario 2) -- Scenario 1/3/1B/3B's gas dispatch has
    historically been priced as fuel-cost-only; add VOM separately if/when that convention changes.
    """
    if heat_rate is None:
        raise ValueError(
            "gas_cost_mwh() requires an explicit heat_rate -- pass SIMPLE_CYCLE_HEAT_RATE for "
            "Scenario 1/3/1B/3B/3C or CCGT_HEAT_RATE for Scenario 2. There is no safe default "
            "(see 2026-08-16 fix note in this function's docstring)."
        )
    mmbtu_points = {2026: 3.70, 2030: 5.40, 2040: 6.35, 2050: 7.50}
    years = sorted(mmbtu_points.keys())
    if year <= years[0]:
        mmbtu = mmbtu_points[years[0]]
    elif year >= years[-1]:
        mmbtu = mmbtu_points[years[-1]]
    else:
        for i in range(len(years)-1):
            y0, y1 = years[i], years[i+1]
            if y0 <= year <= y1:
                v0, v1 = mmbtu_points[y0], mmbtu_points[y1]
                mmbtu = v0 + (v1-v0)*(year-y0)/(y1-y0)
                break
    return mmbtu * heat_rate

def gas_cost_mwh_eia(year):
    """
    NEW (check 2, Scenario 2 Low case): EIA-derived fuel cost, the LOW gas price case, distinct
    from gas_cost_mwh()'s Deloitte/MEDIUM trajectory. Shares the same 2026 starting point ($3.70/
    MMBtu -- both cases start from the same current Henry Hub actual/forecast) but diverges
    afterward: EIA's own $/MMBtu data points are $3.80 (2030), $4.20 (2040), $4.95 (2050
    extrapolated) -- see Assumptions tab -- meaningfully lower than Deloitte's $5.40/$6.35/$7.50.
    Same piecewise-linear interpolation and 6.4 MMBtu/MWh heat rate as gas_cost_mwh(). Does NOT
    include CCGT VOM ($3.00/MWh) -- add separately, matching Scenario 2's established convention.
    """
    mmbtu_points = {2026: 3.70, 2030: 3.80, 2040: 4.20, 2050: 4.95}
    heat_rate = 6.4
    years = sorted(mmbtu_points.keys())
    if year <= years[0]:
        mmbtu = mmbtu_points[years[0]]
    elif year >= years[-1]:
        mmbtu = mmbtu_points[years[-1]]
    else:
        for i in range(len(years)-1):
            y0, y1 = years[i], years[i+1]
            if y0 <= year <= y1:
                v0, v1 = mmbtu_points[y0], mmbtu_points[y1]
                mmbtu = v0 + (v1-v0)*(year-y0)/(y1-y0)
                break
    return mmbtu * heat_rate

def gas_cost_mwh_hughes(year):
    """
    NEW (Scenario 2 High case): Hughes/Post Carbon Institute (2021, "Shale Reality Check")
    fuel cost, the HIGH gas price case -- distinct from both gas_cost_mwh() (Deloitte/MEDIUM)
    and gas_cost_mwh_eia() (EIA/LOW). Source narrative: Marcellus/Utica shale gas production
    peaks 2030-2033, then declines at a 3.2%/yr terminal rate, driving sustained price
    increases as the market tightens -- a genuinely different, depletion-driven thesis, not
    just a different number on the same curve shape as the other two cases.

    CAVEATED, LOAD-BEARING METHODOLOGY NOTE: only two data points are sourced directly from
    Hughes (2021) -- $3.50/MMBtu (2026) and $11.50/MMBtu (2050). This function interpolates
    between them using a CONSTANT COMPOUND ANNUAL GROWTH RATE (~5.08%), not linear
    interpolation -- chosen because compound growth produces the slower-early/faster-later
    shape qualitatively consistent with "escalates," without inventing a specific pre/post-
    2030-33-peak kink point, since no intermediate sourced data exists to credibly anchor
    that more detailed shape. This is a smooth mathematical fit through two real endpoints,
    NOT a year-by-year forecast, and does not attempt to model the source's own described
    peak-then-decline production curve.

    Also flagged elsewhere in this project (Reorganized_Appendices_Draft.md) as "the least
    current of the three [gas price cases], retained for range context" -- Hughes 2021
    predates the more recent EIA/Deloitte forecasts used for the other two cases. Does NOT
    include CCGT VOM ($3.00/MWh) -- add separately, matching Scenario 2's established
    convention.
    """
    start_mmbtu, start_year = 3.50, 2026
    end_mmbtu, end_year = 11.50, 2050
    cagr = (end_mmbtu/start_mmbtu)**(1.0/(end_year-start_year)) - 1
    heat_rate = 6.4
    if year <= start_year:
        mmbtu = start_mmbtu
    elif year >= end_year:
        mmbtu = end_mmbtu
    else:
        mmbtu = start_mmbtu * (1+cagr)**(year-start_year)
    return mmbtu * heat_rate

def gas_cost_mwh_bernstein(year, high_case=False):
    """
    NEW (Scenario 2, fourth reference case -- assessed alongside Deloitte/EIA/Hughes per direct
    user request, not yet adopted as this project's Base/Low/High tier structure). Bernstein
    Research's "Americas Natural Gas Outlook" -- most recently reaffirmed in their 2026 edition
    (Dec 2025): "we continue to have faith in five," i.e. $5.00/mcf Henry Hub as the new
    structural mid-cycle equilibrium, up from a prior decade averaging closer to $3.50/mcf.
    Cross-verified across multiple independent outlets (Hart Energy, Oil & Gas 360, Marcellus
    Drilling News, Seeking Alpha, Investing.com/Yahoo Finance, TradingNews, Capital.com), all
    reporting the same $5/mcf figure and the same underlying LNG-export/data-center-power-demand
    thesis -- not a single, unverified source.

    METHODOLOGICALLY DIFFERENT FROM THE OTHER THREE CASES, disclosed explicitly rather than
    smoothed over: Deloitte/EIA/Hughes all provide multi-decade, rising $/MMBtu trajectories with
    specific year-by-year (or CAGR-interpolated) points. Bernstein provides something different in
    character -- a single "new equilibrium" / "mid-cycle" price level, explicitly NOT framed as a
    year-by-year escalation path. This function therefore returns a FLAT rate for all years by
    default (high_case=False), not an invented trajectory shape Bernstein's own reporting does not
    support. Set high_case=True for Bernstein's own separately-flagged bullish-risk scenario
    ($8-10/mcf, "under more bullish assumptions, such as a shortfall in Haynesville growth") --
    also flat, for the same reason.

    UNIT CONVERSION, made explicit: Bernstein's figure is Henry Hub $/mcf (thousand cubic feet),
    not $/MMBtu like the other three cases. Converted using the standard EIA factor (1.037 MMBtu
    per mcf): $5.00/mcf = $4.82/MMBtu; the $8-10/mcf upside range = $7.71-$9.64/MMBtu.

    COMPARISON TO THE EXISTING THREE CASES, worth noting directly: Bernstein's flat $4.82/MMBtu
    sits BETWEEN Deloitte's 2026 starting point ($3.70) and its 2030 point ($5.40) -- i.e.
    Bernstein reads more bullish than Deloitte near-term, but because Bernstein stays flat while
    Deloitte keeps climbing, Bernstein reads LESS bullish than Deloitte by 2040 ($6.35) and 2050
    ($7.50). Bernstein's own upside case ($7.71-$9.64) lands close to, not meaningfully beyond,
    Hughes's existing long-run endpoint ($11.50 at 2050) -- so this does not obviously function as
    a new, more-extreme high case beyond what Hughes already provides; it is better understood as
    a different KIND of estimate (a mid-cycle equilibrium view) than a fourth point on the same
    Base/Low/High trajectory-style spectrum.

    CAVEAT ON SOURCE RELIABILITY, disclosed rather than assumed: analyst commodity-price views
    shift substantially over time -- the same Bernstein research team held an explicitly BEARISH
    $2.50/MMBtu view for 2018 gas prices as recently as 2017. This is a current (reaffirmed Dec
    2025), well-corroborated call, not an infallible one.

    Does NOT include CCGT VOM ($3.00/MWh) -- add separately, matching Scenario 2's established
    convention. Uses CCGT_HEAT_RATE (6.4 MMBtu/MWh) by default, matching gas_cost_mwh_eia() and
    gas_cost_mwh_hughes() -- pass a different heat_rate only if applying this to a non-CCGT context.
    """
    # Bernstein's own upside range is $8-10/mcf; use the range midpoint ($9.00) when high_case=True
    # rather than either single endpoint, since Bernstein itself gives a range, not a point estimate
    mcf = 9.00 if high_case else 5.00
    mmbtu = mcf / 1.037  # standard EIA mcf->MMBtu conversion factor
    heat_rate = 6.4
    return mmbtu * heat_rate

GAS_COST_MWH = gas_cost_mwh(2044.5, heat_rate=CCGT_HEAT_RATE)  # RETAINED for backward compatibility
                                       # with any code still referencing the flat constant directly --
                                       # uses CCGT_HEAT_RATE since this constant's original consumer
                                       # (pre-parameterization) was Scenario 2. New code should call
                                       # gas_cost_mwh(year, heat_rate=...) explicitly instead.
EXPORT_AVG_PRICE = 37.80  # CORRECTED (2026-08-16): code still had the intermediate $63.0 value, since
                           # rejected on review -- the Assumptions tab's own documented, final figure is
                           # $37.80/MWh ($45/MWh EIA avg LMP x 1.40 DOM-zone premium x 0.60 midday discount,
                           # retained after reconsideration). Code and Assumptions tab had drifted out of sync.
                           # (DOM has priced ~40% above PJM-RTO average every year 2021-2025, data-center-driven).
                           # This constant sets the PRICE LEVEL only. The hour-to-hour SHAPE is set separately
                           # below and is no longer a synthetic assumption -- see the documentation there.

# ============================================================================
# HOURLY PRICE SHAPE -- METHODOLOGY NOTE FOR FUTURE READERS
# ============================================================================
# This shape was originally a hand-specified synthetic sinusoidal curve (a single guessed evening-peak
# pattern). It has been REPLACED with an empirically-derived shape, for a specific, considered reason
# worth stating plainly: this LP models a 2044/2045 resource mix that does not exist today (100,000+ MW
# of new solar, ~150,000 MW of storage, minimal gas) -- so importing TODAY's real hourly LMP data (e.g.
# from the Loudoun/Tysons/Richmond nodes gathered during this project) as the price SHAPE would silently
# impose today's thermal-fleet-driven price pattern onto a grid whose own physics may not produce that
# pattern at all. The economically correct alternative, standard in production-cost/IRP modeling practice:
# derive the future price shape from the future system's OWN simulated dispatch, using the shadow price
# (dual value) on the hourly energy-balance constraint -- which, in a well-functioning market, is exactly
# what a locational marginal price represents by construction.
#
# DERIVATION: extracted from the Scenario 1B (95% clean/5% gas) solve specifically -- Scenario 1's harder
# 100%-clean constraint could not be solved with reliable duals despite several attempts (see project
# history); this is a known, disclosed limitation, not an oversight. Duals came from HiGHS's interior-point
# method with crossover disabled (the same configuration needed to get ANY solution on this problem size) --
# these are LESS precise than crossover-verified basic-solution duals, and a small number of extreme
# outliers (2.01% of hours) were winsorized at the 1st/99th percentile before use, similar in spirit to the
# near-zero-noise clipping applied to the underlying weather data elsewhere in this project.
#
# SEASONAL STRUCTURE: an initial annual-average shape looked almost perfectly flat and showed essentially
# zero correlation (0.07) against real LMP data's shape. Breaking this out by season revealed why: the
# annual average was MASKING real structure, not reflecting an absence of it -- winter is genuinely flat
# (narrow 0.94-1.04x range), but spring and summer show a pronounced, real shape (0.79-1.21x) that simply
# peaks at a different hour (11pm) than real data's summer peak (7pm) -- so averaging across seasons with
# different peak timing cancelled the pattern out. Seasonal shapes are used below specifically to avoid
# repeating that mistake.
#
# VALIDATION AGAINST REAL DATA (Loudoun/Tysons/Richmond nodes, Jan 2025-Aug 2026): winter shows a genuine,
# moderate positive correlation (0.58) with real data's shape -- both today's real grid and the modeled
# 2044/45 grid are fundamentally supply-scarcity-driven in winter, and that basic physics doesn't change
# much between now and then. Summer shows near-zero correlation (-0.05) -- today's real summer peak is an
# AC-driven, thermal-fleet-specific phenomenon tied to solar rolling off in early evening; a 2044 grid with
# massive storage plausibly does not reproduce that same narrow-window dynamic, since storage's entire
# economic function is to arbitrage exactly that kind of price differentiation away. This divergence is
# treated as a genuine, informative finding, not an error to be corrected -- it is direct evidence for why
# deriving the shape from the model's own future dispatch, rather than importing today's market data,
# was the right methodological choice for this project.
#
# EXPLICITLY NOT REPRESENTED in this derivation: Scenario 1's harder no-gas case (blocked, see above);
# any demand-side load-shifting/DSM effect (Scenario 1B has no such mechanism -- the shape reflects supply-
# side storage smoothing only, not demand flexibility); genuine forecast-uncertainty effects a real market
# participant would face (this is a perfect-foresight optimization).
import os
_shapes_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lp_derived_seasonal_shapes_PERMANENT.npz')
_seasonal_shapes = np.load(_shapes_path)
_SEASON_MONTHS = {'DJF': [12,1,2], 'MAM': [3,4,5], 'JJA': [6,7,8], 'SON': [9,10,11]}
def _month_to_season(m):
    for s, months in _SEASON_MONTHS.items():
        if m in months: return s
    raise ValueError(m)

def export_price_profile(T, start_hour_of_day=0, year_start=2044):
    """LP-derived, seasonally-varying price shape (see methodology note above). Assumes T-hour series
    starting Jan 1 of year_start, matching this project's standard 2044(leap)+2045 calendar convention."""
    dates = pd.date_range(f'{year_start}-01-01', periods=min(T, 8784 if year_start==2044 else 8760), freq='h')
    if T > len(dates):
        dates = dates.append(pd.date_range(f'{year_start+1}-01-01', periods=T-len(dates), freq='h'))
    mult = np.array([_seasonal_shapes[_month_to_season(m)][h] for m, h in zip(dates.month, dates.hour)])
    return EXPORT_AVG_PRICE * mult

EXPORT_CAP_MW = 5000.0  # finite transmission/interconnection export limit (assumption; see notes to user)

EXIST_SOLAR_MW_2026 = 5300.0
SOLAR_DEGRADATION_RATE_ANNUAL = 0.005  # standard c-Si industry figure (~0.5%/yr), already in use for
                        # exist_solar_mw() below; refactored into a named constant (2026-08-19) so the
                        # same rate can be reused for carrying prior-checkpoint new-build solar forward
                        # across multi-checkpoint solves (see solar_degradation_factor() and the
                        # prior_solar_mw parameter in lp_model.build_problem()), without duplicating the
                        # magic number in a second place.
def solar_degradation_factor(years_elapsed):
    """Multiplicative factor for solar nameplate capacity after years_elapsed years of degradation at
    the standard SOLAR_DEGRADATION_RATE_ANNUAL rate. Mathematically exact to apply to a combined,
    multi-vintage running total at each checkpoint transition (rather than tracking each vintage
    separately and summing): exponential decay is multiplicative, so (A*r^5+B)*r^5 == A*r^10+B*r^5."""
    return (1 - SOLAR_DEGRADATION_RATE_ANNUAL)**years_elapsed
def exist_solar_mw(year):
    return EXIST_SOLAR_MW_2026 * solar_degradation_factor(year-2026)

CVOW_MW = 2587.2  # CORRECTED (2026-08-16): was 2535.0 (SAM proxy-turbine-count figure, 169 x 15MW NREL
                   # ATB 2020 Reference turbines) -- real nameplate is 176 x 14.7 MW Siemens Gamesa SG
                   # 14-222 DD (Power Boost) turbines = 2,587.2 MW. This correction had previously only
                   # been applied to a separate, narrowly-scoped CVOW_MW_CORRECTED constant used just in
                   # driver.py's reserve-margin constraint -- never propagated to this module-level
                   # constant, which is what the main energy balance equation actually uses in every
                   # checkpoint solve. Caught while preparing the LP model reference document, when
                   # gathering constants directly from source surfaced the inconsistency. ~2.06% wind
                   # generation understatement in every checkpoint solved before this fix.

print(f"SOLAR_CAPEX(${BUILD_YEAR})=${SOLAR_CAPEX:.1f}/kW  CRF={CRF:.5f}")
print(f"NA power capex=${NA_POWER_CAPEX:.2f}/kW  NA energy capex=${NA_ENERGY_CAPEX:.2f}/kWh")
print(f"FE energy capex=${FE_ENERGY_CAPEX:.2f}/kWh")
print(f"Exist solar 2044 MW={exist_solar_mw(2044):.1f}  2045 MW={exist_solar_mw(2045):.1f}")


def make_hv(hv_params):
    NVAR_BUILD, NVAR_PER_HOUR = hv_params
    def hv(t, k):
        return NVAR_BUILD + t*NVAR_PER_HOUR + k
    return hv


UNSERVED_PENALTY = 100000.0  # $/MWh, matching literature convention (e.g. "Preparing for the worst," 2025)
                              # for resource-adequacy dispatch-only feasibility testing -- large enough that
                              # the optimizer always prefers using every available (even capped) resource
                              # before shedding load, but finite, so the LP always remains solvable rather
                              # than infeasible when a fixed design genuinely cannot meet a test year's demand.

def build_dispatch_problem(solar_cf, wind_cf, nuclear, exist_solar, demand, gas_allowed_frac,
                            S_mw, PNA_mw, ENA_mwh, EFE_mwh, init_soc_frac=0.5, verbose=True,
                            gas_price_mwh=None, include_export=False):
    """
    Phase 2: dispatch-only cross-test. Build sizes (S_mw, PNA_mw, ENA_mwh, EFE_mwh) are FIXED constants
    from a prior Phase 1 solve (a different weather year), not decision variables. Tests whether that
    fixed design can serve THIS weather/demand series, adding an unserved-energy slack (at UNSERVED_PENALTY)
    so genuine infeasibility shows up as a quantified gap rather than an unsolvable LP.
    No BUILD_SCALE needed -- no build variables exist in this formulation, so the numerical-conditioning
    issue that motivated BUILD_SCALE in build_problem() does not arise here.

    CORRECTED (2026-08-20): include_export now defaults to False and actually gates the export
    variable's bounds and objective revenue term (previously always active regardless of caller
    intent -- this function's original purpose was export-potential analysis specifically, so export
    was unconditionally included). This silently violated this project's established, project-wide
    convention of keeping export strictly post-hoc (Appendix A.6/A.9) for every OTHER caller of this
    function -- the 12 intermediate-year dispatch-only solves (Activity Tracker item 57) and the
    2026-2029 extension both called this function assuming export was excluded, when it was not.
    Caught when the 2026 dispatch-only solve showed gas dispatch exceeding total demand by exactly
    EXPORT_CAP_MW at its worst hour -- confirmed directly by extracting the 'e' variable, nonzero for
    8,756 of 8,760 hours, totaling 41.9 million MWh against 2026's 95.8 million MWh of total demand.
    See Activity Tracker item 64 and Appendix A.20 for the full correction and re-run.
    """
    T = len(demand)
    NVAR_PER_HOUR = 14  # g, e, bc, bd, bsoc, nc, nd, nsoc, fc, fd, fsoc, gascum, unserved, curt
    NVAR = NVAR_PER_HOUR*T

    def hv(t, k):
        return t*NVAR_PER_HOUR + k
    IDX = dict(g=0, e=1, bc=2, bd=3, bsoc=4, nc=5, nd=6, nsoc=7, fc=8, fd=9, fsoc=10, gascum=11, unserved=12, curt=13)

    residual = demand - nuclear - exist_solar - CVOW_MW*wind_cf - solar_cf*S_mw

    eq_rows, eq_cols, eq_data, eq_rhs = [], [], [], []
    row = 0

    # (A) energy balance, one row per hour -- unserved (shortfall) and curt (excess-generation outlet)
    for t in range(T):
        eq_rows += [row]*8
        eq_cols += [hv(t,IDX['g']), hv(t,IDX['e']), hv(t,IDX['bd']), hv(t,IDX['bc']),
                    hv(t,IDX['nd']), hv(t,IDX['nc']), hv(t,IDX['fd']), hv(t,IDX['fc'])]
        eq_data += [1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0]
        eq_rows += [row, row]; eq_cols += [hv(t,IDX['unserved']), hv(t,IDX['curt'])]; eq_data += [1.0, -1.0]
        eq_rhs.append(residual[t])
        row += 1

    # (B) Bath SoC dynamics -- unchanged, Bath's power/energy were always constants
    init_bath = init_soc_frac*BATH_MWH
    for t in range(T):
        if t == 0:
            eq_rows += [row, row]; eq_cols += [hv(t,IDX['bsoc']), hv(t,IDX['bc'])]; eq_data += [1.0, -BATH_RTE_CHARGE]
            eq_rows += [row]; eq_cols += [hv(t,IDX['bd'])]; eq_data += [1.0]
            eq_rhs.append(init_bath)
        else:
            eq_rows += [row, row, row, row]
            eq_cols += [hv(t,IDX['bsoc']), hv(t-1,IDX['bsoc']), hv(t,IDX['bc']), hv(t,IDX['bd'])]
            eq_data += [1.0, -1.0, -BATH_RTE_CHARGE, 1.0]
            eq_rhs.append(0.0)
        row += 1
    eq_rows += [row]; eq_cols += [hv(T-1, IDX['bsoc'])]; eq_data += [1.0]; eq_rhs.append(init_bath); row += 1

    # (C) Sodium SoC dynamics -- init/end tied to FIXED ENA_mwh (a constant now, not a variable)
    init_na = init_soc_frac*ENA_mwh
    for t in range(T):
        if t == 0:
            eq_rows += [row, row, row]
            eq_cols += [hv(t,IDX['nsoc']), hv(t,IDX['nc']), hv(t,IDX['nd'])]
            eq_data += [1.0, -NA_RTE_CHARGE, 1.0]
            eq_rhs.append(init_na)
        else:
            eq_rows += [row]*4
            eq_cols += [hv(t,IDX['nsoc']), hv(t-1,IDX['nsoc']), hv(t,IDX['nc']), hv(t,IDX['nd'])]
            eq_data += [1.0, -1.0, -NA_RTE_CHARGE, 1.0]
            eq_rhs.append(0.0)
        row += 1
    eq_rows += [row]; eq_cols += [hv(T-1,IDX['nsoc'])]; eq_data += [1.0]; eq_rhs.append(init_na); row += 1

    # (D) Iron-air SoC dynamics -- same treatment
    init_fe = init_soc_frac*EFE_mwh
    for t in range(T):
        if t == 0:
            eq_rows += [row, row, row]
            eq_cols += [hv(t,IDX['fsoc']), hv(t,IDX['fc']), hv(t,IDX['fd'])]
            eq_data += [1.0, -FE_RTE_CHARGE, 1.0]
            eq_rhs.append(init_fe)
        else:
            eq_rows += [row]*4
            eq_cols += [hv(t,IDX['fsoc']), hv(t-1,IDX['fsoc']), hv(t,IDX['fc']), hv(t,IDX['fd'])]
            eq_data += [1.0, -1.0, -FE_RTE_CHARGE, 1.0]
            eq_rhs.append(0.0)
        row += 1
    eq_rows += [row]; eq_cols += [hv(T-1,IDX['fsoc'])]; eq_data += [1.0]; eq_rhs.append(init_fe); row += 1

    # (E) Cumulative gas tracking, GWh
    for t in range(T):
        if t == 0:
            eq_rows += [row, row]; eq_cols += [hv(t,IDX['gascum']), hv(t,IDX['g'])]; eq_data += [1.0, -0.001]
        else:
            eq_rows += [row, row, row]
            eq_cols += [hv(t,IDX['gascum']), hv(t-1,IDX['gascum']), hv(t,IDX['g'])]
            eq_data += [1.0, -1.0, -0.001]
        eq_rhs.append(0.0)
        row += 1

    n_eq_rows = row
    A_eq = sparse.csr_matrix((eq_data, (eq_rows, eq_cols)), shape=(n_eq_rows, NVAR))
    b_eq = np.array(eq_rhs)

    # ---------------- Inequality constraints (only the gas cap; power/energy limits are now simple bounds) ----------------
    ub_rows, ub_cols, ub_data, ub_rhs = [], [], [], []
    row = 0
    if gas_allowed_frac is not None:
        k = gas_allowed_frac/(1-gas_allowed_frac)
        clean_sum_const = np.sum(nuclear + exist_solar + CVOW_MW*wind_cf + solar_cf*S_mw)
        ub_rows += [row]; ub_cols += [hv(T-1,IDX['gascum'])]; ub_data += [1.0]
        ub_rhs.append(k*clean_sum_const/1000.0)
        row += 1
    n_ub_rows = row
    A_ub = sparse.csr_matrix((ub_data, (ub_rows, ub_cols)), shape=(n_ub_rows, NVAR)) if n_ub_rows > 0 else sparse.csr_matrix((0, NVAR))
    b_ub = np.array(ub_rhs)

    # ---------------- Bounds ----------------
    bounds = [(0, None)]*NVAR
    for t in range(T):
        bounds[hv(t,IDX['e'])] = (0, EXPORT_CAP_MW) if include_export else (0, 0)
        bounds[hv(t,IDX['bc'])] = (0, BATH_MW)
        bounds[hv(t,IDX['bd'])] = (0, BATH_MW)
        bounds[hv(t,IDX['bsoc'])] = (0, BATH_MWH)
        bounds[hv(t,IDX['nc'])] = (0, PNA_mw)
        bounds[hv(t,IDX['nd'])] = (0, PNA_mw)
        bounds[hv(t,IDX['nsoc'])] = (0, ENA_mwh)
        bounds[hv(t,IDX['fc'])] = (0, EFE_mwh/FE_DURATION)
        bounds[hv(t,IDX['fd'])] = (0, EFE_mwh/FE_DURATION)
        bounds[hv(t,IDX['fsoc'])] = (0, EFE_mwh)
        if gas_allowed_frac is None:
            bounds[hv(t,IDX['g'])] = (0, 0)

    # ---------------- Objective: gas cost + unserved penalty - export revenue (no capex -- build is fixed) ----------------
    c = np.zeros(NVAR)
    price = export_price_profile(T)
    _gas_price = GAS_COST_MWH if gas_price_mwh is None else gas_price_mwh
    # ADDED (this session, Internal Debugging Log #30): this function had NEITHER of build_problem()'s
    # two simultaneous-charge/discharge protections (discharge-side cycling costs, added 2026-08-16; the
    # SLCR RPS-splice, confirmed still necessary this session -- see driver.apply_slcr_constraint()).
    # Confirmed directly, not assumed: a 2041 dispatch-only test with a realistic fixed build (2040's own
    # checkpoint values) showed 1,717 hours of simultaneous Na-ion dispatch and 952 hours of simultaneous
    # iron-air dispatch, at magnitudes near full built capacity in both directions at once (e.g. charging
    # 23,679 MW while discharging 21,311 MW at the same hour) -- this was not a hypothetical risk. Same
    # formula as build_problem()'s own cycling costs, applied here identically.
    na_cycling_cost = (NA_ENERGY_CAPEX*1000) / (NA_CYCLE_LIFE * (1.0 - NA_DOD_FLOOR))
    fe_cycling_cost = (FE_ENERGY_CAPEX*1000) / (FE_CYCLE_LIFE * FE_DOD)
    for t in range(T):
        c[hv(t,IDX['g'])] = _gas_price
        if include_export:
            c[hv(t,IDX['e'])] = -price[t]
        c[hv(t,IDX['unserved'])] = UNSERVED_PENALTY
        c[hv(t,IDX['nd'])] = na_cycling_cost
        c[hv(t,IDX['fd'])] = fe_cycling_cost
        c[hv(t,IDX['curt'])] = 100.0  # matches build_problem()'s own corrected default (was 0.01)

    if verbose:
        print(f"Dispatch-only (Phase 2) problem: T={T} NVAR={NVAR} n_eq={n_eq_rows} n_ub={n_ub_rows}")
        print(f"Fixed build: S={S_mw:.0f}MW PNA={PNA_mw:.0f}MW ENA={ENA_mwh:.0f}MWh EFE={EFE_mwh:.0f}MWh")

    return dict(c=c, A_eq=A_eq, b_eq=b_eq, A_ub=A_ub, b_ub=b_ub, bounds=bounds,
                IDX=IDX, hv_params=(0, NVAR_PER_HOUR), T=T,
                fixed_build=(S_mw, PNA_mw, ENA_mwh, EFE_mwh))


def make_hv_dispatch():
    return make_hv((0, 14))


def build_scenario2_problem(solar_cf, wind_cf, nuclear, exist_solar, demand,
                              vcea_solar_mw, ccgt_mw, na_power_mw, na_duration_hr,
                              fe_power_mw, fe_duration_hr, gas_price_mwh, ccgt_vom_mwh,
                              init_soc_frac=0.5, verbose=True):
    """
    Scenario 2: dispatch-only, all capacities FIXED (no build variables, no RPS gas-percentage cap).
    Gas capped only by CCGT's hard MW nameplate. VCEA solar/wind target treated as solar-equivalent
    (per model convention), added alongside real CVOW offshore wind. Storage MWh derived from
    fixed MW x assumed duration (sodium: 4-hr assumed: see checkpoint note; iron-air: 100-hr,
    consistent with Scenarios 1/3 throughout this project). gas_price_mwh is the year-specific
    Deloitte-derived fuel cost; ccgt_vom_mwh is added on top for total per-MWh gas dispatch cost.
    Retains the unserved-energy slack as a verification check, not a sizing mechanism -- CCGT was
    sized externally to cover the worst hour with zero storage credit, so unserved should be ~0;
    a nonzero result here would be a real, reportable finding, not expected behavior.
    """
    T = len(demand)
    NVAR_PER_HOUR = 14
    NVAR = NVAR_PER_HOUR*T

    def hv(t, k):
        return t*NVAR_PER_HOUR + k
    IDX = dict(g=0, e=1, bc=2, bd=3, bsoc=4, nc=5, nd=6, nsoc=7, fc=8, fd=9, fsoc=10, gascum=11, unserved=12, curt=13)

    ENA_mwh = na_power_mw * na_duration_hr
    EFE_mwh = fe_power_mw * fe_duration_hr

    residual = demand - nuclear - exist_solar - CVOW_MW*wind_cf - solar_cf*vcea_solar_mw

    eq_rows, eq_cols, eq_data, eq_rhs = [], [], [], []
    row = 0
    for t in range(T):
        eq_rows += [row]*8
        eq_cols += [hv(t,IDX['g']), hv(t,IDX['e']), hv(t,IDX['bd']), hv(t,IDX['bc']),
                    hv(t,IDX['nd']), hv(t,IDX['nc']), hv(t,IDX['fd']), hv(t,IDX['fc'])]
        eq_data += [1.0, -1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0]
        eq_rows += [row, row]; eq_cols += [hv(t,IDX['unserved']), hv(t,IDX['curt'])]; eq_data += [1.0, -1.0]
        eq_rhs.append(residual[t])
        row += 1

    init_bath = init_soc_frac*BATH_MWH
    for t in range(T):
        if t == 0:
            eq_rows += [row, row]; eq_cols += [hv(t,IDX['bsoc']), hv(t,IDX['bc'])]; eq_data += [1.0, -BATH_RTE_CHARGE]
            eq_rows += [row]; eq_cols += [hv(t,IDX['bd'])]; eq_data += [1.0]
            eq_rhs.append(init_bath)
        else:
            eq_rows += [row, row, row, row]
            eq_cols += [hv(t,IDX['bsoc']), hv(t-1,IDX['bsoc']), hv(t,IDX['bc']), hv(t,IDX['bd'])]
            eq_data += [1.0, -1.0, -BATH_RTE_CHARGE, 1.0]
            eq_rhs.append(0.0)
        row += 1
    # CHANGED (this session, Internal Debugging Log #40, per direct user proposal): final-SoC
    # requirement relaxed from an EXACT equality (bsoc[T-1] == init_bath) to an inequality floor
    # (bsoc[T-1] >= init_bath). Addresses the root cause the literature search identified, not just
    # the symptom: an equality constraint can force the LP to actively dispose of energy it would
    # otherwise want to keep, and simultaneous charge/discharge (burning energy via round-trip
    # efficiency loss) is the only way to reduce SoC without touching the instantaneous energy
    # balance -- "if theta_t < 0]... the storage should not sell energy when price is negative" /
    # "we have an intention to store as less energy as possible" (both sources found this session).
    # A floor still guarantees the year doesn't end depleted relative to where it started (the
    # property this project's convention actually needs), without ever requiring the LP to burn
    # off a surplus it would rather keep. Applied to all three storage types below for consistency,
    # not just Na (where the problem was found) -- moved from eq_* to the ub_* lists (added below,
    # after this section) as -x <= -floor, since scipy's A_ub convention is <=.

    init_na = init_soc_frac*ENA_mwh
    for t in range(T):
        if t == 0:
            eq_rows += [row, row, row]
            eq_cols += [hv(t,IDX['nsoc']), hv(t,IDX['nc']), hv(t,IDX['nd'])]
            eq_data += [1.0, -NA_RTE_CHARGE, 1.0]
            eq_rhs.append(init_na)
        else:
            eq_rows += [row]*4
            eq_cols += [hv(t,IDX['nsoc']), hv(t-1,IDX['nsoc']), hv(t,IDX['nc']), hv(t,IDX['nd'])]
            eq_data += [1.0, -1.0, -NA_RTE_CHARGE, 1.0]
            eq_rhs.append(0.0)
        row += 1

    init_fe = init_soc_frac*EFE_mwh
    for t in range(T):
        if t == 0:
            eq_rows += [row, row, row]
            eq_cols += [hv(t,IDX['fsoc']), hv(t,IDX['fc']), hv(t,IDX['fd'])]
            eq_data += [1.0, -FE_RTE_CHARGE, 1.0]
            eq_rhs.append(init_fe)
        else:
            eq_rows += [row]*4
            eq_cols += [hv(t,IDX['fsoc']), hv(t-1,IDX['fsoc']), hv(t,IDX['fc']), hv(t,IDX['fd'])]
            eq_data += [1.0, -1.0, -FE_RTE_CHARGE, 1.0]
            eq_rhs.append(0.0)
        row += 1

    # No cumulative gas tracking needed -- Scenario 2 has no percentage cap, just an hourly MW bound
    n_eq_rows = row
    A_eq = sparse.csr_matrix((eq_data, (eq_rows, eq_cols)), shape=(n_eq_rows, NVAR))
    b_eq = np.array(eq_rhs)

    A_ub = sparse.csr_matrix((0, NVAR))
    b_ub = np.array([])

    bounds = [(0, None)]*NVAR
    for t in range(T):
        bounds[hv(t,IDX['g'])] = (0, ccgt_mw)  # hard MW ceiling, no percentage mechanism
        bounds[hv(t,IDX['e'])] = (0, 0)  # NO EXPORT in Scenario 2 -- CCGT exists to serve Dominion's own LSE
                                           # demand, not to operate as a merchant exporter; export revenue
                                           # in an earlier version of this solve was gas run purely for
                                           # arbitrage, not a byproduct of serving load. Corrected per direct
                                           # instruction.
        bounds[hv(t,IDX['bc'])] = (0, BATH_MW)
        bounds[hv(t,IDX['bd'])] = (0, BATH_MW)
        bounds[hv(t,IDX['bsoc'])] = (0, BATH_MWH)
        bounds[hv(t,IDX['nc'])] = (0, na_power_mw)
        bounds[hv(t,IDX['nd'])] = (0, na_power_mw)
        bounds[hv(t,IDX['nsoc'])] = (0, ENA_mwh)
        bounds[hv(t,IDX['fc'])] = (0, fe_power_mw)
        bounds[hv(t,IDX['fd'])] = (0, fe_power_mw)
        bounds[hv(t,IDX['fsoc'])] = (0, EFE_mwh)

    # ADDED (this session, Internal Debugging Log #40, extended after 2035's own Na-dispatch
    # finding): build_problem()'s own established pattern -- and its own documented history --
    # shows the hard combined constraint is the reliable mechanism here, not the cycling-cost
    # penalty alone: "simultaneous charge/discharge reappeared at large scale (60.4% of hours for
    # Na, 3.5% for Bath) with cycling costs alone." This function had neither the Bath constraint
    # nor the same for Na/iron-air. Found directly, not assumed: 2035's own solve showed 17 hours
    # of simultaneous Na dispatch even with the cycling-cost penalty already in place. Added the
    # same combined constraints build_problem() already uses for Na/Fe/Bath -- fixed capacities
    # here (Scenario 2's own build is statutory, not LP-chosen), so each RHS is simply
    # na_power_mw/fe_power_mw/BATH_MW rather than a build variable.
    ub_rows, ub_cols, ub_data, ub_rhs = [], [], [], []
    row = 0
    for t in range(T):
        ub_rows += [row, row]; ub_cols += [hv(t,IDX['bc']), hv(t,IDX['bd'])]; ub_data += [1.0, 1.0]
        ub_rhs.append(BATH_MW); row += 1
        ub_rows += [row, row]; ub_cols += [hv(t,IDX['nc']), hv(t,IDX['nd'])]; ub_data += [1.0, 1.0]
        ub_rhs.append(na_power_mw); row += 1
        ub_rows += [row, row]; ub_cols += [hv(t,IDX['fc']), hv(t,IDX['fd'])]; ub_data += [1.0, 1.0]
        ub_rhs.append(fe_power_mw); row += 1
    # Final-SoC floors (-x <= -floor, i.e. x >= floor), per the comment above where the equality
    # constraints were removed.
    ub_rows += [row]; ub_cols += [hv(T-1, IDX['bsoc'])]; ub_data += [-1.0]; ub_rhs.append(-init_bath); row += 1
    ub_rows += [row]; ub_cols += [hv(T-1, IDX['nsoc'])]; ub_data += [-1.0]; ub_rhs.append(-init_na); row += 1
    ub_rows += [row]; ub_cols += [hv(T-1, IDX['fsoc'])]; ub_data += [-1.0]; ub_rhs.append(-init_fe); row += 1
    A_ub = sparse.csr_matrix((ub_data, (ub_rows, ub_cols)), shape=(row, NVAR))
    b_ub = np.array(ub_rhs)

    c = np.zeros(NVAR)
    price = export_price_profile(T)
    # ADDED (this session, Internal Debugging Log #38): this function had neither of
    # build_problem()'s two simultaneous-charge/discharge protections either -- same gap found and
    # fixed in build_dispatch_problem() (#31). No RPS row exists here at all ("no cumulative gas
    # tracking needed... no percentage cap" -- see this function's own docstring), so the SLCR
    # splice genuinely does not apply -- but the cycling-cost mechanism is independent of any RPS
    # row and applies here the same as everywhere else. Confirmed necessary before assuming so --
    # see Internal Debugging Log #38 for the direct test this was based on.
    na_cycling_cost = (NA_ENERGY_CAPEX*1000) / (NA_CYCLE_LIFE * (1.0 - NA_DOD_FLOOR))
    fe_cycling_cost = (FE_ENERGY_CAPEX*1000) / (FE_CYCLE_LIFE * FE_DOD)
    for t in range(T):
        c[hv(t,IDX['g'])] = gas_price_mwh + ccgt_vom_mwh
        c[hv(t,IDX['e'])] = -price[t]
        c[hv(t,IDX['unserved'])] = UNSERVED_PENALTY
        c[hv(t,IDX['nd'])] = 100.0  # RAISED (below), was na_cycling_cost
        c[hv(t,IDX['fd'])] = fe_cycling_cost
        # ADDED (this session, Internal Debugging Log #40): the hard bc+bd<=BATH_MW constraint
        # (added above) alone did not suffice for Scenario 2's own problem structure -- confirmed
        # directly, not assumed: simultaneous Bath dispatch persisted after adding it (2026: 5
        # hours). Scenario 1's own checkpoints were checked directly too, and are genuinely clean
        # (zero simultaneous hours across all four) -- the combination of protections already in
        # build_problem() (SLCR splice, Na/FE cycling costs, corrected curtailment cost) apparently
        # already makes simultaneous Bath dispatch unattractive there, without needing a dedicated
        # Bath cost term. Scenario 2 lacks all of those, so needs its own. No sourced capex/cycle-
        # life figure exists for Bath (existing infrastructure, not a new-build decision), so this
        # is a disclosed, nominal token -- not a claimed "true" cycling cost -- sized similarly to
        # Na's own rate (~$5-6/MWh) purely to break the degeneracy, not to represent real economics.
        c[hv(t,IDX['bd'])] = 100.0
        # RAISED (this session, same entry, following the SoC-floor relaxation and direct KKT/
        # reduced-cost check): the SoC-floor relaxation (final SoC >= 50% rather than == 50%)
        # did NOT resolve Na's own simultaneous dispatch -- the LP still chose to land exactly on
        # the new floor (confirmed directly: final nsoc == floor, not above it), showing the root
        # motivation isn't specifically the end-of-year boundary condition. Checked via direct
        # KKT/reduced-cost verification instead (same methodology as this project's own earlier,
        # established degeneracy finding): both nc[295] and nd[295] showed exactly zero reduced
        # cost at interior values -- genuine LP degeneracy, objective provably unaffected either
        # way. Raised to Bath's own value ($100/MWh), a tie-break toward the physically sensible
        # solution among equally-optimal ones, not a distortion of anything real, per direct user
        # decision for consistency with Bath's own fix.
        c[hv(t,IDX['curt'])] = 100.0  # matches build_problem()'s own corrected default (was 0.01)

    if verbose:
        print(f"Scenario2 dispatch problem: T={T} NVAR={NVAR} n_eq={n_eq_rows}")
        print(f"Fixed: VCEA_solar={vcea_solar_mw:.0f}MW CCGT={ccgt_mw:.0f}MW Na={na_power_mw:.0f}MW/{ENA_mwh:.0f}MWh FE={fe_power_mw:.0f}MW/{EFE_mwh:.0f}MWh")
        print(f"Gas price: ${gas_price_mwh:.2f}/MWh fuel + ${ccgt_vom_mwh:.2f}/MWh VOM = ${gas_price_mwh+ccgt_vom_mwh:.2f}/MWh total")

    return dict(c=c, A_eq=A_eq, b_eq=b_eq, A_ub=A_ub, b_ub=b_ub, bounds=bounds,
                IDX=IDX, hv_params=(0, NVAR_PER_HOUR), T=T,
                fixed_build=(vcea_solar_mw, na_power_mw, ENA_mwh, fe_power_mw, EFE_mwh, ccgt_mw))



def build_problem(solar_cf, wind_cf, nuclear, exist_solar, demand, gas_allowed_frac,
                   init_soc_frac=0.5, verbose=True, gas_price_mwh=None, include_export=False,
                   export_price_mwh=37.80,
                   prior_solar_mw=0.0, prior_na_power_mw=0.0, prior_na_energy_mwh=0.0,
                   prior_ironair_energy_mwh=0.0,
                   enable_distributed_segment=False, distributed_solar_cf=None,
                   distributed_share_of_total_solar=0.20, distributed_exogenous_price_mwh=None,
                   prior_distributed_solar_mw=0.0, prior_distributed_na_power_mw=0.0,
                   prior_distributed_na_energy_mwh=0.0, prior_distributed_ironair_energy_mwh=0.0,
                   pin_build_mw=None, enforce_closing_soc=True):
    """
    solar_cf, wind_cf, nuclear, exist_solar, demand: arrays length T (already concatenated for both years if needed)

    DISTRIBUTED SEGMENT (Scenario 3 co-optimization, added 2026-09-09, per direct user decision to
    replace the prior post-hoc compute_distributed_shares() approach -- see checkpoint_solver.py's
    Scenario3Solver for the caller-side change). enable_distributed_segment=False (default) reproduces
    this function's pre-existing behavior EXACTLY -- the eight new decision variables this adds are
    still present in the variable array (fixed array size, simpler than conditional sizing) but pinned
    to bounds (0, 0), contributing nothing, mirroring the existing include_export pattern. Every
    existing Scenario 1/1B/2 call site is unaffected without needing to pass anything new.

    When enabled:
      - distributed_solar_cf (required): the REAL, unblended distributed capacity-factor array (rooftop/
        canopy tilt-based, not the deprecated 0.81-ratio blend). Distinct from solar_cf, which remains
        utility-scale-only in this function from here on.
      - distributed_share_of_total_solar (default 0.20): POLICY-FIXED share, enforced as a hard equality
        constraint (DISTRIBUTED_SOLAR_MW = share/(1-share) * UTILITY_SOLAR_MW), not a free decision the
        LP can grow. This is the specific thing that keeps the export-revenue build-distortion risk from
        reapplying here (see the design discussion this addition follows) -- if this constraint is ever
        relaxed to let distributed solar float freely, that risk reopens and needs re-examining.
      - distributed_exogenous_price_mwh (required): per-hour $/MWh array the distributed segment's own
        storage dispatch responds to -- discharge earns it as revenue, charge costs it as a real
        opportunity cost (SYMMETRIC pricing; see the objective-section comment below for why an earlier,
        discharge-only version was found unbounded via direct testing and corrected). Raw distributed
        generation itself still carries NO price term of its own -- it enters the energy balance exactly
        like exist_solar, cost- and revenue-free. This remains a deliberate, disclosed choice: crediting
        raw generation too would make DISTRIBUTED_SOLAR_MW's own build size responsive to price,
        reopening the build-distortion risk the fixed-share constraint above exists to prevent. Only
        storage dispatch (not distributed solar's own build size) responds to price.
      - prior_distributed_* (all default 0.0): same MULTI-CHECKPOINT CONTINUITY floor-bound mechanism as
        the existing prior_na_power_mw etc., extended to the new distributed storage build variables.
        Applies to Na-ion and iron-air identically -- see the vintage/calendar-life discussion this
        follows for why iron-air's own floor-forever assumption carries a real, still-open, disclosed
        uncertainty (Master_Citations.xlsx C121) that Na-ion's does not (C119/C120).
      - Rooftop-WMA and canopy-WMA share this ONE distributed pool (direct user decision, to avoid an
        overly complex LP) -- not modeled as separate pools. Residential NEM (Scenario 3) has no storage
        at all (direct user decision) and is NOT part of this mechanism -- it continues to enter via
        residential_nem_contribution() exactly as before, added into exist_solar-equivalent treatment by
        the caller, not touched by this function.
      - Both Na-ion and iron-air are offered as real, independent distributed build variables -- not
        forced to one chemistry -- so the LP can discover the mix itself (per direct user agreement that
        a blended/forced-single-chemistry treatment can't find the right NA/FE balance).

    gas_allowed_frac: None -> no gas at all (Scenario 1). Or e.g. 0.05 -> gas <= frac/(1-frac) * clean_gen (Scenario 1B)
    gas_price_mwh: CORRECTED (new parameter, was always the flat GAS_COST_MWH module constant). Pass the
    checkpoint-specific value from gas_cost_mwh(year) so each checkpoint solve uses the correct, time-varying
    Deloitte-derived price rather than a single fixed value regardless of which year is being solved. Defaults
    to the GAS_COST_MWH module constant (a fixed 2044.5 snapshot) ONLY for backward compatibility with any
    existing calls not yet updated -- new/re-solved code should always pass this explicitly.
    EXPORT REMOVED ENTIRELY (user decision): the LP no longer has an export variable or export-price signal
    at all -- it has no way to over-generate gas purely to sell it (the arbitrage problem identified when a
    real export-price spread existed alongside cheap gas). Any generation surplus the LP can't otherwise use
    (e.g. midday solar peaks) flows into curtailment, a real variable (IDX['curt']) at a near-zero 0.01 $/MWh
    penalty -- just enough to avoid solver indifference, not a meaningful cost signal. Use build_problem's
    returned curtailment values afterward to separately, post-hoc compute what COULD have been captured via
    export (min(curt[t], EXPORT_CAP_MW) valued at export_price_profile), without letting that potential
    revenue distort the LP's own dispatch decisions.

    MULTI-CHECKPOINT CONTINUITY (NEW, 2026-08-19): the four prior_* parameters let a checkpoint's solve
    account for capacity already built at an earlier checkpoint, rather than each year solving in complete
    isolation. This function stays deliberately ignorant of *which* year or how many years have elapsed --
    it just takes fixed, already-adjusted MW/MWh values from the caller (driver.py) and uses them exactly
    like it already uses exist_solar/the build variables, keeping all year-gap and degradation-rate logic
    out of the LP itself:
      - prior_solar_mw: prior checkpoint's CUMULATIVE new-solar nameplate, ALREADY degraded by the caller
        to this checkpoint's year (same 0.5%/yr rate as exist_solar_mw()). Enters the energy balance
        exactly like the S_ decision variable does (prior_solar_mw*BUILD_SCALE*solar_cf[t]), so this
        checkpoint's own S_ then represents only the INCREMENTAL new build on top. Mathematically exact,
        not an approximation: since exponential decay is multiplicative, degrading a running combined
        total at each checkpoint transition gives identical results to tracking every vintage separately
        and summing (confirmed directly: (A*r^5+B)*r^5 = A*r^10+B*r^5).
      - prior_na_power_mw, prior_na_energy_mwh, prior_ironair_energy_mwh: prior checkpoint's SOLVED build
        sizes, used as LOWER BOUNDS (floors) on this checkpoint's own PNA_/ENA_/EFE_ build variables --
        storage isn't degraded (this project doesn't model battery degradation), so these floors are used
        as-is, unadjusted for the year gap. Prevents a later checkpoint's independently-optimal build from
        coming out smaller than what an earlier checkpoint already built, which would be physically
        nonsensical without an explicit retirement mechanism this project doesn't have.
    All four default to 0.0, exactly reproducing this function's pre-existing, single-checkpoint behavior
    when omitted -- fully backward compatible with every existing call site.
    Returns dict with build sizes, objective, and full hourly variable arrays.
    """
    T = len(demand)
    # DISCLOSED NUMERICAL-CONDITIONING FLOOR (2026-09-09, added after direct diagnosis via highspy's own
    # startup diagnostics, not a guess): solar_cf and wind_cf naturally pass through values that are
    # physically near-zero but not exactly zero at dawn/dusk (solar) and calm periods (wind) -- confirmed
    # directly this session (Aug-Mar window: 25 utility-solar hours, 43 wind hours with 0 < CF < 0.001,
    # minimum 7.66e-06). Left as literal tiny floats, these become matrix coefficients in the energy-
    # balance equality rows (coefficient = BUILD_SCALE*cf[t] on the corresponding build variable),
    # producing a genuinely bad ~1.25e7 matrix coefficient ratio (HiGHS's own diagnostic output: "Matrix
    # [8e-06, 1e+02]") -- exactly the numerical-conditioning problem HiGHS's own documentation warns about
    # (https://ergo-code.github.io/HiGHS/stable/guide/numerics/). Confirmed directly (not assumed) to be
    # the actual bottleneck for a pinned-build solve: dual simplex was still at 35,276 iterations and
    # climbing after 45s on the unfixed matrix. A CF of 7.66e-06 (0.0008%) is physically indistinguishable
    # from true zero -- no real generation decision is lost by rounding it down, and doing so REMOVES the
    # entry from the sparse matrix entirely (a hard zero contributes nothing to a nonzero-based coefficient
    # ratio), rather than merely shrinking it. Threshold (0.001, i.e. 0.1% CF) chosen as clearly, unambiguously
    # below any physically meaningful generation level, not tuned to a specific target ratio.
    CF_FLOOR = 0.001
    solar_cf = np.where(solar_cf < CF_FLOOR, 0.0, solar_cf)
    wind_cf = np.where(wind_cf < CF_FLOOR, 0.0, wind_cf)
    if distributed_solar_cf is not None:
        distributed_solar_cf = np.where(distributed_solar_cf < CF_FLOOR, 0.0, distributed_solar_cf)
    NVAR_BUILD = 8  # UTILITY_SOLAR_MW, SODIUM_ION_POWER_MW, SODIUM_ION_ENERGY_MWH, IRON_AIR_ENERGY_MWH,
                     # DISTRIBUTED_SOLAR_MW, DISTRIBUTED_SODIUM_ION_POWER_MW,
                     # DISTRIBUTED_SODIUM_ION_ENERGY_MWH, DISTRIBUTED_IRON_AIR_ENERGY_MWH. RENAMED
                     # (2026-09-09, SES compliance, Rule 12) from the original S_/PNA_/ENA_/EFE_ -- this
                     # is a file this session is actively modifying, so per direct user instruction names
                     # touched by this change are brought into SES compliance now, not left as-is. The 4
                     # new distributed build variables are always present (fixed array size; simpler and
                     # less error-prone than conditionally resizing NVAR_BUILD) -- pinned to (0, 0) via
                     # bounds when enable_distributed_segment=False, contributing nothing.
    NVAR_PER_HOUR = 21  # g, bc, bd, bsoc, nc, nd, nsoc, fc, fd, fsoc, gascum, unserved, curt, export,
                        # dist_na_charge_mw, dist_na_discharge_mw, dist_na_soc_mwh, dist_fe_charge_mw,
                        # dist_fe_discharge_mw, dist_fe_soc_mwh, dist_curtailment_mw
                        # DIAGNOSTIC (2026-08-16): export re-added as a real decision variable, gated by
                        # include_export -- testing whether the SAME gas-dispatch-arbitrage distortion that
                        # caused this project to remove export entirely (see the note this replaces) recurs
                        # with the corrected, current export price ($37.80/MWh, not the stale $63 the arbitrage
                        # was likely found under). Defaults to excluded (False) -- the removal remains the
                        # standing decision unless this test proves the distortion no longer applies.
                        # The 7 new distributed per-hour variables (2026-09-09) follow the SAME pinned-to-
                        # zero-when-disabled pattern as export -- see enable_distributed_segment above.
    NVAR = NVAR_BUILD + NVAR_PER_HOUR*T

    def hv(t, k):
        return NVAR_BUILD + t*NVAR_PER_HOUR + k
    # PRE-EXISTING keys ('g' through 'export') deliberately kept as their original short strings, NOT
    # renamed to SES-compliant full words -- driver.py and every solve_*.py checkpoint script reference
    # these exact keys via IDX['g']-style lookups, and renaming them would cascade into files this
    # specific change isn't touching and can't verify against real solve data right now (2026-09-09
    # scoping decision, stated directly rather than silently narrowed). Flagged as a deliberate, separate
    # follow-up rename, not an oversight. The 7 NEW keys below have no such legacy callers, so they're
    # SES-compliant (full, unambiguous words) from the start.
    IDX = dict(g=0, bc=1, bd=2, bsoc=3, nc=4, nd=5, nsoc=6, fc=7, fd=8, fsoc=9, gascum=10, unserved=11,
               curt=12, export=13, dist_na_charge_mw=14, dist_na_discharge_mw=15, dist_na_soc_mwh=16,
               dist_fe_charge_mw=17, dist_fe_discharge_mw=18, dist_fe_soc_mwh=19, dist_curtailment_mw=20)
    (UTILITY_SOLAR_MW, SODIUM_ION_POWER_MW, SODIUM_ION_ENERGY_MWH, IRON_AIR_ENERGY_MWH,
     DISTRIBUTED_SOLAR_MW, DISTRIBUTED_SODIUM_ION_POWER_MW, DISTRIBUTED_SODIUM_ION_ENERGY_MWH,
     DISTRIBUTED_IRON_AIR_ENERGY_MWH) = 0, 1, 2, 3, 4, 5, 6, 7

    # BUILD_SCALE: was 1000.0 (GW/GWh basis for the 4 build-decision variables), intended to keep
    # THEIR OWN magnitude reasonable per HiGHS's numerics guidance. CORRECTED (2026-08-16): this
    # traded one problem for a worse one -- it kept the build variables small, but inflated THEIR
    # OBJECTIVE COEFFICIENTS into the tens of millions (since cost-per-unit scales up by the same
    # factor), which is what actually drove the ~9.9e9 objective coefficient ratio confirmed this
    # session (0.01-scale tie-breakers vs ~$99M build coefficients). Set to 1.0 (natural MW/MWh
    # units): the 4 build variables become larger (hundreds of thousands), but that is far cheaper
    # for numerical conditioning than 113,880 objective coefficients spanning 10 orders of
    # magnitude -- expected to bring the ratio down to roughly ~9.9e6. Every place BUILD_SCALE is
    # used (this function, build_problem_multi_duration, and all of driver.py) already references
    # this named constant rather than hardcoding 1000, so this single change propagates correctly
    # and consistently everywhere.
    BUILD_SCALE = 1.0

    residual = demand - nuclear - exist_solar - CVOW_MW*wind_cf - prior_solar_mw*BUILD_SCALE*solar_cf
    # what solar+storage+gas must net out (no export); prior_solar_mw enters exactly like the
    # UTILITY_SOLAR_MW build variable does below (nameplate MW x hourly capacity factor), just as a
    # fixed constant instead of a decision variable -- see the prior_* docstring above for why this
    # correctly represents carried-forward, already-degraded capacity from an earlier checkpoint.
    # Distributed solar/storage is NOT folded into this constant -- unlike exist_solar/prior_solar_mw,
    # the distributed segment's own build sizes are real decision variables this same solve determines,
    # so its contribution has to be a genuine term in the (A) balance below, not baked into the RHS.

    if enable_distributed_segment and distributed_solar_cf is None:
        raise ValueError("enable_distributed_segment=True requires distributed_solar_cf")
    if enable_distributed_segment and distributed_exogenous_price_mwh is None:
        raise ValueError("enable_distributed_segment=True requires distributed_exogenous_price_mwh")
    # Fail loudly (SES Rule 5) rather than silently defaulting distributed_solar_cf to solar_cf or
    # distributed_exogenous_price_mwh to zero -- either default would silently produce a real, wrong
    # answer (blended-CF-style utility/distributed conflation in the first case; free, unpriced storage
    # dispatch in the second) rather than an obvious failure.
    dist_cf = distributed_solar_cf if enable_distributed_segment else np.zeros(T)

    # DISCLOSED NUMERICAL-CONDITIONING FLOOR (2026-09-09, added after direct measurement -- not a
    # researched figure, a chosen one): distributed_exogenous_price_mwh, built from real congestion/loss
    # data plus a scarcity proxy, naturally passes through near-zero at some hours (components partially
    # cancelling) -- confirmed directly via build_problem's own returned 'c' array to produce objective
    # coefficients as small as $0.0044/MWh sitting alongside the $100,000 unserved penalty and ~$99,159
    # build coefficients, a 2.25e7 max/min ratio -- worse than this project's own established ~9.9e6
    # target from the earlier BUILD_SCALE/curtailment-cost conditioning fixes (see na_cycling_cost/
    # curtailment history above). Floored to a $1/MWh minimum MAGNITUDE, sign preserved (a real negative
    # price is a real economic signal, not noise) -- chosen as small relative to the price series' own
    # observed range (roughly +/-$28/MWh, so the floor only binds the near-zero tail) while still bringing
    # the worst-case ratio down to ~1e5, better-conditioned than this project's own prior accepted bar.
    # Exact zero hours are left at zero (sign()=0 case) -- harmless, since a true zero coefficient does
    # not enter a max/min-of-nonzero ratio calculation at all.
    DISTRIBUTED_PRICE_FLOOR_MWH = 1.0
    if enable_distributed_segment:
        _price = distributed_exogenous_price_mwh
        distributed_exogenous_price_mwh = np.where(
            np.abs(_price) < DISTRIBUTED_PRICE_FLOOR_MWH,
            np.sign(_price) * DISTRIBUTED_PRICE_FLOOR_MWH,
            _price,
        )

    # ---------------- Equality constraints ----------------
    eq_rows, eq_cols, eq_data, eq_rhs = [], [], [], []
    row = 0

    # (A) energy balance, one row per hour -- unserved (shortfall), curt and export (both excess-
    # generation outlets, export subtracted the same way curt is: energy leaving the pool available
    # to serve Virginia demand, whether wasted or sold). The distributed segment's own net contribution
    # (generation + discharge - charge - its own curtailment, both storage types) is added into the SAME
    # row -- coupled, not independent, per the design discussion this follows: whatever the distributed
    # segment doesn't use itself is exactly what the rest of the system no longer has to cover.
    for t in range(T):
        eq_rows += [row]*8
        eq_cols += [UTILITY_SOLAR_MW, hv(t,IDX['g']), hv(t,IDX['bd']), hv(t,IDX['bc']),
                    hv(t,IDX['nd']), hv(t,IDX['nc']), hv(t,IDX['fd']), hv(t,IDX['fc'])]
        eq_data += [solar_cf[t]*BUILD_SCALE, 1.0, 1.0, -1.0, 1.0, -1.0, 1.0, -1.0]
        eq_rows += [row, row, row]; eq_cols += [hv(t,IDX['unserved']), hv(t,IDX['curt']), hv(t,IDX['export'])]; eq_data += [1.0, -1.0, -1.0]
        eq_rows += [row]*6
        eq_cols += [DISTRIBUTED_SOLAR_MW, hv(t,IDX['dist_na_discharge_mw']), hv(t,IDX['dist_na_charge_mw']),
                    hv(t,IDX['dist_fe_discharge_mw']), hv(t,IDX['dist_fe_charge_mw']),
                    hv(t,IDX['dist_curtailment_mw'])]
        eq_data += [dist_cf[t]*BUILD_SCALE, 1.0, -1.0, 1.0, -1.0, -1.0]
        eq_rhs.append(residual[t])
        row += 1

    # (B) Bath SoC dynamics
    init_bath = init_soc_frac*BATH_MWH
    for t in range(T):
        if t == 0:
            eq_rows += [row, row]
            eq_cols += [hv(t,IDX['bsoc']), hv(t,IDX['bc'])]
            eq_data += [1.0, -BATH_RTE_CHARGE]
            # also + bd[0] term
            eq_rows += [row]; eq_cols += [hv(t,IDX['bd'])]; eq_data += [1.0]
            eq_rhs.append(init_bath)
        else:
            eq_rows += [row, row, row, row]
            eq_cols += [hv(t,IDX['bsoc']), hv(t-1,IDX['bsoc']), hv(t,IDX['bc']), hv(t,IDX['bd'])]
            eq_data += [1.0, -1.0, -BATH_RTE_CHARGE, 1.0]
            eq_rhs.append(0.0)
        row += 1
    # end-of-horizon cyclic
    # NEW (2026-09-09): enforce_closing_soc, default True (preserves this function's pre-existing
    # behavior for every current caller). Added per direct project direction: forcing soc[T-1] to
    # exactly init_soc_frac (50%) may be a reasonable convention for a repeating annual cycle, but
    # imposes an artificial, un-economic constraint specifically for a system whose real, seasonal-
    # optimal SoC plausibly differs a lot by calendar position (e.g. still-summer August, early-spring
    # March) -- worth testing directly rather than assumed either way. False removes this specific
    # equality only; the existing per-hour bounds (DoD floor, energy-capacity ceiling) still apply at
    # T-1 same as every other hour, so "free" here means economically free, not physically unbounded.
    if enforce_closing_soc:
        eq_rows += [row]; eq_cols += [hv(T-1, IDX['bsoc'])]; eq_data += [1.0]; eq_rhs.append(init_bath); row += 1

    # (C) Sodium SoC dynamics (init/end tied to SODIUM_ION_ENERGY_MWH variable via init_soc_frac)
    for t in range(T):
        if t == 0:
            eq_rows += [row, row, row, row]
            eq_cols += [hv(t,IDX['nsoc']), hv(t,IDX['nc']), hv(t,IDX['nd']), SODIUM_ION_ENERGY_MWH]
            eq_data += [1.0, -NA_RTE_CHARGE, 1.0, -init_soc_frac*BUILD_SCALE]
            eq_rhs.append(0.0)
        else:
            eq_rows += [row]*4
            eq_cols += [hv(t,IDX['nsoc']), hv(t-1,IDX['nsoc']), hv(t,IDX['nc']), hv(t,IDX['nd'])]
            eq_data += [1.0, -1.0, -NA_RTE_CHARGE, 1.0]
            eq_rhs.append(0.0)
        row += 1
    if enforce_closing_soc:  # see enforce_closing_soc note at the Bath end-of-horizon constraint above
        eq_rows += [row, row]; eq_cols += [hv(T-1,IDX['nsoc']), SODIUM_ION_ENERGY_MWH]; eq_data += [1.0, -init_soc_frac*BUILD_SCALE]; eq_rhs.append(0.0); row += 1

    # (D) Iron-air SoC dynamics
    for t in range(T):
        if t == 0:
            eq_rows += [row, row, row, row]
            eq_cols += [hv(t,IDX['fsoc']), hv(t,IDX['fc']), hv(t,IDX['fd']), IRON_AIR_ENERGY_MWH]
            eq_data += [1.0, -FE_RTE_CHARGE, 1.0, -init_soc_frac*BUILD_SCALE]
            eq_rhs.append(0.0)
        else:
            eq_rows += [row]*4
            eq_cols += [hv(t,IDX['fsoc']), hv(t-1,IDX['fsoc']), hv(t,IDX['fc']), hv(t,IDX['fd'])]
            eq_data += [1.0, -1.0, -FE_RTE_CHARGE, 1.0]
            eq_rhs.append(0.0)
        row += 1
    if enforce_closing_soc:  # see enforce_closing_soc note at the Bath end-of-horizon constraint above
        eq_rows += [row, row]; eq_cols += [hv(T-1,IDX['fsoc']), IRON_AIR_ENERGY_MWH]; eq_data += [1.0, -init_soc_frac*BUILD_SCALE]; eq_rhs.append(0.0); row += 1

    # (C2)/(D2) Distributed Na-ion and iron-air SoC dynamics -- structurally IDENTICAL to (C)/(D) above,
    # reusing the same RTE-charge figures (NA_RTE_CHARGE, FE_RTE_CHARGE) since no distinct, sourced
    # round-trip-efficiency figure exists for distributed/DER-scale storage specifically -- a disclosed,
    # reused assumption, not independently verified for this hardware class. Present but structurally
    # inert (all coefficients multiply variables pinned to 0) when enable_distributed_segment=False.
    for t in range(T):
        if t == 0:
            eq_rows += [row, row, row, row]
            eq_cols += [hv(t,IDX['dist_na_soc_mwh']), hv(t,IDX['dist_na_charge_mw']),
                        hv(t,IDX['dist_na_discharge_mw']), DISTRIBUTED_SODIUM_ION_ENERGY_MWH]
            eq_data += [1.0, -NA_RTE_CHARGE, 1.0, -init_soc_frac*BUILD_SCALE]
            eq_rhs.append(0.0)
        else:
            eq_rows += [row]*4
            eq_cols += [hv(t,IDX['dist_na_soc_mwh']), hv(t-1,IDX['dist_na_soc_mwh']),
                        hv(t,IDX['dist_na_charge_mw']), hv(t,IDX['dist_na_discharge_mw'])]
            eq_data += [1.0, -1.0, -NA_RTE_CHARGE, 1.0]
            eq_rhs.append(0.0)
        row += 1
    if enforce_closing_soc:  # see enforce_closing_soc note at the Bath end-of-horizon constraint above
        eq_rows += [row, row]; eq_cols += [hv(T-1,IDX['dist_na_soc_mwh']), DISTRIBUTED_SODIUM_ION_ENERGY_MWH]; eq_data += [1.0, -init_soc_frac*BUILD_SCALE]; eq_rhs.append(0.0); row += 1

    for t in range(T):
        if t == 0:
            eq_rows += [row, row, row, row]
            eq_cols += [hv(t,IDX['dist_fe_soc_mwh']), hv(t,IDX['dist_fe_charge_mw']),
                        hv(t,IDX['dist_fe_discharge_mw']), DISTRIBUTED_IRON_AIR_ENERGY_MWH]
            eq_data += [1.0, -FE_RTE_CHARGE, 1.0, -init_soc_frac*BUILD_SCALE]
            eq_rhs.append(0.0)
        else:
            eq_rows += [row]*4
            eq_cols += [hv(t,IDX['dist_fe_soc_mwh']), hv(t-1,IDX['dist_fe_soc_mwh']),
                        hv(t,IDX['dist_fe_charge_mw']), hv(t,IDX['dist_fe_discharge_mw'])]
            eq_data += [1.0, -1.0, -FE_RTE_CHARGE, 1.0]
            eq_rhs.append(0.0)
        row += 1
    if enforce_closing_soc:  # see enforce_closing_soc note at the Bath end-of-horizon constraint above
        eq_rows += [row, row]; eq_cols += [hv(T-1,IDX['dist_fe_soc_mwh']), DISTRIBUTED_IRON_AIR_ENERGY_MWH]; eq_data += [1.0, -init_soc_frac*BUILD_SCALE]; eq_rhs.append(0.0); row += 1

    # (D3) Distributed-share policy constraint -- ONLY added when enabled.
    # CHANGED 2026-09-09 from a hard EQUALITY to an INEQUALITY (distributed <= share of total).
    # WHY: as an equality this tied the two variables in BOTH directions, so once distributed solar
    # acquired a real physical siting cap (7,440 MW for the DOM zone -- distributed_physical_bounds.py),
    # that cap propagated backwards and capped TOTAL solar at 7,440/0.20 = 37,200 MW. Confirmed directly
    # in the first 2045 solve this session: distributed landed on exactly 7,440.0 MW and utility on
    # exactly 29,760.0 MW (= 4x distributed, the 20% share to the decimal), forcing 91,908,512 MWh of
    # unserved energy -- 44.5% of 2045 demand -- purely because the LP was PROHIBITED from building
    # utility-scale solar beyond that ratio. The 10%-rooftop + 10%-canopy split in the Scenario 3 spec is
    # a policy TARGET for distributed deployment; it was never meant to cap how much utility-scale solar
    # Virginia may build.
    # The original equality's protective purpose is PRESERVED: it existed to stop the export/arbitrage
    # revenue terms from distorting DISTRIBUTED_SOLAR_MW upward to chase revenue, and this inequality
    # still bounds distributed solar from ABOVE -- the direction that risk runs. Only the lower tie is
    # removed, which served no protective role.
    # Deferred to the inequality section below (this is the equality section) -- see d3_pending.
    d3_pending = None
    if enable_distributed_segment:
        d3_pending = distributed_share_of_total_solar / (1.0 - distributed_share_of_total_solar)

    # (E) Cumulative gas tracking, in GWh (not MWh) to keep constraint-matrix magnitudes
    #      comparable to the rest of the problem -- an earlier MWh-based version produced a
    #      single row with RHS ~9.1 million against a problem where every other row/coefficient
    #      was O(1)-O(20,000), which is a severe numerical-conditioning problem, not a genuine
    #      combinatorial-difficulty one. Sparse banded recursion: gascum[t] = gascum[t-1] + g[t]/1000
    for t in range(T):
        if t == 0:
            eq_rows += [row, row]; eq_cols += [hv(t,IDX['gascum']), hv(t,IDX['g'])]; eq_data += [1.0, -0.001]
        else:
            eq_rows += [row, row, row]
            eq_cols += [hv(t,IDX['gascum']), hv(t-1,IDX['gascum']), hv(t,IDX['g'])]
            eq_data += [1.0, -1.0, -0.001]
        eq_rhs.append(0.0)
        row += 1

    n_eq_rows = row
    A_eq = sparse.csr_matrix((eq_data, (eq_rows, eq_cols)), shape=(n_eq_rows, NVAR))
    b_eq = np.array(eq_rhs)

    # ---------------- Inequality constraints (A_ub x <= b_ub) ----------------
    ub_rows, ub_cols, ub_data, ub_rhs = [], [], [], []
    row = 0
    # (D3) flushed here, as an inequality -- see the deferred block in the equality section above.
    if d3_pending is not None:
        ub_rows += [row, row]; ub_cols += [DISTRIBUTED_SOLAR_MW, UTILITY_SOLAR_MW]
        ub_data += [1.0, -d3_pending]; ub_rhs.append(0.0); row += 1
    # NA_DOD_FLOOR = 0.20 (now module-level, see top of file) -- sodium-ion: standard industry
    # convention -- "80% DoD" means discharging FROM full DOWN TO 20% remaining (usable range
    # [20%,100%], reserve at the BOTTOM), not a restriction on how high SoC can charge. CORRECTED
    # (2026-08-16): this project's earlier implementation had it backwards -- nsoc<=0.80*ENA_
    # (reserve at the TOP, full range at
                   # the bottom) -- caught when a direct question surfaced the mismatch. Matters for a real
                   # reason, not just terminology: the sourced cycle-life figures (10,000/15,000 cycles)
                   # were almost certainly measured under the standard [20%,100%] protocol, not [0%,80%].
                   # Iron-air gets NO such restriction (100% DoD, i.e. floor=0) -- multiple independent
                   # sources describe the iron-air chemistry specifically as tolerant of deep/full discharge,
                   # unlike Li/Na-ion (Fraunhofer UMSICHT: "insensitive to overcharging, partial and deep
                   # discharge"), and Form Energy's own design purpose is surviving rare, full multi-day
                   # discharge events -- restricting it would model against both the chemistry and the
                   # intended use case.
    for t in range(T):
        # nc - P_na <= 0 ; nd - P_na <= 0 (individual bounds, kept)
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['nc']), SODIUM_ION_POWER_MW]; ub_data += [1.0,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['nd']), SODIUM_ION_POWER_MW]; ub_data += [1.0,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        # CORRECTED (2026-08-16): nsoc <= 1.0*SODIUM_ION_ENERGY_MWH (full charge allowed) AND
        # nsoc >= 0.20*SODIUM_ION_ENERGY_MWH (floor, not a ceiling) -- replaces the earlier, backwards
        # nsoc<=0.80*(energy build). Upper bound restored to the full, unrestricted energy build; floor
        # added as a new inequality.
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['nsoc']), SODIUM_ION_ENERGY_MWH]; ub_data += [1.0,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['nsoc']), SODIUM_ION_ENERGY_MWH]; ub_data += [-1.0,NA_DOD_FLOOR*BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['fc']), IRON_AIR_ENERGY_MWH]; ub_data += [FE_DURATION,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['fd']), IRON_AIR_ENERGY_MWH]; ub_data += [FE_DURATION,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['fsoc']), IRON_AIR_ENERGY_MWH]; ub_data += [1.0,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        # RESTORED (2026-08-16): the joint charge+discharge power constraints removed earlier this
        # session (redundancy confirmed WITH the -$2/MWh charging incentive still present) turned out
        # not to be truly redundant on their own -- once the -$2 incentive was ALSO removed (separately,
        # to fix genuine solver instability -- see the incentive-removal note below), simultaneous
        # charge/discharge reappeared at large scale (60.4% of hours for Na, 3.5% for Bath) with cycling
        # costs alone. The earlier redundancy finding was real but conditional on the incentive still
        # being present; it does not hold once that incentive is gone. Restored as a direct, reliable
        # constraint rather than depending on cost-based incentives to prevent a physical impossibility.
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['bc']), hv(t,IDX['bd'])]; ub_data += [1.0,1.0]; ub_rhs.append(BATH_MW); row+=1
        ub_rows += [row,row,row]; ub_cols += [hv(t,IDX['nc']), hv(t,IDX['nd']), SODIUM_ION_POWER_MW]; ub_data += [1.0,1.0,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row,row]; ub_cols += [hv(t,IDX['fc']), hv(t,IDX['fd']), IRON_AIR_ENERGY_MWH]; ub_data += [FE_DURATION,FE_DURATION,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1

        # NEW (2026-09-09): distributed storage bounds -- structurally identical to the utility-scale Na/
        # iron-air bounds above (same DoD floor, duration limit, joint charge+discharge constraint),
        # applied to the new DISTRIBUTED_* build variables and dist_na_*/dist_fe_* per-hour variables.
        # Inert (multiplies variables pinned to 0) when enable_distributed_segment=False.
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['dist_na_charge_mw']), DISTRIBUTED_SODIUM_ION_POWER_MW]; ub_data += [1.0,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['dist_na_discharge_mw']), DISTRIBUTED_SODIUM_ION_POWER_MW]; ub_data += [1.0,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['dist_na_soc_mwh']), DISTRIBUTED_SODIUM_ION_ENERGY_MWH]; ub_data += [1.0,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['dist_na_soc_mwh']), DISTRIBUTED_SODIUM_ION_ENERGY_MWH]; ub_data += [-1.0,NA_DOD_FLOOR*BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['dist_fe_charge_mw']), DISTRIBUTED_IRON_AIR_ENERGY_MWH]; ub_data += [FE_DURATION,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['dist_fe_discharge_mw']), DISTRIBUTED_IRON_AIR_ENERGY_MWH]; ub_data += [FE_DURATION,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['dist_fe_soc_mwh']), DISTRIBUTED_IRON_AIR_ENERGY_MWH]; ub_data += [1.0,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row,row]; ub_cols += [hv(t,IDX['dist_na_charge_mw']), hv(t,IDX['dist_na_discharge_mw']), DISTRIBUTED_SODIUM_ION_POWER_MW]; ub_data += [1.0,1.0,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row,row]; ub_cols += [hv(t,IDX['dist_fe_charge_mw']), hv(t,IDX['dist_fe_discharge_mw']), DISTRIBUTED_IRON_AIR_ENERGY_MWH]; ub_data += [FE_DURATION,FE_DURATION,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1

    # NEW (2026-08-16): Bath County one-cycle-per-day constraint (rolling 24-hour window), per project
    # direction -- Bath was designed for a single cycle per day; used identically across all scenarios,
    # so implemented as a straightforward physical constraint rather than a researched cost.
    for day_start in range(0, T, 24):
        day_hours = list(range(day_start, min(day_start+24, T)))
        cols = [hv(tt,IDX['bd']) for tt in day_hours]
        ub_rows += [row]*len(cols); ub_cols += cols; ub_data += [1.0]*len(cols); ub_rhs.append(BATH_MWH); row += 1

    if gas_allowed_frac is None:
        for t in range(T):
            ub_rows += [row]; ub_cols += [hv(t,IDX['g'])]; ub_data += [1.0]; ub_rhs.append(0.0); row += 1
    else:
        # gas_total(GWh) <= k*(clean_total)/1000, where clean_total(MWh) = sum(nuclear+exist_solar+wind)
        # + (UTILITY_SOLAR_MW*BUILD_SCALE)*sum(solar_cf) + (DISTRIBUTED_SOLAR_MW*BUILD_SCALE)*sum(dist_cf)
        # CORRECTED (2026-08-16): with BUILD_SCALE now 1.0 (was 1000.0), the solar coefficient's implicit
        # cancellation against the /1000 GWh conversion (noted in the original comment above) no longer
        # holds -- that cancellation was BUILD_SCALE and the GWh-conversion factor coincidentally both
        # being 1000, not a structural guarantee. Restored explicitly via BUILD_SCALE so this is correct
        # regardless of its value: utility solar's clean-generation contribution is
        # (UTILITY_SOLAR_MW x BUILD_SCALE x solar_cf), converted to GWh by /1000, same as the constant
        # term already is. EXTENDED (2026-09-09): distributed solar's own generation is real clean energy
        # serving Virginia demand (whether via NEM offset or WMA grid injection) and counts toward this
        # same clean_total the identical way -- inert (multiplies a variable pinned to 0) when
        # enable_distributed_segment=False.
        k = gas_allowed_frac/(1-gas_allowed_frac)
        clean_sum_const = np.sum(nuclear + exist_solar + CVOW_MW*wind_cf)
        ub_rows += [row, row, row]
        ub_cols += [hv(T-1,IDX['gascum']), UTILITY_SOLAR_MW, DISTRIBUTED_SOLAR_MW]
        ub_data += [1.0, -k*BUILD_SCALE*np.sum(solar_cf)/1000.0, -k*BUILD_SCALE*np.sum(dist_cf)/1000.0]
        ub_rhs.append(k*clean_sum_const/1000.0)
        row += 1

    n_ub_rows = row
    A_ub = sparse.csr_matrix((ub_data, (ub_rows, ub_cols)), shape=(n_ub_rows, NVAR))
    b_ub = np.array(ub_rhs)

    # ---------------- Bounds ----------------
    bounds = [(0, None)]*NVAR
    # MULTI-CHECKPOINT CONTINUITY: floor this checkpoint's storage build variables at whatever was
    # already built at the prior checkpoint. Storage isn't degraded (unlike solar, handled via
    # prior_solar_mw in the residual above), so these floors are used unadjusted for the year gap --
    # a later checkpoint's independently-optimal build must be at least as large as what an earlier
    # checkpoint already built, since this project has no storage retirement mechanism. All three
    # default to 0.0 (i.e. (0, None), identical to this function's pre-existing behavior) when the
    # corresponding prior_* argument is omitted.
    bounds[SODIUM_ION_POWER_MW] = (prior_na_power_mw, None)
    bounds[SODIUM_ION_ENERGY_MWH] = (prior_na_energy_mwh, None)
    bounds[IRON_AIR_ENERGY_MWH] = (prior_ironair_energy_mwh, None)
    # NEW (2026-09-09): distributed build variables. When disabled, pinned to exactly (0, 0) -- same
    # pattern as export above -- so this function reproduces its pre-existing behavior exactly. When
    # enabled, DISTRIBUTED_SOLAR_MW itself is left (0, None) here (its actual value is FIXED by the
    # (D3) equality constraint above, not by a bound) and the three distributed storage build variables
    # get the same prior-checkpoint floor treatment as their utility-scale counterparts.
    if enable_distributed_segment:
        bounds[DISTRIBUTED_SODIUM_ION_POWER_MW] = (prior_distributed_na_power_mw, None)
        bounds[DISTRIBUTED_SODIUM_ION_ENERGY_MWH] = (prior_distributed_na_energy_mwh, None)
        bounds[DISTRIBUTED_IRON_AIR_ENERGY_MWH] = (prior_distributed_ironair_energy_mwh, None)
    else:
        bounds[DISTRIBUTED_SOLAR_MW] = (0, 0)
        bounds[DISTRIBUTED_SODIUM_ION_POWER_MW] = (0, 0)
        bounds[DISTRIBUTED_SODIUM_ION_ENERGY_MWH] = (0, 0)
        bounds[DISTRIBUTED_IRON_AIR_ENERGY_MWH] = (0, 0)

    # NEW (2026-09-09): pin_build_mw -- explicit ceiling on top of whatever floor already applies above,
    # applied LAST so it always wins regardless of variable (overrides both the (0,None) default and any
    # prior_* floor). Added specifically for partial-year (e.g. Aug-Mar) diagnostic solves: the RPS
    # constraint's solar coefficient is proportional to sum(solar_cf) over whichever window is solved
    # (see the (k, clean_sum_const) ub_rows block above), so a truncated, lower-average-CF window makes
    # the SAME nameplate MW count for less toward the RPS target, and an unpinned re-solve compensates by
    # over-building -- confirmed directly this session (Aug-Mar re-solve without this pin produced 54 GW
    # of utility solar, over 3x VCEA's entire statutory minimum, and 23.2M MWh of curtailment, inconsistent
    # with this project's own established finding that curtailment is heaviest Apr-Aug and lowest in
    # winter -- Internal_Debugging_Log.md #16). Pinning build size lets the LP optimize ONLY hourly
    # dispatch over the truncated window, which is the actual question a partial-year diagnostic solve is
    # for -- not a re-derivation of build size, which needs the full year's own representative CF mix.
    # Keyed by the same string names used throughout this project's own build-variable vocabulary (Rule 5:
    # an unrecognized key raises rather than being silently ignored).
    if pin_build_mw is not None:
        _pin_name_to_idx = {
            'UTILITY_SOLAR_MW': UTILITY_SOLAR_MW, 'SODIUM_ION_POWER_MW': SODIUM_ION_POWER_MW,
            'SODIUM_ION_ENERGY_MWH': SODIUM_ION_ENERGY_MWH, 'IRON_AIR_ENERGY_MWH': IRON_AIR_ENERGY_MWH,
            'DISTRIBUTED_SOLAR_MW': DISTRIBUTED_SOLAR_MW,
            'DISTRIBUTED_SODIUM_ION_POWER_MW': DISTRIBUTED_SODIUM_ION_POWER_MW,
            'DISTRIBUTED_SODIUM_ION_ENERGY_MWH': DISTRIBUTED_SODIUM_ION_ENERGY_MWH,
            'DISTRIBUTED_IRON_AIR_ENERGY_MWH': DISTRIBUTED_IRON_AIR_ENERGY_MWH,
        }
        for name, value in pin_build_mw.items():
            if name not in _pin_name_to_idx:
                raise ValueError(f"pin_build_mw: unrecognized variable name {name!r} -- "
                                  f"expected one of {sorted(_pin_name_to_idx)}")
            bounds[_pin_name_to_idx[name]] = (value, value)

    for t in range(T):
        bounds[hv(t,IDX['bc'])] = (0, BATH_MW)
        bounds[hv(t,IDX['bd'])] = (0, BATH_MW)
        bounds[hv(t,IDX['bsoc'])] = (0, BATH_MWH)
        # DIAGNOSTIC (2026-08-16): export bounded [0, EXPORT_CAP_MW] only if explicitly included this
        # solve; otherwise pinned to exactly 0, reproducing the standing "export removed entirely"
        # decision by default. See include_export parameter note at function definition.
        bounds[hv(t,IDX['export'])] = (0, EXPORT_CAP_MW) if include_export else (0, 0)
        # NEW (2026-09-09): the 7 distributed per-hour variables, pinned to (0, 0) when disabled --
        # otherwise left at the default (0, None) here since their REAL upper bounds are already fully
        # enforced by the (A_ub) inequality rows added above (tied to the distributed build variables,
        # not a fixed constant the way BATH_MW/EXPORT_CAP_MW are).
        if not enable_distributed_segment:
            for k_ in ('dist_na_charge_mw', 'dist_na_discharge_mw', 'dist_na_soc_mwh',
                       'dist_fe_charge_mw', 'dist_fe_discharge_mw', 'dist_fe_soc_mwh',
                       'dist_curtailment_mw'):
                bounds[hv(t, IDX[k_])] = (0, 0)
        if gas_allowed_frac is None:
            bounds[hv(t,IDX['g'])] = (0, 0)

    # ---------------- Objective ----------------
    c = np.zeros(NVAR)
    c[UTILITY_SOLAR_MW] = CRF*SOLAR_CAPEX*1000 + SOLAR_OM*1000  # $/MW-yr (raw MW basis, scaled to GW basis below)
    c[SODIUM_ION_POWER_MW] = CRF*NA_POWER_CAPEX*1000
    c[SODIUM_ION_ENERGY_MWH] = CRF*NA_ENERGY_CAPEX*1000 + STOR_FOM_PCT*NA_ENERGY_CAPEX*1000
    c[IRON_AIR_ENERGY_MWH] = (CRF*FE_ENERGY_CAPEX*1000 + STOR_FOM_PCT*FE_ENERGY_CAPEX*1000) * (1.0 - RESILIENCE_TILT_PCT)
    # NEW (2026-09-09): distributed build costs. DISCLOSED SIMPLIFICATION -- reuses the SAME capex
    # figures as utility-scale (SOLAR_CAPEX, NA_POWER_CAPEX, NA_ENERGY_CAPEX, FE_ENERGY_CAPEX), since no
    # distinct, sourced rooftop/canopy or DER-scale storage capex figure exists in this project. This is
    # a real, likely-optimistic simplification in one specific direction, not a neutral placeholder --
    # rooftop/small-commercial-scale solar and storage installations are well-documented in the industry
    # as typically costing MORE per kW than utility-scale ground-mount/centralized storage (smaller
    # projects lose the economies of scale utility-scale procurement captures). Flagged here rather than
    # silently assumed at cost parity -- worth sourcing a real distinct figure before this feeds a
    # headline number. DISTRIBUTED_SOLAR_MW itself DOES carry a real build cost, even though its SIZE is
    # policy-fixed (not a free decision) -- the fixed share still has to be paid for.
    c[DISTRIBUTED_SOLAR_MW] = CRF*SOLAR_CAPEX*1000 + SOLAR_OM*1000
    c[DISTRIBUTED_SODIUM_ION_POWER_MW] = CRF*NA_POWER_CAPEX*1000
    c[DISTRIBUTED_SODIUM_ION_ENERGY_MWH] = CRF*NA_ENERGY_CAPEX*1000 + STOR_FOM_PCT*NA_ENERGY_CAPEX*1000
    c[DISTRIBUTED_IRON_AIR_ENERGY_MWH] = (CRF*FE_ENERGY_CAPEX*1000 + STOR_FOM_PCT*FE_ENERGY_CAPEX*1000) * (1.0 - RESILIENCE_TILT_PCT)
    years_factor = T/8760.0
    for _bv in (UTILITY_SOLAR_MW, SODIUM_ION_POWER_MW, SODIUM_ION_ENERGY_MWH, IRON_AIR_ENERGY_MWH,
                DISTRIBUTED_SOLAR_MW, DISTRIBUTED_SODIUM_ION_POWER_MW,
                DISTRIBUTED_SODIUM_ION_ENERGY_MWH, DISTRIBUTED_IRON_AIR_ENERGY_MWH):
        c[_bv] *= years_factor
    # Now convert from $/MW(-equivalent) to $/GW(-equivalent): one unit of a build variable now
    # represents BUILD_SCALE physical MW/MWh, so its cost coefficient must be BUILD_SCALE times larger.
    for _bv in (UTILITY_SOLAR_MW, SODIUM_ION_POWER_MW, SODIUM_ION_ENERGY_MWH, IRON_AIR_ENERGY_MWH,
                DISTRIBUTED_SOLAR_MW, DISTRIBUTED_SODIUM_ION_POWER_MW,
                DISTRIBUTED_SODIUM_ION_ENERGY_MWH, DISTRIBUTED_IRON_AIR_ENERGY_MWH):
        c[_bv] *= BUILD_SCALE
    _gas_price = GAS_COST_MWH if gas_price_mwh is None else gas_price_mwh
    # NEW (2026-08-16): discharge-side cycling/degradation costs, per Sandia National Labs' BESS Cycling
    # Price Model methodology (cost = replacement cost / total lifetime throughput). Na-ion: time-varying
    # cycle life (NA_CYCLE_LIFE, set externally per checkpoint year -- 10,000 pre-2035, 15,000 2035+, per
    # project direction), at 80% usable capacity (1.0 - NA_DOD_FLOOR, i.e. the [20%,100%] range now
    # correctly enforced on the SoC bound above -- CORRECTED 2026-08-16, was backwards as [0%,80%]).
    # Iron-air: Form Energy-specific ~1,000-cycle figure (FE_CYCLE_LIFE), at 100% DoD (FE_DOD=1.0) --
    # multiple independent sources describe the iron-air chemistry as tolerant of deep discharge, unlike
    # Li/Na-ion.
    na_cycling_cost = (NA_ENERGY_CAPEX*1000) / (NA_CYCLE_LIFE * (1.0 - NA_DOD_FLOOR))
    fe_cycling_cost = (FE_ENERGY_CAPEX*1000) / (FE_CYCLE_LIFE * FE_DOD)
    for t in range(T):
        c[hv(t,IDX['g'])] = _gas_price
        c[hv(t,IDX['nd'])] = na_cycling_cost
        c[hv(t,IDX['fd'])] = fe_cycling_cost
        c[hv(t,IDX['unserved'])] = UNSERVED_PENALTY
        # CORRECTED (2026-08-16): the previous 0.01 curtailment token cost, combined with a zero-cost
        # charge variable, produced a coefficient ratio of ~9.9e9 in the objective (0.01 vs ~$99M build-
        # cost coefficients) -- confirmed via direct measurement to be severe enough that HiGHS's automatic
        # scaling could not fully compensate, producing a genuine (reduced-cost-confirmed-zero) LP
        # degeneracy: charging into abundant curtailed surplus and simply discarding it were computed as
        # exactly cost-equivalent, so the solver had no basis to prefer capturing free energy over wasting
        # it. Resized both terms together: curtailment token cost 0.01 -> 1.0 initially.
        # CORRECTED (2026-08-16), second pass: $1.0/MWh was STILL too weak, confirmed directly -- pinning
        # the build size at its own already-solved optimum and testing $1 vs $100 vs $5,000/MWh curtailment
        # cost showed $1 left both Na and iron-air SoC topping out around 71-72% of their own caps despite
        # massive simultaneous curtailment, while $100 (and $5,000, confirming $100 already saturates the
        # effect) drove BOTH to exactly 100% utilization with ZERO additional capacity built -- a 43.7%
        # curtailment reduction from utilization alone. $100/MWh is a defensible figure in its own right
        # (same order of magnitude as gas cost and the export price), not another arbitrary tie-breaker.
        c[hv(t,IDX['curt'])] = 100.0
        # CORRECTED (2026-08-16), removed permanently: the -$2.0/MWh charging incentives on nc/fc were
        # originally added to fix simultaneous charge/discharge, but the discharge-side cycling costs
        # (na_cycling_cost/fe_cycling_cost, set below) were later proven to fully handle that on their
        # own (0% simultaneous dispatch with or without the joint power constraint, confirmed earlier
        # this session). Once redundant, this term turned out to also be a genuine source of solver
        # instability -- three identical solves of the same unpinned 2045 problem gave three DIFFERENT
        # objective values and build sizes with this term present, but landed on the exact same answer
        # (spread of 0.0 across three repeated runs) once removed. Caught when a direct question about
        # this term's original purpose prompted testing whether it was still needed at all.
        if include_export:
            # DIAGNOSTIC (2026-08-16): revenue term, negative cost. Only active when include_export=True
            # -- testing whether the same gas-dispatch-arbitrage distortion that caused this project to
            # remove export entirely recurs under the corrected $37.80/MWh price, before deciding whether
            # to keep this permanently. See function-definition note for full context.
            c[hv(t,IDX['export'])] = -export_price_mwh
        # CORRECTED (2026-09-04): removed permanently, matching the Na/iron-air treatment exactly.
        # Direct testing (synthetic full-year data, since the exact real checkpoint files weren't
        # present in this session's own container) found: (1) no evidence of the same severe
        # non-reproducibility problem that justified removing this style of term from Na/iron-air --
        # three identical solves with this term present gave the exact same objective value each time;
        # (2) but also no evidence it was still earning its keep -- removing it left the build decision
        # completely unchanged (solar/Na/iron-air build sizes identical to the decimal with vs. without),
        # and did not resolve the simultaneous charge/discharge issue it was added to fix (215 hours/
        # 2.45% with the term vs. 197 hours/2.25% without -- both far from zero either way, confirming
        # Bath's own residual issue is not being solved by this mechanism). Removed for consistency with
        # the Na/iron-air precedent, per direct user confirmation, not because it was shown harmful.
        # c[hv(t,IDX['bc'])] = -2.0  -- REMOVED, see comment above
        # NEW (2026-08-16): Bath County cycling cost, discharge-side, same convention as Na/iron-air.
        # $7.50/MWh -- DOE/PNNL (Mongird et al. 2020) PSH-specific RTE-loss cost, computed at 80% RTE,
        # matching this model's own BATH_RTE_CHARGE exactly. Directly addresses the residual simultaneous
        # charge/discharge Bath was still showing (Na and iron-air already went to zero once given a real
        # discharge-side cost; Bath was the only type left without one).
        c[hv(t,IDX['bd'])] = 7.50

        # NEW (2026-09-09): distributed segment. Inert (contributes 0) when enable_distributed_segment=
        # False, since the corresponding decision variables are all pinned to (0, 0) by the bounds above
        # -- these coefficients exist either way, they just multiply variables fixed at zero.
        #
        # Cycling costs: same na_cycling_cost/fe_cycling_cost figures as utility-scale (see the capex
        # comment above -- reused, not independently sourced for distributed-scale hardware).
        c[hv(t,IDX['dist_na_discharge_mw'])] = na_cycling_cost
        c[hv(t,IDX['dist_fe_discharge_mw'])] = fe_cycling_cost
        # Distributed curtailment: same $100/MWh token cost as the main system's curt, for the identical
        # reason (avoid solver indifference between using free generation and discarding it).
        c[hv(t,IDX['dist_curtailment_mw'])] = 100.0
        if enable_distributed_segment:
            # Revenue/cost terms, SYMMETRIC on charge and discharge -- an owner's own arbitrage economics
            # against the exogenous price series, NOT a system-cost term. CORRECTED (2026-09-09, caught
            # via direct testing, not written in silently): an earlier version of this priced discharge
            # only (revenue) and left charge free (no cost), on the theory that charging's opportunity
            # cost was already implicit via the balance-equation coupling. Directly tested against a
            # small synthetic example and found UNBOUNDED (HiGHS status 3) -- confirmed the same failure
            # occurs with gas both locked to zero and freely available, ruling out the gas cap as the
            # cause. Root cause: with charge cost-free and storage build variables unbounded above
            # (prior_distributed_na_power_mw floor, no ceiling), the LP could build arbitrarily large
            # power/energy capacity and cycle arbitrarily large "free" charge into discharge revenue --
            # capex and cycling cost scale with build size, but nothing bounded the MARGIN per MW, so any
            # positive margin drove the objective to -infinity as build size grew without limit.
            # Fixed by pricing charge at the SAME price[t] (a real opportunity cost: charging instead of
            # injecting immediately forgoes that hour's own sale), making the captured margin
            # price[t2]*RTE - price[t1] - cycling_cost*RTE for any charge/discharge pair -- finite for any
            # finite price series, so the LP now builds only enough capacity to capture the REAL, bounded
            # arbitrage opportunity the price series actually contains, not an unlimited one. This does
            # NOT reopen the build-distortion risk the fixed distributed-solar-share constraint exists to
            # prevent -- DISTRIBUTED_SOLAR_MW itself still carries no price term of its own, only its real
            # build cost; only storage DISPATCH (not distributed solar's own build size) responds to
            # price.
            c[hv(t,IDX['dist_na_discharge_mw'])] -= distributed_exogenous_price_mwh[t]
            c[hv(t,IDX['dist_fe_discharge_mw'])] -= distributed_exogenous_price_mwh[t]
            c[hv(t,IDX['dist_na_charge_mw'])] += distributed_exogenous_price_mwh[t]
            c[hv(t,IDX['dist_fe_charge_mw'])] += distributed_exogenous_price_mwh[t]

    if verbose:
        print(f"T={T} NVAR={NVAR} n_eq={n_eq_rows} n_ub={n_ub_rows}")

    problem = dict(c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds,
                    IDX=IDX, hv_params=(NVAR_BUILD, NVAR_PER_HOUR),
                    builds=(UTILITY_SOLAR_MW, SODIUM_ION_POWER_MW, SODIUM_ION_ENERGY_MWH, IRON_AIR_ENERGY_MWH),
                    distributed_builds=(DISTRIBUTED_SOLAR_MW, DISTRIBUTED_SODIUM_ION_POWER_MW,
                                        DISTRIBUTED_SODIUM_ION_ENERGY_MWH, DISTRIBUTED_IRON_AIR_ENERGY_MWH),
                    T=T, BUILD_SCALE=BUILD_SCALE)
    # NEW (2026-09-09): 'builds' kept as the original 4-tuple (utility-scale only) for exact backward
    # compatibility with every existing caller that unpacks it positionally -- 'distributed_builds' added
    # as a new, separate key rather than extending the existing tuple's length, which would silently
    # break any caller doing `S_mw, PNA_mw, ENA_mwh, EFE_mwh = problem['builds']`.
    return problem


def build_problem_multi_duration(solar_cf, wind_cf, nuclear, exist_solar, demand, gas_allowed_frac,
                                  init_soc_frac=0.5, verbose=True, gas_price_mwh=None, na_year=None,
                                  durations=(4.0, 6.0, 8.0)):
    """
    Variant of build_problem() with sodium-ion storage split into discrete, duration-locked
    products (default 4/6/8-hr) instead of one freely-ratioed resource. ASSUMPTION: all duration
    classes share the SAME underlying $/kWh (energy) and $/kW (power) unit costs -- see
    na_power_energy_split() for sourcing. Because those per-unit rates are duration-independent,
    the three products are economically equivalent per unit of useful capacity; the split the
    solver reports among them is not economically meaningful (LP may be indifferent / degenerate
    across ties) and should not be read as "the LP preferred 6hr over 8hr" -- it's a presentation
    choice (stakeholder-recognizable product SKUs) rather than a distinct cost signal. Bath and
    iron-air are unchanged from build_problem(). na_year: year to evaluate na_power_energy_split
    at (defaults to BUILD_YEAR global if not given -- callers doing checkpoint-specific solves
    should pass the checkpoint year explicitly, same caveat as gas_price_mwh above).
    """
    T = len(demand)
    n_dur = len(durations)
    NVAR_BUILD = 2 + 2*n_dur + 1  # S, [P_d,E_d]*n_dur, E_fe
    S_ = 0
    P_ = [1+2*i for i in range(n_dur)]
    E_ = [2+2*i for i in range(n_dur)]
    EFE_ = 1 + 2*n_dur

    IDX = dict(g=0, bc=1, bd=2, bsoc=3)
    base = 4
    NC, ND, NSOC = [], [], []
    for i in range(n_dur):
        NC.append(base+3*i); ND.append(base+3*i+1); NSOC.append(base+3*i+2)
    base2 = base + 3*n_dur
    IDX.update(fc=base2, fd=base2+1, fsoc=base2+2, gascum=base2+3, unserved=base2+4, curt=base2+5)
    NVAR_PER_HOUR = base2 + 6
    NVAR = NVAR_BUILD + NVAR_PER_HOUR*T

    def hv(t, k):
        return NVAR_BUILD + t*NVAR_PER_HOUR + k

    residual = demand - nuclear - exist_solar - CVOW_MW*wind_cf
    BUILD_SCALE = 1.0  # CORRECTED (2026-08-16), consistent with build_problem() -- see that function's
                        # comment for the full rationale.

    eq_rows, eq_cols, eq_data, eq_rhs = [], [], [], []
    row = 0

    # (A) energy balance -- discharge/charge from every sodium duration class
    for t in range(T):
        cols = [S_, hv(t,IDX['g']), hv(t,IDX['bd']), hv(t,IDX['bc'])]
        data = [solar_cf[t]*BUILD_SCALE, 1.0, 1.0, -1.0]
        for i in range(n_dur):
            cols += [hv(t,ND[i]), hv(t,NC[i])]; data += [1.0, -1.0]
        cols += [hv(t,IDX['fd']), hv(t,IDX['fc']), hv(t,IDX['unserved']), hv(t,IDX['curt'])]
        data += [1.0, -1.0, 1.0, -1.0]
        eq_rows += [row]*len(cols); eq_cols += cols; eq_data += data
        eq_rhs.append(residual[t]); row += 1

    # (B) Bath SoC (unchanged)
    init_bath = init_soc_frac*BATH_MWH
    for t in range(T):
        if t == 0:
            eq_rows += [row, row, row]; eq_cols += [hv(t,IDX['bsoc']), hv(t,IDX['bc']), hv(t,IDX['bd'])]
            eq_data += [1.0, -BATH_RTE_CHARGE, 1.0]; eq_rhs.append(init_bath)
        else:
            eq_rows += [row]*4; eq_cols += [hv(t,IDX['bsoc']), hv(t-1,IDX['bsoc']), hv(t,IDX['bc']), hv(t,IDX['bd'])]
            eq_data += [1.0, -1.0, -BATH_RTE_CHARGE, 1.0]; eq_rhs.append(0.0)
        row += 1
    eq_rows += [row]; eq_cols += [hv(T-1, IDX['bsoc'])]; eq_data += [1.0]; eq_rhs.append(init_bath); row += 1

    # (C) SoC dynamics for each sodium duration class
    for i in range(n_dur):
        for t in range(T):
            if t == 0:
                eq_rows += [row]*4; eq_cols += [hv(t,NSOC[i]), hv(t,NC[i]), hv(t,ND[i]), E_[i]]
                eq_data += [1.0, -NA_RTE_CHARGE, 1.0, -init_soc_frac*BUILD_SCALE]; eq_rhs.append(0.0)
            else:
                eq_rows += [row]*4; eq_cols += [hv(t,NSOC[i]), hv(t-1,NSOC[i]), hv(t,NC[i]), hv(t,ND[i])]
                eq_data += [1.0, -1.0, -NA_RTE_CHARGE, 1.0]; eq_rhs.append(0.0)
            row += 1
        eq_rows += [row, row]; eq_cols += [hv(T-1,NSOC[i]), E_[i]]; eq_data += [1.0, -init_soc_frac*BUILD_SCALE]
        eq_rhs.append(0.0); row += 1

    # (D) Iron-air SoC (unchanged)
    for t in range(T):
        if t == 0:
            eq_rows += [row]*4; eq_cols += [hv(t,IDX['fsoc']), hv(t,IDX['fc']), hv(t,IDX['fd']), EFE_]
            eq_data += [1.0, -FE_RTE_CHARGE, 1.0, -init_soc_frac*BUILD_SCALE]; eq_rhs.append(0.0)
        else:
            eq_rows += [row]*4; eq_cols += [hv(t,IDX['fsoc']), hv(t-1,IDX['fsoc']), hv(t,IDX['fc']), hv(t,IDX['fd'])]
            eq_data += [1.0, -1.0, -FE_RTE_CHARGE, 1.0]; eq_rhs.append(0.0)
        row += 1
    eq_rows += [row, row]; eq_cols += [hv(T-1,IDX['fsoc']), EFE_]; eq_data += [1.0, -init_soc_frac*BUILD_SCALE]
    eq_rhs.append(0.0); row += 1

    # (E) Cumulative gas tracking (unchanged)
    for t in range(T):
        if t == 0:
            eq_rows += [row, row]; eq_cols += [hv(t,IDX['gascum']), hv(t,IDX['g'])]; eq_data += [1.0, -0.001]
        else:
            eq_rows += [row]*3; eq_cols += [hv(t,IDX['gascum']), hv(t-1,IDX['gascum']), hv(t,IDX['g'])]
            eq_data += [1.0, -1.0, -0.001]
        eq_rhs.append(0.0); row += 1

    # (F) NEW -- duration lock per class: E_i - duration_i*P_i = 0 (exact fixed-duration product)
    for i, d in enumerate(durations):
        eq_rows += [row, row]; eq_cols += [E_[i], P_[i]]; eq_data += [1.0, -d]; eq_rhs.append(0.0); row += 1

    n_eq_rows = row
    A_eq = sparse.csr_matrix((eq_data, (eq_rows, eq_cols)), shape=(n_eq_rows, NVAR))
    b_eq = np.array(eq_rhs)

    ub_rows, ub_cols, ub_data, ub_rhs = [], [], [], []
    row = 0
    for t in range(T):
        for i in range(n_dur):
            ub_rows += [row,row]; ub_cols += [hv(t,NC[i]), P_[i]]; ub_data += [1.0,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
            ub_rows += [row,row]; ub_cols += [hv(t,ND[i]), P_[i]]; ub_data += [1.0,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
            ub_rows += [row,row]; ub_cols += [hv(t,NSOC[i]), E_[i]]; ub_data += [1.0,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['fc']), EFE_]; ub_data += [FE_DURATION,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['fd']), EFE_]; ub_data += [FE_DURATION,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1
        ub_rows += [row,row]; ub_cols += [hv(t,IDX['fsoc']), EFE_]; ub_data += [1.0,-BUILD_SCALE]; ub_rhs.append(0.0); row+=1

    if gas_allowed_frac is None:
        for t in range(T):
            ub_rows += [row]; ub_cols += [hv(t,IDX['g'])]; ub_data += [1.0]; ub_rhs.append(0.0); row += 1
    else:
        # CORRECTED (2026-08-16), same fix as build_problem() -- see that function's comment for the
        # full rationale.
        k = gas_allowed_frac/(1-gas_allowed_frac)
        clean_sum_const = np.sum(nuclear + exist_solar + CVOW_MW*wind_cf)
        ub_rows += [row, row]; ub_cols += [hv(T-1,IDX['gascum']), S_]; ub_data += [1.0, -k*BUILD_SCALE*np.sum(solar_cf)/1000.0]
        ub_rhs.append(k*clean_sum_const/1000.0); row += 1

    n_ub_rows = row
    A_ub = sparse.csr_matrix((ub_data, (ub_rows, ub_cols)), shape=(n_ub_rows, NVAR))
    b_ub = np.array(ub_rhs)

    bounds = [(0, None)]*NVAR
    for t in range(T):
        bounds[hv(t,IDX['bc'])] = (0, BATH_MW)
        bounds[hv(t,IDX['bd'])] = (0, BATH_MW)
        bounds[hv(t,IDX['bsoc'])] = (0, BATH_MWH)
        if gas_allowed_frac is None:
            bounds[hv(t,IDX['g'])] = (0, 0)

    c = np.zeros(NVAR)
    _na_year = na_year if na_year is not None else BUILD_YEAR
    energy_per_kwh, power_per_kw = na_power_energy_split(_na_year)
    c[S_] = CRF*SOLAR_CAPEX*1000 + SOLAR_OM*1000
    for i in range(n_dur):
        c[P_[i]] = CRF*power_per_kw*1000
        c[E_[i]] = CRF*energy_per_kwh*1000 + STOR_FOM_PCT*energy_per_kwh*1000
    c[EFE_] = (CRF*FE_ENERGY_CAPEX*1000 + STOR_FOM_PCT*FE_ENERGY_CAPEX*1000) * (1.0 - RESILIENCE_TILT_PCT)
    years_factor = T/8760.0
    c[S_] *= years_factor; c[EFE_] *= years_factor
    for i in range(n_dur):
        c[P_[i]] *= years_factor; c[E_[i]] *= years_factor
    c[S_] *= BUILD_SCALE; c[EFE_] *= BUILD_SCALE
    for i in range(n_dur):
        c[P_[i]] *= BUILD_SCALE; c[E_[i]] *= BUILD_SCALE
    _gas_price = GAS_COST_MWH if gas_price_mwh is None else gas_price_mwh
    for t in range(T):
        c[hv(t,IDX['g'])] = _gas_price
        c[hv(t,IDX['unserved'])] = UNSERVED_PENALTY
        c[hv(t,IDX['curt'])] = 0.01

    if verbose:
        print(f"T={T} NVAR={NVAR} n_eq={n_eq_rows} n_ub={n_ub_rows} durations={durations}")

    problem = dict(c=c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds,
                    IDX=IDX, hv_params=(NVAR_BUILD, NVAR_PER_HOUR), T=T, BUILD_SCALE=BUILD_SCALE,
                    S_=S_, P_=P_, E_=E_, EFE_=EFE_, durations=durations)
    return problem


def solve_problem(problem, solver_options=None, method='highs-ds'):
    # CORRECTED (2026-08-16): default was method='highs' (auto-select), which for a problem this large
    # chose HiGHS's interior-point method with a crossover step (confirmed via res.crossover_nit being
    # present). IPM+crossover can land anywhere within a degenerate optimal face largely independent of
    # small cost perturbations, unlike simplex, which pivots directly toward cost improvements -- forcing
    # dual simplex here specifically to make the model responsive to the tie-breaking costs added above.
    res = linprog(problem['c'], A_ub=problem['A_ub'], b_ub=problem['b_ub'],
                  A_eq=problem['A_eq'], b_eq=problem['b_eq'], bounds=problem['bounds'],
                  method=method, options=solver_options or {})
    return res
