"""
test_convergence_verdict_reaches_result.py

The convergence verdict must reach the result a caller actually reads.

THE GAP, found 2026-09-13 by auditing a result against Appendix P.2 §11. converge_frac() sets
'converged' and 'convergence_gap' on ITS OWN result -- but every caller in checkpoint_solver
DISCARDS that result, re-solving at the converged fraction and returning the new one. So the flag
never reached a caller, and a build that missed its gas target was indistinguishable from one that
hit it.

That is precisely the failure the flag was added to prevent, defeated by where it was attached.

AND THERE ARE THREE CONVERGENCE PATHS. Fixing one left the others silently wrong -- which is how
the original gap survived. The audit found only two of three bound after the first fix.
"""
import re

import pytest

import checkpoint_solver as cs


def _paths_with_verdict():
    """Every converge_frac call site, and whether its enclosing method carries the verdict."""
    src = open(cs.__file__).read()
    out = []
    for m in re.finditer(r'converge_result, history = drv\.converge_frac', src):
        start = src.rfind('\n    def ', 0, m.start())
        name = src[start:src.index('(', start)].strip().replace('def ', '')
        end = src.find('\n    def ', m.start())
        body = src[start:end if end != -1 else len(src)]
        out.append((name, '_carry_convergence_verdict' in body))
    return out


class TestEveryConvergencePathCarriesIt:

    def test_there_are_three_paths(self):
        """If this changes, the check below may be scanning the wrong set."""
        assert len(_paths_with_verdict()) == 3

    def test_all_three_carry_the_verdict(self):
        unbound = [n for n, ok in _paths_with_verdict() if not ok]
        assert not unbound, f'convergence paths not carrying the verdict: {unbound}'

    def test_the_helper_is_shared_not_copied(self):
        """Three copies would drift. The original gap survived because one path was fixed and the
        others were not."""
        src = open(cs.__file__).read()
        assert src.count('def _carry_convergence_verdict') == 1


class TestTheHelperItself:

    def test_it_copies_all_three_fields(self):
        solver = cs.CheckpointSolver.__new__(cs.CheckpointSolver)
        solver.result = {}
        cs.CheckpointSolver._carry_convergence_verdict(
            solver, {'converged': True, 'convergence_gap': 0.001, 'achieved_share': 0.42})
        assert solver.result['converged'] is True
        assert solver.result['convergence_gap'] == pytest.approx(0.001)
        assert solver.result['achieved_share'] == pytest.approx(0.42)

    def test_a_missing_flag_defaults_to_NOT_converged(self):
        """Rule 5: absence must not read as success. A result whose convergence is unknown is not
        a converged result."""
        solver = cs.CheckpointSolver.__new__(cs.CheckpointSolver)
        solver.result = {}
        cs.CheckpointSolver._carry_convergence_verdict(solver, {})
        assert solver.result['converged'] is False

    def test_it_raises_before_a_result_exists(self):
        solver = cs.CheckpointSolver.__new__(cs.CheckpointSolver)
        solver.result = None
        with pytest.raises(RuntimeError, match='before a result exists'):
            cs.CheckpointSolver._carry_convergence_verdict(solver, {'converged': True})
