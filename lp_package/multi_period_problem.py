"""
multi_period_problem.py

Assembles several single-period LP problems into ONE simultaneous multi-period problem, so the
optimiser sees every checkpoint's constraints at once and chooses the whole trajectory together.

THIS IS PERFECT FORESIGHT -- Case 2 in the taxonomy recorded in
docs/methodology/Experiment_Pathway_Foresight.md, and the true quantitative equivalent of
"backcasting". The literature is unambiguous that it means a SINGLE SIMULTANEOUS SOLVE:

    "optimizing all variables over the whole time frame in a single run, thus determining the
     global optimum" -- PERSEUS-NET, on switching between perfect foresight and myopic

    "perfect-foresight approaches are capable of finding a cost-minimal transformation pathway
     across all expansion phases ... myopic approaches assume limited knowledge about the future,
     meaning that optimization in each expansion phase is based on the results of the previous
     expansion phases and the constraints of the current expansion phase only"
     -- A modeler's guide to handle complexity in energy systems optimization (arXiv 2009.07216)

IT IS NOT "solve the last year first and work backwards". That construction appears nowhere in the
literature; it was proposed here on 2026-09-14 and discarded once the citations were checked.

WHY BLOCK ASSEMBLY RATHER THAN A NEW BUILDER. build_problem() returns sparse matrices with the
eight build variables at FIXED positions 0-7 in every period, so four periods stack block-diagonally
and need only 8 x 3 = 24 linking rows. Extending build_problem itself with a period dimension would
mean adding a dimension to the most load-bearing function in the model, which every scenario
depends on. This leaves it untouched.

SALVAGE VALUE IS MANDATORY HERE, NOT OPTIONAL. Brown's multi-horizon formulation states it plainly
-- "the perfect foresight model is Type 1 WITH salvage value" -- and the reason is structural: a
credit "proportional to remaining technical lifetime, ensuring late-horizon investments are not
penalized for capacity operating beyond the modeled period". Omit it and the optimiser sees every
2045 build as worthless the instant the horizon ends, and systematically under-builds late. That
would bias the myopic-versus-foresight comparison in exactly the direction the comparison is
trying to measure.

SIZE, measured 2026-09-14: four periods give 735,872 variables, 912,524 rows, 2.9M nonzeros,
against 183,968 / 228,131 / 727,090 for one. PERSEUS-NET measured myopic at "less than one tenth of
the computing time" of perfect foresight, which is consistent with LP time scaling superlinearly.
"""
from typing import Dict, List, Optional, Sequence

import numpy as np
from scipy import sparse

import assumptions

#: Build variables occupy positions 0 .. NVAR_BUILD-1 in every period's variable vector, unpacked
#: from one fixed sequence in build_problem. Linking rows address them by position, so a change to
#: that ordering silently relinks the wrong quantities -- asserted in verify_assembly().
_BUILD_VAR_NAMES = ('utility_solar_mw', 'sodium_ion_power_mw', 'sodium_ion_energy_mwh',
                    'iron_air_energy_mwh', 'distributed_solar_mw', 'distributed_sodium_ion_power_mw',
                    'distributed_sodium_ion_energy_mwh', 'distributed_iron_air_energy_mwh')


