"""
lp_invariance.py

Fingerprints an assembled linear program, so a refactor can be proven to change nothing.

WHY THIS EXISTS

`build_problem` is 831 lines and 27 parameters, nine of them belonging to one scenario, with that
scenario's logic scattered across five locations rather than sitting in one block. It is being
restructured into a shared core plus one thin builder per scenario.

**1,370 tests depend on the assembled matrices not moving.** They check results -- costs, capacities,
clean shares -- which is the right thing to check but a slow and indirect way to detect that a
refactor perturbed the problem. A matrix that differs in one coefficient may still solve to a
similar objective, and the test suite would pass while the model quietly changed.

So: hash the problem itself, before and after, and require exact equality.

WHAT IS FINGERPRINTED, AND WHY EACH

    c            objective coefficients -- what the LP minimises
    bounds       per-variable limits, as a flat array so ordering changes are caught
    A_eq, b_eq   equality rows: energy balance, storage state of charge, rung sums
    A_ub, b_ub   inequality rows: reserve margin, gas caps, cumulative limits

**Sparse matrices are hashed on their COO triplets sorted canonically**, so an assembly that emits
the same coefficients in a different order fingerprints identically. That is deliberate: row order
within a block is an implementation detail, and a refactor that reorders without changing the
problem should pass. What must NOT change is the set of (row, column, value) triples and the
right-hand sides in row order.

**Shape is hashed separately and reported separately**, because a shape change is a different kind of
event from a coefficient change -- it means variables or constraints were added or lost, which is
usually intended during a refactor and always worth seeing explicitly.

WHAT THIS DOES NOT CATCH

A refactor that changes the problem and the expected fingerprint together. The fingerprints must be
captured from the CURRENT code before any change, stored, and compared against -- not regenerated
afterwards. `capture_baseline` writes them; `compare_to_baseline` reads them.
"""
import hashlib
import json
import os
from typing import Dict, Optional

import numpy as np
from scipy import sparse


def _hash_dense(values) -> str:
    array = np.asarray(values, dtype=float)
    # Round to 12 significant figures: float arithmetic can differ in the last bit across orderings
    # that are mathematically identical, and a fingerprint that fails on that is useless.
    return hashlib.sha256(np.round(array, 12).tobytes()).hexdigest()[:16]


def _hash_sparse(matrix) -> str:
    """Hash a sparse matrix on canonically sorted COO triplets.

    Order-independent by design: an assembly emitting the same coefficients in a different sequence
    is the same problem, and a refactor that reorders rows within a block should pass.
    """
    coo = sparse.coo_matrix(matrix)
    order = np.lexsort((coo.col, coo.row))
    triplets = np.column_stack([coo.row[order], coo.col[order],
                                np.round(coo.data[order], 12)])
    return hashlib.sha256(triplets.tobytes()).hexdigest()[:16]


def _flatten_bounds(bounds):
    """Bounds as a flat array, with None represented explicitly.

    None means unbounded and must not collapse to the same value as a large finite bound, so it maps
    to infinity rather than to a sentinel number that could collide with a real limit.
    """
    flat = []
    for low, high in bounds:
        flat.append(-np.inf if low is None else float(low))
        flat.append(np.inf if high is None else float(high))
    return np.array(flat, dtype=float)


def fingerprint(problem: Dict) -> Dict[str, object]:
    """Fingerprint one assembled problem. Shape reported separately from coefficients."""
    required = ('c', 'A_eq', 'b_eq', 'bounds')
    missing = [key for key in required if key not in problem]
    if missing:
        raise KeyError(
            f'problem is missing {missing}, so it cannot be fingerprinted. A partial fingerprint '
            'would compare equal on a problem that had lost a matrix, which is exactly the failure '
            'this is meant to detect.')
    a_ub = problem.get('A_ub')
    b_ub = problem.get('b_ub')
    return {
        'shape': {
            'variables': int(len(problem['c'])),
            'equality_rows': int(problem['A_eq'].shape[0]),
            'inequality_rows': int(a_ub.shape[0]) if a_ub is not None else 0,
            'bounds': int(len(problem['bounds'])),
        },
        'coefficients': {
            'c': _hash_dense(problem['c']),
            'bounds': _hash_dense(_flatten_bounds(problem['bounds'])),
            'A_eq': _hash_sparse(problem['A_eq']),
            'b_eq': _hash_dense(problem['b_eq']),
            'A_ub': _hash_sparse(a_ub) if a_ub is not None else 'absent',
            'b_ub': _hash_dense(b_ub) if b_ub is not None and len(b_ub) else 'absent',
        },
    }


def compare(before: Dict, after: Dict, label: str = 'problem'):
    """Differences between two fingerprints, as a list of readable strings. Empty means identical."""
    differences = []
    for key, was in before['shape'].items():
        now = after['shape'].get(key)
        if was != now:
            differences.append(f'{label}: {key} {was:,} -> {now:,}')
    for key, was in before['coefficients'].items():
        now = after['coefficients'].get(key)
        if was != now:
            differences.append(f'{label}: {key} coefficients CHANGED ({was} -> {now})')
    return differences


def capture_baseline(problems: Dict[str, Dict], path: str):
    """Write fingerprints for a set of named problems.

    MUST BE RUN BEFORE THE CHANGE, not after. A baseline regenerated from modified code proves
    nothing -- it compares the new behaviour against itself.
    """
    baseline = {name: fingerprint(problem) for name, problem in problems.items()}
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w') as handle:
        json.dump(baseline, handle, indent=2, sort_keys=True)
    return baseline


def compare_to_baseline(problems: Dict[str, Dict], path: str):
    """Compare a set of named problems against a stored baseline. Returns a list of differences."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f'no baseline at {path}. Capture one from UNMODIFIED code before refactoring -- a '
            'baseline written afterwards compares the new behaviour against itself.')
    with open(path) as handle:
        baseline = json.load(handle)
    differences = []
    for name, problem in problems.items():
        if name not in baseline:
            differences.append(f'{name}: no baseline entry')
            continue
        differences.extend(compare(baseline[name], fingerprint(problem), label=name))
    for name in baseline:
        if name not in problems:
            differences.append(f'{name}: in the baseline but not built now')
    return differences
