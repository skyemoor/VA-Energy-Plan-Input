# Meeting Virginia's Clean Energy Requirements Under Doubled Demand
## Compliance Pathways, Costs, and Where the Statute Needs Attention

**A working draft prepared as input to the Virginia Energy Plan**
*Version 0.1 — outline and initial text — 2026-09-10*

---

> **Status of this draft.** This is an outline with initial text, not a finished paper. Figures
> marked *(provisional)* rest on stated limitations and should not be quoted as settled; see
> `registers/Provenance_Register.xlsx` for the status of every number. Sections marked
> **[TO WRITE]** are placeholders.

---

## How to read this document

Four tiers, each self-contained:

| Tier | Audience | Length |
|---|---|---|
| **Part I — Executive Summary** | Legislators, Governor's office and staff | ~3 pages |
| **Part II — Technical Summary** | Senior Department of Energy staff | ~8 pages |
| **Part III — Main Body** | Agency staff, county officials, utility and stakeholder engineers | ~30 pages |
| **Part IV — Appendices** | Energy modelers; published in full in the public repository | — |

All modeling code, input data, statutory text, and results are public and reproducible at
`github.com/skyemoor/VA-Energy-Plan-Input` (Apache-2.0 for software, CC BY 4.0 for documents
and data). Every figure can be independently regenerated from public sources.

### Mapping to the statutory Plan elements

§ 45.2-1710(B) enumerates twelve elements the Virginia Energy Plan must include. This paper
addresses the following directly:

| § 45.2-1710(B) element | Addressed in |
|---|---|
| B.1 — Projections of energy consumption and costs | Part III §3, §7 |
| B.2 — Adequacy of generation, transmission, distribution; how distributed energy resources affect the Commonwealth | Part III §5, §6, §9 |
| B.3 — Siting requirements; **state and local impediments to expanded use of distributed resources, and recommendations to reduce or eliminate such impediments** | Part III §8, §9; Part I recommendations |
| B.4 — Fuel diversity, flexibility in meeting future capacity needs | Part III §4, §5 |
| B.5 — Efficient use of energy resources and conservation initiatives | Part III §7 |
| B.12 — **Recommendations for legislative, regulatory, and other public and private actions** | Part I §5; Part III §10 |

Elements B.6–B.11 (regional initiatives, environmental justice siting analysis, EPA § 111(d),
greenhouse gas inventory, electric vehicles, charging infrastructure) are outside this paper's
scope and are noted here so the gap is explicit rather than implied.

---
---

# Part I — Executive Summary

*For legislators, the Governor's office, and their staff.*

## 1. Why this analysis exists

The Virginia Clean Economy Act and the Renewable Portfolio Standard set a legally binding path to
100 percent clean electricity for Dominion Energy Virginia by 2045. Both were enacted in 2020,
against demand projections that have since roughly doubled — driven overwhelmingly by data
centers.

Two things follow that the General Assembly has not yet had analysis on.

**First, no current planning document reflects current law.** HB 895 / SB 448, signed April 13,
2026, raised Dominion's energy storage requirement to 16,000 MW of short-duration and 4,000 MW of
long-duration capacity by 2045. Dominion's most recent Integrated Resource Plan, filed October 15,
2025, carries **2,000 MW** — roughly a tenth of what the law now requires. The 2026 IRP cycle
cannot close that gap, because the legislation post-dates the filing's own input cutoff. Meanwhile
the utility is actively seeking approval for approximately 6,500 MW of new gas generation.

**Second, the statute already contains its own answer to the affordability question — and it may
not be the answer legislators intend.** § 56-585.5(D)(5) caps the cost of non-compliance at $45
per megawatt-hour, escalating one percent annually, reaching roughly **$57/MWh by 2045**. Our
modeling puts the physical cost of a fully clean 2045 system near **$133/MWh** *(provisional)*.
A utility facing that gap can lawfully pay the deficiency instead of building. **The question is
not only whether 100 percent is achievable; it is whether the statute as written creates a
sufficient incentive to try.**

## 2. What we did

We built a physical, hour-by-hour model of the Dominion zone — 8,760 hours per year, real
historical weather, no representative-day shortcuts — and tested candidate resource portfolios
against **eight real historical weather years** run continuously, with storage state carried
across year boundaries rather than reset annually.

Everything uses public data: NREL irradiance, NOAA weather, PJM market data, Dominion's own filed
projections. Any party can reproduce it.

This is deliberately **not** a competing Integrated Resource Plan. It is an independent check on
what enacted law requires, offered during a window in which the utility's own planning process
legitimately cannot reflect it.

## 3. Principal findings

**[TO WRITE — pending completion of the corrections identified in §11]**

The following are stated as provisional findings and are expected to change in magnitude, though
we do not expect the direction to change:

