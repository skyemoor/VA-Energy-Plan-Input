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


class TestCapacityPerRung:
    """Source: Dominion Energy Form ARS FY2023 (SEC), 'Virginia Power Utility Generation', net
    summer capability -- the filed, audited figures. Capacity figures vary by source (Brunswick is
    1,376 in the 10-K, 1,472 in a state inventory, '1,300' in press coverage); the 10-K column is
    used consistently because it is internally consistent across plants."""

    def test_rung_capacities_sum_to_the_filed_total(self):
        assert sum(a.GAS_MERIT_ORDER_CAPACITY_MW.values()) == a.GAS_DOMINION_OWNED_TOTAL_MW == 8_195.0

    def test_modern_ccgt_rung_is_the_three_confirmed_2014_plus_plants(self):
        """Greensville 1,605 (2018) + Brunswick 1,376 (2016) + Warren County 1,349 (2014)."""
        assert a.GAS_MERIT_ORDER_CAPACITY_MW['ccgt_modern'] == 1_605 + 1_376 + 1_349

    def test_ct_capacity_is_explicitly_unallocated_not_assigned_to_a_tier(self):
        """2,066 MW across a 14% marginal-cost difference, on the units that set peak prices.
        Assigning it to either tier without sourcing would be a guess with real consequences."""
        assert 'ct_unallocated' in a.GAS_MERIT_ORDER_CAPACITY_MW
        assert 'ct_aeroderivative' not in a.GAS_MERIT_ORDER_CAPACITY_MW
        assert 'ct_fleet' not in a.GAS_MERIT_ORDER_CAPACITY_MW
        assert 'NOT split' in a.GAS_CT_SPLIT_UNRESOLVED

    def test_the_capacity_basis_discrepancy_is_recorded(self):
        """8,195 MW Dominion-owned against Schedule A's 9,362 MW. Probably IPPs, not documented,
        and the two figures are used by different parts of this project."""
        c = a.GAS_CAPACITY_BASIS_UNRECONCILED
        assert '8,195' in c and '9,362' in c
        assert 'Resolve before wiring the merit order into the LP' in c

    def test_legacy_rung_vintages_are_flagged_provisional(self):
        """Possum Point, Chesterfield and Gordonsville CODs are unconfirmed, so their assignment
        to ccgt_legacy rests on inference rather than sourcing."""
        src = open(a.__file__).read()
        assert 'VINTAGES UNCONFIRMED' in src
