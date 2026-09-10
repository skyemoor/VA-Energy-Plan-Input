"""
assumptions.py

SINGLE SOURCE OF TRUTH for every sourced financial/technology/policy parameter used across this
project's own scripts. Built 2026-08-23, directly prompted by a real, confirmed bug: two separate
CCGT capex definitions coexisted in lp_model.py (a stale $1,775/kW module-level constant alongside
a correct, later-built, well-sourced $3,000/kW function), and a downstream script kept calling the
stale one because nothing forced it to be updated. See Internal Debugging Log for the full incident.

DESIGN PRINCIPLE: exactly one definition per parameter, here, and nowhere else. Every other script
in this project imports from this module rather than defining its own local copy or re-deriving a
value. Flat, truly time-invariant parameters are plain constants; anything that varies by year is a
function of year, not a value baked in at one reference year and then silently stale everywhere else
(the exact shape of bug this module exists to prevent). Every entry keeps its own sourcing comment
inline -- moving a parameter here must not lose the reasoning behind its value.

lp_model.py imports every name it used to define locally from this module (`from assumptions import
*`), so existing code referencing `lp.SOLAR_CAPEX`, `lp.ccgt_capex_kw(y)`, etc. continues to work
unchanged. New code should prefer `import assumptions as asn` directly.
"""

# ============================================================================
# FINANCIAL
# ============================================================================
WACC = 0.045

# BASE_YEAR: this project's own fixed PV/discounting anchor year (2026), not a "sourced" external
# figure like WACC or CCGT capex -- it's a project convention rather than a market data point, and
# is not expected to vary across scenarios or sensitivities the way WACC might. Added here 2026-08-23
# after being found scattered as 17 separate, individually-consistent local copies across downstream
# scripts -- consistent today, but carrying the same structural risk as the CCGT bug (a value that
# must be updated everywhere at once if this project's own analysis year ever shifts, with nothing
# forcing that to happen). Centralized for that reason, not because its value is expected to change.
BASE_YEAR = 2026

CRF_LIFE_YEARS = 25  # solar/storage capital recovery period
CRF = WACC*(1+WACC)**CRF_LIFE_YEARS / ((1+WACC)**CRF_LIFE_YEARS - 1)

# CCGT-specific CRF, distinct from the 25-year figure above. Lazard's LCOE+ v19.0 (already in this
# project's knowledge base) sources CCGT's own facility life directly at 30 years -- using the
# 25-year figure for CCGT would misrepresent an asset this project has actual sourced data for.
# Same WACC, different amortization horizon.
CCGT_LIFE_YEARS = 30
CCGT_CRF = WACC*(1+WACC)**CCGT_LIFE_YEARS / ((1+WACC)**CCGT_LIFE_YEARS - 1)

BUILD_YEAR = 2044.5  # midpoint of the 2-year build window, used for cost-curve lookup convenience
                      # constants below -- NOT a substitute for calling the year-aware functions
                      # directly wherever a specific checkpoint/non-checkpoint year is known.

# ============================================================================
# CAPEX -- SOLAR
# ============================================================================
def solar_capex(y):
    """$/kW-AC, declining 1.5%/yr from a $1,474/kW 2026 base."""
    return 1474 * (1-0.015)**(y-2026)

