"""
test_loudoun_parking_lot_sqft.py

Tests loudoun_parking_lot_sqft.py: hand-verifiable unit tests on a small constructed dataset,
plus an integration test against the real uploaded file that cross-checks against numbers
independently computed via a separate ad-hoc script before this module existed.
"""
import unittest

import pandas as pd

from loudoun_parking_lot_sqft import (
    MIN_QUALIFYING_LOT_SQFT,
    _validate_all_type_2,
    compute_totals,
    load_road_casing_type2,
)

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
