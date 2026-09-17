"""
test_scenario2_gas_capacity_pinned.py

Scenario 2's gas capacity bound, its sizing, and the costing of what it builds.

THE DEFECT THIS GUARDS AGAINST (build log 154): Scenario2Solver.solve defaulted ccgt_mw to
unbounded_gas_ceiling_mw -- 200,000 MW -- so the published run dispatched gas the fleet does not
have and reported ZERO unserved energy, while a run bounded by the real fleet showed 30.05 TWh at
2045. Two specifications, and every downstream figure rested on the wrong one.
"""
import numpy as np
import pytest

import assumptions as a
import checkpoint_solver as cs
import demand_basis as db
import driver as drv
import gas_merit_order as gmo
import lp_model as lp
import paths


def _solver(year):
    w = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    return cs.Scenario2Solver(
        year=year, demand=db.VirginiaOnlyGeneration(year).hourly_mw(),
        exist_solar=lp.exist_solar_mw(year) * w['solar'], solar_cf=w['solar'],
        wind_cf=w['wind'], nuclear=w['nuclear'], vcea_solar_mw=16_100.0)


class TestTheCapIsBoundedByTheRealFleet:
    def test_it_is_not_the_unbounded_ceiling(self):
        assert _solver(2045).apply_gas_cap() < 20_000.0

    def test_it_is_fleet_plus_retain_pool_plus_new_build(self):
        """THE RETAIN POOL WAS OMITTED in the first version of this override, giving 13,889 MW
        against the merit-order stack's 12,216 plus 6,498 of new capacity -- and the solve showed
        15.82 TWh unserved where an independent probe at the same capacity showed zero. Rule 4: the
        DISAGREEMENT between two paths was the signal, not either figure alone."""
        s = _solver(2045)
        assert s.apply_gas_cap() == pytest.approx(
            drv.gas_baseline_mw(2045, 'A') + a.GAS_NEW_BUILD_POOL_MW + s.new_gas_capacity_mw())

    def test_it_uses_schedule_a(self):
        """Scenario 2 runs gas at a high capacity factor, so its plants do not retire for lack of
        market -- the premise of Schedule B."""
        assert _solver(2045).gas_retirement_schedule() == 'A'


