# Appendix Q — Gas Capacity Expansion: Method, Formulas and Presentation

**Established 2026-09-14.** How this analysis decides what gas capacity a scenario needs, what it
costs, and — equally important — **what weight the resulting numbers can carry**.

---

## Q.1 What kind of analysis this is

This is a **brownfield screening curve model**. That is a recognised class of method with a
forty-year literature, not an invention of this project, and it is worth naming precisely because
naming it also fixes what it can and cannot support.

Güner (2018) states the boundary plainly: the screening curve method is *"preferred to be utilized
during the preliminary investigation of the capacity expansion planning studies to narrow down the
technology alternatives for detailed analysis,"* and its solutions are *"guidelines for a detailed
analysis."*

**This analysis accepts that framing.** It produces screening-level results, presented as such.

### The four generations

| generation | adds | source |
|---|---|---|
| **Type 1** — classical (TCSCM) | annual cost curves against a load duration curve | EGEAS, early 1980s |
| **Type 2** | start-up cost via a **chronological** net load curve | — |
| **Type 3** — enhanced | unit commitment constraints | Batlle & Rodilla (2013) |
| **further improved** | detailed thermal cycling | Zhang et al. (2015) |
| **brownfield** | **existing units alongside candidates** | Güner (2018) |

**This analysis sits at Type 3, brownfield.** Chronological because run length is what distinguishes
combined-cycle duty from peaking duty; brownfield because Virginia has an existing gas fleet and the
question is what to add to it, not what to build from nothing.

### Why a load duration curve is not sufficient

Sorting hours by output collapses the time dimension. A tranche needed for one long winter block and
a tranche needed for forty scattered summer afternoons are **identical on a duration curve** and
require entirely different plant. Type 2 exists precisely because *"a chronological net load curve
was included for calculating annual start-up cost."*

Measured on Scenario 2's 2045 profile, the median run length of contiguous blocks falls from
**18 hours** at the fleet ceiling to **3 hours** at 19,000 MW and **1 hour** at 21,000 MW. The
duration curve shows none of that.

---

## Q.2 The cost formulation

Batlle & Rodilla's screening curve gives the total annual cost of serving a loading point *lp* with
technology *i*:

```
TC_i(lp)  =  CC_i  +  EFC_i(lp)  +  SFC_i(lp)  +  OMC_i(lp)
```

| term | what it is |
|---|---|
| **CC** | annualised capital cost, capex × capital recovery factor, plus fixed O&M |
| **EFC** | energy fuel cost |
| **SFC** | **start-up fuel cost** |
| **OMC** | operating and maintenance, **driven by the maintenance interval** |

### EFC — fuel, from the merit order

The residual is loaded onto the merit-order stack cheapest rung first. Each rung has its own heat
rate, so **the fuel burned depends on how much is being asked for in that hour**:

```
MMBtu(t)  =  Σ_rungs  MW_rung(t) × HR_rung
```

and the system cost of energy in that hour is

```
$/MWh(t)  =  MMBtu(t) × fuel_price  /  MWh_served(t)
```

**This is the price signal.** Not a market price and not a modelled dual — the fuel actually burned,
divided by the energy actually served. It is what storage responds to, because storage in this
model does not earn a market price; it displaces fuel.

*Measured, Scenario 2 at 2045:* loading 132.1 TWh of gas onto the stack burns **1,153 million MMBtu**
— an effective heat rate of **8.73**, against the **6.40** a single-rung model assumes. At
$6.92/MMBtu that is **$60.47/MWh against $44.32**, understating fuel by **$16.15/MWh**.

### SFC — start fuel

```
SFC(lp)  =  starts(lp) × start_MMBtu_i × fuel_price
```

Start fuel is **1,000 MMBtu** for a combined-cycle unit against **350** for an open-cycle turbine,
cross-checked against $67,000 and $13,400 per start (arXiv 2311.04398) — roughly a 5× ratio either
way. Starts per tranche come directly from the chronological block count.

### OMC — the maintenance interval function

**This is the dominant cycling cost, and the one most often omitted.** Batlle & Rodilla are explicit:
*"when compared with the start fuel costs, it is evident that these O&M costs have a considerably
higher relevance."* At one loading point their traditional estimate gives **13 k$/MW** against
LEEMA's **31 k$/MW** — a factor of 2.4.

A gas turbine's major inspection is triggered by a **combination** of firing hours and starts, not
either alone. GE's published Maintenance Interval Function spans **8,000–24,000 firing hours and
400–900 starts** (Balevic et al. 2010); Batlle & Rodilla adopt the 600 starts / 24,000 hours
pairing, as does this analysis.

