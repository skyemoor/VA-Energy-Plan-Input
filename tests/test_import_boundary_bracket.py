"""
test_import_boundary_bracket.py

How much of Scenario 2's new gas is a consequence of forbidding imports.

Virginia imports about 20% of its energy from PJM and this model forbids imports entirely (issue
#3), so the solver builds in-state capacity to cover energy Dominion actually buys.
"""
import pytest

import assumptions as a


class TestTheBoundaryIsRecorded:
    def test_the_import_share(self):
        assert a.VIRGINIA_IMPORT_SHARE_OF_ENERGY == 0.20

    def test_the_disclosure_says_to_report_a_bracket(self):
        """Reporting 6,547 MW alone would let a reviewer who knows Virginia imports 20% find the
        problem before we did."""
        assert 'Report the bracket' in a.VIRGINIA_IMPORTS_ARE_NOT_MODELLED

    def test_it_names_the_measured_effect(self):
        assert '6,547 MW to 2,000 MW' in a.VIRGINIA_IMPORTS_ARE_NOT_MODELLED


class TestTheMeasuredBracket:
    """MEASURED 2026-09-14 at 2045: new combined-cycle capacity reaching zero unserved energy,
    against demand reduced to stand in for an import allowance."""

    MEASURED = {0.00: 6_547, 0.10: 5_000, 0.20: 2_000}

    def test_roughly_seventy_percent_is_the_boundary(self):
        at_zero, at_actual = self.MEASURED[0.00], self.MEASURED[0.20]
        assert (at_zero - at_actual) / at_zero == pytest.approx(0.69, abs=0.02)

    def test_the_response_is_non_linear(self):
        """The first 10% removes 1,547 MW, the second removes 3,000 -- the peak coming off the
        steep part of the load duration curve."""
        first = self.MEASURED[0.00] - self.MEASURED[0.10]
        second = self.MEASURED[0.10] - self.MEASURED[0.20]
        assert second > first * 1.5

    def test_the_low_end_is_a_lower_bound_not_an_estimate(self):
        """A flat demand reduction is MORE GENEROUS than imports, which are dispatchable and shaped
        -- available when PJM is long. And in a scarcity year PJM may be tight exactly when Virginia
        is, so the upper bound is not absurd either. The truth sits between."""
        assert 'LOWER bound' in open(a.__file__).read()


class TestObservedCapacityFactorIsABenchmarkNotAConstraint:
    """Capacity factor is a dispatch OUTCOME. The observed values carry three confounds that would
    not transfer to 2045: regional supply, merchant-versus-rate-base ownership, and market
    conditions. Availability is what physically limits a plant."""

    OBSERVED_3YR = {'ccgt_modern': 0.668, 'ccgt_fleet': 0.478, 'ct_fleet': 0.070}

    def test_the_merit_order_is_visible_in_the_observed_data(self):
        """66.8% -> 47.8% -> 7.0% tracks heat rate 6.40 -> 7.55 -> 11.00, which is PJM dispatching
        on efficiency and confirms the rung structure independently."""
        heat_rates = dict(a.GAS_MERIT_ORDER_HEAT_RATES)
        rungs = ['ccgt_modern', 'ccgt_fleet', 'ct_fleet']
        cfs = [self.OBSERVED_3YR[r] for r in rungs]
        hrs = [heat_rates[r] for r in rungs]
        assert all(x > y for x, y in zip(cfs, cfs[1:])), 'capacity factor must fall'
        assert all(x < y for x, y in zip(hrs, hrs[1:])), 'heat rate must rise'

    def test_no_capacity_factor_ceiling_is_imposed(self):
        """Imposing 66.8% would carry today's regional supply, ownership mix and gas prices into
        2045, and would tell the model a plant cannot do something it can."""
        assert not hasattr(a, 'GAS_MAX_CAPACITY_FACTOR')
        assert not hasattr(a, 'CCGT_CAPACITY_FACTOR_CEILING')

    def test_availability_is_the_constraint(self):
        """92%, flat, covering forced outages and planned maintenance together."""
        assert 0.85 <= a.GAS_AVAILABILITY_FACTOR <= 0.95

    def test_observed_capacity_factor_does_not_exceed_availability(self):
        """A cross-check the plant data now makes possible: a rung cannot run above the fraction of
        time it is available. Greensville's 74.3% in 2024 puts a floor under the 92%."""
        assert max(self.OBSERVED_3YR.values()) < a.GAS_AVAILABILITY_FACTOR
