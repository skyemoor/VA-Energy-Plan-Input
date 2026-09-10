"""
large_ci_curtailment_derived.py -- BACK-COMPATIBILITY SHIM

Superseded 2026-09-10 by `cost_derivation.AvoidedCapacityCost`. Per Rule 1 this belongs in a class
hierarchy: it performed the same capex-lookup-then-annualize operation as `peaker_capex.py`.

Retained only so the surviving adapter (`large_ci_curtailment_feature.py`) and its tests keep
working. New code should use the class.
"""
import assumptions
from cost_derivation import AnnualizedCost, AvoidedCapacityCost

ELIGIBILITY_THRESHOLD_KW = assumptions.LARGE_CI_ELIGIBILITY_THRESHOLD_KW
COMPENSATION_USD_PER_KW_YEAR = assumptions.LARGE_CI_COMPENSATION_USD_PER_KW_YEAR


def annualized_avoided_capacity_cost_usd_per_kw_yr(capex_usd_per_kw, fom_usd_per_kw_yr):
    """Fully parameterized (Rule 8) -- the regression test supplies entry #82's own original
    inputs to confirm the derivation still reproduces its published figures, without those inputs
    living anywhere as constants."""
    return AnnualizedCost(capex_usd_per_kw, fom_usd_per_kw_yr).annual_usd_per_kw_yr()


def avoided_generation_capacity_cost_comparison(case='central'):
    return AvoidedCapacityCost(case=case).comparison()
