# Parking-Lot Reference Basis: What Is Measured, What Is Not

**Status: working note, 2026-09-11. Supersedes the reference basis currently encoded in
`lp_package/population_extrapolation.py`.**

This note records a sequence of findings that changed which parking figures in this project are
defensible. The short version: of four jurisdictions believed to have real parking measurements,
**one does** — and it is the one added most recently.

---

## 1. What prompted the review

`population_extrapolation.py` derives a statewide C&I and parking-lot solar potential by applying
per-capita rates from reference counties to 28 other Virginia jurisdictions. Its parking rate range
came out at **0.3607 to 3.8448 kW/capita — a 10.7× spread** — producing a statewide parking
estimate of **1,533 to 16,344 MW**. A range that wide is not a finding; it is an admission that the
basis is unsound.

Two causes were suspected and both turned out to be real, plus a third that was not anticipated.

---

## 2. First finding: the basis was circular

The module excludes Loudoun deliberately, and states why:

> *"Loudoun's own C&I MW/capita is a documented, known outlier (data-center-driven commercial
> boom)... Including either outlier in the reference basis would distort the rate applied to every
> other jurisdiction."*

That reasoning is correct. But of its two reference counties, **Prince William's parking figure
(1,734.7–2,168.4 MW) is itself derived by extrapolating Loudoun's per-capita density** — see
`prince_william_parking_lot_density_estimate.py`, which says so in its own docstring. Loudoun is
excluded at the front door and re-enters through Prince William.

The 10.7× spread is therefore not geographic variation. It is the Loudoun-versus-Fairfax gap,
reproduced inside a basis built to exclude it.

---

## 3. Second finding: Fairfax's extract is coverage-limited

Fairfax was the only remaining reference with a direct GIS measurement. Examining it against the
others:

| | acres (≥6,000 sqft) | % of land area |
|---|---:|---:|
| Loudoun | 5,342 | 1.6% |
| **Fairfax** | **1,298** | **0.5%** |
| Arlington | 1,012 | 6.1% |
| Richmond City | 2,877 | 7.2% |

Fairfax reports **less parking than Loudoun** despite far greater commercial development, and
one-fourteenth of Richmond's land-area share.

The size distribution explains it:

| band | rows | acres |
|---|---:|---:|
| driveway-scale (<6k sqft) | 20,841 | 379 |
| small lot (6k–20k) | 2,011 | 497 |
| mid lot (20k–100k) | 759 | 656 |
| **large lot (>100k)** | **40** | **146** |

Median polygon is **308 sqft — a single parking space**. Eighty-eight percent of rows are
driveway-scale. And there are **only 40 polygons above 100,000 sqft in the entire county**, which
contains Tysons, Reston Town Center, Fair Oaks, Springfield, Seven Corners and Merrifield. Tysons
Corner Center's surface lots alone would supply several.

The dataset is named "Driveways and Parking Lots" and is behaving as a driveways layer that
happens to contain some parking. Mean lot size above 6,000 sqft is 20,125 sqft against Richmond's
35,208 — it is missing the large end, not measuring smaller lots.

### The structured-parking objection, and its limit

Tysons parking is substantially **structured** — multi-level decks rather than surface lots — and a
footprint-based polygon layer records one level's area however many decks sit above it.

For solar canopy purposes that is **correct**, not an error: only the top deck can be canopied, so
footprint is the right measure. This effect is real and explains part of the gap.

It cannot explain all of it. Richmond and Arlington both have structured parking and both land near
6–7% of land area. A 14× gap survives the objection.

---

## 4. Third finding: per-capita is the wrong normalizer

Richmond City and Loudoun have nearly identical per-capita parking — 0.01203 against 0.01188
acres per person — despite being opposite kinds of place. By land area they are nothing alike:
7.2% against 1.6%.

