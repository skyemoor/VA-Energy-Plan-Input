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

    def test_the_increment_is_computed_and_reported(self):
        src = inspect.getsource(r1b.main)
        assert "final['solar_mw_total'] - penultimate['solar_mw_total']" in src

    def test_a_nonzero_increment_is_flagged_with_both_explanations(self):
        """It could mean broken linking, OR that the corrected 6,000 MW cap changed what 2045
        needs against the 4,722 MW N.4 was written at. The message must not assert either."""
        src = inspect.getsource(r1b.main)
        assert 'not carrying 2044 forward' in src
        assert '4,722 when N.4 was written' in src

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
