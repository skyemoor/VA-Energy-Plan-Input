# Data Sourcing Log

## Purpose
Detailed source material one level below what VA_SLCOE_Model.xlsx's "Assumptions & Sources" tab
captures. The XLSX tab holds the summary-level figure and a short citation pointer (e.g. "62
elementary, 17 middle, 13 high -- NCES federal database"); this log holds the full research
record behind that figure -- every source checked, exact wording found, discrepancies between
sources, and how (or whether) each was resolved. When the XLSX or a code module's own comment
says "see research notes" or similar, this is the file that means.

Log structure established 2026-08-27, per direct user instruction. Populated below by migrating
this session's own prior research (originally scattered across `xlsx_update/school_counts_raw.txt`
and inline code comments) into one organized place. The original raw file is left in place,
unmodified -- this log is the organized, authoritative version going forward.

---

## Topic: 11-locality school counts (elementary/middle/high), NoVA + Hampton Roads

Gathered to support Scenario 3's B.1/B.2 rooftop and parking-lot solar work, and the school
rooftop solar capacity/battery estimate (`school_rooftop_solar_analysis/`). Methodology across all
11: prefer each division's own official site; where that wasn't cleanly available, use the most
directly-sourced third-party figure found, and cross-validate against an independent source where
possible. Every discrepancy found is recorded below, not smoothed over.

### Arlington (Arlington Public Schools / APS)
- **Source**: apsva.us/about-aps/ (official, direct).
- **Figures**: 26 elementary, 6 middle, 9 "High Schools & Programs" (a mixed category -- not all
  are comprehensive high schools).
- **Cross-check note**: a dated (~2019) Wikipedia snapshot described Wakefield HS as "one of five"
  high schools in Arlington, suggesting ~5 true comprehensive high schools within the 9 counted --
  the rest being CTE/alternative (Arlington Career Center, Arlington Tech) or smaller/alternative
  programs (Langston, Shriver, Arlington Community HS). The full 9 was used in the final tally
  (not narrowed to ~5), since these are still real, roofed facilities; flagged so a reader can
  substitute ~5 if the narrower reading is preferred.

### Alexandria (Alexandria City Public Schools / ACPS)
- **Source**: acps.k12.va.us/about-us/fast-facts, "Fast Facts 2025-26" (official, direct, current
  year).
- **Figures**: 18 total schools. High: 1 (Alexandria City High School -- has 2 physical campuses,
  King St. + Minnie Howard, counted as one school/division entity). Middle: 2 (Francis C. Hammond,
  George Washington). K-8 (mixed category, doesn't fit cleanly): 2, including Jefferson-Houston
  PreK-8 IB. Pre-K: 1. "Academies at Alexandria City" (alt/CTE program): 1. Elementary is
  **derived, not directly stated**: 18 total - 2 middle - 2 K-8 - 1 Pre-K - 1 HS - 1 academies = 11.
- **Discrepancy flagged**: the City of Alexandria's own government source
  (alexandriava.gov/Schools) states "1 high school, 2 middle schools, 12 elementary schools, 1
  Pre-K (16 schools total)" -- a different total (16 vs. 18) and different categorization (no
  separate K-8 category, elementary count differs). ACPS's own "Fast Facts 2025-26" was used as
  primary, since it's the division's own, most current source.

### Fairfax County (Fairfax County Public Schools / FCPS)
- **Source**: fcps.edu/schools-centers, official filter facets (direct, precise -- verified
  against the page's own "Displaying 1-50 of 264 results" total).
- **Figures**: 142 elementary, 29 high, 23 middle. Edge cases: 6 "Secondary School" (likely 7-12
  or combined MS/HS), 28 "Alternative and Nontraditional School Programs," 8 "Special Education
  Schools," 28 "Administration Centers" (not schools at all). All-category total: 264, confirmed
  directly via the page's own result count.
- **Discrepancy noted**: third-party aggregators (US News, GreatSchools, Wikipedia) report "223
  schools" -- likely an older snapshot, or a different exclusion set (264-28-28-8=200 doesn't
  match either, so the exact reconciliation wasn't found). FCPS's own direct filter facets were
  used as primary, being the most current/authoritative source found. FCPS also opened "Skyview
  High School" per the division's own Aug 20, 2026 homepage news, which may not yet be reflected
  in some third-party counts -- consistent with FCPS's own count being the most current.

### Loudoun County (Loudoun County Public Schools / LCPS)
- **Source**: two independent third-party sources (Absolute Security case study, Idealist.org),
  both appearing to quote LCPS's own official language verbatim, consistently: "15 high schools,
  15 middle schools, 57 elementary schools, and three special purpose schools" -- serving "89
  facilities."
- **Figures**: 15 high, 15 middle, 57 elementary, 3 special purpose.
- **Sum check**: 15+15+57+3 = 90, vs. the stated "89 facilities" -- off by 1, within
  rounding/snapshot noise.
- **Flagged as likely slightly stale**: this breakdown's own totals (89-90 schools, ~78-79K
  students) are lower than Wikipedia's more recent citation (100 schools total, 81,486 students,
  2024-25). LCPS is fast-growing ("1-3 new school facilities opened each year" per its own
  language), so the per-type breakdown probably understates the current total somewhat. Best
  available breakdown found in the time budget for this locality; a more current official
  per-type count was not located.

### Prince William County (Prince William County Public Schools / PWCS) -- see also the dedicated
### correction section below
- **Original finding** (superseded, kept here for the record): potomaclocal.com (Jan 2025) gave
  62 elementary, 18 middle, 16 high. A more recent (Feb 2026) InsideNoVa article explicitly
  referenced "the current 13 high schools" while discussing whether to build a "14th" -- a real,
  unresolved discrepancy at the time (13 vs. 16 high schools). PWCS's own official schools
  directory (pwcs.edu/schools/index) was found to be JavaScript-rendered and did not yield precise
  filter-facet counts the way FCPS's did, making this locality's original breakdown less
  directly-sourced than Arlington's or Fairfax's.
- **Resolution**: see "PWCS correction" section below -- this was fully resolved in a later pass.

### Stafford County (Stafford County Public Schools / SCPS)
- **Source**: bitscale.ai + Wikipedia (consistent): base figures 17 elementary, 8 middle, 5 high
  (33 total).
- **Forward-looking figure, direct from Wikipedia**: "Elementary school 18, 19, and high school 6
  will open in August 2026" -- since the research date was Aug 27, 2026, these should already be
  open, implying current counts of ~19 elementary, 8 middle, ~6 high (34-35 total).
- **Discrepancy flagged**: GreatSchools gives a different count -- "19 Elementary, 10 Middle, 7
  High." The 19 elementary matches Wikipedia's post-opening figure, but 10 middle and 7 high don't
  match (Wikipedia implies 8 middle, 6 high). Not independently resolved -- reported as a real,
  open discrepancy. The Wikipedia-derived figures (19/8/6) were used as primary in the final tally.

### Richmond City (Richmond Public Schools / RPS)
- **Source**: RPS's own LinkedIn page (Nov 2025) + DonorsChoose, exact match: "25 elementary
  schools, including one charter school, seven middle schools, five comprehensive high schools and
  three specialty schools" -- ~24,000 students, 53 total school campuses per RPS's own current
  site.
- **Figures**: 25 elementary (incl. 1 charter), 7 middle, 5 high (comprehensive), 3 specialty
  (edge case).
- **Discrepancy flagged**: Wikipedia's "Education in Richmond" article gives a different,
  likely-stale figure (5 high, 9 middle, 28 elementary, 9 special-purpose/preschools) -- that
  article cites a 2009 source, suggesting an older snapshot. RPS's own current LinkedIn figure was
  used as primary.
- **Named-school detail** (for the 10-school solar project, see the solar-kW rationale topic
  below): of the 37 total RPS schools, only the 10 schools in the Secure Solar Futures/RVA Solar
  Fund project are confidently, individually named (Huguenot HS; Lucille M. Brown MS, Martin
  Luther King Jr. MS; Broad Rock ES, G.H. Reid ES, J.B. Fisher ES, J.H. Blackwell ES, M.J. Jones
  ES, Oak Grove ES, Linwood Holton ES). A longer partial name list was found in a separate RPS
  grant-announcement page, but it mixed in non-standard facilities (Franklin Military School, Open
  High School [alternative], Richmond Adult Technical Center) and was not reliably complete or
  cleanly categorized -- not treated as a trustworthy full name list for the remaining 27 schools.

### Hampton (Hampton City Schools)
- **Source**: hampton.k12.va.us/overview.html (official, direct).
- **Figures**: 1 Early Childhood Center. Elementary K-5: 18 (incl. 1 magnet, 2 fundamental, 1 arts
  school). PK-8 (edge case, mixed elem/middle): 2 (Andrews, Phenix). Middle: 5 (incl. 1
  fundamental, 1 magnet). High: 4 (each including specialized academies).
- **Cross-check performed and a real contradiction resolved**: the Kecoughtan HS Wikipedia article
  explicitly names all four high schools directly ("one of four high schools... the other three
  are Phoebus, Bethel, and Hampton"), resolving a direct contradiction with the separate "Hampton
  City Schools" Wikipedia article, which incorrectly states 5. Hampton's own site plus this
  cross-check both confirm 4 -- used as the reliable figure with high confidence.
- **Named-school detail**: 17 of the 18 elementary schools were found individually named (Aberdeen,
  Armstrong, Asbury, Barron, Bassette, Bryan, Burbank, Christian, Cooper, Forrest, Jackson, Kraft,
  Langley, Machen, Patrick, Peake, Phillips) -- the 18th was not confidently identified from
  available sources and was not guessed.

### Norfolk (Norfolk Public Schools / NPS)
- **Source**: NPS's own LinkedIn (primary) + NPS's own Wikipedia infobox (cross-check) + NPS's own
  current homepage -- all three agree independently on 5 high schools.
- **Figures**: Elementary 33 (LinkedIn) vs. 34 (Wikipedia infobox) -- close, minor variance, likely
  different snapshot dates or differing treatment of K-8/3-8 "choice" schools (Ghent School, Lake
  Taylor, Academy for Discovery at Lakewood). Middle: 7 (LinkedIn) vs. 9 (Wikipedia infobox) --
  same caveat. High: 5, confirmed independently by three separate NPS-linked sources -- highest
  confidence figure found for this locality.

### Virginia Beach (Virginia Beach City Public Schools / VBCPS)
- **Source**: virginiabeach.com named school list, counted directly rather than trusting a
  summary number, cross-validated against Princess Anne HS's own Wikipedia article.
- **Figures**: Elementary 55 (named, directly counted). Middle ~13 (12 named directly + 1
  truncated in the source, likely "Virginia Beach Middle" or similar -- not confidently completed).
  High: 11.
- **Cross-check performed**: Princess Anne HS's own Wikipedia article states directly "one of 11
  high schools" -- an exact match to the direct count, high confidence.
- **Note on division totals**: the division's own "About Us" page (vbschools.com) states a
  different current total (85 schools), consistent with this project's own existing cross-check
  figure of "87 schools" already on record (see the SCHOOL_STARTING_STOCK_2026 methodology note
  in `efficiency_assumptions.py`). The elem/mid/high breakdown above is a named, counted subset of
  that total; some variance in total is expected from specialty/alt programs not individually
  categorized here.

### Chesapeake (Chesapeake Public Schools / CPS)
- **Source**: SchoolDigger.com + virginiabuilders.com (division-sourced promotional text) -- both
  give identical figures.
- **Figures**: 28 elementary, 10 middle, 7 high.
- **Cross-validation performed**: direct count of Wikipedia's own named high-school list (Deep
  Creek, Grassfield, Great Bridge, Hickory, Indian River, Oscar Smith, Western Branch) = exactly 7,
  matching.
- **Strongest consensus of all 11 localities** -- three fully independent sources agree exactly on
  all three figures, no discrepancy found anywhere.

---

## Topic: Prince William County school-count correction (supersedes the original finding above)

The original Jan 2025/Feb 2026 sourcing (62/18/13-or-16, with the high-school figure an unresolved
discrepancy) was superseded by a direct follow-up research pass, prompted by the user re-supplying
the PWCS schools-directory URL after being told the original source was JavaScript-rendered and
incomplete.

**What was tried and didn't work**: PWCS's own official directory (pwcs.edu/schools/index) was
fetched directly twice, and a presumed-static sub-URL (`/schools/middle_schools`) was also tried --
all three attempts hit the same wall: the page is genuinely, thoroughly JavaScript-rendered, with
the sub-URL's own fetch metadata showing a redirect straight back to the same client-side-only
index page. This wasn't a lack of effort; it's a real technical limitation of that specific site
given available tools.

**What worked**: pivoted to NCES's own federal Common Core of Data database
(nces.ed.gov/ccd/schoolsearch), fetched all 7 pages of results (101 schools total), with every
single school's own exact grade range captured directly (e.g. "PK-5," "6-8," "9-12," "KG-8,"
"1-8," or "†" for facilities with no standard grade range reported). Classified programmatically
via a small script rather than by eye, given the volume and the number of edge cases already found
at other localities.

**Result**: 62 elementary (PK-5 or KG-5), 17 middle (6-8), 13 high (9-12) -- sum-checked against
the full 101-school total exactly. Two genuine mixed-grade-band schools (Mary G. Porter
Traditional, grades 1-8; The Nokesville School, grades KG-8) and seven facilities with no standard
grade range (three separate "Independence Nontraditional" entries split by level, N. Virginia
Regional Special Ed Program, PACE West, Prince William Juvenile Detention Home, The Governor's
School @ Innovation Park) were identified and excluded from the elementary/middle/high tally,
rather than force-fit into one of the three categories.

**High-school figure (13) independently confirmed a second way**: two separate Wikipedia articles
state directly and sequentially that Charles J. Colgan Sr. High School is "the 12th high school"
in the division (opened August 2016) and Gainesville High School is "the 13th High School...
opened on August 21, 2021" -- both facts stated as plain, undisputed history in each school's own
article, not as summary statistics subject to the same aggregation ambiguity as a third-party
count. This directly resolved the original 13-vs-16 discrepancy in favor of 13.

**Named-school detail** (62 elementary, 17 middle, 13 high, all individually named from the NCES
listing): see `school_rooftop_solar_analysis/school_rooftop_solar_assumptions.py`'s own git
history for the full transcribed list used in an earlier per-individual-school draft of that
module (not the final version, which groups at locality+type level per direct user decision --
but the named list itself remains a useful, sourced reference).

---

## Topic: School rooftop solar capacity rationale (real installed VA projects)

Gathered to inform the user's own direct-set capacity assumptions (850/500/250 kW for
high/middle/elementary) in `school_rooftop_solar_analysis/school_rooftop_solar_assumptions.py`.
The constants below are also recorded as `RATIONALE_*` constants in that module directly (source
of truth for the numbers); this entry carries the fuller narrative behind each one.

### Huguenot High School (Richmond) -- 534.3 kW
User-supplied data point, verified this session. Part of a 10-campus Richmond Public Schools
solar project completed 2019, developed by Secure Futures (now Secure Solar Futures) with
financing from Standard Solar, funded in part by a $100,000 RVA Solar Fund grant (Community
Foundation for Greater Richmond). Total project capacity: 2.9 MW across 10 schools (7 elementary,
2 middle, 1 high -- Huguenot). The "24% of the building's total energy needs" figure quoted by the
user was confirmed to be genuinely Huguenot-specific (not a program-wide average) by checking the
original 2019 source article, which ties the 24% figure directly to Huguenot in context. One
source (Secure Solar Futures' own customer-story page) states the total as 2.87 MW rather than
2.9 MW -- a small rounding discrepancy, not material, not independently resolved. A separate
source (Standard Solar's own project page) mislabeled Linwood Holton as a "high school" rather
than elementary -- resolved as a clear, isolated error in that one source, since three independent
sources (an NBC12 photo caption, Virginia's own School Quality Profile page URL, and the school's
current website) all confirm it as elementary.

### Patrick Henry HS and William Fleming HS (Roanoke) -- 1,000 kW each
Found via Roanoke City Public Schools' Feb 2026 solar-powered-microgrid grant announcement
(Virginia Department of Emergency Management, $450,000 grant + $2.1M from Secure Solar Futures).
Direct quote: "Each of the two high schools serving as emergency shelters will host 1 megawatt of
solar power generating capacity." This is part of a much larger, 32-site, 10.1 MW RCPS-wide solar
project (17 elementary, 5 middle, 2 high, 5 program locations), being completed in three phases:
Phase 1 (1.6 MW / 6 locations, completed Dec. 2024), Phase 2 (5.7 MW / 11 locations, early 2026),
Phase 3 (2.8 MW / 15 locations, end of 2026). Per-phase average kW/site varies substantially
(266.7 / 518.2 / 186.7 kW/site across the three phases) -- a real, disclosed signal that per-site
capacity depends heavily on roof area, project design intent, and budget, not a clean function of
school type alone.

### Locust Grove Middle School (Orange County) -- 945 kW
Found via a June 2020 Secure Futures Solar press release (solarpowerworldonline.com,
solarbuildermag.com) about an 8-facility, 2.5 MW Orange County Public Schools project. The
source's own phrasing -- "With a capacity of 945 kilowatts, the solar panels installed at Locust
Grove Middle School will be among the..." (sentence truncated in the available snippet, but the
construction "will be among the [largest/highest...]" strongly implies this is being singled out
as notably large, not typical) -- is the reason this figure was NOT treated as a reliable
"typical middle school" data point on its own.

### Other portfolio-level cross-checks (mixed-type, not type-specific)
- **PWCS's own solar project** (distinct from the division's full 101-school count used
  elsewhere): Secure Solar Futures installed arrays at 12 PWCS sites -- 2 middle (Beville,
  Potomac Shores), 7 elementary (Chris Yung, Covington-Harper, Jenkins, Kilby, Kyle Wilson,
  Leesylvania, Minnieville), and (per "in addition to" phrasing implying prior-mentioned sites not
  captured in the available snippet) an inferred ~3 high schools, totaling 7.9 MW -- 658.3 kW/site
  average.
- **Orange County** (8 arrays, 2.5 MW total): 2 arrays at Orange County High School (main building
  + field house, not separately captured), 1 each at Taylor Education Administration Complex,
  Prospect Heights Middle School, Orange Elementary School, Locust Grove Primary School, Locust
  Grove Elementary School, and Locust Grove Middle School (945 kW, see above) -- 312.5 kW/site
  average.
- **Augusta County** (4 schools, 1.0 MW total, financed by Standard Solar): Riverheads Elementary,
  Riverheads High School, Wilson Elementary, Wilson Middle School -- no per-school breakdown found,
  250 kW/site average across the mixed 4.

