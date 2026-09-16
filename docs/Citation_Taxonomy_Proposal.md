# Citation Tagging Taxonomy — Official Structure (v2, hierarchical)

*Revised 2026-09-03 in response to direct user critique of the v1 flat-list structure,
then confirmed as this project's official tag taxonomy (with one further correction
to Axis D's EV-charging cross-reference) — direct user instruction, 2026-09-03.
The prior proposal version is preserved unchanged at
`Citation_Taxonomy_Proposal_v1_flat.md`. This version is now being actively applied
to all 100 rows in `Master_Citations.xlsx`.*

## The two problems this revision fixes, and the core design change

**Problem 1 (user-identified): flat lists mixing parent and child concepts as
peers**, and hierarchical relationships that cross group boundaries invisibly (e.g.
`load-shifting` in one group, `dynamic-pricing` in another, with no link between
them despite a real relationship).

**Problem 2 (user-identified): redundant tags** — the same underlying concept
represented by two different tag names in two different groups (e.g.
`A.1-day-ahead-real-time-pricing` and `DA/RT`).

**The fix is not one bigger tree — it's recognizing this taxonomy has multiple,
genuinely independent axes**, each internally hierarchical, cross-referenced rather
than merged. Verified this directly against Abunima et al. 2018 (*Impacts of
Demand-Side Management on Electrical Power Systems: A Review*, Energies 11(5):1050,
Figures 1-2) — the concrete model pointed to. Reading it precisely surfaced exactly
the flaw the user flagged in their own hierarchy: they nest TOU, Critical Peak Rate,
and Real-Time Rate all as children of a category called "Real-Time Pricing Program"
— but TOU is a fixed, pre-set schedule, the opposite of real-time. Naming a parent
after one property (real-time-ness) that not all of its own children share is a
real structural error, not just a style choice. Their paper is still useful for one
thing this version adopts: DSM's own three-branch top split (EE / DR / **Strategic
Load Growth** — a genuine third branch this taxonomy was missing entirely), and DR's
own reliability-based vs. market-based split.

**General rule applied throughout this revision**: a tag is a *child* of another tag
only when it is genuinely a specific instance/type of that parent (an "is-a"
relationship). Where the real relationship is causal, associative, or "commonly
co-occurs with" rather than is-a, the two tags stay in separate axes with an
explicit cross-reference note instead of being forced into one tree.

---

## AXIS A — Scenario 3 structural elements (unchanged; this project's own necessary
identifier system, and the PRIMARY identifier wherever it overlaps with a generic
industry term elsewhere in this taxonomy — see redundancy fixes throughout)

**Category A — Demand-Side Management**
- `A.1-day-ahead-real-time-pricing` — general-industry synonym/child: `DA/RT` (moved
  here from the old flat Group 3; no longer a separate peer tag)
- `A.2-incentive-DR-smart-thermostat-EV`
- `A.2-water-energy-rewards-DLC`
- `A.2-large-CI-curtailable-tariffs`
- `A.3-heat-pump-efficiency-PHIUS`
- `A.4-heat-pump-water-heaters`
- `A.5-conservation-voltage-reduction`
- `A.6-thermal-energy-storage`
- `A.7-data-center-demand-flexibility` — children (folded in from the old, separate
  Group 7, which was itself a flat peer list that actually nests under this single
  A.7 element): `data-center-siting`, `data-center-load-magnitude`,
  `data-center-flexibility-mechanism`

**Category B — Solar/Storage Location Allocation**
- `B.1-ownership-Dominion-owned`
- `B.1-ownership-third-party-PPA`
- `B.1-ownership-unbundled-REC`
- `B.1-ownership-DER-rooftop`
- `B.1-ownership-DER-parking-canopy`
- `B.2-siting-percentages`

**Category C — Land Use and Siting**
- `C.1-siting-types`
- `C.2-agrivoltaic-land-accounting`
- `C.2-rooftop-canopy-land-treatment`

**Category D — Market Participation**
- `D.1-market-access`
- `D.2-supply-side-price-response`
- `D.2-school-bus-V2G`
- `D.2-citizen-EV-V2G`
- `D.2-municipal-transit-V2G`
- `D.3-compensation-structure`

