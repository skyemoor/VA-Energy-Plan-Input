# Reserves — this analysis's approach

**Reader-facing summary.** What reserve requirements this analysis imposes, what it does not, and
why. Written for a reviewer who will reasonably ask whether a 100%-clean Virginia system was held
to the same reliability standard as the system it replaces.

---

## Short version

| requirement | who holds it in reality | modelled here? |
|---|---|---|
| **Planning reserve margin** | Dominion, for the DOM Zone | **Yes — 17.7% (PJM IRM) at system peak** |
| **Day-ahead scheduling reserve** | PJM, sized for load forecast error + forced outages | No |
| **Contingency reserve** (NERC BAL-002) | **PJM**, as Balancing Authority and Reserve Sharing Group | No — see below |
| **Flexible / ramping capability** | PJM has no CAISO-style product | No |

---

## 1. Planning reserve margin — modelled

The build in every scenario must satisfy:

```
accredited capacity ≥ (1 + 0.177) × gross demand at the hour of maximum NET demand
```

This is PJM's Installed Reserve Margin. It is a **capacity adequacy** test — is enough capacity
*built* — and it is the constraint that sizes the fleet.

**Dominion procures rather than self-supplies.** It elected the Fixed Resource Requirement
alternative in 2021/22 and **terminated that election on 2 May 2024**, returning to the RPM capacity
auction; the 2025 IRP confirms current RPM participation. Under RPM the capacity obligation is met
by buying cleared capacity, not necessarily by building it.

**So requiring Virginia to build its own reserve margin is a conservative simplification**, and it
is stated as one. Two things limit how conservative it actually is:

- PJM cleared **134,205 MW** against a **134,414 MW** reliability requirement for 2026/27 — a
  shortfall, not a surplus. Buying capacity assumes someone else built it.
- Dominion describes the **DOM Zone as a net importer of energy**. Capacity that can be bought is
  not always capacity that can be delivered.

---

## 2. Contingency reserve — not modelled, and why that is defensible

NERC **BAL-002** requires contingency reserve sized to the **Most Severe Single Contingency**, held
to recover Area Control Error after a Balancing Contingency Event. It exists to replace *"capacity
and energy lost due to forced outages of generation or transmission equipment."*

**The obligation belongs to PJM, not to Dominion.** PJM is the Balancing Authority and operates as
a **Reserve Sharing Group**: the MSSC obligation is met jointly across members, and no single
utility holds its own most-severe-contingency worth of reserve. This is unaffected by the FRR/RPM
election, which governs capacity procurement rather than operating reserve.

**Modelling Virginia in isolation and requiring it to self-provide full MSSC reserve would
therefore overstate the requirement** — it would impose on one zone an obligation the region meets
collectively.

### The honest limits of this position

**Sharing is not exemption.** A Reserve Sharing Group allocates the obligation; members contribute a
share. The defensible statement is *"less than full MSSC,"* not *"none."* This analysis models
none, which is the opposite simplification from the one it avoids, and the effect is to make
capacity slightly cheaper than reality.

**Contingency reserve is not the only reason to hold hourly headroom.** BAL-002 addresses
generator and transmission outages. It does not address renewable forecast error or net-load ramps,
both of which grow with penetration. PJM's **day-ahead scheduling reserve** is explicitly sized for
*under-forecasted load-forecasting error* as well as forced outage rate — that requirement is also
not modelled here.

**Contingency reserve may be drawn on, but only under emergency.** BAL-002's drafting record is
explicit: without a Balancing Contingency Event, using contingency reserve *"would violate the NERC
Standard,"* and permission to use it during a declared **Energy Emergency Alert Level 2 or 3** had
to be written in deliberately. So it is a hard floor in normal operation, not a cushion.

---

## 3. What is not modelled, stated plainly

**No operating reserve constraint is active in any hour.** The planning margin binds at one hour —
system peak — and nothing constrains the other 8,759.

This has a consequence the reader should know about: **storage is free to discharge to its floor in
every hour.** In a least-cost optimisation with perfect foresight, it does, and the result is that
the model's internal hourly energy price has **zero variance** (measured: one unique value across
8,760 hours). Real Virginia nodal prices vary by $200–300 within a single day.

That does not affect least-cost capacity sizing, SLCOE comparison between scenarios, or
transmission-deferral conclusions. **It does mean this model should not be used to estimate
arbitrage revenue, scarcity rent, or what a storage owner would earn.** See
`docs/MODEL_WIDE_FINDINGS.md`.

**No CAISO-style flexible capacity requirement.** CAISO sizes a second, parallel requirement against
the *largest 3-hour net-load ramps*, in addition to peak-load planning. PJM has no equivalent
product and this analysis has no equivalent constraint. At high solar penetration the stressing hour
is likely an evening net-load ramp rather than gross peak, so **the single-peak-hour constraint may
be binding at the wrong hour.** This is an acknowledged limitation, not a resolved question.

---

## 4. Direction of travel worth noting

Reserve requirements are not moving toward strictness. **WECC has petitioned to retire** its
regional standard (BAL-002-WECC-3, requiring the greater of MSSC or 3% of load plus 3% of
generation), arguing entities there *"are holding more reserves than the rest of the continent, even
though there is no technical basis for doing so"* — and citing **FERC Order 901**'s concern that
*"holding excess reserves may be inhibiting reliability across the interconnection."*

A reviewer inclined to argue this analysis under-reserves should be aware the regulatory movement
runs the other way.

---

## 5. Summary for a skeptical reader

This analysis holds Virginia to a **capacity adequacy** standard — the full PJM planning reserve
margin, self-supplied, which is stricter than Dominion's actual RPM obligation.

It does **not** impose operating reserves, because those belong to PJM as Balancing Authority and
are met jointly across the Reserve Sharing Group.

The net effect is **conservative on capacity and permissive on operations**. Capacity results are
therefore usable; hourly price, arbitrage and scarcity results are not.

---

## Related

- `docs/MODEL_WIDE_FINDINGS.md` — the flat hourly dual, and the dormant all-hours reserve module
- `docs/research/CAISO_Net_Load_Treatment.md` — the three reserve products and the drawdown rules
- `docs/research/Dominion_FRR_RPM_Status.md` — FRR termination and what it implies for self-supply
