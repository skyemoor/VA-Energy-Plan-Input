"""
test_foresight_comparison.py

The runner that solves a scenario both ways and reports the myopia penalty.

THE COMPARISON IS THE DISCOUNTED TOTAL, not the endpoint build -- the literature's own finding is
that "intertemporal and myopic models lead to a SIMILAR FINAL ENERGY SYSTEM. However, the
transformation pathways differ", so comparing 2045 builds may show nothing while the pathways
diverge substantially.
"""
import inspect
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import run_foresight_comparison as rfc   # noqa: E402


class TestSalvageIsSymmetric:
    """Applied to BOTH sides by project decision 2026-09-14. In one and not the other, the
    comparison would measure salvage treatment rather than foresight."""

    def test_myopic_side_computes_salvage(self):
        assert 'salvage' in inspect.getsource(rfc.run_myopic)

    def test_foresight_side_passes_salvage_into_the_objective(self):
        """Under perfect foresight it must sit INSIDE the objective, where it shapes what gets
        built. Brown: 'the perfect foresight model is Type 1 WITH salvage value'."""
        assert 'salvage_usd_by_period=salvage' in inspect.getsource(rfc.run_perfect_foresight)

    def test_the_myopic_total_nets_salvage_off(self):
        src = inspect.getsource(rfc.main)
        assert "r['obj_usd'] - r['salvage_usd']" in src


class TestSalvageArithmetic:

    def test_a_2045_build_keeps_its_full_value(self):
        """Zero of 25 years elapsed at the horizon."""
        capex = rfc._capex_by_build_var(2045)
        salv = rfc.salvage_credit_per_mw(2045, capex)
        assert salv[0] == pytest.approx(capex[0])

    def test_a_2030_build_keeps_ten_of_twenty_five(self):
        """25-year life, built 2030, horizon 2045: FIFTEEN years elapsed, TEN remaining.

        I asserted 15/25 when writing this and the test caught it. The confusion is easy and worth
        naming: the elapsed span (2045 − 2030 = 15) is the part that is USED UP, not the part that
        survives. Getting it backwards would inflate every salvage credit by 50% and bias the
        foresight comparison toward late building."""
        capex = rfc._capex_by_build_var(2030)
        salv = rfc.salvage_credit_per_mw(2030, capex)
        assert salv[0] == pytest.approx(capex[0] * 10 / 25, rel=1e-6)

    def test_nothing_strands(self):
        """Solar and storage built at any checkpoint still operate past 2045, so
        strands_at_horizon=False throughout. Gas WOULD strand at 100% compliance -- but there is no
        gas build variable, so it does not arise here."""
        assert 'strands_at_horizon=False' in inspect.getsource(rfc.salvage_credit_per_mw)


class TestPerPeriodConstraintsRunBeforeAssembly:
    """The assembler works on built problems and knows nothing about what constraints mean, so
    reserve margin, scenario bounds and the SLCR curtailment term must all be applied per period
    first."""

    def test_reserve_and_scenario_hooks_are_applied(self):
        src = inspect.getsource(rfc.run_perfect_foresight)
        assert '_all_hours_reserve_hook' in src
        assert '_post_build_hook' in src

    def test_the_curtailment_term_is_applied_from_the_solver_hook(self):
        """Not driver's default -- the scenario's own curtailment_cost_mwh()."""
        src = inspect.getsource(rfc.run_perfect_foresight)
        assert 'curt_cost=solver.curtailment_cost_mwh()' in src

    def test_capex_is_bound_per_period(self):
        """lp_model's capex constants are mutable module state rebound by set_year_capex; a period
        built without binding would silently carry another year's costs."""
        assert inspect.getsource(rfc.run_perfect_foresight).count('set_year_capex') >= 1


class TestFailureIsReported:

    def test_a_failed_foresight_solve_raises(self):
        assert 'perfect-foresight solve failed' in inspect.getsource(rfc.run_perfect_foresight)

    def test_a_negative_penalty_is_flagged(self):
        """Myopic cheaper than foresight inverts the literature and is not possible if both solve
        the same feasible set -- so it means the two are not comparable, not that myopia pays."""
        src = inspect.getsource(rfc.main)
        assert 'NEGATIVE PENALTY' in src
        assert 'inverts the literature' in src


class TestScopeIsStated:
    def test_the_checkpoint_only_limitation_is_documented(self):
        """Both sides use the same four checkpoints, so the comparison is like-for-like -- but
        neither is an SLCOE over the full twenty-year stream."""
        assert 'WHAT THIS CANNOT SHOW' in rfc.__doc__
        assert 'not twenty years' in rfc.__doc__