---

## AXIS B — DSM/DR taxonomy (fully rebuilt as three separate sub-axes, replacing the
old flat Group 2 + Group 3, which mixed load-shape outcomes, program mechanisms,
and rate designs together as peers)

### B1 — Load-shape outcome (what happens to the load curve — a DSM measure's
*effect*, independent of what caused it)

- `shed` (= event-based curtailment; this taxonomy's prior `peak-clipping` /
  NSPM's own "Shed")
- `shift` (= this taxonomy's prior `load-shifting` / NSPM's "Shift")
- `valley-fill` (**new** — a genuinely distinct third outcome named in Abunima et
  al., missing from the prior version entirely: building load during off-peak
  periods, the complement of shedding)
- `conserve` (= this taxonomy's prior `load-reduction` / Gellings' "Strategic
  Conservation" — permanent reduction, NOT the same as `shed`; this distinction was
  flagged and preserved correctly in v1 and carries forward unchanged)
- `modulate` (= NSPM's "Modulate" — continuous, fine-grained adjustment, not a
  discrete shed/shift/valley-fill event)

### B2 — Program mechanism (how the utility/program induces the outcome above —
independent of which outcome results)

- `direct-load-control` (= DLC; moved here from the old Group 6, where it was
  redundant with a device/platform-level tag — DLC is the *program type*, not the
  device. See Axis D for the device-level tag, `smart-thermostat`, which
  cross-references this)
- `price-signal` — children (rate-design *types* nest here, not as a separate
  top-level group, since they're all specific ways a price signal can be designed):
  - `DA/RT` (redundant with `A.1` in Axis A — kept here as a cross-reference note
    only, not a duplicate live tag)
  - `TOU`
  - `CPP`
  - `CPR`
- `EE-measure`
- `interruptible-tariff`
- `emergency-program`
- `automated-EE-DR-hybrid` (a cross-cutting combination of `EE-measure` +
  `price-signal`/`direct-load-control`, kept as its own tag since this project uses
  it as a named, recurring mechanism type — see NSPM's own "EE enables DR" /
  "EE affects magnitude of DR benefits" interaction, directly relevant to this
  project's own A.2/A.3 double-counting risk)
- `passive-automatic` (CVR-type — no active customer/program decision point)

### B3 — Reliability-based vs. market-based DR (Abunima et al.'s own top DR split —
a genuinely useful, distinct third sub-axis, since it answers a different question
than B1 or B2: *who bears the risk/gets the incentive structure*)

- `reliability-based-DR` — children: `interruptible-load-program`,
  `direct-load-control-program` (cross-references B2's `direct-load-control`),
  `emergency-program` (cross-references B2's `emergency-program`)
- `market-based-DR` — children: `demand-bidding-program`, `price-signal`
  (cross-references B2's `price-signal` branch directly)

### Cross-axis relationships (associative, not is-a — kept explicit rather than
forcing a single tree)

- A `price-signal` program (B2) commonly *produces* a `shift` or `shed` outcome
  (B1), but doesn't have to — this is causal, not hierarchical.
- `direct-load-control` (B2) can also produce `shift` or `shed` (B1) with no price
  signal involved at all — the same outcome, different mechanism.
- `NWS` (Axis I) commonly *relies on* `conserve`/`shift`/`shed` capability (B1) —
  NSPM's own NWS definition names this explicitly, but NWS is an outcome/use-case
  concept, not a parent of the mechanism tags.

---

## AXIS C — Generation & storage technology (split into two genuinely separate
parent categories, replacing the old flat Group 4; `ELCC` removed entirely — moved
to Axis K, where it was already redundantly duplicated)

**Generation technology**
- `solar` — child: `agrivoltaics` (a siting *configuration* of solar, not a separate
  generation technology — was incorrectly a flat peer in v1)
- `wind`
- `gas`
- `nuclear`

**Storage technology**
- `battery-storage` — children: `Li-ion`, `Na-ion`, `iron-air` (all genuinely
  battery chemistries, correctly nested)
- `pumped-hydro` (a peer of `battery-storage`, NOT a child of it — a fundamentally
  different storage technology; was incorrectly flattened alongside the battery
  chemistries in v1)

---

## AXIS D — Automation/technology platforms (revised; `DLC` removed — it now lives
only in Axis B2 as a program-mechanism concept, not duplicated here as a platform)

- `HEMS`
- `BEMS`
- `smart-thermostat` (cross-references Axis B2's `direct-load-control` — this is the
  device that implements that program mechanism)
- `EV-charging` (cross-references Axis B2's `direct-load-control` — a base/managed
  EV charger is a DLC-capable device the same way `smart-thermostat` is; this
  project's own Axis A label `A.2-incentive-DR-smart-thermostat-EV` already names
  both together as the same DLC-style program element) — child: `V2G` (a specific
  *bidirectional* capability, distinct from the base managed-charging mode above —
  not itself a DLC cross-reference, since V2G is a different, more advanced
  capability than pause/delay)

---

## AXIS E — DER/VPP compensation & market structure (the NEM structural error from
v1 corrected: NEM was incorrectly treated as the parent of three other mechanisms
it's actually a peer of)

- `DG-compensation-mechanism` (**new parent**, corrects the v1 error) — children,
  four genuine peers per NSPM Ch. 10: `NEM`, `net-billing`, `buy-all-sell-all`,
  `community-solar`
- `LSRV`
- `DRV`
- `D-REC`
- `VPP`
- `DERA`
- `value-stacking`
- `wholesale-arbitrage`
- `QF-PURPA` (a distinct federal DG-interconnection framework — kept separate from
  the FERC-order tree in Axis L since it's a different statute, PURPA, not a FERC
  order)

---

## AXIS F — [retired as a standalone axis] Data centers — folded entirely into
Axis A's `A.7-data-center-demand-flexibility`, since every one of the old Group 7
tags was actually a child of that single Scenario-3 element, not a separate,
free-standing topic. See Axis A above.

---

## AXIS G — Cost & economic methodology (the largest revision — `avoided-cost`
becomes the explicit parent of the five-perspective structure rather than sitting
beside it as an unconnected peer tag; `resource-adequacy` removed, duplicated with
Axis K; `lost-revenues-vs-system-costs` moved to Axis N, where it belongs
conceptually with the rest of the rate/bill-impact material)

