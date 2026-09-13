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
import io
import os
import re
import sys
import token
import tokenize

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


def _identifier_used_in_code(source, name):
    """True if `name` appears as an identifier in executable code, ignoring comments and strings.

    Uses tokenize rather than regex because the alternative is matching English, which was tried
    twice and failed twice. A NAME token is an identifier; a COMMENT or STRING token is prose.
    """
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        return any(t.type == token.NAME and t.string == name for t in tokens)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        # An unparseable file cannot be cleared, so report it rather than passing it silently.
        return True



def check_no_conflicting_duplicate_constants():
    """Rule 6: a constant defined in two modules must hold the SAME value.

    Rule 6.2 permits legitimate re-derivation with a cross-check assertion; Rule 6.3 requires
    checking assumptions.py before adding a new name. This catches the case both rules exist to
    prevent: two live constants, one name, different values -- where whichever module a caller
    imported from decides which they get.

    FOUND ONCE, 2026-09-13: CCGT_CAPEX_KW existed in lp_model.py as a superseded SCALAR
    ($1,775/kW, a stale Lazard midpoint kept under a _DO_NOT_USE_SUPERSEDED name but re-aliased to
    the plain name one line later) and in gas_lifecycle_cost.py as a low/central/high DICT
    ($2,000/$2,500/$3,200). Neither was in assumptions.py.
    """
    import ast
    import collections
    pkg = os.path.join(REPO, 'lp_package')
    defs = collections.defaultdict(dict)
    for fname in sorted(os.listdir(pkg)):
        if not fname.endswith('.py'):
            continue
        try:
            tree = ast.parse(read('lp_package', fname))
        except SyntaxError:
            continue
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id.isupper() and not t.id.startswith('_'):
                    try:
                        defs[t.id][fname] = ast.literal_eval(node.value)
                    except (ValueError, TypeError, SyntaxError):
                        pass          # computed values cannot be compared statically
    conflicts = []
    for name, by_file in defs.items():
        vals = list(by_file.values())
        if len(by_file) > 1 and any(v != vals[0] for v in vals[1:]):
            conflicts.append(f'{name} differs across {sorted(by_file)}')
    if conflicts:
        return False, ('conflicting duplicate constants: ' + '; '.join(conflicts)
                       + '. Rule 6: move to assumptions.py, or cross-check with an assertion.')
    return True, f'{len(defs)} module-level constants, no conflicting duplicates'



#: Modules that legitimately have no production caller. Each needs a stated reason -- the point of
#: the check is that "nothing imports this" should be a deliberate choice, not an accident.
#: Import-detection pattern, defined as a plain template rather than an inline rf-string. Written
#: inline, the \b word boundary was repeatedly mangled into a literal backspace by the tooling that
#: edits this file, so the regex silently matched NOTHING and every module looked orphaned.
RE_IMPORTS = r'(?:^|\W)(?:import\s+{m}\b|from\s+{m}\s+import)'

UNCALLED_BY_DESIGN = {
    'assumptions.py':      'the parameter surface; imported by nearly everything',
    'paths.py':            'path resolution; imported by nearly everything',
    'provenance.py':       'provenance helper',
    '__init__.py':          'package marker',
    # --- county-level siting estimates: standalone analyses whose OUTPUT (a MW or sqft figure)
    # was transcribed into assumptions.py. The module is the derivation record, not a runtime
    # dependency. Re-run by hand when a source dataset changes.
    'arlington_ci_rooftop_solar_estimate.py':        'siting derivation; result filed in assumptions',
    'chesapeake_ci_rooftop_solar_estimate.py':       'siting derivation; result filed in assumptions',
    'prince_william_ci_rooftop_solar_estimate.py':   'siting derivation; result filed in assumptions',
    'prince_william_parking_lot_density_estimate.py': 'siting derivation; result filed in assumptions',
    'parking_ratio_basis.py':                        'siting derivation; result filed in assumptions',
    'population_extrapolation.py':                   'siting derivation; result filed in assumptions',
    'loudoun_load_shape_gap_analysis.py':            'one-off analysis, findings documented',
    'loudoun_solar_firming.py':                      'one-off analysis, findings documented',
    'agrivoltaic_basis.py':                          'land-use derivation; constants filed in assumptions',
    'peaker_capex.py':                               'capex derivation; PEAKER_CAPEX_KW_BY_TIER filed in assumptions',
    'der_revenue_stack.py':                          'reporting helper for the whitepaper, not the LP',
    'gas_outage_stress.py':                          'stress analysis, findings documented',
    'foresight_bracket.py':                          'bracketing analysis for issue #5',
    'charging_adequacy.py':                          'storage adequacy check, run on demand',
    'storage_accreditation.py':                      'accreditation analysis, run on demand',
    'large_ci_curtailment_feature.py':               'demand-side feature, not in the base scenarios',
    'supply_gap_analysis.py':                        'gap characterisation, run on solved results',
    'scenario2_all_hours_reserve.py':                'opt-in reserve test; measured 0.00% cost, never binds',
}


def check_no_orphaned_modules():
    """Rule 1: a module built and documented as the standard, then never wired in, is a defect.

    THE PATTERN THIS CATCHES has recurred five times in this project:
      - all_hours_reserve.py           documented as "current standard", never imported
      - the t_peak rename              done, then reverted
      - distributed iron-air exclusion documented in a comment, never implemented as a bound
      - CCGT_CAPEX_KW                  renamed to _DO_NOT_USE_SUPERSEDED, then re-aliased back
      - demand_shape_interpolation.py  built for "intermediate-year dispatch-only re-solves",
                                       referenced only by a test

    Each was found by hand, months apart. A module imported ONLY by tests is doing no work in the
    pipeline, whatever its docstring claims.
    """
    import re
    pkg = os.path.join(REPO, 'lp_package')
    modules = {f[:-3] for f in os.listdir(pkg)
               if f.endswith('.py') and f not in UNCALLED_BY_DESIGN}
    importers = {m: set() for m in modules}
    for root in ('lp_package', '.'):
        d = os.path.join(REPO, root)
        for fname in os.listdir(d):
            if not fname.endswith('.py'):
                continue
            src = read(root, fname) if root != '.' else read(fname)
            if not src:
                continue
            for m in modules:
                if fname == m + '.py':
                    continue
                if re.search(RE_IMPORTS.format(m=re.escape(m)), src):
                    importers[m].add(fname)
    orphans = sorted(m for m, imp in importers.items() if not imp)
    if orphans:
        return False, ('module(s) imported by nothing in the pipeline (tests do not count): '
                       + ', '.join(orphans)
                       + '. Either wire it in or record why it is uncalled in UNCALLED_BY_DESIGN.')
    return True, f'{len(modules)} modules, all imported by production code'


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
        if not s:
            continue
        # Only CODE occurrences count. Prose about the rename is legitimate and expected -- the
        # whole point of documenting a regression is to name what regressed.
        #
        # STRIPS COMMENTS AND STRINGS WITH tokenize RATHER THAN MATCHING PROSE. Two earlier
        # attempts failed: a 400-character window around the word RENAMED missed a later comment in
        # lp_model.py citing the t_peak decision as precedent, and a grammar heuristic then missed a
        # continuation line of driver.py's own docstring. Both produced false positives, and a
        # false positive in a regression audit is expensive -- the audit runs hourly, and its value
        # depends on a failure meaning something. One that cries wolf trains the reader to skip it.
        if _identifier_used_in_code(s, bad_name):
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
    ('no conflicting duplicate constants (Rule 6)', check_no_conflicting_duplicate_constants),
    ('no orphaned modules (Rule 1)', check_no_orphaned_modules),

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
