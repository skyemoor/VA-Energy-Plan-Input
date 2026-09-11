"""
loudoun_load_shape_gap_analysis.py

Builds a worst-case, flattened load SHAPE from Dominion's real hourly load projections
(DOMLSEHourlyLoadProjections2024through2048.csv), then compares it against the real, scaled
9-year solar profile (loudoun_solar_hourly_profile.py) to find where and for how long the gap
between load and solar output is worst -- the "where are we weakest" question, per direct user
framing, deliberately deferred from any absolute Loudoun MWh magnitude ("we'll worry about actual
MWh load that fits that profile later").

LOAD SHAPE CONSTRUCTION, per direct user decisions this round:
- Load is assumed near-flat, reflecting Loudoun's data-center-dominated demand. Rather than a pure
  flat line, the real 2045 Dominion territory-wide hourly shape is used as the starting point (its
  own natural annual load factor -- avg/peak -- was directly verified at 79.4%, consistent with
  this project's already-established 2040/2048 figures of 78.0%/79.8%), then FLATTENED: every hour
  below a solved floor level (as a % of the profile's own peak) is raised up to that floor, while
  hours already at or above the floor are left untouched. The floor is solved via bisection so the
  resulting annual load factor hits exactly 90% -- "we have to think worst case, so 90% should be
  standard" (direct user decision). This only touches the low hours, matching "adjusted higher at
  the lower times" exactly; the peak is never changed by this transform.
- Both load and solar are expressed as a % of their own respective peaks/fleet capacity, not
  absolute MW -- deferring the real Loudoun load magnitude to a later step, per direct user
  framing.

OO STRUCTURE (Rule 1): LoadProfile is the one class tied to a specific data source (Dominion's
DOMLSE export format, via from_domlse_export()). Gap-severity streak-finding reuses
loudoun_streak_finder.find_longest_threshold_streaks (the same shared logic
loudoun_solar_hourly_profile.py's ScaledSolarProfile now also calls), rather than
reimplementing the same "find consecutive hours meeting a condition, respecting real time gaps"
algorithm a second time.
"""
from dataclasses import dataclass
from typing import List

import pandas as pd

from loudoun_streak_finder import ValueStreak, find_longest_threshold_streaks

# Category: Modeler Assumptions -- direct user decision this round ("we have to think worst
# case, so 90% should be standard"), not derived or looked up.
DEFAULT_TARGET_LOAD_FACTOR_PCT = 90.0

# Tooling-level bisection parameters (not a policy/fact constant, so not source-category tagged
# per Rule 8.3 -- same treatment as n_points/top_n defaults elsewhere in this project).
_BISECTION_TOLERANCE = 1e-6
_BISECTION_MAX_ITERATIONS = 100

_HOUR_COLS = [str(i) for i in range(1, 25)]


def _solve_floor_pct_for_target_load_factor(hourly_mw: pd.Series, peak_mw: float,
                                             target_load_factor_pct: float) -> float:
    """Bisection solve for the floor level (as a fraction of peak) such
    that raising every hour below that floor up to it produces the given
    target annual load factor (avg/peak). The resulting function
    (floor_frac -> load factor) is monotonically increasing from the
    series' own natural load factor (at floor_frac=0, no hours are
    raised) up to 100% (at floor_frac=1, every hour equals peak) -- a
    well-behaved root-finding problem, so a simple bisection is used
    rather than an external optimizer dependency for a one-dimensional,
    monotonic function."""
    target_fraction = target_load_factor_pct / 100

    def resulting_load_factor(floor_frac: float) -> float:
        adjusted = hourly_mw.clip(lower=floor_frac * peak_mw)
        return adjusted.mean() / peak_mw

    natural_load_factor = resulting_load_factor(0.0)
    if natural_load_factor >= target_fraction:
        raise ValueError(
            f"Natural load factor ({natural_load_factor:.1%}) already meets or exceeds the "
            f"target ({target_load_factor_pct}%) -- no flattening needed; this function is not "
            f"meant to lower a profile, only raise its low hours."
        )

    low, high = 0.0, 1.0
    for _ in range(_BISECTION_MAX_ITERATIONS):
        mid = (low + high) / 2
        lf = resulting_load_factor(mid)
        if abs(lf - target_fraction) < _BISECTION_TOLERANCE:
            return mid
        if lf < target_fraction:
            low = mid
        else:
            high = mid
    raise ValueError(
        f"Bisection failed to converge on a floor level producing a "
        f"{target_load_factor_pct}% load factor within {_BISECTION_MAX_ITERATIONS} "
        f"iterations -- do not trust an unconverged result."
    )


