"""
gas_merit_order.py

Merit-order dispatch stack for DOM-zone merchant gas: cost per rung, capacity per rung, and
capacity net of retirements and availability in a given year.

SCOPE: all DOM-zone merchant gas, not Dominion-owned only -- Potomac Energy Center sits close to
the Loudoun data-center concentration and will be dispatched whenever prices allow, so restricting
the stack to Dominion-owned plant would omit capacity that genuinely serves zonal load. APCo
territory and CHP are excluded; see assumptions.GAS_PLANT_CAPACITY_MW for why.

CAPACITY BASIS is a required design choice, defaulting to net_summer. See
assumptions.GAS_SEASONAL_BASIS_NOTE -- net winter exceeds net summer by 11.4%, and the DOM zone now
peaks in winter, so the default may be the wrong derate for the binding hour.

WHY THIS EXISTS -- and why it is more than "added realism"

The LP dispatches gas at a SINGLE marginal cost. Its hourly energy-balance dual at 2030 has one
unique value across all 8,760 hours ($54.70/MWh), and the reason is structural rather than a bug:
at 2030 there is no curtailment, so gas is on the margin in every hour, and with one gas price the
marginal cost of one more MWh is the same whether gas runs at 10% or 90% of capacity.

Gas OUTPUT already varies enormously across the day -- less burned at midday when solar is
producing, more in the evening, and wind variation moving dispatch throughout. None of that reaches
the dual, because the dual is MARGINAL cost, not average.

So every physical mechanism that should create intraday price structure is a QUANTITY effect
without a stack and becomes a PRICE effect with one:

    less gas at midday    -> midday clears at ccgt_modern, evening reaches ct_fleet
    battery cycling cost  -> storage has a spread to arbitrage, and its cycling cost floors
                             how far it can close it
    wind variation        -> moves the system up and down the stack rather than along one step

This class is therefore the mechanism by which the model can express any intraday price structure
at all. It is a prerequisite for the arbitrage, demand-flexibility and foresight-bracket work, not
an accuracy improvement on top of them.

RULE 1: this is shared logic every scenario needs with the same formula, differing only in the
year passed in, so it is a class rather than per-scenario code or a free-standing script.

RULE 6: every constant comes from assumptions.py. Nothing is redefined here.

SOURCES
  heat rates          EIA Electric Power Annual Table 8.2 (Form EIA-860, capacity-weighted, 2024)
  capacity per rung   EIA-860 2025 Schedule 3 (Generator Data), Virginia, Operable, NG,
                      Virginia Electric & Power Co; rungs by per-unit Operating Year
  CT VOM              NREL ATB (2022: NGCT $5.00 vs NGCC $2.00; 2020: OCGT $4.49 vs CCGT $1.61)
  retirements         VA_gas_capacity_schedules.md Schedule A
  fuel price          lp_model.gas_cost_mwh(), Deloitte/MEDIUM trajectory
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import assumptions


@dataclass(frozen=True)
class GasRung:
    """One step of the merit order: a cost, a capacity, and what sets each."""
    name: str
    heat_rate_mmbtu_per_mwh: float
    nameplate_mw: float
    vom_mwh: float

    def fuel_cost_mwh(self, year: float) -> float:
        # Imported here rather than at module scope: lp_model imports assumptions, and a
        # module-level import in both directions would be circular.
        import lp_model
        return lp_model.gas_cost_mwh(year, heat_rate=self.heat_rate_mmbtu_per_mwh)

    def marginal_cost_mwh(self, year: float) -> float:
        """Fuel plus VOM -- what the rung costs to run one more MWh, which is what sets price."""
        return self.fuel_cost_mwh(year) + self.vom_mwh


class GasMeritOrder:
    """The Dominion gas fleet as a dispatch stack.

    Construct once per checkpoint year. `available_capacity_mw()` already accounts for
    retirements and the availability factor, so callers do not apply either themselves --
    duplicating that logic at call sites is how the two figures drift apart.
    """

    #: Index into GAS_PLANT_CAPACITY_MW's (rung, nameplate, summer, winter) tuple.
    _BASIS_INDEX = {'nameplate': 1, 'net_summer': 2, 'net_winter': 3}

    def __init__(self,
                 include_new_build: bool = True,
                 capacity_basis: str = 'net_summer',
                 availability_factor: Optional[float] = None,
                 retirement_years: Optional[Dict[str, int]] = None):
        if capacity_basis not in self._BASIS_INDEX:
            raise ValueError(
                f'capacity_basis must be one of {sorted(self._BASIS_INDEX)}, got '
                f'{capacity_basis!r}. There is no default worth guessing: nameplate overstates '
                'deliverable capacity, net summer understates it at a winter-peaking hour, and '
                'mixing two bases produced a phantom 1,167 MW discrepancy on 2026-09-11.')
        self._basis = capacity_basis
        self._availability = (assumptions.GAS_AVAILABILITY_FACTOR
                              if availability_factor is None else availability_factor)
        if not 0.0 < self._availability <= 1.0:
            raise ValueError(
                f'availability_factor must be in (0, 1], got {self._availability!r}. A flat factor '
                'covering forced outages and planned maintenance together -- see '
                'assumptions.GAS_AVAILABILITY_FACTOR for why it is flat rather than scheduled.')
        self._retirements = (dict(assumptions.GAS_PLANT_RETIREMENT_YEAR)
                             if retirement_years is None else dict(retirement_years))
        # The new-build pool is capacity the scenarios PERMIT rather than plant that exists, so it
        # is not in GAS_PLANT_CAPACITY_MW and carries no retirement year. Off by default would be
        # the wrong default: apply_gas_cap() has always included it, and omitting it is what left
        # it unable to dispatch.
        self._include_new_build = include_new_build
        self._vom_by_rung = {
            'new_build_ccgt': assumptions.GAS_NEW_BUILD_VOM_MWH,
            'ccgt_modern': assumptions.CCGT_VOM_MWH,
            'ccgt_fleet': assumptions.CCGT_VOM_MWH,
            'ccgt_legacy': assumptions.CCGT_VOM_MWH,
            'ct_fleet': assumptions.CT_VOM_MWH,
        }
        self._heat_rate_by_rung = dict(assumptions.GAS_MERIT_ORDER_HEAT_RATES)

    # -- reconciling with the scenario's own gas cap -----------------------

    def reconcile_with_scenario_cap(self, year, scenario_cap_mw, new_build_pool_mw=0.0):
        """Compares this stack's hourly availability against the scenario's own gas cap.

        THE PROBLEM THIS EXISTS TO SURFACE (found 2026-09-13). Two independent gas limits were
        being applied and whichever bound first governed, with nobody deciding which should:

            apply_gas_cap()      schedule_b_baseline_mw(year) + 2,862 MW new-build pool,
                                 applied as a per-hour upper bound on IDX['g']
            this stack           sum of rung capacities, net summer x availability

        They disagree:

            2030-2040   cap 12,224 MW   stack 14,054 MW   -> cap binds
            2045        cap  4,722 MW   stack 12,216 MW   -> cap binds

        FIGURES REVISED 2026-09-13 after a filter bug was found: the CHP exclusion was written as
        ~contains('CHP'), and 'IPP Non-CHP' CONTAINS 'CHP', so every merchant independent producer
        was silently dropped -- Doswell, Tenaska and Potomac Energy Center, 3,136 MW, about 30% of
        the DOM-zone fleet. With them restored the STACK NO LONGER BINDS in any year; the scenario
        cap governs throughout. The direction no longer flips.

        The cause is that they use DIFFERENT RETIREMENT SCHEDULES. This stack applies Schedule A
        (physical: Bear Garden 2041, Warren County 2044). schedule_b_baseline_mw applies Schedule B
        (VCEA-driven: a drop to 1,860 MW in 2045). One model, two retirement futures.

        TWO FURTHER MISMATCHES worth naming rather than papering over:
          - Schedule B's 2045 figure of 1,860 MW is Chesterfield + Doswell + Possum Point, and
            DOSWELL IS AN IPP, not Dominion-owned. It is in this stack's DOM-zone scope but is not
            in a Dominion-owned schedule, so the two are not counting the same fleet.
          - The 2,862 MW new-build pool HAS NO RUNG. New gas the scenario permits cannot dispatch,
            because the stack contains only the existing EIA-860 fleet.

        Returns a dict rather than raising: which limit SHOULD govern is a scenario-definition
        question, not something this class can decide. But it must be visible.
        """
        available = self.total_available_mw(year)
        existing_cap = scenario_cap_mw - new_build_pool_mw
        return {
            'year': year,
            'scenario_cap_mw': scenario_cap_mw,
            'scenario_existing_cap_mw': existing_cap,
            'new_build_pool_mw': new_build_pool_mw,
            'stack_available_mw': available,
            'binding': 'stack' if available < scenario_cap_mw else 'scenario_cap',
            'new_build_has_no_rung': new_build_pool_mw > 0,
            'note': (
                f'Scenario cap {scenario_cap_mw:,.0f} MW ({existing_cap:,.0f} existing + '
                f'{new_build_pool_mw:,.0f} new-build pool) against stack availability '
                f'{available:,.1f} MW. '
                + ('The STACK binds, so the scenario\'s own gas allowance is not reachable.'
                   if available < scenario_cap_mw else
                   'The scenario CAP binds, so part of the physically available fleet cannot run.')
                + (f' The {new_build_pool_mw:,.0f} MW new-build pool has NO RUNG and cannot '
                   'dispatch at all.' if new_build_pool_mw > 0 else '')),
        }

    # -- capacity ---------------------------------------------------------

    @property
    def capacity_basis(self) -> str:
        return self._basis

    def rated_capacity_mw_by_rung(self, year: Optional[int] = None) -> Dict[str, float]:
        """Rated capacity per rung on this instance's basis, net of plants retired before `year`.
        No availability applied.

        Built by summing the per-plant table rather than reading the pre-summed rung totals,
        because retirements are plant-specific: Bear Garden (ccgt_fleet) retires 2041 and Warren
        County (ccgt_modern) 2044, so the rung totals move at different times.
        """
        idx = self._BASIS_INDEX[self._basis]
        out = {r: 0.0 for r in self._heat_rate_by_rung}
        if self._include_new_build:
            # The pool is quoted as a single figure, not per-plant, so there is no seasonal
            # (summer/winter) derate to apply and it enters unchanged on all three bases. The
            # AVAILABILITY factor is applied separately in available_capacity_mw() and does apply:
            # a new plant has forced outages and maintenance like any other.
            out['new_build_ccgt'] = assumptions.GAS_NEW_BUILD_POOL_MW
        for plant, row in assumptions.GAS_PLANT_CAPACITY_MW.items():
            if year is not None:
                retire = self._retirements.get(plant)
                if retire is not None and year >= retire:
                    continue
            out[row[0]] = out.get(row[0], 0.0) + row[idx]
        return out

    def available_capacity_mw(self, year: Optional[int] = None) -> Dict[str, float]:
        """Dispatchable capacity per rung: nameplate, net of retirements, times availability."""
        return {r: mw * self._availability for r, mw in self.rated_capacity_mw_by_rung(year).items()}

    def total_available_mw(self, year: Optional[int] = None) -> float:
        return sum(self.available_capacity_mw(year).values())

    # -- the stack --------------------------------------------------------

    def rungs(self, year: float, include_empty: bool = False) -> List[GasRung]:
        """The stack for `year`, ordered cheapest marginal cost first.

        Empty rungs (fully retired) are dropped by default: a zero-capacity step in a dispatch
        stack is a trap for a caller iterating to find the marginal unit.
        """
        cap = self.available_capacity_mw(int(year))
        built = [GasRung(name=r,
                         heat_rate_mmbtu_per_mwh=hr,
                         nameplate_mw=cap.get(r, 0.0),
                         vom_mwh=self._vom_by_rung[r])
                 for r, hr in self._heat_rate_by_rung.items()
                 if r in self._vom_by_rung]
        if not include_empty:
            built = [g for g in built if g.nameplate_mw > 0.0]
        return sorted(built, key=lambda g: g.marginal_cost_mwh(year))

    def marginal_cost_range_mwh(self, year: float) -> Tuple[float, float]:
        """Cheapest and dearest marginal cost in the stack -- the intraday spread gas alone can
        produce, before any scarcity pricing."""
        rs = self.rungs(year)
        if not rs:
            raise ValueError(f'no gas rungs available in {year}; the whole fleet has retired')
        costs = [g.marginal_cost_mwh(year) for g in rs]
        return min(costs), max(costs)

    def marginal_rung_at_output(self, year: float, output_mw: float) -> GasRung:
        """Which rung sets price at a given total gas output -- the price-setting unit.

        Raises rather than clamping if output exceeds the stack (Rule 5): silently returning the
        dearest rung would hide an infeasibility the caller needs to see.
        """
        if output_mw < 0:
            raise ValueError(f'output_mw must be non-negative, got {output_mw!r}')
        cumulative = 0.0
        for rung in self.rungs(year):
            cumulative += rung.nameplate_mw
            if output_mw <= cumulative:
                return rung
        raise ValueError(
            f'gas output {output_mw:,.1f} MW exceeds available stack capacity '
            f'{self.total_available_mw(int(year)):,.1f} MW in {year}. Something above the stack '
            'must serve this -- imports or scarcity, neither of which is modelled.')
