# Compliance definition for the sweep axis

**Settled 2026-09-13**, ahead of restructuring the scenarios into a compliance sweep. Nothing
downstream means anything until the x-axis is one formula, stated once.

---

## The answer: the sweep axis is CLEAN GENERATION SHARE, not statutory RPS percentage

They are different quantities, and `Demand_Basis_and_RPS_Compliance_Working_Notes.md` §5–6 had
already established how. This note picks between them for the sweep and says why.

### What the model enforces

```
gascum[T-1] ≤ k × clean_generation        k = gas_allowed_frac / (1 − gas_allowed_frac)
clean = nuclear + existing solar + CVOW wind + new solar build
```

That is **gas as a share of total generation**. `achieved_share = gas_GWh / non-nuclear demand`.
No denominator is derived from retail sales.

### What § 56-585.5 requires

A percentage of **total electric energy sold in the previous calendar year**, satisfied by
**procuring and retiring RECs** — which may originate anywhere in PJM, with ≥75% from
Virginia-located resources from the 2027 compliance year.

And the statutory base **excludes**:

| exclusion | scale |
|---|---|
| **(a)** In-Commonwealth nuclear operating by 1 July 2020 (Surry, North Anna) | ~32,000 GWh against ~107,000 GWh of Virginia sales — roughly a **30% reduction in the denominator** |
| **(b)** Certified **accelerated clean energy buyers** — C&I with >25 MW aggregate load, opt-in and certified | a behavioural variable, potentially very large |
| **(c)** § H legacy competitive-service customers (>100 MW peak in 2019) | smaller |

### The two give materially different requirements at the same headline percentage

At 2045, 100%:

| | new clean generation required |
|---|---:|
| **Model** (generation share, nuclear counts as clean) | **~121,000 GWh** |
| **Statute** (nuclear excluded from the base) | **~75,000 GWh** |

**The model is the stricter of the two at 2045** — it requires new clean build to cover load that
existing nuclear already serves. At intermediate years the sign can invert, and which effect
dominates has not been worked through.

---

## Why the sweep uses generation share anyway

**It is the physically meaningful question.** "At what share of generation does clean become more
expensive than gas" is answerable from a dispatch model. "At what REC procurement percentage" is an
accounting question whose answer depends on out-of-state REC prices, ACEB certification behaviour
and § H elections — none of which this model contains.

**It is the stricter measure at the endpoint**, so a cost curve built on it does not understate what
compliance demands. A reviewer arguing the analysis is too lenient has to argue against the
stricter of the two definitions.

**The statutory version is not computable here without new inputs.** ACEB participation alone is
described in the source note as *"plausibly the single largest lever on the compliance question"*
and is opt-in behaviour, not a fixed deduction. Putting a behavioural unknown on the x-axis would
make every point on the curve conditional on an unmodelled assumption.

---

## What this obliges the whitepaper to say

**The axis must be labelled "clean generation share", not "VCEA compliance percentage."** They are
not the same number, and the difference is roughly 46,000 GWh at the 100% point. Presenting a
generation-share curve under a statutory label would misstate the requirement by about 38%.

**The nuclear treatment must be stated wherever the axis appears.** Nuclear counts as clean in the
model and is excluded from the statutory base — opposite treatments, and the single largest source
of divergence between the two measures.

**Scenario 2's plotted point inherits the same definition.** Its compliance level is computed on
generation share, so it is comparable to the curve but is *not* a statement about whether
Dominion's build satisfies § 56-585.5.

---

## What would be needed to sweep on the statutory measure instead

Not recommended now, recorded so the gap is explicit:

1. Retail sales by year on the statutory basis, excluding nuclear
2. An ACEB participation assumption, with sensitivity — it is opt-in and aggregates across
   affiliates
3. § H legacy customer load
4. A REC accounting layer, including out-of-state eligibility and the ≥75% in-state floor
5. A position on whether banked RECs and deficiency payments are in scope

Items 2 and 5 are scenario variables in their own right. This is a second study, not an axis change.

---

## Related

- `docs/methodology/Demand_Basis_and_RPS_Compliance_Working_Notes.md` §5–6 — the source findings
- `docs/statutes/56-585.5.md` — the statute

---

# Levelisation — SLCOE from the annual stream

**Added 2026-09-13**, `lp_package/levelised_cost.py`.

```
SLCOE = PV(annual costs) / PV(annual demand served)
```

at `WACC = 0.045` from `BASE_YEAR = 2026`.

## Four checkpoints are not an SLCOE

Averaging 2030/2035/2040/2045 weights each equally, ignores discounting, and misses that **demand
grows 72% across the horizon** so later years carry far more MWh. `verify_complete()` raises on
gaps, because a levelised figure over a partial stream looks identical to one over a complete
stream and is wrong by however much is missing.

Intermediate years come from **dispatch-only re-solves against an interpolated build** — cheap,
since there are no build variables to optimise.

## Terminal value is standard practice

**NREL ATB**, identical across the 2021, 2023 and 2024 editions: *"A technical life that is longer
than the cost recovery period means **residual value** may be left after costs have been
recovered."* The ATB carries a technical-life table separate from the cost-recovery period
precisely so this can be computed.

**NREL 72217** treats it as a distinct valuation phase — *"produces a **residual value (RV)** of
net earnings"* — and quantifies the LCOE effect of extending PV operational life from 20 to 30
years.

**European Commission methodology** gives the two accepted routes: the residual market value as if
sold at the horizon, or the present value of net cash flows beyond the reference period.

**With `CRF_LIFE_YEARS = 25` against a 20-year horizon, omitting terminal value is the choice that
needs defending** — a plant built in 2044 would otherwise be charged in full and credited with
nothing for 24 years of remaining service.

### Why the EC's second method

**It degrades correctly.** An asset with no post-horizon cash flows — gas stranded at 100%
compliance — has **zero residual value by construction**, with no special-case rule. The first
method would require deciding what a stranded plant would sell for, which is a judgement the model
cannot make.

`undepreciated_value(..., strands_at_horizon=True)` returns 0.0 regardless of book age: the plant
exists, it is young, and it is worth nothing because it will never run again.

### Reported both ways

With and without the terminal-value credit, following the convention of the prior 20-year SLCOE
work, so a reader can strip out an assumption they disagree with.

## Applied to all assets in all scenarios

Consistent treatment, per project decision 2026-09-13. An explicit `0.0` records that an asset was
considered; an omission is indistinguishable from an oversight.
