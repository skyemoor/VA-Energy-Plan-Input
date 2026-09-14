"""
test_build_only.py

run_solve(build_only=True) must return the problem EXACTLY as it would be solved.

WHY IT EXISTS: the perfect-foresight path called lp.build_problem directly and applied hooks
itself, skipping every post-build step run_solve performs. That produced 41,718 MWh of unserved
energy at 2030 where the myopic solve had none -- without the VCEA storage floors and
min_na_duration_hr the LP builds cheap power-only storage that cannot sustain an evening.

AND IT WAS PLACED WRONG FIRST TIME. The initial return sat straight after apply_slcr_constraint,
which is BEFORE the VCEA floor block, so the floors it was written to deliver were still skipped.
The comment claimed they were applied. 2030 still came back with 39,682 MWh unserved -- a smaller
number, which is the dangerous kind of partial fix.
"""
import numpy as np
import pytest

import checkpoint_solver as cs
import demand_basis as db
import driver as drv
import lp_model as lp
import paths


@pytest.fixture(scope='module')
def problem_2030():
    w = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    d = db.VirginiaOnlyLoad(2030).hourly_mw()
    s = cs.Scenario1WithReserveMargin(
        year=2030, gas_target_share=drv.gas_target_share(2030), demand=d,
        exist_solar=lp.exist_solar_mw(2030) * w['solar'], solar_cf=w['solar'],
        wind_cf=w['wind'], nuclear=w['nuclear'])
    drv.set_year_capex(2030)
    hook = s._chain_hooks(s._post_build_hook(), s._all_hours_reserve_hook(0.177))
    return drv.run_solve(
        2030, drv.gas_target_share(2030), d, lp.exist_solar_mw(2030) * w['solar'],
        w['solar'], w['wind'], w['nuclear'], capacity_cap_mw=s.apply_gas_cap(),
        build_only=True, post_build_hook=hook, slcr_curt_cost=s.curtailment_cost_mwh())


class TestEveryPostBuildStepIsApplied:
    """Checks the PROBLEM, not the source. A comment saying the floors are applied is what the
    first version had, and it was wrong."""

    def test_vcea_power_floor(self, problem_2030):
        floor = drv.vcea_short_duration_floor_mw(2030)
        assert floor == 4000.0
        got = problem_2030['bounds'][1][0] * problem_2030['BUILD_SCALE']
        assert got == pytest.approx(floor), (
            f'NA power lower bound is {got:,.0f} MW against a {floor:,.0f} MW statutory floor. '
            'The build_only return is placed before the VCEA floor block.')

    def test_the_six_hour_duration_floor(self, problem_2030):
        """Without it the LP builds power with almost no energy -- storage that discharges for
        minutes and cannot cover an evening, which is what produced the unserved energy."""
        power = problem_2030['bounds'][1][0] * problem_2030['BUILD_SCALE']
        energy = problem_2030['bounds'][2][0] * problem_2030['BUILD_SCALE']
        assert energy == pytest.approx(power * 6.0)

    def test_the_capacity_cap_bounds_gas(self, problem_2030):
        nb, nph = problem_2030['hv_params']
        idx = problem_2030['IDX']['g']
        assert problem_2030['bounds'][nb + idx][1] == pytest.approx(12224.0)

    def test_the_reserve_margin_rows_are_present(self, problem_2030):
        """The all-hours hook adds 78,840 rows and 35,040 variables per period."""
        assert problem_2030['A_ub'].shape[0] > 240_000
        assert len(problem_2030['c']) == 219_008

    def test_the_row_count_matches_what_the_solve_consumes(self, problem_2030):
        """245,647, not 245,646. The one-row difference is the SLCR row, and its absence is exactly
        what the misplaced return caused -- an audit comparing build_only against a full solve
        caught the discrepancy before the source inspection did."""
        assert problem_2030['A_ub'].shape[0] == 245_647

    def test_the_curtailment_cost_is_the_solver_hook_value(self, problem_2030):
        import assumptions
        nb, nph = problem_2030['hv_params']
        idx = problem_2030['IDX']['curt']
        assert problem_2030['c'][nb + idx] == pytest.approx(assumptions.CURTAILMENT_COST_MWH)


class TestThePlacementIsGuarded:
    def test_the_return_is_immediately_before_the_solve(self):
        """So it stays correct no matter what is added above it -- the failure mode was a return
        that was correct when written and wrong once the floor block moved past it."""
        import inspect
        import re
        src = inspect.getsource(drv.run_solve)
        ret = src.index('if build_only:')
        solve = src.index('res = lp.solve_problem(problem)')
        assert ret < solve
        between = src[src.index('return problem', ret):solve]
        code = [ln for ln in between.split('\n')
                if ln.strip() and not ln.strip().startswith('#') and 'return problem' not in ln]
        assert not code, f'code between the build_only return and the solve: {code}'