@dataclass
class LoadProfile:
    """The one class tied to a specific data source (Rule 1) -- Dominion's
    DOMLSE hourly load projection export. year, raw_hourly (the real,
    unflattened shape), solved_floor_pct, and adjusted_hourly (the
    flattened result, with both mw and pct_of_peak columns) are all
    recorded explicitly and separately, so the flattening's effect is
    always inspectable against the real starting shape, not just the
    final number."""
    year: int
    target_load_factor_pct: float
    raw_hourly: pd.DataFrame  # columns: timestamp, mw
    solved_floor_pct: float
    adjusted_hourly: pd.DataFrame  # columns: timestamp, mw, pct_of_peak
    peak_mw: float

    @classmethod
    def from_domlse_export(cls, path: str, year: int,
                            target_load_factor_pct: float = DEFAULT_TARGET_LOAD_FACTOR_PCT) -> "LoadProfile":
        df = pd.read_csv(path)
        yr = df[df["Year"] == year]
        if len(yr) == 0:
            raise ValueError(f"No rows found for year {year} in {path}")

        records = []
        for _, row in yr.iterrows():
            base_date = pd.Timestamp(year=int(row["Year"]), month=int(row["Month"]), day=int(row["Day"]))
            for hour_label in _HOUR_COLS:
                # DOMLSE hour labels are 1-24 (hour 1 = 00:00-01:00); hour label h maps to
                # timestamp base_date + (h-1) hours, so label "1" -> 00:00, label "24" -> 23:00.
                records.append({
                    "timestamp": base_date + pd.Timedelta(hours=int(hour_label) - 1),
                    "mw": float(row[hour_label]),
                })
        raw_hourly = pd.DataFrame(records).sort_values("timestamp").reset_index(drop=True)

        peak_mw = raw_hourly["mw"].max()
        floor_pct = _solve_floor_pct_for_target_load_factor(raw_hourly["mw"], peak_mw, target_load_factor_pct)

        adjusted_hourly = raw_hourly.copy()
        adjusted_hourly["mw"] = adjusted_hourly["mw"].clip(lower=floor_pct * peak_mw)
        adjusted_hourly["pct_of_peak"] = adjusted_hourly["mw"] / peak_mw * 100

        achieved_load_factor_pct = adjusted_hourly["mw"].mean() / peak_mw * 100
        if abs(achieved_load_factor_pct - target_load_factor_pct) > 0.01:
            raise ValueError(
                f"Achieved load factor ({achieved_load_factor_pct:.2f}%) does not match target "
                f"({target_load_factor_pct}%) within tolerance -- do not trust this profile."
            )

        return cls(
            year=year, target_load_factor_pct=target_load_factor_pct, raw_hourly=raw_hourly,
            solved_floor_pct=floor_pct, adjusted_hourly=adjusted_hourly, peak_mw=peak_mw,
        )


@dataclass
class GapDurationPoint:
    pct_of_hours_at_or_below: float
    gap_pct_threshold: float