The reason is structural: **a jurisdiction's commercial parking serves its economic catchment, not
its residents.** Richmond City has 239,227 residents but is the employment core of a metro of
roughly 1.3 million. Dividing its parking by its own population produces a number that means very
little.

The error runs in both directions and therefore cannot be corrected by a constant factor. Applying
Fairfax's per-capita rate to Richmond predicts roughly **266 acres** against a measured **2,877** —
understating by about 11×.

### Political type is not the right classification either

The module currently splits targets into `county` and `independent_city`. Virginia's political
geography does not track economic function:

- **Chesapeake** is legally an independent city and functionally a large suburb with its own
  businesses, with Norfolk drawing employment from it.
- **Stafford** is legally a county and functionally the same thing, oriented toward DC.
- **Richmond** and **Norfolk** are employment destinations that draw from surrounding
  jurisdictions.

Chesapeake and Stafford likely have similar parking profiles despite sitting on opposite sides of
the city/county divide. The meaningful cut is **employment destination versus bedroom community**,
not city versus county.

**Census daytime population ratio** operationalizes this with a sourced figure: resident population
plus in-commuters minus out-commuters. Employment destinations exceed 1.0; bedroom communities fall
below it. This is a proposal, not yet tested — see Open Items.

---

## 5. Where the reference basis actually stands

| jurisdiction | measurement | status |
|---|---|---|
| Loudoun | real GIS (Road Casings RD_TYPE=2) | real, excluded as data-center outlier |
| Fairfax | "Driveways and Parking Lots" | **coverage-limited — not usable as an anchor** |
| Arlington | real GIS (Pave Parking Lot Polygons) | real, excluded as "too dense" |
| Prince William | derived from Loudoun per-capita | **circular — not an independent measurement** |
| **Richmond City** | real GIS (Transportation Surfaces, SubType 4) | **sound; currently the only one** |

**Richmond is not an addition to the basis. It is currently the only sound member of it.**

### Arlington should be reconsidered

Arlington was excluded for being "genuinely, distinctively dense... unlike any of the 28
extrapolation targets." At 6.1% of land area it sits close to Richmond's 7.2%. Those two agree with
each other; Fairfax is the outlier.

If two independent urban measurements land at 6–7%, that is a real urban-core rate with
confirmation, and excluding one of only two sound measurements is a larger cost than the
representativeness concern it was meant to address.

---

## 6. Richmond City: the measurement

Source: Richmond City Transportation Surfaces extract, 167,567 rows, 100% FIPS 760 (no
neighbouring-jurisdiction overdraw).

SubType 4 confirmed as parking by direct inspection of known lots in the county's map interface —
**not** inferred. Inference was tried first and failed: compactness analysis separated linear
features cleanly (subtypes 9 and 10 at 142.8 and 104.0) but could not distinguish parking from
driveways and aprons, which all cluster at 24–31. A size-plus-shape heuristic would have picked
SubType 4 for the right answer by the wrong reasoning.

This matters because the same project had already been burned by schema analogy: Richmond
Structures SubType 3 was assumed C&I because Prince William's `StructureType=3` is Commercial. It
turned out to be accessory structures — median area 200 sqft, sheds and detached garages.

| | figure |
|---|---|
| qualifying polygons (≥6,000 sqft) | 3,560 |
| qualifying area | 125,339,845 sqft (2,877.4 acres) |
| share of city land area | 7.2% |
| solar canopy potential | **835.6 – 1,044.5 MW** |
| paired storage (4 h, 1:1) | **3,342 – 4,178 MWh** |

Units confirmed square feet by the same empirical test used for Fairfax and Richmond Structures:
the largest polygon is 37.3 acres read as sqft and 401.8 acres read as sqm; the latter is
impossible for one polygon.

Paved flag present (164,669 yes / 2,898 no) and **not** filtered on, following the Loudoun finding
that unpaved lots skew substantially larger than paved — median area over 5× — consistent with
engineered permeable-pavement facilities rather than informal gravel.

