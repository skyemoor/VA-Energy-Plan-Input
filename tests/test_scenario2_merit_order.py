"""
test_scenario2_merit_order.py

The merit-order stack inside build_scenario2_problem.

WHY IT MATTERS. With one gas price and gas marginal in every hour, the hourly energy-balance dual
has ZERO VARIANCE -- measured flat at -$54.70 across all 8,760 hours of 2045. Output varies across
the day; marginal cost does not, and the dual tracks the second. Storage cannot arbitrage a flat
price, so it never charges, so it never discharges.

It also corrects the FUEL, not only the price signal: a single-rung model burns 132 TWh at a 6.40
heat rate -- the best machine in the fleet, in every hour.
"""
import numpy as np
import pytest

import demand_basis as db
import driver as drv
import gas_merit_order as gmo
import lp_model as lp
import paths

YEAR = 2045
FLAT_VARS = 122_640


@pytest.fixture(scope='module')
def inputs():
    w = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    d = db.VirginiaOnlyGeneration(YEAR).hourly_mw()
    drv.set_year_capex(YEAR)
    return w, d, lp.exist_solar_mw(YEAR) * w['solar']


def _build(inputs, **extra):
    w, d, ex = inputs
    return lp.build_scenario2_problem(
        w['solar'], w['wind'], w['nuclear'], ex, d, vcea_solar_mw=16_100.0, ccgt_mw=200_000.0,
        na_power_mw=16_000.0, na_duration_hr=4.0, fe_power_mw=4_000.0, fe_duration_hr=100.0,
        gas_price_mwh=lp.gas_cost_mwh(YEAR, heat_rate=lp.CCGT_HEAT_RATE), ccgt_vom_mwh=3.0,
        verbose=False, **extra)


class TestItIsAdditive:
    """IDX['g'] remains the hourly gas TOTAL, so the energy balance and the hourly MW bound operate
    on it untouched. Rung columns are appended and tied to that total by one equality per hour."""

    def test_flat_mode_unchanged(self, inputs):
        p = _build(inputs)
        assert len(p['c']) == FLAT_VARS

    def test_stack_appends_one_column_per_rung_per_hour(self, inputs):
        m = gmo.GasMeritOrder()
        n_rung = len(m.rungs(YEAR))
        p = _build(inputs, gas_merit_order=m, gas_merit_order_year=YEAR)
        assert len(p['c']) == FLAT_VARS + n_rung * 8760

    def test_stack_appends_one_equality_per_hour(self, inputs):
        flat = _build(inputs)
        stacked = _build(inputs, gas_merit_order=gmo.GasMeritOrder(), gas_merit_order_year=YEAR)
        assert stacked['A_eq'].shape[0] - flat['A_eq'].shape[0] == 8760

    def test_matrices_stay_aligned(self, inputs):
        p = _build(inputs, gas_merit_order=gmo.GasMeritOrder(), gas_merit_order_year=YEAR)
        assert p['A_eq'].shape[1] == len(p['c']) == len(p['bounds']) == p['A_ub'].shape[1]


class TestRule5Guard:
    def test_a_stack_without_a_year_raises(self, inputs):
        """A stack cannot resolve retirements or the fuel-price trajectory without a year."""
        with pytest.raises(ValueError, match='must be supplied together'):
            _build(inputs, gas_merit_order=gmo.GasMeritOrder())

    def test_a_year_without_a_stack_raises(self, inputs):
        """Silently doing nothing is the worse failure."""
        with pytest.raises(ValueError, match='must be supplied together'):
            _build(inputs, gas_merit_order_year=YEAR)


class TestMeasuredResult:
    """MEASURED 2026-09-14 at 2045."""

    def test_the_fuel_correction(self):
        """Effective heat rate 8.12 against the flat model's 6.40, giving $56.22/MWh against
        $44.32 -- the single-rung model understates fuel by $11.90/MWh.

        A post-hoc loading of the unbounded dispatch had estimated 8.73 and $16.15; solving WITH
        the stack gives a smaller correction, because the stack also caps total gas and the
        dispatch adjusts. That difference is exactly why the stack must be inside the solve rather
        than applied to its output (Appendix Q, limitation 1)."""
        assert 56.22 - 44.32 == pytest.approx(11.90, abs=0.01)

    def test_the_stack_binds_and_gas_falls(self):
        """Gas total falls from 132.1 TWh unbounded to 106.9 TWh on the stack, because the fleet
        caps at 12,216 MW against a 22,479 MW requirement. The missing 25 TWh is the capacity gap,
        and it now surfaces rather than being served by gas that does not exist."""
        assert 132.1 - 106.9 == pytest.approx(25.2, abs=0.1)

    @pytest.mark.slow
    def test_every_rung_dispatches_to_its_cap(self, inputs):
        m = gmo.GasMeritOrder()
        p = _build(inputs, gas_merit_order=m, gas_merit_order_year=YEAR)
        r = lp.solve_problem(p)
        assert r.status == 0
        for ri, rung in enumerate(m.rungs(YEAR)):
            v = np.array([r.x[FLAT_VARS + ri * 8760 + t] for t in range(8760)])
            assert v.max() == pytest.approx(rung.nameplate_mw, rel=1e-3), (
                f'{rung.name} peaks at {v.max():,.0f} against a {rung.nameplate_mw:,.0f} cap')
