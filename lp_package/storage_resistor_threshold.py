"""
storage_resistor_threshold.py

The curtailment price above which the LP prefers to dump surplus energy through storage round-trip
losses rather than curtail it -- producing simultaneous charge and discharge in the same hour.

WHAT WAS FOUND, 2026-09-13

Restoring the $100/MWh curtailment cost from Internal Debugging Log #20 produced **4,710 hours of
simultaneous Na-ion charge/discharge** at 2045. verify_result() raised rather than saving it.

The mechanism is economic, not a solver artifact. Charging 100 MWh and discharging 90 MWh in the
same hour nets 10 MWh ABSORBED -- the round-trip loss -- at a cost of 90 x the discharge cycling
cost. Per MWh absorbed that is

    cycling_cost x RTE / (1 - RTE)

For sodium-ion: $5.43 x 0.90 / 0.10 = **$48.87/MWh**. Against $100/MWh to curtail, using storage as
a resistor is HALF THE PRICE, and the LP takes it.

WHY THIS IS A DERIVATION, NOT ANOTHER DETERRENT

Appendix P.2 §13 records seven attempts at preventing simultaneous dispatch (Internal Debugging Log
#20-20.7) and is careful that the standing mechanism -- discharge-side cycling costs -- qualifies
"not as a cost-based deterrent in the same speculative category" but as a genuine physical cost that
suppresses degeneracy as a SIDE EFFECT.

This module invents nothing. The threshold is arithmetic on two already-sourced parameters: the
Sandia-derived cycling cost and the round-trip efficiency. It states where the existing mechanism
stops working, which §13 explicitly flags as "an empirical question, not a mathematical guarantee".

WHAT IT DELIBERATELY DOES NOT DO

It does not choose the curtailment price. Two different questions are involved and conflating them
would let model mechanics dictate economics:

    what does curtailment COST?          an economic question. #20 answered it at $100/MWh on
                                         stated grounds -- "same order of magnitude as gas cost
                                         and the export price". Nothing found here refutes that.
    where does the LP MISBEHAVE?         a model-mechanics question. This module answers it.

WHEN THE TWO CONFLICT -- as they do now -- that is a DISCLOSED LIMITATION, not a number to tune.
The model cannot represent a defensible curtailment price above the threshold without structural
complementarity (binary variables), which P.2 §13 records as proven correct but impractical at this
scale: ~470 s for one storage type over one month, so plausibly hours per full-year solve.
"""
from typing import Dict, Optional

import assumptions


def _cycling_costs() -> Dict[str, float]:
    """Discharge-side cycling cost per storage type, $/MWh, from the same formulas build_problem
    uses. Read from lp_model rather than duplicated (Rule 6)."""
    import lp_model as lp
    return {
        'sodium_ion': (lp.NA_ENERGY_CAPEX * 1000) / (lp.NA_CYCLE_LIFE * (1.0 - lp.NA_DOD_FLOOR)),
        'iron_air': (lp.FE_ENERGY_CAPEX * 1000) / (lp.FE_CYCLE_LIFE * lp.FE_DOD),
        # Bath's $7.50/MWh is a literal in build_problem, sourced to DOE/PNNL (Mongird et al. 2020)
        # PSH-specific RTE-loss cost at 80% RTE. Mirrored here rather than imported because it is
        # not a module-level constant there; the cross-check below asserts they agree.
        'bath_pumped_hydro': 7.50,
    }


def _round_trip_efficiencies() -> Dict[str, float]:
    import lp_model as lp
    return {'sodium_ion': lp.NA_RTE_CHARGE,
            'iron_air': lp.FE_RTE_CHARGE,
            'bath_pumped_hydro': lp.BATH_RTE_CHARGE}


def _bind_year(year):
    """Binds lp_model's capex constants to `year`, returning the year that was previously bound.

    THE CONSTANTS ARE MUTABLE MODULE STATE. driver.set_year_capex() rebinds them in place, so a
    reader outside a solver gets whichever year ran last -- which may be no checkpoint at all. This
    module computed a sodium-ion threshold of $48.87 that way on 2026-09-14, against $48.06 at
    set_year_capex(2045) and $119.54 at 2030. Found by a test-order failure, not by reading code.

    Callers must state their year. There is no safe default, because the right answer depends on
    which checkpoint is being reasoned about.
    """
    import driver as drv
    import lp_model as lp
    previous = getattr(lp, 'CAPEX_YEAR', None)
    if year is not None:
        drv.set_year_capex(year)
    return previous


