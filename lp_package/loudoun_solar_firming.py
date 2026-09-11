"""
loudoun_solar_firming.py

Multi-day solar firming analysis: for a solar/battery fleet, finds the highest FLAT MW level a
facility could reliably commit to deliver each day in a day-ahead market, using a 72-hour
lookahead (a storm two days out pulls today's committed level down even if today's own solar is
good -- matching the uploaded document's described "weather uncertainty buffering" behavior), with
the battery's real SoC chained continuously across days (not reset). Excess solar above the
committed level charges the battery rather than being delivered, per direct user framing ("every
solar/battery owner who guarantees a firmed energy delivery... doesn't send more power than they
promise as firmed").

Also builds the blended-split optimization: given a fixed total MW, split between a short-duration
(10-hr, sodium-ion, 90% RTE) and long-duration (100-hr, iron-air, 80% RTE) sub-fleet -- both RTE
figures reused directly from VA_SLCOE_Model.xlsx's own Assumptions & Sources tab (rows 35/39) per
Rule 6, not re-derived -- and finds the split that maximizes the WORST daily combined firm level
across the full weather record, per direct user decision ("If we are trying to identify the
highest level of transmission avoidance, I believe we would optimize to maximize the worst daily
firm level").

Reuses BatteryDispatchDesign._dispatch_one_hour directly (Rule 1) -- the per-hour physics are
identical to every other dispatch path in this project; only how "load" is defined differs (a
flat, self-chosen commitment level here, not a load profile lookup).
"""
from dataclasses import dataclass

import pandas as pd

from loudoun_battery_dispatch import BatteryDispatchDesign

# Category: Modeler Assumptions -- direct user decision this round: which chemistry/RTE pairs with
# which duration for the blended-split optimization. 10-hr maps to the project's own established
# short-duration chemistry (sodium-ion, VA_SLCOE_Model.xlsx row 35); 100-hr maps to the project's
# own established long-duration chemistry (iron-air, row 39) -- both RTE values reused directly
# from that sourced assumptions tab, not re-derived here.
SHORT_DURATION_HOURS = 10.0
SHORT_DURATION_RTE_PCT = 90.0  # sodium-ion, VA_SLCOE_Model.xlsx row 35
LONG_DURATION_HOURS = 100.0
LONG_DURATION_RTE_PCT = 80.0  # iron-air, VA_SLCOE_Model.xlsx row 39

# Category: Modeler Assumptions -- direct user decision this round ("chained, with at least a 72
# hour lookahead").
LOOKAHEAD_HOURS = 72

# Category: Modeler Assumptions -- direct user decision this round (matches
# DEFAULT_BUILDOUT_STARTING_SOC_PCT's own established 50% convention in loudoun_battery_dispatch.py).
DEFAULT_FIRMING_STARTING_SOC_PCT = 50.0


def _can_hold_flat_level_without_shortfall(solar_values: list, starting_soc: float,
                                            energy_capacity: float, power_mw: float,
                                            rte_fraction: float, flat_level_mw: float,
                                            tolerance_mw: float = 1e-6) -> bool:
    """Pure feasibility check (a 'what-if', does not mutate any real
    state): simulates hour-by-hour, using BatteryDispatchDesign's own
    _dispatch_one_hour (Rule 1 -- identical physics to every other
    dispatch path in this project), whether committing to deliver
    flat_level_mw for every hour in solar_values would ever produce a
    shortfall (residual_import_mw > tolerance_mw). Returns False at the
    first hour that would shortfall (doesn't bother simulating the rest --
    one violation is enough to reject this flat_level_mw), True if every
    hour clears with zero shortfall."""
    soc = starting_soc
    for solar_mw in solar_values:
        _, _, _, residual_import_mw, soc = BatteryDispatchDesign._dispatch_one_hour(
            solar_mw=solar_mw, load_mw=flat_level_mw, current_soc=soc,
            energy_capacity=energy_capacity, power_mw=power_mw, rte_fraction=rte_fraction,
        )
        if residual_import_mw > tolerance_mw:
            return False
    return True


