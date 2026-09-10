import unittest

import pandas as pd

from fairfax_parking_lot_sqft import (
    MIN_QUALIFYING_LOT_SQFT,
    PAVED_PARKING_LOT_TYPE,
    FairfaxParkingLotTotals,
    _validate_all_paved_parking_lot,
    compute_totals,
)

PROJECT_CSV_PATH = "/mnt/project/FairfaxCounty_Driveways_and_Parking_Lots_387463314629760591.csv"


class TestValidateAllPavedParkingLot(unittest.TestCase):

    def test_all_paved_parking_lot_passes(self):
        df = pd.DataFrame({"Type": ["PAVED PARKING LOT", "PAVED PARKING LOT"], "Shape__Area": [100.0, 200.0]})
        _validate_all_paved_parking_lot(df)  # should not raise

    def test_unexpected_type_raises(self):
        df = pd.DataFrame({"Type": ["PAVED PARKING LOT", "DRIVEWAY"], "Shape__Area": [100.0, 200.0]})
        with self.assertRaises(ValueError):
            _validate_all_paved_parking_lot(df)


class TestComputeTotals(unittest.TestCase):

    def test_hand_computed_case(self):
        df = pd.DataFrame({
            "Type": [PAVED_PARKING_LOT_TYPE] * 4,
            "Shape__Area": [1_000.0, 5_999.0, 6_000.0, 10_000.0],
        })
        totals = compute_totals(df)
        self.assertEqual(totals.total_rows, 4)
        self.assertAlmostEqual(totals.unfiltered_sqft, 22_999.0, places=2)
        # Only the two rows >= 6,000 sqft (exactly 6,000 counts, per >=)
        self.assertAlmostEqual(totals.min_size_filtered_sqft, 16_000.0, places=2)
        self.assertEqual(totals.min_size_filtered_rows, 2)

    def test_custom_threshold(self):
        df = pd.DataFrame({"Type": [PAVED_PARKING_LOT_TYPE] * 3, "Shape__Area": [100.0, 500.0, 1_000.0]})
        totals = compute_totals(df, min_qualifying_sqft=500.0)
        self.assertEqual(totals.min_size_filtered_rows, 2)
        self.assertAlmostEqual(totals.min_size_filtered_sqft, 1_500.0, places=2)

    def test_as_acres_conversion(self):
        df = pd.DataFrame({"Type": [PAVED_PARKING_LOT_TYPE], "Shape__Area": [43_560.0]})
        totals = compute_totals(df)
        self.assertAlmostEqual(totals.as_acres(43_560.0), 1.0, places=6)

    def test_returns_correct_type(self):
        df = pd.DataFrame({"Type": [PAVED_PARKING_LOT_TYPE], "Shape__Area": [100.0]})
        self.assertIsInstance(compute_totals(df), FairfaxParkingLotTotals)


class TestRealDataCrossCheck(unittest.TestCase):
    """Cross-checks against the already-established, hand-verified real
    figures from earlier in this conversation: 23,651 total rows, 2,810
    rows / 56,551,120 sqft at the established 6,000 sqft threshold."""

    def test_real_data_matches_established_figures(self):
        from fairfax_parking_lot_sqft import load_fairfax_parking_lots
        df = load_fairfax_parking_lots(PROJECT_CSV_PATH)
        totals = compute_totals(df)
        self.assertEqual(totals.total_rows, 23_651)
        self.assertEqual(totals.min_size_filtered_rows, 2_810)
        self.assertAlmostEqual(totals.min_size_filtered_sqft, 56_551_120, delta=10)


if __name__ == "__main__":
    unittest.main(verbosity=2)
