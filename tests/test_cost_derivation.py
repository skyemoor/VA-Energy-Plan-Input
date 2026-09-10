"""
test_cost_derivation.py

Tests for the CostDerivation hierarchy, consolidating what were two suites against two
free-standing modules (test_peaker_capex.py and the cost half of
test_large_ci_curtailment_feature.py).

Both modules separately performed capex-lookup-then-annualize. Testing the hierarchy means the
annualization is tested once, and the subclass tests cover only what is subclass-specific.
"""
import pytest

import assumptions
from cost_derivation import AnnualizedCost, PeakerCost, AvoidedCapacityCost


class TestAnnualizedCostSharedBase:
    """The capex-to-annual conversion, tested once rather than in each subclass."""

    def test_annual_is_capital_recovery_plus_fixed_om(self):
        c = AnnualizedCost(1000.0, 10.0, capital_recovery_factor=0.06)
        assert c.annual_usd_per_kw_yr() == pytest.approx(1000.0 * 0.06 + 10.0)

    def test_default_crf_is_the_thirty_year_figure_from_assumptions(self):
        assert AnnualizedCost(1000.0).capital_recovery_factor == assumptions.CCGT_CRF

    def test_capital_and_annual_totals_are_distinguishable(self):
        """They differ by roughly a factor of fifteen and have been confused in this codebase."""
        c = AnnualizedCost(1000.0, 10.0)
        assert c.total_capital_dollars(100.0) > 10 * c.total_annual_dollars(100.0)

    def test_negative_capex_raises(self):
        with pytest.raises(ValueError, match='non-negative'):
            AnnualizedCost(-1.0)


class TestUnitsPlausibilityCheck:
    """Guards the error that reached a published finding: installed capex ($/kW, one-time) used as
    annual avoided capacity cost ($/kW-yr). What caught it was that PJM has never cleared anywhere
    near $713/kW-yr."""

    def test_plausible_annual_value_passes(self):
        assert AnnualizedCost(1425.0, 7.0).units_plausibility_check() is None

    def test_capex_mistaken_for_annual_is_flagged(self):
        """$713/kW treated as though already annual -- the actual historical error."""
        assert AnnualizedCost(0.0, 713.0).units_plausibility_check() is not None

    def test_the_flag_names_the_specific_confusion(self):
        msg = AnnualizedCost(0.0, 1175.0).units_plausibility_check()
        assert 'one-time' in msg and 'kW-yr' in msg

    def test_ceiling_is_pjms_highest_cleared_price(self):
        """$325/MW-day, the 2026/27 BRA cap, as a plausibility bound rather than a cost input."""
        assert AnnualizedCost.PJM_HIGHEST_CLEARED_CAPACITY_PRICE_USD_PER_KW_YR == pytest.approx(118.6, abs=0.1)


class TestPeakerCost:

    def test_size_tiers_match_sourced_breakpoints(self):
        assert PeakerCost(30).size_tier() == 'small'
        assert PeakerCost(105).size_tier() == 'medium'
        assert PeakerCost(418).size_tier() == 'large'

    def test_size_cost_inversion_preserved(self):
        """Smaller units cost MORE per kW -- confirmed independently by Gas Turbine World (105 MW
        at $1,175/kW against 237 MW at $713/kW) and by USP&E's tiers. Locked because it inverts
        intuition and a future edit might 'correct' it."""
        assert PeakerCost(30).capex_usd_per_kw > PeakerCost(418).capex_usd_per_kw

    def test_cases_are_ordered(self):
        assert (PeakerCost(237, 'low').capex_usd_per_kw
                < PeakerCost(237, 'central').capex_usd_per_kw
                < PeakerCost(237, 'high').capex_usd_per_kw)

    def test_adders_apply(self):
        base = PeakerCost(237).capex_usd_per_kw
        assert PeakerCost(237, dual_fuel=True).capex_usd_per_kw == pytest.approx(
            base + assumptions.PEAKER_DUAL_FUEL_ADDER_KW)
        assert PeakerCost(237, fast_track=True).capex_usd_per_kw == pytest.approx(
            base * (1 + assumptions.PEAKER_FAST_TRACK_PREMIUM_FRACTION))

    def test_fuel_type_selects_its_own_fixed_om(self):
        assert (PeakerCost(105, fuel_type='aeroderivative').fixed_om_usd_per_kw_yr
                > PeakerCost(237, fuel_type='f_class').fixed_om_usd_per_kw_yr)

    def test_peaker_is_cheaper_per_kw_than_ccgt(self):
        import lp_model
        assert PeakerCost(237).capex_usd_per_kw < lp_model.ccgt_capex_kw(2030)

    def test_units_required_is_not_silently_rounded(self):
        """Rounding up to whole units is a procurement decision for the caller."""
        n = PeakerCost(237).units_required(2503.0)
        assert n != int(n)

    def test_invalid_case_raises(self):
        with pytest.raises(ValueError, match="'low', 'central' or 'high'"):
            PeakerCost(237, case='expected')


class TestAvoidedCapacityCost:

    def test_derivation_reproduces_entry_82_from_its_own_original_inputs(self):
        """Entry #82's published 40.7%/70.9% came from Gas Turbine World costs since superseded.
        Passing those original inputs explicitly confirms the derivation logic is unchanged,
        without the historical values living anywhere as constants (Rule 8)."""
        for capex, fom, expected in [(1175.0, 16.30, 40.7), (713.0, 7.00, 70.9)]:
            annual = AnnualizedCost(capex, fom).annual_usd_per_kw_yr()
            assert round(36.0 / annual * 100, 1) == pytest.approx(expected, abs=0.1)

    def test_comparison_is_live_not_frozen(self):
        low = AvoidedCapacityCost(case='low').comparison()
        high = AvoidedCapacityCost(case='high').comparison()
        assert (high['fclass_incentive_as_pct_of_avoided_cost']
                < low['fclass_incentive_as_pct_of_avoided_cost'])

    def test_current_costs_give_roughly_a_third(self):
        """~35-38% at central case, against 41-71% on the superseded costs -- tighter and lower."""
        r = AvoidedCapacityCost().comparison()
        assert 30 <= r['aeroderivative_incentive_as_pct_of_avoided_cost'] <= 40
        assert 33 <= r['fclass_incentive_as_pct_of_avoided_cost'] <= 43

    def test_scope_excludes_transmission_and_distribution(self):
        """Percentages are an UPPER bound; including T&D would lower them."""
        r = AvoidedCapacityCost().comparison()
        assert r['td_included'] is False
        assert 'upper bound' in r['scope_note']

    def test_default_incentive_sourced_from_assumptions(self):
        assert (AvoidedCapacityCost().current_incentive_usd_per_kw_yr
                == assumptions.LARGE_CI_COMPENSATION_USD_PER_KW_YEAR)
