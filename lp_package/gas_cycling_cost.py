"""
gas_cycling_cost.py

What thermal cycling costs a gas fleet, computed from a solved dispatch.

WHY THIS IS PRICED AND NOT FORBIDDEN

`assumptions.MAX_ANNUAL_STARTS` gives 300 starts for combined cycle and 900 for simple cycle,
sourced to Batlle & Rodilla's treatment of an infeasible duty cycle -- "if the production profile
turns out to be unfeasible for a certain technology (for example, for involving exceeding the
maximum number of annual starts) then the associated cost of supplying that production profile with
that technology is set to infinite."

**That is a SCREENING-CURVE DEVICE for choosing between candidate technologies, not a dispatch
constraint**, and treating it as one was a category error caught before it was written (build log
157). Exceeding a starts limit does not stop a machine working; it consumes the maintenance interval
faster and costs more, which is exactly what the maintenance-interval function computes.

**A hard threshold on a soft quantity creates a tuning loop with no end.** Every change to the fleet
-- an availability derate, a different weather year, an import sensitivity -- can push a rung over,
and each time the choice is "block the run or move the limit". Neither is a finding. Pricing it
instead means heavy cycling shows up as money a reviewer can weigh, and `MAX_ANNUAL_STARTS` becomes
a reported comparison rather than a gate.

WHAT THE LP CANNOT SEE, AND WHY

A linear program charges per unit of a variable. Fuel is per MWh, so a cost coefficient works, and
the merit order does exactly that -- each rung carries `heat_rate x fuel_price + VOM`.

**A start is not per MWh.** It is a discrete event: the rung was off, and now it is on. The same
1,000 MWh delivered in one block and in fifty blocks costs identical fuel and wildly different
maintenance, and no linear coefficient on a continuous hourly variable can tell those apart --
nothing in the formulation knows about "previously off".

Expressing it needs a binary on/off per rung per hour, a start indicator derived from consecutive
binaries, and a cost on that indicator. That is unit commitment, and at 8,760 hours across six rungs
it is 52,560 binaries per year (assumptions.GAS_UNIT_COMMITMENT_NOT_MODELLED; issue #17 records the
merit order alone costing 3.8x solve time before any binaries).

**SO THE COST HERE IS A CONSEQUENCE OF THE DISPATCH, NOT AN INPUT TO IT**, and the bias runs one
way: the LP chose a more cycling-heavy pattern than one charged for cycling would have, so this is
an UPPER bound on what a commitment-aware operator would incur.

**Measuring it is how the next step gets decided.** If maintenance comes out at tens of millions a
year, nobody should build a mixed-integer program for it. If it is over a billion, that is the
argument for climbing the ladder -- ramp or minimum-run constraints, then clustered unit commitment,
then full commitment.
"""
from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

import assumptions
import gas_capacity_fit

#: MW. Below this a rung counts as off; linear-programming solutions carry small residuals and a
#: dispatch of 1e-9 MW is not a running machine.
RUNNING_TOLERANCE_MW = 1.0


@dataclass(frozen=True)
class RungCycling:
    """Cycling measurements and maintenance cost for one merit-order rung."""
    rung: str
    technology: str
    nameplate_mw: float
    starts: int
    firing_hours: int
    energy_mwh: float
    equivalent_operating_hours: float
    maintenance_cost_usd: float
    max_annual_starts: float

    @property
    def cycling_ratio(self):
        """Firing hours per start. THE RATIO, NOT THE COUNT, drives the maintenance interval --
        Batlle & Rodilla's peaking unit starts 25 times over 108 firing hours and carries HIGH O&M,
        while their mid-merit unit starts 160 times over ~2,900 hours and carries less."""
        return self.firing_hours / self.starts if self.starts else 0.0

    @property
    def capacity_factor(self):
        return self.energy_mwh / (self.nameplate_mw * 8760.0) if self.nameplate_mw else 0.0

    @property
    def starts_against_reference(self):
        """Starts as a fraction of the technology's reference limit. A COMPARISON, not a test --
        above 1.0 is reported, never raised. See the module docstring."""
        return self.starts / self.max_annual_starts if self.max_annual_starts else 0.0