1. **Statutory compliance and physical decarbonization are different targets, and the gap is
   large.** Under § 56-585.5, the 2045 obligation covers roughly **148 TWh**; physically serving
   all load with clean generation requires roughly **206 TWh** *(provisional)*. The difference
   arises because the statute excludes existing in-Commonwealth nuclear from the compliance base,
   permits certificates from anywhere in PJM, and caps the cost of falling short.

2. **The largest single lever is not generation — it is who is counted.** Commercial and
   industrial customers with more than 25 MW of aggregate load who procure their own clean energy
   are removed from the utility's compliance base entirely (§ 56-585.5(G)). Applied to the data
   centers driving demand growth, this alone moves the 2045 obligation from 148 TWh to
   **108 TWh** *(provisional)* — from 72 percent of the physical requirement to 53 percent.

3. **Long-duration storage is a seasonal, not a daily, resource — and the distinction changes the
   sizing.** Testing against eight real weather years, the binding constraint was a continuous
   **90-day winter drawdown**, not a short outage. Storage charged through spring and summer and
   ran down from late October to late January. Sizing for daily cycling would not have revealed
   this.

4. **In 2030, additional storage cannot help much, because there is nothing to charge it with.**
   At the clean-energy penetration the statute requires for 2030, the existing storage fleet
   already captures **75 percent of all surplus clean energy that physically exists**. This is a
   generation problem before it is a storage problem.

5. **Parking canopies and rooftops are statutorily favored and materially under-used.**
   § 56-585.5 defines "previously developed project site" to expressly include parking lots and
   parking-lot canopies, and requires at least 1,000 MW of the 16,100 MW solar requirement to be
   sited on such land. Our four-county assessment of Northern Virginia found roughly
   **4,600–5,400 MW** of technical potential in those jurisdictions alone.

## 4. What this means for the legislature

**[TO WRITE — to be developed once §3 findings are final]**

Framing to develop:
- The compliance question and the affordability question are the same question, connected by the
  deficiency payment
- Whether the 2045 date, the percentage, or the cost cap is the right lever to adjust
- What the accelerated-clean-energy-buyer mechanism implies for data-center policy

## 5. Recommendations

**[TO WRITE]**

Candidate recommendations, to be finalised:

1. **Commission modeling that reflects enacted law before approving long-lived gas assets.** The
   plants now in permitting will operate for decades on planning that predates the storage
   mandate.
2. **Resolve the deficiency-payment ceiling deliberately.** At present the statute permits a
   lawful outcome — pay rather than build — that is inconsistent with its own stated purpose.
3. **Remove identified impediments to distributed resources** (§ 45.2-1710(B)(3) requires the Plan
   to do this). Specific candidates in Part III §9.
4. **Clarify the accelerated-clean-energy-buyer pathway** as deliberate data-center policy rather
   than leaving it as an incidental exemption.

---
---

# Part II — Technical Summary

*For senior Department of Energy staff.*

## 1. Scope and method

**[TO WRITE]** Cover: hourly LP formulation; eight-year chronological weather validation; the
dual-basis compliance treatment; what is and is not optimized.

## 2. The two compliance bases, and why both are reported

Virginia's requirement can be measured two ways, and they are not the same quantity.

**Physical clean-generation requirement.** What fleet must exist so that a given percentage of
electricity *generated* is carbon-free. Existing nuclear counts toward the clean share. At 100
percent this requires new and existing clean resources to cover all load.

**Statutory RPS obligation** (§ 56-585.5). How many renewable energy certificates the utility must
*retire*. The base is Virginia retail sales, **less** energy from in-Commonwealth nuclear plants
operating by July 1, 2020, **less** certified accelerated clean energy buyer load, **less**
§ H legacy competitive-service customers. Certificates may originate anywhere in PJM, with at
least 75 percent from Virginia-located resources beginning in 2027.

Reporting only the first overstates what the law compels. Reporting only the second says nothing
about whether the lights stay on, because certificate retirement is an accounting act. This paper
reports both throughout, and treats the **gap between them** as a finding in its own right.

## 3. Reliability treatment

**[TO WRITE]** Cover: reserve margin methodology and its relationship to PJM's ELCC; the
capacity-versus-energy distinction the eight-year testing exposed; what is not modeled
(probabilistic resource adequacy, forced outages, load forecast error).

## 4. Cost framework

**[TO WRITE]** Cover: SLCOE construction; NPV comparability with the IRP's own 6.62 percent
discount rate; the National Standard Practice Manual framing for demand-side resources; social
cost treatment and the § 56-585.1(A)(6) direction to the Commission.

## 5. Principal quantitative results

**[TO WRITE — pending corrections in Part III §11]**

## 6. Known limitations

Stated plainly, because they bound what this work supports:

1. Build optimization uses a single design weather year; cross-testing against eight historical
   years is validation, not sizing.