def solve_max_flat_level_for_window(solar_values: list, starting_soc: float, energy_capacity: float,
                                     power_mw: float, rte_fraction: float,
                                     tolerance_mw: float = 0.01) -> float:
    """Bisection search (same pattern as
    loudoun_load_shape_gap_analysis.py's own floor-factor solver) for the
    highest flat_level_mw such that
    _can_hold_flat_level_without_shortfall(solar_values, ...) is True.
    Upper bound is power_mw -- the sub-fleet's own discharge/interconnection
    rating, since a facility would not commit to delivering more than its
    own interconnection capacity regardless of how much solar it has (a
    real, physically-motivated bound, not an arbitrary search limit).
    Lower bound is 0.0 (always feasible -- delivering nothing trivially
    never shortfalls). Returns the solved flat_level_mw, accurate to
    within tolerance_mw."""
    if power_mw <= 0:
        return 0.0
    if not _can_hold_flat_level_without_shortfall(
        solar_values, starting_soc, energy_capacity, power_mw, rte_fraction, flat_level_mw=0.0
    ):
        raise ValueError(
            "Even a flat_level_mw of 0.0 is infeasible for this window -- this should be "
            "impossible (delivering nothing should always clear) and indicates a real bug, "
            "not a legitimate result; not silently returning 0.0."
        )

    low, high = 0.0, power_mw
    while high - low > tolerance_mw:
        mid = (low + high) / 2
        if _can_hold_flat_level_without_shortfall(
            solar_values, starting_soc, energy_capacity, power_mw, rte_fraction, flat_level_mw=mid
        ):
            low = mid
        else:
            high = mid
    return low


def _extract_consecutive_hour_window(solar_hourly: pd.DataFrame, start_pos: int, n_hours: int):
    """Extracts exactly n_hours consecutive rows starting at position
    start_pos, verifying each row is exactly 1 hour after the previous --
    the same underlying continuity check already established in
    loudoun_streak_finder.py (found and fixed there as a real bug once:
    positional adjacency in a concatenated multi-year dataframe is not
    the same as genuine 1-hour temporal adjacency), applied here to a
    fixed-length window rather than a variable-length streak. Returns
    None if fewer than n_hours rows remain, or if a gap is found within
    the would-be window -- both cases mean this starting position cannot
    support a full, genuinely-consecutive n_hours window."""
    if start_pos + n_hours > len(solar_hourly):
        return None
    window = solar_hourly.iloc[start_pos:start_pos + n_hours]
    gaps = window["timestamp"].diff().iloc[1:]
    if (gaps != pd.Timedelta(hours=1)).any():
        return None
    return window


