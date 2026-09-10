"""
test_dlc_assumptions.py

Hand-verified tests for the EV Charger DLC per-participant magnitude calculation chain.

Run with: python3 -m pytest test_dlc_assumptions.py -v
"""
import pytest

import dlc_derived_assumptions as da


class TestChainMatchesHandCalculation:
    """Every step of the chain, verified against manual arithmetic using the module's own stated
    inputs -- an independent check, not the same calculation checking itself."""

    def test_daily_vmt_matches_hand_calculation(self):
        # 10,255 / 365 = 28.0959 mi/day
        assert da.VIRGINIA_DAILY_VMT_PER_DRIVER_MILES == pytest.approx(28.0959, abs=0.001)

    def test_daily_charging_energy_matches_hand_calculation(self):
        # 28.0959 * 0.375 = 10.536 kWh
        assert da.DAILY_CHARGING_ENERGY_NEED_KWH == pytest.approx(10.536, abs=0.01)

    def test_active_charging_session_matches_hand_calculation(self):
        # 10.536 / 9.0 = 1.171 hours
        assert da.ACTIVE_CHARGING_SESSION_HOURS == pytest.approx(1.171, abs=0.005)

    def test_probability_active_during_event_matches_hand_calculation(self):
        # 1.171 / 3.0 = 0.3903 (39.0%)
        assert da.PROBABILITY_ACTIVE_CHARGING_DURING_EVENT == pytest.approx(0.3903, abs=0.002)

    def test_expected_kw_reduction_matches_hand_calculation(self):
        # 0.3903 * 9.0 = 3.513 kW
        assert da.EXPECTED_KW_REDUCTION_PER_PARTICIPANT == pytest.approx(3.513, abs=0.02)


class TestPhysicalSanity:
    """Basic physical-plausibility guards -- catches an obviously-wrong input (e.g. a unit
    inversion, the exact class of error already caught once this session with the 4 kWh/mile vs.
    4 miles/kWh mix-up) before it silently propagates."""

    def test_ev_efficiency_in_plausible_real_world_range(self):
        # Real passenger EVs run ~0.20-0.45 kWh/mile; anything outside this is almost certainly a
        # unit error, not a real vehicle.
        assert 0.20 <= da.EV_EFFICIENCY_KWH_PER_MILE <= 0.45

    def test_charger_power_in_plausible_level2_range(self):
        assert 3.3 <= da.LEVEL2_CHARGER_POWER_KW <= 19.2  # full published Level 2 range

    def test_probability_active_during_event_is_a_valid_fraction(self):
        assert 0.0 <= da.PROBABILITY_ACTIVE_CHARGING_DURING_EVENT <= 1.0, (
            "If active charging session length ever exceeds the event window, this probability "
            "would exceed 1.0 -- physically meaningless under the flat-window model and a sign "
            "the window needs revisiting, not silently capping the value."
        )

    def test_expected_kw_reduction_does_not_exceed_charger_rated_power(self):
        assert da.EXPECTED_KW_REDUCTION_PER_PARTICIPANT <= da.LEVEL2_CHARGER_POWER_KW, (
            "A participant cannot contribute more than their own charger's full rated power -- "
            "this is an expected VALUE across the population, always bounded above by the "
            "single-charger max."
        )


class TestImpliedCurrentRate:
    def test_matches_hand_calculation(self):
        # $40 / 3.513 kW ~= $11.39/kW-yr
        result = da.implied_current_rate_usd_per_kw_yr()
        assert result == pytest.approx(11.39, abs=0.05)

    def test_is_derived_from_existing_constants_not_a_bare_literal(self):
        expected = da.ANNUAL_INCENTIVE_USD_PER_PARTICIPANT / da.EXPECTED_KW_REDUCTION_PER_PARTICIPANT
        assert da.implied_current_rate_usd_per_kw_yr() == expected


class TestProperlyPricedIncentiveRule8Parameterization:
    """Confirms every component is an overridable parameter, not hardcoded inside the function --
    Rule 8 -- so a future pass can supply a different benchmark or margin without editing this
    function's own body."""

    def test_default_margin_matches_module_constant(self):
        # Updated 2026-08-27: da.UTILITY_MARGIN_PCT was removed (consolidated into a true global,
        # entry #116) -- this module now imports DEFAULT_UTILITY_MARGIN_PCT directly rather than
        # defining its own copy, so the test references that name instead.
        result_default = da.properly_priced_incentive_usd_per_kw_yr(1000, 100)
        result_explicit = da.properly_priced_incentive_usd_per_kw_yr(
            1000, 100, utility_margin_pct=da.DEFAULT_UTILITY_MARGIN_PCT
        )
        assert result_default == result_explicit

    def test_margin_is_actually_applied_not_ignored(self):
        no_margin = da.properly_priced_incentive_usd_per_kw_yr(1000, 100, utility_margin_pct=0)
        with_margin = da.properly_priced_incentive_usd_per_kw_yr(1000, 100, utility_margin_pct=5)
        assert with_margin < no_margin
        assert with_margin == pytest.approx(1100 * 0.95)

    def test_accepts_different_benchmark_inputs(self):
        # Confirms the function is genuinely parameterized, not silently reading module constants
        # regardless of what's passed in
        low = da.properly_priced_incentive_usd_per_kw_yr(500, 50)
        high = da.properly_priced_incentive_usd_per_kw_yr(2000, 200)
        assert high > low


