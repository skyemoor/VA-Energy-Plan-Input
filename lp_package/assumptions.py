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
import os

# Import-time banner. Routed through a module-level flag rather than a bare print() so a caller can
# silence it (2026-09-10): these lines interleaved with run_all.py's own progress output, appearing
# mid-stage and making a clean run look like something had gone wrong. They remain ON by default,
# because a modeler importing this module interactively benefits from seeing which capex vintage is
# in force -- that is genuinely useful and was the reason they were added.
#
# Set VA_ENERGY_QUIET_IMPORT=1 in the environment, or assumptions.QUIET_IMPORT = True before
# import, to suppress.
QUIET_IMPORT = os.environ.get('VA_ENERGY_QUIET_IMPORT', '') == '1'


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
SIMPLE_CYCLE_HEAT_RATE = 9.5

# ---------------------------------------------------------------------------
# GAS MERIT ORDER -- heat rate tiers (MMBtu/MWh)
# ---------------------------------------------------------------------------
# Added 2026-09-11. The LP currently dispatches gas at a SINGLE marginal cost
# (GAS_COST_MWH), which is one of the reasons its hourly energy-balance dual is
# perfectly flat: with one price and no operating reserve, storage arbitrages
# every hour to that price. A merit order gives the dual a ladder to climb.
#
# SOURCE: EIA Electric Power Annual Table 8.2, "Average Tested Heat Rates by
# Prime Mover and Energy Source", Form EIA-860, capacity-weighted, 2024 values
# unless noted. Vintage splits from EIA Today in Energy #61444 and #60984.
#
#   Natural gas, 2024 (Table 8.2)
#     Combined Cycle        7,548 Btu/kWh
#     Gas Turbine          10,999 Btu/kWh
#     Steam Generator      10,337 Btu/kWh
#     Internal Combustion   8,924 Btu/kWh
#
#   CCGT by vintage (Today in Energy)
#     2014-2023 entry      < 7,000 Btu/kWh
#     2010-2022 entry        6,960 Btu/kWh (2022)
#     2000-2009 entry        7,479 Btu/kWh (2022)
#     1990-1999 entry       ~9,010 Btu/kWh (17% above the 2000-2009 cohort)
#
# A FINDING WORTH RECORDING: SIMPLE_CYCLE_HEAT_RATE = 9.5 above is 14% BETTER
# than EIA's 2024 gas-turbine fleet average of 11.0. 9.5 describes a modern
# aeroderivative unit, not the fleet. Where the question is what the marginal
# peaking unit actually costs to run, 11.0 is the better figure and 9.5 is
# optimistic. Both are retained as separate tiers rather than one being
# corrected into the other, because they describe genuinely different machines.
GAS_HEAT_RATE_CCGT_MODERN = 6.4          # 2014+ entry; our own, consistent with EIA "< 7.0"
GAS_HEAT_RATE_CCGT_FLEET = 7.548         # EIA Table 8.2, 2024 combined cycle
GAS_HEAT_RATE_CCGT_LEGACY = 9.01         # EIA, 1990-1999 entry cohort
GAS_HEAT_RATE_CT_AERODERIVATIVE = 9.5    # = SIMPLE_CYCLE_HEAT_RATE; modern aero unit
GAS_HEAT_RATE_CT_FLEET = 10.999          # EIA Table 8.2, 2024 gas turbine
GAS_HEAT_RATE_STEAM = 10.337             # EIA Table 8.2, 2024 gas steam generator

#: Merit order, cheapest first. Tuples of (label, heat_rate). Capacity per tier
#: is NOT set here -- a merit order needs MW at each rung, and the Virginia
#: fleet split is not yet sourced. See docs/methodology/Gas_Merit_Order.md.
GAS_MERIT_ORDER_HEAT_RATES = (
    ('ccgt_modern', GAS_HEAT_RATE_CCGT_MODERN),
    ('ccgt_fleet', GAS_HEAT_RATE_CCGT_FLEET),
    ('ccgt_legacy', GAS_HEAT_RATE_CCGT_LEGACY),
    ('ct_aeroderivative', GAS_HEAT_RATE_CT_AERODERIVATIVE),
    ('ct_fleet', GAS_HEAT_RATE_CT_FLEET),
)

