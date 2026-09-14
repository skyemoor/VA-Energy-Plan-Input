## Appendix M — Reference Literature (new this session)

*(External sources gathered to inform this project's methodology, distinct
from the C001-C059 dataset/assumption citations tracked separately in
`build_citations.py`. Added as a standing, updatable list per project
decision to maintain a shared record of what's been consulted.)*

### M.1 Integrated Resource Planning Practice

**Biewald, B., Glick, D., Kwok, S. et al. (2024).** *Best Practices in
Integrated Resource Planning: A guide for planners developing the
electricity resource mix of the future.* Synapse Energy Economics /
Lawrence Berkeley National Laboratory. https://escholarship.org/uc/item/8x83n1jf

Directly relevant to this project's core storage strategy. Best Practice 17
("Model battery energy storage options") explicitly validates a
dual short/long-duration approach, citing iron-air by name as a
cost-effective option for longer-duration back-up and reserves distinct
from short-duration lithium-ion's role -- independent confirmation of this
project's Na-ion/iron-air split, not merely a coincidental parallel. Also
useful for Best Practice 18 (consistent treatment of emerging technologies)
as a disclosure-and-transparency standard this project's own approach
(disclosed simplifications throughout) already aligns with.

### M.2 Solver Documentation

**HiGHS Documentation — Feasibility and Optimality.**
https://ergo-code.github.io/HiGHS/stable/guide/kkt/

Directly explains the KKT feasibility/optimality machinery this project
used to verify true LP optimality at a simultaneous-dispatch hour (Internal
Debugging Log #20, MILP trial context). Also directly relevant to two
earlier, separately-diagnosed issues this session: the "HiGHS solutions"
section explicitly describes how a large objective coefficient paired with
a near-zero reduced cost can mask genuine non-optimality behind a reported
"optimal" status -- the exact failure mode this project found and fixed via
the BUILD_SCALE correction, now independently confirmed as a known,
documented HiGHS behavior rather than a project-specific quirk.

### M.3 Broader Modeling Challenges

**Anderson, E., Ferris, M., Philpott, A. et al. (2025).** "Ten challenges
for mathematical modeling of the green-energy transition." *Current
Sustainable/Renewable Energy Reports*, 12, 26.
https://doi.org/10.1007/s40518-025-00274-9

Challenge 1 explicitly frames the curtailment/storage-capacity tradeoff
this project investigated at length (Internal Debugging Log #16/#18/#20)
as a recognized, general modeling challenge, not an isolated bug hunt.
Challenge 10 (computation and validation for large models) is directly
relevant to this project's own MILP-tractability finding (#20.1).

**Korovushkin, V., Boichenko, S., Artyukhov, A. et al. (2025).** "Modern
Optimization Technologies in Hybrid Renewable Energy Systems: A Systematic
Review of Research Gaps and Prospects for Decisions." *Energies*, 18(17),
4727. https://doi.org/10.3390/en18174727

**Barrera-Singaña, C., Comech, M.P., Arcos, H. (2025).** "A Comprehensive
Review on the Integration of Renewable Energy Through Advanced Planning and
Optimization Techniques." *Energies*, 18(11), 2961.
https://doi.org/10.3390/en18112961

Both reviews formalize the decision-variables/objectives/constraints
framework this project has been using throughout (see the LP Model
Reference Document built this session) as the standard structure for this
class of problem, and both catalog MILP vs. LP-relaxation tradeoffs
directly relevant to the simultaneous-dispatch investigation (#20 series).

### M.4 Simultaneous Charge/Discharge ("SCD") — A Named, Recognized Problem

*(Located via a targeted search prompted directly by this project's own
#20 investigation. This is a well-established, named problem in the
literature -- "simultaneous charging and discharging" (SCD) or the
"battery complementarity constraint" -- not something unique to this
project's model. Worth stating plainly: every genuine fix this project
tried (MILP/binaries, netting) has a direct, named counterpart in this
literature, confirming the difficulty was real rather than a symptom of
an implementation error.)*

**Nazir, N. and Almassalkhi, M. (2021).** "Guaranteeing a Physically
Realizable Battery Dispatch Without Charge-Discharge Complementarity
Constraints." *IEEE Transactions on Smart Grid.*
https://madsalma.github.io/pubs/2021_tsg_ccBatt.pdf

The most directly actionable find of this search -- a purely linear
formulation (no binaries, no complementarity constraint) that does not
prevent simultaneous dispatch from occurring, but mathematically
guarantees the resulting SoC trajectory cannot violate physical bounds
regardless. Works by solving with TWO parallel SoC-tracking constraints:
a "relaxed" model (equivalent to this project's current formulation, proven
to always UNDERESTIMATE true SoC) and a "simplified" single-net-input model
using an averaged efficiency (proven to always OVERESTIMATE true SoC).
Bounding both keeps the true, physically-realizable SoC within limits by
construction. Reports 10-200x speedup over MILP in their own benchmarks.
Directly confirms this project's own finding from the netting investigation
(#20.3): model mismatch/conservativeness "depends largely on the charge and
discharge efficiencies... if the round-trip efficiency is low, then the
model mismatch increases" -- explicitly flagging pumped-hydro and hydrogen
storage (~60% RTE) as cases where their method becomes too conservative to
be useful, a caution directly relevant to this project's iron-air storage
specifically (RTE below Na-ion's 90%). Tested against this project's own
model this session, for Scenario 2's own Na-storage problem specifically
(Internal Debugging Log #40) -- rejected there too, for the same reason
originally found: the LP still chose to land exactly on a relaxed SoC
floor rather than being freed from the underlying pressure toward low
SoC, showing the boundary condition alone was not the root cause.

**Two further sources, located via a fresh, targeted search this session** (Internal Debugging Log
#40), prompted directly by Scenario 2's own Na-storage simultaneous-dispatch finding persisting
after the SCD literature's own previously-catalogued options had already been tried and found
insufficient. Author names not independently confirmed via the search snippets retrieved -- cited by
title/URL only, per this project's own standing sourcing convention (never invent an attribution):

"Operational Valuation for Energy Storage under Multi-stage Price Uncertainties."
https://arxiv.org/pdf/1910.09149

"A Lagrangian Policy for Optimal Energy Storage Control." https://arxiv.org/pdf/1901.09507

Both give the same sufficient condition for simultaneous charge/discharge to occur: the Lagrangian
dual (shadow price) on stored energy must be negative -- "we have an intention to store as little
energy as possible," using round-trip efficiency loss specifically to dispose of energy the
optimizer is otherwise forced to hold, most classically arising from negative real-time prices in
market-facing formulations (this project's own problem has no explicit price signal, but the same
mechanism arises from a hard equality boundary condition combined with no export/disposal valve).
Directly confirms and sharpens this project's own earlier KKT/reduced-cost finding (#20, #40) rather
than contradicting it -- both point to the same underlying phenomenon, genuine LP degeneracy driven
by a locally-negative shadow price, not a modeling error.

**Morales, J.M.** "Linear and Second-order-cone Valid Inequalities for
Problems with Storage." https://arxiv.org/pdf/2506.21470

Derives linear inequalities that are facets of the storage feasible
region's convex hull -- tightens the relaxation without full
complementarity or binaries. A second, related but distinct linear-only
candidate.

**Duan, C., Jiang, L., Fang, W., Wen, X., Liu, J.** "Improved Sufficient
Conditions for Exact Convex Relaxation of Storage-Concerned ED."
https://arxiv.org/pdf/1603.07875

Provides sufficient conditions under which a relaxed (no-complementarity)
LP's own optimal solution is automatically guaranteed complementarity-
respecting, without adding any constraint at all -- directly the same
category of check as this project's own KKT verification (#20, MILP-trial
context), formalized as reusable sufficient conditions rather than a
single point-check.

**Han, D., Jiang, N., Dey, S.S., Xie, W.** "Regularized MIP Model for
Integrating Energy Storage Systems..." https://arxiv.org/pdf/2402.04406

A "regularized" MIP with zero integrality gap versus its own LP relaxation
under mild conditions -- potentially a more tractable middle ground between
this project's full-MILP trial (#20.1, proven correct but too slow) and a
pure LP relaxation. Not yet evaluated for tractability at this project's
scale.

### M.5 Multi-Storage Coordination Under Uncertainty — Two Additional Sources

*(Provided directly by the user after the ScienceDirect and PMC links from M.4 could not be retrieved automatically -- the ScienceDirect article as a pasted excerpt, the PMC article as an attached PDF. Replaces the earlier "could not retrieve" note.)*

**"Two-stage stochastic optimization of integrated energy systems with hydrogen and battery
storage under renewable uncertainty."** *International Journal of Hydrogen Energy* (in press,
2026). https://www.sciencedirect.com/science/article/abs/pii/S036031992601387X (author names not
independently confirmed via the excerpt provided or subsequent search; title and journal confirmed)

Develops a hydrogen-centered integrated energy system (HIES) coordinating hydrogen storage (HESS),
battery storage (ESS), and dual-fuel CHP units, solved via a two-stage stochastic program (day-ahead
dispatch, then scenario-based recourse) using Vine Copula-MCMC-generated representative renewable
scenarios and a metaheuristic (scent-guided differential PSO) solver. Relevant less for its specific
solution method (stochastic + metaheuristic, a different paradigm from this project's deterministic LP)
than as a concrete example of the general challenge Anderson et al. (M.3) call out as Challenge 7 --
representing long-term uncertainty -- and as a second, independent example (alongside Bamisile et al.
below) of coordinating two structurally different storage types with different duration/response
characteristics, the same core design choice underlying this project's Na-ion/iron-air split.

**Bamisile, O., Cai, D., Adun, H., Dagbasi, M., Ukwuoma, C.C., Huang, Q., Johnson, N., Bamisile, O.
(2024).** "Towards renewables development: Review of optimization techniques for energy storage and
hybrid renewable energy systems." *Heliyon*, 10, e37482. https://doi.org/10.1016/j.heliyon.2024.e37482

A large (200-article) systematic review (PRISMA methodology) of HRES+ESS optimization, covering storage
technology taxonomy, optimization method categories (conventional/metaheuristic/hybrid), and a detailed
catalog of objective functions and constraints across 20+ specific studies (their Table 4). Two direct,
useful cross-checks against this project's own model:

- **Independent confirmation of the corrected DoD convention.** One cataloged study's battery
  constraint is given explicitly as `EBATT_min = (1 - DOD) x EBATT_max` -- i.e., the floor sits at
  `(1-DOD)` of capacity, confirming the standard convention (reserve at the bottom, not the top) this
  project corrected to earlier this session (Internal Debugging Log #17), independent of the Sandia
  methodology citation already in use.
- **Confirms LP is a recognized, if less common, category.** Their conventional-methods taxonomy
  explicitly lists "linear programming techniques" as one path among several (alongside dynamic
  programming and multi-objective strategies) -- consistent with this project's own finding
  (Section 8.1 discussion in the two MDPI reviews, M.3) that LP/MILP guarantees global optimality but
  metaheuristics dominate this literature's actual sample for tractability at scale, the same trade-off
  this project weighed directly in the MILP trial (#20.1).

---

### M.6 "Unintended Storage Cycling" (USC) — A Named Phenomenon Specifically Tied to Renewable-Target Constraints

*(Located via a broader literature search, deliberately not limited to any single solver's practice,
per direct instruction. This is a distinct, more specific literature thread than M.4's general "SCD"
material -- USC is specifically about simultaneous dispatch caused by renewable-share/RPS-style
constraints, exactly this project's own RPS mechanism, rather than LP relaxation looseness in general.)*

**Kittel, M. and Schill, W-P. (2022).** "Renewable Energy Targets and Unintended Storage Cycling:
Implications for Energy Modeling." *iScience*, 25(4), 104002. https://doi.org/10.1016/j.isci.2022.104002

The originating paper for the USC term and the "SLCR" (Storage Loss Coverage by Renewables) constraint
reformulation -- ties a renewable-share constraint's required generation to storage losses incurred, so
that USC-driven losses can no longer hide from the constraint's own accounting. Key empirical finding
directly relevant to this project's own checkpoint structure: USC "grows disproportionately" with
renewable penetration and does not occur at all below roughly 40% renewable share -- this project's
2045 checkpoint (99.9%+ clean target) sits at the most extreme end of the range their paper identifies
as worst-case. Personally tested against this project's model (Internal Debugging Log #20.7): SLCR did
NOT reduce simultaneous dispatch here (marginally increased it, 644.5M vs. 532.8M MWh phantom volume),
traced to a real, identified reason -- their mechanism specifically targets gaming a BINDING gas
allowance, and this project's 2045 target leaves almost no such allowance to game (confirmed post-trial
at 0.064% gas, tighter than the 0.08% target itself). Flagged as possibly still relevant at less extreme
checkpoints (2030/2035/2040) where a genuine, larger gas allowance exists -- not yet re-tested there.

**Parzen, M., Kittel, M., Friedrich, D., Kiprakis, A.E. (2023).** "Reducing energy system model
distortions from unintended storage cycling through variable costs." *iScience*, 26(1), 105729.
https://doi.org/10.1016/j.isci.2022.105729

Companion paper to the above, from the same research thread, testing a different remedy: correctly-
calibrated variable costs (not structural constraint changes). Empirically tested threshold, specific
and quotable: full USC removal in their PyPSA-Eur case study required a variable cost additive of at
least 10 EUR/MWh -- and they explicitly note the required threshold scales with solver precision, citing
100 EUR/MWh under looser solver accuracy settings. Directly relevant, NOT YET TESTED: this project's own
option 3/4 attempt (Internal Debugging Log, cycling-cost-on-both-sides test) used only $2.67/MWh split
across both charge/discharge sides for Na-ion -- an order of magnitude below this paper's own validated
minimum. The earlier option 3/4 "no effect" finding may reflect an insufficiently large cost, not a
genuine failure of the underlying approach -- a real candidate for re-testing at the properly-scaled
value before concluding cost-based fixes don't work here.

**Independent, practitioner-level confirmation (not an academic source, but a real production tool):**
GitHub, blue-marble/gridpath, Issue #839, "Add constraint to prevent simultaneous charge and discharge
from a storage project." https://github.com/blue-marble/gridpath/issues/839

A GridPath user modeling pumped hydro storage reports the exact mechanism this project independently
diagnosed: "the curtailment cost is more expensive than the cost to operate PSH discharge so it is
cost-optimal to 'dump' wind or solar energy by charging and discharging storage. The energy is 'dumped'
in the efficiency loss of the PSH pumps and generators." Confirms this project's core diagnosis
(curtailment-cost-vs-cycling-cost imbalance driving the phenomenon) was independently arrived at by a
different practitioner, in a different real-world tool, using different language -- not a project-
specific artifact.

**PyPSA mailing list, practitioner discussion** (Google Groups, pypsa, March 2021).
https://groups.google.com/g/pypsa/c/mg8xQD91di4

A PyPSA maintainer's own recommended practice: "you could set a small marginal cost on both links to
discourage simultaneous charging/discharging... It obviously depends on your model, but the need for
curtailment is one situation where this can occur." Same underlying approach as this project's own
option 3/4 (cost on both sides), offered informally by the tool's own maintainers as standard practice
-- consistent with, not contradicting, the Parzen et al. calibration finding above.

### M.7 A Pure-LP Tighter Reformulation — No Binaries, Proven Convex-Hull-Optimal for One Period

**Elgersma, M.B., Morales-España, G., Aardal, K.I., Helistö, N., Kiviluoma, J., de Weerdt, M.M. (2024).**
"Tight MIP Formulations for Optimal Operation and Investment of Storage Including Reserves."
arXiv:2411.17484. https://arxiv.org/pdf/2411.17484

Distinct in kind from every option this project has tried (MILP/binaries, netting, RBD, SLCR) --
derives the exact convex hull of the single-period storage operation problem, and shows the resulting
"TO-LP" reformulation (a pure constraint rewrite: bounding `e[t-1]` by the CURRENT period's
charge/discharge rather than bounding `e[t]` directly, no binary variables needed for the LP relaxation
itself) provably tightens the standard formulation. Own case study results are a genuine, if partial,
improvement: simultaneous-dispatch periods roughly halved (663 to 363 of 1,460 periods) and the phantom-
volume metric also roughly halved, with no MILP-scale computational cost. NOT YET TESTED against this
project's model -- flags one real caveat worth checking first: their tightness guarantee assumes power
rating doesn't exceed what's needed to fill/drain the full usable capacity range in one hour (roughly
`P_rated <= capacity/(η·Δt)`), an assumption this project's Na-ion build (PNA_ often far exceeding
ENA_/duration, given both are chosen independently by the LP) may violate, which could weaken the
guarantee's practical effect here even if implemented correctly.

**Related, not yet reviewed in full:** Elsaadany, M., Almassalkhi, M.R., Tindemans, S.H. (2025). "Linear
Model of Aggregated Homogeneous Energy Storage Elements with Realizable Dispatch Guarantees."
https://arxiv.org/html/2501.04508 -- cited within Elgersma et al. as the "composite battery systems"
exception to standard SCD reasoning (multiple physical sub-units genuinely CAN charge and discharge
simultaneously in aggregate, since different sub-units can be in different states at once). Possibly
relevant given utility-scale Na-ion/iron-air installations are physically composed of many discrete
units, not one monolithic device -- a reframing (aggregate dispatch guarantees, not single-unit
complementarity) not yet explored for this project.

---

### M.8 Storage Under-Utilization at High VRE Penetration — Why Curtailment Despite Headroom Is Expected, Not a Defect

**López Prol, J. and Schill, W-P. (2020).** "The Economics of Variable Renewables and Electricity
Storage." arXiv:2012.15371. https://arxiv.org/pdf/2012.15371

A review synthesizing multiple independent, peer-reviewed lines of evidence (different models,
different methods: price-taker arbitrage models, time-series models, capacity-expansion models) that
directly resolves this project's separate "headroom despite curtailment" pattern (Internal Debugging Log
#21), distinct from the simultaneous-dispatch issue (#20 series). Key finding, quoted directly: "storage
is never deployed to fully take up renewable surplus generation in a least-cost solution, as this would
require excessive and under-utilized investments into storage power and, even more so, storage energy
capacity... there will accordingly always be some level of renewable curtailment, absent geographical
balancing, flexible Power-to-X, or other low-cost flexibility options." Synthesizes and cites directly:

- **Schill, W-P. (2014).** "Residual load, renewable surplus generation and storage requirements in
  Germany." Energy Policy 73, 65-79. Finds storage needs "substantially decrease if small levels of VRE
  curtailment are allowed," and that rare, extreme surplus events -- not typical days -- determine
  storage sizing, so forcing zero curtailment causes storage needs to increase disproportionately.
- **Zerrahn, A., Schill, W-P., Kemfert, C. (2018).** "On the economics of electrical storage for
  variable renewable energy sources." European Economic Review 108, 259-279. Confirms with an
  open-source model that a mix of VRE curtailment and storage deployment minimizes overall system costs
  -- not either alone.
- **Sinn, H-W. (2017).** "Buffering volatility: A study on the limits of Germany's energy revolution."
  European Economic Review 99, 130-150. A particularly strong data point precisely because it set out to
  argue the opposite: a priori ruling out renewable curtailment as a test case, and finding storage needs
  would "very substantially increase" as a result -- reinforcing the same conclusion from the direction
  most likely to contradict it.
- **Denholm, P. and Hand, M. (2011).** "Grid flexibility and storage required to achieve very high
  penetration of variable renewable electricity." Energy Policy 39, 1817-1830. Gives a concrete
  benchmark: even at 80% VRE penetration, keeping curtailment below 10% requires storage sized to
  roughly one full day of average demand -- curtailment at high VRE shares is the literature's norm, not
  an exception requiring correction.

**Resolution for this project:** confirms this project's own earlier, independently-derived finding
(Appendix A.9, curtailment cheaper than buying enough storage to fully avoid it) as an instance of this
same, broader, peer-reviewed principle rather than a project-specific artifact or an unresolved defect.
The mechanism transfers directly: storage capacity gets sized for its everyday role (arbitrage, smoothing
dispatchable full-load hours), not for rare extreme-surplus hours; on those hours the battery has SoC
headroom it was never sized to use, and using it would mean paying a full charge+discharge cycling cost
to serve demand already met more cheaply elsewhere -- making direct curtailment the genuinely
cost-minimizing choice. No further model change made on this basis; the SLCR $5-40/MWh working range
(2045 Scenario 1 final value: $5/MWh) stands as the resolved state, with remaining curtailment and SoC
headroom understood as expected, documented behavior.

---

### M.9 Virginia-Only Demand Data — Dominion's Own 2025 IRP Update, Appendix 2B-2

**Dominion Energy Virginia (Virginia Electric and Power Company). "2025 Integrated Resource Plan
Update." Filed with the Virginia State Corporation Commission (Case No. PUR-2025-00184) and the
North Carolina Utilities Commission, October 15, 2025. Appendix 2B-2: "Virginia Sales (GWh) by
Customer Class," p. 89.**

The demand basis this project's SLCOE/NPV work uses going forward, and the resolution of one of the
three open dimensions on Activity Tracker item 54 (vintage / methodology / geography -- geography is
now resolved by this citation; the other two remain open).

**Why this specific table, not the more commonly-cited "DOM LSE" figures already used elsewhere in
this project's demand work:** PJM's own transmission-zone map shows the "DOM" zone spanning both
Virginia and North Carolina -- Dominion Energy Virginia's own retail service territory is only the
Virginia portion of that zone. Every "DOM LSE" figure examined earlier in this project's demand
investigation (the 2025 IRP Update's own Figure 2.1.9 Company Load Forecast table, a stakeholder-
obtained 2024 hourly load file, PJM's 2026 Load Forecast Report) is the *combined* VA+NC total, not
Virginia alone -- confirmed directly by the filing's own text: Dominion "operates generation,
transmission, and distribution systems to serve approximately 2.8 million electric customers located
across approximately 30,000 square miles of Virginia and North Carolina." Appendix 2B-2 is the
filing's own Virginia-only breakout, distinct from Appendix 2B-1 (the combined DOM LSE total) and
2B-3 (North Carolina only).

**Annual energy, Virginia-only (GWh), key years from the full 2015-2045 table:**

| Year | GWh |
|---|---|
| 2025 | 95,246 |
| 2030 | 110,864 |
| 2035 | 136,645 |
| 2040 | 162,077 |
| 2045 | 186,462 |

**Implied North Carolina share** (this table vs. the combined DOM LSE total already cited elsewhere
in this project): 5.8% (2025), narrowing to 3.1% (2040-2045) -- smaller in magnitude than the other
open dimensions on item 54 (vintage divergence up to ~15%; DOM Zone-vs-DOM-LSE gap up to ~107%),
and directionally sensible: Northern Virginia's data-center growth outpaces Dominion's smaller North
Carolina territory, so Virginia's share of the combined total grows over time.

**Important limitation, stated directly in the filing immediately below the table:** *"Appendix 2B-2
has been provided with the 2025 Company Load Forecast instead of the 2025 PJM Load Forecast because
PJM does not provide forecasted sales or customer counts broken down by rate class."* A Virginia-only
cut of the PJM-derived forecast -- the version the SCC actually directs Dominion to use for portfolio
planning -- does not appear to exist as a published figure at all, since PJM's own underlying data
doesn't break out by state. The Company and PJM-derived forecasts are stated elsewhere in the same
filing to be "in general alignment" (2025 PJM Derived: 2.5%/3.5% CAGR for DOM LSE peak/energy;
2025 Company: 2.3%/3.3% CAGR, same scope and window) -- so this is likely a small, bounded gap
rather than an unresolved discrepancy, but it hasn't been directly confirmed for the Virginia-only cut
specifically.

**Status at time of citation:** used as the working demand basis for this project's SLCOE/NPV
calculations because it is the most directly-sourced, Virginia-specific figure available, and the
next IRP filing (2026) is not expected for several months. The vintage question (this is 2025-vintage
data; a 2024 stakeholder file and PJM's own 2026 report remain separate, unreconciled vintages -- see
Activity Tracker item 54) is not resolved by this citation and should be revisited if a newer,
directly Virginia-scoped source becomes available.

---

### M.10 Solar "Value Factor" — Measured PJM Data, Used to Stress-Test (Not Adopt) the Export-Price Discount

**Seel, J., Mulvaney Kemp, J., Cheyette, A., Gorman, W., Darghouth, N., Robson, D., Rand, J., Jeong,
S. "U.S. Utility-Scale Solar 2025 Data Update." Lawrence Berkeley National Laboratory, October 2025.
utilityscalesolar.lbl.gov**

Cited in Appendix B.5 (export price) as a specific, credible source located and checked in place of
this project's earlier, un-pinned-down "documented in NREL/LBNL solar value reports" citation --
included here because it was a genuine, weighed consideration in reaching the final export-price
figure, not because it was ultimately adopted.

Defines a **value factor**: the ratio of solar's actual generation-weighted captured market value to
a flat 24x7 block's average value at the same location -- exactly the concept this project's export-
price "midday discount" factor is attempting to approximate. National average value factor, 2024:
80%. Regional range is wide: as low as 30% in CAISO (at 30% solar penetration, the report's clearest
illustration of penetration-driven value decline), as high as 181% in SPP (1% penetration). **PJM
specifically is reported slightly above 100%** -- $33/MWh solar value vs. $32/MWh flat-block value in
2024 -- with the report explicitly listing PJM among regions where solar's generation profile *helps*
rather than hurts its relative value.

**Why this was not adopted despite being directly on-point:** two disclosed limitations, both noted
at time of decision rather than found later. (1) PJM-wide, not DOM-zone-specific -- no strong reason
to expect DOM to differ sharply, but not a direct measurement either. (2) A 2024, current-penetration
snapshot -- the same report documents value factor declining as solar's regional load share grows,
with CAISO's trajectory as the clearest within-report precedent. This project's own checkpoints
project solar growing roughly 15,000 MW (2030) to 142,000 MW (2045), a penetration path well beyond
what PJM's current, sub-saturation value factor describes. Retained here as a documented,
directly-relevant data point for future reference (e.g., if this project ever builds a
penetration-dependent export-price curve rather than a flat rate), not as a citation supporting the
model's current $27.00/MWh figure.

---
