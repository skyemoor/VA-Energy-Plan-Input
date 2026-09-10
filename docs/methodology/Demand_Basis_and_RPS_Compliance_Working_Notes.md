# Demand Basis and RPS Compliance Base — Working Notes

*Drafted 2026-09-10. Intended to become a standalone appendix. Retained as working notes so the
findings are captured while still being revised. Everything below was verified directly against
primary sources this session; where a claim is inferred rather than verified, it says so.*

---

## 1. Summary of findings

Four distinct issues surfaced while tracing the demand basis. Two are settled, one is a
correction to existing documentation, one is an open modeling decision.

| # | Finding | Status |
|---|---|---|
| 1 | The hourly file is **load** (losses included); Appendix 2B tables are **sales** (losses excluded). No gross-up needed if the hourly file is used directly. | Settled |
| 2 | The annual totals in `demand_shape_interpolation.py` are from **Appendix 2B-1 (Total DOM LSE, VA+NC)**, not 2B-2 (Virginia-only) as the module's own comment states. | Correction needed |
| 3 | The LP's RPS constraint is a **generation-share ratio**, structurally different from the statutory **REC obligation against a defined sales base**. | Open decision |
| 4 | § 56-585.5(A) excludes existing in-Commonwealth nuclear and certified ACEB load from the compliance base. Neither is reflected. | Open decision |

---

## 2. The two demand bases are different quantities

This was the source of the confusion, and the resolution is that the model needs **both**.

**Dispatch / adequacy basis** — what must be physically served. Full hourly load including
T&D losses and station service, regardless of who procures the clean energy. Reliability does
not depend on REC accounting: if a data center is connected, the grid serves it.

**Compliance basis** — what counts toward the RPS percentage. Per § 56-585.5(A), retail sales
in the Commonwealth, less in-Commonwealth nuclear operating by July 1 2020, less certified
accelerated clean energy buyer (ACEB) load, less § H legacy competitive-service customers.

These are not competing candidates for one number. They serve different constraints and the
compliance basis is materially smaller.

---

## 3. Finding 1 — losses are already in the hourly file

Verified 2030 figures:

| Source | 2030 GWh | Basis |
|---|---:|---|
| `DOMLSEHourlyLoadProjections2024through2048.csv` | 121,115 | Load (losses included) |
| 2025 IRP Update, Appendix 2B-1 | 110,864 | Sales (losses excluded) |
| Ratio | **1.0925** | ≈9.25% losses + station service |

Both figures are VA+NC combined, so the 9.25% gap is **not** a scope difference — it is losses.
The IRP itself distinguishes the two, noting values "at the utility generator and adjusted for
line losses" (Figures 2.1.11/2.1.12).

**Consequence:** using the hourly file directly for dispatch is correct and needs no gross-up.
Scaling that hourly shape to a *sales*-basis annual total would strip the losses back out and
understate generation need by ~9%.

---

## 4. Finding 2 — the annual totals are Total DOM LSE, not Virginia-only

`demand_shape_interpolation.py` documents a correction claiming its values were moved from
Appendix 2B-1 to 2B-2, "verified directly against the raw filing text" with "an independent
row-sum cross-check against 2B-1's own real total column."

Read directly from the filing, Appendix 2B-1 (Total DOM LSE Sales), 2030 row:

```
2030   28,681   65,542   4,101   10,857   235   1,449   110,864
```

The module's entry is `2030: (65542, 110864)` — commercial and total. That is 2B-1 exactly.
The cross-check described could not have distinguished the two tables because it compared
2B-1 against itself.

**Scope reconciliation.** The 2B appendix region in the extracted filing text contains four
data blocks for five headers; one table did not survive extraction. Identifying them by
magnitude:

| Block | 2030 value | Identification |
|---|---:|---|
| 1 | 110,864 GWh | Total DOM LSE sales (2B-1) |
| 2 | 3,870 GWh | North Carolina sales (2B-3) |
| 3 | 2,942,122 | Total DOM LSE customer count (2B-4) |
| 4 | 2,808,041 | Virginia customer count (2B-5) |

Customer counts confirm the reading: NC = 2,942,122 − 2,808,041 = **134,081 customers, 4.6%
of total**, against NC sales of 3,870 ÷ 110,864 = **3.5% of sales**. Consistent with a
residential-heavy NC territory carrying no data-center load.

