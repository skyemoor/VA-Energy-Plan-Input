"""
test_loudoun_solar_hourly_profile.py

Tests loudoun_solar_hourly_profile.py's class-based interface: hand-verifiable unit tests on
small constructed data, integration tests against the real 9-year Sterling dataset, dedicated
tests for the gap-detection and leap-day fixes, and new tests for the Rule 9 physical-invariant
check added during the Software Engineering Standards refactor.
"""
import os
import tempfile
import unittest

import pandas as pd

from loudoun_solar_hourly_profile import (
    AVAILABLE_YEARS,
    OVERIRRADIANCE_TOLERANCE_PCT,
    STERLING_NAMEPLATE_KW,
    DurationCurvePoint,
    LowOutputStreak,
    ScaledSolarProfile,
    SolarSiteProfile,
    _aggregate_to_hourly,
    _load_one_sam_export_year,
)

PROJECT_DIR = "/mnt/project"


class TestLoadOneSamExportYear(unittest.TestCase):
    """Tests the private per-year loading helper directly -- its edge
    cases (wrong structure, wrong row count) are cleanest to test in
    isolation rather than only through the full multi-year pipeline."""

    def test_real_2012_file_loads_with_correct_year_and_row_count(self):
        df = _load_one_sam_export_year(f"{PROJECT_DIR}/SterlingSolar2012.csv", 2012)
        self.assertEqual(len(df), 17_520)
        self.assertEqual(df["timestamp"].iloc[0], pd.Timestamp("2012-01-01 00:00:00"))
        self.assertEqual(df["timestamp"].iloc[-1], pd.Timestamp("2012-12-31 23:30:00"))

    def test_different_year_argument_produces_different_timestamps(self):
        df_2012 = _load_one_sam_export_year(f"{PROJECT_DIR}/SterlingSolar2012.csv", 2012)
        df_2016 = _load_one_sam_export_year(f"{PROJECT_DIR}/SterlingSolar2012.csv", 2016)
        self.assertEqual(df_2012["timestamp"].iloc[0].year, 2012)
        self.assertEqual(df_2016["timestamp"].iloc[0].year, 2016)

    def test_wrong_column_structure_raises(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("Time stamp,Wrong Column Name\nJan 1, 12:00 am,0\n")
            path = f.name
        try:
            with self.assertRaises(ValueError):
                _load_one_sam_export_year(path, 2012)
        finally:
            os.remove(path)

    def test_wrong_row_count_raises(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write('"Time stamp","System power generated | (kW)"\n"Jan 1, 12:00 am",0\n')
            path = f.name
        try:
            with self.assertRaises(ValueError):
                _load_one_sam_export_year(path, 2012)
        finally:
            os.remove(path)


class TestAggregateToHourly(unittest.TestCase):

    def test_hand_verified_averaging(self):
        df = pd.DataFrame({
            "timestamp": pd.to_datetime([
                "2012-01-01 00:00", "2012-01-01 00:30",
                "2012-01-01 01:00", "2012-01-01 01:30",
            ]),
            "kw": [10.0, 20.0, 5.0, 15.0],
        })
        hourly = _aggregate_to_hourly(df)
        self.assertEqual(len(hourly), 2)
        self.assertAlmostEqual(hourly["kw"].iloc[0], 15.0, places=6)  # avg(10,20)
        self.assertAlmostEqual(hourly["kw"].iloc[1], 10.0, places=6)  # avg(5,15)

    def test_real_2012_hourly_energy_matches_raw_30min_sum(self):
        raw = _load_one_sam_export_year(f"{PROJECT_DIR}/SterlingSolar2012.csv", 2012)
        hourly = _aggregate_to_hourly(raw)
        raw_non_feb29 = raw[~((raw["timestamp"].dt.month == 2) & (raw["timestamp"].dt.day == 29))]
        raw_energy_mwh = (raw_non_feb29["kw"] * 0.5).sum() / 1_000
        hourly_energy_mwh = (hourly["kw"] * 1.0).sum() / 1_000
        self.assertAlmostEqual(raw_energy_mwh, hourly_energy_mwh, places=3)
        self.assertEqual(len(hourly), 365 * 24)

    def test_leap_day_hours_are_dropped_not_fabricated(self):
        raw = _load_one_sam_export_year(f"{PROJECT_DIR}/SterlingSolar2012.csv", 2012)
        hourly = _aggregate_to_hourly(raw)
        feb_29_rows = hourly[(hourly["timestamp"].dt.month == 2) & (hourly["timestamp"].dt.day == 29)]
        self.assertEqual(len(feb_29_rows), 0)
        self.assertFalse(hourly["kw"].isna().any())


class TestSolarSiteProfileFromSamExportYearlyFiles(unittest.TestCase):

    def test_real_all_9_years_load_and_concatenate_correctly(self):
        profile = SolarSiteProfile.from_sam_export_yearly_files(PROJECT_DIR, site_name="Sterling")
        self.assertEqual(len(profile.hourly), 78_840)  # (365*9) days * 24 hrs, leap days excluded
        self.assertEqual(profile.hourly["timestamp"].iloc[0], pd.Timestamp("2012-01-01 00:00:00"))
        self.assertEqual(profile.hourly["timestamp"].iloc[-1], pd.Timestamp("2020-12-31 23:00:00"))
        self.assertTrue(profile.hourly["timestamp"].is_monotonic_increasing)
        self.assertEqual(profile.nameplate_kw, STERLING_NAMEPLATE_KW)

    def test_available_years_constant_matches_actual_files_present(self):
        self.assertEqual(AVAILABLE_YEARS, [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020])
        for year in AVAILABLE_YEARS:
            self.assertTrue(os.path.exists(f"{PROJECT_DIR}/SterlingSolar{year}.csv"))

    def test_custom_filename_pattern_is_a_real_parameter_not_hardcoded(self):
        """Rule 8.1: filename_pattern must be a genuine, working override,
        not a parameter that's accepted but ignored."""
        with self.assertRaises(FileNotFoundError):
            SolarSiteProfile.from_sam_export_yearly_files(
                PROJECT_DIR, site_name="Sterling", years=[2012],
                filename_pattern="NonexistentPattern{year}.csv",
            )


class TestScaleToFleetMw(unittest.TestCase):

    def test_hand_verified_scaling(self):
        hourly = pd.DataFrame({
            "timestamp": pd.to_datetime(["2012-01-01 00:00", "2012-01-01 01:00"]),
            "kw": [50.0, 100.0],
        })
        profile = SolarSiteProfile(
            site_name="test", nameplate_kw=100, tilt_degrees=15, system_losses_pct=14,
            years=[2012], hourly=hourly,
        )
        scaled = profile.scale_to_fleet_mw(fleet_mw=1_000)
        self.assertAlmostEqual(scaled.hourly["mw"].iloc[0], 500.0, places=6)
        self.assertAlmostEqual(scaled.hourly["mw"].iloc[1], 1_000.0, places=6)

    def test_default_nameplate_matches_sterling_dataset(self):
        self.assertEqual(STERLING_NAMEPLATE_KW, 100)


class TestPhysicalInvariantOutputNeverExceedsFleetCapacity(unittest.TestCase):
    """New tests for the Rule 9 invariant check added during the Software
    Engineering Standards refactor."""

    def _make_profile(self, kw_values):
        hourly = pd.DataFrame({
            "timestamp": pd.date_range("2012-01-01", periods=len(kw_values), freq="h"),
            "kw": kw_values,
        })
        return SolarSiteProfile(
            site_name="test", nameplate_kw=100, tilt_degrees=15, system_losses_pct=14,
            years=[2012], hourly=hourly,
        )

    def test_normal_output_within_tolerance_does_not_raise(self):
        profile = self._make_profile([100.0])  # exactly at nameplate, well within tolerance
        scaled = profile.scale_to_fleet_mw(fleet_mw=1_000)  # should not raise
        self.assertAlmostEqual(scaled.hourly["mw"].iloc[0], 1_000.0, places=6)

    def test_output_within_stated_overirradiance_tolerance_does_not_raise(self):
        # 101.5 kW is within the 2% tolerance of 100 kW nameplate (max allowed 102 kW)
        profile = self._make_profile([101.5])
        scaled = profile.scale_to_fleet_mw(fleet_mw=1_000)  # should not raise
        self.assertGreater(scaled.hourly["mw"].iloc[0], 1_000.0)

    def test_output_exceeding_tolerance_raises(self):
        profile = self._make_profile([200.0])  # far beyond any plausible overirradiance tolerance
        with self.assertRaises(ValueError):
            profile.scale_to_fleet_mw(fleet_mw=1_000)

    def test_tolerance_constant_is_reasonable_and_documented(self):
        self.assertEqual(OVERIRRADIANCE_TOLERANCE_PCT, 2.0)

    def test_real_9_year_sterling_data_passes_the_invariant_check(self):
        """Confirms the real dataset, at real scaling factors, genuinely
        passes this check rather than the check being untested against
        real data."""
        profile = SolarSiteProfile.from_sam_export_yearly_files(PROJECT_DIR, site_name="Sterling")
        scaled = profile.scale_to_fleet_mw(fleet_mw=1_551.2)  # should not raise
        self.assertLessEqual(scaled.hourly["mw"].max(), 1_551.2 * 1.02)


class TestComputeDurationCurve(unittest.TestCase):

    def test_hand_verified_percentiles(self):
        hourly = pd.DataFrame({
            "timestamp": pd.date_range("2012-01-01", periods=11, freq="h"),
            "mw": [float(x) for x in range(11)],
        })
        scaled = ScaledSolarProfile(source_site_name="test", fleet_mw=10, nameplate_kw=100, hourly=hourly)
        curve = scaled.compute_duration_curve(n_points=11)
        self.assertAlmostEqual(curve[0].mw_threshold, 0.0, places=6)
        self.assertAlmostEqual(curve[-1].mw_threshold, 10.0, places=6)
        self.assertAlmostEqual(curve[5].mw_threshold, 5.0, places=6)


class TestComputeMonthHourHeatmap(unittest.TestCase):

    def test_hand_verified_single_cell_average(self):
        hourly = pd.DataFrame({
            "timestamp": pd.to_datetime([
                "2012-01-15 06:00", "2013-01-20 06:00", "2012-06-15 06:00",
            ]),
            "mw": [10.0, 20.0, 999.0],
        })
        scaled = ScaledSolarProfile(source_site_name="test", fleet_mw=1000, nameplate_kw=100, hourly=hourly)
        heatmap = scaled.compute_month_hour_heatmap()
        self.assertAlmostEqual(heatmap.loc[1, 6], 15.0, places=6)
        self.assertAlmostEqual(heatmap.loc[6, 6], 999.0, places=6)


class TestFindLongestLowOutputStreaks(unittest.TestCase):

    def _make_scaled(self, timestamps, mw_values):
        hourly = pd.DataFrame({"timestamp": pd.to_datetime(timestamps), "mw": mw_values})
        return ScaledSolarProfile(source_site_name="test", fleet_mw=max(mw_values) or 1, nameplate_kw=100, hourly=hourly)

    def test_hand_verified_streaks(self):
        timestamps = pd.date_range("2012-01-01 00:00", periods=8, freq="h")
        mw_values = [10, 1, 1, 1, 10, 1, 1, 10]
        scaled = self._make_scaled(timestamps, mw_values)
        streaks = scaled.find_longest_low_output_streaks(mw_threshold=5)
        self.assertEqual(len(streaks), 2)
        self.assertEqual(streaks[0].length_hours, 3)
        self.assertEqual(streaks[1].length_hours, 2)

    def test_streak_extending_to_final_row_is_found_correctly(self):
        timestamps = pd.date_range("2012-01-01 00:00", periods=3, freq="h")
        mw_values = [10, 1, 1]
        scaled = self._make_scaled(timestamps, mw_values)
        streaks = scaled.find_longest_low_output_streaks(mw_threshold=5)
        self.assertEqual(len(streaks), 1)
        self.assertEqual(streaks[0].length_hours, 2)

    def test_real_time_gap_breaks_a_streak_rather_than_bridging_it(self):
        timestamps = pd.to_datetime(["2012-01-01 00:00", "2012-01-01 03:00"])
        scaled = self._make_scaled(timestamps, [1, 1])
        streaks = scaled.find_longest_low_output_streaks(mw_threshold=5)
        self.assertEqual(len(streaks), 2, "a time gap must produce two streaks, not one bridged streak")
        self.assertEqual(streaks[0].length_hours, 1)
        self.assertEqual(streaks[1].length_hours, 1)

    def test_real_9_year_dataset_has_no_unexpected_gaps(self):
        profile = SolarSiteProfile.from_sam_export_yearly_files(PROJECT_DIR, site_name="Sterling")
        scaled = profile.scale_to_fleet_mw(fleet_mw=100)  # 1:1, just to reuse the pipeline
        gaps = scaled.hourly["timestamp"].diff()
        non_hour_gaps = gaps[(gaps.notna()) & (gaps != pd.Timedelta(hours=1))]
        self.assertEqual(len(non_hour_gaps), 3, "exactly the 3 leap-day gaps, no others")
        for gap in non_hour_gaps:
            self.assertEqual(gap, pd.Timedelta(hours=25))

    def test_real_leap_day_gap_correctly_breaks_a_streak(self):
        profile = SolarSiteProfile.from_sam_export_yearly_files(
            PROJECT_DIR, site_name="Sterling", years=[2012],
        )
        scaled = profile.scale_to_fleet_mw(fleet_mw=100)
        streaks = scaled.find_longest_low_output_streaks(mw_threshold=1_000_000, top_n=1)
        self.assertLess(streaks[0].length_hours, 365 * 24, "the leap-day gap must break the streak")


if __name__ == "__main__":
    unittest.main(verbosity=2)
