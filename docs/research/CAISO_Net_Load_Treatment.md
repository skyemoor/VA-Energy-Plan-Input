# CAISO Net-Load Treatment — and what it implies for our reserve constraint

**Research note, 2026-09-11.** Prompted by the finding that this project's reserve constraint uses
**gross demand at a single peak hour**, which at ~174 GW of solar may be sizing against the wrong
hour entirely.

Complements `CA_NY_PJM_Reliability_Compliance_Comparison_2026-08-23.md`, which covers CAISO's
FCDS/EODS deliverability split and the RPS-versus-reliability separation. **This note covers a
different question** — how CAISO sizes reserves against net load — which that document does not
address.

---

## The answer: CAISO uses two requirements, not one

> *"...their peak load including a planning reserve margin **and** flexible capacity to address
> largest 3-hour net load ramps plus contingency reserves."*
> — CAISO, Flexible Capacity Needs and Availability

| requirement | sized against | our equivalent |
|---|---|---|
| **Resource Adequacy** | peak load + planning reserve margin | **IRM 17.7% at `t_peak`** ✓ we have this |
| **Flexible Capacity** | **largest 3-hour net load ramps** + contingency reserves | **nothing** ✗ |

**CAISO does not replace peak-load planning with net-load planning. It adds a second, parallel
requirement.** That is the structural answer: net load is addressed *in addition to* peak, not
instead of it.

---

## How the flexible capacity requirement is built

**Annual Flexible Capacity Needs Assessment**, producing **monthly minimum requirements**. Inputs:
load, PV generation and wind generation measurements from the previous year, adjusted for new PV
and wind installations and load growth.

**Three categories**, with different must-offer hours by month:

| category | scope |
|---|---|
| **Base flexibility** | general |
| **Peak ramping** | the five-hour periods of peak demand |
| **Super-peak ramping** | the most extreme ramping periods, typically weekdays excluding holidays |

Resources under an RA contract carry a **must-offer obligation** — they must submit economic bids
into the real-time market consistent with their flexible capacity category. The requirement is not
merely a planning number; it binds operationally.

### Scale, for calibration

CAISO net load in 2025 **fluctuates by about 25 GW over a day**, dipping **below zero just after
noon**, and rises **6.5 GW in the 6pm hour** on average.

---

## The Flexible Ramping Product — the market instrument

Separate from the capacity requirement. Procures upward (FRU) and downward (FRD) ramping capability
in the **real-time market only** (MISO procures in both day-ahead and real-time).

CAISO's **"Mosaic" statistical model** sets requirement sizes from current solar, wind and demand
forecasts plus **historical forecast errors**. Each requirement splits into a **forecasted
movement** segment and an **uncertainty** segment. Thresholds are set at the **98th percentile** of
historical uncertainty to prevent extreme outlier requirements, reviewed quarterly.

A **diversity benefit** applies: system-level ramping need is smaller than the sum of individual
area needs, because geography decorrelates.

**Batteries are structurally advantaged here.** Unlike thermal units that need time to change
output, they ramp instantly, which makes FRU/FRD a natural revenue stream for storage — relevant to
any Scenario 3 argument about what distributed storage could earn beyond energy arbitrage.

---

## Two documented shortcomings, worth carrying

**The requirement has under-delivered.** *"The stipulated average flexible capacity requirements
fell short of the magnitude of the actual primary three-hour net load ramps in the eight months of
2018."* Sizing against historical ramps does not guarantee coverage of future ones.

**Monthly granularity is too coarse.** *"One-size-fits-all monthly requirements cannot sufficiently
capture the idiosyncrasies of the magnitude or start time of daily primary three-hour net load
ramps."*

Both matter for how faithfully we would want to copy the design rather than adapt it.

---

## What this implies for this project

### Our constraint is sizing against the wrong hour

```
S × BUILD_SCALE × solar_cf[t_peak] ≥ (1 + IRM) × demand[t_peak]
```

**Gross demand, one hour.** In a system with ~174 GW of solar, the hour that stresses the fleet is
almost certainly an **evening net-load ramp**, not gross peak — and CAISO's own data shows net load
dipping below zero at midday while rising 6.5 GW in a single evening hour.

### Three candidate responses

**1. Add a flexible capacity requirement — CAISO's actual design.** Size against the largest
3-hour net-load ramp per month, in addition to the existing peak constraint. Faithful, and the
ramp is computable directly from the hourly series we already hold.

**2. Move the existing constraint to net load** rather than gross. Cheaper, but **loses what the
peak constraint is for** — CAISO keeps both deliberately, and a net-load-only constraint would
under-size for a high-demand, high-solar hour.

**3. Wire in `all_hours_reserve.py`**, which already exists and is documented as this project's
"current standard" but is never called. It enforces reserve in **every** hour, which subsumes both
the peak and ramp cases without requiring a ramp requirement to be specified.

**Option 3 is the cheapest and most likely sufficient**, and should be tried first — it is already
built and was validated once. Option 1 becomes worth adding if the all-hours constraint proves too
weak or too slow.

### Note on what this does not fix

None of these produce scarcity *pricing*. They constrain storage from arbitraging every hour to its
floor — which should give the dual structure it currently lacks — but the stack still terminates at
the dearest gas tier and then jumps to VOLL. See `MODEL_WIDE_FINDINGS.md` §1 and §3.

---

## Sources

- CAISO, *Flexible Capacity Needs and Availability* — the two-requirement structure and the
  three flexibility categories
- CAISO, *Flexible Ramping Product Uncertainty Calculation Implementation Issues*
- CAISO, *Flexible Ramping Product Requirements and Load Forecast* (June 2018) — 98th percentile
  thresholds
- CAISO, *Report — Flexible Ramping Product Performance* (March 2022) — WEIM diversity, pricing
- arXiv 2012.07117, *Forecasting Daily Primary Three-Hour Net Load Ramps in the CAISO System* —
  the 2018 shortfall and the monthly-granularity critique
- arXiv 2409.00429, *Flexible Ramping Product Procurement in Day-Ahead Markets* — MISO/CAISO/SPP
  comparison
- Modo Energy (Aug 2025) — 25 GW daily net load swing, 6.5 GW 6pm ramp, BESS positioning
- PCI Energy Solutions (Aug 2025) — peak and super-peak ramping resource categories
