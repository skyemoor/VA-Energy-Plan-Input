# Appendix — Data Center Demand Flexibility (A.7): Existing Practices, Statutes, and Regulatory Structure

**Status: WORKING DOCUMENT, ALL THREE PARTS COMPLETE (existing practice; PJM's and Dominion's own
proposed measures; other proposed demand-reduction measures) — ready for the holistic review pass
across all three parts together, per direct user instruction, before this document is consolidated
and added to the main appendix set.**

Direct user framing for why this item is being pursued despite thinner sourcing than every other
demand-side item in this project: "an extremely sensitive political/tech topic with many billions
of dollars riding on it... we can always make a fully transparent assumption and let others argue
about which is going to be actually finalized." This document exists to lay out, with full sourcing,
what is verifiably real and current *before* any modeling assumption gets built on top of it.

---

## 1. Dominion Energy Virginia — existing practices, tariffs, and statutes

### 1.1 Dominion's C&I curtailment programs — two real, distinct programs under one page, previously conflated here and now corrected

**Correction (2026-08-24)**: this section originally described a single program. Fetching the full
page directly (not just search snippets) revealed **two separate, distinct programs** under the
"Targeted Sector Programs" umbrella, which had been merged into one description here. This is
corrected below, split into its own two subsections.

#### 1.1a The Non-Residential Curtailment Program — genuine operational load reduction, no backup generation required

This is the program actually analogous to residential DLC (same mechanism: temporarily reduce real
operational load, not switch to another power source) — the correct anchor for A.2 (extended), not
1.1b below.

- **Eligibility**: "designed for medium and large commercial and industrial customers, typically
  with peak demand of at least **100 kW** of curtailable load." Facilities with controllable loads —
  HVAC, lighting, refrigeration, industrial processes, pumping stations — are named as strong
  candidates.
- **No backup generation required** — this is a real, direct operational-load-reduction program, not
  a generator-switchover mechanism.
- **Compensation**: "participants receive **$36 per kW per year, paid monthly**" — confirming the
  originally-sourced figure was correct, but for this program specifically, not the one in 1.1b.
- **Event commitment**: customers "must be able to reasonably commit to following their curtailment
  plan when called (**10 to 20 times per year**)."
- **Curtailment mechanism, two participation modes**: manual (staff receive a notification and
  implement pre-agreed actions) or automated (building control systems adjust HVAC/lighting
  automatically during events).
- **Verification**: performance validated via AMI data, interval metering, or approved engineering
  calculations — customers are paid for actual, measured load reduction.
- **Typical curtailment strategies, directly listed**: HVAC temperature resets/reduced fan
  speeds/supply air modifications; lighting dimming in non-essential areas; slowing or pausing
  industrial processes; cycling refrigeration compressors or reducing pump loads.
- **Mutual exclusivity**: cannot simultaneously enroll in Schedule 10, PJM peak-shaving programs, or
  the Distributed Generation program (1.1b below). Must be on standard GS rates, paying into the T&D
  rider C1A.
- **Program administrator**: Clearesult (contact: BusinessCurtailment@clearesult.com), not
  PowerSecure — a different vendor than 1.1b.

#### 1.1b The Non-Residential Distributed Generation Program — backup-generation switchover, the original mechanism already documented, now correctly separated from 1.1a

This is the program already documented in earlier entries this session (the ≥200 kW backup-
generation-required, PowerSecure-managed mechanism) — confirmed as real and distinct from 1.1a, not
the same program.

- **Eligibility**: non-residential customers on rate schedules *other than* Schedule CS, Schedule
  SG, Schedule 10, Schedule DP-1, or Schedule DP-2, with backup generation facilities of **200 kW or
  greater**, either owned or under a lease used as a financing instrument.
- **Mechanism, confirmed directly and precisely**: "switch their power source from the Dominion grid
  to a backup generator for a limited number of hours each year" — up to **120 hours per year** total
  (previously not precisely quantified in this appendix). A "control event" may be called with at
  least 30 minutes' notice to PowerSecure, typically lasting 4-6 hours, though some events can run
  longer within the 120-hour annual cap.
- **Compensation, now precisely quantified (correcting the earlier, less precise "$36/kW/yr" figure
  that had been applied to this program in error)**: Monthly Participation Payment = Load
  Curtailment Capability Payment + (Diesel Fuel Payment or Natural Gas Fuel Payment) + Variable
  O&M Adder, where:
  - Load Curtailment Capability Payment = **$8.25/kW-month** of committed curtailment capacity
    (≈$99/kW/year on the capacity component alone, before fuel/O&M).
  - Diesel Fuel Payment = (EIA Ultra-Low Sulfur No. 2 Diesel Index Price / 0.14) × Generator Heat
    Rate (MMBtu/MWh) × Generator Output (MWh), reimbursing actual fuel burned.
  - Natural Gas Fuel Payment = EIA Henry Hub Spot Price ($/MMBtu) × Generator Heat Rate (10
    MMBtu/MWh, stated directly) × Generator Output (MWh).
  - Variable O&M Adder = **$3.75/MWh** of metered dispatched output, escalating annually.
- **Program administrator**: PowerSecure International (contracts, payments, remote operation of
  enrolled generators) — different vendor than 1.1a's Clearesult.
- **Regulatory basis**: approved by the Virginia SCC for a five-year period.
- **Mutual exclusivity**: cannot simultaneously enroll in any other Dominion, PJM, or third-party
  load curtailment program.

**Published event windows and full event history (2023-2026), applying to 1.1b specifically, per the
separate "Curtailment Notices" page**:
- **Summer**: May 16 – September 30, potential operation 2:00 p.m. – 9:00 p.m., **maximum 19
  requests**.
- **Winter**: December 1 – March 31, potential operation 6:00 a.m. – 11:00 a.m. and 5:00 p.m. –
  10:00 p.m. (a same-day morning-and-evening call counts as two separate requests), **maximum 13
  requests**.

**Full, real, dated event history (2023-2026), fetched directly from Dominion's own live page**:

| Season | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|
| Summer events | 19 | 19 | 19 | 19 |
| Winter events | — | 1 | 6 | 2 |

Full date lists preserved (not just counts) since the specific dates are what enable cross-checks
against the other DLC programs already sourced this session:

- **2026 Summer** (19 events, all 2:00pm-9:00pm): Jun 11, 12, 18; Jul 1, 2, 3, 4, 5, 15, 16, 17;
  Aug 6, 7, 8, 9, 10, 11, 13, 17.
- **2026 Winter** (2 events): Jan 27 (6:00-11:00am), Jan 30 (6:00-11:00am).
- **2025 Summer** (19 events): Jun 12, 22, 23, 24, 25, 26; Jul 8, 15, 17, 24, 25, 26, 28, 29, 30;
  Aug 14, 17, 20; Sep 5.
- **2025 Winter** (6 events): Jan 20 (both AM and PM = 2 requests), 21, 22 (both AM and PM), 23.
- **2024 Summer** (19 events): Jun 18, 20, 21, 22, 23, 24, 25, 26; Jul 5, 6, 8, 9, 10, 15, 16, 17,
  31; Aug 1, 5.
- **2024 Winter** (1 event): Jan 17.
- **2023 Summer** (19 events): Jul 3, 5, 12, 13, 17, 18, 21, 26, 27, 28, 29; Aug 7, 12, 13, 14, 21,
  25, 26; Sep 5.

**Cross-check performed directly against this project's own already-sourced residential DLC event
data (entries #63/#65), not assumed**: the 2026 summer C&I curtailment dates are nearly identical to
the already-known 2026 Smart Thermostat Rewards / EV Telematics Rewards dates (Jun 11, 12, 18; Jul
1, 2, 3, 15, 16, 17; Aug 6, 7, 10, 11, 13, 17 — the large majority overlap exactly). This is now the
**third** independent program confirming the same pattern: Dominion appears to call a single,
system-wide stress condition that triggers multiple DR/curtailment programs simultaneously, not
independent per-program logic. However, the C&I curtailment list includes **four additional dates**
the residential programs don't share (Jul 4, Jul 5, Aug 8, Aug 9) — worth flagging as a real,
unexplained difference rather than glossing over it: this program is called somewhat more often than
the residential DLC programs, suggesting either a slightly lower activation threshold, or additional
localized/distribution-level events layered on top of the shared system-wide ones.

**Open question, not yet resolved**: whether large data centers specifically participate in this
program. The 200 kW backup-generation eligibility threshold is easily met by hyperscale data center
campuses (which typically run substantial on-site diesel backup for their own reliability purposes
independent of any DR program), making them structurally *eligible* — but no source found confirms
actual data-center enrollment or participation rates in this specific program.

### 1.2 Other real, existing Dominion rate schedules and tariffs relevant to large loads

- **Schedule CS ("Curtailable Service")** and **Schedule SG**: named as separate, pre-existing rate
  schedules in the Targeted Sector Programs eligibility exclusion list. Full terms not yet directly
  sourced (the Dominion rates-and-tariffs search did not surface the schedule's own filed tariff
  document directly) — flagged as a gap for a future, more targeted search if this schedule turns
  out to be directly relevant to data-center-scale curtailment specifically, given its name suggests
  it may be the more direct "sell curtailability for a lower base rate" mechanism, structurally
  different from the backup-generation-switching program in 1.1 above.
- **Schedule 10**: a real, existing rate schedule with an explicit exclusivity clause — "not
  available to Customers electing to participate, either directly or indirectly through a
  third-party curtailment service provider, in any PJM Interconnection, LLC Demand Response Program
  or any Company-sponsored peak-shaving demand response program." Applies to customers with peak
  demand ≥500 kW. Confirms Dominion structurally separates its own rate schedules from DR-program
  participation at the tariff level, not just as a policy preference.
- **Schedule CFG (Carbon-Free or Renewable Generation Supply Service)**: a voluntary, non-DR-related
  tariff allowing customers to purchase up to 100% of net energy/RECs from a new carbon-free
  facility built by Dominion on the customer's behalf, or via a Dominion-arranged PPA. Available to
  large (>500 kW) non-residential customers. Not a curtailment/flexibility mechanism — noted here
  only as another real, existing large-customer tariff structure for completeness.
- **GS-2/GS-2T/GS-3/GS-4 on-peak demand structure** (pre-GS-5, still the schedule most current large
  loads sit under until GS-5 takes effect): on-peak generation demand charges run ~$8.976/kW-month
  under GS-3, with on-peak windows defined as June-September 10am-10pm and October-May 7am-10pm,
  Monday-Friday. This is the economic backdrop against which any voluntary load-shifting behavior
  by a large customer *not* enrolled in a formal DR program would already be incentivized — trimming
  100 kW of on-peak demand saves roughly $900/month under this structure alone, independent of any
  DR/curtailment program enrollment.

### 1.3 The GS-5 rate class — real, enacted, but a cost-allocation mechanism, not a demand-flexibility mechanism

**Directly answers the user's own question about "a new law that puts data centers in a different
rate structure."** This is real and enacted, not proposed:

- **Approved**: Virginia SCC final order, Dominion's 2025 Biennial Review (Case PUR-2025-00058),
  November 25, 2025.
- **A real, structural reason GS-5's own published rate figures are not yet publicly available,
  confirmed directly from Dominion's own cover letter to the SCC (Dec. 9, 2025, PUR-2025-00058)**:
  the Final Order required two separate filings, not one. Per Ordering Paragraph No. 3, Dominion's
  December 9, 2025 filing covers rates effective **January 1, 2026** only. Per Ordering Paragraph
  No. 4, a **separate** filing covering rates effective **January 1, 2027** — the year GS-5 itself
  takes effect — is due "at least 45 days in advance of the effective date," i.e. roughly
  **mid-November 2026**. As of this project's own session date (August 24, 2026), that filing is
  still about three months from its own deadline and may not yet exist as a published document. Any
  attempt to locate GS-5's own actual, filed rate figures (as opposed to the terms already documented
  below — threshold, minimum-take percentages, contract length) should account for this: the
  December 2025 filing structurally cannot contain them, regardless of how it is searched or
  screenshotted, since GS-5 did not yet exist as an active rate schedule at the time that filing was
  made.
