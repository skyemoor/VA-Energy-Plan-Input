# Cover Crops and Agrivoltaics

**Working note, 2026-09-11.** Consolidates findings currently scattered across
`lp_package/agrivoltaic_basis.py` inline comments and §6A–6B of
`NSPM_Rural_Economic_Development.md`.

---

## 1. Why this came up

USDA Farm Service Agency's 2026 Virginia crop acreage data lists **COVER CROP at 302,940 acres —
10.1% of all planted acreage**, the fourth-largest entry after mixed forage, soybeans and corn.

An early draft of this analysis excluded that acreage from the agrivoltaic-compatible base on two
grounds: that cover crops are *"not a cash crop"* and that cover cropping under panels is
*"unaddressed in the agrivoltaic literature reviewed."*

**Both were wrong.** The first misunderstands how the acreage is counted; the second understates
the compatibility. Neither error changed a published quantity, but both would have led somewhere
wrong if carried forward.

---

## 2. Correction 1 — the acreage is double-counted, not additional

Cover crops are planted **between** cash crops on the **same ground** — to fix nitrogen, suppress
weeds, prevent erosion, or carry a fallow year against soil exhaustion. FSA's 3,014,135 "planted
acres" therefore **counts some land twice**, and is not a unique-area figure.

**The arithmetic shows it:**

| | acres |
|---|---:|
| FSA planted acres, 2026 | 3,014,135 |
| Census cropland, 2022 | 2,884,293 |
| FSA less cover crop | **2,711,195** — *now below the cropland base* |

FSA exceeds Census cropland; removing cover crop puts it below. That is the signature of
double-cropping, not of additional land.

### Three independent confirmations

| source | wording |
|---|---|
| **Virginia Tech / SLEAC** | winter annuals are *"always followed by a summer crop"*; double-crop acreage is subtracted explicitly to avoid this exact error |
| **University of Georgia** | cover crop choice depends on *"your planting window (the time between cash crops)"* |
| **Virginia DCR** | cover crops are *"non-cash crops planted between primary crops"* |

Virginia's own land-assessment methodology, a land-grant extension service, and Virginia's own
conservation agency all describe the same mechanic.

### What this does and does not affect

**Affected:** the "47.8% of planted acreage" forage share is computed against a double-counted
denominator and is now qualified wherever it appears.

**Not affected:** the compatible-base finding, which rests on FSA forage plus **Census**
pastureland — neither of which is a planted-acres percentage.

---

## 3. Correction 2 — cover crops are *more* agrivoltaic-compatible than cash crops, not less

### They are harvestable as forage

SARE's *Managing Cover Crops Profitably* (3rd ed.) states directly:

> *"Many cover crops offer harvest possibilities as forage, grazing or seed that work well in
> systems with multiple crop enterprises and livestock."*

Its own illustration caption notes winter wheat as a cover *"grows well in fall, then provides
forage and protects soil over winter."*

### The species are largely the forage species already counted

UGA's regionally-appropriate list:

| season | species |
|---|---|
| **Fall/winter** | cereal rye, oats, annual ryegrass, triticale, wheat; crimson, balansa and other clovers; hairy and common vetch; Austrian winter peas; blue and white lupin; daikon radish and other brassicas |
| **Spring/summer** | sorghum, sorghum-sudangrass, pearl and browntop millet, Japanese millet; cowpeas, sunn hemp, velvetbean; buckwheat, sunflower |

**Sorghum-sudangrass and millet appear in both this list and the FSA forage group already counted
as strong-evidence.** The categories overlap in the data, not merely in agronomy — which is why the
compatibility conclusion transfers rather than being asserted.

### Three reasons the fit is better than for a cash crop

1. **The objective is soil health and nitrogen fixation, not yield.** UGA: cover crops are
   *"planted primarily for their agro-ecosystem benefits rather than for harvest."* A shading
   penalty that would disqualify corn is largely immaterial when yield is not the goal.
2. **Solar sites require vegetation management regardless.** A cover crop serves that purpose *and*
   delivers its agronomic benefits — one operation, two outcomes.
3. **The opportunity cost is near zero.** During a cover or fallow period the land is already
   earning no cash-crop income, so hosting an array in that window costs the farmer nothing in
   foregone production.