#: Capacity per rung, MW NAMEPLATE. Source: EIA-860 2025, Schedule 3 (Generator Data),
#: Virginia file, Operable sheet, filtered to Energy Source 1 = NG and Utility Name =
#: Virginia Electric & Power Co. Rungs assigned by per-unit Operating Year.
#:
#: REBUILT 2026-09-12 on generator-level data, replacing a mapping derived from the
#: Dominion 10-K. The 10-K gave NET SUMMER CAPABILITY (8,195 MW); this gives NAMEPLATE
#: (9,359.5 MW). Same fleet, different rating basis -- 8,195/9,359.5 = 87.6%, a normal
#: summer derate. Mixing the two bases created a phantom 1,167 MW discrepancy against
#: VA_gas_capacity_schedules.md Schedule A (9,362 MW), now resolved: Schedule A is
#: Dominion-owned gas at NAMEPLATE and agrees to within 2.5 MW (rounding).
GAS_MERIT_ORDER_CAPACITY_MW = {
    'ccgt_modern': 4_717.7,    # 12 units, operating year >= 2014
    'ccgt_fleet': 1_172.0,     # 6 units, 2000-2013
    'ccgt_legacy': 747.0,      # 8 units, pre-2000
    'ct_fleet': 2_722.8,       # 20 units, ALL FRAME -- see GAS_CT_SPLIT_RESOLVED
}
GAS_DOMINION_OWNED_NAMEPLATE_MW = 9_359.5
GAS_DOMINION_OWNED_NET_SUMMER_MW = 8_195.0   # 10-K basis, retained for cross-reference

#: RESOLVED 2026-09-12. The simple-cycle fleet is entirely frame-class, established from
#: per-unit nameplate rather than inferred: Ladysmith 5 x 178.5 MW (2001, 2008-09),
#: Remington 4 x 170-178.5 (2000), Elizabeth River 3 x 129.6 (1992), Gravel Neck
#: 4 x 91.9 (1989), Darbytown 4 x 92.1 (1990). Aeroderivative machines are 36-54 MW
#: (LM6000 is 44.5-53.8); not one Dominion unit is in that class. Statewide, 91.9% of
#: Virginia simple-cycle capacity is frame (4,426 of 4,814 MW), with 388 MW in eight
#: units under 60 MW -- none of it Dominion's.
GAS_CT_SPLIT_RESOLVED = (
    'Dominion simple-cycle capacity is 100% FRAME class, confirmed from EIA-860 '
    'per-unit nameplate (92-178.5 MW units; aeroderivatives are 36-54 MW). Use '
    'GAS_HEAT_RATE_CT_FLEET (10.999). GAS_HEAT_RATE_CT_AERODERIVATIVE (9.5) remains '
    'defined for NEW-BUILD analysis where a specific machine is chosen, and must not be '
    'applied to the existing fleet.')

#: CT variable O&M, $/MWh. SOURCE: NREL Annual Technology Baseline -- ATB 2022 gives
#: NGCC $2.00 and NGCT $5.00/MWh; ATB 2020 gives CCGT $1.61 and OCGT $4.49. Both put CT
#: VOM at roughly 2.5-2.8x CCGT, reflecting more starts and more cycling wear.
#:
#: NOTE AN INCONSISTENCY, recorded rather than silently reconciled: CCGT_VOM_MWH = 3.0
#: above sits ABOVE ATB's $2.00 for the same technology. Taking CT at ATB's $5.00 while
#: CCGT stays at 3.0 narrows the ratio to 1.67x. Scaling our own CCGT figure by the ATB
#: ratio would instead give ~$7.50. The ATB absolute is used because it is the sourced
#: figure; the CCGT constant's own provenance should be revisited.
#:
#: MATTERS BECAUSE ct_fleet IS THE PRICE-SETTING RUNG. Using CCGT's 3.0 for peakers
#: understated their marginal cost, compounding with the heat-rate finding (the fleet is
#: frame at 11.0, not aeroderivative at 9.5). Both errors ran the same direction.
CT_VOM_MWH = 5.0

