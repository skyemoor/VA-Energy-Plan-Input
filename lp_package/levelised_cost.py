"""
levelised_cost.py

Levelises a stream of annual costs and demand into a single $/MWh figure, with terminal value.

    SLCOE = PV(annual costs) / PV(annual demand served)

WHY A SEPARATE CLASS (Rule 1). Every scenario needs this in the same form, and it is not a property
of any one year -- ScenarioLifecycleCost answers "what did 2045 cost", this answers "what does the
pathway cost per MWh". Putting levelisation inside a single-year class would confuse the two scopes.

WHY FOUR CHECKPOINTS ARE NOT ENOUGH. A levelised figure needs the whole stream. Solving 2030, 2035,
2040 and 2045 and averaging them is not an SLCOE: it weights each checkpoint equally, ignores
discounting, and misses that demand grows 72% across the horizon so later years carry far more MWh.
Intermediate years come from dispatch-only re-solves against an interpolated build -- cheap, because
there are no build variables to optimise.

TERMINAL VALUE IS STANDARD PRACTICE, not an optional refinement. NREL's ATB states it directly
across the 2021, 2023 and 2024 editions: "A technical life that is longer than the cost recovery
period means RESIDUAL VALUE may be left after costs have been recovered." NREL 72217 treats it as a
distinct valuation phase producing "a residual value (RV) of net earnings". The European Commission
methodology gives two accepted routes: the residual market value as if sold at the horizon, or the
present value of net cash flows beyond the reference period.

THIS USES THE SECOND EC METHOD, and the reason is that it degrades correctly. An asset with no
post-horizon cash flows -- a gas plant stranded at 100% compliance -- has zero residual value BY
CONSTRUCTION, with no special-case rule needed. The first method would require deciding what a
stranded plant would sell for, which is a judgement the model cannot make.

OMITTING TERMINAL VALUE IS THE CHOICE THAT NEEDS DEFENDING, not including it: with CRF_LIFE_YEARS
= 25 against a 20-year horizon, a plant built in 2044 would otherwise be charged in full and
credited with nothing for the 24 years of service remaining.
"""
from typing import Dict, Optional

import assumptions


class LevelisedCost:
    """Annual cost and demand streams reduced to one $/MWh figure.

    Years are added explicitly and the sequence is checked for gaps, because a levelised cost over
    a partial stream looks identical to one over a complete stream and is wrong by however much is
    missing.
    """

    def __init__(self, base_year: Optional[int] = None, discount_rate: Optional[float] = None):
        self.base_year = assumptions.BASE_YEAR if base_year is None else base_year
        self.discount_rate = assumptions.WACC if discount_rate is None else discount_rate
        if self.discount_rate <= -1.0:
            raise ValueError(f'discount_rate must exceed -1, got {self.discount_rate!r}')
        self.years: Dict[int, Dict] = {}
        self.terminal_values: Dict[str, float] = {}

    # -- building the stream ----------------------------------------------

    def add_year(self, year: int, cost_usd: float, demand_mwh: float):
        """One year of the stream. `cost_usd` should already be on an SLCOE basis -- see
        ScenarioLifecycleCost, which nets out the curtailment penalty and asserts unserved is zero.
        """
        if year in self.years:
            raise ValueError(
                f'{year} already added. Adding a year twice would double its weight in the '
                'levelised figure without changing the denominator visibly.')
        if year < self.base_year:
            raise ValueError(
                f'{year} precedes base_year {self.base_year}; discounting it would INFLATE rather '
                'than discount the cost. Move the base year or drop the year deliberately.')
        if demand_mwh <= 0:
            raise ValueError(f'{year}: demand_mwh must be positive, got {demand_mwh!r}')
        self.years[year] = {'cost_usd': float(cost_usd), 'demand_mwh': float(demand_mwh)}
        return self

    def add_terminal_value(self, asset: str, undepreciated_usd: float, note: str = ''):
        """Residual value of one asset class at the horizon, as a PRESENT value at the final year.

        Pass 0.0 for an asset with no post-horizon cash flows -- a gas plant stranded at 100%
        compliance -- rather than omitting it. An explicit zero records that the asset was
        considered; an omission is indistinguishable from an oversight.
        """
        if undepreciated_usd < 0:
            raise ValueError(
                f'{asset}: terminal value is negative ({undepreciated_usd:,.0f}). A negative '
                'residual is a decommissioning liability, which is a different quantity -- add it '
                'as a cost in the final year rather than as a negative credit here.')
        self.terminal_values[asset] = float(undepreciated_usd)
        return self

    # -- checks ------------------------------------------------------------

    def missing_years(self):
        """Gaps in the stream. A levelised cost over a partial series looks exactly like one over a
        complete series."""
        if not self.years:
            return []
        lo, hi = min(self.years), max(self.years)
        return [y for y in range(lo, hi + 1) if y not in self.years]

    def verify_complete(self):
        gaps = self.missing_years()
        if gaps:
            raise ValueError(
                f'stream has {len(gaps)} missing year(s): {gaps[:8]}'
                f'{"..." if len(gaps) > 8 else ""}. Levelising over a partial stream understates '
                'or overstates by however much is missing, and the result looks identical to a '
                'complete one. Add the missing years or state the range deliberately.')
        if min(self.years) > self.base_year:
            raise ValueError(
                f'stream starts at {min(self.years)} but base_year is {self.base_year}. Either '
                f'extend it back to {self.base_year} or construct with '
                f'base_year={min(self.years)} so the levelised figure states its own period.')

    # -- the figure --------------------------------------------------------

    def discount_factor(self, year: int) -> float:
        return 1.0 / (1.0 + self.discount_rate) ** (year - self.base_year)

    @property
    def pv_cost_usd(self) -> float:
        return sum(v['cost_usd'] * self.discount_factor(y) for y, v in self.years.items())

    @property
    def pv_demand_mwh(self) -> float:
        return sum(v['demand_mwh'] * self.discount_factor(y) for y, v in self.years.items())

    @property
    def pv_terminal_value_usd(self) -> float:
        """Terminal values are stated at the final year, so they discount from there."""
        if not self.years or not self.terminal_values:
            return 0.0
        return sum(self.terminal_values.values()) * self.discount_factor(max(self.years))

    def slcoe(self, include_terminal_value: bool = True) -> float:
        """$/MWh. Reported BOTH ways by convention -- see summary() -- because the terminal-value
        credit is an assumption a reader may want to strip out."""
        if not self.years:
            raise ValueError('no years added; there is nothing to levelise')
        pv = self.pv_cost_usd
        if include_terminal_value:
            pv -= self.pv_terminal_value_usd
        return pv / self.pv_demand_mwh

    def summary(self) -> Dict:
        return {
            'base_year': self.base_year,
            'discount_rate': self.discount_rate,
            'first_year': min(self.years) if self.years else None,
            'final_year': max(self.years) if self.years else None,
            'years_in_stream': len(self.years),
            'missing_years': self.missing_years(),
            'pv_cost_usd': self.pv_cost_usd,
            'pv_demand_mwh': self.pv_demand_mwh,
            'pv_terminal_value_usd': self.pv_terminal_value_usd,
            'terminal_values': dict(self.terminal_values),
            'slcoe_with_terminal_value': self.slcoe(True) if self.years else None,
            'slcoe_without_terminal_value': self.slcoe(False) if self.years else None,
        }