@dataclass
class LoadSolarGapAnalysis:
    """Combines a LoadProfile (a single representative year's flattened
    shape) with a ScaledSolarProfile (9 real weather years) by mapping the
    load shape's own (month, day, hour) onto each of the 9 solar years in
    turn, then computing gap_pct = load_pct_of_peak - solar_pct_of_fleet
    for every hour of the real 9-year solar record. Both load and solar
    are pure percentages of their own respective peaks/capacities -- no
    absolute Loudoun MW magnitude is assumed anywhere in this class, per
    direct user framing that this step is deliberately deferred."""
    load_profile: LoadProfile
    hourly: pd.DataFrame  # columns: timestamp, load_pct, solar_pct, gap_pct

    def __post_init__(self):
        self._verify_gap_within_physical_bounds()

    def _verify_gap_within_physical_bounds(self) -> None:
        """Physical invariant (Rule 9): gap_pct = load_pct - solar_pct can
        never exceed 100 percentage points (load_pct maxes at 100,
        solar_pct is never negative) or fall below -100 (solar_pct maxes
        at 100, load_pct is never negative). Checked automatically on
        construction, raising rather than warning."""
        max_gap = self.hourly["gap_pct"].max()
        min_gap = self.hourly["gap_pct"].min()
        if max_gap > 100 + _BISECTION_TOLERANCE or min_gap < -100 - _BISECTION_TOLERANCE:
            raise ValueError(
                f"gap_pct out of physically possible bounds: min={min_gap:.2f}, "
                f"max={max_gap:.2f} (must be within [-100, 100]) -- this result is not usable."
            )

    @classmethod
    def compute(cls, load_profile: LoadProfile, scaled_solar) -> "LoadSolarGapAnalysis":
        """scaled_solar is a loudoun_solar_hourly_profile.ScaledSolarProfile
        instance -- not type-hinted directly to avoid a hard import
        dependency in this module's own class definitions, but the
        classmethod is the only place that assumes its shape."""
        load_by_month_day_hour = load_profile.adjusted_hourly.copy()
        load_by_month_day_hour["month"] = load_by_month_day_hour["timestamp"].dt.month
        load_by_month_day_hour["day"] = load_by_month_day_hour["timestamp"].dt.day
        load_by_month_day_hour["hour"] = load_by_month_day_hour["timestamp"].dt.hour
        load_lookup = load_by_month_day_hour.set_index(["month", "day", "hour"])["pct_of_peak"]

        solar = scaled_solar.hourly.copy()
        solar["month"] = solar["timestamp"].dt.month
        solar["day"] = solar["timestamp"].dt.day
        solar["hour"] = solar["timestamp"].dt.hour
        solar["solar_pct"] = solar["mw"] / scaled_solar.fleet_mw * 100

        # The load profile's source year (2045, not a leap year) has no Feb 29 to begin with;
        # the solar data has Feb 29 already dropped (see loudoun_solar_hourly_profile.py). If a
        # future caller passes a leap-year load profile, any (month, day, hour) combination with
        # no match in load_lookup raises via .loc below rather than silently producing NaN --
        # consistent with this project's fail-loudly standard rather than guessing.
        matched_load_pct = load_lookup.loc[list(zip(solar["month"], solar["day"], solar["hour"]))].values

        result = pd.DataFrame({
            "timestamp": solar["timestamp"],
            "load_pct": matched_load_pct,
            "solar_pct": solar["solar_pct"].values,
        })
        result["gap_pct"] = result["load_pct"] - result["solar_pct"]
        return cls(load_profile=load_profile, hourly=result)

    def compute_gap_duration_curve(self, n_points: int = 101) -> List[GapDurationPoint]:
        """Standard duration-curve treatment, applied to gap_pct instead
        of raw MW: for each percentile of hours, the gap level at or
        below which that percentage of all hours falls."""
        sorted_gap = self.hourly["gap_pct"].sort_values().reset_index(drop=True)
        n = len(sorted_gap)
        points = []
        for i in range(n_points):
            pct = i / (n_points - 1) * 100
            idx = min(int(round(pct / 100 * (n - 1))), n - 1)
            points.append(GapDurationPoint(pct_of_hours_at_or_below=pct, gap_pct_threshold=sorted_gap.iloc[idx]))
        return points

    def find_longest_high_gap_streaks(self, gap_pct_threshold: float, top_n: int = 10) -> List[ValueStreak]:
        """Finds the longest consecutive runs of hours where the gap is at
        or above gap_pct_threshold -- i.e. where load is running well
        ahead of what local solar can cover, the hours that matter most
        for sizing how much transmission import (or battery discharge)
        capacity is needed. Delegates to the same shared streak-finder
        loudoun_solar_hourly_profile.py uses (Rule 1)."""
        return find_longest_threshold_streaks(
            self.hourly, value_col="gap_pct", threshold=gap_pct_threshold,
            top_n=top_n, condition="at_or_above",
        )