#: Per-plant capacity by merit-order rung, three rating bases. Source: EIA-860 2025
#: Schedule 3 (Generator Data), Virginia, Operable sheet, Energy Source 1 = NG.
#:
#: SCOPE EXPANDED 2026-09-12 from Dominion-owned to ALL DOM-ZONE MERCHANT GAS, by
#: decision. Potomac Energy Center sits close to the Loudoun data-center concentration
#: and will be dispatched whenever prices allow -- and prices have been high -- so
#: restricting the stack to Dominion-owned plant would omit capacity that genuinely
#: serves zonal load. Doswell, Marsh Run (ODEC), Louisa (ODEC) and Gordonsville are in
#: for the same reason.
#:
#: TWO FILTERS APPLIED, both deliberate:
#:   APCo TERRITORY EXCLUDED -- Clinch River, Wolf Hills, Buchanan and the southwest
#:   Virginia industrial units are in Appalachian Power's zone, not DOM. Filtered by
#:   county, since EIA-860 carries no PJM zone field.
#:   CHP EXCLUDED -- Industrial and IPP CHP (Celanese, Radford Army Ammunition, Hopewell
#:   Cogeneration, Virginia Tech, Spruance, Park 500, Georgia-Pacific, HP Hood, Elkton)
#:   run to serve host steam loads, not economic dispatch. Including them in a merit
#:   order would imply a dispatch decision their operators do not make.
#:
#: THREE BASES, all retained. Mixing nameplate with net summer created a phantom
#: 1,167 MW discrepancy on 2026-09-11 and produced two wrong hypotheses before the units
#: were checked. Naming all three prevents a repeat.
#:   nameplate      manufacturer rating at ISO conditions (59F, sea level)
#:   net summer     sustained output at summer ambient (~95F), net of station service
#:   net winter     same at winter ambient -- HIGHER for gas, since cold dense air
#:                  raises compressor mass flow
#:
#: WINTER EXCEEDS SUMMER BY 11.4% fleet-wide (10,596 vs 9,512 MW). That matters here:
#: the DOM zone's winter peak (25,413 MW, 2025-26) now EXCEEDS its summer peak (23,905
#: MW, 2025), and winter has grown far faster (+45% since 2019-20 against +23%). If the
#: binding hour is a winter evening -- which a high-solar system makes likely -- then net
#: SUMMER is the wrong derate and understates available gas at the hour that sizes the
#: fleet.
#:
#: THE COUNTER-ARGUMENT, recorded because it is not modelled: winter CAPABILITY is not
#: winter DELIVERABILITY. Pipeline constraints and competition with heating load can make
#: gas unavailable in a cold snap regardless of what the turbine could produce. That is a
#: fuel-supply constraint, and this project models neither it nor storage of fuel on site.
#: Using net winter without that caveat would overstate cold-snap gas availability.
GAS_PLANT_CAPACITY_MW = {
    # plant: (rung, nameplate, net_summer, net_winter)
    'Greensville County Power Station': ('ccgt_modern', 1_773.3, 1_605.0, 1_727.3),
    'Warren County':                    ('ccgt_modern', 1_472.2, 1_370.0, 1_485.0),
    'Brunswick County Power Station':   ('ccgt_modern', 1_472.2, 1_376.0, 1_511.8),
    'Ladysmith':                        ('ct_fleet',      892.5,   789.0,   935.0),
    'Remington':                        ('ct_fleet',      705.5,   614.0,   760.0),
    'Possum Point':                     ('ccgt_fleet',    613.0,   571.0,   630.0),
    'Marsh Run Generation Facility':    ('ct_fleet',      597.0,   484.0,   576.0),
    'Bear Garden':                      ('ccgt_fleet',    559.0,   628.0,   644.0),
    'Louisa Generation Facility':       ('ct_fleet',      546.0,   466.0,   555.0),
    'Chesterfield':                     ('ccgt_legacy',   446.6,   386.0,   466.0),
    'Elizabeth River Power Station':    ('ct_fleet',      388.8,   325.0,   351.0),
    'Darbytown':                        ('ct_fleet',      368.4,   340.0,   359.0),
    'Gravel Neck':                      ('ct_fleet',      367.6,   340.0,   356.0),
    'Gordonsville Energy LP':           ('ccgt_legacy',   300.4,   218.0,   240.0),
    'Martinsville LFG Generator':       ('ccgt_fleet',      1.1,     1.0,     1.0),
}
GAS_DOM_ZONE_NAMEPLATE_MW = 10_503.6
GAS_DOM_ZONE_NET_SUMMER_MW = 9_513.0
GAS_DOM_ZONE_NET_WINTER_MW = 10_596.1

