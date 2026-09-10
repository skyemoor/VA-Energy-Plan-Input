"""
test_loudoun_siting.py

Rooftop and parking-lot solar siting tests for Loudoun County, bundled into one file (2026-09-10).

WHY BUNDLED BY COUNTY RATHER THAN PARAMETERIZED ACROSS COUNTIES

The first consolidation proposed was a single suite parameterized over all four counties.
Inspecting them showed that would have been wrong: they do not test the same logic with different
data. Arlington tests building-type eligibility against GIS footprints; Loudoun tests address
parsing and unique-building counting from business-account records; the others differ again --
because each county publishes different source data. A parameterized suite would assert a
commonality that does not exist, which this project's own standards warn against directly
("forcing a single unit across genuinely different feature types would be a false consistency, not
a real one").

What IS genuinely shared -- descriptive statistics, compute_totals(), the abstract-base contract --
is tested once in test_rooftop_solar_estimation_base.py and deliberately not repeated here.

Bundling by county removes the one-file-per-measure split, which was an artifact of how the work
was written rather than a property of the analysis, while keeping each county's real
county-specific logic intact.

COLLECTED ONLY WHEN THIS COUNTY'S MODULES ARE PRESENT. They are recorded as not-yet-restored in
docs/PIPELINE_COMPLETENESS.md, so conftest.py ignores this file until they return -- determined by
attempting the import, so it un-ignores itself automatically rather than needing a list updated.
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
import pandas as pd
from loudoun_parking_lot_sqft import (
    MIN_QUALIFYING_LOT_SQFT,
    _validate_all_type_2,
    compute_totals,
    load_road_casing_type2,
)


# ==========================================================================
# ROOFTOP -- merged from test_loudoun_ci_rooftop_solar_estimate.py
# ==========================================================================

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


# ==========================================================================
# PARKING -- merged from test_loudoun_parking_lot_sqft.py
# ==========================================================================

REAL_FILE_PATH = "/mnt/project/Loudoun_Road_Casing_type_2.xlsx"


class TestValidateAllType2(unittest.TestCase):

    def test_accepts_all_type_2(self):
        df = pd.DataFrame({"RD_TYPE": [2, 2, 2]})
        _validate_all_type_2(df)  # should not raise

    def test_rejects_mixed_types(self):
        df = pd.DataFrame({"RD_TYPE": [2, 2, 1]})
        with self.assertRaises(ValueError):
            _validate_all_type_2(df)


class TestComputeTotals(unittest.TestCase):
    """Uses a small, fully hand-verifiable dataset so every field of the
    result can be checked against an independent, by-hand calculation."""

    def setUp(self):
        # Row 1: 500 sqft, paved      -- below threshold
        # Row 2: 3,000 sqft, unpaved  -- below threshold
        # Row 3: 10,000 sqft, paved   -- above threshold
        # Row 4: 50,000 sqft, unpaved -- above threshold (also the largest)
        # Row 5: 8,000 sqft, paved    -- above threshold
        self.df = pd.DataFrame({
            "RD_TYPE": [2, 2, 2, 2, 2],
            "RD_SURFACE": ["P", "N", "P", "N", "P"],
            "Shape_Area": [500, 3000, 10000, 50000, 8000],
        })

    def test_total_rows(self):
        result = compute_totals(self.df)
        self.assertEqual(result.total_rows, 5)

    def test_unfiltered_sqft(self):
        result = compute_totals(self.df)
        self.assertEqual(result.unfiltered_sqft, 500 + 3000 + 10000 + 50000 + 8000)

    def test_paved_only(self):
        result = compute_totals(self.df)
        self.assertEqual(result.paved_only_rows, 3)
        self.assertEqual(result.paved_only_sqft, 500 + 10000 + 8000)

    def test_min_size_filtered_default_threshold(self):
        result = compute_totals(self.df)  # default threshold = 6,000
        self.assertEqual(result.min_size_filtered_rows, 3)  # rows 3, 4, 5
        self.assertEqual(result.min_size_filtered_sqft, 10000 + 50000 + 8000)

    def test_min_size_and_paved(self):
        result = compute_totals(self.df)
        self.assertEqual(result.min_size_and_paved_rows, 2)  # rows 3, 5
        self.assertEqual(result.min_size_and_paved_sqft, 10000 + 8000)

    def test_small_fragments(self):
        result = compute_totals(self.df)
        self.assertEqual(result.small_fragment_rows, 2)  # rows 1, 2
        self.assertEqual(result.small_fragment_sqft, 500 + 3000)

    def test_largest_single_polygon(self):
        result = compute_totals(self.df)
        self.assertEqual(result.largest_single_polygon_sqft, 50000)

    def test_top_38_with_fewer_than_38_rows_returns_all_rows(self):
        """Edge case: nlargest(38, ...) on a 5-row dataset should just
        return all 5 rows, equal to the unfiltered total -- worth locking
        in explicitly since the real file's 'top 38' finding depends on
        this behaving sensibly at any row count."""
        result = compute_totals(self.df)
        self.assertEqual(result.top_38_polygons_sqft, result.unfiltered_sqft)

    def test_custom_threshold_changes_the_split(self):
        """Confirms the threshold is a real, live parameter, not hardcoded
        despite being exposed as one."""
        result = compute_totals(self.df, min_qualifying_sqft=20000)
        self.assertEqual(result.min_size_filtered_rows, 1)  # only row 4 (50,000)
        self.assertEqual(result.min_size_filtered_sqft, 50000)

    def test_as_acres_conversion(self):
        result = compute_totals(self.df)
        self.assertAlmostEqual(result.as_acres(43560), 1.0, places=6)


class TestAgainstRealUploadedFile(unittest.TestCase):
    """Integration test against the actual file the user uploaded --
    cross-checks this module's output against figures independently
    computed via a separate, earlier ad-hoc script, per this project's
    standing practice of verifying a real run's output against an
    independent baseline rather than trusting a single code path."""

    def test_real_file_loads_and_validates_cleanly(self):
        df = load_road_casing_type2(REAL_FILE_PATH)
        self.assertEqual(len(df), 11317)

    def test_real_file_totals_match_independently_computed_baseline(self):
        df = load_road_casing_type2(REAL_FILE_PATH)
        result = compute_totals(df)
        # Baseline figures computed via a separate ad-hoc script before
        # this module existed -- see Data_Sourcing_Log.md for the run.
        self.assertAlmostEqual(result.unfiltered_sqft, 246_091_777, delta=1)
        self.assertAlmostEqual(result.paved_only_sqft, 209_692_142, delta=1)
        self.assertEqual(result.paved_only_rows, 10429)
        self.assertAlmostEqual(result.min_size_filtered_sqft, 232_679_056, delta=1)
        self.assertEqual(result.min_size_filtered_rows, 3500)
        self.assertAlmostEqual(result.min_size_and_paved_sqft, 196_917_109, delta=1)
        self.assertEqual(result.min_size_and_paved_rows, 2821)
        self.assertAlmostEqual(result.largest_single_polygon_sqft, 4_043_822, delta=1)
        self.assertAlmostEqual(result.top_38_polygons_sqft, 32_691_805, delta=1)


class TestUnpavedLotsAreNotSmallInformalAreas(unittest.TestCase):
    """Locks in a key, non-obvious finding from direct data inspection,
    made after the user raised permeable-pavement requirements as a likely
    explanation for RD_SURFACE='N': unpaved lots are NOT smaller/more
    informal than paved lots -- they skew dramatically LARGER, consistent
    with being real, engineered commercial facilities (plausibly permeable
    pavement, given Loudoun's own zoning ordinance explicitly pairs
    "unpaved or permeable surfaced" as one category) rather than random
    rural gravel overflow areas. This is why RD_SURFACE should NOT be used
    as a simple "paved=trustworthy, unpaved=exclude" filter."""

    def test_unpaved_lots_have_higher_median_area_than_paved(self):
        df = load_road_casing_type2(REAL_FILE_PATH)
        paved_median = df[df["RD_SURFACE"] == "P"]["Shape_Area"].median()
        unpaved_median = df[df["RD_SURFACE"] == "N"]["Shape_Area"].median()
        self.assertGreater(
            unpaved_median, paved_median * 5,
            "Unpaved lots should skew substantially larger than paved lots, "
            "not smaller -- consistent with being engineered facilities, "
            "not informal gravel areas."
        )

    def test_majority_of_unpaved_lots_meet_qualifying_size_threshold(self):
        """76.5% of unpaved lots meet the county's own '20+ space' implied
        size threshold, vs. only 27.0% of paved lots -- the opposite of
        what a 'paved=real, unpaved=noise' assumption would predict."""
        df = load_road_casing_type2(REAL_FILE_PATH)
        unpaved = df[df["RD_SURFACE"] == "N"]
        qualifying_share = (unpaved["Shape_Area"] >= MIN_QUALIFYING_LOT_SQFT).mean()
        self.assertGreater(qualifying_share, 0.5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
