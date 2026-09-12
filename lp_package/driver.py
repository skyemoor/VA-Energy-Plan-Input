import numpy as np
import json, time, sys
from scipy import sparse
import lp_model as lp

# ---------------- RPS Program requirement schedule, Va. Code SS56-585.5(C)(1)(a), Phase II Utilities
# (Dominion Energy Virginia is the Phase II utility -- confirmed by user). Full, explicit, year-by-year
# statutory table -- fetched and verified directly against the statute's own text on 2026-08-21, not
# interpolated. Values are the CLEAN (RPS-compliant) percentage; gas_target_share() below is 1 minus this.
#
# CORRECTED (this session): supersedes an earlier, much sparser RPS_CLEAN_PCT (only 2030/2035/2040/2045
# populated) that left every other year -- the 12 intermediate years and 2026-2029 -- either fully banned
# from gas (build_dispatch_problem() defaults g to (0,0) when gas_allowed_frac=None, as solve_2026_2029.py
# left it) or entirely unconstrained by any RPS target at all (solve_intermediate_years.py, which only
# capped gas at physical fleet capacity, no RPS share at all). Both were wrong, not just approximate --
# the full ban is off by a wide margin (the statute allows 62-71% gas in 2026-2029, not 0%), consistent
# with what the user identified as likely orphan code from an earlier, incorrect "100% clean every year"
# assumption. The full table below replaces both approaches for every affected year.
RPS_CLEAN_PCT_PHASE_II = {
    2021: 0.14, 2022: 0.17, 2023: 0.20, 2024: 0.23, 2025: 0.26,
    2026: 0.29, 2027: 0.32, 2028: 0.35, 2029: 0.38, 2030: 0.41,
    2031: 0.45, 2032: 0.49, 2033: 0.52, 2034: 0.55, 2035: 0.59,
    2036: 0.63, 2037: 0.67, 2038: 0.71, 2039: 0.75, 2040: 0.79,
    2041: 0.83, 2042: 0.87, 2043: 0.91, 2044: 0.95, 2045: 1.00,
}
# 2045 and thereafter is 100% per the statute's own "2045 and thereafter" row -- any year > 2045 also
# maps to 1.00 (handled in gas_target_share() below, not baked into this dict, to keep the dict itself
# a direct, literal transcription of the statute's own table).

RPS_CLEAN_PCT = RPS_CLEAN_PCT_PHASE_II  # kept for any existing caller still using the old name
# CORRECTED (2026-08-16): 2044.5's 0.999 was always an approximation for "~100% by 2045," per its own
# comment -- Scenario 1 is specifically the scenario meant to track VCEA to its real, full endpoint (unlike
# 1B/3B, which deliberately stop at a permanent 5% floor), so a genuine 2045 entry (true 100% clean, 0% gas)
# is now added as its own checkpoint rather than only ever approximating it.
def gas_target_share(year):
    if year >= 2045:
        return 0.0  # 100% clean, "2045 and thereafter" per the statute's own final row
    if year in RPS_CLEAN_PCT_PHASE_II:
        return 1.0 - RPS_CLEAN_PCT_PHASE_II[year]
    raise ValueError(f"No statutory RPS Program requirement defined for year {year} "
                      f"(table covers 2021-2045; check Va. Code SS56-585.5(C)(1)(a) directly "
                      f"if a year outside this range is genuinely needed).")

# ---------------- VCEA storage floors (Va. Code SS56-585.5(E)), interpolated between explicit statutory
# milestones -- per project direction (2026-08-16): pick the higher/more-stringent implied requirement at
# any checkpoint year, including years that don't land exactly on a milestone, using interpolation rather
# than carrying the last known floor flat. Applies to BOTH storage types now (an earlier, more conservative
# choice had held short-duration flat at 4,000 MW past 2030, given no interim milestone is specified in the
# statute itself -- superseded by this direction).
def vcea_short_duration_floor_mw(year):
    """Interpolated between (2030, 4,000 MW) and (2045, 16,000 MW) -- the only two explicit statutory
    points (SS56-585.5(E)(2)); no interim milestone is specified in the law itself (delegated to SCC
    regulations per subsection (E)(8), not yet fixed), so linear interpolation is this project's own
    reasonable choice for years between, not a statutory figure itself."""
    if year <= 2030:
        return 4000.0
    if year >= 2045:
        return 16000.0
    frac = (year - 2030) / (2045 - 2030)
    return 4000.0 + (16000.0 - 4000.0) * frac

def vcea_long_duration_floor_mw(year):
    """0 MW before 2035 (no statutory requirement exists yet -- the first explicit milestone IS 2035,
    unlike short-duration's 2030 start, so no ramp is assumed before it), interpolated between (2035,
    2,000 MW) and (2045, 4,000 MW) per SS56-585.5(E)(4) thereafter."""
    if year < 2035:
        return 0.0
    if year >= 2045:
        return 4000.0
    frac = (year - 2035) / (2045 - 2035)
    return 2000.0 + (4000.0 - 2000.0) * frac

# ---------------- Gas fleet capacity schedule (Schedule B, VA_gas_capacity_schedules.md) ----------------
def schedule_b_baseline_mw(year):
    if year <= 2044:
        return 9362.0
    return 1860.0  # 2045 VCEA-driven drop (Chesterfield+Doswell+Possum Point only)

