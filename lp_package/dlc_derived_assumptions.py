"""
dlc_derived_assumptions.py

RENAMED 2026-09-10 from `dlc_assumptions.py`, because the old name no longer described what this
module holds. Its primitive inputs -- EV efficiency, charger power, event window length, the flat
incentive, Dominion's own fleet projections -- moved to `assumptions.py`, the project-wide
policy-adjustable surface. What remains here is the DERIVATION CHAIN built on top of them:

    daily charging energy need   = daily VMT x EV efficiency
    active session hours         = daily energy need / charger power
    P(charging during an event)  = session hours / event window hours
    expected kW reduction        = ... etc.

Those stay here deliberately rather than moving. A derived value sitting in `assumptions.py` would
look adjustable while silently disagreeing with the inputs it was computed from -- worse than
duplication, because the disagreement would be invisible. To change any input, edit
`assumptions.py`; everything below recomputes.

dlc_derived_assumptions.py

SINGLE SOURCE OF TRUTH for every input to the EV Charger DLC per-participant magnitude estimate.
Same design principle as this project's existing assumptions.py / efficiency_assumptions.py:
exactly one definition per parameter, confidence-tagged (CONFIRMED / DERIVED / ASSUMED), sourcing
kept inline with the value it justifies.

CONTEXT: Dominion does not publish a per-participant kW load-reduction figure for its EV Charger
Rewards DLC program. Rather than treat this as a blocking gap, this module builds the figure
bottom-up from Virginia driving/EV-efficiency data plus the user's own local knowledge of NoVA
commute/dinner-time patterns -- an explicitly-stated, bottom-up estimate, not an empirically
measured one. Every step in the chain is a separate, named constant here so a future session can
see exactly which link in the chain to revisit if better data becomes available.

WHY THIS METHODOLOGY, NOT AN ALTERNATIVE: an early design question (raised directly by the user)
was whether to build a full hourly charging-start probability curve instead of a single flat
window -- explicitly rejected as "a deep rabbit hole" relative to the value it would add. The
single-window approach here is a deliberate simplification, not an oversight.
"""

import assumptions  # Rule 6: policy-adjustable values live there

import sys
import os

# NEW dependency edge, 2026-08-27, direct user request: this module previously had NO cross-module
# imports (a fully self-contained "source of truth" file, per this project's own established
# convention). Consolidating UTILITY_MARGIN_PCT into a single global (see
# shared_base_classes/demand_side_feature.py's own DEFAULT_UTILITY_MARGIN_PCT and its full
# rationale) requires this module to import it rather than maintain its own, separately-defined
# copy -- entry #112 already had to manually keep two independent copies in sync once; a true
# single source eliminates that fragility going forward. Safe: demand_side_feature.py itself has no
# downward dependency on this or any other analysis module, so no circularity risk.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared_base_classes'))
from demand_side_feature import DEFAULT_UTILITY_MARGIN_PCT  # noqa: E402

# ============================================================================
# STEP 1: Daily driving distance (Virginia-specific)
# ============================================================================

# CONFIRMED. truedrivingcost.com, citing FHWA PS-1 (2024) and 2020 Census. Cross-checked
# internally (Rule 4): the same source's own separately-stated "88.5 billion VMT, population
# 8,631,393" implies 10,254 mi/capita -- matches this figure almost exactly, confirming internal
# consistency of the underlying source rather than a typo or unit error.
VIRGINIA_ANNUAL_VMT_PER_DRIVER_MILES = assumptions.VIRGINIA_ANNUAL_VMT_PER_DRIVER_MILES

# DERIVED.
VIRGINIA_DAILY_VMT_PER_DRIVER_MILES = VIRGINIA_ANNUAL_VMT_PER_DRIVER_MILES / 365.0  # ~28.1 mi/day


# ============================================================================
# STEP 2: EV efficiency (national, most current available)
# ============================================================================