Define the **cycling ratio**:

```
ρ(lp)  =  firing_hours(lp) / starts(lp)
```

Annual variable O&M is then the fraction of an overhaul consumed:

```
OMC(lp)  =  ( F(lp) / F*(ρ) ) × major_overhaul_cost
```

where `F*(ρ)` is the firing-hour allowance read off the MIF at that cycling ratio.

**A larger number of starts does not imply a larger O&M cost.** Batlle & Rodilla's peaking unit
starts 25 times over 108 firing hours — ratio 4.3, high O&M. Their mid-merit unit starts 160 times
over roughly 2,900 hours — ratio 18, lower O&M. **It is the ratio that drives the interval.**

Major overhaul cost: $20M–60M in their range, $40M for a 540 MW combined-cycle unit — carried here
as **$74,074/MW** so it scales with the fitted build.

### Feasibility, not cost, for impossible duty

Batlle & Rodilla set an infeasible profile to infinite cost rather than pricing it: *"if the
production profile turns out to be unfeasible for a certain technology (for example, for involving
exceeding the maximum number of annual starts) then the associated cost of supplying that
production profile with that technology is set to infinite."*

Two filters apply before any cost is computed:

● **Minimum up time.** A tranche whose blocks are typically shorter than a combined-cycle unit's
  six-hour minimum cannot be served by one without running it past the need.
● **Maximum annual starts**, by technology.

**This respects commitment physics without modelling unit commitment.** Blocks assigned to
combined-cycle plant are long enough that its up-time constraint would not bind; blocks assigned to
turbines are within their one-hour minimum. The assignment honours the constraint rather than a
binary variable enforcing it.

---

## Q.3 Existing units enter at zero fixed cost

Güner's brownfield contribution: *"the existing units are modeled to have **no fixed costs** (i.e.
sunk fixed costs). Indeed, the existing units possess **shadow prices** of their capacity values
which can be considered as their fixed costs."*

So an existing unit's screening curve has a **zero intercept** — variable cost only — and the
decision becomes what Güner states directly:

> *"a tradeoff between incurring investment costs by commissioning candidate units **or** taking
> online existing units with relatively higher variable costs compared to the candidate units."*

**That is exactly this analysis's question.** Virginia's surviving gas fleet is sunk capital. The
question is how much new build is worth commissioning rather than running that fleet harder.

### The build test

A new combined-cycle unit lowers system cost when it displaces higher-heat-rate operation for
enough hours to recover its annualised fixed cost:

```
break_even_hours  =  ( capex × CRF  +  FOM )  /  ( (HR_displaced − HR_new) × fuel_price )
```

*Worked at 2045, fuel $6.92/MMBtu, displacing an 11.00 heat rate with 6.40 — a saving of
$31.85/MWh:*

| capex case | $/kW | annualised $/MW-yr | break-even | capacity factor |
|---|---:|---:|---:|---:|
| low | 2,000 | 152,630 | 4,791 h | 54.7% |
| central | 2,500 | 186,350 | 5,850 h | 66.8% |
| high | 3,200 | 233,558 | 7,332 h | 83.7% |

Against a measured **7,504 hours** on the turbine rung at 2045, the test clears in all three cases —
comfortably at low capex, marginally at high.

**This figure counts fuel only and is therefore conservative.** Adding SFC and OMC makes peaking
plant worse, since it cycles far more, so the true saving exceeds $31.85/MWh and the break-even
falls.

---

## Q.3a Worked result — Scenario 2's 2045 capacity gap

Applying the method end to end, with the merit-order stack inside the solve.

### The gap, measured rather than inferred

With gas bounded by the real fleet (12,216 MW available at 2045) rather than an unbounded ceiling,
Scenario 2 leaves **17.96 TWh unserved over 3,294 hours**, peaking at **10,263 MW**.

**And storage begins working.** Sodium-ion discharges **13.04 TWh over 2,666 hours**, where the
flat-price unbounded model had it at exactly zero in every hour of the year. Not arbitrage —
**scarcity**: with gas capped, the alternative to discharging is unserved energy at the penalty
price, so storage runs whenever it holds charge.

That revises an earlier finding. Scenario 2's storage is not idle because the mandate is mismatched;
it is working hard **and still leaving 17.96 TWh unserved**. The mandate is insufficient, which is a
different and stronger claim.

### The gap is peaking duty, uniformly