- **A related, directly-connected mechanism identified through this same cover letter**: the filing
  also includes "revised terms and conditions, rate schedules, and **Rider D – TERF**." TERF is the
  **Tax Effect Recovery Factor**, confirmed via Dominion's own North Carolina tariff documentation as
  applying specifically to CIAC (Contribution in Aid of Construction) payments — the same mandatory
  CIAC mechanism already documented above and in Section 6.3a. This appears to be the tax-treatment
  rider that accompanies GS-5's own mandatory CIAC payments, though this specific confirmation comes
  from a sister-state (NC) tariff page, not a directly-confirmed Virginia-specific source — the
  underlying tax-recovery concept is very likely identical across Dominion's subsidiaries, but this
  has not been independently verified against Virginia's own tariff language.

- **Effective**: January 1, 2027.
- **Scope**: customers with demand ≥25 MW *and* an average annual load factor ≥75%. Most of
  Dominion's ~450 data centers are expected to fall under this class.
- **Terms**: 14-year contracts; minimum payment of 85% of contracted transmission/distribution
  demand and 60% of generation demand, regardless of actual usage; collateral of $1.5 million per
  MW booked.
- **Purpose, stated directly by the SCC and Dominion**: cost allocation and stranded-cost risk
  protection for other ratepayers — ensuring data centers pay for the infrastructure built to serve
  them, not a mechanism to induce load reduction or flexibility. **This is a billing/cost-recovery
  structure, not a DLC/DR mechanism** — worth being precise about this distinction, since it's easy
  to conflate "new data center rate class" with "new data center demand-response program." They are
  different things addressing different problems.
- **Legislative context**: a related but separate effort, SB 253 (Sen. Louise Lucas), would let the
  SCC shift additional distribution/capacity-auction costs onto the GS-5 class specifically, cleared
  the Senate, still moving through the House as of this research (2026). Same cost-allocation
  purpose as GS-5 itself, not a flexibility mechanism either.

### 1.3a Direct attempts to source GS-5's actual filed dollar figures — one real comparison table obtained (GS-3, not GS-5), one genuine GS-5 table obtained but internally inconsistent, both flagged rather than used uncritically

Documented directly because real effort went into sourcing this and the results are genuinely mixed
— worth preserving the full picture rather than only the clean parts.

**Attempt 1 — a full GS-3 rate comparison table, screenshotted directly from Dominion's own
December 9, 2025 SCC filing (Case PUR-2025-00058, document control number 251220100)**. This table
was initially mislabeled "GS-5" by whoever saved the file, but its own header clearly reads
"SCHEDULE GS-3 — LARGE GENERAL SERVICE — SECONDARY VOLTAGE, 500 KW AND ABOVE," confirmed in three
separate places in the document text itself. Per Section 1.3's own filing-timeline finding above,
this is structurally expected: this December 2025 filing covers only 2026 rates, and GS-5 does not
exist as a filed rate schedule until the separate 2027-rates filing (due ~November 2026, likely not
yet published as of this project's own session date). The GS-3 data itself is real and directly
useful as comparative context for an existing, currently-active large-customer schedule:

| Component | Current Rate | Proposed Rate (eff. 2026) | Current Revenue | Proposed Revenue |
|---|---|---|---|---|
| Basic Customer Charge | $142.76 | $185.34 | $1,669,871 | $2,167,931 |
| Distribution Demand ($/kW) | $2.507 | $3.316 | $40,112,495 | $53,052,576 |
| On-Peak Power Supply ($/kW) | $8.743 | $8.976 | $101,802,311 | $104,515,995 |
| Energy, On-Peak ($/kWh) | $0.003876 | $0.004648 | $7,659,121 | $9,184,622 |
| Energy, Off-Peak ($/kWh) | $0.007609 | $0.003299 | $5,946,859 | $7,519,620 |
| **Total** | — | — | **$153,464,213** | **$181,204,341** |

Overall: a 32.14% distribution increase and 14.38% generation increase for GS-3 (18.47% blended,
+$27.2M) — a real, specific figure for an existing schedule, useful for understanding the general
shape of Dominion's own 2026 rate case even though it is not GS-5.

**Attempt 2 — a genuine GS-5 table obtained, but internally inconsistent in a way that should be
resolved before use, not silently accepted**. A follow-up screenshot from the same source document
carries the header "SCHEDULE GS-5 — LARGE GENERAL SERVICE — SECONDARY VOLTAGE — **CHOICE**" but its
own subtitle still reads "500 KW AND ABOVE" — directly contradicting the 25 MW threshold already
confirmed repeatedly from primary SCC sourcing (Section 1.3 above). Working theory, not confirmed:
this table was likely built from the GS-3 table as a structural template (identical row layout and
labels) with the schedule number updated but the "500 KW" subtitle text left stale — but this has
not been verified against the source document directly and should not be treated as settled.
**"Choice" itself is understood and explains the table's own all-zero generation figures**: Choice
customers purchase generation from a competitive retail supplier rather than from Dominion, so a
Dominion-side billing summary would correctly show $0 generation revenue for this segment — this is
expected structure, not a data quality problem. This GS-5-Choice segment is very likely a small,
non-representative slice of the overall GS-5 class; most hyperscale data centers are expected to
take bundled (non-Choice) service, which would have real, non-zero generation dollar figures in a
separate table not yet located.

**Resolution attempt blocked by image-quality limits, not effort**: further zoomed screenshots were
attempted to resolve remaining ambiguous figures and locate the non-Choice GS-5 table, but (a) the
source PDF's own embedded scan is confirmed low-resolution at the image level (zooming a raster
scan cannot recover detail never captured), and (b) this chat separately reached its own image
upload limit before a workable second source could be obtained. **Given GS-5's own actual dollar
figures are not expected to be publicly filed until the separate 2027-rates filing (~November 2026,
per Section 1.3), further effort chasing precise figures from this particular December 2025 document
is likely not worthwhile right now** — the structural terms already fully confirmed from primary SCC
sourcing (25 MW/75% load factor threshold, 85%/60% minimum-take, 14-year contracts, $1.5M/MW
collateral) are what materially drive this project's own A.7 analysis; specific $/kW rate figures
are useful color, not load-bearing for the demand-flexibility question this appendix addresses.
**Flagged as pending GS-5's own actual future filing, not resolved.**