- `SLCOE`
- `SC-CO2`
- `NPV`
- `avoided-cost` (**parent**, corrected from v1's flat, disconnected placement) —
  children, NSPM's own five-perspective structure (Ch. 6), each with its own
  further-nested sub-impacts, verified directly against NSPM's own table structure:
  - `electric-utility-system-impact` → `generation-impacts`,
    `transmission-impacts`, `distribution-impacts`, `general-impacts`
  - `natural-gas-utility-system-impact` → `distribution-impacts` (gas),
    `general-impacts` (gas)
  - `other-fuel-system-impact`
  - `host-customer-impact` → `host-customer-energy-impacts`,
    `host-customer-non-energy-impacts`, `host-customer-resilience`
  - `societal-impact` → `societal-resilience`
- The eight former "NSPM Principles" (confirmed genuinely flat/co-equal per NSPM's
  own presentation — no change from v1): `policy-alignment`, `utility-system-
  resource`, `material-impacts`, `symmetry`, `forward-looking`, `avoid-double-
  counting`, `separate-from-complementary-analyses`, `transparency`
- BCA test types (confirmed genuinely flat/co-equal — JST is NSPM's recommended
  approach, not a parent/container of the traditional five, so keeping all six as
  peers is correct, not a v1 error): `JST`, `UCT-PACT`, `TRC-test`, `SCT-test`,
  `RIM-test`, `participant-test`
- `use-case` (NSPM's own central organizing concept for every DER, Ch. 11)
- `reference-case-vs-DER-case`
- `proxy-values`
- `net-benefits-vs-BC-ratio`
- `CPCN-justification` (moved here from the old Group 12, since it's fundamentally
  a BCA-application context per NSPM Appendix A.3, not a regulatory-framework tag
  like VCEA/RPS) — children: `repower`, `ceiling-price` (both were incorrectly flat
  peers of VCEA/RPS/FERC-order in v1; they're specific concepts *within* the CPCN-
  justification use case, not general regulatory frameworks)

---

## AXIS H — Grid/demand flexibility (explicit parent/child nesting, replacing v1's
flat pair)

- `grid-flexibility` (**parent** — system-wide balancing capability) → child:
  `demand-flexibility` (a *component* of grid flexibility specifically,
  consumer-side — NSPM's own stated relationship, corrected from v1's flat peer
  listing)

Cross-axis note: Axis A's `data-center-flexibility-mechanism` is a specific
instance of `demand-flexibility`, not a child of it in this axis — flagged as a
cross-reference, not merged, since A.7 needs to stay under Axis A structurally.
Methodological reminder carried forward from v1: NSPM states flexibility is not its
own BCA line-item — it modifies the *magnitude* of other impacts.

---

## AXIS I — Outcome-level DER combination patterns (confirmed genuinely flat/
co-equal — no v1 error here; these four are real peers, each a distinct "use case"
pattern at the same level)

