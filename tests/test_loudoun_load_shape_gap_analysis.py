"""
test_loudoun_load_shape_gap_analysis.py

Tests loudoun_load_shape_gap_analysis.py: hand-verifiable unit tests on small constructed data,
and integration tests against the real 2045 DOMLSE load projection combined with the real 9-year
Sterling solar profile.
"""
import unittest

import pandas as pd

from loudoun_load_shape_gap_analysis import (
    DEFAULT_TARGET_LOAD_FACTOR_PCT,
    LoadProfile,
    LoadSolarGapAnalysis,
    _solve_floor_pct_for_target_load_factor,
)
from loudoun_solar_hourly_profile import ScaledSolarProfile, SolarSiteProfile

PROJECT_DIR = "/mnt/project"
DOMLSE_PATH = f"{PROJECT_DIR}/DOMLSEHourlyLoadProjections2024through2048.csv"


class TestSolveFloorPctForTargetLoadFactor(unittest.TestCase):

    def test_hand_verified_solve(self):
        # peak=100, natural avg=(10+20+100)/3=43.33, natural LF=43.33%
        series = pd.Series([10.0, 20.0, 100.0])
        floor = _solve_floor_pct_for_target_load_factor(series, peak_mw=100.0, target_load_factor_pct=60.0)
        adjusted = series.clip(lower=floor * 100.0)
        achieved_lf = adjusted.mean() / 100.0 * 100
        self.assertAlmostEqual(achieved_lf, 60.0, places=3)

    def test_only_low_hours_are_touched(self):
        series = pd.Series([10.0, 20.0, 100.0])
        floor = _solve_floor_pct_for_target_load_factor(series, peak_mw=100.0, target_load_factor_pct=60.0)
        adjusted = series.clip(lower=floor * 100.0)
        # The hour already at peak (100) must be completely untouched
        self.assertEqual(adjusted.iloc[2], 100.0)

    def test_raises_if_natural_load_factor_already_meets_target(self):
        series = pd.Series([90.0, 95.0, 100.0])  # natural LF = 95%
        with self.assertRaises(ValueError):
            _solve_floor_pct_for_target_load_factor(series, peak_mw=100.0, target_load_factor_pct=90.0)

    def test_real_2045_data_solves_to_exactly_90_percent(self):
        profile = LoadProfile.from_domlse_export(DOMLSE_PATH, year=2045, target_load_factor_pct=90.0)
        achieved = profile.adjusted_hourly["mw"].mean() / profile.peak_mw * 100
        self.assertAlmostEqual(achieved, 90.0, places=2)


class TestLoadProfileFromDomlseExport(unittest.TestCase):

    def test_real_2045_loads_with_correct_row_count_and_peak(self):
        profile = LoadProfile.from_domlse_export(DOMLSE_PATH, year=2045)
        self.assertEqual(len(profile.raw_hourly), 365 * 24)  # 2045 is not a leap year
        self.assertEqual(len(profile.adjusted_hourly), 365 * 24)
        # Peak must be unchanged by the flattening -- only low hours move
        self.assertAlmostEqual(profile.adjusted_hourly["mw"].max(), profile.peak_mw, places=3)
        self.assertAlmostEqual(profile.raw_hourly["mw"].max(), profile.peak_mw, places=3)

    def test_hours_already_above_floor_are_left_untouched(self):
        """Direct test of 'only the lower times are adjusted': any raw
        hour already at or above the solved floor must be bit-for-bit
        identical in the adjusted series."""
        profile = LoadProfile.from_domlse_export(DOMLSE_PATH, year=2045)
        floor_mw = profile.solved_floor_pct * profile.peak_mw
        already_high = profile.raw_hourly["mw"] >= floor_mw
        pd.testing.assert_series_equal(
            profile.raw_hourly.loc[already_high, "mw"].reset_index(drop=True),
            profile.adjusted_hourly.loc[already_high, "mw"].reset_index(drop=True),
        )

    def test_hour_label_mapping_matches_expected_peak_timing(self):
        """Cross-checks the hour-label-to-timestamp mapping against a
        known-sensible real-world pattern: a summer day's peak load
        should fall in late afternoon, not some other, implausible hour."""
        profile = LoadProfile.from_domlse_export(DOMLSE_PATH, year=2045)
        july = profile.raw_hourly[profile.raw_hourly["timestamp"].dt.month == 7]
        peak_row = july.loc[july["mw"].idxmax()]
        self.assertIn(peak_row["timestamp"].hour, range(14, 19), "summer peak should fall in mid-late afternoon")

    def test_nonexistent_year_raises(self):
        with self.assertRaises(ValueError):
            LoadProfile.from_domlse_export(DOMLSE_PATH, year=1999)

    def test_default_target_matches_established_user_decision(self):
        self.assertEqual(DEFAULT_TARGET_LOAD_FACTOR_PCT, 90.0)


