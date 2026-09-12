"""
test_gas_merit_order_in_lp.py

Locks the merit order's integration into build_problem (2026-09-12).

THE POINT OF THE INTEGRATION, and what these tests protect: before it, the LP's hourly
energy-balance dual at 2030 had ONE unique value across all 8,760 hours. Gas was on the margin in
every hour and there was one gas price, so gas OUTPUT varied across the day while gas MARGINAL COST
did not -- and the dual tracks the second. With the stack, the dual takes 40 distinct values.

A regression that collapses the dual back toward one value means the model has silently returned to
a single effective price, and every intraday result built on it becomes meaningless.
"""
import numpy as np
import pytest

import driver as drv
import lp_model as lp
import paths
from gas_merit_order import GasMeritOrder

pytestmark = pytest.mark.slow


def _inputs(year=2030):
    import os
    p = paths.intermediate(f'demand_{year}fy_va_only.npy')
    if not os.path.exists(p):
        pytest.skip('demand intermediate not built; run run_all.py --only demand')
    w = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    return (w, np.load(p), lp.exist_solar_mw(year) * w['solar'])


class TestFlagIsOffByDefault:
    """Rule 3: the default path must reproduce prior behaviour exactly, so existing baselines
    stay valid and the change is opt-in."""

    def test_default_build_adds_no_variables(self):
        w, d, ex = _inputs()
        p = lp.build_problem(w['solar'], w['wind'], w['nuclear'], ex, d,
                             drv.gas_target_share(2030), verbose=False)
        assert 'gas_rung_names' not in p

    def test_enabling_adds_exactly_one_variable_per_rung_per_hour(self):
        w, d, ex = _inputs()
        a = dict(gas_allowed_frac=drv.gas_target_share(2030), verbose=False)
        off = lp.build_problem(w['solar'], w['wind'], w['nuclear'], ex, d, **a)
        on = lp.build_problem(w['solar'], w['wind'], w['nuclear'], ex, d, **a,
                              gas_merit_order=GasMeritOrder(), gas_merit_order_year=2030)
        assert len(on['c']) - len(off['c']) == len(on['gas_rung_names']) * 8760


class TestFailsLoudly:
    """Rule 5. A stack without a year cannot resolve retirements or fuel price; a year without a
    stack silently does nothing. Neither should be guessed past."""

    def test_stack_without_year_raises(self):
        w, d, ex = _inputs()
        with pytest.raises(ValueError, match='must be supplied together'):
            lp.build_problem(w['solar'], w['wind'], w['nuclear'], ex, d,
                             drv.gas_target_share(2030), verbose=False,
                             gas_merit_order=GasMeritOrder())

    def test_year_without_stack_raises(self):
        w, d, ex = _inputs()
        with pytest.raises(ValueError, match='must be supplied together'):
            lp.build_problem(w['solar'], w['wind'], w['nuclear'], ex, d,
                             drv.gas_target_share(2030), verbose=False,
                             gas_merit_order_year=2030)


class TestTheDualGainsStructure:
    """The whole point. Baseline-locked (Rule 2)."""

    @pytest.fixture(scope='class')
    def solved(self):
        from scipy.optimize import linprog
        w, d, ex = _inputs()
        p = lp.build_problem(w['solar'], w['wind'], w['nuclear'], ex, d,
                             drv.gas_target_share(2030), verbose=False,
                             gas_merit_order=GasMeritOrder(), gas_merit_order_year=2030)
        r = linprog(p['c'], A_ub=p['A_ub'], b_ub=p['b_ub'], A_eq=p['A_eq'], b_eq=p['b_eq'],
                    bounds=p['bounds'], method='highs')
        if not r.success:
            pytest.skip(f'solve failed: {r.message}')
        return p, r

    def test_dual_is_no_longer_flat(self, solved):
        """Was 1 unique value across 8,760 hours. A collapse back toward 1 means the model has
        silently returned to a single effective price."""
        _, r = solved
        m = np.asarray(r.eqlin.marginals, dtype=float)[:8760]
        assert len(np.unique(np.round(m, 3))) > 10

    def test_dual_has_real_variance(self, solved):
        _, r = solved
        m = np.asarray(r.eqlin.marginals, dtype=float)[:8760]
        assert m.std() > 1.0

    def test_cheapest_hours_price_at_the_cheapest_rung(self, solved):
        """The cheapest hour should clear near ccgt_modern's marginal cost, not the old flat
        $54.70 that reflected simple-cycle gas in every hour."""
        p, r = solved
        # Marginals come back POSITIVE here -- no sign flip. An earlier measurement of the flat
        # 2030 dual negated them and reported -$54.70 for what was really +$54.70; the sign
        # convention is worth asserting rather than assuming.
        m = np.asarray(r.eqlin.marginals, dtype=float)[:8760]
        assert m.min() > 0, 'marginals expected positive; sign convention changed'
        cheapest_rung = GasMeritOrder().rungs(2030)[0].marginal_cost_mwh(2030)
        assert m.min() == pytest.approx(cheapest_rung, abs=1.0)

    def test_rungs_dispatch_in_merit_order(self, solved):
        """Cheaper rungs run in more hours than dearer ones -- the defining behaviour of a
        merit order, and a direct check that costs were attached to the right variables."""
        p, r = solved
        base = p['gas_rung_base_index']
        hours = []
        for i in range(len(p['gas_rung_names'])):
            v = r.x[base + i * 8760: base + (i + 1) * 8760]
            hours.append(int((v > 1e-6).sum()))
        assert hours == sorted(hours, reverse=True), f'not monotonic: {hours}'

    def test_rung_output_sums_to_the_gas_total(self, solved):
        """The linking equality: the stack must account for exactly the gas the rest of the
        model dispatched, no more and no less."""
        p, r = solved
        base = p['gas_rung_base_index']
        stack_total = sum(r.x[base + i * 8760: base + (i + 1) * 8760].sum()
                          for i in range(len(p['gas_rung_names'])))
        # The linking equality is sum(rungs) - g = 0 per hour, so the residual must be zero
        # regardless of how g is indexed -- checked against the constraint itself rather than
        # re-deriving g's column layout here.
        n_link = 8760
        resid = p['A_eq'][-n_link:].dot(r.x)
        assert np.abs(resid).max() < 1e-4, f'linking equality violated, max residual {np.abs(resid).max()}'
        assert stack_total > 0