---

## 7. What this changes in the whitepaper

The statewide extrapolated parking figure (1,533–16,344 MW) **should not be cited**. Its low bound
rests on a coverage-limited dataset and its high bound on a circular derivation.

The four-county NoVA distributed-solar figures are **not** affected by the per-capita findings —
those are direct measurements, not extrapolations. Fairfax's parking component within them carries
the coverage limitation and should be footnoted.

---

## 8. Open items

1. **Fairfax parking needs a different source** — or exclusion with the reason stated. Check
   whether Fairfax publishes a parking-only layer separate from "Driveways and Parking Lots."
2. **Reinstate Arlington** in the reference basis, subject to a decision on the density concern.
3. **Replace Prince William's derived figure** with a real measurement, or drop it from the basis.
4. **Acquire Chesapeake and Stafford** — a matched functional pair spanning the city/county divide,
   which tests the employment-destination classification directly rather than adding two unmatched
   points.
5. **Test land-area and daytime-population normalizers** against per-capita once three or more
   sound measurements exist. Not before: a normalizer chosen on two points is asserted, not tested.
6. **Re-derive the DOM zone distributed siting cap** (currently 7,440 MW in `assumptions.py`) once
   the basis is repaired, since it descends from this work.

---

## 9. Addendum: Chesapeake C&I, and a limit on coded domains (2026-09-11)

Chesapeake City's building outlines were added as the fifth C&I measurement: **4,859 buildings,
60,686,088 sqft (1,393.2 acres), 412.2 MW mean-based, 722,088 MWh/yr.**

Its 14-value `BUILDINGCLASS` domain was read from the city's own ArcGIS REST endpoint rather than
inferred, and it is the richest legend of the five counties. Two classes it has that Arlington
lacked improve the classification:

- **Industrial (12)** exists separately. Arlington had no industrial category; Prince William folds
  industrial into Commercial. Including it makes Chesapeake consistent with Fairfax and Prince
  William and more complete than Arlington.
- **Apartment (14)** removes Arlington's weakest step — a size heuristic assuming
  "General / Residential" over 2,000 sqft was commercial, applied to 9,956 buildings. Chesapeake
  states the category, so the heuristic is unnecessary and General/Residential is excluded whole.

Chesapeake and Arlington consequently use **different rules**. That is deliberate — use the best
classification each dataset supports rather than degrading one to match the other's limitation —
but the two are not strictly like-for-like and cross-county comparison should say so.

### The finding: a sourced legend does not mean a consistently applied one

Chesapeake is the only extract of the five carrying a **NAME** field, which made the classification
checkable against reality. It failed that check.

**A 636,190 sqft Amazon distribution centre — 14.6 acres — is classified `Commercial` (6), not
`Industrial` (12)**, in a schema that has an Industrial class.

| consequence | effect |
|---|---|
| C&I total | **unaffected** — both classes are included, 412.2 MW stands |
| per-class breakdown | **indicative only** — the 32.0% Industrial share understates reality |
| load-shape use | **not supported** — industrial and retail roofs sit above very different profiles |
| other counties | **unknown and undetectable** — none of the other four carry a name field |

This is a general caution, not a Chesapeake defect: a published coded domain states what the codes
*mean*, never how consistently they were *applied*. Every county figure in this project rests on a
classification that could carry the same inconsistency, and only Chesapeake gave any means of
noticing.

The per-class breakdown was worth computing regardless: **Industrial and Apartment together are
45.9% of Chesapeake's footprint**, and both are included on this project's own judgment rather than
established precedent. A decision of that size should be visible rather than sitting inside a
total someone has to take on trust. A test asserts that share, so a change to it requires a
documented decision rather than passing silently.

### Still outstanding

This is the **C&I** side, which already had four measurements. **Parking remains the broken side**,
with Richmond as its only sound member. Chesapeake's paved-surfaces or parking layer, if it
publishes one, is the higher-value acquisition — and Stafford alongside it would give the matched
functional pair that tests the employment-destination classification.

