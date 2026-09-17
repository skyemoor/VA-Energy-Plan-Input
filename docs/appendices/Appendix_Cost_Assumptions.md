# Appendix — Cost Assumptions

**Extracted 2026-09-14 from `Reorganized_Appendices_Draft.md`, where it existed only inside a 4,682-line composite file.** That draft also carried stale copies of five appendices that have their own authoritative files; this one had no standalone version at all, which made it invisible to the index, untestable, and impossible to revise without editing a file about something else.

Lettering is deliberately omitted here. The scheme is being reworked into reader order (methods, scenarios, topics, reference) and a letter baked into the filename now would be wrong twice.

---

### B.1 Solar CAPEX
2026 base of $1,474/kW-AC, derived from Lazard LCOE+ v18.0 (June 2025) Low/High
cases linearly interpolated to Virginia's actual blended capacity factor
(22.8%), corroborated independently by NREL ATB's 2024 base-year figure
projected forward. Superseded an earlier, generic $1,100/kW placeholder.

### B.2 Solar O&M
$24/kW-yr, reconciled across three sources: Lazard and LBNL's 2025 Data
Update (real FERC Form 1 data) both report $11-14/kW-yr for a narrow
core-maintenance scope; NREL's broader $24/kWAC-yr figure was confirmed, via
NREL's own 2021 ATB documentation, to deliberately include land lease,
property tax, insurance, asset management, and security — costs this model
has no separate line items for, making the comprehensive NREL figure the
correct match once scope is properly accounted for.

### B.3 Vegetation Management
A specific claim -- "$3-5/kW-yr in humid southeastern states, double the
national average" -- was traced to its source (an uncited spreadsheet-vendor
marketing blog, internally inconsistent with its own stated baseline, and
separately shown to misattribute an unrelated NREL figure) and REJECTED; no
regional climate penalty is quantified or applied in this model. The related
claim that agrivoltaic sheep grazing offsets such a penalty is similarly not
well-supported at the fleet-average level: the best available peer-reviewed
data (NREL/MDPI Sustainability 2023, 54 real utility-scale sites) finds
grazing roughly cost-neutral against conventional turfgrass mowing on
average (mean $1.55 vs. $1.51/kWdc-yr; turfgrass actually cheaper at the
median). Specific well-documented cases (OSU Extension's worked example;
Tampa Electric via Utility Dive) do show 50-75% site-level savings, but
these are best-case, well-optimized programs, not the typical outcome, and
are presented as such rather than as a fleet-wide offset.

**A refinement to the above, prompted by a direct question about whether the
NREL/MDPI grazing figure is even measuring the right business model for
Virginia specifically (2026-08-16).** The NREL/MDPI dataset's "sheep
grazing" sites appear to reflect a third-party, professionally-contracted
roving-grazier business model (the paper's own text: "Graziers incur costs
to purchase, haul, set up, and take down supplies and equipment, including
water tanks, pumps, mineral feeders, and temporary fencing" -- explicitly
attributing fencing/water/herding costs to the grazier, not the site
operator) -- a real model, and one some utilities do pay directly (Maryland,
for instance, has utilities paying shepherds to rotate herds between solar
sites). But Virginia's own statutory agrivoltaics definition (Va. Code
SS10.1-1197.5, already verified in the Agrivoltaics appendix) is explicitly
about integrating solar into an *existing* farm operation, not contracting
a specialized rotating-herd business -- a structurally different case, where
herding and water systems are the farmer's own pre-existing operating
costs, not a utility-borne line item.