GAS_SEASONAL_BASIS_NOTE = (
    'Net WINTER capability exceeds net SUMMER by 11.4% fleet-wide (10,596 vs 9,512 MW), '
    'because cold dense air raises compressor mass flow. The DOM zone now peaks in '
    'WINTER (25,413 MW in 2025-26 against 23,905 MW summer 2025, winter growing +45% '
    'since 2019-20 against +23%), so net summer may be the wrong derate for the binding '
    'hour. NOT MODELLED and cutting the other way: winter capability is not winter '
    'DELIVERABILITY -- pipeline constraints and competition with heating load can make '
    'gas unavailable in a cold snap whatever the turbine could produce.')

#: Retirement year per plant, from VA_gas_capacity_schedules.md Schedule A (physical,
#: data-driven). A plant is available in year Y if Y < its retirement year.
#:
#: ONLY TWO RETIREMENTS ARE PLANT-SPECIFIC IN SCHEDULE A -- Bear Garden 2041 and Warren
#: County 2044. Everything else runs past 2045 under Schedule A. Schedule B (VCEA-driven)
#: retires Brunswick, Potomac Energy Center and Greensville in 2045 "for lack of market",
#: which is a DIFFERENT schedule and must not be mixed with this one.
#:
#: A DISCREPANCY IN SCHEDULE B worth flagging before it is used: it lists Doswell among
#: the plants remaining in 2045, but Doswell is an IPP (Doswell Ltd Partnership,
#: confirmed EIA-860 Schedule 2), not Dominion-owned, and is therefore not in this
#: Dominion-only mapping at all. Schedule B's 1,860 MW figure cannot be reproduced from
#: Dominion-owned plant alone.
GAS_PLANT_RETIREMENT_YEAR = {
    'Bear Garden': 2041,
    'Warren County': 2044,
}

GAS_RETIREMENT_SCHEDULE_B_UNRESOLVED = (
    'Schedule B (VCEA-driven) retires Brunswick, Potomac Energy Center and Greensville '
    'in 2045 and lists Chesterfield + Doswell + Possum Point as remaining (1,860 MW). '
    'Doswell is an IPP, not Dominion-owned, so that 1,860 MW cannot be reproduced from '
    'GAS_PLANT_CAPACITY_MW. Resolve before using Schedule B with the merit '
    'order. Potomac Energy Center is likewise absent from the Dominion-owned set.')

#: Flat availability factor applied to every rung's nameplate, covering forced outages
#: and planned maintenance together.
#:
#: FLAT RATHER THAN SCHEDULED, by decision 2026-09-12. Scheduling maintenance into
#: low-gas-usage periods would be more realistic, but in a high-solar system those are
#: the shoulder seasons -- and the nuclear profile already dips there (September 2,989
#: MW, October 2,946, March 3,008, against a February peak of 3,695, a refuelling-shaped
#: ~750 MW trough). Concentrating gas maintenance into the same windows would compound
#: with nuclear refuelling. A flat factor derates uniformly instead, which avoids
#: creating a coincident-outage artifact the model cannot presently reason about.
GAS_AVAILABILITY_FACTOR = 0.92

GAS_MERIT_ORDER_CAPACITY_SOURCING_NOTE = (
    'GAS_MERIT_ORDER_HEAT_RATES gives cost per rung but NOT capacity per rung. '
    'A merit order needs MW at each tier to bind. The Virginia fleet split by '
    'vintage and prime mover is not yet sourced -- the Dominion IRP PDFs in the '
    'project folder are truncated and unreadable (no /Root object, confirmed '
    'with both pypdf and pdfplumber), so EIA-860 generator-level data is the '
    'likely source. FULLY RESOLVED 2026-09-12 from EIA-860 Schedule 3 generator data: '
    'capacity per rung is sourced at nameplate, the CT aero/frame split is settled (all '
    'frame), and the 8,195-vs-9,362 discrepancy was a nameplate-versus-net-summer units '
    'mismatch, not missing capacity. The merit order is no longer blocked on data.')
  # MMBtu/MWh HHV, GE 7F.05 simple-cycle spec (8,580-8,610 Btu/kWh LHV,
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

if not QUIET_IMPORT:
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
# Fixed O&M by unit type, Gas Turbine World. Varies by TYPE rather than size tier -- an
# aeroderivative carries materially higher fixed O&M than a frame machine of similar output.
PEAKER_FOM_USD_PER_KW_YR = {
    'aeroderivative': 16.30,   # 105 MW twin genset, 41.5% efficiency
    'f_class': 7.00,           # 237 MW single genset, 38.2% efficiency
}