# CONFIRMED, cross-checked across multiple independent sources during sourcing (Recurrent's own
# 2026-model-year EPA-based analysis: 37.5 kWh/100mi = 0.375 kWh/mi; Edmunds/EnergySage: 0.35
# kWh/mi). Recurrent's figure used here as the primary value -- most current (2026 model year)
# and explicitly notes average EV efficiency has been DECLINING since 2018 as the market shifts
# toward larger SUVs/trucks, so this is a real, current figure, not a stale one to round down
# from. The Edmunds/EnergySage 0.35 figure is kept as a documented lower-bound cross-check, not
# discarded -- see EV_EFFICIENCY_KWH_PER_MILE_LOW_BOUND below.
EV_EFFICIENCY_KWH_PER_MILE = assumptions.EV_EFFICIENCY_KWH_PER_MILE  # Recurrent 2026 model-year average
EV_EFFICIENCY_KWH_PER_MILE_LOW_BOUND = assumptions.EV_EFFICIENCY_KWH_PER_MILE_LOW_BOUND  # Edmunds/EnergySage cross-check, kept for sensitivity

# DERIVED.
DAILY_CHARGING_ENERGY_NEED_KWH = VIRGINIA_DAILY_VMT_PER_DRIVER_MILES * EV_EFFICIENCY_KWH_PER_MILE


# ============================================================================
# STEP 3: Charger power rating
# ============================================================================

# ASSUMED. User confirmed direct ownership of a JuiceBox charger, but not which specific model
# (JuiceBox models span roughly 32A/7.7kW to 48A/11.5kW at 240V). Rather than guess a specific
# model, this uses the midpoint of the typical residential Level 2 range (7.2-11.5 kW) as a
# stated, revisable placeholder. If the specific JuiceBox model/amperage is confirmed later, this
# single constant is the only thing that needs updating -- nothing downstream needs to change
# structurally.
LEVEL2_CHARGER_POWER_KW = assumptions.LEVEL2_CHARGER_POWER_KW  # working midpoint, not model-specific


# ============================================================================
# STEP 4: Active charging session length
# ============================================================================

# DERIVED.
ACTIVE_CHARGING_SESSION_HOURS = DAILY_CHARGING_ENERGY_NEED_KWH / LEVEL2_CHARGER_POWER_KW  # ~1.1 hr


# ============================================================================
# STEP 5: Event window -- iteratively narrowed across this session's own conversation, from an
# initial full-24-hour uniform assumption down to a NoVA-specific 3pm-6pm window, based on two
# pieces of direct local knowledge from the user, not a generic assumption:
#   (a) "Rush hour here in NoVA is broad, and starts around 3:15pm" -- motivated narrowing from
#       24 hours to a rush-hour-anchored afternoon window.
#   (b) "People want to be home for dinner" -- motivated further narrowing from the full 4-hour
#       3-7pm DLC event window (per Dominion's own published EV Charger Rewards parameters) down
#       to a 3-hour 3pm-6pm window, since arrivals/charging-starts concentrate in the earlier part
#       of the event window as people get home before dinner, not evenly across the full window.
# Explicitly a SINGLE FLAT WINDOW with a uniform-arrival assumption within it -- not a shaped
# hourly curve -- per direct user instruction that a fully shaped profile was "a deep rabbit hole"
# not worth pursuing relative to its marginal value here.
# ============================================================================

EVENT_WINDOW_HOURS = assumptions.EV_CHARGER_REWARDS_EVENT_WINDOW_HOURS  # 3:00pm-6:00pm, locked in by direct user confirmation

# DERIVED. Probability a given enrolled vehicle is actively charging at any random moment within
# the event window, under the uniform-arrival-within-window simplification.
PROBABILITY_ACTIVE_CHARGING_DURING_EVENT = ACTIVE_CHARGING_SESSION_HOURS / EVENT_WINDOW_HOURS


# ============================================================================
# STEP 6: Per-participant expected kW reduction during an event
# ============================================================================

# DERIVED. This is an EXPECTED VALUE averaged across the full enrolled population -- not "each
# actively-charging vehicle loses this much power," but "each enrolled participant contributes
# this much, on average, accounting for the chance they aren't charging at that exact moment at
# all." Multiplying by enrolled participant count gives the aggregate MW reduction for a given
# event; that participant/enrollment count is a separate, not-yet-sourced input (see this
# module's own KNOWN LIMITATIONS note below).
EXPECTED_KW_REDUCTION_PER_PARTICIPANT = (
    PROBABILITY_ACTIVE_CHARGING_DURING_EVENT * LEVEL2_CHARGER_POWER_KW
)