def compute_chained_daily_firm_levels(solar_hourly: pd.DataFrame, power_mw: float, duration_hours: float,
                                       rte_pct: float,
                                       starting_soc_pct: float = DEFAULT_FIRMING_STARTING_SOC_PCT,
                                       lookahead_hours: int = LOOKAHEAD_HOURS) -> pd.Series:
    """Chained, day-by-day flat-level solver across the full record. For
    each day, uses the REAL, chained current SoC and the next
    lookahead_hours of solar data to solve for that day's max feasible
    flat level (via solve_max_flat_level_for_window -- a 'what-if', not
    yet committed), then ACTUALLY operates the battery for just that
    day's 24 hours at the solved level (mutating the real running SoC
    this time, via BatteryDispatchDesign._dispatch_one_hour directly,
    Rule 1) -- the real ending SoC becomes tomorrow's starting SoC. Days
    without a full lookahead_hours of genuinely-consecutive data
    remaining (e.g. the last ~2 days of a 9-year record, per direct user
    decision) are skipped entirely rather than silently truncating the
    lookahead rule for those days. A day whose lookahead window spans a
    MID-record gap (e.g. a dropped Feb 29) is also skipped, but
    processing continues with later days past the gap -- SoC simply
    stays frozen at its last successfully-processed value across any
    skipped day(s), rather than being fabricated or reset, and the next
    successfully-processed day picks up from there. Returns a pandas
    Series of daily firm levels (MW), indexed by date."""
    df = solar_hourly.sort_values("timestamp").reset_index(drop=True)
    energy_capacity = power_mw * duration_hours
    rte_fraction = rte_pct / 100
    soc = starting_soc_pct / 100 * energy_capacity

    daily_results = []
    i = 0
    while i < len(df):
        if i + lookahead_hours > len(df):
            # Genuinely out of future data -- no later starting position could ever succeed
            # either, since the record is finite. This is the only case where halting the whole
            # loop (rather than skipping just this one day) is correct.
            break

        lookahead_window = _extract_consecutive_hour_window(df, i, lookahead_hours)
        if lookahead_window is None:
            # Enough ROWS remain, but they're not genuinely consecutive (a gap -- e.g. a dropped
            # Feb 29 -- falls within this specific 72-hr window). This starting position can't
            # support a full lookahead, but LATER starting positions past the gap still might --
            # skip just this one day and try the next, do NOT break the entire loop. A real bug
            # found and fixed this round: the original version used `break` here too, which
            # silently discarded every day after the FIRST gap anywhere in the record (e.g. only
            # ~57 of ~3,285 days survived on the real 9-year Sterling record, since the first
            # Feb-29 gap in 2012 halted processing before 2013-2020 were ever reached at all).
            i += 24
            continue

        today_window = _extract_consecutive_hour_window(df, i, 24)
        if today_window is None:
            # Should not happen if the longer lookahead window already succeeded (24 hours is a
            # subset of lookahead_hours), but defensive -- same skip-not-break reasoning as above.
            i += 24
            continue

        solar_lookahead_values = lookahead_window["mw"].tolist()
        firm_level_mw = solve_max_flat_level_for_window(
            solar_values=solar_lookahead_values, starting_soc=soc, energy_capacity=energy_capacity,
            power_mw=power_mw, rte_fraction=rte_fraction,
        )

        # Now ACTUALLY operate the battery for just today's 24 hours at firm_level_mw, mutating
        # the real running soc (not a what-if this time).
        for _, row in today_window.iterrows():
            _, _, _, _, soc = BatteryDispatchDesign._dispatch_one_hour(
                solar_mw=row["mw"], load_mw=firm_level_mw, current_soc=soc,
                energy_capacity=energy_capacity, power_mw=power_mw, rte_fraction=rte_fraction,
            )

        daily_results.append({"date": today_window["timestamp"].iloc[0].date(), "firm_level_mw": firm_level_mw})
        i += 24  # advance by one day (24 hours), not by the full lookahead window

    if len(daily_results) == 0:
        # A real edge case, not just a test artifact: pd.DataFrame([]).set_index("date") raises
        # KeyError rather than producing a sensible empty result, since an empty list of dicts has
        # no columns at all -- return an explicitly-typed empty Series instead of crashing.
        return pd.Series(dtype=float, name="firm_level_mw")
    return pd.DataFrame(daily_results).set_index("date")["firm_level_mw"]


@dataclass
class BlendedSplitResult:
    """One grid point's result: the split fraction tested, and the
    resulting combined (short + long sub-fleet summed) daily firm-level
    series across the full weather record."""
    split_fraction_short: float  # 0.0-1.0, share of total_mw allocated to the 10-hr sub-fleet
    daily_combined_firm_levels: pd.Series  # F_short(day) + F_long(day), summed per day

    @property
    def worst_daily_firm_level_mw(self) -> float:
        """The MINIMUM daily combined firm level across the record --
        per direct user decision, this is what the split optimization
        maximizes ("optimize to maximize the worst daily firm level")."""
        return self.daily_combined_firm_levels.min()


