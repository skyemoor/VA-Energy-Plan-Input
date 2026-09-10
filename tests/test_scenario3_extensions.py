"""
test_scenario3_extensions.py

Tests for the 2026-09-05 Scenario 3 extensions: utility-scale ownership/land-use split
(B.1.a-c, C.1) and the A.2/A.3/A.4 demand-side adjustment. Per SES Rule 2, each test
locks a new shared calculation to an independently-derivable baseline, not just internal
self-consistency.
"""
import numpy as np
import pytest
import scenario3_build as s3b
import dlc_assumptions as dlc


class TestUtilityScaleOwnershipSplit:
    """B.1.a-c: the three Dominion riders must partition the utility-scale 80% share
    exactly, and UtilityScalePolicy must reject a non-partitioning set of shares
    (mirrors Scenario3Policy's own __post_init__ validation pattern, SES Rule 1 --
    consistent enforcement across the two taxonomy layers, not a one-off check)."""

    def test_default_shares_sum_to_utility_share_of_total(self):
        total_solar_mw = 100_000.0
        result = s3b.utility_scale_ownership_mw(total_solar_mw)
        expected_utility_scale_total = total_solar_mw * s3b.UTILITY_SHARE
        actual_sum = sum(result.values())
        assert abs(actual_sum - expected_utility_scale_total) < 1e-6, (
            f"Rider shares sum to {actual_sum}, expected {expected_utility_scale_total} "
            f"(total_solar_mw * UTILITY_SHARE)")

    def test_equal_default_split_gives_equal_thirds(self):
        # Cross-check against an independently-computed baseline: with the default
        # equal-thirds policy, each rider should get exactly total*UTILITY_SHARE/3
        # (SES Rule 4 -- an independent arithmetic path, not just calling the function
        # again and comparing to itself).
        total_solar_mw = 90_000.0
        result = s3b.utility_scale_ownership_mw(total_solar_mw)
        expected_each = total_solar_mw * s3b.UTILITY_SHARE / 3.0
        for key in ('rider_ce_mw', 'rider_ppa_mw', 'rider_rps_mw'):
            assert abs(result[key] - expected_each) < 1e-6

    def test_non_partitioning_shares_raise(self):
        with pytest.raises(ValueError, match="Rider shares sum to"):
            s3b.UtilityScalePolicy(rider_ce_share=0.5, rider_ppa_share=0.5, rider_rps_share=0.5)

    def test_agrivoltaic_share_out_of_range_raises(self):
        with pytest.raises(ValueError, match="agrivoltaic_share_of_nonurban"):
            s3b.UtilityScalePolicy(agrivoltaic_share_of_nonurban=1.5)


class TestUtilityScaleLandUseSplit:
    """C.1: agrivoltaic vs. standard ground-mount split of the utility-scale share."""

    def test_default_90_percent_agrivoltaic(self):
        total_solar_mw = 100_000.0
        result = s3b.utility_scale_land_use_mw(total_solar_mw)
        utility_scale_mw = total_solar_mw * s3b.UTILITY_SHARE
        # Independent baseline: this project's own established 90%-of-non-urban figure
        # (Scenario3_Scope_and_Gaps.md §5.4/C.1), computed here via a separate
        # multiplication, not by re-calling the function under test.
        expected_agrivoltaic = utility_scale_mw * 0.90
        assert abs(result['agrivoltaic_mw'] - expected_agrivoltaic) < 1e-6
        assert abs(result['standard_ground_mount_mw'] - utility_scale_mw * 0.10) < 1e-6

    def test_split_sums_to_utility_scale_total(self):
        total_solar_mw = 75_000.0
        result = s3b.utility_scale_land_use_mw(total_solar_mw)
        expected_total = total_solar_mw * s3b.UTILITY_SHARE
        assert abs(sum(result.values()) - expected_total) < 1e-6


class TestDemandAdjustment:
    """A.2/A.3/A.4 demand-side adjustment, cross-checked against the underlying
    dlc_assumptions.py ceiling figure directly (SES Rule 4 -- an independent source,
    not this module's own re-derivation)."""

    def test_invalid_year_raises(self):
        demand = np.full(8760, 15000.0)
        with pytest.raises(ValueError, match="checkpoint years"):
            s3b.apply_scenario3_demand_adjustment(demand, 2033)

    def test_ev_dlc_ceiling_matches_dlc_assumptions_directly(self):
        # Cross-check: the 2035+ (flat 90% adoption) EV DLC reduction should equal
        # dlc_assumptions.py's own ceiling figure directly, not a re-derived copy.
        expected_ceiling = dlc.territory_wide_ceiling_estimate_50_50_split_mw()['ceiling_mw']
        computed = s3b.ev_charger_dlc_reduction_mw(2035)
        assert abs(computed - expected_ceiling * 0.90) < 1e-6

    def test_adoption_rate_at_ramp_endpoints(self):
        assert abs(s3b.residential_ev_dlc_adoption_rate(2026) - 0.02) < 1e-9
        assert abs(s3b.residential_ev_dlc_adoption_rate(2035) - 0.90) < 1e-9
        assert abs(s3b.residential_ev_dlc_adoption_rate(2040) - 0.90) < 1e-9  # flat after 2035

    def test_adjustment_only_reduces_demand_during_event_window(self):
        demand = np.full(8760, 15000.0)
        adjusted = s3b.apply_scenario3_demand_adjustment(demand, 2030)
        hour_of_day = np.arange(8760) % 24
        event_mask = (hour_of_day >= 15) & (hour_of_day < 18)
        # Outside the event window, only the flat A.3/A.4 reduction should apply --
        # verify the reduction is IDENTICAL across all non-event hours (a real bug this
        # guards against: an off-by-one in the event mask silently touching adjacent
        # hours differently would break this exact-equality check).
        non_event_reductions = demand[~event_mask] - adjusted[~event_mask]
        assert np.allclose(non_event_reductions, non_event_reductions[0]), (
            "Non-event-window hours should all see the identical flat A.3/A.4 "
            "reduction -- found variation, suggesting the event mask leaked into "
            "hours it shouldn't have.")
        # Inside the event window, the reduction should be strictly larger (flat
        # reduction PLUS the EV DLC MW).
        event_reductions = demand[event_mask] - adjusted[event_mask]
        assert np.all(event_reductions > non_event_reductions[0]), (
            "Event-window hours should show a larger reduction than non-event hours "
            "(flat A.3/A.4 reduction plus EV DLC), found at least one that didn't.")

    def test_does_not_mutate_input(self):
        demand = np.full(8760, 15000.0)
        original = demand.copy()
        s3b.apply_scenario3_demand_adjustment(demand, 2030)
        assert np.array_equal(demand, original), "Input demand array was mutated in place"


if __name__ == '__main__':
    import sys
    sys.exit(pytest.main([__file__, '-v']))
