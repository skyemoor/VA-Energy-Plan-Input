"""
test_scenario2_baseline.py

Scenario 2 -- the whitepaper's BASELINE: Dominion's approach of building only the solar and storage
assets the Code specifically names.

BROKEN UNTIL 2026-09-13. Scenario2Solver.solve() passed six arguments to build_scenario2_problem(),
which requires thirteen. Every call raised TypeError, so the baseline scenario had never run
through the solver class.
"""
import numpy as np
import os
import pytest

import assumptions
import checkpoint_solver as cs
import driver as drv
import lp_model as lp
import paths

pytestmark = pytest.mark.slow


def _solver(year=2045):
    p = paths.intermediate(f'demand_{year}fy_va_only.npy')
    if not os.path.exists(p):
        pytest.skip('demand intermediate not built')
    w = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    return w, cs.Scenario2Solver(
        year=year, demand=np.load(p), exist_solar=lp.exist_solar_mw(year) * w['solar'],
        solar_cf=w['solar'], wind_cf=w['wind'], nuclear=w['nuclear'], vcea_solar_mw=16_100.0)


class TestItRuns:
    def test_solve_succeeds(self):
        _, s = _solver()
        r = s.solve(gas_price_mwh=lp.gas_cost_mwh(2045, heat_rate=lp.CCGT_HEAT_RATE))
        assert r['success'], 'the baseline scenario must run before it can be a baseline'


class TestEverythingIsPinned:
    """The whole point. If any of the three were optimised, the run would be a partially-optimised
    hybrid rather than Dominion's approach, and the baseline point would move toward the least-cost
    curve for the wrong reason."""

    def test_storage_is_pinned_to_the_statutory_floors(self):
        _, s = _solver()
        r = s.solve(gas_price_mwh=50.0)
        assert r['na_power_mw'] == drv.vcea_short_duration_floor_mw(2045) == 16_000.0
        assert r['fe_power_mw'] == drv.vcea_long_duration_floor_mw(2045) == 4_000.0

    def test_sodium_duration_is_four_hours_by_decision(self):
        """The Code names MW, not MWh, so duration is an INTERPRETATION rather than a requirement,
        and it is the single largest discretionary number in the baseline."""
        _, s = _solver()
        r = s.solve(gas_price_mwh=50.0)
        assert r['na_duration_hr'] == assumptions.DISTRIBUTED_STORAGE_DURATION_HR == 4.0

    def test_the_problem_has_no_build_variables(self):
        """build_scenario2_problem is dispatch-only: NVAR = 14 x T, no build block."""
        _, s = _solver()
        r = s.solve(gas_price_mwh=50.0)
        assert len(r['problem']['c']) == 14 * 8760


class TestComplianceLevel:
    """The number the compliance sweep needs, and the whitepaper's central finding."""

    def test_clean_share_is_about_35_percent(self):
        """BASELINE MOVED 2026-09-13, from 39.2% to 34.7%.

        The earlier figure double-counted post-VCEA solar: it passed the full 16,100 MW target
        alongside the existing fleet, treating the target as entirely new build. Only 645 MW of
        the existing 5,300 predates the statute; the other ~4,655 MW was approved under
        § 56-585.5 D.4's annual petition process, which is the mechanism the target is measured by.
        New build required is ~11,445 MW, not 16,100.

        WHY IT IS SO LOW: demand has roughly doubled since the VCEA was written, while the
        statutory MW targets did not change. The statutory build was sized against a much smaller
        system."""
        w, s = _solver()
        r = s.solve(gas_price_mwh=lp.gas_cost_mwh(2045, heat_rate=lp.CCGT_HEAT_RATE))
        x, I = r['raw'].x, r['problem']['IDX']
        gas = sum(x[t * 14 + I['g']] for t in range(8760))
        demand = s.demand.sum()
        assert 1 - gas / demand == pytest.approx(0.347, abs=0.02)

    def test_it_falls_below_the_sweep_range(self):
        """CONSEQUENCE FOR THE RESTRUCTURING: the sweep was scoped at 75-100% clean generation
        share. Scenario 2 lands at ~39%, far below it, so the baseline cannot be plotted on that
        axis as designed -- the sweep must extend down to reach it, or the chart must show it as
        an off-scale reference."""
        assert 0.347 < min(assumptions.COMPLIANCE_SWEEP_LEVELS)

    def test_unserved_is_zero(self):
        """Gas is effectively unbounded here, so it should always be able to serve load. Nonzero
        unserved would mean something else is wrong."""
        _, s = _solver()
        r = s.solve(gas_price_mwh=50.0)
        x, I = r['raw'].x, r['problem']['IDX']
        assert sum(x[t * 14 + I['unserved']] for t in range(8760)) == pytest.approx(0.0, abs=1.0)


class TestPostVceaSolarIsDeducted:
    """The statutory target is a TOTAL, not an increment on top of everything existing."""

    def test_new_build_is_the_target_less_post_vcea_capacity(self):
        _, s = _solver()
        r = s.solve(gas_price_mwh=50.0)
        assert r['vcea_target_mw'] == 16_100.0
        assert r['vcea_new_build_mw'] == pytest.approx(11_445.2, abs=1.0)

    def test_only_pre_vcea_capacity_is_excluded_from_the_target(self):
        """645 MW of 5,300 predates the statute. The rest was approved under § 56-585.5 D.4's
        annual petition process -- 'construct, acquire, or enter into agreements to purchase' --
        which is the mechanism the 16,100 MW is measured by."""
        assert assumptions.EXIST_SOLAR_PRE_VCEA_MW == pytest.approx(645.2)
        counted = assumptions.EXIST_SOLAR_MW_2026 - assumptions.EXIST_SOLAR_PRE_VCEA_MW
        assert counted == pytest.approx(4_654.8, abs=1.0)

    def test_the_flag_can_reproduce_the_uncorrected_result(self):
        """Kept so the size of the correction stays measurable rather than becoming folklore."""
        _, s = _solver()
        r = s.solve(gas_price_mwh=50.0, deduct_existing_post_vcea=False)
        assert r['vcea_new_build_mw'] == 16_100.0

    def test_exceeding_the_target_raises_rather_than_going_negative(self):
        """A negative build requirement would silently subtract solar. It is a reportable finding
        instead."""
        with pytest.raises(ValueError, match='already exceeds'):
            assumptions.vcea_new_solar_mw(target_mw=1_000.0)


class TestImpliedGasCapacity:
    def test_peak_gas_is_reported_as_an_output(self):
        """Gas is unbounded by decision, because the external sizing that produced ccgt_mw lived in
        a /tmp file that did not survive. The resulting peak is the answer to a better question:
        how much gas capacity does the statutory build imply?"""
        _, s = _solver()
        r = s.solve(gas_price_mwh=lp.gas_cost_mwh(2045, heat_rate=lp.CCGT_HEAT_RATE))
        x, I = r['raw'].x, r['problem']['IDX']
        peak = max(x[t * 14 + I['g']] for t in range(8760))
        assert peak == pytest.approx(22_478, rel=0.05)
        assert peak < r['ccgt_ceiling_mw'], 'the ceiling bound, so the result is not unbounded'