# ---------------- 8-plant overhaul/retain pool, youngest-first (commissioning date desc) ----------------
# (name, MW, commission_year, needs_overhaul)
# "needs_overhaul": plants with documented low EOH (well below 48,000-100,000 mid-life window) => no capital
# work; older plants with no EOH data (1989-1994 commissioning, near/beyond nominal 30-45yr CT life) => treated
# as needing a genuine overhaul, using the established $22.5M midpoint (see new_peaker_ccgt_costs_by_size.md)
POOL = [
    ("Marsh Run",       550.0, 2004, False),  # EOH 13,835 -- well below overhaul window
    ("Louisa",          525.0, 2003, False),  # EOH 11,295
    ("Wolf Hills",      285.0, 2001, False),  # EOH 7,026 (lowest)
    ("Remington",       619.0, 2000, False),  # EOH 15,892
    ("Gordonsville",    218.0, 1994, True),   # no EOH data; 32yr old by 2026 -- treated as overhaul candidate
    ("Elizabeth River", 327.0, 1992, True),   # no EOH data; 34yr old
    ("Darbytown",       168.0, 1990, True),   # no EOH data; 36yr old
    ("Gravel Neck",     170.0, 1989, True),   # no EOH data; 37yr old
]
OVERHAUL_COST_M = 22.5          # $M per plant needing overhaul (midpoint of $15-30M range)
OVERHAUL_CRF_10YR = 0.045*(1.045**10)/((1.045**10)-1)   # accelerated 10-yr recovery, matches Tenaska precedent

# New-build simple-cycle units, cheapest $/kW first (F-Class), for any residual gap beyond the pool
NEWBUILD_UNITS = [
    ("F-Class",       237.0, 165.8, 7.00),    # MW, $M total, $/kW-yr fixed O&M
    ("H-Class",       418.0, 453.2, 13.10),
    ("Aeroderivative",105.0, 123.5, 16.30),
]

def select_overhaul_retain(shortfall_mw):
    """Youngest-first greedy: examine plants newest->oldest, stop once cumulative MW clears the shortfall."""
    selected = []
    cum = 0.0
    for name, mw, yr, needs_overhaul in POOL:
        if cum >= shortfall_mw:
            break
        selected.append((name, mw, yr, needs_overhaul))
        cum += mw
    remaining = max(0.0, shortfall_mw - cum)
    annual_cost = sum(OVERHAUL_COST_M*OVERHAUL_CRF_10YR*1e6 for (_,_,_,nh) in selected if nh)
    newbuild = []
    if remaining > 0:
        # use F-Class units (cheapest $/kW) to cover the residual gap
        name, mw, cost_m, fom_kw = NEWBUILD_UNITS[0]
        n_units = int(np.ceil(remaining/mw))
        newbuild = [(name, mw, cost_m, fom_kw)]*n_units
        cum += n_units*mw
    newbuild_annual_cost = sum(cost_m*1e6*lp.CRF + mw*1000*fom_kw for (_,mw,cost_m,fom_kw) in newbuild)
    return dict(selected=selected, cum_mw=cum, newbuild=newbuild,
                overhaul_annual_cost=annual_cost, newbuild_annual_cost=newbuild_annual_cost)


def set_year_capex(year):
    """Override module-level capex/RTE globals (not parameterized in build_problem) for this checkpoint year.
    CORRECTED: was using the stale na_capex_kwh_4hr_ref name plus an ad-hoc 25%/75% power/energy split;
    now uses na_power_energy_split() directly, which is properly NREL-share-derived AND correctly
    benchmarked to the validated 6-hr reference (per Assumptions tab row 33 / prior session's finding)."""
    lp.SOLAR_CAPEX = lp.solar_capex(year)
    lp.NA_POWER_CAPEX, lp.NA_ENERGY_CAPEX = lp.na_power_energy_split(year)
    lp.FE_ENERGY_CAPEX = lp.fe_capex_kwh(year)
    lp.FE_RTE_CHARGE = lp.iron_air_rte(year)
    # NEW (2026-08-16): time-varying Na-ion cycle life per project direction -- deployments before 2035
    # reflect currently-available technology (10,000 cycles, the credible manufacturer-spec figure);
    # 2035 and later assume the currently-promised 15,000-cycle figure has been achieved at commercial
    # scale by then, given Na-ion's fast-moving development trajectory.
    lp.NA_CYCLE_LIFE = 10000 if year < 2035 else 15000


def apply_slcr_constraint(problem, frac, curt_cost=5.0):
    """SLCR (storage loss coverage by renewables): modifies the RPS row so storage charge/
    discharge is correctly accounted for in the gas-allowance constraint, and sets curtailment
    cost to $5/MWh. Every one of this project's own "*_final.py" scripts applied this manually,
    near-identically, ~20 times over -- consolidated here as this project's own single, shared
    implementation (Internal Debugging Log #26).

    CONFIRMED NECESSARY, NOT SUPERSEDED (this session): build_problem()'s own more recent
    (2026-08-16) discharge-side cycling-cost mechanism was validated only against the 2045
    checkpoint's own parameterization and does NOT generalize on its own -- the 2035 checkpoint
    showed 388 hours of large-magnitude simultaneous Na-ion dispatch without this splice (e.g.
    charging 8,425 MW while discharging 965 MW at the same hour), which a freshly-reoptimized,
    SLCR-included solve resolved to zero simultaneous hours AND a lower objective than the
    no-SLCR baseline. Applied on top of the cycling-cost mechanism, not instead of it -- nothing
    found this session says the 2026-08-16 fix was wrong, only that it is necessary but not
    sufficient on its own.

    EXTENDED (2026-09-09): also covers the distributed segment's own Na-ion/iron-air charge and
    discharge, for the identical reason it already covers utility-scale storage -- distributed
    storage cycling represents the same kind of RPS-accounting loss this constraint exists to
    correct for, and there's no reason to expect it exempt just because it's a newer addition.
    Structurally inert (the IDX keys resolve to variables pinned at (0, 0)) when
    enable_distributed_segment=False, so this extension changes nothing for any existing caller.

    MUST be applied BEFORE any solve that will inform a build-size decision (including every
    iteration of frac convergence) -- applying it only to a final solve, after the build size was
    already optimized WITHOUT it, produces an invalid comparison (confirmed directly this
    session: doing so produced 1.19M MWh of unserved energy and a wildly inflated objective, not
    a genuine test of the mechanism). Modifies problem['A_ub']/problem['c'] in place; returns the
    same problem dict for chaining."""
    IDX = problem['IDX']; NVAR_BUILD, NVAR_PER_HOUR = problem['hv_params']; T = problem['T']
    def hv(t, k): return NVAR_BUILD + t*NVAR_PER_HOUR + k
    for t in range(T):
        problem['c'][hv(t, IDX['curt'])] = curt_cost
    A_ub = problem['A_ub'].tolil()
    gascum_last = hv(T-1, IDX['gascum'])
    col_data = problem['A_ub'][:, gascum_last].toarray().flatten()
    rps_row = int(np.where(col_data != 0)[0][0])
    k = frac / (1 - frac)
    for t in range(T):
        A_ub[rps_row, hv(t, IDX['bc'])] += k/1000.0
        A_ub[rps_row, hv(t, IDX['bd'])] += -k/1000.0
        A_ub[rps_row, hv(t, IDX['nc'])] += k/1000.0
        A_ub[rps_row, hv(t, IDX['nd'])] += -k/1000.0
        A_ub[rps_row, hv(t, IDX['fc'])] += k/1000.0
        A_ub[rps_row, hv(t, IDX['fd'])] += -k/1000.0
        if 'dist_na_charge_mw' in IDX:  # present since 2026-09-09; guards older/other problem dicts
            A_ub[rps_row, hv(t, IDX['dist_na_charge_mw'])] += k/1000.0
            A_ub[rps_row, hv(t, IDX['dist_na_discharge_mw'])] += -k/1000.0
            A_ub[rps_row, hv(t, IDX['dist_fe_charge_mw'])] += k/1000.0
            A_ub[rps_row, hv(t, IDX['dist_fe_discharge_mw'])] += -k/1000.0
    problem['A_ub'] = A_ub.tocsr()
    return problem


