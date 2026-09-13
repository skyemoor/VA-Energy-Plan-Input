"""
test_audit_identifier_check.py

The audit's identifier check must distinguish a name IN USE from prose ABOUT that name.

Two earlier implementations failed this, both producing false positives: a 400-character window
around the word RENAMED missed a comment citing the rename as precedent, and a grammar heuristic
then missed a continuation line of a docstring. The audit runs hourly and its value depends
entirely on a failure meaning something, so a false positive is expensive -- it trains the reader
to skip it.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))

from audit_documented_fixes import _identifier_used_in_code as used


class TestProseIsNotUsage:

    def test_hash_comment_is_not_usage(self):
        assert used('# the t_peak decision aged badly\nx = 1\n', 't_peak') is False

    def test_docstring_is_not_usage(self):
        src = '"""RENAMED from t_peak because the name was ambiguous."""\nx = 1\n'
        assert used(src, 't_peak') is False

    def test_docstring_continuation_line_is_not_usage(self):
        """The case the grammar heuristic missed -- a second line of a docstring carrying no
        keyword that marked it as prose."""
        src = ('def f():\n'
               '    """RENAMED 2026-09-11.\n'
               '    function boundary gets a real name -- t_peak crossed four.\n'
               '    """\n'
               '    return 1\n')
        assert used(src, 't_peak') is False

    def test_string_literal_is_not_usage(self):
        assert used('msg = "t_peak was renamed"\n', 't_peak') is False


class TestCodeIsUsage:

    def test_assignment_is_usage(self):
        assert used('t_peak = 5\n', 't_peak') is True

    def test_subscript_is_usage(self):
        assert used('x = demand[t_peak]\n', 't_peak') is True

    def test_keyword_argument_is_usage(self):
        assert used('f(t_peak=3)\n', 't_peak') is True

    def test_substring_does_not_count(self):
        """test_peaker_capex contains 't_peak'. A naive substring search corrupted five test names
        during the original rename."""
        assert used('def test_peaker_capex():\n    pass\n', 't_peak') is False


class TestUnparseableFilesAreReported:
    def test_syntax_error_returns_true_rather_than_clearing(self):
        """A file that cannot be parsed cannot be cleared. Reporting it is the safe direction --
        silently passing an unparseable file would hide exactly what the audit exists to catch."""
        assert used('def broken(\n', 't_peak') is True
