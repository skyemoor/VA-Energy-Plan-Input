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
    'levelised_cost.py':                             'SLCOE assembly; wired when the annual stream exists',
    'storage_resistor_threshold.py':                 'derivation + disclosure; checked by assumptions and the audit',
    'distributed_solar_profile.py':                  'statutory carve-out profile; built 2026-09-14, wired when the carve-out enters the solvers',
    'multi_period_problem.py':                       'perfect-foresight assembler; wired when the comparison runner exists',
    'rps_compliance.py':                             'optional statutory layer, sits alongside the physical formulation by design; not the sweep axis',
    'virginia_only_demand.py':                       'declared back-compatibility shim, superseded by demand_basis.VirginiaOnlyLoad',
    'demand_shape_interpolation.py':                 'SUPERSEDED 2026-09-13 -- the source projections already flatten; retained for its sourced IRP series',
    # --- shared base layers of the siting derivations above. Unreachable from an entry point
    # because their only callers are themselves derivations, which is correct: the transitive
    # walk added 2026-09-13 surfaces these, where the earlier any-importer check hid them.
    'rooftop_solar_estimation_base.py':              'base class for the county rooftop derivations',
    'nsrdb_data.py':                                 'NSRDB reader for the Loudoun profile derivation',
    'loudoun_battery_dispatch.py':                   'used by loudoun_solar_firming, itself a derivation',
    'loudoun_solar_hourly_profile.py':               'siting derivation; result filed in assumptions',
    'loudoun_ci_rooftop_solar_estimate.py':          'siting derivation; result filed in assumptions',
    'loudoun_parking_canopy_and_storage.py':         'siting derivation; result filed in assumptions',
    'loudoun_parking_lot_sqft.py':                   'siting derivation; result filed in assumptions',
    'loudoun_streak_finder.py':                      'one-off analysis, findings documented',
    'arlington_parking_lot_sqft.py':                 'siting derivation; result filed in assumptions',
    'fairfax_parking_lot_sqft.py':                   'siting derivation; result filed in assumptions',
    'fairfax_ci_rooftop_solar_estimate.py':          'siting derivation; result filed in assumptions',
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
    # TRANSITIVE REACHABILITY, added 2026-09-13. A module imported only by another ORPHANED module
    # is still doing no work -- the first version of this check counted any importer, so an
    # orphaned chain (A imports B, nothing imports A) reported B as reachable. Walk outward from
    # the genuine entry points instead: the top-level scripts, and anything listed as called by
    # design.
    entry_points = {f for f in os.listdir(REPO) if f.endswith('.py')}
    reachable, frontier = set(), set(entry_points)
    while frontier:
        nxt = set()
        for f in frontier:
            for m, imp in importers.items():
                if m in reachable:
                    continue
                if f in imp:
                    reachable.add(m)
                    nxt.add(m + '.py')
        frontier = nxt
    orphans = sorted(m for m in importers if m not in reachable)
    if orphans:
        return False, ('module(s) imported by nothing in the pipeline (tests do not count): '
                       + ', '.join(orphans)
                       + '. Either wire it in or record why it is uncalled in UNCALLED_BY_DESIGN.')
    return True, f'{len(modules)} modules, all imported by production code'



def check_no_export_revenue_in_objectives():
    """Appendix P.2 #8: "Export revenue must never appear inside any year-solve's own optimization
    objective, in any scenario." A standing, project-wide rule.

    WHY IT NEEDS A CHECK RATHER THAN A COMMENT: this exact bug has occurred twice. P.2 #8 records
    the first -- an earlier Scenario 2 calculation included it, "carried over from Scenario 1/3's
    code without reconsidering whether it belonged there", and the optimizer began running gas as a
    profit-seeking merchant generator. It was found on 2026-09-13 to have returned, live and
    unguarded in build_scenario2_problem while the equivalent in build_dispatch_problem sat behind
    an `if include_export:` flag.

    An unguarded assignment of a NEGATIVE cost to the export variable is the signature: negative
    cost in a minimisation is revenue.
    """
    import re
    src = read('lp_package', 'lp_model.py')
    if not src:
        return False, 'lp_model.py not readable'
    offenders = []
    for i, line in enumerate(src.split('\n'), 1):
        stripped = line.strip()
        if stripped.startswith('#'):
            continue
        if re.search(r"c\[hv\(t,\s*IDX\['e'\]\)\]\s*=\s*-", stripped):
            # Guarded assignments are permitted -- the caller decides. Look back a few lines for
            # the flag rather than assuming any nearby `if` is the right one.
            window = src.split('\n')[max(0, i - 4):i - 1]
            if not any('include_export' in w for w in window):
                offenders.append(i)
    if offenders:
        return False, (f'export revenue assigned in the objective, unguarded, at line(s) '
                       f'{offenders}. Appendix P.2 #8 forbids this in every scenario -- it gives '
                       'the optimizer an incentive to overbuild purely to capture export revenue. '
                       'Compute export POST-SOLVE from curtailment instead.')
    return True, 'no unguarded export revenue in any objective (Appendix P.2 #8)'



