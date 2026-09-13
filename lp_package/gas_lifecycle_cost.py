"""
gas_lifecycle_cost.py

Full lifecycle cost of gas in a scenario: capital on NEW build only, fixed and variable costs on
everything that runs.

WHY THIS EXISTS

Scenario 2 -- the whitepaper's baseline, Dominion's approach of building only the statutory solar
and storage -- dispatched gas against a ceiling high enough never to bind, and carried **fuel and
VOM only, no capital at all**. Its 22,478 MW peak at 2045 appeared for free.

That is wrong in the direction that flatters the baseline, which is the direction a reviewer will
attack. But the naive correction is wrong the other way: charging capital on the whole 22,478 MW
would bill Dominion for plant that already exists and is already paid for.

THE DISTINCTION THIS MODULE MAKES

    existing fleet   FOM + fuel + VOM          capital is sunk
    new build        capex + FOM + fuel + VOM  capital is incurred

At 2045 the existing DOM-zone fleet can deliver **12,215.8 MW** (net summer x 0.92 availability,
net of retirements). Scenario 2 peaks at **22,478 MW**. The difference -- about **10,262 MW** -- is
new gas the statutory build implies, and it is currently invisible in the scenario's cost.

WHY POST-SOLVE RATHER THAN IN THE LP

build_scenario2_problem has ONE gas variable and ONE gas price -- no merit order, so no existing/new
distinction is available inside it. Wiring the merit order into that function is a model change.
Computing the increment from the reported peak is an accounting layer, and it gets the baseline's
SLCOE right today without touching dispatch.

WHAT IT CANNOT DO, and this is the reason to eventually wire the merit order in: it cannot split the
new build between CCGT and CT. That split is a capital-versus-fuel trade the LP must make
endogenously -- see estimate_technology_crossover_cf() for why it matters and where the boundary
falls.
"""
from dataclasses import dataclass
from typing import Optional

import assumptions


#: CCGT overnight capital, $/kW, with a band.
#:
#: CENTRAL $2,500 by decision 2026-09-13. A single point figure is not defensible in this market:
#: Gas_Consolidated_Reference.md section 6 records that simple-cycle plant entering service in 2023
#: averaged $562/kW while 2025 costs range $728-1,544/kW -- a 2-3x move in two years -- and that
#: "the most recent CCGT projects are routinely reporting costs of $2,000/kW" against an earlier
#: $1,116-1,427/kW range.
#:
#: WHAT A REVIEWER WILL ASK, and why the band matters more than the level: not "why $2,500" but
#: "why ONE number in a market that moved 3x in two years". The band is the answer. The crossover
#: between CCGT and CT should be reported across it, not at the central value alone.
#:
#: The prior constant was $3,000/kW, above even the "routinely $2,000" recent reports. $2,500
#: central sits between that and recent experience while leaving the high case above it.
CCGT_CAPEX_KW = {'low': 2_000.0, 'central': 2_500.0, 'high': 3_200.0}

#: CT capital, $/kW. Sourced from PEAKER_CAPEX_KW_BY_TIER 'medium' -- the 100-250 MW
#: "classic single new peaker" scale, which is the relevant unit size for filling a capacity gap.
CT_CAPEX_KW = dict(assumptions.PEAKER_CAPEX_KW_BY_TIER['medium'])


@dataclass(frozen=True)
class GasLifecycleCost:
    """Annualised gas cost for one scenario-year, split so the sunk and incurred parts are visible
    separately rather than summed into an unexaminable total."""
    year: int
    peak_gas_mw: float
    existing_available_mw: float
    generation_mwh: float
    capex_basis: str
    new_build_mw: float
    new_build_capex_usd: float
    annualised_capex_usd: float
    fom_existing_usd: float
    fom_new_usd: float
    fuel_and_vom_usd: float

    @property
    def total_annual_usd(self) -> float:
        return (self.annualised_capex_usd + self.fom_existing_usd + self.fom_new_usd
                + self.fuel_and_vom_usd)

    @property
    def capital_share(self) -> float:
        """How much of the annual gas bill is capital on NEW plant. If this is small, the
        existing/new distinction does not change conclusions and the accounting layer is enough.
        If it is large, wiring the merit order into the scenario becomes worth doing."""
        return self.annualised_capex_usd / self.total_annual_usd if self.total_annual_usd else 0.0


