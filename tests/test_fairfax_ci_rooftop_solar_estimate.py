import unittest

from fairfax_ci_rooftop_solar_estimate import (
    HOURS_PER_YEAR,
    NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR,
    NVRC_SAMPLE_KW_DATA_POINTS,
    NVRC_SAMPLE_ROOF_SQFT_DATA_POINTS,
    PerSqftKwDensityStats,
    compute_kw_per_sqft_density_stats,
    estimate_fairfax_ci_rooftop_solar,
)


class TestReusedSharedConstants(unittest.TestCase):
    """Rule 2: every shared calculation needs a test that locks it to a
    trusted baseline IN EVERY CONSUMER that uses it, not just the module
    where it was first established. These constants are imported from
    loudoun_ci_rooftop_solar_estimate.py, not redefined here (Rule 6) --
    but this module's own test suite still needs to confirm the import
    genuinely resolves to the correct, established values."""

    def test_capacity_factor_matches_established_source_value(self):
        # VA_SLCOE_Model.xlsx, "Assumptions & Sources" tab, row 13
        self.assertEqual(NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR, 0.20)

    def test_hours_per_year_is_correct(self):
        self.assertEqual(HOURS_PER_YEAR, 8_760)

    def test_nvrc_sample_kw_points_match_established_8_point_sample(self):
        self.assertEqual(len(NVRC_SAMPLE_KW_DATA_POINTS), 8)
        # Spot-check a couple of the real, sourced values directly
        self.assertIn(132.41, NVRC_SAMPLE_KW_DATA_POINTS)
        self.assertIn(9.72, NVRC_SAMPLE_KW_DATA_POINTS)


class TestRoofSqftPointsAlignWithKwPoints(unittest.TestCase):
    """The paired roof-sqft list must be in the SAME order as the
    imported kW list -- these are zipped together elsewhere, so a silent
    order mismatch would corrupt every downstream ratio without raising
    any error. Checked directly against loudoun_test_batch_results.md's
    own table, not assumed."""

    def test_same_length(self):
        self.assertEqual(len(NVRC_SAMPLE_ROOF_SQFT_DATA_POINTS), len(NVRC_SAMPLE_KW_DATA_POINTS))

    def test_first_point_matches_source_table(self):
        # 21335 Signal Hill Plz, Sterling: 20,922.30 sqft, 132.41 kW
        self.assertAlmostEqual(NVRC_SAMPLE_ROOF_SQFT_DATA_POINTS[0], 20_922.30, places=2)
        self.assertAlmostEqual(NVRC_SAMPLE_KW_DATA_POINTS[0], 132.41, places=2)

    def test_last_point_matches_source_table(self):
        # 44375 Apache Cir, Ashburn: 2,225.08 sqft, 10.31 kW
        self.assertAlmostEqual(NVRC_SAMPLE_ROOF_SQFT_DATA_POINTS[-1], 2_225.08, places=2)
        self.assertAlmostEqual(NVRC_SAMPLE_KW_DATA_POINTS[-1], 10.31, places=2)


class TestComputeKwPerSqftDensityStats(unittest.TestCase):

    def test_hand_verified_against_real_8_point_nvrc_sample(self):
        """Hand-computed independently in chat before writing this test
        (see prior turn's calculation): n=8, mean=0.006792,
        median=0.006661, min=0.003948, max=0.009860 kW/sqft."""
        pairs = list(zip(NVRC_SAMPLE_ROOF_SQFT_DATA_POINTS, NVRC_SAMPLE_KW_DATA_POINTS))
        result = compute_kw_per_sqft_density_stats(pairs)
        self.assertEqual(result.n, 8)
        self.assertAlmostEqual(result.mean_kw_per_sqft, 0.006792, places=6)
        self.assertAlmostEqual(result.median_kw_per_sqft, 0.006661, places=6)
        self.assertAlmostEqual(result.min_kw_per_sqft, 0.003948, places=6)
        self.assertAlmostEqual(result.max_kw_per_sqft, 0.009860, places=6)

    def test_simple_two_point_case_hand_computed(self):
        # (1000 sqft, 10 kW) -> 0.01 kW/sqft; (2000 sqft, 30 kW) -> 0.015 kW/sqft
        # mean = median = 0.0125 for this simple, symmetric 2-point case
        result = compute_kw_per_sqft_density_stats([(1000.0, 10.0), (2000.0, 30.0)])
        self.assertEqual(result.n, 2)
        self.assertAlmostEqual(result.mean_kw_per_sqft, 0.0125, places=8)
        self.assertAlmostEqual(result.median_kw_per_sqft, 0.0125, places=8)
        self.assertAlmostEqual(result.min_kw_per_sqft, 0.01, places=8)
        self.assertAlmostEqual(result.max_kw_per_sqft, 0.015, places=8)

    def test_returns_correct_dataclass_type(self):
        result = compute_kw_per_sqft_density_stats([(100.0, 1.0)])
        self.assertIsInstance(result, PerSqftKwDensityStats)


