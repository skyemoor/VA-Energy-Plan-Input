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
