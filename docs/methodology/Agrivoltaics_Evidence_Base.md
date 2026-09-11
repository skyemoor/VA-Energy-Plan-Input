# Agrivoltaics: Evidence Base and Findings

**Working note, 2026-09-11.** Consolidates findings from `lp_package/agrivoltaic_basis.py` and
§6A–6D of `NSPM_Rural_Economic_Development.md`. Complements the earlier
`docs/appendices/Appendix_Agrivoltaics.md`, which covers statutory definition, regional practice
and vertical bifacial design in more narrative form.

Companion note: `Cover_Crops_and_Agrivoltaics.md`.

---

## 1. The basis adopted

**85% of total solar capacity** sited agrivoltaically under utility or PPA ownership. At the 2045
Build to Zero solar build of ~173,781 MW that is **147,714 MW agrivoltaic**.

This is a **stated allocation assumption**, not a bottom-up siting result — see
`share_is_assumed()`. NREL counts 13 existing agrivoltaic projects in Virginia, so present-day
practice is far below it.

It supersedes, for allocation purposes, the nested formulation in `scenario3_build.py` (90% of an
80% utility share = 72% of total). The two differ by 13 points on every derived figure.

---

## 2. The economic foundation, and why yield is secondary

**Virginia Tech / SLEAC** — the statutory basis for agricultural use-value assessment under
**Va. Code § 58.1-3239**. These are the figures Virginia's own tax system runs on.

| crop | net return $/acre/yr | lease is |
|---|---:|---:|
| Soybeans | $197.83 | 6–13× |
| Alfalfa | $98.73 | 12–25× |
| Corn | $76.27 | 16–33× |
| Pasture | $3.69 | 325–678× |
| Hay | $0.32 | 3,750–7,812× |
| **Composite farm** | **$17.69** | **68–141×** |

Against Virginia lease rates of **$1,200–2,500/acre/yr** (national average $500–700).

**This reframes everything downstream.** A farmer could lose the entire crop and remain far ahead.
The agrivoltaic case therefore does not depend on the contested crop-yield evidence — what
agrivoltaics adds is the *option to keep farming*, with the food-production and land-preservation
benefits that follow.

**The variance argument, in SLEAC's own data.** Prince Edward corn by year: +$156.45, **−$52.39**,
**−$65.55**, +$27.09, +$38.28, **−$112.44**, **−$65.47**. Four of seven years negative — and the
methodology *floors negatives at zero* before averaging, so the published $76.27 is generous
relative to what the farmer lived through. A contracted lease is a hedge, not a supplement.

*Caveats:* Prince Edward is the publication's worked example, not a Virginia average — across
jurisdictions net returns run **$20–88/acre**, still 14–28× behind. Use-value is **not** annual net
return. Livestock is excluded from use-value entirely.

---

## 3. Where the acreage lands

**Virginia land in farms, 2022 Census of Agriculture:** 38,995 farms, **7,309,687 acres** —
cropland 2,884,293; pastureland 1,915,266; woodland 2,053,786; other 456,342.

The agrivoltaic requirement of **605,626–921,733 acres** reads very differently by denominator:

| base | share |
|---|---:|
| All land in farms | 8.3–12.6% |
| **Cropland alone** | **21.0–32.0%** |
| Pasture + forage | **18–27%** |

**The cropland figure is what an opponent reaches for** and must be stated, not hidden behind the
flattering denominator.

### Two independent sources agree the requirement fits within forage

| source | forage base | share |
|---|---:|---:|
| Census (pasture + hay/haylage 1,117,726) | 3,032,992 | 20.0–30.4% |
| FSA 2026 (pasture + forage 1,440,010) | 3,355,276 | **18–27%** |

**USDA FSA 2026** is the better source: 4,384 records, 98 counties, **121 crops**, county
resolution, annual, with intended use recorded.

| rank | crop | planted acres | % |
|---:|---|---:|---:|
| 1 | **MIXED FORAGE** | **1,373,771** | 45.6% |
| 2 | Soybeans | 584,642 | 19.4% |
| 3 | Corn | 418,778 | 13.9% |
| 4 | Cover crop | 302,940 | 10.1% |
| 5 | Wheat | 73,643 | 2.4% |
| 6 | Cotton, upland | 73,417 | 2.4% |
| 7 | Grass | 45,947 | 1.5% |
| 8 | Peanuts | 29,526 | 1.0% |
| 9–15 | Rye, barley, tobacco, sorghum, triticale, sorghum forage, alfalfa | 79,388 | 2.6% |