Excluding the NREL/MDPI dataset's "Grazing" ($224/acre/yr mean) and
"Fencing" ($55/acre/yr mean) activity costs on this basis -- as costs that
belong to the farmer's own operation under Virginia's statutory model, not
to utility-borne O&M -- leaves only the residual mechanical maintenance
livestock don't fully handle. The same dataset shows mowing still occurs
even at grazing sites (6 real observations, mean $95/acre/yr, at an average
frequency of ~1 event/year per the dataset). **A conservative floor for
this residual, USING TWICE-YEARLY MOWING (spring and fall growth flush)
rather than the dataset's own once-yearly average**, informed directly by
a project stakeholder's personal, first-hand experience operating a small
sheep flock (explicitly NOT a published, peer-reviewed figure -- flagged as
expert testimony, a different and lower-confidence source category than
the rest of this appendix's citations) -- $95/acre-per-mowing-event x 2 =
**$190/acre/yr, approximately $1.02/kWdc/yr** using the same dataset's own
median land-use ratio (5.35 acres/MWdc).

This is presented as a documented, disclosed finding -- not as a change to
the model's $24/kW-yr blanket O&M figure, since vegetation management is
only one of several bundled cost categories in that comprehensive-scope
NREL ATB figure (alongside asset management, insurance, site security,
cleaning, and component failure), and isolating just the vegetation slice
with the precision this would require is not well-supported by available
data. The finding stands as qualitative record: for the assumed 90%
agrivoltaic-siting share (farmer-integrated model, not roving-grazier), the
defensible utility-borne vegetation-management floor is meaningfully lower
than the NREL/MDPI dataset's full grazing-site total ($1.02 vs. $1.55/kWdc-
yr) -- though likely still understates the true figure somewhat, since
herbicide application and site monitoring (both still reported at grazing
sites in the source data) are excluded from this floor along with
Grazing/Fencing, for conservatism rather than because they're known to be
zero.

### B.4 Storage and Gas-Price Assumptions
Sodium-ion and iron-air CAPEX/O&M carried forward unchanged from prior
sourcing. Three gas-price tiers established for Scenario 2: Base (Deloitte),
Low (EIA reference case), High (Hughes/Post Carbon Institute 2021 — flagged
as the least current of the three, retained for range context).

### B.4.1 Bernstein Research Natural Gas Outlook — Assessed as a Fourth Reference Case (Not Yet Adopted)

**Code location**: `lp_model.py`, `gas_cost_mwh_bernstein(year, high_case=False)`.
Assessed directly at user request, in the same manner as the existing
Deloitte/EIA/Hughes cases — not yet incorporated into Scenario 2's active
Base/Low/High tier structure.

**Source, cross-verified across multiple independent outlets, not a single
unverified article**: Bernstein Research's "Americas Natural Gas Outlook,"
most recently reaffirmed in the 2026 edition (December 2025) — "we
continue to have faith in five," i.e. $5.00/mcf Henry Hub as the new
structural mid-cycle equilibrium, up from a prior decade averaging closer
to $3.50/mcf. The same $5/mcf figure and underlying LNG-export/data-center
thesis is independently corroborated across Hart Energy, Oil & Gas 360,
Marcellus Drilling News, Seeking Alpha, Investing.com, TradingNews, and
Capital.com — not resting on the single originally-provided article alone.
Bullish-risk scenario, separately flagged by Bernstein itself: $8-10/mcf
"under more bullish assumptions, such as a shortfall in Haynesville
growth."

**Methodologically different in character from the other three cases,
disclosed rather than smoothed over**: Deloitte/EIA/Hughes each provide
multi-decade, rising $/MMBtu trajectories with specific year-by-year (or
CAGR-interpolated) points. Bernstein provides something different — a
single "new equilibrium"/"mid-cycle" price level, explicitly not framed by
Bernstein as a year-by-year escalation path. `gas_cost_mwh_bernstein()`
therefore returns a FLAT rate for all years, for both the base and
high case, rather than inventing a trajectory shape Bernstein's own
reporting does not support.

**Unit conversion, made explicit**: Bernstein's figure is Henry Hub
$/mcf, not $/MMBtu like the other three cases. Converted via the standard
EIA factor (1.037 MMBtu/mcf): $5.00/mcf = $4.82/MMBtu; the $8-10/mcf
upside range = $7.71-$9.64/MMBtu (midpoint $9.00/mcf = $8.68/MMBtu used
as the function's `high_case=True` value, since Bernstein gives a range,
not a single upside point).

