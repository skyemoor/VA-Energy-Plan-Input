"""
conftest.py

Puts lp_package/ on sys.path for every test in this directory.

Replaces the per-file `sys.path.insert(...)` preamble that several test modules carried. That
pattern worked only for files that remembered it -- test_provenance.py did not, because it was
written while provenance.py sat in the same working directory and only failed once moved into
the repository layout. A single conftest.py is the correct scope for this.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lp_package'))
