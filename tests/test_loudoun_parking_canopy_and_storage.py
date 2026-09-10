"""
test_loudoun_parking_canopy_and_storage.py

Tests loudoun_parking_canopy_and_storage.py: hand-verifiable unit tests on known inputs, an
integration test against the real uploaded file, and a dedicated test locking in the key
conceptual correction (battery footprint must never reduce solar MW/MWh).
"""
import unittest

from loudoun_parking_canopy_and_storage import (
    BatteryStorageDesign,
    CountyParkingData,
    ParkingCanopyAssessment,
    SolarCanopyDesign,
)

REAL_FILE_PATH = "/mnt/project/Loudoun_Road_Casing_type_2.xlsx"
REAL_FAIRFAX_FILE_PATH = "/mnt/project/FairfaxCounty_Driveways_and_Parking_Lots_387463314629760591.csv"
REAL_ARLINGTON_FILE_PATH = "/mnt/project/Arlington_Pave_Parking_Lot_Polygons.csv"


class TestCountyParkingDataFromRoadCasingExtract(unittest.TestCase):
    """Confirms this picks up the size-filtered-only total specifically --
    getting the wrong field from ParkingLotTotals would silently use the
    wrong base number for everything downstream."""

    def test_real_file_uses_size_filtered_total_not_unfiltered_or_paved(self):
        data = CountyParkingData.from_road_casing_extract(REAL_FILE_PATH, county_name="Loudoun")
        # Baseline figure from loudoun_parking_lot_sqft.py's own real-file test:
        # min_size_filtered_sqft = 232,679,056 (>=6,000 sqft filter, n=3,500) --
        # NOT the unfiltered total (246,091,777) or the paved-only total (209,692,142).
        self.assertAlmostEqual(data.filtered_parking_sqft, 232_679_056, delta=1)
        self.assertEqual(data.county_name, "Loudoun")


class TestCountyParkingDataFromFairfaxParkingExtract(unittest.TestCase):
    """Mirrors the Loudoun test above -- confirms the new, second-county
    classmethod (added to satisfy this class's own documented extension
    pattern: 'a second county needs only its own CountyParkingData-
    producing classmethod') picks up the correct, already-established
    size-filtered total from the real Fairfax file."""

    def test_real_file_uses_size_filtered_total(self):
        data = CountyParkingData.from_fairfax_parking_extract(REAL_FAIRFAX_FILE_PATH)
        # Baseline figure established directly in chat, cross-checked against
        # fairfax_parking_lot_sqft.py's own real-data test:
        # min_size_filtered_sqft = 56,551,120 (>=6,000 sqft filter, n=2,810).
        self.assertAlmostEqual(data.filtered_parking_sqft, 56_551_120, delta=1)
        self.assertEqual(data.county_name, "Fairfax")

    def test_engineering_classes_are_genuinely_unchanged_for_a_second_county(self):
        """The real point of this module's own design: running a full
        assessment for Fairfax must require ONLY the new classmethod --
        SolarCanopyDesign, BatteryStorageDesign, and ParkingCanopyAssessment
        themselves must not need any Fairfax-specific code path. Confirmed
        by running a full, real assessment and checking it produces a
        sensible, non-degenerate result using the exact same classes
        Loudoun's own tests already exercise."""
        data = CountyParkingData.from_fairfax_parking_extract(REAL_FAIRFAX_FILE_PATH)
        result = ParkingCanopyAssessment(county_data=data).run()
        self.assertGreater(result.mw_low, 0)
        self.assertGreater(result.mw_high, result.mw_low)
        self.assertEqual(result.county_name, "Fairfax")


