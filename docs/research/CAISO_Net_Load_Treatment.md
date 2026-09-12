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
S × BUILD_SCALE × solar_cf[h] ≥ (1 + IRM) × demand[h]
    where h = hour_of_maximum_net_demand
```

**One hour.** The hour is selected on NET demand — `find_hour_of_maximum_net_demand()` — so the
selection is already net-load based, a point earlier drafts of this note got wrong. The requirement
written at that hour is against GROSS demand. What is missing is a RAMP requirement and any
constraint on the other 8,759 hours — and CAISO's own data shows net load
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

## Can reserves be drawn on for outlier peaks? — researched 2026-09-11

Asked because it bears on whether a reserve constraint should be a hard floor in every hour or a
cushion the system may dip into. **The answer is that "reserves" is three different things with
three different rules.**

### 1. Planning reserve margin — covers everything, statistically

Long- and near-term planning follows the **one-day-in-ten-years** guideline (NERC BAL-502-RF-03),
an annual **LOLE of 0.1 events/year**. It is a probabilistic adequacy target covering outages,
load forecast error and weather together. It does not distinguish causes.

**This is our IRM 17.7%.**

### 2. Day-ahead scheduling reserve — explicitly includes load forecast error

Per **PJM Manual 13**, the day-ahead scheduling 30-minute reserve requirement is calculated from
the annual peak load forecast **adjusted for under-forecasted load-forecasting error** *and*
generator forced outage rate.

**So yes — PJM's day-ahead reserve is sized for demand being higher than forecast, not only for
units failing.** Outlier peaks are covered here.

### 3. Contingency reserve (NERC BAL-002) — outage recovery only, with one exception

Contingency reserve is *"necessary to replace capacity and energy lost due to forced outages of
generation or transmission equipment."* It is sized to the **Most Severe Single Contingency** and
is intended for recovery from a **Balancing Contingency Event**.

**It may not be used for load being high.** The drafting record is explicit that this was a real
problem:

> *"Without a Balancing Contingency Event, a Responsible Entity cannot utilize its Contingency
> Reserve without violating the NERC Standard BAL-002. To resolve this conflict, the drafting team
> elected to allow the Responsible Entity to use its Contingency Reserve while in a declared
> **Energy Emergency Alert 2** [or] **Level 3**."*

**So the answer to "can you dip in for an outlier peak" is: not freely, but yes once an Energy
Emergency Alert Level 2 or 3 is declared** — and that permission had to be written in
deliberately, because before it, doing so was a standards violation.

### A live direction of travel worth noting

WECC has petitioned to **retire** its stricter regional requirement (BAL-002-WECC-3, which demands
the greater of MSSC or 3% of load plus 3% of generation), arguing entities there *"are holding more
reserves than the rest of the continent, even though there is no technical basis for doing so"* and
that **FERC Order 901** raises concern that *"holding excess reserves may be inhibiting reliability
across the interconnection."*

That cuts against any instinct to make our reserve constraint conservative by default.

### What it implies for our modelling choice

| product | may cover a high-load hour? | our equivalent |
|---|---|---|
| Planning reserve margin | yes — statistically | IRM at `t_peak` ✓ |
| Day-ahead scheduling reserve | **yes — explicitly sized for load forecast error** | none |
| Contingency reserve | **no**, except under declared EEA-2/3 | none |

`all_hours_reserve.py` enforces availability in every hour, which behaves like a **hard floor**.
That is stricter than any of the three above: contingency reserve is drawable under emergency, and
planning margin is probabilistic rather than hourly. **Worth checking whether the implementation
permits any drawdown, or whether it will force overbuild by treating reserve as untouchable in all
8,760 hours.**

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
- NERC BAL-002-2 Background Document (July 2015) — contingency reserve purpose; the EEA-2/3
  exception and why it was added
- NERC BAL-502-RF-03 — one-day-in-ten-years planning standard
- PJM Manual 13, via arXiv 2506.01358 — day-ahead scheduling reserve includes load forecast error
- WECC-0142 white paper (Sept 2025) — petition to retire BAL-002-WECC-3; FERC Order 901 on excess
  reserves
