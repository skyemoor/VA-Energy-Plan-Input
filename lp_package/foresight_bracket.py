"""
foresight_bracket.py

Bounds distributed storage arbitrage value between a no-lookahead lower bound and a
perfect-foresight upper bound, rather than producing a single point estimate.

WHY BOUND RATHER THAN ESTIMATE (decision 2026-09-11)

Scenario 3's distributed segment responds to `distributed_exogenous_price_mwh`, whose scarcity
component is near-constant -- coefficient of variation 3.99%, minimum 84% of mean, zero hours below
half the mean (see scenario3_build.six_day_scarcity_value_proxy). The series therefore carries no
multi-day lookahead content, while the LP dispatches utility-scale storage with perfect foresight.

That asymmetry systematically favours utility-scale storage in precisely the comparison Scenario 3
exists to make. Three responses were considered and rejected:

  FIX THE PROXY       needs a capacity reference AND a price-response curve, both unsourced. Either
                      choice materially determines how much value distributed storage captures, and
                      a hand-chosen signal favouring the thing the paper advocates is the easiest
                      finding in the document to attack.
  BLINDFOLD BOTH      run utility dispatch without foresight too. Cheaper than it sounds -- the
                      machinery exists -- but the LP SIZES the fleet assuming perfect dispatch, so
                      stripping foresight afterwards leaves a fleet optimised for an operator that
                      does not exist. Doing it properly needs an iterative sizing loop around a
                      heuristic dispatch, which is a different optimisation problem.
  REPORT AND ABSTAIN  state the asymmetry, claim nothing about relative storage performance. Costs
                      nothing but editorial discipline, and remains the fallback.

Bracketing was adopted because it introduces NO NEW PARAMETER. There is no capacity reference to
choose and no curve to shape, so there is nothing for a reviewer to name as arbitrary. It also
converts an unquantified bias into a measured range.

ESTABLISHED PRECEDENT, not a construction invented here

  Brattle, "Stacked Benefits" (California)     Limited vs Perfect Foresight, 16% gap,
                                                upper bound $328/kW-yr, regulatory valuation
  Hornek et al., arXiv 2501.07121               forecast-driven vs perfect foresight, 11% gap
  arXiv 2505.12538                              Limited vs Perfect Foresight capacity expansion,
                                                long-duration storage
  arXiv 2407.21409                              perfect vs myopic, 96-hour rolling horizon
  Nature Comms (Switch, Western Interconnect)   analogous bias "less than 10% for nearly all
                                                technologies"

Published gaps cluster at 10-16%. Ours may be wider: those are day-ahead or intraday problems,
while this is multi-day rationing at high renewable penetration -- where foresight should matter
most.

SCOPE -- READ BEFORE USING THIS FOR ANYTHING ELSE

This bounds ARBITRAGE VALUE ONLY. Perfect foresight is a genuine ceiling there: nobody beats an
operator who captures every spread.

It does NOT bound RELIABILITY CONTRIBUTION, and must not be used for capacity accreditation.
Shen, Ilic & Parsons (arXiv 2607.27021) find that demand uncertainty induces a PRECAUTIONARY
policy -- hedging against scarcity that may not arrive -- which is qualitatively different from a
degraded perfect foresight. A precautionary operator may deliver MORE reliability than one spending
storage optimally against known outcomes, so perfect foresight is not the ceiling on that metric.
Capacity accreditation is deferred; see docs/PIPELINE_COMPLETENESS.md.
"""
from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class ForesightBracket:
    """A bounded arbitrage value with the caveats that must travel with it."""
    lower_bound_usd: float
    upper_bound_usd: float
    checkpoint_year: int
    storage_mwh: float
    gap_fraction: float          # (upper - lower) / upper. EXCEEDS 1 when the realised dispatch
                                 # is value-destroying (negative lower bound) -- which is a real
                                 # possibility for a badly-signalled operator, not an error.
    realised_cycles_per_year: float
    envelope_cycles_per_year: float
    caveats: tuple

    @property
    def lower_bound_is_value_destroying(self) -> bool:
        """True when the realised dispatch loses money -- charging dearer than it discharges.

        Possible in reality: an operator responding to a price signal with no lookahead can buy
        into a rising market and sell into a falling one. When this is True, gap_fraction exceeds
        1 and should be reported as 'the signal is worse than not operating' rather than as a
        percentage shortfall.
        """
        return self.lower_bound_usd < 0

    def as_range_string(self) -> str:
        return (f'${self.lower_bound_usd/1e6:,.1f}M - ${self.upper_bound_usd/1e6:,.1f}M/yr '
                f'({self.gap_fraction:.0%} gap)')


#: The five statements that must accompany any figure derived from this bracket. Returned with
#: every result rather than left in documentation, so a caller building a table attaches them
#: programmatically and cannot omit one by forgetting.
BRACKET_CAVEATS = (
    'The upper bound is theoretical. In Brattle\'s own words for the equivalent case, it is "not '
    'intended to represent an estimate of the most likely value".',
    'The lower bound is probably conservative. arXiv 2505.12538 finds fixed-price heuristic rules '
    '"likely to underestimate", and the flat scarcity term used here is close to one.',
    'Real fleets are heterogeneous. This range spans a population with differing lookahead '
    'sophistication, not an error bar on a single operator.',
    'The WIDTH is itself the finding: it measures what longer-horizon market signals would unlock.',
    'This bounds ARBITRAGE VALUE ONLY. No claim about reliability contribution or capacity '
    'accreditation follows from it -- perfect foresight is not a ceiling on that metric.',
)


