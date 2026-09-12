"""
der_revenue_stack.py

What a rooftop or canopy owner actually earns from FERC Order 2222 participation, decomposed by
stream -- including the streams this model does NOT capture.

WHY A STACK RATHER THAN A NUMBER

Scenario 3's premise is that distributed owners participate in PJM wholesale markets, directly or
through a DER Aggregator, and that this participation is worth enough to drive the build. The model
currently represents that as ONE stream: energy arbitrage against distributed_exogenous_price_mwh.

That understates an owner's economics substantially, and in a way that is invisible unless the
streams are named. Reporting a single arbitrage figure invites the reader to treat it as the whole
answer. Reporting a stack with zeros in it shows what the model sees and what it does not.

THE STREAM THAT MATTERS MOST IS THE ONE LEAST MODELLED

For a C&I rooftop owner, BEHIND-THE-METER SELF-CONSUMPTION is usually the largest value stream,
because it displaces RETAIL purchase (roughly $80-120/MWh all-in for Virginia C&I) rather than
wholesale (roughly $40). The model has no retail rate and no behind-the-meter accounting, so it
sees none of it. An owner reading a wholesale-arbitrage-only figure would not recognise their own
project.

WHAT PJM ACTUALLY ALLOWS, which constrains three of these streams

From docs/research/DERA_VPP_WMA_Consolidated_Working_Notes.md:
  - the Order 2222 DER Aggregator model is NOT OPERATIONAL until February 2028 for energy and
    ancillary services, and the 2028/2029 BRA for capacity. The legacy CSP / Emergency Load
    Response path IS live and self-registrable today.
  - ENERGY-market aggregations must sit at a SINGLE PJM PRICING NODE. Capacity and ancillary
    services may aggregate across nodes; energy may not. A fleet scattered across a county cannot
    bid as one block for energy.
  - 5 MW ceiling per Component DER.

And from Va. Code § 56-594(E): aggregate net metering is capped at 6% of adjusted Virginia peak,
about 1,740 MW at 2045 -- which the measured canopy resource alone exceeds by 2.4x. That cap is why
Scenario 3 routes through wholesale participation rather than net metering at all.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional


#: Streams an owner can earn, and whether this model captures them. The point of the dataclass is
#: that an unmodelled stream reports 0.0 WITH a reason, rather than being absent from the output.
STREAM_STATUS = {
    'energy_arbitrage': (
        True,
        'Modelled: distributed dispatch against distributed_exogenous_price_mwh. Note that series '
        'is the LOCATIONAL adder (congestion + losses); the energy component reaches the segment '
        'through the LP energy balance instead.'),
    'capacity': (
        False,
        'NOT modelled. PJM capacity revenue via RPM or FRR. Requires the Order 2222 aggregator '
        'model, not operational for capacity until the 2028/2029 BRA, or participation through an '
        'existing CSP.'),
    'ancillary_services': (
        False,
        'NOT modelled. Synchronized reserve and regulation, for which batteries are structurally '
        'advantaged (instant ramp). May aggregate ACROSS nodes, unlike energy.'),
    'behind_the_meter': (
        False,
        'NOT modelled, and usually the LARGEST stream for a C&I owner. Self-consumption displaces '
        'RETAIL purchase (~$80-120/MWh Virginia C&I) rather than wholesale (~$40). The model has '
        'no retail rate and no behind-the-meter accounting.'),
    'net_metering_credit': (
        False,
        'NOT modelled, and capped regardless: Va. Code § 56-594(E) limits aggregate net metering '
        'to 6% of adjusted Virginia peak, ~1,740 MW at 2045. Measured canopy resource alone '
        'exceeds that 2.4x, which is why Scenario 3 routes through wholesale participation.'),
}


@dataclass(frozen=True)
class RevenueStack:
    """Annual revenue per kW of installed distributed capacity, by stream.

    Unmodelled streams are present at 0.0 with a reason attached. That is the design: an owner or
    reviewer must be able to see what is missing without reading the source.
    """
    year: int
    segment: str                                   # 'rooftop' or 'canopy'
    installed_mw: float
    streams_usd_per_kw_year: Dict[str, float]
    unmodelled: Dict[str, str] = field(default_factory=dict)
    caveats: tuple = ()

    @property
    def modelled_total_usd_per_kw_year(self) -> float:
        return sum(self.streams_usd_per_kw_year.values())

    def as_lines(self):
        """Rows for a report table, unmodelled streams included at zero."""
        out = []
        for name, (modelled, reason) in STREAM_STATUS.items():
            value = self.streams_usd_per_kw_year.get(name, 0.0)
            out.append((name, value, 'modelled' if modelled else 'NOT modelled', reason))
        return out


def build_stack(year, segment, installed_mw, energy_arbitrage_usd,
                extra_streams: Optional[Dict[str, float]] = None) -> RevenueStack:
    """Assembles the stack from whatever the solve produced.

    `energy_arbitrage_usd` is the only input the model can currently supply. Passing values for
    other streams is allowed -- if a later pass models capacity or ancillary revenue, it lands here
    rather than in a parallel structure -- but nothing is invented on the caller's behalf.
    """
    if installed_mw <= 0:
        raise ValueError(
            f'installed_mw must be positive, got {installed_mw!r}. A revenue-per-kW figure on zero '
            'installed capacity is undefined, not zero.')
    per_kw = {'energy_arbitrage': energy_arbitrage_usd / (installed_mw * 1000.0)}
    for name, usd in (extra_streams or {}).items():
        if name not in STREAM_STATUS:
            raise ValueError(
                f'unknown revenue stream {name!r}; known: {sorted(STREAM_STATUS)}. Add it to '
                'STREAM_STATUS with a modelled flag and a reason rather than passing it silently.')
        per_kw[name] = usd / (installed_mw * 1000.0)
    unmodelled = {n: r for n, (m, r) in STREAM_STATUS.items() if not m and n not in per_kw}
    return RevenueStack(
        year=year, segment=segment, installed_mw=installed_mw,
        streams_usd_per_kw_year=per_kw, unmodelled=unmodelled,
        caveats=(
            'Energy arbitrage rests on a price series whose scarcity component is near-constant '
            '(CV 3.99%), so it carries no multi-day lookahead value -- see foresight_bracket.py.',
            'PJM requires ENERGY-market aggregations at a SINGLE pricing node; capacity and '
            'ancillary services may aggregate across nodes. A fleet scattered across a county '
            'cannot bid as one block for energy, which this model assumes it can.',
            'The Order 2222 aggregator model is not operational until Feb 2028 (energy and '
            'ancillary) and the 2028/2029 BRA (capacity). The legacy CSP path is live today.',
            'Behind-the-meter self-consumption -- usually the largest stream for a C&I owner -- is '
            'not modelled at all, because the model has no retail rate.'))
