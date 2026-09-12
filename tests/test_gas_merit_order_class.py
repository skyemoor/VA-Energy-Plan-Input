"""
test_gas_merit_order_class.py

Baseline-locked tests for GasMeritOrder (Rule 2).

The class exists because the LP's hourly dual has zero variance at 2030: gas is marginal in every
hour and there is one gas price, so gas OUTPUT varies across the day while gas MARGINAL COST does
not. These tests lock the spread the stack produces, because that spread is the whole point -- if
it collapses, the model has silently returned to a single effective price.
"""
import pytest

import assumptions
from gas_merit_order import GasMeritOrder, GasRung


@pytest.fixture
def stack():
    return GasMeritOrder()


class TestTheStackProducesARealSpread:
    """The reason the class exists. Locked to baselines so a regression is visible."""

    def test_2030_spread(self, stack):
        lo, hi = stack.marginal_cost_range_mwh(2030)
        assert hi - lo == pytest.approx(26.83, abs=0.05)

    def test_2045_spread(self, stack):
        lo, hi = stack.marginal_cost_range_mwh(2045)
        assert hi - lo == pytest.approx(33.85, abs=0.05)

    def test_spread_widens_with_the_fuel_price_trajectory(self, stack):
        """Heat-rate differences multiply the fuel price, so a rising trajectory widens the stack
        in absolute terms while the ratio stays fixed."""
        s30 = stack.marginal_cost_range_mwh(2030)
        s45 = stack.marginal_cost_range_mwh(2045)
        assert (s45[1] - s45[0]) > (s30[1] - s30[0])

    def test_rungs_are_ordered_cheapest_first(self, stack):
        for year in (2030, 2045):
            costs = [r.marginal_cost_mwh(year) for r in stack.rungs(year)]
            assert costs == sorted(costs)

    def test_ct_fleet_is_the_dearest_rung(self, stack):
        """It is the price-setting rung at peak, which is why its VOM and heat rate both being
        understated mattered."""
        assert stack.rungs(2045)[-1].name == 'ct_fleet'


class TestCapacityAndRetirements:

    def test_nameplate_sums_to_the_filed_total_before_any_retirement(self, stack):
        assert sum(stack.nameplate_mw_by_rung(2030).values()) == pytest.approx(
            assumptions.GAS_DOMINION_OWNED_NAMEPLATE_MW, abs=0.1)

    def test_availability_derates_uniformly(self, stack):
        name = stack.nameplate_mw_by_rung(2030)
        avail = stack.available_capacity_mw(2030)
        for r in name:
            assert avail[r] == pytest.approx(name[r] * assumptions.GAS_AVAILABILITY_FACTOR)

    def test_bear_garden_retires_from_ccgt_fleet_in_2041(self, stack):
        """Retirements are plant-specific, so rung totals move at different times -- which is why
        capacity is summed from the per-plant table rather than pre-summed rung figures."""
        before = stack.nameplate_mw_by_rung(2040)['ccgt_fleet']
        after = stack.nameplate_mw_by_rung(2041)['ccgt_fleet']
        assert before - after == pytest.approx(559.0, abs=0.1)

    def test_warren_county_retires_from_ccgt_modern_in_2044(self, stack):
        before = stack.nameplate_mw_by_rung(2043)['ccgt_modern']
        after = stack.nameplate_mw_by_rung(2044)['ccgt_modern']
        assert before - after == pytest.approx(1_472.2, abs=0.1)

    def test_retirements_hit_different_rungs(self, stack):
        """Bear Garden is ccgt_fleet, Warren County is ccgt_modern. A single fleet-wide retirement
        figure would lose that, and the stack shape matters more than the total."""
        p = assumptions.GAS_PLANT_NAMEPLATE_MW_BY_RUNG
        assert p['Bear Garden'][0] != p['Warren County'][0]


class TestVOMIsRungSpecific:

    def test_ct_vom_exceeds_ccgt_vom(self, stack):
        """NREL ATB: NGCT $5.00 vs NGCC $2.00 (2022); OCGT $4.49 vs CCGT $1.61 (2020). Using
        CCGT's figure for peakers understated their marginal cost."""
        assert assumptions.CT_VOM_MWH > assumptions.CCGT_VOM_MWH

    def test_ct_rung_carries_the_ct_vom(self, stack):
        ct = [r for r in stack.rungs(2045) if r.name == 'ct_fleet'][0]
        assert ct.vom_mwh == assumptions.CT_VOM_MWH

    def test_ccgt_rungs_carry_the_ccgt_vom(self, stack):
        for r in stack.rungs(2045):
            if r.name.startswith('ccgt'):
                assert r.vom_mwh == assumptions.CCGT_VOM_MWH


class TestFailsLoudly:
    """Rule 5."""

    def test_invalid_availability_raises(self):
        with pytest.raises(ValueError, match='availability_factor must be'):
            GasMeritOrder(availability_factor=0.0)
        with pytest.raises(ValueError, match='availability_factor must be'):
            GasMeritOrder(availability_factor=1.5)

    def test_output_beyond_the_stack_raises_rather_than_clamping(self, stack):
        """Silently returning the dearest rung would hide an infeasibility -- something above the
        stack must serve it, and neither imports nor scarcity are modelled."""
        with pytest.raises(ValueError, match='exceeds available stack capacity'):
            stack.marginal_rung_at_output(2045, 99_999.0)

    def test_negative_output_raises(self, stack):
        with pytest.raises(ValueError, match='non-negative'):
            stack.marginal_rung_at_output(2045, -1.0)

    def test_marginal_rung_identifies_the_price_setting_step(self, stack):
        cheap = stack.marginal_rung_at_output(2045, 100.0)
        dear = stack.marginal_rung_at_output(2045, 6_000.0)
        assert cheap.name == 'ccgt_modern'
        assert dear.marginal_cost_mwh(2045) > cheap.marginal_cost_mwh(2045)


class TestEmptyRungsAreDropped:
    def test_fully_retired_rung_is_not_returned(self):
        """A zero-capacity step is a trap for a caller iterating to find the marginal unit."""
        s = GasMeritOrder(retirement_years={'Bear Garden': 2030, 'Possum Point': 2030})
        assert 'ccgt_fleet' not in [r.name for r in s.rungs(2035)]
        assert 'ccgt_fleet' in [r.name for r in s.rungs(2035, include_empty=True)]
