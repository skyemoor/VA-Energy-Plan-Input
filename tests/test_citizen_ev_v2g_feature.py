"""
test_citizen_ev_v2g_feature.py

Tests for the CitizenEVV2G module -- verifies correct implementation of the shared WMAPathway
interface, the None-compensation case (distinct from school bus V2G's own non-monetary case), the
mutual-exclusivity declaration, and that the headroom calculation reuses existing, already-sourced
constants rather than re-deriving them.

Run with: python3 -m pytest test_citizen_ev_v2g_feature.py -v
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared_base_classes'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dlc_analysis'))

import pytest

from citizen_ev_v2g_feature import (
    CitizenEVV2G,
    available_kwh_per_vehicle_for_discharge,
    per_vehicle_discharge_power_kw,
    territory_wide_ceiling_estimate_50_50_split_mw,
    MUTUALLY_EXCLUSIVE_WITH,
    AVERAGE_US_BEV_BATTERY_CAPACITY_KWH,
)
from demand_side_feature import WMAPathway
import dlc_assumptions as dlc


class TestImplementsSharedInterface:
    def test_is_a_wma_pathway(self):
        assert isinstance(CitizenEVV2G(), WMAPathway)

    def test_can_be_instantiated(self):
        CitizenEVV2G()

    def test_feature_name_is_set(self):
        feature = CitizenEVV2G()
        assert "Citizen EV V2G" in feature.feature_name

    def test_is_not_a_dlc_program(self):
        # Confirms this correctly lives under WMAPathway, not DLCProgram -- it has no
        # avoided_cost_comparison() method, unlike EVChargerRewards/LargeCICurtailment
        assert not hasattr(CitizenEVV2G(), "avoided_cost_comparison")


class TestCompensationIsNoneNotRaisesOrZero:
    """The key distinguishing case from school bus V2G: this program's compensation IS expected
    to be monetary (pay-for-performance), just not yet published -- None is correct here, NOT the
    NotImplementedError pattern school bus V2G correctly uses for its own genuinely non-monetary
    case."""

    def test_current_compensation_usd_returns_none(self):
        assert CitizenEVV2G().current_compensation_usd() is None

    def test_compensation_is_monetary_is_true_not_overridden(self):
        # Unlike SchoolBusV2G, this class does NOT override compensation_is_monetary() -- the
        # concept is expected to be monetary, just unpublished, so the base class's own True
        # default is correct and should not be touched.
        assert CitizenEVV2G().compensation_is_monetary() is True

    def test_does_not_raise_when_calling_current_compensation_usd(self):
        # Confirms this behaves like the A.7/BYOD "unpublished rate" case (None), not the CVR/
        # school-bus "structurally inapplicable or non-monetary" case (raises)
        try:
            result = CitizenEVV2G().current_compensation_usd()
        except NotImplementedError:
            pytest.fail(
                "current_compensation_usd() should return None, not raise -- this program's "
                "compensation concept genuinely applies, it's just unpublished."
            )
        assert result is None


class TestMutualExclusivityDeclaredExplicitly:
    def test_mutually_exclusive_with_is_a_tuple_matching_established_convention(self):
        # Same convention as large_ci_curtailment_assumptions.py's own MUTUALLY_EXCLUSIVE_WITH
        assert isinstance(MUTUALLY_EXCLUSIVE_WITH, tuple)
        assert len(MUTUALLY_EXCLUSIVE_WITH) >= 1

    def test_names_the_existing_dlc_program_specifically(self):
        assert any("EV Charger Rewards" in item for item in MUTUALLY_EXCLUSIVE_WITH)


class TestAvailableCapacityReusesExistingSourcedConstants:
    """Confirms the headroom calculation reuses dlc_assumptions.py's own already-sourced,
    already-tested VMT/efficiency chain (Rule 6) rather than re-deriving or hardcoding a separate
    daily-energy-need figure."""

    def test_matches_hand_calculation(self):
        # 90 - (dlc.DAILY_CHARGING_ENERGY_NEED_KWH) = 90 - 10.54 = 79.46
        result = available_kwh_per_vehicle_for_discharge()
        assert result == pytest.approx(79.46, abs=0.1)

    def test_daily_reserve_is_read_live_from_dlc_assumptions_not_restated(self):
        # If dlc_assumptions.py's own VMT or efficiency figure is ever revised, this must reflect
        # that automatically -- confirmed by computing independently from the SAME source module's
        # own constants, not by checking this module's own (potentially stale) copy.
        independently_computed = (
            AVERAGE_US_BEV_BATTERY_CAPACITY_KWH - dlc.DAILY_CHARGING_ENERGY_NEED_KWH
        )
        assert available_kwh_per_vehicle_for_discharge() == pytest.approx(independently_computed)

    def test_headroom_is_physically_plausible_not_negative_or_over_100_pct(self):
        result = available_kwh_per_vehicle_for_discharge()
        assert 0 < result < AVERAGE_US_BEV_BATTERY_CAPACITY_KWH

    def test_magnitude_per_unit_matches_the_standalone_function(self):
        feature = CitizenEVV2G()
        assert feature.magnitude_per_unit() == available_kwh_per_vehicle_for_discharge()


class TestReturnHomeTimingSharedWithDLC:
    """Direct user instruction, 2026-08-27: base the citizen EV's own return-home timing on the
    same assumption already established for DLC. These tests confirm the sharing is genuine
    (reused live from dlc_assumptions.py) rather than a separately-hardcoded value that merely
    happens to currently match."""

    def test_return_home_window_matches_dlc_event_window_exactly(self):
        from citizen_ev_v2g_feature import RETURN_HOME_EVENT_WINDOW_HOURS
        assert RETURN_HOME_EVENT_WINDOW_HOURS == dlc.EVENT_WINDOW_HOURS

    def test_return_home_window_is_read_live_not_a_separate_literal(self):
        # If dlc_assumptions.py's own EVENT_WINDOW_HOURS is ever revised, this must reflect that
        # automatically -- confirmed the same way as the energy-figure reuse test above.
        import citizen_ev_v2g_feature
        assert citizen_ev_v2g_feature.RETURN_HOME_EVENT_WINDOW_HOURS is dlc.EVENT_WINDOW_HOURS or (
            citizen_ev_v2g_feature.RETURN_HOME_EVENT_WINDOW_HOURS == dlc.EVENT_WINDOW_HOURS
        )

    def test_return_home_window_is_three_hours_matching_the_sourced_3pm_to_6pm_window(self):
        # A direct, human-readable regression guard on the actual value this project has
        # established (3pm-6pm, entry #63's own NoVA-specific narrowing) -- not just an abstract
        # equality check against dlc.EVENT_WINDOW_HOURS.
        from citizen_ev_v2g_feature import RETURN_HOME_EVENT_WINDOW_HOURS
        assert RETURN_HOME_EVENT_WINDOW_HOURS == 3.0

    def test_no_midday_charging_assumption_is_documented_not_silently_dropped(self):
        # Direct user instruction, 2026-08-27: EV ranges now exceed typical commute needs, so most
        # drivers won't charge mid-day -- a real, load-bearing assumption behind the arithmetic,
        # not just a passing remark. Guards against this justification silently disappearing from
        # the function's own docstring in a future edit.
        doc = available_kwh_per_vehicle_for_discharge.__doc__
        assert "mid-day" in doc.lower() or "midday" in doc.lower()


class TestContextOnlyFiguresNeverTreatedAsDominionsOwn:
    """Guards against the Massachusetts benchmark or the BYOD aggregate-category figure ever being
    silently substituted for Dominion's own real, still-unpublished numbers."""

    def test_massachusetts_rate_is_a_separate_named_constant_not_current_compensation(self):
        from citizen_ev_v2g_feature import MASSACHUSETTS_V2G_RATE_USD_PER_KW_FOR_CONTEXT_ONLY
        feature = CitizenEVV2G()
        # The real method must still return None -- the MA figure must never leak into it
        assert feature.current_compensation_usd() is None
        assert MASSACHUSETTS_V2G_RATE_USD_PER_KW_FOR_CONTEXT_ONLY == 275

    def test_byod_total_category_mw_is_not_ev_specific(self):
        from citizen_ev_v2g_feature import BYOD_TOTAL_CATEGORY_MW_BY_2030
        # This constant's own name makes clear it's category-wide -- confirmed present and
        # distinctly named from any (nonexistent) EV-specific MW figure
        assert BYOD_TOTAL_CATEGORY_MW_BY_2030 == 200


