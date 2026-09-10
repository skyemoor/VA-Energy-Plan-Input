# Dominion Energy Virginia DLC/DR Program Parameters — Sourced 2026-08-24

Real program details fetched directly from Dominion's own program pages and administrator portals,
grounding this project's A.2 (incentive-based DR / DLC) modeling in actual, current program design
rather than assumed/generic figures. All three programs are mutually exclusive with each other at
the individual-customer level (a customer cannot enroll in more than one), per each program's own
stated eligibility rules.

## 1. Smart Thermostat Rewards (space heating/cooling DLC) — user's own decision: model as DLC

**Source**: dominionenergy.com/virginia/save-energy/my-home/smart-thermostat-rewards, and the STR
Events page (dominionenergy.com/en/Virginia/Save-Energy/My-Home/STR-Events), fetched directly.

- **Mechanism**: utility-initiated "energy events" — brief thermostat adjustments during high-demand
  periods. FERC-DLC by definition (§7.5), not price-based.
- **Incentive**: $25 signup rebate + $25/yr continued-participation rebate. Separately, $50 instant
  rebate on eligible thermostats purchased through Dominion's marketplace.
- **Eligible brands**: Amazon, Ecobee, Google Nest, Honeywell Home, Sensi.
- **Magnitude constraint**: explicitly stated as "a few degrees" from the customer's usual setting —
  a real, published ceiling on per-event adjustment depth.
- **Opt-out**: customers can opt out of any individual event — directly confirms the participant-
  override risk already established in this project's own §7.5 research (Wildstein, Craig &
  Vaishnav: overrides can halve DLC reliability value) is an active, real feature of this specific
  program, not just a theoretical risk.

**Real event history, 2021-2026 (six full years, from the STR Events page directly)**:

| Year | Events | Total hours |
|---|---|---|
| 2021 | 25 | 71 |
| 2022 | 25 | 73 |
| 2023 | 23 | 60 |
| 2024 | 20 | 56 |
| 2025 | 17 | 50 |
| 2026 (YTD, through 8/17) | 18 | 52 |

**Observed pattern across all six years**: overwhelmingly summer (June-August), with rare winter
exceptions (1/22/2025 6-9am; 12/4/2024 6-9am). Time-of-day overwhelmingly mid-afternoon to early
evening — most commonly 3-6pm or 4-7pm windows. Per-event duration typically 2-3 hours (occasional
4-hour events in 2021). This is real, empirical, dated/timed event data — a direct foundation for
DLC's own event-trigger definition, not a modeled proxy.

## 2. EV Charger Rewards (EV charging DLC) — the model for smart thermostats, per user's own decision

**Source**: chargingrewards.com/dominionenergy-ev/ and its FAQ page (Dominion's own program
administrator, EnergyHub), cross-confirmed by Dominion's own program pages and AFDC.

- **Mechanism**: "you'll allow Dominion Energy to control your EV charging during peak hours" —
  explicit, direct remote control. FERC-DLC by definition, same as Smart Thermostat Rewards.
- **Incentive**: $125 one-time equipment rebate (must apply within 60-120 days of charger purchase —
  minor discrepancy across sources on the exact window) + $40/yr ongoing rebate after each
  program-participation anniversary.
- **Eligible equipment**: qualifying Level 2 chargers (ChargePoint or JuiceBox brands specifically
  named).
- **Event timing, explicitly published**: "Adjustment events can occur any day of the week except
  holidays. Typical event times are between 2-7pm during the summer and between 5-10am and 2-7pm
  during the winter." This is a genuinely broader window than Smart Thermostat Rewards -- the EV
  program has an explicit, regular WINTER MORNING window (5-10am) in addition to the afternoon/
  evening window, not just the rare exceptions seen in STR's own event history. Directly consistent
  with this project's own already-established Winter Storm Fern / §7.6 finding that winter morning
  hours are a genuine stress period, not just a summer-afternoon phenomenon.
- **Maximum 45 energy events per year** — an explicit, published cap, substantially more frequent
  than Smart Thermostat Rewards' ~17-25 events/yr (consistent with EV charging being a more
  flexible, less comfort-sensitive load than space heating/cooling).
- **Opt-out**: same as Smart Thermostat Rewards — customers can opt out via the charger or its app
  at any time.
- **Eligibility constraint**: must be on a standard rate structure, NOT enrolled in the Off-Peak Plan
  (a separate, existing time-of-use rate) — real mutual-exclusivity, same pattern as PTR below.