#: Result keys for the four utility build variables, in the order their capex figures are derived
#: below. The pairing is positional and nothing enforces it, so a reordering of either list would
#: credit solar salvage against storage MW without raising -- checked in build_salvage_credit.
BUILD_RESULT_KEYS = ('S_mw', 'PNA_mw', 'ENA_mwh', 'EFE_mwh')


def build_salvage_credit(result, year, horizon_year, life_years=None):
    """Total salvage credit for one solved checkpoint, on an ANNUITY basis, across ALL build assets.

    ONE IMPLEMENTATION FOR BOTH RUNNERS. run_scenario1.py credited SOLAR ONLY while
    run_foresight_comparison.py credited four build variables -- so a comparison drawing its myopic
    side from a saved run_scenario1 result would have weighed a solar-only salvage against a
    four-asset one, biasing the myopia penalty by whatever the storage credit is worth. Found by
    audit 2026-09-14, before either figure was published.

    THE ANNUITY BASIS MATTERS. build_problem charges build variables as CRF x capex x 1000, an
    ANNUAL cost. Crediting raw undepreciated CAPITAL against an annuity-based objective made
    salvage exceed the entire year's cost when this was first written -- $6.50B against $4.13B.

    Uses each asset's own vintage: a 2035 build has 2035's remaining life. Crediting the CUMULATIVE
    total at every checkpoint would count the same capacity once per checkpoint.
    """
    import lp_model as lp
    import assumptions
    life_years = assumptions.CRF_LIFE_YEARS if life_years is None else life_years

    lp_year = getattr(lp, 'CAPEX_YEAR', None)
    if lp_year != year:
        raise ValueError(
            f'capex constants are bound to {lp_year}, not {year}. Call driver.set_year_capex('
            f'{year}) first -- lp_model\'s capex values are mutable module state, and a salvage '
            'credit computed against another year\'s costs is wrong in a way nothing else catches.')

    capex_per_unit = (lp.SOLAR_CAPEX * 1000, lp.NA_POWER_CAPEX * 1000,
                      lp.NA_ENERGY_CAPEX * 1000, lp.FE_ENERGY_CAPEX * 1000)
    if not capex_per_unit[0] > capex_per_unit[2] * 5:
        raise AssertionError(
            f'build ordering looks wrong: position 0 ({capex_per_unit[0]:,.0f}) should be solar '
            f'$/MW and position 2 ({capex_per_unit[2]:,.0f}) storage energy $/MWh, which differ by '
            'an order of magnitude. Check BUILD_RESULT_KEYS against the capex tuple.')

    total = 0.0
    per_asset = {}
    for key, capex in zip(BUILD_RESULT_KEYS, capex_per_unit):
        quantity = float(result.get(key, 0.0))
        credit = undepreciated_value(capex, year, horizon_year, life_years) * lp.CRF * quantity
        per_asset[key] = credit
        total += credit
    return total, per_asset


def undepreciated_value(capex_usd, build_year, horizon_year, life_years,
                        strands_at_horizon=False):
    """Straight-line residual value of an asset at the horizon.

    `strands_at_horizon=True` returns 0.0 -- an asset with no post-horizon cash flows has no
    residual value under the EC's present-value-of-future-cash-flows method, whatever its book
    age. That is the gas case at 100% compliance: the plant exists, it is young, and it is worth
    nothing because it will never run again.

    Raises on an asset built after the horizon rather than returning a value, since that is a
    caller error rather than a modelling case.
    """
    if build_year > horizon_year:
        raise ValueError(
            f'build_year {build_year} is after horizon_year {horizon_year}; an asset not yet built '
            'has no residual value at the horizon.')
    if life_years <= 0:
        raise ValueError(f'life_years must be positive, got {life_years!r}')
    if strands_at_horizon:
        return 0.0
    remaining = max(0.0, life_years - (horizon_year - build_year))
    return capex_usd * (remaining / life_years)