def run_solve(year, frac, demand, exist_solar, solar_cf, wind_cf, nuclear, capacity_cap_mw=None, return_hourly=False,
              min_na_power_mw='vcea_default', min_na_duration_hr=6.0, min_efe_power_mw='vcea_default',
              reserve_margin_hint=None, IRM=0.177, prior_solar_mw=0.0, prior_na_power_mw=0.0,
              prior_na_energy_mwh=0.0, prior_ironair_energy_mwh=0.0, apply_slcr=True, slcr_curt_cost=5.0,
              enable_distributed_segment=False, distributed_solar_cf=None,
              distributed_share_of_total_solar=0.20, distributed_exogenous_price_mwh=None,
              prior_distributed_solar_mw=0.0, prior_distributed_na_power_mw=0.0,
              prior_distributed_na_energy_mwh=0.0, prior_distributed_ironair_energy_mwh=0.0,
              distributed_reserve_margin_credit_fraction=0.0, pin_build_mw=None,
              enforce_closing_soc=True, return_raw_result=False, post_build_hook=None,
              gas_merit_order=None, gas_merit_order_year=None):
    # EXTENDED (this session): prior_* kwargs, passed straight through to build_problem(), so
    # run_solve()/converge_frac() can be used directly for linked checkpoints too -- previously
    # linking required bypassing run_solve() entirely and manually replicating its own internals
    # (see the older solve_20XX_linked_final.py scripts), which meant frac convergence and linking
    # could not be combined in one call. Defaults (0.0) reproduce this function's own prior,
    # unlinked behavior exactly -- no change for any existing caller that doesn't pass these.
    # EXTENDED AGAIN (this session, Internal Debugging Log #26): apply_slcr, default True. Every
    # one of this project's own "final" scripts applied the SLCR splice manually; run_solve()
    # never did, which was silently relied upon by this session's own initial corrected-demand
    # re-solves before the gap was caught. Confirmed necessary (not a stale, superseded
    # mechanism) via direct testing at the 2035 checkpoint -- see apply_slcr_constraint()'s own
    # docstring. Default True makes this function's own behavior match every "final" script's
    # own established practice; pass apply_slcr=False only to deliberately reproduce the older,
    # incomplete behavior (e.g. for a controlled A/B test, not for a result meant to be trusted).
    # CORRECTED (2026-08-16): min_na_power_mw now defaults to the INTERPOLATED VCEA short-duration floor
    # (vcea_short_duration_floor_mw(year)) rather than a flat 4,000 MW carried forward past 2030 -- per
    # project direction, both storage floors should be interpolated between explicit statutory milestones
    # rather than holding the last known value flat. Pass an explicit MW value (or None) to override.
    #
    # EXTENDED (2026-09-09): the distributed_* kwargs, passed straight through to build_problem()'s own
    # distributed-segment parameters -- see that function's docstring for the full mechanism (fixed
    # 20%-of-total solar share, symmetric price-based storage arbitrage, no build-distortion risk).
    # Defaults reproduce this function's pre-existing behavior exactly -- no change for Scenario 1/1B/2
    # or any existing Scenario 3 caller that doesn't pass enable_distributed_segment=True.
    #
    # distributed_reserve_margin_credit_fraction (default 0.0, i.e. UNCHANGED existing behavior): what
    # fraction of the distributed segment's own nameplate solar+storage power counts toward the reserve-
    # margin constraint's own peak-hour availability, alongside nuclear/gas/wind/utility Na-power/utility
    # solar. NOT a settled question -- disclosed explicitly rather than silently resolved either
    # direction. 0.0 (current default) means the distributed segment contributes nothing to reliability
    # accounting even under enable_distributed_segment=True, which is conservative but doesn't reflect
    # the "full WMA participation" policy premise (Scenario3_Technical_Notes.md #10) at all. Crediting it
    # at 1.0 (full nameplate) would directly contradict the six-day-lookahead firming analysis's own
    # finding that only ~4.3% of this fleet's nameplate is reliably firm even at 6-day perfect foresight
    # (Six_Day_Lookahead_Firming_Documentation.md) -- that ~4.3% figure is the empirically-grounded
    # reference point if/when a real, non-zero, non-nameplate value is decided on, not something this
    # session is choosing on its own.
    # pin_build_mw (default None, i.e. UNCHANGED existing behavior): passed straight through to
    # build_problem()'s own pin mechanism -- see that function's docstring for the full rationale
    # (partial-year diagnostic solves, where the RPS constraint's own sum(solar_cf)-proportional
    # coefficient makes an UNPINNED build size artifically window-dependent). None reproduces this
    # function's pre-existing behavior exactly for every current caller.
    if min_na_power_mw == 'vcea_default':
        min_na_power_mw = vcea_short_duration_floor_mw(year)
    if min_efe_power_mw == 'vcea_default':
        min_efe_power_mw = vcea_long_duration_floor_mw(year)
    set_year_capex(year)
    # gas_merit_order (2026-09-12): when supplied, build_problem zeroes the flat gas cost and
    # per-rung variables carry it instead. gas_price_mwh below is still passed -- it is ignored in
    # that mode rather than being made conditional here, so the two call paths stay identical in
    # shape and a future reader sees one signature, not two.
    #
    # NOTE what the flat price actually is: SIMPLE_CYCLE heat rate. That is why the pre-stack 2030
    # dual sat at $54.70 = $51.30 simple-cycle fuel + $3.00 VOM -- the model priced every hour as
    # though a peaker were marginal, in all 8,760.
    if gas_merit_order is not None and gas_merit_order_year is None:
        gas_merit_order_year = year          # the caller's own checkpoint year is the only sane default
    problem = lp.build_problem(solar_cf, wind_cf, nuclear, exist_solar, demand, frac,
                                verbose=False, gas_price_mwh=lp.gas_cost_mwh(year, heat_rate=lp.SIMPLE_CYCLE_HEAT_RATE),
                                gas_merit_order=gas_merit_order,
                                gas_merit_order_year=gas_merit_order_year,
                                prior_solar_mw=prior_solar_mw, prior_na_power_mw=prior_na_power_mw,
                                prior_na_energy_mwh=prior_na_energy_mwh,
                                prior_ironair_energy_mwh=prior_ironair_energy_mwh,
                                enable_distributed_segment=enable_distributed_segment,
                                distributed_solar_cf=distributed_solar_cf,
                                distributed_share_of_total_solar=distributed_share_of_total_solar,
                                distributed_exogenous_price_mwh=distributed_exogenous_price_mwh,
                                prior_distributed_solar_mw=prior_distributed_solar_mw,
                                prior_distributed_na_power_mw=prior_distributed_na_power_mw,
                                prior_distributed_na_energy_mwh=prior_distributed_na_energy_mwh,
                                prior_distributed_ironair_energy_mwh=prior_distributed_ironair_energy_mwh,
                                pin_build_mw=pin_build_mw, enforce_closing_soc=enforce_closing_soc)
    # post_build_hook (default None -- no behavior change for any existing caller): a callable taking
    # the just-built problem dict and returning a (possibly extended) problem dict. Applied immediately
    # after build_problem() and BEFORE any of the bound/constraint logic below, so hook-added rows see
    # the same variable indexing build_problem() itself established. Added this session so additional
    # constraint modules (charging_adequacy.py, all_hours_reserve.py) can extend the LP without either
    # duplicating this function's own intricate bound-adjustment logic or being hard-coded into it.
    if post_build_hook is not None:
        problem = post_build_hook(problem)
    if capacity_cap_mw is not None:
        IDX = problem['IDX']; NVAR_BUILD, NVAR_PER_HOUR = problem['hv_params']; T = problem['T']
        def hv(t,k): return NVAR_BUILD + t*NVAR_PER_HOUR + k
        for t in range(T):
            lo, hi = problem['bounds'][hv(t,IDX['g'])]
            problem['bounds'][hv(t,IDX['g'])] = (lo, capacity_cap_mw)
    # SLCR must be applied before any of the VCEA-floor/reserve-margin logic below touches the
    # same A_ub matrix, and well before the solve -- applying it after those steps risks operating
    # on a stale row reference if row count changes; applying it after the solve (as this
    # session's own first attempt at fixing this did) produces an invalid, infeasible comparison.
    if apply_slcr:
        problem = apply_slcr_constraint(problem, frac, curt_cost=slcr_curt_cost)
    if min_na_power_mw is not None:
        # PNA_ is variable index 1, expressed in GW-equivalent units (BUILD_SCALE=1000).
        # Na battery is the short-duration (4-hr reference) resource here -- VCEA's short-duration
        # (<10hr) storage mandate maps onto this power rating. Bath County (existing, 8hr duration,
        # not "newly acquired") doesn't count per SS56-585.5(E)(9); iron-air (100hr) is long-duration,
        # a separate VCEA bucket, so it's excluded from this constraint too.
        # CORRECTED (this session, Internal Debugging Log #39): this used to unconditionally
        # OVERWRITE whatever lower bound build_problem() had already set from prior_na_power_mw,
        # rather than combining the two. Harmless for every regular Scenario 1 checkpoint solved
        # this session, since the RPS-driven build always exceeded the VCEA floor there anyway --
        # but a real bug once a relaxed target (Scenario 1B's own 5%-gas 2045) makes the LP want
        # to build less than the VCEA floor would allow, while the prior checkpoint's own,
        # already-built capacity is LARGER than that floor: this line was silently erasing the
        # monotonicity bound, letting the LP "unbuild" storage that would, in reality, already
        # physically exist. Caught directly: Scenario 1B's 2045 solve showed PNA_mw dropping below
        # its own prior (2044) checkpoint's value. Fixed by taking the max of the two floors.
        PNA_ = 1
        lo, hi = problem['bounds'][PNA_]
        combined_floor = max(min_na_power_mw, lo * problem['BUILD_SCALE']) / problem['BUILD_SCALE']
        problem['bounds'][PNA_] = (combined_floor, hi)
        # Pair with a realistic duration (default 4hr, matching the model's own NA cost-basis reference)
        # so the LP can't satisfy the MW mandate with a near-zero-energy degenerate battery.
        ENA_ = 2
        min_mwh = min_na_power_mw * min_na_duration_hr
        lo2, hi2 = problem['bounds'][ENA_]
        combined_floor_ena = max(min_mwh, lo2 * problem['BUILD_SCALE']) / problem['BUILD_SCALE']
        problem['bounds'][ENA_] = (combined_floor_ena, hi2)
        # CORRECTED (2026-08-16): the fixed-floor bound above only enforces the duration ratio at
        # the regulatory MANDATE level (min_na_power_mw) -- if the LP builds MORE than that (e.g. to
        # satisfy the reserve-margin constraint below), that additional power isn't required to carry
        # any paired energy, producing a degenerate near-zero-duration increment for exactly the
        # portion beyond the mandate. Add a TRUE proportional constraint tying ENA_ to whatever PNA_
        # the LP actually builds, not just the fixed mandate number: ENA_ >= min_na_duration_hr * PNA_.
        BS = problem['BUILD_SCALE']
        prop_row = sparse.csr_matrix(([min_na_duration_hr, -1.0], ([0,0],[PNA_,ENA_])), shape=(1, len(problem['c'])))
        problem['A_ub'] = sparse.vstack([problem['A_ub'], prop_row]).tocsr()
        problem['b_ub'] = np.concatenate([problem['b_ub'], [0.0]])
    if min_efe_power_mw is not None and min_efe_power_mw > 0:
        # NEW (2026-08-16): VCEA long-duration storage floor -- previously not enforced anywhere in this
        # model at all (EFE_ floated freely from a bound of 0). SS56-585.5(E)(4): 4,000 MW total by 2045,
        # half (2,000 MW) by 2035, interpolated for years between via vcea_long_duration_floor_mw(). Iron-
        # air's build variable (EFE_) is energy (MWh), so the MW floor is converted via its fixed 100-hour
        # duration design (FE_DURATION) -- no separate power-vs-energy pairing needed the way Na has one,
        # since iron-air has only one build variable, not two.
        # CORRECTED (this session, same fix and same reasoning as the PNA_/ENA_ bounds above,
        # Internal Debugging Log #39): combine with, rather than overwrite, whatever lower bound
        # prior_ironair_energy_mwh already set.
        EFE_ = 3
        min_efe_mwh = min_efe_power_mw * lp.FE_DURATION
        lo3, hi3 = problem['bounds'][EFE_]
        combined_floor_efe = max(min_efe_mwh, lo3 * problem['BUILD_SCALE']) / problem['BUILD_SCALE']
        problem['bounds'][EFE_] = (combined_floor_efe, hi3)
    reserve_info = None
    if reserve_margin_hint is not None:
        hour_of_maximum_net_demand, demand_at_peak, nuclear_at_peak, wind_cf_at_peak, solar_cf_at_peak = reserve_margin_hint
        # EXTENDED (2026-09-09): the distributed segment's own peak-hour CF, when enabled -- passed as
        # a SEPARATE parameter rather than folded into the existing 5-tuple above, so Scenario 1/1B's
        # own reserve_margin_hint shape (and every place that already unpacks it) is completely
        # unaffected. See add_reserve_margin_constraint()'s own docstring for the credit-fraction
        # question this deliberately does not resolve on its own.
        dist_solar_cf_at_peak = distributed_solar_cf[hour_of_maximum_net_demand] if (enable_distributed_segment and distributed_solar_cf is not None) else 0.0
        problem, reserve_info = add_reserve_margin_constraint(
            problem, capacity_cap_mw, hour_of_maximum_net_demand, demand_at_peak, nuclear_at_peak,
            wind_cf_at_peak, solar_cf_at_peak, IRM=IRM,
            distributed_solar_cf_at_peak=dist_solar_cf_at_peak,
            distributed_reserve_margin_credit_fraction=distributed_reserve_margin_credit_fraction)
    res = lp.solve_problem(problem)
    IDX = problem['IDX']; hv_params = problem['hv_params']; T = problem['T']
    NVAR_BUILD, NVAR_PER_HOUR = hv_params
    def hv(t,k): return NVAR_BUILD + t*NVAR_PER_HOUR + k
    x = res.x
    S_mw = x[0]*problem['BUILD_SCALE']; PNA_mw = x[1]*problem['BUILD_SCALE']
    ENA_mwh = x[2]*problem['BUILD_SCALE']; EFE_mwh = x[3]*problem['BUILD_SCALE']
    g = np.array([x[hv(t,IDX['g'])] for t in range(T)])
    unserved = np.array([x[hv(t,IDX['unserved'])] for t in range(T)])
    curt = np.array([x[hv(t,IDX['curt'])] for t in range(T)])
    gas_gwh = g.sum()/1000.0
    nonnuclear_demand = (demand - nuclear).sum()
    achieved_share = g.sum()/nonnuclear_demand
    peak_g = g.max()
    out = dict(status=res.status, success=res.success, obj=res.fun, S_mw=S_mw, PNA_mw=PNA_mw,
                ENA_mwh=ENA_mwh, EFE_mwh=EFE_mwh, gas_gwh=gas_gwh, achieved_share=achieved_share,
                peak_g_mw=peak_g, unserved_mwh=unserved.sum(), curt_mwh=curt.sum())
    # EXTENDED (2026-09-09): distributed build sizes, extracted the same way as the utility-scale
    # ones above -- exact zeros when enable_distributed_segment=False, since 'distributed_builds'
    # indices point at variables pinned to (0, 0) in that case.
    dist_S_idx, dist_PNA_idx, dist_ENA_idx, dist_EFE_idx = problem['distributed_builds']
    dist_S_mw = x[dist_S_idx]*problem['BUILD_SCALE']; dist_PNA_mw = x[dist_PNA_idx]*problem['BUILD_SCALE']
    dist_ENA_mwh = x[dist_ENA_idx]*problem['BUILD_SCALE']; dist_EFE_mwh = x[dist_EFE_idx]*problem['BUILD_SCALE']
    out.update(dist_S_mw=dist_S_mw, dist_PNA_mw=dist_PNA_mw, dist_ENA_mwh=dist_ENA_mwh, dist_EFE_mwh=dist_EFE_mwh)
    # NEW (2026-09-09): return_raw_result, default False (no change for any existing caller). Exposes
    # the raw scipy OptimizeResult (res) and the problem dict (for its own IDX/hv() mapping) so a
    # caller can inspect reduced costs / shadow prices directly -- e.g. res.lower.marginals[PNA_idx]
    # to check whether the VCEA storage floor is genuinely binding -- without having to replicate this
    # function's own bound-adjustment logic (min_na_power_mw combining, the ENA_>=duration*PNA_
    # proportional constraint, capacity_cap_mw) a second time elsewhere, which risks drifting out of
    # sync with the real logic here.
    if return_raw_result:
        out['res'] = res
        out['problem'] = problem
    if return_hourly:
        bsoc = np.array([x[hv(t,IDX['bsoc'])] for t in range(T)])
        nsoc = np.array([x[hv(t,IDX['nsoc'])] for t in range(T)])
        fsoc = np.array([x[hv(t,IDX['fsoc'])] for t in range(T)])
        bd = np.array([x[hv(t,IDX['bd'])] for t in range(T)]); bc = np.array([x[hv(t,IDX['bc'])] for t in range(T)])
        nd = np.array([x[hv(t,IDX['nd'])] for t in range(T)]); nc = np.array([x[hv(t,IDX['nc'])] for t in range(T)])
        fd = np.array([x[hv(t,IDX['fd'])] for t in range(T)]); fc = np.array([x[hv(t,IDX['fc'])] for t in range(T)])
        new_solar_gen = S_mw*solar_cf
        # EXTENDED (2026-09-09): distributed hourly arrays -- all exactly zero when
        # enable_distributed_segment=False.
        dist_nc = np.array([x[hv(t,IDX['dist_na_charge_mw'])] for t in range(T)])
        dist_nd = np.array([x[hv(t,IDX['dist_na_discharge_mw'])] for t in range(T)])
        dist_nsoc = np.array([x[hv(t,IDX['dist_na_soc_mwh'])] for t in range(T)])
        dist_fc = np.array([x[hv(t,IDX['dist_fe_charge_mw'])] for t in range(T)])
        dist_fd = np.array([x[hv(t,IDX['dist_fe_discharge_mw'])] for t in range(T)])
        dist_fsoc = np.array([x[hv(t,IDX['dist_fe_soc_mwh'])] for t in range(T)])
        dist_curt = np.array([x[hv(t,IDX['dist_curtailment_mw'])] for t in range(T)])
        dist_solar_gen = dist_S_mw * (distributed_solar_cf if distributed_solar_cf is not None else np.zeros(T))
        out['hourly'] = dict(g=g, curt=curt, unserved=unserved, bsoc=bsoc, nsoc=nsoc, fsoc=fsoc,
                              bd=bd, bc=bc, nd=nd, nc=nc, fd=fd, fc=fc, new_solar_gen=new_solar_gen,
                              exist_solar=exist_solar, demand=demand, nuclear=nuclear,
                              wind_gen=lp.CVOW_MW*wind_cf,
                              dist_solar_gen=dist_solar_gen, dist_nc=dist_nc, dist_nd=dist_nd,
                              dist_nsoc=dist_nsoc, dist_fc=dist_fc, dist_fd=dist_fd,
                              dist_fsoc=dist_fsoc, dist_curt=dist_curt)
    return out


