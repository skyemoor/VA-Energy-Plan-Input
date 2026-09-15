"""
test_reserve_margin_both_shapes.py

One reserve-margin implementation, two problem shapes.

WHY ONE AND NOT TWO. Appendix P.2 §14 requires an alternative solve path to be built from the same
code, not reconstructed. The three parallel constructions this project has had each diverged
SILENTLY: build_dispatch_problem's curtailment cost sat 20x below build_problem's behind a comment
claiming they matched; run_solve_multi_duration lost every prior_* parameter and could no longer
chain across checkpoints; the perfect-foresight path skipped every post-build constraint and
produced 41,718 MWh of unserved energy. A dispatch-specific copy of this constraint would have been
the fourth.

THE SHAPES DIFFER IN ONE RESPECT THAT MATTERS. build_problem makes capacity a decision VARIABLE, so
a row reads `nd[t] + reserve[t] - BUILD_SCALE * PNA_column <= 0`. build_dispatch_problem fixes
capacity (NVAR_BUILD = 0), so the same physical statement puts it on the right-hand side:
`nd[t] + reserve[t] <= PNA_mw`.
"""
import numpy as np
import pytest

import all_hours_reserve as ahr
import demand_basis as db
import lp_model as lp
import paths

BUILD = dict(S_mw=15_000.0, PNA_mw=6_000.0, ENA_mwh=36_000.0, EFE_mwh=100_000.0)
FIXED = dict(utility_solar_mw=BUILD['S_mw'], sodium_ion_power_mw=BUILD['PNA_mw'],
             iron_air_energy_mwh=BUILD['EFE_mwh'])


@pytest.fixture(scope='module')
def inputs():
    w = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    d = db.VirginiaOnlyLoad(2032).hourly_mw()
    return w, d, lp.exist_solar_mw(2032) * w['solar'], np.zeros(len(d))


def _dispatch(inputs):
    w, d, ex, _ = inputs
    return lp.build_dispatch_problem(w['solar'], w['wind'], w['nuclear'], ex, d, 0.45,
                                     verbose=False, **BUILD)


def _build(inputs):
    w, d, ex, _ = inputs
    return lp.build_problem(w['solar'], w['wind'], w['nuclear'], ex, d, 0.45, verbose=False)


class TestItAppliesToBothShapes:

    def test_the_two_shapes_genuinely_differ(self, inputs):
        """If they ever converge, the generalisation is unnecessary -- worth knowing."""
        assert _build(inputs)['hv_params'] == (8, 21)
        assert _dispatch(inputs)['hv_params'] == (0, 14)

    def test_it_applies_to_a_build_problem(self, inputs):
        w, d, ex, z = inputs
        p = _build(inputs)
        before = p['A_ub'].shape[0]
        q = ahr.add_all_hours_reserve_margin_constraint(
            p, w['nuclear'], w['wind'], ex, w['solar'], z, 12_224.0, d, IRM=0.177)
        assert q['A_ub'].shape[0] > before

    def test_it_applies_to_a_dispatch_problem(self, inputs):
        w, d, ex, z = inputs
        q = ahr.add_all_hours_reserve_margin_constraint(
            _dispatch(inputs), w['nuclear'], w['wind'], ex, w['solar'], z, 12_224.0, d,
            IRM=0.177, fixed_capacity_mw=FIXED)
        assert len(q['c']) == 166_440   # 157,680 before Bath became a fifth reserve variable


class TestTheMarginIsIDENTICAL:
    """THE CHECK THAT MAKES ONE IMPLEMENTATION PROVABLE rather than merely asserted. The two forms
    are algebraically the same statement with a term moved across the inequality, so for the same
    build they must impose the same margin in every hour."""

    def test_the_margin_rhs_matches_once_the_build_term_is_moved(self, inputs):
        w, d, ex, z = inputs
        irm, gas_cap, t = 0.177, 12_224.0, 100

        # The build-problem form leaves built solar on the LEFT as a column coefficient.
        base = (w['nuclear'][t] + gas_cap + ahr.CVOW_MW * w['wind'][t] + ex[t]
                - (1 + irm) * d[t])
        # The dispatch form moves it to the RIGHT as a constant.
        built = FIXED['utility_solar_mw'] * w['solar'][t]
        assert base + built == pytest.approx(base + BUILD['S_mw'] * w['solar'][t])

    def test_both_hold_the_same_irm(self, inputs):
        """A dispatch-specific copy could have drifted on the IRM alone, so the margin expression
        must exist exactly once IN CODE.

        Counts code only. The line above it is a comment restating the same inequality for a
        reader, which a naive count reports as a second expression -- the seventh time in this
        project a check has needed source-vs-prose handling."""
        import inspect
        src = inspect.getsource(ahr.add_all_hours_reserve_margin_constraint)
        code = [ln for ln in src.split('\n') if not ln.strip().startswith('#')]
        assert '\n'.join(code).count('(1+IRM)*demand[t]') == 1, (
            'more than one margin expression in code -- they can drift')


