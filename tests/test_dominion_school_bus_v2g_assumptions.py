"""
test_dominion_school_bus_v2g_assumptions.py

Hand-verified tests for D.2 (extended) -- Dominion's own electric school bus V2G program.

Run with: python3 -m pytest test_dominion_school_bus_v2g_assumptions.py -v
"""
import pytest

import dominion_school_bus_v2g_assumptions as db


class TestFleetSizeCorrection:
    """Regression guard on the fleet-size correction (entry #99) -- the original target must never
    be silently used as a current-state figure again."""

    def test_actual_is_far_below_original_target(self):
        assert db.FLEET_SIZE_ACTUAL_MARCH_2024_BUSES < db.FLEET_SIZE_ORIGINAL_TARGET_BUSES
        # Confirms the correction remains a real, large gap (~13% of target), not a rounding issue
        ratio = db.FLEET_SIZE_ACTUAL_MARCH_2024_BUSES / db.FLEET_SIZE_ORIGINAL_TARGET_BUSES
        assert ratio < 0.20

    def test_root_cause_is_documented_not_blank(self):
        assert len(db.FLEET_SIZE_GAP_ROOT_CAUSE) > 20
        assert "legislation" in db.FLEET_SIZE_GAP_ROOT_CAUSE.lower()


class TestBatteryCapacityDiscrepancyPreserved:
    """Confirms both battery-capacity figures are preserved distinctly, and that the module
    actively steers future use toward the stated (not derived) figure."""

    def test_stated_and_derived_figures_differ(self):
        assert db.BATTERY_CAPACITY_STATED_KWH != db.BATTERY_CAPACITY_DERIVED_KWH_DO_NOT_USE

    def test_derived_figure_variable_name_flags_itself_as_deprecated(self):
        # A structural guard: if this variable is ever renamed to drop the warning, this test
        # forces a conscious decision, not a silent rename.
        assert hasattr(db, "BATTERY_CAPACITY_DERIVED_KWH_DO_NOT_USE")

    def test_discrepancy_arithmetic_is_correctly_described(self):
        # 1,050 buses * 220 kWh should NOT equal 105,000 kWh (105 MWh) -- confirming the
        # documented discrepancy is real, not a description error
        implied_total_mwh = db.FLEET_SIZE_ORIGINAL_TARGET_BUSES * db.BATTERY_CAPACITY_STATED_KWH / 1000
        assert implied_total_mwh == pytest.approx(231, abs=1)
        assert implied_total_mwh != pytest.approx(105, abs=1)


class TestRouteHeadroom:
    def test_headroom_calculation_matches_hand_calculation(self):
        # 1 - 80/160 = 0.5 = 50.0%
        result = db.summary()
        assert result["route_headroom_pct_of_range"] == pytest.approx(50.0, abs=0.1)

    def test_average_route_is_less_than_minimum_range(self):
        # The route should be comfortably LESS than the range, leaving headroom for V2G --
        # not the other way around. Confirms the relationship, not just that both numbers exist.
        assert db.AVERAGE_DAILY_ROUTE_MILES < db.RANGE_MILES_MIN


class TestCompensationStructureDistinctFromCashPrograms:
    """Regression guard against ever treating Dominion's in-kind mechanism as if it were a $/kWh
    cash rate the way the cross-state comparison programs are."""

    def test_compensation_is_explicitly_not_cash(self):
        assert db.COMPENSATION_IS_CASH is False

    def test_no_cash_rate_variable_exists(self):
        # Deliberately confirms this module does NOT define a $/kWh or $/kW cash-equivalent
        # figure for Dominion -- one should not be silently added without a stated methodology
        assert not hasattr(db, "COMPENSATION_USD_PER_KWH")
        assert not hasattr(db, "COMPENSATION_USD_PER_KW")

    def test_warranty_cost_share_is_partial_not_full(self):
        assert 0 < db.BATTERY_WARRANTY_COST_SHARE_DOMINION_PCT < 100