# ============================================================================
# CAPEX -- CCGT (Scenario 2)
# ============================================================================
def ccgt_capex_kw(y):
    """
    Full installed project cost ($/kW), NOT turbine-equipment-only cost -- an important scope
    distinction, since the two differ by roughly 4x in the sourced data and are easy to conflate.

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
      Wood Mackenzie's converted turbine-only projection reaches by 2027.
    - GridLab/Energy Futures Group/Component Reliability Consultants/Halcyon (Sept 2025, via
      Latitude Media): pre-surge/near-term cost $1,116-1,427/kW, 2030-2031-vintage projects
      "routinely" $2,000/kW or more -- corroborates the same magnitude of increase, from a
      different, independent methodology.

    METHODOLOGY: flat $3,000/kW for all years, anchored to EPRI's most recent, directly-stated
    full-project figure. NOT extrapolated further upward or downward beyond this point --
    disclosed limitation, not an oversight. Wood Mackenzie explicitly diagnoses the current spike
    as a temporary manufacturing-capacity shortfall (110 GW of global orders against 60-70 GW/yr of
    capacity), not a permanent structural cost driver, with OEMs actively expanding capacity -- no
    sourced basis to assume continued escalation or reversion once that constraint eases, and this
    project's own checkpoints (earliest: 2030) all fall after Wood Mackenzie's own
    "supply crunch through 2027" window.

    CALL THIS FUNCTION, not a cached constant -- an earlier, stale $1,775/kW module-level constant
    (an average of Lazard's own, older $1,450-2,100/kW range) coexisted with this function for a
    period and was mistakenly used by downstream scripts; that constant has been removed entirely
    (not just deprecated) specifically to prevent this recurring. If this function is ever made
    genuinely year-varying, every caller updates automatically -- the entire reason to call it as a
    function even though it presently returns a flat value.
    """
    return 3000.0

CCGT_FOM_KW_YR = (10.00 + 25.50) / 2.0    # = $17.75/kW-yr, Lazard LCOE+ v19.0 "Gas Combined Cycle"
                                            # fixed-O&M range midpoint

# ============================================================================
# CAPEX -- SODIUM-ION STORAGE
# ============================================================================
def na_capex_kwh_6hr_ref(y):
    """$/kWh at a 6-hour duration reference (per the Assumptions & Sources tab, row 33 -- 6-hour was
    deliberately settled on as the best fit across a number of scenario runs, not 4-hour, despite an
    earlier mislabeling). $97.50/kWh 2026 base, declining toward $43.40/kWh by 2050."""
    return 97.50 * (43.40/97.50)**((y-2026)/24)

# Power/energy cost decomposition for sodium-ion, derived from NREL's 2025 utility-scale lithium-ion
# bottom-up cost model (Cole, Ramasamy, Turan, "Cost Projections for Utility-Scale Battery Storage:
# 2025 Update," NREL/TP-6A40-93281, June 2025), Figure 2 regression:
#   Total System Cost ($/kW) = $240.8/kWh * Duration(hr) + $379.16/kW   (2024$, R^2=0.9999)
# No sodium-ion-specific power/energy cost breakdown is publicly documented at this level of detail,
# so as a reasonable proxy this applies NREL's lithium-ion PROPORTIONAL power/energy cost SHARE (not
# the absolute $ figures) to this model's own sodium-ion reference price, at the 6-hr reference:
# energy share = (240.8*6)/(240.8*6+379.16) = 79.21%, power share = 20.79%.
# ASSUMPTION, not a sourced sodium-ion-specific figure -- flagged for review.
_NREL_ENERGY_SHARE_6HR = (240.8*6)/(240.8*6+379.16)   # 0.79210
_NREL_POWER_SHARE_6HR = 379.16/(240.8*6+379.16)       # 0.20790

def na_power_energy_split(y):
    """Returns (energy_$_per_kWh, power_$_per_kW), both duration-independent unit rates, derived by
    applying the NREL lithium-ion power/energy share above to this model's own sodium-ion 6-hr
    reference price at year y."""
    ref = na_capex_kwh_6hr_ref(y)
    energy_per_kwh = _NREL_ENERGY_SHARE_6HR * ref
    power_per_kw = _NREL_POWER_SHARE_6HR * 6.0 * ref
    return energy_per_kwh, power_per_kw

# ============================================================================
# CAPEX -- IRON-AIR STORAGE
# ============================================================================
def fe_capex_kwh(y):
    """$/kWh, source already quotes at 100-hr duration. $52.50/kWh 2026 base, declining toward
    $13.13/kWh (25% of base) by 2050."""
    return 52.50 * 0.25**((y-2026)/24)

