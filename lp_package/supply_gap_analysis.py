"""
supply_gap_analysis.py

Characterises the hours where clean resources cannot meet demand, and matches each family of gaps
against the gas technology that fits it.

WHY THIS RATHER THAN PUTTING CAPEX IN THE LP

The LP sees only MARGINAL cost, where CCGT is always cheaper than CT ($47.32/MWh at 2045 against
$81.17). Without capital in the objective it builds CCGT for peaking duty a CT should serve, at
roughly twice the capital per kW. The obvious fix is to make gas a build variable -- but that
returns a single MW split, and a single number cannot say whether 7 GW should be CT or whether it
is really 3 GW of CT plus 4 GW of something else.

Characterising the gaps returns the DISTRIBUTION. And it does so without a MILP: minimum up/down
time and start cost become post-hoc tests against gap shape rather than 43,800 binary variables.

It can also find gaps that NO gas technology fits. Sixty-hour events with 15 GW ramps would be a
finding about storage duration, not about gas, and the framing would shift entirely.

THE TRAP THIS MODULE CANNOT PREVENT ON ITS OWN

Gap shape depends on what was already built. A solve with gas dispatching freely shows a different
profile than one with none, because gas smooths its own gaps. Characterising gaps from a
gas-inclusive solve measures the residual AFTER gas filled it, which says nothing about what gas was
needed for.

So the input must come from a CLEAN-ONLY solve -- clean resources, no gas, unserved energy allowed.
The unserved profile IS the gap profile. `SupplyGapProfile.from_unserved()` documents this at the
call site, and `verify_source_is_clean_only()` refuses input that looks gas-inclusive.

See Gas_Consolidated_Reference.md section 8, "Gap-driven technology matching".
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

import numpy as np

import assumptions

#: Hours in a season, indexed from the weather year's April start. Used to label events rather than
#: to compute anything, so an off-by-a-few-hours boundary does not affect results.
_SEASON_BOUNDS = ((0, 2184, 'spring-summer'), (2184, 4368, 'summer-autumn'),
                  (4368, 6552, 'autumn-winter'), (6552, 8760, 'winter-spring'))

#: A gap below this is numerical noise from the solver, not an event.
MIN_EVENT_MW = 1.0

#: Minimum interval below which a CCGT cannot cycle off and back, hours. From the sourced
#: minimum-down-time of 6 h (arXiv 2311.04398 Table D.1); below this it must idle at minimum stable
#: output rather than shutting down, which is a cost the dispatch objective does not see.
CCGT_MIN_CYCLE_INTERVAL_HR = 6.0


@dataclass(frozen=True)
class GapEvent:
    """One contiguous run of hours where clean supply fell short."""
    start_hour: int
    duration_hr: int
    peak_mw: float
    energy_mwh: float
    ramp_in_mw_per_hr: float
    ramp_out_mw_per_hr: float
    hours_since_previous: Optional[int]
    season: str

    @property
    def capacity_factor(self) -> float:
        """Utilisation of a unit sized to this event's peak, over the event only. NOT the annual
        capacity factor -- that needs all events together, which is what
        SupplyGapProfile.annual_capacity_factor() computes."""
        if self.peak_mw <= 0:
            return 0.0
        return self.energy_mwh / (self.peak_mw * self.duration_hr)


class SupplyGapProfile:
    """All gap events from one solve, with the technology matching built on them."""

    def __init__(self, events: List[GapEvent], total_hours: int = 8760):
        self.events = list(events)
        self.total_hours = total_hours

    # -- construction ------------------------------------------------------

    @classmethod
    def from_dispatchable_residual(cls, residual_mw: Sequence[float], source: str,
                                   unserved_mw: Optional[Sequence[float]] = None,
                                   min_mw: float = MIN_EVENT_MW):
        """Builds a profile from the hourly residual left after clean resources and storage.

        `source` names which column the series came from, and is REQUIRED because the same array
        means different things depending on where it was read:

            'gas_dispatch'       the gas column of a gas-inclusive solve.      VALID.
                                 In a solve where gas is the only dispatchable resource,
                                 gas[t] IS the residual after clean supply and optimal storage
                                 cycling. That is precisely the gap profile.
            'unserved_clean_only' the unserved column of a solve with NO gas.  VALID.
                                 The same residual under a different name.
            'unserved_with_gas'   the unserved column of a gas-inclusive solve. INVALID.
                                 This is a DOUBLE residual -- what gas FAILED to cover, not what
                                 gas is needed for. It is small, plausible-looking, and describes
                                 the wrong thing.

        WHY GAS DISPATCH IS PREFERRED over a purpose-built clean-only solve: with unserved
        penalised at $100,000/MWh, a clean-only solve has enormous incentive to build storage
        rather than leave gaps, distorting the very shape being measured. Gas at ~$47/MWh creates
        no such distortion, so the storage dispatch behind it is the realistic one. It also means
        every sweep point yields a gap profile with no extra solve.

        `unserved_mw` should be passed when available. If the solve left any unserved energy, the
        true gap is gas PLUS unserved, and omitting it understates the peak.
        """
        valid = {'gas_dispatch', 'unserved_clean_only'}
        if source == 'unserved_with_gas':
            raise ValueError(
                'source="unserved_with_gas" is a DOUBLE RESIDUAL -- the unserved column of a solve '
                'where gas already ran measures what gas FAILED to cover, not what gas is needed '
                'for. Pass the GAS DISPATCH column of that same solve instead, with '
                'source="gas_dispatch".')
        if source not in valid:
            raise ValueError(
                f'source must be one of {sorted(valid)} (or the rejected "unserved_with_gas"), got '
                f'{source!r}. It is required rather than defaulted because the same array means '
                'different things depending on which column it came from.')

        r = np.asarray(residual_mw, dtype=float)
        if r.ndim != 1:
            raise ValueError(f'residual_mw must be 1-D, got shape {r.shape}')
        if unserved_mw is not None:
            u = np.asarray(unserved_mw, dtype=float)
            if u.shape != r.shape:
                raise ValueError(f'unserved_mw shape {u.shape} does not match residual {r.shape}')
            if source == 'gas_dispatch' and u.sum() > 0:
                # The gap is what gas served PLUS what nothing served. Omitting the second
                # understates the peak, which is the figure the technology match turns on.
                r = r + u
        return cls._scan(r, min_mw)

    @classmethod
    def _scan(cls, r, min_mw):
        events, i, prev_end = [], 0, None
        while i < len(r):
            if r[i] < min_mw:
                i += 1
                continue
            j = i
            while j < len(r) and r[j] >= min_mw:
                j += 1
            block = r[i:j]
            before = r[i - 1] if i > 0 else 0.0
            after = r[j] if j < len(r) else 0.0
            events.append(GapEvent(
                start_hour=i,
                duration_hr=j - i,
                peak_mw=float(block.max()),
                energy_mwh=float(block.sum()),
                ramp_in_mw_per_hr=float(block[0] - before),
                ramp_out_mw_per_hr=float(block[-1] - after),
                hours_since_previous=(i - prev_end) if prev_end is not None else None,
                season=cls._season(i)))
            prev_end, i = j, j
        return cls(events, total_hours=len(r))

    @staticmethod
    def _season(hour: int) -> str:
        for lo, hi, name in _SEASON_BOUNDS:
            if lo <= hour < hi:
                return name
        return 'unknown'

    # -- guards ------------------------------------------------------------

    @staticmethod
    def source_guidance() -> str:
        """Which series to use, and why the obvious choice is wrong.

        CORRECTED 2026-09-13. An earlier version of this class required a purpose-built CLEAN-ONLY
        solve and refused any input from a solve where gas had run. That was aimed at the wrong
        thing. The failure to prevent is using the UNSERVED column of a gas-inclusive solve -- a
        double residual. Using the GAS DISPATCH column of that same solve is not merely acceptable,
        it is preferable.
        """
        return (
            'Use the GAS DISPATCH column of a solve where gas is the only dispatchable resource. '
            'In such a solve gas[t] is the residual after clean supply and optimal storage cycling, '
            'which is the gap profile by definition. A purpose-built clean-only solve is also valid '
            'but is WORSE: with unserved penalised at $100,000/MWh it has enormous incentive to '
            'build storage rather than leave gaps, distorting the shape being measured, whereas gas '
            'at ~$47/MWh creates no such distortion. Never use the UNSERVED column of a '
            'gas-inclusive solve -- that is what gas FAILED to cover, a different and much smaller '
            'quantity.')

    # -- aggregate shape ---------------------------------------------------

    def annual_capacity_factor(self, sized_to_mw: Optional[float] = None) -> float:
        """Capacity factor of a fleet sized to cover the largest gap, across the whole year.

        This is the figure that meets the CCGT/CT crossover (28.1% central -- see
        gas_lifecycle_cost.estimate_technology_crossover_cf). Sizing defaults to the largest event
        peak, which is what a fleet built to serve every gap must cover.
        """
        if not self.events:
            return 0.0
        size = sized_to_mw if sized_to_mw is not None else self.peak_mw
        if size <= 0:
            return 0.0
        return self.total_energy_mwh / (size * self.total_hours)

    @property
    def peak_mw(self) -> float:
        return max((e.peak_mw for e in self.events), default=0.0)

    @property
    def total_energy_mwh(self) -> float:
        return sum(e.energy_mwh for e in self.events)

    @property
    def total_gap_hours(self) -> int:
        return sum(e.duration_hr for e in self.events)

    # -- technology matching -----------------------------------------------

    def match_technology(self, year: int, crossover_cf: Optional[float] = None) -> Dict:
        """Which gas technology fits this gap profile, and on what grounds.

        Tests the four attributes that actually discriminate, rather than returning a bare verdict:
        annual capacity factor against the cost crossover, event duration against minimum up time,
        inter-event interval against minimum down time, and required ramp against each machine's
        rate.

        Returns a dict rather than a single answer because the attributes can disagree -- a profile
        can sit above the cost crossover while containing events too short for a CCGT to serve. A
        disagreement is a finding, not something to resolve by majority.
        """
        if not self.events:
            return {'verdict': 'no gaps', 'note': 'Clean resources met demand in every hour.'}
        if crossover_cf is None:
            from gas_lifecycle_cost import estimate_technology_crossover_cf
            crossover_cf = estimate_technology_crossover_cf(year)

        cf = self.annual_capacity_factor()
        durations = [e.duration_hr for e in self.events]
        intervals = [e.hours_since_previous for e in self.events
                     if e.hours_since_previous is not None]
        ramps = [max(abs(e.ramp_in_mw_per_hr), abs(e.ramp_out_mw_per_hr)) for e in self.events]

        ccgt_ramp = assumptions.GAS_RAMP_FRACTION_PER_HOUR['ccgt_modern'] * self.peak_mw
        too_short = sum(1 for d in durations if d < 6)          # CCGT minimum up time, hours
        too_close = sum(1 for h in intervals if h < CCGT_MIN_CYCLE_INTERVAL_HR)
        too_steep = sum(1 for r in ramps if r > ccgt_ramp)

        return {
            'events': len(self.events),
            'annual_capacity_factor': cf,
            'crossover_cf': crossover_cf,
            'cost_favours': 'CCGT' if cf > crossover_cf else 'CT',
            'median_duration_hr': float(np.median(durations)),
            'max_duration_hr': max(durations),
            'events_shorter_than_ccgt_min_up': too_short,
            'events_closer_than_ccgt_min_down': too_close,
            'events_steeper_than_ccgt_ramp': too_steep,
            'peak_mw': self.peak_mw,
            'total_energy_mwh': self.total_energy_mwh,
            'attributes_agree': (cf > crossover_cf) == (too_short == 0 and too_steep == 0),
            'note': self._verdict_note(cf, crossover_cf, too_short, too_close, too_steep,
                                       len(self.events), max(durations)),
        }

    @staticmethod
    def _verdict_note(cf, crossover, too_short, too_close, too_steep, n_events, max_dur):
        parts = [f'{n_events} gap events, annual CF {cf:.1%} against a {crossover:.1%} crossover, '
                 f'so COST favours {"CCGT" if cf > crossover else "CT"}.']
        if too_short:
            parts.append(f'{too_short} events are shorter than CCGT minimum up time (6 h), which '
                         'cost alone cannot see.')
        if too_close:
            parts.append(f'{too_close} events fall within 6 h of the previous one, so a CCGT could '
                         'not cycle off between them and would idle at minimum stable output.')
        if too_steep:
            parts.append(f'{too_steep} events need a ramp steeper than a CCGT can deliver.')
        if max_dur > 100:
            parts.append(f'The longest event runs {max_dur} h. Events of this length are a finding '
                         'about STORAGE DURATION, not about which gas turbine to build.')
        if not (too_short or too_close or too_steep):
            parts.append('No event violates a CCGT operating constraint.')
        return ' '.join(parts)

    def families(self, duration_breaks: Sequence[int] = (6, 24, 72)) -> Dict[str, List[GapEvent]]:
        """Groups events into duration families, which is where the technology answer differs.

        Breaks at 6 h (CCGT minimum up time), 24 h (a day) and 72 h (multi-day). Chosen from the
        operating parameters rather than fitted to the data, so the families mean the same thing
        across scenarios and years.
        """
        names = ['under_6h', '6_to_24h', '24_to_72h', 'over_72h']
        out = {n: [] for n in names}
        for e in self.events:
            d = e.duration_hr
            if d < duration_breaks[0]:
                out['under_6h'].append(e)
            elif d < duration_breaks[1]:
                out['6_to_24h'].append(e)
            elif d < duration_breaks[2]:
                out['24_to_72h'].append(e)
            else:
                out['over_72h'].append(e)
        return out
