"""
large_ci_curtailment_derived.py

Dominion Energy Virginia's Non-Residential Curtailment Program (Scenario 3, A.2 extended): the
avoided-generation-capacity comparison recorded as Internal Debugging Log entry #82.

RENAMED 2026-09-10 from `large_ci_curtailment_assumptions.py`. The old name was wrong twice over:
this module holds no assumptions of its own -- every input now comes from `assumptions.py` -- and
what it does hold is a DERIVATION. Same split as `dlc_derived_assumptions.py`.

WHAT CHANGED, and why it matters

An earlier version of this module hardcoded the peaker capital costs the entry #82 finding was
originally computed from ($1,175/kW aeroderivative, $713/kW F-Class, Gas Turbine World) under
names ending `_ENTRY82_BASELINE`, to keep that cited finding reproducible while current costs
moved on.

That was wrong, for a reason worth stating plainly: entry #82's claim is *"Dominion's current
$36/kW-yr rate captures X% of avoided generation-capacity cost"*. That is a claim about what a
peaker costs to build NOW, against what Dominion pays NOW. It was never a claim about history.
Freezing the input to protect the output inverts the dependency -- and a hardcoded historical
value in code violates Software Engineering Standards Rule 8 regardless of what it is named.

So the chain is now live end to end:

    avoided capacity cost = peaker capex x CCGT_CRF + fixed O&M
                            ^assumptions   ^assumptions  ^assumptions

Change a peaker cost in `assumptions.py` and the avoided cost, the percentages, and the figure
reported in the whitepaper all move together.

The historical RESULT (40.7% / 70.9%, computed on the then-current Gas Turbine World costs) is
recorded in `registers/Provenance_Register.xlsx` as a superseded result, which is where a
historical figure belongs -- not frozen in code as an input.

WHAT THE CURRENT FIGURES SAY

On current costs (`assumptions.PEAKER_CAPEX_KW_BY_TIER`, sourced to GridLab September 2025 and
Wood Mackenzie April 2026 -- see that block for the derivation), Dominion's $36/kW-yr captures
roughly 35-38% of avoided generation-capacity cost at the central case, against 41-71% on the
older costs. Tighter and lower: a stronger, cleaner finding, and one that is still an UPPER bound
because avoided transmission and distribution are deliberately excluded.

Note both benchmark units now fall in the same size tier under current cost data, which is tiered
by size rather than by unit model, so the remaining spread between them comes from fixed O&M
rather than capital cost.
"""
import assumptions


def annualized_avoided_capacity_cost_usd_per_kw_yr(capex_usd_per_kw, fom_usd_per_kw_yr):
    """Annualized avoided capacity cost: capital recovery plus fixed O&M.

    Fully parameterized (Rule 8) so a caller can supply any capex/FOM pair -- which is how the
    regression test verifies this derivation reproduces entry #82's original figures from its
    original inputs, without those inputs living in the module as constants.

    Uses `assumptions.CCGT_CRF` (30-year life at the project WACC) rather than a local copy.
    """
    return capex_usd_per_kw * assumptions.CCGT_CRF + fom_usd_per_kw_yr


def avoided_generation_capacity_cost_comparison(case='central'):
    """Internal Debugging Log entry #82, computed live on current peaker costs.

    `case` selects 'low', 'central' or 'high' from the sourced cost range. Central is this
    project's reporting convention; the range belongs in a footnote wherever the figure appears.

    Scope: generation capacity ONLY. Avoided transmission and distribution are deliberately
    excluded, so the resulting percentages are an UPPER bound on how much of true total avoided
    cost the current rate captures -- including T&D would lower them further.
    """
    import peaker_capex

    rate = assumptions.LARGE_CI_COMPENSATION_USD_PER_KW_YEAR
    units = {
        'aeroderivative': (105.0, assumptions.PEAKER_FOM_USD_PER_KW_YR['aeroderivative']),
        'f_class': (237.0, assumptions.PEAKER_FOM_USD_PER_KW_YR['f_class']),
    }
    out = {'compensation_usd_per_kw_yr': rate, 'cost_case': case, 'td_included': False}
    for name, (unit_mw, fom) in units.items():
        capex = peaker_capex.peaker_capex_kw(unit_mw, case)
        avoided = annualized_avoided_capacity_cost_usd_per_kw_yr(capex, fom)
        key = 'aeroderivative' if name == 'aeroderivative' else 'fclass'
        out[f'{key}_capex_usd_per_kw'] = capex
        out[f'{key}_avoided_cost_usd_per_kw_yr'] = round(avoided, 2)
        out[f'{key}_incentive_as_pct_of_avoided_cost'] = round(rate / avoided * 100, 1)
    out['scope_note'] = (
        'Generation capacity only -- avoided transmission and distribution deliberately excluded, '
        'so these percentages are an upper bound on the share of true total avoided cost the '
        'current rate captures.')
    return out


# Back-compatible aliases for the surviving adapter (large_ci_curtailment_feature.py), which
# references these names directly.
ELIGIBILITY_THRESHOLD_KW = assumptions.LARGE_CI_ELIGIBILITY_THRESHOLD_KW
COMPENSATION_USD_PER_KW_YEAR = assumptions.LARGE_CI_COMPENSATION_USD_PER_KW_YEAR