def gas_lifecycle_cost(year, peak_gas_mw, existing_available_mw, generation_mwh,
                       marginal_cost_mwh, capex_basis='central',
                       crf=None, ccgt_fom_kw_yr=None) -> GasLifecycleCost:
    """Annualised gas cost, charging capital only on capacity above the existing fleet.

    `existing_available_mw` should come from GasMeritOrder.total_available_mw(year) -- net summer
    capability times availability, net of retirements -- so the increment is measured against what
    can actually deliver, not against nameplate.

    Raises on a negative increment rather than clamping (Rule 5): a peak below existing
    availability means no new build is needed, which is a real and reportable outcome, but a
    NEGATIVE new_build_mw would silently produce a capital credit.
    """
    if peak_gas_mw < 0 or existing_available_mw < 0:
        raise ValueError(
            f'capacities must be non-negative: peak={peak_gas_mw!r}, '
            f'existing={existing_available_mw!r}')
    if capex_basis not in CCGT_CAPEX_KW:
        raise ValueError(
            f'capex_basis must be one of {sorted(CCGT_CAPEX_KW)}, got {capex_basis!r}. There is no '
            'default worth guessing in a market that moved 2-3x in two years -- report the band.')
    import lp_model
    crf = lp_model.CRF if crf is None else crf
    ccgt_fom_kw_yr = (assumptions.CCGT_FOM_KW_YR if ccgt_fom_kw_yr is None else ccgt_fom_kw_yr)

    new_build_mw = max(0.0, peak_gas_mw - existing_available_mw)
    capex = new_build_mw * 1000.0 * CCGT_CAPEX_KW[capex_basis]
    return GasLifecycleCost(
        year=year,
        peak_gas_mw=peak_gas_mw,
        existing_available_mw=existing_available_mw,
        generation_mwh=generation_mwh,
        capex_basis=capex_basis,
        new_build_mw=new_build_mw,
        new_build_capex_usd=capex,
        annualised_capex_usd=capex * crf,
        # FOM is charged on capacity that EXISTS, whether or not its capital is sunk -- an
        # already-paid-for plant still costs money to keep available.
        fom_existing_usd=min(peak_gas_mw, existing_available_mw) * 1000.0 * ccgt_fom_kw_yr,
        fom_new_usd=new_build_mw * 1000.0 * ccgt_fom_kw_yr,
        fuel_and_vom_usd=generation_mwh * marginal_cost_mwh)


def estimate_technology_crossover_cf(year, ccgt_capex_basis='central', ct_capex_basis='central',
                                     ccgt_marginal_mwh=None, ct_marginal_mwh=None,
                                     crf=None) -> float:
    """Capacity factor at which CCGT and CT have equal total cost per MWh.

    Above it, build CCGT -- lower fuel cost repays higher capital. Below it, build CT.

    WHY IT MATTERS. The LP sees only MARGINAL cost, where CCGT is always cheaper ($47.32/MWh at
    2045 against $81.17). So without capital in the objective it would build CCGT for peaking duty
    a CT should serve, at roughly twice the capital per kW. This function says where the boundary
    actually falls, and is the check on whether making gas a build variable is worth the work.

    MATCH THE BASES. Comparing CCGT 'high' against CT 'low' would move the crossover by an artifact
    of mismatched conservatism rather than by anything real, which is why both are explicit.
    """
    import lp_model
    crf = lp_model.CRF if crf is None else crf
    if ccgt_marginal_mwh is None:
        ccgt_marginal_mwh = (lp_model.gas_cost_mwh(year, heat_rate=assumptions.GAS_HEAT_RATE_CCGT_MODERN)
                             + assumptions.CCGT_VOM_MWH)
    if ct_marginal_mwh is None:
        ct_marginal_mwh = (lp_model.gas_cost_mwh(year, heat_rate=assumptions.GAS_HEAT_RATE_CT_FLEET)
                           + assumptions.CT_VOM_MWH)
    # PEAKER_FOM_USD_PER_KW_YR is keyed by machine class, not a scalar. F-class is the match for
    # the 'medium' capex tier (100-250 MW, the classic single new peaker); aeroderivative is the
    # small tier. Taking the wrong one would shift the crossover by an artifact of pairing a
    # capex from one machine class with FOM from another.
    ct_fom_kw_yr = assumptions.PEAKER_FOM_USD_PER_KW_YR['f_class']
    fixed_delta_per_kw_yr = (CCGT_CAPEX_KW[ccgt_capex_basis] * crf + assumptions.CCGT_FOM_KW_YR
                             - CT_CAPEX_KW[ct_capex_basis] * crf
                             - ct_fom_kw_yr)
    marginal_saving_per_mwh = ct_marginal_mwh - ccgt_marginal_mwh
    if marginal_saving_per_mwh <= 0:
        raise ValueError(
            f'CCGT marginal cost ({ccgt_marginal_mwh:.2f}) is not below CT ({ct_marginal_mwh:.2f}), '
            'so there is no capacity factor at which its higher capital is repaid and no crossover '
            'exists. Check the heat rates before using this result.')
    return fixed_delta_per_kw_yr * 1000.0 / 8760.0 / marginal_saving_per_mwh
