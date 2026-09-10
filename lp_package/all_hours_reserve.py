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
from scipy import sparse

IRM = 0.177
CVOW_MW = 2587.2
FE_DURATION = 100.0


def add_all_hours_reserve_margin_constraint(problem, nuclear, wind_cf, exist_solar, solar_cf,
                                             dist_solar_cf, gas_cap_mw, demand):
    IDX = problem['IDX']
    NB, NPH = problem['hv_params']
    T = problem['T']
    BUILD_SCALE = problem.get('BUILD_SCALE', 1.0)

    def hv(t, k):
        return NB + t * NPH + k

    NVAR = NB + T * NPH
    # 4 new per-hour reserve variables: na_reserve, fe_reserve, dist_na_reserve, dist_fe_reserve
    def new_var(t, which):  # which in 0..3
        return NVAR + t * 4 + which

    NVAR_NEW = NVAR + T * 4

    UTILITY_SOLAR_MW, SODIUM_ION_POWER_MW, SODIUM_ION_ENERGY_MWH, IRON_AIR_ENERGY_MWH = 0, 1, 2, 3
    DISTRIBUTED_SOLAR_MW, DISTRIBUTED_SODIUM_ION_POWER_MW = 4, 5
    DISTRIBUTED_SODIUM_ION_ENERGY_MWH, DISTRIBUTED_IRON_AIR_ENERGY_MWH = 6, 7

    rows, cols, data, rhs = [], [], [], []
    row = 0

    for t in range(T):
        nar, fer, dnar, dfer = new_var(t, 0), new_var(t, 1), new_var(t, 2), new_var(t, 3)

        # nd[t] + na_reserve[t] <= PNA_mw
        rows += [row, row, row]; cols += [hv(t, IDX['nd']), nar, SODIUM_ION_POWER_MW]
        data += [1.0, 1.0, -BUILD_SCALE]; rhs.append(0.0); row += 1
        # na_reserve[t] - nsoc[t] <= 0
        rows += [row, row]; cols += [nar, hv(t, IDX['nsoc'])]; data += [1.0, -1.0]; rhs.append(0.0); row += 1

        # fd[t] + fe_reserve[t] <= EFE_mwh / FE_DURATION
        rows += [row, row, row]; cols += [hv(t, IDX['fd']), fer, IRON_AIR_ENERGY_MWH]
        data += [1.0, 1.0, -BUILD_SCALE / FE_DURATION]; rhs.append(0.0); row += 1
        # fe_reserve[t] - fsoc[t] <= 0
        rows += [row, row]; cols += [fer, hv(t, IDX['fsoc'])]; data += [1.0, -1.0]; rhs.append(0.0); row += 1

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

        # All-hours reserve margin itself, in <= form:
        # -na_reserve -fe_reserve -dist_na_reserve -dist_fe_reserve
        #   -BUILD_SCALE*solar_cf[t]*UTILITY_SOLAR_MW -BUILD_SCALE*dist_solar_cf[t]*DISTRIBUTED_SOLAR_MW
        #   <= nuclear[t] + gas_cap_mw + CVOW_MW*wind_cf[t] + exist_solar[t] - (1+IRM)*demand[t]
        rows += [row]*6
        cols += [nar, fer, dnar, dfer, UTILITY_SOLAR_MW, DISTRIBUTED_SOLAR_MW]
        data += [-1.0, -1.0, -1.0, -1.0, -BUILD_SCALE*solar_cf[t], -BUILD_SCALE*dist_solar_cf[t]]
        rhs.append(nuclear[t] + gas_cap_mw + CVOW_MW*wind_cf[t] + exist_solar[t] - (1+IRM)*demand[t])
        row += 1

    n_new_rows = row
    A_new = sparse.coo_matrix((data, (rows, cols)), shape=(n_new_rows, NVAR_NEW)).tocsr()

    A_ub_old = problem['A_ub']
    zero_pad = sparse.csr_matrix((A_ub_old.shape[0], T*4))
    A_ub_left = sparse.hstack([A_ub_old, zero_pad], format='csr')
    A_ub_full = sparse.vstack([A_ub_left, A_new], format='csr')
    b_ub_full = np.concatenate([problem['b_ub'], rhs])

    A_eq_old = problem['A_eq']
    zero_pad_eq = sparse.csr_matrix((A_eq_old.shape[0], T*4))
    A_eq_full = sparse.hstack([A_eq_old, zero_pad_eq], format='csr')

    c_full = np.concatenate([problem['c'], np.zeros(T*4)])
    bounds_full = list(problem['bounds']) + [(0, None)] * (T*4)

    new_problem = dict(problem)
    new_problem['A_ub'] = A_ub_full
    new_problem['b_ub'] = b_ub_full
    new_problem['A_eq'] = A_eq_full
    new_problem['c'] = c_full
    new_problem['bounds'] = bounds_full
    new_problem['_reserve_var_offset'] = NVAR
    return new_problem
