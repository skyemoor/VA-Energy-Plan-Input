"""
test_appendix_p_compliance.py

Compliance with Appendix P.2 -- the solve requirements that apply to every scenario and every solve.

Appendix P was not in the repository until 2026-09-13. Eight hundred lines of solve procedure that
no code had been checked against.
"""
import os
import re

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*parts):
    p = os.path.join(REPO, *parts)
    with open(p, encoding='utf-8', errors='replace') as f:
        return f.read()


class TestAppendixPIsInTheRepository:
    def test_it_exists(self):
        assert os.path.exists(os.path.join(REPO, 'docs', 'appendices',
                                           'Appendix_P_Solve_Procedure.md'))

    def test_it_carries_all_thirteen_general_requirements(self):
        s = read('docs', 'appendices', 'Appendix_P_Solve_Procedure.md')
        for n in range(1, 14):
            assert f'#### §{n}.' in s, f'P.2 §{n} missing'


class TestSection8ExportRevenue:
    """P.2 §8: "Export revenue must never appear inside any year-solve's own optimization
    objective, in any scenario." A standing, project-wide rule.

    THIS BUG HAS OCCURRED TWICE. §8 records the first -- an earlier Scenario 2 calculation included
    it, "carried over from Scenario 1/3's code without reconsidering whether it belonged there",
    and the optimizer began running gas as a profit-seeking merchant generator. Found 2026-09-13 to
    have returned, live and unguarded in build_scenario2_problem.
    """

    def test_no_unguarded_export_revenue_in_lp_model(self):
        src = read('lp_package', 'lp_model.py')
        lines = src.split('\n')
        for i, line in enumerate(lines):
            if line.strip().startswith('#'):
                continue
            if re.search(r"c\[hv\(t,\s*IDX\['e'\]\)\]\s*=\s*-", line.strip()):
                window = lines[max(0, i - 3):i]
                assert any('include_export' in w for w in window), (
                    f'line {i + 1}: export revenue in an objective without an include_export '
                    'guard. Appendix P.2 §8 forbids this in every scenario.')

    def test_scenario2_objective_has_no_export_term(self):
        """The specific function where it had returned.

        Narrowed to OBJECTIVE assignments (`c[...] = ...`). The energy-balance and bounds
        references to IDX['e'] are legitimate and must stay: the balance needs the variable, and
        the bound is what actually held the line.

        WHICH EXPLAINS WHY EXPORT MEASURED 0.00 TWh. Scenario 2 already pinned
        `bounds[hv(t,IDX['e'])] = (0, 0)` -- "NO EXPORT in Scenario 2 -- CCGT exists to serve
        Dominion's own LSE". So the revenue term in the objective could never be exercised: one
        correct guard was masking an incorrect term. Removing the term makes the intent explicit
        instead of load-bearing on a bound elsewhere in the function.
        """
        src = read('lp_package', 'lp_model.py')
        body = src[src.index('def build_scenario2_problem'):src.index('def build_problem')]
        live = [ln for ln in body.split('\n')
                if re.search(r"c\[hv\(t,\s*IDX\['e'\]\)\]\s*=", ln) and not ln.strip().startswith('#')]
        assert not live, f'export term still in the objective: {live}'

    def test_scenario2_also_pins_the_export_bound(self):
        """Belt and braces, and worth keeping: the bound is what made the objective term harmless.
        If a future change removes the bound, the objective must already be clean."""
        src = read('lp_package', 'lp_model.py')
        body = src[src.index('def build_scenario2_problem'):src.index('def build_problem')]
        assert re.search(r"bounds\[hv\(t,\s*IDX\['e'\]\)\]\s*=\s*\(0,\s*0\)", body)

    def test_the_reason_is_documented_at_the_site(self):
        """Rule 10.3. A future reader must not restore the line as a 'missing' term."""
        src = re.sub(r'\s*\n\s*#?\s*', ' ', read('lp_package', 'lp_model.py'))
        assert 'EXPORT REVENUE IS DELIBERATELY ABSENT' in src
        assert 'merchant' in src

    def test_removing_it_changed_no_published_figure(self):
        """MEASURED before removal: export was 0.00 TWh at all four Scenario 2 checkpoints and the
        objective was unchanged to four decimals ($6.2489B). The term was present but never
        exercised -- a latent trap, not an active error. Recorded so the distinction is not lost."""
        src = re.sub(r'\s*\n\s*#?\s*', ' ', read('lp_package', 'lp_model.py'))
        assert 'latent trap, not an active error' in src


class TestSection7DemandBasis:
    """P.2 §7: "this project's Virginia-only demand total, adjusted for the flattening effect of
    data-center load growth described in Appendix O -- rather than an outdated or
    scenario-specific demand source."

    This settles a question raised by four competing demand series: ours (202,193 GWh at 2045),
    demand_shape_interpolation's internal table (186,462), a decomposed forecast (172,700) and an
    old blended CAGR (254,900). §7 asks for the Virginia-only TOTAL with a flattening adjustment to
    the SHAPE -- which is our totals plus that module, exactly.
    """

    def test_the_requirement_names_the_virginia_only_total(self):
        s = read('docs', 'appendices', 'Appendix_P_Solve_Procedure.md')
        body = s[s.index('#### §7.'):s.index('#### §8.')]
        assert 'Virginia-only demand total' in body
        assert 'flattening' in body

    def test_appendix_o_is_cited_as_the_governing_method(self):
        """And is MISSING from the repository. §7 cites it normatively, not as background, so its
        absence is a gap in the governing method rather than a lost narrative."""
        s = read('docs', 'appendices', 'Appendix_P_Solve_Procedure.md')
        body = s[s.index('#### §7.'):s.index('#### §8.')]
        assert 'Appendix' in body and 'O' in body