def run_solve_multi_duration(year, frac, demand, exist_solar, solar_cf, wind_cf, nuclear, capacity_cap_mw=None,
                              return_hourly=False, min_total_storage_mw=None, durations=(4.0,6.0,8.0)):
    """Same as run_solve() but using build_problem_multi_duration -- discrete 4/6/8hr sodium products,
    all sharing the same NREL-derived per-unit costs (see na_power_energy_split). min_total_storage_mw
    applies to the SUM of power capacity across all duration classes (VCEA's short-duration mandate
    doesn't care which specific duration class satisfies it, only that it's <10hr)."""
    lp.SOLAR_CAPEX = lp.solar_capex(year)
    lp.FE_ENERGY_CAPEX = lp.fe_capex_kwh(year)
    lp.FE_RTE_CHARGE = lp.iron_air_rte(year)
    problem = lp.build_problem_multi_duration(solar_cf, wind_cf, nuclear, exist_solar, demand, frac,
                                                verbose=False, gas_price_mwh=lp.gas_cost_mwh(year, heat_rate=lp.SIMPLE_CYCLE_HEAT_RATE),
                                                na_year=year, durations=durations)
    IDX = problem['IDX']; NVAR_BUILD, NVAR_PER_HOUR = problem['hv_params']; T = problem['T']
    def hv(t,k): return NVAR_BUILD + t*NVAR_PER_HOUR + k
    if capacity_cap_mw is not None:
        for t in range(T):
            lo, hi = problem['bounds'][hv(t,IDX['g'])]
            problem['bounds'][hv(t,IDX['g'])] = (lo, capacity_cap_mw)
    if min_total_storage_mw is not None:
        n = len(problem['P_'])
        new_row = sparse.csr_matrix(([-1.0]*n, ([0]*n, problem['P_'])), shape=(1, len(problem['c'])))
        problem['A_ub'] = sparse.vstack([problem['A_ub'], new_row]).tocsr()
        problem['b_ub'] = np.concatenate([problem['b_ub'], [-min_total_storage_mw/problem['BUILD_SCALE']]])
    res = lp.solve_problem(problem)
    x = res.x; BS = problem['BUILD_SCALE']
    S_mw = x[problem['S_']]*BS
    dur_results = []
    for i, d in enumerate(problem['durations']):
        P = x[problem['P_'][i]]*BS; E = x[problem['E_'][i]]*BS
        dur_results.append((d, P, E))
    EFE_mwh = x[problem['EFE_']]*BS
    g = np.array([x[hv(t,IDX['g'])] for t in range(T)])
    unserved = np.array([x[hv(t,IDX['unserved'])] for t in range(T)])
    curt = np.array([x[hv(t,IDX['curt'])] for t in range(T)])
    gas_gwh = g.sum()/1000.0
    nonnuclear_demand = (demand - nuclear).sum()
    achieved_share = g.sum()/nonnuclear_demand
    out = dict(status=res.status, success=res.success, obj=res.fun, S_mw=S_mw, dur_results=dur_results,
               EFE_mwh=EFE_mwh, gas_gwh=gas_gwh, achieved_share=achieved_share, peak_g_mw=g.max(),
               unserved_mwh=unserved.sum(), curt_mwh=curt.sum())
    return out