| level | hours | blocks | median run |
|---|---:|---:|---:|
| 1 MW | 3,294 | 1,233 | **2.0 h** |
| 3,000 MW | 2,860 | 1,100 | 2.0 h |
| 5,000 MW | 2,307 | 950 | 2.0 h |
| 7,000 MW | 671 | 332 | 1.0 h |

**1,233 separate blocks, median 2 hours, longest 27.** Nothing clears a combined-cycle unit's
six-hour minimum uptime, at any level.

*An earlier fit on the UNBOUNDED gas series had given 10,500 MW of combined-cycle plant, because
that series was flat baseload running 18-hour blocks. It described what gas served in total, not
what capacity was missing — the wrong requirement.*

### Full cost comparison

Duty cycle: **1,233 starts, 3,294 firing hours**, cycling ratio **2.67** against the maintenance
interval's reference 40 — fifteen times more cycling-intensive. Implied capacity factor **20.0%**.

| | CC | EFC | SFC | OMC | **total** |
|---|---:|---:|---:|---:|---:|
| **CT, large frame** | $937M | $1,368M | $31M | **$1,303M** | **$3,639M** |
| **CCGT** | $2,258M | $796M | $88M | **$1,862M** | **$5,004M** |

**Combustion turbine by $1,365M/yr — 27%.**

**Maintenance dominates start fuel by a factor of 42** ($1,303M against $31M for the turbine case),
which is Batlle & Rodilla's central finding reproduced on this project's own data.

### The conclusion is over-determined

The turbine wins on **every** term that varies:

● **capital** — $1,250/kW against $3,000/kW
● **maintenance** — smaller overhaul scope
● **capacity factor** — 20.0%, well below the 28.1% crossover this project carries
● **duty shape** — median two-hour blocks against a six-hour minimum uptime

Only fuel favours combined cycle, and at a 20% capacity factor there are not enough hours to earn
it. **No single assumption is load-bearing**: the result survives reversing the simple-cycle
overhaul ratio to parity.

### Two capex figures that were conflated

Recorded because the constant names give no hint which is operative.

● **`ccgt_capex_kw(year)` is the model's CCGT capex** — year-varying, Wood Mackenzie April 2026,
  **$3,000/kW** at the build year, and what the import banner prints.
  `CCGT_CAPEX_KW_BY_CASE['central'] = $2,500` is the sensitivity band's midpoint and **does not
  match**. Using it understated combined cycle by 20%, and so understated the turbine's advantage
  by roughly $350M/yr.
● **`SCENARIO_1B_NEW_CT_CAPEX_KW = $2,000/kW` is not a benchmark** — it is the midpoint of a
  $1,200–3,000 sweep, chosen because Scenario 1B's capacity answer proved insensitive across the
  range, and it prices a 1,278 MW build. **`PEAKER_CAPEX_KW_BY_TIER` is the benchmark**, pricing a
  large build at $1,250/kW. The two answer different questions.

---

## Q.4 Static per year, chained — and what that costs

Güner distinguishes the two approaches: *"A **static** capacity expansion model is utilized for the
analysis of energy mix in a **target year**, whereas a **dynamic** model is utilized for a planning
horizon of 2–50 years by which an expansion problem is solved **simultaneously across all time
periods**."*

Batlle & Rodilla's formulation is static. This analysis applies it **per year and chains forward**,
carrying a running maximum: capacity persists, so nothing already built is unbuilt, and the year a
tranche first appears is the year it is built.

**Static-per-year is myopic by construction**, and this project already measures what myopia costs
through its perfect-foresight comparison. That comparison is the honest treatment: rather than
asserting that per-year chaining approximates simultaneous optimisation, it computes the gap.

### What foresight would change, and why the answer is not obvious

The naive expectation is that foresight builds combined-cycle plant earlier — a unit built in 2030
earns its fuel saving for fifteen years rather than ten.

**But early combined-cycle plant runs in short blocks**, which is exactly the duty that consumes a
maintenance interval fastest. Batlle & Rodilla found that accounting for cycling *"favors the
installation of the more flexible technologies."*

So foresight faces a genuine trade-off: **earlier combined-cycle capacity buys fifteen years of fuel
savings and pays cycling damage in the early ones.** Whether that nets positive is an empirical
question this method can answer and intuition cannot.

---

## Q.5 What this method does not support, stated plainly

A senior energy modeller reviewing this approach would accept the structure and press on five
points. All five are recorded here rather than left to be discovered.

● **Repricing a dispatch optimised under different prices is circular.** Loading an existing gas
  series onto a multi-rung stack after the fact gives a fuel figure the original solve would never
  have produced — higher marginal cost changes the gas-versus-curtailment trade and everything
  downstream. **The stack must be inside the solve.** Figures produced by post-hoc loading are
  indicative of magnitude and direction only.