2. No probabilistic resource adequacy — no loss-of-load expectation, no forced outages, no load
   forecast error. Industry practice is LOLE ≤ 0.1 day/year; this paper cannot state the
   reliability level its portfolios achieve.
3. The investment model (linear program, perfect foresight) and the dispatch validation model
   (heuristic, no foresight) differ. That gap has not been fully quantified.
4. Single-node — no transmission representation, which the transmission-avoidance objective
   requires.
5. No technology cost-decline curves applied to 2045; costs are likely conservative.
6. REC banking under § 56-585.5(C)(4) is not modeled.

**This paper is intended to induce deeper modeling, not to substitute for it.** Its most useful
output may be a specification of what a rigorous effort must address.

---
---

# Part III — Main Body

## 1. Introduction and statutory framework
**[TO WRITE]** § 56-585.5, § 45.2-1706.1, and the 2026 amendments. Full text in Part IV.

## 2. The demand question
**[TO WRITE]** Growth since 2020; data-center concentration; what "doubled" means precisely and
on what basis. Draws on `docs/methodology/Demand_Basis_and_RPS_Compliance_Working_Notes.md`.
*Addresses § 45.2-1710(B)(1).*

## 3. Scenarios

Scenarios are named for what they do, not numbered by preference. Internal code identifiers
(`S1`, `S2`, and so on) are retained unchanged in the model, filenames, and test baselines; the
mapping is in the table below and in the repository README.

| Presentation name | Code | Definition |
|---|---|---|
| **Build to Zero** | S1 | Physical 100 percent clean generation by 2045. Solar and storage only; no new gas. |
| **Build to Zero, 2045 Gas Exception** | S1B | Identical to Build to Zero through 2044; permits up to 5 percent gas generation from 2045. |
| **Statutory Floor** | S2 | Builds exactly the minimums § 56-585.5 names — 16,100 MW solar (D.2), 16,000 MW short-duration and 4,000 MW long-duration storage (E.2, E.4) — and serves remaining demand with the existing and expanded gas fleet. |
| **Distributed Build** | S3 | Build to Zero, weighted toward rooftop, parking-canopy, and agrivoltaic siting, with distributed owners participating in PJM markets under FERC Order 2222. |
| **Moderated Demand** | S5 | Lower data-center growth trajectory. |
| **Utility Preferred Plan** | — | Dominion's filed 2025 IRP portfolio, evaluated on this paper's own method for comparability. **Not yet built.** |

Two points about these definitions matter for reading the results.

**"Statutory Floor" is not a small portfolio.** Following HB 895 / SB 448 it includes 20,000 MW of
storage — roughly ten times what the utility's current plan contemplates. The name describes what
the law compels, not the size of the build.

**Compliance is not binary.** Build to Zero achieves physical 100 percent clean generation.
Statutory Floor may satisfy the § 56-585.5 obligation through certificate retirement while still
burning gas, or by paying the § 56-585.5(D)(5) deficiency. Both can be lawful. This paper reports
the physical and statutory measures separately throughout rather than labelling one scenario
"compliant" and another not.

**The Utility Preferred Plan is included because the current comparison lacks it.** Dominion's
filed plan carries 2,000 MW of storage against a 19,480 MW statutory requirement — placing it
*below* the Statutory Floor. Without this scenario the paper compares against a counterfactual no
party is actually proposing.

## 4. Resource adequacy under real weather
**[TO WRITE]** The eight-year continuous test; the seasonal storage finding; the capacity-versus-
energy distinction. *Addresses § 45.2-1710(B)(2), (B)(4).*

## 5. Storage
**[TO WRITE]** Short- versus long-duration; the § 56-585.5(E) duration definitions and their
modeling consequences; the 2030 charge-starvation finding.

## 6. Cost results
**[TO WRITE]** SLCOE by scenario; NPV comparison with the IRP; social cost; RGGI.
*Addresses § 45.2-1710(B)(1).*

## 7. Demand-side resources
**[TO WRITE]** NSPM framing; measure-level analysis; what was scoped in and out and why.
*Addresses § 45.2-1710(B)(5).*

## 7A. Pricing demand-side incentives so customers capture the savings

*A substantive section in its own right, not a subsection of §7.*

**The argument.** A demand-side program's incentive should reflect the value it delivers to the
system. Where it does not, the customer bears the inconvenience while the utility and its other
ratepayers capture the surplus — and participation stays low, so the resource never scales to the
level the reliability analysis in §4 shows is needed. This is NSPM Principle 2 applied directly:
if DERs are to be treated as a utility system resource, they must be *valued* like one.

**Two independent lines of evidence, deliberately kept separate.**

**(a) Peer utility comparison** — the stronger of the two, because it is utility-to-utility rather
than model-derived, and needs no methodology to be accepted.

