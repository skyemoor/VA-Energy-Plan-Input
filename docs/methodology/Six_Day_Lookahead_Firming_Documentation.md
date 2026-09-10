# Lookahead-Window Firming Analysis — Full Documentation

*Compiled 2026-09-05. Covers the true 4-county rooftop+canopy fleet (6,159.0 MW),
Sterling+Arlington insolation averaged, two rooftop tilt configurations, and three
lookahead windows (1-day, 3-day, 6-day) — organized around the framework below, which
this set of runs itself surfaced as the right lens for interpreting them.*

## 1. The framework — three distinctions this set of runs revealed are easy to
conflate, and shouldn't be

**Market clearing cadence is not the same thing as a participant's own planning
horizon.** PJM's day-ahead market clears one day at a time — bids close ~11am,
results publish by ~1:30pm, for the following day's 24-hour schedule. But nothing
about that daily clearing cadence limits how far ahead a real market participant
looks when *deciding* what to offer into that market. A sophisticated operator
running a large storage fleet can and would consult a multi-day weather outlook when
deciding how much to withhold today in anticipation of a tighter, higher-value day
later this week — even though the actual transaction still clears one day at a time.
Conflating "PJM clears daily" with "a realistic PJM participant only plans one day
ahead" understates what real operators do. A 1-day lookahead model is not, on its
own, "the PJM-realistic case" — it specifically models a fully myopic participant who
never looks past tomorrow even in their own internal planning, which is a narrower
and less representative claim than it first appears.

**Perfect foresight is not the same thing as real forecast skill.** Every result in
this document is computed retrospectively against real, already-known historical
solar output — the algorithm "sees" the coming lookahead window with certainty,
because it is being run after the fact against data that already happened. A real
operator using an actual multi-day weather forecast faces genuine forecast error,
which grows with the length of the horizon (a 6-day-ahead forecast is meaningfully
less reliable than tomorrow's). This means every multi-day result below is a
**ceiling** — the best any firming strategy could achieve with perfect information —
not a claim about what a real forecast-based strategy would deliver in practice. The
gap between this ceiling and real-world achievable performance depends on forecast
skill this project's own methodology deliberately does not model.

**Reliability-optimization and price-arbitrage are related but distinct objectives.**
This project's own method optimizes for the highest *guaranteed physical delivery*
level across the worst day in the historical record — a reliability question,
answered independent of price. A profit-driven operator instead withholds capacity
specifically when a multi-day price forecast suggests an upcoming spike, in order to
sell into that spike. The two objectives often point the same direction, since tight
supply (low solar) and high prices are frequently correlated — but not always: prices
can spike for reasons unrelated to solar output (outages elsewhere, demand surges),
and a pure arbitrageur's withholding decisions would not always match what a
reliability-focused operator would choose to hold in reserve. The numbers in this
document answer the reliability question specifically — a firm-capacity ceiling, not
a revenue-optimal bidding strategy's own result.

**Why this framework matters for reading the results below**: it reframes the 1-day
result from "the realistic PJM-aligned finding" to "the floor a purely myopic
operator would deliver" — and reframes the 3-day/6-day results from "less
market-realistic but more sophisticated" to "a closer model of what a real,
multi-day-planning operator's own ceiling looks like," even though the market itself
still clears daily underneath that planning.

## 2. This project's own method — explanation

**What it is**: a deterministic, retrospective (not forward-forecasting)
optimization. Run against real, already-known historical solar output (2012-2020,
real NSRDB-derived generation), it answers: *given the actual solar output that
occurred, what is the best possible battery charge/discharge schedule, chosen with
perfect foresight of the coming lookahead window, and what is the resulting
worst-case day across the full historical record?*

**Algorithm, step by step**:
1. For each of the two storage duration classes (short: 10-hr sodium-ion, 90% RTE;
   long: 100-hr iron-air, 80% RTE), and for a grid of possible MW splits between them
   (0% to 100% short-duration share, in 5% increments):
2. For each day in the 9-year record (3,277-3,285 real days depending on data-gap
   handling), look ahead `lookahead_hours` from that day's start.
3. Solve for the highest FLAT power level the battery can sustain for that entire
   day, given: the real solar generation known over the lookahead window, the
   battery's own power/energy capacity, its round-trip efficiency, and its starting
   state of charge.
4. Chain days together: each day's ending state of charge becomes the next day's
   starting state of charge (not reset to 100% each day) — this is what lets the
   algorithm "save" charge across a multi-day low-solar stretch it can see coming in
   its lookahead window.
5. Record that day's achievable flat level as the "daily firm level" for that
   short/long split.
6. Across all days, take the MINIMUM daily firm level — the worst day in the entire
   9-year record, for that split.
7. Across all splits in the grid, find the split that MAXIMIZES this worst-day
   minimum — the split giving the highest guaranteed floor.

**Formula** — per-day flat level solve: for a given day with starting state-of-charge
`SoC_0`, real hourly solar generation `solar[h]` for h = 0...`lookahead_hours`-1,
battery power capacity `P_batt`, energy capacity `E_batt`, and round-trip efficiency
`RTE`, find the maximum flat level `L` such that a feasible charge/discharge schedule
exists satisfying, for every hour h in the lookahead window:

```
SoC[h+1] = SoC[h] + (charge[h] * sqrt(RTE) - discharge[h] / sqrt(RTE)) / E_batt
0 <= SoC[h] <= 1                              (state of charge stays in bounds)
solar[h] + discharge[h] - charge[h] = L        (net delivery holds flat at L every hour)
0 <= charge[h] <= P_batt,  0 <= discharge[h] <= P_batt
```

Chained multi-day linkage: `SoC_0` for day `d+1` = `SoC[end]` from day `d`'s own
solve — not reset — the mechanism that lets the algorithm bank charge ahead of an
approaching low-solar stretch its lookahead window can already see.

```
best_split = argmax over split s in {0%, 5%, ..., 100%} of:
    min over all real days d of:
        firm_level_short(d, s * total_MW) + firm_level_long(d, (1-s) * total_MW)
```

**Citation**: the generic "multi-day solar lookahead firming algorithm" explainer
(uploaded 2026-09-05, no formal citation) describes the general MPC/rolling-horizon
concept this project's own method shares in spirit (re-optimize at each new day,
weather-uncertainty buffering to avoid "midnight blindness"), though this project's
own implementation is a full-record, perfect-foresight grid search rather than a true
rolling MPC controller reacting to evolving forecasts in real time.