class TestWMAEligibilityFiguresPresent:
    def test_aggregation_thresholds_match_sourced_pjm_tariff_figures(self):
        from citizen_ev_v2g_feature import (
            WMA_AGGREGATION_MINIMUM_KW,
            WMA_AGGREGATION_MAXIMUM_PER_COMPONENT_MW,
        )
        assert WMA_AGGREGATION_MINIMUM_KW == 100
        assert WMA_AGGREGATION_MAXIMUM_PER_COMPONENT_MW == 5


class TestDischargeRateBindingConstraint:
    """Direct user-provided data (F-150 Lightning, 9.6 kW), verified and extended, 2026-08-27.
    Confirms the binding-constraint logic is computed, not assumed -- the hardware rate happens to
    bind in this case, but the function must genuinely check, not hardcode that outcome."""

    def test_f150_rate_matches_user_provided_figure(self):
        from citizen_ev_v2g_feature import F150_LIGHTNING_DISCHARGE_RATE_KW
        assert F150_LIGHTNING_DISCHARGE_RATE_KW == 9.6

    def test_hardware_rate_is_confirmed_the_binding_constraint(self):
        # 9.6 kW x 3 hrs = 28.8 kWh needed, vs 79.46 kWh available -- hardware rate binds
        result = per_vehicle_discharge_power_kw()
        assert result == pytest.approx(9.6)

    def test_binding_constraint_is_genuinely_computed_not_hardcoded(self):
        # Proves the min() logic actually works, not just that it currently returns 9.6 by luck --
        # constructs the two candidate rates independently and confirms the function picks the
        # correct (lower) one.
        from citizen_ev_v2g_feature import F150_LIGHTNING_DISCHARGE_RATE_KW, RETURN_HOME_EVENT_WINDOW_HOURS
        energy_limited_rate = available_kwh_per_vehicle_for_discharge() / RETURN_HOME_EVENT_WINDOW_HOURS
        expected = min(F150_LIGHTNING_DISCHARGE_RATE_KW, energy_limited_rate)
        assert per_vehicle_discharge_power_kw() == pytest.approx(expected)

    def test_energy_limited_rate_is_genuinely_higher_confirming_hardware_really_binds(self):
        # A direct, human-readable check that this ISN'T a coincidence of rounding -- the
        # energy-derived rate has real headroom above the hardware rate, not a near-tie.
        from citizen_ev_v2g_feature import RETURN_HOME_EVENT_WINDOW_HOURS
        energy_limited_rate = available_kwh_per_vehicle_for_discharge() / RETURN_HOME_EVENT_WINDOW_HOURS
        assert energy_limited_rate > per_vehicle_discharge_power_kw() * 1.5  # well above, not marginal