---

## 10. Fairfax corrected, and the normalizer question resolved (2026-09-11)

Section 3 above concluded that Fairfax's parking extract was coverage-limited and unusable. **That
conclusion was wrong.** Two real errors existed, but neither was coverage, and the comparison that
condemned the dataset was using the wrong normalizer.

### Error 1: the extract was missing unpaved parking lots

Fairfax's parent feature class `GIS_MINOR_TRANSPORTATION_AREAS` carries eight coded values,
obtained from the county's REST endpoint:

| code | included? |
|---|---|
| PAVED PARKING LOT | yes — the original extract |
| **UNPAVED PARKING LOT** | **was missing** |
| PAVED / UNPAVED PRIVATE ROAD | no, correctly |
| PAVED / UNPAVED DRIVEWAY | no, correctly |
| PAVED / UNPAVED SHARED DRIVE | no, correctly |

Unpaved adds **851 polygons, 100 acres — 6.0%** of the paved total. Smaller than Loudoun's 14.8%,
which is consistent: Loudoun's unpaved lots are engineered permeable-pavement facilities at rural
commercial sites, a pattern with less scope in Fairfax.

The direction holds, though. Unpaved lots here are again **substantially larger** than paved —
median 1,759 against 308 sqft — confirming Loudoun's finding that these are real facilities, not
informal gravel, and should never be filtered out as noise.

### Error 2: the 6,000 sqft threshold does not transfer

Adopted on the instruction *"use at least the amount we filtered for Loudoun"*, where it derived
from Loudoun's own data-dictionary definition of a qualifying Type 2 feature.

Fairfax's median paved parking polygon is **308 sqft — one parking space**. These are fragments:
pieces of real lots split by islands, aisles, or repaving dates. Loudoun's module anticipated the
pattern exactly —

> *"many real parking lots are digitized as multiple adjacent polygon fragments (islands,
> different paving dates, etc.) rather than one polygon per physical lot"*

— but the consequence was not carried across. **Fragments sum to real lot area**, so a minimum-size
filter discards genuine parking rather than excluding noise.

| | polygons | acres |
|---|---:|---:|
| paved | 23,651 | 1,677 |
| unpaved | 851 | 100 |
| **corrected total** | **24,502** | **1,777** |
| *previously reported* | *2,810* | *1,298* |

**Fairfax canopy potential: 516.2 – 645.2 MW**, against 377.0 – 471.3 previously. A 37% correction.

### The normalizer: parking scales with commercial floorspace

Fairfax was condemned in §3 for reporting 0.65% of land area as parking against Richmond's 7.82%
and Arlington's 6.08%. Land area is the wrong denominator — it conflates undeveloped land,
development intensity, and structured-versus-surface parking into a single number, and those vary
enormously between Loudoun's farmland, Fairfax's suburbs and Arlington's urban core.

Normalized against **C&I building footprint** — what parking physically scales with:

| | C&I footprint | parking | ratio | reading |
|---|---:|---:|---:|---|
| **Fairfax** | 19.5M sqft | 73.1M sqft | **3.75×** | surface-parked suburb |
| **Arlington** | 55.0M sqft | 44.1M sqft | **0.80×** | structured, transit-served |

3.75× is the expected range for surface-parked suburban development. 0.80× is the signature of a
jurisdiction that parks vertically — Rosslyn-Ballston, Crystal City. **Fairfax is normal and
Arlington is the outlier**, the reverse of the §3 reading.

### Why this normalizer is the right one

1. **It is causal, not correlative.** Parking is built to serve floorspace. Population and land
   area are proxies at best; a jurisdiction's commercial parking serves its economic catchment
   (see §4), and its land area includes however much farmland it happens to contain.
2. **It discriminates structured from surface parking** — which is exactly what matters for canopy
   solar, since a deck yields only its top level of footprint.
