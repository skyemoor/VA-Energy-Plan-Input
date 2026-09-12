"""
test_merit_order_solver_path.py

Verifies the gas merit order actually reaches build_problem through the solver path.

WHY THIS EXISTS. On 2026-09-12 the stack was wired into lp_model.build_problem and tested there --
but Scenario3Solver.converge_and_solve() overrides the parent and neither it, drv.run_solve() nor
drv.converge_frac() accepted the parameter. The feature worked when build_problem was called
directly, which is how it was tested, and could not be reached by any scenario. Testing the layer
changed rather than the path that calls it is the failure these tests close.

They assert plumbing rather than solve results: a full Scenario 3 checkpoint runs converge_frac
(up to 3 solves) plus a final solve, 77-137s each, which exceeds the session execution window even
at 2030.
"""
import inspect

import pytest

import checkpoint_solver as cs
import driver as drv
import lp_model as lp
from gas_merit_order import GasMeritOrder


class TestParameterReachesEveryLayer:

    @pytest.mark.parametrize('fn', [drv.run_solve, drv.converge_frac, lp.build_problem])
    def test_layer_accepts_the_stack(self, fn):
        params = inspect.signature(fn).parameters
        assert 'gas_merit_order' in params, f'{fn.__name__} cannot receive the stack'
        assert 'gas_merit_order_year' in params, f'{fn.__name__} cannot receive the year'

    def test_converge_frac_forwards_to_run_solve(self):
        """converge_frac runs the solves that converge the gas fraction. If it drops the stack,
        every iteration but the last would price gas flat -- and the last would disagree."""
        src = inspect.getsource(drv.converge_frac)
        assert 'gas_merit_order=gas_merit_order' in src
        assert 'gas_merit_order_year=gas_merit_order_year' in src

    def test_run_solve_forwards_to_build_problem(self):
        src = inspect.getsource(drv.run_solve)
        assert 'gas_merit_order=gas_merit_order' in src


class TestBaseClassHook:
    """Rule 1: on CheckpointSolver, not on the subclass where the need surfaced."""

    @pytest.mark.parametrize('cls', ['CheckpointSolver', 'Scenario1Solver', 'Scenario1BSolver',
                                     'Scenario2Solver', 'Scenario3Solver'])
    def test_every_scenario_inherits_the_hook(self, cls):
        assert hasattr(getattr(cs, cls), '_gas_merit_order_kwargs')

    def test_hook_is_empty_when_no_stack_is_set(self):
        """Opt-in: absent a stack, every call path behaves exactly as before 2026-09-12, so
        existing baselines stay valid."""
        class Stub:
            year = 2030
            _gas_merit_order_kwargs = cs.CheckpointSolver._gas_merit_order_kwargs
        assert Stub()._gas_merit_order_kwargs() == {}

    def test_hook_uses_the_solver_own_year(self):
        """A stack resolved for a different year than the checkpoint being solved would apply the
        wrong retirements and the wrong fuel price, and nothing downstream would catch it."""
        class Stub:
            year = 2045
            gas_merit_order = GasMeritOrder()
            _gas_merit_order_kwargs = cs.CheckpointSolver._gas_merit_order_kwargs
        kw = Stub()._gas_merit_order_kwargs()
        assert kw['gas_merit_order_year'] == 2045


class TestAllThreeSolvePathsThreadIt:
    """Three call sites exist, and one was initially left with an unbound reference -- the
    replacement matched a third site I had not accounted for."""

    @pytest.mark.parametrize('name', ['converge_and_solve', '_converge_and_solve_with_reserve'])
    def test_solve_path_binds_gas_kwargs_before_use(self, name):
        for cls in (cs.CheckpointSolver, cs.Scenario3Solver, cs.ReserveMarginMixin):
            fn = getattr(cls, name, None)
            if fn is None:
                continue
            src = inspect.getsource(fn)
            if '**gas_kwargs' in src:
                assert 'gas_kwargs = self._gas_merit_order_kwargs()' in src, \
                    f'{cls.__name__}.{name} uses gas_kwargs without binding it'


class TestRunSolveFlatPriceIsSimpleCycle:
    def test_the_flat_price_uses_the_simple_cycle_heat_rate(self):
        """Documents where $54.70 came from: run_solve passes gas_cost_mwh(year,
        heat_rate=SIMPLE_CYCLE_HEAT_RATE), so the pre-stack model priced every one of 8,760 hours
        as though a peaker were marginal."""
        assert 'SIMPLE_CYCLE_HEAT_RATE' in inspect.getsource(drv.run_solve)