def find_optimal_blended_split(raw_solar_profile, total_mw: float, split_step_pct: float = 5.0,
                                starting_soc_pct: float = DEFAULT_FIRMING_STARTING_SOC_PCT,
                                lookahead_hours: int = LOOKAHEAD_HOURS,
                                split_fraction_min: float = 0.0,
                                split_fraction_max: float = 1.0) -> dict:
    """Grid search over the split fraction s (split_fraction_min to
    split_fraction_max of total_mw, in split_step_pct increments --
    defaults to the full 0%-100% range, unchanged from this function's
    original behavior) between a SHORT-duration (10-hr,
    sodium-ion, 90% RTE) and LONG-duration (100-hr, iron-air, 80% RTE)
    sub-fleet -- each getting s (or 1-s) of total_mw and a proportional
    share of the total solar (per this project's established 1:1
    solar:storage pairing convention, reusing
    SolarSiteProfile.scale_to_fleet_mw for the rescaling, Rule 1) -- and
    finds the split that maximizes the WORST (minimum) daily COMBINED
    (short + long summed) firm level across the full weather record, per
    direct user decision ("If we are trying to identify the highest level
    of transmission avoidance, I believe we would optimize to maximize
    the worst daily firm level"). A grid search (not a gradient-based
    optimizer) since the objective -- a minimum over thousands of daily
    values -- is likely not smooth; slower but transparent and directly
    hand-checkable at each point.

    ADDED 2026-09-05 (split_fraction_min/max): extends this function
    (SES Rule 1 -- backward-compatible, default behavior unchanged)
    rather than a new duplicate function, so a longer lookahead's own
    heavier per-point cost (both short AND long duration compute at
    every interior point, roughly double the cost of the 0%/100%
    extremes alone) can be split across multiple calls -- e.g. one call
    per half of the range -- while preserving full split_step_pct
    resolution, instead of coarsening the grid to fit one call's own
    timeout. Caller is responsible for combining multiple partial-range
    results' own all_results lists and re-deriving best_result across
    the combined set if the range is split this way.

    raw_solar_profile is the UN-scaled SolarSiteProfile (this function
    calls .scale_to_fleet_mw() internally, twice per grid point, once
    per sub-fleet's own MW share).

    Returns {'all_results': [BlendedSplitResult, ...], 'best_result':
    BlendedSplitResult} -- the single grid point with the highest
    worst_daily_firm_level_mw, plus every grid point's own result for
    inspection."""
    if not (0.0 <= split_fraction_min < split_fraction_max <= 1.0):
        raise ValueError(
            f"split_fraction_min ({split_fraction_min}) must be < "
            f"split_fraction_max ({split_fraction_max}), both within [0,1].")
    all_results = []
    split_fraction = split_fraction_min
    while split_fraction <= split_fraction_max + 1e-9:
        short_mw = split_fraction * total_mw
        long_mw = (1 - split_fraction) * total_mw

        short_solar = raw_solar_profile.scale_to_fleet_mw(short_mw) if short_mw > 0 else None
        long_solar = raw_solar_profile.scale_to_fleet_mw(long_mw) if long_mw > 0 else None

        if short_mw > 0:
            short_daily = compute_chained_daily_firm_levels(
                solar_hourly=short_solar.hourly, power_mw=short_mw, duration_hours=SHORT_DURATION_HOURS,
                rte_pct=SHORT_DURATION_RTE_PCT, starting_soc_pct=starting_soc_pct,
                lookahead_hours=lookahead_hours,
            )
        else:
            short_daily = None

        if long_mw > 0:
            long_daily = compute_chained_daily_firm_levels(
                solar_hourly=long_solar.hourly, power_mw=long_mw, duration_hours=LONG_DURATION_HOURS,
                rte_pct=LONG_DURATION_RTE_PCT, starting_soc_pct=starting_soc_pct,
                lookahead_hours=lookahead_hours,
            )
        else:
            long_daily = None

        if short_daily is not None and long_daily is not None:
            combined_daily = short_daily.add(long_daily, fill_value=0.0)
        elif short_daily is not None:
            combined_daily = short_daily
        else:
            combined_daily = long_daily

        all_results.append(BlendedSplitResult(
            split_fraction_short=split_fraction, daily_combined_firm_levels=combined_daily,
        ))
        split_fraction += split_step_pct / 100

    best_result = max(all_results, key=lambda r: r.worst_daily_firm_level_mw)
    return {"all_results": all_results, "best_result": best_result}