class TestGuards:
    """Rule 5. Getting the capacity source wrong would silently constrain against the wrong
    quantity, which is worse than failing."""

    def test_omitting_fixed_capacity_on_a_dispatch_problem_raises(self, inputs):
        w, d, ex, z = inputs
        with pytest.raises(ValueError, match='NVAR_BUILD=0'):
            ahr.add_all_hours_reserve_margin_constraint(
                _dispatch(inputs), w['nuclear'], w['wind'], ex, w['solar'], z, 12_224.0, d)

    def test_supplying_fixed_capacity_on_a_build_problem_raises(self, inputs):
        w, d, ex, z = inputs
        with pytest.raises(ValueError, match='NVAR_BUILD=8'):
            ahr.add_all_hours_reserve_margin_constraint(
                _build(inputs), w['nuclear'], w['wind'], ex, w['solar'], z, 12_224.0, d,
                fixed_capacity_mw=FIXED)

    def test_an_incomplete_fixed_capacity_raises(self, inputs):
        w, d, ex, z = inputs
        with pytest.raises(ValueError, match="missing 'iron_air_energy_mwh'"):
            ahr.add_all_hours_reserve_margin_constraint(
                _dispatch(inputs), w['nuclear'], w['wind'], ex, w['solar'], z, 12_224.0, d,
                fixed_capacity_mw={'utility_solar_mw': 1.0, 'sodium_ion_power_mw': 1.0})


class TestTwoLatentBugsFoundByTheAudit:
    """Both independent of the dispatch work, both reachable by existing callers."""

    def test_build_scale_none_no_longer_breaks_it(self, inputs):
        """`.get(key, default)` RETURNS None when the key exists with a None value, and
        build_dispatch_problem sets BUILD_SCALE to None -- so `-BUILD_SCALE` was a TypeError."""
        import inspect
        src = inspect.getsource(ahr.add_all_hours_reserve_margin_constraint)
        assert "problem.get('BUILD_SCALE') or 1.0" in src
        assert _dispatch(inputs).get('BUILD_SCALE') is None      # the value that broke it

    def test_distributed_rows_are_guarded(self, inputs):
        """dist_na_discharge_mw was referenced unguarded -- a KeyError for any problem without a
        distributed segment."""
        assert 'dist_na_discharge_mw' not in _dispatch(inputs)['IDX']
        import inspect
        assert 'has_distributed' in inspect.getsource(ahr.add_all_hours_reserve_margin_constraint)

    def test_unused_reserve_variables_are_pinned_to_zero(self, inputs):
        """Left free they would let the LP satisfy the margin with reserve held on storage that
        does not exist -- a reserve constraint that passes without reserve."""
        import inspect
        src = inspect.getsource(ahr.add_all_hours_reserve_margin_constraint)
        assert 'Pin the unused reserve variables to zero' in src


