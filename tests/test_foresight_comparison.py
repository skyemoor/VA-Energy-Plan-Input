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

    def test_salvage_is_passed_per_build_variable_not_averaged(self):
        """An earlier version averaged four credits into one figure. assemble() applies the credit
        to EVERY build variable in the period, so an average gives each variable a number belonging
        to none of them -- solar, storage power and storage energy have different capex bases."""
        src = inspect.getsource(rfc.run_perfect_foresight)
        assert '/ 4 for y in CHECKPOINTS' not in src
        assert 'salvage_credit_per_mw(y, _capex_by_build_var(y)) for y in CHECKPOINTS' in src

    def test_foresight_side_passes_salvage_into_the_objective(self):
        """Under perfect foresight it must sit INSIDE the objective, where it shapes what gets
        built. Brown: 'the perfect foresight model is Type 1 WITH salvage value'."""
        assert 'salvage_usd_by_period=salvage' in inspect.getsource(rfc.run_perfect_foresight)

    def test_the_myopic_total_nets_salvage_off(self):
        src = inspect.getsource(rfc.main)
        assert "r['obj_usd'] - r['salvage_usd']" in src


class TestSalvageArithmetic:

    def test_the_credit_is_on_an_ANNUITY_basis(self):
        """THE BASIS WAS WRONG FIRST TIME, caught in a live run. build_problem charges build
        variables as CRF x capex x 1000 -- an ANNUAL cost in $/MW-yr, not the capital outlay.
        Crediting raw undepreciated CAPITAL against an annuity-based objective made salvage swamp
        the cost: $6.50B reported against a $4.13B objective at 2030, larger than the entire year.

        Multiplying by CRF puts the credit on the same basis as the charge."""
        import lp_model as lp
        capex = rfc._capex_by_build_var(2045)
        salv = rfc.salvage_credit_per_mw(2045, capex)
        assert salv[0] == pytest.approx(capex[0] * lp.CRF, rel=1e-9)

    def test_a_2045_build_keeps_its_full_value(self):
        """Zero of 25 years elapsed at the horizon -- so the credit is the full annuity."""
        import lp_model as lp
        capex = rfc._capex_by_build_var(2045)
        salv = rfc.salvage_credit_per_mw(2045, capex)
        assert salv[0] == pytest.approx(capex[0] * lp.CRF, rel=1e-9)

    def test_salvage_is_small_relative_to_the_objective(self):
        """The sanity check the live run failed. At 2030's measured 8,660 MW of solar the credit is
        ~$0.32B against a $4.13B objective -- proportionate. It was $6.50B before the fix."""
        import lp_model as lp
        salv = rfc.salvage_credit_per_mw(2030, rfc._capex_by_build_var(2030))
        assert salv[0] * 8_660 / 1e9 < 1.0

    def test_a_2030_build_keeps_ten_of_twenty_five(self):
        """25-year life, built 2030, horizon 2045: FIFTEEN years elapsed, TEN remaining.

        I asserted 15/25 when writing this and the test caught it. The confusion is easy and worth
        naming: the elapsed span (2045 − 2030 = 15) is the part that is USED UP, not the part that
        survives. Getting it backwards would inflate every salvage credit by 50% and bias the
        foresight comparison toward late building."""
        capex = rfc._capex_by_build_var(2030)
        salv = rfc.salvage_credit_per_mw(2030, capex)
        import lp_model as lp
        assert salv[0] == pytest.approx(capex[0] * lp.CRF * 10 / 25, rel=1e-6)

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


class TestVerificationIsSymmetric:
    """P.2 §11. The myopic side verifies through solve_with_reserve_margin; the foresight side had
    nothing, so the comparison would have held the two to different standards."""

    def test_the_foresight_side_verifies(self):
        src = inspect.getsource(rfc.run_perfect_foresight)
        assert 'mp.verify_solution(assembled, res.x)' in src

    def test_the_verification_travels_with_the_result(self):
        assert "'verification': verification" in inspect.getsource(rfc.run_perfect_foresight)


class TestBuildOrderingIsAsserted:
    """_capex_by_build_var and _BUILD_RESULT_KEYS are aligned POSITIONALLY and nothing in the type
    system enforces it. A reordering of either would credit solar salvage against storage MW
    without raising."""

    def test_the_check_passes(self):
        assert rfc._assert_build_ordering() is True

    def test_it_runs_before_any_solve(self):
        assert '_assert_build_ordering()' in inspect.getsource(rfc.main)

    def test_it_would_catch_a_swap(self):
        """Checked by magnitude, the only available signal: solar $/MW is ~17x storage energy
        $/MWh at 2045, so a swap shows up immediately."""
        capex = rfc._capex_by_build_var(2045)
        assert capex[0] > capex[2] * 5

    def test_salvage_uses_the_increment_not_the_cumulative_total(self):
        """S_mw, not S_mw_total. Salvage credits what each VINTAGE built -- a 2035 build has 2035's
        remaining life -- and crediting the cumulative total at every checkpoint would count the
        same capacity four times. The reported solar_mw_total field is the right figure for the
        build trajectory and the wrong one here; the two differing is deliberate.

        MOVED 2026-09-14: this lived in run_foresight_comparison._build_value, which was orphaned
        when build_salvage_credit replaced the myopic salvage path. The canonical ordering is now
        levelised_cost.BUILD_RESULT_KEYS, used by both runners."""
        from levelised_cost import BUILD_RESULT_KEYS
        assert BUILD_RESULT_KEYS[0] == 'S_mw'
        assert 'S_mw_total' in inspect.getsource(rfc.run_myopic)      # the reported trajectory
        import levelised_cost as lc
        assert 'CUMULATIVE' in inspect.getsource(lc.build_salvage_credit)


class TestScopeIsStated:
    def test_the_checkpoint_only_limitation_is_documented(self):
        """Both sides use the same four checkpoints, so the comparison is like-for-like -- but
        neither is an SLCOE over the full twenty-year stream."""
        assert 'WHAT THIS CANNOT SHOW' in rfc.__doc__
        assert 'not twenty years' in rfc.__doc__
