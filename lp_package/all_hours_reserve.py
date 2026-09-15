"""
all_hours_reserve.py

Rebuilds add_all_hours_reserve_margin_constraint() per the documented spec in
Weather_Year_Robustness_Approaches_and_Findings_2026-08-23.md (the code itself, chained_dispatch_test.py,
did not survive into this session's files -- only this documentation did; rebuilt from its exact,
stated formulas, not from a vague recollection). Extended beyond the original spec to also cover the
distributed segment (na_reserve/fe_reserve only existed for utility-scale in the original document,
since the distributed segment didn't exist yet when it was written) -- both are held to the same
"actually available given real SoC" standard for consistency.

Mechanically: takes an already-built lp.build_problem() output dict and extends it (new columns via
sparse.hstack, new rows via sparse.vstack) rather than rebuilding lp_model.py's own build_problem()
from scratch -- matches the documented approach exactly.
"""
import numpy as np

from lp_model import BATH_MW
from scipy import sparse

_DEFAULT_IRM = 0.177
CVOW_MW = 2587.2
FE_DURATION = 100.0


def add_all_hours_reserve_margin_constraint(problem, nuclear, wind_cf, exist_solar, solar_cf,
                                             dist_solar_cf, gas_cap_mw, demand, IRM=None,
                                             fixed_capacity_mw=None):
    """Holds the installed reserve margin in EVERY hour.

    WORKS ON BOTH PROBLEM SHAPES from one implementation (generalised 2026-09-14), rather than a
    dispatch-specific copy. Appendix P.2 #14 requires an alternative solve path to be built from the
    same code, not reconstructed -- and the three parallel constructions this project has had
    (build_dispatch_problem's curtailment cost 20x adrift, run_solve_multi_duration losing every
    prior_* parameter, the perfect-foresight path skipping every post-build constraint) each
    diverged silently rather than failing.

    The generalisation is small because the shapes differ in one respect that matters. In
    build_problem, capacity is a DECISION VARIABLE, so a row reads

        nd[t] + na_reserve[t] - BUILD_SCALE * PNA_column <= 0

    In build_dispatch_problem, capacity is a fixed input (NVAR_BUILD = 0), so the same physical
    statement moves the capacity term to the right-hand side:

        nd[t] + na_reserve[t] <= PNA_mw

    Pass `fixed_capacity_mw` -- a dict with keys utility_solar_mw, sodium_ion_power_mw,
    iron_air_energy_mwh, and optionally the distributed equivalents -- for a dispatch problem. Omit
    it for a build problem, where the columns carry the capacity.

    A test asserts both paths produce IDENTICAL reserve margins for the same build, so the two
    cannot drift apart without failing.
    """
    # IRM was a module-level literal (0.177) with no way to vary it per call. Made a parameter
    # 2026-09-14 so the solver's own IRM argument reaches the constraint; defaults to the module
    # value so existing behaviour is unchanged.
    if IRM is None:
        IRM = _DEFAULT_IRM
    IDX = problem['IDX']
    NB, NPH = problem['hv_params']
    T = problem['T']
    # `.get(key, default)` RETURNS None WHEN THE KEY EXISTS WITH A None VALUE -- and
    # build_dispatch_problem sets BUILD_SCALE to None. That made `-BUILD_SCALE` a TypeError for any
    # caller passing such a problem: a latent bug in this function, independent of the dispatch
    # work, found by auditing the two shapes against each other on 2026-09-14.
    BUILD_SCALE = problem.get('BUILD_SCALE') or 1.0

    fixed = dict(fixed_capacity_mw or {})
    if bool(fixed) != (NB == 0):
        raise ValueError(
            f'problem has NVAR_BUILD={NB} but fixed_capacity_mw was '
            f'{"supplied" if fixed else "omitted"}. Supply it for a dispatch problem (no build '
            'variables, capacity fixed) and omit it for a build problem (capacity is a column). '
            'Getting this wrong would silently constrain against the wrong quantity.')
    if fixed:
        for required in ('utility_solar_mw', 'sodium_ion_power_mw', 'iron_air_energy_mwh'):
            if required not in fixed:
                raise ValueError(f'fixed_capacity_mw is missing {required!r}')

    # Distributed rows apply only where the problem HAS a distributed segment. build_dispatch_problem
    # has none (NPH 14 against build_problem's 21), and these keys were referenced unguarded --
    # a KeyError for any dispatch caller.
    has_distributed = 'dist_na_discharge_mw' in IDX

    def hv(t, k):
        return NB + t * NPH + k

    NVAR = NB + T * NPH
    # 5 new per-hour reserve variables: na, fe, dist_na, dist_fe, BATH.
    #
    # BATH WAS ABSENT UNTIL 2026-09-14. It is 3,000 MW of dispatchable existing storage, fully
    # modelled for dispatch -- charge and discharge bounded at BATH_MW, state of charge at
    # BATH_MWH, with SOC continuity and a cyclical end condition -- but it contributed NOTHING to
    # reserve margin, so every reserve-constrained solve in this project understated available
    # capacity by 3,000 MW in every hour. Found while diagnosing a 2026 infeasibility whose worst
    # hour was 3,900 MW short.
    _N_RESERVE_VARS = 5

    def new_var(t, which):  # which in 0..4
        return NVAR + t * _N_RESERVE_VARS + which

    NVAR_NEW = NVAR + T * _N_RESERVE_VARS

    UTILITY_SOLAR_MW, SODIUM_ION_POWER_MW, SODIUM_ION_ENERGY_MWH, IRON_AIR_ENERGY_MWH = 0, 1, 2, 3
    DISTRIBUTED_SOLAR_MW, DISTRIBUTED_SODIUM_ION_POWER_MW = 4, 5
    DISTRIBUTED_SODIUM_ION_ENERGY_MWH, DISTRIBUTED_IRON_AIR_ENERGY_MWH = 6, 7

    rows, cols, data, rhs = [], [], [], []
    row = 0

    for t in range(T):
        nar, fer, dnar, dfer = new_var(t, 0), new_var(t, 1), new_var(t, 2), new_var(t, 3)
        bar = new_var(t, 4)

        # nd[t] + na_reserve[t] <= PNA_mw -- capacity as a COLUMN when it is a decision variable,
        # as a right-hand-side CONSTANT when it is fixed. Same physical statement either way.
        if fixed:
            rows += [row, row]; cols += [hv(t, IDX['nd']), nar]
            data += [1.0, 1.0]; rhs.append(fixed['sodium_ion_power_mw']); row += 1
        else:
            rows += [row, row, row]; cols += [hv(t, IDX['nd']), nar, SODIUM_ION_POWER_MW]
            data += [1.0, 1.0, -BUILD_SCALE]; rhs.append(0.0); row += 1
        # na_reserve[t] - nsoc[t] <= 0
        rows += [row, row]; cols += [nar, hv(t, IDX['nsoc'])]; data += [1.0, -1.0]; rhs.append(0.0); row += 1

        # fd[t] + fe_reserve[t] <= EFE_mwh / FE_DURATION
        if fixed:
            rows += [row, row]; cols += [hv(t, IDX['fd']), fer]
            data += [1.0, 1.0]; rhs.append(fixed['iron_air_energy_mwh'] / FE_DURATION); row += 1
        else:
            rows += [row, row, row]; cols += [hv(t, IDX['fd']), fer, IRON_AIR_ENERGY_MWH]
            data += [1.0, 1.0, -BUILD_SCALE / FE_DURATION]; rhs.append(0.0); row += 1
        # fe_reserve[t] - fsoc[t] <= 0
        rows += [row, row]; cols += [fer, hv(t, IDX['fsoc'])]; data += [1.0, -1.0]; rhs.append(0.0); row += 1

        # DISTRIBUTED ROWS ONLY WHERE THE SEGMENT EXISTS. A dispatch problem has none, and these
        # keys were referenced unguarded -- a KeyError for any such caller.
        if has_distributed:
            # dist_nd[t] + dist_na_reserve[t] <= DISTRIBUTED_SODIUM_ION_POWER_MW
            rows += [row, row, row]; cols += [hv(t, IDX['dist_na_discharge_mw']), dnar, DISTRIBUTED_SODIUM_ION_POWER_MW]
            data += [1.0, 1.0, -BUILD_SCALE]; rhs.append(0.0); row += 1
            # dist_na_reserve[t] - dist_nsoc[t] <= 0
            rows += [row, row]; cols += [dnar, hv(t, IDX['dist_na_soc_mwh'])]; data += [1.0, -1.0]; rhs.append(0.0); row += 1

            # dist_fd[t] + dist_fe_reserve[t] <= DISTRIBUTED_IRON_AIR_ENERGY_MWH / FE_DURATION
            rows += [row, row, row]; cols += [hv(t, IDX['dist_fe_discharge_mw']), dfer, DISTRIBUTED_IRON_AIR_ENERGY_MWH]
            data += [1.0, 1.0, -BUILD_SCALE / FE_DURATION]; rhs.append(0.0); row += 1
            # dist_fe_reserve[t] - dist_fsoc[t] <= 0
            rows += [row, row]; cols += [dfer, hv(t, IDX['dist_fe_soc_mwh'])]; data += [1.0, -1.0]; rhs.append(0.0); row += 1
        else:
            # Pin the unused reserve variables to zero so they cannot contribute margin the system
            # does not have. Leaving them free would let the LP satisfy the margin with reserve held
            # on storage that does not exist.
            rows += [row]; cols += [dnar]; data += [1.0]; rhs.append(0.0); row += 1
            rows += [row]; cols += [dfer]; data += [1.0]; rhs.append(0.0); row += 1

        # All-hours reserve margin itself, in <= form:
        # -na_reserve -fe_reserve -dist_na_reserve -dist_fe_reserve
        #   -BUILD_SCALE*solar_cf[t]*UTILITY_SOLAR_MW -BUILD_SCALE*dist_solar_cf[t]*DISTRIBUTED_SOLAR_MW
        #   <= nuclear[t] + gas_cap_mw + CVOW_MW*wind_cf[t] + exist_solar[t] - (1+IRM)*demand[t]
        # BATH. Existing capacity, so the power limit is a constant on the right-hand side in BOTH
        # problem shapes -- unlike Na and Fe, whose capacity is a decision variable in build_problem.
        #   bd[t] + bath_reserve[t] <= BATH_MW
        rows += [row, row]; cols += [hv(t, IDX['bd']), bar]
        data += [1.0, 1.0]; rhs.append(BATH_MW); row += 1
        #   bath_reserve[t] - bsoc[t] <= 0   -- reserve cannot exceed stored energy
        rows += [row, row]; cols += [bar, hv(t, IDX['bsoc'])]; data += [1.0, -1.0]
        rhs.append(0.0); row += 1

        base_rhs = (nuclear[t] + gas_cap_mw + CVOW_MW*wind_cf[t] + exist_solar[t]
                    - (1+IRM)*demand[t])
        if fixed:
            # Built solar is a known constant, so its contribution moves to the right-hand side.
            built = (fixed['utility_solar_mw'] * solar_cf[t]
                     + fixed.get('distributed_solar_mw', 0.0) * dist_solar_cf[t])
            rows += [row]*5
            cols += [nar, fer, dnar, dfer, bar]
            data += [-1.0, -1.0, -1.0, -1.0, -1.0]
            rhs.append(base_rhs + built)
        else:
            rows += [row]*7
            cols += [nar, fer, dnar, dfer, bar, UTILITY_SOLAR_MW, DISTRIBUTED_SOLAR_MW]
            data += [-1.0, -1.0, -1.0, -1.0, -1.0,
                     -BUILD_SCALE*solar_cf[t], -BUILD_SCALE*dist_solar_cf[t]]
            rhs.append(base_rhs)
        row += 1

    n_new_rows = row
    A_new = sparse.coo_matrix((data, (rows, cols)), shape=(n_new_rows, NVAR_NEW)).tocsr()

    A_ub_old = problem['A_ub']
    zero_pad = sparse.csr_matrix((A_ub_old.shape[0], T*_N_RESERVE_VARS))
    A_ub_left = sparse.hstack([A_ub_old, zero_pad], format='csr')
    A_ub_full = sparse.vstack([A_ub_left, A_new], format='csr')
    b_ub_full = np.concatenate([problem['b_ub'], rhs])

    A_eq_old = problem['A_eq']
    zero_pad_eq = sparse.csr_matrix((A_eq_old.shape[0], T*_N_RESERVE_VARS))
    A_eq_full = sparse.hstack([A_eq_old, zero_pad_eq], format='csr')

    c_full = np.concatenate([problem['c'], np.zeros(T*_N_RESERVE_VARS)])
    bounds_full = list(problem['bounds']) + [(0, None)] * (T*_N_RESERVE_VARS)

    new_problem = dict(problem)
    new_problem['A_ub'] = A_ub_full
    new_problem['b_ub'] = b_ub_full
    new_problem['A_eq'] = A_eq_full
    new_problem['c'] = c_full
    new_problem['bounds'] = bounds_full
    new_problem['_reserve_var_offset'] = NVAR
    return new_problem


