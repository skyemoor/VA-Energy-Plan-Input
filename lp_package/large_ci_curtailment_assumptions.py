"""
large_ci_curtailment_assumptions.py

Dominion Energy Virginia's Non-Residential Curtailment Program (Scenario 3, A.2 extended):
eligibility, compensation, and the avoided-generation-capacity cross-check recorded as Internal
Debugging Log entry #82.

RECONSTRUCTED 2026-09-10. READ THIS BEFORE RELYING ON IT.

The original file did not survive into this repository. A prior session confirmed by direct search
that it is absent from outputs, uploads and working directories, while its adapter
(`large_ci_curtailment_feature.py`) and that adapter's test suite did survive. The adapter is
non-functional without this module -- importing it raises ModuleNotFoundError -- so anything
downstream in the A.2 large-C&I work is currently broken.

This reconstruction is NOT rebuilt from recollection. It is derived from four surviving artefacts
that between them pin every value:

1. `test_large_ci_curtailment_feature.py` is an executable specification. It names the constants
   this module must expose (`ELIGIBILITY_THRESHOLD_KW`, `COMPENSATION_USD_PER_KW_YEAR`), the
   function it must provide (`avoided_generation_capacity_cost_comparison()`), and every key that
   function's return dict must contain.
2. That test asserts the headline figures directly, with tolerance bands:
   `38 <= aeroderivative_incentive_as_pct_of_avoided_cost <= 43` and
   `68 <= fclass_incentive_as_pct_of_avoided_cost <= 73`.
3. The adapter's own docstring states the original applied NO utility-margin concept, and cites
   the reproduced figures as 40.7% and 70.9%.
4. Back-solving those percentages against the known $36/kW-yr rate gives the avoided-cost values
   the original must have held: 36/0.407 = $88.45/kW-yr and 36/0.709 = $50.78/kW-yr. Those match
   `capex x CCGT_CRF + FOM` on this project's own Gas Turbine World figures to the cent
   ($88.435 and $50.772). The derivation is therefore recovered, not guessed.

The reconstruction is verified by the surviving test suite passing unmodified. Any figure here
that the tests do not constrain is marked below.

WHY THE ANNUALIZATION MATTERS -- a real error found in a sibling module

Avoided capacity cost is an ANNUAL value ($/kW-yr). The Gas Turbine World figures this project
uses ($1,175/kW aeroderivative, $713/kW F-Class) are INSTALLED CAPITAL COSTS -- one-time $/kW.
Converting requires annualizing over the asset life and adding fixed O&M, which is what this
module does and what produces the 40.7%/70.9% finding.

`dlc_assumptions.py` copied the raw capex constants instead, naming them
`AERODERIVATIVE_AVOIDED_COST_USD_PER_KW_YR = 1175` and `F_CLASS_AVOIDED_COST_USD_PER_KW_YEAR = 713`
-- the right module, the wrong variable. Its own comment says so: "matches
AERODERIVATIVE_CAPEX_USD_PER_KW there." That produces a properly-priced benchmark roughly 14x too
high and a headline finding ("70-115x below properly priced") that is off by two orders of
magnitude against this module's own ~41-71%.

Independent cross-check confirming this module's figures rather than the other's: PJM capacity has
never cleared near $713/kW-yr. The 2025/26 record BRA was ~$270/MW-day = $98.5/kW-yr and the
2026/27 cap is $325/MW-day = $118.6/kW-yr. This module's $50.77-$88.44/kW-yr sits inside that
historical range; $713-$1,175/kW-yr sits roughly 6x above the highest price ever cleared.

STALENESS, disclosed

The underlying Gas Turbine World capex figures predate the 2025-2026 gas turbine price surge.
`lp_package/peaker_capex.py` (built 2026-09-10) puts current simple-cycle installed cost at
roughly $1,116-$1,900/kW for the relevant size tiers, against the $713-$1,175/kW used here. Using
current figures would RAISE the avoided-cost benchmark and therefore LOWER the percentage of it
that Dominion's $36/kW-yr rate captures -- strengthening the underpricing finding, not weakening
it. The original figures are retained here so the reconstruction reproduces the established entry
#82 result exactly; updating them is a deliberate decision to be taken separately, not folded into
a reconstruction.
"""
import assumptions


# --- Program terms, Dominion Non-Residential Curtailment Program ---------------------------
# Both constrained by the surviving test suite: the adapter returns ELIGIBILITY_THRESHOLD_KW from
# magnitude_per_unit() and COMPENSATION_USD_PER_KW_YEAR from current_compensation_usd(), and the
# adapter's own docstring names the threshold as 100 kW and the rate as $36/kW/yr.
ELIGIBILITY_THRESHOLD_KW = assumptions.LARGE_CI_ELIGIBILITY_THRESHOLD_KW
COMPENSATION_USD_PER_KW_YEAR = assumptions.LARGE_CI_COMPENSATION_USD_PER_KW_YEAR