# ============================================================================
# KNOWN LIMITATIONS -- stated explicitly, not silently assumed away
# ============================================================================
# 1. This figure is derived, not measured. Dominion does not publish a per-participant kW figure
#    for EV Charger Rewards; this bottom-up estimate was built specifically because that direct
#    data isn't available, per the user's own stated reasoning at the start of this thread.
# 2. The 3pm-6pm window is well-matched to the SUMMER afternoon events (the large majority of
#    real events in both the Smart Thermostat Rewards and EV Telematics tables already sourced --
#    17-18 of ~20 events/yr). It is a poor match for the rarer WINTER-morning events (6-9am,
#    2 events in the 2026 EV Telematics table) -- no separate winter-window logic has been built;
#    this is a disclosed gap, not a hidden one.
# 3. The participant-override discount is a real, disclosed open item -- NOT yet applied to this
#    figure (this is a gross, not net-of-override, expected kW reduction). CORRECTED 2026-08-26:
#    the Wildstein/Craig/Vaishnav citation previously referenced here was about 403 Ecobee smart
#    THERMOSTATS (SCE's 2019 program), not EV chargers -- citing it for this program was a device-
#    type mismatch, caught and corrected directly rather than left standing. EV-specific override
#    research (Burlig, Bushnell, Rapson, 2026) is now the right citation -- see STEP 7 below.
# 4. LEVEL2_CHARGER_POWER_KW is a stated midpoint, not the user's own specific JuiceBox model's
#    actual rating -- see Step 3's own note.
# 5. No enrollment/penetration rate (what share of Dominion's EV-owning customers are actually
#    enrolled in EV Charger Rewards) has been sourced or applied -- this figure is per-enrolled-
#    participant, not scaled to any aggregate MW total yet.


# ============================================================================
# STEP 7: Properly-priced incentive -- avoided-cost cross-check, direct user request, 2026-08-26.
# Follows the same pattern as large_ci_curtailment_analysis's own
# avoided_generation_capacity_cost_comparison() function (Rule 1) -- same underlying methodology
# (compare an actual incentive against what avoided capacity + avoided energy/WMA cost would
# justify), applied here to the residential EV Charger Rewards program instead of large C&I.
# ============================================================================

# CONFIRMED, the same real, currently-operating Dominion incentive already used in Step 6 above --
# restated here as its own named constant (not a bare literal) so this section's own calculations
# are self-documenting.
ANNUAL_INCENTIVE_USD_PER_PARTICIPANT = assumptions.EV_CHARGER_REWARDS_ANNUAL_INCENTIVE_USD  # $/yr flat, EV Charger Rewards

# CORRECTED 2026-09-10 -- a real units error, not a staleness issue.
#
# These previously read:
#     AERODERIVATIVE_AVOIDED_COST_USD_PER_KW_YR = 1175
#     F_CLASS_AVOIDED_COST_USD_PER_KW_YR        = 713
# with the comment "matches AERODERIVATIVE_CAPEX_USD_PER_KW there" -- which is exactly the defect.
# Those figures ARE the installed CAPITAL cost ($/kW, one-time) from
# large_ci_curtailment_derived.py. They were copied into a variable named _PER_KW_YR and used
# as an ANNUAL avoided capacity cost. The right module, the wrong variable.
#
# Consequence: the properly-priced benchmark came out roughly 14x too high, producing a headline
# finding that Dominion's current rate is "70-115x below properly priced" -- against
# large_ci_curtailment_derived.py's own ~41-71%, computed from the same source figures
# correctly annualized. Two modules, same benchmark, two orders of magnitude apart.
#
# Independent cross-check that settles which is right: PJM capacity has never cleared near
# $713/kW-yr. The 2025/26 record BRA was ~$270/MW-day = $98.5/kW-yr; the 2026/27 cap is
# $325/MW-day = $118.6/kW-yr. The annualized figures ($50.77-$88.44/kW-yr) sit inside that
# historical range; the capex figures sit ~6x above the highest price ever cleared.
#
# Now IMPORTED rather than restated (Rule 6). The prior comment justified restatement on the
# grounds that "this project has no shared package structure across analysis modules (confirmed
# directly, 2026-08-26 -- no __init__.py, no cross-module imports anywhere in lp_package/)". That
# was true then and is not now: scenario3_build imports dlc_derived_assumptions, checkpoint_solver imports
# assumptions, and lp_model imports assumptions. The convention that justified copying no longer
# describes the codebase -- and copying is what produced this error.
import large_ci_curtailment_derived as _large_ci