## 3. Peak Time Rebates (PTR) — a GENUINELY DIFFERENT mechanism, not DLC

**Source**: dominionenergyptr.com, fetched directly.

**This is not the same mechanism as the two DLC programs above — worth being precise about the
distinction, not folding it in.** PTR is voluntary, customer-initiated conservation in response to
an event notification, NOT remote utility control of equipment. FERC's own taxonomy (§7.5) would
classify this as incentive-based DR, but specifically the non-DLC subtype (voluntary curtailment/
demand bidding), distinct from the direct-control mechanism DLC requires by definition.

- **Mechanism**: customers receive a text/email notifying them of a scheduled event, then voluntarily
  choose what actions to take (or none at all) — no remote control of any device.
- **Incentive**: rebate calculated from a customer-specific BASELINE (highest 4 of the 5 most recent
  weekday hourly averages, weather-adjusted) vs. actual usage during the event. **$1.25 per kWh**
  reduced below baseline. No penalty for non-participation or for using more than baseline.
- **Frequency**: "about 10 events a year," each "around three or four hours" — explicitly published.
- **Timing**: "typically when the weather is very hot (summer afternoons) or very cold (winter
  mornings or early evenings)" — same summer/winter dual-season pattern as the EV program.
- **Mutual exclusivity, explicit**: cannot be enrolled in PTR simultaneously with Smart Thermostat
  Rewards, EV Charger Rewards (referred to here as "EV Telematics Rewards"), Water Energy Rewards,
  or Net Metering. A customer picks one program, not several — directly relevant to any future
  modeling of program enrollment/overlap, since these are NOT additive across a single customer base
  the way three independent, freely-combinable programs would be.

## Implication for this project's own modeling, not yet acted on

Per direct user decision this session: smart thermostats modeled as DLC, matching the EV Charger
Rewards program's own real mechanism (rather than splitting thermostats between DLC and price-
responsive/A.1 treatment, which was the theoretically-possible but more complex alternative
discussed immediately prior to this decision). PTR remains a separate, third mechanism — real and
worth tracking, but not yet decided whether it factors into this project's own scope at all, since
it wasn't part of the original three-item list (smart thermostats, EV charger control, C&I BEMS).

## 4. EV Charger Rewards per-participant kW magnitude — bottom-up estimate, since Dominion doesn't publish this directly

**Full chain** (see `dlc_analysis/dlc_assumptions.py` for the sourced/tested implementation,
`Internal_Debugging_Log.md` #63 for the full derivation record):

| Step | Value | Basis |
|---|---|---|
| Virginia daily VMT/driver | 28.10 mi/day | truedrivingcost.com, FHWA PS-1 2024 + 2020 Census |
| EV efficiency | 0.375 kWh/mile | Recurrent 2026-model-year EPA-based average |
| Daily charging energy need | 10.54 kWh/day | Derived |
| Charger power (Level 2 midpoint) | 9.0 kW | Stated midpoint; user's own JuiceBox model unspecified |
| Active charging session length | 1.17 hours | Derived |
| Event window | 3:00pm-6:00pm (3 hrs) | Locked in via NoVA rush-hour (~3:15pm start) + dinner-time local knowledge |
| Probability active during event | 39.0% | Derived |
| **Expected kW reduction per participant** | **~3.51 kW** | Derived, gross figure |

**Not yet applied**: the participant-override discount (Section "7.5 Direct Load Control vs.
price-based signals" of `Scenario3_Scope_and_Gaps.md` — overrides can halve DLC reliability value)
and any enrollment/penetration rate. This is a per-participant, gross figure, not yet scaled to an
aggregate MW total for the model.

**Sourcing detail on the override-discount citation, confirmed directly (2026-08-24)**: Wildstein,
Craig & Vaishnav, "Participant overrides can halve the reliability value of direct load control
programs," *Energy & Buildings* 299 (2023), derived from Wildstein's own University of Michigan
master's thesis (April 2022). The underlying empirical data is a **single-summer snapshot**: 403
Ecobee smart thermostats enrolled in Southern California Edison's 2019 Summer Smart Energy Program
(five-minute AC data via Ecobee's Donate Your Data initiative). Headline finding: SCE's 2019 program
achieved a 41% AC-demand reduction from DLC, but lost 48% of potential additional reduction to
override behavior. **Worth flagging plainly before this gets applied to the Dominion calculation**:
single summer, single utility, Southern California (not Virginia), n=403 — a real and well-
documented effect, but one data point from one place/year, not a general, directly-transferable
constant.