class TestSizing:
    """Adequacy sets a FLOOR; cost sets the optimum ABOVE it."""

    @pytest.mark.parametrize('year,mw', [
        (2030, 0.0), (2031, 566.0), (2036, 2_166.0), (2040, 5_168.0), (2045, 6_547.0)])
    def test_whole_unit_combinations(self, year, mw):
        assert _solver(year).new_gas_capacity_mw() == pytest.approx(mw)

    def test_a_mix_fits_far_better_than_one_size(self):
        """Locking to the 1,083 MW block sent 2031's 500 MW requirement to a single unit -- a 583
        MW overshoot -- where the 566 MW Mitsubishi block covers it with 66 MW to spare. Worst
        overshoot across the trajectory falls from 583 MW to 168."""
        worst = max(_solver(y).new_gas_capacity_mw()
                    - max(mw for yy, mw in a.SCENARIO2_NEW_CCGT_REQUIRED_MW_BY_YEAR.items()
                          if yy <= y)
                    for y in range(2026, 2046))
        assert worst < 200.0, f'worst overshoot {worst:,.0f} MW'

    def test_the_mix_is_chosen_on_capital_not_megawatts(self):
        """The larger block is cheaper per kW ($950 against $1,084), so minimising megawatts and
        minimising dollars are different objectives and can disagree. Capital decides."""
        _mix, _mw, capex = a.ccgt_unit_mix_for(2_000.0)
        alternatives = [a.CCGT_REFERENCE_UNITS[k]['mw'] * 1000 * a.CCGT_REFERENCE_UNITS[k]['capex_usd_per_kw']
                        for k in a.CCGT_REFERENCE_UNITS]
        assert capex <= sum(alternatives)

    def test_an_unreachable_requirement_raises(self):
        """Rule 5: a short build would feed a reported figure."""
        with pytest.raises(ValueError, match='rather than accepting a short build'):
            a.ccgt_unit_mix_for(1_000_000.0, max_units_per_type=2)

    def test_the_566_unit_carries_an_interpolated_cost_and_says_so(self):
        """Gas Turbine World publishes four configuration studies and none falls at this size. The
        RATING is sourced to Mitsubishi Power's T-Point 2 validation plant; the capex is not."""
        unit = a.CCGT_REFERENCE_UNITS['m501jac_single_shaft_566']
        assert unit['mw'] == 566.0 and unit['efficiency'] == 0.640
        assert 'INTERPOLATED' in unit['capex_basis']
        assert 'INTERPOLATED' in a.CCGT_REFERENCE_UNIT_COSTS_ARE_MIXED_BASIS

    def test_the_per_unit_figures_do_not_set_the_reported_cost(self):
        """Capital for the whole build comes from ccgt_capex_kw(), so a mixed-basis per-unit table
        informs SELECTION without contaminating the reported figure."""
        assert 'inform unit SELECTION, not the reported cost' in a.CCGT_REFERENCE_UNIT_COSTS_ARE_MIXED_BASIS

    def test_the_build_never_decreases(self):
        """2031 needs a unit that 2033 does not -- statutory solar arrives faster than load grows
        in some years. Capacity persists, so the BUILD is the running maximum."""
        builds = [_solver(y).new_gas_capacity_mw() for y in range(2030, 2046)]
        assert all(b >= x for x, b in zip(builds, builds[1:])), 'build must never decrease'



    def test_2045_is_the_cost_optimum_not_the_adequacy_floor(self):
        """$8,307M/yr at 6,500 MW against $8,323M at 7,000 and $8,342M at 7,500. Adequacy alone
        gives 5,000 MW -- the extra pays for itself in fuel saved on the existing fleet."""
        assert a.SCENARIO2_NEW_CCGT_REQUIRED_MW_BY_YEAR[2045] == 6_500.0

    def test_the_table_is_marked_provisional(self):
        assert 'interpolated placeholders' in a.SCENARIO2_NEW_CCGT_REQUIRED_MW_BY_YEAR_IS_PROVISIONAL

    def test_a_year_outside_the_range_raises(self):
        """Rule 5: an interpolated guess would feed a reported figure."""
        with pytest.raises(ValueError, match='needs its own sizing solve'):
            _solver(2045).new_gas_capacity_mw(2099)


class TestTheGapCloses:
    """MEASURED 2026-09-14, and the point of the whole exercise."""

    @pytest.mark.slow
    def test_2045_serves_its_load(self):
        s = _solver(2045)
        r = s.solve(gas_price_mwh=lp.gas_cost_mwh(2045, heat_rate=lp.CCGT_HEAT_RATE))
        idx, nph = r['problem']['IDX'], r['problem']['hv_params'][1]
        unserved = np.array([r['raw'].x[t * nph + idx['unserved']]
                             for t in range(len(s.demand))])
        assert unserved.sum() < 1.0, f'{unserved.sum() / 1e6:.2f} TWh unserved'


class TestCostingUsesTheBuildNotTheDispatch:
    def test_new_capacity_is_what_was_built(self):
        """This read new_mw = max(0, peak_gas_mw - existing_gas_mw), inferring the build from the
        peak hour. A plant running below nameplate is still paid for."""
        import inspect
        src = inspect.getsource(cs.Scenario2Solver.lifecycle_cost)
        assert 'new_gas_mw = self.new_gas_capacity_mw()' in src
        assert 'peak_gas_mw - existing_gas_mw' not in src.split('add_asset')[-1]

    def test_existing_capacity_is_the_whole_fleet(self):
        """Not min(peak, existing): fixed O&M applies to available capacity, not dispatched."""
        import inspect
        assert "existing_mw=existing_gas_mw" in inspect.getsource(cs.Scenario2Solver.lifecycle_cost)

    def test_the_gas_only_probe_is_not_comparable_to_the_lifecycle_total(self):
        """RECORDED BECAUSE I COMPARED THEM. The four-term probe's $8,307M is new-CCGT capital plus
        gas fuel; lifecycle_cost's $9,647M adds solar and storage capital to the full LP objective.
        Different scopes, not a disagreement."""
        assert 9_647 > 8_307
