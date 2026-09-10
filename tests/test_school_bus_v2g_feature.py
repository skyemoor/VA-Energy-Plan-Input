"""
test_school_bus_v2g_feature.py

Tests for the SchoolBusV2G adapter -- verifies correct implementation of the shared WMAPathway
interface, correct use of the new non-monetary compensation pattern, and that migration did not
change any already-established figure.

Run with: python3 -m pytest test_school_bus_v2g_feature.py -v
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared_base_classes'))

import pytest

from school_bus_v2g_feature import SchoolBusV2G
from demand_side_feature import WMAPathway
import dominion_school_bus_v2g_assumptions as sb


class TestImplementsSharedInterface:
    def test_is_a_wma_pathway(self):
        assert isinstance(SchoolBusV2G(), WMAPathway)

    def test_can_be_instantiated(self):
        SchoolBusV2G()

    def test_feature_name_is_set(self):
        feature = SchoolBusV2G()
        assert feature.feature_name != "UNNAMED FEATURE -- subclass must set this"
        assert "School Bus" in feature.feature_name


class TestNonMonetaryCompensationCorrectlyApplied:
    """The single most important test class here -- confirms this is the real, motivating use
    case for the base class's own new compensation_is_monetary()/compensation_description() pair,
    and that it's applied correctly, not just present."""

    def test_compensation_is_monetary_returns_false(self):
        assert SchoolBusV2G().compensation_is_monetary() is False

    def test_matches_existing_module_constant_not_a_separate_literal(self):
        # Confirms this reads the existing module's own constant rather than restating True/False
        # as a new, separately-maintained literal
        assert SchoolBusV2G().compensation_is_monetary() == sb.COMPENSATION_IS_CASH

    def test_current_compensation_usd_raises(self):
        with pytest.raises(NotImplementedError):
            SchoolBusV2G().current_compensation_usd()

    def test_current_compensation_usd_error_points_to_description_method(self):
        with pytest.raises(NotImplementedError, match="compensation_description"):
            SchoolBusV2G().current_compensation_usd()

    def test_compensation_description_returns_real_mechanism_not_placeholder(self):
        result = SchoolBusV2G().compensation_description()
        assert result == sb.COMPENSATION_MECHANISM
        assert "in-kind" in result.lower()


class TestValuesReadLiveFromExistingModule:
    def test_magnitude_matches_existing_calculation(self):
        feature = SchoolBusV2G()
        assert feature.magnitude_per_unit() == sb.available_kwh_per_bus_for_discharge()

    def test_fleet_size_matches_existing_constant(self):
        feature = SchoolBusV2G()
        assert feature.fleet_size_actual() == sb.FLEET_SIZE_ACTUAL_MARCH_2024_BUSES


class TestPassthroughsMatchOriginalUnmigratedFunctions:
    """Confirms the two turnstile scenarios, migrated through the adapter, produce IDENTICAL
    results to calling the underlying, untouched module directly -- the same migration-fidelity
    guard already established for LargeCICurtailment."""

    def test_observed_trend_scenario_matches_original_exactly(self):
        feature = SchoolBusV2G()
        via_adapter = feature.turnstile_estimate_observed_trend(target_year=2030)
        via_original = sb.turnstile_estimate_observed_trend_continuation(target_year=2030)
        assert via_adapter == via_original

    def test_full_statewide_adoption_scenario_matches_original_exactly(self):
        feature = SchoolBusV2G()
        via_adapter = feature.turnstile_estimate_full_statewide_adoption()
        via_original = sb.turnstile_estimate_full_statewide_adoption()
        assert via_adapter == via_original

    def test_full_statewide_figures_still_match_the_already_established_range(self):
        # Direct, human-readable regression guard on the actual cited figures
        result = SchoolBusV2G().turnstile_estimate_full_statewide_adoption()
        assert result["potential_annual_mwh_upper_bound_low"] == pytest.approx(21450.0)
        assert result["potential_annual_mwh_upper_bound_high"] == pytest.approx(26400.0)