Non-residential curtailment, $/kW-yr *(Cross_State_Commercial_Curtailment_Incentive_Comparison)*:

| Utility | $/kW-yr | Multiple of Dominion |
|---|---:|---:|
| **Dominion (VA)** | **$36** | **1.00×** |
| Hawaiian Electric | $60 | 1.67× |
| NYSEG (capacity component) | $49–52 | 1.37–1.45× |
| Puget Sound Energy | up to $130 | 3.61× |
| PG&E BIP / CBP | $50–200 | 1.39–5.56× |
| **Con Edison Smart Usage Rewards** | **$216–300** | **6.00–8.33×** |

Residential battery/VPP *(Cross_Utility_VPP_Compensation_Comparison)*: Dominion pays a flat
**$294/year, size-independent** — meaning a larger battery earns no more than a small one, which
removes any incentive to size for grid value. Green Mountain Power pays ~$850/year plus
$850–1,050/kW upfront; Massachusetts ConnectedSolutions works out to roughly $1,375/year on a 5 kW
example. Third-party benchmarks *(ThirdParty_VPP_DERA_Compensation_Benchmarks)* show Tesla-operated
programs at $80–275/kW seasonal across seven utilities.

**(b) Avoided-cost benchmark** — what the incentive *should* be if it reflected system value.

Current EV Charger Rewards compensation sits roughly **12–20× below** a properly-priced benchmark
built from avoided capacity plus avoided energy. **[FIGURE PENDING RE-DERIVATION]** — see the
correction note below; do not use the 70–115× figure that appears in earlier working material.

**Structural observations that matter more than the levels.**

1. **Flat, size-independent payments** (Dominion residential, $294/yr) sever the link between
   incentive and delivered value entirely. Every peer program that scales — $/kW, $/kWh, or
   per-event — preserves it.
2. **Backup reserve is unconfirmed.** Peer programs increasingly publish an explicit reserve
   state-of-charge the customer always retains (PG&E/Sunrun: 20%, published; APS: 20–50% implied;
   PG&E/Tesla: customer-set in-app). Dominion's is unconfirmed after two direct searches — a
   participation barrier independent of price.
3. **Energy performance contracting is available and underused.** § 45.2-1702 lets public bodies
   implement measures with no net budget impact, contractor-guaranteed. Requires no new
   legislation. Connects to § 56-585.5(C)(2)'s school-sited distributed carve-out.

**Recommendations to develop** *(addresses § 45.2-1710(B)(12))*: whether incentive levels should
be tied to a published avoided-cost methodology rather than set administratively; whether flat
payments should be replaced with value-scaled ones; whether backup reserve should be a published
program term.

**Correction note for drafting.** Working material computed the avoided-cost benchmark using
installed capital cost ($/kW, one-time) as though it were annual avoided capacity cost ($/kW-yr).
Properly annualized, the F-Class benchmark is ~$51/kW-yr rather than $713, and the aeroderivative
~$88/kW-yr rather than $1,175. Cross-check: PJM capacity has never cleared near $713/kW-yr — the
2025/26 record BRA was ~$98.5/kW-yr and the 2026/27 cap is $118.6/kW-yr, while the corrected
figures land inside that historical range. The qualitative finding survives comfortably; the
multiple does not. Full detail in `docs/methodology/`.

## 8. Distributed generation and siting
**[TO WRITE]** The four-county assessment; extrapolation and its limits; the statutory preference
for previously developed project sites. *Addresses § 45.2-1710(B)(3).*

## 9. Impediments to distributed resources
**[TO WRITE]** § 45.2-1710(B)(3) requires the Plan to identify these and recommend removing them.
Candidates: the 100 MW co-located solar-plus-storage cap and its transmission consequences;
interconnection process; data availability for independent verification.

## 10. Legislative and regulatory options
**[TO WRITE]** *Addresses § 45.2-1710(B)(12).*

## 11. Corrections and open items
**[TO WRITE]** Deliberately included. Documents what this analysis found wrong in its own prior
work and what remains unresolved — see `docs/Internal_Debugging_Log.md` for the full record.

---
---

# Part IV — Appendices

Published in full at `github.com/skyemoor/VA-Energy-Plan-Input`.

| | |
|---|---|
| A | Resource adequacy methodology |
| B | Cost assumptions |
| C | Scenario 2 methodology |
| D | Tiered social cost framework |
| E | Distributed energy resource owner economics |
| F | Known limitations |
| O | Demand shape and data-center flattening |
| — | Demand basis and RPS compliance working notes |
| — | Statutory text (§ 56-585.5, § 56-585.1:4, § 45.2-1701, § 45.2-1702, § 45.2-1706.1, § 45.2-1710) |
| — | Northern Virginia solar siting assessment |
| — | Weather-year selection and robustness |
| — | Internal debugging log |
| — | Provenance and citation registers |