**Mixed forage is the largest crop in Virginia — larger than soybeans and corn combined.** Forage
exceeds the weak-evidence row crops by **2.6×**, so the compatible base has margin.

*Caution:* FSA counts **planted** acres and therefore double-counts double-cropped land (see the
cover crop note). It excludes pastureland entirely. FSA forage **can** be combined with Census
pasture — they are disjoint. FSA planted acres **cannot** be summed with Census cropland.

---

## 4. Configuration: the question is crop-specific

**Riaz et al.'s Light Productivity Factor** measures how effectively an array shares irradiance
between panels and crop *for a given crop*. LPF = 1 for PV-only or crop-only; agrivoltaic systems
score 1–2.

| crop type | indicated configuration |
|---|---|
| **Shade-tolerant** | **single-axis tracking — LPF maximised at 2** |
| **Shade-sensitive** | **east/west vertical bifacial** — smallest seasonal variability |

### This resolves the corn evidence

| study | configuration | result |
|---|---|---|
| **Purdue** (farm-scale, validated model) | east–west tracking | **7.1% reduction** — 10,182 vs 10,955 kg/ha |
| **Colorado State** (plot, establishment year) | vertical bifacial N–S | **no significant difference** (p > 0.05) |

Corn is shade-sensitive. These are the expected outcomes of the right and the less-right
configuration — **not contradictory results**.

**Why the Purdue study carries more weight:** farm-scale rather than plot; APSIM calibrated on the
*unshaded* control then validated against the shaded region within ~1%; and it establishes the
mechanism — **yield is governed by spatiotemporal shadow distribution, not total radiation**. Two
configurations delivering identical total light give different yields depending on *when* the
shadow falls. That is why results do not transfer between mounting types.

### Purdue design findings

- **Tracker height is a weak lever** — yield is *"a weak function of tracker height up to 2.44 m"*
- **Row spacing stops helping at 9.1 m** at constant total power, materially tighter than the
  11.3–13.7 m modelled for vertical bifacial
- **Anti-tracking is a poor trade** — 5.6% yield gain against *"a substantial decline in solar
  power"*

### The operational constraint no other source raised

East/west vertical arrays offer *"ease of movement of large-scale combine-harvester and other
farming equipment."* **Machinery access likely binds before light does** for row crops — a farmer
who cannot run a combine through the array cannot farm it at any yield.

### Bifacial synergy

Bifacial gain *"depends mainly on the ground albedo and the distance between rows. The smaller the
distance between the module rows, the lower the BG."* Agrivoltaics needs wide spacing; wide spacing
raises bifacial gain. **The spacing penalty is partly repaid in per-module yield** — this narrows
the land gap without closing it.

**Crop albedo is therefore an energy variable**, not just agronomic. Not represented in this
analysis.

---

## 5. SLCOE — the comparison that matters

Since yield protection is largely moot (§2), configuration should be optimised for **SLCOE**.

**The finding is not a compromise:** LPF is maximised for shade-tolerant crops under single-axis
tracking — which is *also* the conventional, lowest-cost utility configuration. Virginia's
compatible base **is** the shade-tolerant group.

> **On forage land, the highest-LPF configuration and the cheapest configuration are the same
> configuration.**

| configuration | SLCOE delta vs conventional |
|---|---:|
| **Standard tracking on forage** | **~$0.00/MWh** |
| East/west vertical bifacial | +$4.40/MWh (**+3.3%**) |
| Elevated tilted | **+88% LCOE** on solar |

**Land is the only channel** by which agrivoltaic intensity reaches SLCOE — hardware cost is
unchanged by siting. At 5 acres/MW and $1,850/acre/yr, land is $4.40/MWh.

**What this supports:** agrivoltaic siting is usually assumed to carry a cost penalty making it a
nice-to-have. On shade-tolerant forage it does not — the rural benefits come at **no generation
cost**. That is materially different from *"worth paying a little more for."*

*Limits:* assumes shade-tolerant forage, standard-density tracking, and grazing access within
normal O&M. Does **not** hold for row crops, elevated racking, or where machinery access forces
vertical.

---

## 6. Crops examined, and crops not yet examined

### Examined