class TestCountyParkingDataFromArlingtonParkingExtract(unittest.TestCase):
    """Third county to use this class's own documented extension
    pattern. Mirrors the Loudoun and Fairfax tests above."""

    def test_real_file_uses_size_filtered_total(self):
        data = CountyParkingData.from_arlington_parking_extract(REAL_ARLINGTON_FILE_PATH)
        # Baseline established directly in chat, cross-checked against
        # arlington_parking_lot_sqft.py's own real-data test:
        # min_size_filtered_sqft = 44,057,781 (>=6,000 sqft filter, n=1,428).
        self.assertAlmostEqual(data.filtered_parking_sqft, 44_057_781, delta=1)
        self.assertEqual(data.county_name, "Arlington")

    def test_engineering_classes_are_genuinely_unchanged_for_a_third_county(self):
        data = CountyParkingData.from_arlington_parking_extract(REAL_ARLINGTON_FILE_PATH)
        result = ParkingCanopyAssessment(county_data=data).run()
        self.assertGreater(result.mw_low, 0)
        self.assertGreater(result.mw_high, result.mw_low)
        self.assertEqual(result.county_name, "Arlington")


class TestSolarCanopyDesign(unittest.TestCase):

    def test_compute_mw_with_hand_verified_input(self):
        design = SolarCanopyDesign()  # defaults: 2.0-2.5 kW/space, 300 sqft/space
        # 300,000 sqft / 300 sqft-per-space = 1,000 implied spaces
        mw_low, mw_high = design.compute_mw(300_000)
        self.assertAlmostEqual(mw_low, 2.0, places=6)   # 1,000 spaces x 2.0 kW / 1,000 = 2.0 MW
        self.assertAlmostEqual(mw_high, 2.5, places=6)  # 1,000 spaces x 2.5 kW / 1,000 = 2.5 MW

    def test_custom_density_is_a_real_override_not_ignored(self):
        design = SolarCanopyDesign(kw_per_space_low=1.0, kw_per_space_high=1.0)
        mw_low, mw_high = design.compute_mw(300_000)
        self.assertAlmostEqual(mw_low, 1.0, places=6)
        self.assertAlmostEqual(mw_high, 1.0, places=6)


class TestBatteryStorageDesign(unittest.TestCase):

    def test_compute_storage_with_hand_verified_input(self):
        design = BatteryStorageDesign()  # defaults: 4 hrs, 600 sqft/MWh, 25 sqft/MWh equipment
        result = design.compute_storage(solar_mw=2.0, sqft_per_space=300)
        self.assertAlmostEqual(result.mwh, 8.0, places=6)                 # 2.0 MW x 4 hrs
        self.assertAlmostEqual(result.footprint_sqft, 4_800, places=6)    # 8.0 MWh x 600 sqft/MWh
        self.assertAlmostEqual(result.equipment_only_sqft, 200, places=6)  # 8.0 MWh x 25 sqft/MWh
        self.assertAlmostEqual(result.spaces_displaced, 16.0, places=6)   # 4,800 / 300

    def test_duration_hours_is_an_overridable_instance_field_not_a_constant(self):
        """Direct test of this round's specific correction: duration_hours
        must be a live, per-instance dataclass field, not a fixed module
        constant -- two differently-configured instances must produce
        genuinely different, independently-correct results."""
        design_4hr = BatteryStorageDesign(duration_hours=4.0)
        design_8hr = BatteryStorageDesign(duration_hours=8.0)
        result_4hr = design_4hr.compute_storage(solar_mw=2.0, sqft_per_space=300)
        result_8hr = design_8hr.compute_storage(solar_mw=2.0, sqft_per_space=300)
        self.assertAlmostEqual(result_4hr.mwh, 8.0, places=6)
        self.assertAlmostEqual(result_8hr.mwh, 16.0, places=6)
        self.assertNotEqual(result_4hr.mwh, result_8hr.mwh)
        # Confirms the default itself is really 4.0, not something else
        self.assertEqual(BatteryStorageDesign().duration_hours, 4.0)