def converge_frac(year, gas_target_share, demand, exist_solar, solar_cf, wind_cf, nuclear, tol=0.003, max_iter=3,
                   capacity_cap_mw=None, start_frac=None, min_na_power_mw='vcea_default', min_na_duration_hr=6.0,
                   min_efe_power_mw='vcea_default', prior_solar_mw=0.0, prior_na_power_mw=0.0,
                   prior_na_energy_mwh=0.0, prior_ironair_energy_mwh=0.0,
                   reserve_margin_hint=None, IRM=0.177,
                   enable_distributed_segment=False, distributed_solar_cf=None,
                   distributed_share_of_total_solar=0.20, distributed_exogenous_price_mwh=None,
                   prior_distributed_solar_mw=0.0, prior_distributed_na_power_mw=0.0,
                   prior_distributed_na_energy_mwh=0.0, prior_distributed_ironair_energy_mwh=0.0,
                   distributed_reserve_margin_credit_fraction=0.0,
                   gas_merit_order=None, gas_merit_order_year=None):
    # NOTE (2026-08-23, renamed from the ambiguous 'target_share' -- see Internal Debugging Log #51):
    # this parameter SHADOWS the module-level gas_target_share(year) function within this function's
    # own body -- confirmed harmless here (this function never calls that module-level function
    # internally, only uses its own parameter as a value), but worth knowing before adding new code
    # to this function that might need to call gas_target_share(some_other_year) directly.
    # EXTENDED (this session): prior_* kwargs, passed through to run_solve() at every iteration --
    # without this, frac would converge against the WRONG problem (unlinked), and a fresh re-solve
    # at that frac WITH linking added afterward would not actually hit gas_target_share, since linking
    # changes the LP's own energy balance and therefore the frac/achieved-share relationship itself.
    # EXTENDED AGAIN (this session): reserve_margin_hint/IRM, same reasoning -- converging frac
    # without the reserve-margin constraint, then bolting the constraint onto a single final solve
    # afterward, is the identical shortcut that produced a $124.8B, 1.19M-MWh-unserved false start
    # when first attempted with SLCR (Internal Debugging Log #26). Not repeating that mistake here.
    # EXTENDED (2026-09-09): distributed_* kwargs, forwarded to run_solve() at every iteration, same
    # reasoning as above -- distributed solar/storage change the LP's own energy balance too (the
    # coupled (A) row in build_problem()), so frac must converge WITH the distributed segment present
    # when enable_distributed_segment=True, not against an unrelated, distributed-free problem.
    frac = start_frac if start_frac is not None else gas_target_share  # first guess
    history = []
    for i in range(max_iter):
        t0 = time.time()
        r = run_solve(year, frac, demand, exist_solar, solar_cf, wind_cf, nuclear, capacity_cap_mw=capacity_cap_mw,
                      min_na_power_mw=min_na_power_mw, min_na_duration_hr=min_na_duration_hr,
                      min_efe_power_mw=min_efe_power_mw, prior_solar_mw=prior_solar_mw,
                      prior_na_power_mw=prior_na_power_mw, prior_na_energy_mwh=prior_na_energy_mwh,
                      prior_ironair_energy_mwh=prior_ironair_energy_mwh,
                      reserve_margin_hint=reserve_margin_hint, IRM=IRM,
                      gas_merit_order=gas_merit_order, gas_merit_order_year=gas_merit_order_year,
                      enable_distributed_segment=enable_distributed_segment,
                      distributed_solar_cf=distributed_solar_cf,
                      distributed_share_of_total_solar=distributed_share_of_total_solar,
                      distributed_exogenous_price_mwh=distributed_exogenous_price_mwh,
                      prior_distributed_solar_mw=prior_distributed_solar_mw,
                      prior_distributed_na_power_mw=prior_distributed_na_power_mw,
                      prior_distributed_na_energy_mwh=prior_distributed_na_energy_mwh,
                      prior_distributed_ironair_energy_mwh=prior_distributed_ironair_energy_mwh,
                      distributed_reserve_margin_credit_fraction=distributed_reserve_margin_credit_fraction)
        dt = time.time()-t0
        history.append((frac, r['achieved_share'], dt))
        print(f"  iter{i}: frac={frac:.4f} achieved={r['achieved_share']:.4f} target={gas_target_share:.4f} "
              f"gap={gas_target_share-r['achieved_share']:+.4f} ({dt:.0f}s)", flush=True)
        gap = gas_target_share - r['achieved_share']
        if abs(gap) <= tol:
            return frac, r, history
        if len(history) >= 2:
            (f0,a0,_),(f1,a1,_) = history[-2], history[-1]
            if abs(a1-a0) < 1e-6:
                print("  achieved share unchanged across two fracs -- capacity-cap-style saturation; stopping search", flush=True)
                return frac, r, history
        # linear extrapolation using ratio frac/achieved from most recent point
        ratio = frac/r['achieved_share'] if r['achieved_share'] > 1e-9 else 1.0
        frac = min(0.999, max(0.0001, gas_target_share*ratio))
    return frac, r, history