def margin_shortfall_hours(problem, x, nuclear, wind_cf, exist_solar, solar_cf, built_solar_mw,
                           na_power_mw, fe_power_mw, gas_ceiling_mw, demand, bath_mw=None,
                           irm=None):
    """Hours where available capacity falls short of (1 + irm) x demand, given a solved dispatch.

    A READ-ONLY CROSS-CHECK (Rule 4), not a substitute for the constraint. Against a solve that HAD
    the constraint applied it should return empty; against one that did not, it reports how far
    short the dispatch actually was, and in which hours.

    WHY IT MATTERS BEYOND CHECKING. When a pinned-build year comes back INFEASIBLE -- which is how
    an inadequate interpolated build announces itself in the annual stream -- the solver says only
    "infeasible". This says which hours and by how much, which is the difference between a finding
    and a dead end.

    STORAGE CONTRIBUTES min(rated_power, soc[t]) -- the "actually available" standard, not rated
    power assumed full. A battery at 10% charge cannot deliver its nameplate.

    PORTED 2026-09-14 from scenario2_all_hours_reserve.py, which was deleted. THE ORIGINAL OMITTED
    BATH -- the same gap the constraint itself had until the day before -- so a shortfall it
    reported was overstated by whatever Bath could have delivered. Bath is included here, defaulting
    to the model's BATH_MW.
    """
    IDX = problem['IDX']
    _, NPH = problem['hv_params']
    bath_mw = BATH_MW if bath_mw is None else bath_mw
    irm = _DEFAULT_IRM if irm is None else irm
    short = []
    for t in range(len(demand)):
        nsoc = x[t * NPH + IDX['nsoc']]
        fsoc = x[t * NPH + IDX['fsoc']]
        bsoc = x[t * NPH + IDX['bsoc']] if 'bsoc' in IDX else 0.0
        avail = (nuclear[t] + gas_ceiling_mw + CVOW_MW * wind_cf[t] + exist_solar[t]
                 + built_solar_mw * solar_cf[t]
                 + min(na_power_mw, nsoc) + min(fe_power_mw, fsoc) + min(bath_mw, bsoc))
        need = (1.0 + irm) * demand[t]
        if avail < need:
            short.append((t, need - avail))
    return short