class TestLoadSolarGapAnalysis(unittest.TestCase):

    def _make_synthetic_load_profile(self):
        # A tiny, fully hand-verifiable 2-hour "profile": hour 0 load_pct=90, hour 1 load_pct=100
        timestamps = pd.to_datetime(["2045-01-01 00:00", "2045-01-01 01:00"])
        raw = pd.DataFrame({"timestamp": timestamps, "mw": [90.0, 100.0]})
        adjusted = raw.copy()
        adjusted["pct_of_peak"] = adjusted["mw"] / 100.0 * 100
        return LoadProfile(
            year=2045, target_load_factor_pct=90.0, raw_hourly=raw,
            solved_floor_pct=0.9, adjusted_hourly=adjusted, peak_mw=100.0,
        )

    def _make_synthetic_scaled_solar(self):
        # Same 2 hours: hour 0 solar=10% of fleet, hour 1 solar=80% of fleet
        timestamps = pd.to_datetime(["2045-01-01 00:00", "2045-01-01 01:00"])
        hourly = pd.DataFrame({"timestamp": timestamps, "mw": [10.0, 80.0]})
        return ScaledSolarProfile(source_site_name="test", fleet_mw=100.0, nameplate_kw=100, hourly=hourly)

    def test_hand_verified_gap_computation(self):
        load_profile = self._make_synthetic_load_profile()
        scaled_solar = self._make_synthetic_scaled_solar()
        analysis = LoadSolarGapAnalysis.compute(load_profile, scaled_solar)
        # Hour 0: load=90%, solar=10% -> gap=80
        self.assertAlmostEqual(analysis.hourly["gap_pct"].iloc[0], 80.0, places=6)
        # Hour 1: load=100%, solar=80% -> gap=20
        self.assertAlmostEqual(analysis.hourly["gap_pct"].iloc[1], 20.0, places=6)

    def test_find_longest_high_gap_streaks_hand_verified(self):
        timestamps = pd.date_range("2045-01-01 00:00", periods=4, freq="h")
        raw = pd.DataFrame({"timestamp": timestamps, "mw": [90.0] * 4})
        adjusted = raw.copy()
        adjusted["pct_of_peak"] = 90.0
        load_profile = LoadProfile(
            year=2045, target_load_factor_pct=90.0, raw_hourly=raw,
            solved_floor_pct=0.9, adjusted_hourly=adjusted, peak_mw=100.0,
        )
        # solar: 0%, 0%, 50%, 0% of fleet -> gaps: 90, 90, 40, 90
        hourly_solar = pd.DataFrame({"timestamp": timestamps, "mw": [0.0, 0.0, 50.0, 0.0]})
        scaled_solar = ScaledSolarProfile(source_site_name="test", fleet_mw=100.0, nameplate_kw=100, hourly=hourly_solar)
        analysis = LoadSolarGapAnalysis.compute(load_profile, scaled_solar)
        streaks = analysis.find_longest_high_gap_streaks(gap_pct_threshold=80.0)
        self.assertEqual(len(streaks), 2)  # hours 0-1 (streak of 2), hour 3 (streak of 1)
        self.assertEqual(streaks[0].length_hours, 2)
        self.assertEqual(streaks[1].length_hours, 1)

    def test_real_9_year_integration_gap_within_physical_bounds(self):
        """Full integration test against real data: real 2045 load
        profile x real 9-year Sterling solar, scaled to our established
        canopy MW range. Confirms it runs end to end and the Rule 9
        invariant holds on real data, not just synthetic examples."""
        load_profile = LoadProfile.from_domlse_export(DOMLSE_PATH, year=2045)
        solar_profile = SolarSiteProfile.from_sam_export_yearly_files(PROJECT_DIR, site_name="Sterling")
        scaled_solar = solar_profile.scale_to_fleet_mw(fleet_mw=1_551.2)
        analysis = LoadSolarGapAnalysis.compute(load_profile, scaled_solar)

        self.assertEqual(len(analysis.hourly), len(scaled_solar.hourly))
        self.assertLessEqual(analysis.hourly["gap_pct"].max(), 100.0001)
        self.assertGreaterEqual(analysis.hourly["gap_pct"].min(), -100.0001)

        # At night, solar_pct is 0 and load_pct is at least the solved floor (~<90 but > natural
        # min) -- so nighttime gap should be strictly positive and among the largest gaps.
        night_hours = analysis.hourly[analysis.hourly["timestamp"].dt.hour.isin([2, 3])]
        self.assertTrue((night_hours["gap_pct"] > 0).all())

    def test_gap_pct_is_invariant_to_fleet_mw_choice(self):
        """Locks in a real, important, non-obvious property: since both
        load_pct and solar_pct are expressed as a % of their own
        respective peaks/capacity (per direct user framing deferring
        absolute Loudoun MW to a later step), the resulting gap_pct is
        mathematically IDENTICAL regardless of which fleet_mw the solar
        profile is scaled to. This was directly observed when running the
        real analysis at both established canopy MW scenarios (1,551.2
        and 1,939.0 MW) and getting byte-for-byte identical duration
        curves and streaks -- confirmed here as an intentional, tested
        property of the analysis design, not a bug to fix."""
        load_profile = LoadProfile.from_domlse_export(DOMLSE_PATH, year=2045, target_load_factor_pct=90.0)
        solar_profile = SolarSiteProfile.from_sam_export_yearly_files(PROJECT_DIR, site_name="Sterling", years=[2012])

        analysis_small = LoadSolarGapAnalysis.compute(load_profile, solar_profile.scale_to_fleet_mw(fleet_mw=10.0))
        analysis_large = LoadSolarGapAnalysis.compute(load_profile, solar_profile.scale_to_fleet_mw(fleet_mw=10_000.0))

        pd.testing.assert_series_equal(
            analysis_small.hourly["gap_pct"].reset_index(drop=True),
            analysis_large.hourly["gap_pct"].reset_index(drop=True),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