- `NWS` (Non-Wires Solution)
- `NPS` (Non-Pipes Solution)
- `bridging-solution`
- `microgrid`

Cross-axis note: `NWS`'s own NSPM definition explicitly relies on Axis B1's
`shed`/`shift`/`conserve` capability — an associative link, not a parent-child one,
kept as a note rather than nesting B1 under I.

---

## AXIS K — Reliability & Resource Adequacy (now the sole home for `ELCC` and
`resource-adequacy`, both removed from their duplicate locations in Axes C and G;
internal nesting added since `ELCC` is a specific method, not a peer of the broader
concept it's a method for)

- `reserve-margin`
- `resource-adequacy`
- `capacity-accreditation` (**parent**, corrected from v1's flat listing) → child:
  `ELCC` (one specific accreditation methodology, not a peer concept)
- `reliability-compliance`

---

## AXIS L — Regulatory & policy (repositioned; `CPCN-justification`/`repower`/
`ceiling-price` moved OUT to Axis G, since they're BCA-application concepts, not
general regulatory-framework tags; `FERC-order` is now the explicit parent of the
specific order already living in Axis E)

- `VCEA`
- `RPS`
- `FERC-order` (**parent**) → child: `FERC-2222` (a specific order; cross-
  references Axis E, where FERC-2222/DER-aggregation material actually lives —
  kept as a pointer here rather than duplicating the full DER-market content)
- `SCC-proceeding`
- `Dominion-tariff`
- `PJM-rules`

---

## AXIS M — Geography/jurisdiction (split into two genuinely different levels of
abstraction that were incorrectly flattened together in v1 — state/jurisdiction is
not the same kind of thing as utility/ISO)

**State/jurisdiction level**: `Virginia`, `CA`, `HI`, `MD`, `WA`
**Utility/ISO level**: `ComEd-IL`, `NY-NYISO`
**Regional/multi-state**: `EU-UK`

---

## AXIS N — Rate/bill impact analysis (Appendix B material — now includes
`lost-revenues-vs-system-costs`, moved here from Axis G, since it's conceptually
the same distinction as `BCA-vs-rate-impact-question` already in this axis)

- `participant` / `non-participant` (a genuine pair, not a hierarchy)
- `sunk-costs`
- `BCA-vs-rate-impact-question`
- `lost-revenues-vs-system-costs` (moved from Axis G)
- `cost-recovery-mechanism` (**new parent**, corrects a v1 flat pairing) →
  children: `decoupling`, `performance-based-ratemaking`

---

## AXIS O — Equity and economic-development analysis (renamed the two
similar-looking acronyms to avoid confusion, and nested each analysis's own
metrics underneath it rather than leaving them as flat peers)

- `DEA-distributional-equity` (**parent**, renamed from bare `DEA` to disambiguate
  from the economic-development acronym below) → children: `priority-populations`,
  `energy-burden`
- `EDA-economic-development` (**parent**, renamed from bare `EDA` for the same
  reason) → children: `job-years`, `GDP-impact`

---

## AXIS P — Geographic/regional boundary questions (confirmed mostly flat/
co-equal, with one genuine nesting opportunity added: the two emissions-specific
boundary questions share a real parent the price-effects question doesn't)