# ---------------------------------------------------------------------------
# Reserve-margin constraint (PJM IRM), added per project decisions 2026-08-16:
#   1. Hourly actual resource availability, not one blended average (disclosed assumption)
#   2. Peak NET demand (not gross peak) is the target hour -- a system headed toward 100%
#      clean energy makes the net-demand-stress hour the real adequacy risk (disclosed assumption)
#   3. Full rated power for dispatchable resources (gas, storage) -- installed capacity available
#      if called upon, consistent with NSPM's own definition (disclosed assumption)
#   4. This is an explicit, simplified proxy for full LOLE-based adequacy on a single deterministic
#      weather-year solve -- NOT a replication of PJM's actual 40,300-simulated-year methodology
#      (A.12/A.13) -- stated plainly, not implied to be equivalent
#   5. Hard constraint, not a soft/priced shortfall (decision)
# ---------------------------------------------------------------------------

# CVOW_MW_CORRECTED removed (2026-08-16): was a separate, narrowly-scoped duplicate of the same
# correction (2,587.2 MW real nameplate) that had already been applied here but never propagated to
# lp_model.py's own CVOW_MW -- exactly the kind of drift a duplicated constant invites. Fixed at the
# source (lp_model.CVOW_MW) instead; this constraint now references that directly, so there is only
# ever one place this value can go stale.

