"""
gas_outage_stress.py

Applies a GAS-OUTAGE STRESS WINDOW to an already-built lp.build_problem() output: gas dispatch is
capped at (or near) zero for a contiguous window placed at the design weather year's own worst
cumulative-net-load stretch, while the rest of the year keeps its normal capacity cap.

WHY (this session, 2026-09-09): the 8-year continuous dispatch test found 6.44M MWh unserved against
the 2030 build, yet the LP's own reduced cost said it would build LESS storage if allowed
($4,543/MW positive at the VCEA floor). Diagnosis established this is correct, not a bug: at 2030's
54.8% clean-energy penetration, storage already captures 75.4% of every MWh of surplus that
physically exists, and gas at 12,224 MW covers everything else more cheaply than storage can. Storage
therefore has near-zero marginal value in a 2030 solve -- so a 2030 checkpoint carries almost no
information about the fleet 2045 needs, even though its build becomes the monotonic floor every later
checkpoint inherits.

A prior attempt (charging_adequacy.py, this session) tried to force solar/storage complementarity from
the storage side and failed structurally: constraining "if you build storage you must fill it" is
vacuous when the LP freely chooses zero storage, and it makes storage MORE expensive where it isn't
mandated. This module instead acts on the actual binding variable -- gas availability -- giving storage
real value inside the solve rather than taxing it.

WINDOW LENGTH: 144 hours (6 days), matching this project's own established six-day-lookahead firming
methodology rather than an arbitrary duration.

WINDOW PLACEMENT: located automatically at the maximum-cumulative-net-load 144-hour window in the
weather year actually being solved (net load = demand - available clean generation), so the stress
lands where that year is genuinely hardest rather than at a hand-picked calendar date.

IMPLEMENTED AS BOUND CHANGES ONLY -- no new rows or columns. Deliberate: charging_adequacy.py's four
dense constraint rows (8,760 entries each) made dual simplex stall badly on the full-year problem
(two 290s timeouts). Bounds carry no such penalty.

NOTE ON capacity_cap_mw: this hook sets the gas upper bound for EVERY hour (normal cap outside the
window, stress cap inside it). Callers must therefore pass capacity_cap_mw=None to run_solve and let
this module own that bound entirely -- otherwise run_solve's own capacity_cap_mw logic, which runs
after the hook, overwrites the stress window and silently produces an ordinary unstressed solve.
"""
import numpy as np
import assumptions

SIX_DAY_WINDOW_HOURS = assumptions.GAS_OUTAGE_STRESS_WINDOW_HOURS  # Rule 6


def find_worst_net_load_window(demand, clean_gen, window_hours=SIX_DAY_WINDOW_HOURS):
    """Start index of the contiguous window with the greatest cumulative net load."""
    net = demand - clean_gen
    csum = np.concatenate([[0.0], np.cumsum(net)])
    totals = csum[window_hours:] - csum[:-window_hours]
    return int(np.argmax(totals)), float(totals.max())


def add_gas_outage_stress_window(problem, normal_gas_cap_mw, window_start,
                                  window_hours=SIX_DAY_WINDOW_HOURS, stress_gas_cap_mw=0.0):
    IDX = problem['IDX']
    NB, NPH = problem['hv_params']
    T = problem['T']
    bounds = list(problem['bounds'])

    def hv(t, k):
        return NB + t * NPH + k

    for t in range(T):
        lo, _ = bounds[hv(t, IDX['g'])]
        in_window = window_start <= t < window_start + window_hours
        cap = stress_gas_cap_mw if in_window else normal_gas_cap_mw
        bounds[hv(t, IDX['g'])] = (lo, max(lo or 0.0, cap))

    new_problem = dict(problem)
    new_problem['bounds'] = bounds
    return new_problem
