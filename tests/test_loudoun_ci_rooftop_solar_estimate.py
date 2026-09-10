"""
test_loudoun_ci_rooftop_solar_estimate.py

Tests loudoun_ci_rooftop_solar_estimate.py, including an independent, by-hand cross-check of the
mean/median statistics computed from the real 8-point NVRC sample (per this project's own
standing practice of cross-verifying computed results against an independent baseline).
"""
import unittest

from loudoun_ci_rooftop_solar_estimate import (
    NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR,
    NVRC_SAMPLE_KW_DATA_POINTS,
    HOURS_PER_YEAR,
    BuildingDedupResult,
    build_unique_building_list,
    compute_per_building_kw_stats,
    count_unique_buildings,
    estimate_loudoun_ci_rooftop_solar,
    strip_suite_from_address,
)


class TestStripSuiteFromAddress(unittest.TestCase):

    def test_strips_ste_with_number(self):
        self.assertEqual(strip_suite_from_address("21631 RIDGETOP CIR STE 250"), "21631 RIDGETOP CIR")

    def test_strips_unit(self):
        self.assertEqual(strip_suite_from_address("123 MAIN ST UNIT 5"), "123 MAIN ST")

    def test_leaves_address_with_no_suite_unchanged(self):
        self.assertEqual(strip_suite_from_address("44375 APACHE CIR"), "44375 APACHE CIR")

    def test_strips_trailing_comma_left_behind(self):
        self.assertEqual(strip_suite_from_address("123 MAIN ST, STE 100"), "123 MAIN ST")


class TestCountUniqueBuildings(unittest.TestCase):
    """Uses small, constructed record sets that mirror the two real patterns
    found in the actual data: many business records sharing the exact same
    suite address, and different suites within one building."""

    def test_same_exact_suite_shared_by_many_businesses_counts_as_one_building(self):
        """Mirrors the real, confirmed pattern: e.g. '20130 Lakeview Center
        Plz Ste 400' registered under 33 different business names -- must
        count as ONE building, not 33."""
        records = [
            {"address": "20130 LAKEVIEW CENTER PLZ STE 400", "city": "STERLING"},
            {"address": "20130 LAKEVIEW CENTER PLZ STE 400", "city": "STERLING"},
            {"address": "20130 LAKEVIEW CENTER PLZ STE 400", "city": "STERLING"},
        ]
        result = count_unique_buildings(records)
        self.assertEqual(result.total_records, 3)
        self.assertEqual(result.unique_exact_addresses, 1)
        self.assertEqual(result.unique_buildings, 1)

    def test_different_suites_in_the_same_building_count_as_one_building(self):
        records = [
            {"address": "123 MAIN ST STE 100", "city": "LEESBURG"},
            {"address": "123 MAIN ST STE 200", "city": "LEESBURG"},
            {"address": "123 MAIN ST STE 300", "city": "LEESBURG"},
        ]
        result = count_unique_buildings(records)
        self.assertEqual(result.unique_exact_addresses, 3, "exact addresses differ by suite")
        self.assertEqual(result.unique_buildings, 1, "but all are the same building")

    def test_genuinely_different_buildings_count_separately(self):
        records = [
            {"address": "123 MAIN ST", "city": "LEESBURG"},
            {"address": "456 OAK AVE", "city": "STERLING"},
        ]
        result = count_unique_buildings(records)
        self.assertEqual(result.unique_buildings, 2)

    def test_same_street_address_in_different_cities_counts_separately(self):
        """A safety check: two genuinely different buildings should not be
        merged just because they happen to share a street address string in
        different towns."""
        records = [
            {"address": "100 MAIN ST", "city": "LEESBURG"},
            {"address": "100 MAIN ST", "city": "PURCELLVILLE"},
        ]
        result = count_unique_buildings(records)
        self.assertEqual(result.unique_buildings, 2)

    def test_empty_address_is_excluded_from_building_count_not_fabricated(self):
        """A record with no address text at all (e.g. an unrecoverable
        corruption case) must not be silently counted as its own distinct
        building -- there's no addressable evidence to deduplicate against."""
        records = [
            {"address": "123 MAIN ST", "city": "LEESBURG"},
            {"address": "", "city": ""},
            {"address": "", "city": ""},
        ]
        result = count_unique_buildings(records)
        self.assertEqual(result.total_records, 3)
        self.assertEqual(result.unique_buildings, 1)


class TestComputePerBuildingKwStats(unittest.TestCase):
    """Cross-verifies against an independent, by-hand calculation of the
    real 8-point NVRC sample's mean and median, per this project's standing
    practice of not trusting a computed result without a second, independent
    check."""

    def test_stats_match_independent_by_hand_calculation(self):
        stats = compute_per_building_kw_stats(NVRC_SAMPLE_KW_DATA_POINTS)
        self.assertEqual(stats.n, 8)
        # Independently computed by hand: sum=923.89, mean=115.48625
        self.assertAlmostEqual(stats.mean_kw, 115.48625, places=5)
        # Independently computed by hand: sorted values, avg of 4th & 5th = 133.13
        self.assertAlmostEqual(stats.median_kw, 133.13, places=5)
        self.assertAlmostEqual(stats.min_kw, 9.72, places=2)
        self.assertAlmostEqual(stats.max_kw, 226.09, places=2)