class TestTDExplicitlyExcluded:
    """Regression guard on the direct user decision to remove T&D from this calculation -- confirms
    it stays excluded rather than silently reintroduced in a future edit."""

    def test_no_td_constant_feeds_the_calculation(self):
        result = da.avoided_cost_comparison()
        assert result["td_included"] is False

    def test_low_bound_uses_only_capacity_and_energy_not_a_third_component(self):
        # F-Class + Southill LMP, no T&D -- if a third term were silently added, this would fail
        expected_low = da.properly_priced_incentive_usd_per_kw_yr(
            da.F_CLASS_AVOIDED_COST_USD_PER_KW_YR, da.LMP_AVOIDED_ENERGY_USD_PER_KW_SOUTHILL
        )
        result = da.avoided_cost_comparison()
        assert result["properly_priced_low_usd_per_kw_yr"] == round(expected_low, 2)


class TestAvoidedCostComparisonEndToEnd:
    def test_matches_hand_calculation(self):
        # Values updated 2026-08-26: utility margin changed from 5% to 0% (direct user decision --
        # 5% was never a sourced figure). Recomputed precisely, not guessed:
        # (713 + 90.98) * 1.00 = 803.98; (1175 + 136.29) * 1.00 = 1311.29
        result = da.avoided_cost_comparison()
        assert result["properly_priced_low_usd_per_kw_yr"] == pytest.approx(803.98, abs=0.5)
        assert result["properly_priced_high_usd_per_kw_yr"] == pytest.approx(1311.29, abs=0.5)

    def test_current_rate_is_far_below_properly_priced_range(self):
        # The core finding this section exists to establish -- a regression guard against it ever
        # silently flipping (e.g. if a future benchmark revision brought them close together, that
        # would be worth knowing, not masked by a loose test bound)
        result = da.avoided_cost_comparison()
        assert result["current_rate_as_multiple_of_low"] > 50
        assert result["current_rate_as_multiple_of_high"] > 50

    def test_low_bound_is_actually_lower_than_high_bound(self):
        result = da.avoided_cost_comparison()
        assert result["properly_priced_low_usd_per_kw_yr"] < result["properly_priced_high_usd_per_kw_yr"]

    def test_energy_component_flagged_as_upper_bound_not_silently_treated_as_realistic(self):
        result = da.avoided_cost_comparison()
        assert result["energy_component_is_upper_bound"] is True

    def test_returns_every_intermediate_value_not_just_the_final_multiple(self):
        result = da.avoided_cost_comparison()
        for key in ("current_rate_usd_per_kw_yr", "properly_priced_low_usd_per_kw_yr",
                    "properly_priced_high_usd_per_kw_yr", "current_rate_as_multiple_of_low",
                    "current_rate_as_multiple_of_high", "td_included",
                    "energy_component_is_upper_bound", "framing_note"):
            assert key in result