_LARGE_CI_COMPARISON = _large_ci.avoided_generation_capacity_cost_comparison()
AERODERIVATIVE_AVOIDED_COST_USD_PER_KW_YR = _LARGE_CI_COMPARISON['aeroderivative_avoided_cost_usd_per_kw_yr']
F_CLASS_AVOIDED_COST_USD_PER_KW_YR = _LARGE_CI_COMPARISON['fclass_avoided_cost_usd_per_kw_yr']

# SOURCED, but with a real, disclosed gap: these are the real-time LMP-derived avoided-energy/WMA
# figures already computed and reported in Dominion_Zone_Load_Shape_and_LMP_Analysis.md (N=97,
# top ~1% of hours, Sep 2025-Aug 2026, five real Dominion-zone locations). UNLIKE the peaker
# benchmarks above, these do NOT yet have a tested code module computing them from the raw LMP
# CSV -- they were computed ad-hoc in a prior session and only persisted into the markdown working
# notes. Treat as sourced-but-not-regression-tested at the raw-data level; only this module's own
# USE of the already-computed figures is tested below, not the underlying LMP calculation itself.
LMP_AVOIDED_ENERGY_USD_PER_KW_SOUTHILL = 90.98  # lowest of the five locations
LMP_AVOIDED_ENERGY_USD_PER_KW_TYSONS = 136.29  # highest of the five locations
LMP_AVOIDED_ENERGY_IS_PERFECT_FORESIGHT_UPPER_BOUND = True  # NOT a realistic capture rate -- see
                                                               # Dominion_Zone_Load_Shape_and_LMP_
                                                               # Analysis.md's own call-window-
                                                               # coverage finding (70-85%, not 100%)

# T&D deliberately excluded, direct user decision 2026-08-26: found and quantified
# (Dominion's own SCC-approved standby charge, Case PUE-2011-00088: $4.19/kW total), but removed
# from this calculation given its own contribution was only ~0.3-0.5% of the total -- not worth the
# added complexity for negligible precision gain. See Scenario3_Scope_and_Gaps.md's own D.2 Citizen
# EV V2G section for the full T&D research and the SCC's own separate finding (avoided T&D value
# from DG/DR is "insufficient to pay for their proportionate share of the grid") -- kept as sourced
# context there, deliberately not part of this module's own calculation.

# REMOVED, 2026-08-27, direct user request: this was previously a separate, independently-defined
# module constant (UTILITY_MARGIN_PCT = 0) -- now imported directly from shared_base_classes/
# demand_side_feature.py's own DEFAULT_UTILITY_MARGIN_PCT instead (see the import at this file's
# own top). No local alias kept -- the user's own stated goal was reducing the number of PLACES
# this value exists, and an alias would still be a second name pointing at one value rather than
# truly one place. Every reference below (and in this module's own tests) now uses
# DEFAULT_UTILITY_MARGIN_PCT directly.


def implied_current_rate_usd_per_kw_yr() -> float:
    """Converts the existing $40/yr flat incentive to a $/kW-yr basis, using the already-derived
    (Step 6) per-participant kW reduction figure -- a live calculation from that existing constant,
    not a separately-hardcoded number, per Rule 6."""
    return ANNUAL_INCENTIVE_USD_PER_PARTICIPANT / EXPECTED_KW_REDUCTION_PER_PARTICIPANT


def properly_priced_incentive_usd_per_kw_yr(
    avoided_capacity_usd_per_kw_yr: float,
    avoided_energy_usd_per_kw: float,
    utility_margin_pct: float = None,
) -> float:
    """Combines avoided capacity + avoided energy/WMA, then applies a utility margin (the utility
    retains `utility_margin_pct`, passing the remainder through as the incentive). Both cost
    components and the margin are parameters, not hardcoded inside this function (Rule 8) -- a
    future pass can call this with different benchmark choices (e.g. a different peaker type, a
    revised LMP figure, or T&D added back in) without editing this function's own body.
    """
    if utility_margin_pct is None:
        utility_margin_pct = DEFAULT_UTILITY_MARGIN_PCT
    total_avoided_cost = avoided_capacity_usd_per_kw_yr + avoided_energy_usd_per_kw
    return total_avoided_cost * (1 - utility_margin_pct / 100)