# ============================================================================
# O&M
# ============================================================================
# NREL ATB 2022 base year, comprehensive scope: land lease, property tax, insurance, asset
# management, and security are all included, per NREL's own 2021 ATB documentation, which states
# these five categories were deliberately added that year based on LBNL industry-survey feedback
# that they were missing from the prior, narrower figure. Reconciled directly against Lazard's own
# $11-14/kW-yr and LBNL's own $11/kW-yr figures, both of which explicitly and intentionally exclude
# these same five categories by design -- not competing estimates of the same thing, two different
# scopes. This project's model has no separate line items for insurance/land/admin costs on
# utility-scale solar, so this figure must function as an all-in proxy -- $24, not the narrower
# $11-14, is the correct reference for that purpose. See Assumptions tab for the full three-source
# reconciliation.
SOLAR_OM = 24.0        # $/kW-yr
STOR_FOM_PCT = 0.025   # %/yr of capex

# ============================================================================
# STORAGE OPERATING PARAMETERS
# ============================================================================
BATH_MW = 3000.0
BATH_MWH = 24000.0
BATH_RTE_CHARGE = 0.80
NA_RTE_CHARGE = 0.90
NA_CYCLE_LIFE = 15000   # default/fallback; driver.set_year_capex() overrides per checkpoint year
                         # (10,000 pre-2035, 15,000 2035+, per project direction 2026-08-16)
FE_CYCLE_LIFE = 1000    # Form Energy-specific published figure ("maintained over 80% capacity after
                         # more than 1,000 cycles"), held constant across all years -- no established
                         # improvement trajectory the way Na-ion has one
FE_DOD = 1.0             # iron-air gets no DoD restriction -- see na_cycling_cost/fe_cycling_cost
                         # note in lp_model.build_problem() for the sourcing behind this asymmetry
NA_DOD_FLOOR = 0.20      # sodium-ion: standard industry convention -- "80% DoD" means discharging
                         # FROM 100% down to a 20% floor, not to 0%

RESILIENCE_TILT_PCT = 0.03  # SYNCHRONIZED 2026-09-10 from 0.0. This module had been left at the old
                            # held-at-zero value after lp_model.py reinstated 0.03 on 2026-09-04
                            # (RBD trial, Internal Debugging Log #20.6, concluded -- removing the reason
                            # it was held at zero). lp_model.py's copy is the one the LP actually reads
                            # (applied to IRON_AIR_ENERGY_MWH's objective coefficient), so solved results
                            # were never wrong; but any caller importing THIS module's copy would have
                            # silently received 0.0. Found 2026-09-10 by a direct value-by-value
                            # comparison of every constant shared between the two modules: 24 agreed,
                            # this one did not. Exactly the divergence Rule 6.2 exists to catch, and the
                            # same class of defect as Internal Debugging Log #49. A runtime assertion at
                            # the foot of this module now cross-checks the two rather than trusting them
                            # to stay in step by convention.

def iron_air_rte(year):
    """Linear round-trip-efficiency improvement: 45% (2026) -> 80% (2033), held flat after."""
    if year <= 2026:
        return 0.45
    if year >= 2033:
        return 0.80
    return 0.45 + (0.80-0.45)*(year-2026)/(2033-2026)

FE_DURATION = 100.0

# ============================================================================
# GAS -- HEAT RATES
# ============================================================================
SIMPLE_CYCLE_HEAT_RATE = 9.5  # MMBtu/MWh HHV, GE 7F.05 simple-cycle spec (8,580-8,610 Btu/kWh LHV,
                               # x1.108 LHV->HHV) -- Scenario 1/3/1B/3B/3C fleet
CCGT_HEAT_RATE = 6.4          # MMBtu/MWh HHV, GE 7F.05 combined-cycle spec (5,660 Btu/kWh LHV,
                               # x1.108) -- Scenario 2, genuinely CCGT-based

