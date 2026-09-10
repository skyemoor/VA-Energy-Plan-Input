"""
test_loudoun_battery_dispatch.py

Tests loudoun_battery_dispatch.py: hand-verifiable unit tests for the core charge/discharge
logic, direct tests of each Rule 9 physical invariant (including deliberately constructing
violating DispatchResult instances to confirm the checks themselves catch what they claim to),
and an integration test against real data for one of the 5 identified low-output windows.
"""
import unittest

import pandas as pd

from loudoun_battery_dispatch import (
    DEFAULT_BUILDOUT_STARTING_SOC_PCT,
    DEFAULT_ROUND_TRIP_EFFICIENCY_PCT,
    LOUDOUN_LOAD_ANCHOR_MW,
    LOUDOUN_LOAD_ANCHOR_YEAR,
    LOUDOUN_LOAD_ANNUAL_GROWTH_RATE,
    BatteryDispatchDesign,
    DispatchResult,
    IncrementalBuildoutDispatchResult,
    WorstCaseAcrossCandidateYearsResult,
    compute_anchored_compound_growth_schedule,
    compute_linear_buildout_schedule,
    extract_hydro_year_window,
)
from loudoun_load_shape_gap_analysis import LoadProfile
from loudoun_solar_hourly_profile import SolarSiteProfile

PROJECT_DIR = "/mnt/project"
DOMLSE_PATH = f"{PROJECT_DIR}/DOMLSEHourlyLoadProjections2024through2048.csv"


class TestDispatchOneHourStaticMethod(unittest.TestCase):
    """Direct, isolated tests of the pure per-hour helper extracted this
    round -- the real benefit of the extraction (Rule 2): these no longer
    need a full LoadProfile/ScaledSolarProfile/window setup to verify,
    just a plain tuple of already-resolved inputs."""

    def test_excess_charges_battery(self):
        charge, discharge, curtailment, residual, new_soc = BatteryDispatchDesign._dispatch_one_hour(
            solar_mw=80.0, load_mw=50.0, current_soc=0.0,
            energy_capacity=100.0, power_mw=100.0, rte_fraction=1.0,
        )
        self.assertAlmostEqual(charge, 30.0, places=6)
        self.assertAlmostEqual(discharge, 0.0, places=6)
        self.assertAlmostEqual(curtailment, 0.0, places=6)
        self.assertAlmostEqual(residual, 0.0, places=6)
        self.assertAlmostEqual(new_soc, 30.0, places=6)

    def test_deficit_discharges_battery(self):
        charge, discharge, curtailment, residual, new_soc = BatteryDispatchDesign._dispatch_one_hour(
            solar_mw=20.0, load_mw=80.0, current_soc=100.0,
            energy_capacity=100.0, power_mw=100.0, rte_fraction=0.9,
        )
        self.assertAlmostEqual(discharge, 60.0, places=6)
        self.assertAlmostEqual(charge, 0.0, places=6)
        self.assertAlmostEqual(residual, 0.0, places=6)
        self.assertAlmostEqual(new_soc, 40.0, places=6)

    def test_takes_power_mw_as_an_explicit_parameter_not_self(self):
        """Direct confirmation this is genuinely usable with a DIFFERENT
        power_mw than any particular design instance's own field --
        exactly the property the incremental-buildout use case needs
        (varying power_mw per build-out year without needing a different
        design instance each time)."""
        result_small = BatteryDispatchDesign._dispatch_one_hour(
            solar_mw=0.0, load_mw=100.0, current_soc=100.0,
            energy_capacity=100.0, power_mw=10.0, rte_fraction=1.0,
        )
        result_large = BatteryDispatchDesign._dispatch_one_hour(
            solar_mw=0.0, load_mw=100.0, current_soc=100.0,
            energy_capacity=100.0, power_mw=100.0, rte_fraction=1.0,
        )
        self.assertAlmostEqual(result_small[1], 10.0, places=6)   # discharge, power-limited
        self.assertAlmostEqual(result_large[1], 100.0, places=6)  # discharge, not power-limited


class TestComputeLinearBuildoutSchedule(unittest.TestCase):

    def test_hand_verified_schedule(self):
        schedule = compute_linear_buildout_schedule(start_year=2026, end_year=2045, end_fleet_mw=2_908.4)
        self.assertAlmostEqual(schedule[2026], 0.0, places=6)
        self.assertAlmostEqual(schedule[2045], 2_908.4, places=6)
        # Midpoint check: 2035 is 9 years into a 19-year span -> 9/19 of the way there
        expected_2035 = 2_908.4 * 9 / 19
        self.assertAlmostEqual(schedule[2035], expected_2035, places=6)

    def test_covers_every_year_inclusive(self):
        schedule = compute_linear_buildout_schedule(start_year=2026, end_year=2045, end_fleet_mw=100.0)
        self.assertEqual(sorted(schedule.keys()), list(range(2026, 2046)))
        self.assertEqual(len(schedule), 20)  # 2026 through 2045 inclusive = 20 years

    def test_nonzero_start_fleet_mw(self):
        schedule = compute_linear_buildout_schedule(
            start_year=2026, end_year=2027, end_fleet_mw=100.0, start_fleet_mw=20.0
        )
        self.assertAlmostEqual(schedule[2026], 20.0, places=6)
        self.assertAlmostEqual(schedule[2027], 100.0, places=6)

    def test_end_year_before_start_year_raises(self):
        with self.assertRaises(ValueError):
            compute_linear_buildout_schedule(start_year=2045, end_year=2026, end_fleet_mw=100.0)

    def test_end_year_equal_start_year_raises(self):
        with self.assertRaises(ValueError):
            compute_linear_buildout_schedule(start_year=2026, end_year=2026, end_fleet_mw=100.0)

    def test_default_buildout_starting_soc_matches_established_user_decision(self):
        self.assertEqual(DEFAULT_BUILDOUT_STARTING_SOC_PCT, 50.0)


