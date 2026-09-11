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
| **Forage, hay, haylage** | 1,117,726–1,440,010 | **JDS 2026: biomass down under heavy shade, but CP, fiber digestibility and minerals maintained or improved**; Illinois plot | **strong — quality offsets tonnage** |
| **Pasture / grazing** | 1,915,266 | **OSU: lamb growth 120 vs 119 g/hd/d (P=0.90) at +22% stocking**; ASGA 2024 ~113k sheep, 500+ sites; UMinn dairy | **strongest — measured animal performance** |
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

## 6B. Statutory framing (added 2026-09-11)

### The definition, and where it applies

**Va. Code § 10.1-1197.5** — six clauses. Agrivoltaics means intentional co-location of
agricultural production and solar generation on the same land that:

| | |
|---|---|
| (i) | is designed to **prioritize and sustain agricultural productivity** while integrating renewable energy |
| (ii) | allows ongoing production and sale of **marketable agricultural products throughout the array's life** |
| (iii) | is part of a **farm business consistent with commercial agricultural production** |
| (iv) | has **decommissioning provisions** protecting agricultural resources and productivity |
| (v) | **does not significantly displace farming activity** |
| (vi) | ensures **flexibility for farmers** to adapt to market conditions and support operational needs |

Added 2026 (cc. 156 HB508, 157 SB340, 901 SB645) — **recent, with no interpretive practice yet**.

**Correction:** earlier drafts of this analysis cited **§ 45.2-1706.1** for this definition. That
section is the Commonwealth Clean Energy Policy and **contains no agrivoltaic definition at all**.

**Scope:** the definition opens *"As used in this article"* (Article 5, Small Renewable Energy
Projects, ≤150 MW solar, DEQ permit by rule) — **but it is not confined there in practice**.
§ 15.2-2288.8(A)(3) imports it by reference into Title 15.2 zoning, which reaches **any
ground-mounted solar project of 1 MW or more**.

### § 15.2-2288.8 uses agrivoltaics permissively, in two places

**(A)(3) — enabling, not restricting.** Panel height is capped at 25 ft at full tilt *"except in
cases where a height variance is necessary to allow for agrivoltaics activity below or in proximity
to the panels."* Agrivoltaics is grounds to **exceed** a limit. A standard-height array never
invokes the clause.

**(A)(9) — grazing is treated as ordinary.** An ordinance may require *up to 75% vegetative cover*
maintained for the project's life. *"For projects or portions of projects **not used for animal
grazing, co-located crop production**, native and naturalized pollinator plant species... shall be
planted."* Grazing and crops sit in the same list as pollinator plantings, with **no additional
design condition**.

Two consequences: vegetation management is **mandatory regardless**, so grazing adds no burden that
was not already required; and the statute plainly contemplates livestock or crops under an
otherwise conventional array.

### The clause (i) concern, downgraded

An earlier draft argued standard-density single-axis tracking might fail clause (i) because such
arrays are *designed to prioritize energy yield*.

**That reading is weaker than the alternative.** The relevant counterfactual is not an idealised
agrivoltaic design — it is **conventional solar development, which removes the land from
agriculture entirely**. Against that, a configuration keeping land in production *does* prioritize
and sustain agricultural productivity. Clause (v) reads the same way, and § 15.2-2288.8(A)(9)
supports it.

Neither reading is authoritative. The statute quantifies neither *"prioritize"* nor *"significantly
displace"*, and there is no permitting practice yet. But the earlier framing **overstated the
risk** and should not be repeated as settled.

### Scale note

At 4–6 acres/MW a project at the 150 MW ceiling occupies **600–900 acres** against Virginia's
**187-acre average farm** (VDACS / 2022 Census) — roughly **3 to 5 farms**. Projects at that cap
are typically **multi-landowner aggregations**, which bears on clause (iii) *"part of a farm
business"* and clause (vi) *"flexibility for farmers"*: both read naturally for one farm, less
obviously for four.

Size distribution around the mean is not held; the Census reports 1,367 farms of 1,000+ acres out
of 38,995 (≈3.5%).

---

## 6C. Grazing and forage — measured animal performance

Added 2026-09-11. Pasture and forage are **3.03–3.36M Virginia acres**, the largest compatible
category. Prior evidence was an industry census and one dairy observation; these are measurements.