**Comparison against the existing three cases** (all $/MMBtu):

| Year | Deloitte | EIA | Hughes | Bernstein (base) | Bernstein (high) |
|---|---|---|---|---|---|
| 2026 | 3.70 | 3.70 | 3.50 | 4.82 | 8.68 |
| 2030 | 5.40 | 3.80 | 4.27 | 4.82 | 8.68 |
| 2035 | 5.88 | 4.00 | 5.47 | 4.82 | 8.68 |
| 2040 | 6.35 | 4.20 | 7.01 | 4.82 | 8.68 |
| 2045 | 6.92 | 4.58 | 8.98 | 4.82 | 8.68 |
| 2050 | 7.50 | 4.95 | 11.50 | 4.82 | 8.68 |

**Reading the comparison, stated plainly**: Bernstein's flat $4.82 starts
*above* both Deloitte's and EIA's 2026 points — reading more bullish
near-term. But because Bernstein stays flat while Deloitte keeps climbing,
Bernstein reads *less* bullish than Deloitte by 2040 and beyond, and
Deloitte alone exceeds Bernstein's own flat rate for the entire second
half of this project's window. Bernstein's own upside case ($8.68) lands
close to, not meaningfully beyond, Hughes's existing long-run trajectory
(which reaches 8.98 by 2045 and 11.50 by 2050 on its own) — so Bernstein
does not obviously function as a new, more-extreme high case beyond what
Hughes already provides for this project. It is better understood as a
different *kind* of estimate — a near/mid-term equilibrium view — than a
natural fourth point on the same Base/Low/High trajectory spectrum
already established.

**Caveat on source reliability, disclosed rather than assumed**: analyst
commodity-price views shift substantially over time. The same Bernstein
research team held an explicitly bearish $2.50/MMBtu view for 2018 gas
prices as recently as 2017 — the opposite direction from today's
"supercycle" call. This is a current (reaffirmed December 2025),
well-corroborated view, not an infallible one.

**Status**: assessed and built into the code (`gas_cost_mwh_bernstein()`),
available for use in sensitivity testing or as an additional Scenario 2
tier if desired, but not yet adopted as an active part of Scenario 2's
Base/Low/High structure. No Scenario 2 solves have used it.

### B.5 Export Price for Post-Hoc Curtailment Revenue

**Final value: $27.00/MWh flat** ($45/MWh EIA average LMP x 0.60 midday-
discount factor), applied post-hoc to curtailed energy (bounded by the
5,000 MW/hour `EXPORT_CAP_MW` transmission ceiling already established in
the hourly LP), never fed back into the LP's own dispatch optimization —
consistent with this session's earlier, separate decision to exclude
export entirely from the LP objective.

**Full reasoning trail (worth preserving, not just the answer):** this
value went through three distinct states within this session alone,
following the same "correction history, kept for transparency" convention
already used elsewhere in this model. The prior figure was $37.80/MWh
($45 EIA LMP x 1.40 DOM-zone premium x 0.60 midday discount).

The 1.40x DOM-zone premium was removed based on a user-identified
directional error, not just a magnitude concern: the premium is a
*buy-side, import-scarcity* signal — it reflects what DOM-zone load
currently pays to import roughly 20% of its electricity under supply-
constrained conditions (see PJM's own Operating Reserve Demand Curve
mechanism, C077's companion citations). Applying an import-scarcity premium
to the *reverse* transaction (DOM selling surplus out) very plausibly gets
the sign backwards rather than merely the size: PJM's LMP/congestion
framework means a constrained zone pays more to import precisely because
transmission congestion limits inbound flow — the same congestion
mechanism would be expected to depress, not inflate, the price DOM could
realize exporting out under otherwise-similar conditions. This is the same
underlying transmission constraint already captured by this model's own
5,000 MW/hour export cap, now recognized as bearing on price direction as
well as volume.

A second, independent consideration reinforces dropping the premium:
Virginia's neighboring PJM states that DOM interconnects with (North
Carolina, New Jersey, Maryland, Delaware, Pennsylvania) each have their own
RPS or renewable-energy targets, heavily solar-weighted. Regional solar
generation is weather-correlated across a compact footprint like the
Mid-Atlantic — a sunny day producing DOM surplus is likely producing
surplus in neighboring solar-heavy zones simultaneously, making them
probable *competing sellers*, not scarcity-driven buyers, at precisely the
hours DOM has curtailed energy to sell. This would be expected to suppress
the clearing price further, not support a premium.