- `MPE` (Market Price Effects)
- `offsetting-transfers`
- `emissions-boundary-question` (**new parent**, corrects a v1 flat pairing) →
  children: `GHG-boundary-question`, `criteria-pollutant-boundary-question`

---

## AXIS Q — BCA process framework (confirmed genuinely sequential, not
parent-child — no change from v1)

`Phase-1-develop-primary-test` → `Phase-2-select-methodologies` →
`Phase-3-conduct-and-interpret`

---

## AXIS R — Cross-cutting technical terms (genuinely standalone, applied across
multiple other axes rather than nested under any one of them)

- `BTM` / `FTM` (behind-the-meter / front-of-the-meter)
- `ELEC` (electrification-related DERs, NSPM's own shorthand) — cross-reference
  note: Axis A's `A.3-heat-pump-efficiency-PHIUS` and `A.4-heat-pump-water-heaters`
  are specific instances of the broader `ELEC` category, not children of it in this
  axis, since they need to stay under Axis A structurally.

---

## Evidence-type and modeling-method metadata columns (unchanged from v1 — these
were never part of the flat-list problem, since they were already correctly
designed as separate metadata fields, not topic tags)

- `Evidence_Type`: `field-pilot` `simulation` `meta-analysis` `regulatory-filing`
  `industry-standard`
- `Modeling_Method`: `LP-optimization` `Monte-Carlo` `econometric-regression`
  `machine-learning` `agent-based` `survey-stated-preference` `N/A`

---

## Full redundancy-elimination summary (every fix made in this revision, in one
place for quick review)

1. `A.1-day-ahead-real-time-pricing` / `DA/RT` — merged, A.1 primary, DA/RT is now
   a cross-referenced child, not a separate live tag.
2. `NEM` — was incorrectly the parent of `net-billing`/`buy-all-sell-all`/
   `community-solar`; corrected to a new peer parent, `DG-compensation-mechanism`,
   with NEM as one of four children.
3. `ELCC` — existed redundantly in both Axis C (generation tech) and Axis K
   (reliability); removed from C entirely, now lives only in K, nested under the
   new `capacity-accreditation` parent.
4. `resource-adequacy` — existed redundantly in both Axis G (cost methodology) and
   Axis K (reliability); removed from G entirely, now lives only in K.
5. `lost-revenues-vs-system-costs` — was awkwardly placed in Axis G; moved to Axis
   N, where it belongs with `BCA-vs-rate-impact-question`, a conceptually
   equivalent distinction.
6. `agrivoltaics` — was a flat peer of `solar`/`wind`/`gas`/etc.; corrected to a
   child of `solar` specifically (a siting configuration, not a separate
   generation technology).
7. `DLC` — existed redundantly as both a program-mechanism concept (old Group 2)
   and a platform tag (old Group 6); removed from the platform axis entirely, now
   lives only as a program mechanism, cross-referenced from the platform-level
   `smart-thermostat` tag.
8. `V2G` — was a flat peer of `HEMS`/`BEMS`; corrected to a child of `EV-charging`.
9. Data centers (old Group 7) — was a free-standing group of three flat tags that
   were all actually children of Axis A's own `A.7`; folded in entirely, group
   retired.
10. `FERC-2222` — existed in Axis E with no connection to the general `FERC-order`
    concept in Axis L; added an explicit parent-child cross-reference between them.
11. `DEA` / `EDA` — two similar-looking acronyms for genuinely different things
    (distributional equity vs. economic development); renamed to
    `DEA-distributional-equity` / `EDA-economic-development` to disambiguate.
12. `CPCN-justification`/`repower`/`ceiling-price` — were flat peers of general
    regulatory-framework tags (VCEA/RPS/FERC-order); moved to Axis G as children of
    `CPCN-justification`, since they're BCA-application-context concepts, not
    general regulatory frameworks.

## Not yet implemented

None of the above has been applied yet to the 100 rows in `Master_Citations.xlsx` —
this remains the proposal/plan. The detailed NSPM chapter-by-chapter sourcing notes
from v1 (which chapter/appendix each tag came from, direct quotes, page-level
detail) are preserved unchanged in `Citation_Taxonomy_Proposal_v1_flat.md` and were
not duplicated here to keep this document focused on structure; refer to v1 for
provenance detail on any individual tag.