class TestEventFrequencyGapExplicitlyDisclosed:
    """The single most important test in this module -- confirms the event-frequency gap is
    preserved as None (explicitly unknown), never silently replaced with a guessed number,
    including one borrowed from another program."""

    def test_event_frequency_is_none_not_a_number(self):
        assert db.EVENT_FREQUENCY_PER_YEAR is None

    def test_context_range_is_clearly_separated_from_the_unknown_actual_figure(self):
        # The other-programs range must exist (for context) but must be a clearly-differently-named
        # variable from the (unknown) Dominion-specific figure, so the two can never be confused
        # by a future reader skimming variable names.
        assert db.OTHER_PROGRAMS_EVENT_FREQUENCY_RANGE_FOR_CONTEXT_ONLY != db.EVENT_FREQUENCY_PER_YEAR
        assert isinstance(db.OTHER_PROGRAMS_EVENT_FREQUENCY_RANGE_FOR_CONTEXT_ONLY, tuple)

    def test_summary_surfaces_the_gap_explicitly(self):
        result = db.summary()
        assert result["event_frequency_per_year"] is None


class TestScenarioNamingDisambiguatesObservedVsFullAdoption:
    """Confirms the two scenarios (observed-trend continuation vs. full statewide adoption) can
    never be confused by name -- the exact failure mode that caused this project to build the wrong
    scenario on the first attempt (misreading 'model the Dominion program... by 2030' as a
    pace-continuation projection rather than the full-statewide-adoption 'bold move' actually
    requested)."""

    def test_backward_compat_alias_points_to_observed_trend_not_full_adoption(self):
        assert db.turnstile_estimate is db.turnstile_estimate_observed_trend_continuation

    def test_each_scenario_self_identifies_in_its_own_return_value(self):
        result_a = db.turnstile_estimate_observed_trend_continuation()
        result_b = db.turnstile_estimate_full_statewide_adoption()
        assert result_a["scenario"] == "observed_trend_continuation"
        assert result_b["scenario"] == "full_statewide_adoption_2030"
        assert result_a["scenario"] != result_b["scenario"]

    def test_full_adoption_uses_the_statewide_total_not_dominions_own_enrolled_fleet(self):
        # The full-adoption scenario must NOT reuse FLEET_SIZE_ACTUAL_MARCH_2024_BUSES (Dominion's
        # own currently-enrolled count) -- it needs the much larger statewide total.
        result = db.turnstile_estimate_full_statewide_adoption()
        assert result["statewide_fleet_buses_low"] > db.FLEET_SIZE_ACTUAL_MARCH_2024_BUSES * 10
        assert result["statewide_fleet_buses_high"] > db.FLEET_SIZE_ACTUAL_MARCH_2024_BUSES * 10


class TestFullStatewideAdoptionScenario:
    def test_low_high_matches_hand_calculation(self):
        # 13,000 * 110 kWh * 15 / 1000 = 21,450 MWh
        # 16,000 * 110 kWh * 15 / 1000 = 26,400 MWh
        result = db.turnstile_estimate_full_statewide_adoption()
        assert result["potential_annual_mwh_upper_bound_low"] == pytest.approx(21450.0)
        assert result["potential_annual_mwh_upper_bound_high"] == pytest.approx(26400.0)

    def test_low_is_actually_lower_than_high(self):
        # Guards against the two statewide-total constants ever being accidentally swapped
        result = db.turnstile_estimate_full_statewide_adoption()
        assert result["potential_annual_mwh_upper_bound_low"] < result["potential_annual_mwh_upper_bound_high"]
        assert db.STATEWIDE_TOTAL_SCHOOL_BUSES_LOW < db.STATEWIDE_TOTAL_SCHOOL_BUSES_HIGH

    def test_both_statewide_totals_preserved_not_collapsed_to_one(self):
        # Consistent with this project's own established practice of preserving genuine
        # discrepancies (e.g. the battery-capacity discrepancy) rather than silently picking one
        assert db.STATEWIDE_TOTAL_SCHOOL_BUSES_LOW == 13000
        assert db.STATEWIDE_TOTAL_SCHOOL_BUSES_HIGH == 16000

    def test_reuses_the_same_per_bus_mechanics_as_scenario_a(self):
        # Confirms Scenario B is a fleet-size input swap on Step 7's own existing mechanics, not a
        # separately-reimplemented calculation (Rule 1/6) -- both scenarios must report the same
        # available_kwh_per_bus, since that figure doesn't depend on which scenario is being run
        result_a = db.turnstile_estimate_observed_trend_continuation()
        result_b = db.turnstile_estimate_full_statewide_adoption()
        assert result_a["available_kwh_per_bus"] == result_b["available_kwh_per_bus"]

    def test_full_adoption_result_is_far_larger_than_observed_trend_result(self):
        # A basic sanity check on the magnitude of the "bold move" contrast this scenario is
        # specifically meant to illustrate
        result_a = db.turnstile_estimate_observed_trend_continuation()
        result_b = db.turnstile_estimate_full_statewide_adoption()
        assert result_b["potential_annual_mwh_upper_bound_low"] > result_a["potential_annual_mwh_upper_bound"] * 10


