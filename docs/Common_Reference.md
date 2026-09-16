# Common Reference

**Cross-cutting facts and conventions that apply to every scenario.** Where a quantity, unit basis
or convention is shared across the model, it is defined here once rather than restated in each
scenario's working paper.

**This is a reference, not a log.** LP issues and their solutions go to
`Internal_Debugging_Log.md`; recurring error patterns go to `Common_Mistake_Log.md`; scenario
findings go to that scenario's working document; where things stand goes to
`Scenario_Completion_Dashboard.md`; open problems go to GitHub issues.

---

## Index

| # | section | covers |
|---|---|---|
| 1 | Transmission and distribution | loss factor, load against generation basis, what "energy sold" means in statute |

*Sections are added as cross-cutting questions arise. A topic belongs here when a second scenario
would otherwise need the same answer.*

---

## 1. Transmission and distribution

### 1.1 The loss factor is 1.0925

Derived from two Dominion sources for the same year and scope, so the gap is losses and nothing
else:

| source | 2030 GWh | basis |
|---|---:|---|
| `DOMLSEHourlyLoadProjections2024through2048.csv` | 121,115 | losses **included** |
| 2025 IRP Update, Appendix 2B-1 | 110,864 | losses **excluded** |
| **ratio** | **1.0925** | ≈9.25% losses and station service |

Both figures are Virginia plus North Carolina, so this is **not** a scope difference. The IRP
itself distinguishes the two bases, describing values *"at the utility generator and adjusted for
line losses"* (Figures 2.1.11 and 2.1.12).

**This is Dominion's own figure for Dominion's own system**, which is preferable to any general
modelling assumption for T&D losses.

### 1.2 Two bases, and which applies where

● **Generation basis** — what must be produced at the generator, losses included. **121,115 GWh**
  in 2030 for Virginia plus North Carolina.
● **Meter basis** — what arrives at the customer and is sold. **110,864 GWh** for the same year and
  scope.

**Dispatch uses the generation basis.** The hourly file already carries the gross-up, so it is used
directly and needs none.

**Statutory obligations use the meter basis**, where the Code says so. Va. Code § 56-585.5(C): the
RPS Program requirement is *"a percentage of the total electric energy **sold** in the previous
calendar year."* Sold means metered, so the base is generation ÷ 1.0925.

**The same series is therefore divided for one purpose and not for the other**, sometimes within
the same function. That is correct, and it is the single most likely place in this model for a
plausible-looking error.

### 1.3 The class name says "load" and returns generation

`demand_basis.VirginiaOnlyLoad` returns the **generation-side** quantity. "Load" here follows the
utility-planning convention — what must be generated to serve load — rather than the ordinary
reading of load as the quantity at the meter.

**The name points the wrong way for statutory work**, and the docstring's warning is what makes the
basis clear rather than the name. A reader who takes "load" at face value and divides by the loss
factor for dispatch would understate generation need by 9.25%; the working notes flag exactly that.

### 1.4 What is not represented

● **Losses are a scalar gross-up, not modelled physically.** There is no distinction between
  transmission and distribution losses, no variation by hour or by load level, and no locational
  detail. Real losses rise with the square of current, so they are higher at peak than the flat
  9.25% implies.
● **Avoided losses from distributed generation are not credited.** Generation at the meter avoids
  the losses that serving the same load from a central station would incur — worth roughly 9% of
  the energy it displaces. Scenario 3's transmission-deferral assessment is where this would be
  quantified; it is not currently anywhere in the model.

**Both omissions run the same way: they understate the value of distributed generation.**