def technology_for_rung(rung_name):
    """Which maintenance basis a rung uses. Simple-cycle rungs are named for it; everything else in
    this fleet is combined cycle."""
    return 'CT' if rung_name.startswith('ct_') else 'CCGT'


def for_rung(rung_name, hourly_mw, nameplate_mw, technology=None,
             eoh_per_start=None, tolerance_mw=RUNNING_TOLERANCE_MW):
    """Cycling measurements and maintenance cost for one rung's hourly dispatch.

    Maintenance follows Batlle & Rodilla: the fraction of an overhaul interval consumed this year,
    times the overhaul cost, where equivalent operating hours count each start as many run-hours.

        EOH          =  firing_hours  +  starts x EOH_per_start
        maintenance  =  (EOH / overhaul_interval) x overhaul_cost_per_MW x nameplate

    THE START WEIGHTING MATTERS MORE THAN THE TECHNOLOGY SPLIT. GE GER-3620 weights a cold start at
    150-200 run-hour equivalents, warm at 30-60, hot at 10-20, and this project assumes WARM at 45
    (assumptions.EOH_PER_START_ASSUMED_STATE) because the duty is short blocks separated by short
    gaps -- a machine idle two hours has not cooled to 50 C.
    """
    hourly_mw = np.asarray(hourly_mw, dtype=float)
    if hourly_mw.ndim != 1:
        raise ValueError(f'hourly_mw must be a 1-D series, got shape {hourly_mw.shape}')
    if nameplate_mw <= 0:
        raise ValueError(
            f'nameplate_mw must be positive, got {nameplate_mw}. A rung with no capacity cannot '
            'have a maintenance cost, and returning zero would hide a mis-wired stack.')

    technology = technology or technology_for_rung(rung_name)
    if technology not in assumptions.OVERHAUL_INTERVAL_FFH:
        raise ValueError(
            f'unknown technology {technology!r} for rung {rung_name!r}; expected one of '
            f'{sorted(assumptions.OVERHAUL_INTERVAL_FFH)}. Guessing would price the wrong '
            'overhaul scope -- a combined-cycle overhaul covers the steam side as well.')
    if eoh_per_start is None:
        eoh_per_start = assumptions.EOH_PER_START_BY_STATE[
            assumptions.EOH_PER_START_ASSUMED_STATE]

    running = hourly_mw > tolerance_mw
    starts = int(len(gas_capacity_fit.run_lengths(running)))
    firing_hours = int(running.sum())
    equivalent_operating_hours = firing_hours + starts * eoh_per_start
    interval = assumptions.OVERHAUL_INTERVAL_FFH[technology]
    overhaul_per_mw = assumptions.MAJOR_OVERHAUL_USD_PER_MW_BY_TECH[technology]

    return RungCycling(
        rung=rung_name, technology=technology, nameplate_mw=float(nameplate_mw),
        starts=starts, firing_hours=firing_hours, energy_mwh=float(hourly_mw.sum()),
        equivalent_operating_hours=float(equivalent_operating_hours),
        maintenance_cost_usd=float(
            equivalent_operating_hours / interval * overhaul_per_mw * nameplate_mw),
        max_annual_starts=float(assumptions.MAX_ANNUAL_STARTS[technology]))


def for_fleet(rung_series: Dict[str, np.ndarray], nameplate_by_rung: Dict[str, float], **kwargs):
    """Cycling for every rung in a solved dispatch, plus the fleet total.

    Returns (per_rung, total_maintenance_usd). Rungs absent from `nameplate_by_rung` raise rather
    than being skipped: a rung that dispatched energy but has no capacity recorded means the stack
    and the result disagree, which is the kind of mismatch Rule 4 exists to surface.
    """
    missing = sorted(set(rung_series) - set(nameplate_by_rung))
    if missing:
        raise ValueError(
            f'rung(s) {missing} dispatched energy but have no nameplate recorded. The stack and '
            'the solved result disagree about which rungs exist.')
    per_rung = {name: for_rung(name, series, nameplate_by_rung[name], **kwargs)
                for name, series in rung_series.items()}
    return per_rung, sum(r.maintenance_cost_usd for r in per_rung.values())