class TestSummaryCompleteness:
    def test_summary_returns_all_expected_keys(self):
        result = db.summary()
        expected_keys = {
            "fleet_size_original_target_buses", "fleet_size_actual_march_2024_buses",
            "fleet_size_gap_root_cause", "battery_capacity_stated_kwh",
            "battery_capacity_derived_kwh_do_not_use", "battery_capacity_discrepancy_note",
            "range_miles", "average_daily_route_miles", "route_headroom_pct_of_range",
            "utility_cannot_own_bus", "utility_may_own_battery",
            "ownership_wording_discrepancy_note", "compensation_mechanism",
            "compensation_is_cash", "charger_maintenance_coverage_years",
            "battery_warranty_cost_share_dominion_pct", "event_frequency_per_year",
            "event_frequency_context_only_range",
        }
        assert set(result.keys()) == expected_keys


class TestObservedGrowthRateDerivation:
    """Confirms the growth rate is genuinely derived from the two named data points, not a
    hardcoded literal -- and that it's unmistakably distinct from the never-achieved original
    target rate (Rule 7/12)."""

    def test_matches_hand_calculation(self):
        # (135 - 50) / (2024 - 2020) = 21.25
        assert db.OBSERVED_HISTORICAL_GROWTH_BUSES_PER_YR == pytest.approx(21.25)

    def test_is_derived_from_named_constants_not_a_bare_literal(self):
        expected = (
            (db.FLEET_SIZE_ACTUAL_MARCH_2024_BUSES - db.FLEET_SIZE_PHASE1_BUSES)
            / (db.FLEET_SIZE_ACTUAL_YEAR - db.FLEET_SIZE_PHASE1_YEAR)
        )
        assert db.OBSERVED_HISTORICAL_GROWTH_BUSES_PER_YR == expected

    def test_observed_rate_is_far_below_the_never_achieved_original_target_rate(self):
        # Original target implied ~200/yr (1000 additional buses / 5 years). The observed rate
        # must stay clearly, unmistakably lower -- confirms the two are not being conflated.
        implied_original_target_rate = 1000 / 5  # per the original 2019 Phase 2 announcement
        assert db.OBSERVED_HISTORICAL_GROWTH_BUSES_PER_YR < implied_original_target_rate / 5


class TestAvailableKwhPerBusDerivedNotHardcoded:
    def test_matches_hand_calculation(self):
        # 220 * (1 - 80/160) = 220 * 0.5 = 110.0
        assert db.available_kwh_per_bus_for_discharge() == pytest.approx(110.0)

    def test_changes_correctly_if_underlying_inputs_change(self):
        # Confirms this is a live calculation from Step 2/3's own constants, not a separately
        # hardcoded 110 that would silently drift if BATTERY_CAPACITY_STATED_KWH were ever revised.
        # Computed independently here, not by calling the function, to make this a genuine
        # cross-check rather than the function checking itself.
        independently_computed = db.BATTERY_CAPACITY_STATED_KWH * (
            1 - db.AVERAGE_DAILY_ROUTE_MILES / db.RANGE_MILES_MAX
        )
        assert db.available_kwh_per_bus_for_discharge() == pytest.approx(independently_computed)


