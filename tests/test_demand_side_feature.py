"""
test_demand_side_feature.py

Tests for the shared abstract base class hierarchy. Uses minimal, purpose-built test-double
subclasses (not real Dominion programs) so these tests verify the HIERARCHY's own behavior in
isolation, independent of any real program's own sourcing status -- migrating a real module (e.g.
dlc_analysis) onto this hierarchy gets its own separate migration tests, not covered here.

Run with: python3 -m pytest test_demand_side_feature.py -v
"""
import pytest

from demand_side_feature import DemandSideFeature, EEMeasure, DLCProgram, WMAPathway, PriceBasedDR


class TestAbstractRootCannotBeInstantiated:
    """Confirms Python's own abc machinery actually enforces the abstract methods -- not just
    documentation, real instantiation-time enforcement."""

    def test_demand_side_feature_cannot_be_instantiated_directly(self):
        with pytest.raises(TypeError):
            DemandSideFeature()

    def test_intermediate_abstract_classes_also_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            EEMeasure()
        with pytest.raises(TypeError):
            DLCProgram()
        with pytest.raises(TypeError):
            WMAPathway()
        with pytest.raises(TypeError):
            PriceBasedDR()


class TestSubclassMissingRequiredMethodCannotBeInstantiated:
    """The core enforcement guarantee: a subclass that forgets to implement a required abstract
    method cannot silently exist as a half-built object -- Python refuses to instantiate it."""

    def test_subclass_missing_current_compensation_usd_cannot_be_instantiated(self):
        class IncompleteFeature(DLCProgram):
            feature_name = "Incomplete Test Feature"

            def magnitude_per_unit(self):
                return 1.0
            # current_compensation_usd() deliberately NOT implemented

        with pytest.raises(TypeError):
            IncompleteFeature()

    def test_subclass_missing_magnitude_per_unit_cannot_be_instantiated(self):
        class IncompleteFeature(DLCProgram):
            feature_name = "Incomplete Test Feature"

            def current_compensation_usd(self):
                return 10.0
            # magnitude_per_unit() deliberately NOT implemented

        with pytest.raises(TypeError):
            IncompleteFeature()


class TestNoneVsNotImplementedErrorDistinction:
    """The single most important test class in this suite -- directly proves the two deliberately
    different 'missing value' mechanisms actually behave differently, per the user's own core
    design instruction."""

    def test_none_return_is_allowed_and_propagates_cleanly(self):
        class UnpublishedRateFeature(DLCProgram):
            feature_name = "Unpublished Rate Test Feature"

            def magnitude_per_unit(self):
                return 100.0

            def current_compensation_usd(self):
                return None  # concept applies, rate not yet published

        feature = UnpublishedRateFeature()
        assert feature.current_compensation_usd() is None

    def test_notimplementederror_is_allowed_and_raises_cleanly(self):
        class StructurallyInapplicableFeature(DLCProgram):
            feature_name = "CVR-style Test Feature"

            def magnitude_per_unit(self):
                return 50.0

            def current_compensation_usd(self):
                raise NotImplementedError(
                    "No customer-facing compensation mechanism exists for this feature."
                )

        feature = StructurallyInapplicableFeature()
        with pytest.raises(NotImplementedError):
            feature.current_compensation_usd()

    def test_the_two_mechanisms_are_genuinely_distinguishable_by_a_caller(self):
        # A caller MUST be able to tell these two situations apart programmatically -- this test
        # directly proves that distinguishability, not just that each mechanism works alone.
        class UnpublishedRateFeature(DLCProgram):
            feature_name = "Unpublished"
            def magnitude_per_unit(self): return 1.0
            def current_compensation_usd(self): return None

        class InapplicableFeature(DLCProgram):
            feature_name = "Inapplicable"
            def magnitude_per_unit(self): return 1.0
            def current_compensation_usd(self): raise NotImplementedError("N/A")

        unpublished = UnpublishedRateFeature()
        inapplicable = InapplicableFeature()

        # The caller can safely call current_compensation_usd() on the unpublished-rate feature
        # and get a real (if empty) answer:
        result = unpublished.current_compensation_usd()
        assert result is None

        # The caller CANNOT safely call it on the inapplicable feature without handling the
        # exception -- this is the point: the inapplicable case forces explicit handling, the
        # unpublished case does not.
        with pytest.raises(NotImplementedError):
            inapplicable.current_compensation_usd()