class TestComputeAnchoredCompoundGrowthSchedule(unittest.TestCase):

    def test_anchor_year_returns_anchor_value_exactly(self):
        schedule = compute_anchored_compound_growth_schedule(
            start_year=2026, end_year=2045, anchor_year=2028, anchor_value=11_560.0,
            annual_growth_rate=0.041,
        )
        self.assertAlmostEqual(schedule[2028], 11_560.0, places=6)

    def test_forward_and_backward_compounding_hand_verified(self):
        schedule = compute_anchored_compound_growth_schedule(
            start_year=2026, end_year=2030, anchor_year=2028, anchor_value=100.0,
            annual_growth_rate=0.10,
        )
        self.assertAlmostEqual(schedule[2029], 110.0, places=6)          # 100 * 1.10^1
        self.assertAlmostEqual(schedule[2030], 121.0, places=6)          # 100 * 1.10^2
        self.assertAlmostEqual(schedule[2027], 100.0 / 1.10, places=6)   # 100 / 1.10^1
        self.assertAlmostEqual(schedule[2026], 100.0 / 1.10**2, places=6)  # 100 / 1.10^2

    def test_matches_the_independently_logged_loudoun_values(self):
        """Cross-check against the exact values already hand-computed and
        logged in Data_Sourcing_Log.md before this function existed."""
        schedule = compute_anchored_compound_growth_schedule(
            start_year=2026, end_year=2045, anchor_year=LOUDOUN_LOAD_ANCHOR_YEAR,
            anchor_value=LOUDOUN_LOAD_ANCHOR_MW, annual_growth_rate=LOUDOUN_LOAD_ANNUAL_GROWTH_RATE,
        )
        self.assertAlmostEqual(schedule[2026] / 1000, 10.67, places=2)
        self.assertAlmostEqual(schedule[2027] / 1000, 11.10, places=2)
        self.assertAlmostEqual(schedule[2028] / 1000, 11.56, places=2)
        self.assertAlmostEqual(schedule[2045] / 1000, 22.89, places=2)

    def test_anchor_year_outside_range_is_allowed(self):
        """anchor_year need not fall inside [start_year, end_year] --
        confirms this isn't accidentally required."""
        schedule = compute_anchored_compound_growth_schedule(
            start_year=2030, end_year=2035, anchor_year=2000, anchor_value=1.0,
            annual_growth_rate=0.05,
        )
        self.assertEqual(len(schedule), 6)

    def test_end_year_before_start_year_raises(self):
        with self.assertRaises(ValueError):
            compute_anchored_compound_growth_schedule(
                start_year=2045, end_year=2026, anchor_year=2028, anchor_value=100.0,
                annual_growth_rate=0.041,
            )

    def test_loudoun_constants_match_documented_provenance(self):
        self.assertEqual(LOUDOUN_LOAD_ANCHOR_YEAR, 2028)
        self.assertEqual(LOUDOUN_LOAD_ANCHOR_MW, 11_560.0)
        self.assertEqual(LOUDOUN_LOAD_ANNUAL_GROWTH_RATE, 0.041)


def _make_load_profile(pct_of_peak_by_ts: dict) -> LoadProfile:
    """Builds a minimal, fully-controlled synthetic LoadProfile for
    hand-verifiable dispatch tests. Sets pct_of_peak directly (0-100),
    since that's what simulate() actually reads after the scale-mismatch
    fix -- NOT a raw 'mw' value, which is what the pre-fix code read and
    is why the original version of these tests didn't catch that bug."""
    timestamps = list(pct_of_peak_by_ts.keys())
    pcts = list(pct_of_peak_by_ts.values())
    df = pd.DataFrame({"timestamp": pd.to_datetime(timestamps), "mw": pcts, "pct_of_peak": pcts})
    return LoadProfile(
        year=2045, target_load_factor_pct=90.0, raw_hourly=df,
        solved_floor_pct=0.9, adjusted_hourly=df, peak_mw=100.0,
    )


def _make_scaled_solar(mw_by_ts: dict, fleet_mw: float):
    """fleet_mw is now an explicit, independent parameter (rather than
    derived from max(values)) specifically so tests can control 'solar
    output at this hour' and 'the fleet's own MW capacity' separately --
    needed to construct valid test cases where load_mw (bounded by
    fleet_mw, per the new Rule 9 invariant) and solar_mw at a given hour
    are set to different, independently-chosen values."""
    timestamps = list(mw_by_ts.keys())
    mws = list(mw_by_ts.values())
    hourly = pd.DataFrame({"timestamp": pd.to_datetime(timestamps), "mw": mws})
    from loudoun_solar_hourly_profile import ScaledSolarProfile
    return ScaledSolarProfile(source_site_name="test", fleet_mw=fleet_mw, nameplate_kw=100, hourly=hourly)


class TestBatteryDispatchDesign(unittest.TestCase):

    def test_energy_capacity_hand_verified(self):
        design = BatteryDispatchDesign(power_mw=10.0, duration_hours=4.0)
        self.assertEqual(design.energy_capacity_mwh, 40.0)

    def test_default_rte_matches_established_assumption(self):
        self.assertEqual(DEFAULT_ROUND_TRIP_EFFICIENCY_PCT, 90.0)