| crop / group | VA acres | evidence | verdict |
|---|---:|---|---|
| **Forage, hay, haylage** | 1,117,726–1,440,010 | Illinois research plot: switchgrass, orchardgrass | **strong** |
| **Pasture / grazing** | 1,915,266 | ASGA 2024: ~113k sheep, 500+ US sites; UMinn dairy | **strongest practice** |
| **Corn** | 384,337–418,778 | Purdue farm-scale; CSU vertical; Sekiyama 2019 | **configuration-dependent** |
| **Winter wheat** | 73,643–165,415 | German trial: −19% to +3%, **+2.7% in a hot dry summer** | **strong for a field crop** |
| Soybeans | 584,642–610,605 | thin | weak |
| Cover crops | 302,940 | inferred from species overlap | see companion note |

### Not yet examined — and several matter

| crop | VA acres | why it matters |
|---|---:|---|
| **Cotton, upland** | 73,417–91,073 | sixth-largest crop; no agrivoltaic evidence reviewed |
| **Peanuts** | 29,526 | Virginia speciality; legume, possibly shade-tolerant |
| **Tobacco, flue-cured** | 12,643 | high value/acre — lease multiple much lower here |
| **Barley, rye, triticale** | 40,625 | small grains; wheat evidence may transfer |
| **Sorghum** | 11,188 | C4 like corn; sorghum-sudangrass already in forage group |
| **Vegetables, melons, potatoes** | not published | **strongest evidence in the entire literature** — tomatoes and peppers good-to-improved across four studies; Eastern Shore tomato industry |
| **Fruits, tree nuts, berries** | not published | orchards: different geometry entirely; VT use-value shows orchards already loss-making |
| **Nursery, greenhouse, sod** | not published | $398.6M sales — second-largest crop category by value |

**The vegetable gap is the most notable.** It has the best yield evidence of any crop group, sits
in Virginia's Eastern Shore industry, and its acreage is not published in the sources used so far.
Worth pulling from Census Table 36 (Vegetables, Potatoes and Melons Harvested for Sale).

**The tobacco case is the inverse.** At high value per acre the 68–141× lease multiple collapses —
possibly below 1×. It is the one Virginia crop where the economic argument may not hold, and that
should be checked rather than assumed away.

---

## 7. Open items

1. **An agrivoltaic-specific acres/MW figure.** 4–6 acres/MW is standard single-axis tracking.
   Every acreage figure here is a **lower bound** until this is resolved. *Second-highest priority.*
