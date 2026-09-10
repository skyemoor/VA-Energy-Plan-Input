"""
test_loudoun_streak_finder.py

Tests loudoun_streak_finder.py directly -- the shared logic extracted from
loudoun_solar_hourly_profile.py, now covering both the original at_or_below condition (re-run
here to confirm the extraction preserved behavior exactly) and the new at_or_above condition
needed for gap-severity analysis.
"""
import unittest

import pandas as pd

from loudoun_streak_finder import find_longest_threshold_streaks


class TestFindLongestThresholdStreaksAtOrBelow(unittest.TestCase):
    """Re-verifies the original at_or_below behavior, preserved exactly
    from the pre-extraction implementation in loudoun_solar_hourly_profile.py."""

    def _make_df(self, timestamps, values, col="mw"):
        return pd.DataFrame({"timestamp": pd.to_datetime(timestamps), col: values})

    def test_hand_verified_streaks(self):
        timestamps = pd.date_range("2012-01-01 00:00", periods=8, freq="h")
        values = [10, 1, 1, 1, 10, 1, 1, 10]
        df = self._make_df(timestamps, values)
        streaks = find_longest_threshold_streaks(df, "mw", threshold=5, condition="at_or_below")
        self.assertEqual(len(streaks), 2)
        self.assertEqual(streaks[0].length_hours, 3)
        self.assertEqual(streaks[1].length_hours, 2)

    def test_streak_extending_to_final_row_is_found_correctly(self):
        timestamps = pd.date_range("2012-01-01 00:00", periods=3, freq="h")
        values = [10, 1, 1]
        df = self._make_df(timestamps, values)
        streaks = find_longest_threshold_streaks(df, "mw", threshold=5, condition="at_or_below")
        self.assertEqual(len(streaks), 1)
        self.assertEqual(streaks[0].length_hours, 2)

    def test_real_time_gap_breaks_a_streak_rather_than_bridging_it(self):
        timestamps = pd.to_datetime(["2012-01-01 00:00", "2012-01-01 03:00"])
        df = self._make_df(timestamps, [1, 1])
        streaks = find_longest_threshold_streaks(df, "mw", threshold=5, condition="at_or_below")
        self.assertEqual(len(streaks), 2, "a time gap must produce two streaks, not one bridged streak")


class TestFindLongestThresholdStreaksAtOrAbove(unittest.TestCase):
    """New coverage for the generalized at_or_above condition, needed for
    gap-severity analysis (looking for hours where the load-vs-solar gap
    is large, not small)."""

    def _make_df(self, timestamps, values, col="gap_pct"):
        return pd.DataFrame({"timestamp": pd.to_datetime(timestamps), col: values})

    def test_hand_verified_streaks_above_threshold(self):
        timestamps = pd.date_range("2012-01-01 00:00", periods=6, freq="h")
        values = [10, 80, 90, 85, 20, 95]  # threshold=70 -> indices 1,2,3 form a streak; index 5 alone
        df = self._make_df(timestamps, values)
        streaks = find_longest_threshold_streaks(df, "gap_pct", threshold=70, condition="at_or_above")
        self.assertEqual(len(streaks), 2)
        self.assertEqual(streaks[0].length_hours, 3)
        self.assertEqual(streaks[1].length_hours, 1)

    def test_invalid_condition_raises(self):
        df = self._make_df(pd.date_range("2012-01-01", periods=2, freq="h"), [1, 2])
        with self.assertRaises(ValueError):
            find_longest_threshold_streaks(df, "gap_pct", threshold=1, condition="sideways")


if __name__ == "__main__":
    unittest.main(verbosity=2)