class TestSimulateCoreDispatchLogic(unittest.TestCase):

    def test_excess_solar_charges_battery(self):
        # fleet_mw=100; load_pct=50 -> load_mw=50; solar_mw=80 -> excess=30
        ts = pd.Timestamp("2018-02-23 00:00")
        load = _make_load_profile({ts: 50.0})
        solar = _make_scaled_solar({ts: 80.0}, fleet_mw=100.0)
        design = BatteryDispatchDesign(power_mw=100.0, duration_hours=1.0, round_trip_efficiency_pct=100.0, starting_soc_pct=0.0)
        result = design.simulate(load, solar, start=ts, end=ts)
        row = result.hourly.iloc[0]
        self.assertAlmostEqual(row["load_mw"], 50.0, places=6)
        self.assertAlmostEqual(row["charge_mw"], 30.0, places=6)
        self.assertAlmostEqual(row["discharge_mw"], 0.0, places=6)
        self.assertAlmostEqual(row["soc_mwh"], 30.0, places=6)  # 100% RTE -> full 30 stored
        self.assertAlmostEqual(row["residual_import_mw"], 0.0, places=6)
        self.assertAlmostEqual(row["curtailment_mw"], 0.0, places=6)  # battery absorbed all excess

    def test_deficit_discharges_battery(self):
        # fleet_mw=100; load_pct=80 -> load_mw=80; solar_mw=20 -> deficit=60
        ts = pd.Timestamp("2018-02-23 00:00")
        load = _make_load_profile({ts: 80.0})
        solar = _make_scaled_solar({ts: 20.0}, fleet_mw=100.0)
        design = BatteryDispatchDesign(power_mw=100.0, duration_hours=1.0, round_trip_efficiency_pct=90.0, starting_soc_pct=100.0)
        result = design.simulate(load, solar, start=ts, end=ts)
        row = result.hourly.iloc[0]
        self.assertAlmostEqual(row["load_mw"], 80.0, places=6)
        # deficit=60, power=100, soc starts at 100 MWh (100% of 100 MW x 1hr capacity) -> full 60 covered
        self.assertAlmostEqual(row["discharge_mw"], 60.0, places=6)
        self.assertAlmostEqual(row["charge_mw"], 0.0, places=6)
        self.assertAlmostEqual(row["residual_import_mw"], 0.0, places=6)
        self.assertAlmostEqual(row["soc_mwh"], 40.0, places=6)  # 100 - 60
        self.assertAlmostEqual(row["curtailment_mw"], 0.0, places=6)  # no excess solar this hour

    def test_deficit_exceeding_battery_ability_leaves_residual_import(self):
        # fleet_mw=100; load_pct=100 -> load_mw=100; solar_mw=0 -> deficit=100
        ts = pd.Timestamp("2018-02-23 00:00")
        load = _make_load_profile({ts: 100.0})
        solar = _make_scaled_solar({ts: 0.0}, fleet_mw=100.0)
        # power=10, duration=1hr -> only 10 MWh available -- far short of the 100 MW deficit
        design = BatteryDispatchDesign(power_mw=10.0, duration_hours=1.0, starting_soc_pct=100.0)
        result = design.simulate(load, solar, start=ts, end=ts)
        row = result.hourly.iloc[0]
        self.assertAlmostEqual(row["discharge_mw"], 10.0, places=6)  # power-limited
        self.assertAlmostEqual(row["residual_import_mw"], 90.0, places=6)  # 100 - 10

    def test_charging_capped_by_headroom_not_just_power(self):
        """A battery already mostly full should not overcharge past
        capacity even if the power rating and available excess solar
        would otherwise allow more."""
        # fleet_mw=100; load_pct=0 -> load_mw=0; solar_mw=100 -> huge excess
        ts = pd.Timestamp("2018-02-23 00:00")
        load = _make_load_profile({ts: 0.0})
        solar = _make_scaled_solar({ts: 100.0}, fleet_mw=100.0)
        # capacity = 10 MW x 1hr = 10 MWh; starting at 90% = 9 MWh, only 1 MWh headroom
        design = BatteryDispatchDesign(power_mw=10.0, duration_hours=1.0, round_trip_efficiency_pct=100.0, starting_soc_pct=90.0)
        result = design.simulate(load, solar, start=ts, end=ts)
        row = result.hourly.iloc[0]
        self.assertAlmostEqual(row["soc_mwh"], 10.0, places=6)  # capped at full capacity, not overcharged
        self.assertLessEqual(row["charge_mw"], 10.0)  # also respects power rating

    def test_curtailment_when_excess_exceeds_battery_ability_to_absorb(self):
        """Direct test of curtailment: when excess solar exceeds what the
        battery can absorb (headroom-limited here), the un-absorbed
        remainder must show up as curtailment_mw, not simply vanish."""
        # fleet_mw=100; load_pct=0 -> load_mw=0; solar_mw=100 -> excess=100
        ts = pd.Timestamp("2018-02-23 00:00")
        load = _make_load_profile({ts: 0.0})
        solar = _make_scaled_solar({ts: 100.0}, fleet_mw=100.0)
        # capacity = 10 MW x 1hr = 10 MWh, starting empty -> only 10 MWh of headroom
        design = BatteryDispatchDesign(power_mw=10.0, duration_hours=1.0, round_trip_efficiency_pct=100.0, starting_soc_pct=0.0)
        result = design.simulate(load, solar, start=ts, end=ts)
        row = result.hourly.iloc[0]
        self.assertAlmostEqual(row["charge_mw"], 10.0, places=6)  # headroom-limited
        self.assertAlmostEqual(row["curtailment_mw"], 90.0, places=6)  # 100 excess - 10 absorbed

    def test_discharging_capped_by_available_soc_not_just_power(self):
        # fleet_mw=100; load_pct=100 -> load_mw=100; solar_mw=0 -> deficit=100
        ts = pd.Timestamp("2018-02-23 00:00")
        load = _make_load_profile({ts: 100.0})
        solar = _make_scaled_solar({ts: 0.0}, fleet_mw=100.0)
        # power=50 (would allow up to 50 MW discharge), but only 5 MWh actually stored
        # (10% of a 50 MW x 1hr = 50 MWh capacity)
        design = BatteryDispatchDesign(power_mw=50.0, duration_hours=1.0, starting_soc_pct=10.0)
        result = design.simulate(load, solar, start=ts, end=ts)
        row = result.hourly.iloc[0]
        self.assertAlmostEqual(row["discharge_mw"], 5.0, places=6)  # soc-limited, not power-limited
        self.assertAlmostEqual(row["soc_mwh"], 0.0, places=6)

    def test_rte_reduces_stored_energy_relative_to_grid_side_charge(self):
        # fleet_mw=100; load_pct=0 -> load_mw=0; solar_mw=50 -> excess=50
        ts = pd.Timestamp("2018-02-23 00:00")
        load = _make_load_profile({ts: 0.0})
        solar = _make_scaled_solar({ts: 50.0}, fleet_mw=100.0)
        design = BatteryDispatchDesign(power_mw=100.0, duration_hours=10.0, round_trip_efficiency_pct=80.0, starting_soc_pct=0.0)
        result = design.simulate(load, solar, start=ts, end=ts)
        row = result.hourly.iloc[0]
        self.assertAlmostEqual(row["charge_mw"], 50.0, places=6)  # full excess drawn from grid side
        self.assertAlmostEqual(row["soc_mwh"], 40.0, places=6)  # but only 80% actually stored
        self.assertAlmostEqual(row["curtailment_mw"], 0.0, places=6)  # power/headroom not limiting here

    def test_load_mw_derived_from_pct_times_fleet_mw_not_a_raw_absolute_value(self):
        """Direct test of the scale-mismatch fix itself: load_mw must
        equal load_pct_of_peak/100 * fleet_mw, and must therefore always
        stay within [0, fleet_mw] -- never independently large regardless
        of fleet_mw, which is exactly the shape of the original bug (a
        ~29,587 MW absolute load compared against a ~1,551 MW fleet)."""
        ts = pd.Timestamp("2018-02-23 00:00")
        load = _make_load_profile({ts: 37.0})  # 37% of peak
        solar = _make_scaled_solar({ts: 10.0}, fleet_mw=1_551.2)
        design = BatteryDispatchDesign(power_mw=1_551.2, duration_hours=4.0)
        result = design.simulate(load, solar, start=ts, end=ts)
        row = result.hourly.iloc[0]
        self.assertAlmostEqual(row["load_mw"], 0.37 * 1_551.2, places=4)
        self.assertLessEqual(row["load_mw"], 1_551.2)

    def test_window_with_no_solar_data_raises(self):
        ts = pd.Timestamp("2018-02-23 00:00")
        load = _make_load_profile({ts: 50.0})
        solar = _make_scaled_solar({ts: 50.0}, fleet_mw=100.0)
        design = BatteryDispatchDesign(power_mw=10.0, duration_hours=1.0)
        with self.assertRaises(ValueError):
            design.simulate(load, solar, start=pd.Timestamp("2020-01-01"), end=pd.Timestamp("2020-01-02"))