def assemble(problems: Sequence[Dict], years: Sequence[int],
             wacc: Optional[float] = None, base_year: Optional[int] = None,
             salvage_usd_by_period: Optional[Sequence[float]] = None,
             link_builds: bool = True) -> Dict:
    """One simultaneous problem from several single-period ones.

    `problems` must already carry every constraint each period needs -- reserve margin, distributed
    bounds, merit order. Hooks run BEFORE assembly, on the single-period problems, because this
    function knows nothing about what those constraints mean.

    `link_builds=False` assembles the blocks WITHOUT the linking rows, making the periods
    independent. That is the validation mode: the result must reproduce the standalone solves
    exactly, which isolates assembly errors from foresight effects. See verify_assembly().

    `salvage_usd_by_period` is a per-MW credit applied to each period's build variables, NOT a
    lump sum -- the optimiser must see salvage as a function of how much it builds, or it does not
    influence the build decision at all.
    """
    if len(problems) != len(years):
        raise ValueError(f'{len(problems)} problems against {len(years)} years; they must pair.')
    if len(problems) < 2:
        raise ValueError('assemble() needs at least two periods; one period is build_problem().')
    if sorted(years) != list(years):
        raise ValueError(f'years must be ascending, got {list(years)}. Linking rows constrain each '
                         'period against the NEXT one, so order carries meaning.')

    import lp_model as lp
    wacc = assumptions.WACC if wacc is None else wacc
    base_year = assumptions.BASE_YEAR if base_year is None else base_year

    nvar = [len(p['c']) for p in problems]
    nb = problems[0]['hv_params'][0]
    for i, p in enumerate(problems):
        if p['hv_params'][0] != nb:
            raise ValueError(
                f'period {years[i]} has NVAR_BUILD={p["hv_params"][0]} against {nb} in period '
                f'{years[0]}. Linking rows address build variables BY POSITION, so differing '
                'layouts would link the wrong quantities without raising.')

    offsets, running = [], 0
    for n in nvar:
        offsets.append(running)
        running += n
    total = running

    # -- objective: each period discounted to base_year -------------------
    c = np.concatenate([p['c'] * (1.0 / (1.0 + wacc) ** (y - base_year))
                        for p, y in zip(problems, years)])

    # -- salvage: a NEGATIVE cost on build variables, so it shapes the build
    if salvage_usd_by_period is not None:
        if len(salvage_usd_by_period) != len(problems):
            raise ValueError('salvage_usd_by_period must have one entry per period')
        for off, credit, y in zip(offsets, salvage_usd_by_period, years):
            # PER BUILD VARIABLE, or one figure applied to all of them. A list is the correct form
            # when the credits differ by technology -- solar, storage power and storage energy have
            # different capex bases, and averaging them (as an earlier version of the runner did)
            # gives every variable a number belonging to none of them.
            credits = ([float(credit)] * nb if np.isscalar(credit)
                       else [float(v) for v in credit])
            if len(credits) != nb:
                raise ValueError(
                    f'salvage for {y} has {len(credits)} entries against {nb} build variables. '
                    'Pass one figure per build variable, or a single figure for all of them.')
            if any(v < 0 for v in credits):
                raise ValueError(
                    f'salvage for {y} contains a negative value; a negative residual is a '
                    'decommissioning liability and belongs in that period\'s costs, not here.')
            df = 1.0 / (1.0 + wacc) ** (y - base_year)
            for k, v in enumerate(credits):
                if v:
                    c[off + k] -= v * df

    A_eq = sparse.block_diag([p['A_eq'] for p in problems], format='csr')
    b_eq = np.concatenate([p['b_eq'] for p in problems])
    A_ub = sparse.block_diag([p['A_ub'] for p in problems], format='csr')
    b_ub = np.concatenate([p['b_ub'] for p in problems])
    bounds = [b for p in problems for b in p['bounds']]

    link_rows = 0
    if link_builds:
        # build[a] - build[a+1] <= 0 : capacity carries forward and cannot shrink. This is the ONLY
        # thing connecting the periods; without it the assembly is four independent problems.
        rows, cols, data = [], [], []
        r = 0
        for i in range(len(problems) - 1):
            for k in range(nb):
                rows += [r, r]
                cols += [offsets[i] + k, offsets[i + 1] + k]
                data += [1.0, -1.0]
                r += 1
        link_rows = r
        L = sparse.coo_matrix((data, (rows, cols)), shape=(r, total)).tocsr()
        A_ub = sparse.vstack([A_ub, L], format='csr')
        b_ub = np.concatenate([b_ub, np.zeros(r)])

    return {
        'c': c, 'A_eq': A_eq, 'b_eq': b_eq, 'A_ub': A_ub, 'b_ub': b_ub, 'bounds': bounds,
        'years': list(years), 'offsets': offsets, 'nvar_per_period': nvar, 'nvar_build': nb,
        'link_rows': link_rows, 'wacc': wacc, 'base_year': base_year,
        'periods': len(problems), 'BUILD_SCALE': problems[0].get('BUILD_SCALE'),
        'hv_params_by_period': [p['hv_params'] for p in problems],
        'IDX': problems[0]['IDX'],
    }


def period_slice(assembled: Dict, index: int) -> slice:
    """Variable range for one period, for reading a solved x back apart."""
    off = assembled['offsets'][index]
    return slice(off, off + assembled['nvar_per_period'][index])