class TestDLCProgramSharedAvoidedCostComparison:
    """Tests the ONE shared, concrete method DLCProgram adds -- the exact calculation that was
    previously reimplemented independently (and inconsistently) per module."""

    @pytest.fixture
    def known_rate_feature(self):
        class KnownRateFeature(DLCProgram):
            feature_name = "Known Rate Test Feature"

            def magnitude_per_unit(self):
                return 3.51

            def current_compensation_usd(self):
                return 11.40  # matches the real EV Charger Rewards implied rate, entry #105

        return KnownRateFeature()

    def test_matches_hand_calculation(self, known_rate_feature):
        # Value updated 2026-08-26: default margin changed from 5% to 0% (direct user decision --
        # 5% was never a sourced figure). (713 + 90.98) * 1.00 = 803.98
        result = known_rate_feature.avoided_cost_comparison(
            avoided_capacity_usd_per_kw_yr=713, avoided_energy_usd_per_kw=90.98
        )
        assert result["properly_priced_usd_per_kw_yr"] == pytest.approx(803.98, abs=0.5)

    def test_current_rate_fields_populated_when_rate_is_known(self, known_rate_feature):
        result = known_rate_feature.avoided_cost_comparison(avoided_capacity_usd_per_kw_yr=713)
        assert result["current_rate_usd_per_kw_yr"] == 11.40
        assert result["current_rate_as_pct_of_properly_priced"] is not None
        assert result["properly_priced_as_multiple_of_current"] is not None

    def test_energy_component_defaults_to_zero_not_required(self, known_rate_feature):
        # Confirms this works cleanly for capacity-only comparisons too (e.g. large C&I's own
        # original entry #82 cross-check, which had no energy/WMA component at the time)
        result = known_rate_feature.avoided_cost_comparison(avoided_capacity_usd_per_kw_yr=713)
        assert result["avoided_energy_usd_per_kw"] == 0.0
        # Updated 2026-08-26: default margin changed from 5% to 0%
        assert result["properly_priced_usd_per_kw_yr"] == pytest.approx(713 * 1.0, abs=0.1)

    def test_feature_name_included_in_output_for_multi_feature_comparisons(self, known_rate_feature):
        result = known_rate_feature.avoided_cost_comparison(avoided_capacity_usd_per_kw_yr=713)
        assert result["feature_name"] == "Known Rate Test Feature"

    def test_notimplementederror_from_current_compensation_propagates_through_comparison(self):
        # The CVR case: asking for an avoided-cost comparison against a feature with no
        # compensation concept at all should fail loudly, not silently produce a partial result.
        class InapplicableFeature(DLCProgram):
            feature_name = "CVR-style"
            def magnitude_per_unit(self): return 1.0
            def current_compensation_usd(self): raise NotImplementedError("No compensation exists.")

        feature = InapplicableFeature()
        with pytest.raises(NotImplementedError):
            feature.avoided_cost_comparison(avoided_capacity_usd_per_kw_yr=713)

    def test_none_current_rate_still_returns_the_benchmark_gracefully(self):
        # The A.7/BYOD case: the concept applies but the rate isn't published -- the benchmark
        # itself should still be computed and returned, not blocked by the missing current rate.
        class UnpublishedRateFeature(DLCProgram):
            feature_name = "BYOD-style"
            def magnitude_per_unit(self): return 1.0
            def current_compensation_usd(self): return None

        feature = UnpublishedRateFeature()
        result = feature.avoided_cost_comparison(avoided_capacity_usd_per_kw_yr=713)
        # Updated 2026-08-26: default margin changed from 5% to 0%
        assert result["properly_priced_usd_per_kw_yr"] == pytest.approx(713 * 1.0, abs=0.1)
        assert result["current_rate_usd_per_kw_yr"] is None
        assert result["current_rate_as_pct_of_properly_priced"] is None
        assert result["properly_priced_as_multiple_of_current"] is None

    def test_utility_margin_is_a_parameter_not_hardcoded(self, known_rate_feature):
        # Rule 8 -- confirms the margin can be overridden, matching the same parameterization
        # already established in dlc_derived_assumptions.py's own standalone function (entry #109)
        default_result = known_rate_feature.avoided_cost_comparison(
            avoided_capacity_usd_per_kw_yr=1000
        )
        custom_result = known_rate_feature.avoided_cost_comparison(
            avoided_capacity_usd_per_kw_yr=1000, utility_margin_pct=10
        )
        assert default_result["properly_priced_usd_per_kw_yr"] != custom_result["properly_priced_usd_per_kw_yr"]
        assert custom_result["properly_priced_usd_per_kw_yr"] < default_result["properly_priced_usd_per_kw_yr"]

    def test_default_resolves_from_the_true_global_constant(self, known_rate_feature):
        # Consolidation, entry #116, direct user request: DEFAULT_UTILITY_MARGIN_PCT is now the
        # single source of truth (previously duplicated across this file and dlc_derived_assumptions.py
        # independently). Confirms the method's own None-sentinel default genuinely resolves to
        # THIS module-level constant specifically, not a separately-hardcoded literal that happens
        # to currently match it.
        import demand_side_feature
        result = known_rate_feature.avoided_cost_comparison(avoided_capacity_usd_per_kw_yr=1000)
        expected = 1000 * (1 - demand_side_feature.DEFAULT_UTILITY_MARGIN_PCT / 100)
        assert result["properly_priced_usd_per_kw_yr"] == pytest.approx(expected)
        assert result["utility_margin_pct"] == demand_side_feature.DEFAULT_UTILITY_MARGIN_PCT


