"""
gas_capacity_fit.py

Fits new gas capacity to the SHAPE of the hourly requirement, not to a peak.

WHY SHAPE RATHER THAN PEAK

A peak-based figure says how many megawatts are needed at the worst hour. It says nothing about
whether those megawatts should be combined-cycle or combustion turbine, and the answer is not a
matter of taste: a tranche that runs in blocks of fifteen hours is CCGT duty, and one that runs in
blocks of two is not.

A load duration curve does not settle it either. Sorting hours by output collapses the time
dimension, so a tranche needed for one long winter block and a tranche needed for forty scattered
summer afternoons look identical on it. **Run length is what distinguishes them.**

THE SPLIT RULE COMES FROM MINIMUM UPTIME, NOT FROM INSPECTION

A CCGT has a minimum up time of about six hours (assumptions.GAS_UNIT_COMMITMENT_NOT_MODELLED,
sourced there alongside start costs). A tranche whose blocks are typically shorter than that cannot
be served by a CCGT without running it past the need, so it is CT duty. A tranche whose blocks are
typically longer can.

So the threshold is derived from a sourced operating constraint and applies to any profile, rather
than being read off one year's curve. Measured at Scenario 2's 2045 profile, the break falls
between 17,000 and 19,000 MW: median run 11 hours at 17,000, 3 hours at 19,000, 1 hour at 21,000.

**This respects minimum uptime without modelling unit commitment.** Blocks assigned to CCGT are long
enough that its uptime constraint would not bind; blocks assigned to CT are within OCGT's one-hour
minimum. The commitment physics is honoured by the assignment rather than by a constraint.

CAPACITY PERSISTS, SO THE FIT IS A TRAJECTORY

Each year is fitted to its own profile and the result carried forward as a running maximum: nothing
already built is unbuilt, and the year a tranche first appears is the year it is built. That matters
for cost -- capacity needed in 2045 should not be charged from 2026.

If a later year needs LESS of a tranche than an earlier one, the running maximum keeps the earlier
build and shows it running at lower utilisation. That is a real result about stranded peaking
capacity, not an artifact to be smoothed away.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

import assumptions

#: Hours. A tranche whose blocks are typically shorter than this cannot be served by a CCGT without
#: running it past the need. Sourced in assumptions.GAS_UNIT_COMMITMENT_NOT_MODELLED as CCGT 6/6 h
#: against OCGT 1/1 h.
CCGT_MIN_UPTIME_HR = 6.0

#: MW. Tranche width for the scan. Fine enough to place the break within a few hundred MW, coarse
#: enough that a single noisy hour cannot define a tranche.
TRANCHE_MW = 500.0


@dataclass(frozen=True)
class CapacityFit:
    """New gas capacity fitted to one year's hourly requirement."""
    year: int
    fleet_mw: float
    peak_requirement_mw: float
    ccgt_mw: float
    ct_mw: float
    ccgt_ceiling_mw: float          #: the output level at which median run falls below uptime
    tranche_detail: Tuple[dict, ...]

    @property
    def total_new_mw(self):
        return self.ccgt_mw + self.ct_mw


def _run_lengths(mask):
    """Lengths of contiguous True blocks. Empty array when there are none."""
    flags = np.concatenate(([0], mask.astype(np.int8), [0]))
    edges = np.diff(flags)
    return np.flatnonzero(edges == -1) - np.flatnonzero(edges == 1)


def median_run_hours(gas_mw, level_mw):
    """Median length, in hours, of the blocks where gas is at or above `level_mw`.

    Returns 0.0 where the level is never reached, which correctly assigns an unreachable tranche to
    neither technology.
    """
    runs = _run_lengths(np.asarray(gas_mw) >= level_mw)
    return float(np.median(runs)) if len(runs) else 0.0


def fit_year(year, gas_mw, fleet_mw, min_uptime_hr=CCGT_MIN_UPTIME_HR, tranche_mw=TRANCHE_MW):
    """Fit CCGT and CT capacity above `fleet_mw` to one year's hourly gas requirement.

    Scans upward in tranches from the fleet ceiling. Each tranche is CCGT duty while the median run
    at its lower edge is at least `min_uptime_hr`, and CT duty above that. The scan does not stop at
    the first short tranche: a profile can have a short block low down and long blocks above it, and
    assigning on each tranche's own median rather than on the first crossing handles that.
    """
    gas_mw = np.asarray(gas_mw, dtype=float)
    if gas_mw.ndim != 1:
        raise ValueError(f'gas_mw must be a 1-D hourly series, got shape {gas_mw.shape}')
    peak = float(gas_mw.max())
    if peak <= fleet_mw:
        return CapacityFit(year=year, fleet_mw=fleet_mw, peak_requirement_mw=peak,
                           ccgt_mw=0.0, ct_mw=0.0, ccgt_ceiling_mw=fleet_mw, tranche_detail=())

    ccgt_mw = ct_mw = 0.0
    ccgt_ceiling = fleet_mw
    detail: List[dict] = []
    level = fleet_mw
    while level < peak:
        top = min(level + tranche_mw, peak)
        med = median_run_hours(gas_mw, level)
        width = top - level
        is_ccgt = med >= min_uptime_hr
        if is_ccgt:
            ccgt_mw += width
            ccgt_ceiling = top
        else:
            ct_mw += width
        detail.append({'from_mw': level, 'to_mw': top, 'median_run_hr': med,
                       'technology': 'CCGT' if is_ccgt else 'CT',
                       'hours_at_or_above': int((gas_mw >= level).sum())})
        level = top
    return CapacityFit(year=year, fleet_mw=fleet_mw, peak_requirement_mw=peak,
                       ccgt_mw=ccgt_mw, ct_mw=ct_mw, ccgt_ceiling_mw=ccgt_ceiling,
                       tranche_detail=tuple(detail))


def fit_trajectory(fits: Sequence[CapacityFit]):
    """Running maximum across years: what must EXIST in each year, and what is BUILT in it.

    CAPACITY PERSISTS. A year needing less than an earlier year builds nothing and retires nothing;
    it simply runs what exists at lower utilisation.

    Returns a list of dicts in year order, each with the cumulative requirement and the increment
    built that year -- the increment being what a cost model should charge to that year.
    """
    ordered = sorted(fits, key=lambda f: f.year)
    out = []
    held_ccgt = held_ct = 0.0
    for f in ordered:
        new_ccgt = max(0.0, f.ccgt_mw - held_ccgt)
        new_ct = max(0.0, f.ct_mw - held_ct)
        held_ccgt = max(held_ccgt, f.ccgt_mw)
        held_ct = max(held_ct, f.ct_mw)
        out.append({'year': f.year,
                    'ccgt_required_mw': f.ccgt_mw, 'ct_required_mw': f.ct_mw,
                    'ccgt_held_mw': held_ccgt, 'ct_held_mw': held_ct,
                    'ccgt_built_mw': new_ccgt, 'ct_built_mw': new_ct,
                    'peak_requirement_mw': f.peak_requirement_mw, 'fleet_mw': f.fleet_mw})
    return out


def peaker_tier_for(mw):
    """Which PEAKER_CAPEX_KW_BY_TIER tier a CT build of this size falls in.

    The tiers exist because unit cost falls with size, and a fit that ignores them would price a
    3,000 MW CT build at small-unit rates.
    """
    if mw <= assumptions.PEAKER_SMALL_TIER_MAX_MW:
        return 'small'
    if mw <= assumptions.PEAKER_MEDIUM_TIER_MAX_MW:
        return 'medium'
    return 'large'
