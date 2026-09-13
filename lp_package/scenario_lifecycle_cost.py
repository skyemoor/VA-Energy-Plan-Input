"""
scenario_lifecycle_cost.py

Full annualised cost of a scenario: capital recovery and fixed O&M on every asset, plus the
operating cost the LP objective already carries.

WHY THIS EXISTS

`build_scenario2_problem` is dispatch-only. Its objective contains fuel, VOM, storage cycling,
export revenue and the unserved penalty -- and **no capital whatsoever**, for gas, solar or
storage. Everything is pinned, so there is nothing for the LP to trade capital against.

That makes `result['obj']` an OPERATING cost, not a scenario cost. Reading it as the latter
understates Scenario 2 by billions and, worse, understates it in the direction that flatters the
baseline the whitepaper is measured against.

RULE 1: this extends cost_derivation.AnnualizedCost rather than reimplementing capital recovery.
That class already carries the units discipline -- including a plausibility check for the
one-time-capex-used-as-annual error, which reached a published finding once -- and its own
docstring anticipates capital costing moving into the scenario hierarchy.

THE EXISTING/NEW DISTINCTION, which is the whole difficulty

Capital is charged only on capacity that must be BUILT. Charging it on the existing fleet would
bill Dominion twice for plant already paid for; charging none of it would treat 10 GW of new gas as
free. See gas_lifecycle_cost for the gas case; this class applies the same rule to solar.

WHAT IT DOES NOT DO

It does not annualise over the years an asset actually runs. A CT built in 2035 and stranded at
2045 under 100% compliance has been charged 10 years of a 30-year annuity, implicitly assuming the
remaining 20 have value -- and at 100% they do not. Recorded in `stranding_caveat()` rather than
silently assumed, because it makes late-built gas look cheap when it is very expensive.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import assumptions
from cost_derivation import AnnualizedCost


@dataclass(frozen=True)
class AssetCost:
    """One asset class in the scenario, with its existing and new capacity separated."""
    name: str
    existing_mw: float
    new_mw: float
    capex_usd_per_kw: float
    fixed_om_usd_per_kw_yr: float
    annualised_capital_usd: float
    fixed_om_usd: float
    note: str = ''

    @property
    def total_annual_usd(self) -> float:
        return self.annualised_capital_usd + self.fixed_om_usd


class ScenarioLifecycleCost:
    """Annualised cost of one scenario-year, built asset by asset.

    Assets are added explicitly rather than inferred from the result dict, because a missing asset
    would silently reduce the total and look like a cheaper scenario.
    """

    def __init__(self, year: int, operating_cost_usd: float,
                 capital_recovery_factor: Optional[float] = None):
        if operating_cost_usd < 0:
            raise ValueError(
                f'operating_cost_usd is negative ({operating_cost_usd:,.0f}). The LP objective can '
                'go negative only through export revenue exceeding all costs, which would be a '
                'result worth investigating rather than passing through.')
        self.year = year
        self.operating_cost_usd = float(operating_cost_usd)
        import lp_model
        self.crf = lp_model.CRF if capital_recovery_factor is None else capital_recovery_factor
        self.assets: List[AssetCost] = []
        self.warnings: List[str] = []

    @classmethod
    def from_build_problem_result(cls, year, result, existing_assets,
                                  curtailment_mwh=0.0, unserved_mwh=0.0,
                                  curtailment_penalty_usd_per_mwh=5.0,
                                  capital_recovery_factor=None):
        """Lifecycle cost for a scenario solved through `lp_model.build_problem`.

        THIS IS NOT THE SAME ADJUSTMENT AS SCENARIO 2's, and confusing the two would double-count
        billions. The two objectives contain different things:

            build_scenario2_problem   dispatch-only. NO capital, NO FOM, on anything.
                                      -> add capital and FOM for every asset.
            build_problem             capital AND FOM on BUILT assets are already in the
                                      objective: c[UTILITY_SOLAR_MW] = CRF*SOLAR_CAPEX*1000 +
                                      SOLAR_OM*1000, and the storage energy terms carry
                                      STOR_FOM_PCT.
                                      -> add FOM on EXISTING assets only. Adding capital again
                                         would count the build twice.

        THREE ADJUSTMENTS, and only one of them is an addition:

        1. FOM on EXISTING assets -- ADDED. A plant already paid for still costs money to keep
           available, and the objective has no term for capacity it did not build.

        2. CURTAILMENT PENALTY -- REMOVED. `apply_slcr_constraint(curt_cost=5.0)` exists to
           discourage curtailment in dispatch, not to price it. Real curtailment does cost
           something -- foregone RECs, PPA curtailment payments -- but not $5/MWh, and not as a
           cheque anyone writes. At 100% compliance the build is large enough that curtailment
           reaches tens of TWh, so leaving it in makes high-compliance scenarios look worse by an
           amount that GROWS WITH OVERBUILD, which is exactly where the sweep is most sensitive.

           It is netted out of every scenario, not only the clean ones. Scenario 2's happens to be
           zero, so its total is unchanged -- that symmetry is the point, and a reviewer seeing "a
           cost was removed from the clean scenario" needs it stated.

        3. UNSERVED PENALTY -- ASSERTED ZERO, not adjusted. At $100,000/MWh it would dominate any
           total it appeared in, so a nonzero value is a failed solve rather than a cost. Raises.
        """
        if unserved_mwh > 1.0:
            raise ValueError(
                f'unserved energy is {unserved_mwh:,.1f} MWh, not zero. At $100,000/MWh that term '
                f'contributes ${unserved_mwh * 100_000 / 1e9:,.2f}B and would dominate the total. '
                'A solve with unserved energy has failed verify_result() and its cost is not '
                'meaningful -- fix the solve rather than costing it.')

        curtailment_usd = curtailment_mwh * curtailment_penalty_usd_per_mwh
        c = cls(year, operating_cost_usd=float(result['obj']) - curtailment_usd,
                capital_recovery_factor=capital_recovery_factor)
        c.objective_usd = float(result['obj'])
        c.curtailment_removed_usd = curtailment_usd
        c.curtailment_mwh = curtailment_mwh
        for name, mw, capex, fom in existing_assets:
            # new_mw=0 throughout: build_problem already charged capital and FOM on what it built.
            c.add_asset(name, existing_mw=mw, new_mw=0.0, capex_usd_per_kw=capex,
                        fixed_om_usd_per_kw_yr=fom,
                        note='existing asset -- FOM only; capital is sunk, and any NEW build of '
                             'this type is already priced inside the LP objective')
        return c

    def add_asset(self, name, existing_mw, new_mw, capex_usd_per_kw,
                  fixed_om_usd_per_kw_yr=0.0, note=''):
        """Adds one asset class. Capital is charged on `new_mw` only; FOM on both.

        FOM APPLIES TO EXISTING CAPACITY TOO -- an already-paid-for plant still costs money to keep
        available. Only the capital is sunk.
        """
        if new_mw < 0 or existing_mw < 0:
            raise ValueError(
                f'{name}: capacities must be non-negative, got existing={existing_mw!r}, '
                f'new={new_mw!r}. A negative new-build figure would produce a capital credit.')
        cost = AnnualizedCost(capex_usd_per_kw, fixed_om_usd_per_kw_yr,
                              capital_recovery_factor=self.crf)
        warn = cost.units_plausibility_check()
        if warn:
            self.warnings.append(f'{name}: {warn}')
        self.assets.append(AssetCost(
            name=name, existing_mw=existing_mw, new_mw=new_mw,
            capex_usd_per_kw=capex_usd_per_kw, fixed_om_usd_per_kw_yr=fixed_om_usd_per_kw_yr,
            annualised_capital_usd=new_mw * 1000.0 * capex_usd_per_kw * self.crf,
            fixed_om_usd=(existing_mw + new_mw) * 1000.0 * fixed_om_usd_per_kw_yr,
            note=note))
        return self

    # -- totals ------------------------------------------------------------

    @property
    def annualised_capital_usd(self) -> float:
        return sum(a.annualised_capital_usd for a in self.assets)

    @property
    def fixed_om_usd(self) -> float:
        return sum(a.fixed_om_usd for a in self.assets)

    @property
    def total_annual_usd(self) -> float:
        return self.annualised_capital_usd + self.fixed_om_usd + self.operating_cost_usd

    def cost_per_mwh(self, demand_mwh: float) -> float:
        """Total annual cost divided by demand served. NOT an LCOE -- it is a system average
        including every asset, which is the figure the compliance sweep compares across scenarios.
        """
        if demand_mwh <= 0:
            raise ValueError(f'demand_mwh must be positive, got {demand_mwh!r}')
        return self.total_annual_usd / demand_mwh

    def summary(self) -> Dict:
        return {
            'year': self.year,
            'annualised_capital_usd': self.annualised_capital_usd,
            'fixed_om_usd': self.fixed_om_usd,
            'operating_cost_usd': self.operating_cost_usd,
            'total_annual_usd': self.total_annual_usd,
            'capital_share': (self.annualised_capital_usd / self.total_annual_usd
                              if self.total_annual_usd else 0.0),
            'assets': [{'name': a.name, 'existing_mw': a.existing_mw, 'new_mw': a.new_mw,
                        'annualised_capital_usd': a.annualised_capital_usd,
                        'fixed_om_usd': a.fixed_om_usd, 'note': a.note} for a in self.assets],
            'objective_usd': getattr(self, 'objective_usd', None),
            'curtailment_removed_usd': getattr(self, 'curtailment_removed_usd', 0.0),
            'curtailment_mwh': getattr(self, 'curtailment_mwh', 0.0),
            'warnings': list(self.warnings),
            'caveats': self.stranding_caveat(),
        }

    @staticmethod
    def stranding_caveat() -> str:
        """The limitation a reader must know about before using these figures on a pathway."""
        return (
            'Capital is annualised over the asset\'s full economic life, which assumes it earns '
            'across that whole life. On a PATHWAY that assumption can fail: a CT built in 2035 and '
            'stranded at 2045 under 100% compliance has been charged 10 years of a 30-year annuity, '
            'implicitly crediting the remaining 20 with value they do not have. Correcting it means '
            'either amortising over the years the asset actually runs -- roughly 3x the annual '
            'charge -- or recognising the stranding as a write-off. Until then, LATE-BUILT GAS '
            'LOOKS CHEAP WHEN IT IS VERY EXPENSIVE, which biases against building in the 2035-2040 '
            'window being correctly penalised.')
