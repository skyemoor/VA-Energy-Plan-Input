import unittest

import pandas as pd

from loudoun_solar_firming import (
    DEFAULT_FIRMING_STARTING_SOC_PCT,
    LONG_DURATION_HOURS,
    LONG_DURATION_RTE_PCT,
    LOOKAHEAD_HOURS,
    SHORT_DURATION_HOURS,
    SHORT_DURATION_RTE_PCT,
    BlendedSplitResult,
    _can_hold_flat_level_without_shortfall,
    compute_chained_daily_firm_levels,
    find_optimal_blended_split,
    solve_max_flat_level_for_window,
)
from loudoun_solar_hourly_profile import SolarSiteProfile

PROJECT_DIR = "/mnt/project"


class TestCanHoldFlatLevelWithoutShortfall(unittest.TestCase):

    def test_solar_always_exceeds_flat_level_is_feasible_even_with_zero_soc(self):
        # solar=10 every hour, flat_level=5 -> solar alone always covers it, battery never needed
        result = _can_hold_flat_level_without_shortfall(
            solar_values=[10.0, 10.0, 10.0], starting_soc=0.0, energy_capacity=100.0,
            power_mw=50.0, rte_fraction=0.9, flat_level_mw=5.0,
        )
        self.assertTrue(result)

    def test_zero_solar_zero_soc_nonzero_flat_level_is_infeasible(self):
        result = _can_hold_flat_level_without_shortfall(
            solar_values=[0.0], starting_soc=0.0, energy_capacity=100.0,
            power_mw=50.0, rte_fraction=0.9, flat_level_mw=5.0,
        )
        self.assertFalse(result)

    def test_exactly_sufficient_soc_is_feasible(self):
        # flat_level=5 for 2 hours, zero solar -> needs exactly 10 MWh of discharge
        result = _can_hold_flat_level_without_shortfall(
            solar_values=[0.0, 0.0], starting_soc=10.0, energy_capacity=10.0,
            power_mw=50.0, rte_fraction=1.0, flat_level_mw=5.0,
        )
        self.assertTrue(result)

    def test_one_short_hour_below_soc_is_infeasible(self):
        # Same as above but SoC is 0.01 MWh short of what's needed
        result = _can_hold_flat_level_without_shortfall(
            solar_values=[0.0, 0.0], starting_soc=9.99, energy_capacity=10.0,
            power_mw=50.0, rte_fraction=1.0, flat_level_mw=5.0,
        )
        self.assertFalse(result)

    def test_mixed_excess_and_deficit_hours_hand_verified(self):
        # Hour 1: solar=20, flat=5 -> excess=15 charges battery (100% RTE) -> soc: 0 -> 15
        # Hour 2: solar=0, flat=5 -> deficit=5, soc=15 covers it easily -> soc: 15 -> 10
        result = _can_hold_flat_level_without_shortfall(
            solar_values=[20.0, 0.0], starting_soc=0.0, energy_capacity=100.0,
            power_mw=50.0, rte_fraction=1.0, flat_level_mw=5.0,
        )
        self.assertTrue(result)

    def test_does_not_mutate_starting_soc_across_repeated_calls(self):
        """Direct confirmation this is a pure 'what-if' check -- calling
        it twice with the same starting_soc must give the same answer
        both times, not a stateful/degrading one."""
        args = dict(solar_values=[0.0, 0.0], starting_soc=10.0, energy_capacity=10.0,
                    power_mw=50.0, rte_fraction=1.0, flat_level_mw=5.0)
        first = _can_hold_flat_level_without_shortfall(**args)
        second = _can_hold_flat_level_without_shortfall(**args)
        self.assertEqual(first, second)
        self.assertTrue(first)


