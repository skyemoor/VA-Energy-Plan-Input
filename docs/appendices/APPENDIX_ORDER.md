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

## Proposed sequence — methods, scenarios, topics, reference

| | appendix | source | state |
|---|---|---|---|
| **A** | Resource adequacy and capacity planning | `Appendix_Resource_Adequacy_Methodology.md` + `Reserves_Approach.md` + `Common_Reference.md` 2–3 | **merge needed** |
| **B** | Demand basis | `Demand_Basis_and_RPS_Compliance_Working_Notes.md` | promote |
| **C** | Cost assumptions and levelisation | `Appendix_Cost_Assumptions.md` | ready |
| **D** | Tiered social cost | `Appendix_D_Tiered_Social_Cost.md` | ready |
| **E** | Scenario 1 and 1B | `Appendix_N_Scenario_1B.md` | pending Scenario 1 |
| **F** | Scenario 2 | `Appendix_Scenario2_Methodology.md` | method current, **figures superseded** |
| **G** | Scenario 3 and DER owner economics | `Appendix_DER_Owner_Economics.md` + the DER policy material | **assembly needed** |
| **H** | Gas capacity method | `Appendix_Q_Gas_Capacity_Method.md` | ready |
| **I** | Agrivoltaics | `Appendix_Agrivoltaics.md` | ready |
| **J** | Data-centre demand flexibility | `Appendix_DataCenter_DemandFlexibility_A7.md` | ready |
| **K** | Efficiency stock turnover | `Appendix_Efficiency_Stock_Turnover_Model.md` | ready |
| **L** | Intermediate-year demand shape | `Appendix_O_Intermediate_Year_Demand_Shape.md` | ready |
| **M** | Reference literature | `Appendix_M_Reference_Literature.md` | ready |
| **N** | Solve procedure and requirements | `Appendix_P_Solve_Procedure.md` | ready |
| **O** | Known limitations | `Appendix_Known_Limitations.md` | **stub, 967 chars** |

**The order follows the reader**, not the order things were written: how adequacy and cost are
measured, then what each scenario does, then the topics that need their own treatment, then
reference material someone consults rather than reads.

---

## What renumbering costs

**Q becomes H and P becomes N**, and every cross-reference to them breaks — build-log entries,
code comments, the citation register's Key Finding Relevance column, and the whitepaper outline.

**Worth doing once, now.** The alternative is more citations accumulating against letters that will
move anyway, and a scheme where Q sits after P for no reason other than the order it was written.

**Filenames stay descriptive** rather than becoming `Appendix_H.md` — a letter in a filename is a
second place for the scheme to drift out of sync with itself, which is how this arose. The letter
lives in the compiled document and in this table.

---

## Before any of it

● **A needs merging.** Three sources describe accreditation and reserve margin, and the most
  complete one predates the capacity-planning/resource-adequacy distinction the project now draws.
● **G needs assembling.** The DER policy material — aggregator market access, distribution upgrades,
  DER caps, Direct Transfer Trip, near-term recommendations — sits in `Virginia_Energy_Plan_Input`
  outside the repository, and is the largest unversioned piece of the project.
● **F's figures are superseded** and the appendix says so at the top.
● **O is a stub** and should draw from the limitations already stated in P.2, Appendix Q section 5,
  and `Common_Reference.md`.
