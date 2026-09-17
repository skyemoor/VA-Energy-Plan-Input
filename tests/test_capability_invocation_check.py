"""
test_capability_invocation_check.py

Audit check 18: an optional capability must be INVOKED, not merely imported.

THE FAILURE IT GUARDS AGAINST, twice now. `all_hours_reserve` was built, documented as standard, and
imported by nothing -- which is why check_module_is_actually_called exists. The merit-order stack
then failed the same way ONE LEVEL DEEPER: gas_merit_order was imported by three modules and passed
that check comfortably, while `Scenario2Solver.solve` never passed the kwargs, so every reported
figure burned 132 TWh at a flat 6.40 heat rate.

IMPORT IS NOT INVOCATION, and a capability that is never invoked is indistinguishable from one that
does not exist -- except that it passes every other check.
"""
import importlib
import inspect
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                'scripts'))
import audit_documented_fixes as audit  # noqa: E402


class TestTheRegistry:
    def test_it_covers_the_capabilities_added_this_session(self):
        capabilities = {c for c, _call, _target in audit.OPTIONAL_CAPABILITY_CALL_SITES}
        for expected in ('merit-order stack', 'thermal cycling cost', 'distributed carve-out',
                         'new-gas capacity bound', 'physical invariants'):
            assert expected in capabilities, f'{expected} not registered'

    def test_every_entry_names_a_real_target(self):
        for capability, _call, target in audit.OPTIONAL_CAPABILITY_CALL_SITES:
            module_name, _, attribute_path = target.partition('.')
            obj = importlib.import_module(module_name)
            for part in attribute_path.split('.'):
                obj = getattr(obj, part, None)
                assert obj is not None, f'{capability}: {target} does not resolve'


class TestTheCheckPasses:
    def test_all_capabilities_are_currently_invoked(self):
        passed, message = audit.check_optional_capabilities_are_invoked()
        assert passed, message


class TestItCatchesTheOriginalDefect:
    """The value of a check is what it catches, not that it passes."""

    def test_a_capability_that_is_imported_but_not_called_fails(self):
        """Simulates the merit-order defect: the module is imported, the helper exists, and the
        function that should call it does not."""
        original = audit.OPTIONAL_CAPABILITY_CALL_SITES
        try:
            audit.OPTIONAL_CAPABILITY_CALL_SITES = (
                ('fictitious', '_this_call_does_not_appear_anywhere(',
                 'checkpoint_solver.Scenario2Solver.solve'),)
            passed, message = audit.check_optional_capabilities_are_invoked()
            assert not passed
            assert 'never calls' in message
        finally:
            audit.OPTIONAL_CAPABILITY_CALL_SITES = original

    def test_an_unresolvable_target_fails_rather_than_passing_silently(self):
        """Rule 5: a registry entry pointing at a renamed function must not quietly succeed."""
        original = audit.OPTIONAL_CAPABILITY_CALL_SITES
        try:
            audit.OPTIONAL_CAPABILITY_CALL_SITES = (
                ('fictitious', 'anything(', 'checkpoint_solver.NoSuchClass.no_such_method'),)
            passed, message = audit.check_optional_capabilities_are_invoked()
            assert not passed
            assert 'cannot inspect' in message
        finally:
            audit.OPTIONAL_CAPABILITY_CALL_SITES = original


class TestWhyImportIsNotEnough:
    def test_the_merit_order_module_is_imported_by_several_modules(self):
        """Which is why check_module_is_actually_called passed while the capability was dead."""
        importers = [name for name, source in audit.source_files().items()
                     if source and 'import gas_merit_order' in source]
        assert len(importers) >= 2, importers

    def test_the_registry_records_the_reason(self):
        source = inspect.getsource(audit)
        assert 'IMPORT IS NOT INVOCATION' in source
        assert 'TWICE NOW' in source
