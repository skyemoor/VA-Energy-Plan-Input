import unittest

import pandas as pd

from arlington_ci_rooftop_solar_estimate import (
    DIRECTLY_INCLUDED_CM_TYPES,
    MIN_VIABLE_ROOFTOP_SQFT,
    RESIDENTIAL_CM_TYPE,
    RESIDENTIAL_TO_COMMERCIAL_SQFT_THRESHOLD,
    ArlingtonCiRooftopSolarEstimate,
    build_ci_eligible_population,
    build_school_education_population,
    estimate_arlington_ci_rooftop_solar,
    estimate_arlington_school_rooftop_solar,
)

PROJECT_CSV_PATH = "/mnt/project/Arlington_Buildings.csv"


class TestBuildCiEligiblePopulation(unittest.TestCase):

    def _make_df(self, rows):
        return pd.DataFrame(rows)

    def test_directly_included_types_pass_regardless_of_size(self):
        df = self._make_df([
            {"CM_Type": "Commercial / Retail", "SHAPE_Area": 5000.0},
            {"CM_Type": "Medical", "SHAPE_Area": 800.0},
            {"CM_Type": "Hotel", "SHAPE_Area": 700.0},
        ])
        result = build_ci_eligible_population(df)
        self.assertEqual(len(result), 3)

    def test_directly_included_type_below_600_sqft_is_excluded(self):
        """Confirms the >=600 sqft floor genuinely applies to the
        directly-included categories too, not just the size-heuristic
        residential rows."""
        df = self._make_df([
            {"CM_Type": "Commercial / Retail", "SHAPE_Area": 500.0},  # below 600
            {"CM_Type": "Commercial / Retail", "SHAPE_Area": 600.0},  # exactly at threshold
        ])
        result = build_ci_eligible_population(df)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["SHAPE_Area"], 600.0)

    def test_residential_over_threshold_included(self):
        df = self._make_df([
            {"CM_Type": RESIDENTIAL_CM_TYPE, "SHAPE_Area": 2001.0},  # just over
            {"CM_Type": RESIDENTIAL_CM_TYPE, "SHAPE_Area": 2000.0},  # exactly at (not included, "over")
            {"CM_Type": RESIDENTIAL_CM_TYPE, "SHAPE_Area": 1999.0},  # just under
        ])
        result = build_ci_eligible_population(df)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["SHAPE_Area"], 2001.0)

    def test_excluded_types_never_included_regardless_of_size(self):
        df = self._make_df([
            {"CM_Type": "Religious", "SHAPE_Area": 50000.0},
            {"CM_Type": "Government / Military", "SHAPE_Area": 50000.0},
            {"CM_Type": "Education", "SHAPE_Area": 50000.0},
            {"CM_Type": "Community Center", "SHAPE_Area": 50000.0},
            {"CM_Type": "Transportation", "SHAPE_Area": 50000.0},
            {"CM_Type": "Recreation", "SHAPE_Area": 50000.0},
            {"CM_Type": "Airport", "SHAPE_Area": 50000.0},
        ])
        result = build_ci_eligible_population(df)
        self.assertEqual(len(result), 0)

    def test_hand_computed_mixed_case(self):
        df = self._make_df([
            {"CM_Type": "Commercial / Retail", "SHAPE_Area": 3000.0},  # in: directly included
            {"CM_Type": "Religious", "SHAPE_Area": 10000.0},           # out: excluded type
            {"CM_Type": RESIDENTIAL_CM_TYPE, "SHAPE_Area": 2500.0},    # in: over threshold
            {"CM_Type": RESIDENTIAL_CM_TYPE, "SHAPE_Area": 500.0},     # out: under threshold
            {"CM_Type": "Hotel", "SHAPE_Area": 400.0},                 # out: under 600 floor
        ])
        result = build_ci_eligible_population(df)
        self.assertEqual(len(result), 2)
        self.assertAlmostEqual(result["SHAPE_Area"].sum(), 5500.0, places=2)


class TestEstimateArlingtonCiRooftopSolar(unittest.TestCase):

    def test_hand_computed_simple_case(self):
        """2 buildings, total footprint 10,000 sqft. Uses the real NVRC
        density (mean=0.006792, median=0.006661 kW/sqft, same as
        Fairfax's own hand-verified baseline) -- so
        total_mw_mean = 10,000 * 0.006792 / 1000 = 0.06792 MW."""
        df = pd.DataFrame([
            {"CM_Type": "Commercial / Retail", "SHAPE_Area": 6000.0},
            {"CM_Type": "General / Residential", "SHAPE_Area": 4000.0},
        ])
        result = estimate_arlington_ci_rooftop_solar(df)
        self.assertEqual(result.n_buildings, 2)
        self.assertAlmostEqual(result.total_footprint_sqft, 10_000.0, places=2)
        self.assertAlmostEqual(result.total_mw_mean_based, 0.06792, places=5)
        self.assertAlmostEqual(result.density_stats.mean_kw_per_sqft, 0.006792, places=6)

    def test_no_combined_field_exists(self):
        df = pd.DataFrame([{"CM_Type": "Commercial / Retail", "SHAPE_Area": 6000.0}])
        result = estimate_arlington_ci_rooftop_solar(df)
        self.assertFalse(hasattr(result, "total_mw_combined"))
        self.assertFalse(hasattr(result, "total_mwh_per_year_combined"))

    def test_returns_correct_type(self):
        df = pd.DataFrame([{"CM_Type": "Commercial / Retail", "SHAPE_Area": 6000.0}])
        self.assertIsInstance(estimate_arlington_ci_rooftop_solar(df), ArlingtonCiRooftopSolarEstimate)

    def test_empty_eligible_population_gives_zero(self):
        df = pd.DataFrame([{"CM_Type": "Religious", "SHAPE_Area": 50000.0}])
        result = estimate_arlington_ci_rooftop_solar(df)
        self.assertEqual(result.n_buildings, 0)
        self.assertEqual(result.total_mw_mean_based, 0.0)


