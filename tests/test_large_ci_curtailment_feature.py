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
import large_ci_curtailment_derived as lci


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

    def test_derivation_reproduces_entry_82_from_its_own_original_inputs(self):
        """REPLACED 2026-09-10. This previously asserted fixed bands (38-43% and 68-73%) on the
        live figures. Those bands were a function of hardcoded historical peaker costs, which
        violated Rule 8 -- and once the cost chain was made live, a test asserting fixed
        percentages would break every time someone adjusted a cost in assumptions.py, which is
        precisely what that surface exists for.

        What is genuinely worth locking is the DERIVATION, not the output. This passes entry #82's
        own original inputs explicitly and confirms the logic still reproduces its published
        figures -- which also preserves the guarantee that validated this module's reconstruction
        from its tests, without those inputs living in the module as constants.

        The 40.7%/70.9% result itself is recorded in registers/Provenance_Register.xlsx as a
        superseded result, which is where a historical figure belongs.
        """
        import large_ci_curtailment_derived as derived
        rate = 36.0
        for capex, fom, expected_pct in [(1175.0, 16.30, 40.7), (713.0, 7.00, 70.9)]:
            avoided = derived.annualized_avoided_capacity_cost_usd_per_kw_yr(capex, fom)
            assert round(rate / avoided * 100, 1) == pytest.approx(expected_pct, abs=0.1)

    def test_live_figures_move_with_assumptions_rather_than_being_frozen(self):
        """The point of making the chain live: changing a cost input must change the result."""
        import large_ci_curtailment_derived as derived
        low = derived.avoided_generation_capacity_cost_comparison('low')
        high = derived.avoided_generation_capacity_cost_comparison('high')
        assert (high['fclass_incentive_as_pct_of_avoided_cost']
                < low['fclass_incentive_as_pct_of_avoided_cost'])

    def test_current_costs_give_a_tighter_lower_range_than_entry_82(self):
        """On current costs the finding is ~35-38% at central case, against 41-71% on the older
        Gas Turbine World figures -- tighter, lower, and a stronger result."""
        import large_ci_curtailment_derived as derived
        r = derived.avoided_generation_capacity_cost_comparison('central')
        assert 30 <= r['aeroderivative_incentive_as_pct_of_avoided_cost'] <= 40
        assert 33 <= r['fclass_incentive_as_pct_of_avoided_cost'] <= 43

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