## 3. Results, read through the framework above

**Fleet** (all three lookahead windows): true 4-county combined total, 6,159.0 MW
(rooftop 2,202.4 MW [C&I + schools, all four counties], canopy 3,956.6 MW [low end of
the established 3,956.6-4,945.8 MW range]). Insolation: Sterling + Arlington,
averaged by real timestamp. Canopy fixed at 15° throughout (not tilt-adjustable). 9
real historical years (2012-2020).

| Rooftop tilt | Lookahead | What this models, per the framework | Worst-day firm level (MW) | Optimal split |
|---|---|---|---:|---|
| 39° (latitude) | 1-day | A fully myopic operator, no multi-day planning at all | **0.00** | undefined (flat across all splits) |
| 39° (latitude) | 3-day | A perfect-foresight ceiling for a 3-day-planning operator | 159.77 | 100% short-duration |
| 39° (latitude) | 6-day | A perfect-foresight ceiling for a 6-day-planning operator | 265.42 | 100% short-duration |
| 45° | 1-day | A fully myopic operator, no multi-day planning at all | **0.00** | undefined (flat across all splits) |
| 45° | 3-day | A perfect-foresight ceiling for a 3-day-planning operator | 160.90 | 100% short-duration |
| 45° | 6-day | A perfect-foresight ceiling for a 6-day-planning operator | 266.72 | 100% short-duration |

**MWh/yr** (same across all lookahead windows, since annual energy doesn't depend on
how far ahead the firming algorithm looks): 39° latitude-tilt rooftop = 7,945,892
MWh/yr; 45° rooftop = 7,895,667 MWh/yr (-0.63% relative to the annual-optimal
latitude-tilt angle).

**The 1-day result, investigated directly rather than accepted as a bare number**:
checked the full daily series before treating this as final — 820 of 3,285 days
(~25%, concentrated in winter months) hit exactly zero or near-zero. The cause is
structural: with only 24 hours of foresight, each day's dispatch decision is
optimized in complete isolation, with no visibility into tomorrow, so the algorithm
routinely drains the battery whenever that is optimal for maximizing *today's own*
flat level — and when a severe day then arrives with the battery already drained,
there is nothing left to draw on. A minimum-reserve-SoC floor was tested directly as
a candidate fix (20%, confirmed working correctly in isolation via a direct unit
test) and found not to genuinely solve this: it only relocates what "depleted" means,
reducing the zero-day count merely from 820 to 808, since a per-day-isolated
optimizer still has no incentive to preserve any margin beyond whatever floor exists.
This is expected to persist at any fixed floor below 100%, for the same structural
reason — not a value-tuning problem. **Accepted, under these particular
circumstances, as the real, final finding for this lookahead horizon**: a genuine,
dependable, nonzero firm-capacity floor is not achievable at a 1-day, fully-myopic
planning horizon for this fleet, given the real 9-year weather record. Per the
framework in Section 1, this is best read as the floor a purely myopic operator
delivers — not as "the PJM-realistic answer" — since a real PJM participant's own
internal planning is not constrained to match the market's own daily clearing
cadence.

**The tilt difference is consistently small across every lookahead window that
produces a nonzero result**: +1.13 MW (~0.7%) at 3-day, +1.30 MW (~0.5%) at 6-day.
45° trades a small amount of annual energy for a similarly small reliability-floor
gain — not a clearly one-sided choice on this evidence.

## 4. Implications for the whitepaper — what these numbers can and cannot support

- **Do not present the 1-day result as "the PJM-market-realistic firm-capacity
  figure."** Per the market-cadence-vs-planning-horizon distinction (Section 1), it
  specifically represents a fully myopic operator, not a realistic model of how a
  sophisticated participant would actually plan around a market that happens to clear
  daily.
- **Present the 3-day and 6-day results as perfect-foresight ceilings**, not as
  claims about real-world-achievable firm capacity. The true, real-world-achievable
  figure sits somewhere between the 1-day floor (0 MW) and these ceilings, with the
  gap determined by real forecast skill at each horizon — a question this project's
  own methodology deliberately does not answer.
- **Do not present these figures as a price-arbitrage or revenue-optimization
  result.** They answer a specific, different question — the highest guaranteed
  physical delivery level, independent of price — which a profit-maximizing
  operator's own real bidding behavior would not exactly reproduce, even though the
  two objectives are related and often point the same direction.
- **The transmission-reduction implication should be stated with these bounds
  attached**: this fleet's own solar+storage resource can support a dependable firm
  MW level, for planning purposes, somewhere in the range this analysis establishes
  (0 MW at the fully-myopic floor, up to ~160-267 MW at the perfect-foresight,
  multi-day-planning ceiling depending on lookahead length and rooftop tilt) — not a
  single, precise number independent of these framing choices.