def arbitrage_value_no_lookahead(price_mwh, charge_mwh, discharge_mwh) -> float:
    """Realised arbitrage value from a dispatch the caller already produced.

    Takes dispatch as input rather than computing it: the lower bound IS the Scenario 3 solve's own
    distributed dispatch, and recomputing it here with a different heuristic would compare two
    things that differ by more than foresight.
    """
    p = np.asarray(price_mwh, dtype=float)
    c = np.asarray(charge_mwh, dtype=float)
    d = np.asarray(discharge_mwh, dtype=float)
    if not (len(p) == len(c) == len(d)):
        raise ValueError(
            f'length mismatch: price {len(p)}, charge {len(c)}, discharge {len(d)}. All three must '
            'describe the same hours.')
    return float(np.sum(d * p) - np.sum(c * p))


def arbitrage_value_perfect_foresight(price_mwh, power_mw, energy_mwh,
                                      cycles_per_year=None,
                                      round_trip_efficiency=0.90,
                                      depth_of_discharge_floor=0.20) -> float:
    """Maximum extractable arbitrage value given full knowledge of the price series.

    Sorts the year's hours and pairs the cheapest charging hours against the dearest discharging
    hours, up to the energy throughput a year of cycling permits.

    DEFECT FOUND AND FIXED 2026-09-11: the first version computed a SINGLE cycle's value across the
    whole year -- n = usable_mwh / power_mw hours of charge and discharge, full stop -- so a naive
    dispatch cycling daily beat the supposed upper bound, and bracket() correctly refused the
    inverted result. The fix is to multiply by cycles per year.

    cycles_per_year defaults to assumptions.NA_CYCLES_PER_YEAR_REQUIREMENT. That is NOT a new
    parameter introduced for this method -- it is the project's own established sodium-ion cycling
    figure, already used by charging_adequacy.py, and the property that makes bracketing defensible
    (no tunable knob) is preserved. A caller may override it for iron-air, whose own figure is far
    lower.

    THIS IS AN UPPER ENVELOPE, NOT A DISPATCH SIMULATION. It ignores state-of-charge chronology, so
    it can pair hours no chronologically-feasible schedule could reach. That overstatement is
    DELIBERATE and appropriate -- the bound's job is to be unreachable, and a
    chronologically-constrained optimum would understate the ceiling this is meant to establish.
    Stated plainly rather than buried, because a reader could otherwise mistake this for a
    simulation. It is an upper envelope.
    """
    import assumptions

    if cycles_per_year is None:
        cycles_per_year = assumptions.NA_CYCLES_PER_YEAR_REQUIREMENT
    p = np.sort(np.asarray(price_mwh, dtype=float))
    usable_mwh = energy_mwh * (1.0 - depth_of_discharge_floor)
    if usable_mwh <= 0 or power_mw <= 0 or cycles_per_year <= 0:
        return 0.0

    hours_per_cycle = usable_mwh / power_mw
    # Total charging hours a year of cycling permits, capped at half the series -- charge and
    # discharge hours are disjoint, so neither can exceed T/2.
    n = int(min(round(hours_per_cycle * cycles_per_year), len(p) // 2))
    if n < 1:
        return 0.0
    cheapest, dearest = p[:n], p[-n:]
    return float(np.sum(dearest) * power_mw * round_trip_efficiency
                 - np.sum(cheapest) * power_mw)


def bracket(checkpoint_year: int, price_mwh, charge_mwh, discharge_mwh,
            power_mw: float, energy_mwh: float,
            cycles_per_year: Optional[float] = None,
            round_trip_efficiency: float = 0.90,
            depth_of_discharge_floor: float = 0.20) -> ForesightBracket:
    """Bounds distributed arbitrage value for one checkpoint.

    Both bounds use the SAME price series and the SAME fleet. Only foresight differs -- which is
    the whole point: any other difference between the two runs would contaminate the gap with
    something other than lookahead.
    """
    lo = arbitrage_value_no_lookahead(price_mwh, charge_mwh, discharge_mwh)

    # The envelope must allow AT LEAST the cycling the realised dispatch actually used, or the two
    # bounds are computed under different constraints and the gap measures cycling rather than
    # foresight. Found 2026-09-11: with a fixed default, a dispatch cycling more than the default
    # inverted the bracket and bracket() raised on legitimate input.
    import assumptions
    usable = energy_mwh * (1.0 - depth_of_discharge_floor)
    realised_cycles = (float(np.sum(charge_mwh)) / usable) if usable > 0 else 0.0
    default_cycles = (assumptions.NA_CYCLES_PER_YEAR_REQUIREMENT if cycles_per_year is None
                      else cycles_per_year)
    effective_cycles = max(default_cycles, realised_cycles)

    hi = arbitrage_value_perfect_foresight(price_mwh, power_mw, energy_mwh, effective_cycles,
                                           round_trip_efficiency, depth_of_discharge_floor)
    if hi < lo:
        raise ValueError(
            f'perfect-foresight bound ({hi:,.0f}) below no-lookahead bound ({lo:,.0f}) at '
            f'{checkpoint_year}. The upper bound is an envelope and cannot legitimately fall below '
            'a realised dispatch -- check that both were computed on the same price series and '
            'fleet.')
    return ForesightBracket(
        lower_bound_usd=lo, upper_bound_usd=hi, checkpoint_year=checkpoint_year,
        storage_mwh=energy_mwh,
        gap_fraction=(hi - lo) / hi if hi > 0 else 0.0,
        realised_cycles_per_year=realised_cycles,
        envelope_cycles_per_year=effective_cycles,
        caveats=BRACKET_CAVEATS)