class TestRealDataCrossCheck(unittest.TestCase):
    """Cross-checks against the figures hand-verified directly in chat
    before writing this test: 164 Commercial/Retail + 15 Medical + 8
    Hotel directly included; 9,956 of 48,517 General/Residential rows
    clear the >2,000 sqft heuristic; 0 duplicated GIS_IDs within the
    eligible set (no dedup needed)."""

    def test_real_data_population_matches_hand_verified_figures(self):
        df = pd.read_csv(PROJECT_CSV_PATH)
        eligible = build_ci_eligible_population(df)

        commercial_count = len(df[df["CM_Type"] == "Commercial / Retail"])
        medical_count = len(df[df["CM_Type"] == "Medical"])
        hotel_count = len(df[df["CM_Type"] == "Hotel"])
        self.assertEqual(commercial_count, 164)
        self.assertEqual(medical_count, 15)
        self.assertEqual(hotel_count, 8)

        resi_over_threshold = df[
            (df["CM_Type"] == RESIDENTIAL_CM_TYPE) & (df["SHAPE_Area"] > RESIDENTIAL_TO_COMMERCIAL_SQFT_THRESHOLD)
        ]
        self.assertEqual(len(resi_over_threshold), 9_956)

        # After the >=600 sqft floor removes some of the smallest directly-included rows
        # (10 of 164 Commercial/Retail rows were confirmed < 600 sqft directly in chat)
        self.assertLess(len(eligible), commercial_count + medical_count + hotel_count + len(resi_over_threshold))

    def test_real_data_no_duplicated_gis_id_within_eligible_set(self):
        df = pd.read_csv(PROJECT_CSV_PATH)
        eligible = build_ci_eligible_population(df)
        # GIS_ID isn't used by build_ci_eligible_population itself, but confirming this
        # property holds on the real, current data locks in why no dedup step was added.
        gis_id_counts = eligible["GIS_ID"].value_counts()
        self.assertEqual((gis_id_counts > 1).sum(), 0)

    def test_real_data_full_estimate_runs_and_is_sensible(self):
        df = pd.read_csv(PROJECT_CSV_PATH)
        result = estimate_arlington_ci_rooftop_solar(df)
        self.assertGreater(result.n_buildings, 0)
        self.assertGreater(result.total_mw_mean_based, 0)
        self.assertGreater(result.total_mwh_per_year_mean_based, 0)


class TestBuildSchoolEducationPopulation(unittest.TestCase):

    def test_only_education_type_included(self):
        df = pd.DataFrame([
            {"CM_Type": "Education", "SHAPE_Area": 50000.0},
            {"CM_Type": "Commercial / Retail", "SHAPE_Area": 5000.0},
            {"CM_Type": "General / Residential", "SHAPE_Area": 3000.0},
        ])
        result = build_school_education_population(df)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]["SHAPE_Area"], 50000.0)

    def test_no_size_floor_applied(self):
        """Unlike build_ci_eligible_population, this has no >=600 sqft
        floor -- every Education-tagged row passes through regardless of
        size, per direct user instruction (no per-type categorization,
        just a straight aggregate of the real, identified population)."""
        df = pd.DataFrame([{"CM_Type": "Education", "SHAPE_Area": 100.0}])
        result = build_school_education_population(df)
        self.assertEqual(len(result), 1)


class TestEstimateArlingtonSchoolRooftopSolar(unittest.TestCase):

    def test_hand_computed_simple_case(self):
        """2 education buildings, total footprint 10,000 sqft -- same
        real NVRC density as the C&I estimate's own hand-verified case,
        confirming this reuses the identical rate, not a re-derived one.
        total_mw_mean = 10,000 * 0.006792 / 1000 = 0.06792 MW."""
        df = pd.DataFrame([
            {"CM_Type": "Education", "SHAPE_Area": 6000.0},
            {"CM_Type": "Education", "SHAPE_Area": 4000.0},
        ])
        result = estimate_arlington_school_rooftop_solar(df)
        self.assertEqual(result.n_buildings, 2)
        self.assertAlmostEqual(result.total_footprint_sqft, 10_000.0, places=2)
        self.assertAlmostEqual(result.total_mw_mean_based, 0.06792, places=5)

    def test_non_education_rows_excluded_regardless_of_size(self):
        df = pd.DataFrame([
            {"CM_Type": "Education", "SHAPE_Area": 6000.0},
            {"CM_Type": "Commercial / Retail", "SHAPE_Area": 500000.0},  # huge, but not Education
        ])
        result = estimate_arlington_school_rooftop_solar(df)
        self.assertEqual(result.n_buildings, 1)
        self.assertAlmostEqual(result.total_footprint_sqft, 6000.0, places=2)


class TestRealDataSchoolCrossCheck(unittest.TestCase):
    """Cross-checks against the real, hand-verified figures from chat:
    44 CM_Type='Education' rows total (the same population already
    explored when the HS/MS/ES breakdown was computed the prior turn)."""

    def test_real_data_school_population_count(self):
        df = pd.read_csv(PROJECT_CSV_PATH)
        eligible = build_school_education_population(df)
        self.assertEqual(len(eligible), 44)

    def test_real_data_school_estimate_runs_and_is_sensible(self):
        df = pd.read_csv(PROJECT_CSV_PATH)
        result = estimate_arlington_school_rooftop_solar(df)
        self.assertEqual(result.n_buildings, 44)
        self.assertGreater(result.total_mw_mean_based, 0)
        self.assertGreater(result.total_mwh_per_year_mean_based, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