def check_curtailment_cost_is_present_and_agrees():
    """Internal Debugging Log #20 set curtailment cost at $100/MWh "permanently", defending it as
    "a defensible figure (same order of magnitude as gas cost and the export price), not another
    arbitrary tie-breaker".

    IT REGRESSED, and the failure mode is why this checks PRESENCE and not just agreement.
    build_problem() carried NO curtailment cost at all by 2026-09-13 -- its only one came from
    apply_slcr_constraint(curt_cost=5.0), twenty times too low -- while build_dispatch_problem()
    still set 100.0 behind a comment claiming it "matches build_problem()'s own corrected default".
    The comment described a value its counterpart no longer had. A check on agreement alone would
    have passed if both were absent.
    """
    import importlib
    import sys
    sys.path.insert(0, os.path.join(REPO, 'lp_package'))
    try:
        a = importlib.import_module('assumptions')
        d = importlib.import_module('driver')
        cs_mod = importlib.import_module('checkpoint_solver')
    except Exception as exc:                                              # noqa: BLE001
        return False, f'could not import to check: {type(exc).__name__}'

    import inspect
    problems = []
    if not hasattr(a, 'CURTAILMENT_COST_MWH'):
        problems.append('assumptions.CURTAILMENT_COST_MWH is absent')
    else:
        want = a.CURTAILMENT_COST_MWH
        solver_value = cs_mod.CheckpointSolver.curtailment_cost_mwh(
            cs_mod.CheckpointSolver.__new__(cs_mod.CheckpointSolver))
        if solver_value != want:
            problems.append(f'CheckpointSolver hook returns {solver_value}, not {want}')
        src = read('lp_package', 'lp_model.py') or ''
        if 'CURTAILMENT_COST_MWH' not in src:
            problems.append('lp_model.py does not reference the constant -- a hardcoded value has '
                            'returned')
        # driver's default is the fallback when no hook binds; it must not be the stale 5.0
        # None is correct: the function resolves it to the constant. A LITERAL default is the
        # failure -- that is how 5.0 persisted while build_dispatch_problem used 100.0.
        default = inspect.signature(d.apply_slcr_constraint).parameters['curt_cost'].default
        # The curtailment price must also stay below the storage-resistor threshold, or the LP
        # dumps surplus through round-trip losses instead of curtailing. Checked here so a raise is
        # caught WITHOUT running a solve -- it failed loudly once (4,710 hours, verify_result) but
        # only because a solve happened to be run.
        try:
            a.assert_curtailment_below_resistor_threshold()
        except AssertionError as exc:                                     # noqa: BLE001
            problems.append(str(exc)[:200])
        if default is not None:
            problems.append(f'driver.apply_slcr_constraint has a literal default of {default} '
                            'rather than None -- it must resolve to the constant, or a caller that '
                            'does not bind the hook silently gets a different value')
    if problems:
        return False, '; '.join(problems) + '. See Internal Debugging Log #20.'
    return True, f'curtailment cost ${a.CURTAILMENT_COST_MWH}/MWh, one source, hook and default agree'