**Therefore Virginia-only 2030 sales ≈ 110,864 − 3,870 = 106,994 GWh**, and the 2B-2 table
itself was not captured in the extraction. This should be confirmed against the original PDF
before being relied on.

**Consequence:** demand is currently ~3.5% above true Virginia-only. Note this runs *opposite*
to the losses issue, so the two partially offset.

---

## 5. Finding 3 — the RPS constraint uses a different formulation than the statute

`lp_model.build_problem()` constructs:

```
gascum[T-1] ≤ k × clean_generation,   k = gas_allowed_frac / (1 − gas_allowed_frac)
clean_sum_const = nuclear + exist_solar + CVOW_MW·wind_cf   (+ solar as decision variables)
```

This enforces `gas ≤ frac × (gas + clean)` — gas as a share of **total generation**. No
denominator is derived from retail sales.

The statute instead sets the RPS requirement as "a percentage of the total electric energy sold
in the previous calendar year" (§ 56-585.5(C)(1)(a)), satisfied by **procuring and retiring
RECs** — which may originate anywhere in the PJM region, with at least 75% from Virginia-located
resources beginning in the 2027 compliance year (§ C.3).

Worked comparison at 2045 (100% requirement):

- **Model**: `frac = 0` → `k = 0` → gas ≤ 0. Nuclear counts on the clean side. New clean build
  must cover roughly **121,000 GWh**.
- **Statute**: nuclear is excluded from the base entirely, so the obligation covers roughly
  **75,000 GWh**.

Same headline percentage, materially different requirement. **At 2045 the model is the stricter
of the two** — it requires new clean generation to cover load that existing nuclear already
serves.

For intermediate years the sign can invert: nuclear on the clean side *loosens* the ratio, while
the statutory exclusion *tightens* the base. Which effect dominates is year-dependent and has
not been worked through.

**Assessment:** this is a modeling-convention divergence, not a coding error. The generation-share
formulation is internally consistent and is arguably the right frame for a *physical*
decarbonization question. It is not what § 56-585.5 requires, and the deliverables describe the
scenarios as modeling statutory compliance.

---

## 6. Finding 4 — statutory exclusions from the compliance base

§ 56-585.5(A) defines "total electric energy" as sales to retail customers in the Commonwealth
service territory, **excluding**:

**(a) In-Commonwealth nuclear** operating by July 1, 2020 — Surry and North Anna qualify.
Roughly 3,691 MW producing on the order of 32,000 GWh/year, against ~107,000 GWh of Virginia
sales: approximately a **30% reduction in the compliance denominator**. Magnitude is
approximate and should be computed from actual generation rather than nameplate.

**(b) Certified accelerated clean energy buyers.** Commercial/industrial customers with
**aggregate load over 25 MW** in the prior calendar year who enter subsection G arrangements
and are certified by the Commission. § G is explicit: "the calculation of the utility's RPS
Program requirements shall not include the electric load covered by customers certified as
accelerated clean energy buyers," and contracted nameplate "shall be offset from the utility's
procurement requirements pursuant to subsection D."

Three properties matter for modeling:

1. **Opt-in, not automatic.** Exceeding 25 MW is insufficient; the customer must contract and
   be certified. This is a behavioral variable, not a fixed deduction.
2. **Aggregation crosses sites and affiliates** ("aggregate load," § 56-585.5(A)) — multiple
   campuses under common control combine toward the threshold.
3. **Expanded July 1, 2026** to permit contracting for zero-carbon (not only solar/wind)
   resources in PJM placed in service after January 1, 2015, including nuclear uprates and
   agreements preventing announced retirements.

**(c) § H legacy competitive-service customers** — Phase II customers with >100 MW peak demand
in 2019 who elected competitive service before April 1, 2019.

ACEB participation is properly a **scenario variable** and is plausibly the single largest lever
on the compliance question. Directly relevant to Scenario 5.

---

## 7. Related statutory features not currently modeled

**$45/MWh deficiency payment ceiling** (§ 56-585.5(D)(5)). A utility unable to meet the
obligation — *or facing REC costs above $45/MWh* — pays $45 per MWh of shortfall, escalating
1%/year after 2021. Higher rates apply to specific carve-outs: $75/MWh for shortfalls in
sub-1 MW Virginia solar/wind/anaerobic digestion, $100/MWh for geothermal.

