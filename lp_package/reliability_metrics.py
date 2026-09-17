"""
reliability_metrics.py

Resource adequacy metrics computed from a solved hourly unserved-energy series.

WHY THESE THREE, AND WHY NOT LOLE

NERC's *Risk Mitigation for Emerging Large Loads* (2026) asks resource planners for "multiple
probabilistic metrics... such as loss of load hours, expected unserved energy, and conditional value
at risk", because these "provide information on the **duration, magnitude, and severity** of
potential shortfall events."

It is explicit that the single aggregate metric is not enough: "without expanded metrics, RPs risk
being surprised by rare, severe outages that **aggregate metrics like loss of load expectation
cannot detect**." So LOLE is the metric the guideline steers away from as a sole measure, which
happens to suit a model that cannot produce it.

WHAT THIS MODULE MEASURES, AND WHAT IT DOES NOT CLAIM

Every solver already extracts the hourly unserved series to verify it is near zero, then discards
it. That series IS a loss-of-load record; these functions name it rather than measure anything new.

**These are REALISATIONS, not EXPECTATIONS.** A proper EUE is an expectation over many scenarios --
NERC asks for "thousands of integrated weather, load, and generation scenarios". This model solves
one weather year at a time, with no forced-outage draws, so what it produces is a single
realisation under a single assumed availability.

The functions are therefore named `unserved_energy_mwh` and `loss_of_load_hours` rather than `eue`.
The correspondence is stated; the term is not claimed. Using `eue` for a deterministic quantity
would invite a reader to compare it against a probabilistic standard it cannot meet.

**Conditional value at risk is not offered at all.** CVaR at 95% needs at least 20 scenarios for a
single tail observation and realistically several hundred for a stable estimate. Eight weather years
give 0.4 observations in that tail. What would close the gap is not more weather years but
FORCED-OUTAGE DRAWS layered on the eight already held -- 8 x 100 draws is 800 scenarios, in NERC's
range. That is scoped as its own piece of work.

ZERO UNSERVED IS A CORRECTNESS TEST; NON-ZERO UNSERVED IS A RESULT

These are different questions and the distinction matters. A scenario built to serve its load must
show zero, and a non-zero value there is a defect -- which is why the runners raise. Scenario 2
bounded by its real gas fleet legitimately shows 30.05 TWh at 2045, and that is a finding about the
statutory minimum rather than a bug. This module reports; it does not judge.
"""
from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np

#: MWh. Below this an hour counts as served: linear-programming solutions carry small residuals, and
#: an unserved value of 1e-9 MWh is a solver artifact rather than a loss-of-load hour.
UNSERVED_TOLERANCE_MWH = 1.0


@dataclass(frozen=True)
class ReliabilityMetrics:
    """Adequacy metrics for one solved year."""
    loss_of_load_hours: int
    unserved_energy_mwh: float
    peak_shortfall_mw: float
    unserved_fraction_of_demand: float
    longest_event_hours: int
    event_count: int

    @property
    def mean_event_hours(self):
        return self.loss_of_load_hours / self.event_count if self.event_count else 0.0


def _events(flag):
    """Lengths of contiguous shortfall blocks."""
    edges = np.diff(np.concatenate(([0], flag.astype(np.int8), [0])))
    return np.flatnonzero(edges == -1) - np.flatnonzero(edges == 1)


def compute(unserved_mwh, demand_mwh=None, tolerance_mwh=UNSERVED_TOLERANCE_MWH):
    """Adequacy metrics from an hourly unserved-energy series.

    `demand_mwh` may be the hourly demand series or its total; it is used only to normalise, and
    omitting it leaves `unserved_fraction_of_demand` at zero.

    NERC's three dimensions map as: DURATION to loss_of_load_hours and longest_event_hours,
    MAGNITUDE to unserved_energy_mwh and peak_shortfall_mw, SEVERITY to the event distribution --
    which is as close as a single realisation gets to the third.
    """
    u = np.asarray(unserved_mwh, dtype=float)
    if u.ndim != 1:
        raise ValueError(f'unserved_mwh must be a 1-D hourly series, got shape {u.shape}')
    if (u < -tolerance_mwh).any():
        raise ValueError(
            f'unserved_mwh contains a value of {u.min():,.1f} MWh. Negative unserved energy is not '
            'a small residual -- it means the variable is being used for something other than '
            'shortfall, and every metric here would be wrong.')
    flag = u > tolerance_mwh
    runs = _events(flag)
    total_demand = (float(np.sum(demand_mwh)) if demand_mwh is not None
                    and np.ndim(demand_mwh) else float(demand_mwh or 0.0))
    return ReliabilityMetrics(
        loss_of_load_hours=int(flag.sum()),
        unserved_energy_mwh=float(u[flag].sum()),
        peak_shortfall_mw=float(u.max(initial=0.0)),
        unserved_fraction_of_demand=(float(u[flag].sum()) / total_demand) if total_demand else 0.0,
        longest_event_hours=int(runs.max()) if len(runs) else 0,
        event_count=int(len(runs)),
    )


def across_weather_years(per_year_metrics: Sequence[ReliabilityMetrics]):
    """Range across weather years, for the thin distribution eight draws support.

    NOT a probabilistic expectation. Eight correlated weather realisations with no outage draws give
    a RANGE, which is worth reporting, and nothing resembling a tail estimate. See the module
    docstring on why conditional value at risk is not offered.
    """
    if not per_year_metrics:
        raise ValueError('no per-year metrics supplied; nothing to summarise across weather years')
    lolh = [m.loss_of_load_hours for m in per_year_metrics]
    eue = [m.unserved_energy_mwh for m in per_year_metrics]
    return {
        'weather_years': len(per_year_metrics),
        'loss_of_load_hours_min': min(lolh), 'loss_of_load_hours_max': max(lolh),
        'loss_of_load_hours_mean': float(np.mean(lolh)),
        'unserved_energy_mwh_min': min(eue), 'unserved_energy_mwh_max': max(eue),
        'unserved_energy_mwh_mean': float(np.mean(eue)),
        'basis': ('range across weather years, not a probabilistic expectation; no forced-outage '
                  'draws, so neither LOLE nor CVaR is derivable from these'),
    }