PEAKER_DUAL_FUEL_ADDER_KW = 200.0            # USP&E: $150-250/kW, midpoint
PEAKER_FAST_TRACK_PREMIUM_FRACTION = 0.15    # USP&E: 10-20% for delivery under 18 months


# ============================================================================
# DEMAND-SIDE PROGRAM TERMS -- Dominion tariffs and program design
# ============================================================================
# What Dominion currently pays and requires. These are LEVERS: the whitepaper's own DSM-incentive
# section recommends changing several of them, so they must be adjustable in one place. Peer
# comparisons for each are in docs/research/Cross_State_Commercial_Curtailment_Incentive_Comparison.md
# and Cross_Utility_VPP_Compensation_Comparison.md.

# Non-Residential Curtailment Program (Scenario 3 A.2 extended).
# $36/kW-yr captures only 40.7-70.9% of avoided generation-capacity cost alone (Internal Debugging
# Log #82), against peers at $49-52 (NYSEG), $60 (Hawaiian Electric), up to $130 (Puget Sound) and
# $216-300 (Con Edison).
LARGE_CI_COMPENSATION_USD_PER_KW_YEAR = 36.0
LARGE_CI_ELIGIBILITY_THRESHOLD_KW = 100.0

# EV Charger Rewards. Flat annual payment, size-independent -- the structural defect is as
# significant as the level: a larger enrolled load earns no more than a smaller one, severing the
# link between incentive and delivered value that every scaling peer program preserves.
EV_CHARGER_REWARDS_ANNUAL_INCENTIVE_USD = 40.0
EV_CHARGER_REWARDS_EVENT_WINDOW_HOURS = 3.0        # 3:00pm-6:00pm
DLC_VS_V2G_POPULATION_SPLIT_PCT = 50               # working assumption, not a sourced split


# ============================================================================
# ELECTRIC VEHICLE FLEET AND CHARGING
# ============================================================================
# Primitive inputs only. Values DERIVED from these (daily charging energy need, active session
# hours, probability of charging during an event window, expected kW reduction per participant)
# stay in dlc_derived_assumptions.py and recompute from these -- moving a derived value here would create
# something that looks adjustable but silently disagrees with its own inputs.
VIRGINIA_ANNUAL_VMT_PER_DRIVER_MILES = 10_255
EV_EFFICIENCY_KWH_PER_MILE = 0.375                 # Recurrent, 2026 model-year average
EV_EFFICIENCY_KWH_PER_MILE_LOW_BOUND = 0.35        # Edmunds/EnergySage cross-check, sensitivity
LEVEL2_CHARGER_POWER_KW = 9.0                      # working midpoint, not model-specific

# Fleet size. The 2030 low/high spread is Dominion's own and is wide enough to matter: the high
# case is 3.3x the low.
TOTAL_VA_REGISTERED_EVS_APRIL_2025 = 134_486
TOTAL_VA_REGISTERED_BEV_ONLY_JUNE_2024 = 91_000
DOMINION_SHARE_OF_VA_EVS_PCT_2021_SNAPSHOT = 76
DOMINION_PROJECTED_VA_NC_EVS_BY_2027 = 220_000
DOMINION_PROJECTED_VA_EVS_BY_2030_LOW = 150_000
DOMINION_PROJECTED_VA_EVS_BY_2030_HIGH = 500_000
DOMINION_EV_PEAK_DEMAND_MW_BY_2038 = 1_600


# ---------------------------------------------------------------------------
# NOTE on the former Rule 6.2 cross-check (removed 2026-09-10)
#
# This module previously ended with _assert_consistent_with_lp_model(), comparing its own values
# against lp_model.py's duplicate copies. That assertion existed only to police a duplication that
# no longer exists: lp_model.py now IMPORTS these values from here rather than defining its own.
#
# It was removed rather than kept, for a concrete reason beyond redundancy. Once lp_model.py
# imports this module at its top, the assertion becomes circular -- Python would reach this point
# while lp_model is still partially initialized, hasattr() would return False for every name, and
# every check would silently pass without comparing anything. An assertion that looks like it is
# protecting something while checking nothing is worse than no assertion.
#
# Rule 6 is now enforced structurally (single definition, imported) rather than by runtime
# comparison, and tests/test_single_source_of_truth.py asserts the import linkage holds.
# ---------------------------------------------------------------------------