def avoided_cost_comparison() -> dict:
    """Full comparison: Dominion's actual current EV Charger Rewards rate vs. a properly-priced
    range (capacity + energy/WMA, 5% utility margin, T&D excluded per direct user decision).
    Returns both the low (F-Class + Southill) and high (Aeroderivative + Tysons) bounds, plus the
    implied multiple, so every intermediate value remains independently inspectable -- not just
    the final headline number.
    """
    current_rate = implied_current_rate_usd_per_kw_yr()

    low_incentive = properly_priced_incentive_usd_per_kw_yr(
        F_CLASS_AVOIDED_COST_USD_PER_KW_YR, LMP_AVOIDED_ENERGY_USD_PER_KW_SOUTHILL
    )
    high_incentive = properly_priced_incentive_usd_per_kw_yr(
        AERODERIVATIVE_AVOIDED_COST_USD_PER_KW_YR, LMP_AVOIDED_ENERGY_USD_PER_KW_TYSONS
    )

    return {
        "current_rate_usd_per_kw_yr": round(current_rate, 2),
        "properly_priced_low_usd_per_kw_yr": round(low_incentive, 2),
        "properly_priced_high_usd_per_kw_yr": round(high_incentive, 2),
        "current_rate_as_multiple_of_low": round(low_incentive / current_rate, 1),
        "current_rate_as_multiple_of_high": round(high_incentive / current_rate, 1),
        "td_included": False,  # explicit, so a future reader never has to guess
        "energy_component_is_upper_bound": LMP_AVOIDED_ENERGY_IS_PERFECT_FORESIGHT_UPPER_BOUND,
        "framing_note": (
            "Properly-priced range reflects avoided capacity + avoided energy/WMA only "
            "(T&D deliberately excluded, see comment above), after a 0% utility margin "
            "(changed from an earlier, unsourced 5% -- see DEFAULT_UTILITY_MARGIN_PCT's own comment "
            "in shared_base_classes/demand_side_feature.py). "
            "The energy component is a perfect-foresight upper bound, not a realistic "
            "capture rate -- see LMP_AVOIDED_ENERGY_IS_PERFECT_FORESIGHT_UPPER_BOUND."
        ),
    }


# ============================================================================
# STEP 8: Territory-wide ceiling estimate -- direct user-provided data, verified and extended,
# 2026-08-27
# ============================================================================
# CRITICAL FRAMING, stated directly rather than implied: this section answers "if every EV in
# Dominion's territory were enrolled, what would the total ceiling be" -- a full-adoption CEILING,
# matching Scenario 3's own explicit framing (entry #109's own already-established caveat: "what if
# every feature were adopted," not a realistic near-term trajectory). It does NOT answer "how many
# will actually enroll" -- that remains a genuinely separate, still-unresolved question. Do not
# treat the output of territory_wide_ceiling_estimate() below as a realistic MW figure for near-term
# planning without a real enrollment/participation-rate assumption layered on top.

# CONFIRMED directly, VA Clean Cities/EValuateVA (dashboard update, dated ~April 2025): 134,486
# total registered EVs statewide (102,049 BEV + 32,437 PHEV). LIKELY STALE/UNDERSTATED for the
# current date, not a current-as-of-2026 figure -- the same source chain shows ~56,000 in July 2023
# growing to 134,486 by April 2025 (~2.4x in under two years), so the true current total is plausibly
# meaningfully higher. No more-recent statewide total was found.
TOTAL_VA_REGISTERED_EVS_APRIL_2025 = assumptions.TOTAL_VA_REGISTERED_EVS_APRIL_2025

# CONFIRMED, a separate, BEV-only cut (does not include PHEV) from a different source/date
# (RenewableEnergyWorld, Feb. 2025, citing state data as of June 30 [2024]) -- preserved separately
# rather than conflated with the combined BEV+PHEV figure above, since they measure different things.
TOTAL_VA_REGISTERED_BEV_ONLY_JUNE_2024 = assumptions.TOTAL_VA_REGISTERED_BEV_ONLY_JUNE_2024