class TestBatteryFootprintNeverReducesSolarCalculation(unittest.TestCase):
    """Locks in the key conceptual correction directly, per the user: the
    canopy spans the full parking-lot footprint regardless of what sits
    underneath any given section of it, so battery siting must NEVER
    subtract from solar MW/MWh -- only from the separate, owner-facing
    'spaces displaced' figure."""

    def test_mw_is_identical_regardless_of_storage_design_parameters(self):
        county_data = CountyParkingData(
            county_name="Test County", filtered_parking_sqft=300_000,
            source_description="synthetic test data",
        )
        solar_design = SolarCanopyDesign()

        assessment_small_battery = ParkingCanopyAssessment(
            county_data=county_data, solar_design=solar_design,
            storage_design=BatteryStorageDesign(sqft_per_mwh=1),  # tiny footprint
        )
        assessment_huge_battery = ParkingCanopyAssessment(
            county_data=county_data, solar_design=solar_design,
            storage_design=BatteryStorageDesign(sqft_per_mwh=1_000_000),  # enormous footprint
        )

        result_small = assessment_small_battery.run()
        result_huge = assessment_huge_battery.run()

        # Solar MW must be identical either way -- battery footprint size
        # must have zero effect on the energy-generation numbers.
        self.assertEqual(result_small.mw_low, result_huge.mw_low)
        self.assertEqual(result_small.mw_high, result_huge.mw_high)
        self.assertEqual(result_small.parking_sqft, result_huge.parking_sqft)

        # But the owner-facing spaces-displaced figure SHOULD differ a lot --
        # confirming the battery parameters aren't simply being ignored
        # entirely, just correctly kept out of the solar calculation.
        self.assertLess(
            result_small.storage_low.spaces_displaced,
            result_huge.storage_low.spaces_displaced,
        )

    def test_solar_canopy_design_compute_mw_has_no_storage_parameter_at_all(self):
        """Structural confirmation, not just behavioral: compute_mw's own
        signature takes only parking_sqft, so there is no parameter through
        which storage data could ever be threaded in, accidentally or
        otherwise."""
        import inspect
        sig = inspect.signature(SolarCanopyDesign.compute_mw)
        param_names = list(sig.parameters.keys())
        self.assertEqual(param_names, ["self", "parking_sqft"])


class TestParkingCanopyAssessmentEndToEnd(unittest.TestCase):

    def test_full_run_with_known_inputs(self):
        county_data = CountyParkingData(
            county_name="Test County", filtered_parking_sqft=300_000,
            source_description="synthetic test data",
        )
        assessment = ParkingCanopyAssessment(county_data=county_data)
        result = assessment.run()

        self.assertEqual(result.county_name, "Test County")
        self.assertAlmostEqual(result.mw_low, 2.0, places=6)
        self.assertAlmostEqual(result.mw_high, 2.5, places=6)
        self.assertAlmostEqual(result.storage_low.mwh, 8.0, places=6)    # 2.0 MW x 4 hrs
        self.assertAlmostEqual(result.storage_high.mwh, 10.0, places=6)  # 2.5 MW x 4 hrs

    def test_defaults_are_used_when_designs_not_provided(self):
        """Confirms __post_init__ correctly supplies default designs
        rather than leaving them as None (which would crash .run())."""
        county_data = CountyParkingData(
            county_name="Test County", filtered_parking_sqft=300_000,
            source_description="synthetic test data",
        )
        assessment = ParkingCanopyAssessment(county_data=county_data)
        self.assertIsInstance(assessment.solar_design, SolarCanopyDesign)
        self.assertIsInstance(assessment.storage_design, BatteryStorageDesign)

    def test_real_loudoun_file_end_to_end(self):
        """Integration test against the actual uploaded file, cross-
        checking the real, final headline figures."""
        county_data = CountyParkingData.from_road_casing_extract(REAL_FILE_PATH, county_name="Loudoun")
        assessment = ParkingCanopyAssessment(county_data=county_data)
        result = assessment.run()

        # 232,679,056 sqft / 300 sqft-per-space = 775,596.85 implied spaces
        implied_spaces = 232_679_056 / 300
        expected_mw_low = implied_spaces * 2.0 / 1_000
        expected_mw_high = implied_spaces * 2.5 / 1_000
        self.assertAlmostEqual(result.mw_low, expected_mw_low, delta=0.1)
        self.assertAlmostEqual(result.mw_high, expected_mw_high, delta=0.1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