class TestTerritoryWideCeilingEstimate:
    """Tests for territory_wide_ceiling_estimate_mw() -- the full-adoption ceiling, direct
    user-provided data verified and extended, entry #115."""

    def test_matches_hand_calculation(self):
        # (134,486 * 0.76) * 3.5119863... / 1000 = 359.0 MW
        result = da.territory_wide_ceiling_estimate_mw()
        assert result["ceiling_mw"] == pytest.approx(359.0, abs=0.5)

    def test_evs_in_dominion_territory_matches_hand_calculation(self):
        result = da.territory_wide_ceiling_estimate_mw()
        expected = round(
            da.TOTAL_VA_REGISTERED_EVS_APRIL_2025 * da.DOMINION_SHARE_OF_VA_EVS_PCT_2021_SNAPSHOT / 100
        )
        assert result["evs_in_dominion_territory_estimate"] == expected

    def test_explicitly_flagged_as_not_a_realistic_enrollment_estimate(self):
        # The single most important field in this function's own output -- a regression guard
        # against this ever being silently treated as a realistic near-term MW figure
        result = da.territory_wide_ceiling_estimate_mw()
        assert result["is_realistic_enrollment_estimate"] is False

    def test_reuses_existing_kw_per_participant_constant_not_a_new_literal(self):
        # Confirms this is derived from the SAME already-tested per-participant figure used
        # throughout this module (Rule 6), not a separately-hardcoded number
        result = da.territory_wide_ceiling_estimate_mw()
        independently_computed_kw = (
            da.TOTAL_VA_REGISTERED_EVS_APRIL_2025
            * da.DOMINION_SHARE_OF_VA_EVS_PCT_2021_SNAPSHOT / 100
            * da.EXPECTED_KW_REDUCTION_PER_PARTICIPANT
        )
        assert result["ceiling_mw"] == pytest.approx(independently_computed_kw / 1000, abs=0.1)

    def test_dominion_2038_peak_demand_figure_present_as_context_not_conflated(self):
        result = da.territory_wide_ceiling_estimate_mw()
        assert result["dominion_own_ev_peak_demand_mw_by_2038_for_context"] == 1_600
        # Confirms this context figure is NOT equal to (and thus not silently substituted for)
        # the actual ceiling calculation -- they are genuinely different metrics
        assert result["dominion_own_ev_peak_demand_mw_by_2038_for_context"] != result["ceiling_mw"]

    def test_two_different_dominion_2030_projections_both_preserved(self):
        # Guards against either projection ever being silently dropped in favor of the other
        assert da.DOMINION_PROJECTED_VA_EVS_BY_2030_LOW == 150_000
        assert da.DOMINION_PROJECTED_VA_EVS_BY_2030_HIGH == 500_000
        assert da.DOMINION_PROJECTED_VA_EVS_BY_2030_LOW < da.DOMINION_PROJECTED_VA_EVS_BY_2030_HIGH

    def test_bev_only_figure_is_distinct_from_combined_bev_phev_total(self):
        # Confirms the two different statewide cuts (91,000 BEV-only vs 134,486 BEV+PHEV) are
        # preserved as genuinely separate constants, not conflated
        assert da.TOTAL_VA_REGISTERED_BEV_ONLY_JUNE_2024 != da.TOTAL_VA_REGISTERED_EVS_APRIL_2025
        assert da.TOTAL_VA_REGISTERED_BEV_ONLY_JUNE_2024 < da.TOTAL_VA_REGISTERED_EVS_APRIL_2025


class TestFiftyFiftySplitCeilingEstimate:
    """Tests for territory_wide_ceiling_estimate_50_50_split_mw() -- the governing estimate,
    direct user instruction 2026-08-27, splitting the Dominion-territory EV population between
    EVChargerRewards and CitizenEVV2G given their mutual exclusivity."""

    def test_is_exactly_half_the_original_100_pct_ceiling(self):
        original = da.territory_wide_ceiling_estimate_mw()
        split = da.territory_wide_ceiling_estimate_50_50_split_mw()
        assert split["ceiling_mw"] == pytest.approx(original["ceiling_mw"] / 2, abs=0.1)

    def test_matches_hand_calculation(self):
        # (134,486 * 0.76 * 0.50) * 3.5119863... / 1000 = 179.5 MW
        result = da.territory_wide_ceiling_estimate_50_50_split_mw()
        assert result["ceiling_mw"] == pytest.approx(179.5, abs=0.5)

    def test_split_pct_is_a_named_overridable_constant_not_hardcoded_inline(self):
        # Rule 8 -- confirms DLC_VS_V2G_POPULATION_SPLIT_PCT is a real, reusable constant, not a
        # bare 50 buried inside the function body
        assert da.DLC_VS_V2G_POPULATION_SPLIT_PCT == 50
        result = da.territory_wide_ceiling_estimate_50_50_split_mw()
        assert result["population_split_pct"] == da.DLC_VS_V2G_POPULATION_SPLIT_PCT

    def test_still_explicitly_flagged_as_not_a_realistic_enrollment_estimate(self):
        # A 50/50 split is still an assumption, not a sourced enrollment rate -- this flag must
        # remain False, not flip to True just because the ceiling became more refined
        result = da.territory_wide_ceiling_estimate_50_50_split_mw()
        assert result["is_realistic_enrollment_estimate"] is False

    def test_original_100_pct_function_still_directly_callable_as_reference_point(self):
        # Confirms the original function was preserved, not deleted or silently repurposed --
        # per this project's own "never silently overwrite" practice
        original = da.territory_wide_ceiling_estimate_mw()
        assert original["ceiling_mw"] == pytest.approx(359.0, abs=0.5)
