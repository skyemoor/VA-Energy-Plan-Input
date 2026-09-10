import unittest

from rooftop_solar_estimation_base import (
    BaseRooftopSolarEstimator,
    DescriptiveStats,
    RooftopSolarTotals,
    compute_descriptive_stats,
)


class TestComputeDescriptiveStats(unittest.TestCase):

    def test_hand_computed_case(self):
        result = compute_descriptive_stats([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
        self.assertEqual(result.n, 8)
        self.assertAlmostEqual(result.mean, 5.0, places=6)
        self.assertAlmostEqual(result.median, 4.5, places=6)
        self.assertEqual(result.min, 2.0)
        self.assertEqual(result.max, 9.0)

    def test_single_value(self):
        result = compute_descriptive_stats([42.0])
        self.assertEqual(result.n, 1)
        self.assertEqual(result.mean, 42.0)
        self.assertEqual(result.median, 42.0)
        self.assertEqual(result.min, 42.0)
        self.assertEqual(result.max, 42.0)

    def test_returns_correct_type(self):
        self.assertIsInstance(compute_descriptive_stats([1.0, 2.0]), DescriptiveStats)


class TestBaseRooftopSolarEstimatorIsGenuinelyAbstract(unittest.TestCase):

    def test_cannot_instantiate_base_directly(self):
        """Confirms scale_per_unit_value_to_total_mw has no default
        implementation -- attempting to instantiate the base class
        directly (without a subclass providing the hook) must raise,
        not silently succeed with some fallback behavior."""
        with self.assertRaises(TypeError):
            BaseRooftopSolarEstimator()


class _TenXTestEstimator(BaseRooftopSolarEstimator):
    """Minimal concrete subclass for testing compute_totals() in
    isolation, deliberately NOT one of the two real counties -- keeps
    this test suite genuinely testing the shared base's own logic,
    independent of either county's specific scaling scenario."""

    def scale_per_unit_value_to_total_mw(self, per_unit_value: float) -> float:
        return per_unit_value * 10


class TestComputeTotals(unittest.TestCase):

    def test_hand_computed_case(self):
        """mean_per_unit=5, median_per_unit=3, scale factor=10 (from
        _TenXTestEstimator) -> total_mw_mean=50, total_mw_median=30.
        capacity_factor=0.2, hours_per_year=8760 ->
        total_mwh_mean = 50 * 8760 * 0.2 = 87,600
        total_mwh_median = 30 * 8760 * 0.2 = 52,560"""
        estimator = _TenXTestEstimator()
        result = estimator.compute_totals(
            mean_per_unit=5.0, median_per_unit=3.0, capacity_factor=0.2, hours_per_year=8_760,
        )
        self.assertAlmostEqual(result.total_mw_mean_based, 50.0, places=6)
        self.assertAlmostEqual(result.total_mw_median_based, 30.0, places=6)
        self.assertAlmostEqual(result.total_mwh_per_year_mean_based, 87_600.0, places=2)
        self.assertAlmostEqual(result.total_mwh_per_year_median_based, 52_560.0, places=2)
        self.assertEqual(result.capacity_factor_used, 0.2)

    def test_returns_correct_type(self):
        estimator = _TenXTestEstimator()
        result = estimator.compute_totals(1.0, 1.0, 0.2, 8_760)
        self.assertIsInstance(result, RooftopSolarTotals)

    def test_no_combined_field_exists(self):
        """Direct, explicit lock-in of the fix: RooftopSolarTotals must
        NOT expose any 'combined' (mean+median averaged) field -- that
        pattern was removed after direct user challenge established it
        has no sound statistical justification for an aggregate/sum
        estimate (see RooftopSolarTotals' own docstring)."""
        estimator = _TenXTestEstimator()
        result = estimator.compute_totals(5.0, 3.0, 0.2, 8_760)
        self.assertFalse(hasattr(result, "total_mw_combined"))
        self.assertFalse(hasattr(result, "total_mwh_per_year_combined"))
        self.assertFalse(hasattr(result, "combined"))

    def test_zero_per_unit_values_give_zero_totals(self):
        estimator = _TenXTestEstimator()
        result = estimator.compute_totals(0.0, 0.0, 0.2, 8_760)
        self.assertEqual(result.total_mw_mean_based, 0.0)
        self.assertEqual(result.total_mw_median_based, 0.0)
        self.assertEqual(result.total_mwh_per_year_mean_based, 0.0)
        self.assertEqual(result.total_mwh_per_year_median_based, 0.0)

    def test_mean_and_median_scaled_independently_not_conflated(self):
        """A genuinely different mean vs. median per-unit value must
        produce genuinely different totals -- confirms the two are
        scaled independently through the same hook, not silently
        collapsed to one value somewhere in the shared logic."""
        estimator = _TenXTestEstimator()
        result = estimator.compute_totals(mean_per_unit=100.0, median_per_unit=1.0,
                                           capacity_factor=0.2, hours_per_year=8_760)
        self.assertNotAlmostEqual(result.total_mw_mean_based, result.total_mw_median_based, places=2)
        self.assertAlmostEqual(result.total_mw_mean_based, 1_000.0, places=6)
        self.assertAlmostEqual(result.total_mw_median_based, 10.0, places=6)


if __name__ == "__main__":
    unittest.main(verbosity=2)