3. **It is computable from data already held**: C&I footprint exists for Loudoun, Fairfax,
   Arlington, Prince William and Chesapeake.

This supersedes both the per-capita method encoded in `population_extrapolation.py` and the
land-area and daytime-population alternatives proposed in §4.

### Corrections to the earlier sections of this note

- **§3 is withdrawn.** Fairfax is usable. Its two errors are fixed above.
- **§5's table is superseded.** Fairfax returns to the basis as the surface-parked suburban
  reference — the type the eight-jurisdiction survey found nowhere else.
- **§4's normalizer proposals are superseded** by parking-per-C&I-footprint.
- **§6 stands.** Richmond remains sound.
- **The Arlington reinstatement recommendation stands**, and is now better supported: at 0.80× it
  is a genuine structured-parking datum rather than merely "too dense".

### What the survey established about coverage

Eight jurisdictions checked for parking layers:

| has a parking layer | does not |
|---|---|
| Loudoun, Fairfax, Arlington, Richmond | Chesapeake, Prince William, Stafford, Chesterfield |

Four of eight, and three of those four are Northern Virginia. **Statewide parking extrapolation
cannot be grounded in per-jurisdiction measurement** — that is a finding with evidence behind it,
not a suspicion. Any statewide figure must rest on a ratio applied to measured commercial
floorspace, with the ratio conditioned on whether a jurisdiction parks on the surface or in decks.

### Open items, revised

1. ~~Fairfax needs a different source~~ — **resolved**; corrected above.
2. **Reinstate Arlington** as the structured-parking reference. Still outstanding.
3. **Replace Prince William's derived figure.** Its circularity is unaffected by any of this.
4. **Rework `population_extrapolation.py`** onto parking-per-C&I-footprint, with separate ratios
   for surface-parked and structured jurisdictions.
5. **Re-derive the DOM zone distributed siting cap** (7,440 MW) once the basis is repaired.
6. Chesapeake, Stafford, Chesterfield and Henrico publish no parking data — their parking must be
   estimated from measured C&I footprint via the ratio, not extrapolated per capita.

---

## 10. Fairfax corrected — and the diagnosis in §3 was wrong (2026-09-11)

Section 3 concluded Fairfax's parking extract was "coverage-limited — not usable as an anchor."
**That was wrong**, and the reasoning that produced it was wrong in an instructive way. Fairfax is
recoverable, and is now the project's suburban parking reference — the gap identified as most
significant, since surface parking is overwhelmingly a suburban phenomenon.

Two real errors existed, neither of them the one diagnosed.

### Error 1: the extract omitted unpaved parking lots

Fairfax's parent feature class `GIS_MINOR_TRANSPORTATION_AREAS` carries eight coded values, **two**
of which are parking:

| code | in extract? |
|---|---|
| `PAVED PARKING LOT` | yes — 23,651 rows |
| `UNPAVED PARKING LOT` | **no — omitted** |
| `PAVED / UNPAVED PRIVATE ROAD` | correctly excluded |
| `PAVED / UNPAVED DRIVEWAY` | correctly excluded |
| `PAVED / UNPAVED SHARED DRIVE` | correctly excluded |

Unpaved adds **851 polygons, 100 acres — 6.0%** of the paved total. Smaller than Loudoun's 14.8%,
which is consistent rather than contradictory: Loudoun's unpaved lots are engineered
permeable-pavement facilities at rural commercial sites, a pattern with less scope in Fairfax.

The direction holds. Unpaved lots are again substantially **larger** than paved — median 1,759 sqft
against 308 — confirming Loudoun's finding that they are real facilities, not informal gravel, and
must not be filtered out as noise.

### Error 2: the 6,000 sqft threshold does not transfer

Adopted on the instruction *"use at least the amount we filtered for Loudoun."* Loudoun derived it
from its own data dictionary — a qualifying Type 2 feature is "over 200 ft long, for 20 spaces or
more," about 6,000 sqft at ~300 sqft/space.

