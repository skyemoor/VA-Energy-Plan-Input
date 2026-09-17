# Appendix order — proposed

**Status 2026-09-14.** A recommended sequence, not yet applied. Filenames deliberately carry no
letters until this is agreed, because a letter baked into a filename now would be wrong twice.

---

## Why the existing lettering cannot be kept

**Three competing schemes were in play.** A lettered A–P set lived inside
`Reorganized_Appendices_Draft.md`; standalone files existed for D, M, N, O, P; and Q was added
without a place in either.

**The draft also held stale copies.** Its Appendix P carried 14 of the solve procedure's
requirements where the live file has 17 — so a reader could open the composite, find a complete-
looking appendix, and miss three requirements added since.

**And the letters collided.** `Appendix_DataCenter_DemandFlexibility_A7` used a letter the scheme
assigned to resource adequacy.

Both draft files were removed on 2026-09-14 after their five draft-only appendices were extracted.

---

## Appendices are for the end reader; working documents are for us

**This is the division that governs everything below.** They are different kinds of document, not
two versions of one, and material moves in one direction only.

| | audience | holds | changes |
|---|---|---|---|
| **Appendices** | VDOE, legislators, stakeholders, other modelers | the settled account of a subject | when a subject is finalised |
| **Working documents** | this collaboration | findings in progress, what moved and why | continuously |
| **`Common_Reference.md`** | this collaboration | cross-scenario decisions, conventions, measured facts | continuously |

**Material MIGRATES from working documents to appendices when a subject is finalised.** It is
rewritten for a reader who was not present for the reasoning, not copied.

**Which means an appendix whose figures are superseded is not "out of sync with" its working
document** — it is simply awaiting migration. `Appendix_Scenario2_Methodology.md` predates the
bounded gas fleet and says so; it will be rewritten from
`docs/scenarios/Scenario2_Working_Document.md` once Scenario 2 is settled, which is close.

**And `Appendix_Resource_Adequacy_Methodology.md` does NOT need merging with
`Common_Reference.md` sections 2–3**, which an earlier version of this file proposed. That was a
category error. Common Reference holds the working position — what the metrics are, what is
deliberately not claimed, what the forced-outage draw loop would cost. The appendix is the
reader-facing account, and it needs rewriting to match current practice rather than absorbing the
working material.

---

## Proposed sequence — methods, scenarios, topics, reference

| | appendix | source | state |
|---|---|---|---|
| **A** | Resource adequacy and capacity planning | `Appendix_Resource_Adequacy_Methodology.md` + `Reserves_Approach.md` + `Common_Reference.md` 2–3 | **rewrite on migration** |
| **B** | Demand basis | `Demand_Basis_and_RPS_Compliance_Working_Notes.md` | promote |
| **C** | Cost assumptions and levelisation | `Appendix_Cost_Assumptions.md` | ready |
| **D** | Tiered social cost | `Appendix_D_Tiered_Social_Cost.md` | ready |
| **E** | Scenario 1 and 1B | `Appendix_N_Scenario_1B.md` | pending Scenario 1 |
| **F** | Scenario 2 | `Appendix_Scenario2_Methodology.md` | method current, **figures await migration** |
| **G** | Scenario 3 | working document | pending siting cap |
| **H** | **Distributed energy resources** | `Appendix_DER_Owner_Economics.md` + policy material to be located | **assembly needed** |
| **I** | Gas capacity method | `Appendix_Q_Gas_Capacity_Method.md` | ready |
| **J** | Agrivoltaics | `Appendix_Agrivoltaics.md` | ready |
| **K** | Data-centre demand flexibility | `Appendix_DataCenter_DemandFlexibility_A7.md` | ready |
| **L** | Efficiency stock turnover | `Appendix_Efficiency_Stock_Turnover_Model.md` | ready |
| **M** | Intermediate-year demand shape | `Appendix_O_Intermediate_Year_Demand_Shape.md` | ready |
| **N** | Reference literature | `Appendix_M_Reference_Literature.md` | ready |
| **O** | Solve procedure and requirements | `Appendix_P_Solve_Procedure.md` | ready |
| **P** | Known limitations | `Appendix_Known_Limitations.md` | **stub, 967 chars** |

**The order follows the reader**, not the order things were written: how adequacy and cost are
measured, then what each scenario does, then the topics that need their own treatment, then
reference material someone consults rather than reads.

---

## What renumbering costs

**Q becomes I and P becomes O**, and every cross-reference to them breaks — build-log entries,
code comments, the citation register's Key Finding Relevance column, and the whitepaper outline.

**Worth doing once, now.** The alternative is more citations accumulating against letters that will
move anyway, and a scheme where Q sits after P for no reason other than the order it was written.

**Filenames stay descriptive** rather than becoming `Appendix_H.md` — a letter in a filename is a
second place for the scheme to drift out of sync with itself, which is how this arose. The letter
lives in the compiled document and in this table.

---

## Before any of it

● **A needs rewriting, not merging.** It remains the fullest account of the accreditation and
  reserve-margin method, and predates the capacity-planning versus resource-adequacy distinction.
  It migrates from `Reserves_Approach.md` and `Common_Reference.md` sections 2–3 when that subject
  is finalised.
● **H needs assembling, and is likely two kinds of material.** DER OWNER ECONOMICS is modelling —
  what a rooftop or canopy owner earns, and under what market access. The DER POLICY material is
  recommendation: aggregator participation in the wholesale market, distribution system upgrades
  where DER penetration crosses a threshold, DER caps, Direct Transfer Trip, and near-term actions.
  Those read differently and a VDOE reader would use them differently, so they may warrant
  separating once the full extent of the policy material is known. It sits in
  `Virginia_Energy_Plan_Input` and elsewhere outside the repository, and is the largest unversioned
  piece of the project.
● **Scenario 3 implies distribution upgrade cost that the model does not carry.** If 20% of solar
  sits on rooftops and canopies, feeder upgrades to host it are real capital and are absent from
  Scenario 3's figure. The transmission-deferral benefit is the offset and is equally absent. **Both
  missing, pointing opposite ways** — worth stating rather than quietly netting to zero.
● **F's figures are superseded** and the appendix says so at the top.
● **O is a stub** and should draw from the limitations already stated in P.2, Appendix Q section 5,
  and `Common_Reference.md`.