**A specific, credible counter-consideration was checked and found not to
apply at the relevant time horizon.** Seel, Mulvaney Kemp et al., "U.S.
Utility-Scale Solar 2025 Data Update" (Lawrence Berkeley National
Laboratory, October 2025 — see M.10 below) defines a directly relevant
"value factor" metric (solar's captured market value ÷ a flat 24x7 block's
average value) and reports PJM's 2024 value factor as slightly *above*
100% ($33/MWh solar value vs. $32/MWh flat-block value) — solar's
generation profile currently *helps*, not hurts, its captured value in
PJM, the opposite of a midday discount. This was weighed directly and set
aside for two disclosed reasons rather than silently ignored: (1) it is a
PJM-wide average, not DOM-zone-specific; (2) more importantly, it is a
2024, current-penetration snapshot, and the same LBNL report documents
value factor declining as solar's share of load grows (CAISO's own
trajectory to a 30% value factor at 30% penetration is the demonstrated
precedent within the same report). This project's checkpoints project
solar growing from roughly 15,000 MW (2030) to 142,000 MW (2045) — a
penetration trajectory the current PJM-wide, sub-saturation snapshot does
not describe. The finding is retained as a documented, disclosed
consideration, not incorporated into the final figure.

**Net result**: $45 x 0.60 = $27.00/MWh — numerically identical to this
model's original, pre-correction figure, but now reached through a
different and more defensible chain of reasoning specific to the export
(not import) transaction, rather than by omission.

### B.5.1 Post-Hoc Export Revenue: Computed Across All 16 Solved Years

**Code location**: `lp_package/compute_export_revenue.py`. Applies the
formula above (min(curtailment, EXPORT_CAP_MW) x $27.00/MWh) directly to
the already-solved hourly curtailment arrays for all four checkpoints and
all twelve intermediate years — no re-solving involved, consistent with
this being a strictly post-hoc valuation, never fed back into any LP
objective.

**Finding worth stating plainly, not just tabulating**: the fixed 5,000
MW/hour transmission cap means export's ability to offset curtailment
shrinks sharply over time, even as curtailment itself grows enormously.
Capture rate (share of a year's total curtailment actually exportable
under the cap) starts near-total at the earliest checkpoint and falls to a
small fraction by the last one, simply because curtailment volume grows
far faster than the fixed cap can absorb:

| Year | Curtailed (GWh) | Exported (GWh) | Capture rate | Revenue ($M) |
|---|---|---|---|---|
| 2030 | 1,072 | 1,064 | 99.3% | 28.7 |
| 2035 | 4,228 | 2,297 | 54.3% | 62.0 |
| 2040 | 16,130 | 4,461 | 27.7% | 120.5 |
| 2045 | 142,266 | 12,260 | 8.6% | 331.0 |

(Full year-by-year table for all 16 years, including the 12 intermediate
years, in the Activity Tracker item logging this work.)

**Total across all 16 solved years: $1,314.7M, undiscounted/nominal.** This
is the raw sum, not yet the present-value figure the SLCOE formula
actually requires — still needs discounting at the 4.5% real WACC (see
Appendix B, Assumptions) before being netted against costs in the final
calculation. Included here as the intermediate result, not the final one.

For scale: this 16-year cumulative total is smaller than a single year's
total system cost at the latest checkpoint alone (2045 objective value:
~$16.2B) — export revenue is a real, worth-including factor in this
project's SLCOE, but not a dominant one.

---