● **Effective load carrying capability at a single point overstates a large block.** PJM's marginal
  ELCC declines with penetration — that is the purpose of the accreditation reform — so applying a
  marginal value to 16,000 MW of storage flatters it. The ELCC curve is needed, not a point.
● **A deterministic reserve margin is not a loss-of-load calculation.** A 17.7% installed margin is
  a proxy for an LOLE study with forced outage rates, not a substitute for one.
● **Continuous megawatts are not turbines.** Scenario 1B already demonstrates the gap: 1,278 MW
  continuous against 1,422 MW as six F-class units — a 144 MW overshoot that discreteness forces.
● **Part-load operation is not represented.** A combined-cycle unit at minimum stable load burns
  well above its rated heat rate, and Batlle & Rodilla's own heuristic keeps units at roughly 40%
  output through valleys to avoid a start. Both raise off-peak cost, so **the modelled price spread
  is an upper bound**.

**What a reviewer would accept:** that this is screening-level analysis, correctly identified as
such, indicating which alternatives warrant detailed production-cost modelling.

**Production cost modelling is a separate tool at a later stage**, not an earlier one. It answers
*"given this fleet, what does it cost to operate hour by hour"* — it does not decide what to build.
The conventional sequence is screening, then capacity expansion, then production-cost validation,
iterating if validation fails. A procurement decision would require that validation. This analysis
informs the question put to those models; it does not replace them.

---

## Q.6 How the results are presented, and why

The limitations above bind on **absolute levels**, not on **comparisons**. This governs presentation.

### Every scenario shares the method

Same weather years, same demand projection, same cost assumptions, same solver, same formulation.
**The only thing that varies is the policy constraint.** That is a controlled experiment: a bias
that inflates one scenario's cost inflates the others by roughly the same amount, so the **shape**
of the relationship survives even where the **height** is uncertain.

### Therefore

● **Lead with the curve**, not a number. The primary output is annualised cost against compliance
  level from 30% to 100%, with Scenario 2 plotted as a point on it. A curve is inherently a
  comparison and answers *"what does the statutory minimum buy, and what would more buy"* without
  requiring any single level to be defensible in isolation.
● **Report levels in a table beneath it**, with the screening-level caveat attached **once** rather
  than hedged at every figure. Hedging every number reads as a lack of confidence in all of them;
  stating the caveat once and clearly reads as knowing what the method is.
● **Make comparative claims where the method is strongest.** "Reaching 95% compliance costs X% more
  than the statutory minimum" is supported. "The statutory minimum costs $32.80/MWh" is supported
  less well, and a reviewer will say so.
● **State that a procurement decision requires production-cost validation.** Not as a disclaimer but
  as a description of where this work sits in a sequence that ends elsewhere.

**None of this changes the modelling.** The same numbers are produced; the weight placed on them
differs.

---

## Q.7 Sources

● **Batlle, C. and Rodilla, P. (2013).** An enhanced screening curves method for considering
  thermal cycling operation costs in generation expansion planning. *IEEE Transactions on Power
  Systems* 28(4). Instituto de Investigación Tecnológica, Comillas.
● **Güner, Y. E. (2018).** The improved screening curve method regarding existing units. *European
  Journal of Operational Research* 264(1), 310–326. DOI 10.1016/j.ejor.2017.06.007.
● **Zhang, T., Baldick, R. and Deetjen, T. (2015).** Optimized generation capacity expansion using a
  further improved screening curve method. *Electric Power Systems Research*.
● **Zhang, T. and Baldick, R. (2017).** Consideration of start-up costs and existing-unit retirement
  on a chronological load profile.
● **Balevic, D. et al. (2010).** Heavy-duty gas turbine operating and maintenance considerations.
  GE Energy. Source of the maintenance interval function.
● **Liu, Y. et al. (2020).** The economics of peaking power resources in China: screening curve
  analysis and policy implications. *Resources, Conservation and Recycling* 158. Extends the
  candidate set to demand response and storage, finding that for peak gaps of 50–100 hours
  *"the most economical choice is demand response or energy storage"* rather than any thermal plant.
● **Gillich, A. et al. (2020).** *Energy Policy* 147. Uses the term "brownfield screening curves
  model" and applies it to coal phase-out cost redistribution.
● **arXiv 2311.04398.** Start-cost cross-check, $67,000 combined-cycle against $13,400 open-cycle.