class TestPhysicalInvariants(unittest.TestCase):
    """Direct tests of each Rule 9 check, including deliberately
    constructing violating DispatchResult instances to confirm the checks
    themselves actually catch what they claim to -- not just that the real
    simulate() logic happens not to trigger them."""

    def _make_design(self):
        return BatteryDispatchDesign(power_mw=10.0, duration_hours=1.0)  # 10 MWh capacity

    def test_soc_exceeding_capacity_raises(self):
        design = self._make_design()
        hourly = pd.DataFrame({
            "timestamp": [pd.Timestamp("2018-01-01")], "load_mw": [0], "solar_mw": [0],
            "charge_mw": [0], "discharge_mw": [0], "curtailment_mw": [0],
            "soc_mwh": [11.0],  # exceeds 10 MWh capacity
            "soc_pct": [110.0], "residual_import_mw": [0],
        })
        with self.assertRaises(ValueError):
            DispatchResult(design=design, hourly=hourly, fleet_mw=100.0)

    def test_negative_soc_raises(self):
        design = self._make_design()
        hourly = pd.DataFrame({
            "timestamp": [pd.Timestamp("2018-01-01")], "load_mw": [0], "solar_mw": [0],
            "charge_mw": [0], "discharge_mw": [0], "curtailment_mw": [0],
            "soc_mwh": [-1.0],
            "soc_pct": [-10.0], "residual_import_mw": [0],
        })
        with self.assertRaises(ValueError):
            DispatchResult(design=design, hourly=hourly, fleet_mw=100.0)

    def test_simultaneous_charge_and_discharge_raises(self):
        """Direct test of the specific, previously-found bug class this
        project's own broader model history documents."""
        design = self._make_design()
        hourly = pd.DataFrame({
            "timestamp": [pd.Timestamp("2018-01-01")], "load_mw": [0], "solar_mw": [0],
            "charge_mw": [5.0], "discharge_mw": [3.0],  # both nonzero in the same hour -- invalid
            "curtailment_mw": [0],
            "soc_mwh": [5.0], "soc_pct": [50.0], "residual_import_mw": [0],
        })
        with self.assertRaises(ValueError):
            DispatchResult(design=design, hourly=hourly, fleet_mw=100.0)

    def test_load_mw_exceeding_fleet_mw_raises(self):
        """Direct test of the invariant added specifically in response to
        the scale-mismatch bug: load_mw derived from a valid [0,100]
        pct_of_peak can never legitimately exceed fleet_mw, so a
        DispatchResult claiming otherwise (e.g. the old bug's raw,
        absolute DOMLSE MW leaking through) must be rejected."""
        design = self._make_design()
        hourly = pd.DataFrame({
            "timestamp": [pd.Timestamp("2018-01-01")], "load_mw": [29_587.0],  # the old bug's shape
            "solar_mw": [10.0], "charge_mw": [0], "discharge_mw": [10.0], "curtailment_mw": [0],
            "soc_mwh": [0.0], "soc_pct": [0.0], "residual_import_mw": [29_577.0],
        })
        with self.assertRaises(ValueError):
            DispatchResult(design=design, hourly=hourly, fleet_mw=1_551.2)

    def test_negative_load_mw_raises(self):
        design = self._make_design()
        hourly = pd.DataFrame({
            "timestamp": [pd.Timestamp("2018-01-01")], "load_mw": [-5.0], "solar_mw": [10.0],
            "charge_mw": [0], "discharge_mw": [0], "curtailment_mw": [0],
            "soc_mwh": [0.0], "soc_pct": [0.0],
            "residual_import_mw": [0],
        })
        with self.assertRaises(ValueError):
            DispatchResult(design=design, hourly=hourly, fleet_mw=100.0)

    def test_negative_curtailment_raises(self):
        """Direct test of the invariant added this round: curtailment_mw
        represents un-absorbed excess solar and can never legitimately be
        negative."""
        design = self._make_design()
        hourly = pd.DataFrame({
            "timestamp": [pd.Timestamp("2018-01-01")], "load_mw": [0], "solar_mw": [10],
            "charge_mw": [10.0], "discharge_mw": [0], "curtailment_mw": [-1.0],  # invalid
            "soc_mwh": [10.0], "soc_pct": [100.0], "residual_import_mw": [0],
        })
        with self.assertRaises(ValueError):
            DispatchResult(design=design, hourly=hourly, fleet_mw=100.0)

    def test_energy_balance_violation_raises(self):
        """Direct test of the energy-balance invariant added this round:
        deliberately constructs a row where sources (solar+discharge+
        residual_import) do not equal uses (load+charge+curtailment) --
        here, solar=10 goes in but neither load, charge, nor curtailment
        account for it anywhere, so the row is not usable."""
        design = self._make_design()
        hourly = pd.DataFrame({
            "timestamp": [pd.Timestamp("2018-01-01")], "load_mw": [0], "solar_mw": [10],
            "charge_mw": [0], "discharge_mw": [0], "curtailment_mw": [0],  # the 10 MW of solar vanishes
            "soc_mwh": [0.0], "soc_pct": [0.0], "residual_import_mw": [0],
        })
        with self.assertRaises(ValueError):
            DispatchResult(design=design, hourly=hourly, fleet_mw=100.0)

    def test_valid_result_does_not_raise(self):
        """Uses 100% RTE explicitly (rather than the design default) so
        every value is round and hand-verifiable, including full
        energy-balance closure in both hours -- the real, meaningful bar
        this test now has to clear now that the energy-balance invariant
        is checked automatically. Row 1: excess solar (10) fully charges
        an empty battery. Row 2: the stored 10 MWh fully covers a 10 MW
        deficit."""
        design = BatteryDispatchDesign(power_mw=10.0, duration_hours=1.0, round_trip_efficiency_pct=100.0)
        hourly = pd.DataFrame({
            "timestamp": [pd.Timestamp("2018-01-01"), pd.Timestamp("2018-01-01 01:00")],
            "load_mw": [0, 10], "solar_mw": [10, 0],
            "charge_mw": [10.0, 0.0], "discharge_mw": [0.0, 10.0], "curtailment_mw": [0.0, 0.0],
            "soc_mwh": [10.0, 0.0], "soc_pct": [100.0, 0.0], "residual_import_mw": [0, 0],
        })
        DispatchResult(design=design, hourly=hourly, fleet_mw=100.0)  # should not raise


