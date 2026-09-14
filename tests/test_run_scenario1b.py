"""
test_run_scenario1b.py

The Scenario 1B runner. 1B needs its own rather than a --scenario flag because three things differ
from Scenario 1: a five-checkpoint set, a 5% gas target from 2045, and a 6,000 MW gas cap.
"""
import inspect
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import run_scenario1b as r1b   # noqa: E402

import assumptions   # noqa: E402
import driver as drv  # noqa: E402
import lp_model as lp  # noqa: E402


class TestTheCheckpointSet:
    """2044 IS NOT OPTIONAL. Its own RPS target is 5% gas -- which IS 1B's 2045 target."""

    def test_there_are_five_checkpoints(self):
        assert r1b.CHECKPOINTS == (2030, 2035, 2040, 2044, 2045)

    def test_2044_carries_the_same_target_as_1bs_2045(self):
        """The reason the checkpoint exists. 1B's 2045 build should equal its 2044 build."""
        assert drv.gas_target_share(2044) == pytest.approx(0.05)

    def test_skipping_2044_is_what_produced_the_known_bug(self):
        """Appendix N.4: linking 2045 back to 2040 gave 'a physically nonsensical, wildly oversized
        2045 buildout'. Rule 10.3 -- a future reader must not trim the checkpoint set back to four
        for consistency with the other scenarios."""
        assert 'NOT OPTIONAL' in r1b.__doc__
        assert 'wildly oversized' in r1b.__doc__


class TestTheRunnerChecksWhatMatters:
    """For this scenario the 2044 -> 2045 increment is the diagnostic: same target, so it should be
    zero. A nonzero value means the linking is not carrying 2044 forward."""

    def test_it_tests_new_build_not_the_increment(self):
        """CORRECTED 2026-09-14 after the first real run. The cumulative total FALLS between
        checkpoints even when nothing is built, because the carried-forward fleet degrades at
        0.5%/yr: 125,193.88 x 0.995 = 124,567.91, exactly the -626 MW measured. An increment-based
        test can therefore NEVER read zero, and flagged a correct result as suspicious."""
        src = inspect.getsource(r1b.main)
        assert "final['solar_mw_new'] > 1.0" in src

    def test_the_degradation_arithmetic_is_explained_not_just_tolerated(self):
        """A reader seeing a negative increment needs to know it is expected and why."""
        src = inspect.getsource(r1b.main)
        assert 'degradation of the' in src
        assert '0.5%/yr' in src

    def test_a_real_nonzero_build_is_still_flagged_with_both_explanations(self):
        """It could mean broken linking, OR that the corrected 6,000 MW cap changed what 2045
        needs against the 4,722 MW N.4 was written at. The message must not assert either."""
        src = inspect.getsource(r1b.main)
        assert 'not carrying 2044 forward' in src
        assert 'cap has changed what 2045 needs' in src

    def test_the_gas_share_is_compared_against_the_prior_finding(self):
        src = inspect.getsource(r1b.main)
        assert '1.63%' in src


class TestTheNewCtIsCostedExternally:
    """The LP carries no capex penalty for gas -- only marginal fuel cost -- which is exactly why
    N.2 swept capacities rather than letting the LP choose. Given free rein the uncapped LP picked
    17,704 MW."""

    def test_it_is_not_in_the_lp_objective(self):
        assert 'costed externally' in inspect.getsource(r1b.solve_checkpoint).lower()

    def test_it_applies_only_from_2045(self):
        """Before 2045, 1B is identical to Scenario 1 and its capacity is Scenario 1's."""
        src = inspect.getsource(r1b.solve_checkpoint)
        assert "if year >= 2045 else 0.0" in src

    def test_the_figures_are_the_locked_sweep_result(self):
        assert assumptions.SCENARIO_1B_NEW_CT_MW == 1_278.0
        assert assumptions.SCENARIO_1B_NEW_CT_CAPEX_KW == 2_000.0

    def test_the_annualised_cost_is_reported_not_just_capital(self):
        """$2.56B of capital is $0.172B/yr -- the figure comparable to the LP objective, which is
        itself an annual quantity. Reporting only capital invites the same basis confusion that
        made salvage swamp the objective in the foresight runner."""
        capital = (assumptions.SCENARIO_1B_NEW_CT_MW * 1000
                   * assumptions.SCENARIO_1B_NEW_CT_CAPEX_KW)
        assert capital == pytest.approx(2.556e9, rel=0.01)
        assert capital * lp.CRF == pytest.approx(0.172e9, rel=0.05)
        assert 'new_ct_annualised_usd' in inspect.getsource(r1b.solve_checkpoint)