class TestEstimateFairfaxCiRooftopSolar(unittest.TestCase):

    def test_hand_computed_simple_case(self):
        """total_footprint_sqft=5,000, using the simple 2-point density
        sample from above (mean=median=0.0125 kW/sqft).
        total_mw = 5,000 * 0.0125 / 1000 = 0.0625 MW (mean AND median,
        since the sample's mean equals its median here).
        total_mwh = 0.0625 * 8,760 * 0.20 = 109.5 MWh."""
        result = estimate_fairfax_ci_rooftop_solar(
            total_footprint_sqft=5_000.0, n_buildings=3,
            roof_sqft_and_kw_pairs=[(1000.0, 10.0), (2000.0, 30.0)],
        )
        self.assertAlmostEqual(result.total_mw_mean_based, 0.0625, places=6)
        self.assertAlmostEqual(result.total_mw_median_based, 0.0625, places=6)
        self.assertAlmostEqual(result.total_mwh_per_year_mean_based, 109.5, places=2)
        self.assertAlmostEqual(result.total_mwh_per_year_median_based, 109.5, places=2)
        # No total_mw_combined / total_mwh_per_year_combined check -- removed after direct user
        # challenge; averaging a mean-based and median-based total has no sound statistical
        # justification for an aggregate/sum estimate (see dataclass docstring note).
        self.assertFalse(hasattr(result, "total_mw_combined"))
        self.assertFalse(hasattr(result, "total_mwh_per_year_combined"))

    def test_default_uses_real_nvrc_sample_when_pairs_not_supplied(self):
        """Confirms the default (no roof_sqft_and_kw_pairs argument)
        genuinely uses the real, established 8-point NVRC sample -- not
        silently falling back to some other default."""
        result = estimate_fairfax_ci_rooftop_solar(total_footprint_sqft=1_000_000.0, n_buildings=100)
        self.assertEqual(result.density_stats.n, 8)
        self.assertAlmostEqual(result.density_stats.mean_kw_per_sqft, 0.006792, places=6)

    def test_capacity_factor_used_is_the_reused_shared_constant(self):
        result = estimate_fairfax_ci_rooftop_solar(total_footprint_sqft=1_000.0, n_buildings=1)
        self.assertEqual(result.capacity_factor_used, NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR)

    def test_n_buildings_and_total_footprint_pass_through_unchanged(self):
        """These two fields aren't used in any calculation -- just carried
        through for reporting -- so confirm they're stored exactly as
        given, not silently altered."""
        result = estimate_fairfax_ci_rooftop_solar(total_footprint_sqft=19_493_424.0, n_buildings=4_510)
        self.assertEqual(result.n_buildings, 4_510)
        self.assertEqual(result.total_footprint_sqft, 19_493_424.0)

    def test_zero_footprint_gives_zero_mw_and_mwh(self):
        result = estimate_fairfax_ci_rooftop_solar(total_footprint_sqft=0.0, n_buildings=0)
        self.assertEqual(result.total_mw_mean_based, 0.0)
        self.assertEqual(result.total_mwh_per_year_mean_based, 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
