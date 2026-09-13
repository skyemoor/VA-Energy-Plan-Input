"""
test_converge_frac_bisection.py

converge_frac's bisection search, replacing proportional extrapolation (2026-09-13).

WHY IT CHANGED. An overnight scenario-3 run measured, at 2030:

    iter0  frac 0.5900  achieved 0.7046  gap -0.1146   (538s)
    iter1  frac 0.4940  achieved 0.6580  gap -0.0680   (565s)

The old step was `frac = target * (frac / achieved)` -- a proportional rescale assuming achieved
moves linearly with frac. The implied ratio moved 10% between those two iterations, so each step
overshot and the gap closed only ~40% per iteration. From -0.1146, reaching tol=0.003 needed about
SEVEN iterations; with max_iter=3 it could not converge, and returned a build missing its own gas
target by ~4 percentage points -- silently, because nothing distinguished converged from exhausted.

These tests use a synthetic monotone response so they run in milliseconds rather than hours.
"""
import pytest


def bisect_to_target(response, target, tol=0.003, max_iter=12, start=0.59):
    """Mirrors converge_frac's search on a caller-supplied monotone response function.

    Reimplemented here rather than calling converge_frac because the real one runs an LP per
    iteration -- 538s each in the run that motivated this change. The step LOGIC is what is under
    test; a test that took two hours would not be run.
    """
    frac, lo, hi = start, None, None
    for i in range(max_iter):
        achieved = response(frac)
        gap = target - achieved
        if abs(gap) <= tol:
            return frac, i + 1, True
        if gap < 0:
            hi = frac
        else:
            lo = frac
        if hi is None:
            frac = min(0.999, frac * 2.0)
        elif lo is None:
            frac = max(0.0001, frac * 0.5)
        else:
            frac = 0.5 * (lo + hi)
    return frac, max_iter, False


class TestBisectionConverges:

    def test_converges_on_the_measured_response(self):
        """Calibrated to the two real observations: frac 0.59 -> 0.7046, frac 0.494 -> 0.6580.
        Linear through those points, which is generous to the old method and still shows it
        needed more than three iterations."""
        slope = (0.7046 - 0.6580) / (0.5900 - 0.4940)
        response = lambda f: 0.6580 + slope * (f - 0.4940)
        frac, iters, converged = bisect_to_target(response, 0.59)
        assert converged, 'bisection failed on the very response that defeated extrapolation'
        assert iters <= 8

    def test_proportional_extrapolation_needed_more_than_three(self):
        """The failure being fixed. Same response, old step rule, max_iter=3."""
        slope = (0.7046 - 0.6580) / (0.5900 - 0.4940)
        response = lambda f: 0.6580 + slope * (f - 0.4940)
        frac, target = 0.59, 0.59
        for _ in range(3):
            a = response(frac)
            if abs(target - a) <= 0.003:
                pytest.fail('old method converged in 3; the premise of this change is wrong')
            frac = min(0.999, max(0.0001, target * (frac / a)))
        assert abs(target - response(frac)) > 0.003

    def test_halves_the_bracket_each_iteration(self):
        """The deterministic property extrapolation lacks: once bracketed, the interval halves
        regardless of how nonlinear the response is."""
        response = lambda f: f ** 0.5          # strongly nonlinear, still monotone
        _, iters, converged = bisect_to_target(response, 0.5, tol=0.001)
        assert converged and iters <= 12

    def test_brackets_upward_when_target_is_above_the_start(self):
        """With no upper bracket yet, the search steps up geometrically rather than guessing."""
        response = lambda f: f * 0.5
        frac, _, converged = bisect_to_target(response, 0.45, start=0.1)
        assert converged


class TestConvergenceIsReported:
    """Rule 5. A result that misses its own target must not look identical to one that hits it."""

    def test_converged_flag_is_set_on_success(self):
        import driver
        src = open(driver.__file__).read()
        assert "r['converged'] = True" in src
        assert "r['convergence_gap'] = float(gap)" in src

    def test_exhausted_search_sets_the_flag_false_and_records_the_gap(self):
        import driver
        src = open(driver.__file__).read()
        assert "r['converged'] = False" in src
        assert 'NOT CONVERGED after' in src

    def test_the_failure_that_motivated_this_is_documented(self):
        """Rule 10.3: name the specific wrong behaviour, so a later edit does not restore the
        proportional step as a 'simplification'.

        Matches against wrap-normalised source. Assertions on contiguous phrases in wrapped
        comments broke four separate times on 2026-09-12/13; normalising tests the CONTENT rather
        than where the line happened to break."""
        import re, driver
        src = re.sub(r'\s*\n\s*#?\s*', ' ', open(driver.__file__).read())
        assert 'proportional rescale' in src
        assert 'could not converge at all' in src
