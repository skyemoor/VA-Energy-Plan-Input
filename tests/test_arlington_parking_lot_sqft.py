import unittest

import pandas as pd

from arlington_parking_lot_sqft import (
    MIN_QUALIFYING_LOT_SQFT,
    ArlingtonParkingLotTotals,
    _validate_expected_columns,
    compute_totals,
)

PROJECT_CSV_PATH = "/mnt/project/Arlington_Pave_Parking_Lot_Polygons.csv"


class TestValidateExpectedColumns(unittest.TestCase):

    def test_valid_columns_passes(self):
        df = pd.DataFrame({"OBJECTID": [1, 2], "SHAPE_Area": [100.0, 200.0]})
        _validate_expected_columns(df)  # should not raise

    def test_missing_required_column_raises(self):
        df = pd.DataFrame({"OBJECTID": [1, 2]})  # missing SHAPE_Area
        with self.assertRaises(ValueError):
            _validate_expected_columns(df)


class TestComputeTotals(unittest.TestCase):

    def test_hand_computed_case(self):
        df = pd.DataFrame({
            "OBJECTID": [1, 2, 3, 4],
            "SHAPE_Area": [1_000.0, 5_999.0, 6_000.0, 10_000.0],
        })
        totals = compute_totals(df)
        self.assertEqual(totals.total_rows, 4)
        self.assertAlmostEqual(totals.unfiltered_sqft, 22_999.0, places=2)
        self.assertAlmostEqual(totals.min_size_filtered_sqft, 16_000.0, places=2)
        self.assertEqual(totals.min_size_filtered_rows, 2)

    def test_custom_threshold(self):
        df = pd.DataFrame({"OBJECTID": [1, 2, 3], "SHAPE_Area": [100.0, 500.0, 1_000.0]})
        totals = compute_totals(df, min_qualifying_sqft=500.0)
        self.assertEqual(totals.min_size_filtered_rows, 2)
        self.assertAlmostEqual(totals.min_size_filtered_sqft, 1_500.0, places=2)

    def test_as_acres_conversion(self):
        df = pd.DataFrame({"OBJECTID": [1], "SHAPE_Area": [43_560.0]})
        totals = compute_totals(df)
        self.assertAlmostEqual(totals.as_acres(43_560.0), 1.0, places=6)

    def test_returns_correct_type(self):
        df = pd.DataFrame({"OBJECTID": [1], "SHAPE_Area": [100.0]})
        self.assertIsInstance(compute_totals(df), ArlingtonParkingLotTotals)


class TestRealDataCrossCheck(unittest.TestCase):
    """Cross-checks against the already-established, hand-verified real
    figures from earlier in this conversation: 2,783 total rows, 1,428
    rows / 44,057,781 sqft at the established 6,000 sqft threshold."""

    def test_real_data_matches_established_figures(self):
        from arlington_parking_lot_sqft import load_arlington_parking_lots
        df = load_arlington_parking_lots(PROJECT_CSV_PATH)
        totals = compute_totals(df)
        self.assertEqual(totals.total_rows, 2_783)
        self.assertEqual(totals.min_size_filtered_rows, 1_428)
        self.assertAlmostEqual(totals.min_size_filtered_sqft, 44_057_781, delta=10)

    def test_objectid_is_genuinely_unique(self):
        """Direct confirmation (not assumed) -- if this ever stops being
        true, the size-filtering logic above would still work correctly
        since it doesn't depend on OBJECTID uniqueness, but any future
        dedup logic added to this loader would need to know."""
        from arlington_parking_lot_sqft import load_arlington_parking_lots
        df = load_arlington_parking_lots(PROJECT_CSV_PATH)
        self.assertTrue(df["OBJECTID"].is_unique)


if __name__ == "__main__":
    unittest.main(verbosity=2)
