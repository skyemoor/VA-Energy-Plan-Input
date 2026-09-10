"""
test_run_all_stages.py

Tests for run_all.py's stage dependency logic.

WHY THIS EXISTS: unmet_prerequisites() has been wrong twice, both times in ways that only appeared
when someone actually ran the pipeline rather than when it was written.

  1. `inputs` was declared as data and never read. A stage ran even when the stage producing its
     inputs had skipped, then died on a missing file.
  2. Prerequisites were then judged on which stages ran in the current invocation. Under --only
     the upstream stages never entered the loop, so their outputs were reported missing even when
     sitting on disk -- a false block.

Both were reported by a user, not caught here. These tests exercise the specific usage patterns
that exposed them.
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import pytest
from run_all import Stage, STAGES


class FakeStage(Stage):
    """A Stage whose outputs live in a temp directory, so disk state can be controlled directly."""

    def __init__(self, name, output_paths, inputs=()):
        super().__init__(name, f'fake {name}', output_paths, lambda: None, inputs=inputs)
        self._paths = output_paths

    def outputs_exist(self):
        return all(os.path.exists(p) for p in self._paths)


class TestPrerequisitesJudgedOnDiskNotInvocation:
    """Guards defect 2: the --only false block."""

    def test_prerequisite_satisfied_when_outputs_exist_even_if_upstream_not_in_this_run(self):
        with tempfile.TemporaryDirectory() as d:
            produced = os.path.join(d, 'demand.npy')
            open(produced, 'w').close()
            upstream = FakeStage('demand', [produced])
            downstream = FakeStage('capacity', [os.path.join(d, 'out.csv')], inputs=['demand'])
            # The full stage set, as run_all.py now passes -- NOT the --only filtered view.
            assert downstream.unmet_prerequisites({'demand': upstream, 'capacity': downstream}) == []

    def test_prerequisite_unmet_when_outputs_genuinely_absent(self):
        with tempfile.TemporaryDirectory() as d:
            upstream = FakeStage('demand', [os.path.join(d, 'never_created.npy')])
            downstream = FakeStage('capacity', [os.path.join(d, 'out.csv')], inputs=['demand'])
            assert downstream.unmet_prerequisites(
                {'demand': upstream, 'capacity': downstream}) == ['demand']

    def test_unknown_upstream_stage_is_reported_unmet_not_silently_satisfied(self):
        """Rule 5: a typo in an inputs= declaration must surface, not pass."""
        with tempfile.TemporaryDirectory() as d:
            downstream = FakeStage('capacity', [os.path.join(d, 'out.csv')], inputs=['typo_stage'])
            assert downstream.unmet_prerequisites({'capacity': downstream}) == ['typo_stage']


class TestDeclaredGraphIsConsistent:
    """Guards defect 1 indirectly: if `inputs` names a stage that does not exist, the check that
    reads it can never work."""

    def test_every_declared_input_names_a_real_stage(self):
        names = {s.name for s in STAGES}
        for stage in STAGES:
            for dep in stage.inputs:
                assert dep in names, f"stage '{stage.name}' declares unknown input '{dep}'"

    def test_no_stage_depends_on_itself(self):
        for stage in STAGES:
            assert stage.name not in stage.inputs

    def test_dependencies_point_backwards_only(self):
        """A stage's inputs must be produced by an EARLIER stage, or the pipeline cannot satisfy
        them in a single pass."""
        seen = set()
        for stage in STAGES:
            for dep in stage.inputs:
                assert dep in seen, (
                    f"stage '{stage.name}' depends on '{dep}', which is declared later")
            seen.add(stage.name)

    def test_no_two_stages_claim_the_same_output(self):
        claimed = {}
        for stage in STAGES:
            for out in stage.outputs:
                assert out not in claimed, (
                    f"'{out}' claimed by both '{claimed[out]}' and '{stage.name}'")
                claimed[out] = stage.name

    def test_every_stage_declares_at_least_one_output(self):
        """A stage with no outputs can never be skipped as already-built, so it would re-run
        forever and could never satisfy a downstream prerequisite."""
        for stage in STAGES:
            assert stage.outputs, f"stage '{stage.name}' declares no outputs"


class TestMergedSuitesHaveNoShadowedNames:
    """Guards a defect introduced by the 2026-09-10 county test merge.

    Both Arlington source files defined PROJECT_CSV_PATH. The parking definition appeared later in
    the merged file and silently overrode the rooftop one, so every rooftop test read the parking
    CSV and failed with KeyError: 'CM_Type'.

    The merge had checked for CLASS name collisions -- and found one, TestRealDataCrossCheck --
    but not module-level CONSTANT collisions. Python shadows silently, so nothing warned. This
    checks every merged suite for any top-level name assigned more than once.
    """

    MERGED_SUITES = ['test_arlington_siting.py', 'test_fairfax_siting.py',
                     'test_loudoun_siting.py', 'test_prince_william_siting.py']

    def _duplicate_top_level_assignments(self, path):
        import ast
        from collections import Counter
        tree = ast.parse(open(path).read())
        names = []
        for node in tree.body:
            if isinstance(node, ast.Assign):
                names += [t.id for t in node.targets if isinstance(t, ast.Name)]
            elif isinstance(node, (ast.ClassDef, ast.FunctionDef)):
                names.append(node.name)
        return [n for n, c in Counter(names).items() if c > 1]

    def test_no_top_level_name_is_defined_twice(self):
        import os
        here = os.path.dirname(os.path.abspath(__file__))
        for suite in self.MERGED_SUITES:
            path = os.path.join(here, suite)
            if not os.path.exists(path):
                continue
            dupes = self._duplicate_top_level_assignments(path)
            assert not dupes, (
                f"{suite} defines these top-level names more than once: {dupes}. "
                f"The later definition silently shadows the earlier one -- prefix them by section "
                f"(ROOFTOP_/PARKING_) rather than leaving which one wins to file order.")