class TestRealDataIntegration(unittest.TestCase):
    """Integration test against real data: the Feb 2018 window (+/- 1
    week), run at both a short and a long duration, confirming the
    simulation runs end to end on real data and that a longer-duration
    battery achieves less residual import than a shorter one -- a
    meaningful, real cross-check (Rule 4), not just an internal
    self-consistency check."""

    def test_longer_duration_battery_reduces_residual_import(self):
        load_profile = LoadProfile.from_domlse_export(DOMLSE_PATH, year=2045)
        solar_profile = SolarSiteProfile.from_sam_export_yearly_files(PROJECT_DIR, site_name="Sterling")
        scaled_solar = solar_profile.scale_to_fleet_mw(fleet_mw=1_551.2)

        # Feb 2018 streak (2018-02-23 09:00 -> 2018-02-26 11:00), +/- 1 week
        start = pd.Timestamp("2018-02-16 09:00")
        end = pd.Timestamp("2018-03-05 11:00")

        design_short = BatteryDispatchDesign(power_mw=1_551.2, duration_hours=4.0)
        design_long = BatteryDispatchDesign(power_mw=1_551.2, duration_hours=100.0, round_trip_efficiency_pct=80.0)

        result_short = design_short.simulate(load_profile, scaled_solar, start, end)
        result_long = design_long.simulate(load_profile, scaled_solar, start, end)

        self.assertLess(result_long.total_residual_import_mwh, result_short.total_residual_import_mwh)

    def test_real_data_energy_balance_and_curtailment_are_sane(self):
        """Confirms the energy-balance invariant (checked automatically
        in __post_init__ on every simulate() call, including this one)
        genuinely holds on real, full-scale data, not only small
        synthetic examples -- and that curtailment on the real Feb 2018
        window is exactly zero, consistent with the already-established
        finding that solar never once exceeds load in that window."""
        load_profile = LoadProfile.from_domlse_export(DOMLSE_PATH, year=2045)
        solar_profile = SolarSiteProfile.from_sam_export_yearly_files(PROJECT_DIR, site_name="Sterling")
        scaled_solar = solar_profile.scale_to_fleet_mw(fleet_mw=1_551.2)
        design = BatteryDispatchDesign(power_mw=1_551.2, duration_hours=100.0, round_trip_efficiency_pct=80.0)

        start = pd.Timestamp("2018-02-16 09:00")
        end = pd.Timestamp("2018-03-05 11:00")
        result = design.simulate(load_profile, scaled_solar, start, end)  # would raise if imbalanced

        self.assertAlmostEqual(result.hourly["curtailment_mw"].sum(), 0.0, places=4)


class TestExtractHydroYearWindow(unittest.TestCase):

    def _make_synthetic_solar_profile(self, timestamps, mws):
        from loudoun_solar_hourly_profile import SolarSiteProfile
        hourly = pd.DataFrame({"timestamp": pd.to_datetime(timestamps), "kw": mws})
        return SolarSiteProfile(
            site_name="test", nameplate_kw=100, tilt_degrees=15, system_losses_pct=14,
            years=[2016, 2017], hourly=hourly,
        )

    def test_hand_verified_window_boundaries(self):
        timestamps = [
            "2016-03-31 23:00", "2016-04-01 00:00", "2016-06-15 12:00",
            "2017-03-31 23:00", "2017-04-01 00:00",
        ]
        profile = self._make_synthetic_solar_profile(timestamps, [1, 2, 3, 4, 5])
        windowed = extract_hydro_year_window(profile, start_year=2016)
        # Should include indices 1,2,3 (Apr 1 2016 through Mar 31 2017 23:00) and exclude
        # index 0 (before the window) and index 4 (the next window, Apr 1 2017)
        self.assertEqual(len(windowed.hourly), 3)
        self.assertEqual(windowed.hourly["kw"].tolist(), [2, 3, 4])

    def test_site_name_labeled_clearly(self):
        profile = self._make_synthetic_solar_profile(["2016-06-01 00:00"], [1])
        windowed = extract_hydro_year_window(profile, start_year=2016)
        self.assertIn("Apr2016-Mar2017", windowed.site_name)

    def test_empty_window_raises(self):
        profile = self._make_synthetic_solar_profile(["2020-06-01 00:00"], [1])
        with self.assertRaises(ValueError):
            extract_hydro_year_window(profile, start_year=2016)

    def test_real_apr2016_mar2017_window(self):
        """Real-data check: this specific window is this project's own
        already-established 'design weather year' (per the README),
        independently derived by a different part of this model."""
        solar_profile = SolarSiteProfile.from_sam_export_yearly_files(
            PROJECT_DIR, site_name="Sterling", years=[2016, 2017],
        )
        windowed = extract_hydro_year_window(solar_profile, start_year=2016)
        self.assertEqual(windowed.hourly["timestamp"].min(), pd.Timestamp("2016-04-01 00:00:00"))
        self.assertEqual(windowed.hourly["timestamp"].max(), pd.Timestamp("2017-03-31 23:00:00"))
        self.assertEqual(len(windowed.hourly), 365 * 24)  # neither 2016 nor this window includes Feb 29