class TestNonMonetaryCompensationThirdCase:
    """Tests the third missing-value case, added while migrating school_bus_v2g_analysis (which
    has real, known, but non-monetary compensation -- in-kind battery replenishment, not a dollar
    figure) -- found not to fit either of the two originally-designed cases (None / structural
    NotImplementedError), so a distinct pair of methods was added rather than forcing a misleading
    fit into one of the first two."""

    def test_compensation_is_monetary_defaults_to_true(self):
        class OrdinaryFeature(DLCProgram):
            feature_name = "Ordinary"
            def magnitude_per_unit(self): return 1.0
            def current_compensation_usd(self): return 10.0

        # Confirms every subclass built BEFORE this method existed still works unmodified --
        # the whole point of a concrete default rather than a new abstract requirement.
        assert OrdinaryFeature().compensation_is_monetary() is True

    def test_compensation_description_raises_by_default(self):
        class OrdinaryFeature(DLCProgram):
            feature_name = "Ordinary"
            def magnitude_per_unit(self): return 1.0
            def current_compensation_usd(self): return 10.0

        with pytest.raises(NotImplementedError):
            OrdinaryFeature().compensation_description()

    def test_in_kind_feature_can_override_both_consistently(self):
        class InKindFeature(WMAPathway):
            feature_name = "In-kind Test Feature"

            def magnitude_per_unit(self):
                return 110.0

            def current_compensation_usd(self):
                raise NotImplementedError(
                    "Compensation is in-kind -- see compensation_description()."
                )

            def compensation_is_monetary(self):
                return False

            def compensation_description(self):
                return "Free battery replenishment within 3 hours of a call."

        feature = InKindFeature()
        assert feature.compensation_is_monetary() is False
        assert "replenishment" in feature.compensation_description()
        with pytest.raises(NotImplementedError):
            feature.current_compensation_usd()

    def test_three_cases_are_all_mutually_distinguishable_by_a_caller(self):
        # Extends the original two-case distinguishability test (TestNoneVsNotImplementedError
        # Distinction) to confirm the third case is also cleanly separable from the other two --
        # a caller checking compensation_is_monetary() first can route correctly among all three.
        class UnpublishedRate(DLCProgram):
            feature_name = "Unpublished"
            def magnitude_per_unit(self): return 1.0
            def current_compensation_usd(self): return None

        class StructurallyInapplicable(DLCProgram):
            feature_name = "Inapplicable"
            def magnitude_per_unit(self): return 1.0
            def current_compensation_usd(self): raise NotImplementedError("N/A")

        class InKind(WMAPathway):
            feature_name = "In-kind"
            def magnitude_per_unit(self): return 1.0
            def current_compensation_usd(self): raise NotImplementedError("See description.")
            def compensation_is_monetary(self): return False
            def compensation_description(self): return "A real, non-cash service."

        unpublished, inapplicable, in_kind = UnpublishedRate(), StructurallyInapplicable(), InKind()

        # All three default to compensation_is_monetary() == True EXCEPT the in-kind one --
        # this is exactly the signal a caller uses to route to compensation_description()
        assert unpublished.compensation_is_monetary() is True
        assert inapplicable.compensation_is_monetary() is True
        assert in_kind.compensation_is_monetary() is False


class TestFeatureNameRequired:
    def test_default_feature_name_signals_unset_rather_than_silently_blank(self):
        class UnnamedFeature(EEMeasure):
            def magnitude_per_unit(self): return 1.0
            def current_compensation_usd(self): return None

        feature = UnnamedFeature()
        assert "subclass must set this" in feature.feature_name