def check_modules_import_what_they_reference():
    """Catches a name referenced in a module that the module never imports.

    FOUND 2026-09-14, and only by a live run. driver.apply_slcr_constraint referenced
    `assumptions.CURTAILMENT_COST_MWH` while driver.py had no `import assumptions` at all. Every
    solve through run_solve raised NameError.

    WHY THE TEST SUITE MISSED IT: 1,004 tests passed. The tests that touch apply_slcr_constraint
    check its SIGNATURE and its source text, not its execution, and the tests that run real solves
    are marked slow and deselected by default. A module-level import error would have been caught
    at import; a function-level one only fires when that line runs.
    """
    import ast
    pkg = os.path.join(REPO, 'lp_package')
    problems = []
    for fname in sorted(os.listdir(pkg)):
        if not fname.endswith('.py'):
            continue
        src = read('lp_package', fname)
        if not src:
            continue
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {(a.asname or a.name).split('.')[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom):
                imported |= {(a.asname or a.name) for a in node.names}
                if node.module:
                    imported.add(node.module.split('.')[0])
        # Every `X.something` where X names a sibling module must be imported -- UNLESS X is bound
        # locally as a parameter, assignment or comprehension target.
        #
        # THE SHADOWING CASE IS REAL, NOT HYPOTHETICAL: lp_model.build_problem takes a parameter
        # literally called `gas_merit_order`, which is also a module name. A check that ignored
        # local bindings reported three false positives on it immediately. A false positive in this
        # audit is expensive -- it runs hourly, and one that cries wolf trains the reader to skip it.
        siblings = {f[:-3] for f in os.listdir(pkg) if f.endswith('.py')} - {fname[:-3]}
        bound_locally = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                a = node.args
                bound_locally |= {x.arg for x in
                                  a.args + a.posonlyargs + a.kwonlyargs + ([a.vararg] if a.vararg
                                  else []) + ([a.kwarg] if a.kwarg else [])}
            elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
                bound_locally.add(node.id)
        for node in ast.walk(tree):
            if (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                    and node.value.id in siblings and node.value.id not in imported
                    and node.value.id not in bound_locally):
                problems.append(f'{fname} references {node.value.id}.{node.attr} without importing '
                                f'{node.value.id}')
    if problems:
        uniq = sorted(set(problems))
        return False, '; '.join(uniq[:4]) + ('' if len(uniq) <= 4 else f' (+{len(uniq)-4} more)')
    return True, 'every module imports the sibling modules it references'



#: Driver functions with no caller outside driver.py, each with a stated reason. A function that is
#: dormant BY DESIGN is fine; one that is dormant by accident is the build-document-never-wire
#: pattern at function granularity, which the module-level orphan check cannot see.
DORMANT_BY_DESIGN = {
    'add_reserve_margin_constraint': 'peak-hour reserve; reached only by PeakHourReserveMarginMixin, '
                                     'retained for A/B against the all-hours standard',
    'find_hour_of_maximum_net_demand': 'same -- peak-hour path only',
    'select_overhaul_retain': 'gas retain/overhaul selector; wired into Scenario 1B 2026-09-14',
}


def check_no_dormant_driver_functions():
    """Public driver functions with no external caller must be listed as dormant by design.

    THE MODULE-LEVEL ORPHAN CHECK CANNOT SEE THIS. driver.py is imported everywhere, so it is never
    orphaned -- but individual functions inside it can be, and four were found that way on
    2026-09-14: two correctly dormant (the peak-hour reserve path, superseded by all-hours), one
    drifted so far it could no longer chain across checkpoints, and one -- select_overhaul_retain --
    that was real, sourced machinery nobody had connected.
    """
    import ast
    import re
    src = read('lp_package', 'driver.py')
    if not src:
        return False, 'driver.py not readable'
    tree = ast.parse(src)
    public = [f.name for f in tree.body
              if isinstance(f, ast.FunctionDef) and not f.name.startswith('_')]
    others = ([os.path.join('lp_package', f) for f in os.listdir(os.path.join(REPO, 'lp_package'))
               if f.endswith('.py') and f != 'driver.py']
              + [f for f in os.listdir(REPO) if f.endswith('.py')])
    blob = ''
    for rel in others:
        blob += (read(rel) or '')
    undocumented = []
    for fn in public:
        if re.search(rf'\b(?:drv|driver)\.{fn}\b', blob):
            continue
        if fn not in DORMANT_BY_DESIGN:
            undocumented.append(fn)
    if undocumented:
        return False, ('driver function(s) with no external caller and no stated reason: '
                       + ', '.join(sorted(undocumented))
                       + '. Wire it in, or record why it is dormant in DORMANT_BY_DESIGN.')
    return True, f'{len(public)} public driver functions, dormant ones all accounted for'



def check_no_dead_functions_in_runners():
    """Functions in the top-level runners with no real call site.

    THE PATTERN THIS CATCHES occurred twice in two days: removing or replacing a caller without
    checking what it uniquely reached. Deleting run_solve_multi_duration orphaned
    build_problem_multi_duration and two helpers, 178 lines; replacing the myopic salvage path with
    build_salvage_credit orphaned _build_value.

    COUNTS CODE ONLY. Comments and docstrings mention function names constantly -- a naive text
    search reported four live callers for a function nothing called. tokenize separates them, which
    is the fifth time in this project a check needed that to be trustworthy.
    """
    import ast
    import io
    import re
    import tokenize
    dead = []
    for fname in sorted(f for f in os.listdir(REPO)
                        if f.startswith(('run_', 'solve_')) and f.endswith('.py')):
        src = read(fname)
        if not src:
            continue
        try:
            tree = ast.parse(src)
            toks = [t.string for t in tokenize.generate_tokens(io.StringIO(src).readline)
                    if t.type not in (tokenize.COMMENT, tokenize.STRING)]
        except (SyntaxError, tokenize.TokenError):
            continue
        blob = ' '.join(toks)
        for fn in tree.body:
            if not isinstance(fn, ast.FunctionDef) or fn.name == 'main':
                continue
            # COUNT REFERENCES, NOT CALL SYNTAX. run_all.py registers its stage functions as bare
            # names inside Stage objects -- `stage_demand_arrays,` with no parentheses -- so a
            # check looking for `name(` reported all six as dead on its first run. A function
            # passed as a value is used.
            refs = len(re.findall(r'(?<![\w.])' + fn.name + r'(?![\w])', blob)) - 1
            if refs <= 0:
                dead.append(fname + ':' + fn.name)
    if dead:
        return False, 'function(s) with no call site: ' + ', '.join(dead) + '. Delete, or wire in.'
    return True, 'no dead functions in the top-level runners'



def check_one_demand_source():
    """Demand must come from demand_basis, not the cached intermediate.

    THE TWO ARE BYTE-IDENTICAL where both exist -- the intermediate is produced by run_all from
    exactly the demand_basis call -- but the CACHE ONLY EXISTS FOR CHECKPOINT YEARS while the
    source works for any year in 2026-2045. A runner reading the cache is silently checkpoint-only,
    which is a real limitation for the SLCOE work that needs all twenty years, and it puts a second
    demand path in the repository for no gain.

    Found 2026-09-14: run_foresight_comparison read the cache while three other runners read the
    source.
    """
    import re
    offenders = []
    for fname in sorted(f for f in os.listdir(REPO)
                        if f.startswith(('run_', 'solve_')) and f.endswith('.py')):
        src = read(fname)
        if not src or fname == 'run_all.py':
            # run_all PRODUCES the cache -- it is the only thing that should name that path.
            continue
        for i, line in enumerate(src.split('\n'), 1):
            if line.strip().startswith('#'):
                continue
            if re.search(r"intermediate\(\s*f?['\"]demand_", line):
                offenders.append(fname + ':' + str(i))
    if offenders:
        return False, ('demand read from the cached intermediate at ' + ', '.join(offenders)
                       + '. Use demand_basis.VirginiaOnlyLoad(year), which works for any year.')
    return True, 'demand read from demand_basis everywhere in the runners'



def check_scenarios_state_their_own_gas_split():
    """Every Scenario*Solver must declare get_existing_new_mw in its OWN namespace.

    SocialCostRGGIMixin refuses to supply a default, on the stated grounds that "a wrong-but-silent
    default (e.g. reusing another scenario's own split) is worse than an explicit failure here".

    THAT GUARD CANNOT FIRE THROUGH INHERITANCE. Scenario3Solver inherits from Scenario1Solver, so
    it picked up Scenario 1's implementation through the MRO and the raise was never reached -- the
    decision the guard exists to force was being made by the class hierarchy instead of by anyone.
    Found 2026-09-14; the split turned out to be genuinely identical, but nobody had checked.

    A formal ABC would NOT catch this: abstractmethod is satisfied by an inherited implementation.
    The check has to look at the class's own __dict__.

    VARIANT CLASSES ARE EXEMPT -- Scenario1WithReserveMargin IS Scenario 1, and forcing a
    meaningless override on every marker class would train people to write `return super()`
    without thinking, which is worse than the problem.
    """
    import importlib
    import sys
    sys.path.insert(0, os.path.join(REPO, 'lp_package'))
    try:
        cs = importlib.import_module('checkpoint_solver')
    except Exception as exc:                                              # noqa: BLE001
        return False, 'could not import checkpoint_solver: ' + type(exc).__name__
    missing = []
    for name in dir(cs):
        if not (name.startswith('Scenario') and name.endswith('Solver')):
            continue
        klass = getattr(cs, name)
        if not isinstance(klass, type):
            continue
        if 'get_existing_new_mw' not in vars(klass):
            missing.append(name)
    if missing:
        return False, ('scenario solver(s) not stating their own gas existing/new split: '
                       + ', '.join(sorted(missing))
                       + '. Declare get_existing_new_mw, delegating to super() if the split is '
                       'genuinely identical -- but say so.')
    return True, 'every scenario solver states its own gas existing/new split'



def check_section_symbol_only_in_va_code_citations():
    """The section symbol is reserved for Virginia Code citations.

    PROJECT CONVENTION set 2026-09-14: using it for our own numbered items is distracting, and its
    meaning should be unambiguous -- seeing it should tell a reader "this is statute". Numbered
    items use #.

    404 uses were replaced across 61 files. THE FIRST PASS WALKED FOUR DIRECTORIES AND MISSED THE
    TOP LEVEL, leaving 8 in the runners -- caught by a test, not by the sweep. The runners are where
    a reader meets the convention first, so this check covers them.
    """
    import re
    va_code = re.compile('\u00a7\\s*(?:56-|45\\.2-|10\\.1-|58\\.1-|2\\.2-|67-)')
    offenders = []
    roots = [REPO] + [os.path.join(REPO, d) for d in ('docs', 'lp_package', 'tests', 'scripts')]
    for base in roots:
        if not os.path.isdir(base):
            continue
        walk = [(base, [], os.listdir(base))] if base == REPO else os.walk(base)
        for dirpath, _dirs, files in walk:
            if '__pycache__' in dirpath:
                continue
            for fn in files:
                if not fn.endswith(('.md', '.py')):
                    continue
                path = os.path.join(dirpath, fn)
                if not os.path.isfile(path):
                    continue
                with open(path, encoding='utf-8', errors='replace') as fh:
                    src = fh.read()
                for m in re.finditer('\u00a7', src):
                    if not va_code.match(src[m.start():m.start() + 12]):
                        offenders.append(os.path.relpath(path, REPO) + ':'
                                         + str(src[:m.start()].count('\n') + 1))
    if offenders:
        uniq = sorted(set(offenders))
        return False, ('section symbol used outside a Virginia Code citation at '
                       + ', '.join(uniq[:5])
                       + ('' if len(uniq) <= 5 else ' (+%d more)' % (len(uniq) - 5))
                       + '. Use # for numbered items.')
    return True, 'section symbol appears only in Virginia Code citations'


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
    ('modules import what they reference', check_modules_import_what_they_reference),
    ('no undocumented dormant driver functions', check_no_dormant_driver_functions),
    ('no dead functions in the runners', check_no_dead_functions_in_runners),
    ('one demand source in the runners', check_one_demand_source),
    ('section symbol only in VA Code citations', check_section_symbol_only_in_va_code_citations),
    ('scenarios state their own gas split', check_scenarios_state_their_own_gas_split),
    ('no export revenue in objectives (Appendix P.2 #8)', check_no_export_revenue_in_objectives),
    ('curtailment cost present and agreeing (log #20)', check_curtailment_cost_is_present_and_agrees),

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
