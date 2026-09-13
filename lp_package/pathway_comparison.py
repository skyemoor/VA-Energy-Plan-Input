"""
pathway_comparison.py

Compares a myopic checkpoint chain against a target-first snapshot, and reports the myopia penalty.

RULE 1. The orchestration -- running two pathways overnight -- belongs in a free-standing script.
The COMPARISON LOGIC does not: computing the myopia penalty, checking build deltas, and testing the
iron-air trajectory are all things a second scenario will need in the same form. They live here.

WHAT IS BEING COMPARED (see docs/methodology/Experiment_Pathway_Foresight.md)

    MYOPIC CHAIN      2030 -> 2035 -> 2040 -> 2045, each checkpoint minimising cost for its own
                      year with the prior build as a floor. 2030 solves against
                      gas_target_share = 0.59 and has no knowledge that 2045 requires zero gas.
                      Case 3a in the literature's taxonomy: myopic foresight with goals imposed
                      exogenously via an annual trajectory.

    TARGET-FIRST      2045 solved standalone, no prior build. Case 1: a snapshot year in which the
                      goal is achieved, with no pathway modelled.

WHAT THE LITERATURE PREDICTS, so the result can be read against it rather than in isolation:
  - myopia costs more, cumulatively: 23% higher NPC to 2050 (European study PMC11665420), 14% in a
    sector-coupled review, rising to 61% when combined with waiting for a breakthrough technology
  - but "intertemporal and myopic models lead to a SIMILAR FINAL ENERGY SYSTEM. However, the
    transformation pathways differ" -- so the 2045 BUILD may be close while cumulative cost diverges

THE SPECIFIC RISK THIS CLASS TESTS FOR. At 2030 with 59% gas allowed there is almost no reason to
build 100-hour storage; at 2045 with zero gas it is essential. A myopic chain may therefore arrive
at 2045 needing to build the entire long-duration fleet in one checkpoint -- expensive, and
implausible against any real deployment rate. That is the delay-then-overbuild pattern the European
study describes, and `iron_air_deferral()` looks for it directly rather than leaving it to a reader
to spot in a table.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional

#: Build variables compared across pathways. Named rather than inferred from the result dict,
#: because a key appearing in one pathway and not the other would otherwise silently drop from the
#: comparison.
COMPARED_BUILDS = ('solar_mw_total', 'na_power_mw', 'na_energy_mwh', 'ironair_energy_mwh')

#: A build difference below this is rounding, not a finding. Expressed as a fraction.
MATERIAL_DIFFERENCE_FRACTION = 0.02

#: Literature range for the cumulative myopia penalty, for reading our own result against.
#: 14% (sector-coupled review) to 23% (European system study). Not a bound -- one study reports 61%
#: when myopia is combined with waiting for a breakthrough technology.
LITERATURE_MYOPIA_PENALTY_RANGE = (0.14, 0.23)


@dataclass(frozen=True)
class BuildDelta:
    """One build variable, both pathways, and whether the difference is material."""
    name: str
    myopic: float
    target_first: float

    @property
    def absolute(self) -> float:
        return self.myopic - self.target_first

    @property
    def fraction(self) -> Optional[float]:
        """None rather than zero when the target-first value is zero -- a percentage against a zero
        base is undefined, and reporting 0.0 would read as agreement."""
        if self.target_first == 0:
            return None
        return (self.myopic - self.target_first) / self.target_first

    @property
    def is_material(self) -> bool:
        f = self.fraction
        return f is not None and abs(f) > MATERIAL_DIFFERENCE_FRACTION


class PathwayComparison:
    """Myopic chain against target-first snapshot.

    Construct from the two result sets, then read the properties. Nothing is computed in __init__
    beyond validation, so a caller can inspect a partial comparison if one pathway failed overnight.
    """

    def __init__(self, chain_checkpoints: List[Dict], target_first_2045: Dict):
        if not chain_checkpoints:
            raise ValueError(
                'chain_checkpoints is empty. A comparison needs at least the 2045 endpoint of the '
                'myopic chain; pass the checkpoints the chain completed even if it did not finish.')
        years = [c['year'] for c in chain_checkpoints]
        if years != sorted(years):
            raise ValueError(f'chain checkpoints out of order: {years}. The chain is sequential and '
                             'a later checkpoint depends on the earlier one, so order is meaningful.')
        if 2045 not in years:
            raise ValueError(
                f'chain does not reach 2045 (got {years}); there is nothing to compare the '
                'target-first snapshot against.')
        self.chain = list(chain_checkpoints)
        self.target_first = dict(target_first_2045)
        self._chain_2045 = next(c for c in self.chain if c['year'] == 2045)

    # -- build comparison at the endpoint ---------------------------------

    def build_deltas(self) -> List[BuildDelta]:
        return [BuildDelta(name=k,
                           myopic=float(self._chain_2045.get(k, 0.0)),
                           target_first=float(self.target_first.get(k, 0.0)))
                for k in COMPARED_BUILDS]

    def final_systems_agree(self) -> bool:
        """Whether the two pathways reach a similar 2045 system.

        This is the literature's own claim -- 'intertemporal and myopic models lead to a similar
        final energy system' -- tested against our own numbers rather than assumed.
        """
        return not any(d.is_material for d in self.build_deltas())

    # -- the myopia penalty -----------------------------------------------

    def cumulative_myopia_penalty(self, chain_cost_key='annual_cost_usd',
                                  target_cost_key='annual_cost_usd') -> Optional[float]:
        """Fractional cost penalty of the myopic pathway at 2045, or None if costs are absent.

        Returns None rather than 0.0 when either pathway lacks a cost figure: a missing cost is not
        a zero penalty, and reporting one would be worse than reporting nothing (Rule 5).

        NOTE this compares 2045 ANNUAL cost, not cumulative net present cost across the pathway.
        The literature's 14-23% figures are cumulative NPC and are NOT directly comparable. A true
        cumulative comparison needs a discount rate and per-checkpoint costs the chain does not yet
        emit; until then this is a weaker, endpoint-only proxy and should be labelled as one.
        """
        a = self._chain_2045.get(chain_cost_key)
        b = self.target_first.get(target_cost_key)
        if a is None or b is None or not b:
            return None
        return (float(a) - float(b)) / float(b)

    def penalty_against_literature(self) -> str:
        """Reads our own penalty against the published range, or says why it cannot."""
        p = self.cumulative_myopia_penalty()
        if p is None:
            return ('Cost penalty not computable: one or both pathways emitted no cost figure. '
                    'Note that even when available, this is an endpoint annual-cost proxy, not the '
                    'cumulative NPC the literature reports.')
        lo, hi = LITERATURE_MYOPIA_PENALTY_RANGE
        if p < 0:
            return (f'Myopic pathway is CHEAPER at 2045 by {abs(p):.1%}. That inverts the '
                    'literature and warrants checking before it is reported -- the usual cause is '
                    'the two pathways not solving the same problem.')
        where = 'below' if p < lo else ('within' if p <= hi else 'above')
        return (f'Myopia penalty {p:.1%} at 2045 (annual-cost proxy), {where} the published '
                f'cumulative-NPC range of {lo:.0%}-{hi:.0%}. Not directly comparable -- ours is an '
                'endpoint annual figure, theirs is cumulative and discounted.')

    # -- the specific risk -------------------------------------------------

    def iron_air_deferral(self) -> Dict:
        """Tests whether the myopic chain defers long-duration storage and then builds it late.

        At 2030 with 59% gas allowed there is little reason to build 100-hour storage; at 2045 with
        zero gas it is essential. A chain that arrives at 2045 needing the whole long-duration fleet
        in one checkpoint is the delay-then-overbuild pattern the European study describes, and it
        is implausible against any real deployment rate.
        """
        series = [(c['year'], float(c.get('ironair_energy_mwh', 0.0))) for c in self.chain]
        final = series[-1][1]
        if final <= 0:
            return {'deferred': False, 'series': series,
                    'note': 'No iron-air built in any checkpoint; deferral is not the question here.'}
        pre_2045 = [v for y, v in series if y < 2045]
        largest_before = max(pre_2045) if pre_2045 else 0.0
        share_in_final = (final - largest_before) / final
        return {
            'deferred': share_in_final > 0.5,
            'series': series,
            'share_built_in_final_checkpoint': share_in_final,
            'note': (
                f'{share_in_final:.0%} of the 2045 iron-air fleet appears in the final checkpoint. '
                + ('That is the delay-then-overbuild pattern: the chain had little reason to build '
                   '100-hour storage while gas was still allowed, and must build it all at once '
                   'when gas goes to zero. Check this against any credible deployment rate before '
                   'treating the pathway as feasible.'
                   if share_in_final > 0.5 else
                   'Long-duration build is spread across checkpoints rather than deferred.')),
        }

    # -- reporting ---------------------------------------------------------

    def summary(self) -> Dict:
        deltas = self.build_deltas()
        return {
            'final_systems_agree': self.final_systems_agree(),
            'build_deltas': [
                {'name': d.name, 'myopic': d.myopic, 'target_first': d.target_first,
                 'absolute': d.absolute, 'fraction': d.fraction, 'material': d.is_material}
                for d in deltas],
            'myopia_penalty_fraction': self.cumulative_myopia_penalty(),
            'penalty_reading': self.penalty_against_literature(),
            'iron_air': self.iron_air_deferral(),
            'caveats': (
                'The myopia penalty here is an ENDPOINT ANNUAL cost comparison. The literature\'s '
                '14-23% figures are CUMULATIVE NET PRESENT COST across the whole pathway and are '
                'not directly comparable.',
                'Target-first is solved as a standalone 2045 snapshot (Case 1), not as a '
                'perfect-foresight transition (Case 2). Case 2 is the true backcasting equivalent '
                'and is not implemented.',
                'A similar final system with differing pathways is the literature\'s own expected '
                'result, not evidence that the pathway choice does not matter.'),
        }
