"""
test_large_ci_curtailment_feature.py

Tests for the LargeCICurtailment adapter -- verifies both that it correctly implements the shared
DLCProgram interface AND that migrating onto that interface did not silently change the original,
already-tested entry #82 finding.

Run with: python3 -m pytest test_large_ci_curtailment_feature.py -v
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared_base_classes'))

import pytest

from large_ci_curtailment_feature import LargeCICurtailment
from demand_side_feature import DLCProgram
import large_ci_curtailment_assumptions as lci


class TestImplementsSharedInterface:
    def test_is_a_dlc_program(self):
        assert isinstance(LargeCICurtailment(), DLCProgram)

    def test_can_be_instantiated(self):
        # Confirms both abstract methods are actually implemented -- if either were missing,
        # this would raise TypeError per the base class's own abc enforcement.
        LargeCICurtailment()

    def test_feature_name_is_set(self):
        feature = LargeCICurtailment()
        assert feature.feature_name != "UNNAMED FEATURE -- subclass must set this"
        assert "Large C&I" in feature.feature_name


class TestValuesReadLiveFromExistingModule:
    """Confirms this adapter reuses the existing module's own constants rather than restating them
    -- if the underlying module's own constant ever changes, this adapter must reflect that
    automatically, not silently drift out of sync."""

    def test_magnitude_matches_existing_eligibility_threshold(self):
        feature = LargeCICurtailment()
        assert feature.magnitude_per_unit() == lci.ELIGIBILITY_THRESHOLD_KW

    def test_compensation_matches_existing_rate_constant(self):
        feature = LargeCICurtailment()
        assert feature.current_compensation_usd() == lci.COMPENSATION_USD_PER_KW_YEAR


class TestOriginalFindingUntouched:
    def test_original_function_still_directly_accessible_and_unchanged(self):
        feature = LargeCICurtailment()
        result = feature.original_avoided_cost_finding()
        # Cross-checked directly against the existing module's own function, called independently
        independent_call = lci.avoided_generation_capacity_cost_comparison()
        assert result == independent_call


class TestMigrationFidelityTheCriticalRegressionGuard:
    """The single most important test class in this file -- proves the new shared-method pathway
    reproduces the ORIGINAL entry #82 finding exactly when called with the matching methodology
    (margin=0), rather than silently changing an already-established, already-tested result."""

    def test_aeroderivative_pct_matches_original_exactly(self):
        feature = LargeCICurtailment()
        original = feature.original_avoided_cost_finding()

        via_shared = feature.avoided_cost_comparison_matching_original_methodology(
            avoided_capacity_usd_per_kw_yr=original["aeroderivative_avoided_cost_usd_per_kw_yr"]
        )
        assert via_shared["current_rate_as_pct_of_properly_priced"] == pytest.approx(
            original["aeroderivative_incentive_as_pct_of_avoided_cost"], abs=0.01
        )

    def test_fclass_pct_matches_original_exactly(self):
        feature = LargeCICurtailment()
        original = feature.original_avoided_cost_finding()

        via_shared = feature.avoided_cost_comparison_matching_original_methodology(
            avoided_capacity_usd_per_kw_yr=original["fclass_avoided_cost_usd_per_kw_yr"]
        )
        assert via_shared["current_rate_as_pct_of_properly_priced"] == pytest.approx(
            original["fclass_incentive_as_pct_of_avoided_cost"], abs=0.01
        )

    def test_the_already_established_headline_figures_still_hold(self):
        # A direct, human-readable regression guard on the actual numbers this project has cited
        # repeatedly (~41% Aero, ~71% F-Class) -- if a future change to either module ever moved
        # these substantially, this test failing is the signal, not a silent drift.
        feature = LargeCICurtailment()
        original = feature.original_avoided_cost_finding()
        assert 38 <= original["aeroderivative_incentive_as_pct_of_avoided_cost"] <= 43
        assert 68 <= original["fclass_incentive_as_pct_of_avoided_cost"] <= 73

    def test_default_margin_now_matches_the_original_directly(self):
        # UPDATED 2026-08-26: the shared method's own default margin changed from 5% to 0%
        # (direct user decision -- 5% was never a sourced figure). This means the shared method's
        # PLAIN default now matches the original entry #82 finding directly, without needing the
        # explicit utility_margin_pct=0 override this adapter still passes for self-documentation.
        # This test replaces the prior version (which proved the opposite, when the shared default
        # was still 5%) -- the roles are now reversed, and that reversal is itself the point.
        feature = LargeCICurtailment()
        original = feature.original_avoided_cost_finding()

        default_margin_result = feature.avoided_cost_comparison(
            avoided_capacity_usd_per_kw_yr=original["aeroderivative_avoided_cost_usd_per_kw_yr"]
        )
        assert default_margin_result["current_rate_as_pct_of_properly_priced"] == pytest.approx(
            original["aeroderivative_incentive_as_pct_of_avoided_cost"], abs=0.01
        )

    def test_a_nonzero_margin_still_produces_a_different_result(self):
        # The genuinely still-useful check from the original test, inverted: confirms the margin
        # parameter is still real and functioning -- a NON-zero margin should diverge from the
        # zero-margin original, proving the parameterization itself still works correctly even
        # though the DEFAULT no longer demonstrates this on its own.
        feature = LargeCICurtailment()
        original = feature.original_avoided_cost_finding()

        nonzero_margin_result = feature.avoided_cost_comparison(
            avoided_capacity_usd_per_kw_yr=original["aeroderivative_avoided_cost_usd_per_kw_yr"],
            utility_margin_pct=5,
        )
        assert nonzero_margin_result["current_rate_as_pct_of_properly_priced"] != pytest.approx(
            original["aeroderivative_incentive_as_pct_of_avoided_cost"], abs=0.01
        )
