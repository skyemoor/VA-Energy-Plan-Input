"""
test_curtailment_cost.py

Curtailment cost -- $100/MWh, and why it is a PRICE rather than a tie-breaker.

Internal Debugging Log #20 set it "permanently" and defended it as "a defensible figure (same order
of magnitude as gas cost and the export price), not another arbitrary tie-breaker", replacing an
earlier $1.0/MWh which had itself replaced $0.01. The distinction matters for cost accounting: a
shaping term could legitimately be netted out of an SLCOE; a price cannot.

WHEN FIRST APPLIED it drove curtailment from 141.8 million MWh to EXACTLY ZERO at 2045, with the LP
rebalancing toward less solar overbuild (-22.6%) and substantially more iron-air (+148%).

IT REGRESSED BY 2026-09-13: build_problem() carried no curtailment cost at all, while
build_dispatch_problem() still set 100.0 behind a comment claiming the two matched.
"""
import inspect

import pytest

import assumptions
import checkpoint_solver as cs
import driver as drv
import lp_model as lp


class TestOneSourceOfTruth:

    def test_the_constant_is_the_model_constrained_figure(self):
        """BASELINE MOVED 2026-09-13, $100 -> $25, and the reason is a disclosed limitation rather
        than a revised estimate. $100 sits ABOVE the $30/MWh storage-resistor threshold set by Bath
        pumped hydro, so the LP dumps surplus through round-trip losses instead of curtailing --
        4,710 hours of simultaneous Na-ion charge/discharge at 2045.

        The economically defensible figure is retained separately as
        CURTAILMENT_COST_ECONOMIC_MWH, because #20's defence of it was never refuted: the model
        simply cannot represent it without structural complementarity."""
        assert assumptions.CURTAILMENT_COST_MWH == 25.0
        assert assumptions.CURTAILMENT_COST_ECONOMIC_MWH == 100.0

    def test_lp_model_references_the_constant_not_a_literal(self):
        """Both build_dispatch_problem sites previously hardcoded 100.0."""
        src = inspect.getsource(lp.build_dispatch_problem)
        assert 'CURTAILMENT_COST_MWH' in src

    def test_driver_default_is_none_so_it_resolves_to_the_constant(self):
        """A LITERAL default is the failure mode -- that is how 5.0 persisted in driver while
        build_dispatch_problem used 100.0, twenty times apart."""
        for f, param in ((drv.apply_slcr_constraint, 'curt_cost'),
                         (drv.run_solve, 'slcr_curt_cost')):
            assert inspect.signature(f).parameters[param].default is None

    def test_resolution_produces_the_constant(self):
        src = inspect.getsource(drv.apply_slcr_constraint)
        assert 'assumptions.CURTAILMENT_COST_MWH if curt_cost is None' in src


class TestScenarioOverridable:
    """Rule 1 and project direction 2026-09-13: the base class holds what is common; a scenario
    that needs different behaviour overrides rather than the base branching on scenario identity."""

    def test_base_class_returns_the_constant(self):
        s = cs.CheckpointSolver.__new__(cs.CheckpointSolver)
        assert cs.CheckpointSolver.curtailment_cost_mwh(s) == assumptions.CURTAILMENT_COST_MWH

    def test_a_subclass_can_override(self):
        class Cheap(cs.Scenario1Solver):
            def curtailment_cost_mwh(self):
                return 5.0
        s = Cheap.__new__(Cheap)
        assert Cheap.curtailment_cost_mwh(s) == 5.0

    def test_the_hook_reaches_run_solve(self):
        s = cs.CheckpointSolver.__new__(cs.CheckpointSolver)
        assert cs.CheckpointSolver._curtailment_kwargs(s) == {
            'slcr_curt_cost': assumptions.CURTAILMENT_COST_MWH}

    def test_every_solver_call_site_binds_it(self):
        """converge_frac runs run_solve per iteration, so a call site that fails to bind would use
        the fallback for every iteration and only the final solve would be right.

        Matches whole CALL EXPRESSIONS, not lines -- these calls span several lines and the binding
        sits on the last one, so a line-based check reports a false failure."""
        import re
        src = inspect.getsource(cs)
        for m in re.finditer(r'drv\.(run_solve|converge_frac)\(', src):
            depth, j = 0, m.end() - 1
            while True:
                if src[j] == '(':
                    depth += 1
                elif src[j] == ')':
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            call = src[m.start():j + 1]
            # `drv.converge_frac()` with empty parens is PROSE in a docstring, not a call. A
            # paren-matching scan cannot tell the two apart, and an earlier automated edit that
            # made the same mistake corrupted a docstring by inserting an argument into it.
            if call.endswith('()'):
                continue
            assert '_curtailment_kwargs()' in call or 'slcr_curt_cost' in call, (
                f'unbound call site: {call[:70]}...')

    def test_converge_frac_accepts_and_forwards_it(self):
        """It previously did not, so every convergence iteration silently used run_solve's own
        default while only the final solve got the right value."""
        assert 'slcr_curt_cost' in inspect.signature(drv.converge_frac).parameters
        assert 'slcr_curt_cost' in inspect.getsource(drv.converge_frac)


class TestItIsAPriceNotATieBreaker:
    def test_the_economic_figure_is_the_same_order_as_gas_cost(self):
        """#20's own defence, which applies to the ECONOMIC figure. At 2045 gas marginal is
        ~$47/MWh; $100 is the same order of magnitude, where $0.01 and $1.00 plainly were not.

        The value actually used ($25) is lower not because that defence failed but because the
        model cannot represent $100 -- see test_the_constant_is_the_model_constrained_figure."""
        gas = lp.gas_cost_mwh(2045, heat_rate=lp.CCGT_HEAT_RATE)
        assert 0.1 < gas / assumptions.CURTAILMENT_COST_ECONOMIC_MWH < 10.0

    def test_the_regression_is_documented_at_the_constant(self):
        """Rule 10.3: a future reader must not restore a lower value as a 'reasonable' default."""
        import re
        src = re.sub(r'\s*\n\s*#?:?\s*', ' ', inspect.getsource(assumptions))
        assert 'not another arbitrary tie-breaker' in src
        assert '141.8 million MWh' in src