This is an economic ceiling on compliance cost already in law. Against a modeled 2045 SLCOE
of roughly $129/MWh, a rational utility would pay the deficiency rather than build. **The
statute effectively prices the answer to "how close can we come."** This deserves its own
treatment in the deliverables.

**Distributed carve-out** (§ C.2): 4.5% of RPS requirements for compliance years 2026–2030 and
5% for 2031–2045 must come from solar, wind, or anaerobic digestion resources **≤1 MW located
in Virginia**, with ≥25% low-income qualifying projects, remainder on or adjacent to public
elementary or secondary schools. Maximum 3,000 kW at any single or contiguous location.

**Geothermal carve-out** (§ C.1.b): 0.5% (2027), 0.75% (2028), 1% (2029 onward) of RECs used
for compliance.

**Previously developed project sites** (§ 56-585.5(A) definition) explicitly include "(ii) as a
parking lot; (iii) as the site of a parking lot canopy or structure." At least 1,000 MW of the
16,100 MW must be sited on such land — statutory support for the Scenario 3 canopy approach.

---

## 8. Open items

**Decision taken 2026-09-10:** item 2 below is RESOLVED — the dual-basis approach is adopted and
implemented in `lp_package/rps_compliance.py` with 21 baseline-locked tests
(`tests/test_rps_compliance.py`). The physical LP is unchanged; the statutory basis is a
post-processing layer. Reporting entry point is `compare_bases()`, which returns both figures and
their gap. Remaining items below are unchanged.

First illustrative output (2045, provisional inputs):

| | TWh |
|---|---:|
| Statutory RPS obligation | 148.0 |
| Physical clean requirement | 205.9 |
| **Gap** | **57.9** |
| Statutory as share of physical | 71.9% |
| Deficiency ceiling | $57.14/MWh |

With heavy ACEB participation (40 TWh self-procured) the statutory obligation falls to 108.0 TWh —
52.5% of the physical requirement. ACEB participation is the largest single lever.

1. **Confirm Virginia-only totals** against the original IRP PDF; the 2B-2 table was lost in
   text extraction and 106,994 GWh (2030) is currently derived by subtraction.
2. **Decide the RPS formulation.** Recommendation: implement the statutory basis *alongside*
   the current generation-share basis and report both, rather than replacing one with the
   other. The gap between "physical 100% clean" and "statutory RPS compliance" is itself a
   substantive finding.
3. **Compute actual nuclear generation** (not nameplate) for the exclusion.
4. **Add ACEB participation as a scenario variable**, with the § D procurement offset.
5. **Add the deficiency-payment ceiling** as a cost cap.
6. **Resolve the leap-year discrepancy.** `demand_shape_interpolation.py` as available shows no
   trim; `BASE_SHAPE_YEAR = 2024` has 8,784 hours (verified). Internal Debugging Log #24 states
   the fix was applied at source and propagates to Scenarios 1 and 2. Either the available copy
   predates the fix or the trim lives elsewhere. A silent 24-hour misalignment against
   8,760-hour weather arrays would corrupt every subsequent hour.
7. **Decide dispatch scope** (VA-only vs VA+NC). VCEA governs Virginia generation; Dominion
   dispatches one system. Recommendation: VA-only for consistency with the compliance basis,
   stated explicitly.

---

## 9. Effect on existing results

Every scenario result currently in the repository rests on the generation-share formulation and
the Total DOM LSE annual totals. The 2045 figures produced in the 2026-09-09/10 sessions
additionally used the **raw hourly file directly** (121,115 GWh for 2030; 205,902 GWh for 2045),
which is Total DOM LSE **load** — a third basis, distinct from both of the above.

None of these are wrong on their own terms, but they are not the same quantity, and the
deliverables do not currently distinguish them. All affected figures should carry
`provisional` status in the provenance register pending a decision on item 2 above.

---

## 10. Statutory Floor (S2) capacity standard — resolved 2026-09-10

Investigating whether Scenario 2 lacked a reserve margin found something different: it uses a
*different* standard, not no standard. Appendix C.2 sizes its gas to the worst single hourly gap
while **crediting storage at zero**. Scenarios 1 and 3 apply a 17.7% margin with storage credited
at its power rating. The two are conservative in opposite directions and are not comparable.