class TestSolveMaxFlatLevelForWindow(unittest.TestCase):

    def test_hand_computed_case_bounded_by_soc(self):
        # 2 hours, zero solar, power_mw high enough not to bind -> max flat level = starting_soc / 2
        result = solve_max_flat_level_for_window(
            solar_values=[0.0, 0.0], starting_soc=20.0, energy_capacity=20.0,
            power_mw=999.0, rte_fraction=1.0,
        )
        self.assertAlmostEqual(result, 10.0, delta=0.02)  # 20 MWh / 2 hours = 10 MW

    def test_bounded_by_power_mw_not_solar_or_soc(self):
        # Solar and SoC are both generous; power_mw=5 should be the binding constraint
        result = solve_max_flat_level_for_window(
            solar_values=[100.0, 100.0, 100.0], starting_soc=1000.0, energy_capacity=1000.0,
            power_mw=5.0, rte_fraction=1.0,
        )
        self.assertAlmostEqual(result, 5.0, delta=0.02)

    def test_zero_solar_zero_soc_gives_zero(self):
        result = solve_max_flat_level_for_window(
            solar_values=[0.0, 0.0, 0.0], starting_soc=0.0, energy_capacity=100.0,
            power_mw=50.0, rte_fraction=0.9,
        )
        self.assertAlmostEqual(result, 0.0, delta=0.02)

    def test_zero_power_mw_returns_zero_without_raising(self):
        result = solve_max_flat_level_for_window(
            solar_values=[10.0, 10.0], starting_soc=5.0, energy_capacity=5.0,
            power_mw=0.0, rte_fraction=0.9,
        )
        self.assertEqual(result, 0.0)

    def test_result_is_actually_feasible_when_checked_directly(self):
        """Cross-check (Rule 4): the solved value, fed back into the
        feasibility checker directly, must itself return True -- not
        just trust the bisection's own internal bookkeeping."""
        solar_values = [3.0, 1.0, 8.0, 0.0, 12.0]
        result = solve_max_flat_level_for_window(
            solar_values=solar_values, starting_soc=15.0, energy_capacity=40.0,
            power_mw=20.0, rte_fraction=0.85,
        )
        self.assertTrue(_can_hold_flat_level_without_shortfall(
            solar_values, starting_soc=15.0, energy_capacity=40.0,
            power_mw=20.0, rte_fraction=0.85, flat_level_mw=result,
        ))

    def test_result_plus_small_increment_is_infeasible(self):
        """Cross-check the OTHER direction: a level just above the solved
        maximum should fail -- confirming the bisection actually found the
        boundary, not just some conservative, much-too-low feasible value."""
        solar_values = [3.0, 1.0, 8.0, 0.0, 12.0]
        result = solve_max_flat_level_for_window(
            solar_values=solar_values, starting_soc=15.0, energy_capacity=40.0,
            power_mw=20.0, rte_fraction=0.85, tolerance_mw=0.01,
        )
        self.assertFalse(_can_hold_flat_level_without_shortfall(
            solar_values, starting_soc=15.0, energy_capacity=40.0,
            power_mw=20.0, rte_fraction=0.85, flat_level_mw=result + 0.5,
        ))