---

## 4. Two cover crop purposes an array actively improves

UGA's list of why farmers plant cover crops includes two entries that a solar array **helps** rather
than hinders:

**"To extend the grazing season."** Panel shade reduces heat stress on both sward and livestock —
the mechanism behind the University of Minnesota research dairy finding that shade improved cattle
comfort during heat events with an associated milk-production benefit. A cover crop planted for
grazing extension *under* an array compounds two effects aimed at the same outcome.

**"To provide habitat and nectar for beneficial insects."** Virginia DCR concurs: cover crops
*"enhance biodiversity by providing a habitat for beneficial insects and pollinators."*

Pollinator habitat sits in this project's NSPM channel table as **identified but unquantified**.
Cover cropping under panels reaches it with **no additional land and no separate program**, because
the planting is happening anyway.

---

## 5. Virginia policy already attaches — two existing mechanisms

Source: Virginia DCR, *"Cover crops: a win for farmers and the environment"* (September 2024),
originally published through Virginia State University's Small Farm Outreach Program.

### VACS already cost-shares the practice

The **Virginia Agricultural Best Management Practices Cost-Share Program**, administered by DCR and
delivered through local Soil and Water Conservation Districts, *"can decrease the cost of planting
cover crops on your farm"* and covers *"over 70 other conservation practices."*

This is the same shape as the § 45.2-1702 energy performance contracting finding in §7A of the NSPM
note: **a funding mechanism that already exists**, requiring no new legislation and no new
appropriation. Cover cropping under an array is the same practice VACS already funds.

### Chesapeake Bay nutrient reduction — the highest-value unquantified channel

DCR states cover crops reduce *"nonpoint source pollution by slowing runoff and absorbing excess
nitrogen that otherwise would leach into the water table"* and can *"potentially reduce the need for
synthetic fertilizer."*

Virginia carries **binding nutrient-reduction obligations under the Chesapeake Bay TMDL**, and cover
crops are an established BMP against them.

**This differs in kind from the other unquantified channels.** Pollinator spillover and construction
employment are diffuse benefits. Bay nutrient reduction is a **quantified obligation the
Commonwealth is already required to meet at cost** — so an array whose vegetation management is a
cover crop delivers reduction on land that would otherwise need a separate BMP to achieve it. That
is a cost offset against a known liability.

Quantifying it requires Bay-model nutrient-reduction efficiencies per acre, which is out of scope
here. It is **channel 10** in the NSPM table and the highest-value addition remaining.

---

## 6. Equity dimension, recorded and undeveloped

The DCR piece ran through VSU's **Small Farm Outreach Program**, which serves *"small,
limited-resource, socially disadvantaged and veteran farmers and ranchers."*

The farms for which a contracted lease payment most changes the survival calculus are those least
able to absorb a bad year — the same population. Relevant to NSPM treatment of distributional
impacts, and not developed here.

---

## 7. What is *not* claimed

**Cover crop acreage is not added to the compatible base.** Because of §2 it overlaps land already
counted, so including it would double-count. It is recorded because it strengthens the
**qualitative** case — 302,940 acres of Virginia cropland are already being managed for soil health
rather than yield in any given year, on species that graze well — **without changing any quantity.**

A test asserts the exclusion reason is *double-counting*, not incompatibility, so that distinction
cannot be lost in a later edit and quietly become "cover crops don't work under panels."

**No cover-crop-specific agrivoltaic field trial was identified.** The compatibility argument here
is inferred from species overlap with forage crops that *do* have field evidence, plus the
shading-tolerance argument in §3. That is reasoning, not measurement, and should be presented as
such.

---

## 8. Sources

| | |
|---|---|
| SARE | *Managing Cover Crops Profitably*, 3rd ed., 2007 — benefits, forage/grazing harvest possibilities |
| University of Georgia | Sustainable Agriculture, Farm Management: Cover Crops — species lists, purposes, planting-window mechanic |
| Virginia DCR | *"Cover crops: a win for farmers and the environment"*, Sept 2024 — VACS, Bay nutrient reduction, Virginia framing |
| Virginia Tech / SLEAC | VCE 446-011 — double-crop acreage treatment |
| USDA FSA | 2026 Virginia crop acreage — the 302,940-acre figure |
