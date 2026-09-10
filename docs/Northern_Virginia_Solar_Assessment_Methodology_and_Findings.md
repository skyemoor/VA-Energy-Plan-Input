# Northern Virginia C&I Rooftop, Parking-Lot, and School Solar/Battery Assessment
## Methodology and Findings -- Loudoun, Fairfax, Arlington, and Prince William Counties

This assessment estimates the aggregate rooftop solar, parking-lot canopy solar, and school solar
potential across Loudoun, Fairfax, Arlington, and Prince William Counties -- Northern Virginia's
four most developed jurisdictions -- built from each county's own real business-registration and
GIS building/parcel data wherever available, supplemented by a clearly-labeled density-based
estimate for the one dataset (Prince William's parking lots) that direct GIS extraction could not
yet produce. It supports Scenario 3's urban and suburban solar siting component, which aims to
reduce the need for new high-voltage transmission by generating clean energy closer to where it's
used rather than exclusively at greenfield, utility-scale sites. Across all four counties and all
three asset types combined, this assessment finds an estimated **6.2 to 7.1 GW** of aggregate solar
potential -- a real, data-grounded figure, but one that should be read alongside the caveats below
and each county's own detailed methodology: it combines several genuinely different kinds of
estimate (real measured building/parcel data in most cases, a density-based extrapolation for one
county's parking lots, and full theoretical ceilings for most school figures), and Fairfax's own
figures in particular exclude several incorporated jurisdictions within the county's own geographic
boundary.

---

## Executive Summary

### Northern Virginia grand total

| | MW | MWh/yr |
|---|---:|---:|
| **All four counties, all components** | **6,159.0–7,148.2** | **10,790,592–12,523,613** |

**This grand total sums twelve genuinely different estimates across four counties and should not be
read as one homogeneous figure.** Each county's own methodology differs in real, material ways (most
significantly: Loudoun's C&I estimate scales a flat per-building kW rate by a business-derived
building count, while Fairfax's, Arlington's, and Prince William's own C&I estimates scale a kW/sq
ft density rate by real, measured footprint area; Prince William's parking-lot figure is a
density-based estimate rather than measured GIS data -- see Section 1 and Section 5 for why, and
Section 7 for a full cross-county comparison). Each county's own subsection below should be read in
full before its figures are used in isolation.

### By asset type (all four counties combined)

| Component | MW | MWh/yr |
|---|---:|---:|
| C&I buildings | 2,039.9 | 3,573,878 |
| Parking lots | 3,956.6–4,945.8 | 6,932,082–8,665,102 |
| Schools | 162.50 | 284,633 |

### By county

| County | Component | MW | MWh/yr |
|---|---|---:|---:|
| **Loudoun** | C&I buildings | 1,260.9 | 2,209,060 |
| | Parking lots | 1,551.2–1,939.0 | 2,717,691–3,397,114 |
| | Schools (theoretical potential, all 87) | 34.5 | 60,444 |
| | **Combined** | **2,846.6–3,234.4** | **4,987,195–5,666,618** |
| **Fairfax** | C&I buildings | 132.4 | 231,947 |
| | Parking lots | 377.0–471.3 | 660,517–825,646 |
| | Schools (theoretical potential, all 194) | 71.65 | 125,531 |
| | **Combined** | **581.0–675.3** | **1,017,995–1,183,124** |
| **Arlington** | C&I buildings | 373.8 | 654,886 |
| | Parking lots | 293.7–367.1 | 514,595–643,244 |
| | Schools (all 44 identified education buildings) | 21.3 | 37,250 |
| | **Combined** | **688.8–762.2** | **1,206,731–1,335,380** |
| **Prince William** | C&I buildings | 272.8 | 477,985 |
| | Parking lots (ESTIMATED, not measured -- see Section 5.3) | 1,734.7–2,168.4 | 3,039,279–3,799,098 |
| | Schools (theoretical potential, all 92) | 35.05 | 61,408 |
| | **Combined** | **2,042.6–2,476.3** | **3,578,671–4,338,491** |

**Critical scope caveat -- read before using any Fairfax figure:** Fairfax County's figures cover
*unincorporated Fairfax County only*. They do **not** include the independent cities of
**Alexandria, Fairfax, and Falls Church**, or the incorporated towns of **Clifton, Herndon, and
Vienna** -- all six of which maintain their own separate business-licensing and GIS systems, entirely
outside Fairfax County government's own data. Full detail in Section 3.1. Loudoun and Arlington have
no equivalent embedded-jurisdiction exclusion (detail in Sections 2.1 and 4.1 respectively).

**Critical data caveat -- read before using any Prince William parking-lot figure:** this is a
density-based *estimate*, not measured GIS data. Direct Prince William County GIS extraction has
not yet succeeded (the TYPE_CODE field returns zero results despite repeated attempts). The figure
above extrapolates from Loudoun's own real, measured per-capita parking density, per direct user
decision -- full reasoning and an explicit sensitivity check against a Fairfax-anchored alternative
are in Section 5.3. Should be replaced with real data at the first opportunity.

**Schools figures are not all the same kind of estimate.** Loudoun's, Fairfax's, and Prince
William's own school figures are each a full *theoretical potential* across every school in the
division, regardless of actual or planned deployment -- not real, current, or committed solar.
Arlington's school figure is real footprint of identifiable education-related buildings, but
includes one private school and one non-school facility not filtered out. None of the four
counties' school figures reflect verified, real-world deployed capacity -- see each county's own
schools subsection for what real deployment data does exist and its limitations.

---

## 1. Shared Methodology (Applies to All Four Counties)

### 1.1 Two genuinely different C&I sizing approaches, and why both are correct for their own inputs

Loudoun's own C&I rooftop estimate and Fairfax's/Arlington's own C&I rooftop estimates are built on
the same shared base class (`BaseRooftopSolarEstimator` in `rooftop_solar_estimation_base.py`),
following the same pattern used elsewhere in this project: a base class defines shared logic and
calls an abstract hook; each scenario class implements only the hook. The shared logic -- mean-based
and median-based MW+MWh totals via a common `compute_totals()` method -- is identical across all
four counties. The hook differs by what a per-unit rate gets multiplied by:

- **Loudoun's own hook** scales a **flat per-building kW figure** by a **building count**, because
  Loudoun's source data (business-license registration records) has no roof-area field at all --
  only a street address per business, requiring address-based deduplication down to a building
  count first (Section 2, full detail).
- **Fairfax's, Arlington's, and Prince William's own hook** scales a **kW/sq ft density rate** by a
  **known total footprint area**, because each county's source data is a direct building-footprint
  GIS inventory that already gives real, measured roof area per building -- no
  deduplication-to-a-count step is needed, but a density rate is, since raw footprint sq ft isn't
  itself a kW figure.

Neither approach is more "correct" in the abstract -- each is the right fit for what its own source
data actually provides. This is a genuine, load-bearing methodological difference between Loudoun's
figures and the other three counties' own, not an inconsistency, and readers comparing counties
directly should keep it in mind (Section 7 has a fuller comparison).

### 1.2 The real NVRC density sample

All four counties' kW conversions -- Loudoun's flat per-building figure and Fairfax's/Arlington's/
Prince William's own per-sq-ft density rate -- are ultimately built from the same real, 8-point NVRC
Solar Map sample, gathered directly from real, field-tested Loudoun buildings (roof area, usable
roof %, and kW
capacity for each):

| Address | Roof sqft | Usable % | kW |
|---|---:|---:|---:|
| 21335 Signal Hill Plz, Sterling | 20,922 | 42.6% | 132.4 |
| 19 E Market St, Leesburg | 2,462 | 26.6% | 9.7 |
| 21631 Ridgetop Cir, Sterling | 29,788 | 44.2% | 195.6 |
| 21370 Potomac View Rd, Sterling | 5,604 | 53.2% | 44.3 |
| 20365 Exchange St, Ashburn | 20,576 | 56.2% | 171.6 |
| 20405 Exchange St, Ashburn | 19,812 | 45.5% | 133.9 |
| 22405 Enterprise St, Sterling | 22,930 | 66.4% | 226.1 |
| 44375 Apache Cir, Ashburn | 2,225 | 31.2% | 10.3 |

Mean kW/building: 115.5; median: 133.1 (used directly for Loudoun's own flat-rate scaling). Derived
mean density: 0.006792 kW/sq ft; median density: 0.006661 kW/sq ft (used for Fairfax's and
Arlington's own footprint-based scaling).

**This sample's limitations apply to every county's figures in this document, not just Loudoun's:**
n=8, geographically narrow (Sterling/Leesburg/Ashburn only -- none of the 8 points are themselves
Fairfax or Arlington buildings, a real, additional extrapolation for those two counties beyond what
Loudoun's own figures already carry), and a data vintage understood to be approximately 2016.
Loudoun's own newer construction, and Fairfax's/Arlington's/Prince William's construction generally
(none of the 8 sample points are from any of those three counties at all), is likely undercounted
or missing a proportional share of representation as a result.

### 1.3 Capacity factor and annual energy conversion

All annual MWh/yr figures in this document, for all four counties and all three components (C&I,
parking, schools), use the same 20% NEM distributed solar capacity factor (`VA_SLCOE_Model.xlsx`,
"Assumptions & Sources" tab, row 13) and 8,760 hours/year -- reused directly throughout, never
re-derived per county.

### 1.4 Mean-based is the primary figure everywhere, not a mean+median "combined" blend

**A real statistical correction made mid-project, applied retroactively to Loudoun's own
already-delivered figures:** earlier versions of this project's rooftop-solar modules (Loudoun's
first, then briefly Fairfax's own before the fix propagated) exposed a `total_mw_combined` property,
computed by simple-averaging the mean-based and median-based totals. Direct challenge established
this has no sound statistical justification: when scaling a per-unit rate across a known, fixed
population (a building count or a footprint area) to estimate a sum, the sample **mean** is the
correct, unbiased estimator of that sum. The sample **median** is a *biased* estimator of the same
sum whenever the underlying sample is skewed -- true of this project's own NVRC sample, in both its
forms (raw kW values span ~23x min-to-max; derived kW/sq ft ratios span ~2.5x) -- because
median-based scaling implicitly assumes a symmetry the data doesn't have. Averaging a correct
estimator with a biased one produces an undefined third number, not a more conservative one.

**Consequence, applied uniformly across all four counties in this document:** the mean-based total
is the primary, recommended figure throughout. The median-based total is retained everywhere as an
explicit, separately-labeled sensitivity check, never blended into a headline number.
`total_mw_combined` / `total_mwh_per_year_combined` no longer exist anywhere in this project's
codebase. Loudoun's own previously-reported "combined" headline (1,357.2 MW / 2,377,808 MWh/yr) is
corrected to its mean-based figure (1,260.9 MW / 2,209,060 MWh/yr) throughout this document.

### 1.5 Parking-lot canopy engineering: one shared, unchanged module across all four counties

Loudoun's, Fairfax's, and Arlington's own real parking-lot MW/MWh figures (Prince William's own
figure is a density-based estimate, Section 5.3, not built from this same real-data pipeline) are
computed by the same, unchanged engineering
classes (`SolarCanopyDesign`, `BatteryStorageDesign`, `ParkingCanopyAssessment` in
`loudoun_parking_canopy_and_storage.py`), originally built for Loudoun and extended to Fairfax and
then Arlington via new, county-specific `CountyParkingData` classmethods only -- confirming that
module's own originally-stated design goal ("a second county needs only its own classmethod, not
changes to the engineering classes themselves") held for a second *and* third county. Prince
William's own estimate (Section 5.3) reuses these same, still-unchanged engineering classes too --
via a directly-constructed `CountyParkingData` object rather than a new classmethod, since there is
no real file to load from. Canopy density
range: 2.0 (low) to 2.5 (high) kW per parking space, ~300 sq ft/space including a pro-rated
drive-aisle share; paired battery storage at a 1:1 MW ratio, 4-hour duration.

---

## 2. Loudoun County

### 2.1 Jurisdictional scope

Loudoun County has no equivalent of Fairfax's embedded-independent-city exclusion (Section 3.1).
Loudoun's incorporated towns (Leesburg, Purcellville, Hamilton, etc.) are understood to fall under
the county's own Commissioner of the Revenue business-licensing system, unlike Fairfax's cities and
towns, which run entirely separate systems. This has not been independently re-verified as part of
this document's own preparation, consistent with how it was originally treated when Loudoun's
figures were first established.

### 2.2 C&I rooftop buildings

**Source:** Loudoun County's own Active Business Accounts list (Office of the Commissioner of the
Revenue), 23,373 real business registration records.

**Data acquisition:** the source list was provided in two successive file formats, and both turned
out to be different from what their file extensions implied -- a `.pdf`-named file that was actually
plain ASCII text, and a `.docx`-named file that was also plain text, formatted as an inconsistent mix
of Markdown pipe-tables and leftover tab-delimited rows. A two-branch parser handled both row
formats, with three distinct data-corruption patterns (address/city field merges, fully-merged
adjacent records, and lost delimiters) each handled explicitly rather than guessed at. A genuine
parser bug -- a Markdown table separator row being silently counted as a fake business record -- was
caught by comparing the parsed total against an independent line-count baseline, and fixed with a
permanent regression test.

**Classification:** each record was checked for out-of-state addresses, PO Boxes, and non-Loudoun
cities. The initial "known Loudoun communities" reference list was found to be incomplete -- the
historic village of Bluemont was missing entirely, wrongly excluding 70 real records, the single
largest correctable gap found in this entire project. ZIP codes were used as a second, independent
cross-check (not a replacement for city-name matching), which caught a separate real error: an
initial ZIP-code reference list included Herndon and Centreville ZIP codes, both genuinely in
Fairfax County, not Loudoun.

**Deduplication:** a two-pass approach (exact address match including suite, then suite-stripped
address match) reduced the population from 14,303 valid business records to 12,758 unique exact
addresses to 10,918 unique buildings. One suite address alone was shared by 35 separate business
registrations.

**Result:** 10,918 unique C&I buildings.

| | MW | MWh/yr |
|---|---:|---:|
| Mean-based (primary) | 1,260.9 | 2,209,060 |
| Median-based (sensitivity check) | 1,453.5 | 2,546,555 |

### 2.3 Parking lots

**Source:** Loudoun's own Road Casings GIS extract (`Loudoun_Road_Casing_type_2.xlsx`), filtered to
`RD_TYPE=2` (parking lots specifically, out of a broader layer also covering roads, driveways, and
runways) and paved surfaces only.

**Size threshold:** ≥6,000 sq ft -- the threshold this project's later Fairfax and Arlington work
both explicitly adopted from Loudoun's own precedent here.

**Result:** 5,341.6 acres (232,679,056 sq ft) of qualifying parking-lot area.

| | Low (2.0 kW/space) | High (2.5 kW/space) |
|---|---:|---:|
| MW | 1,551.2 | 1,939.0 |
| Battery storage capacity (MWh, 4-hr) | 6,204.8 | 7,756.0 |
| Annual energy (MWh/yr, at 20% capacity factor) | 2,717,691 | 3,397,114 |

### 2.4 Schools

**Real Loudoun school counts:** 57 elementary, 15 middle, 15 high (87 total).

**Full theoretical potential** (flat per-type kW assumptions -- Elementary 250 kW, Middle 500 kW,
High 850 kW -- applied uniformly to every school regardless of actual deployment, the same
methodology used for Fairfax's own school figure): 34.5 MW / 138,000 kWh paired battery *storage
capacity*. Derived annual energy at the established 20% capacity factor: 60,444 MWh/yr.

No real-deployed-solar research specific to Loudoun schools has been conducted as part of this
project to date -- unlike Fairfax and Arlington (Sections 3.4 and 4.3), where real deployment data
was separately researched and found to diverge substantially from the theoretical-potential figure.
This is a genuine, open gap for Loudoun specifically, not yet addressed.

### 2.5 Combined total

| Component | MW | MWh/yr |
|---|---:|---:|
| C&I buildings | 1,260.9 | 2,209,060 |
| Parking lots | 1,551.2–1,939.0 | 2,717,691–3,397,114 |
| Schools (theoretical potential, all 87) | 34.5 | 60,444 |
| **Combined** | **2,846.6–3,234.4** | **4,987,195–5,666,618** |

---

## 3. Fairfax County

### 3.1 Jurisdictional scope -- what is and is not included

Fairfax County's own business-licensing framework explicitly excludes six embedded/adjacent
jurisdictions: *"Businesses located in the cities of Alexandria, Fairfax, and Falls Church, and the
towns of Clifton, Herndon, and Vienna (except contractors) are not subject to Fairfax County
Business, Professional and Occupational License (BPOL) tax."* Fairfax County's own GIS
boundary-layer documentation independently corroborates this at the mapping level: the county's own
boundary is described as bordered in part by "the cities of Alexandria and Falls Church" as
external, surrounding jurisdictions -- and Fairfax County's GIS division homepage lists "City of
Alexandria GIS," "City of Fairfax GIS," and "City of Falls Church GIS" as separate systems entirely
distinct from the county's own.

**This is a well-supported inference, not a directly, empirically confirmed fact about the specific
Buildings and Driveways/Parking Lots layers used in this analysis** -- no row-by-row check was
performed (e.g., confirming a known building within the City of Fairfax's own limits is absent from
the source data). Given the consistency of evidence across both the licensing and GIS-boundary
documentation, the working assumption throughout this analysis is that both source layers are scoped
to unincorporated Fairfax County only, and both the C&I and parking-lot figures below should be read
as understating the true "greater Fairfax area" total to whatever degree real commercial buildings
and parking lots exist within those six excluded jurisdictions.

### 3.2 C&I rooftop buildings

**Source:** Fairfax County's own "Buildings" GIS layer (`FairfaxCounty_Buildings_....csv`, 20,955
rows), Fairfax County Department of Information Technology GIS Division. Building outlines with
elevation, captured primarily via planimetric updates from imagery ranging ORTHO1997 through
EAGLEVIEW 2023.

**Classification:** buildings tagged `Community Maps Type` as `Commercial or Retail Facility`,
`Industrial Facility`, `Hotel / Motel`, or `Health or Medical Facility`. Government/Military and
Education excluded (the latter to avoid double-counting with the separate school-solar analysis).

**Deduplication:** a real, confirmed data issue -- podium/multi-component buildings can appear as
multiple rows sharing one `Building Identification Number`, each row a different vertical component
(different top elevation, same ground elevation). Resolved via max(`Shape__Area`) per unique Building
ID -- the largest single component's footprint used as a defensible proxy for the building's overall
roof, rather than naively summing all components (which would double-count).

**Size threshold:** ≥600 sq ft (the established minimum-viable-rooftop threshold for buildings,
distinct from the ≥6,000 sq ft threshold used for parking lots).

**Result:** 4,510 buildings, 19,493,424 sq ft total footprint.

| | MW | MWh/yr |
|---|---:|---:|
| Mean-based (primary) | 132.4 | 231,947 |
| Median-based (sensitivity check) | 129.9 | 227,507 |

### 3.3 Parking lots

**Source:** Fairfax County's own "Driveways and Parking Lots" GIS layer
(`FairfaxCounty_Driveways_and_Parking_Lots_....csv`, 23,651 rows), already pre-filtered at source to
`Type = "PAVED PARKING LOT"` only (confirmed directly -- 23,651 of 23,651 rows).

**Size threshold:** ≥6,000 sq ft, matching Loudoun's own established threshold.

**Result:** 2,810 lots, 56,551,120 sq ft (1,298.2 acres) -- notably smaller than Loudoun's own
qualifying acreage (24% of Loudoun's figure) despite Fairfax being the larger, more built-up county;
not fully explained, flagged as an open question in Section 7.

| | Low (2.0 kW/space) | High (2.5 kW/space) |
|---|---:|---:|
| MW | 377.0 | 471.3 |
| Battery storage capacity (MWh, 4-hr) | 1,508.0 | 1,885.0 |
| Annual energy (MWh/yr, at 20% capacity factor) | 660,517 | 825,646 |

### 3.4 Schools

Two genuinely different kinds of figure exist for Fairfax schools -- not directly comparable, and
should not be added together without clear labeling:

**(a) Full theoretical potential, all 194 schools (142 elementary + 23 middle + 29 high):**
71.65 MW / 286,600 kWh paired battery *storage capacity*, computed from flat, user-set per-type kW
assumptions (Elementary 250 kW, Middle 500 kW, High 850 kW) benchmarked against real, installed
solar at *other* Virginia divisions (Richmond, Roanoke, Orange Co., Augusta Co.) -- applied uniformly
to every Fairfax school regardless of actual deployment status. Derived annual energy at the
established 20% capacity factor: 125,531 MWh/yr.

**(b) Real, currently deployed or committed solar:** FCPS's own most-current page (dated April 2026)
states a solar PPA covering 33 schools, board-approved April 2025, of which only 6 were individually
named as "currently producing" as of that page's own snapshot. Separately, 7 small (≤5 kW)
grant/fundraising-funded arrays exist at named schools. Across all sources, 16 individually-named
Fairfax schools could be confirmed with solar (3 high / 3 middle / 10 elementary); the broader
program, once the PPA pipeline completes, covers roughly 40 schools total. FCPS explicitly evaluated
and rejected parking-lot solar canopies for schools as not currently cost-effective. Dominion's
interconnection requirements have repeatedly stalled or shrunk FCPS projects across multiple
independent sources.

No reliable per-school-type kW or battery-storage figure exists for FCPS's real, deployed systems --
a genuine, unresolved data gap.

### 3.5 Combined total

| Component | MW | MWh/yr |
|---|---:|---:|
| C&I buildings | 132.4 | 231,947 |
| Parking lots | 377.0–471.3 | 660,517–825,646 |
| Schools (theoretical potential, all 194) | 71.65 | 125,531 |
| **Combined** | **581.0–675.3** | **1,017,995–1,183,124** |

---

## 4. Arlington County

### 4.1 Jurisdictional scope

Arlington County has no equivalent of Fairfax's embedded-independent-city exclusion -- Arlington has
no incorporated towns, and while it borders the City of Falls Church and the City of Alexandria,
neither is an enclave within Arlington's own boundary the way the City of Fairfax is within Fairfax
County. Arlington's figures are believed complete for the county as a whole, though this has not
been separately, independently verified the way the Fairfax exclusion was.

### 4.2 C&I rooftop buildings

**Source:** Arlington County's own "Buildings" GIS layer (`Arlington_Buildings.csv`, 49,064 rows),
Arlington County GIS Mapping Center / Department of Environmental Services.

**A real classification problem, diagnosed and corrected per direct user instruction:** Arlington's
own `CM_Type` field (its own "Community Maps Type"-style classification, directly parallel to
Fairfax's naming) severely under-tags commercial buildings -- only 164 of 49,064 rows (0.33%) are
tagged `Commercial / Retail`, confirmed exactly against the real data before acting on it. An
implausibly low figure for a dense, highly-commercialized jurisdiction.

**Fix, per direct user instruction:** any `General / Residential`-tagged building over 2,000 sq ft is
assumed commercial (rationale: large "residential"-classified structures in this context are likely
company-owned apartment/condo buildings -- economically more like a commercial building's roof than a
single-family home's). `Medical` and `Hotel` are included directly (parallel to Fairfax's own Health
and Hotel categories). `Religious` and `Government / Military` are excluded per direct user
instruction. `Education`, `Community Center`, `Transportation`, `Recreation`, and `Airport` are
excluded following the same precedent already established for Fairfax (Education specifically to
avoid double-counting with the school analysis below; `Airport` is a single 762,694 sq ft row,
almost certainly Reagan National's own terminal).

**Deduplication:** checked directly via Arlington's own `GIS_ID` field (the same underlying concern
Fairfax's Building ID field addressed) -- zero duplicated GIS_IDs found within the C&I-eligible
population specifically (0 of 10,120 eligible rows). No dedup step was needed; this is a checked
finding, not an assumption that Arlington's data lacks the same multi-part-building issue Fairfax's
had (Arlington's own dataset description uses the identical "a building may be made up of many
parts" language) -- it simply doesn't manifest within this specific eligible subset.

**Size threshold:** the same ≥600 sq ft floor established for Fairfax, confirmed to do real work: 10
of the 164 explicit Commercial/Retail rows fall under 600 sq ft and are correctly excluded.

**Result:** 10,133 eligible buildings (154 Commercial/Retail + 9,956 size-heuristic Residential + 15
Medical + 8 Hotel), 55,038,330 sq ft (1,263.5 acres) total footprint.

| | MW | MWh/yr |
|---|---:|---:|
| Mean-based (primary) | 373.8 | 654,886 |
| Median-based (sensitivity check) | 366.6 | 642,349 |

### 4.3 Parking lots

**Source:** Arlington County's own "Pave Parking Lot Polygons" GIS layer
(`Arlington_Pave_Parking_Lot_Polygons.csv`, 2,783 rows). No type/category field exists in this
dataset at all (unlike both Loudoun's and Fairfax's own parking-lot loaders) -- trusted via the
dataset's own authoritative name rather than a per-row type validation.

**One honest, unresolved limitation:** `GeoSyncDate` is a single, uniform timestamp across all 2,783
rows (to the second) -- this looks like an extraction/sync timestamp, not genuine per-row survey
vintage the way Fairfax's own `Source` field was. Data-collection age for this specific dataset
cannot be assessed from the fields provided.

**Size threshold:** ≥6,000 sq ft, same as Loudoun and Fairfax.

**Result:** 1,428 of 2,783 lots (51.3% -- notably higher than Fairfax's own 11.9% at the identical
threshold, an honest observation flagged rather than explained away: Arlington's parking-lot size
distribution skews larger, with the median sitting just above the threshold itself), 44,057,781 sq ft
(1,011.4 acres).

| | Low (2.0 kW/space) | High (2.5 kW/space) |
|---|---:|---:|
| MW | 293.7 | 367.1 |
| Battery storage capacity (MWh, 4-hr) | 1,174.9 | 1,468.6 |
| Annual energy (MWh/yr, at 20% capacity factor) | 514,595 | 643,244 |

### 4.4 Schools

**Real Arlington school counts** ("intermediate" = "middle"): 26 elementary, 6 middle, 9 high -- the
"9" figure is APS's own full "High Schools & Programs" category, which already includes
CTE/alternative programs (Arlington Career Center, Arlington Tech, Langston, Shriver) alongside ~5
comprehensive high schools; a narrower ~5 count is a valid alternate reading if preferred.

**How many are identifiable in the real buildings data:** Arlington's `Buildings` file has a separate
`SCHOOL` column that was checked directly and found to be an *attendance-zone* indicator, not a
building-use classification -- the large majority of its 287 flagged rows are actually tagged
`CM_Type = 'General / Residential'` with no school name at all. The genuine building-use field is
`CM_Type = 'Education'` (44 rows, directly parallel to Fairfax's own scheme), broken down via the
`SCHOOL` sub-code within those rows: 25 Elementary (ES+AES), 6 Middle (MS+AMS), 6 High (HS).

Two real catches within the "High" group, flagged rather than silently absorbed: one row is **Bishop
O'Connell High School** (private/Catholic, not APS); another is the **David M Brown Planetarium**
(not a comprehensive high school building at all). The genuine APS-public comprehensive high school
count in the footprint data is 3 (Wakefield, Washington-Liberty, Yorktown), not 6.

**Real roof sizes (sq ft), computed directly from the buildings file:**

| Type | n | Mean | Median | Min | Max |
|---|---:|---:|---:|---:|---:|
| Elementary | 25 | 60,225 | 58,651 | 43,606 | 83,006 |
| Middle | 6 | 117,746 | 117,092 | 75,775 | 159,953 |
| High -- full set (6, incl. non-comprehensive) | 6 | 115,032 | 143,241 | 2,458 | 199,248 |
| High -- 3 comprehensive only (Wakefield/W-L/Yorktown) | 3 | 187,515 | 189,345 | 173,952 | 199,248 |

**A genuine, unresolved methodological finding:** applying the same real NVRC density rate (0.006792
kW/sq ft) to these real, measured roof sizes gives implied kW figures **~1.5–1.64x higher** than the
flat per-type kW assumptions currently used in the theoretical-potential module (250/500/850 kW for
ES/MS/HS, the same assumptions used for both Loudoun's and Fairfax's own school figures above) -- a
fairly consistent ratio across all three types, not random noise:

| Type | Real mean roof → implied kW | Currently assumed | Ratio |
|---|---:|---:|---:|
| Elementary | 409 kW | 250 kW | 1.64x |
| Middle | 800 kW | 500 kW | 1.60x |
| High (comprehensive) | 1,274 kW | 850 kW | 1.50x |

This does not necessarily mean the original assumptions (used identically for Loudoun and Fairfax
above) were wrong -- they were themselves benchmarked against real, installed systems at other
divisions, which reflect real-world constraints (HVAC/mechanical equipment, budget, etc.) that a pure
footprint-area calculation doesn't capture. Presented as an open question for the reader to weigh,
not resolved in this document, and not yet checked against Loudoun's or Fairfax's own real building
footprints (no equivalent real-roof-size cross-check has been run for either of those two counties'
own schools).

**Aggregate rooftop-to-kW conversion** (per direct user instruction: no HS/MS/ES breakdown needed for
this figure): all 44 `CM_Type = 'Education'` rows converted as a single population. Includes Bishop
O'Connell and the Planetarium (not filtered out, since the question this figure answers is "how much
potential exists across all identifiable education-related buildings," not "at APS-owned
comprehensive schools specifically").

**Result:** 44 buildings, 3,130,564 sq ft (71.9 acres).

| | MW | MWh/yr |
|---|---:|---:|
| Mean-based (primary) | 21.3 | 37,250 |
| Median-based (sensitivity check) | 20.9 | 36,537 |

**Real, deployed solar -- a genuine data gap:** web research found real deployment activity but with
an honest, unresolved discrepancy between sources on the current count (APS's own page: "9 schools"
with arrays; a separate recent source: "8 solar schools"; 10 distinctly-named schools found across
all sources combined -- Discovery, Alice West Fleet, Washington-Liberty, Kenmore, Jefferson,
Tuckahoe, Cardinal, Glebe, Wakefield, Abingdon). Only one confirmed real per-school kW figure was
found (Discovery Elementary, ~500 kW). **Zero mentions of paired battery storage** were found at any
real, deployed Arlington school solar system, across every source checked -- genuinely different from
the paired-storage convention this project's own theoretical-potential figures assume throughout. No
avg kW/battery-kWh "already deployed" figure is computed here, since the underlying data is too thin
and inconsistent to average without manufacturing false precision.

### 4.5 Combined total

| Component | MW | MWh/yr |
|---|---:|---:|
| C&I buildings | 373.8 | 654,886 |
| Parking lots | 293.7–367.1 | 514,595–643,244 |
| Schools (all 44 identified education buildings, incl. 1 private + 1 non-school) | 21.3 | 37,250 |
| **Combined** | **688.8–762.2** | **1,206,731–1,335,380** |

---

## 5. Prince William County

### 5.1 Jurisdictional scope

Like Loudoun and Arlington, Prince William County has no equivalent of Fairfax's embedded
-independent-city exclusion for its own general land area. Worth noting separately: the
independent city of Manassas (and Manassas Park) sit within/adjacent to Prince William's own
boundary as their own, separate jurisdictions, analogous in kind to Fairfax's own independent
cities -- this has not been independently verified as an exclusion in the data sources used below,
consistent with how Loudoun's and Arlington's own scope was treated.

### 5.2 C&I rooftop buildings

**Source:** user-provided extract of Prince William County's own buildings GIS layer
(`PWCCommericialBuildings.xlsx`, 3,876 rows). The full county buildings layer exceeded the upload
size limit, so this extract was already pre-filtered to `StructureType=3` ("Commercial") before
upload.

**A real classification limitation, broader than initially flagged:** the user first noted "no type
information for industrial." Checked directly: the gap is broader than industrial specifically --
`StructureType` is uniformly the value 3 across all 3,876 rows, so no sub-type distinction survives
within this extract at all. The user then supplied Prince William's own full 10-value StructureType
legend (1=Residence, 2=House Trailer, 3=Commercial, 4=Residential Outbuilding, 5=Tank, 6=Silo,
7=Tower, 8=Pool, 9=Recreation Field, 10=Mixed Use), confirming there is **no separate "Industrial"
code anywhere in Prince William's own schema** -- industrial buildings are almost certainly folded
into "3=Commercial" rather than absent from the dataset. This means this county's population is
likely broader in composition than Fairfax's or Arlington's own "Commercial or Retail" categories
alone (which explicitly exclude industrial, tagged separately there) -- plausibly closer to their
"Commercial + Industrial" combined total. There is no way to split industrial back out from this
data.

**Deduplication:** no parcel/building-grouping field exists in this schema at all -- unlike
Fairfax's Building Identification Number or Arlington's GIS_ID, both `OBJECTID` and `GlobalID` are
confirmed fully unique across all 3,876 rows (checked directly). This means there is no way to
check for the same kind of podium/multi-component-building issue found in Fairfax's data -- each
row is treated as one distinct structure, since no field is available to test that assumption
against. A real, open limitation, not assumed away.

**Size threshold:** the same ≥600 sq ft minimum-viable-rooftop floor established for Fairfax's and
Arlington's buildings, using `ShapeSTArea` as the footprint field.

**Result:** 2,497 buildings, 922.2 acres (40,171,076 sq ft) total footprint.

| | MW | MWh/yr |
|---|---:|---:|
| Mean-based (primary) | 272.8 | 477,985 |
| Median-based (sensitivity check) | 267.6 | 468,834 |

### 5.3 Parking lots -- ESTIMATED, not measured

**Direct Prince William County GIS extraction has not yet succeeded.** The `TYPE_CODE` field
returns zero results despite repeated attempts. Rather than omit this component entirely, an
explicitly-labeled density-based estimate was built instead, using Loudoun's and Fairfax's own
real, GIS-measured parking-lot acreage and 2025 population estimates (both independently sourced
and verified: Loudoun 449,749; Fairfax 1,167,873; Prince William 502,966).

**The two source counties' own per-capita parking densities differ enormously** -- Loudoun 0.011877
acres/capita vs. Fairfax's 0.001112 acres/capita, a 10.7x gap -- so which county is used as the
anchor materially changes the result; this is not a minor methodological footnote.

**Anchor chosen per direct user decision: Loudoun.** Rationale given directly: Prince William's
greater distance from Washington, DC compared to Fairfax implies less structured/garage parking
(which land-value pressure near the urban core pushes developers toward) and proportionally more
surface-lot parking -- a development pattern more similar to Loudoun's own than to Fairfax's more
urbanized one. This is a substantive, mechanism-based argument, not an arbitrary anchor pick.

**Result (Loudoun-anchored, primary):** an estimated 5,974 acres of qualifying parking, run through
the same, unchanged canopy-sizing engineering already used for every other county in this document.

| | Low (2.0 kW/space) | High (2.5 kW/space) |
|---|---:|---:|
| MW | 1,734.7 | 2,168.4 |
| Battery storage capacity (MWh, 4-hr) | 6,939.0 | 8,673.7 |
| Annual energy (MWh/yr, at 20% capacity factor) | 3,039,279 | 3,799,098 |

**Fairfax-anchored sensitivity check, retained rather than discarded:** an estimated 559 acres ->
162.4–203.0 MW / 284,456–355,570 MWh/yr. The two anchors' results do not overlap at all, underlining
that this component carries real, substantial uncertainty until real Prince William GIS data
becomes available -- at which point this entire subsection should be replaced, not merely adjusted.

### 5.4 Schools

**Real Prince William school counts:** 62 elementary, 17 middle, 13 high (92 total).

**Full theoretical potential** (the same flat per-type kW assumptions -- Elementary 250 kW, Middle
500 kW, High 850 kW -- used identically for Loudoun's and Fairfax's own school figures, applied
uniformly regardless of actual deployment): 35.05 MW / 140,200 kWh paired battery *storage
capacity*. Derived annual energy at the established 20% capacity factor: 61,408 MWh/yr.

No real-deployed-solar research specific to Prince William schools has been conducted as part of
this project to date -- the same open gap already noted for Loudoun's own schools (Section 2.4).

### 5.5 Combined total

| Component | MW | MWh/yr |
|---|---:|---:|
| C&I buildings | 272.8 | 477,985 |
| Parking lots (ESTIMATED) | 1,734.7–2,168.4 | 3,039,279–3,799,098 |
| Schools (theoretical potential, all 92) | 35.05 | 61,408 |
| **Combined** | **2,042.6–2,476.3** | **3,578,671–4,338,491** |

---

## 6. Northern Virginia Grand Total

See the Executive Summary at the top of this document for the full Northern Virginia grand total,
the by-asset-type breakout (C&I / parking lots / schools, summed across all four counties), and
the by-county breakdown -- all three tables, and the caveats immediately following them, live there
rather than being repeated here.

---

## 7. Cross-County Comparison

- **C&I methodology differs by necessity, not inconsistency** (Section 1.1): Loudoun's own figure is
  a building-count × flat-kW estimate; Fairfax's, Arlington's, and Prince William's own figures are
  a footprint-area × density-rate estimate. The two approaches are not directly interchangeable, and
  a reader attempting to infer "typical building size" by dividing Loudoun's own MW by its building
  count would be extrapolating well beyond what that number actually represents.

- **Parking-lot data quality/availability varies sharply by county.** Loudoun, Fairfax, and
  Arlington all have real, measured GIS parking-lot data; Prince William's own GIS extraction has
  not yet succeeded, so its parking-lot figure is a density-based estimate rather than measured
  data (Section 5.3) -- the only component in this entire document that is not built from real,
  county-specific source data of some kind. Among the three real-data counties, qualification rates
  at the identical ≥6,000 sq ft threshold vary substantially: Fairfax 11.9%, Arlington 51.3%
  (Loudoun's own qualification rate was not separately computed as a percentage in the original
  Loudoun documentation, only the resulting acreage). Fairfax's own qualifying acreage, in
  particular, is only ~24% of Loudoun's -- despite Fairfax's much larger overall size -- an open
  question not resolved in this document, and the same underlying uncertainty (real densities can
  differ by an order of magnitude between counties) is exactly why Prince William's estimate carries
  a >10x spread between its two candidate anchors.

- **Arlington's and Prince William's own C&I estimates each required a real, non-trivial
  methodological adaptation** that neither Loudoun's nor Fairfax's own C&I estimate needed.
  Arlington's source data's own `Commercial / Retail` tag captured only 0.33% of buildings, an order
  of magnitude below a plausible reading of the county's real commercial density, requiring a
  size-based reclassification heuristic layered on top of the tag (Section 4.2). Prince William's
  own source schema has no "Industrial" category at all, folding it into "Commercial" with no way to
  split it back out (Section 5.2) -- a different kind of composition uncertainty than Arlington's,
  but a real one.

- **All four counties' school figures share the same core limitation**: none reflect verified, real
  -world deployed solar capacity. Loudoun's and Prince William's have not yet had real-deployment
  research conducted at all; Fairfax's and Arlington's own real-deployment research both found
  genuine, unresolved discrepancies between sources on current counts, and zero evidence of paired
  battery storage at any real, deployed system in either county -- despite every theoretical
  -potential figure in this document assuming paired storage throughout.

---

## 8. Open Questions and Limitations (Consolidated Across All Four Counties)

1. **Fairfax jurisdictional scope** (Section 3.1) -- the single largest known gap in this document.
   Six jurisdictions' worth of real commercial buildings and parking lots are excluded from every
   Fairfax figure.
2. **Prince William's parking-lot figure is estimated, not measured** (Section 5.3) -- the only
   component in this entire document not built from real, county-specific source data. Carries a
   >10x spread between its two candidate anchor counties; should be replaced with real GIS data at
   the first opportunity, not merely refined.
3. **Fairfax parking-lot acreage is only ~24% of Loudoun's own established figure** despite Fairfax
   being the larger county -- not explained, flagged as open. The same unexplained magnitude of
   cross-county variation is part of why Prince William's own estimate (item 2) carries such wide
   uncertainty.
4. **Prince William's C&I building population cannot be split into commercial vs. industrial**
   (Section 5.2) -- the source schema has no industrial code at all, unlike Fairfax's and
   Arlington's own schemas, which tag industrial separately. This county's own C&I composition is
   therefore not directly comparable to the other three on an apples-to-apples basis.
5. **No reliable per-school-type kW/battery figure exists for real, deployed solar** at any of the
   four counties' schools -- a genuine, unresolved data gap common to all four.
6. **Zero evidence of paired battery storage at any real, deployed school solar system** found in
   either Fairfax or Arlington (Loudoun's and Prince William's own schools not yet researched),
   despite this project's own theoretical-potential figures assuming paired storage throughout every
   county.
7. **The real-vs-assumed school roof-size/kW discrepancy** (Arlington only, ~1.5–1.64x) has not been
   checked against Loudoun's, Fairfax's, or Prince William's own real school building footprints,
   nor resolved or applied to any county's theoretical-potential figures -- presented as an open
   question.
8. **Arlington's school rooftop figure includes one private school and one non-school facility**
   (Bishop O'Connell, the Planetarium) not filtered out of the aggregate conversion, per the scope
   of the question asked when it was computed.
9. **Prince William's C&I building data has no parcel/building-grouping field at all** (Section
   5.2), unlike Fairfax's Building Identification Number or Arlington's GIS_ID -- there is no way to
   check for the same kind of podium/multi-component-building issue found in Fairfax's own data.
10. **The real 8-point NVRC density sample underlying every kW conversion in this entire document,
    for all four counties**, is geographically narrow (Loudoun only -- none of the 8 points are
    themselves Fairfax, Arlington, or Prince William buildings) and of a mid-2010s imagery vintage.
11. **Loudoun's own source-data vintage limitation** (NVRC data ~2016, while Loudoun has led Virginia
   in new commercial investment every year since) likely undercounts newer Loudoun construction
   specifically, on top of the shared sample-narrowness limitation above.
12. **The different C&I methodologies (Section 1.1, Section 7) are not directly comparable without
   care** -- a reader should not treat Loudoun's own building-count-based figure and Fairfax's/
   Arlington's/Prince William's own footprint-based figures as measuring exactly the same underlying
   quantity in exactly the same way -- nor should Prince William's own broader
   commercial-plus-industrial composition (item 4) be treated as directly comparable to Fairfax's or
   Arlington's own narrower "commercial only" figures without accounting for that difference.

---

## Appendix: Supporting Files and Code

| County | File | Contents |
|---|---|---|
| Shared | `rooftop_solar_estimation_base.py` / `test_rooftop_solar_estimation_base.py` | Shared base class hierarchy for C&I/school MW+MWh estimation (9 tests) |
| Shared | `loudoun_parking_canopy_and_storage.py` / `test_loudoun_parking_canopy_and_storage.py` | Shared, county-agnostic parking-canopy engineering classes; Loudoun/Fairfax/Arlington classmethods (30 tests) |
| Loudoun | `address_classifier.py` / `test_address_classifier.py` | Business-record parsing and classification (56 tests) |
| Loudoun | `loudoun_ci_rooftop_solar_estimate.py` / `test_loudoun_ci_rooftop_solar_estimate.py` | Deduplication and solar-sizing logic (16 tests) |
| Loudoun | `loudoun_parking_lot_sqft.py` / `test_loudoun_parking_lot_sqft.py` | Road-casing extract loader and filtering |
| Fairfax | `fairfax_ci_rooftop_solar_estimate.py` / `test_fairfax_ci_rooftop_solar_estimate.py` | C&I building classification and solar-sizing logic (14 tests) |
| Fairfax | `fairfax_parking_lot_sqft.py` / `test_fairfax_parking_lot_sqft.py` | Parking-lot extract loader and filtering (7 tests) |
| Arlington | `arlington_ci_rooftop_solar_estimate.py` / `test_arlington_ci_rooftop_solar_estimate.py` | C&I and school building classification and solar-sizing logic (18 tests) |
| Arlington | `arlington_parking_lot_sqft.py` / `test_arlington_parking_lot_sqft.py` | Parking-lot extract loader and filtering (8 tests) |
| Prince William | `prince_william_ci_rooftop_solar_estimate.py` / `test_prince_william_ci_rooftop_solar_estimate.py` | C&I building classification and solar-sizing logic (11 tests) |
| Prince William | `prince_william_parking_lot_density_estimate.py` / `test_prince_william_parking_lot_density_estimate.py` | Density-based parking-lot ESTIMATE (not a real GIS loader, since direct extraction has not yet succeeded) (12 tests) |
| Shared | `school_rooftop_solar_assumptions.py` | Per-locality school counts and theoretical-potential kW/battery-kWh assumptions (11 NoVA/Hampton Roads localities, including all four counties in this document) |
| Shared | `Data_Sourcing_Log.md` | The full, chronological research and methodology record this document was distilled from |