def find_hour_of_maximum_net_demand(hourly_data, demand, nuclear, exist_solar):
    """Returns the hour index of maximum NET demand -- the adequacy-stress hour.

        net demand = demand - nuclear - exist_solar - wind_gen - new_solar_gen

    RENAMED 2026-09-11, from find_peak_net_demand_hour returning t_peak. The old name violated
    Software_Engineering_Standards Rule 12.2 (no terse fragments) and 12.4 (anything crossing a
    function boundary gets a real name) -- t_peak crossed four. It also said nothing about WHICH
    peak, which mattered: a reader could reasonably assume gross demand, and this analysis's own
    documentation did assume that, in three places, until the code was read.

    THE ASYMMETRY WORTH KNOWING, because the name cannot carry it: this function selects the hour
    on NET demand, but add_reserve_margin_constraint writes its requirement against GROSS demand at
    that hour -- (1 + IRM) * demand[hour], not net demand. That is deliberate and defensible: the
    stress hour is a net-load question, while the adequacy test is against the load actually served.
    But the two quantities differ, and any reader tracing this constraint needs both facts.
    """
    net_demand = demand - nuclear - exist_solar - hourly_data['wind_gen'] - hourly_data['new_solar_gen']
    hour_of_maximum_net_demand = int(np.argmax(net_demand))
    return hour_of_maximum_net_demand, net_demand[hour_of_maximum_net_demand]