Gas capacity required under each, all four checkpoints
(`scripts/compare_scenario2_capacity_standards.py`):

| Year | Peak demand MW | Appendix C.2 rule | Reserve-margin standard | Difference | Storage credited |
|---|---:|---:|---:|---:|---:|
| 2030 | 19,511 | 15,604 | 12,058 | −3,547 | 7,000 |
| 2035 | 23,325 | 19,098 | 10,227 | −8,871 | 13,000 |
| 2040 | 27,782 | 23,556 | 10,473 | −13,083 | 18,000 |
| 2045 | 28,466 | 22,446 | **4,485** | **−17,962** | 23,000 |

**The reserve-margin standard requires less gas at every checkpoint, and the gap widens as the
statutory storage build grows** — from 3.5 GW in 2030 to 18.0 GW in 2045. By 2045, crediting
23,000 MW of storage at nameplate leaves the Statutory Floor needing only 4,485 MW of gas for
capacity purposes, against 22,446 MW under the zero-credit rule.

**This does not mean 4,485 MW is the right answer.** The entire 18 GW difference is the storage
accreditation assumption, and this project's own evidence argues that assumption is optimistic:

- The eight-year continuous dispatch test found reserve margin was **never violated** on a
  nameplate-credited basis while 6.44 million MWh went unserved, because storage sat empty 85% of
  hours (see § 9 above and the 2030 charge-starvation finding).
- E3's independent evaluation of PJM's capacity model states that scrambling "risks overstating
  … the ELCC of energy storage resources" because storage "is likely to run out of charge" during
  the multi-day events that method underrepresents (citation C126 region; see
  `registers/Master_Citations_updated.xlsx`).
- PJM's own Independent Market Monitor has separately criticised class-level ELCC accreditation
  as not "unit specific" and not incorporating "hourly supply and demand matching."

**Adopted approach:** report both figures for the Statutory Floor rather than selecting one.
The reserve-margin figure is the *comparable* one and should carry the headline, since Scenarios
1 and 3 use it. The Appendix C.2 figure is retained as a bounding case. The difference between
them is not a modeling nuisance — it is a quantification of how much rests on storage capacity
accreditation, which is unsettled at PJM and material at this scale.

**Consequence for existing figures:** every published Statutory Floor cost rests on the Appendix
C.2 sizing and is therefore not comparable to the Build to Zero figures it has been compared
against. Those cost figures require re-derivation before the comparison is used externally. The
direction of change is now known — less gas capacity under the comparable standard, so lower
capital cost, narrowing rather than widening the gap the Executive Summary currently reports.

**Note on leap years:** building these fiscal years by hour offset failed on 2040 (8,784 hours).
The script selects by calendar date and excludes February 29 explicitly. This is open item 6
below, encountered in practice rather than in theory.

---

## 11. Storage capacity accreditation — the foresight artifact (2026-09-10)

§ 10 left an 18 GW question resting entirely on how storage is credited at the peak hour. The
approach adopted was Appendix A.13's own-data method: rank hours by net demand, take the top ten,
measure what storage could actually have delivered. **Applying it surfaced a methodological
problem serious enough to change the recommendation.**

### The result depends almost entirely on which dispatch is measured

Same 2045 fleet, same weather, same peak-hour definition:

| Basis | Na-ion capacity credit |
|---|---:|
| LP dispatch (perfect foresight) | **100.0%** |
| Heuristic dispatch (no foresight) | **31.8%** |

The LP series across checkpoints also moves the wrong way:

| Year | Storage penetration | LP-derived credit |
|---|---:|---:|
| 2030 | 27% | 40.3% |
| 2035 | 60% | 60.0% |
| 2040 | 127% | 70.0% |
| 2045 | 228% | 100.0% |

Capacity credit should **fall** as penetration rises — PJM's own fixed-tilt solar rating fell from
33% to 7–8% for precisely that reason. A rising series is the signature of an artifact, not a
finding.

### Cause

Perfect foresight. The LP knows exactly which hours are the peak net-demand hours and
pre-positions storage to be full for them. Measuring "availability at the peak hours" against a
dispatch optimized *knowing which hours those are* measures the optimizer's foresight, not the
fleet's capability — and the larger the fleet, the more completely it can be pre-positioned,
which is why credit rises with penetration rather than falling.