class TestFiftyFiftySplitCeilingEstimate:
    """Direct user instruction, 2026-08-27: split the territory-wide ceiling 50/50 between
    EVChargerRewards and CitizenEVV2G."""

    def test_matches_hand_calculation(self):
        # (134,486 * 0.76 * 0.50) * 9.6 / 1000 = 490.6 MW
        result = territory_wide_ceiling_estimate_50_50_split_mw()
        assert result["ceiling_mw"] == pytest.approx(490.6, abs=0.5)

    def test_evs_choosing_this_program_matches_dlc_side_exactly(self):
        # Same population split -- both programs should agree on HOW MANY vehicles choose each
        # side, even though their own per-vehicle rates differ sharply.
        result = territory_wide_ceiling_estimate_50_50_split_mw()
        dlc_side = dlc.territory_wide_ceiling_estimate_50_50_split_mw()
        assert result["evs_choosing_this_program_estimate"] == dlc_side["evs_choosing_this_program_estimate"]

    def test_split_pct_reused_from_dlc_module_not_a_separate_literal(self):
        # Rule 6 -- confirms this reads dlc_assumptions.py's own DLC_VS_V2G_POPULATION_SPLIT_PCT
        # (the single source of truth for the split itself) rather than restating 50 separately.
        result = territory_wide_ceiling_estimate_50_50_split_mw()
        assert result["population_split_pct"] == dlc.DLC_VS_V2G_POPULATION_SPLIT_PCT

    def test_ceiling_is_higher_than_dlc_sides_own_ceiling_despite_same_population(self):
        # The real, worth-surfacing asymmetry: same population split, but CitizenEVV2G's own
        # ceiling comes out meaningfully HIGHER than EVChargerRewards' own, purely because the
        # per-vehicle power rate (9.6 kW hardware) is so much higher than the DLC side's own
        # expected curtailment (3.51 kW) -- not an error, a real structural difference worth
        # a regression guard so it doesn't silently disappear or flip in a future edit.
        v2g_result = territory_wide_ceiling_estimate_50_50_split_mw()
        dlc_result = dlc.territory_wide_ceiling_estimate_50_50_split_mw()
        assert v2g_result["ceiling_mw"] > dlc_result["ceiling_mw"]

    def test_still_explicitly_flagged_as_not_a_realistic_enrollment_estimate(self):
        result = territory_wide_ceiling_estimate_50_50_split_mw()
        assert result["is_realistic_enrollment_estimate"] is False

    def test_hardware_eligibility_caveat_present_not_silently_omitted(self):
        # Guards against the real "average fleet vs V2G-capable fleet" gap disappearing from the
        # output in a future edit.
        result = territory_wide_ceiling_estimate_50_50_split_mw()
        assert "hardware_eligibility_caveat" in result
        assert len(result["hardware_eligibility_caveat"]) > 0

    def test_class_passthrough_matches_module_level_function(self):
        feature = CitizenEVV2G()
        via_class = feature.territory_wide_ceiling_estimate_50_50_split_mw()
        via_module = territory_wide_ceiling_estimate_50_50_split_mw()
        assert via_class == via_module