class TestFleetProjection:
    def test_2030_matches_hand_calculation(self):
        # 135 + 21.25 * (2030 - 2024) = 135 + 127.5 = 262.5
        assert db.project_fleet_size(2030) == pytest.approx(262.5)

    def test_raises_on_backward_projection(self):
        with pytest.raises(ValueError):
            db.project_fleet_size(2020)

    def test_never_falls_below_observed_actual(self):
        result = db.project_fleet_size(2030)
        assert result >= db.FLEET_SIZE_ACTUAL_MARCH_2024_BUSES

    def test_accepts_an_overridden_growth_rate_per_rule_8(self):
        # A future, more detailed pass should be able to supply a different assumption (e.g. a
        # renewed-funding scenario) without editing this function's own body.
        result_default = db.project_fleet_size(2030)
        result_overridden = db.project_fleet_size(2030, growth_buses_per_yr=200)
        assert result_overridden > result_default


class TestTurnstileAssumptionDistinctFromRealGap:
    """The single most important test class in this section -- confirms the new, deliberately
    round modeling assumption can never be confused with, or silently substituted for, the real
    (still-unknown) Dominion figure from Step 6."""

    def test_turnstile_assumption_and_real_gap_are_different_variables(self):
        assert db.EVENT_FREQUENCY_PER_YEAR is None  # the real gap -- must remain unresolved
        assert db.TURNSTILE_ASSUMED_EVENT_FREQUENCY_PER_YR is not None  # the deliberate assumption
        assert db.TURNSTILE_ASSUMED_EVENT_FREQUENCY_PER_YR == 15

    def test_turnstile_estimate_does_not_read_the_real_unknown_gap(self):
        # If turnstile_estimate() were ever refactored to default to EVENT_FREQUENCY_PER_YEAR
        # instead of TURNSTILE_ASSUMED_EVENT_FREQUENCY_PER_YR, it would silently return None-based
        # nonsense. This test would catch that regression immediately.
        result = db.turnstile_estimate()
        assert result["assumed_event_frequency_per_yr"] is not None
        assert result["assumed_event_frequency_per_yr"] == db.TURNSTILE_ASSUMED_EVENT_FREQUENCY_PER_YR


class TestTurnstileEstimateEndToEnd:
    """Full end-to-end check on the combined function, cross-checked against independently
    hand-computed values, not just against the module's own intermediate functions (Rule 4)."""

    def test_2030_default_matches_hand_calculation(self):
        # 262.5 buses * 110 kWh * 15 events/yr / 1000 = 433.125 MWh/yr
        result = db.turnstile_estimate()
        assert result["potential_annual_mwh_upper_bound"] == pytest.approx(433.1, abs=0.1)

    def test_rounds_fleet_size_to_a_whole_bus_for_readability(self):
        result = db.turnstile_estimate()
        assert result["projected_fleet_buses"] == round(262.5)
        assert isinstance(result["projected_fleet_buses"], int)

    def test_returns_every_intermediate_value_not_just_the_final_number(self):
        result = db.turnstile_estimate()
        for key in ("target_year", "projected_fleet_buses", "growth_buses_per_yr_used",
                    "available_kwh_per_bus", "assumed_event_frequency_per_yr",
                    "potential_annual_mwh_upper_bound", "framing_note"):
            assert key in result

    def test_framing_note_states_upper_bound_explicitly(self):
        result = db.turnstile_estimate()
        assert "upper-bound" in result["framing_note"].lower() or "upper bound" in result["framing_note"].lower()

    def test_all_parameters_are_overridable_per_rule_8(self):
        default_result = db.turnstile_estimate()
        overridden_result = db.turnstile_estimate(
            target_year=2035, growth_buses_per_yr=50, assumed_event_frequency_per_yr=20
        )
        assert overridden_result["target_year"] == 2035
        assert overridden_result != default_result
