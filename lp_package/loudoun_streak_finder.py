"""
loudoun_streak_finder.py

Shared, reusable "find longest consecutive runs of hours meeting a condition, respecting real
time gaps" logic -- extracted from loudoun_solar_hourly_profile.py's
ScaledSolarProfile.find_longest_low_output_streaks, per Software Engineering Standards Rule 1
("if every scenario needs it and the underlying formula is the same... it belongs in a shared
method, not reimplemented per scenario"). The algorithm is genuinely identical whether applied to
raw solar MW output or to a computed load-vs-solar gap value -- only the column being thresholded
differs -- so this extraction lets both loudoun_solar_hourly_profile.py and
loudoun_load_shape_gap_analysis.py call the same, already-tested code rather than maintaining two
copies of the same logic.
"""
from dataclasses import dataclass

import pandas as pd


@dataclass
class ValueStreak:
    """Generic result type -- 'value' rather than 'mw' or 'gap' in the
    field name, since this same structure now serves both the solar
    module's MW streaks and the gap-analysis module's gap streaks."""
    start: pd.Timestamp
    end: pd.Timestamp
    length_hours: int
    threshold_used: float


def find_longest_threshold_streaks(hourly_df: pd.DataFrame, value_col: str,
                                    threshold: float, top_n: int = 10,
                                    condition: str = "at_or_below") -> list:
    """Finds the longest consecutive runs of hours where hourly_df[value_col]
    meets threshold, per the given condition ('at_or_below' or
    'at_or_above' -- generalized from the solar module's original
    at-or-below-only logic, since gap analysis needs 'gap at or ABOVE some
    severity' rather than 'output at or below some level').

    Explicitly verifies each row is exactly 1 hour after the previous one
    (not just adjacent by row position) before treating them as part of
    the same streak -- a real correctness concern given multi-year hourly
    data is typically built by concatenating separately-loaded yearly
    files, where a missing hour or a leap-day gap should correctly break a
    streak rather than being silently bridged by two rows that merely sit
    next to each other in the dataframe. See Data_Sourcing_Log.md,
    "Hourly solar profile built from real 9-year Sterling SAM data" entry,
    bug #1, for the original case this fixed.
    """
    if condition not in ("at_or_below", "at_or_above"):
        raise ValueError(f"condition must be 'at_or_below' or 'at_or_above', got {condition!r}")

    df = hourly_df.sort_values("timestamp").reset_index(drop=True)
    if condition == "at_or_below":
        meets_condition = df[value_col] <= threshold
    else:
        meets_condition = df[value_col] >= threshold
    time_gap_from_prev = df["timestamp"].diff()

    streaks = []
    start_idx = None
    for i in range(len(df)):
        has_gap_here = i > 0 and time_gap_from_prev.iloc[i] != pd.Timedelta(hours=1)
        if has_gap_here and start_idx is not None:
            streaks.append((start_idx, i - 1))
            start_idx = None

        if meets_condition.iloc[i] and start_idx is None:
            start_idx = i

        is_last = i == len(df) - 1
        breaks_here = not meets_condition.iloc[i] or is_last
        if start_idx is not None and breaks_here:
            end_idx = i if not meets_condition.iloc[i] else i
            end_idx = end_idx - 1 if not meets_condition.iloc[i] else end_idx
            streaks.append((start_idx, end_idx))
            start_idx = None

    results = []
    for s, e in streaks:
        results.append(ValueStreak(
            start=df["timestamp"].iloc[s], end=df["timestamp"].iloc[e],
            length_hours=e - s + 1, threshold_used=threshold,
        ))
    results.sort(key=lambda r: -r.length_hours)
    return results[:top_n]