class TestComputeChainedDailyFirmLevels(unittest.TestCase):

    def _make_hourly_solar_df(self, solar_values: list, start: str = "2018-01-01 00:00"):
        timestamps = pd.date_range(start=start, periods=len(solar_values), freq="h")
        return pd.DataFrame({"timestamp": timestamps, "mw": solar_values})

    def test_constant_solar_zero_starting_soc_gives_flat_level_equal_to_solar_every_day(self):
        """Simplest possible case: no initial buffer, no future variation
        -- the sustainable flat level should be exactly the constant
        solar value, every single day."""
        solar = [10.0] * (24 * 4)  # 4 days, constant 10 MW
        df = self._make_hourly_solar_df(solar)
        result = compute_chained_daily_firm_levels(
            solar_hourly=df, power_mw=100.0, duration_hours=1.0, rte_pct=100.0,
            starting_soc_pct=0.0,
        )
        self.assertEqual(len(result), 2)  # positions 0 and 24 both have a full 72-hr lookahead in 96 hours
        self.assertAlmostEqual(result.iloc[0], 10.0, delta=0.02)

    def test_storm_coming_pulls_down_earlier_days_firm_level(self):
        """Direct confirmation of the central behavior this module
        exists to capture: a known future zero-solar day pulls the
        commitment level down on EARLIER, good-solar days too -- matching
        the uploaded document's described 'weather uncertainty
        buffering.' Hand-verified precisely before writing this test (see
        chat trace): 5 days, solar=20 for days 1-2, solar=0 for day 3 (the
        storm), solar=20 for days 4-5; power_mw=100 (not binding),
        duration_hours=0.24 -> energy_capacity=24 MWh, starting_soc=100%
        (full), RTE=100%. Every one of days 1-3 has the storm somewhere in
        its own 72-hr lookahead, and since the battery starts full and
        never discharges before the storm (solar always covers the low
        committed level with curtailed excess), the achievable flat level
        is identical and exact on all three: 24 zero-solar hours can only
        sustain 24 MWh / 24 hours = 1.0 MW flat, even though solar itself
        is 20 MW on days 1-2. Days 4-5 lack a full 72-hr lookahead in this
        120-hour record and are correctly skipped."""
        solar = [20.0] * 48 + [0.0] * 24 + [20.0] * 48  # days 1-2 good, day 3 storm, days 4-5 good
        df = self._make_hourly_solar_df(solar)
        result = compute_chained_daily_firm_levels(
            solar_hourly=df, power_mw=100.0, duration_hours=0.24, rte_pct=100.0,
            starting_soc_pct=100.0,
        )
        self.assertEqual(len(result), 3)  # only days 1-3 have a full 72-hr lookahead in 120 hours
        for day_firm_level in result:
            self.assertAlmostEqual(day_firm_level, 1.0, delta=0.02)

    def test_soc_chains_across_days_not_reset(self):
        """A day that draws SoC down should leave a LOWER starting SoC for
        the next day -- not silently reset to some standardized value.
        Confirmed by checking firm levels are non-increasing across a
        stretch of zero-solar days that follow one good day, since each
        day's own achievable level depends on the real, chained-down SoC
        left over from the day before."""
        solar = [50.0] * 24 + [0.0] * 96  # 1 great day, then 4 straight zero-solar days
        df = self._make_hourly_solar_df(solar)
        result = compute_chained_daily_firm_levels(
            solar_hourly=df, power_mw=100.0, duration_hours=0.5, rte_pct=100.0,
            starting_soc_pct=50.0,
        )
        self.assertGreaterEqual(len(result), 2)
        for i in range(1, len(result)):
            self.assertLessEqual(result.iloc[i], result.iloc[i - 1] + 1e-6)

    def test_days_without_full_lookahead_are_excluded_not_truncated(self):
        """A record with fewer than lookahead_hours total should produce
        zero daily results, not a truncated/partial-lookahead answer."""
        solar = [10.0] * 48  # only 48 hours total, less than the 72-hr lookahead requirement
        df = self._make_hourly_solar_df(solar)
        result = compute_chained_daily_firm_levels(
            solar_hourly=df, power_mw=100.0, duration_hours=1.0, rte_pct=100.0,
        )
        self.assertEqual(len(result), 0)

    def test_gap_in_data_correctly_excludes_days_whose_lookahead_would_cross_it(self):
        """Strengthened this round after a real bug was found: the
        original version of this test only checked len(result) > 0 and
        that qualifying days had the right value -- it never checked HOW
        MANY days qualified or whether days AFTER the gap were included
        at all, so it did not catch a real bug where the main loop used
        `break` instead of `continue`/skip when a day's lookahead window
        hit a gap, silently discarding every day after the FIRST gap
        anywhere in the record (on the real 9-year Sterling data, this
        reduced ~3,285 possible days to just 57, since the first Feb-29
        gap in 2012 halted processing before 2013-2020 were ever reached
        at all). This version explicitly builds days on BOTH sides of a
        gap and asserts days from the far side are present, which is
        exactly the assertion the original test was missing."""
        # 10 days before the gap, a real gap, then 10 more days after it
        df1 = self._make_hourly_solar_df([10.0] * 24 * 10, start="2018-01-01 00:00")
        df2 = self._make_hourly_solar_df([10.0] * 24 * 10, start="2018-01-15 09:00")  # a real 5-hr gap
        df = pd.concat([df1, df2], ignore_index=True)
        result = compute_chained_daily_firm_levels(
            solar_hourly=df, power_mw=100.0, duration_hours=1.0, rte_pct=100.0, starting_soc_pct=0.0,
        )
        for day_firm_level in result:
            self.assertAlmostEqual(day_firm_level, 10.0, delta=0.02)

        result_dates = set(result.index)
        # Days far enough before the gap that their 72-hr lookahead never crosses it
        self.assertIn(pd.Timestamp("2018-01-01").date(), result_dates)
        self.assertIn(pd.Timestamp("2018-01-02").date(), result_dates)
        # THE key assertion the original, too-weak test was missing: days from the far side of
        # the gap must also be present -- this fails if the loop incorrectly halts at the first gap.
        self.assertIn(pd.Timestamp("2018-01-16").date(), result_dates)
        self.assertIn(pd.Timestamp("2018-01-20").date(), result_dates)

    def test_real_data_small_slice_and_runtime_check(self):
        """Real-data check on a small slice (~30 days) of the real
        Sterling 2018 record, both to confirm this runs correctly end to
        end on genuine data and to measure real per-day runtime before
        committing to the full 9-year run."""
        import time
        solar_profile = SolarSiteProfile.from_sam_export_yearly_files(
            PROJECT_DIR, site_name="Sterling", years=[2018],
        )
        scaled = solar_profile.scale_to_fleet_mw(fleet_mw=2_908.4)
        small_slice = scaled.hourly[scaled.hourly["timestamp"] < pd.Timestamp("2018-02-01")].reset_index(drop=True)

        t0 = time.time()
        result = compute_chained_daily_firm_levels(
            solar_hourly=small_slice, power_mw=2_908.4, duration_hours=100.0, rte_pct=80.0,
        )
        elapsed = time.time() - t0
        print(f"\n[runtime check] {len(result)} days in {elapsed:.3f}s "
              f"({elapsed / max(len(result), 1) * 1000:.1f} ms/day)")

        self.assertGreater(len(result), 0)
        self.assertTrue((result >= 0).all())
        self.assertTrue((result <= 2_908.4 + 1e-6).all())