### What was checked and found not to be a usable source
`data.securefutures.solar` -- Secure Futures' own live generation-monitoring dashboard, listing
individual site names (Linwood Holton Elementary, Huguenot High School, and others that appear to
belong to a different division entirely, e.g. Metz Middle School, Hugh K. Cassell Elementary,
likely Augusta/Waynesboro-area sites given Secure Futures' Staunton headquarters). Checked
directly and found to expose live, time-series generation data (kW at a given moment, varying by
weather/time-of-day) via a CSV download endpoint -- not a static, nameplate installed-capacity
figure like the numbers above. Not pursued further as a source for capacity figures.

---

## Topic: NVRC Solar Map's underlying building-footprint service (C&I rooftop-area research)

Gathered in pursuit of a C&I rooftop-area estimation method after the CBECS-scaled-down approach
was rejected (see the module docstring in `school_rooftop_solar_analysis/` and the compacted
session summary's own A.6 note for that original rejection).

**The map itself**: novasolarmap.com, built by the Northern Virginia Regional Commission (NVRC)
with George Mason University's Department of Geography & GeoInformation Science, launched August
2016. Per NVRC's own ESRI case study (esri.com/about/newsroom/arcuser/web-app-sheds-light-on-solar-
energy-potential): covers 1,338 square miles with **534,000 individual building polygons** and
47 GB of LiDAR-derived imagery -- genuinely comprehensive, not a sample. Explicitly covers
"home and/or business" (i.e. includes C&I, not residential-only). Hosted on NVRC's own ArcGIS for
Server instance (not the standard ArcGIS Online domain), which is why the standard ArcGIS Online
item-metadata REST route did not resolve it.

**Real, important dated-data caveat**: the same case study states the app will keep running
"until updated LiDAR data is available" -- strongly implying the underlying building/LiDAR data is
still substantially the original 2016 vintage. Given the volume of C&I/data-center construction in
NoVA since 2016, this likely undercounts current rooftop stock meaningfully. Not independently
confirmed with a specific "last updated" date beyond this inference.

**Underlying service, discovered directly by the user via browser DevTools -> Network tab**
(not found through web search or any static fetch -- confirmed independently that this service
name/host isn't indexed or discoverable that way): when searching an address on the live map
(https://nvrc.maps.arcgis.com/apps/webappviewer/index.html?id=ef5c5dc969f341cc986cd431d94cdfe9),
three distinct services fire in sequence:
1. `https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/suggest` -- Esri's public,
   free, no-key World Geocoding Service, autocomplete step.
2. `https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates` --
   same public service, resolves the full address to Web Mercator (WKID 102100) coordinates.
3. `https://services5.arcgis.com/6MUPhDX27Ne3DNOw/arcgis/rest/services/BuildingFootprintCO2/
   FeatureServer/0/query` -- **the actual building-footprint feature service**. Queried via
   bounding-box (envelope) requests as the user pans/zooms; multiple sequential tile queries were
   observed for one large, irregularly-shaped shopping-center building, confirming the query
   pattern is tile-based, not one-building-per-request. Default map-client requests use
   `f=pbf` (a binary, tile-optimized encoding, not directly readable) -- the service is expected
   to also support `f=json` for a readable response, per standard ArcGIS Feature Service behavior,
   though this has NOT been independently confirmed since the service could not be reached from
   this environment (see below).

**What could NOT be verified directly, and why**: attempted to fetch this service (both the exact
captured query URLs and a shortened/metadata-only variant) via this environment's own web-fetch
tool. Two distinct, confirmed limitations, not one: (1) the exact captured URLs are too long for
the fetch tool's own length limit -- confirmed by a specific "URL_TOO_LONG" error, distinct from a
permissions error; (2) any shortened or modified variant of the same URL -- even one sharing the
identical host and path -- is rejected as "not in any prior search or fetch result," confirming
the tool requires an exact previously-seen URL, not just a matching host/path prefix. A targeted
web search for the service name ("BuildingFootprintCO2") did not surface its own schema or
documentation either -- it is not a widely-known, publicly-documented dataset by that name (unlike,
say, NREL's own published technical-potential study).

**Resolution -- a script written for someone with normal network access to run**:
`query_nvrc_building_footprints.py` (in this session's outputs) implements the full pipeline --
geocode an address via Esri's free service, query BuildingFootprintCO2 with `f=json`, and
independently compute roof area via the shoelace formula from the returned polygon geometry
(rather than trusting an unverified attribute field name). Includes a mandatory "Step 0" that
fetches and prints the layer's own field schema before any address lookup, since the real schema
is still unknown and was explicitly not guessed at. Not run or tested by Claude directly -- this
environment's own network access does not extend to arcgis.com domains. The one address already
manually confirmed to resolve on the live map (43670 Greenway Corporate Dr, Ashburn, VA 20147) is
pre-filled as a known-good first test case.

**Real field schema, verified via one manually-run example** (21335 Signal Hill Plaza, Sterling,
VA -- run by the user directly on the live map, output cross-checked against the map's own
on-screen popup): `Area` (roof area, sqft) and `UsblArea` (solar-suitable subset, sqft) are
directly usable and match the map's own labels exactly; `UsblArea/Area*100` exactly equals
`PctArea`. `SysSize` (kW array size) confirmed directly by the user from the map's own UI.
`Savings` = `SysSize * 1000 * $0.11` exactly, confirming the $0.11/kWh rate stated on the map's own
"Assumptions" page and revealing the tool's own methodology treats `(SysSize_kW * 1000)` as an
implied annual kWh estimate (~1,000 kWh/kW-yr, a round, slightly-conservative capacity-factor
heuristic for VA -- real fixed-tilt systems typically run somewhat higher). A separate, much larger
`kWh` field (not the same as the `kwhr` field `Savings` is actually computed from) remains
UNEXPLAINED -- not a clean multiple of anything else checked, left flagged rather than guessed.
`CO2Ton`/`CO2MetTon` confirmed as the same figure in US short tons vs. metric tons (exact
1.10231 conversion match). A real, UNRESOLVED discrepancy was also found: the `Area` attribute
(20,922.3 sqft) did not match this script's own independently-computed geometry-derived area
(34,717.1 sqft, itself confirmed against the service's own `Shape__Area` field) -- a 1.66x
difference, on a complex, multi-tenant shopping-center building. Best available hypothesis, not
confirmed: `Area` may be computed per tenant unit/roof section while the returned polygon geometry
is the whole shared building footprint.

**Suite/tenant deduplication, a second real methodological issue surfaced directly by the user**:
a single bounding-box query returns every feature in the map window, which for a multi-tenant
building means multiple rows sharing the same underlying `OBJECTID` but different `Address`
attribute values (one row per suite). The user's own observation -- "we need to filter out the
additional addresses for buildings that have suites" -- was implemented as two separate
deduplication passes in the script: (1) input addresses deduplicated by base street address
(suite/unit stripped) before any geocoding happens, an efficiency measure; and (2) final results
deduplicated by `OBJECTID`, the definitive safeguard against double-counting a building queried via
two different suite addresses, since two genuinely different base street addresses can still
occasionally resolve to the same building. A real bug was caught and fixed while implementing the
first pass: the initial suite-stripping regex matched "STE" at the start of the unrelated word
"STERLING" (no word-boundary anchor on the trailing side of the keyword), silently deleting the
city name from a real Sterling, VA address. Caught via direct testing before being treated as
complete -- not caught by reading the regex. See Common_Mistake_Log.md's own regex-boundary
pattern entry for the general, reusable lesson.

CONFIRMED DATA GAP, real and observed, not hypothetical: a real Loudoun C&I
building (900 Sycolin Rd SE, Leesburg -- part of the established Leesburg Tech
Park flex/R&D development) is visible on the map's own base layer but returns
NO solar-evaluation data at all when queried -- confirmed with AND without the
suite text included, ruling out address-formatting as the cause. A second,
deliberately old comparison building (19 E Market St, Leesburg, in the town's
historic downtown, established as a historic district in 1963) DID return data
successfully -- corroborating, not just hypothesizing, that buildings postdating
the map's own evaluation date are the ones affected. Further corroborated by a
third, independent, strongly-suggestive fact: Loudoun County's own Economic
Development office states directly that the county "has led the Commonwealth of
Virginia in new commercial investment every year since 2016" -- a striking
coincidence with the map's own ~2016 LiDAR vintage, meaning the map's data
essentially predates the START of Loudoun's historic C&I construction boom, not
some minor recent slice of it. No precise "% of Loudoun C&I stock built since
2016" figure was found (the evidence is strong and directional, not a hard
percentage) -- but the practical implication is that this is a SUBSTANTIAL, not
marginal, undercount for Loudoun specifically, and the gap should be expected to
be worse in fast-growing NoVA localities generally than in more established
urban cores (Richmond, Norfolk, etc.) where more existing C&I stock predates
2016. This is the single most important open question for treating this data
source as usable for a comprehensive C&I rooftop-area estimate -- the true gap
rate remains unquantified, but is now understood to plausibly be large,
specifically concentrated in newer construction, and worst in exactly the
localities where recent C&I growth (and therefore rooftop solar opportunity) has
been largest -- an asymmetric skew worth carrying forward into any aggregate
estimate built from this source.

MEASURED, not just hypothesized: a 13-address batch (see loudoun_test_batch.md) was run manually
by the user, deliberately mixing older established Sterling/Leesburg addresses against newer
developments (One Loudoun, Brambleton). Result: 10/13 (76.9%) success, 3/13 (23.1%) no-data.
Refined finding, more precise than the original "too new" hypothesis: One Loudoun (20365, 20405
Exchange St) went 2/2 success, while Brambleton (23677 Sailfish Sq, 42544 Dreamweaver Dr) went 0/2
-- despite both being "newer developments" by community founding date. This suggests the real
driver is the SPECIFIC BUILDING's own construction date, not how new the surrounding community is
as a whole -- One Loudoun's downtown opened in phases starting 2013-14 (plausibly predating the
~2016 evaluation), while the specific Brambleton addresses tested may be from later phases of that
community's ongoing 20+ year buildout. Full per-address results and field values recorded in
loudoun_test_batch.md and the session's own conversation history.

NEW, UNRESOLVED observation requiring follow-up: 22611 Markey Ct (Sterling) returned a very large
roof area (73,716.87 sqft) for what is presumably a single medical practice's building (Sterling
Urology and Sexual Health LLC) -- comparable in scale to the largest buildings tested. The user
directly observed, viewing the live map, that "the underlying shape now looks much larger than
what appears to be the previous building evaluated coloring," and separately described it as
looking like "a smaller older building that was likely torn down with a much larger building
built." Follow-up research found this address is part of "Loudoun Business Park," a MULTI-UNIT
complex (separate listings reference units 107, 111, 112, and suite 104 at the same address) --
one listing for a different unit at this address gives a direct data point: built 1991, only 5,057
sqft. This suggests an alternative (not confirmed, not mutually exclusive with the user's own
explanation) hypothesis: rather than one building being redeveloped, the evaluated 73,716.87 sqft
shape more likely represents MULTIPLE SEPARATE BUILDINGS within the business park merged into one
evaluated area by the search/query, not one tenant's actual building. This is a second, distinct
data-quality risk, different in kind from the earlier Sterling Signal Hill Plaza finding: that one
was a MULTI-TENANT SINGLE BUILDING (one structure, many suites, Area attribute vs. geometry-derived
area diverging 1.66x); this one is a MULTI-BUILDING BUSINESS PARK (multiple separate structures
within one search radius, plausibly merged into a single reported result). CONCLUSION: the
22611 Markey Ct data point should be treated as UNRELIABLE and excluded from any aggregate total
built from this batch, pending further investigation -- not trusted at face value the way the
cleaner single-building results (Signal Hill, 19 E Market St, Ridgetop Cir) have been.

ADDENDUM, later same session -- full detail in loudoun_test_batch_results.md, summarized here to
keep this log in sync: (1) the click-away-then-click-back UI-quirk concern was directly resolved
by re-testing all 3 no-data addresses with the workaround -- all three stayed genuinely uncolored/
data-free, confirming they are real gaps, not popup-retrieval artifacts. The 23.1% (3/13) no-data
rate stands as confirmed, not merely an upper bound. (2) 42340 Soave Dr, initially an unexplained
large outlier, was confirmed via Street View to be a parking garage -- reassigned out of the C&I
rooftop bucket entirely and categorized as a top-level solar canopy candidate (Scenario 3(b)
territory), per direct user input. (3) DECISION, 2026-08-27: no further exhaustive gap-correction
effort will be pursued for the post-2016 data-vintage limitation -- the analysis is strategic, not
tactical; parking-garage-type structures are estimated at the lowest of single-digit percentages
of total C&I stock (clustered along corridors like the Dulles Toll Road); the gap will instead be
documented as a stated modeling limitation. Added to VA_SLCOE_Model.xlsx "Assumptions & Sources"
tab, rows 126-127. Net result across the 13-address batch: 8/13 (61.5%) cleanly usable C&I
rooftop data points, 3/13 confirmed genuine gaps, 1 excluded as unreliable (Markey Ct), 1
reassigned to the parking-canopy category (Soave Dr).

## LOUDOUN BUSINESS-LIST ADDRESS CLASSIFIER (address_classifier.py, session continued 2026-08-28)

Built to systematically sort real Loudoun County business-account records into likely-real-C&I vs.
likely-not, per direct user correction of an earlier, cruder draft. Source: Loudoun County's own
official "Active Business Accounts" list (Commissioner of the Revenue); a real, verbatim 65-record
slice saved at loudoun_address_pull/raw_active_business_accounts_A.txt.

Per direct user guidance, NOT a binary filter -- every record is tagged with explicit, separate
signals (hard-exclude status + reason, suite presence, entity-type category, person-name flag)
rather than collapsed into one opaque confidence score, since the underlying signals are genuinely
too fuzzy to responsibly combine: a business owning its whole building has no suite for the
opposite reason a home-based registration doesn't; "Inc"/"Corp"/"PC"/"PLLC" skew toward real,
established tenants; a person-like name paired with LLC is a weak sole-proprietor signal, but a
person-like name with no suffix at all must NOT be auto-assumed small (Charles Schwab given as the
illustrative counterexample) since real, substantial firms are routinely named after their founders.

KEY DESIGN POINT, directly motivated by a real record in this data: entity-type suffix is checked
across BOTH business_name and trade_name fields, not business_name alone. "Albert Reed Patterson" /
"Mr. Print of Middleburg LLC" -- business_name alone is a bare person name with no suffix; the
actual LLC signal sits in trade_name. Checking business_name only would silently miss it, producing
PERSON_NO_SUFFIX instead of the correct LLC_PERSON_NAME. Verified directly: the combined check
correctly finds it.

TWO REAL BUGS caught by tests before being trusted, not just assumed correct from the design:
(1) "Advanced Electro LLC" matched the bare person-name pattern, since neither "Advanced" nor
"Electro" was on the original company-style wordlist -- expanded the wordlist, and documented in
the module's own docstring that this remains a PERMANENT, accepted limitation (no finite wordlist
covers every company-style name), which is exactly why this signal is designed to never drive a
hard exclusion on its own. (2) "Agilerank LLC" was being checked for the person-name pattern
INCLUDING the "LLC" suffix itself as one of the two words -- fixed by stripping the known suffix
before running the person-name check.

REAL, UNRESOLVED EDGE CASE flagged via a dedicated test rather than silently handled either way:
the Patterson record's own address field is a COMPOUND string, "PO BOX 1121 5 E FEDERAL ST" -- a PO
Box AND a real street address (Middleburg's own historic downtown corridor) concatenated in one
field. Current hard-exclude logic drops the whole record as PO-Box, the conservative default -- but
this means a real, in-county building may be getting dropped along with genuinely PO-Box-only
records. Not fixed here; locked in as a known, documented limitation via
test_compound_po_box_and_street_address_is_still_excluded, so a future change to this behavior is a
deliberate choice, not an accidental regression.

RESULTS across the real 65-record file: 21 hard-excluded (11 wrong city, 8 out-of-state, 2 PO Box),
44 pass through (16 Inc/Corp, 13 LLC-company-style, 6 licensed-profession, 4 unclear,
3 person-no-suffix, 2 LLC-person-style). 22/22 tests passing.

Files: address_classifier.py, test_address_classifier.py, in loudoun_address_pull/.

## FULL-COUNTY SCALE-UP: 23,373 real records classified (session continued 2026-08-28)

The user provided the FULL county business-account list, first as a "PDF" (actually plain ASCII
text despite the extension -- 28,146 lines, full A-through-Z, confirmed byte-identical after
securing a local copy), then as a "docx" conversion of the same data (also not a real binary
.docx -- another plain-text file, this time formatted as an interleaved mix of Markdown pipe-table
rows and leftover tab-delimited rows). Both files were secured locally (MD5-verified) before the
user deleted them from Project KB to free up quota, per direct instruction to do so promptly.

**Format discovery**: the docx conversion produced two DIFFERENT delimiter formats mixed
throughout the same file, not one uniform format -- 24,179 rows as clean pipe-tables
("| NAME | TRADE | ADDR | CITY | ST | ZIP |") and 867 rows still tab-delimited with a variable
number of leading empty fields (0, 3, 4, or 5 observed). Both are genuine improvements over the
original plain-text export (which had no delimiter between fields at all), but required a
two-branch parser rather than one.

**THREE real, confirmed corruption patterns found via direct inspection, each handled explicitly
rather than guessed at or silently dropped** -- new function `parse_mixed_delimiter_docx_export()`
added to address_classifier.py:
1. Address and city merged into one field (105 pipe rows) -- preserved verbatim with an explicit
   "[UNSPLIT ADDRESS+CITY, NEEDS REVIEW]" flag rather than guessing the split point (city names
   are frequently multi-word -- Stone Ridge, South Riding, Round Hill -- so splitting on the last
   word would silently produce wrong data for those).
2. Two entire records merged onto one line because a line-break was lost during conversion (35 tab
   rows with irregular field counts of 2, 4, 8, 10, or 11 -- confirmed by direct inspection, e.g.
   one record's zip code sitting directly against the next record's business name with only a
   space, not a newline, between them) -- routed to unparseable_lines, not force-split.
3. The same lost-line-break corruption in a more severe variant where even tab-delimiting was
   lost entirely (166 lines with zero delimiters at all, confirmed by direct inspection to be
   fully-concatenated pairs of records or orphaned fragments) -- also routed to unparseable_lines.

**A real bug caught during full-file testing, not by the unit tests written first**: the parser
initially checked only for the repeated Markdown table HEADER row ("BUSINESS NAME"), not the
table's own SEPARATOR row ("|---|---|---|---|---|---|", which repeats once per table block
throughout the file same as the header does). Every separator row was being silently parsed as a
fake 6-field record with every field literally "---". This was caught via Rule 4 (cross-verify
against an independent baseline): the parsed total (24,431) was 982 higher than the 23,449-line
baseline from the original plain-text file, and investigating that gap directly (not assuming
either number was simply correct) surfaced 863 exact-duplicate BusinessRecord(business_name='---',
...) entries, all traced to this one root cause. Fixed by also checking whether every field in a
pipe-table row consists entirely of dashes; a regression test was added
(test_markdown_table_separator_row_is_skipped_not_counted_as_fake_record) documenting the specific
bug and the log entry it corresponds to, per Rule 2's own standing requirement. After the fix, the
baseline discrepancy dropped from 982 to 125 (99% explained), and remaining exact-duplicate tuples
dropped from 863 to 7 -- small enough now to plausibly be genuine source-data cases (e.g. a
business with two separate license records at the same address) rather than a parsing artifact,
though this wasn't independently confirmed either way.

**RESULTS across the full, real, corrected dataset**: 23,373 successfully parsed, 201 flagged as
unparseable (not guessed at, saved verbatim to loudoun_unparseable_lines.txt for manual review).
Of the 23,373, 105 carry the unsplit-address+city flag; 23,268 are cleanly parsed with no flags.
Classifier results: 9,217 (39.4%) hard-excluded (5,434 out-of-state, 2,802 wrong city, 981 PO Box),
14,156 (60.6%) pass through (4,358 LLC-company-style, 3,086 LLC-person-style, 2,782 Inc/Corp, 2,580
person-no-suffix, 971 unclear, 379 licensed-profession). Full classified output saved to
loudoun_full_classified.csv (23,373 rows, all original fields plus every classifier signal).

Test suite: 33/33 passing (11 new tests added this round, covering every corruption pattern found
plus the separator-row regression).

Files added this round: loudoun_active_business_accounts_FULL_RAW.txt (secured copy of the "PDF"),
loudoun_docx_export_RAW.txt (secured copy of the "docx"), loudoun_full_classified.csv,
loudoun_unparseable_lines.txt -- all in loudoun_address_pull/.

## KNOWN_LOUDOUN_CITIES gap found and fixed (session continued 2026-08-28)

User asked for the distinct city names behind the 2,802 "wrong city" exclusions. Producing that
breakdown surfaced a real, measurable bug: "BLUEMONT" (a real Loudoun historic village) was never
in KNOWN_LOUDOUN_CITIES, wrongly hard-excluding 70 real records -- the single largest false-
positive exclusion found in this work. The user then provided a cited reference list (visitloudoun.org,
Loudoun County GIS town metadata, Wikipedia's Loudoun County and unincorporated-communities pages)
covering all of Loudoun's major CDPs and historic unincorporated villages. Cross-checked against the
existing set: all 6 major CDPs and all 7 incorporated towns were already present; 9 historic
villages were missing (Arcola, Bluemont, Willisville, Airmont, Bloomfield, Britain, Conklin, Dover,
Wheatland). Added all 9. Only Bluemont had measurable impact in the actual 23,373-record dataset --
the other 8 didn't appear in the city breakdown at all, suggesting few or no registered businesses
currently use them as a mailing address, but they're real Loudoun locations and were added
regardless rather than only fixing the one with observed impact.

Two new regression tests added (test_bluemont_is_recognized_as_loudoun_not_wrongly_excluded,
test_other_user_confirmed_loudoun_communities_are_recognized) -- 35/35 tests passing.

RESULTS after the fix: hard-excluded dropped from 9,217 to 9,147 (39.1%), not-hard-excluded rose
from 14,156 to 14,226 (60.9%) -- exactly +70/-70 as expected, no side effects elsewhere. CSV
regenerated with corrected classifications.

STILL OPEN, not addressed this round: a separate, smaller issue was flagged when reporting the
city breakdown -- roughly 8-10 records where the underlying city IS in KNOWN_LOUDOUN_CITIES but
got excluded anyway due to formatting variants in the source data not matching an exact string
("ASHBURN, VA", "ASHBURN, VA, USA", "BROADLANDS VA", "PAEONIAN SPGS" as an abbreviation, "CHANTILY"
as a misspelling). This is a normalization problem (strip trailing state text, handle known
abbreviations/typos), distinct from the missing-city problem just fixed, and remains unaddressed.

## City-normalization fix (session continued 2026-08-28)

The previously-flagged formatting-variant issue was fixed. Two new functions added:
_normalize_city_for_comparison() strips trailing zip-code-like tokens, ", USA", ", VA"/" VA", and
punctuation before comparison (handles "ASHBURN, VA", "ASHBURN, VA, USA", "BROADLANDS VA",
"CHANTILLY, VA", "STERLING VA", "LEESBURG, VA", "LEESBURG,", and the compound
"LEESBURG VA  201764475" case where a zip got concatenated into the city field). CITY_ALIASES is a
small, explicit, hand-reviewed map for known typos/abbreviations (ASHBIRN, CHANTILY, LEESBUG,
LEESBURGE, LEESEBURG, PAEONIAN SPGS, PURCELLIVLLE, LANDSDOWNE).

IMPORTANT, confirmed via direct testing before trusting the approach: fuzzy/edit-distance matching
was tried against the real "wrong city" list as a way to systematically find candidates, and found
18 close matches to a known Loudoun city -- but 4 of them (Bealeton, Hampton, Petersburg,
Scottsville) are genuinely different, real Virginia cities/towns outside Loudoun, only
coincidentally close in spelling to a Loudoun city name (Brambleton, Hamilton, Leesburg,
Lovettsville respectively). Auto-accepting fuzzy matches would have wrongly aliased all four into
being treated as in-county. CITY_ALIASES is therefore a manually-reviewed, explicit list, not a
fuzzy-matching function -- each of the 8 entries was individually confirmed to be a real variant of
the city it maps to, not a coincidental near-match. A dedicated regression test
(test_genuinely_different_virginia_places_stay_excluded) locks this distinction in.

RESULTS after this fix: hard-excluded dropped from 9,147 to 9,128; not-hard-excluded rose from
14,226 to 14,245 (+19). Final categorized breakdown across the full, corrected 23,373-record
dataset: 5,434 (23.2%) out-of-state, 2,713 (11.6%) city not a known Loudoun community, 981 (4.2%)
PO Box -- 9,128 (39.1%) total hard-excluded, 14,245 (60.9%) not hard-excluded. Confirmed via direct
test: all 16 known formatting-variant cases now resolve correctly, and none of the 4 genuine
false-positive risks were swept in. Test suite: 39/39 passing. CSV regenerated.

## Zip-code cross-verification signal added, then corrected against the real Zillow list (session continued 2026-08-28)

User suggested zip-code matching as a potentially better approach than city names, pointing to
Zillow's "browse homes in Loudoun County" page. Direct fetch returned a 429 (rate-limited); fell
back to zip-codes.com (34 zips) and zipdatamaps.com (38 zips, explicitly documenting 7 as extending
into adjacent counties) via search + fetch. Built KNOWN_LOUDOUN_ZIPS from zipdatamaps.com's list and
added a NEW, SEPARATE signal (AddressClassification.zip_in_known_loudoun_zips) rather than replacing
the city-name check -- deliberately, because cross-verifying the two immediately surfaced a real
risk: 20120 (Centreville) and 20170 (Herndon) were on that list, and both are confirmed, from the
real dataset, to be genuine Fairfax County locations (89 and 181 records) that a pure zip-based
check would have wrongly pulled back in.

The user then provided the actual Zillow list directly (38 zips, matching the count from the other
two sources). Direct comparison against the zipdatamaps-derived set found real differences: Zillow's
list does NOT include 20120 or 20170 (independently confirming the boundary-straddle concern was
correct) and DOES include three zips the earlier set lacked -- 20107, 20151, 22093. All three were
independently verified via multiple other sources before being trusted, not just adopted on
Zillow's say-so: 20107 confirmed via unitedstateszipcodes.org as "Arcola · Loudoun County" (a nice
independent cross-check of the Arcola city-name fix from earlier this session); 22093 confirmed via
multiple sources as a second, unique Ashburn zip (Natl Assn Letter Carriers); 20151 confirmed as a
second, Loudoun-side Chantilly zip distinct from 20152, resolving an open question from earlier the
same session (129 records with city=Chantilly, zip=20151 had been flagged as a possible
false-inclusion risk -- they are very likely correct as-is). KNOWN_LOUDOUN_ZIPS was replaced with
this Zillow-sourced list. 20598 (on both earlier sources, a non-residential DHS/Falls Church
single-entity zip) is not on Zillow's list -- plausibly because a zero-population government
mail-routing code would never have home listings to show, not because it's genuinely non-Loudoun --
noted but not added back in, per direct instruction to use the provided list.

Re-running the cross-check with the corrected list dropped the city/zip disagreement count from 215
to 56 (171 of the original 215 were exactly the Herndon/Centreville/Upperville noise the switch was
meant to resolve). The remaining 11 Upperville records were investigated and added to
KNOWN_LOUDOUN_CITIES too -- Zillow's own page separately lists "Upperville Real Estate" alongside
the other unambiguously-Loudoun communities. After that fix, only 45 disagreements remain: 44 with a
blank city (the unsplit-address+city corruption cases -- clean recovery candidates, no conflicting
signal at all) and 1 ("STE J108," an obvious data-entry glitch, not a real place name).

RESULTS: hard-excluded 9,117 (39.0%: 5,434 out-of-state, 2,702 wrong-city, 981 PO Box);
not-hard-excluded 14,256 (61.0%). Test suite: 47/47 passing. CSV regenerated with the new
zip_in_known_loudoun_zips column.

STILL OPEN: whether to reclassify the 44 blank-city + zip-match records as not-hard-excluded --
proposed to the user, not yet decided.

## City recovery from unsplit-address text, using address + zip together (session continued 2026-08-28)

User asked whether the 44 blank-city + zip-match records have address text, and suggested the zip
should give the biggest clue for looking up city. Investigation confirmed: none of the 44 have an
empty address field, and in most cases the real city name is already sitting verbatim at the end of
the merged "[UNSPLIT ADDRESS+CITY]" text -- e.g. "...STE 190  STERLING". Built
recover_city_from_unsplit_address(), using BOTH signals together rather than either alone: looks up
the zip's known primary city (new ZIP_TO_PRIMARY_CITY mapping, sourced from the same references as
KNOWN_LOUDOUN_ZIPS), then CONFIRMS that exact city name is textually present at the end of the
record's own merged address before recovering -- never fabricates a city from the zip alone with no
corroborating text. Deliberately still avoids guessing where a multi-word city name starts within
the merged string; only acts when the two signals agree.

MID-SESSION NOTE: the container filesystem reset during this work (a new environment; /home/claude
was empty). No work was lost -- /mnt/user-data/outputs/ persisted across the reset and had the
latest synced copies of every needed file, restored from there. One casualty: the original
raw_active_business_accounts_A.txt fixture (an early-session, hand-transcribed 65-record sample)
was never copied to outputs since it was only ever an intermediate working file, so it was
unrecoverable in its exact original form. Regenerated a valid replacement by extracting 65 real
records directly from the (recovered) full docx export, deliberately including both named test
cases (Advanced Dermatology, Albert Reed Patterson) the existing tests assert against.

Applying recovery surfaced a related, previously-uncatalogued corruption sub-variant: 8 of the 44
records had a genuinely empty state field (not "VA"), traced to a DIFFERENT 5-field pipe-row
corruption pattern than the one originally handled -- the street address merged into trade_name
instead of into the address+city field (e.g. "KI & KA LLC" / trade_name="KI & KA LLC 25504 FALLING
CEDARS CT" / address="[UNSPLIT...] CHANTILLY"), which shifts the remaining fields so state ends up
blank rather than "VA". Confirmed this doesn't need separate handling: a record only reaches
successful recovery when BOTH its zip is a confirmed Loudoun zip AND its address text textually
confirms that exact Loudoun city -- that combination is definitive evidence of being in Virginia
regardless of what the original state field held, so recover_city_from_unsplit_address now also
normalizes state to "VA" on successful recovery.

Broader investigation of this 14-record "empty state" group (broader than just the 8) found it's
actually a mix of distinct cases, not one pattern: 8 genuinely recoverable Loudoun records (fixed as
above); 3 genuinely non-Loudoun records with the same field-shift but a real non-Loudoun city
(Alexandria, Annandale, McLean) -- correctly staying excluded, not a bug; 1 foreign address (Air
Canada) -- correctly excluded; 1 severely corrupted row (Otsuka Pharmaceutical, nearly every field
empty, including zip) -- recovery correctly declines since there's no zip to confirm against; 1
genuine, still-unresolved gap (Crown & Maven LLC -- the "address" field is a real street address
with no city text anywhere, zip implies Leesburg, but there's no textual confirmation to safely act
on, so it correctly stays flagged rather than being guessed).

RESULTS: 48 records recovered total (44 from the original blank-city+zip-match set, plus 4 more
whose original hard-exclude reason was "out-of-state" rather than "wrong city" due to the empty-
state variant, so they weren't in the original 44 count). Of the 48, 47 are now cleanly included;
the 1 remaining (Worlds Best Prep Course Inc) is correctly still excluded for a separate, legitimate
reason -- its recovered street address is "PO Box 1278," correctly caught by the existing PO-Box
check, the same pattern as the Patterson record from earlier in the session (city recovery and a
separate valid exclusion reason can coexist). Final totals: 9,070 hard-excluded (38.8%: 5,426
out-of-state, 2,662 wrong-city, 982 PO Box), 14,303 not-hard-excluded (61.2%). Test suite: 56/56
passing. CSV regenerated with a new city_was_recovered_from_zip column for transparency.

## Loudoun C&I rooftop solar MW/MWh estimate, from the classified building population (session continued 2026-08-28)

User asked for MW/MWh of rooftop solar the not-hard-excluded (14,303) buildings are suited for.
New module: loudoun_ci_rooftop_solar_estimate.py, in a new loudoun_ci_rooftop_solar/ directory.

METHODOLOGY NOTE surfaced before building anything: ArcGIS (the NVRC Solar Map's own domain)
isn't on this environment's bash network allowlist, so a per-building NVRC lookup across all
14,303 records isn't feasible here even in principle -- this reuses the REAL n=8 NVRC data points
already gathered directly from the live map earlier this session (loudoun_test_batch_results.md)
to establish a per-building kW average/median, rather than a per-record live lookup.

KEY METHODOLOGY STEP: deduplicated business-account records to a unique-BUILDING count before
applying any per-building kW figure, since counting each business record as its own roof would
badly overcount. Real pattern confirmed directly in the data motivated a two-pass dedup: many
business records share the EXACT SAME address including suite number (e.g. one suite -- 44679
Endicott Dr, Ashburn -- shared by 35 separate business-account records), consistent with shared/
virtual-office registrations, not one business per suite. Pass 1 dedups by exact address (catches
this); pass 2 by suite-stripped address (catches the separate different-suites-one-building case).
14,303 business records -> 12,758 unique exact addresses -> 10,918 unique buildings.

Cross-checks: 10,918 unique buildings sits sensibly below zip-codes.com's census-derived "total
businesses" figure for the county (12,489, gathered two turns ago) -- fewer unique buildings than
total businesses is the expected relationship once multi-tenant sharing is accounted for. Separately,
21631 Ridgetop Cir, Sterling appears in both the real NVRC sample (3rd-highest kW, 195.62 kW) and
independently as a top-10 shared-building by record count (34 records, 17 suites) -- a large
building showing up as large via two unrelated signals.

Per-building kW comes directly from the real n=8 NVRC sample (mean 115.49 kW, median 133.13 kW,
range 9.72-226.09 kW -- ~23x spread) rather than an invented W/sqft density, since the NVRC
platform's own kW figure is already the more authoritative number for those specific real
buildings. Both mean- and median-based totals are carried through rather than collapsed to one
number, given the sample's wide spread. Annual MWh conversion reuses the project's own, already-
sourced 20% NEM distributed solar capacity factor (VA_SLCOE_Model.xlsx "Assumptions & Sources" row
13 -- distinct from the 24% utility-scale figure, row 23), not a new assumption.

STATED LIMITATIONS, all surfaced directly to the user: (1) n=8 sample is geographically narrow --
all 8 points are in Sterling, Leesburg, or Ashburn, none from Round Hill, Hamilton, Middleburg,
Purcellville, or the county's more rural/historic communities, which may have a different
building-size profile. (2) Inherits the already-established NVRC data-vintage limitation
(VA_SLCOE_Model.xlsx rows 126-127, ~2016 LiDAR evaluation date) -- both the sample and the
14,303-record building population being sized are drawn from sources affected by the same
post-2016 undercount, so this result should be presented as a conservative lower bound, consistent
with the project's own already-established framing for NVRC-sourced C&I rooftop figures.

RESULTS: 10,918 unique buildings. Mean-based: 1,260.9 MW / 2,209,060 MWh/yr. Median-based:
1,453.5 MW / 2,546,555 MWh/yr. Test suite: 14/14 passing.

Files: loudoun_ci_rooftop_solar_estimate.py, test_loudoun_ci_rooftop_solar_estimate.py,
loudoun_ci_unique_buildings.csv (10,918 rows), loudoun_ci_rooftop_solar_summary.json -- all in
loudoun_ci_rooftop_solar/.

## Added a single combined total-aggregate figure (session continued 2026-08-28)

User asked for a total aggregate MW/MWh in addition to the mean- and median-based figures already
given (both of which were already county-wide totals, just via two different per-building
multipliers). Added total_mw_combined / total_mwh_per_year_combined as properties on
LoudounCiRooftopSolarEstimate -- the simple average of the mean-based and median-based totals,
explicitly stated as a way of combining the two already-computed numbers into one headline point,
not a new independently-derived estimate. Test added confirming MWh-combined (averaging the two
MWh totals) exactly matches re-deriving MWh from MW-combined directly, since the conversion is
linear at a fixed capacity factor. Test suite: 16/16 passing.

RESULT: total combined = 1,357.2 MW / 2,377,808 MWh/yr.

## Parking lot sqft estimation approach devised, then real Loudoun GIS data received (session continued 2026-08-29)

User asked for an approach to estimating parking lot sqft in Loudoun, ahead of Scenario 3(b)'s
parking-canopy solar component. Checked whether the NVRC platform (already trusted for rooftops)
also covers parking lots -- confirmed, via multiple independent search results, that it's
explicitly rooftop-only, so that source doesn't transfer. Found Loudoun County's own GIS
maintains a "Road Casings" dataset (OMAGI) where parking lots are a separate, explicitly-defined
feature type (RD_TYPE=2, "commercial parking over 200 ft long, 20+ spaces"), each with a
pre-computed area attribute -- real, surveyed county geometry, not an inferred density. Also
confirmed Loudoun's own zoning ordinance has a dedicated "7.06.02 Parking Ratios" section as a
possible cross-check, though its hosting site (encodeplus.com) blocks automated fetching so its
actual numbers weren't retrieved. NOTABLE NEAR-MISS: an early search nearly surfaced parking-ratio
figures ("one space per 250 sqft...") that were actually from Rockford, Illinois's zoning code, a
different jurisdiction that matched the search terms -- caught before use, not incorporated.

User then uploaded the actual Road Casing Type 2 extract directly (Loudoun_Road_Casing_type_2.xlsx,
11,317 rows, confirmed 100% RD_TYPE=2). New module: loudoun_parking_lot_sqft.py, in a new
loudoun_parking_lot_solar/ directory.

GOOD NEWS ON VINTAGE: this dataset is far more current than the NVRC rooftop data used elsewhere
in this project -- 96%+ of rows last updated 2022 or later (77% in 2024 alone), vs. NVRC's ~2016
evaluation date. The post-2016-undercount caveat that applies to the rooftop and building-count
figures is much less of a concern here.

TWO REAL, UNRESOLVED DATA-QUALITY QUESTIONS surfaced by direct inspection, deliberately not
silently resolved in the module -- compute_totals() returns multiple totals side by side rather
than committing to one:
1. Nearly half of all 11,317 polygons (5,572) are smaller than the county's own "20+ space"
   definition implies (~6,000 sqft at a standard ~300 sqft/space planning figure) -- but these
   only account for ~4.8% of total area, so filtering them doesn't swing the headline number much.
   Suggests many real lots are digitized as multiple adjacent polygon fragments rather than one
   polygon per physical lot.
2. Genuine concentration at the top end, unverified: the single largest polygon is 92.8 acres
   (1.64% of the entire county total from one row); the 38 largest polygons combined (0.34% of
   rows) account for 13.3% of the total. Unlike the NVRC rooftop sample (where a real merge
   artifact was caught specifically because an address was available to check against Street
   View), this extract has no address/parcel/location field to cross-reference against, so these
   large polygons could not be independently verified either way.

RESULTS (multiple totals, filtering choice not yet made):
- Unfiltered, all rows: 246,091,777 sqft (5,649.5 acres), n=11,317
- Paved only: 209,692,142 sqft (4,813.9 acres), n=10,429
- >=6,000 sqft only (approx. matches county's own "20+ space" definition): 232,679,056 sqft
  (5,341.6 acres), n=3,500
- >=6,000 sqft AND paved: 196,917,109 sqft (4,520.6 acres), n=2,821

Test suite: 14/14 passing, including an integration test against the real uploaded file
cross-checking against figures independently computed via a separate ad-hoc script first.

STILL OPEN: which filtered total (if any) to use as the headline figure; whether/how to
investigate the large-polygon concentration further; whether to pursue the zoning-ratio
cross-check (7.06.02) as a second, independent signal the way city-name and zip-code signals
cross-checked each other earlier in this project.

Files: loudoun_parking_lot_sqft.py, test_loudoun_parking_lot_sqft.py -- in loudoun_parking_lot_solar/.

## Large-polygon concern partially de-risked; distribution visualized (session continued 2026-08-29)

User suggested the single largest polygon (92.8 acres) is plausibly Dulles Airport's main lot.
Web search corroborated the general plausibility (Dulles: 13,000-acre total footprint; ~21,500
total parking spaces across all on-airport facilities per MWAA) without finding an exact acreage
match -- consistent with, not confirming, the claim.

Checked OBJECTID clustering among the top 38 largest polygons as a further, independent check:
they are NOT randomly scattered, but cluster tightly into ~6 distinct groups (e.g. 11 of the 38,
including the single largest polygon, fall within a span of just 508 IDs, 22477-36375). Tight
ID-clustering is consistent with polygons digitized together as part of the same large facility in
one mapping pass -- genuine merge-artifact errors would be expected to scatter more randomly
across ID space. This meaningfully raises confidence that the large-polygon group represents a
small number of genuinely huge real facilities (plausibly Dulles, major data center campuses, or
large distribution centers, all real, large-footprint land uses in Loudoun) rather than a random
data-quality glitch -- though which specific facilities they are remains unconfirmed, since this
extract has no address/location field to check against.

Distribution visualized as two histograms (log-spaced bins, since the data spans ~8 orders of
magnitude): by polygon COUNT (heavily right-skewed -- 5,572 of 11,317 polygons, essentially half,
fall in the 1,000-6,000 sqft "sub-20-space" range) and by TOTAL SQFT per bin (dominated by the
100K-250K bin at 69.5M sqft, the single largest area contributor, not the very largest polygons).

## RD_SURFACE='N' (unpaved) reinterpreted: likely permeable pavement, not gravel/informal areas (session continued 2026-08-29)

User raised two points on the 888 "unpaved" (N) records: (1) a past effort required some
percentage of parking lot area to be permeable surface, which N may actually be capturing rather
than genuine gravel/dirt; (2) Western Loudoun event venues sometimes use grass fields for
intermittent parking, likely uncaptured by this dataset.

On (1): web search found real, supportive regional context -- Loudoun's own zoning ordinance
(Chapter 57) explicitly pairs "unpaved or permeable surfaced" as one combined category, and
neighboring Arlington County has a formal "permeable parking lot" stormwater credit program.
Important honest caveat: this specific layer's OWN data dictionary (read directly two turns ago)
defines "N" narrowly as "gravel, dirt or un-improved," with no mention of permeable pavement --
likely because that definition predates widespread permeable-paver adoption, not a confirmed
statement that N=permeable specifically.

Direct data inspection then found strong, independent supporting evidence: unpaved lots do NOT
skew smaller/more informal than paved lots as a naive reading of "unpaved" might suggest -- they
skew dramatically LARGER. Median 16,815 sqft (unpaved) vs. 1,940 sqft (paved), an 8.7x difference;
76.5% of unpaved lots meet the county's own implied "20+ space" qualifying-size threshold, vs. only
27.0% of paved lots. The 10 largest unpaved polygons run 354K-781K sqft (8-18 acres) each --
consistent with engineered, purpose-built commercial facilities, not random rural gravel overflow
areas. Two new regression tests lock this finding in.

PRACTICAL EFFECT: revises the "paved-only" filter recommendation from two turns ago. Given unpaved
lots look like real, large commercial facilities rather than noise, filtering them out likely
excluded ~36.4M sqft of genuinely legitimate parking area. Unfiltered or size-filtered (>=6,000
sqft) are now the more defensible headline-candidate totals; the paved-only variants are likely
UNDERcounts, not a safer conservative choice.

On (2): confirmed as a real, plausible coverage gap (intermittent-use grass fields wouldn't be
digitized as parking lots, since they don't look like permanent lots in aerial imagery most of the
time), but assessed as NOT consequential for this project's purpose specifically -- intermittent
event-use grass fields are not viable solar-canopy sites regardless of whether they're captured in
this dataset, since a permanent canopy structure would conflict with the field's primary,
non-parking use.

MINOR SELF-CAUGHT ERROR this round: an str_replace edit to add the new test class accidentally
deleted the REAL_FILE_PATH assignment mid-edit, breaking the file's syntax entirely (a stray
`) = "..."` left behind). Caught immediately by the mandatory post-edit syntax check before any
test was run -- fixed before proceeding, not shipped.

Test suite: 16/16 passing.

## Solar canopy + battery storage sizing, refactored to OO for multi-county reuse (session continued 2026-08-29)

User confirmed "filtered sites" = the size-filtered-only total (232,679,056 sqft, >=6,000 sqft
filter, n=3,500 -- NOT paved-only, which the prior turn's finding suggested likely undercounts).
Asked to determine solar canopy parameters and identify space for >=4 hours of battery storage,
noting the workflow: explain the plan, discuss changes, THEN write code per Software Engineering
Standards -- and to design with OO structure since other counties will follow.

PARAMETER RESEARCH: canopy density -- SurgePV's "Solar Carport Design Guide 2026" gives two
figures: a conservative planning estimate ("1 space ~= 800 W DC") and a real-layout worked
example ("100-space lot in a double-row W-frame layout typically supports 200-250 kW DC... the
800 W figure is a planning estimate; the actual layout is always denser," since continuous panel
rows spanning multiple stalls beat one-pair-per-stall). User selected the real-layout figure only:
2.0-2.5 kW/space. BESS footprint -- user provided a more precise two-tier breakdown than the
module's first draft: "pure equipment footprint" (~25-160 sqft/MWh, driven by rapidly-improving
container density) vs. "total developed site footprint" (~600-1,000 sqft/MWh, already including
IFC-mandated 10-ft setbacks, foundations, access, PCS/inverters). User instruction: use the LOWER
end of both ranges (600 and 25 sqft/MWh respectively) given recent density improvements.

KEY CONCEPTUAL CORRECTION, direct from user: the canopy structure spans the full parking-lot
footprint regardless of what sits underneath any given section -- a battery enclosure occupies the
same footprint under the canopy a parked car would, so battery siting does NOT reduce solar
MW/MWh. The only real consequence is fewer available vehicle parking SPACES, an operational/
owner-facing concern, entirely separate from the energy-generation question. Enforced
structurally, not just numerically: SolarCanopyDesign.compute_mw's signature takes only
parking_sqft, with no storage-related parameter through which battery footprint could ever be
threaded in and accidentally subtracted -- confirmed with a dedicated test
(test_solar_canopy_design_compute_mw_has_no_storage_parameter_at_all) plus a behavioral test
proving MW is identical regardless of storage design parameters
(test_mw_is_identical_regardless_of_storage_design_parameters, using a 1,000,000x difference in
sqft_per_mwh between two assessments to confirm zero effect on MW either way).

OO STRUCTURE, for multi-county reuse: CountyParkingData is the only class tied to a specific data
source (Loudoun's Road Casing GIS format, via from_road_casing_extract() -- wraps the existing,
already-tested loudoun_parking_lot_sqft.py rather than duplicating its logic). SolarCanopyDesign,
BatteryStorageDesign, and ParkingCanopyAssessment are county-agnostic dataclasses with overridable
defaults; a second county needs only its own CountyParkingData-producing classmethod. Per direct
user correction, duration_hours is a BatteryStorageDesign INSTANCE FIELD with a default of 4.0,
not a module-level constant -- specifically so a future county or scenario can use a different
duration without editing the class. sqft_per_space is NOT duplicated onto BatteryStorageDesign;
ParkingCanopyAssessment passes it in from SolarCanopyDesign when wiring the two together, keeping
both design classes independently reusable without referencing each other directly.

WORKFLOW NOTE: the module's first draft (written before this OO-restructuring conversation) was
replaced outright rather than incrementally refactored, since it had only been syntax-checked, not
tested or run against real data -- nothing depended on it yet.

RESULTS (Loudoun, real data): 1,551.2-1,939.0 MW canopy solar. Storage (4-hr, 1:1 MW pairing):
6,204.8-7,756.0 MWh; developed-site footprint 3,722,865-4,653,581 sqft (85.5-106.8 acres, all
co-located under the canopy, zero net land beyond the parking footprint itself); 12,410-15,512
parking spaces displaced out of ~775,597 total implied spaces (~1.6-2.0% of the lot -- a small,
plausible operational impact for the site owner, not a barrier). Test suite: 10/10 passing.

Files: loudoun_parking_canopy_and_storage.py, test_loudoun_parking_canopy_and_storage.py -- in
loudoun_parking_lot_solar/.

## Solar generation profile scope addition: tilt and GCR decided for user's own NREL SAM pull (session continued 2026-08-29)

New project scope, reaffirming the original secondary objective (reduce transmission-line need via
locally-generated firmed clean energy): identify Loudoun's solar generation profile using 8+ years
of data, and determine capture/storage needs during the lowest-insolation months/weeks. Checked
existing project files for a usable source: no genuinely Loudoun-specific solar-generation dataset
found (Sterling VA weather file is real NOAA daily weather data, no irradiance fields; the existing
"hourlyresults"/"insolation" files are for Albemarle/Chesapeake/King George, not Loudoun -- though
they do span exactly 8 distinct years, 2012-2020 minus 2015, matching the "8+ years" ask). A real
format inconsistency was found within those files (2019 is in "AC inverter output power | (W)"
while the other 7 years are in "System power generated | (kW)" -- a different metric and unit, not
just a units mismatch) -- flagged, not silently blended. NREL's NSRDB was checked as a direct
source and confirmed to require an api_key parameter for actual downloads, not accessible without
the user registering one themselves.

User decided to pull genuinely Loudoun-specific data via NREL SAM directly, superseding the
Albemarle-proxy plan. Asked for a tilt-angle recommendation.

TILT ANGLE: initial instinct (latitude+15 deg =~54 deg, a winter-optimization heuristic) was
checked against real carport-engineering sources and found to point the WRONG direction for this
specific application -- flagged directly rather than quietly revised. Multiple independent sources
converge: commercial solar carports standardize on 10-15 deg tilt, not latitude-match (~39 deg for
Loudoun) or steeper, because wind uplift on an elevated, open-underside structure scales sharply
with tilt, and one source explicitly ties higher tilts (15-20 deg) to sites above 45N latitude --
Loudoun (~39N) doesn't clear that threshold. C&I flat-roof systems converge on the same low-tilt
range for a related but distinct reason: row-to-row self-shading trades directly against panel
count on a fixed footprint, and roof/lot area is usually the binding constraint, not per-panel
yield (one source: a 30 deg tilt loses ~50% of available roof area to required row spacing vs. 22%
at 15 deg). Recommended ~12 deg (a fixed 10 deg tilt was cited as capturing ~92% of latitude-matched
annual irradiance -- a modest energy trade-off for materially lower structural cost).

USER DECISION: 15 deg tilt (upper end of the 10-15 deg standard range, not the 12 deg midpoint
recommended -- user's own choice, noted not overridden).

GROUND COVERAGE RATIO (GCR), asked as a follow-up specifically for the 15 deg tilt: researched
general commercial/fixed-tilt range (0.30-0.50, with 0.35-0.45 often cited as the balanced
sweet spot). Independently calculated, via code, the zero-shading-at-winter-solstice-solar-noon
GCR specifically for Loudoun's latitude (~39N) at 15 deg tilt: 0.684 -- presented as an honest upper
bound / reference point only, since real designs accept a small shading loss (5-10% per the
research) rather than target zero shading at the single worst moment of the year, which is why the
general industry range sits meaningfully lower. Cross-checked against the ALREADY-ESTABLISHED
2.0-2.5 kW/space canopy density (from the real "100-space lot" SurgePV example used earlier this
session): backing out implied panel area at typical module efficiency (~20-22 W/sqft) against the
established 300 sqft/space total footprint gives an implied GCR of ~0.30-0.42 -- landing inside the
directly-researched range despite being derived independently, a reassuring internal-consistency
finding, not a new assumption. Recommended ~0.40 GCR (centered in the sweet spot, consistent with
the cross-check).

USER DECISION: 0.42 GCR (within the recommended range, slightly denser than the 0.40 midpoint).

STILL OPEN / NOT YET ADDRESSED: the actual 8+ year Loudoun-specific SAM pull itself (user's own
task, in progress); Loudoun's zoning ordinance may have height/structure limits on carports beyond
the wind-load-driven tilt constraints researched here -- flagged as worth checking, not yet
independently verified.

## Hourly solar profile built from real 9-year Sterling SAM data; reframed toward transmission/reliability question (session continued 2026-08-29)

User delivered the promised SAM pull: 9 years (2012-2020, including 2015 -- fills the gap the old
Albemarle-proxy data had) of real Sterling, VA solar generation data, 100kW DC array, 15 deg tilt,
14% system losses -- the exact parameters agreed over the prior several turns. All 9 files verified
structurally identical before use (same columns, same 17,520-row 30-min-interval count) and
consistent with the stated system (observed 83-87 kW peaks across all 9 years line up with the
expected 100*(1-0.14)=86kW AC peak).

User then reframed the analytical goal: monthly/weekly energy totals (the original framing) answer
an energy-BALANCE question; "we'd be looking for low power times, as low firmed generation impacts
how much we can reduce extra transmission line capacity" is a reliability/PEAK-IMPORT question,
which only shows up at hourly resolution -- transmission capacity has to be sized for the worst
hour, not the average. New module: loudoun_solar_hourly_profile.py, in a new
loudoun_solar_profile/ directory. Aggregates 30-min data to hourly; scales the 100kW profile's
SHAPE (not absolute value) up to the already-established canopy MW range from the parking-lot
sizing work (1,551.2-1,939.0 MW) -- necessary now specifically because "how much can we reduce
transmission capacity" is an absolute-MW question, not a normalized one.

TWO REAL BUGS CAUGHT AND FIXED before trusting any output, neither found by the unit tests written
first -- both surfaced by running against the real data:
1. find_longest_low_output_streaks initially only checked row POSITION for consecutive-hour runs,
   not actual elapsed TIME between rows -- despite a docstring claiming otherwise. Caught on review
   before even running against real data. Fixed by explicitly checking each row is exactly 1 hour
   after the previous one; a real time gap now correctly breaks a streak rather than silently
   bridging it. Two dedicated tests added.
2. compute_duration_curve's 100th percentile returned NaN on the real data. Traced to a real,
   confirmed data-structure fact: the Sterling SAM export uses a standardized 365-day year (typical
   of TMY-style solar datasets), so Feb 29 has no source rows at all, for any year. Applying the
   real calendar year to an actual leap year (2012, 2016, 2020 in this dataset) means pandas'
   hourly resample correctly produces NaN for those 24 hours -- genuinely no data to average, not
   a resample bug. Fixed by dropping these hours in aggregate_to_hourly rather than filling with
   zero (which would fabricate 24 fake "outage" hours per leap year, inflating streak findings) or
   interpolating (fabricating data that doesn't exist). A related, genuinely-wrong test assertion
   was also caught and fixed in the same round: initially assumed year-boundaries (Dec 31 23:00 ->
   next Jan 1 00:00) would also produce a gap: they don't, since that's continuous calendar time
   exactly 1 hour apart. Only the 3 leap-day skips (25-hour jumps) are real gaps -- test corrected
   to assert the right count (3, not 11) after the test failure correctly caught the wrong
   assumption.

RESULTS (mw_low=1,551.2 MW scenario): duration curve shows >=25% of all hours at literal zero MW
(expected -- nighttime). Low-output streak analysis directly supports the user's stated hypothesis
("we likely will find that longer duration batteries are necessary"): at a <=1% threshold, streaks
cap around 19-20 hours (close to pure nighttime). But at <=5% and <=10% thresholds, streaks extend
to 63-75 hours (2.6-3.1 days) -- far beyond what a 4-hour battery (the project's established
short-duration benchmark) could bridge, and squarely in the range where the project's existing
~100-hour long-duration benchmark becomes directly relevant. Most of the longest streaks cluster in
Nov/Dec/Feb as expected, but a real, non-obvious exception was found and flagged rather than forced
into the winter-only framing: a 71-hour streak in Sep 2018 (2018-09-08 to 09-11), plausibly a
multi-day tropical-remnant or persistent-overcast event, not a winter phenomenon.

Test suite: 18/18 passing.

Files: loudoun_solar_hourly_profile.py, test_loudoun_solar_hourly_profile.py -- in
loudoun_solar_profile/.

## Software Engineering Standards audit and refactor (session continued 2026-08-29)

User asked directly whether SES was followed for loudoun_solar_hourly_profile.py; re-read the full,
authoritative software_engineering_standards.md from project KB (rather than rely on memory of it)
and audited honestly. Confirmed no assumptions.py or checkpoint_solver.py exists anywhere in this
project (those are illustrative examples in the standards doc from a different reference context,
not literal files to check against here) and no other lp_package/ file duplicated the Sterling
constants -- Rule 6 not meaningfully violated.

REAL GAPS FOUND AND FIXED:
1. Rule 1 (OO structure): the module was free-standing functions plus plain data-container
   dataclasses, contradicting the precedent set two turns earlier for the parking-canopy module
   (same "we'll do this for other sites/counties" reusability rationale applies here). Refactored
   to SolarSiteProfile (the one class tied to a specific data source/format, via
   from_sam_export_yearly_files()) and ScaledSolarProfile (county/site-agnostic analysis methods:
   compute_duration_curve, compute_month_hour_heatmap, find_longest_low_output_streaks) -- mirrors
   the CountyParkingData/SolarCanopyDesign/ParkingCanopyAssessment pattern directly.
2. Rule 8.3 (source-category tagging): constants now explicitly tagged with their category from
   the established 12-category taxonomy (e.g. STERLING_NAMEPLATE_KW etc. tagged "Modeler
   Assumptions" -- direct user-provided input this round, not derived).
3. Rule 9 (physical invariants checked automatically): added
   ScaledSolarProfile._verify_output_does_not_exceed_fleet_capacity(), called automatically in
   __post_init__, raising (not warning) if scaled output exceeds fleet nameplate capacity by more
   than a stated 2% overirradiance tolerance. 5 new tests, including one confirming the real
   9-year Sterling data genuinely passes this check at real scaling factors.
4. Rule 10.2 (pointer to log entry): comments now reference this log's own entries by name for the
   two bugs fixed two turns ago (leap-day handling, gap-detection), rather than explaining the
   reasoning in prose alone with no pointer to go verify it in full.

Also fixed incidentally: filename_pattern is now a real, working parameter on
from_sam_export_yearly_files (Rule 8.1) rather than a hardcoded literal, tested directly.

VERIFICATION: refactor preserved all underlying logic exactly -- re-ran the real 9-year analysis
after the refactor and confirmed the duration curve and streak results are identical to the
pre-refactor figures reported last turn (75 hrs/2018-02-23 top streak, same duration-curve
percentiles), not just "tests still pass."

Test suite: 24/24 passing (18 prior + 6 new: filename_pattern test + 5 Rule 9 invariant tests).

## Worst-case flat-load shape + load-vs-solar gap analysis (session continued 2026-08-29)

User: for load, think worst case -- 90% load factor as standard. GS-5 data-center rate is fixed
for a decade so DA/RT pricing doesn't apply to that load (though the battery ASSET itself can
still chase price for arbitrage regardless of what's driving demand behind it -- kept distinct
from the load-side point). Confirmed local RT price as a decentralized proxy for local
transmission scarcity. Approach: build a load SHAPE, find where solar output is weakest relative
to it, defer actual Loudoun MWh magnitude to later. Clarified: "100%" is the real 2045 DOMLSE
profile's own peak (not an invented normalization), adjusted higher only at the lower hours until
the overall annual load factor reaches 90% -- confirmed as the intended floor-clip mechanic
(hours below a solved floor level, as % of peak, raised to that floor; hours already above are
untouched; peak itself never changes).

New modules, following the OO/Rule-1 precedent directly:
1. loudoun_streak_finder.py -- extracted the "find longest consecutive hours meeting a condition,
   respecting real time gaps" logic OUT of loudoun_solar_hourly_profile.py's
   find_longest_low_output_streaks (Rule 1: needed unchanged by the new gap-analysis module too,
   so shared rather than duplicated), generalized to support both at_or_below (original) and
   at_or_above (new, needed for gap severity) conditions. loudoun_solar_hourly_profile.py's
   ScaledSolarProfile.find_longest_low_output_streaks now delegates to this shared helper; all 24
   pre-existing tests re-run and confirmed to pass with byte-identical behavior after the
   extraction.
2. loudoun_load_shape_gap_analysis.py -- LoadProfile.from_domlse_export() loads the real 2045
   DOMLSE hourly shape (peak=29,587 MW, natural load factor directly verified at 79.4%, consistent
   with already-established 2040/2048 figures of 78.0%/79.8%), solves via bisection for the floor
   level (in % of peak) that produces exactly a 90% annual load factor when hours below it are
   raised to it, verifies the achieved load factor actually hits 90% before returning (Rule 9).
   Hour-label-to-timestamp mapping cross-checked against a real, known-sensible pattern (summer
   peak load falls in mid-late afternoon, hour 16-17) before trusting it. LoadSolarGapAnalysis
   combines this with the existing 9-year ScaledSolarProfile by mapping the single-year load shape
   onto each of the 9 real solar weather years via (month, day, hour), computing
   gap_pct = load_pct_of_peak - solar_pct_of_fleet for every hour -- both sides expressed as % of
   their own peak/capacity, no absolute Loudoun MW assumed anywhere, per direct user deferral.
   Reuses the shared streak-finder (at_or_above condition) to find the longest high-gap streaks.

REAL FINDING CAUGHT DURING THIS ROUND, not a bug -- an intentional, now-tested property: running
the real analysis at both established canopy MW scenarios (1,551.2 and 1,939.0 MW) produced
byte-for-byte IDENTICAL duration curves and streaks. Traced to the % framing itself being
scale-invariant by construction (solar_pct = mw/fleet_mw*100 -- numerator and denominator scale
together) -- confirmed as intentional given the user's own explicit deferral of absolute MW to a
later step, not a bug. Locked in with a dedicated test
(test_gap_pct_is_invariant_to_fleet_mw_choice) rather than left as an unexplained observation.

RESULTS (identical across both canopy MW scenarios, per the finding above): solved floor = 90.0%
of peak (very close to the target itself, since the natural profile was already fairly flat --
most hours get clipped to exactly the floor). Duration curve is heavily "squared off" at ~90 gap
points across the 75th-99th percentiles, since the load side is now pinned near its floor for the
large majority of hours -- meaning the ANALYSIS'S gap severity is now predominantly driven by
solar variability alone, not meaningful load-side variation, a direct and honest consequence of
how aggressively the 90% worst-case flattening compresses the load side. Longest gap>=80-point
streaks are consequently nearly identical to the raw low-solar-output streaks found two turns ago
(75 hrs Feb 2018, 71 hrs Sep 2018 and Dec 2018, 69 hrs Nov/Dec 2015, 68 hrs Jan 2013).

Test suite: 42/42 passing across all three modules (loudoun_solar_hourly_profile.py,
loudoun_streak_finder.py, loudoun_load_shape_gap_analysis.py).

Files: loudoun_streak_finder.py, test_loudoun_streak_finder.py, loudoun_load_shape_gap_analysis.py,
test_loudoun_load_shape_gap_analysis.py -- all in loudoun_solar_profile/. loudoun_solar_hourly_profile.py
and its tests updated in place (streak-finding now delegates to the shared helper).

## View #1 investigation, battery dispatch simulator built, real scale-mismatch bug caught and fixed (session continued 2026-08-29)

User asked for "View #1" from the VA SLCOE spreadsheet for the 5 identified low-output windows +/-
1 week each. Thorough search of VA_SLCOE_Model.xlsx (README, all sheet contents, defined names,
chart titles, full-workbook text search) found no sheet/range/chart/cell named "View #1" or
"Views" anywhere. Searched /mnt/transcripts/ (journal.txt catalog + full-text grep across all raw
transcripts) and found the real origin: a DIFFERENT, earlier file (Virginia_Grid_Analysis_Tracker.xlsx,
from the very first session of this project, not in current project KB) had a "Graphical Views" tab
with View #1 defined as: "stacked bar+line combo chart -- nuclear/battery discharge (by type)/wind/
solar as positive stacked bars, battery charging (by type) as negative bars, demand as a line, total
battery SoC as a line on a secondary 0-100% axis." Also confirmed VA_SLCOE_Model.xlsx itself contains
no hourly dispatch arrays for any year (largest sheet is 400 rows; nothing near 8,760) -- it's an
annual/checkpoint-year summary workbook, not a raw hourly-array container. Real README connection
also surfaced: the model's own established "design weather year" methodology (Apr 2016-Mar 2017,
cross-validated against 2013-14 Polar Vortex and a "2012-13 acute insolation lull" that may be the
same event as the independently-found Jan 2013 streak) -- not yet cross-checked against our own
finding, flagged for later.

Given the model has no nuclear/wind/battery-by-type hourly data for these specific historical
windows (they come from our own separate Sterling-solar analysis thread, not the model's own
checkpoint solves), user chose to build the real battery dispatch simulation first (rather than a
simplified partial View #1), following SES.

New module: loudoun_battery_dispatch.py. BatteryDispatchDesign (power_mw, duration_hours,
round_trip_efficiency_pct, starting_soc_pct=100% -- a well-operated battery assumed pre-positioned
full ahead of a known low-solar event) .simulate() against a LoadProfile + ScaledSolarProfile,
producing an hourly DispatchResult (load/solar/charge/discharge/SoC/residual_import). RTE default
(90%) sourced directly from VA_SLCOE_Model.xlsx's own Assumptions & Sources tab row 35
(sodium-ion/short-duration storage, the closest analog to a Li-ion-class parking-canopy battery),
per Rule 6 -- distinct from the model's own 80% figure for long-duration iron-air storage (row 39),
used for the long-duration comparison case here. Rule 9 invariants: SoC within [0, capacity], no
simultaneous charge+discharge (a real, previously-found bug class in this project's own broader
LP-model history, guarded against explicitly since this is an independent simulation that could
reintroduce it).

REAL BUG CAUGHT BEFORE PRESENTING RESULTS: first real-data run (all 5 windows, 4hr vs 100hr
battery) showed only a ~1.4% difference between durations -- directly contradicting the
already-established finding that duration matters a great deal at 63-75hr streak lengths. Traced to
a genuine ~19x scale mismatch: load_mw was read directly from LoadProfile's raw, absolute DOMLSE
value (Dominion-zone peak ~29,587 MW, the whole utility territory) while solar/battery were sized to
the Loudoun-specific canopy fleet (~1,551-1,939 MW) -- a battery matched to the solar fleet was
trivially overwhelmed by a load ~19x its own scale, regardless of duration. Root cause:
LoadSolarGapAnalysis (built earlier) deliberately worked in %-of-peak specifically to avoid needing
real Loudoun MW, but this new dispatch module needs both sides on ONE real MW scale to move real
MWh, and that distinction wasn't carried through when building it.

FIX, confirmed directly by user: load_mw now derived as load_pct_of_peak/100 * scaled_solar.fleet_mw
-- an explicit, STATED placeholder assumption (Loudoun's load peak assumed equal to the canopy MW
sized), not a rediscovery of real Loudoun load magnitude, which remains deferred per the user's own
earlier framing. New Rule 9 invariant added directly in response
(_verify_load_within_scale_assumption_bounds): load_mw can never exceed fleet_mw, catching exactly
the shape of this bug if it recurs.

RULE 3 IN ACTION: the existing synthetic tests built LoadProfile objects with only a raw "mw"
column, exactly matching what the buggy code read -- they would have kept silently passing with
the old, wrong assumption baked in. Rebuilt _make_load_profile/_make_scaled_solar to require
pct_of_peak directly and an independent fleet_mw parameter, then re-derived every hand-verified
expected value under the corrected logic. Added a direct test of the fix itself
(test_load_mw_derived_from_pct_times_fleet_mw_not_a_raw_absolute_value) and a direct test of the
new invariant (test_load_mw_exceeding_fleet_mw_raises, constructed using the old bug's exact
numbers -- load_mw=29,587 against fleet_mw=1,551.2 -- to confirm the check catches precisely that
failure mode).

RESULTS (corrected, all 5 windows, fleet_mw=1,551.2): 4-hr battery leaves 495,000-508,000 MWh
residual import per ~17-day window; 100-hr (80% RTE) battery leaves 346,000-359,000 MWh --
consistently a 29.3-30.1% reduction, directly supporting the user's stated hypothesis. Hours at 0%
SoC remain high (270-410 of ~408 total hours) even for the 100-hr battery, consistent with the
load side being pinned near its 90% floor for most hours while solar is frequently zero (nighttime)
-- a battery this size genuinely cannot fully cover a ~17-day window under the worst-case flat-load
assumption, which is itself an honest, informative finding, not a modeling failure.

Test suite: 17/17 passing for this module; 59/59 passing across all modules in loudoun_solar_profile/.

STILL OPEN: View #1 itself (the stacked bar+line chart) not yet built -- next step. Whether to add
a "Graphical Views" tab to VA_SLCOE_Model.xlsx itself (recreating the original tracker's View #/
Description structure) or deliver as an inline visual not yet decided.

Files: loudoun_battery_dispatch.py, test_loudoun_battery_dispatch.py -- in loudoun_solar_profile/.

## Virginia_Grid_Analysis_Tracker.xlsx recreated; View #1 built for all 5 windows (session continued 2026-08-29)

User: keep Virginia_Grid_Analysis_Tracker.xlsx up to date, and proceed building View #1 for the 5
previously-listed windows. Confirmed directly: the file is not currently in project KB or the
working directory -- everything known about it comes from the transcript search two turns ago.
Recreated it fresh (build_tracker.py, in loudoun_solar_profile/), with a "Graphical Views" tab
reproducing the original View #1/#2 definitions VERBATIM (not reworded) plus an explicit
Loudoun-adaptation note (nuclear/wind omitted -- statewide/Dominion-zone assets never modeled in
this local analysis, not fabricated or silently dropped), and one data sheet + native Excel combo
chart per window, using the real, already-verified 100-hr/80%-RTE dispatch results from last turn.

REAL CHART-BUILDING ISSUE CAUGHT AND RESOLVED (a misdiagnosis, not a code bug): first inspection of
the built chart via chart.series showed only 3 of the intended 5 series (missing the demand line
and SoC line), appearing to confirm the `bar += line_chart` combination had silently failed. Traced
via openpyxl's own source (ChartBase.__iadd__ vs __add__): explicit `+` between different chart
types correctly raises TypeError, but `+=` does NOT merge series into `.series` at all -- it
appends the other chart object to a separate `._charts` list, openpyxl's actual mechanism for
overlaying chart types on one plot area. Checking `.series` was checking the wrong attribute
entirely. Confirmed via `._charts` directly (3 entries: the bar chart itself, the demand line
sharing the primary axis, the SoC line on its own axId=200 secondary axis) that the original build
was structurally correct all along. Per the xlsx skill's own "a clean result isn't necessarily a
correct one" principle, went further and actually rendered the file (PDF export -> page images) to
visually confirm the combo chart displays correctly, rather than trust the object inspection alone.

REAL, HONEST FINDING surfaced by the visual render, verified against the underlying data before
presenting (not assumed from the picture): in every one of the 5 windows, the "Battery Charging"
series is entirely empty -- solar output never once exceeds the ~90%-of-peak flat load anywhere in
any 17-day window (e.g. Feb 2018: solar peaks at 1,212.8 MW vs. a constant 1,395.3 MW load), so the
battery never has an opportunity to recharge once depleted. SoC drops from 100% to 0% within the
first ~140 hours of every window and never recovers. A stark, direct consequence of the worst-case
90% flat-load assumption, not a modeling error.

Test suite (loudoun_battery_dispatch.py, etc.): still 59/59 passing, unaffected by this chart-layer
work. Workbook itself: recalc.py clean (0 formulas, 0 errors -- expected, since this is derived
simulation output, not a live formula model).

STILL OPEN: whether/how to build View #2 (weekly SoC by year); whether the Loudoun-adaptation
charts should also be added to VA_SLCOE_Model.xlsx itself, or remain solely in the recreated
tracker file per the user's original naming.

Files: Virginia_Grid_Analysis_Tracker.xlsx (new), build_tracker.py -- tracker in lp_package/,
build script in loudoun_solar_profile/.

## Real Virginia_Grid_Analysis_Tracker.xlsx uploaded; merged in rather than using the recreation; real View #1 spec discrepancy found (session continued 2026-08-29)

User uploaded their real Virginia_Grid_Analysis_Tracker_updated.xlsx and asked to preserve its
history rather than use last turn's from-scratch recreation. Confirmed by direct inspection: real
file has "Activity Tracker" (53 rows, a genuine 48-item project history from early bug fixes
through recent methodology work, with Seq/ID/Short Name/Description/Priority/Status columns and
real status codes), "Legend" (status-code definitions), and "Graphical Views" (matching the
transcript-reconstructed View #1/#2 text exactly, confirming that reconstruction was accurate as
far as it went -- see discrepancy below).

Checked real formatting conventions before adding anything (Rule: match existing conventions
exactly) -- header row Arial bold white-on-navy fill; DATA rows Calibri (not Arial), wrap_text,
specific wide column widths (C=39, D=126) for the long description fields. New Activity Tracker
row and Graphical Views pointer note built to match this real styling; the new View1_* sheets
(genuinely new sheets, no pre-existing convention to match) kept their own already-verified Arial
styling from last turn's build.

merge_into_real_tracker.py: loads the REAL uploaded file as the base (not the recreation), reuses
build_window_sheet from build_tracker.py unchanged (Rule 1), confirmed next ID=49/next row=54
directly rather than assumed, appended one new Activity Tracker row documenting this work
(matching real column/style conventions), added a pointer note to Graphical Views (not altering
the original View #1/#2 text). Verified directly: row 53 (original last row) unchanged, View #1's
original text unaltered, recalc clean (0 formulas/0 errors), and the actual Feb 2018 chart
re-rendered correctly within the real merged file (found via pdftotext page search rather than
guessing page numbers, after an earlier verification-copy attempt showed a misleading render --
traced to that copy being a separate, standalone workbook with none of the source data sheets
present, so the chart's cross-sheet references were genuinely dangling in that copy specifically,
not in the real merged file).

REAL, IMPORTANT DISCREPANCY FOUND: pulling the View #1 text directly from the real file (not the
transcript-reconstructed version) revealed it has evolved since the early-session version found
via transcript search two turns ago -- the current spec adds (1) "gas" to the positive stack
between battery discharge and wind, and (2) "hourly curtailment (replaces export, which no longer
exists in the corrected no-export model) as a negative bar alongside battery charging." Gas: would
be omitted for the same already-stated reason as nuclear/wind (not modeled in this Loudoun-specific
local analysis). Curtailment is different and more consequential: a real, computable quantity
(excess solar the battery couldn't absorb, i.e. excess - charge_mw within simulate()'s existing
charging branch) that loudoun_battery_dispatch.py does not currently track or output at all --
a genuine gap in the underlying dispatch simulation's output, not just a chart-labeling fix. Not
yet resolved -- flagged directly to the user rather than silently shipped incomplete or unilaterally
rebuilt.

Files: Virginia_Grid_Analysis_Tracker_updated.xlsx (the real file, now containing both the
original history and the new View1_* work), merge_into_real_tracker.py -- tracker in lp_package/,
script in loudoun_solar_profile/.

## Curtailment added to dispatch simulation and all 5 View #1 charts (session continued 2026-08-29)

User: add curtailment. Added curtailment_mw to loudoun_battery_dispatch.py's simulate() -- excess
solar the battery couldn't absorb (excess - charge_mw, computed inside the existing net<0 branch),
per the real View #1 spec text found last turn ("hourly curtailment (replaces export, which no
longer exists in the corrected no-export model) as a negative bar alongside battery charging").

Derived and added a materially stronger Rule 9 invariant alongside simple curtailment
non-negativity: a full hourly energy-balance closure check
(solar+discharge+residual_import == load+charge+curtailment, within tolerance), verified to hold
exactly in both branches of simulate()'s own logic before implementing. This is a genuinely
stronger check than curtailment alone -- it verifies the entire dispatch loop's internal
consistency every hour, not just this one new field.

RULE 3 IN FULL EFFECT: every synthetic DispatchResult constructor in TestPhysicalInvariants needed
curtailment_mw added (would otherwise KeyError against the new invariants). More significantly,
test_valid_result_does_not_raise's original synthetic numbers turned out to not even be
RTE-consistent once actually checked against the new energy-balance invariant -- a real gap in the
original test that no check had been able to surface before this round. Rebuilt with 100% RTE
explicit and both hours' full energy balance hand-verified before writing. Added 4 new tests
(curtailment when excess exceeds battery ability to absorb, negative-curtailment invariant,
energy-balance-violation invariant, real-data energy-balance+curtailment sanity check) -- caught one
real bug in my own new test while writing it (test_curtailment_when_excess_exceeds_battery_ability_
to_absorb used power_mw=100 instead of the intended 10, so the battery fully absorbed the excess
instead of being headroom-limited as the test name claimed -- fixed before it shipped). Test suite:
21/21 passing for this module; 63/63 across all modules.

Chart-building updated (build_tracker.py): curtailment inserted as a new negative-bar column
between battery charging and demand; all downstream column references (SoC line, chart anchor,
column widths) shifted accordingly. Adaptation note updated to state gas is also consciously
omitted (same reasoning as nuclear/wind) and that curtailment IS included per the real spec.

Second pass against the ALREADY-MERGED real tracker file (not the original upload again, which
would have duplicated the first Activity Tracker row): new script
add_curtailment_to_tracker.py removes and rebuilds the 5 View1_* sheets with curtailment included,
updates the existing Graphical Views pointer note in place (rather than appending a redundant
second one), and logs this as a NEW, separate Activity Tracker entry (ID=50, "Add curtailment to
View #1 dispatch simulation") rather than editing the ID=49 entry -- consistent with the real
tracker's own established practice of logging each fix as its own item, not rewriting prior ones.

RESULT: curtailment is exactly 0.00 MWh in all 5 windows -- consistent with, and a direct
confirmation of, the already-established finding that solar never once exceeds the worst-case flat
load in any of them, so there was never any excess to curtail in the first place. Recalc clean (0
formulas/0 errors). Chart verified via PDF page search (found via searching for the literal
"Curtailment (MW," column header text in the data table, then cross-referenced against the
"Battery Charging" text to land on the correct chart page): structure consistent with the
pre-curtailment version; the curtailment series itself is invisibly flat at zero, which is
expected and correct given the underlying finding, not a rendering gap.

Files: loudoun_battery_dispatch.py, test_loudoun_battery_dispatch.py (updated in place),
build_tracker.py (updated in place), add_curtailment_to_tracker.py (new),
Virginia_Grid_Analysis_Tracker_updated.xlsx (updated in place, now with 2 Activity Tracker
entries and curtailment-inclusive View1_* charts).

## PJM transmission planner user story: incremental-buildout dependable-capacity simulator built (session continued 2026-08-29)

User presented a user story ("as a PJM transmission planner...LSRV rates...") and asked for
clarification before proceeding. Checked existing assumptions first: found this project already
has a real, sourced LSRV figure ($36.864/kW-yr, VA_SLCOE_Model.xlsx Scenario 3's "Locational Value
Adder Sensitivity") -- but flagged directly that LSRV is a NY/NYISO tariff mechanism, not a native
PJM concept, and that figure is explicitly documented there as a NY benchmark/proxy, not a
PJM/Virginia-specific rate. User confirmed proceeding on that basis.

Clarified over several turns: (1) MWh on an hourly basis, not annual (annual doesn't show
point-in-time performance); (2) rooftop + parking-lot combined (1,357.2 + 1,551.2 = 2,908.4 MW
combined fleet); (3) a 2045 system built out incrementally, fleet size only varies by year; (4)
cost-effectiveness framing confirmed -- "whatever the lowest contribution to demand over the []
period would define the maximum capacity to rely on," explicitly not an official reliability test
like ELCC, a deliberate simplification for now; (5) SoC starts at 50%, never reset at year
boundaries (a real, meaningful change from the 100%-start assumption used in the single-window
work, which fit a "pre-positioned ahead of a known event" scenario that doesn't apply to a
continuous multi-year run).

Weakest-year discussion: checked total annual solar output under both calendar-year and this
project's own established Apr-Mar fiscal-year boundary -- 2018 is weakest under both conventions
(117 vs 118 MWh-equivalent), and is also the year containing the already-identified worst single
streak (75hr Feb 2018), two converging signals. User's refinement: rather than committing to one
weakest year, run ALL candidate weather years (the 9 real calendar years 2012-2020, plus the
project's own independently-established Apr2016-Mar2017 "design weather year" from the broader
model's README) and take the single worst dependable-capacity result across all of them --
correctly anticipating that a year weakest by annual total isn't guaranteed weakest at every fleet
size across a 19-year buildout, and specifically naming 2016-2017 (this model's own separately-
derived worst case) as a real candidate for divergence from the 2018 pick.

ABSTRACTION-BOUNDARY CORRECTION (user pushed back directly, twice, on "extend the class" and then
on my first proposed helper boundary): the per-hour dispatch step is NOT one shared blob -- it
splits into (A) input resolution (fixed-scale lookup in simulate() vs. year-aware rescaling in the
buildout case, genuinely different between callers) and (B) the pure charge/discharge/curtailment/
SoC math given already-resolved inputs (genuinely identical between callers). Extracting the whole
per-hour step as originally proposed would have relocated the branchy-method problem one layer
down rather than solving it. Corrected to a narrow @staticmethod, _dispatch_one_hour(solar_mw,
load_mw, current_soc, energy_capacity, power_mw, rte_fraction), taking power_mw as an explicit
parameter (not self.power_mw) specifically so the buildout caller can vary it per year without
needing a different design instance each time. simulate() refactored to call it; all 63
then-existing tests re-verified to pass with byte-identical behavior before building anything new
(Rule 3/4).

BUILT (all in loudoun_battery_dispatch.py, following Rule 1 -- extending the existing class/module
rather than creating parallel structures):
- _dispatch_one_hour: the extracted pure helper, now independently unit-testable (3 new direct
  tests) rather than only verifiable indirectly through full simulations.
- compute_linear_buildout_schedule: standalone function (2026->0 MW to 2045->2,908.4 MW), matching
  the standalone-function pattern already used for _solve_floor_pct_for_target_load_factor.
- extract_hydro_year_window: pulls an Apr1-Mar31 window out of a multi-year SolarSiteProfile,
  reusing the existing class rather than building a new one -- used for the Apr2016-Mar2017
  candidate specifically.
- simulate_with_incremental_buildout: one continuous multi-year run, repeating one weather year's
  shape once per build-out year, each rescaled via the EXISTING SolarSiteProfile.scale_to_fleet_mw
  (reused, not reimplemented -- gets that method's own overirradiance Rule-9 check for free every
  year as a side benefit), SoC carrying continuously across every year boundary starting at 50% in
  year 1 only. self is treated as the end-state (2045) design; only duration_hours and RTE are held
  fixed across years, power_mw/energy capacity scale via the schedule under the established 1:1
  solar:storage pairing convention.
- IncrementalBuildoutDispatchResult: a NEW dataclass, deliberately not a reuse/subclass of
  DispatchResult, since its Rule 9 invariants are genuinely different in shape (fleet_mw varies
  PER ROW here, so every capacity/load bound must be checked row-by-row against that row's own
  fleet_mw, not one global scalar) -- same "don't force two different shapes into one structure"
  principle just established for the helper-boundary correction, applied a second time.
  dependable_capacity_mw property: single lowest hourly (solar_mw + discharge_mw) across the full
  run, per direct user framing.
- find_worst_dependable_capacity_across_candidate_years + WorstCaseAcrossCandidateYearsResult:
  runs the buildout simulation once per candidate weather year, returns the single worst result
  plus all individual results for inspection.

Test suite: 44/44 passing for this module (up from 21), 86/86 across all modules in
loudoun_solar_profile/.

Files: loudoun_battery_dispatch.py, test_loudoun_battery_dispatch.py (both substantially extended
in place).

## Degenerate metric caught on first real run, fixed to per-year evaluation (session continued 2026-08-29)

First full run of find_worst_dependable_capacity_across_candidate_years (all 10 candidates:
2012-2020 + Apr2016-Mar2017) returned exactly 0.00 MW for every single candidate -- not a genuine
finding. Traced directly: the single-global-minimum metric (min of solar+discharge across the
ENTIRE 20-year run) is mechanically dominated by build_out_year=2026's own trivial fleet_mw=0.0
starting condition every time, regardless of how the system performs in any later, meaningfully-
built-out year -- a real gap in the metric's own design (present since the metric was confirmed
two turns before the buildout dimension was added), not a code bug, only visible once real data
was run. Flagged directly and owned as something that should have been caught during design,
before building.

User confirmed the proposed fix: evaluate dependable capacity PER BUILD-OUT YEAR rather than one
global minimum. Implemented:
- IncrementalBuildoutDispatchResult.dependable_capacity_mw/dependable_capacity_hour (the old,
  now-confirmed-degenerate single-number properties) REMOVED entirely rather than kept alongside
  the fix -- keeping both would invite exactly the "someone calls the wrong one" bug this fix
  exists to prevent.
- dependable_capacity_by_year (new): groupby on build_out_year, min of (solar_mw+discharge_mw)
  within each year's own hours only.
- dependable_capacity_hour_by_year (new): same grouping, returning full row detail per year.
- final_year_dependable_capacity_mw (new): convenience accessor for the last/fully-built year
  specifically -- proposed as the headline comparison figure (the fully-built system's own worst
  case is what's actually relevant to "how much can we rely on once built"), stated explicitly in
  the docstring as a deliberate but not separately-reconfirmed choice, since the full per-year
  series remains available regardless and this choice is cheap to revisit later.
- find_worst_dependable_capacity_across_candidate_years / WorstCaseAcrossCandidateYearsResult
  updated to compare candidates on final_year_dependable_capacity_mw instead of the removed
  property.

RULE 3: ran the full suite before touching tests, to find exactly which broke rather than guess --
exactly the 2 tests that touched the removed property, both reworked (not just renamed) to
genuinely exercise the per-year distinction: the first now uses two build-out years with different
minimums (the original only had one year, so it never actually tested "per-year, not global");
added a dedicated multi-year test for final_year_dependable_capacity_mw that also asserts the
result does NOT equal a different year's value, ruling out "always returns some other year by
coincidence" false passes.

Test suite: 46/46 passing for this module, 88/88 across all modules.

Files: loudoun_battery_dispatch.py, test_loudoun_battery_dispatch.py (both updated in place).

## Rationale: real Loudoun load magnitude (~22.9 GW by 2045), replacing the load/fleet coupled scale assumption (session continued 2026-08-29)

### The problem this resolves

The first full 10-candidate dependable-capacity run returned exactly 0.00 MW for every candidate,
every build-out year including 2045. Traced precisely: load was derived as
`load_pct_of_peak * fleet_mw` -- the SAME fleet_mw as the solar/battery build-out -- so load and
solar's ratio at any hour is scale-invariant (fleet_mw cancels out of both sides). Checked directly:
Sterling's real peak output only ever reaches ~82.7% of its own nameplate (realistic for a real PV
system -- inverter clipping, temperature derating, real irradiance never quite hitting STC), while
the load floor sits at 90% of peak. Since 82.7% < 90% structurally, solar can never once exceed
load at ANY fleet size -- confirmed directly: total battery charge across the entire 175,200-hour,
20-year run was exactly 0.0000 MW. Not a bug; a real, mechanical consequence of coupling load's
scale to the same fleet_mw as solar/battery. User's framing: this needs a real, independent load
magnitude, not a placeholder tied to the fleet being sized.

### Search process

1. Checked project KB first, per Rule 6 (single source of truth) -- both PDF-named IRP documents
   in project KB turned out to be mislabeled, not actually valid PDFs (pdfinfo/pdffonts both
   failed with trailer-dictionary errors). Investigated rather than giving up:
   2025_Integrated_Resource_Plan_Update.pdf is plain text (readable directly via grep);
   2025_Dominion_VA_NC_Plan_Update.pdf is a page-image+OCR-text ZIP archive (extracted and read
   all 7 pages' text). Neither contains Loudoun-specific load data -- only Dom-zone/company-wide
   figures (a real, useful one found along the way: PJM-derived DOM Zone coincident peak load
   growth of 4.1% CAGR over a 20-year horizon, from the 2025 VA/NC IRP Update filing overview
   deck) and, in the first file, unrelated Loudoun-substation transmission-line-upgrade cost line
   items (real but not load data).
2. User provided PJM Data Miner 2's own stated confidentiality policy: nodal load (load at an
   individual location) is confidential in PJM's public data release, as are individual generator
   output and RPM capacity commitments. This closes off the "find an official, granular PJM source"
   path definitively -- a standard confidentiality carve-out across ISO/RTO markets generally, not
   a PJM-specific gap, so not expected to be found via any other official market-operator channel
   either.
3. Web search found real, sourced Loudoun-specific AGGREGATE (not hourly) power figures:
   - Loudoun County's own government strategic report (June 2024 Board of Supervisors item,
     "Loudoun County - Data Center Capital - A Strategy for a Changing Paradigm"): the county will
     require approximately 11.56 GW of power. Per user-provided additional context: this is
     specifically a **2028 projection**, not a current or 2045 figure, calculated by extrapolating
     Dominion's own reported historical trajectory (1 GW in 2018 -> ~3.4 GW by 2023, a 340%
     increase over 5 years) forward. Cross-validated within the same report by an independently
     commissioned Kimley-Horn consulting estimate of 11.59 GW over the same timeframe -- genuinely
     two different methodologies landing on nearly the same number.
   - NREL/DOE Grid Deployment Office data (via a Visual Capitalist visualization): Loudoun has
     ~6,000 MW active + ~6,300 MW planned capacity (~12.3 GW). HONEST CORRECTION made this round:
     initially presented as a second, independent confirming source; user-provided context shows
     this is described as tracing toward "the same 11.56 GW to 12 GW... baseline" -- i.e. likely
     the same underlying trajectory viewed through a different lens (capacity pipeline vs. direct
     demand projection), not independent corroboration. Should not have called the earlier
     convergence "reassuring" without checking whether the two were actually independent.
   - A third, smaller figure found and explicitly NOT used, to avoid conflating it with the above:
     the Piedmont Environmental Council's "~300 MW, approximately the same amount of energy needed
     to power Loudoun County" almost certainly refers to the county's own non-data-center
     household/commercial load specifically (it is ~38x smaller than the aggregate figures above),
     not total demand including data centers.

### Growth-rate math (verified via code, not by hand)

- 2018 -> 2023 (1 GW -> 3.4 GW, 5 years): implied CAGR = 27.7%
- 2023 -> 2028 (3.4 GW -> 11.56 GW, 5 more years): implied CAGR = 27.7% -- the SAME rate in both
  segments. Honest note on the source's own description: it calls this a "linear growth
  extrapolation," but the math that actually reproduces both segments is compound/exponential (a
  steady % rate, not a steady absolute GW increment) -- a real, worth-flagging discrepancy in the
  source's own terminology, not something to silently smooth over.
- Naive continuation of the same 27.7% CAGR another 17 years to 2045: 741.3 GW -- implausible on
  its face (data-center growth cannot compound at ~28%/yr indefinitely given real-world grid/land/
  cooling-water constraints), ruled out as an extension method.
- Held flat at 11.56 GW through 2045: the most conservative option, but doesn't reflect the
  established (if decelerating) growth trajectory at all.
- **Chosen approach**: grow the 2028 anchor (11.56 GW) forward to 2045 at Dominion's own,
  already-established, already-sourced SYSTEMWIDE DOM Zone coincident-peak CAGR of 4.1% (from the
  same 2025 IRP Update deck found earlier this round) -- reusing an already-sourced rate rather
  than inventing a new one (Rule 6), while being honest that applying a systemwide average rate to
  a locality that has clearly been growing far faster than that average is itself a real
  simplifying assumption, not a precise Loudoun-specific growth forecast.
  Formula: 11.56 * (1.041)^17 = **22.89 GW by 2045**.

### Decision

User confirmed: use the ~22.9 GW (Dominion systemwide-CAGR-grown) figure as Loudoun's real,
independent load magnitude for 2045, decoupled entirely from the solar/battery fleet's own
build-out schedule -- replacing the earlier `load_pct_of_peak * fleet_mw` coupled-scale
placeholder. Implementation (updating loudoun_battery_dispatch.py to use this real, independent
magnitude instead of the coupled scale assumption) is a separate, not-yet-started next step.

### 2026-2027 values (filling the gap before the 2028 anchor)

The 2028 anchor (11.56 GW) and 2045 endpoint (~22.89 GW) leave 2026-2027 undefined -- both years
fall BEFORE the real anchor point, not after it. User asked whether to "simply extend the linear
relationship." Flagged directly rather than assumed: everything established so far (both the
original 2018-2028 trajectory and the new 2028-2045 extension) is actually COMPOUND (a steady %
rate), not literally linear (a steady absolute GW/year) -- so "linear" was genuinely ambiguous
given the project's own prior work. Computed three real candidates before proposing one:
- Back-extend at the ORIGINAL 27.7% CAGR (the 2018-2023-2028 trajectory itself): 2026=7.09 GW,
  2027=9.05 GW. Rejected: reuses the steep early-hypergrowth rate already ruled out as implausible
  for the forward direction (741 GW by 2045 if naively continued) -- applying it backward while
  rejecting it forward would be a real methodological asymmetry.
- Back-extend at the SAME 4.1% Dominion systemwide CAGR used for the 2028->2045 segment:
  2026=10.67 GW, 2027=11.11 GW.
- Literally linear (constant GW/year, derived from the 2028->2045 segment's own average rate of
  0.666 GW/yr): 2026=10.23 GW, 2027=10.89 GW.

**User decision: option B (the 4.1% CAGR back-extension)** -- the most internally consistent
choice, since the entire 2026-2045 series now uses ONE single rate (Dominion's own, already-
sourced 4.1% systemwide CAGR), anchored at the one real data point (11.56 GW in 2028), rather than
introducing a third, different rate just for two years.

### Final load-magnitude series (all years, formula-derived from the single 4.1% CAGR anchored at 2028)

| Year | GW |
|---|---|
| 2026 | 10.67 |
| 2027 | 11.11 |
| 2028 | 11.56 (real, sourced anchor) |
| ... | (compound growth at 4.1%/yr) |
| 2045 | 22.89 |

Full rationale for the anchor value, its provenance, the systemwide 4.1% CAGR's own sourcing, and
the rejected alternatives is documented in the section immediately above this one. Implementation
(replacing the coupled `load_pct_of_peak * fleet_mw` placeholder in loudoun_battery_dispatch.py
with this real, independent load-magnitude series) remains the next, not-yet-started step.

## Load-magnitude decoupling implemented; multi-day solar-firming module built (session continued 2026-08-29)

Implemented the load-magnitude decoupling designed in the prior entry: loudoun_battery_dispatch.py's
simulate_with_incremental_buildout() now takes a new required loudoun_load_peak_mw_schedule
parameter, deriving load_mw as load_pct_of_peak * loudoun_load_peak_mw (the real, independent
series) instead of the old, degenerate load_pct_of_peak * fleet_mw. New constants
LOUDOUN_LOAD_ANCHOR_YEAR/MW/ANNUAL_GROWTH_RATE (2028, 11,560 MW, 4.1%) plus
compute_anchored_compound_growth_schedule() -- a standalone function distinct in kind from
compute_linear_buildout_schedule (compound, anchored at one real point, not a two-endpoint linear
interpolation), verified via code to exactly reproduce the earlier hand-computed/logged values
(2026=10.67, 2027=11.10, 2028=11.56, 2045=22.89 GW). IncrementalBuildoutDispatchResult's per-row
load-bound invariant renamed and re-derived to check loudoun_load_peak_mw (the correct bound now)
instead of fleet_mw (the solar/battery side's own, now-genuinely-decoupled scale).

Scoping decision made explicitly: simulate() (the original single-window method, used for the
already-delivered 5 View #1 charts) was left UNCHANGED -- the fix only touches
simulate_with_incremental_buildout, since the user's instruction was specifically in that context,
and changing simulate() would have silently altered already-delivered results never asked to be
revisited.

Flagged proactively, before running anything: Loudoun's real load (~10.7-22.9 GW) vastly exceeds
the solar/battery fleet's own peak (2,908.4 MW, ~2.9 GW even at full 2045 build-out) -- so solar can
still never exceed load at this scale either, and the battery is expected to still never charge.
Not a bug recurring a third time -- the honest, correct answer once real-world magnitudes are used
on both sides: Loudoun's actual data-center-driven load is simply far larger than any plausible
rooftop+parking-canopy deployment on its own.

RULE 3: this change broke 11 existing tests (construct-synthetic-hourly-dataframe tests missing the
new loudoun_load_peak_mw column, plus two orchestration tests missing the new required schedule
parameter). All 11 reworked properly (not patched around) across two turns -- interrupted mid-way
through by the solar-firming digression (see below), finished on return. Full suite: 52/52 in
loudoun_battery_dispatch.py's own test file, 119/119 across the whole directory.

### Multi-day solar firming module (new, separate concern -- does not touch the Loudoun load series)

User asked whether treating solar as "firmed" over a 72-hour lookahead (uploaded document: MPC/
rolling-horizon battery dispatch, "weather uncertainty buffering") could minimize the low troughs
found in the incremental-buildout work. Initial answer: no, evaluated against Loudoun's full load --
a firming algorithm can only redistribute EXISTING excess energy across time, and solar never once
exceeds Loudoun's real load at any hour (confirmed: ~22.5% of load's own lowest point in the series,
even at solar's realistic peak), so there's no excess for any algorithm to work with there.

User corrected the framing directly: the real mechanism is a SELF-IMPOSED commitment ceiling (a
day-ahead firm delivery promise), not a comparison against Loudoun's load at all -- "solar minus
whatever conservative firm level the facility itself chose to promise," a self-contained property
of the solar+battery system alone, unrelated to the Loudoun load series. Design confirmed over
several turns: (1) chained SoC across days (>= 72-hr lookahead), (2) flat commitment per day, (3)
optimize the blended split between a 10-hr (sodium-ion, 90% RTE, VA_SLCOE_Model.xlsx row 35) and
100-hr (iron-air, 80% RTE, row 39) sub-fleet, maximizing the WORST daily combined firm level across
the record (direct user framing: "if we are trying to identify the highest level of transmission
avoidance").

New module loudoun_solar_firming.py, built incrementally, each piece tested before building on it:
- _can_hold_flat_level_without_shortfall / solve_max_flat_level_for_window: pure, non-mutating
  "what-if" feasibility check and bisection solver, reusing BatteryDispatchDesign._dispatch_one_hour
  directly (Rule 1) -- identical physics to every other dispatch path in this project.
- _extract_consecutive_hour_window: reuses the SAME continuity-verification principle already
  established in loudoun_streak_finder.py (a real bug found and fixed there once: positional
  adjacency in concatenated multi-year data is not genuine 1-hour temporal adjacency) -- applied
  here to a fixed-length lookahead window rather than a variable-length streak.
- compute_chained_daily_firm_levels: the core chained, day-by-day solver. Central behavior
  hand-verified precisely BEFORE writing the test (see chat trace): a 5-day pattern with solar=20
  for days 1-2, solar=0 for day 3 (the "storm"), solar=20 for days 4-5, power=100 (not binding),
  energy_capacity=24 MWh, starting SoC=100%, RTE=100% -- days 1-3 (every day whose 72-hr lookahead
  includes the storm) are all pulled down to EXACTLY 1.0 MW flat, even though solar itself is 20 MW
  on days 1-2 -- directly confirming the "weather uncertainty buffering" behavior the uploaded
  document describes. A real edge-case bug found and fixed in this same function: zero-qualifying-
  days produced a KeyError (pd.DataFrame([]).set_index("date") has no columns to index) rather than
  a sensible empty result -- fixed to return an explicitly-typed empty Series.
- find_optimal_blended_split: grid search (not gradient-based -- the objective, a minimum over
  thousands of daily values, is likely not smooth) over the split fraction, cross-checked at both
  0% and 100% against direct compute_chained_daily_firm_levels calls (Rule 4) to confirm the
  wrapper doesn't silently alter the underlying per-day solve.

REAL, GENERALIZABLE FINDING (not a code bug -- an incorrect test assumption was the actual bug):
under a strict worst-day objective, pure long-duration (100% iron-air) dominates any blend,
confirmed directly on two genuinely different constructed patterns (one with a 3-day trough, one
with only isolated 1-day dips and no multi-day event at all) -- worst_daily_firm_level is
monotonically non-increasing as split_fraction_short rises from 0% to 100% in both cases. Reason:
since both sub-fleets share one total MW pool, reallocating MW from 100-hr to 10-hr duration loses
10x its energy-storage capacity to gain only a 10-point RTE improvement -- nowhere near enough to
compensate under a worst-day objective, since the worst day is bounded by how much stored energy is
available to draw down, not how efficiently it was charged. An earlier version of the relevant test
wrongly assumed a genuine interior optimum would exist; fixed to assert the real, verified property
instead of an incorrect a priori expectation.

Real-data runtime measured directly (not estimated) on a small slice: ~1.9-2.5 ms/day -> extrapolated
to ~4.4 minutes for the full 9-year x 2-sub-fleet x 21-grid-point search -- confirmed feasible to run
as-is before committing to it.

Test suite: 25/25 in loudoun_solar_firming.py; 119/119 across the whole directory including this
new module.

STILL OPEN: the full, real 9-year x full-grid firming analysis has not yet been run -- everything
built and verified so far uses synthetic and small real-data slices only.

Files: loudoun_battery_dispatch.py, test_loudoun_battery_dispatch.py (both updated in place),
loudoun_solar_firming.py, test_loudoun_solar_firming.py (both new).

## Real bug found on first full 9-year firming run: break vs. skip at mid-record gaps (session continued 2026-08-29)

First full run of find_optimal_blended_split on the real 9-year Sterling record (2012-2020,
78,840 hours) completed suspiciously fast (4.5s vs. ~276s extrapolated from the measured per-day
rate) and every grid point showed only 57 days of results -- not the ~3,285 expected. Also showed
pure short-duration (100% sodium-ion) as optimal, the opposite direction from the earlier synthetic
tests (pure long-duration dominant) -- a real, suspicious discrepancy that warranted investigation
before presenting anything, not acceptance at face value.

Traced directly: the 9-year concatenated data itself was fine (verified: 78,840 hours, exactly 3
real gaps, all at the expected Feb-29 leap-year drops, no duplicates/ordering issues). The bug was
in compute_chained_daily_firm_levels's own main loop: _extract_consecutive_hour_window returns None
for two genuinely different reasons (out of future data entirely, vs. enough rows remaining but a
gap falls within this specific window), and the loop used `break` for both cases identically. A
mid-record gap should only skip that one starting position (later positions past the gap may still
be fully valid) -- but `break` halted the ENTIRE loop at the first gap encountered anywhere, which
for the real record meant the 2012 Feb-29 gap (day ~58) discarded 2013-2020 entirely, explaining
both the 57-day count and the fast runtime.

FIX: distinguished the two cases explicitly. `i + lookahead_hours > len(df)` (genuinely out of
data) still breaks -- no later position could ever succeed either. A mid-record gap now does
`i += 24; continue` -- skip just this one day, keep processing. Documented explicitly in the
docstring: SoC stays frozen (not fabricated, not reset) across any skipped day(s), picked back up
by the next successfully-processed day.

RULE 2/3: the existing gap-in-data test was too weak to have caught this -- it only asserted
len(result) > 0 and that qualifying days had the right value, never checking HOW MANY days
qualified or whether days from the FAR SIDE of the gap were present at all (both would pass
trivially even with the bug, since some early, before-the-gap days did produce valid results).
Rewrote the test with 10 days before and 10 days after a real gap, explicitly asserting far-side
dates (e.g. Jan 16, Jan 20) are present in the result -- confirmed directly (not assumed) that this
new test actually fails against the reverted, buggy code before restoring the fix, then re-confirmed
25/25 passing with the fix restored, 119/119 across the whole directory.

Files: loudoun_solar_firming.py, test_loudoun_solar_firming.py (both updated in place).

### Real 9-year multi-day firming result

With the fix in place, re-ran the full real analysis: 9-year Sterling record (2012-2020, 78,840
hours), total_mw=2,908.4 (the established combined rooftop+parking-canopy fleet), split_step_pct=5%.
Runtime 244s (~4.1 min), matching the extrapolated estimate closely -- confirms the fix processes
the full record correctly (3,277 days per grid point, vs. ~57 before the fix).

RESULT: optimal split is 100% short-duration (sodium-ion, 10-hr, 90% RTE) / 0% long-duration
(iron-air, 100-hr, 80% RTE) -- worst_daily_firm_level_mw is monotonically INCREASING from 71.59 MW
(0% short) to 77.85 MW (100% short) across the full grid, the OPPOSITE direction from the earlier
synthetic-pattern finding (where pure long-duration dominated). Investigated directly rather than
just reported: checked whether the real 9-year record actually contains multi-day drought events
analogous to the synthetic "storm" test pattern. It does not -- only 7 of 3,285 days ever have a
daily max solar output below the optimal firm level itself (77.85 MW, just 2.68% of the 2,908.4 MW
fleet), and the longest streak of consecutive days with daily max solar under a generous 500 MW
threshold is only 4 days. Real Sterling weather essentially always gives the battery a genuine
daily recharge opportunity at this very low committed firm level, so the extra energy-storage
capacity of long-duration chemistry goes largely unused, while the higher RTE of short-duration
storage compounds across thousands of real daily cycles -- the opposite mechanism from the
synthetic "3-day storm" pattern, which was specifically constructed to require bridging a multi-day
drought the real 9-year record simply does not contain at this magnitude/location.

Daily firm-level distribution at the optimum (100% short-duration): min=77.85, 5th pct=161.90,
25th pct=281.99, median=399.63, mean=398.47, 75th pct=508.12, max=836.89 MW.

Files: firming_daily_results_fixed.csv (the full 3,277-day daily series at the optimal split) --
in /home/claude/work/, not yet copied to outputs/.

## Fairfax C&I rooftop module built; "combined" mean+median fix applied to both counties via a shared class hierarchy (session continued 2026-08-30)

Built fairfax_ci_rooftop_solar_estimate.py: converts the already-filtered C&I building footprint
population (4,510 buildings >=600 sq ft, Commercial/Industrial/Hotel/Health, deduped by
max(Shape__Area) per unique Building Identification Number to handle podium/multi-component
structures) into MW/MWh. Reuses NEM_DISTRIBUTED_SOLAR_CAPACITY_FACTOR, HOURS_PER_YEAR, and the
real 8-point NVRC_SAMPLE_KW_DATA_POINTS directly from loudoun_ci_rooftop_solar_estimate.py (Rule
6) rather than duplicating them. New: NVRC_SAMPLE_ROOF_SQFT_DATA_POINTS, the roof-sqft half of the
same 8 real NVRC data points (from loudoun_test_batch_results.md, not previously extracted into
code since Loudoun's own use case only needed the flat kW values) -- paired with the existing kW
points to derive a kW/sqft DENSITY rate, since Fairfax's source data (unlike Loudoun's
business-license records) already gives real per-building footprint area directly, so what's
needed is a rate to convert known area into kW, not a flat per-building figure.

User pushed back hard, correctly, on two things in sequence:

1. Provided real ArcGIS REST API call sequences (geocode -> BuildingFootprintCO2 FeatureServer
   query) as a path to pull genuine per-building NVRC data instead of relying on the 8-point
   sample. Tried directly: bash_tool's network confirmed rejects services5.arcgis.com ("Host not
   in allowlist"); web_fetch rejected all three query URLs (including the shortest) as too long.
   Confirmed this exact limitation was already known and documented in
   query_nvrc_building_footprints.py's own header comment from an earlier session ("cannot be run
   inside Claude's own sandboxed environment"). Also surfaced from that script's own docstring: an
   unresolved internal discrepancy in the NVRC sample itself (one point's "Area" attribute didn't
   match its own geometry-derived area, a 1.66x difference) -- the 8-point sample has its own
   internal question mark, independent of the small-n/geographic-narrowness caveats already
   carried forward.

2. Directly challenged the "total_mw_combined" property (simple average of mean-based and
   median-based totals) -- correctly identified this as statistically unjustified. Worked through
   why explicitly: when scaling a per-unit rate across a KNOWN, FIXED total (building count or
   footprint area) to estimate a SUM, the sample mean is the correct, unbiased estimator -- the
   sample median is a BIASED estimator of that same sum whenever the sample is skewed (true for
   both counties' own samples: Loudoun's raw kW spans ~23x min-to-max, Fairfax's derived kW/sqft
   ratios span ~2.5x), since median-based scaling implicitly assumes a symmetry the data doesn't
   have. Averaging a correct estimator with a biased one produces an undefined third number, not a
   more conservative one. This exact flawed pattern existed in loudoun_ci_rooftop_solar_estimate.py
   too (Fairfax's module was built by mirroring it) -- user explicitly asked for the fix to be
   applied "so it is defensible, and so we can reuse the logic in our software class hierarchy."

RULE 1 REFACTOR: built rooftop_solar_estimation_base.py -- a real shared base class
(BaseRooftopSolarEstimator, ABC) following this project's own established get_existing_new_mw()-
style pattern (base class defines shared logic, calls an abstract hook; each scenario class
implements only the hook). Shared, identical logic lives once in compute_totals(): mean-based and
median-based MW+MWh totals (RooftopSolarTotals -- deliberately no "combined" field), the same for
every county. Scenario-specific: what a per-unit mean/median value gets scaled by to reach a
county-wide total (the abstract scale_per_unit_value_to_total_mw hook) -- Loudoun's own
_LoudounRooftopEstimator scales by a deduplicated BUILDING COUNT (its source data had no area
field at all); Fairfax's own _FairfaxRooftopEstimator scales by a total FOOTPRINT AREA (its source
data already had real per-building area). Also factored the genuinely-shared n/mean/median/min/max
computation into compute_descriptive_stats(), reversing an earlier judgment call (originally
deemed "too trivial to extract" when only Fairfax needed it) now that two real, concrete consumers
justify it per direct user request -- both counties' own PerBuildingKwStats/PerSqftKwDensityStats
dataclasses stay separate and properly-named (semantically real: "_kw" vs "_kw_per_sqft"), but
both now build themselves by delegating to the one shared computation.

Refactored both loudoun_ci_rooftop_solar_estimate.py and fairfax_ci_rooftop_solar_estimate.py to
use the new shared base internally, removing total_mw_combined/total_mwh_per_year_combined from
both. RULE 4 cross-check: reconstructed a synthetic 10,918-building input and ran it through the
refactored Loudoun code, confirming it reproduces the exact, already-established pre-refactor
mean-based (1,260.9 MW) and median-based (1,453.5 MW) figures precisely -- the refactor is
structural only, no computation silently changed. Fairfax's real result also confirmed unchanged
post-refactor: 132.4 MW mean-based (now the stated primary estimate), 129.9 MW median-based (now
an explicit sensitivity check, not blended in).

RULE 3: two existing Loudoun tests that had specifically locked in the removed "combined" behavior
were replaced (not just deleted) with tests locking in the fix itself (property genuinely absent)
plus a retained check that the two real totals still compute correctly independently. New shared
base module has its own dedicated test suite (9 tests, including a genuine-abstractness check that
the base class cannot be instantiated directly). Full suite: 9 (shared base) + 16 (Loudoun) + 14
(Fairfax) = 39/39 passing.

STILL OPEN: Loudoun's original 1,357.2 MW "combined" figure (now understood to be a statistically
unmotivated blend, not carried forward) may already be referenced elsewhere in this project's
delivered materials (e.g. prior comparisons/whitepaper drafts) -- not yet checked/reconciled.

Files: rooftop_solar_estimation_base.py, test_rooftop_solar_estimation_base.py (new),
loudoun_ci_rooftop_solar_estimate.py, test_loudoun_ci_rooftop_solar_estimate.py (both updated in
place), fairfax_ci_rooftop_solar_estimate.py, test_fairfax_ci_rooftop_solar_estimate.py (both
updated in place).

## Stale Loudoun figures corrected; Fairfax parking-lot MW/MWh built; all three Fairfax components combined (session continued 2026-08-30)

Systematic search for stale references to the old, now-removed Loudoun "combined" figure
(1,357.2 MW / 2,377,808 MWh/yr) across every file type: text grep across all .py/.md/.json/.txt
(both /home/claude/work and /mnt/user-data/outputs), all 5 .xlsx tracker/model files (checked via
openpyxl, since grep can't see inside binary spreadsheets), and the one .docx file (checked via
python-docx). Several CSV hits were coincidental digit-sequence matches inside unrelated
floating-point hourly-dispatch values (e.g. "443.9641357..."), confirmed and ruled out directly,
not assumed. Two genuinely stale locations found and fixed:
- Loudoun_CI_Rooftop_Solar_Assessment_Methodology_and_Findings.md: the delivered methodology doc
  had the old combined figure as its headline in 3 places, including a paragraph justifying the
  since-debunked averaging. Updated to the mean-based figure (1,260.9 MW / 2,209,060 MWh/yr)
  throughout, rewrote the Section 4 explanation with the corrected statistical reasoning, added a
  dated correction note.
- loudoun_ci_rooftop_solar_summary.json: had total_mw_combined/total_mwh_per_year_combined
  hardcoded as stored values (the field no longer exists in code at all). Removed, with an
  explanatory _note field.
No stale references found in any tracker/model spreadsheet or the docx file.

Clarified on request: the Fairfax school figure (71.65 MW / 286,600 kWh) is NOT current or
planned deployment -- it's the full theoretical potential across all 194 Fairfax schools (142
elem + 23 middle + 29 high), computed from flat per-type kW rates (250/500/850 kW) the user set
directly, informed by REAL installed systems at OTHER VA divisions (Richmond, Roanoke, Orange Co.,
Augusta Co.) as a benchmark proxy -- applied uniformly to every Fairfax school regardless of actual
deployment status. Real current+planned deployment is far smaller: ~16 individually-named schools
with confirmed solar today, ~40 total once the PPA pipeline (33 approved schools) completes. Also
flagged precisely: "286,600 kWh" is paired BATTERY STORAGE CAPACITY, not annual MWh production --
a different kind of metric than the C&I module's own MWh/yr figure, not directly comparable
without computing an annual production number first (done this round, see below).

Built the Fairfax parking-lot MW/MWh conversion that was never finished -- prior session work
stopped at acreage (1,298.2 acres / 56,551,120 sqft, >=6,000 sqft threshold) and never applied a
canopy-sizing conversion. Reused loudoun_parking_canopy_and_storage.py's own already-established,
explicitly county-agnostic engineering classes (SolarCanopyDesign, BatteryStorageDesign,
ParkingCanopyAssessment) UNCHANGED -- that module's own docstring already anticipated this exact
extension ("a second county needs only its own CountyParkingData-producing classmethod, not
changes to the engineering classes themselves"). New: fairfax_parking_lot_sqft.py (loader/validator
for FairfaxCounty_Driveways_and_Parking_Lots_..., mirroring loudoun_parking_lot_sqft.py's pattern
but simpler -- Fairfax's data is already pre-filtered to parking lots only, no RD_TYPE/paved-surface
split needed, and uses a different field name, Shape__Area double-underscore vs. Loudoun's
Shape_Area single-underscore, confirmed directly not assumed to match). New:
CountyParkingData.from_fairfax_parking_extract() classmethod added directly to the existing shared
module (not a new base-class file, unlike the C&I rooftop case -- here the engineering logic was
already in one shared, county-agnostic file by design, so only the county-specific data-loading
classmethod needed to be added). Real result: 377.0-471.3 MW (2.0-2.5 kW/space canopy density
range), 1,508-1,885 MWh paired battery storage capacity. Test suite: 7 (new loader) + 28 (parking
canopy module, now including 2 new Fairfax-specific tests) = 35/35 passing; cross-checked the real
loader against the already-established figures (23,651 total rows, 2,810/56,551,120 sqft at
threshold) directly, not assumed correct.

Computed the two annual-MWh-production figures still missing (schools, parking lots) via the same,
already-established 20% NEM distributed capacity factor (reused, not re-derived) -- computed
inline in chat, not yet formalized into tested code, since this is a one-off combination of three
already-computed county-level totals, not a new shared calculation pattern across scenarios/
counties the way the rooftop base class was.

FINAL COMBINED RESULT (buildings + schools + parking lots, all Fairfax):
- MW: 581.1-675.3 (buildings 132.4 fixed + schools 71.65 fixed + parking lots 377.0-471.3 range)
- MWh/yr: 1,017,995-1,183,124

Explicitly flagged when presenting this: the three components have genuinely different
methodological natures and should not be read as one homogeneous estimate -- C&I is real measured
footprint + a small (n=8) sample-derived density, mean-based; schools is a full theoretical
ceiling at assumed flat rates across every school, not actual/planned deployment; parking lots is
real parcel area + canopy-sizing assumptions, presented as a low/high range rather than collapsed
to one point.

Files: fairfax_parking_lot_sqft.py, test_fairfax_parking_lot_sqft.py (new),
loudoun_parking_canopy_and_storage.py, test_loudoun_parking_canopy_and_storage.py (both updated in
place, new Fairfax classmethod + tests added).

## Arlington County workflow started: schools (already available), parking lots (built), buildings (open) (session continued 2026-08-30)

User asked to replicate the full workflow for Arlington County. Checked what already existed first
(same discipline as Fairfax): no Arlington building-footprint or parking-lot GIS file yet, but the
school module already covers Arlington (11-locality set) -- 26 elementary, 6 middle, 9 high ->
17.15 MW / 68,600 kWh paired battery storage capacity, pulled directly, no new work. One caveat
specific to Arlington, genuinely different in kind from Fairfax's exclusions: the "9" high schools
figure is APS's own full "High Schools & Programs" category, which already INCLUDES CTE/alternative
programs (Arlington Career Center, Arlington Tech, Langston, Shriver) alongside ~5 comprehensive
high schools -- not something excluded, a broader reading explicitly flagged as substitutable for
a narrower ~5 count if wanted.

Searched for Arlington's GIS sources. Real find: unlike Fairfax's ArcGIS Hub pages (JavaScript-
rendered, blocked), Arlington's own dataset pages on the Virginia Open Data Portal
(data.virginia.gov) proved directly fetchable via web_fetch, including a live CSV data pull for the
"Building Height Polygons" layer -- a genuine capability difference from the Fairfax workflow, not
yet fully exploited (see below). One real near-miss caught before it became an error: an early
search result for a "Building Outlines" dataset with its own working URL turned out, on checking
the page's own breadcrumb, to belong to Chesapeake City, not Arlington -- caught and discarded
before use, not silently trusted.

Parking lots: built directly from the user-uploaded Arlington_Pave_Parking_Lot_Polygons.csv (2,783
rows). New arlington_parking_lot_sqft.py loader -- genuinely simpler than both Loudoun's and
Fairfax's own loaders since this dataset has NO type/category field at all (confirmed by
inspection, not assumed) -- trusted via the dataset's own authoritative name ("Pave Parking Lot
Polygons") rather than a per-row type validation the way the other two counties' loaders have.
Field name confirmed directly (SHAPE_Area, single underscore, matching Arlington's own Building
Height Polygons convention and Loudoun's Shape_Area -- NOT Fairfax's double-underscore
Shape__Area). One honest, unresolved limitation flagged rather than glossed over: GeoSyncDate is a
single uniform timestamp across all 2,783 rows (to the second) -- looks like an extraction/sync
time, not genuine per-row survey vintage the way Fairfax's Source field was, so data-collection age
can't be assessed the same way here. SNOW_OWNER/SNOW_PRIORITY present but correctly not used for
filtering -- snow-removal-responsibility metadata, not a parking-lot validity/type classification
(92.7% "UNK" doesn't mean "not a real lot").

Added CountyParkingData.from_arlington_parking_extract() as a THIRD classmethod on the same shared,
unchanged engineering module (loudoun_parking_canopy_and_storage.py) -- confirms the module's own
originally-stated design goal ("a second county needs only its own classmethod") holds for a third
county too, with zero changes needed to SolarCanopyDesign/BatteryStorageDesign/
ParkingCanopyAssessment. Real result: >=6,000 sqft threshold gives 1,428 of 2,783 rows (51.3% --
notably higher than Fairfax's 11.9% at the same threshold, an honest observation flagged not
explained away: Arlington's parking-lot size distribution skews larger, median sitting just above
the threshold itself), 44,057,781 sqft (1,011.4 acres) -> 293.7-367.1 MW canopy range, 1,174.9-
1,468.6 MWh paired battery storage capacity. Test suite: 8 (new loader) + 30 (parking canopy
module, now 2 Loudoun + 2 Fairfax + 2 Arlington real-data tests) = 38/38 passing; cross-checked the
real loader against the already-established figures directly, not assumed correct.

STILL OPEN: Arlington C&I building footprints. Direct web_fetch of the live "Building Height
Polygons" CSV worked but appeared truncated (cut off mid-row around record ~1,164, no clear EOF) --
real Arlington building count is almost certainly much larger. Schema also looks genuinely
different from Fairfax's: TYPE field here appears to classify STRUCTURE type (Commercial/
Residential/Canopy seen so far, no Industrial observed yet) rather than Fairfax's LAND-USE
classification (Commercial or Retail Facility/Industrial Facility/etc.), and no obvious building-ID
field for the podium/multi-part dedup the way Fairfax had one, despite the same "a building may be
made up of many parts" language appearing in Arlington's own dataset description. Neither resolved
yet -- flagged to user, awaiting direction on whether to keep pushing on direct fetch/pagination or
have the file uploaded directly instead.

Files: arlington_parking_lot_sqft.py, test_arlington_parking_lot_sqft.py (new),
loudoun_parking_canopy_and_storage.py, test_loudoun_parking_canopy_and_storage.py (both updated in
place, new Arlington classmethod + tests added).

## Arlington C&I buildings resolved: real file uploaded, user-directed reclassification applied (session continued 2026-08-30)

User uploaded Arlington_Buildings.csv directly (49,064 rows) -- a genuinely different, more
comprehensive dataset than the "Building Height Polygons" layer being fetched live last turn (which
had appeared truncated around row ~1,164). This one has its own "CM_Type" field, directly parallel
to Fairfax's "Community Maps Type" naming.

User made a direct, substantive methodological observation and instruction: only 164 of 49,064 rows
(0.33%) are tagged "Commercial / Retail" -- verified directly against the real data before acting
on it, confirmed exactly correct, not taken on faith. User's diagnosis: this implausibly undercounts
real commercial stock for a dense jurisdiction like Arlington. User's fix, given directly: treat any
"General / Residential"-tagged building over 2,000 sqft as commercial (rationale given: large
"residential" structures here are likely company-owned apartment/condo buildings, economically more
like commercial buildings than single-family homes). User also directed excluding Religious and
Government/Military.

Checked the full CM_Type distribution directly rather than only the two categories the user
mentioned: General/Residential 98.89%, Government/Military 0.42%, Commercial/Retail 0.33%,
Religious 0.15%, Education 0.09%, Community Center 0.04%, Medical 0.03%, Hotel 0.02%, Transportation
0.01%, Recreation/Airport ~0%. For the small remaining categories the user didn't explicitly
address, followed the same precedent already established for Fairfax rather than silently guess:
included Medical and Hotel directly (parallel to Fairfax's own Health/Medical and Hotel/Motel
categories); excluded Education (avoid double-counting with the separate school-solar module,
same reasoning as Fairfax), Community Center, Transportation, Recreation, and Airport (the latter a
single 762,694 sqft row, almost certainly Reagan National's own terminal -- federal infrastructure,
not a conventional C&I candidate, parallel to Fairfax's own Airport Terminal exclusion). Stated
explicitly to the user as a decision open to correction, not silently assumed.

Checked for the podium/multi-part dedup concern (same underlying issue Fairfax's Building
Identification Number field addressed) via Arlington's own GIS_ID field -- a real, direct check,
not assumed either way given the dataset's own description uses the same "a building may be made
up of many parts" language Fairfax's did: zero duplicated GIS_IDs within the C&I-eligible
population specifically (0 of 10,120 eligible rows), so no dedup step was added. The >=600 sqft
minimum-viable-rooftop floor (Fairfax's own established building threshold, distinct from the
parking-lot 6,000 sqft one) was confirmed to do real work on the directly-included categories: 10
of 164 Commercial/Retail rows fall under 600 sqft and are correctly excluded by it.

New arlington_ci_rooftop_solar_estimate.py, reusing the shared rooftop_solar_estimation_base.py
class hierarchy directly (Arlington's situation -- known per-building footprint needing a kW/sqft
density conversion -- is structurally identical to Fairfax's, not Loudoun's flat-per-building-count
approach) and the same real 8-point NVRC density sample already established for Fairfax, imported
directly rather than re-typed a third time.

Real result: 10,133 eligible buildings (154 Commercial/Retail + 9,956 size-heuristic Residential +
15 Medical + 8 Hotel, after the 600 sqft floor), 55,038,330 sqft (1,263.5 acres) total footprint.
Mean-based (primary): 373.8 MW / 654,886 MWh/yr. Median-based (sensitivity check): 366.6 MW /
642,349 MWh/yr. Test suite: 12 new tests, all passing; confirmed the three existing rooftop-solar
modules (Loudoun 16, Fairfax 14, shared base 9) remain fully untouched by the new cross-directory
imports -- 51/51 across all four modules together.

Files: arlington_ci_rooftop_solar_estimate.py, test_arlington_ci_rooftop_solar_estimate.py (new).

## Real Arlington school roof sizes computed and cross-checked; aggregate school rooftop-to-kW conversion added (session continued 2026-08-30)

User asked for real Arlington school counts by type, how many are identifiable in our buildings
data, and avg kW+battery deployed per type. Clarified directly: intermediate = middle.

Checked the buildings file's own SCHOOL column directly rather than assume it meant "is a school
building" -- it does not. 287 rows are SCHOOL-flagged, but the large majority are tagged
CM_Type='General / Residential' with no school name at all -- this is an attendance-zone
indicator, not a building-use classification. The real building-use field is CM_Type='Education'
(44 rows, directly parallel to Fairfax's own scheme) -- confirmed via cross-reference, not assumed.
Broken down by the SCHOOL sub-code within Education rows: 25 Elementary (ES+AES), 6 Middle
(MS+AMS), 6 High (HS). Two real catches flagged rather than silently absorbed: one "HS" row is
Bishop O'Connell High School (private/Catholic, not APS); another is the David M Brown Planetarium
(not a comprehensive high school building at all) -- genuine APS-public comprehensive high school
count in the footprint data is 3 (Wakefield, Washington-Liberty, Yorktown), not 6.

Researched real, deployed solar at Arlington schools (web search, mirroring the earlier Fairfax
approach) -- found genuine deployment data but an honest, unresolved discrepancy between sources
(APS's own current page: "9 schools" with arrays; one other recent source: "8 solar schools"; 10
distinctly-named schools found across all sources combined) and, critically, ZERO mentions of
paired battery storage at any real, deployed Arlington school system -- flagged directly as a real
data gap rather than force an "avg kW and battery kWh already deployed" figure from insufficient,
inconsistent data.

Computed real roof-size stats per type directly from the buildings file (genuinely available,
unlike the deployed-solar question): Elementary mean 60,225 / median 58,651 sqft (n=25); Middle
mean 117,746 / median 117,092 sqft (n=6); High mean/median vary sharply depending on whether the
2 non-comprehensive entries are included (full 6: mean 115,032; comprehensive-only 3 -- Wakefield/
Washington-Liberty/Yorktown: mean 187,515, tightly clustered ~174K-199K sqft, ~13% spread).
Cross-checked these real sizes against the existing flat per-type kW assumptions (250/500/850,
originally benchmarked off REAL installed systems at other VA divisions) using the same established
NVRC density rate (0.006792 kW/sqft) already used for C&I buildings: implied kW came out ~1.5-1.64x
higher than the current assumptions across all three types, a fairly consistent (not random) gap --
surfaced as a genuine, unresolved methodological question, not silently resolved either way.

Per direct user instruction ("no need then to categorize as HS, MS, and ES"), added a single,
aggregate school rooftop-to-kW conversion instead of a per-type one. New
build_school_education_population() (all CM_Type='Education' rows, no size floor -- deliberately
different from build_ci_eligible_population's own >=600 sqft floor, since the user's instruction
was specifically about not needing per-type/per-size narrowing here) and
estimate_arlington_school_rooftop_solar(), both added to the existing Arlington module, reusing the
SAME _ArlingtonRooftopEstimator hook and ArlingtonCiRooftopSolarEstimate dataclass already built for
C&I buildings (Rule 1 -- the fields are genuinely identical in meaning, just describing a different
building population, so reusing the one dataclass is real reuse, not a naming mismatch).

RULE 3: a real structural bug was introduced mid-edit (str_replace's old_str/new_str boundaries
split _ArlingtonRooftopEstimator and the ArlingtonCiRooftopSolarEstimate @dataclass decorator
apart, leaving orphaned field declarations) -- caught immediately via the mandatory post-edit
syntax check before any test was run, fixed by restructuring the insertion cleanly. Full suite
re-run after the fix, confirmed clean.

Real result (all 44 Education-tagged buildings, no HS/MS/ES split): 3,130,564 sqft (71.9 acres)
total footprint. Mean-based (primary): 21.3 MW / 37,250 MWh/yr. Median-based (sensitivity): 20.9 MW
/ 36,537 MWh/yr. Test suite: 18 (up from 12, 6 new school-specific tests) passing; confirmed
Loudoun (16), Fairfax (14), and the shared base (9) remain fully untouched -- 57/57 across all four
rooftop-solar modules together.

Files: arlington_ci_rooftop_solar_estimate.py, test_arlington_ci_rooftop_solar_estimate.py (both
updated in place).

## Formal documentation pass: Fairfax and Arlington methodology and findings document (session continued 2026-08-30)

Created Fairfax_and_Arlington_Solar_Assessment_Methodology_and_Findings.md -- a new, comprehensive
methodology/findings document (not a revision of the Loudoun one) covering everything since the
last formal documentation pass: Fairfax C&I/parking/schools, Arlington C&I/parking/schools, the
shared rooftop-estimation base class hierarchy, the mean-vs-combined statistical correction (and
its retroactive application to Loudoun's own already-delivered figures), and both counties'
combined totals.

Per direct user instruction, the Fairfax jurisdictional exclusion (cities of Alexandria, Fairfax,
Falls Church; towns of Clifton, Herndon, Vienna -- all six maintaining separate business-licensing
and GIS systems outside Fairfax County government's own data) is given prominent placement in both
the executive summary and its own dedicated subsection (3.1), explicitly flagged as a
well-supported inference from licensing/GIS-boundary documentation rather than a row-by-row
empirically confirmed fact about the specific Buildings/Driveways-and-Parking-Lots layers used.
Arlington's own lack of an equivalent exclusion is separately noted and distinguished (no
incorporated towns; bordering jurisdictions are not enclaves within Arlington's own boundary the
way the City of Fairfax is within Fairfax County), while being honest that this has not been
independently verified the same way the Fairfax exclusion was.

RULE 4: every headline figure in the document was re-verified directly against the real, current
code immediately before writing (not pulled from memory of earlier turns), including a small
floating-point rounding-boundary catch in the Fairfax combined MW range (581.05 rounds to 581.0 in
standard Python rounding, not 581.1) -- caught by cross-checking the rounded combined figure
against a full-precision recomputation, and corrected in both places the figure appeared in the
document.

Document consolidates 7 open questions/limitations in one place (Section 6) rather than leaving
them scattered across the conversation: the Fairfax jurisdictional gap; Fairfax's parking-lot
acreage being only ~24% of Loudoun's own established figure; the missing real-deployed-solar
per-school-type data for both counties; zero evidence of paired battery storage at any real
deployed school system found in either county; the unresolved ~1.5-1.64x real-roof-size-vs-assumed
-kW discrepancy found for Arlington schools; Arlington's school rooftop figure including one
private school and one non-school facility; and the underlying NVRC sample's own geographic/vintage
limitations, now extended across two more counties beyond Loudoun.

Files: Fairfax_and_Arlington_Solar_Assessment_Methodology_and_Findings.md (new).

## Combined Northern Virginia document: Loudoun + Fairfax + Arlington merged into one (session continued 2026-08-30)

Created Northern_Virginia_Solar_Assessment_Methodology_and_Findings.md, combining and superseding
both prior documents (Loudoun's own C&I-only doc, and the Fairfax/Arlington C&I+parking+schools
doc) into one, with each county getting parallel C&I + parking + schools subsections per direct
user instruction.

Before merging, re-read the full, current Loudoun methodology doc directly (not from memory, since
many turns had passed) to pull its exact, post-correction content. Also directly re-verified
Loudoun's own real parking-lot and school figures via the actual code -- these existed as real,
already-computed results (used elsewhere in this project, e.g. the earlier solar-firming/battery-
dispatch work) but had never been formally written into the Loudoun methodology document itself,
which was scoped to C&I rooftop only. Confirmed matching the earlier-established figures exactly:
parking 1,551.2-1,939.0 MW / 5,341.6 acres; schools 34.5 MW / 138,000 kWh storage capacity (57
elementary + 15 middle + 15 high = 87 schools). Computed the missing annual MWh/yr for Loudoun
schools using the same established 20% capacity factor (60,444 MWh/yr) and built Loudoun's own full
combined total (2,846.6-3,234.4 MW / 4,987,195-5,666,618 MWh/yr) for the first time.

New Section 1 (shared methodology) explicitly documents the real, load-bearing difference between
Loudoun's own C&I approach (flat per-building kW x building count, since Loudoun's source data has
no area field) and Fairfax's/Arlington's own approach (kW/sqft density x footprint area, since
their source data already has real per-building area) -- framed as two correct approaches for two
genuinely different kinds of source data, not an inconsistency. New Section 5 (grand total) and
Section 6 (cross-county comparison) are new synthesis, not present in either source document --
the actual value of combining three previously-separate documents into one.

RULE 4: every figure re-verified directly (Loudoun via live code re-run; Fairfax/Arlington
carried forward from the already-verified prior document) rather than assembled from memory across
two source documents. Caught and fixed one small transcription error while cross-checking Section
5's own arithmetic against independently-recomputed sums: the parking MWh/yr high-end figure was
off by $100 (4,865,904 vs. the correct 4,866,004) -- the error didn't propagate into the grand
total (computed correctly, separately), but was still fixed for precision in a formal document.

Northern Virginia grand total (all three counties, all three components): 4,116.4-4,671.9 MW /
7,211,921-8,185,122 MWh/yr. Consolidated Section 7 now carries 9 open questions/limitations across
all three counties (up from Fairfax/Arlington's own 7), adding Loudoun's own un-researched
real-school-deployment gap and its own NVRC-vintage-vs-new-construction limitation, plus a new
explicit note that the two different C&I methodologies aren't directly comparable without care.

Files: Northern_Virginia_Solar_Assessment_Methodology_and_Findings.md (new -- combines and
supersedes both Loudoun_CI_Rooftop_Solar_Assessment_Methodology_and_Findings.md and
Fairfax_and_Arlington_Solar_Assessment_Methodology_and_Findings.md).

## Executive summary restructured per direct user request (session continued 2026-08-30)

User requested a specific reordering of the Northern Virginia document's opening: grand total at
the top of the table, then component breakouts (C&I/parking/schools summed across all three
counties), then the per-county breakdown -- and a new executive-level introductory paragraph, with
the "combines and supersedes prior documents" provenance note removed.

Restructured the executive summary into three tables in the requested order (grand total; by asset
type; by county), each with its own short caveat paragraph following where relevant. Added a new
opening paragraph (plain prose, no table) covering what the assessment is, why it matters
(Scenario 3's transmission-avoidance rationale), and the headline magnitude (4.1-4.7 GW) stated in
prose before the reader reaches any table -- written for the stated legislator/Sr-leadership
audience who may only read this paragraph. Removed the italic "combines and supersedes" note
entirely, per direct instruction.

Simplified Section 5 (Northern Virginia Grand Total), which would otherwise now duplicate the exact
same three tables just moved into the executive summary -- replaced with a short pointer back to the
executive summary rather than repeating identical content twice in one document. Verified the
already-corrected parking MWh/yr figure (4,866,004, the $100 transcription fix from the prior turn)
carried through correctly into the new by-asset-type table.

Files: Northern_Virginia_Solar_Assessment_Methodology_and_Findings.md (updated in place).

## Prince William County: C&I buildings (real) and parking lots (estimated) built (session continued 2026-08-31)

Read claude.md directly per user reference -- established workflow going forward: explore (tightly
scoped) -> plan -> WAIT for confirmation -> implement -> verify. Applied to all Prince William work
this round: proposed each piece as a plan first, waited for explicit user confirmation before
building.

C&I buildings: user uploaded PWCCommericialBuildings.xlsx (3,876 rows), already pre-filtered to
StructureType=3 ("Commercial") before upload since the full county buildings layer exceeded the
upload size limit. User flagged "no type information for industrial" -- confirmed directly this is
broader than industrial specifically: StructureType is uniformly "3" across all 3,876 rows (no
usable sub-type distinction survives the pre-filtering at all). User then provided the full
10-value StructureType legend, confirming there is no separate "Industrial" code anywhere in Prince
William's own schema -- industrial buildings are almost certainly folded into "3=Commercial" rather
than absent, making this population's composition broader than Fairfax's/Arlington's own
"Commercial or Retail" categories alone (which exclude industrial as a separate tag there). No
dedup field exists in this schema at all (both OBJECTID and GlobalID confirmed fully unique, unlike
Fairfax's Building ID or Arlington's GIS_ID) -- flagged as a real, unresolved limitation rather than
assumed away. New prince_william_ci_rooftop_solar_estimate.py, reusing the same shared
BaseRooftopSolarEstimator hierarchy and real NVRC density sample already used for Fairfax/Arlington
(11 tests). Real result: 2,497 buildings >=600 sqft, 922.2 acres (40,171,076 sqft) -> 272.8 MW /
477,985 MWh/yr (mean-based, primary); 267.6 MW / 468,834 MWh/yr (median-based, sensitivity check).

Parking lots: direct Prince William GIS extraction continues to fail (TYPE_CODE field returning
zero results) -- built a density-based estimate instead, given real, verified 2025-population and
parking-acreage figures already established for Loudoun and Fairfax. Presented both methods (per-
capita vs. per-land-area) and both anchor counties as options with the full uncertainty range shown
(559-5,974 acres, >10x spread) rather than picking one silently. User made a direct, reasoned
decision: Loudoun-anchored per-capita as primary, with explicit rationale (Prince William's greater
distance from DC vs. Fairfax implies less structured/garage parking and more surface-lot parking,
similar to Loudoun's own development pattern -- a real, substantive argument tied to the underlying
mechanism, not an arbitrary pick). New prince_william_parking_lot_density_estimate.py, formalizing
the extrapolation into small, tested functions (12 tests, cross-checking the full pipeline against
every figure hand-computed directly in chat) rather than leaving it as an untested one-off
script -- reuses the same, unchanged ParkingCanopyAssessment engineering classes via a directly
-constructed CountyParkingData object (no real file to load from, so no new classmethod, unlike
every real county's own loader). Explicitly labeled "ESTIMATED, NOT real GIS data" in the
source_description field itself, not just in chat, so the distinction survives into any downstream
export. Real result (Loudoun-anchored, primary): 5,974 acres estimated -> 1,734.7-2,168.4 MW /
3,039,279-3,799,098 MWh/yr. Fairfax-anchored sensitivity check retained: 559 acres -> 162.4-203.0 MW
/ 284,456-355,570 MWh/yr.

Test suite this round: 11 (C&I) + 12 (parking estimate) = 23 new tests, all passing. Confirmed
Loudoun, Fairfax, Arlington, and the shared rooftop/parking-canopy modules remain fully untouched --
68/68 across all five rooftop-solar modules, 30/30 in the shared parking-canopy module.

STILL OPEN: Prince William school figures not yet pulled (schools were confirmed present in the
existing school_rooftop_solar_assumptions.py module in an earlier turn -- 62 elementary, 17 middle,
13 high, 35.05 MW / 140,200 kWh -- but not yet assembled into a Prince William combined total).
Prince William's own real parking-lot data should replace this estimate immediately if/when the
county GIS extraction issue is resolved.

Files: prince_william_ci_rooftop_solar_estimate.py, test_prince_william_ci_rooftop_solar_estimate.py,
prince_william_parking_lot_density_estimate.py, test_prince_william_parking_lot_density_estimate.py
(all new).

## Prince William combined total assembled; Northern Virginia document updated to four counties (session continued 2026-08-31)

Per direct user confirmation of the Loudoun-anchored parking-lot approach, assembled Prince
William's full combined total following claude.md's workflow (explore -> plan -> wait for
confirmation -> implement -> verify), now already satisfied by the user's explicit go-ahead. Pulled
the real school figure directly from school_rooftop_solar_assumptions.py (re-verified, not from
memory: 62 elementary + 17 middle + 13 high = 92 schools, 35.05 MW / 140,200 kWh storage capacity),
derived annual MWh via the same established 20% capacity factor (61,408 MWh/yr), and re-verified
both the C&I and parking-lot figures directly from the real code rather than trust memory before
combining. Cross-checked the by-asset-type sum against the combined total independently -- matched
to within $1 (floating-point rounding only).

Real result -- Prince William combined: 2,042.6-2,476.3 MW / 3,578,671-4,338,491 MWh/yr (C&I 272.8
MW/477,985 MWh/yr real; parking lots 1,734.7-2,168.4 MW/3,039,279-3,799,098 MWh/yr estimated,
Loudoun-anchored; schools 35.05 MW/61,408 MWh/yr theoretical potential).

Updated Northern_Virginia_Solar_Assessment_Methodology_and_Findings.md throughout to add Prince
William as a fourth county: new Section 5 (mirroring the other three counties' own structure --
jurisdictional scope, C&I, parking [explicitly marked ESTIMATED], schools, combined total),
renumbered all subsequent sections (old 5-7 -> new 6-8), recomputed and cross-verified the grand
total and by-asset-type tables (new grand total: 6,159.0-7,148.2 MW / 10,790,592-12,523,613 MWh/yr),
expanded the cross-county comparison and consolidated limitations sections to fold in Prince
William-specific findings (no industrial code in its own schema, no dedup field, the estimated-not
-measured parking-lot caveat), and updated the appendix's file table.

RULE 4/thoroughness: a systematic sweep after the main edits caught 6 stale "three counties"
references still remaining in the Shared Methodology section (which predates this round's Prince
William addition) that a first-pass search had missed, including one stale internal cross-reference
("Section 6" that should have read "Section 7" after renumbering) that wouldn't have matched a
literal "three counties" text search -- both categories of staleness were searched for and fixed
explicitly, not assumed absent after the first pass. Final full-document verification confirmed
section numbering 1-8 sequential, limitations list 1-12 with no duplicate numbers, and the two
remaining "three counties" text matches confirmed correct as-is (not stale) rather than reflexively
changed.

Full test suite re-confirmed clean before and after the document update: 110 tests across all
county/shared modules (9 shared rooftop base + 16 Loudoun + 14 Fairfax + 18 Arlington + 23 Prince
William C&I/parking + 30 shared parking-canopy module).

Files: Northern_Virginia_Solar_Assessment_Methodology_and_Findings.md (updated in place, now
covering four counties).
