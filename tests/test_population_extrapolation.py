"""
test_population_extrapolation.py

Per SES Rule 2: each test locks a shared calculation to an independently-derivable
baseline, not just internal self-consistency.
"""
import pytest
import population_extrapolation as pe


class TestReferenceRates:
    def test_loudoun_not_in_reference_set(self):
        names = [c.name for c in pe.REFERENCE_COUNTIES]
        assert "Loudoun" not in names, "Loudoun must be excluded per documented outlier rationale"

    def test_arlington_not_in_reference_set(self):
        names = [c.name for c in pe.REFERENCE_COUNTIES]
        assert "Arlington" not in names, "Arlington must be excluded -- distinctively dense, non-representative"

    def test_exactly_two_reference_counties(self):
        assert len(pe.REFERENCE_COUNTIES) == 2

    def test_fairfax_ci_rate_matches_independent_arithmetic(self):
        # Independent cross-check (SES Rule 4): 132.4 MW / 1,175,940 population, computed
        # here directly, not by re-calling the property under test.
        fairfax = next(c for c in pe.REFERENCE_COUNTIES if c.name == "Fairfax")
        expected = 132.4 * 1_000_000 / 1_175_940 / 1000  # MW->W->kW/capita, then back to kW
        assert abs(fairfax.ci_kw_per_capita - expected) < 0.0001

    def test_ci_range_bounds_are_fairfax_low_prince_william_high(self):
        # Independently verify which county produces each bound, given the real numbers --
        # not just that SOME range comes out, but that it's the RIGHT range.
        low, high = pe.ci_kw_per_capita_range()
        fairfax = next(c for c in pe.REFERENCE_COUNTIES if c.name == "Fairfax")
        pwc = next(c for c in pe.REFERENCE_COUNTIES if c.name == "Prince William")
        assert abs(low - fairfax.ci_kw_per_capita) < 0.0001
        assert abs(high - pwc.ci_kw_per_capita) < 0.0001


class TestDeduplication:
    """The specific, real double-counting risk this module was built to avoid."""

    def test_no_cdps_or_incorporated_towns_present(self):
        excluded_names = {"Dale City", "Woodbridge", "Centreville", "Reston", "McLean",
                           "Tuckahoe", "Leesburg"}
        target_names = {t.name for t in pe.EXTRAPOLATION_TARGETS}
        overlap = excluded_names & target_names
        assert overlap == set(), f"CDPs/incorporated towns leaked into targets: {overlap}"

    def test_none_of_the_four_drilled_down_counties_present(self):
        excluded_names = {"Loudoun", "Fairfax", "Arlington", "Prince William"}
        target_names = {t.name for t in pe.EXTRAPOLATION_TARGETS}
        overlap = excluded_names & target_names
        assert overlap == set(), f"Already-covered counties leaked into extrapolation targets: {overlap}"

    def test_roanoke_city_and_roanoke_county_both_present_and_distinct(self):
        # A real, easy-to-get-wrong case: these are two genuinely different jurisdictions
        # with confusingly similar names -- verify both survived as distinct entries with
        # their own correct populations, not merged or one silently dropped.
        names_and_pops = {t.name: t.population for t in pe.EXTRAPOLATION_TARGETS}
        assert names_and_pops.get("Roanoke County") == 96_927
        assert names_and_pops.get("Roanoke") == 98_807

    def test_target_count_matches_expected_28(self):
        # 16 counties + 12 independent cities, per the deduplicated source lists.
        assert len(pe.EXTRAPOLATION_TARGETS) == 28


class TestExtrapolationArithmetic:
    def test_single_target_mw_range_matches_independent_calculation(self):
        richmond = next(t for t in pe.EXTRAPOLATION_TARGETS if t.name == "Richmond")
        low_rate, high_rate = pe.ci_kw_per_capita_range()
        expected_low = low_rate * 239_227 / 1000
        expected_high = high_rate * 239_227 / 1000
        actual_low, actual_high = richmond.ci_mw_range()
        assert abs(actual_low - expected_low) < 0.01
        assert abs(actual_high - expected_high) < 0.01

    def test_total_is_sum_of_individual_targets_not_average(self):
        # Cross-check the aggregate against summing each target's own range independently,
        # rather than trust total_extrapolated_mw()'s own internal sum.
        manual_ci_low = sum(t.ci_mw_range()[0] for t in pe.EXTRAPOLATION_TARGETS)
        manual_ci_high = sum(t.ci_mw_range()[1] for t in pe.EXTRAPOLATION_TARGETS)
        totals = pe.total_extrapolated_mw()
        assert abs(totals["ci_mw_low"] - manual_ci_low) < 0.01
        assert abs(totals["ci_mw_high"] - manual_ci_high) < 0.01

    def test_low_bound_never_exceeds_high_bound(self):
        for t in pe.EXTRAPOLATION_TARGETS:
            ci_low, ci_high = t.ci_mw_range()
            park_low, park_high = t.parking_mw_range()
            assert ci_low <= ci_high, f"{t.name}: C&I low > high"
            assert park_low <= park_high, f"{t.name}: parking low > high"


if __name__ == '__main__':
    import sys
    sys.exit(pytest.main([__file__, '-v']))
