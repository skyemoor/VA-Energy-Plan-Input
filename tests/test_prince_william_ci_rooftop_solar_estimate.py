import unittest

import pandas as pd

from prince_william_ci_rooftop_solar_estimate import (
    COMMERCIAL_STRUCTURE_TYPE_CODE,
    MIN_VIABLE_ROOFTOP_SQFT,
    PrinceWilliamCiRooftopSolarEstimate,
    build_ci_eligible_population,
    estimate_prince_william_ci_rooftop_solar,
)

PROJECT_XLSX_PATH = "/mnt/project/PWCCommericialBuildings.xlsx"


class TestBuildCiEligiblePopulation(unittest.TestCase):

    def _make_df(self, rows):
        return pd.DataFrame(rows)

    def test_commercial_above_floor_included(self):
        df = self._make_df([
            {"StructureType": 3, "ShapeSTArea": 1000.0},
            {"StructureType": 3, "ShapeSTArea": 600.0},  # exactly at floor
        ])
        result = build_ci_eligible_population(df)
        self.assertEqual(len(result), 2)

    def test_commercial_below_floor_excluded(self):
        df = self._make_df([
            {"StructureType": 3, "ShapeSTArea": 599.0},
        ])
        result = build_ci_eligible_population(df)
        self.assertEqual(len(result), 0)

    def test_non_commercial_types_excluded_regardless_of_size(self):
        """Defensive re-check: even though the source is described as
        already pre-filtered to StructureType=3, this confirms the
        function doesn't blindly trust that -- a future, less-filtered
        extract would still be handled correctly."""
        df = self._make_df([
            {"StructureType": 1, "ShapeSTArea": 50000.0},  # Residence, large
            {"StructureType": 10, "ShapeSTArea": 50000.0},  # Mixed Use, large
            {"StructureType": 5, "ShapeSTArea": 50000.0},  # Tank, large
        ])
        result = build_ci_eligible_population(df)
        self.assertEqual(len(result), 0)

    def test_commercial_type_code_matches_confirmed_legend(self):
        self.assertEqual(COMMERCIAL_STRUCTURE_TYPE_CODE, 3)


class TestEstimatePrinceWilliamCiRooftopSolar(unittest.TestCase):

    def test_hand_computed_simple_case(self):
        """2 buildings, total footprint 10,000 sqft. Uses the real NVRC
        density (mean=0.006792, median=0.006661 kW/sqft, same baseline
        already hand-verified for Fairfax/Arlington) -- so
        total_mw_mean = 10,000 * 0.006792 / 1000 = 0.06792 MW."""
        df = pd.DataFrame([
            {"StructureType": 3, "ShapeSTArea": 6000.0},
            {"StructureType": 3, "ShapeSTArea": 4000.0},
        ])
        result = estimate_prince_william_ci_rooftop_solar(df)
        self.assertEqual(result.n_buildings, 2)
        self.assertAlmostEqual(result.total_footprint_sqft, 10_000.0, places=2)
        self.assertAlmostEqual(result.total_mw_mean_based, 0.06792, places=5)
        self.assertAlmostEqual(result.density_stats.mean_kw_per_sqft, 0.006792, places=6)

    def test_no_combined_field_exists(self):
        df = pd.DataFrame([{"StructureType": 3, "ShapeSTArea": 6000.0}])
        result = estimate_prince_william_ci_rooftop_solar(df)
        self.assertFalse(hasattr(result, "total_mw_combined"))
        self.assertFalse(hasattr(result, "total_mwh_per_year_combined"))

    def test_returns_correct_type(self):
        df = pd.DataFrame([{"StructureType": 3, "ShapeSTArea": 6000.0}])
        self.assertIsInstance(estimate_prince_william_ci_rooftop_solar(df), PrinceWilliamCiRooftopSolarEstimate)

    def test_empty_eligible_population_gives_zero(self):
        df = pd.DataFrame([{"StructureType": 1, "ShapeSTArea": 50000.0}])
        result = estimate_prince_william_ci_rooftop_solar(df)
        self.assertEqual(result.n_buildings, 0)
        self.assertEqual(result.total_mw_mean_based, 0.0)


class TestRealDataCrossCheck(unittest.TestCase):
    """Cross-checks against the figures hand-verified directly in chat
    before this module was built: 2,497 buildings >=600 sqft, 40,171,076
    sqft (922.2 acres) total footprint."""

    def test_real_data_population_matches_hand_verified_figures(self):
        df = pd.read_excel(PROJECT_XLSX_PATH)
        eligible = build_ci_eligible_population(df)
        self.assertEqual(len(eligible), 2_497)
        self.assertAlmostEqual(eligible["ShapeSTArea"].sum(), 40_171_076, delta=10)

    def test_real_data_full_estimate_runs_and_is_sensible(self):
        df = pd.read_excel(PROJECT_XLSX_PATH)
        result = estimate_prince_william_ci_rooftop_solar(df)
        self.assertEqual(result.n_buildings, 2_497)
        self.assertGreater(result.total_mw_mean_based, 0)
        self.assertGreater(result.total_mwh_per_year_mean_based, 0)

    def test_objectid_and_globalid_are_genuinely_unique(self):
        """Direct confirmation (not assumed) of the no-dedup-field
        limitation stated in the module's own docstring."""
        df = pd.read_excel(PROJECT_XLSX_PATH)
        self.assertTrue(df["OBJECTID"].is_unique)
        self.assertTrue(df["GlobalID"].is_unique)


if __name__ == "__main__":
    unittest.main(verbosity=2)