def add_reserve_margin_constraint(problem, gas_cap_mw, hour_of_maximum_net_demand, demand_at_peak, nuclear_at_peak,
                                    wind_cf_at_peak, solar_cf_at_peak, IRM=0.177,
                                    distributed_solar_cf_at_peak=0.0,
                                    distributed_reserve_margin_credit_fraction=0.0):
    """Hard constraint at hour_of_maximum_net_demand: nuclear + gas_cap + CVOW*wind_cf[hour_of_maximum_net_demand] + PNA_*BUILD_SCALE +
    S_*BUILD_SCALE*solar_cf[hour_of_maximum_net_demand] >= (1+IRM)*demand[hour_of_maximum_net_demand]. Modifies problem in place (A_ub/b_ub)
    and returns it. S_ and PNA_ are looked up from problem['S_']/problem['P_'][0] (multi-duration)
    or hardcoded indices 0/1 (single-resource build_problem). Iron-air is NOT counted toward reserve-
    margin availability for utility-scale storage either (pre-existing behavior, unchanged here) --
    the distributed segment's own iron-air is excluded from the credit below for the same consistency
    reason, not a new, separately-made decision.

    EXTENDED (2026-09-09): distributed_reserve_margin_credit_fraction (default 0.0) scales how much of
    the distributed segment's own solar + Na-power nameplate counts toward this constraint's available
    capacity -- 0.0 (default) reproduces this function's pre-existing behavior exactly, crediting
    nothing. NOT a settled question -- see run_solve()'s own docstring for the full disclosure: 1.0
    (full nameplate) would contradict the six-day-lookahead firming analysis's own ~4.3%-firm finding;
    that figure, not 1.0 or 0.0, is the empirically-grounded reference point if/when this gets a real,
    decided value."""
    BS = problem['BUILD_SCALE']
    S_idx = problem.get('S_', 0)
    if 'P_' in problem:  # multi-duration: sum contribution across all duration classes
        PNA_idxs = problem['P_']
    else:
        PNA_idxs = [1]
    target = (1+IRM) * demand_at_peak
    wind_mw = lp.CVOW_MW * wind_cf_at_peak
    fixed_avail = nuclear_at_peak + gas_cap_mw + wind_mw
    rhs = fixed_avail - target
    cols, data = [], []
    for p_idx in PNA_idxs:
        cols.append(p_idx); data.append(-BS)
    if solar_cf_at_peak > 1e-9:
        cols.append(S_idx); data.append(-BS*solar_cf_at_peak)
    if distributed_reserve_margin_credit_fraction > 1e-9 and 'distributed_builds' in problem:
        dist_S_idx, dist_PNA_idx, _, _ = problem['distributed_builds']
        f = distributed_reserve_margin_credit_fraction
        cols.append(dist_PNA_idx); data.append(-BS*f)
        if distributed_solar_cf_at_peak > 1e-9:
            cols.append(dist_S_idx); data.append(-BS*f*distributed_solar_cf_at_peak)
    new_row = sparse.csr_matrix((data, ([0]*len(cols), cols)), shape=(1, len(problem['c'])))
    problem['A_ub'] = sparse.vstack([problem['A_ub'], new_row]).tocsr()
    problem['b_ub'] = np.concatenate([problem['b_ub'], [rhs]])
    gap = target - fixed_avail
    return problem, dict(hour_of_maximum_net_demand=hour_of_maximum_net_demand, target_mw=target, fixed_avail_mw=fixed_avail, gap_mw=gap)
