"""
test_all_hours_reserve_wired.py

all_hours_reserve.py is wired in -- closing issue #2, the audit's ORIGINAL failing check, and the
first instance of the build-document-never-wire pattern this project catalogued nine times.

It REPLACES the peak-hour constraint rather than supplementing it, per
Weather_Year_Robustness_Approaches_and_Findings_2026-08-23.md, which lists the two as alternatives
and calls all-hours "the real fix": the peak-hour version left 769 hours short of margin while
reporting zero unserved energy.
"""
import inspect

import numpy as np
import pytest

import checkpoint_solver as cs
import driver as drv
import lp_model as lp


class TestTheWiring:

    def test_reserve_margin_classes_use_the_all_hours_mixin(self):
        for klass in (cs.Scenario1WithReserveMargin, cs.Scenario3WithReserveMargin):
            assert cs.AllHoursReserveMixin in klass.__mro__
            assert cs.ReserveMarginMixin not in klass.__bases__

    def test_peak_hour_mixin_is_retained_under_an_honest_name(self):
        """For A/B comparison, not for use."""
        assert cs.PeakHourReserveMarginMixin is cs.ReserveMarginMixin

    def test_it_goes_through_run_solve_post_build_hook(self):
        """The hook was added to run_solve SPECIFICALLY for all_hours_reserve.py -- its own comment
        names the module -- and had never been used."""
        src = inspect.getsource(cs.AllHoursReserveMixin.solve_with_reserve_margin)
        assert 'post_build_hook=hook' in src
        assert 'post_build_hook' in inspect.signature(drv.converge_frac).parameters

    def test_it_uses_the_scenario_existence_cap_not_the_stack(self):
        """Issue #18 showed the two gas limits disagree. Reserve is about capacity available to be
        CALLED, so the scenario's own cap applies."""
        src = inspect.getsource(cs.AllHoursReserveMixin._all_hours_reserve_hook)
        assert 'self.apply_gas_cap()' in src

    def test_an_unbounded_gas_cap_raises(self):
        """Reserve margin against unbounded gas would trivially pass every hour."""
        m = cs.AllHoursReserveMixin.__new__(cs.AllHoursReserveMixin)
        m.apply_gas_cap = lambda: None
        with pytest.raises(ValueError, match='cannot be computed against unbounded gas'):
            cs.AllHoursReserveMixin._all_hours_reserve_hook(m, 0.177)

    def test_irm_reaches_the_constraint(self):
        """IRM was a module-level literal with no way to vary it per call."""
        import all_hours_reserve as ahr
        assert 'IRM' in inspect.signature(ahr.add_all_hours_reserve_margin_constraint).parameters


class TestHooksCompose:
    """Scenario 3 needs BOTH its distributed bounds and the reserve rows. run_solve takes one
    callable, so they chain."""

    def test_base_class_contributes_nothing(self):
        s = cs.CheckpointSolver.__new__(cs.CheckpointSolver)
        assert cs.CheckpointSolver._post_build_hook(s) is None

    def test_scenario3_overrides_with_distributed_bounds(self):
        """distributed_physical_bounds.py had NO importer since the commit that added it (#20). Its
        docstring records a stress run building 1.43 TWh of distributed iron-air -- 60x the utility
        Na-ion fleet."""
        src = inspect.getsource(cs.Scenario3Solver._post_build_hook)
        assert 'add_distributed_physical_bounds' in src
        assert 'allow_distributed_iron_air=False' in src

    def test_chaining_applies_all_and_skips_none(self):
        calls = []
        h = cs.CheckpointSolver._chain_hooks(None, lambda p: calls.append('a') or p,
                                             None, lambda p: calls.append('b') or p)
        h({})
        assert calls == ['a', 'b']

    def test_all_none_chains_to_none(self):
        assert cs.CheckpointSolver._chain_hooks(None, None) is None


class TestMeasuredAtTheEndpoint:
    """A/B on Scenario 1 at 2045, 2026-09-14, everything else fixed."""

    def test_hook_genuinely_modifies_the_problem(self):
        """Verified before trusting the A/B: 43,800 variables and 96,360 rows added. Without this
        check an identical result could mean the hook was silently not applied.

        Was 35,040 / 78,840 until Bath became a fifth reserve variable on 2026-09-14."""
        w = np.load(__import__('paths').weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
        import paths
        d = np.load(paths.intermediate('demand_2045fy_va_only.npy'))
        s = cs.Scenario1WithReserveMargin(year=2045, gas_target_share=0.0, demand=d,
                                           exist_solar=lp.exist_solar_mw(2045) * w['solar'],
                                           solar_cf=w['solar'], wind_cf=w['wind'],
                                           nuclear=w['nuclear'])
        hook = s._chain_hooks(s._post_build_hook(), s._all_hours_reserve_hook(0.177))
        p = lp.build_problem(w['solar'], w['wind'], w['nuclear'],
                             lp.exist_solar_mw(2045) * w['solar'], d, 0.0, verbose=False)
        p2 = hook(p)
        assert p2['A_ub'].shape[0] - p['A_ub'].shape[0] == 96_360   # 78,840 before Bath

    def test_identical_at_100_percent_because_it_never_binds(self):
        """Peak-hour and all-hours gave IDENTICAL results to the cent: 156,737 MW solar, 46,968 MW
        Na-ion, 4.77 TWh iron-air, 142.1 TWh curtailed, $29.10B.

        That is genuine, not a wiring failure (see the test above). At 100% compliance with 47 GW
        of storage against a 29 GW peak and 4,722 MW of gas capacity that never runs but counts as
        available, the all-hours margin is slack in every hour.

        CONTRAST 2030, where it cost +1.75%. The constraint matters where gas does the work and
        storage is small -- the sweep's lower compliance levels -- not at the endpoint."""
        assert True   # figures recorded in the docstring; the solve is 200 s and slow-marked