### Lamb growth and stocking (Andrew, OSU, 2020)

| | under panels | open pasture | |
|---|---:|---:|---|
| Lamb growth | **120 g/hd/d** | 119 g/hd/d | P = 0.90 |
| Stocking density | **36.6 lambs/ha** | 30 lambs/ha | **+22%** |
| Liveweight production | 1.5 kg/ha/d | 1.3 kg/ha/d | P = 0.67 |

**Parity is not the finding.** The panelled pasture **carried 22% more animals at equal per-animal
performance** — it did not merely fail to harm the flock, it supported higher carrying capacity.

Drought-relevant observations: *"some aspects were more favorable in the fully solar treatments,
including water consumption in late spring 2019, the ability to maintain a higher stocking rate
towards summer, and increased herbage yields in July of 2019."* Lower water use, better late-season
carrying capacity, higher mid-summer herbage — precisely when unshaded pasture fails.

### Forage quality (Florentino et al., *JDS Communications* 2026)

Biomass **is** lowest under the most-shaded (50 kW) array. But crude protein is **higher**,
total-tract fiber digestibility **higher**, mineral content maintained. Nutritive value *"maintained
or improved"*. The authors conclude shading can produce high-quality forage *"potentially offsetting
lower biomass yields through increased nutritional content."*

**This is a methodological point, not just a result.** Every other crop study reviewed measures
biomass or grain. For forage the relevant output is **animal product**, and a shaded sward with
higher protein and digestibility converts better per kilogram. Reporting the biomass decline alone
would understate the agricultural outcome.

### Limits

Corvallis is Mediterranean (dry summer, wet winter), not humid subtropical. The Florentino arrays
are 30–50 kW, not utility-scale tracking geometry. The lamb study covers two spring seasons.
**Neither is a Virginia trial.**

## 7. Open items

1. **An agrivoltaic-specific acres/MW figure.** 4–6 acres/MW is standard single-axis tracking.
   Every acreage figure here is a **lower bound** until this is resolved. *Second-highest priority.*
2. **Does standard-density tracking satisfy § 10.1-1197.5?** **Risk downgraded 2026-09-11.** An
   earlier draft argued clause (i) — *"designed to prioritize and sustain agricultural
   productivity"* — might exclude conventional arrays. That reading is weaker than the
   alternative: the relevant counterfactual is not an idealised agrivoltaic design but
   **conventional solar development, which removes the land from agriculture entirely**. Against
   that, a configuration keeping land in production *does* prioritize agricultural productivity.

   **§ 15.2-2288.8 supports the permissive reading in two places.** (A)(3) uses the definition as
   an **enabling** provision — agrivoltaics is grounds for a height *variance* above the 25 ft cap,
   not a design standard imposed on projects that don't need one. (A)(9) lists *"animal grazing,
   co-located crop production"* as ordinary alternatives to pollinator or meadow plantings, with no
   additional design condition — and requires up to 75% vegetative cover regardless, so vegetation
   management is mandatory whether or not anything grazes.

   (A)(3) also shows the definition is **not article-limited in practice**: Title 15.2 zoning
   imports it by reference, covering any ground-mounted project ≥1 MW.

   Still unresolved, but no longer the most consequential question. Full notes:
   `docs/statutes/15.2-2288.8.md`.

3. **Vegetable and speciality crop acreage** — Census Table 36.
4. **Tobacco lease multiple** — the one crop where the economics may invert.
5. **Humid-subtropical transfer — partly inverted 2026-09-11.** An earlier version of this item
   assumed Virginia growing seasons are reliably humid, so moisture retention under panels might
   raise disease pressure rather than help. **Virginia has had drought issues in each of the last
   five years.** The established mechanism — arrays "decrease air and soil temperature and increase
   soil moisture" (Marrou et al.), favourable "especially in drought years" (Amaducci et al.) — is
   therefore a **benefit** in Virginia too, and lands hardest on pasture and forage, which have no
   irrigation to fall back on. The disease-pressure concern remains real for wet seasons; the two
   now cut in opposite directions depending on the year, which is itself an argument for a
   resource whose value rises when conditions are worst.

   **Owed:** the five-drought-year premise is currently **asserted, not sourced**. The US Drought
   Monitor (NDMC / University of Nebraska-Lincoln, with USDA, NOAA, NASA) publishes Virginia
   history — *Weeks in Drought*, the *DSCI time series*, or *Comprehensive Statistics* CSV. The
   current-map page renders its table via JavaScript and could not be read programmatically. An
   inverted caution resting on an unsourced premise is weaker than the caution it replaced, so this
   should be pulled before the drought argument appears in the paper.