**Fairfax's median `PAVED PARKING LOT` polygon is 308 sqft — one parking space.** These are
fragments: pieces of real lots split by islands, aisles, or repaving dates. Loudoun's own module
anticipated the pattern —

> *"many real parking lots are digitized as multiple adjacent polygon fragments (islands, different
> paving dates, etc.) rather than one polygon per physical lot"*

— but the consequence was never carried across. Fragments sum to real lot area, so the threshold
discards genuine parking rather than excluding noise.

### Corrected figure

| | polygons | acres |
|---|---:|---:|
| paved | 23,651 | 1,677 |
| unpaved | 851 | 100 |
| **total** | **24,502** | **1,777** |

Previously reported: 1,298 acres. **Canopy potential 516.2 – 645.2 MW**, against 377.0 – 471.3 —
a **37% correction**.

### Why the §3 diagnosis failed: land area is the wrong normalizer

Fairfax was condemned on reporting 0.65% of land area as parking against Richmond's 7.82% and
Arlington's 6.08%. But land area conflates undeveloped acreage, development intensity, and
structured-versus-surface parking into a single number, and those vary enormously between
Loudoun's farmland, Fairfax's suburbs and Arlington's urban core.

Normalized against **C&I building footprint** — the quantity parking actually scales with — the
picture inverts:

| | C&I footprint | parking | ratio |
|---|---:|---:|---:|
| **Fairfax** | 19.5M sqft | 73.1M sqft | **3.75×** |
| **Arlington** | 55.0M sqft | 44.1M sqft | **0.80×** |

3.75× is the expected range for surface-parked suburban development. 0.80× is the signature of a
jurisdiction that parks vertically. **Fairfax's data was sound; the comparison that condemned it
was not.**

This also resolves the "Fairfax has less parking than Loudoun despite more commercial development"
objection. Loudoun has abundant malls and shopping centres, far less transit — fewer Metro stops,
so more car trips — and a dramatically lower structured-to-surface ratio. Fairfax's parking at
Tysons, Reston, Merrifield and Springfield is substantially decked. For canopy solar that is
**correctly** counted as footprint, since only the top deck can be covered. Loudoun exceeding
Fairfax per square mile is the expected result, not an anomaly.

### Recommended normalizer

**Parking area per unit of C&I building footprint**, replacing per-capita. It is physically causal
rather than correlative, computable from data already held for five jurisdictions, and it
discriminates structured from surface parking — precisely the distinction that matters for canopy
solar. Separate ratios should be carried for surface-parked and structured jurisdictions.

---

## 11. Statewide parking coverage: a finding, not an obstacle

Eight jurisdictions were checked for published parking-lot GIS. **Four have it; four do not.**

| has parking layer | no parking layer |
|---|---|
| Loudoun, Fairfax, Arlington, Richmond City | Chesapeake, Prince William, Stafford, Henrico, Chesterfield |

Three of the four with data are Northern Virginia; the fourth is Richmond. **No suburban county
outside NoVA publishes parking geometry.** Per-jurisdiction collection therefore cannot produce
statewide coverage, however much effort is spent — this is a property of Virginia's GIS landscape,
not of the search.

The corrected reference basis:

| jurisdiction | acres | status |
|---|---:|---|
| **Fairfax** | 1,777 | **sound — the suburban reference** |
| **Richmond City** | 2,877 | **sound — urban employment destination** |
| **Arlington** | 1,012 | **sound — structured/transit-served**; reinstate |
| Loudoun | 5,342 | real, data-centre outlier; usable with caveat |
| Prince William | derived | circular — replace or drop |

Four real measurements spanning three genuinely different development types. That is a basis for a
**typed** estimate — apply a surface-parked ratio to surface-parked jurisdictions and a structured
ratio to structured ones — rather than a single per-capita rate applied uniformly.