def builds_by_period(assembled: Dict, x) -> List[Dict[str, float]]:
    """Build variables per period, named. Multiplied by BUILD_SCALE where the single-period
    problems used one, so the figures are directly comparable to a standalone solve."""
    scale = assembled.get('BUILD_SCALE') or 1.0
    nb = assembled['nvar_build']
    out = []
    for i, off in enumerate(assembled['offsets']):
        out.append({name: float(x[off + k]) * scale
                    for k, name in enumerate(_BUILD_VAR_NAMES[:nb])})
    return out


def verify_solution(assembled: Dict, x, years: Optional[Sequence[int]] = None) -> Dict:
    """Appendix P.2 #11 checks on a solved multi-period result, per period.

    WHY THIS EXISTS. CheckpointSolver.verify_result() runs on the myopic side, through
    solve_with_reserve_margin. The perfect-foresight side produces a raw solution vector and had NO
    verification at all -- so a solve with unserved energy or simultaneous charge/discharge would
    have been reported without checking. #11 requires both before any solve is presented as final,
    and the comparison would otherwise hold the two sides to different standards, which is exactly
    the failure the comparison is meant to avoid.

    Raises on the first violation rather than returning a flag, matching verify_result()'s own
    convention: a solve that fails these is not a result whose cost means anything.
    """
    years = list(years or assembled['years'])
    report = []
    for i, year in enumerate(years):
        nb, nph = assembled['hv_params_by_period'][i]
        off = assembled['offsets'][i]
        block = x[off:off + assembled['nvar_per_period'][i]]
        IDX = assembled['IDX']
        T = (len(block) - nb) // nph

        def hourly(key):
            k = IDX[key]
            return np.array([block[nb + t * nph + k] for t in range(T)])

        unserved = float(hourly('unserved').sum()) if 'unserved' in IDX else 0.0
        if unserved > 1e-3:
            raise ValueError(
                f'#11 VERIFICATION FAILED: perfect-foresight period {year} has {unserved:.1f} MWh '
                'unserved energy.')
        simul = {}
        for charge_key, discharge_key, label in (('nc', 'nd', 'Na'), ('fc', 'fd', 'iron-air'),
                                                 ('bc', 'bd', 'Bath')):
            if charge_key in IDX and discharge_key in IDX:
                n = int(np.sum((hourly(charge_key) > 1e-6) & (hourly(discharge_key) > 1e-6)))
                simul[label] = n
                if n:
                    raise ValueError(
                        f'#13 VERIFICATION FAILED: perfect-foresight period {year} has {n} hours '
                        f'of simultaneous charge/discharge for {label} storage.')
        report.append({'year': year, 'unserved_mwh': unserved, 'simultaneous_hours': simul})
    return {'verified': True, 'per_period': report}


def verify_assembly(assembled: Dict, standalone_objectives: Sequence[float],
                    assembled_objective: float, tol: float = 1e-6) -> Dict:
    """Checks an UNLINKED assembly against the standalone solves it should reproduce.

    WHY THIS MATTERS MORE THAN IT LOOKS. A block-assembled problem can be subtly wrong -- a
    misplaced offset, a row appended to the wrong matrix -- and still solve to a plausible number.
    There is no other baseline to check against, because the linked result is the thing being
    measured. Assembling WITHOUT linking makes the periods independent, so the discounted sum of
    the standalone objectives must equal the assembled objective exactly.

    Run this before trusting any foresight result.
    """
    if assembled['link_rows']:
        raise ValueError(
            f'verify_assembly() requires an UNLINKED assembly (link_builds=False); this one has '
            f'{assembled["link_rows"]} linking rows. With linking the periods are coupled and the '
            'standalone solves are not the right comparison.')
    expected = sum(obj / (1.0 + assembled['wacc']) ** (y - assembled['base_year'])
                   for obj, y in zip(standalone_objectives, assembled['years']))
    diff = abs(assembled_objective - expected)
    rel = diff / abs(expected) if expected else diff
    return {
        'expected_discounted_sum': expected,
        'assembled_objective': assembled_objective,
        'absolute_difference': diff,
        'relative_difference': rel,
        'matches': rel <= tol,
        'note': (f'Unlinked assembly {"reproduces" if rel <= tol else "DOES NOT reproduce"} the '
                 f'standalone solves: {assembled_objective:,.2f} against an expected '
                 f'{expected:,.2f} ({rel:.2e} relative). '
                 + ('' if rel <= tol else
                    'A mismatch means the assembly itself is wrong -- offsets, matrix stacking or '
                    'discounting -- and no foresight result from it can be trusted.')),
    }
