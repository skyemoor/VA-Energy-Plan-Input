"""
test_solve_checkpoint_resolve.py

Locks the 2026-09-12 fix to solve_checkpoint.py's dual-extraction re-solve.

THE BUG. The re-solve called run_solve WITHOUT capacity_cap_mw and WITHOUT the prior_* kwargs,
making it an unlinked checkpoint with no prior-checkpoint build and no gas cap -- a DIFFERENT
optimisation from the one whose build figures were reported beside it. Duals, the dual profile, the
hourly dispatch and every derived statistic described a problem that was not the scenario.

WHY IT SURVIVED TESTING. Scenario 1 at 2030 is the FIRST checkpoint, so prior_* is all zeros and
the two calls are nearly identical. The script was verified on exactly that case. Scenario 3 at
2045 is the fourth checkpoint with substantial carried-forward build, and there the two problems
diverged badly enough to produce a dispatch that could not balance: ~4,300 MW of supply against
~47,900 MW of demand, charging and curtailment, with zero unserved energy.

Testing the cheap case is how a whole afternoon of 2045 analysis got built on the wrong problem.
"""
import inspect
import os


def source():
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                     'solve_checkpoint.py')
    with open(p) as f:
        return f.read()


class TestResolveReproducesTheSolverCall:

    def test_capacity_cap_is_passed(self):
        """Its absence made the re-solve an uncapped problem."""
        s = source()
        assert 'capacity_cap_mw=solver.apply_gas_cap()' in s

    def test_prior_kwargs_are_passed(self):
        """Without these the checkpoint is unlinked -- no prior build carried forward."""
        assert 'solver._prior_kwargs()' in source()

    def test_kwargs_come_from_the_solver_not_reassembled_by_hand(self):
        """Rebuilding them by hand is how they drifted. Sourcing from the solver's own accessors
        means the re-solve cannot diverge from what converge_and_solve() ran."""
        s = source()
        for accessor in ('_prior_kwargs()', '_gas_merit_order_kwargs()', '_distributed_kwargs()'):
            assert f'solver.{accessor}' in s

    def test_the_dead_extra_dict_is_gone(self):
        """The original built an `extra` dict of leftover kwargs and then never passed it -- the
        code looked like it threaded them through and did not."""
        s = source()
        assert 'extra = dict(kwargs)' not in s


class TestCrossCheckGuardsTheOutput:
    """Rule 4: cross-verify against the solve whose results are being reported."""

    def test_builds_are_compared_before_writing(self):
        s = source()
        assert 'Re-solve does not reproduce the converged solve' in s

    def test_mismatch_refuses_to_write_results(self):
        """Writing duals that describe a different problem is worse than writing nothing."""
        s = source()
        assert 'Not writing results' in s

    def test_the_bug_is_documented_at_the_fix_site(self):
        """Rule 10.3: name the specific wrong behaviour, so a future edit does not reintroduce it
        by simplifying what looks like an odd, unexplained call signature."""
        s = source()
        assert 'BUG FIXED 2026-09-12' in s
        assert 'could not balance' in s