# --- Peaker benchmarks, Gas Turbine World ---------------------------------------------------
# Installed capital cost and fixed O&M, as published. NOT avoided costs -- see the annualization
# note in this module's docstring. Same figures cited in docs/research/
# new_peaker_ccgt_costs_by_size.md.
# DELIBERATELY NOT sourced from assumptions.PEAKER_CAPEX_KW_BY_TIER, which holds CURRENT
# (2026) simple-cycle costs of $1,116-1,900/kW. These are the older Gas Turbine World figures the
# established entry #82 finding was computed from, retained ONLY so this reconstruction reproduces
# that finding exactly (40.7% / 70.9%) and its surviving tests pass unmodified.
#
# They are therefore a HISTORICAL BASELINE, not a current cost, and the names say so. Re-running
# the comparison on current costs is a deliberate, separate decision -- it would raise the avoided-
# cost benchmark and LOWER these percentages, strengthening the underpricing finding rather than
# weakening it. Do not silently swap in the current figures; that would change an established,
# cited result without a note.
AERODERIVATIVE_CAPEX_USD_PER_KW_ENTRY82_BASELINE = 1175.0   # 105 MW twin genset, 41.5% efficiency
AERODERIVATIVE_FOM_USD_PER_KW_YR = 16.30
F_CLASS_CAPEX_USD_PER_KW_ENTRY82_BASELINE = 713.0           # 237 MW single genset, 38.2% efficiency
F_CLASS_FOM_USD_PER_KW_YR = 7.00

# Back-compatible aliases -- the adapter and dlc_assumptions reference the original names.
AERODERIVATIVE_CAPEX_USD_PER_KW = AERODERIVATIVE_CAPEX_USD_PER_KW_ENTRY82_BASELINE
F_CLASS_CAPEX_USD_PER_KW = F_CLASS_CAPEX_USD_PER_KW_ENTRY82_BASELINE


def annualized_avoided_capacity_cost_usd_per_kw_yr(capex_usd_per_kw, fom_usd_per_kw_yr):
    """Annualized avoided capacity cost: capital recovery plus fixed O&M.

    Uses `assumptions.CCGT_CRF` (30-year life at the project WACC) rather than a local copy, per
    Rule 6. Recovered by back-solving the surviving test's own expected percentages -- see this
    module's docstring, point 4.
    """
    return capex_usd_per_kw * assumptions.CCGT_CRF + fom_usd_per_kw_yr


def avoided_generation_capacity_cost_comparison():
    """Internal Debugging Log entry #82: Dominion's $36/kW-yr non-residential curtailment rate
    benchmarked against avoided generation-capacity cost alone.

    NO utility margin is applied, matching the original -- the adapter's docstring states this
    explicitly and its tests depend on it.

    "Generation capacity alone" is the deliberate scope: avoided transmission and distribution
    are excluded, so the resulting percentages are an UPPER bound on how much of true total
    avoided cost the current rate captures. Including T&D would lower them further.
    """
    aero = annualized_avoided_capacity_cost_usd_per_kw_yr(
        AERODERIVATIVE_CAPEX_USD_PER_KW, AERODERIVATIVE_FOM_USD_PER_KW_YR)
    fclass = annualized_avoided_capacity_cost_usd_per_kw_yr(
        F_CLASS_CAPEX_USD_PER_KW, F_CLASS_FOM_USD_PER_KW_YR)
    return {
        'compensation_usd_per_kw_yr': COMPENSATION_USD_PER_KW_YEAR,
        'aeroderivative_avoided_cost_usd_per_kw_yr': round(aero, 2),
        'fclass_avoided_cost_usd_per_kw_yr': round(fclass, 2),
        'aeroderivative_incentive_as_pct_of_avoided_cost': round(
            COMPENSATION_USD_PER_KW_YEAR / aero * 100, 1),
        'fclass_incentive_as_pct_of_avoided_cost': round(
            COMPENSATION_USD_PER_KW_YEAR / fclass * 100, 1),
        'td_included': False,
        'scope_note': (
            'Generation capacity only -- avoided transmission and distribution deliberately '
            'excluded, so these percentages are an upper bound on the share of true total avoided '
            'cost the current rate captures.'),
        'staleness_note': (
            'Peaker capex figures predate the 2025-2026 price surge; see lp_package/'
            'peaker_capex.py. Current figures would raise the benchmark and lower these '
            'percentages, strengthening the underpricing finding.'),
    }
