"""
test_gas_merit_order.py

Gas heat-rate tiers sourced from EIA Electric Power Annual Table 8.2 (Form EIA-860 tested heat
rates, capacity-weighted) plus EIA's vintage breakdown.

Added because the LP dispatches gas at a SINGLE marginal cost, which is one reason its hourly
energy-balance dual is perfectly flat: with one price and no operating reserve, storage arbitrages
every hour to that price. These tiers give the dual a ladder to climb -- once capacity per tier is
sourced and they are wired in.
"""
import pytest

import assumptions as a
import lp_model as lp


class TestTiersMatchEIA:

    def test_combined_cycle_and_gas_turbine_match_table_8_2(self):
        assert a.GAS_HEAT_RATE_CCGT_FLEET == 7.548
        assert a.GAS_HEAT_RATE_CT_FLEET == 10.999
        assert a.GAS_HEAT_RATE_STEAM == 10.337

    def test_modern_ccgt_is_within_eia_stated_range(self):
        """EIA: 2014+ entry typically below 7,000 Btu/kWh."""
        assert a.GAS_HEAT_RATE_CCGT_MODERN < 7.0

    def test_legacy_ccgt_sits_above_the_fleet_average(self):
        assert a.GAS_HEAT_RATE_CCGT_LEGACY > a.GAS_HEAT_RATE_CCGT_FLEET


class TestOurSimpleCycleAssumptionIsOptimistic:
    """A finding, not a defect: 9.5 describes a modern aeroderivative unit, while EIA's 2024
    gas-turbine fleet average is 11.0. Both are retained as separate tiers because they describe
    genuinely different machines -- but where the question is what the marginal peaking unit costs
    to run, 9.5 is the optimistic end."""

    def test_our_simple_cycle_beats_the_eia_fleet_average(self):
        assert a.SIMPLE_CYCLE_HEAT_RATE < a.GAS_HEAT_RATE_CT_FLEET
        gap = 1 - a.SIMPLE_CYCLE_HEAT_RATE / a.GAS_HEAT_RATE_CT_FLEET
        assert gap == pytest.approx(0.136, abs=0.01), 'about 14% better than fleet'

    def test_both_are_kept_as_distinct_tiers(self):
        labels = [l for l, _ in a.GAS_MERIT_ORDER_HEAT_RATES]
        assert 'ct_aeroderivative' in labels and 'ct_fleet' in labels


class TestMeritOrderStructure:

    def test_tiers_are_ordered_cheapest_first(self):
        rates = [hr for _, hr in a.GAS_MERIT_ORDER_HEAT_RATES]
        assert rates == sorted(rates)

    def test_the_stack_produces_a_real_cost_spread(self):
        """1.72x from cheapest to dearest rung -- the variation the flat dual currently lacks."""
        for year in (2030, 2045):
            lo = lp.gas_cost_mwh(year, heat_rate=a.GAS_MERIT_ORDER_HEAT_RATES[0][1])
            hi = lp.gas_cost_mwh(year, heat_rate=a.GAS_MERIT_ORDER_HEAT_RATES[-1][1])
            assert hi / lo == pytest.approx(1.72, abs=0.02)

    def test_capacity_per_tier_is_flagged_as_unsourced(self):
        """A merit order needs MW at each rung to bind, not just prices. Until the Virginia fleet
        split is sourced these tiers cannot be wired into the LP, and saying so prevents them
        being used as though they were complete."""
        c = a.GAS_MERIT_ORDER_CAPACITY_UNSOURCED
        assert 'NOT capacity per rung' in c
        assert 'cannot be wired into the LP' in c

    def test_the_truncated_irp_pdfs_are_recorded(self):
        """Confirmed unreadable with both pypdf and pdfplumber. Other work may depend on them."""
        assert 'truncated and unreadable' in a.GAS_MERIT_ORDER_CAPACITY_UNSOURCED