class TestSimulateWithIncrementalBuildout(unittest.TestCase):

    def _make_two_hour_load_profile(self):
        # Two hours, both with load_pct=50 -- kept simple/constant so this test isolates
        # fleet-size and SoC-continuity behavior, not load-shape behavior (already covered
        # elsewhere).
        timestamps = pd.to_datetime(["2018-06-01 00:00", "2018-06-01 01:00"])
        df = pd.DataFrame({"timestamp": timestamps, "mw": [50.0, 50.0], "pct_of_peak": [50.0, 50.0]})
        return LoadProfile(
            year=2045, target_load_factor_pct=90.0, raw_hourly=df,
            solved_floor_pct=0.9, adjusted_hourly=df, peak_mw=100.0,
        )

    def _make_two_hour_weather_profile(self, solar_values):
        from loudoun_solar_hourly_profile import SolarSiteProfile
        timestamps = pd.to_datetime(["2018-06-01 00:00", "2018-06-01 01:00"])
        hourly = pd.DataFrame({"timestamp": timestamps, "kw": solar_values})
        return SolarSiteProfile(
            site_name="test", nameplate_kw=100, tilt_degrees=15, system_losses_pct=14,
            years=[2018], hourly=hourly,
        )

    def test_fleet_mw_scales_correctly_per_year(self):
        load_profile = self._make_two_hour_load_profile()
        # solar=100 (in the profile's own kW units, which scale_to_fleet_mw treats as a
        # nameplate-relative shape); load_pct=50 -> both years produce excess solar, so charge
        # dynamics don't interfere with reading fleet_mw/load_mw back out directly.
        weather = self._make_two_hour_weather_profile([100.0, 100.0])
        weather.nameplate_kw = 100  # 1:1 kW-to-fleet-scale for a simple, hand-verifiable ratio
        design = BatteryDispatchDesign(power_mw=999, duration_hours=4.0)  # power_mw unused here
        schedule = {2026: 10.0, 2027: 20.0}
        # Deliberately DIFFERENT from the fleet schedule above -- confirms load_mw is derived from
        # this independent series, not fleet_mw, per this round's real load-magnitude decoupling.
        loudoun_load_peak_mw_schedule = {2026: 200.0, 2027: 400.0}
        result = design.simulate_with_incremental_buildout(
            load_profile, weather, schedule, loudoun_load_peak_mw_schedule, weather_year_label="test-2018",
        )
        year_2026_rows = result.hourly[result.hourly["build_out_year"] == 2026]
        year_2027_rows = result.hourly[result.hourly["build_out_year"] == 2027]
        self.assertTrue((year_2026_rows["fleet_mw"] == 10.0).all())
        self.assertTrue((year_2027_rows["fleet_mw"] == 20.0).all())
        self.assertTrue((year_2026_rows["loudoun_load_peak_mw"] == 200.0).all())
        self.assertTrue((year_2027_rows["loudoun_load_peak_mw"] == 400.0).all())
        # load_mw = load_pct/100 * loudoun_load_peak_mw -> 50% of 200 = 100, 50% of 400 = 200
        self.assertAlmostEqual(year_2026_rows["load_mw"].iloc[0], 100.0, places=6)
        self.assertAlmostEqual(year_2027_rows["load_mw"].iloc[0], 200.0, places=6)

    def test_soc_carries_over_continuously_across_year_boundary_not_reset(self):
        load_profile = self._make_two_hour_load_profile()
        # Solar far below load in both hours -> battery only ever discharges, so SoC should
        # decline MONOTONICALLY across the whole 2-year run with no reset/jump at the boundary.
        weather = self._make_two_hour_weather_profile([0.0, 0.0])
        design = BatteryDispatchDesign(power_mw=999, duration_hours=100.0, round_trip_efficiency_pct=100.0)
        schedule = {2026: 10.0, 2027: 10.0}  # constant fleet size, isolates the SoC-continuity check
        loudoun_load_peak_mw_schedule = {2026: 10.0, 2027: 10.0}  # any valid schedule works here
        result = design.simulate_with_incremental_buildout(
            load_profile, weather, schedule, loudoun_load_peak_mw_schedule,
            weather_year_label="test-2018", starting_soc_pct=50.0,
        )
        soc_series = result.hourly["soc_mwh"].tolist()
        # Strictly non-increasing across all 4 hours (2 years x 2 hours), including AT the
        # year-boundary transition (index 1 -> 2) -- would show a jump back up if SoC were
        # incorrectly reset to 50% of year 2's capacity instead of carrying over.
        for i in range(1, len(soc_series)):
            self.assertLessEqual(soc_series[i], soc_series[i - 1] + 1e-9)

    def test_real_data_full_run_does_not_raise(self):
        """Full, real-data integration test: real 2018 weather year, real
        load profile, a realistic build-out schedule, AND the real,
        sourced Loudoun load-magnitude schedule (not a synthetic
        stand-in) -- confirms this runs end to end and all Rule 9
        invariants (checked automatically in __post_init__) hold on
        genuine, full-scale data."""
        load_profile = LoadProfile.from_domlse_export(DOMLSE_PATH, year=2045)
        solar_2018 = SolarSiteProfile.from_sam_export_yearly_files(
            PROJECT_DIR, site_name="Sterling", years=[2018],
        )
        design = BatteryDispatchDesign(power_mw=2_908.4, duration_hours=100.0, round_trip_efficiency_pct=80.0)
        schedule = compute_linear_buildout_schedule(start_year=2026, end_year=2045, end_fleet_mw=2_908.4)
        loudoun_load_peak_mw_schedule = compute_anchored_compound_growth_schedule(
            start_year=2026, end_year=2045, anchor_year=LOUDOUN_LOAD_ANCHOR_YEAR,
            anchor_value=LOUDOUN_LOAD_ANCHOR_MW, annual_growth_rate=LOUDOUN_LOAD_ANNUAL_GROWTH_RATE,
        )
        result = design.simulate_with_incremental_buildout(
            load_profile, solar_2018, schedule, loudoun_load_peak_mw_schedule, weather_year_label="2018",
        )
        self.assertEqual(len(result.hourly), 20 * 365 * 24)  # 20 years (2026-2045 incl.), no leap days
        self.assertEqual(set(result.hourly["build_out_year"]), set(range(2026, 2046)))


