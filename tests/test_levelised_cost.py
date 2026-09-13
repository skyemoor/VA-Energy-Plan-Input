"""
test_levelised_cost.py

LevelisedCost -- PV(cost)/PV(demand) with terminal value.

WHY FOUR CHECKPOINTS ARE NOT AN SLCOE: averaging 2030/2035/2040/2045 weights each equally, ignores
discounting, and misses that demand grows 72% across the horizon so later years carry far more MWh.
"""
import pytest

import assumptions
from levelised_cost import LevelisedCost, undepreciated_value


def flat(cost=1.0e9, demand=100e6, lo=2026, hi=2045):
    lc = LevelisedCost()
    for y in range(lo, hi + 1):
        lc.add_year(y, cost, demand)
    return lc


class TestTheFigureItself:

    def test_flat_stream_levelises_to_its_own_unit_cost(self):
        """The check that catches most discounting errors: if cost and demand are constant, the
        discount factors cancel exactly and SLCOE is cost/demand regardless of the rate."""
        assert flat(1.0e9, 100e6).slcoe(include_terminal_value=False) == pytest.approx(10.0)

    def test_discounting_reduces_the_weight_of_later_years(self):
        """A cost stream rising over time levelises BELOW its arithmetic mean."""
        lc = LevelisedCost()
        for i, y in enumerate(range(2026, 2046)):
            lc.add_year(y, 1.0e9 * (1 + i * 0.1), 100e6)
        arithmetic = sum(1.0e9 * (1 + i * 0.1) for i in range(20)) / 20 / 100e6
        assert lc.slcoe(False) < arithmetic

    def test_uses_the_project_discount_rate_and_base_year(self):
        lc = LevelisedCost()
        assert lc.discount_rate == assumptions.WACC == 0.045
        assert lc.base_year == assumptions.BASE_YEAR == 2026

    def test_base_year_is_undiscounted(self):
        assert LevelisedCost().discount_factor(2026) == 1.0

    def test_empty_stream_raises(self):
        with pytest.raises(ValueError, match='nothing to levelise'):
            LevelisedCost().slcoe()


class TestStreamIntegrity:
    """A levelised cost over a partial stream looks identical to one over a complete stream."""

    def test_gaps_are_detected(self):
        lc = LevelisedCost()
        for y in (2030, 2035, 2040, 2045):
            lc.add_year(y, 1e9, 100e6)
        assert len(lc.missing_years()) == 12

    def test_verify_complete_raises_on_gaps(self):
        lc = LevelisedCost()
        for y in (2030, 2035, 2040, 2045):
            lc.add_year(y, 1e9, 100e6)
        with pytest.raises(ValueError, match='missing year'):
            lc.verify_complete()

    def test_the_four_checkpoints_alone_are_rejected(self):
        """The specific mistake this class exists to prevent -- levelising the checkpoints as if
        they were the stream."""
        lc = LevelisedCost(base_year=2030)
        for y in (2030, 2035, 2040, 2045):
            lc.add_year(y, 1e9, 100e6)
        with pytest.raises(ValueError, match='Levelising over a partial stream'):
            lc.verify_complete()

    def test_duplicate_year_raises(self):
        lc = LevelisedCost().add_year(2030, 1e9, 100e6)
        with pytest.raises(ValueError, match='already added'):
            lc.add_year(2030, 2e9, 100e6)

    def test_year_before_base_raises(self):
        """Discounting a pre-base year would INFLATE rather than discount it."""
        with pytest.raises(ValueError, match='precedes base_year'):
            LevelisedCost(base_year=2030).add_year(2028, 1e9, 100e6)

    def test_stream_starting_after_base_year_raises(self):
        lc = LevelisedCost(base_year=2026)
        for y in range(2030, 2046):
            lc.add_year(y, 1e9, 100e6)
        with pytest.raises(ValueError, match='levelised figure states its own period'):
            lc.verify_complete()

    def test_zero_demand_raises(self):
        with pytest.raises(ValueError, match='must be positive'):
            LevelisedCost().add_year(2030, 1e9, 0.0)


class TestTerminalValue:
    """NREL ATB across 2021/2023/2024: 'A technical life that is longer than the cost recovery
    period means RESIDUAL VALUE may be left after costs have been recovered.' With
    CRF_LIFE_YEARS = 25 against a 20-year horizon, omitting it is the choice needing defence."""

    def test_it_reduces_the_levelised_cost(self):
        lc = flat()
        lc.add_terminal_value('solar', 5.0e9)
        assert lc.slcoe(True) < lc.slcoe(False)

    def test_both_figures_are_reported(self):
        """Convention from the prior 20-year SLCOE work: with and without, so a reader can strip
        the credit out."""
        lc = flat()
        lc.add_terminal_value('solar', 5.0e9)
        d = lc.summary()
        assert d['slcoe_with_terminal_value'] < d['slcoe_without_terminal_value']

    def test_terminal_value_discounts_from_the_final_year(self):
        lc = flat()
        lc.add_terminal_value('solar', 1.0e9)
        assert lc.pv_terminal_value_usd == pytest.approx(1.0e9 * lc.discount_factor(2045))

    def test_negative_terminal_value_raises(self):
        """A negative residual is a decommissioning liability -- a different quantity, belonging in
        the final year's cost rather than as a negative credit."""
        with pytest.raises(ValueError, match='decommissioning liability'):
            LevelisedCost().add_terminal_value('gas', -1.0e9)


class TestUndepreciatedValue:

    def test_straight_line_by_remaining_life(self):
        """Built 2044, 25-year life, horizon 2045: 24 of 25 years remain."""
        assert undepreciated_value(1000.0, 2044, 2045, 25) == pytest.approx(1000.0 * 24 / 25)

    def test_fully_depreciated_asset_has_none(self):
        assert undepreciated_value(1000.0, 2020, 2045, 25) == 0.0

    def test_stranded_asset_has_zero_regardless_of_age(self):
        """The gas case at 100% compliance. Under the EC's present-value-of-future-cash-flows
        method an asset that will never run again is worth nothing, however young -- which is why
        that method was chosen over residual market value: it degrades correctly with no
        special-case rule."""
        assert undepreciated_value(1000.0, 2044, 2045, 25, strands_at_horizon=True) == 0.0

    def test_asset_built_after_the_horizon_raises(self):
        with pytest.raises(ValueError, match='has no residual value at the horizon'):
            undepreciated_value(1000.0, 2050, 2045, 25)

    def test_zero_life_raises(self):
        with pytest.raises(ValueError, match='life_years must be positive'):
            undepreciated_value(1000.0, 2040, 2045, 0)