CCGT_VOM_MWH = 3.00  # $/MWh, established value (Lazard LCOE+ v19.0) -- Scenario 2 only; Scenario
                      # 1/3/1B/3B's gas dispatch has historically been priced as fuel-cost-only

# ============================================================================
# GAS -- PRICE CASES
# ============================================================================
def gas_cost_mwh(year, heat_rate=None):
    """
    Deloitte-derived fuel cost -- the BASE/MEDIUM case, matching the trajectory Scenario 2 uses.
    Piecewise-linear interpolation between Deloitte's own $/MMBtu data points ($3.70 2026, $5.40
    2030, $6.35 2040, $7.50 2050 extrapolated -- see Assumptions tab).

    heat_rate has NO default and must be supplied by the caller -- there is no single correct
    default, since Scenario 2 is CCGT (CCGT_HEAT_RATE) while Scenario 1/3/1B/3B/3C are simple-cycle
    only (SIMPLE_CYCLE_HEAT_RATE). Does NOT include CCGT VOM -- add CCGT_VOM_MWH separately for
    Scenario 2.
    """
    if heat_rate is None:
        raise ValueError(
            "gas_cost_mwh() requires an explicit heat_rate -- pass SIMPLE_CYCLE_HEAT_RATE for "
            "Scenario 1/3/1B/3B/3C or CCGT_HEAT_RATE for Scenario 2. There is no safe default."
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
    """EIA-derived fuel cost, the LOW gas price case. Same 2026 starting point ($3.70/MMBtu) as the
    Deloitte case, diverging afterward: $3.80 (2030), $4.20 (2040), $4.95 (2050 extrapolated). Fixed
    CCGT_HEAT_RATE (6.4). Does NOT include CCGT VOM -- add separately."""
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
    Hughes/Post Carbon Institute (2021, "Shale Reality Check") fuel cost, the HIGH gas price case --
    a genuinely different, depletion-driven thesis (Marcellus/Utica shale gas production peaks
    2030-2033, then declines at a 3.2%/yr terminal rate), not just a different number on the same
    curve shape as the other two cases.

    Only two data points sourced directly: $3.50/MMBtu (2026), $11.50/MMBtu (2050). Interpolated via
    constant compound annual growth rate (~5.08%), a smooth mathematical fit through two real
    endpoints, not a year-by-year forecast attempting the source's own peak-then-decline shape.

    Flagged elsewhere in this project as "the least current of the three [gas price cases], retained
    for range context" -- Hughes 2021 predates the more recent EIA/Deloitte forecasts. Does NOT
    include CCGT VOM -- add separately.
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
    Fourth reference case -- assessed alongside Deloitte/EIA/Hughes, not adopted as this project's
    Base/Low/High tier structure. Bernstein Research's "Americas Natural Gas Outlook" (2026 edition,
    Dec 2025): $5.00/mcf Henry Hub as the new structural mid-cycle equilibrium. Cross-verified across
    multiple independent outlets, all reporting the same figure and the same LNG-export/data-center
    thesis.

    Methodologically different from the other three: a single equilibrium level, not a multi-decade
    trajectory -- returns a FLAT rate for all years by default. Set high_case=True for Bernstein's
    own bullish-risk scenario ($8-10/mcf, midpoint $9.00 used).

    Unit conversion: $/mcf -> $/MMBtu via the standard EIA factor (1.037 MMBtu/mcf).
    Does NOT include CCGT VOM -- add separately. Uses CCGT_HEAT_RATE (6.4) by default.
    """
    mcf = 9.00 if high_case else 5.00
    mmbtu = mcf / 1.037
    heat_rate = 6.4
    return mmbtu * heat_rate

# ============================================================================
# RGGI
# ============================================================================
# Regulatory-schedule tier (the figure actually used throughout this project's own SLCOE-with-RGGI
# work) -- RGGI's own published Cost Containment Reserve trigger-price schedule, a conservative
# reference point. Current-market tier retained for context/footnote only: RGGI's own actual
# market-clearing price has run above this schedule since Virginia's July 2026 re-entry (most recent
# auction, Auction 72 June 2026: $35.00/ton flat).
RGGI_REGULATORY_SCHEDULE_2026 = 18.22
RGGI_REGULATORY_SCHEDULE_2027 = 19.50
RGGI_REGULATORY_SCHEDULE_ESCALATION = 1.07
RGGI_CURRENT_MARKET_FLAT = 35.00  # $/ton, Auction 72, June 2026, held flat throughout (footnote tier)

def rggi_regulatory_schedule_price(year):
    if year <= 2026:
        return RGGI_REGULATORY_SCHEDULE_2026
    return RGGI_REGULATORY_SCHEDULE_2027 * (RGGI_REGULATORY_SCHEDULE_ESCALATION ** (year - 2027))

def rggi_current_market_price(year):
    return RGGI_CURRENT_MARKET_FLAT

# ============================================================================
# EXPORT / TRANSMISSION
# ============================================================================
# $45/MWh EIA average LMP x 1.40 DOM-zone structural premium (DOM has priced ~40% above the
# PJM-RTO average every year 2021-2025, data-center-driven, structurally widening) x 0.60 midday
# discount (applies to raw, unmanaged surplus export specifically, which genuinely clusters at
# midday -- NOT to a well-timed, storage-backed owner's own dispatch; see the Recommended Program
# component list, which deliberately does not apply this discount for exactly that reason).
EXPORT_AVG_PRICE = 37.80  # $/MWh, price LEVEL only -- hour-to-hour SHAPE is set separately via the
                           # LP-derived seasonal shape mechanism in lp_model.py, not a synthetic
                           # assumption

EXPORT_CAP_MW = 5000.0  # A STATIC PROXY for a fundamentally dynamic reality, not a researched
                         # Dominion transmission/interconnection figure -- introduced originally to
                         # prevent unbounded LP export arbitrage. Real power flow between Dominion
                         # and neighboring zones is governed by continuously-recalculated thermal,
                         # voltage, and stability constraints across specific interfaces (N-1
                         # contingency analysis across the whole topology), not a single scalar. This
                         # project's entire hourly LP treats the system as one "copper-plate" node
                         # with no internal transmission structure -- representing this accurately
                         # would require actual line-level topology and full AC power-flow modeling,
                         # genuinely out of this LP's own framework. Any curtailment or export-revenue
                         # figure downstream of this constraint inherits this limitation directly.

# ============================================================================
# EXISTING ASSETS
# ============================================================================
EXIST_SOLAR_MW_2026 = 5300.0
SOLAR_DEGRADATION_RATE_ANNUAL = 0.005  # standard c-Si industry figure (~0.5%/yr)

def solar_degradation_factor(years_elapsed):
    """Multiplicative factor for solar nameplate capacity after years_elapsed years of degradation."""
    return (1 - SOLAR_DEGRADATION_RATE_ANNUAL)**years_elapsed

def exist_solar_mw(year):
    return EXIST_SOLAR_MW_2026 * solar_degradation_factor(year-2026)

CVOW_MW = 2587.2  # Real nameplate: 176 x 14.7 MW Siemens Gamesa SG 14-222 DD (Power Boost) turbines.
                   # (Corrected from an earlier 2,535.0 MW SAM-proxy-turbine-count figure.)

# ============================================================================
# SOCIAL COST FIGURES (Tier 1/2/3)
# ============================================================================
# EPA Dec 2023 Social Cost of Greenhouse Gases report (pre-dating a Jan 2025 executive-branch policy
# change withdrawing these estimates as governmental policy) -- this project uses the pre-2025
# peer-reviewed methodology as a deliberate, documented policy choice. 2020$ base year.
SC_CO2_2020USD = 190.0       # $/ton, central estimate, 2% discount rate
SC_CH4_2020USD = 1600.0      # $/ton
SC_N2O_2020USD = 5400.0      # $/ton

# CPI deflators to this project's own 2026$ base year (BLS historical table + BLS Jul 2026 release,
# CPI-U 333.918): 2020 avg CPI-U = 258.811.
CPI_DEFLATOR_2020_TO_2026 = 1.2902

# EPA BenMAP/COBRA benefit-per-ton, area-source category, 2016$ base year (2016 avg CPI-U = 240.007).
PM25_BENEFIT_PER_TON_2016USD = 350000.0
SO2_BENEFIT_PER_TON_2016USD = 54000.0
NOX_BENEFIT_PER_TON_2016USD = 8600.0
CPI_DEFLATOR_2016_TO_2026 = 1.3913

print(f"[assumptions.py] SOLAR_CAPEX(${BUILD_YEAR})=${solar_capex(BUILD_YEAR):.1f}/kW  "
      f"CCGT_CAPEX=${ccgt_capex_kw(BUILD_YEAR):.1f}/kW  CRF={CRF:.5f}")


# ============================================================================
# STATUTORY PARAMETERS -- Va. Code § 56-585.5
# ============================================================================
#
#   *** READ BEFORE CHANGING ANY VALUE IN THIS BLOCK ***
#
# These are figures the LAW currently specifies, not modeling judgments. Changing one does NOT
# model Virginia as it is -- it models Virginia under a HYPOTHETICAL AMENDMENT to § 56-585.5.
#
# They are deliberately mutable, because this project's own purpose includes evaluating whether
# the statute should be amended and what such an amendment would cost. Scenario 1B (Build to Zero,
# 2045 Gas Exception) is exactly that case: it relaxes the 2045 requirement from 100% to 95%,
# which is a legislative recommendation, not a fact about current law.
#
# THEREFORE: any result computed with a changed value here MUST be labelled as modeling a proposed
# statutory change, never as compliance with existing law. The verbatim text of every provision
# below is in docs/statutes/56-585.5.md -- check it before altering a value, and record the
# rationale in the relevant scenario's technical notes.
#
# Values below reflect the statute as amended through 2026 (cc. 43, 512, 645, 646, 694, 695,
# 733, 734), including HB 895 / SB 448.
# ============================================================================

# § 56-585.5(D)(5) -- deficiency payments. An economic CEILING on compliance cost: a utility
# facing higher build costs may lawfully pay these instead of building.
DEFICIENCY_PAYMENT_BASE_RATE_PER_MWH = 45.0
DEFICIENCY_PAYMENT_SUB_ONE_MW_RATE_PER_MWH = 75.0      # sub-1 MW VA solar/wind/anaerobic shortfalls
DEFICIENCY_PAYMENT_GEOTHERMAL_RATE_PER_MWH = 100.0     # § C.1.b geothermal shortfalls
DEFICIENCY_PAYMENT_BASE_YEAR = 2021
DEFICIENCY_PAYMENT_ANNUAL_ESCALATION = 0.01            # "shall increase by one percent annually"

# § 56-585.5(A) -- accelerated clean energy buyer threshold. Aggregate load, prior calendar year.
# Opt-in: exceeding this does not itself remove load from the compliance base; the customer must
# contract under subsection G AND be certified by the Commission.
ACCELERATED_CLEAN_ENERGY_BUYER_THRESHOLD_MW = 25.0

# § 56-585.5(C)(3) -- minimum share of RECs from resources located in the Commonwealth.
IN_COMMONWEALTH_REC_MINIMUM_SHARE = 0.75
IN_COMMONWEALTH_REC_MINIMUM_FIRST_YEAR = 2027

# § 56-585.5(C)(2) -- distributed carve-out: share of the RPS requirement that must come from
# solar/wind/anaerobic digestion resources of one megawatt or less located in Virginia.
DISTRIBUTED_CARVE_OUT_SHARE_2026_THROUGH_2030 = 0.045
DISTRIBUTED_CARVE_OUT_SHARE_2031_THROUGH_2045 = 0.05

# § 56-585.5(E)(6) -- maximum size of any single energy storage project.
MAX_SINGLE_STORAGE_PROJECT_MW = 500.0
MAX_SINGLE_STORAGE_PROJECT_PHASE_II_MW = 800.0

# § 56-585.5(D)(2) -- Phase II solar/onshore wind requirement by December 31, 2035.
STATUTORY_SOLAR_TARGET_MW = 16100.0
STATUTORY_SOLAR_PREVIOUSLY_DEVELOPED_SITE_MIN_MW = 1000.0   # parking lots and canopies qualify


# ============================================================================
# RELIABILITY AND CAPACITY ACCREDITATION
# ============================================================================
# PJM Installed Reserve Margin. Applied uniformly across scenarios -- see
# docs/methodology/ for the Statutory Floor asymmetry this corrected.
INSTALLED_RESERVE_MARGIN = 0.177

# Number of highest-net-demand hours used for own-data capacity credit, per Appendix A.13
# Algorithm 1 step 2. A methodological choice, not a sourced figure.
CAPACITY_CREDIT_PEAK_HOURS_COUNT = 10

# Contiguous stress-window length for gas-outage testing. 144 hours = 6 days, matching this
# project's own six-day-lookahead firming methodology rather than an arbitrary duration.
GAS_OUTAGE_STRESS_WINDOW_HOURS = 144


# ============================================================================
# DISTRIBUTED SEGMENT -- physical bounds
# ============================================================================
# Distributed solar siting cap, DOM zone. Derived 2026-09-10 by re-basing the four-county NoVA
# assessment (Prince William parking re-anchored to C&I footprint) and extrapolating statewide at
# 0.93 kW/capita EXCLUDING Loudoun, whose data-center density is not representative.
# See docs/methodology/Demand_Basis_and_RPS_Compliance_Working_Notes.md § 13.
DOM_ZONE_DISTRIBUTED_SOLAR_CAP_MW = 7440.0

# Distributed storage pairing, from this project's own parking-canopy convention: 1:1 MW with
# distributed solar, 4-hour duration. Structurally excludes iron-air from the distributed segment,
# since FE_DURATION=100 cannot satisfy a 4-hour duration -- which is also the physically right
# answer, iron-air being a utility-scale rather than rooftop technology.
DISTRIBUTED_STORAGE_DURATION_HR = 4.0
DISTRIBUTED_STORAGE_POWER_RATIO_TO_SOLAR = 1.0


# ============================================================================
# STORAGE CYCLING REQUIREMENTS
# ============================================================================
# Annual cycle requirements for the charging-adequacy constraint. DISCLOSED MODELING CHOICES, not
# sourced constants -- see lp_package/charging_adequacy.py for the full reasoning. Deliberately
# per-technology: iron-air's ~1,000-cycle demonstrated life (FE_CYCLE_LIFE, citation C122) over a
# ~25-year life is ~40 cycles/year, so requiring it to cycle at a sodium-ion-like daily rate would
# consume its entire rated life in under three years.
NA_CYCLES_PER_YEAR_REQUIREMENT = 200.0    # well inside sodium-ion's own ~500-600/yr envelope (C119)
FE_CYCLES_PER_YEAR_REQUIREMENT = 40.0


# ============================================================================
# CAPEX -- SIMPLE-CYCLE PEAKERS (VCEA scenarios)
# ============================================================================
# Full INSTALLED PROJECT cost ($/kW), not turbine-equipment-only -- the two differ by roughly 4x.
# Used by the VCEA scenarios (Build to Zero, 2045 Gas Exception, Distributed Build), where gas is
# a residual gap-filler and cycling wear makes simple-cycle correct. The Statutory Floor uses
# ccgt_capex_kw() instead, its gas running at 42-58% capacity factor -- see
# docs/methodology/Gas_Technology_Selection_By_Scenario.md.
#
# Two independent derivations converge here: Wood Mackenzie's April 2026 equipment figure
# ($600/kW by end-2027) converted at the SIMPLE-CYCLE equipment share of 40-50% (versus 20-30% for
# combined cycle) gives $1,200-1,500/kW; GridLab's September 2025 survey of project filings
# reports CT projects completing 2026-2027 at $1,116-1,427/kW. Size tiering from USP&E April 2026.
#
# VOLATILE. Global orders reached 110 GW against 60-70 GW/yr manufacturing capacity; EPRI's
# combined-cycle figure moved $2,000 -> $3,000/kW in six months. The 'high' case is not a tail
# scenario, and checkpoints beyond ~2030 need an explicit escalation assumption rather than these
# held flat.
PEAKER_SMALL_TIER_MAX_MW = 50.0
PEAKER_MEDIUM_TIER_MAX_MW = 250.0
PEAKER_CAPEX_KW_BY_TIER = {
    'small':  {'low': 1400.0, 'central': 1750.0, 'high': 2400.0},   # <= 50 MW
    'medium': {'low': 1116.0, 'central': 1425.0, 'high': 1900.0},   # 50-250 MW
    'large':  {'low':  950.0, 'central': 1250.0, 'high': 1700.0},   # > 250 MW
}
PEAKER_DUAL_FUEL_ADDER_KW = 200.0            # USP&E: $150-250/kW, midpoint
PEAKER_FAST_TRACK_PREMIUM_FRACTION = 0.15    # USP&E: 10-20% for delivery under 18 months


# ---------------------------------------------------------------------------
# Rule 6.2 cross-check: this module and lp_model.py legitimately both define these values --
# lp_model.py needs them at import time for its own objective construction, and this module is the
# project-wide source of truth. Rather than trusting them to stay in sync by convention, assert it.
#
# Added 2026-09-10 after finding RESILIENCE_TILT_PCT had silently diverged (0.0 here, 0.03 there)
# for six days. Internal Debugging Log #49 documents the same class of defect costing a full
# Scenario 2 re-run across three gas cases with and without RGGI.
#
# Deliberately raises at import rather than warning: a divergence here means some caller is
# already receiving a wrong number, and which caller is not knowable from this module.
# ---------------------------------------------------------------------------
def _assert_consistent_with_lp_model():
    try:
        import lp_model
    except ImportError:
        return  # lp_model not importable in this context; nothing to check against
    shared_scalars = [
        'WACC', 'CRF', 'CCGT_CRF', 'CCGT_LIFE_YEARS', 'BUILD_YEAR', 'CVOW_MW',
        'BATH_MW', 'BATH_MWH', 'BATH_RTE_CHARGE', 'NA_RTE_CHARGE', 'NA_CYCLE_LIFE',
        'NA_DOD_FLOOR', 'FE_CYCLE_LIFE', 'FE_DOD', 'FE_DURATION', 'RESILIENCE_TILT_PCT',
        'SOLAR_OM', 'STOR_FOM_PCT', 'SOLAR_DEGRADATION_RATE_ANNUAL', 'EXIST_SOLAR_MW_2026',
        'SIMPLE_CYCLE_HEAT_RATE', 'CCGT_HEAT_RATE', 'CCGT_FOM_KW_YR',
        'EXPORT_AVG_PRICE', 'EXPORT_CAP_MW',
    ]
    divergent = []
    for name in shared_scalars:
        if not hasattr(lp_model, name):
            continue
        here, there = globals()[name], getattr(lp_model, name)
        if abs(float(here) - float(there)) > 1e-9:
            divergent.append(f"{name}: assumptions.py={here!r} lp_model.py={there!r}")
    if divergent:
        raise AssertionError(
            "assumptions.py and lp_model.py have diverged on shared constants -- some caller is "
            "already receiving a wrong value:\n  " + "\n  ".join(divergent) +
            "\nResolve by determining which is current (check each module's own change note) and "
            "synchronizing, rather than deleting this assertion.")


_assert_consistent_with_lp_model()