class TestEstimateLoudounCiRooftopSolar(unittest.TestCase):
    """End-to-end test with a small, fully-known record set, where every
    intermediate number can be verified by hand rather than trusted from a
    large, opaque real run."""

    def test_end_to_end_with_known_small_input(self):
        # 4 unique buildings after dedup (2 exact-address duplicates collapse to 1)
        records = [
            {"address": "1 MAIN ST", "city": "LEESBURG"},
            {"address": "1 MAIN ST", "city": "LEESBURG"},  # duplicate of above
            {"address": "2 OAK AVE STE 100", "city": "STERLING"},
            {"address": "2 OAK AVE STE 200", "city": "STERLING"},  # same building, different suite
            {"address": "3 ELM DR", "city": "ASHBURN"},
        ]
        # Simple sample: mean = median = 100 kW, for an easily hand-checked result
        sample = [100.0, 100.0]
        result = estimate_loudoun_ci_rooftop_solar(records, sample_kw_data_points=sample)

        self.assertEqual(result.dedup.unique_buildings, 3)  # 1 MAIN ST; 2 OAK AVE; 3 ELM DR
        self.assertEqual(result.kw_stats.mean_kw, 100.0)
        self.assertEqual(result.kw_stats.median_kw, 100.0)

        # 3 buildings x 100 kW = 300 kW = 0.3 MW
        self.assertAlmostEqual(result.total_mw_mean_based, 0.3, places=6)
        self.assertAlmostEqual(result.total_mw_median_based, 0.3, places=6)

        # 0.3 MW x 8,760 hrs/yr x 0.20 CF = 525.6 MWh/yr
        expected_mwh = 0.3 * 8_760 * 0.20
        self.assertAlmostEqual(result.total_mwh_per_year_mean_based, expected_mwh, places=4)
        self.assertEqual(result.capacity_factor_used, NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR)

    def test_default_capacity_factor_is_the_established_project_value(self):
        """Locks in that this module reuses the project's own, already-
        sourced 20% NEM distributed solar capacity factor (VA_SLCOE_Model.xlsx
        row 13) by default, rather than a newly-invented number."""
        self.assertEqual(NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR, 0.20)

    def test_no_combined_field_exists(self):
        """Direct, explicit lock-in of the fix: LoudounCiRooftopSolarEstimate
        must NOT expose any 'combined' (mean+median averaged) field --
        removed after direct user challenge established it has no sound
        statistical justification for an aggregate/sum estimate (see
        RooftopSolarTotals' own docstring in rooftop_solar_estimation_base.py).
        Replaces the two tests this module used to have that specifically
        locked in the removed behavior (test_combined_total_is_the_simple_
        average_of_mean_and_median_based, test_combined_mwh_matches_combined_
        mw_via_the_same_capacity_factor)."""
        records = [
            {"address": "1 MAIN ST", "city": "LEESBURG"},
            {"address": "2 OAK AVE", "city": "STERLING"},
        ]
        sample = [0.0, 100.0, 100.0, 100.0, 700.0]
        result = estimate_loudoun_ci_rooftop_solar(records, sample_kw_data_points=sample)
        self.assertFalse(hasattr(result, "total_mw_combined"))
        self.assertFalse(hasattr(result, "total_mwh_per_year_combined"))

    def test_mean_and_median_based_totals_remain_independently_correct(self):
        """Confirms the fix didn't silently break the two totals that ARE
        still meant to be reported -- deliberately asymmetric sample
        (mean=200, median=100) so this is a real, checkable computation."""
        records = [
            {"address": "1 MAIN ST", "city": "LEESBURG"},
            {"address": "2 OAK AVE", "city": "STERLING"},
        ]
        sample = [0.0, 100.0, 100.0, 100.0, 700.0]
        result = estimate_loudoun_ci_rooftop_solar(records, sample_kw_data_points=sample)
        self.assertEqual(result.kw_stats.mean_kw, 200.0)
        self.assertEqual(result.kw_stats.median_kw, 100.0)
        # 2 buildings x 200 kW = 0.4 MW (mean-based); 2 x 100 kW = 0.2 MW (median-based)
        self.assertAlmostEqual(result.total_mw_mean_based, 0.4, places=6)
        self.assertAlmostEqual(result.total_mw_median_based, 0.2, places=6)


class TestBuildUniqueBuildingList(unittest.TestCase):

    def test_row_count_matches_unique_building_count(self):
        records = [
            {"address": "1 MAIN ST", "city": "LEESBURG", "state": "VA"},
            {"address": "1 MAIN ST", "city": "LEESBURG", "state": "VA"},
            {"address": "2 OAK AVE STE 100", "city": "STERLING", "state": "VA"},
            {"address": "2 OAK AVE STE 200", "city": "STERLING", "state": "VA"},
        ]
        rows = build_unique_building_list(records)
        self.assertEqual(len(rows), 2)

    def test_suite_and_record_counts_are_correct(self):
        """Mirrors the real, confirmed pattern directly: one building with
        two distinct suites, one of which is shared by multiple business
        records."""
        records = [
            {"address": "2 OAK AVE STE 100", "city": "STERLING", "state": "VA"},
            {"address": "2 OAK AVE STE 100", "city": "STERLING", "state": "VA"},  # same suite, 2nd business
            {"address": "2 OAK AVE STE 200", "city": "STERLING", "state": "VA"},
        ]
        rows = build_unique_building_list(records)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["base_address"], "2 OAK AVE")
        self.assertEqual(row["unique_suites_at_this_building"], 2)
        self.assertEqual(row["total_business_records_at_this_building"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
