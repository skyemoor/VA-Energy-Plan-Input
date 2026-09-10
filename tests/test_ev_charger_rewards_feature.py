"""
test_ev_charger_rewards_feature.py

Tests for the EVChargerRewards adapter -- verifies correct implementation of the shared DLCProgram
interface and that migration reproduces the existing, already-tested findings exactly, using the
shared method's own DEFAULT parameters (unlike large_ci, which required an explicit margin=0
override -- confirmed and tested as a real, deliberate difference between the two migrations).

Run with: python3 -m pytest test_ev_charger_rewards_feature.py -v
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared_base_classes'))

import pytest

from ev_charger_rewards_feature import EVChargerRewards
from demand_side_feature import DLCProgram
import dlc_derived_assumptions as dlc


class TestImplementsSharedInterface:
    def test_is_a_dlc_program(self):
        assert isinstance(EVChargerRewards(), DLCProgram)

    def test_can_be_instantiated(self):
        EVChargerRewards()

    def test_feature_name_is_set(self):
        feature = EVChargerRewards()
        assert "EV Charger Rewards" in feature.feature_name

    def test_compensation_is_monetary_defaults_true_correctly(self):
        # Unlike school bus V2G, this program's compensation genuinely IS monetary -- confirms
        # the adapter did NOT override compensation_is_monetary(), relying correctly on the base
        # class's own default rather than needing the non-monetary pattern.
        assert EVChargerRewards().compensation_is_monetary() is True


class TestValuesReadLiveFromExistingModule:
    def test_magnitude_matches_existing_calculation(self):
        feature = EVChargerRewards()
        assert feature.magnitude_per_unit() == dlc.EXPECTED_KW_REDUCTION_PER_PARTICIPANT

    def test_compensation_matches_existing_derived_rate(self):
        feature = EVChargerRewards()
        assert feature.current_compensation_usd() == dlc.implied_current_rate_usd_per_kw_yr()


class TestMigrationFidelityViaDefaultParameters:
    """The key difference from the large_ci migration, tested directly: this module's own existing
    methodology already matches the shared method's own default (5% margin), so no override is
    needed to reproduce the original finding -- confirmed here rather than assumed."""

    def test_shared_method_matches_original_with_default_margin_no_override_needed(self):
        feature = EVChargerRewards()
        original = feature.original_avoided_cost_finding()

        via_shared = feature.avoided_cost_comparison(
            avoided_capacity_usd_per_kw_yr=713, avoided_energy_usd_per_kw=90.98
            # deliberately NOT passing utility_margin_pct -- using the shared method's own default
        )
        assert via_shared["properly_priced_usd_per_kw_yr"] == pytest.approx(
            original["properly_priced_low_usd_per_kw_yr"], abs=0.5
        )

    def test_high_bound_also_matches_via_default_margin(self):
        feature = EVChargerRewards()
        original = feature.original_avoided_cost_finding()

        via_shared = feature.avoided_cost_comparison(
            avoided_capacity_usd_per_kw_yr=1175, avoided_energy_usd_per_kw=136.29
        )
        assert via_shared["properly_priced_usd_per_kw_yr"] == pytest.approx(
            original["properly_priced_high_usd_per_kw_yr"], abs=0.5
        )

    def test_the_already_established_headline_multiple_still_holds(self):
        # Regression guard on the actual cited finding (~67-109x)
        feature = EVChargerRewards()
        original = feature.original_avoided_cost_finding()
        assert original["current_rate_as_multiple_of_low"] > 50
        assert original["current_rate_as_multiple_of_high"] > 50

    def test_original_function_still_directly_accessible_and_unchanged(self):
        feature = EVChargerRewards()
        result = feature.original_avoided_cost_finding()
        independent_call = dlc.avoided_cost_comparison()
        assert result == independent_call


class TestTerritoryWideCeilingPassthrough:
    def test_matches_the_underlying_module_exactly(self):
        feature = EVChargerRewards()
        via_adapter = feature.territory_wide_ceiling_estimate_mw()
        via_original = dlc.territory_wide_ceiling_estimate_mw()
        assert via_adapter == via_original

    def test_still_flagged_as_not_realistic_through_the_adapter(self):
        feature = EVChargerRewards()
        result = feature.territory_wide_ceiling_estimate_mw()
        assert result["is_realistic_enrollment_estimate"] is False
