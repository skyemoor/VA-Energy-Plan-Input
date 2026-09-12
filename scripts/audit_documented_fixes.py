#!/usr/bin/env python3
"""
audit_documented_fixes.py

Checks that things the documentation says are fixed, wired in, or standard are actually true of the
code right now.

WHY THIS EXISTS
Two regressions were found on 2026-09-11, both by reading code rather than documentation:

  1. all_hours_reserve.py implements the LP-integrated all-hours reserve constraint that
     Weather_Year_Robustness_Approaches_and_Findings_2026-08-23.md names as "current standard".
     Nothing calls it.
  2. That same document records a t_peak -> t_peak_net_load rename done 2026-08-23, made because
     "the ambiguous name directly caused a real analysis error mid-session". The rename did not
     survive, and the same class of error recurred: four documents were written stating the reserve
     constraint used gross demand, when the hour selection has always been net-load based.

Documentation recording that something was fixed is not evidence that it is still fixed. This
script turns that from a caution into a check.

CADENCE (set 2026-09-12): run hourly during an active session, and again whenever a session resumes
after more than an hour idle. Cheap enough that there is no reason to skip it -- it reads files and
greps; it does not solve.

EXIT CODES
  0  all checks pass
  1  one or more regressions detected
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*parts):
    p = os.path.join(REPO, *parts)
    if not os.path.exists(p):
        return None
    with open(p, encoding='utf-8', errors='replace') as f:
        return f.read()


def source_files(subdirs=('lp_package', 'scripts'), exclude=()):
    out = {}
    for sub in subdirs:
        d = os.path.join(REPO, sub)
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.endswith('.py') and f not in exclude:
                out[f] = read(sub, f)
    return out


# --------------------------------------------------------------------------
# Checks. Each returns (passed, message).
# --------------------------------------------------------------------------

def check_module_is_actually_called(module_name, doc_claim):
    """A module that exists and is documented as standard, but is imported by nothing, is the
    exact failure this script was written for."""
    callers = [f for f, s in source_files(exclude=(f'{module_name}.py',)).items()
               if s and re.search(rf'\b(import\s+{module_name}\b|from\s+{module_name}\s+import)', s)]
    if callers:
        return True, f'{module_name} imported by: {", ".join(sorted(callers))}'
    return False, (f'{module_name}.py exists but NOTHING IMPORTS IT. {doc_claim} '
                   f'This is the all_hours_reserve failure pattern.')


def check_name_absent(bad_name, replacement, why):
    """A name renamed for a stated reason should not reappear."""
    hits = []
    # This script names the banned identifier in order to check for it; exclude itself.
    for f, s in source_files(exclude=('audit_documented_fixes.py',)).items():
        if s and re.search(rf'\b{re.escape(bad_name)}\b', s):
            # docstrings explaining the rename are legitimate
            if re.search(rf'RENAMED.{{0,400}}\b{re.escape(bad_name)}\b', s, re.S):
                continue
            hits.append(f)
    if not hits:
        return True, f'{bad_name} absent (renamed to {replacement})'
    return False, f'{bad_name} has REAPPEARED in {", ".join(hits)}. {why}'


def check_constant_superseded(module, gone, present):
    """A constant replaced by a corrected one should be removed, not left alongside it."""
    s = read('lp_package', f'{module}.py')
    if s is None:
        return True, f'{module}.py not present, skipped'
    has_gone = re.search(rf'^{re.escape(gone)}\s*=', s, re.M)
    has_present = re.search(rf'^{re.escape(present)}\s*=', s, re.M)
    if has_gone:
        return False, f'{gone} still defined in {module}.py; it was superseded by {present}'
    if not has_present:
        return False, f'{present} MISSING from {module}.py'
    return True, f'{gone} removed, {present} present'


def check_claim_matches_code(doc_path, claim_substring, code_check, description):
    """Guards against a document asserting something the code does not do."""
    doc = read(*doc_path.split('/'))
    if doc is None or claim_substring not in doc:
        return True, f'{description}: claim not present in {doc_path}, nothing to check'
    ok, detail = code_check()
    if ok:
        return True, f'{description}: document and code agree'
    return False, f'{doc_path} claims "{claim_substring[:50]}..." but {detail}'


CHECKS = [
    ('all_hours_reserve is wired in',
     lambda: check_module_is_actually_called(
         'all_hours_reserve',
         'Weather_Year_Robustness_...2026-08-23.md names the all-hours constraint as "current standard".')),

    ('t_peak stays renamed',
     lambda: check_name_absent(
         't_peak', 'hour_of_maximum_net_demand',
         'It was renamed 2026-08-23 and again 2026-09-11; the first rename did not survive and the '
         'same class of analysis error recurred.')),

    ('CT split constant reflects the resolved finding',
     lambda: check_constant_superseded(
         'assumptions', 'GAS_CT_SPLIT_UNRESOLVED', 'GAS_CT_SPLIT_RESOLVED')),

    ('capacity basis constant reflects the resolved finding',
     lambda: check_constant_superseded(
         'assumptions', 'GAS_CAPACITY_BASIS_UNRECONCILED', 'GAS_DOMINION_OWNED_NAMEPLATE_MW')),

    ('derived hay constant stays deleted',
     lambda: check_constant_superseded(
         'agrivoltaic_basis', 'VA_HAY_ACRES_APPROX', 'VA_TOP_CROPS_ACRES')),
]


def main():
    print('Documented-fix audit')
    print('=' * 72)
    failures = []
    for name, fn in CHECKS:
        try:
            ok, msg = fn()
        except Exception as exc:                                  # noqa: BLE001
            ok, msg = False, f'check raised {type(exc).__name__}: {exc}'
        print(f'  [{"PASS" if ok else "FAIL"}] {name}')
        print(f'         {msg}')
        if not ok:
            failures.append(name)
    print('=' * 72)
    if failures:
        print(f'{len(failures)} REGRESSION(S): {", ".join(failures)}')
        print('A documented fix is no longer true of the code. Fix the code or correct the document.')
        return 1
    print(f'All {len(CHECKS)} checks pass.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