2. **Does standard-density tracking satisfy § 10.1-1197.5 clause (i)?** The statute requires a
   design that *"prioritize[s] and sustain[s] agricultural productivity"*; standard-density
   single-axis tracking is designed to prioritize energy yield. Clause (v), *"does not
   significantly displace farming activity"*, is the second test. A conventional array with sheep
   beneath it plausibly satisfies (ii), (iii), (iv) and (vi). **Most consequential single
   question** — if the answer is no, the land term rises and the ~zero SLCOE delta with it.

   Two qualifiers found 2026-09-11: the definition is **article-limited** ("As used in this
   article" — DEQ permit by rule), so it may not bind outside that context; and a "small renewable
   energy project" is capped at **150 MW**, so whether it applies depends on individual project
   sizing rather than programme total.
3. **Vegetable and speciality crop acreage** — Census Table 36.
4. **Tobacco lease multiple** — the one crop where the economics may invert.
5. **Humid-subtropical transfer.** All corn evidence is from Indiana (humid continental) and
   northern Colorado (semi-arid). Virginia is humid subtropical — reduced airflow under panels may
   raise disease pressure in ways neither site would show.
6. **Multi-year results.** CSU is establishment-year only; Purdue is a single season.
7. **Crop albedo as an energy variable** — unrepresented.
8. **Ray tracing required** for any array-level yield modelling; view-factor methods assume
   uniformly distributed vegetation.

---

## 8. Citations

### Field trials and modelling

**Gupta, V., Gruss, S.M., Cammarano, D., … Tuinstra, M.R., Gitau, M.W., Agrawal, R.** (2024).
"Optimizing corn agrivoltaic farming through farm-scale experimentation and modeling."
*Cell Reports Sustainability* 1, 100148. DOI 10.1016/j.crsus.2024.100148. Open access.
→ Farm-scale corn, east–west tracking; APSIM validated; SSD mechanism; 9.1 m spacing; tracker
height; anti-tracking.

**AgriVoltaics Conference Proceedings** (Colorado State University). "Impacts of a Vertical
Bifacial Agrivoltaics System on Field Corn in Northern Colorado, USA: Performance of Silage Corn in
the Establishment Year." eISSN 2751-6172.
→ Vertical bifacial N–S, no significant yield difference, p > 0.05.

**Sekiyama, T. & Nagashima, A.** (2019). "Solar sharing for both food and clean energy production:
Performance of agrivoltaic systems for corn, a typical shade-intolerant crop." *Environments* 6(6),
65. **Cited but not read — findings not yet incorporated.**

### Configuration and optimisation

**Riaz, M.H., Imran, H., Alam, H., Alam, M.A. & Butt, N.Z.** (2022). "Crop-Specific Optimization of
Bifacial PV Arrays for Agrivoltaic Food-Energy Production: The Light-Productivity-Factor Approach."
*IEEE Journal of Photovoltaics* 12(2), 572–580. DOI 10.1109/JPHOTOV.2021.3136158.
→ LPF metric; shade-tolerant → tracking (LPF 2); shade-sensitive → E/W vertical; combine access.

**Mouhib, E., Micheli, L., Almonacid, F.M. & Fernández, E.F.** (2022). "Overview of the
Fundamentals and Applications of Bifacial Photovoltaic Technology: Agrivoltaics and Aquavoltaics."
*Energies* 15(23), 8777. DOI 10.3390/en15238777. Open access.
→ Bifacial gain vs row spacing and albedo; ray-tracing requirement; market share forecast.

**Jordan pilot, Amman** — comparative tilted vs vertical east–west bifacial, first operational year.
DOI 10.3390/su18020931.
→ 1,962 vs 1,288 kWh/kWp; elevated tilted +88% LCOE; vertical no LCOE premium.

**University of Turku** — "Performance evaluation of high latitude agrivoltaic systems with
vertically mounted bifacial panels." *Applied Energy*. Via pv-magazine, 13 Nov 2025.
→ 11.3–13.7 m row spacing for 90% agricultural yield; crop type influences albedo. **Computational,
not experimental.**

### Virginia economic and land data

**Friedel, J.S. & Kayser, P.H.** Virginia Tech / SLEAC. "Methods and Procedures: Determining the
Use Value of Agricultural and Horticultural Land in Virginia." VCE publication **446-011
(AAEC-215P)**, last reviewed August 2025. Statutory basis under Va. Code § 58.1-3239.
→ Net returns per acre; composite farm; olympic averaging; negative-year flooring.

**USDA NASS.** 2022 Census of Agriculture, Virginia State Profile (cp99051).
→ Land in farms by use; top crops in acres; crop sales by category; livestock inventory.

**USDA Farm Service Agency.** Crop Acreage Data, 2026 Virginia rows, August 2026 release, via FOIA
electronic reading room.
→ 121 crops, 98 counties, county-level planted acres by crop, type, intended use, irrigation.

### Statute

**Va. Code § 58.1-2636** — Revenue share for solar energy projects and energy storage systems.
→ $1,400/MW AC on generation *and separately* on storage; 10% escalation every five years from
1 July 2026; 5 MW and net-metered exemptions.

**Va. Code § 58.1-3239** — State Land Evaluation Advisory Council; use-value assessment.

**Va. Code § 10.1-1197.5** — Definitions, Article 5 (Small Renewable Energy Projects).
→ The agrivoltaics definition, six clauses. Amended 2026, cc. 156, 157, 901 — recent. Full text in
`docs/statutes/10.1-1197.5.md`.

**Va. Code § 45.2-1706.1** — Commonwealth Clean Energy Policy. **Contains NO agrivoltaic
definition**; earlier drafts of this analysis cited it for one in error.

### Grazing and livestock

**American Solar Grazing Association**, 2024 Census. ~113,000 sheep across 500+ US solar sites.

**University of Minnesota** research dairy. *AIP Conference Proceedings* (2022). Cattle grazed
under elevated array since 2020; shade improved comfort during heat events with associated
milk-production benefit.

**Cornell University & The Nature Conservancy**, 2026 study on barriers to scaling cattle
agrivoltaics. *In progress.*

### Cover crops

See `Cover_Crops_and_Agrivoltaics.md` §8 for SARE, University of Georgia and Virginia DCR
citations.