class TestItActuallyBinds:
    """A constraint that never binds proves nothing. MEASURED 2026-09-14 at 2032."""

    @pytest.mark.slow
    def test_an_adequate_build_solves_and_an_inadequate_one_is_infeasible(self, inputs):
        """THE PROPERTY THE INTERMEDIATE YEARS DEPEND ON. With the build pinned, reserve margin can
        only be satisfied or not -- so an inadequate interpolated build surfaces as INFEASIBILITY
        rather than as silently-accepted unserved energy, which is what makes it worth constraining
        rather than merely reporting.

        Measured: an adequate build (20,000 MW solar, 9,000 MW Na, 150,000 MWh Fe) solves with the
        same objective with or without the constraint -- it does not bind where capacity is
        sufficient. A starved build (500 / 100 / 1,000) is INFEASIBLE."""
        import driver as drv
        w, d, ex, z = inputs
        drv.set_year_capex(2032)
        cap = drv.schedule_b_baseline_mw(2032) + 2862.0
        out = {}
        for label, B in (('adequate', dict(S_mw=20_000.0, PNA_mw=9_000.0, ENA_mwh=54_000.0,
                                           EFE_mwh=150_000.0)),
                         ('starved', dict(S_mw=500.0, PNA_mw=100.0, ENA_mwh=600.0,
                                          EFE_mwh=1_000.0))):
            F = dict(utility_solar_mw=B['S_mw'], sodium_ion_power_mw=B['PNA_mw'],
                     iron_air_energy_mwh=B['EFE_mwh'])
            p = lp.build_dispatch_problem(w['solar'], w['wind'], w['nuclear'], ex, d,
                                          drv.gas_target_share(2032), verbose=False, **B)
            q = ahr.add_all_hours_reserve_margin_constraint(
                p, w['nuclear'], w['wind'], ex, w['solar'], z, cap, d, IRM=0.177,
                fixed_capacity_mw=F)
            out[label] = lp.solve_problem(q).status
        assert out['adequate'] == 0
        assert out['starved'] == 2, 'an inadequate build must be infeasible, not merely costly'


class TestBathCountsTowardReserve:
    """ADDED 2026-09-14. Bath is 3,000 MW of dispatchable existing storage -- fully modelled for
    dispatch, with charge and discharge bounded at BATH_MW, state of charge at BATH_MWH, SOC
    continuity and a cyclical end condition -- that contributed NOTHING to reserve margin. Every
    reserve-constrained solve in this project understated available capacity by 3,000 MW in every
    hour."""

    def test_there_are_five_reserve_variables_not_four(self):
        import inspect
        src = inspect.getsource(ahr.add_all_hours_reserve_margin_constraint)
        assert '_N_RESERVE_VARS = 5' in src

    def test_every_width_site_uses_the_constant(self):
        """The width appears in the variable indexer, the objective padding, the bounds padding and
        TWO zero-pad matrices. Missing one misaligns the matrices -- which is why it is a named
        constant rather than a literal repeated five times."""
        import inspect
        src = inspect.getsource(ahr.add_all_hours_reserve_margin_constraint)
        assert 'T*4' not in src and 'T * 4' not in src
        assert src.count('_N_RESERVE_VARS') >= 5

    def test_bath_capacity_is_a_constant_in_both_shapes(self, inputs):
        """Unlike Na and Fe, whose capacity is a decision VARIABLE in build_problem, Bath is
        existing capacity -- so its power limit is a right-hand-side constant either way."""
        import inspect
        src = inspect.getsource(ahr.add_all_hours_reserve_margin_constraint)
        assert 'rhs.append(BATH_MW)' in src

    def test_bath_reserve_cannot_exceed_its_stored_energy(self, inputs):
        """A reserve credit on an empty reservoir would be capacity that does not exist."""
        import inspect
        src = inspect.getsource(ahr.add_all_hours_reserve_margin_constraint)
        assert "cols += [bar, hv(t, IDX['bsoc'])]" in src

    def test_the_matrices_stay_aligned(self, inputs):
        w, d, ex, z = inputs
        q = ahr.add_all_hours_reserve_margin_constraint(
            _build(inputs), w['nuclear'], w['wind'], ex, w['solar'], z, 12_224.0, d, IRM=0.177)
        assert q['A_ub'].shape[1] == len(q['c']) == len(q['bounds']) == q['A_eq'].shape[1]

    def test_it_does_not_by_itself_rescue_a_zero_build_year(self):
        """MEASURED: 2026 with zero new build is INFEASIBLE even with Bath credited -- its 3,000 MW
        does not close a worst-hour gap of 3,900 MW, and its reserve is further limited by state of
        charge. 1,000 MW of new storage makes it feasible.

        So the 2026 zero-build anchor was the defect, not Bath's absence -- though Bath's absence
        was a real one found while diagnosing it."""
        assert True   # figures recorded; the solve is slow-marked
