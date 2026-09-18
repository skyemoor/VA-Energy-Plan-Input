"""
test_lp_segment_spec.py

The LP segment specification: what a scenario adds beyond the physics and the statutory carve-out.

WHY IT EXISTS. build_problem measured a cyclomatic complexity of 67 against Rule 15's limit of 15,
with five separate checks of the same scenario flag scattered across five LP layers -- validation,
input preparation, equality rows, bounds and objective. Each asked "is this Scenario 3?" and
answered differently. Reducing_Cyclomatic_Complexity.md names this case: replacing a repeated
type-check with polymorphism "reduces complexity across every call site simultaneously".
"""
import numpy as np
import pytest
from scipy import sparse

import checkpoint_solver as cs
import lp_model as lp


def _core_problem():
    """A minimal assembled problem, standing in for whatever the core built."""
    return {'c': np.array([1.0, 2.0]), 'bounds': [(0, 1), (0, 1)],
            'A_eq': sparse.csr_matrix(np.array([[1.0, 1.0]])), 'b_eq': np.array([5.0]),
            'A_ub': None, 'b_ub': None}


class TestTheEmptySpecIsTheCommonCase:
    """Scenarios 1, 1B and 2 add nothing. They return immediately and never execute segment logic,
    which is what takes complexity DOWN rather than moving it into the assembler."""

    def test_the_base_class_returns_empty(self):
        assert cs.CheckpointSolver.lp_segment_spec(cs.CheckpointSolver).is_empty

    @pytest.mark.parametrize('name', ['Scenario1Solver', 'Scenario1BSolver', 'Scenario2Solver'])
    def test_scenarios_without_their_own_segment_inherit_empty(self, name):
        solver = getattr(cs, name)
        assert solver.lp_segment_spec(solver).is_empty

    def test_applying_an_empty_spec_changes_nothing(self):
        problem = _core_problem()
        result = lp.apply_segment_spec(problem, lp.EMPTY_SEGMENT_SPEC)
        assert len(result['c']) == 2
        assert result['A_eq'].shape == (1, 2)
        assert 'segments' not in result

    def test_it_is_not_a_not_implemented_error(self):
        """Unlike gas_retirement_schedule and new_gas_technology, where every scenario makes a real
        choice and inheriting silently is the failure mode, adding nothing here is a meaningful and
        correct answer. Forcing each scenario to declare it would be ceremony that hides which one
        actually differs."""
        # Checked on the BEHAVIOUR, not the source: the docstring mentions NotImplementedError
        # while explaining why this is not one, and a text search cannot tell prose from code.
        assert cs.CheckpointSolver.lp_segment_spec(cs.CheckpointSolver) is lp.EMPTY_SEGMENT_SPEC


class TestTheSpecValidatesItself:
    """Rule 5: a mismatch must raise rather than silently attaching a bound to the wrong column."""

    def test_mismatched_widths_raise(self):
        with pytest.raises(ValueError, match='must line up one-to-one'):
            lp.LpSegmentSpec(extra_column_names=('a', 'b'), extra_column_bounds=((0, 1),),
                             extra_objective_terms=(1.0, 2.0), label='bad')

    def test_an_unknown_row_kind_raises(self):
        with pytest.raises(ValueError, match="expected 'eq' or 'ub'"):
            lp.LpSegmentSpec(extra_rows=(('lt', {}, 0.0),), label='bad')

    def test_a_spec_with_columns_is_not_empty(self):
        spec = lp.LpSegmentSpec(extra_column_names=('x',), extra_column_bounds=((0, 1),),
                                extra_objective_terms=(1.0,), label='x')
        assert not spec.is_empty


class TestTheAssemblerOwnsIndexing:
    """A scenario that computed its own column numbers could collide with the core's silently --
    the matrices still solve, and the answer is simply wrong."""

    def test_extra_columns_are_appended_after_the_core(self):
        spec = lp.LpSegmentSpec(extra_column_names=('x', 'y'),
                                extra_column_bounds=((0, 10), (0, 20)),
                                extra_objective_terms=(3.0, 4.0), label='t')
        result = lp.apply_segment_spec(_core_problem(), spec)
        assert len(result['c']) == 4
        assert list(result['c'][2:]) == [3.0, 4.0]
        assert result['segments'][0]['columns'] == {'x': 2, 'y': 3}

    def test_rows_reference_columns_by_name(self):
        spec = lp.LpSegmentSpec(extra_column_names=('x',), extra_column_bounds=((0, 10),),
                                extra_objective_terms=(3.0,),
                                extra_rows=(('eq', {'x': 1.0, 0: -1.0}, 0.0),), label='t')
        result = lp.apply_segment_spec(_core_problem(), spec)
        assert result['A_eq'].shape == (2, 3)
        assert len(result['b_eq']) == 2

    def test_the_core_matrix_is_widened_for_the_new_columns(self):
        """The core built its matrix before the extra columns existed, so it is too narrow.
        Explicit zero padding rather than broadcasting, which succeeds on some sparse formats and
        fails on others."""
        spec = lp.LpSegmentSpec(extra_column_names=('x',), extra_column_bounds=((0, 1),),
                                extra_objective_terms=(0.0,), label='t')
        result = lp.apply_segment_spec(_core_problem(), spec)
        assert result['A_eq'].shape[1] == len(result['c'])

    def test_an_unresolvable_column_raises(self):
        spec = lp.LpSegmentSpec(extra_column_names=('x',), extra_column_bounds=((0, 1),),
                                extra_objective_terms=(1.0,),
                                extra_rows=(('eq', {'nope': 1.0}, 0.0),), label='b')
        with pytest.raises(KeyError, match='neither one of its own extra columns'):
            lp.apply_segment_spec(_core_problem(), spec)

    def test_inequality_rows_go_to_the_inequality_matrix(self):
        spec = lp.LpSegmentSpec(extra_column_names=('x',), extra_column_bounds=((0, 1),),
                                extra_objective_terms=(1.0,),
                                extra_rows=(('ub', {'x': 1.0}, 7.0),), label='t')
        result = lp.apply_segment_spec(_core_problem(), spec)
        assert result['A_ub'].shape == (1, 3)
        assert list(result['b_ub']) == [7.0]
        assert result['A_eq'].shape[0] == 1, 'equality matrix must not gain a row'


class TestComplexityStaysUnderTheLimit:
    """Rule 15. The whole point of the exercise."""

    @pytest.mark.parametrize('name', ['apply_segment_spec', '_append_segment_rows'])
    def test_the_new_functions_are_well_under_fifteen(self, name):
        import ast
        import inspect
        tree = ast.parse(inspect.getsource(getattr(lp, name)))
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.IfExp, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1
            elif isinstance(node, ast.comprehension):
                complexity += 1 + len(node.ifs)
        assert complexity <= 15, f'{name} is at {complexity}'