6. **Multi-year results.** CSU is establishment-year only; Purdue is a single season.
7. **Crop albedo as an energy variable** — unrepresented.
8. **Ray tracing required** for any array-level yield modelling; view-factor methods assume
   uniformly distributed vegetation.

---

## 8. Citations

### Field trials and modelling

**Andrew, A.C.** (2020). "Lamb growth and pasture production in agrivoltaic production system."
Oregon State University Honors College thesis, advisor Serkan Ates. Corvallis, spring 2019–2020.
→ Lamb growth 120 vs 119 g/head/day (P=0.90); stocking 36.6 vs 30 lambs/ha; liveweight 1.5 vs
1.3 kg/ha/day (P=0.67); lower water consumption, better late-season stocking, higher July herbage.

**Florentino, A. et al.** (2026). "Agrivoltaic arrays and effects on forage biomass."
*JDS Communications* 7:112–118. DOI 10.3168/jdsc.2025-0973.
→ Biomass lowest under the most-shaded (50 kW) array; crude protein, total-tract fiber
digestibility and mineral content maintained or improved; quality may offset tonnage.

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

**VDACS.** Agriculture Facts and Figures. → Average Virginia farm 187 acres; 2022 Census
derivatives.

**USDA Farm Service Agency.** Crop Acreage Data, 2026 Virginia rows, August 2026 release, via FOIA
electronic reading room.
→ 121 crops, 98 counties, county-level planted acres by crop, type, intended use, irrigation.

### Statute

**Va. Code § 58.1-2636** — Revenue share for solar energy projects and energy storage systems.
→ $1,400/MW AC on generation *and separately* on storage; 10% escalation every five years from
1 July 2026; 5 MW and net-metered exemptions.

**Va. Code § 58.1-3239** — State Land Evaluation Advisory Council; use-value assessment.

**Va. Code § 15.2-2288.8** — Special exceptions for solar photovoltaic projects. Amended 2026,
cc. 1005 (SB347), 1068 (HB711). Applies to ground-mounted solar ≥1 MW.
→ (A)(3) imports the § 10.1-1197.5 definition and makes agrivoltaics grounds for a height variance;
(A)(9) lists animal grazing and co-located crop production alongside pollinator plantings, and
requires up to 75% vegetative cover. Full text in `docs/statutes/15.2-2288.8.md`.

**Va. Code § 10.1-1197.5** — Definitions, Article 5 (Small Renewable Energy Projects).
→ The agrivoltaics definition, six clauses. Amended 2026, cc. 156, 157, 901 — recent. Full text in
`docs/statutes/10.1-1197.5.md`.

**Va. Code § 45.2-1706.1** — Commonwealth Clean Energy Policy. **Contains NO agrivoltaic
definition**; earlier drafts of this analysis cited it for one in error.

### Drought

**US Drought Monitor** — National Drought Mitigation Center, University of Nebraska-Lincoln, with
USDA, NOAA and NASA. droughtmonitor.unl.edu.
→ **Not yet pulled.** The current-map page renders its statistics table via JavaScript. Virginia
2021–2026 history is available via *Weeks in Drought*, the *DSCI time series*, or *Comprehensive
Statistics* CSV. **The five-drought-year premise is asserted until this is sourced.**

### Grazing and livestock

**Andrew, A.C.** (2020) — see Field trials above.

**Florentino, A. et al.** (2026) — see Field trials above.

**American Solar Grazing Association**, 2024 Census. ~113,000 sheep across 500+ US solar sites.

**University of Minnesota** research dairy. *AIP Conference Proceedings* (2022). Cattle grazed
under elevated array since 2020; shade improved comfort during heat events with associated
milk-production benefit.

**Cornell University & The Nature Conservancy**, 2026 study on barriers to scaling cattle
agrivoltaics. *In progress.*

### Cover crops

See `Cover_Crops_and_Agrivoltaics.md` §8 for SARE, University of Georgia and Virginia DCR
citations.