**Direct source document link, for manual reference**:
https://www.scc.virginia.gov/docketsearch/DOCS/89lc01!.PDF — the actual December 9, 2025 filing
containing both the GS-3 table (Attempt 1) and the GS-5-Choice table (Attempt 2) documented above.
This is the same document referenced by document control number 251220100 (visible in both
screenshots' own headers) and by the December 9, 2025 cover letter (Section 1.3 above). **This
tool's own web_fetch could not retrieve it directly** — confirmed via direct fetch attempt, not
assumed: scc.virginia.gov disallows automated access site-wide per its own robots.txt, consistent
with the same restriction already found blocking the news-release and docket-search-case pages
earlier in this research. A human reader can access it directly via a standard browser; preserved
here specifically so this citation is not lost to a future session that lacks this conversation's
own context.


  purpose as GS-5 itself, not a flexibility mechanism either.
- **A real structural constraint directly relevant to A.7's own demand-flexibility question, not
  previously documented here**: per the Thomas Jefferson Institute's own reporting on the SCC's final
  order, GS-5 customers "must give three years' notice of any plans to reduce demand, with limits on
  how much they can reduce it." This is a genuine, contractual limit on how freely a GS-5 customer
  could actually offer demand flexibility through IRAS, LLDF, or any other mechanism documented
  elsewhere in this appendix — independent of whether the customer would otherwise be willing to.
  Worth carrying forward into any future modeling of A.7's own realistic near-term magnitude: even a
  fully-designed, fully-incentivized flexibility program cannot draw on capacity a customer is
  contractually restricted from offering on short notice.
- **Also confirmed in this same round of research**: Google and Amazon directly testified in this
  proceeding and requested that CIAC payments (Section 1.1) be voluntary rather than mandatory — the
  SCC rejected this and made the payments mandatory. See Section 6.3a for the full finding, recorded
  there alongside this project's other documented industry counter-proposals.

### 1.4 Loudoun County's data center "commercial building" classification — a real history, but zoning, not electric-rate classification

**Directly answers the second half of the user's own question.** This is a genuinely separate
regulatory track from Dominion's own rate schedules (1.1-1.3 above) — a *local land-use zoning*
classification, not a *utility rate* classification. Worth being precise about this distinction,
since the two are easy to conflate given both use the word "commercial."

**Timeline, fully sourced**:
- **2000**: Loudoun County's zoning administrator issued a quiet ruling classifying data centers as
  equivalent to "office parks" for zoning purposes — decided before officials had any real concept
  of what a modern data center would become, and specifically so it would remain in effect only
  "until such time as the Zoning Ordinance may be amended to define these types of facilities as a
  separate use classification." This made data centers a **by-right** use in commercially-zoned
  areas — approvable administratively, with no discretionary review or public hearings required.
- **2006**: Amazon Web Services builds its first Loudoun facilities, taking direct advantage of this
  by-right pathway.
- **April 2, 2014**: A Zoning Ordinance Amendment (ZOAM) formally added and defined "data center" as
  its own distinct use category — the point at which data centers stopped being purely an "office"
  designation by rule, though the by-right pathway itself persisted for years afterward in practice.
- **2018-2025**: County-wide data center energy demand grew from 1 GW to 5.33 GW — nearly a quarter
  of Dominion's entire Virginia load from this one county alone.
- **March 18, 2025**: The Loudoun Board of Supervisors approved a Comprehensive Plan Amendment and
  Zoning Ordinance Amendment eliminating by-right development entirely. New data centers now require
  a special exception — full legislative review and public hearings before both the Planning
  Commission and Board of Supervisors. A grandfathering provision covers already-under-review
  applications (as of Feb. 12, 2025), limited to projects more than 500 feet from residential areas.
- **Summer 2026** (exact date within this research not pinned down further): the County's zoning
  administrator issued a further opinion that the original 2000 determination itself is now
  "obsolete" — since data centers now have their own separate land-use classification and a fully
  articulated regulatory scheme, the office-park equivalence the whole by-right era was built on no
  longer has a live legal basis, though what this means for land still grandfathered under the older
  1972 zoning ordinance in parts of the county remained unclear per the reporting found.

**Why this matters for A.7's own modeling, despite being a zoning (not rate) mechanism**: the
by-right history explains *why* Loudoun's data center buildout happened as fast and as densely as it
did, which is directly relevant background for understanding the scale problem A.7 is meant to
address — but it does not itself create or constrain any demand-flexibility mechanism. Zoning
governs whether/how a facility gets built; it says nothing about how that facility's own load
behaves once built. Not a source of any curtailment magnitude or eligibility figure for A.7's own
modeling — included here for complete, accurate context per the user's own direct question, not
because it feeds the eventual DLC/DR calculation chain.

---

## 2. PJM — existing practices (not proposals; see forthcoming Part 2 document for proposed measures)

### 2.1 Pre-Emergency Load Management (PELM) — the existing, general DR program

An already-operating mechanism, not new and not data-center-specific: PJM's own "suite of Emergency
Procedures" includes Load Management resources that are paid in advance to reduce consumption when
PJM directs during extreme grid conditions. This is the pre-existing DR program structure that any
new data-center-specific mechanism (see Part 2) would sit *ahead of or behind* in PJM's own
emergency-response sequencing.

### 2.2 Real, already-invoked emergency curtailment actions in 2026 (not proposals — these happened)

Two separate, real DOE emergency orders were issued and used in 2026, both authorizing PJM to direct
large-load curtailment as a last resort before rolling blackouts:

- **May 18, 2026**: DOE emergency order authorizing PJM to curtail data centers and other large
  loads *with backup generation*, tied to a specific hot-weather/planned-maintenance-outage
  convergence. PJM had requested this Sunday, order issued Monday, covering a 3-day window
  (beginning May 18) with an expected peak load of 134,027 MW, 135,961 MW, and 119,103 MW on
  successive days, against under 5,800 MW of expected reserves.
- **July 2026 (record heat wave)**: A similar order, explicitly authorizing curtailment of data
  centers and large loads ≥50 MW peak, requiring a switch to backup generators within 15 minutes of
  an emergency signal. **Explicit exemptions**: hospitals, 911 call centers, water treatment plants,
  air traffic control towers, and defense installations. **Both orders included temporary relief
  from environmental permit restrictions** — power plants (and, by extension, the backup generators
  being invoked) allowed to exceed normal SO2/NOx and other emissions limits for the duration.

**Structural mechanism, both orders**: this is, again, a "switch to on-site backup generation"
action, not a "reduce compute/operational demand" action — the same fundamental mechanism as
Dominion's own Targeted Sector Programs (1.1 above). Confirmed independently in academic literature
(Chen, Ren, Ren & Wierman, "Greening Multi-Tenant Data Center Demand Response," arXiv): "data
centers typically participate in [emergency demand response] by turning on backup (diesel)
generators," which the paper's own authors describe as "both expensive and environmentally
unfriendly" — directly consistent with what this research found in Dominion/PJM's own real-world
2026 actions, not a divergent or purely theoretical claim.

### 2.3 A hard structural limit on what PJM itself can do

Directly relevant to how any future A.7 mechanism should be modeled: **PJM has confirmed it cannot
order individual data centers to curtail.** That authority sits exclusively with states and
utilities under the Federal Power Act. PJM can only direct transmission owners and utility zones;
the utility and state authorities decide which actual retail customers are affected and how. This is
precisely why the real activity addressing this problem is split across two tracks — PJM-level
wholesale/interconnection rule proposals (Part 2) and state/utility-level retail tariff development
(Part 3, most notably the Virginia SCC's own work with the Data Center Coalition on model
interruptible/emergency-load-reduction tariffs) — rather than PJM simply issuing direct orders to
individual facilities.

---

## Sources (direct citations, all fetched or searched during this research pass)

- dominionenergy.com/virginia/save-energy/targeted-sector-programs
- dominionenergy.com/virginia/rates-and-tariffs/curtailment-notices (fetched directly, full event
  history 2023-2026)
- dominionenergy.com/virginia/rates-and-tariffs/schedule-10-data
- Virginia SCC, final order, Dominion Energy Virginia 2025 Biennial Review, Case PUR-2025-00058
  (Nov. 25, 2025). Full press-release text confirmed verbatim by direct user-supplied copy
  (2026-08-24) against every figure already documented in Section 1.3 above -- no discrepancies
  found. Docket case detail page (scc.virginia.gov/docketsearch#/caseDetails/146025) is blocked
  site-wide by the SCC's own robots.txt, same as the news-release page itself -- confirmed by direct
  fetch attempt, not assumed; the full docket (filings, exhibits, order text) is not accessible via
  this tool, only via manual browser access. Media contact of record: Greg Weatherford,
  news@scc.virginia.gov.
- Virginia SCC, "Data Center Initiatives" fact sheet (Feb. 2026)
- E&E News/POLITICO, "Virginia to treat data centers differently on the grid" (Dec. 2, 2025)
- American Action Forum, "Virginia's New Data Center Electricity Rate Class" (Apr. 22, 2026)
- WTOP/Virginia Mercury, SB 253 coverage (Feb. 2026)
- Utility Dive, "PJM gets emergency approval to curtail data centers, large loads during hot
  weather" (May 19, 2026)
- Electric Choice, "PJM Emergency Order: Record Heat Wave (2026)" (Jul. 2, 2026)
- Chen, Ren, Ren & Wierman, "Greening Multi-Tenant Data Center Demand Response" (arXiv:1504.07308)
- Piedmont Environmental Council, "Data Centers in Loudoun: A Primer" (Jul. 2, 2026)
- NBC4 Washington, "How Loudoun County became the data center capital of the world" (Jul. 7, 2026)
- Patch (Ashburn), "Decades-Old Loudoun County Rule Treating Data Centers Like Offices No Longer
  Holds" (2026)
- Holland & Knight, "Loudoun County, Virginia, Eliminates By-Right Data Center Development" (Apr. 4,
  2025)
- Loudoun County official FAQ pages (loudoun.gov)
- Nectar (nectarclimate.com), Dominion Energy Virginia rate optimization guide (rate figures for
  GS-2/GS-3/GS-4 on-peak demand structure)

---

## 3. PJM's proposed measures (not yet in effect — regulatory process, current as of Aug. 2026)

### 3.1 Interim Resource Adequacy Service (IRAS) — the most concrete, furthest-along proposal

Formerly called "Connect and Manage" in earlier PJM stakeholder process documents. This is PJM's
central, formally-filed answer to the question "how does a data center connect before enough
generation exists to serve it reliably."

**Timeline, fully confirmed**:
- July 27, 2026: PJM Board of Managers issues a "decisional letter" directing staff to file.
- August 13, 2026: PJM formally files the IRAS proposal with FERC (a 435-page filing).
- FERC comment deadline: September 3, 2026 (already noted in Part 1).

**Mechanics, now fully sourced**:
- **Scope**: applies only to "New Large Loads" (defined as 50 MW+ at a single point of
  interconnection, or multiple points within a one-mile radius) that, as of **June 1, 2027**, do not
  bring sufficient capacity to cover their own registered peak.
- **Not automatic for all large loads**: a load with enough qualifying capacity (new generation,
  bilateral contracts, storage, or coverage secured through the Reliability Backstop Procurement —
  see 3.2 below) to cover its own registered peak faces no IRAS obligation at all. IRAS applies only
  to the *uncovered portion* of demand.
- **Sequencing**: IRAS reductions occur *before* PJM deploys Pre-Emergency Load Management (PELM,
  the existing general DR program documented in Part 1, section 2.1) — i.e., new large loads without
  their own capacity are curtailed ahead of everyone else, not as a last resort.
- **Compensation mechanism, quantified**: the credit rate is set equal to 50% of the existing
  Performance Assessment Interval (PAI) rate already used for PELM's own Non-PAI events (FERC-
  approved June 26, 2026). PAI penalties/payments run "on the order of $3,000/MWh" per industry
  sources — meaning IRAS compensation is roughly **$1,500/MWh, order-of-magnitude, not a precisely
  confirmed figure** (the 50% relationship itself is precise and FERC-approved; the underlying PAI
  rate this session found only as an "on the order of" figure). Justification given: IRAS load is
  reduced at an earlier, less severe stage of emergency conditions than full PELM events, so the
  value of the reduction, while substantial, is lower.
- **Cost recovery explicitly left to states, not PJM**: PJM's own filing does not propose a specific
  wholesale cost-allocation mechanism for IRAS compensation. Recovery is left to Electric
  Distributors (i.e., Dominion) "consistent with their state-approved program" — another instance of
  the same PJM-cannot-touch-retail-customers structural limit already found in Part 1.
- **Waiver provision**: Large Loads may waive compensation entirely, consistent with the federal
  "Ratepayer Protection Pledge" (a policy commitment, referenced across multiple PJM filings, to
  "protect the American people from increased utility bills as a result of the development of these
  data centers").
- **A structural change to future capacity auctions**: beginning with the 2029/2030 capacity
  auction, new Large Loads that don't bring their own new supply will not be counted when PJM
  calculates future procurement needs — directly linked to IRAS, since a load excluded from the
  auction's own demand forecast is, by construction, one PJM isn't planning to have firm capacity
  for.

**Scale context, a genuinely useful cross-check against this project's own earlier "blue whale"
comparison**: PJM's own filing states it expects **32 GW of load growth from 2024-2030, with 30 GW
of that from data centers specifically**. Worth setting directly against the 70,000 MW *requested*
pipeline figure already used in the blue-whale comparison (entry #72) — the requested queue is more
than double what PJM itself is forecasting will actually materialize by 2030, a real and worth-
remembering gap between "requested" and "predicted to actually connect."

### 3.2 The Large Load Registry — the shared data infrastructure underlying IRAS and the Reliability Backstop Procurement

A database PJM will build and maintain, tracking the location and MW quantity of every Large Load
(50 MW+) by detailed site, whether it brings its own supply, and its service area. Its own stated
purpose is dual: improving load forecast accuracy generally, and directly supporting both IRAS and
the Reliability Backstop Procurement (3.3 below). Information will be shared with states, utilities,
and regulators, and made public "to the extent permitted by applicable confidentiality
requirements" — meaning at least some of this data is expected to become genuinely public, a
potentially valuable future data source for A.7's own modeling if it materializes.

### 3.3 Reliability Backstop Procurement (RBP) — a real, dated, one-time capacity auction

- **Filed**: July 31, 2026, FERC Docket ER26-3380.
- **Purpose**: address the 6,831 MW capacity shortfall from PJM's own July 2026 Base Residual
  Auction for the 2028/2029 delivery year (an auction that cleared at PJM's own price cap,
  $325/MW-day, across its entire footprint).
- **Timeline**: bid window September 30 – October 21, 2026; results due by December 2, 2026 —
  ahead of the next regular base auction.
- **Structural note from independent analysis** (Electron Economics): the RBP effectively splits new
  supply into two tracks — a privately-contracted track for large loads with the balance-sheet
  strength to secure their own capacity directly, and a "residual" (socialized, ratepayer-funded)
  track for everyone/everything else. Worth flagging as an analytical interpretation, not a PJM
  self-description, but a useful framing for understanding who actually bears the cost risk here.

### 3.4 NCBL and PRD — NCBL's fate is confirmed; PRD's fate in the final filing is not, and an earlier claim in this document was corrected

The Non-Capacity-Backed Load (NCBL) concept (a separate load category for very large, 50+ MW new
consumers, offering lower capacity charges in exchange for mandatory curtailment) was PJM's initial
"conceptual proposal" (August 2025), triggered broad stakeholder opposition (data center operators
argued it would undermine capacity market integrity), and was withdrawn. **IRAS (3.1 above) is its
direct successor** — the same underlying problem (new large loads without matching capacity), a
different, now-formally-filed mechanism. This part is confirmed directly.

**Correction, per direct user question (2026-08-24)**: this section originally stated that PRD
modifications "do not appear in the final August 2026 IRAS filing... superseded by IRAS itself." That
was an inference from absence in the sources reviewed at the time, not a directly verified fact, and
it should not have been stated as settled. Two follow-up searches confirm:

- **PRD itself, as a general PJM capacity-market mechanism, is unambiguously still active** — not a
  proposal at all, but a real program dating to 2012. PJM's own official Base Residual Auction
  reports confirm current participation: 210.2 MW of PRD cleared in the 2025/2026 delivery year,
  105.5 MW in the 2026/2027 delivery year.
- **Whether the specific October 2025 idea — using PRD as a voluntary data-center opt-in alternative
  to mandatory NCBL/IRAS — was folded into the final IRAS filing, dropped, or remains a separate,
  still-open track could not be confirmed either way** in this research. No source found directly
  states its final disposition. This should be treated as a genuinely open question, not as
  resolved in either direction, until a source directly addressing it is found.

---

## 4. Dominion's own proposed measure: the Large Load Demand Flexibility Program (LLDF)

**This is the single most directly relevant finding in this entire research pass** — a real,
legally-mandated, Dominion-specific demand flexibility program, currently in active development as
of this research (fetched directly from dominionenergy.com/about/delivering-energy/demand-
flexibility).

### 4.1 Legal basis and current status

- **HB 284 / SB 371, 2026 Virginia General Assembly**, codified at **§ 56-596.7 of the Code of
  Virginia**. Became law July 1, 2026.
- **Mandate**: directs Dominion Energy Virginia to develop a **voluntary** demand flexibility program
  specifically for "High Energy Demand Customers" — defined identically to the GS-5 threshold (25 MW
  contracted/measured demand, 75%+ annual load factor), excluding certain defense facilities.
- **No program design exists yet.** This is worth stating plainly, not glossed over: as of this
  research, Dominion has not filed, and stakeholder feedback is still actively being gathered to
  inform "potential program design options" before any filing happens. Any modeling assumption this
  project makes about LLDF's own eventual mechanism or magnitude is necessarily a placeholder for
  something genuinely still being decided in real time — directly consistent with the user's own
  framing that "we can always make a fully transparent assumption and let others argue about which
  is going to be actually finalized."

### 4.2 Full timeline (fetched directly from Dominion's own program page)

| Date | Milestone |
|---|---|
| July 1, 2026 | HB 284/SB 371 becomes law |
| July 2026 | Stakeholder engagement launch (virtual kickoff held July 29, 2026; survey opened) |
| August 2026 | Survey feedback concludes; working group established |
| Fall 2026 | Collaborative program development |
| January 2027 | Program filed with the SCC |
| November 30, 2027 | SCC issues its final order |

**Relative to this project's own current session date (August 24, 2026): this program is, right
now, in its "survey feedback concludes / working group established" stage.** Genuinely live,
ongoing regulatory process, not a completed or even fully-designed one.

### 4.3 Why this is structurally different from every other mechanism found in this research

Dominion's own program page states this directly, not inferred: **"Existing demand-side management
programs help reduce system-wide peak demand but are not designed to address localized grid
constraints."** Every mechanism documented in Parts 1-3 above — STR, EV Telematics, the C&I
curtailment program, PELM, IRAS — operates at the system-wide or PJM-zone level. LLDF is explicitly
conceived to address **localized** distribution-grid constraints instead (formalized in its own
glossary as "Locational Value" — resources in areas with local constraints providing greater system
benefit than identical resources elsewhere). This is a genuinely different problem than anything
else in this document, not a smaller-scale version of the same one.

### 4.4 Key mechanism definitions (from Dominion's own stakeholder-working-group glossary, fetched directly)

- **Demand Flexibility**, defined with two genuinely distinct paths, not one: "lowering electric grid
  system load requirements or shifting such requirements from time periods of peak system demand to
  time periods of lower system demand, **including through programs by which high energy demand
  customers temporarily reduce or interrupt their electricity usage or through programs by which
  high energy demand customers secure measurable and verifiable electric load reductions from other
  retail electric service customers** during time periods of peak system demand." **The second path
  is genuinely novel relative to everything else found in this research**: a data center could, in
  principle, satisfy its own compliance obligation not by cutting its own operations at all, but by
  *paying other retail customers* (residential or C&I) to reduce their load instead — a direct,
  official acknowledgment that this program could financially connect to and fund the very
  residential/C&I DLC mechanisms this project has already built (A.2's smart thermostats/EV
  chargers/Water Energy Rewards, A.6's thermal storage), not operate independently of them.
- **Capacity Reduction Credit (CRC)**: "a measured and verified unit of demand flexibility" — the
  likely compensation/accounting unit, though its own $/unit value is explicitly not yet
  established (left to future SCC rulemaking).
- **Demand Flexibility Standard**: a measurable annual performance target the SCC will set, which
  Dominion is expected to make "best, reasonable efforts to achieve" — a utility-level target,
  structurally similar in kind to the CVR 1% system-wide target already documented for A.5, but for a
  genuinely different mechanism and customer population.
- **Eligible technology, an explicit and important constraint**: must not "emit carbon dioxide as a
  byproduct of combusting fuel or manufacturing fuel for combustion to generate electricity." **This
  explicitly excludes diesel backup generators** — the exact mechanism already documented as the
  current, standard practice for both the C&I curtailment program (Part 1) and the DOE emergency
  orders (Part 1/2). LLDF is deliberately designed to be a genuinely different kind of mechanism from
  everything currently in practice, not an extension of it.
- **Virtual Power Plant (VPP)** and **Distributed Energy Resource (DER, up to 5 MW)** are both
  formally defined and in scope — confirming aggregation-based mechanisms are a real, considered
  design option for this program, not just direct large-load curtailment.
- **Aggregator**: explicitly defined as a real, distinct third-party role, separate from the utility
  itself — consistent with the DERA/VPP participation model already discussed elsewhere in this
  project's own work (WMA/D.2).

---

## Updated sources list (Part 2/3 additions)

- Foley Hoag, "PJM Board Directs FERC Filing on Reliability Backstop Procurement and Interim
  Resource Adequacy Service" (Aug. 2026)
- GridBeyond, same subject (Aug. 2026)
- PJM.com, "Interim Resource Adequacy Service Proposal" fact sheet (Aug. 13, 2026 filing date)
- PJM.com, CIFP Framework executive summary and Board Decisional Letter (July 27, 2026)
- Data Center Knowledge, "PJM's New Deal for Data Centers: Bring Power or Face Cuts" (Aug. 2026)
- EnergyChoiceMatters.com, "PJM Not Proposing Specific Cost Allocation To LSEs..." (Aug. 14, 2026)
- PA Environment Digest Blog, PJM FERC submission coverage (Aug. 2026)
- Dominion Post, "PJM proposes plan to handle power demands caused by data centers" (Aug. 14, 2026)
- Electron Economics (Substack), RBP/IRAS analysis (Aug. 2026)
- Babst Calland, "PJM's Proposal to FERC Targets Data Centers..." (Aug. 2026)
- CRAI, "Addressing capacity performance risk for variable energy..." (PAI penalty-rate context)
- KilowattLogic, "PJM Capacity Performance (CP): The Complete 2026 Guide"
- **dominionenergy.com/about/delivering-energy/demand-flexibility** (fetched directly — LLDF program
  page, full timeline)
- **LLDF Definitions and Acronyms glossary PDF** (fetched directly, cdn-dominionenergy-prd-001)
- HB 284/SB 371 (2026 VA General Assembly), full bill text (lis.blob.core.windows.net)
- Utility Dive (sponsored/Dominion), "Adapting utility tariffs for data center driven load growth"
- Virginia Mercury, "New state law mandates review of Dominion's load forecasting..." (Apr. 30, 2026)
- Virginia Mercury, "SCC orders Dominion to develop tariff to assign more transmission costs..."
  (Aug. 5, 2026)

---

## 5. Other proposed demand-reduction measures (Part 3)

### 5.1 The Virginia SCC / Data Center Coalition joint working group — the most directly relevant lead, now fully sourced from the primary document itself

Fetched directly (not summarized from news coverage): the actual June 30, 2026 letter from VA SCC
Chair Kelsey Bagot and Data Center Coalition President Josh Levi to the PJM Board, hosted on PJM's
own site. This is a **state-level, non-PJM regulatory effort**, distinct from everything in Section 3
— PJM itself has no authority here (per the structural limit already established in Part 1/2); this
is states and industry building their own tools directly.

**Three distinct workstreams, each with a real, stated deadline**:

1. **Model State Interruptible Tariffs** (due **February 1, 2027**). Would establish standardized
   retail provisions for interruptible service (voluntary election *or* state regulatory
   requirement), define operational expectations and utility responsibilities, and establish the
   actual retail mechanisms for responding to curtailment requests — while explicitly preserving each
   state's own independent regulatory authority (i.e., a template, not a binding multi-state rule).

2. **Emergency Load Reduction** (also due **February 1, 2027**) — **the most directly relevant
   workstream to A.7's own demand-reduction question**. Would "establish retail mechanisms
   authorizing utilities to curtail designated large commercial and industrial customers, **or
   require the use of available on-site backup generation**, once PJM has exhausted all other
   available reliability resources, including demand response, but before implementation of broad
   manual load shed." This gives a precise, stated position in the full emergency-response hierarchy,
   worth recording explicitly:
   **(1) DR/load management (PELM, then IRAS) → (2) this new, targeted large-C&I mechanism → (3)
   broad manual load shed (rolling blackouts).**
   Direct, stated rationale for why this sits where it does: "by targeting reductions from large
   commercial and industrial customers before implementing widespread feeder-level outages, this
   approach can significantly reduce the likelihood that residential customers are interrupted
   during the most severe reliability emergencies." A real inter-jurisdictional equity point is made
   explicitly too: this protects "jurisdictions with little or no large-load development," where
   residential customers could otherwise face manual load shed even though targeted large-load
   curtailment *elsewhere in the PJM region* would have been sufficient — i.e., without a
   region-wide coordinated mechanism, a state with few data centers could still suffer rolling
   blackouts because *other* states' data centers weren't curtailed first.

3. **Reliability Backstop Cost Allocation** (due **January 1, 2028**) — assigns RBP costs (Section
   3.3) to the large loads that drove the need for that procurement. Cost allocation, not a
   demand-reduction mechanism itself — noted for completeness, not because it feeds A.7's own
   magnitude question.

**A real, unresolved tension worth flagging directly, not smoothed over**: this Emergency Load
Reduction workstream explicitly includes "require the use of available on-site backup generation" as
one of its two core mechanisms (alongside direct curtailment) — the same backup-generation-switching
approach already documented as standard current practice (Part 1's C&I curtailment program, the DOE
emergency orders). This sits in direct tension with LLDF's own explicit exclusion of CO2-emitting
backup generation (Section 4.4 above). **Neither track has been finalized**, so this tension is
itself still open, not resolved one way or the other — two different, simultaneously-in-progress
regulatory efforts that may end up pulling in different directions on the same underlying question
(is diesel backup generation an acceptable data-center flexibility mechanism, or not).

**A real critique worth including for balance, not just the official framing**: the Piedmont
Environmental Council characterized the letter as "vague and lack[ing] details on who will be
involved," and is "especially worried about how discussions on possible increased use of the backup
diesel generators as a way to manage grid strain will play out" — direct, on-record concern from an
environmental advocacy group about the same backup-generation tension just noted, not an
after-the-fact interpretation.

### 5.2 Comparative precedent — AEP Ohio's Data Center Tariff (DCT), a cost-allocation mechanism with a real, quantified queue-reduction result

**Important distinction stated directly**: this is structurally a cost-allocation tariff (closely
comparable to GS-5, Part 1 section 1.3), not a demand-flexibility/curtailment mechanism like Sections
3-5.1 above. Included here as comparative regulatory context and — genuinely useful — as the one
real, quantified precedent found in this entire research thread for what this type of measure
actually does to a speculative interconnection queue.

- **Approved**: PUCO, July 9, 2025. Effective July 23, 2025.
- **Terms**: data centers >25 MW pay minimum 85% of contracted capacity for up to 12 years,
  regardless of actual usage; 4-year ramp-up period; exit fees; collateral/creditworthiness
  requirements. Structurally near-identical to GS-5's own terms (85%/60% minimums, multi-year
  contract, collateral) — Virginia and Ohio arrived at closely comparable solutions independently.
- **A newer, more targeted AEP Ohio tariff (Schedule DCD, approved October 2025)** offers *lower*
  demand charges ($12.50/kW-month first 5 years, $9.80/kW-month after, vs. AEP's standard $21.40/kW-
  month) specifically to hyperscale customers who commit to 50+ MW for 15 years *and* source 20% of
  their energy from new renewables within 5 years — a real example of a utility using rate design to
  actively reward genuine long-term commitment and clean-energy sourcing, not just penalize
  uncertainty.
- **The single most directly useful quantified result in this entire research thread**: "speculative
  queue dropped from 30 GW to 13 GW after tariff approval required firm financial commitments" — a
  real, ~57% reduction in Ohio's own requested-but-unbuilt pipeline, directly following
  implementation of a firm-commitment cost-allocation tariff. **Directly relevant to this project's
  own "blue whale" scale comparison** (entry #72): if Dominion's GS-5 (effective Jan. 2027, same
  structural design as Ohio's DCT) produces a similar proportional effect on Virginia's own 70,000 MW
  requested pipeline, a meaningfully smaller share of that figure should be expected to actually
  materialize than the raw requested number alone would suggest — worth carrying forward as a
  reasoned basis for treating "requested" and "will actually connect" as genuinely different
  numbers, not just a vague caveat.

---

## Updated sources list (Part 3 additions)

- PJM.com (hosted, primary source), VA SCC/DCC letter to PJM Board of Managers (June 30, 2026)
- Virginia Mercury / Fredericksburg Free Press / Royal Examiner / Rappahannock News / Henrico
  Citizen / Warren County VA (syndicated coverage), "Data centers want to build their own gas
  turbines..." (Jul. 20-21, 2026)
- PowerMag, "AEP Ohio Proposes New Utility Tariff for Data Centers..." (Oct. 25, 2024)
- FactSet Insight, "Ohio Utility Proposes New Data Center Tariffs, Angers Tech Giants" (Jul. 12,
  2024)
- MGrid, "AEP Ohio Data Center Tariff Sets National Precedent After 30 GW" (Jun. 16, 2026) — source
  of the 30 GW→13 GW queue-reduction figure
- KJK (Kohrman Jackson Krantz), "Regulating the Surge: Legal Analysis of AEP Ohio's New Data Center
  Tariff..." (Nov. 14, 2025)
- Vorys, PUCO tariff-approval client alert (Jul. 11, 2025)
- PUCO official release, "PUCO orders AEP Ohio to create data center specific tariff" (Jul. 9, 2025)
- Utility Dive, "Ohio regulators approve AEP data center interconnection rules" (Jul. 10, 2025)
- Buckeye Institute, "Undermining Ohio's Competitive Edge" policy brief (Mar. 16, 2026) — critical
  perspective, included for balance

---

## 6. Industry counter-proposals — what data center coalitions, hyperscalers, and IPPs have proposed back, not just responded to

Everything documented in Sections 1-5 above originates from PJM, Dominion, or state regulators. This
section covers the other direction: what industry itself has proposed, pushed back on, or offered as
alternatives. Direct user question prompting this section: "are there any counter proposals from
data center coalitions, tech companies, or related?"

### 6.1 The October 2025 hyperscaler counterproposal — a real, named alternative, not generic opposition

Reported directly (Latitude Media): after PJM's August 2025 "conceptual proposal" (the origin of the
NCBL concept later withdrawn — Section 3.4), **"six of the biggest power users that would be subject
to the rules — the tech giants Amazon, Google, and Microsoft, and the utilities Calpine,
Constellation, and Talen — proposed an alternative."** Two specific, named elements:

- **A new procurement process locking in current (high) prices for seven years**, intended to give
  developers a stronger incentive to invest in new clean, firm generation.
- **A load-forecast correction mechanism** modeled on how ERCOT (unlike PJM at the time) adjusts its
  own forecasts based on how successfully large loads actually materialize historically —
  **explicitly including factors that have nothing to do with generation itself, such as microchip
  availability over the next five years to actually construct proposed data centers.**

**This second point is a genuinely novel, worth-flagging reason — distinct from the cost-allocation-
tariff effect already documented in Section 5.2 — for why "requested" pipeline figures overstate
what will actually connect.** GS-5/AEP-DCT-style tariffs affect the *financial* incentive to hold a
speculative queue position; chip availability is a *physical* supply constraint on the industry as a
whole, independent of any single utility's own tariff design. Both mechanisms point the same
direction (requested > actual), but for genuinely different reasons — worth keeping both in mind
rather than treating "tariffs will shrink the queue" as the only explanation.

**Important nuance on the underlying position, not just opposition for its own sake**: the same
source reports hyperscalers had "just begun endorsing" the general idea that occasionally dialing
down data center load could help the existing grid serve more load sooner — citing a specific,
named intellectual source, a Duke University paper (see 6.4 below) — before pushing back specifically
on PJM's own implementation, "repeatedly accusing PJM of 'exceeding' its authority." **The industry
is not uniformly opposed to flexibility as a concept; the pushback is on the specific mechanism and
PJM's own legal authority to impose it**, a distinction worth preserving rather than flattening into
simple "industry against, regulators for."

### 6.2 The "Coalition Reliability Backstop Procurement" — the industry-utility proposal that actually won a supermajority vote, but PJM's board didn't adopt it

Now precisely named and sourced (National Law Review, citing PJM's own July 27, 2026 Board
Decisional Letter directly): during PJM's Critical Issue Fast Path stakeholder process, **only one
proposal — the "Coalition Reliability Backstop Procurement" — received a supermajority of
stakeholder votes.** This was, per earlier reporting already found, "a plan from utilities and the
trade group Data Center Coalition," which "would have potentially forced large loads to pay for the
capacity they need." **PJM's Board explicitly declined to adopt it anyway**, stating it "would not
provide sufficient assurance that capacity equal to the identified near-term shortfall would actually
be procured." The Board proposed its own, more limited Reliability Backstop Procurement (Section 3.3)
instead — a real, direct instance of PJM's board overriding a stakeholder-majority-backed industry
proposal, worth being precise about rather than implying the RBP as filed reflects industry
consensus.

### 6.3 The March 2026 colocation-framework pushback — Vistra, Constellation, and the DCC jointly, on a separate track from IRAS

A distinct proposal track, not the IRAS/NCBL lineage — this concerns PJM's separate framework for
**colocating** generation directly with large loads (e.g., a data center built next to its own
dedicated power plant). Direct, quoted DCC filing language: **"These proposals will not enable
commercially viable arrangements... the proposals introduce significant operational rigidity, limit
flexibility, and create disincentives that will impede the development of co-located load and
associated generation."** Vistra (an independent power producer, not a data center operator itself)
joined this criticism — worth noting the coalition here included IPPs, not just tech companies,
suggesting the concern was more about regulatory workability broadly than data-center-specific
interests alone.

### 6.3a Google and Amazon's own counter-proposal within the GS-5 proceeding itself — rejected by the SCC

A Virginia-specific, GS-5-specific counter-proposal, distinct from the PJM-level items in 6.1-6.3
above — found via a follow-up search cross-checking the SCC's own press release on the DEV Biennial
Review (Case PUR-2025-00058), confirming detail beyond what the release's own snippets had already
provided. Per Utility Dive's own reporting on a related SCC transmission-cost docket: **"Hyperscaler
companies including Google and Amazon also testified in the SCC's hearings about the case, and both
of those companies requested the introduction of voluntary CIACs, but the SCC ruled that the
payments will be mandatory."** A real, specific, named industry counter-proposal — Google and Amazon
asked that Contribution in Aid of Construction payments (Section 1.1's own CIAC terminology) be
voluntary rather than a mandatory condition of service — and the SCC directly rejected it, ruling
the payments mandatory instead. Worth recording as a concrete instance of industry pushback that did
not succeed, alongside the Coalition Reliability Backstop Procurement (6.2 above), which won a
stakeholder supermajority vote but was still not adopted by PJM's own board — a second, separate
example of an industry-preferred term being directly overridden by the relevant regulator.

### 6.4 The Duke University Nicholas Institute study — the quantified basis for the original flexibility pitch

Cited directly in Utility Dive's own reporting on industry positioning: **"just a 1% to 2% reduction
in data center peak demand can reduce electricity rates 0.5% to 2.8% and protect reliability,"**
per a 2026 Duke University Nicholas Institute study. This is the real, quantified intellectual
foundation the hyperscalers' own initial flexibility endorsement (6.1 above) was built on — worth
recording directly since it's the source of the "even a little flexibility goes a long way" framing
that recurs across this entire research thread, not just an unsupported industry talking point.

### 6.5 The Independent Market Monitor's third, distinct voice — skeptical of both sides' framing

Genuinely useful because it's neither a utility nor an industry position — PJM's own Independent
Market Monitor (Monitoring Analytics) published a report directly skeptical of data-center-
flexibility proposals generally, not aligned with either the utility or industry framing. Direct
quote: **"there is not now and not likely to be in the near future sufficient capacity supply in PJM
to meet large data center load... the solution is not to create reliability issues and wealth
transfer issues by clearing the capacity market at the maximum price and at a quantity less than the
reliability requirement by allowing the ongoing interconnection of large data center loads without
adequate generation to serve them."** The IMM's own stated position: the *only* form of flexibility
it considers "ready to deploy" is load that brings its own new, matched generation (timing and
location) alongside it — i.e., essentially the same "Bring Your Own New Generation" (BYONG) concept
already documented in Section 3, not the demand-response/curtailment-based flexibility this entire
document otherwise focuses on. **A genuinely important point of convergence, not just disagreement**:
this BYONG approach is "being endorsed by a handful of governors and the Data Center Coalition" as
part of the same CIFP process — meaning the IMM and at least part of the industry agree on this one
point, even as they disagree elsewhere.

### 6.6 Synthesis — what this means for how A.7 should eventually be modeled

Taken together, Sections 6.1-6.5 confirm this is a genuinely live, multi-sided negotiation, not a
settled question with industry simply resisting regulators. At least three distinct positions exist
simultaneously: (1) PJM/state regulators pushing mandatory curtailment-based mechanisms (IRAS, the
SCC/DCC Emergency Load Reduction workstream), (2) industry counter-proposals favoring locked-in
procurement pricing and BYONG over mandatory curtailment, and (3) the IMM's own skeptical view that
only physically-matched new generation, not demand flexibility, is a credible near-term solution.
**No single mechanism documented anywhere in this three-part research thread has unanimous
industry, utility, and independent-monitor support** — directly relevant to the user's own original
framing that this project should "make a fully transparent assumption and let others argue about
which is going to be actually finalized," since the finalized mechanism is not just undetermined
procedurally (as already established for LLDF, Section 4) but genuinely contested substantively
across every party involved.

---

## Updated sources list (Section 6 additions)

- Latitude Media, "Hyperscalers give PJM a counterproposal on load flexibility" (Oct. 8, 2025)
- Latitude Media, "Is data center flexibility a 'regulatory fiction'?" (Feb. 8, 2026)
- Latitude Media, "How much would flexible data centers really reduce rates in PJM?" (Mar. 26, 2026)
- Utility Dive, "Data centers are ready to negotiate flexibility for speed" (Jun. 26, 2026) — source
  of the Duke University Nicholas Institute 1-2%/0.5-2.8% figure
- Utility Dive, "PJM data center colocation plan takes fire from Vistra, data center group, others"
  (Mar. 27, 2026)
- National Law Review, "PJM's Proposal to FERC Targets Data Centers and Other Large Load Customers"
  — source of the Coalition Reliability Backstop Procurement supermajority-vote detail
- Ohio Capital Journal / Capitol News Illinois, "PJM's big new data center plan: Make the states
  figure it out" (Aug. 10, 2026)
- Construction Owners, "PJM Data Center Colocation Plan Criticized by Energy Firms and Industry
  Groups" (Apr. 1, 2026)
- Utility Dive, "Solving PJM's data center problem" (Dec. 2, 2025)
- Maryland Office of People's Counsel, letter to PJM Board re: 2026 Load Adjustment forecasts (Oct.
  14, 2025) — includes the AEP Ohio "slashed data center pipeline by more than half" citation

---

## 7. A real, new cost lever confirmed — the Virginia Data Center Electricity Consumption Tax — plus two corrections to earlier cost figures in this document

Prompted directly by the user cross-checking a non-primary summary against this document's own
findings, then supplying and asking for verification of two specific secondary sources. Two
corrections are recorded here explicitly, not silently folded in, consistent with this project's
own established practice of correcting rather than quietly overwriting.

### 7.1 The Virginia Data Center Electricity Consumption Tax — real, confirmed directly, and genuinely new to this document

**This is a real, separate, state-level tax — not a Dominion tariff or rider**, confirmed across
many independent primary and legal-analysis sources (Bloomberg Tax, BDO, Greenberg Traurig, Williams
Mullen, Holland & Knight, the Virginia budget bill text itself). Worth being precise about this
distinction, since an earlier non-primary summary presented it as part of "Dominion's base tariff and
fuel riders," which is incorrect — it is imposed by the Virginia General Assembly, not set by
Dominion, though Dominion collects it on the state's behalf.

- **Legal basis**: Virginia's 2026 biennial budget (HB 30, Item 3-5.24#1c), signed by Gov. Abigail
  Spanberger on June 30, 2026.
- **Rate**: $0.011 per kWh of all electricity consumed at each data center per month.
- **Effective**: July 1, 2026. **Explicitly temporary** — sunsets July 1, 2028 unless renewed by the
  legislature. This expiration was omitted from the non-primary summary that prompted this check.
- **Scope**: applies to electricity from any source — incumbent utility, competitive retail
  provider, or self-supplied/behind-the-meter generation, with no carve-out for on-site renewables.
- **Revenue cap and refund mechanism**: collections capped at $600 million/year; any excess is
  refunded pro rata to data center operators. Estimated to raise up to $1.2 billion over the full
  two-year window.
- **Definitional carve-out**: the statute's own definition of "data center" excludes facilities whose
  primary function is providing internet access or communications services — meaning the tax's real
  target is understood to be AI/compute-focused facilities specifically, not all data centers in the
  broadest sense.
- **Concrete magnitude, for scale**: a continuously-operating 500 MW facility would owe roughly $48
  million/year; a 1 GW facility close to $100 million/year — described by one source as "an increase
  of roughly 10 percent on a data center's effective electricity rate."
- **Relationship to GS-5**: this is a second, separate, additive cost lever alongside GS-5's own
  cost-allocation provisions (Section 1.3) — a data center subject to GS-5 is also subject to this
  tax; they are not alternatives to each other.

### 7.2 Correction — the "6.28 cents/kWh" figure is real, but was mischaracterized as a "spike"; it is Dominion's own stated average wholesale purchase cost

Fetched directly from Inspenet's own article (the specific source a non-primary summary had cited
for this figure), which in turn cites Dominion Energy Virginia regulatory testimony directly
(Scott Gaskill, VP of Regulatory Affairs, filed July 28, 2026): **"buying electricity on the
wholesale market can cost around 6.28 cents per kilowatt-hour."**

This is real and properly sourced — but it is Dominion's own **average** estimated wholesale
purchase cost, not a spike or extreme-event figure. The non-primary summary that prompted this check
described it as "spot power can spike to 6.28 cents per kWh," which mischaracterizes the number
itself. The same Inspenet article, in the very next sentence, separately and distinctly cites the
real extreme-event figure already documented elsewhere in this project: Virginia SCC staff warning
that "spot prices can reach several thousand dollars per megawatt-hour during episodes of extreme
heat or prolonged periods of cold." These are two different, non-contradictory metrics measuring two
different things (a typical average vs. an extreme tail event) — there was no actual discrepancy
between sources, only a mislabeling of which figure represented which concept. **Correcting this
project's own earlier flagged "discrepancy"**: no contradiction exists once the 6.28¢ figure is
correctly understood as an average, not a spike.

**One genuinely new, useful figure surfaced from the same source**: the same testimony states
**"nuclear fuel would have an average cost of less than one cent per kilowatt-hour"** — a direct,
sourced comparison point putting the 6.28¢ wholesale-market average in context (roughly 6x or more
Dominion's own nuclear generation cost), and a real, attributable quote from Gaskill's own testimony:
"Each megawatt-hour generated by the company's own resources reduces the need to purchase energy on
the PJM market."

### 7.3 The "4.8 to 7.5 cents per kWh" data-center effective-rate figure — not found in either cited source, after reading both in full

Both sources a non-primary summary cited for this specific range (Yahoo Finance/The Cool Down, and
Inspenet) were fetched and read in full for this entry. **Neither contains this figure, or anything
resembling it, anywhere in the text.** Both articles instead contain the same, already-documented
3.95 cents/kWh fuel-cost-component figure and the 6.28 cents/kWh average wholesale-purchase figure
addressed in 7.2 above. This specific claim should be treated as unsupported by its own cited
sourcing unless a source directly confirming it is found elsewhere — not repeated as if verified.

### 7.4 Resolved — GS-5's specific per-kWh/per-kW rates are not yet publicly available anywhere; only the structural terms already documented in Section 1.3 exist in public sources

A multi-turn effort to obtain the actual filed GS-5 rate schedule (not just its structural terms)
concluded without finding one, and the reason is now confirmed rather than left as an open search
failure. A screenshot search intended to locate the GS-5 tariff page instead returned **Schedule
GS-3** (500 kW and above, an existing, different schedule) — traced directly to the source
document's own search function confusing the digits "3" and "5." Two independent transcription
attempts on a subsequent, genuinely low-resolution image also failed to produce a reliable reading,
and a side-by-side comparison of that transcription against the already-confirmed GS-3 figures
showed seven matching rate values in a row — strong evidence the second attempt was pattern-matching
against GS-3 rather than reading distinct GS-5 data, not a real transcription of a different
schedule. Both dead ends are recorded here for completeness, not repeated as findings.

**The underlying reason confirmed directly, via three independent, converging signals, rather than
assumed from a single AI-generated summary**:

1. **Dominion's own current, official rate-schedule listing does not include GS-5 at all**:
   "Customers that wish to participate in Retail Access will do so under Virginia Jurisdictional Rate
   Schedules 1, GS-1, GS-2, GS-3, GS-3EV, GS-4, 5C, 24, 27, or 28" — GS-5 is absent from Dominion's
   own published list, consistent with its January 1, 2027 effective date still being several months
   out from this research (August 2026).
2. **The single most detailed annotated legal analysis of the GS-5 order found anywhere in this
   research** (covering contract terms, the 14-year term, minimum-take provisions, and collateral in
   real depth) never cites a $/kWh or $/kW figure anywhere in it.
3. **Across this project's entire GS-5 research thread** — the full SCC press release read verbatim,
   dozens of legal and news sources, multiple dedicated searches — not one source has ever cited a
   specific per-unit rate for GS-5. Every source describes it exclusively in structural/contractual
   terms (the same terms already fully documented in Section 1.3: 25 MW/75% load factor threshold,
   85%/60% minimum-take, 14-year contract, $1.5M/MW collateral, three-years'-notice constraint).

**Conclusion, stated directly rather than left open**: GS-5's specific energy/demand pricing is not
yet public. The November 2025 biennial-review order established the structural/contractual
framework; the actual filed tariff sheet with per-unit rates has apparently not yet been published,
likely pending a separate compliance filing closer to the January 2027 effective date.

**Why this doesn't leave a gap in this project's own Scenario 3 work, and if anything reinforces the
existing conclusion**: nothing found anywhere suggests GS-5 introduces any new *dynamic*-pricing
mechanism. Every structural term documented is cost-allocation and risk-shifting machinery (minimum
payments, contract length, collateral), not a change to how energy itself is priced hour-to-hour.
GS-5 customers' actual underlying energy-rate mechanics almost certainly remain built on the same
TOU structure already confirmed for GS-4 (fixed, pre-scheduled on-/off-peak windows, not real-time
wholesale-linked pricing) — GS-5 layers new contractual terms on top of that existing mechanism
rather than replacing it with anything resembling the ComEd-style day-ahead/real-time design central
to Scenario 3's own Part D. This closes the loop on the original question that motivated this whole
GS-5 rate search: data centers are not moving to anything resembling dynamic retail pricing under
GS-5 either, so the earlier conclusion (no retail-price-driven flexibility incentive exists for
Virginia data centers today, under GS-4 or GS-5) stands confirmed rather than merely unresolved.

---

## Updated sources list (Section 7 additions)

- Bloomberg Tax, "Virginia Data Center Tax Needs Work, But Lays a Good Foundation" (opinion, dated
  within the past month)
- BDO, "Virginia Enacts Unprecedented Electricity Consumption Tax on Data Centers"
- Greenberg Traurig, "Virginia Legislature Approves Tax on Data Center Electricity Consumption"
  (Jun. 26, 2026)
- Williams Mullen, "Virginia Budget Creates New Electricity Consumption Tax for Data Centers"
  (Jun. 30, 2026)
- Holland & Knight, "Virginia Preserves Data Center Tax Incentive, Adds New Electricity Consumption
  Tax" (Aug. 2026)
- Data Center Knowledge, "Virginia Approves First-Ever Data Center Power Tax" (Jun. 23, 2026)
- MGrid, "Virginia Enacts First US Data Center Electricity Tax at $0.011/kWh" (Jun. 30, 2026) —
  source of the $48M/500MW and $100M/1GW magnitude figures
- Virginia budget bill text, HB30, Item 3-5.24#1c (budget.lis.virginia.gov) — primary legislative text
- Virginia Mercury, "Virginia legislators advance $205 billion budget including new tax on data
  centers" (Jun. 22, 2026)
- Yahoo Finance / The Cool Down, "Virginia data center boom drives utility costs up 88%..." (fetched
  directly in full, Aug. 19, 2026) — confirms 3.95¢ figure; does NOT contain 4.8-7.5¢ or 6.28¢
- Inspenet, "Data centers in Virginia increase energy pressure on Dominion" (fetched directly in
  full, Aug. 15, 2026) — source of the 6.28¢ average wholesale figure and the sub-1¢ nuclear figure,
  citing Dominion VP Scott Gaskill's own July 28, 2026 regulatory testimony

---

## 8. "Phantom" data center requests — the user's hypothesis that GS-5 was designed to filter speculative queue entries, confirmed directly

Prompted by a direct user hypothesis: given GS-5's minimum-take/collateral provisions, is it
plausible the class was specifically intended to weed out speculative ("phantom") interconnection
requests, not just allocate cost? Confirmed directly, not just plausible.

### 8.1 Direct confirmation, from a named attorney in the actual case

Nate Benforado, a Southern Environmental Law Center attorney who participated in the GS-5
proceeding, told Inside Climate News the financial commitments are **"the best way to shake out
that speculative load."** This is close to a direct statement of the user's own hypothesis, from
someone who was actually in the case, not an outside inference.

**The collateral figure's own contested history, not previously documented here**: Dominion
originally proposed $1.5 million/MW; the data center industry pushed to cut it to **$450,000/MW**
(a ~70% reduction), arguing Dominion was shifting its own shareholder risk onto customers. The
Commission kept the higher figure. A third, concrete instance (alongside the CIAC voluntary-payment
request and the Coalition Reliability Backstop Procurement, both already documented in Section 6) of
an industry-preferred term being directly rejected by the relevant regulator.

### 8.2 The scale of the phantom-load problem, quantified across several independent sources

- **"One expert estimated that speculative interconnection requests were five to 10 times more than
  the number of actual data centers"** (Utility Dive) — a real, if imprecise, order-of-magnitude
  estimate for the scale of the problem nationally.
- **"With 40 to 50 GW of phantom load in U.S. forecasts, the potential stranded investment exceeds
  $70 billion"** — each GW of unnecessary capacity estimated to cost $1-2 billion to construct.
- **Virginia-specific, Dominion-specific figure**: "between 2022 and 2025, Dominion Energy revised
  its 15-year load forecast upward by more than 40 percent, driven largely by speculative data
  center proposals in Loudoun County."
- **A real, Dominion-sourced split between committed and uncommitted pipeline** (Virginia Mercury,
  citing Dominion's own SCC testimony), distinct from and more precise than the 70,000 MW *requested*
  figure already used in the blue-whale comparison (entry #72): "the current list of projects the
  utility has slated for connection to the grid add up to **25,000 megawatts** of power and all have
  an energized date. The company has additional projects in the pipeline that would add **75,000
  MW** and do not have a power up date yet." This gives a direct, utility-sourced division of the
  pipeline into a firmly-committed portion (25 GW) and a portion without any confirmed timeline (75
  GW) — worth treating as a separate, complementary data point rather than conflating with the
  70,000 MW/32 GW figures already documented, since the underlying methodology and date differ.

### 8.3 Both sides agree the problem is real, even while disagreeing on the fix — worth preserving directly rather than flattening into one-sided advocacy

Genuinely balanced finding, not just regulator/advocate framing: **the Data Center Coalition itself
has separately complained that Dominion's own queue process doesn't adequately distinguish real from
speculative projects.** Cody Murphey (DCC): "As proposed by Dominion, the large load interconnection
queue process standards lack transparency and treat high quality, well capitalized projects, the
same as speculative projects." Separately, data companies testifying in that case, including Google,
"raised concerns that Dominion does not have financial guardrails in place to protect against
possible duplicate applications." **This means industry and consumer/regulatory advocates agree the
phantom-load problem is real** — they disagree about whether GS-5-style financial filters are the
right solution or an over-broad one that penalizes legitimate developers alongside speculative ones.

Also confirmed at the federal/PJM level, reinforcing this isn't a Virginia-only concern: PJM "has
warned of 'unclear and uncertain' data centre demand projections" and has "pushed utilities to throw
out projects which hide duplicative requests"; US Energy Secretary Chris Wright separately "urged
the Federal Energy Regulatory Commission to 'deter speculative projects.'"

### 8.4 GS-5 and the new consumption tax (Section 7.1) are not the same tool, and don't fail the same way — a real, useful distinction for future modeling

Directly stated by Enverus's own analysis, worth preserving precisely: **"One taxes what gets used.
The other taxes what gets reserved. They are not the same instrument, and they don't fail the same
way."** A consumption tax (Section 7.1) "is simple to explain to ratepayers but does nothing about
speculative capacity sitting idle in the queue" — it only ever charges for real, metered usage, so a
phantom request that never gets built never generates any tax revenue or queue cost either. A
capacity-based rate class like GS-5 "filters the queue but is harder to defend if a developer argues
they're being billed for power they never drew" — it directly discourages speculative filing (since
holding a queue position now carries real financial exposure) but is legally more contestable.
**Virginia is running both mechanisms simultaneously**, addressing genuinely different failure modes
of the same underlying problem rather than being redundant with each other.

### 8.5 The AEP Ohio precedent, a second, complementary figure to the one already documented

Already documented (Section 5.2, entry #77): Ohio's speculative queue dropped from 30 GW to 13 GW
after AEP's tariff. A second, related but distinct metric from the same underlying episode, found in
this search: **"connection requests dropped roughly 50% within months"** of the tariff taking
effect. These are two different measurements (total speculative queue volume vs. number of
connection requests) from the same real-world precedent, not competing or contradictory figures —
worth citing both, since they measure different things and a future analysis might need one or the
other depending on what's being modeled.

---

## Updated sources list (Section 8 additions)

- Enverus, "Why Virginia Is Taxing Data Centers Two Different Ways" (blog, within past 2 weeks of
  this research) — source of the "taxes what gets used vs. reserved" distinction and the AEP Ohio
  "~50% connection request drop" figure
- AIX Energy, "Managing Data Center Uncertainty Part II — Phantom Data Centers: How Strategic
  Opacity Drives Overbuild" (Nov. 18, 2025) — source of the 40-50 GW/$70B stranded-investment
  figures and the Dominion 40%-forecast-revision figure
- LPPC (citing Financial Times/other wire coverage), "'Phantom' data centres muddy forecasts for US
  power needs" (Nov. 14, 2025) — source of the PJM and Energy Secretary Wright quotes
- Utility Dive, "A fraction of proposed data centers will get built. Utilities are wising up."
  (May 15, 2025) — source of the "5-10x" speculative-request estimate
- Forbes, "Virginia Now Makes Data Centers Post $1.5 Million A Megawatt" (Jun. 10, 2026) — source of
  the Benforado quote and the $1.5M vs. $450K collateral negotiation history
- Virginia Mercury, "New state law mandates review of Dominion's load forecasting..." (Apr. 30,
  2026) — source of the DCC/Murphey quote, the Google testimony, and the 25,000 MW/75,000 MW
  committed-vs-uncommitted pipeline split
- ONMINE, "Phantom data centers: What they are (or aren't)..." (undated, recent)
- Compute Law Blog, "Virginia PJM market and Dominion power service for AI data centers" (May 23,
  2026) — background on the ELOA/CLOA/ESA three-stage contractual process already partially
  documented elsewhere in this appendix
- Enkiai, "Dominion Energy's 2026 Pivot: Taming Data Center Demand" (Apr. 28, 2026)

---

## 9. Public and political opposition — a distinct, non-financial constraint on how much of the pipeline actually gets built

Raised directly by the user: rising public opposition, including in traditionally permissive states
like Texas, as another real-world reason the requested/announced pipeline overstates what will
actually be built — distinct in mechanism from the phantom-load/financial-filtering material in
Section 8, though pointing the same direction on the "requested vs. actual" question central to this
appendix.

### 9.1 The Gallup poll, confirmed precisely, not just approximately

Fetched directly from Gallup's own site. The precise figure is **71%** ("seven in 10" is the
accurate rounding the user used), with **48% "strongly" opposed** and only **7% "strongly" in
favor**. Real methodology behind it: telephone interviews conducted by Recon MR, March 2-18, 2026,
1,000 U.S. adults, ±4 percentage point margin at 95% confidence — a standard, credible national poll,
not a fringe or low-quality source.

**A genuinely striking comparison point from the same poll**: opposition to local AI data centers
(71%) now *exceeds* opposition to local nuclear power plants (53%) — "Americans now appear more
willing to live near a nuclear plant than an AI data center," as one outlet summarized it.

**Reasons for opposition, quantified directly from Gallup's own breakdown**: half of opponents cite
excessive resource use (18% each specifically citing water and energy); 16% cite pollution
(including noise, air, water); about one in five cite local quality-of-life impact; a similar share
cite economic concerns (higher utility bills, cost-of-living increases, use of taxpayer funds).

**The single most directly relevant figure for this appendix's own "requested vs. actual" theme**:
per Wikipedia's own sourced summary (citing Data Center Watch), **"in 2025, local opposition to AI
data centers led to the delay or cancellation of projects totalling US$156 billion."** This is a
real, quantified dollar figure for capacity actually removed from the pipeline by public opposition
specifically — a third, distinct mechanism (alongside AEP-Ohio-style financial-filtering tariffs and
chip-availability constraints, both already documented) pointing toward the same conclusion: the
requested pipeline systematically overstates what gets built, for several independent reasons, not
just one.

**A second, independent poll, not Gallup, showing an even higher figure**: a Heatmap Pro poll found
"three-quarters of Americans say they'd oppose a data center near their home, and more than six in
10 strongly so" — worth citing as a cross-validating (though not identical) data point, not treated
as redundant with Gallup's own 71%/48% figures.

### 9.2 Texas, confirmed directly as a genuine, high-profile case — not just "some pushback," but the state's own Republican governor reversing course

**Governor Greg Abbott himself — previously the most enthusiastically pro-data-center voice among
state officials, having called Texas "the epicenter of AI development" as recently as November
2025 — reversed course directly**: in July 2026 he "called for blocking new data center development
in rural parts of the state"; in August 2026 he "ordered regulators to set new restrictions and
conduct an audit before permitting any more projects to break ground," which one source describes as
"effectively creating a statewide pause on new projects until the review is complete." This is not a
minor policy adjustment — it is the state's own chief executive, previously the industry's biggest
booster, imposing what amounts to a de facto moratorium.

**The scale in Texas, quantified directly**: at least 248 data center projects planned statewide
(second only to Virginia nationally); more than half of Texas's proposed data centers are headed to
rural areas; and — the single most directly relevant figure to the user's own "even rural
Republicans" framing — **"the majority of facilities planned or under construction are in state
House districts that voted for President Donald Trump and elected a Republican state representative
in 2024,"** per the Texas Tribune's own district-level analysis. This is a real, quantified
confirmation, not just anecdote: most of the projects triggering opposition sit in solidly
Republican-held territory, directly explaining why Republican officials are breaking with their own
party's usual small-government, pro-development instincts.

**A real, named grassroots organization**: the Texas Coalition Against Datacenters, described as
"grassroots, social-media-originated." A directly quoted activist (Rena Schroeder): fighting "for
Texas land because if I don't, where's my daughter gonna go? This is her inheritance right here."

**A genuinely important nuance on the limits of local action, not just its existence**: Hill County
was the first Texas county to pass a moratorium, but "quickly reversed course after getting hit with
a $100 million lawsuit by a data center developer" — which "caused other Texas counties to abandon
similar plans." This is a real, concrete illustration of a countervailing legal force: public
opposition is genuine and widespread, but county-level moratoriums face real legal and financial
risk from developer litigation, meaning opposition doesn't translate mechanically into blocked
projects at the local level. State-level action (Abbott's own audit/pause) has proven more durable
than county-level moratoriums specifically because it doesn't carry the same direct litigation
exposure to a single jurisdiction.

**Confirmed as a live 2026 electoral issue, not just a policy dispute**: State Rep. Gina Hinojosa,
the Democrat challenging Abbott, is campaigning on a full moratorium; several rural GOP county chairs
signed a letter to Abbott urging a special legislative session on data center rules; anti-data-center
groups in various Texas communities have "openly urg[ed] members to vote against Republicans, or not
vote at all" — a direct threat to the state's own dominant party's normal voter coalition.

### 9.3 This is a national, not Texas-specific or Virginia-specific, pattern — with real electoral evidence

**A national, non-Texas data point on the underlying geography of the issue**: per the Pew Research
Center (cited via a secondary source, not yet independently verified from Pew directly), "two-thirds
of new data center construction or planned sites are in rural areas" nationally — meaning the
Texas pattern (rural-sited projects, rural political backlash) is not a Texas-specific anomaly but
reflective of where the industry is actually building nationwide.

**Real, named electoral examples beyond Texas**, confirming this cuts across the political spectrum
rather than being a single-party issue: in Ohio's governor's race, both the Republican candidate
(Vivek Ramaswamy, who has called for data center companies to cover nearby residents' power bills)
and the Democratic candidate (Amy Acton, proposing a "conditional moratorium") are addressing data
center opposition directly; in Michigan's 7th Congressional District, a Democratic primary candidate
(Abdul El-Sayed) found the issue resonating with his own populist-economics campaign themes without
it being his central pitch. Bernie Sanders has separately called for a national moratorium — real,
direct evidence of opposition spanning from the progressive left to the Trump-aligned right, not a
single ideological faction's concern.

**A dated, named nationwide protest event, confirming organized opposition beyond polling
sentiment**: a nationwide protest against AI data center expansion took place outside Peace Hall in
New Port Richey, Florida, on July 18, 2026 — one specific, dated, documented instance of the
"dozens of protests against AI data centers since 2022" that Data Center Watch has tracked, per
Wikipedia's own sourced summary.

### 9.4 Why this matters for this appendix's own "requested vs. actual" theme, stated directly

This appendix has already documented two other independent reasons the requested/announced pipeline
overstates what will actually be built: financial-filtering tariffs modeled on AEP Ohio's own
precedent (Section 5.2/8.5), and physical supply constraints like chip availability (Section 6.1).
**Public and political opposition is a third, genuinely independent mechanism pointing the same
direction** — not redundant with the other two, since it operates through a different channel
entirely (siting/permitting/political viability, rather than cost-allocation economics or physical
component supply). The $156 billion 2025 delay/cancellation figure (9.1 above) is a real, if
imprecise, order-of-magnitude anchor for this mechanism's own scale, comparable in kind (though not
directly additive, given different measurement methodologies and time periods) to the AEP Ohio
30→13 GW and Dominion's own 25,000/75,000 MW committed/uncommitted split already documented.

---

## Updated sources list (Section 9 additions)

- Gallup, "Americans Oppose AI Data Centers in Their Area" (May 13, 2026) — primary source, fetched
  directly
- Washington Post, "7 in 10 Americans oppose data centers being built in their communities" (May 13,
  2026)
- The Hill, "Poll: Nearly half of Americans against AI data centers in their area" (May 13, 2026)
- ConstructConnect News, "Gallup Survey Finds Local Opposition to Data Centers as U.S. Construction
  Surges" (May 14, 2026) — source of the $46.5B/2026-starts and $63.2B pipeline figures
- Planetizen, "More Americans oppose data centers than nuclear plants: Gallup" (Jul. 9, 2026)
- Townhall, "Americans Are United Against Data Centers" (Aug. 24, 2026) — source of the 63%-of-
  Republicans figure
- NPR, "Data centers are a political issue crossing party lines, driving voters to candidates"
  (Aug. 8, 2026) — source of the Ohio and Michigan electoral examples and the July 18, 2026 New Port
  Richey, FL protest
- Wikipedia, "Opposition to AI data centers" — source of the $156B 2025 delay/cancellation figure
  (citing Data Center Watch) and the Pew Research two-thirds-rural figure
- Houston Public Media, "Gov. Greg Abbott calls for ban on data center development in rural Texas
  neighborhoods" (Jul. 1, 2026)
- Texas Tribune, "Texas Republicans have a data center problem" (May 7, 2026) — source of the
  district-level Trump/GOP-representative figure and the Rena Schroeder quote
- Houston Chronicle, "Are Greg Abbott's new data center restrictions enough to sway rural voters?"
  (Aug. 2026) — source of the GOP county chairs' letter and Hinojosa campaign detail
- MultiState, "The local fight over data centers: A Texas case study" (Aug. 19, 2026) — source of
  the 248-projects figure, the Hill County lawsuit/reversal detail, and the statewide-audit-as-pause
  characterization
- Rural News Clips (Substack)/Daily Yonder Q&A with Taylor Goldenstein — source of the "unicorn,
  bipartisan issue" framing and the Heatmap Pro poll citation
- Times-Journal, "Opposition to data centers uniting polar extremes of political spectrum" (Aug. 20,
  2026) — source of the Bernie Sanders moratorium call and additional Abbott detail

---

## 10. Broader AI-risk sentiment — a distinct thread from data-center siting opposition, and a real distinction between expert assessment and public opinion worth preserving

Raised by the user as a related but broader concern: public alarm not just about local data-center
siting (Section 9), but about AI itself — job displacement, misalignment, truthfulness, and other
risks. Two genuinely different kinds of evidence were checked here, and they should not be
conflated with each other or with the Gallup siting-opposition poll in Section 9.

### 10.1 The MIT AI Risk Initiative — an expert consensus study, not a public-opinion poll

**Important distinction, confirmed by fetching the page directly rather than assumed from the
user's own framing**: this is not a survey of the American public. It is a Delphi-method study
surveying **272 international experts** — "AI risk and governance practitioners from financial
services and other large corporates," "AI safety experts at the Korea and UK AI Safety Institutes,"
"professors and researchers from MIT, Harvard, Oxford, Stanford, Tsinghua and more," and "AI
policymakers from national governments." Funded by Commonwealth Bank of Australia, which "reviewed
the design, but did not influence the collection, analysis, interpretation or reporting of the
data." This is expert risk assessment, not public sentiment — a genuinely different, complementary
kind of evidence to the Gallup/Pew material in 10.2 and Section 9, not a redundant restatement of
it. Worth keeping this distinction explicit in any future use of this material, since the user's own
framing ("Americans are alarmed... captured by the MIT AI Risk Initiative") could be read as implying
the study itself measures public alarm, when it measures expert judgment instead.

**Key findings, directly relevant to the user's own named concerns**:
- **18 of 24 assessed AI risk domains carry ≥10% probability of catastrophic outcomes within five
  years** under a "business as usual" (no additional mitigation) scenario — catastrophic defined as,
  for example, over 1 million deaths, over $100 billion in damage, or civilization-scale intangible
  harm such as collapse of democratic norms or privacy.
- **A named, defined risk domain directly matching the user's "propensity for misalignment" point**:
  "AI pursuing its own goals in conflict with human goals or values" — defined as AI that "may arise
  in design and may lead AI to use manipulation, deception, or situational awareness to seek power or
  self-proliferate."
- **A named, defined risk domain directly matching "not always be truthful"**: "False or misleading
  information" — AI that "inadvertently generate[s] or spread[s] incorrect or deceptive information."
- **A named, defined risk domain directly matching "job displacement"**: "Increased inequality and
  decline in employment quality" — with a direct expert quote: "AI may exacerbate existing
  inequalities through automation-driven job losses in certain sectors while creating wealth for
  those who own and control AI systems."
- **A "responsibility gap" finding directly relevant to the user's own separate point about
  "distrust in tech leadership"**: experts found "AI users and the general public are most
  vulnerable to risks, but general-purpose AI developers and governance actors are most responsible
  for addressing them" — a real, expert-validated mismatch between who bears the risk and who holds
  the power to address it, offered as a structural explanation for public distrust rather than mere
  public sentiment about it.
- **A named risk domain with a direct data-center connection**, worth cross-referencing against
  Section 9's own findings on why the public opposes local siting: "Environmental harm" is explicitly
  defined to include harm "through data center energy consumption or the materials and carbon
  footprints of AI hardware" — meaning the same water/energy/pollution concerns Gallup's own
  respondents cited (Section 9.1) are independently recognized as a legitimate risk category by this
  separate expert panel, not merely a public misunderstanding of a technology experts consider safe.

### 10.2 Pew Research Center's own job-fear data — confirmed, with one sourcing correction

**Correction**: the user's own citation pointed to a Washington Post article, but the Post (writer
Shira Ovide) was reporting on a separate, primary survey — the actual source is **Pew Research
Center**, not the Post itself. Worth citing Pew directly as the primary source going forward.

Confirmed precisely across many independent outlets (Pew's own site, Axios, Bloomberg, Courthouse
News, The Register): survey conducted **June 22-28, 2026, 3,488 U.S. adults**.

- **73% of adults under 30 now expect AI to lead to fewer jobs over the next 20 years, up from 61%
  in 2024** — the user's own figure, confirmed exactly.
- **A broader, all-age figure, also real and worth including**: 71% of all U.S. adults think AI will
  lead to fewer jobs over the next two decades (up from 64% two years ago); "just 5 percent believe
  the optimists who say AI will lead to more jobs."
- **A genuine generational reversal, not just a static statistic**: 55% of adults under 30 are now
  "more concerned than excited" about AI (up from 31% in 2021, "the first majority since Pew began
  asking the question in 2021"), while only ~10-11% are "more excited than concerned" (down from 25%
  in 2021). Young adults have gone from AI's most enthusiastic cohort to among its most skeptical in
  five years.
- **A real, carefully-hedged empirical data point worth preserving with its own caveats intact, not
  just the polling figures**: "a Stanford payroll study found no widespread economy-wide
  displacement, but workers ages 22-25 in highly AI-exposed occupations had a 19% employment
  shortfall relative to less-exposed peers. The Stanford result is descriptive, not causal, and was
  larger in the ADP payroll sample than in national benchmarks." This is a real labor-market data
  point, distinct in kind from the polling/sentiment figures around it — it measures actual
  employment outcomes, not perceptions, though the source itself is explicit that it shows
  correlation/description rather than proven causation.

### 10.3 Why this belongs in this appendix, stated directly rather than left implicit

This section is deliberately kept distinct from Section 9's data-center-siting-opposition material,
even though both ultimately bear on public sentiment toward the AI/data-center buildout. Section 9
covers opposition to *where* facilities get built (siting, water, local grid strain). This section
covers broader unease about *what AI itself does* (jobs, truthfulness, misalignment, power
concentration) — a genuinely separate, though related, current running alongside the siting-specific
backlash. Both are real and both plausibly bear on the same underlying question already central to
this appendix (how much of the announced/requested pipeline actually gets built), but they operate
through different channels — siting opposition blocks specific projects directly; broader AI
skepticism plausibly affects political will for pro-AI-buildout policy, investor sentiment, and labor
availability/support for the industry more diffusely, rather than blocking individual projects the
way a county moratorium does.

---

## Updated sources list (Section 10 additions)

- MIT AI Risk Initiative, "Priority AI risks" (airisk.mit.edu/priorities) — fetched directly in
  full; primary source for the Delphi study findings
- Washington Post, "Americans under 30 are becoming more pessimistic about artificial intelligence"
  (Aug. 18, 2026) — secondary coverage; primary source is Pew, below
- Pew Research Center, "Young US adults are increasingly wary of AI, concerned it will take jobs"
  (Aug. 18, 2026) — primary source for the 73%/71%/55% figures
- Axios, "AI optimism fades as young adults worry about jobs" (Aug. 18, 2026)
- Bloomberg, "Young Americans Become More Hostile to AI, Fearing Job Losses" (Aug. 19, 2026)
- Courthouse News Service, "Pew: Young Americans grow more wary of AI as job fears rise" (Aug. 2026)
- The Register, "More than half of Americans now view AI negatively" (Aug. 19, 2026)
- Implicator.ai, "Young Adults' AI Concern Reaches 55% as Job Fears Rise" (Aug. 2026) — source of the
  Stanford payroll-study detail

---

## Note — a project-wide implication, held for future discussion, tracked centrally

Sections 8-10 above, taken together, motivated a direct user question about whether this project
should build a second, lower demand-projection model set across *all* scenarios (not just S3/A.7),
given four independent mechanisms (phantom-load filtering, physical supply constraints, financial
filtering, and public/political opposition) all pointing toward the same conclusion: the announced
pipeline this project's current demand projections are built against likely overstates actual 2045
build-out. This is explicitly held as a future discussion, not yet scoped or acted on. Tracked
centrally in `Scenario3_Scope_and_Gaps.md`, Section 11, rather than only here, since it is a
project-wide methodological question that would affect every scenario's own demand assumptions, not
an A.7-specific one — this appendix is where the motivating evidence lives, but the decision itself
belongs in the main scope document alongside this project's other standing structural/methodological
questions.