---

## 12. Limitation: no site survey was performed

**No shading assessment was undertaken for any location in this analysis.** Every rooftop and
canopy figure in this project assumes unobstructed solar access, which no real site has entirely.

The effect differs between the two resource types, and the parking figures are the more exposed:

**Rooftop.** The NVRC Solar Map sample underlying every county's density rate reports each
building's *usable* roof area alongside its kW, so shading and obstruction are reflected **for
those eight buildings** — HVAC plant, parapets, adjacent structures. Extrapolating that density
assumes other buildings are shaded similarly. Since all eight are in Sterling, Leesburg and
Ashburn — relatively open suburban commercial sites — the rate is more likely optimistic for older,
denser, more treed areas than pessimistic.

**Parking canopy — the larger exposure.** The canopy figures apply a kW-per-space density to
measured lot area with **no shading deduction at all**. Mature tree canopy in parking lots is
common and frequently *mandated*: many Virginia jurisdictions impose parking-lot tree canopy
requirements precisely to reduce heat island effect. A lot meeting a 10% canopy standard has real
generation loss, concentrated at exactly the perimeter and island locations where trees are placed.

Neither figure should be read as deliverable capacity. They are **upper bounds on the physical
resource**, and a project-level assessment would apply site-specific derates.

This is a known and stated limitation, not a correctable one within this analysis — a shading
assessment requires LiDAR-derived canopy models or site visits, neither of which is in scope. It
should appear in the whitepaper wherever a rooftop or canopy MW figure is cited.

---

## 13. Resolution: `parking_ratio_basis.py` (2026-09-11)

`population_extrapolation.py` is superseded for parking. The replacement estimates parking area
from **measured C&I building footprint**, typed by development pattern.

### The two anchors, and why there are only two

| type | anchor | C&I footprint | parking | ratio |
|---|---|---:|---:|---:|
| surface-parked | **Fairfax County** | 19,493,424 | 77,426,918 | **3.97** |
| structured | **Arlington County** | 55,038,330 | 47,300,701 | **0.86** |

Every other jurisdiction is blocked structurally, not for want of effort:

| | has parking | has C&I | blocked because |
|---|---|---|---|
| Loudoun | ✓ | ✗ | C&I source is business-licence records with no area field |
| Richmond City | ✓ | ✗ | Structures layer carries no building-use field |
| Chesapeake | ✗ | ✓ | publishes no parking layer |
| Prince William | ✗ | ✓ | publishes no parking layer |

**One anchor per type.** There is no within-type variance to estimate from, so the module offers
no confidence interval, and a test asserts that no result field ever implies one. The two anchors
differ by 4.6×, which makes **classification into the wrong type the dominant source of error** —
larger than any measurement uncertainty in the anchors themselves.

### Typing is by development pattern, not political category

`SURFACE_PARKED` and `STRUCTURED` are named for the physical mechanism. Virginia's political
geography does not track it: Chesapeake is legally an independent city and functionally a
surface-parked suburb; Stafford is legally a county and functionally the same. The city/county
split in the superseded module was the wrong cut.

### Recommendation for the whitepaper

**Report measured jurisdictions; state that Virginia's GIS coverage does not support statewide
parking extrapolation.**

Of eight jurisdictions checked, four publish parking geometry and **no suburban county outside
Northern Virginia does**. That is a property of the data landscape. A defensible *"here is what
four jurisdictions have, and the data does not permit more"* is stronger before the SCC than a wide
extrapolated range that invites exactly the challenge it cannot survive.

`parking_ratio_basis.py` exists so an estimate CAN be produced where one is genuinely needed, with
its limitations attached programmatically via `basis_warning()`, rather than produced ad hoc
without them.

### Measured figures, corrected