class TestIncrementalBuildoutDispatchResultInvariants(unittest.TestCase):
    """Direct tests of each per-row Rule 9 invariant, including
    deliberately constructing violating instances -- same pattern as
    TestPhysicalInvariants above, but for the per-row-fleet_mw-aware
    versions specific to this class."""

    def _make_design(self):
        return BatteryDispatchDesign(power_mw=999, duration_hours=1.0)

    def test_soc_exceeding_that_rows_own_capacity_raises(self):
        design = self._make_design()
        hourly = pd.DataFrame({
            "timestamp": [pd.Timestamp("2026-01-01")], "build_out_year": [2026], "fleet_mw": [10.0],
            "loudoun_load_peak_mw": [100.0],
            "load_mw": [0], "solar_mw": [0], "charge_mw": [0], "discharge_mw": [0],
            "curtailment_mw": [0], "soc_mwh": [11.0], "soc_pct": [110.0], "residual_import_mw": [0],
        })
        with self.assertRaises(ValueError):
            IncrementalBuildoutDispatchResult(design=design, hourly=hourly, weather_year_label="test")

    def test_load_exceeding_that_rows_own_loudoun_load_peak_raises(self):
        """Renamed and re-derived this round: the correct bound for
        load_mw is now loudoun_load_peak_mw (a real, independent series),
        not fleet_mw (the solar/battery side's own scale, genuinely
        decoupled from load's scale after this round's fix)."""
        design = self._make_design()
        hourly = pd.DataFrame({
            "timestamp": [pd.Timestamp("2026-01-01")], "build_out_year": [2026], "fleet_mw": [10.0],
            "loudoun_load_peak_mw": [12.0],
            "load_mw": [15.0],  # exceeds loudoun_load_peak_mw (12.0), though well under fleet_mw (10.0 -- N/A now)
            "solar_mw": [0], "charge_mw": [0], "discharge_mw": [0],
            "curtailment_mw": [0], "soc_mwh": [0.0], "soc_pct": [0.0], "residual_import_mw": [15.0],
        })
        with self.assertRaises(ValueError):
            IncrementalBuildoutDispatchResult(design=design, hourly=hourly, weather_year_label="test")

    def test_a_larger_later_years_loudoun_load_peak_does_not_falsely_trigger_the_earlier_years_bound(self):
        """Direct test that the per-row check is genuinely per-row: a
        load_mw that would exceed an EARLIER, smaller year's
        loudoun_load_peak_mw but is valid for its OWN, later, larger
        year's loudoun_load_peak_mw must NOT raise -- confirming the
        check reads each row's own loudoun_load_peak_mw, not some single
        global value."""
        design = self._make_design()
        hourly = pd.DataFrame({
            "timestamp": [pd.Timestamp("2026-01-01"), pd.Timestamp("2027-01-01")],
            "build_out_year": [2026, 2027], "fleet_mw": [10.0, 100.0],
            "loudoun_load_peak_mw": [10.0, 100.0],
            "load_mw": [10.0, 90.0],  # 90 > 10 (year 1's own peak) but < 100 (year 2's own peak)
            "solar_mw": [0, 0], "charge_mw": [0, 0], "discharge_mw": [10.0, 90.0],
            "curtailment_mw": [0, 0], "soc_mwh": [0.0, 0.0], "soc_pct": [0.0, 0.0],
            "residual_import_mw": [0, 0],
        })
        IncrementalBuildoutDispatchResult(design=design, hourly=hourly, weather_year_label="test")  # should not raise

    def test_valid_result_does_not_raise(self):
        design = BatteryDispatchDesign(power_mw=999, duration_hours=1.0, round_trip_efficiency_pct=100.0)
        hourly = pd.DataFrame({
            "timestamp": [pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-01 01:00")],
            "build_out_year": [2026, 2026], "fleet_mw": [10.0, 10.0],
            "loudoun_load_peak_mw": [100.0, 100.0],
            "load_mw": [0, 10], "solar_mw": [10, 0],
            "charge_mw": [10.0, 0.0], "discharge_mw": [0.0, 10.0], "curtailment_mw": [0.0, 0.0],
            "soc_mwh": [10.0, 0.0], "soc_pct": [100.0, 0.0], "residual_import_mw": [0, 0],
        })
        IncrementalBuildoutDispatchResult(design=design, hourly=hourly, weather_year_label="test")  # should not raise

    def test_dependable_capacity_by_year_hand_verified(self):
        """Two distinct build-out years with different minimums, to
        directly confirm each year is evaluated independently (not
        collapsed into one global minimum -- the degenerate behavior this
        property replaced)."""
        design = BatteryDispatchDesign(power_mw=999, duration_hours=1.0, round_trip_efficiency_pct=100.0)
        hourly = pd.DataFrame({
            "timestamp": [
                pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-01 01:00"),
                pd.Timestamp("2027-01-01"), pd.Timestamp("2027-01-01 01:00"),
            ],
            "build_out_year": [2026, 2026, 2027, 2027], "fleet_mw": [10.0, 10.0, 20.0, 20.0],
            "loudoun_load_peak_mw": [100.0, 100.0, 100.0, 100.0],
            "load_mw": [10.0, 6.0, 15.0, 20.0], "solar_mw": [3.0, 1.0, 13.0, 12.0],
            "charge_mw": [0.0, 0.0, 0.0, 0.0],
            "discharge_mw": [7.0, 5.0, 2.0, 8.0],  # solar+discharge: [10,6] year1, [15,20] year2
            "curtailment_mw": [0.0, 0.0, 0.0, 0.0],
            "soc_mwh": [3.0, 0.0, 18.0, 0.0], "soc_pct": [30.0, 0.0, 90.0, 0.0],
            "residual_import_mw": [0.0, 0.0, 0.0, 0.0],
        })
        result = IncrementalBuildoutDispatchResult(design=design, hourly=hourly, weather_year_label="test")
        by_year = result.dependable_capacity_by_year
        self.assertAlmostEqual(by_year.loc[2026], 6.0, places=6)   # min(10, 6)
        self.assertAlmostEqual(by_year.loc[2027], 15.0, places=6)  # min(15, 20)

    def test_dependable_capacity_hour_by_year_hand_verified(self):
        design = BatteryDispatchDesign(power_mw=999, duration_hours=1.0, round_trip_efficiency_pct=100.0)
        hourly = pd.DataFrame({
            "timestamp": [
                pd.Timestamp("2026-01-01"), pd.Timestamp("2026-01-01 01:00"),
                pd.Timestamp("2027-01-01"), pd.Timestamp("2027-01-01 01:00"),
            ],
            "build_out_year": [2026, 2026, 2027, 2027], "fleet_mw": [10.0, 10.0, 20.0, 20.0],
            "loudoun_load_peak_mw": [100.0, 100.0, 100.0, 100.0],
            "load_mw": [10.0, 6.0, 15.0, 20.0], "solar_mw": [3.0, 1.0, 13.0, 12.0],
            "charge_mw": [0.0, 0.0, 0.0, 0.0],
            "discharge_mw": [7.0, 5.0, 2.0, 8.0],
            "curtailment_mw": [0.0, 0.0, 0.0, 0.0],
            "soc_mwh": [3.0, 0.0, 18.0, 0.0], "soc_pct": [30.0, 0.0, 90.0, 0.0],
            "residual_import_mw": [0.0, 0.0, 0.0, 0.0],
        })
        result = IncrementalBuildoutDispatchResult(design=design, hourly=hourly, weather_year_label="test")
        hours_by_year = result.dependable_capacity_hour_by_year
        self.assertEqual(hours_by_year.loc[2026, "load_mw"], 6.0)   # the year-1 worst hour's own row
        self.assertEqual(hours_by_year.loc[2027, "load_mw"], 15.0)  # the year-2 worst hour's own row

    def test_final_year_dependable_capacity_uses_the_last_year_specifically(self):
        design = BatteryDispatchDesign(power_mw=999, duration_hours=1.0, round_trip_efficiency_pct=100.0)
        hourly = pd.DataFrame({
            "timestamp": [
                pd.Timestamp("2026-01-01"), pd.Timestamp("2027-01-01"), pd.Timestamp("2028-01-01"),
            ],
            "build_out_year": [2026, 2027, 2028], "fleet_mw": [1.0, 1.0, 1.0],
            "loudoun_load_peak_mw": [10.0, 10.0, 10.0],
            "load_mw": [1.0, 1.0, 1.0], "solar_mw": [0.0, 0.0, 0.0],
            "charge_mw": [0.0, 0.0, 0.0],
            "discharge_mw": [0.5, 0.9, 0.3],  # 2026=0.5, 2027=0.9, 2028(final)=0.3 -- the LOWEST
            "curtailment_mw": [0.0, 0.0, 0.0],
            "soc_mwh": [0.5, 0.1, 0.7], "soc_pct": [50.0, 10.0, 70.0],
            "residual_import_mw": [0.5, 0.1, 0.7],
        })
        result = IncrementalBuildoutDispatchResult(design=design, hourly=hourly, weather_year_label="test")
        # Must pick 2028's own value (0.3) specifically -- NOT the global min across all three
        # years (which would also be 0.3 here by coincidence, so also check it does NOT equal
        # 2027's higher value, ruling out "always returns the max year label's row by accident"
        # style bugs).
        self.assertAlmostEqual(result.final_year_dependable_capacity_mw, 0.3, places=6)
        self.assertNotAlmostEqual(result.final_year_dependable_capacity_mw, 0.9, places=6)


class TestFindWorstDependableCapacityAcrossCandidateYears(unittest.TestCase):

    def _make_load_profile(self):
        timestamps = pd.to_datetime(["2018-06-01 00:00", "2018-06-01 01:00"])
        df = pd.DataFrame({"timestamp": timestamps, "mw": [50.0, 50.0], "pct_of_peak": [50.0, 50.0]})
        return LoadProfile(
            year=2045, target_load_factor_pct=90.0, raw_hourly=df,
            solved_floor_pct=0.9, adjusted_hourly=df, peak_mw=100.0,
        )

    def _make_weather_profile(self, solar_values, label):
        from loudoun_solar_hourly_profile import SolarSiteProfile
        timestamps = pd.to_datetime(["2018-06-01 00:00", "2018-06-01 01:00"])
        hourly = pd.DataFrame({"timestamp": timestamps, "kw": solar_values})
        return SolarSiteProfile(
            site_name=label, nameplate_kw=100, tilt_degrees=15, system_losses_pct=14,
            years=[2018], hourly=hourly,
        )

    def test_hand_verified_worst_candidate_identified_correctly(self):
        load_profile = self._make_load_profile()
        # "mild" candidate: plenty of solar both hours -> battery barely needs to discharge
        mild = self._make_weather_profile([100.0, 100.0], "mild")
        # "severe" candidate: zero solar both hours -> battery must discharge hard, hitting a
        # much lower dependable-capacity floor
        severe = self._make_weather_profile([0.0, 0.0], "severe")
        design = BatteryDispatchDesign(power_mw=999, duration_hours=4.0, round_trip_efficiency_pct=100.0)
        schedule = {2026: 10.0}
        loudoun_load_peak_mw_schedule = {2026: 100.0}  # any valid schedule works here

        result = design.find_worst_dependable_capacity_across_candidate_years(
            load_profile, {"mild": mild, "severe": severe}, schedule, loudoun_load_peak_mw_schedule,
        )
        self.assertEqual(result.worst_label, "severe")
        self.assertEqual(len(result.all_results), 2)
        self.assertAlmostEqual(
            result.final_year_dependable_capacity_mw,
            result.all_results["severe"].final_year_dependable_capacity_mw,
        )
        # And the mild candidate's own result should show a HIGHER dependable capacity,
        # confirming "severe" wasn't picked arbitrarily
        self.assertGreater(
            result.all_results["mild"].final_year_dependable_capacity_mw,
            result.final_year_dependable_capacity_mw,
        )

    def test_real_data_small_multi_candidate_run(self):
        """Real-data check with a small (not the full 10-candidate)
        subset, to confirm the orchestration works end to end on genuine
        data without paying the full cost of every candidate in the test
        suite itself."""
        load_profile = LoadProfile.from_domlse_export(DOMLSE_PATH, year=2045)
        solar_2018 = SolarSiteProfile.from_sam_export_yearly_files(PROJECT_DIR, site_name="Sterling", years=[2018])
        solar_2013 = SolarSiteProfile.from_sam_export_yearly_files(PROJECT_DIR, site_name="Sterling", years=[2013])
        design = BatteryDispatchDesign(power_mw=2_908.4, duration_hours=100.0, round_trip_efficiency_pct=80.0)
        # A short schedule (just 2 years) to keep this fast -- the full run happens separately.
        schedule = compute_linear_buildout_schedule(start_year=2026, end_year=2027, end_fleet_mw=2_908.4)
        loudoun_load_peak_mw_schedule = compute_anchored_compound_growth_schedule(
            start_year=2026, end_year=2027, anchor_year=LOUDOUN_LOAD_ANCHOR_YEAR,
            anchor_value=LOUDOUN_LOAD_ANCHOR_MW, annual_growth_rate=LOUDOUN_LOAD_ANNUAL_GROWTH_RATE,
        )

        result = design.find_worst_dependable_capacity_across_candidate_years(
            load_profile, {"2018": solar_2018, "2013": solar_2013}, schedule, loudoun_load_peak_mw_schedule,
        )
        self.assertIn(result.worst_label, ["2018", "2013"])
        self.assertEqual(len(result.all_results), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
