"""
scenario3_build.py

Scenario 3's own technical foundation, built per direct user decision
(2026-08-23) to pursue the "broader" scope -- a genuinely distinct LP,
not a relabeling of Scenario 1's own build.

Three structural sub-decisions from this module's original build (2026-08-23; proposed
by Claude, not pushed back on at the time -- kept here as history, not as current
architecture):
1. SUPERSEDED (2026-09-09): distributed storage was originally dispatched independently
   via a post-hoc, outside-the-LP heuristic (the same pattern as export revenue). Direct
   user decision replaced this entirely -- distributed solar+storage is now CO-OPTIMIZED
   within the central LP itself (lp_model.build_problem()'s own distributed-segment
   parameters). The functions this decision originally justified (blended_solar_cf(),
   wma_storage_mw(), wma_storage_dispatch()) are removed from this file, not just
   deprecated in place -- see checkpoint_solver.Scenario3Solver for the real, current
   mechanism.
2. Rooftop and canopy share the same 0.81 CF ratio (Scenario3_Technical_
   Notes.md #1) -- separating them would need real, not-yet-done
   research; not pursued given the likely-small marginal value.
3. The 0.81 ratio itself is used as a single point estimate spanning both
   the shallow-tilt and east-west layout cases, per that same note's own
   recommendation -- not narrowed to one end of the range without new
   evidence.

DISTRIBUTED_CF_RATIO = 0.81 (NREL 2024 ATB, Commercial vs. Utility-Scale
PV, full derivation in Scenario3_Technical_Notes.md #1).
DISTRIBUTED_SHARE = 0.20 (10% rooftop + 10% canopy, Scenario 3's own core
definition, Scenario3_Scope_and_Gaps.md §1).

SUB-ALLOCATION WITHIN DISTRIBUTED_SHARE (direct user decision, 2026-08-23,
finalized after two rounds of revision -- see the session's own record for
the earlier, superseded 50/50 residential/C&I split within rooftop):

  Rooftop (10% of total utility solar):
    - Residential, NEM-only:        6% -- full statutory NEM cap
                                          (Va. Code §56-594), no battery
                                          counted toward dispatchable
                                          system capacity (PJM's own NEM/
                                          energy-market restriction --
                                          see Cross_Utility_VPP_
                                          Compensation_Comparison.md's own
                                          PJM section)
    - C&I + Government, WMA:        4% -- forgoes NEM (a voluntary choice,
                                          not a regulatory requirement --
                                          non-residential NEM in Dominion
                                          territory caps at 3 MW/system,
                                          confirmed via VA SCC docket
                                          filings this session), 4-hour
                                          batteries, actively dispatched
                                          for wholesale market arbitrage

  Canopy (10% of total utility solar):
    - C&I + Government, WMA:       10% -- >100kW, all WMA, 4-hour
                                          batteries. (No explicit C&I/Gov
                                          split within canopy was given --
                                          both sub-categories share
                                          identical compensation type and
                                          battery duration, so they are
                                          modeled as one economically
                                          identical block; the ownership
                                          distinction would only matter
                                          for reporting/narrative purposes,
                                          not the underlying LP economics.)

RESIDENTIAL NEM MODELING SIMPLIFICATION, stated explicitly rather than
silently assumed: residential NEM+battery systems are modeled as
contributing ONLY their net annual energy (via the blended CF, same as
before) to the grid's own energy balance. No explicit hourly battery-
dispatch/arbitrage pattern is modeled for this segment, since (a) their
batteries do not count toward system dispatchable capacity given the PJM
NEM restriction, and (b) any customer-side self-consumption shifting a
residential battery performs does not materially affect utility-scale
capacity-adequacy modeling beyond what the annual NEM energy figure
already captures. This is a real simplification, not a claim that
residential batteries do nothing -- just that their effect is out of
scope for this LP's own capacity accounting.
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass
import lp_model as lp
import dlc_derived_assumptions as dlc  # SES Rule 6: EV Charger DLC constants are owned there,
                                 # imported here rather than re-defined locally.

DISTRIBUTED_CF_RATIO_STALE_PRE_WINTER_TILT_DECISION = 0.81  # SEE WARNING BELOW -- DO NOT
# TREAT AS CURRENT. This NREL-2024-ATB-sourced ratio was explicitly superseded, not
# adopted, once the project moved from a flat CF-ratio approach to a direct panel-angle
# decision (winter-output-maximizing tilt, both rooftop and canopy -- see
# Scenario3_Technical_Notes.md #4). Deriving the correct replacement ratio requires a
# real solar-position/irradiance model comparing a winter-optimized (steeper) tilt
# against this project's existing utility-scale CF array -- that derivation has NOT been
# done. Per SES Rule 5 (fail loudly, never silently default or guess), this stale value
# is kept, renamed unmissably, and used ONLY as an explicit, disclosed placeholder until
# the real derivation is complete -- not silently replaced with a guessed number.
DISTRIBUTED_CF_RATIO = DISTRIBUTED_CF_RATIO_STALE_PRE_WINTER_TILT_DECISION  # TODO:
# replace with the real winter-tilt-derived ratio before treating any Scenario 3 result
# built with this module as final.
DISTRIBUTED_SHARE = 0.20   # of total solar nameplate MW (10% rooftop + 10% canopy)
UTILITY_SHARE = 1.0 - DISTRIBUTED_SHARE


# ============================================================================
# UTILITY-SCALE (80%) OWNERSHIP AND LAND-USE TAXONOMY -- B.1.a-c and C.1
# Added 2026-09-05, extending this module rather than replacing it (SES Rule 1).
# The DISTRIBUTED-share taxonomy above (Scenario3Policy, residential NEM / rooftop WMA
# / canopy WMA) was already correct and unchanged by this addition -- it covers B.1.d
# (rooftop) and B.1.e (canopy) precisely. This section covers the remaining 80%
# (utility-scale), which the original module never allocated by ownership/rider tier
# or by land use at all -- both were genuinely new gaps, not previously modeled.
# ============================================================================

@dataclass(frozen=True)
class UtilityScalePolicy:
    """Bundles the utility-scale (80%) share's own ownership-rider split (B.1.a-c) and
    land-use split (C.1) as changeable policy values, same design principle as
    Scenario3Policy above (direct user request, 2026-08-23, applied consistently to this
    new taxonomy layer rather than hardcoding it separately).

    Ownership shares (B.1.a-c) are fractions OF THE UTILITY-SCALE (80%) SHARE, not of
    total solar -- multiply by UTILITY_SHARE to get each tier's share of TOTAL solar.
    Rider shares are this project's own working assumption (Scenario3_Scope_and_Gaps.md
    §5.2/§1) pending confirmation against Dominion's own real rider-enrollment mix; kept
    equal by default as a disclosed starting split, not a sourced finding.

    Land-use shares (C.1) are fractions of the NON-URBAN portion specifically (the 80%
    utility-scale share, since B.1.d/e's rooftop/canopy 20% is definitionally not
    non-urban) -- agrivoltaic_share_of_nonurban=0.90 matches this project's own
    established 90%-agrivoltaic-within-non-urban figure (Scenario3_Scope_and_Gaps.md
    §5.4/C.1) exactly.
    """
    rider_ce_share: float = 1.0 / 3.0   # Dominion Rider CE -- company-owned
    rider_ppa_share: float = 1.0 / 3.0  # Dominion Rider PPA -- third-party physical PPA
    rider_rps_share: float = 1.0 / 3.0  # Dominion Rider RPS -- unbundled RECs only,
                                          # NOT a physical build allocation (see
                                          # __post_init__ handling below)
    agrivoltaic_share_of_nonurban: float = 0.90  # C.1: 90% of the 80% non-urban share

    def __post_init__(self):
        rider_total = self.rider_ce_share + self.rider_ppa_share + self.rider_rps_share
        if abs(rider_total - 1.0) > 1e-9:
            raise ValueError(
                f"Rider shares sum to {rider_total:.4f}, not 1.0 -- these must "
                f"partition the full utility-scale (80%) share.")
        if not (0.0 <= self.agrivoltaic_share_of_nonurban <= 1.0):
            raise ValueError(
                f"agrivoltaic_share_of_nonurban ({self.agrivoltaic_share_of_nonurban}) "
                f"must be a fraction in [0,1].")


UTILITY_SCALE_STANDARD = UtilityScalePolicy()  # this project's own current, disclosed
# working split (2026-09-05) -- see class docstring on rider-share sourcing status.


def utility_scale_ownership_mw(total_solar_mw, utility_policy=UTILITY_SCALE_STANDARD):
    """Splits the utility-scale (80%) share of total_solar_mw across Dominion's three
    VCEA-compliance riders (B.1.a-c). Returns a dict, not a tuple (same reasoning as
    sub_allocation_mw's own docstring: self-documenting call sites).

    NOTE, stated explicitly per SES Rule 8 (facts vs. decisions): Rider RPS is a
    financial/REC instrument, not an independent physical build -- its MW figure here
    represents the portion of utility-scale build whose RECs are sold unbundled, not a
    separate physical asset class. Downstream code that sums this dict's values to
    reconstruct total utility-scale MW is still correct (all three are drawn from the
    same physical utility_scale_mw total), but code computing PHYSICAL asset counts or
    siting footprint should be aware Rider RPS is not a distinct site-selection category.
    """
    utility_scale_mw = total_solar_mw * UTILITY_SHARE
    return dict(
        rider_ce_mw=utility_scale_mw * utility_policy.rider_ce_share,
        rider_ppa_mw=utility_scale_mw * utility_policy.rider_ppa_share,
        rider_rps_mw=utility_scale_mw * utility_policy.rider_rps_share,
    )


def utility_scale_land_use_mw(total_solar_mw, utility_policy=UTILITY_SCALE_STANDARD):
    """Splits the utility-scale (80%) share of total_solar_mw by land use (C.1):
    agrivoltaic vs. standard non-urban ground-mount. Both land-use categories have the
    SAME capacity factor (agrivoltaic confirmed energy-equivalent to standard ground-
    mount, Scenario3_Scope_and_Gaps.md C.1) -- this split affects land-acreage
    accounting and lease-income treatment downstream, not the LP's own energy balance,
    so it does not touch generation-side calculation at all."""
    utility_scale_mw = total_solar_mw * UTILITY_SHARE
    return dict(
        agrivoltaic_mw=utility_scale_mw * utility_policy.agrivoltaic_share_of_nonurban,
        standard_ground_mount_mw=utility_scale_mw * (1.0 - utility_policy.agrivoltaic_share_of_nonurban),
    )



@dataclass(frozen=True)
class Scenario3Policy:
    """Bundles every value in this module that represents a POLICY CHOICE rather than a
    physical/technical constant -- direct user request (2026-08-23): 'let's keep all of
    these values as changeable policy values.' Construct an alternate instance to run a
    variant (e.g. a different NEM/WMA split, a different battery duration) without
    touching any function logic below. STANDARD is this project's own current, agreed
    allocation; nothing about the functions in this module depends on STANDARD
    specifically -- they all take a `policy` argument.

    Frozen (immutable) so a given policy instance can't be accidentally mutated mid-run
    and silently produce inconsistent results across a solve.
    """
    residential_nem_share: float = 0.06   # rooftop, full statutory NEM cap (Va. Code
                                            # §56-594), no dispatchable battery.
                                            # SIMPLIFICATION, stated explicitly per direct
                                            # user confirmation (2026-08-23): assumes the
                                            # full 6% cap is consumed entirely by
                                            # residential rooftop, for LP tractability --
                                            # not a claim that this is the only realistic
                                            # outcome. In practice the 6% cap is shared
                                            # across residential/C&I/agricultural NEM
                                            # statewide, and a real deployment would very
                                            # likely see a mix.
    rooftop_wma_share: float = 0.04       # rooftop, C&I + Government, forgoes NEM
                                            # (voluntary -- non-residential NEM caps at
                                            # 3 MW/system in Dominion territory, confirmed
                                            # via VA SCC docket filings), WMA-eligible
    canopy_wma_share: float = 0.10        # canopy, C&I + Government (single block --
                                            # see module docstring on why these aren't
                                            # split further), all WMA
    wma_battery_duration_hours: float = 4.0   # both rooftop and canopy WMA segments

    def __post_init__(self):
        total = self.residential_nem_share + self.rooftop_wma_share + self.canopy_wma_share
        if abs(total - DISTRIBUTED_SHARE) > 1e-9:
            raise ValueError(
                f"Policy's own three shares sum to {total:.4f}, not DISTRIBUTED_SHARE "
                f"({DISTRIBUTED_SHARE}) -- if this is intentional (e.g. testing a "
                f"different total distributed share), update DISTRIBUTED_SHARE itself "
                f"too, since build_problem()'s own distributed_share_of_total_solar "
                f"parameter depends on it.")


STANDARD = Scenario3Policy()   # this project's own current, agreed allocation (2026-08-23)

# Blended CF factor: total energy per unit of TOTAL nameplate MW, relative to pure
# utility-scale. Confirmed directly (2026-08-23): 0.9620, implying Scenario 3 needs
# ~3.95% more total solar nameplate than Scenario 1 to hit the same energy target --
# the real effect the "narrower" (relabel Scenario 1's build) option would have missed.
# NOTE: depends only on DISTRIBUTED_SHARE and DISTRIBUTED_CF_RATIO, neither of which is
# a Scenario3Policy field -- both describe the physical rooftop/canopy CF derating and
# the total urban-solar fraction, not the NEM/WMA sub-split, so this does not vary by
# policy instance.
# BLENDED_CF_FACTOR REMOVED (2026-09-09): was used only by blended_solar_cf(), itself
# removed the same day now that the LP co-optimizes a real, separate DISTRIBUTED_SOLAR_MW
# build variable using distributed_solar_cf directly -- no blended proxy array is needed
# anymore. DISTRIBUTED_CF_RATIO/DISTRIBUTED_CF_RATIO_STALE_PRE_WINTER_TILT_DECISION above
# are KEPT, unchanged -- they no longer feed a blending calculation, but the real gap they
# disclose (no properly-derived, winter-tilt-based distributed_solar_cf construction exists
# anywhere in this codebase yet) is now a HARDER dependency than before: Scenario3Solver's
# own __init__ requires a real distributed_solar_cf array as a parameter with no safe
# default (SES Rule 5) -- whoever calls it needs this gap closed first, not later.


def sub_allocation_mw(total_solar_mw, policy=STANDARD):
    """Splits total_solar_mw into the three sub-allocations, per the given policy.
    Returns a dict, not a tuple, so call sites are self-documenting rather than relying
    on positional order.

    NARROWED ROLE (2026-09-09): only residential_nem_mw is actually consumed downstream
    now -- residential NEM has no storage (direct user decision) and was never part of
    the co-optimized LP segment, so it's still computed this same, unchanged way, from
    total_solar_mw = S_mw_total + dist_S_mw_total (the checkpoint's own combined solved
    total) after converge_and_solve() completes. rooftop_wma_mw/canopy_wma_mw are still
    returned (this function's own math is otherwise unchanged) but are now informational
    only -- those two sub-segments are combined into ONE co-optimized distributed pool in
    the LP itself (direct user decision, to avoid an overly complex LP), not separately
    sized or dispatched anymore."""
    return dict(
        residential_nem_mw=total_solar_mw * policy.residential_nem_share,
        rooftop_wma_mw=total_solar_mw * policy.rooftop_wma_share,
        canopy_wma_mw=total_solar_mw * policy.canopy_wma_share,
    )


def residential_nem_contribution(residential_nem_mw, distributed_solar_cf):
    """Residential NEM sub-allocation's own contribution to the grid energy balance --
    ANNUAL ENERGY ONLY, no hourly battery dispatch modeled (see module docstring
    simplification). Returns the same shape as a *_gen array (MW at each hour) so it can
    be added directly into the LP's own net-demand adjustment, analogous to exist_solar,
    but with no charge/discharge decomposition since none is modeled for this segment."""
    return residential_nem_mw * distributed_solar_cf


# ============================================================================
# DEMAND-SIDE ADJUSTMENT -- A.2 (EV Charger DLC only), A.3 (heat pump/PHIUS), A.4 (HPWH)
# Added 2026-09-05, direct user confirmation to build fresh against the base `demand`
# series rather than reuse the unverified `demand_dsm` series already present in this
# project's checkpoint files (its reduction, 0.9%-4.07% across checkpoints, is too small
# to be the full A.2+A.3+A.4 stack, and its provenance was never confirmed).
#
# EXPLICITLY EXCLUDED from this adjustment, per direct user decisions (not oversights):
#   - A.1 (DA/RT price-responsive demand) -- moved to Scenario 4 entirely.
#   - A.2's Water Energy Rewards DLC and Large C&I curtailable tariffs -- both have real,
#     quantified per-participant/per-kW magnitudes, but neither has a sourced aggregate
#     territory-wide scale figure (same "scale-up gap" pattern as A.6/A.7, which were
#     excluded for the identical reason). Only EV Charger Rewards has a real, sourced
#     territory-wide ceiling (dlc_derived_assumptions.territory_wide_ceiling_estimate_50_50_split_mw)
#     to apply here.
#   - A.2's participant-override discount -- evidence too thin/inconsistent (California-
#     only, one study contradicted directionally by a second) to anchor a discount on;
#     the EV Charger Rewards magnitude used here is the GROSS 3.51 kW/participant figure.
#   - A.5 (CVR) -- deprioritized, real double-counting risk with Dominion's active
#     Voltage Optimization program.
#   - A.7 (data center flexibility) -- excluded as premature (direct user decision,
#     2026-09-05: real parameters are >1 year out), not deferred with a placeholder.
# ============================================================================

# A.3: Residential Cooling (SEER2+PHIUS) and Heating (HSPF2) reductions, as a % of the
# RESIDENTIAL COOLING/HEATING END-USE specifically -- NOT % of total system demand (see
# _END_USE_SHARE_OF_TOTAL_DEMAND below for the total-demand conversion).
# Source: Appendix_Efficiency_Stock_Turnover_Model.md, Section 1 headline table. Per that
# appendix's own explicit warning, these two rows are NOT summed directly (PHIUS's
# combined heating+cooling reduction is already fully attributed to the Cooling row).
# 2030 values linearly interpolated between the appendix's own documented 2028 and 2035
# points, since 2030 itself was not a directly-documented milestone there.
A3_RESIDENTIAL_COOLING_PCT_OF_END_USE = {2030: 0.077, 2035: 0.145, 2040: 0.239, 2045: 0.305}
A3_RESIDENTIAL_HEATING_PCT_OF_END_USE = {2030: 0.052, 2035: 0.099, 2040: 0.194, 2045: 0.256}

# A.4: HPWH, scoped to ~73% of South Atlantic households using electric water heating
# (EIA RECS Table HC 8.8) -- ~35.9% by 2045, triggered by DOE's May 2029 rule (zero
# before then, linearly ramping 2029-2045). Figure already reflects the ~73% scoping.
A4_HPWH_PCT_OF_END_USE = {2030: 0.045, 2035: 0.135, 2040: 0.247, 2045: 0.359}

# DISCLOSED ASSUMPTION, not independently re-derived this session (SES Rule 8: this is a
# FACT about end-use composition, belongs here as a named, changeable value, not buried
# in a formula) -- standard, order-of-magnitude EIA-RECS-consistent shares for a mixed-
# humid climate zone. Worth cross-checking against a real Virginia-specific end-use
# study before treating the resulting total-demand reduction figure as final (SES Rule 4).
COOLING_SHARE_OF_TOTAL_DEMAND = 0.16
HEATING_SHARE_OF_TOTAL_DEMAND = 0.10
HPWH_SHARE_OF_TOTAL_DEMAND = 0.09

_VALID_CHECKPOINT_YEARS = (2030, 2035, 2040, 2045)


def a3_a4_total_reduction_pct_of_total_demand(year):
    """Combined A.3+A.4 reduction as a % of TOTAL system demand for a given checkpoint
    year. Raises, rather than silently defaulting, if year is not one of this project's
    own four checkpoints (SES Rule 5) -- 2045_46 checkpoints should pass 2045 explicitly,
    not rely on an implicit fallback."""
    if year not in _VALID_CHECKPOINT_YEARS:
        raise ValueError(
            f"year={year} is not one of this project's checkpoint years "
            f"{_VALID_CHECKPOINT_YEARS} -- A.3/A.4 reduction percentages are only "
            f"documented at these four points (Appendix_Efficiency_Stock_Turnover_"
            f"Model.md). Pass 2045 explicitly for the 2045_46 checkpoint.")
    cooling = A3_RESIDENTIAL_COOLING_PCT_OF_END_USE[year] * COOLING_SHARE_OF_TOTAL_DEMAND
    heating = A3_RESIDENTIAL_HEATING_PCT_OF_END_USE[year] * HEATING_SHARE_OF_TOTAL_DEMAND
    hpwh = A4_HPWH_PCT_OF_END_USE[year] * HPWH_SHARE_OF_TOTAL_DEMAND
    return cooling + heating + hpwh


# Residential adoption-rate curve for EV Charger Rewards (A.2): linear ramp 2% (2026) ->
# 90% (2035), flat thereafter. Direct user instruction, 2026-09-04.
_RAMP_START_YEAR, _RAMP_START_PCT = 2026, 0.02
_RAMP_END_YEAR, _RAMP_END_PCT = 2035, 0.90

# EV Charger Rewards event window: 3:00pm-6:00pm, same convention as dlc_derived_assumptions.py's
# own EVENT_WINDOW_HOURS (imported for the duration; the specific clock hours are this
# module's own scheduling detail, since dlc_derived_assumptions.py deliberately stays agnostic to
# which hours the window covers -- see that module's own docstring).
EV_EVENT_START_HOUR = 15
EV_EVENT_END_HOUR = 18


def residential_ev_dlc_adoption_rate(year):
    if year <= _RAMP_START_YEAR:
        return _RAMP_START_PCT
    if year >= _RAMP_END_YEAR:
        return _RAMP_END_PCT
    frac = (year - _RAMP_START_YEAR) / (_RAMP_END_YEAR - _RAMP_START_YEAR)
    return _RAMP_START_PCT + frac * (_RAMP_END_PCT - _RAMP_START_PCT)


def ev_charger_dlc_reduction_mw(year):
    """MW reduction during the 3-6pm event window, for a given checkpoint year. Ceiling
    MW is imported directly from dlc_derived_assumptions.py (SES Rule 6) -- not re-derived or
    duplicated here."""
    ceiling = dlc.territory_wide_ceiling_estimate_50_50_split_mw()['ceiling_mw']
    return ceiling * residential_ev_dlc_adoption_rate(year)


def apply_scenario3_demand_adjustment(base_demand_mw, year):
    """Applies A.2 (EV Charger DLC, event-window-only) + A.3/A.4 (heat pump/PHIUS/HPWH,
    flat across all hours) to an 8760-hour base demand series (MW), for a given
    checkpoint year. Returns the adjusted series; does not mutate the input.

    SIMPLIFICATION, disclosed directly per SES Rule 10 (not silently assumed): the
    original stock-turnover model's own hourly-shape logic did not survive between
    sessions (filesystem reset) -- only its documented, sourced % reduction outputs did.
    This applies those % reductions FLAT across every hour, rather than reconstruct the
    original hourly HVAC/water-heating load shape. Real HVAC/HPWH savings are
    concentrated in cooling/heating-season hours and DHW draw periods, not spread evenly
    across all 8,760 hours -- a flat approach is a reasonable first pass but likely
    understates the effect's concentration during coincident-peak hours specifically.
    Worth revisiting with a full hourly-shape reconstruction if this project pursues one
    later."""
    if year not in _VALID_CHECKPOINT_YEARS:
        raise ValueError(
            f"year={year} is not one of this project's checkpoint years "
            f"{_VALID_CHECKPOINT_YEARS}.")
    adjusted = base_demand_mw.copy()
    hour_of_day = np.arange(len(adjusted)) % 24

    flat_reduction_pct = a3_a4_total_reduction_pct_of_total_demand(year)
    adjusted = adjusted * (1.0 - flat_reduction_pct)

    ev_dlc_mw = ev_charger_dlc_reduction_mw(year)
    event_window_mask = (hour_of_day >= EV_EVENT_START_HOUR) & (hour_of_day < EV_EVENT_END_HOUR)
    adjusted[event_window_mask] = adjusted[event_window_mask] - ev_dlc_mw

    return adjusted


# ============================================================================
# DISTRIBUTED SEGMENT'S EXOGENOUS PRICE SERIES -- feeds build_problem()'s own
# distributed_exogenous_price_mwh parameter. Added 2026-09-09, following the co-
# optimization design discussion: exogenous_price[t] = six_day_scarcity_value[t] +
# congestion_price_rt[t] + marginal_loss_price_rt[t] -- a stack, not a choice between
# a weather-driven reliability signal and real nodal price components, since PJM's own
# real LMP already decomposes exactly this way (system energy + congestion + losses =
# total LMP).
#
# NEW DESIGN WORK, disclosed plainly: unlike the congestion/loss component (real PJM
# data, straightforward to apply), the six-day-scarcity component has no prior
# implementation anywhere in this project to extend -- the six-day-lookahead firming
# analysis (Six_Day_Lookahead_Firming_Documentation.md) produced a single MAX FLAT MW
# level per fleet, not a per-hour scarcity VALUE, and this module doesn't have access to
# that analysis's own underlying code (only its documented results). What's built below
# is a genuinely first-pass, clearly-flagged proxy for that component specifically --
# not a re-implementation of the real six-day-lookahead methodology. Treat it as a
# placeholder to replace, not a validated result, until it gets its own dedicated design
# and verification pass the way the co-optimization mechanism itself did.
# ============================================================================

# Real PJM Mid-Atlantic/APS zone data (PJMMidAtlAPSrt_hrl_lmpsAug2025aug2026.csv,
# Aug 2025-Aug 2026) -- the locational pnode, not the system-wide PJM-RTO average, since
# congestion is fundamentally a locational signal PJM-RTO wouldn't meaningfully carry.
LMP_DATA_PNODE_NAME = 'MID-ATL/APS'


def congestion_and_loss_shape_by_month_hour(lmp_csv_path='PJMMidAtlAPSrt_hrl_lmpsAug2025aug2026.csv',
                                             pnode_name=LMP_DATA_PNODE_NAME):
    """Derives a representative (month, hour-of-day) -> (avg congestion $/MWh, avg loss
    $/MWh) shape from one real year of PJM data. Returns two (12, 24) arrays.

    YEAR-MISMATCH, addressed explicitly, not silently ignored: this real LMP data is
    calendar 2025-2026; this project's own checkpoint solves run against a DIFFERENT
    weather year (2016-17, hydro_year1_2016_17.npz). Hour-by-hour concatenation across
    different years would wrongly imply a physical relationship between, e.g., a specific
    2016 Tuesday and a specific 2025 Tuesday that doesn't exist. Using a (month,
    hour-of-day) AVERAGE shape instead, applied by calendar position rather than absolute
    date, is the same technique lp_model.export_price_profile() already uses for exactly
    this reason -- not a new precedent."""
    df = pd.read_csv(lmp_csv_path)
    df = df[df['pnode_name'] == pnode_name].copy()
    if len(df) == 0:
        raise ValueError(f"No rows found for pnode_name={pnode_name!r} in {lmp_csv_path} -- "
                          f"check the name matches exactly (SES Rule 5: fail loudly).")
    dt = pd.to_datetime(df['datetime_beginning_ept'], format='%m/%d/%Y %I:%M:%S %p')
    df['month'] = dt.dt.month
    df['hour'] = dt.dt.hour
    congestion_shape = np.zeros((12, 24))
    loss_shape = np.zeros((12, 24))
    for m in range(1, 13):
        for h in range(24):
            mask = (df['month'] == m) & (df['hour'] == h)
            if mask.sum() > 0:
                congestion_shape[m-1, h] = df.loc[mask, 'congestion_price_rt'].mean()
                loss_shape[m-1, h] = df.loc[mask, 'marginal_loss_price_rt'].mean()
            # else: stays 0.0 -- a real gap in the source data for that (month, hour)
            # combination, not silently interpolated over.
    return congestion_shape, loss_shape


def apply_congestion_and_loss_shape(month_of_hour, hour_of_day, congestion_shape, loss_shape):
    """Maps a weather-year's own (month_of_hour, hour_of_day) arrays -- length T, matching
    whatever checkpoint's demand/solar_cf arrays are being used -- onto the (12,24) shape
    from congestion_and_loss_shape_by_month_hour(), by calendar position. Returns
    (congestion_mwh, loss_mwh), each length T."""
    congestion = congestion_shape[month_of_hour - 1, hour_of_day]
    loss = loss_shape[month_of_hour - 1, hour_of_day]
    return congestion, loss


def six_day_scarcity_value_proxy(demand, exist_solar, distributed_solar_cf, wind_cf, nuclear,
                                  cvow_mw, scarcity_price_per_mw_shortfall=50.0, window_hours=144):
    """FIRST-PASS PROXY, not the real six-day-lookahead methodology -- see this section's
    own module-level disclosure above. Computes a rolling 6-day (144-hour) forward-looking
    net-load metric, and prices each hour proportionally to how tight the worst point in
    its own upcoming 6-day window is -- higher when a real physical scarcity risk is
    close ahead, near-zero when the upcoming week looks comfortable. This is NOT validated
    against the real six-day-lookahead firming analysis's own results and should not be
    treated as equivalent to it.

    scarcity_price_per_mw_shortfall: $/MWh per MW of net-load-to-capacity tightness in the
    worst hour of the forward window -- an arbitrary, disclosed placeholder scale (not
    sourced), chosen only to put this proxy in a plausible $/MWh range for a first pass.

    DEFECT FOUND 2026-09-11 -- THIS DOES NOT BEHAVE AS THE DOCSTRING ABOVE DESCRIBES.

    The docstring claims the output is "higher when a real physical scarcity risk is close ahead,
    near-zero when the upcoming week looks comfortable". Measured on the 2045 Virginia-only demand:

        min $0.8633   max $1.1653   mean $1.0255   coefficient of variation 3.99%
        hours below half the mean: 0 of 8760; the minimum is 84% of the mean

    It never approaches zero and barely varies at all.

    CAUSE: the formula has NO CAPACITY REFERENCE TERM. It computes

        max(0, worst_net_load_in_window / 1000) * 50 / 1000

    which is simply peak net load in GW x 0.05 -- an ABSOLUTE LEVEL, not a tightness ratio.
    "Tightness" requires comparing net load against available capacity, and no capacity appears
    anywhere in the calculation. Because the peak net load within any rolling 144-hour window is
    similar year-round, the result is close to constant.

    CONSEQUENCE FOR SCENARIO 3: this component contributes a near-flat ~$1/MWh OFFSET to
    distributed_exogenous_price_mwh rather than a time-varying signal. Since the purpose of that
    price series is to drive FERC 2222 wholesale arbitrage by the distributed segment, and
    arbitrage responds to VARIATION rather than level, the scarcity term currently contributes
    almost nothing to the arbitrage decision. The time-varying content of the price series comes
    entirely from the congestion and marginal-loss shapes, which are real PJM data.

    That is not necessarily wrong for a first pass -- congestion and loss are the better-sourced
    components anyway -- but any Scenario 3 result must not be described as incorporating a
    six-day-lookahead scarcity signal. It incorporates a constant.

    WHAT A CORRECT SIGNAL WOULD DO, AND WHY THE DEFECT IS WORSE THAN A MISSING DAILY SPREAD

    The first statement of this defect framed it as "adds no daily spread, so arbitrage timing is
    unaffected". That understates it. A correct six-day signal does not primarily act on daily
    spread at all -- it produces a RISING PRICE PATH ACROSS A MULTI-DAY EVENT, which switches the
    operating mode from "cycle daily" to "RATION ACROSS DAYS".

    At high solar and battery penetration, a forecast dunkelflaute implies steadily rising expected
    prices through its duration. An operator seeing that meters stored energy out judiciously, and
    may hold charge for days waiting for the best hour. A battery seeing a flat $1/MWh adder has no
    reason to hold anything back into day four. The proxy produces none of this behaviour in any
    form, not merely a weakened version of it.

    THE REBOUND EFFECT -- A COORDINATION FAILURE, NOT JUST FORGONE VALUE

    If PJM remains day-ahead-only and DER fleets optimise on that horizon, every operator
    discharges into the same first-day peak, storage is exhausted early, and the later days of a
    multi-day event arrive with the fleet empty. The resulting spike is WORSE than if nobody had
    discharged. Short lookahead does not merely forgo value; it manufactures the scarcity it failed
    to anticipate.

    Fleet heterogeneity is what makes this tractable rather than catastrophic. Real DER fleets carry
    a wide range of lookahead sophistication; longer-lookahead operators profit heavily from the
    day-four spike, and that profit is the signal that drives adaptation. The rebound is therefore
    self-correcting over time -- but only where some operators have the lookahead to begin with,
    and only after at least one expensive event has taught it.

    THE ASYMMETRY THIS CREATES INSIDE THIS PROJECT'S OWN MODEL -- the most consequential point here

    This project has already established (see lp_package/capacity_accreditation.py) that the LP
    dispatches storage with PERFECT FORESIGHT: own-data accreditation measured on LP dispatch read
    100.0% against 31.8% from a no-foresight heuristic on the same fleet.

    So within a single model:

        utility-scale storage, dispatched inside the LP   -> PERFECT lookahead, knows the year
        distributed storage, responding to this price     -> effectively NO lookahead

    That is not a neutral modelling choice. It systematically favours utility-scale storage in
    precisely the comparison Scenario 3 exists to make. The distributed segment is being asked to
    compete while blindfolded, and any finding that distributed storage underperforms utility-scale
    storage on arbitrage value inherits that bias.

    NOT FIXED HERE, deliberately: correcting it means choosing a capacity reference, which is a
    modelling decision rather than a bug fix, and changing it would alter the distributed arbitrage
    result. Recorded so the Scenario 3 run is interpreted correctly -- and so the foresight
    asymmetry is not mistaken for a finding about distributed storage.
    """
    T = len(demand)
    net_load = demand - exist_solar - cvow_mw * wind_cf - nuclear
    # Distributed generation's own contribution reduces net load further, if present --
    # the scarcity signal should reflect what's left AFTER the distributed segment's own
    # (fixed-share, non-decision) generation, not before it.
    if distributed_solar_cf is not None:
        # Approximate distributed generation at the fixed 20% share ratio -- this proxy
        # doesn't have access to the LP's own solved DISTRIBUTED_SOLAR_MW build size
        # (chicken-and-egg: the price series is an INPUT to that solve, not an output of
        # it), so it uses the utility-scale exist_solar's own rough order of magnitude as
        # a stand-in. Disclosed approximation, not a precise figure.
        net_load = net_load - exist_solar.mean() * 0.25 * distributed_solar_cf
    scarcity = np.zeros(T)
    for t in range(T):
        window_end = min(t + window_hours, T)
        worst_in_window = net_load[t:window_end].max() if window_end > t else net_load[t]
        scarcity[t] = max(0.0, worst_in_window / 1000.0) * scarcity_price_per_mw_shortfall / 1000.0
    return scarcity


def build_distributed_exogenous_price_mwh(demand, exist_solar, distributed_solar_cf, wind_cf,
                                           nuclear, cvow_mw, month_of_hour, hour_of_day,
                                           lmp_csv_path='PJMMidAtlAPSrt_hrl_lmpsAug2025aug2026.csv'):
    """Assembles the full exogenous_price[t] = six_day_scarcity_value[t] +
    congestion_price_rt[t] + marginal_loss_price_rt[t] stack -- the value
    build_problem()'s own distributed_exogenous_price_mwh parameter needs. See this
    section's own module-level disclosure: the congestion/loss component is real PJM
    data, properly year-aligned; the scarcity component is a first-pass, unvalidated
    proxy, not the real six-day-lookahead methodology."""
    congestion_shape, loss_shape = congestion_and_loss_shape_by_month_hour(lmp_csv_path)
    congestion, loss = apply_congestion_and_loss_shape(month_of_hour, hour_of_day,
                                                         congestion_shape, loss_shape)
    scarcity = six_day_scarcity_value_proxy(demand, exist_solar, distributed_solar_cf,
                                             wind_cf, nuclear, cvow_mw)
    return scarcity + congestion + loss



    # ---- Quick sanity test on a single representative year (2045) ----
    # NARROWED (2026-09-09): rooftop/canopy WMA sizing+dispatch used to be demonstrated
    # here too, via the now-removed wma_storage_mw()/wma_storage_dispatch() heuristics --
    # that's genuinely gone, not just hidden; the real distributed build+dispatch now
    # comes out of Scenario3Solver.converge_and_solve() itself (checkpoint_solver.py),
    # solved jointly with everything else, not something this standalone script can
    # demonstrate in isolation anymore. What's left below (residential NEM's own
    # allocation and contribution, and the policy-variance demo) is exactly the subset of
    # this file's original logic that's still real, standalone functionality.
    h = np.load('hydro_year1_2016_17.npz')
    solar_cf = h['solar']

    # Illustrative total -- the real Scenario 3 checkpoint solve determines its own total
    # (S_mw_total + dist_S_mw_total) via Scenario3Solver; this is just for demonstrating
    # sub_allocation_mw()/residential_nem_contribution() in isolation.
    total_solar_mw_test = 50000.0
    policy = STANDARD
    alloc = sub_allocation_mw(total_solar_mw_test, policy)
    # Distributed CF still has no properly-derived source (see the DISTRIBUTED_CF_RATIO
    # comment above) -- using the stale placeholder ratio here ONLY for this illustrative
    # demo, exactly as disclosed, not as a stand-in for a real answer.
    dist_cf = solar_cf * DISTRIBUTED_CF_RATIO

    print(f"Total solar (illustrative): {total_solar_mw_test:.1f} MW")
    print(f"Policy in use: {policy}")
    print(f"\n--- Sub-allocation split ({DISTRIBUTED_SHARE*100:.0f}% of total) ---")
    print(f"Residential NEM ({policy.residential_nem_share*100:.0f}%): {alloc['residential_nem_mw']:.1f} MW -- no dispatchable battery")
    print(f"Rooftop C&I/Gov WMA ({policy.rooftop_wma_share*100:.0f}%): {alloc['rooftop_wma_mw']:.1f} MW -- informational only, see note above")
    print(f"Canopy C&I/Gov WMA ({policy.canopy_wma_share*100:.0f}%): {alloc['canopy_wma_mw']:.1f} MW -- informational only, see note above")
    print(f"Sum check: {sum(alloc.values()):.1f} MW (should equal "
          f"{total_solar_mw_test * DISTRIBUTED_SHARE:.1f} MW)")

    # Residential NEM: annual energy only, no dispatch -- still real, unchanged logic
    residential_gen = residential_nem_contribution(alloc['residential_nem_mw'], dist_cf)
    print(f"\n--- Residential NEM (energy-only, no battery dispatch) ---")
    print(f"Annual generation: {residential_gen.sum()/1000:.1f} GWh")

    # ---- Demonstrate policy variance: an alternate allocation, no code changes needed ----
    print(f"\n{'='*70}")
    print("POLICY VARIANCE DEMO -- alternate split, same functions, no code edits")
    print(f"{'='*70}")
    alt_policy = Scenario3Policy(residential_nem_share=0.05, rooftop_wma_share=0.05,
                                   canopy_wma_share=0.10, wma_battery_duration_hours=6.0)
    alt_alloc = sub_allocation_mw(total_solar_mw_test, alt_policy)
    print(f"Alternate policy: {alt_policy}")
    print(f"Residential NEM: {alt_alloc['residential_nem_mw']:.1f} MW")
    print(f"Rooftop (informational): {alt_alloc['rooftop_wma_mw']:.1f} MW")
    print(f"Canopy (informational): {alt_alloc['canopy_wma_mw']:.1f} MW")
