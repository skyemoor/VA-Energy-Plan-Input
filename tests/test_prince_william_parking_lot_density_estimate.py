import unittest

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
