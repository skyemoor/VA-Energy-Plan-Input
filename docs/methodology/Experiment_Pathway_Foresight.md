# Experiment: pathway foresight — myopic chain versus target-first

**Recorded 2026-09-12.** A methodology tension raised early in this project and never resolved,
now framed as a measurable experiment rather than a choice to argue about.

---

## The tension

**Forward / myopic.** Solve 2030 first, carry its build forward as a floor, then 2035, 2040, 2045.
Each checkpoint minimises cost for *its own* year. 2030 solves against `gas_target_share = 0.59`
and **has no knowledge that 2045 requires zero gas.**

**Target-first.** Solve 2045 first to establish the end state, then work backwards so earlier
checkpoints build toward it.

Both were argued for at the time. `solve_chain.py` implements the first — which is a choice, and
should not be made silently.

---

## Terminology

**"Backcasting"** is the right instinct, but it comes from futures studies (Robinson 1982;
Dreborg 1996): define a desirable end state, then work backwards to the policies connecting it to
the present. Often normative and qualitative.

Its quantitative cousin in capacity-expansion modelling is **perfect-foresight** or **intertemporal
optimisation**, and that is the term this literature searches on. Worth knowing when citing: a
reviewer from an energy-modelling background will expect the latter.

---

## The established taxonomy

From the European study (PMC11665420), three ways long-term goals enter a model:

| case | description | ours |
|---|---|---|
| **1** | No transition pathway modelled — optimise a **snapshot year** in which the goal is achieved | **"target-first", as a standalone 2045 solve** |
| **2** | Transition optimised under **perfect foresight** — the optimiser knows all future goals | true backcasting equivalent; not implemented |
| **3a** | **Myopic** foresight, goals imposed exogenously via an annual trajectory | **`solve_chain.py`** — our `gas_target_share` trajectory is exactly this |
| 3b | Myopic, goals imposed via a carbon price | not used |

**Our two candidates are Case 1 and Case 3a.** Case 2 — genuine intertemporal optimisation across
all four checkpoints simultaneously — is a different and much larger problem we have not built.

A fourth option exists: **rolling horizon**, where foresight spans more than one investment period
but less than the full pathway. Positioned in the literature as the realistic middle.

---

## What the literature finds

**Myopia costs money, consistently, and the magnitude is large.**

| source | finding |
|---|---|
| European system (PMC11665420) | Cumulative NPC 2050 **23% higher** under myopia (€7,495bn vs €6,106bn). Generation costs in 2050 **+59%**. Myopia *saves* €16bn (−8%) in 2024, then pays far more later. |
| UCL (Fuso-Nerini) | MY-20 and MY-10 scenarios carry **£100bn and £500bn** extra cumulative cost to 2050 |
| Sector-coupled review (S1364032123004197) | Lack of foresight raises cumulative power system costs **14%** — rising to **61%** if combined with waiting for a "low-carbon unicorn technology" |
| Indonesia net-zero (PMC12271591) | Cost discrepancies track the gap between endogenous and exogenously-imposed emissions targets |

**The mechanism is consistent:** myopic planning delays investment, then overbuilds and strands
assets. *"Not only does myopic planning lead to an overshoot of the carbon budget, but the
investment in over-capacities and stranded assets furthermore raises the cost for electricity
generation in the long run."*

### The nuance that matters most for us

> *"Intertemporal and myopic models lead to a **similar final energy system**. However, the
> **transformation pathways differ**."* — S1364032123004197

**So the 2045 build may come out similar either way. It is the path and the cumulative cost that
diverge.** That is testable here and directly determines whether this tension matters for the
whitepaper's conclusions or only for its cost figures.

---

## The experiment

Run both and compare:

**A — myopic chain.** `python3 solve_chain.py --scenario 3 --merit-order`
2030 → 2035 → 2040 → 2045, each carrying the prior build forward as a floor.

**B — target-first snapshot.** `python3 solve_checkpoint.py --year 2045 --scenario 3 --merit-order`
2045 solved standalone, no prior build. (Note this is what the script does by default, which was
itself an unintended gap — see its docstring.)

### What to compare

| metric | what a difference means |
|---|---|
| 2045 solar, storage power, storage energy | if close, the literature's "similar final system" holds here |
| **Cumulative cost across checkpoints** | the myopia penalty, directly measured |
| **Iron-air trajectory** | the specific risk — see below |
| Monotonicity | whether the chain ever wants to *shrink* a build |

### The specific risk in the myopic version

**Iron-air.** At 2030 with 59% gas allowed, there is almost no reason to build 100-hour storage. At
2045 with zero gas, it is essential. If the floor mechanism carries forward only what 2030 chose,
the chain may arrive at 2045 needing to build the **entire long-duration fleet in one checkpoint**
— expensive, and physically implausible against any real deployment rate.

That is exactly the "delay then overbuild" pattern the European study describes, and it would show
as `ironair_energy_mwh` near zero through 2040 then jumping at 2045.

---

## Which to use for the whitepaper

**Not yet decided, and the experiment should decide it.** But the prior:

**The myopic chain is the safer claim.** It is closer to how utilities actually plan — Dominion
files an IRP against a horizon, not against 2045 — and it produces a **conservative** cost estimate.
For a paper arguing VCEA targets *are achievable*, "achievable even under myopic planning, at cost
X" is stronger than "achievable if every decision from 2026 is optimal against 2045."

**The target-first snapshot is the benchmark.** It answers what the end state costs if you plan for
it, and the gap between the two **is the value of long-horizon planning** — which is itself a
finding worth reporting, and one the literature says is typically 14–23%.

**Neither is "right".** They answer different questions, and the paper should say which it prices.

---

## Related foresight questions already in this project

This is the **third** foresight problem here, and they are structurally the same:

| | question | status |
|---|---|---|
| Storage **dispatch** | LP has perfect foresight; distributed segment has none | issue #5, bracketed |
| **LDES seasonal** dispatch | perfect foresight gives "very unrealistic" patterns (arXiv 2505.12538) | recorded, unresolved |
| **Investment pathway** | this experiment | recorded here |

Worth stating in the whitepaper's methodology section as one theme rather than three scattered
caveats.

---

## Sources

- **Myopic foresight and constrained technology deployment in the European energy system**,
  PMC11665420 — the three-case taxonomy, 23% cumulative NPC penalty, stranded-asset mechanism
- **Fuso-Nerini et al.**, *Myopic decision making in energy system decarbonisation pathways*,
  UCL Discovery 1559614 — £100bn/£500bn cumulative penalties at MY-20/MY-10
- **Evaluation of sector-coupled energy systems using different foresight horizons**,
  ScienceDirect S1364032123004197 — 14% and 61% figures; the "similar final system, different
  pathway" finding
- **Impact of foresight horizons on energy system decarbonization pathways**,
  ScienceDirect S2666792425000113 — rolling horizon as the intermediate method
- **Myopic versus perfect foresight target setting for Indonesia's net zero electricity
  transition**, PMC12271591
- **Planning Strategies for Sustainable Electricity Systems Amidst Uncertainty: Yukon**,
  PMC13262050 — "dynamic myopic foresight", decisions locked in before values are revealed
- Robinson, J. (1982) and Dreborg, K. (1996) — backcasting in futures studies, for the terminology
  distinction