# CONFIRMED directly, Virginia Mercury (Oct. 2023), quoting Dominion's own 2021 Charging Tariff
# program filing: "approximately 76% within the company's service territory," tied to a specific,
# dated snapshot (25,500 total VA EVs at the time of that 2021 filing) -- NOT a current, ongoing
# measurement. No more-recent %-share figure was found; used here as the best available proxy,
# not a confirmed-current figure.
DOMINION_SHARE_OF_VA_EVS_PCT_2021_SNAPSHOT = assumptions.DOMINION_SHARE_OF_VA_EVS_PCT_2021_SNAPSHOT

# CONFIRMED, two DIFFERENT Dominion-attributed projections found, from different sources/vintages --
# preserved separately rather than collapsed to one, consistent with this project's own established
# practice of not silently resolving genuine multi-source discrepancies:
DOMINION_PROJECTED_VA_NC_EVS_BY_2027 = assumptions.DOMINION_PROJECTED_VA_NC_EVS_BY_2027  # RenewableEnergyWorld, Feb. 2025
DOMINION_PROJECTED_VA_EVS_BY_2030_LOW = assumptions.DOMINION_PROJECTED_VA_EVS_BY_2030_LOW  # Microgrid Knowledge, undated (cites a 2022 baseline)
DOMINION_PROJECTED_VA_EVS_BY_2030_HIGH = assumptions.DOMINION_PROJECTED_VA_EVS_BY_2030_HIGH  # same source -- a genuinely wide range, not a point estimate

# CONFIRMED, Dominion's own reporting per RenewableEnergyWorld (Feb. 2025): "the peak need from
# electric vehicles by 2038 is 1,600 megawatts." A DIFFERENT METRIC from the DLC-ceiling calculation
# below -- this is Dominion's own estimate of TOTAL EV charging peak load added to the grid, not the
# portion of that load reducible via the DLC program specifically. Not directly comparable or
# additive to the ceiling figure below without a stated methodology connecting the two, which does
# not currently exist -- kept here as real, useful, independently-sourced context only.
DOMINION_EV_PEAK_DEMAND_MW_BY_2038 = assumptions.DOMINION_EV_PEAK_DEMAND_MW_BY_2038

# A real, formal regulatory challenge to Dominion's own EV-adoption forecasts, found while
# verifying the above -- disclosed directly rather than silently omitted, since it bears on how
# much confidence to place in DOMINION_PROJECTED_VA_NC_EVS_BY_2027 and the 2030 range above. Erin
# Camp, PhD (Synapse Energy, expert witness testimony on behalf of Sierra Club, in a real SCC
# proceeding on Dominion's own EV Smart Charging Infrastructure Pilot Program) found that
# registered-EV counts in Dominion's own service territory are likely to be roughly DOUBLE what
# Dominion's own utility forecast predicted by 2030 -- i.e., a formal, sourced argument that
# Dominion's own numbers above may be UNDERSTATED, not just uncertain.
SYNAPSE_SIERRA_CLUB_FORECAST_CHALLENGE_NOTE = (
    "Sierra Club expert witness testimony (Erin Camp, PhD, Synapse Energy) found Dominion's own "
    "service-territory EV registration is likely to be roughly double the utility's own forecast "
    "by 2030 -- a formal regulatory argument that Dominion's own adoption projections above may "
    "be understated, not merely uncertain."
)


