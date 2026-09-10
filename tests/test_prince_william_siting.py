"""
test_prince_william_siting.py

Rooftop and parking-lot solar siting tests for Prince William County, bundled into one file (2026-09-10).

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
import pandas as pd
from prince_william_ci_rooftop_solar_estimate import (
    COMMERCIAL_STRUCTURE_TYPE_CODE,
    MIN_VIABLE_ROOFTOP_SQFT,
    PrinceWilliamCiRooftopSolarEstimate,
    build_ci_eligible_population,
    estimate_prince_william_ci_rooftop_solar,
)
from prince_william_parking_lot_density_estimate import (
    FAIRFAX_POPULATION_2025,
    FAIRFAX_QUALIFYING_PARKING_ACRES,
    LOUDOUN_POPULATION_2025,
    LOUDOUN_QUALIFYING_PARKING_ACRES,
    PRINCE_WILLIAM_POPULATION_2025,
    PrinceWilliamParkingEstimate,
    build_estimated_county_parking_data,
    compute_per_capita_density,
    estimate_prince_william_parking_acres,
    run_prince_william_parking_estimate,
)


# ==========================================================================
# ROOFTOP -- merged from test_prince_william_ci_rooftop_solar_estimate.py
# ==========================================================================

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


class TestRooftopRealDataCrossCheck(unittest.TestCase):
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


# ==========================================================================
# PARKING -- merged from test_prince_william_parking_lot_density_estimate.py
# ==========================================================================

class TestComputePerCapitaDensity(unittest.TestCase):

    def test_hand_computed_case(self):
        # 100 acres / 1,000 population = 0.1 acres/capita
        self.assertAlmostEqual(compute_per_capita_density(100.0, 1000.0), 0.1, places=6)

    def test_loudoun_density_matches_established_figure(self):
        """Hand-verified two turns ago in chat: 5,341.6 / 449,749 = 0.011877 acres/capita."""
        density = compute_per_capita_density(LOUDOUN_QUALIFYING_PARKING_ACRES, LOUDOUN_POPULATION_2025)
        self.assertAlmostEqual(density, 0.011877, places=6)

    def test_fairfax_density_matches_established_figure(self):
        """Hand-verified two turns ago in chat: 1,298.2 / 1,167,873 = 0.001112 acres/capita."""
        density = compute_per_capita_density(FAIRFAX_QUALIFYING_PARKING_ACRES, FAIRFAX_POPULATION_2025)
        self.assertAlmostEqual(density, 0.001112, places=6)


class TestEstimateAcres(unittest.TestCase):

    def test_hand_computed_case(self):
        # 0.1 acres/capita x 500,000 population = 50,000 acres
        result = estimate_prince_william_parking_acres(0.1, prince_william_population=500_000)
        self.assertAlmostEqual(result, 50_000.0, places=2)

    def test_loudoun_anchored_matches_established_figure(self):
        """Hand-verified two turns ago: ~5,974 acres."""
        density = compute_per_capita_density(LOUDOUN_QUALIFYING_PARKING_ACRES, LOUDOUN_POPULATION_2025)
        result = estimate_prince_william_parking_acres(density)
        self.assertAlmostEqual(result, 5_974, delta=1)

    def test_fairfax_anchored_matches_established_figure(self):
        """Hand-verified two turns ago: ~559 acres."""
        density = compute_per_capita_density(FAIRFAX_QUALIFYING_PARKING_ACRES, FAIRFAX_POPULATION_2025)
        result = estimate_prince_william_parking_acres(density)
        self.assertAlmostEqual(result, 559, delta=1)


class TestBuildEstimatedCountyParkingData(unittest.TestCase):

    def test_sqft_conversion_correct(self):
        data = build_estimated_county_parking_data(1.0, "Test")  # 1 acre
        self.assertAlmostEqual(data.filtered_parking_sqft, 43_560.0, places=2)

    def test_source_description_labels_as_estimate_not_real_data(self):
        data = build_estimated_county_parking_data(100.0, "Loudoun")
        self.assertIn("NOT real GIS data", data.source_description)
        self.assertIn("Loudoun", data.source_description)


class TestRunPrinceWilliamParkingEstimate(unittest.TestCase):

    def test_loudoun_anchored_full_pipeline_matches_established_figures(self):
        """Cross-check against the full result hand-verified two turns
        ago: MW 1734.7-2168.4, annual MWh/yr 3,039,279-3,799,098."""
        density = compute_per_capita_density(LOUDOUN_QUALIFYING_PARKING_ACRES, LOUDOUN_POPULATION_2025)
        result = run_prince_william_parking_estimate(density, "Loudoun")
        self.assertAlmostEqual(result.mw_low, 1734.7, delta=1)
        self.assertAlmostEqual(result.mw_high, 2168.4, delta=1)
        self.assertAlmostEqual(result.annual_mwh_low, 3_039_279, delta=1000)
        self.assertAlmostEqual(result.annual_mwh_high, 3_799_098, delta=1000)

    def test_fairfax_anchored_full_pipeline_matches_established_figures(self):
        """Cross-check against the sensitivity-check result hand-verified
        two turns ago: MW 162.4-203.0, annual MWh/yr 284,456-355,570."""
        density = compute_per_capita_density(FAIRFAX_QUALIFYING_PARKING_ACRES, FAIRFAX_POPULATION_2025)
        result = run_prince_william_parking_estimate(density, "Fairfax")
        self.assertAlmostEqual(result.mw_low, 162.4, delta=1)
        self.assertAlmostEqual(result.mw_high, 203.0, delta=1)
        self.assertAlmostEqual(result.annual_mwh_low, 284_456, delta=1000)
        self.assertAlmostEqual(result.annual_mwh_high, 355_570, delta=1000)

    def test_returns_correct_type(self):
        result = run_prince_william_parking_estimate(0.01, "Test")
        self.assertIsInstance(result, PrinceWilliamParkingEstimate)

    def test_loudoun_anchor_gives_larger_result_than_fairfax_anchor(self):
        """Direct sanity check that the two anchors produce genuinely
        different results in the expected direction, given Loudoun's
        real density is ~10.7x Fairfax's own."""
        loudoun_density = compute_per_capita_density(LOUDOUN_QUALIFYING_PARKING_ACRES, LOUDOUN_POPULATION_2025)
        fairfax_density = compute_per_capita_density(FAIRFAX_QUALIFYING_PARKING_ACRES, FAIRFAX_POPULATION_2025)
        loudoun_result = run_prince_william_parking_estimate(loudoun_density, "Loudoun")
        fairfax_result = run_prince_william_parking_estimate(fairfax_density, "Fairfax")
        self.assertGreater(loudoun_result.mw_low, fairfax_result.mw_high)


if __name__ == "__main__":
    unittest.main(verbosity=2)