def resistor_threshold_mwh(storage_type: Optional[str] = None, year: Optional[float] = None):
    """Curtailment price, $/MWh, above which dumping through this storage type's round-trip losses
    is cheaper than curtailing.

    With no argument, returns every type. The BINDING threshold is the minimum across types --
    the LP will use whichever resistor is cheapest, so one low threshold governs regardless of how
    high the others sit.
    """
    import lp_model as lp
    previous = _bind_year(year)
    try:
        cyc, rte = _cycling_costs(), _round_trip_efficiencies()
        bound_year = lp.CAPEX_YEAR
    finally:
        if year is not None and previous is not None:
            _bind_year(previous)
    out = {}
    for name in cyc:
        r = rte[name]
        if not 0.0 < r < 1.0:
            raise ValueError(
                f'{name}: round-trip efficiency must be strictly between 0 and 1, got {r!r}. At '
                'RTE = 1 there is no round-trip loss to absorb energy and the threshold is '
                'undefined rather than infinite.')
        out[name] = cyc[name] * r / (1.0 - r)
    out['_capex_year'] = bound_year
    if storage_type is not None:
        if storage_type not in out:
            raise ValueError(f'unknown storage type {storage_type!r}; known: '
                             f'{sorted(k for k in out if not k.startswith("_"))}')
        return out[storage_type]
    return out


def binding_threshold_mwh(year: Optional[float] = None) -> float:
    """The lowest threshold across storage types -- the one that actually constrains.

    BATH IS THE BINDING TYPE AT EVERY YEAR, because its $7.50/MWh is a literal in build_problem
    rather than a year-indexed capex term. So this figure does NOT move with the checkpoint even
    though sodium-ion's does ($119.54 at 2030, $48.06 at 2045) -- which is why the conclusions
    drawn from it hold across the horizon.
    """
    t = resistor_threshold_mwh(year=year)
    return min(v for k, v in t.items() if not k.startswith('_'))


def check_curtailment_cost(curtailment_cost_mwh: Optional[float] = None,
                           year: Optional[float] = None) -> Dict:
    """Reports whether the curtailment price sits below the binding threshold.

    Returns a dict rather than raising, because a conflict is a DISCLOSED LIMITATION requiring a
    decision -- run below the threshold and state that the price is model-constrained rather than
    economically derived, or accept MILP for the solves where it matters -- not something this
    module should resolve by silently lowering a sourced figure.
    """
    if curtailment_cost_mwh is None:
        curtailment_cost_mwh = assumptions.CURTAILMENT_COST_MWH
    thresholds = {k: v for k, v in resistor_threshold_mwh(year=year).items()
                  if not k.startswith('_')}
    binding = min(thresholds, key=thresholds.get)
    limit = thresholds[binding]
    safe = curtailment_cost_mwh < limit
    return {
        'curtailment_cost_mwh': curtailment_cost_mwh,
        'thresholds_mwh': thresholds,
        'capex_year': resistor_threshold_mwh(year=year)['_capex_year'],
        'binding_type': binding,
        'binding_threshold_mwh': limit,
        'safe': safe,
        'note': (
            f'Curtailment at ${curtailment_cost_mwh:,.2f}/MWh against a binding threshold of '
            f'${limit:,.2f}/MWh set by {binding}. '
            + ('Below the threshold: curtailing stays cheaper than dumping through round-trip '
               'losses, so the LP has no incentive to charge and discharge simultaneously.'
               if safe else
               'ABOVE THE THRESHOLD. The LP can absorb surplus more cheaply through round-trip '
               'losses than by curtailing, which appears as simultaneous charge and discharge. '
               'Measured at 2045 with $100/MWh: 4,710 hours for Na-ion, caught by verify_result(). '
               'This is a MODEL LIMITATION, not evidence about what curtailment truly costs -- the '
               'model cannot represent a price above the threshold without structural '
               'complementarity, which Appendix P.2 §13 records as proven correct but impractical '
               'at this scale.')),
    }


def cross_check_bath_cycling_cost():
    """Rule 6.2: Bath's cycling cost is a literal in build_problem and mirrored here, so assert
    they agree rather than trusting convention."""
    import inspect
    import lp_model as lp
    src = inspect.getsource(lp.build_problem)
    expected = _cycling_costs()['bath_pumped_hydro']
    if f"c[hv(t,IDX['bd'])] = {expected}" not in src:
        raise AssertionError(
            f'Bath discharge cost in build_problem no longer matches {expected} as mirrored in '
            'storage_resistor_threshold._cycling_costs(). The resistor threshold would be computed '
            'from a stale figure.')
    return True