def territory_wide_ceiling_estimate_mw() -> dict:
    """Full-adoption CEILING estimate for EV Charger Rewards ALONE, territory-wide -- answers "if
    every EV in Dominion's own territory enrolled in THIS program specifically, what's the
    ceiling," NOT "how many will actually enroll." See this section's own top-level framing note --
    the latter question remains genuinely unresolved.

    UPDATED 2026-08-27, direct user instruction: given EVChargerRewards and CitizenEVV2G are
    mutually exclusive (a vehicle picks one or the other, never both -- see
    citizen_ev_v2g_analysis/citizen_ev_v2g_feature.py's own MUTUALLY_EXCLUSIVE_WITH), this
    100%-of-population figure is now a REFERENCE UPPER BOUND ("if this program alone captured
    every eligible vehicle"), preserved and still directly callable, but no longer the governing
    estimate for how the two programs together are expected to split the same population --
    see `territory_wide_ceiling_estimate_50_50_split_mw()` below for that.

    Computed as: (statewide EV total x Dominion's own share) x per-participant kW reduction,
    converted to MW. Uses the most current statewide total available
    (TOTAL_VA_REGISTERED_EVS_APRIL_2025) and Dominion's own historical share
    (DOMINION_SHARE_OF_VA_EVS_PCT_2021_SNAPSHOT) -- both flagged in their own comments as
    plausibly stale, not current-as-of-today figures.
    """
    evs_in_dominion_territory = (
        TOTAL_VA_REGISTERED_EVS_APRIL_2025 * DOMINION_SHARE_OF_VA_EVS_PCT_2021_SNAPSHOT / 100
    )
    ceiling_kw = evs_in_dominion_territory * EXPECTED_KW_REDUCTION_PER_PARTICIPANT
    ceiling_mw = ceiling_kw / 1000

    return {
        "evs_in_dominion_territory_estimate": round(evs_in_dominion_territory),
        "ceiling_mw": round(ceiling_mw, 1),
        "is_realistic_enrollment_estimate": False,  # explicit, so no caller can miss this
        "dominion_own_ev_peak_demand_mw_by_2038_for_context": DOMINION_EV_PEAK_DEMAND_MW_BY_2038,
        "framing_note": (
            "This is a full-adoption CEILING FOR THIS PROGRAM ALONE (every EV in Dominion's "
            "territory enrolled in EV Charger Rewards specifically), matching Scenario 3's own "
            "explicit framing -- NOT a realistic near-term enrollment estimate, and NOT the "
            "governing estimate once EVChargerRewards/CitizenEVV2G mutual exclusivity is taken "
            "into account (see territory_wide_ceiling_estimate_50_50_split_mw()). Dominion's own "
            "EV-count and share figures used here are historical snapshots (2021/2025), not "
            "current measurements, and Sierra Club's own expert testimony argues Dominion's own "
            "forecasts have historically been understated -- see "
            "SYNAPSE_SIERRA_CLUB_FORECAST_CHALLENGE_NOTE."
        ),
    }


# DECISION, not a physical fact -- direct user instruction, 2026-08-27: split the Dominion-territory
# EV population 50/50 between EVChargerRewards (existing DLC) and CitizenEVV2G (new BYOD/V2G), given
# their mutual exclusivity. Exposed as a named, overridable constant per Rule 8, not hardcoded
# inline -- easily reconsidered if a different split is later justified.
DLC_VS_V2G_POPULATION_SPLIT_PCT = assumptions.DLC_VS_V2G_POPULATION_SPLIT_PCT


def territory_wide_ceiling_estimate_50_50_split_mw() -> dict:
    """The GOVERNING territory-wide ceiling for EV Charger Rewards, direct user instruction
    2026-08-27: splits the same Dominion-territory EV population used in
    `territory_wide_ceiling_estimate_mw()` 50/50 with CitizenEVV2G, rather than assuming 100% of
    that population enrolls in this program alone. Half the population, same per-participant kW
    figure -- exactly half the original 100% ceiling.
    """
    evs_in_dominion_territory = (
        TOTAL_VA_REGISTERED_EVS_APRIL_2025 * DOMINION_SHARE_OF_VA_EVS_PCT_2021_SNAPSHOT / 100
    )
    evs_choosing_this_program = evs_in_dominion_territory * DLC_VS_V2G_POPULATION_SPLIT_PCT / 100
    ceiling_kw = evs_choosing_this_program * EXPECTED_KW_REDUCTION_PER_PARTICIPANT
    ceiling_mw = ceiling_kw / 1000

    return {
        "evs_choosing_this_program_estimate": round(evs_choosing_this_program),
        "population_split_pct": DLC_VS_V2G_POPULATION_SPLIT_PCT,
        "ceiling_mw": round(ceiling_mw, 1),
        "is_realistic_enrollment_estimate": False,  # still a ceiling, not a realistic near-term figure
        "framing_note": (
            f"Governing estimate, direct user instruction 2026-08-27: assumes "
            f"{DLC_VS_V2G_POPULATION_SPLIT_PCT}% of Dominion-territory EVs choose EV Charger "
            f"Rewards over CitizenEVV2G (mutually exclusive programs), rather than the 100%-of-"
            f"population reference ceiling in territory_wide_ceiling_estimate_mw(). Still a "
            f"full-adoption-style ceiling, not a realistic enrollment estimate -- the split "
            f"itself is a stated assumption, not a sourced enrollment rate."
        ),
    }

