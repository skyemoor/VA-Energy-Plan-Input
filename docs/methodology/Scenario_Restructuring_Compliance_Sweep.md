# Scenario restructuring: compliance as the axis

**Decided 2026-09-13.** Supersedes the four-named-scenario framing as the organising structure for
the whitepaper's central result. The scenarios remain defined; they become points and overlays on a
curve rather than the curve itself.

---

## Why

The stated goal has two halves:

1. What does 100% VCEA compliance cost?
2. At what lesser compliance level is clean generation cost-competitive with gas?

**The model served the first and could not serve the second.** `gas_target_share` is an *input*
fixed at 0.59 → 0.41 → 0.21 → 0.00, and `converge_frac` searches for the fraction that *hits* that
target. The LP is never free to choose less clean because gas is cheaper. So the model answers
point queries, while the question is a search over compliance levels.

---

## The restructuring

| was | becomes |
|---|---|
| Scenario 1 | the **100%** point on the curve |
| Scenario 1B | the **95%** point |
| **Scenario 2** | **the reference** — a fixed statutory build whose compliance level is an *output*, plotted as a single point |
| Scenario 3 (a–c) | a **siting overlay**, re-solved at each level |
| Scenario 3 (d) | **a second curve** — see below |

**Primary output: one chart.** Annualised cost against clean generation share, 75% → 100%, with
Scenario 2 plotted as a point. *Is Dominion's approach cost-efficient?* becomes *does that point sit
on the curve or above it?*

### Three axes

1. **Compliance level** — 0.75, 0.80, 0.85, 0.90, 0.95, 1.00 at 2045. The primary axis.
2. **Siting overlay** — utility-only / 20% distributed / 85% agrivoltaic.
3. **Gas price** — Deloitte MEDIUM, HIGH, EIA. Turns the curve into a **band**, which is what
   "cost-competitive with gas" honestly requires.

---

## Four corrections to the initial framing

These were raised in review and the initial proposal was wrong on each.

**Scenario 1's colocation constraint stays.** Scenario 1 is not merely "100%" — it is *firmed solar
colocated with storage, no standalone storage*. That is a **configuration** rule, and a bare sweep
at 100% would not enforce it. **Decision: it stays**, because the transmission costs of the
alternative would be high and undefinable without a full siting study, which is far beyond this
effort's scope.

**Scenario 3(d) is not an overlay.** Elements (a)–(c) change *where* the build goes. Element (d) —
retail day-ahead and real-time rates — **changes demand**, because hourly pricing induces load
shifting, which changes the load shape, which changes the optimal build at *every* level. It
alters the problem, not the answer. **It is a second curve, and a separate scenario.**

**The overlay is not a constant delta.** The distributed segment has a siting cap. At 100% the cap
binds hard; at 75% it may not bind at all, so the overlay's effect **varies along the axis**. It
must be re-solved at each level, not applied as an adjustment.

**Scenario 2 is the baseline, and stays so.** Dominion's approach — building only the solar and
storage specifically named in the Code — is the comparison the whitepaper exists to make.

---

## The counterfactual for "cost-competitive with gas"

Most candidates fail scrutiny:

| candidate | why it fails |
|---|---|
| Dominion's IRP | a *mix*, not "gas" — and it already occupies the Scenario 2 reference role |
| An all-gas system | never proposed by anyone; a straw man |
| Today's fleet extended | demand doubles, so this needs massive new gas anyway — not a status quo |

**What survives: unconstrained least-cost.** Run the LP with **no clean requirement** and let it
build whatever is cheapest for 2045 — *what the market would do with no VCEA*. The compliance curve
then measures **the cost of the policy at each level**, and "cost-competitive" gets a precise
meaning: the range over which the curve stays flat before rising.

### The model cannot run it yet

**Gas is not a build variable.** Capacity is capped by `apply_gas_cap()`, and the 2,862 MW
new-build pool is a fixed allowance rather than something the LP chooses to build against
`CCGT_CAPEX`. An "unconstrained" run today would still be constrained to ~12,224 MW of gas.

For the counterfactual to mean anything, **gas capacity must become a decision variable with its
own capex**, so the LP can genuinely trade a new CCGT at $3,000/kW against solar at $1,114/kW plus
storage. **That is a model change, and it precedes the sweep** — without it the sweep has nothing
to be measured against.

**It may produce an inconvenient answer.** At current turbine costs and Deloitte's trajectory, the
unconstrained LP might build mostly solar and storage anyway — in which case the competitiveness
question is settled before the sweep starts. That would be a strong finding, but a reviewer will
test it by pushing gas capex and gas price down, so the gas-price band and a capex sensitivity are
not optional.

---

## What the sweep deliberately drops

**The checkpoint chain.** Six levels × four checkpoints × up to eight solves is not viable. The
sweep is about the **2045 end state**; run it target-first. The myopic-versus-target-first question
stays open as a separate sensitivity on one or two points — see
`Experiment_Pathway_Foresight.md`.

**Scenario names as the organising concept.** They served the initial framing. The sweep serves the
question actually asked.

---

## Sequence

1. ~~Define compliance in model terms~~ — done, `Compliance_Definition_For_Sweep.md`
2. Fix the gas cap / schedule mismatch, since the cap sets what the sweep can reach (issue #18)
3. Run Scenario 2 pinned → its compliance level and cost
4. Run the sweep, MEDIUM gas, 2045 target-first — **11 levels, 30% to 100%**
   (`assumptions.COMPLIANCE_SWEEP_LEVELS`), dense above 75% where compliance trades against cost,
   coarse below it where the curve mainly establishes where Scenario 2 sits
5. Add the gas-price band
6. Apply overlays to the two or three most interesting points

~~**Step 3 is not currently runnable**~~ — **done 2026-09-14.** Scenario 2 runs, and its compliance
level is 34.7% at 2045 with an SLCOE of $32.80/MWh. That figure is what set the sweep's lower bound:
the floor is 30% so the reference case falls *inside* the range rather than on its edge.

---

## The intended result, in one sentence

> Dominion's statutory build reaches **X%** clean generation share at cost **Y**; the least-cost
> build at **X%** costs **Z**; reaching 100% costs **W**.