| jurisdiction | acres | canopy MW | status |
|---|---:|---:|---|
| Loudoun | 5,650 | — | data-centre outlier, usable with caveat |
| Richmond City | 3,128 | — | sound, urban employment destination |
| **Fairfax** | **1,777** | **516.2 – 645.2** | **sound, surface-parked suburban** |
| Arlington | 1,086 | — | sound, structured/transit-served |

All figures carry the §12 limitation: no site survey, no shading deduction, upper bounds on the
physical resource rather than deliverable capacity.

---

## 14. Data vintage: a systematic understatement across every source (2026-09-11)

The NREL rooftop workbook was obtained to provide an independent benchmark. It does, but examining
it surfaced a limitation that applies to **every** figure in this assessment, not only to NREL's.

### Virginia's NREL LiDAR coverage is 79% from 2007

The workbook covers 79 Virginia ZIPs — Hampton Roads and Richmond metro. There is **no Northern
Virginia coverage**, so it cannot check the four-county assessment at all.

| jurisdiction | LiDAR year | medium+large MW |
|---|---|---:|
| Virginia Beach | 2007 | 859 |
| Norfolk | 2007 | 544 |
| **Chesapeake** | **2007** | 445 |
| Newport News | 2007 | 386 |
| Hampton | 2007 | 312 |
| Richmond City | 2008 / 2013 | 274 |
| Henrico | 2013 | 228 |
| Chesterfield | 2013 | 219 |
| Portsmouth | 2007 | 184 |
| York, Prince George, Poquoson, Dinwiddie | mixed | 121 |

**All of Hampton Roads is 2007 — nineteen years old.** Two effects, both understating:
buildings constructed since are absent, and the shading screen (roof planes producing below 70% of
unshaded output) was assessed against 2007 tree canopy, which nineteen years of growth has since
made stricter.

### The Chesapeake cross-check is weaker than it first appeared

Our 412.2 MW rests on **current** building geometry; NREL's 445 MW rests on **2007** geometry.
They are not contemporaneous. The gap attributed to methodology differences — NREL covering more
building uses but applying shading, azimuth and tilt screens — is partly just nineteen years of
construction, including an Amazon distribution centre that almost certainly postdates the survey.

The comparison remains worth recording, but it **cannot distinguish "our method is sound" from
"our method is wrong and the vintage gap masks it."**

### The pattern across all sources

| source | vintage |
|---|---|
| NREL Virginia LiDAR | **2007** (79%), 2013 |
| NVRC rooftop sample (all county density rates) | ~2016 |
| Fairfax parking | 2007 / 2009 / 2017 / 2023 mixed |
| Arlington parking | single sync timestamp; real vintage undeterminable |
| Loudoun parking | 96%+ updated 2022 or later |
| Richmond surfaces | 2023–2026 |
| Chesapeake buildings | undetermined |

**Every figure understates by whatever was built after its own vintage, and the vintages span
nineteen years.** Because the direction is consistent, the aggregate is a floor — which is the
useful property. But **relative comparisons between jurisdictions carry a vintage artifact that
could easily be mistaken for a real difference in development pattern.** Loudoun's 2022+ parking
data and Chesapeake's 2007-based NREL benchmark are not on the same footing, and neither is
Fairfax's four-vintage mixture.

### Consequence for the whitepaper

Distributed figures should be presented as **floors with stated vintages**, not as current
capability, and cross-jurisdiction comparison should be avoided or explicitly caveated. This sits
alongside the §12 shading limitation: both push the same direction, and together they mean the
distributed resource is understated by an amount this analysis cannot quantify.

### Decision, 2026-09-11

Further per-jurisdiction data collection is **discontinued**. Eight jurisdictions were examined;
four publish parking geometry; the vintage spread undermines cross-comparison even where data
exists; and the effort was consuming disproportionate time for diminishing returns. The
distributed resource is carried as a documented floor, and scenario weighting moves to a stated
allocation assumption rather than a bottom-up siting build — see the agrivoltaic basis adopted for
Scenario 3.