class TestFindOptimalBlendedSplit(unittest.TestCase):

    def _make_solar_profile(self, solar_values: list, nameplate_kw: float = 200.0):
        timestamps = pd.date_range(start="2018-01-01 00:00", periods=len(solar_values), freq="h")
        hourly = pd.DataFrame({"timestamp": timestamps, "kw": solar_values})
        return SolarSiteProfile(
            site_name="test", nameplate_kw=nameplate_kw, tilt_degrees=15, system_losses_pct=14,
            years=[2018], hourly=hourly,
        )

    def test_split_zero_pct_matches_pure_long_duration_run_exactly(self):
        """Cross-check (Rule 4): split=0% (all long-duration) must
        reproduce EXACTLY the same daily series as calling
        compute_chained_daily_firm_levels directly with only the
        long-duration design -- confirms the grid-search wrapper isn't
        silently altering the underlying per-day solve."""
        solar_kw = [200.0] * 24 * 10  # 10 days, ample solar
        profile = self._make_solar_profile(solar_kw)
        total_mw = 50.0

        grid = find_optimal_blended_split(profile, total_mw=total_mw, split_step_pct=100.0)
        zero_pct_result = next(r for r in grid["all_results"] if abs(r.split_fraction_short - 0.0) < 1e-9)

        direct_long_solar = profile.scale_to_fleet_mw(total_mw)
        direct_daily = compute_chained_daily_firm_levels(
            solar_hourly=direct_long_solar.hourly, power_mw=total_mw, duration_hours=LONG_DURATION_HOURS,
            rte_pct=LONG_DURATION_RTE_PCT,
        )
        pd.testing.assert_series_equal(
            zero_pct_result.daily_combined_firm_levels.sort_index(), direct_daily.sort_index(),
            check_names=False,
        )

    def test_split_100_pct_matches_pure_short_duration_run_exactly(self):
        solar_kw = [200.0] * 24 * 10
        profile = self._make_solar_profile(solar_kw)
        total_mw = 50.0

        grid = find_optimal_blended_split(profile, total_mw=total_mw, split_step_pct=100.0)
        full_pct_result = next(r for r in grid["all_results"] if abs(r.split_fraction_short - 1.0) < 1e-9)

        direct_short_solar = profile.scale_to_fleet_mw(total_mw)
        direct_daily = compute_chained_daily_firm_levels(
            solar_hourly=direct_short_solar.hourly, power_mw=total_mw, duration_hours=SHORT_DURATION_HOURS,
            rte_pct=SHORT_DURATION_RTE_PCT,
        )
        pd.testing.assert_series_equal(
            full_pct_result.daily_combined_firm_levels.sort_index(), direct_daily.sort_index(),
            check_names=False,
        )

    def test_best_result_is_genuinely_the_maximum_across_the_grid(self):
        solar_kw = [150.0] * 24 * 10
        profile = self._make_solar_profile(solar_kw)
        grid = find_optimal_blended_split(profile, total_mw=30.0, split_step_pct=25.0)

        best = grid["best_result"]
        for r in grid["all_results"]:
            self.assertGreaterEqual(best.worst_daily_firm_level_mw, r.worst_daily_firm_level_mw - 1e-9)

    def test_pure_long_duration_dominates_under_a_strict_worst_day_objective(self):
        """A real, generalizable finding (not a code bug): the worst-daily
        firm level is monotonically non-increasing as split_fraction_short
        rises from 0% to 100%, confirmed directly against two genuinely
        different constructed patterns (one with a 3-day trough, one with
        only isolated 1-day dips and no multi-day event at all) before
        writing this test -- an earlier version of this test wrongly
        assumed a genuine interior optimum would exist. The reason: since
        both sub-fleets share the same total MW, reallocating MW from the
        100-hr to the 10-hr sub-fleet loses 10x its energy-storage
        capacity (duration) to gain only a 10-point RTE improvement (90%
        vs 80%) -- nowhere near enough to compensate under a strict
        worst-day objective, since the worst day is fundamentally bounded
        by how much stored energy is available to draw down, not how
        efficiently it was charged. This is a real, substantive result
        about how this specific objective interacts with these specific
        duration/RTE choices, not a test-design artifact -- worth
        reporting directly, not silently working around."""
        pattern = [200.0] * 24 * 4 + [20.0] * 24 + [200.0] * 24 * 6 + [20.0] * 24 * 3 + [200.0] * 24 * 6
        profile = self._make_solar_profile(pattern)
        grid = find_optimal_blended_split(profile, total_mw=40.0, split_step_pct=10.0)

        worst_by_split = [r.worst_daily_firm_level_mw for r in
                          sorted(grid["all_results"], key=lambda r: r.split_fraction_short)]
        for i in range(1, len(worst_by_split)):
            self.assertLessEqual(worst_by_split[i], worst_by_split[i - 1] + 1e-9)
        self.assertAlmostEqual(grid["best_result"].split_fraction_short, 0.0, places=6)

    def test_real_data_small_slice(self):
        """Real-data sanity check on a small slice before the full
        9-year run."""
        solar_profile = SolarSiteProfile.from_sam_export_yearly_files(
            PROJECT_DIR, site_name="Sterling", years=[2018],
        )
        small_slice_hourly = solar_profile.hourly[
            solar_profile.hourly["timestamp"] < pd.Timestamp("2018-02-15")
        ].reset_index(drop=True)
        small_profile = SolarSiteProfile(
            site_name="Sterling-slice", nameplate_kw=solar_profile.nameplate_kw,
            tilt_degrees=solar_profile.tilt_degrees, system_losses_pct=solar_profile.system_losses_pct,
            years=[2018], hourly=small_slice_hourly,
        )
        grid = find_optimal_blended_split(small_profile, total_mw=2_908.4, split_step_pct=25.0)
        self.assertEqual(len(grid["all_results"]), 5)  # 0, 25, 50, 75, 100
        self.assertGreater(grid["best_result"].worst_daily_firm_level_mw, 0.0)


class TestModuleConstants(unittest.TestCase):

    def test_duration_and_rte_constants_match_established_user_decisions(self):
        self.assertEqual(SHORT_DURATION_HOURS, 10.0)
        self.assertEqual(SHORT_DURATION_RTE_PCT, 90.0)  # sodium-ion, VA_SLCOE_Model.xlsx row 35
        self.assertEqual(LONG_DURATION_HOURS, 100.0)
        self.assertEqual(LONG_DURATION_RTE_PCT, 80.0)  # iron-air, VA_SLCOE_Model.xlsx row 39

    def test_lookahead_and_starting_soc_match_established_user_decisions(self):
        self.assertEqual(LOOKAHEAD_HOURS, 72)
        self.assertEqual(DEFAULT_FIRMING_STARTING_SOC_PCT, 50.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
