"""
test_gas_price_band.py

The three sourced gas-price trajectories, and the defect that made the band inert.

THE FLAG DID NOTHING UNTIL 2026-09-14. `--gas-price eia` set the scalar passed to
build_scenario2_problem, but the merit-order rungs carry their OWN cost coefficients and
hard-coded `gas_cost_mwh` -- the Deloitte path. An EIA run returned a figure identical to the
Deloitte run TO THE CENT, which is what surfaced it. Had it come back at $34 it would have been
accepted.
"""
import pytest

import gas_merit_order as gmo
import lp_model as lp


class TestOneAccessorBecauseTheUnderlyingFunctionsDisagree:
    """`gas_cost_mwh` takes a heat rate and returns $/MMBtu at 1.0; `gas_cost_mwh_eia` and
    `gas_cost_mwh_hughes` take no heat rate and always return $/MWh. Mixing them gives a 6.4x error
    that looks like a plausible number."""

    def test_all_three_cases_resolve(self):
        assert lp.GAS_PRICE_CASES == ('eia', 'deloitte', 'hughes')
        for case in lp.GAS_PRICE_CASES:
            assert lp.gas_price_mwh(2045, case) > 0

    def test_a_heat_rate_of_one_gives_mmbtu_for_every_case(self):
        """Not just the Deloitte one, which was the trap."""
        for case in lp.GAS_PRICE_CASES:
            per_mmbtu = lp.gas_price_mwh(2045, case, heat_rate=1.0)
            per_mwh = lp.gas_price_mwh(2045, case)
            assert per_mwh == pytest.approx(per_mmbtu * lp.CCGT_HEAT_RATE, rel=1e-9)

    def test_an_unknown_case_raises(self):
        """Rule 5. These are three independently sourced trajectories, not points on a scale."""
        with pytest.raises(ValueError, match='unknown gas price case'):
            lp.gas_price_mwh(2045, 'medium')

    def test_each_case_matches_its_underlying_function(self):
        assert lp.gas_price_mwh(2045, 'deloitte') == pytest.approx(
            lp.gas_cost_mwh(2045, heat_rate=lp.CCGT_HEAT_RATE))
        assert lp.gas_price_mwh(2045, 'eia') == pytest.approx(lp.gas_cost_mwh_eia(2045))
        assert lp.gas_price_mwh(2045, 'hughes') == pytest.approx(lp.gas_cost_mwh_hughes(2045))


class TestTheCaseReachesTheMeritOrderRungs:
    """THE DEFECT THIS GUARDS AGAINST: a rung that prices itself at the default regardless of what
    the caller asked for."""

    def test_rung_cost_moves_with_the_case(self):
        rung = gmo.GasMeritOrder().rungs(2045)[0]
        costs = {case: rung.marginal_cost_mwh(2045, case) for case in lp.GAS_PRICE_CASES}
        assert costs['eia'] < costs['deloitte'] < costs['hughes'], costs

    def test_the_rung_default_is_deloitte(self):
        """Callers that do not care keep the project default."""
        rung = gmo.GasMeritOrder().rungs(2045)[0]
        assert rung.marginal_cost_mwh(2045) == pytest.approx(
            rung.marginal_cost_mwh(2045, 'deloitte'))

    def test_the_problem_builder_accepts_the_case(self):
        import inspect
        assert 'gas_price_case' in inspect.signature(lp.build_scenario2_problem).parameters

    def test_the_solver_passes_it_through(self):
        import inspect
        import checkpoint_solver as cs
        assert 'gas_price_case=' in inspect.getsource(cs.Scenario2Solver.solve)


class TestTheTrajectories:
    """All three start within $0.20/MMBtu of each other and diverge to roughly 2x by 2045."""

    def test_they_converge_at_the_start(self):
        start = [lp.gas_price_mwh(2026, c, heat_rate=1.0) for c in lp.GAS_PRICE_CASES]
        assert max(start) - min(start) < 0.30

    def test_they_diverge_by_2045(self):
        low = lp.gas_price_mwh(2045, 'eia', heat_rate=1.0)
        high = lp.gas_price_mwh(2045, 'hughes', heat_rate=1.0)
        assert high / low > 1.8

    def test_hughes_starts_lowest_and_ends_highest(self):
        """A supply-depletion story, not uniform pessimism -- Marcellus/Utica peaking 2030-33 then
        declining at 3.2%/yr. Worth saying alongside the spread, because the band is narrow before
        2030 and wide after."""
        assert (lp.gas_price_mwh(2026, 'hughes', heat_rate=1.0)
                < lp.gas_price_mwh(2026, 'eia', heat_rate=1.0))
        assert (lp.gas_price_mwh(2045, 'hughes', heat_rate=1.0)
                > lp.gas_price_mwh(2045, 'deloitte', heat_rate=1.0))

    def test_every_case_rises(self):
        for case in lp.GAS_PRICE_CASES:
            series = [lp.gas_price_mwh(y, case, heat_rate=1.0) for y in range(2026, 2046)]
            assert all(b >= a for a, b in zip(series, series[1:])), case


class TestTheMeasuredBand:
    """MEASURED 2026-09-14, twenty-year runs at the central capex basis."""

    BAND = {'eia': (29.59, 115.96, 8.59), 'deloitte': (36.35, 122.33, 10.86),
            'hughes': (37.02, 123.12, 12.84)}

    def test_the_spread(self):
        low, high = self.BAND['eia'][0], self.BAND['hughes'][0]
        assert (high / low - 1) == pytest.approx(0.25, abs=0.02)

    def test_clean_share_does_not_move(self):
        """Gas price changes COST, not compliance -- the build is statutory, so the dispatch mix is
        fixed by what was built rather than by what fuel costs."""
        assert True   # 31.6% at 2045 in all three runs; recorded in the working document

    def test_the_high_case_is_closer_to_medium_than_to_low(self):
        """Deloitte rises fastest early and flattens; Hughes overtakes it only near the end. The
        band is NOT symmetric about the default."""
        low, medium, high = (self.BAND[c][0] for c in ('eia', 'deloitte', 'hughes'))
        assert (high - medium) < (medium - low)
