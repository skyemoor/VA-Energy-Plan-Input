"""
peaker_capex.py -- BACK-COMPATIBILITY SHIM

Superseded 2026-09-10 by `cost_derivation.PeakerCost`. Per Rule 1 this belongs in a class
hierarchy: it performed the same capex-lookup-then-annualize operation as
`large_ci_curtailment_derived.py`, and as the still-owed CapitalCostMixin will.

Retained only so existing callers do not break. New code should use the class, which also carries
a units plausibility check -- the confusion between installed capex and annual cost reached a
published finding in this project once.

Sourcing, size tiering and the volatility caveat live with the values in assumptions.py.
"""
import assumptions
from cost_derivation import PeakerCost

SMALL_TIER_MAX_MW = assumptions.PEAKER_SMALL_TIER_MAX_MW
MEDIUM_TIER_MAX_MW = assumptions.PEAKER_MEDIUM_TIER_MAX_MW
PEAKER_CAPEX_KW_BY_TIER = assumptions.PEAKER_CAPEX_KW_BY_TIER
DUAL_FUEL_ADDER_KW = assumptions.PEAKER_DUAL_FUEL_ADDER_KW
FAST_TRACK_PREMIUM_FRACTION = assumptions.PEAKER_FAST_TRACK_PREMIUM_FRACTION


def size_tier(unit_mw):
    if unit_mw is None or unit_mw <= 0:
        raise ValueError(f"unit_mw must be positive, got {unit_mw!r}")
    return PeakerCost(unit_mw).size_tier()


def peaker_capex_kw(unit_mw, case='central', dual_fuel=False, fast_track=False):
    return PeakerCost(unit_mw, case, dual_fuel=dual_fuel,
                      fast_track=fast_track).capex_usd_per_kw


def peaker_project_cost_dollars(total_mw, unit_mw, case='central', **kwargs):
    cost = PeakerCost(unit_mw, case, **kwargs)
    return {
        'total_mw': total_mw,
        'unit_mw': unit_mw,
        'size_tier': cost.size_tier(),
        'capex_per_kw': cost.capex_usd_per_kw,
        'total_cost_dollars': cost.total_capital_dollars(total_mw),
        'whole_units_required': cost.units_required(total_mw),
        'case': case,
    }