class TestItUsesTheReserveMarginVariant:
    def test_the_solver_class_is_the_reserve_variant(self):
        """1B had none until 2026-09-14, so it solved with no reserve margin while Scenarios 1 and
        3 carried the all-hours constraint."""
        assert 'Scenario1BWithReserveMargin' in inspect.getsource(r1b.solve_checkpoint)

    def test_convergence_and_unserved_are_recorded_per_checkpoint(self):
        src = inspect.getsource(r1b.solve_checkpoint)
        assert "'converged'" in src and "'unserved_mwh'" in src


class TestBothShareBasesAreReported:
    """MEASURED 2026-09-14: the runner printed "gas share at 2045: 3.66% against a 5% ceiling",
    comparing gas / TOTAL DEMAND against a ceiling defined on gas / (demand - nuclear). The correct
    comparison is 4.27% against 5%. At 2030 the two bases differ by FOURTEEN percentage points."""

    def test_both_are_carried_in_the_row(self):
        src = inspect.getsource(r1b.solve_checkpoint)
        assert "'gas_share_statutory'" in src and "'gas_share_of_demand'" in src

    def test_the_statutory_base_is_the_one_compared_against_the_ceiling(self):
        src = inspect.getsource(r1b.main)
        assert 'gas_share_statutory' in src
        assert 'the comparison that' in src

    def test_the_driver_computes_both(self):
        import driver as drv
        src = inspect.getsource(drv)
        assert 'gas_share_of_demand = g.sum()/demand.sum()' in src
        assert 'achieved_share = g.sum()/nonnuclear_demand' in src

    def test_a_failure_to_converge_is_reported_as_a_result(self):
        """2045 did not converge: the achieved share was unchanged across a TRIPLING of the
        allowance (0.0427 at frac 0.1649, 0.2562 and 0.5124). Gas cannot reach the ceiling at
        6,000 MW. That is Appendix N.4's conclusion surviving the capacity correction, not a solver
        failure -- and the runner must say so rather than reporting a bare 'not converged'.

        Joins adjacent string literals before matching. The message is built from several
        concatenated literals, so the source contains `binding ' 'constraint` -- normalising
        whitespace alone is not enough, because the QUOTE CHARACTERS survive. That caught my first
        two attempts at this assertion."""
        import re
        src = inspect.getsource(r1b.main)
        src = re.sub(r"['\"]\s*\+?\s*['\"]", "", src)       # join adjacent literals
        src = re.sub(r"\s+", " ", src)
        assert 'that is the result rather than a failure' in src
        assert 'binding constraint is physical fleet capacity' in src


class TestTheObjectiveIsLabelledIncremental:
    """Scenario 1B's 2045 objective ($8.25B) sits BELOW its 2044 ($13.29B) on higher demand,
    because 2045 builds nothing and so is charged almost no capital while operating a 124,568 MW
    fleet. Read as a cost trajectory that is simply wrong."""

    def test_the_column_says_incremental(self):
        assert 'incr obj $B' in inspect.getsource(r1b.main)

    def test_the_reason_is_stated(self):
        src = inspect.getsource(r1b.main)
        assert 'NOT A COST TRAJECTORY' in src
        assert 'not charged for' in src