**This means own-data accreditation computed from LP dispatch is the LEAST conservative option
available, not the most.** That is the opposite of the reason it was selected. Appendix A.13's
cross-validation rule (take the lower of own-data and published) is what prevents the 100% figure
from being adopted; without that rule the method would have produced a materially wrong answer
that looked rigorous.

### Adopted approach

Accreditation must be computed from a **no-foresight dispatch** — this project's eight-year
heuristic simulation (`scripts/sim_2045_8yr.py`) or an equivalent rolling-horizon dispatch. An
LP-derived figure may be reported only as an optimistic bound, and only with this artifact
stated.

The 31.8% figure is adopted for 2045. It sits below PJM's published 50% for four-hour storage, so
the cross-validation rule takes it, and it is consistent with the mechanism the eight-year test
independently established: storage empty 85% of hours, 6.44 million MWh unserved while reserve
margin was never violated on a nameplate-credited basis.

### Effect on the § 10 range

At 2045 with 23,000 MW of storage:

| Credit basis | Accredited MW | Statutory Floor gas requirement |
|---|---:|---:|
| Nameplate (100%) | 23,000 | 4,485 MW |
| **No-foresight own-data (31.8%)** | **7,314** | **~20,200 MW** |
| Zero credit (Appendix C.2) | 0 | 22,446 MW |

The conservative end of the range is now derived rather than assumed, and sits close to — but
below — the zero-credit bound.

### Open

Credits for 2030, 2035 and 2040 still require no-foresight dispatch runs for their own fleets;
only 2045 has one. The LP-derived figures in the table above must **not** be used for those years.

---

## 12. Checkpoint dispatch files are not a consistent set (2026-09-10)

Attempting to compute accreditation for 2030, 2035 and 2040 from the stored checkpoint dispatch
CSVs found that **the four files are not from one consistent solve vintage.** Three independent
indications:

**Stale demand basis.** The 2030 file shows 144.1 TWh annual and a 19,038 MW peak. Internal
Debugging Log #24 identified exactly this vintage as 1.30x too high against the current sourced
figure of 110,864 GWh.

**Wrong growth shape, not just wrong level.** The files run 144.1 -> 167.4 -> 171.9 -> 176.7 TWh
(+23% over fifteen years). The current Appendix 2B-1 series runs 110,864 -> 186,462 GWh (+68%).
This matches #24's finding that the discrepancy decayed toward 2040 and flipped sign by 2045.

**Different schema at 2045.** Seventeen columns rather than nineteen — net storage columns instead
of separate charge and discharge — indicating a different code vintage.

Two further incoherences: long-duration storage is non-monotonic across checkpoints
(0 -> 116,127 -> 0 -> 6,352,286 MWh), which the project's own monotonic-build convention should
prevent; and curtailment runs 2,955 -> 2,658,772 -> 13,044,965 -> **0** MWh, with the zero
appearing in a file named `TRUE_FINAL_ZeroCurt` alongside 109,560 MW of solar, suggesting
curtailment was suppressed rather than solved.

### Consequence for accreditation

The 2030, 2035 and 2040 credits computed from these files are **discarded, not merely uncertain.**
They returned 0.0%, and the underlying mechanism (storage sitting at exactly its 20% depth-of-
discharge floor at every one of the ten peak hours) is real and consistent with the separately
established charge-starvation finding. But the peak hours themselves were identified from stale
demand, so they are the wrong hours. A separate defect — crediting Na-ion only, omitting the
116,127 MWh of long-duration storage present at 2035 — biases the result further downward.
Correcting the second would not fix the first.

Recorded as `R-ACCREDIT-2030/2035/2040`, status `superseded`, superseded_by "pending re-solve on
corrected demand".

### What stands

**The 2045 figure of 31.8% stands.** It derives from this session's own eight-year heuristic
simulation using corrected demand and a fleet from this session's own solve, not from these files.
Recorded as `R-ACCREDIT-2045`, status `provisional` — provisional because it credits Na-ion only
and rests on a single heuristic dispatch policy, which a more anticipatory policy would improve on.

### Blocked

Accreditation for 2030, 2035 and 2040 is blocked pending a re-solve of those checkpoints on
corrected demand. Until then the whitepaper can report 2045 only, and must state the earlier years
as not yet available rather than substituting the LP-derived figures — which are the foresight
artifact described in § 11.
