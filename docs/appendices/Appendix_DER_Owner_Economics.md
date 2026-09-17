# Appendix — DER Owner Economics

**Extracted 2026-09-14 from `Reorganized_Appendices_Draft.md`, where it existed only inside a 4,682-line composite file.** That draft also carried stale copies of five appendices that have their own authoritative files; this one had no standalone version at all, which made it invisible to the index, untestable, and impossible to revise without editing a file about something else.

Lettering is deliberately omitted here. The scheme is being reworked into reader order (methods, scenarios, topics, reference) and a letter baked into the filename now would be wrong twice.

---

Ownership-split allocation methodology (80/10/10 utility/rooftop/parking-lot),
the Recommended VA Program composition (locational value adder, D-REC, and
event-based compensation), and the floor-price transition structure are
*(carried forward from the existing white paper section's A.5 and C.2-C.5,
relabeled and consolidated. No content changes.)*

**ELCC/capacity treatment — UPDATED, no longer "no content changes" (2026-08-16).**
VPP/owner-economics capacity revenue was originally computed using illustrative
flat placeholder ELCC assumptions (solar 40%, storage 95%) rather than PJM's
actual published class ratings. This has since been corrected in the
`DER_Owner_Economics` workbook tab itself (marked inline as "[CORRECTED]... 
DISCLOSED FIX APPLIED") to use PJM's real, current 2026/27 BRA class ratings
(see A.12 for the authoritative sourced table: Tracking Solar 11%, 4-hr
Storage 50%, 6-hr Storage 58%, 8-hr Storage 62% -- all materially lower than
the original placeholders). This appendix text had not yet caught up to that
workbook correction until this update; it now points to A.12 as the single
source of truth for current ELCC values rather than restating them here, to
avoid the two drifting out of sync again as PJM's own published ratings
change year to year (the 2026/27 values above already differ from 2025/26 --
see A.12's full BRA-over-BRA table).

Both directions of this correction push the same way: since capacity revenue
is a subtraction from cost (utility side) or an addition to cash flow (owner
side), the flat placeholders overstated capacity revenue in both scenarios.
Correcting to PJM's real, lower figures raises Scenario 1's SLCOE (less
capacity revenue offsetting new-build capex) and pushes Scenario 3's owner
NPV further negative (a smaller capacity-credit component on top of the
already-negative wholesale-compensation finding), not less negative.

**Not yet done, flagged rather than silently assumed away:** PJM's real ELCC
is not flat over a 25-year horizon either -- it declines with cumulative
penetration (see A.12's citation to Advanced Energy United/Ascend Analytics:
storage ELCC potentially falling from ~57% toward ~20% within a single BRA
cycle as more storage clears the market; NREL's own national projections
show solar's median capacity credit falling from ~21% in 2026 to ~3.5% by
2050). Given this project's own Scenario 1 storage buildout is exactly the
kind of large-scale addition that would drive this decline, using a single
corrected-but-still-constant ELCC value across the full 25-year horizon is a
real, disclosed simplification -- directionally conservative in the sense
that it likely still overstates capacity revenue in the model's later years,
compounding rather than offsetting the corrections above. A fully rigorous
treatment would tie ELCC to this project's own cumulative buildout at each
checkpoint rather than holding it constant; this has not been built.

**Double-counting verification (2026-08-16, prompted by a direct question
about whether owner/farmer-side benefits are counted twice into the
ratepayer-facing SLCOE).** This project's stated priority is ratepayer
benefit as the primary analysis; DER-owner economics (this appendix) and
agrivoltaic farmer lease income (the separate Agrivoltaics appendix) are
explicitly secondary, informational content, not intended to net against
or modify the primary ratepayer number. Verified directly against the
workbook rather than assumed: **zero formula cross-references exist in
either direction between the `Scenario3` and `DER_Owner_Economics` tabs.**
`DER_Owner_Economics`'s capacity payments, VPP revenue, and owner NPV
calculations are structurally isolated from Scenario3's ratepayer-facing
SLCOE/Net Cost -- there is no live double-counting mechanism, because
these are two fully independent calculations, not one feeding the other.
This is the correct architecture, not a lucky accident: Scenario3's core
SLCOE reflects the total physical system cost (how much solar/storage
gets built and what it costs), which does not change based on who legally
owns which share of the 80/10/10 split -- only `DER_Owner_Economics`'s
distributional question (what would a hypothetical owner's cash flow look
like) is affected by ownership, and that question was never wired back
into the ratepayer number.

**Agrivoltaic vs. non-agrivoltaic lease treatment: already satisfied by
construction, no fix required.** Per explicit project direction, agrivoltaic
leases should be treated identically to non-agrivoltaic leases from the
ratepayer perspective. Verified: the model's solar O&M/land-cost assumption
($24/kW-yr, B.2) is a single, blanket figure applied uniformly to all
solar regardless of agrivoltaic status -- there is no agrivoltaic-specific
adjustment anywhere in the LP or the ratepayer-facing SLCOE calculation.
Agrivoltaic status is farmer-benefit-relevant information (the separate
Agrivoltaics appendix), not a ratepayer-cost differentiator, and the model
already reflects that correctly.

**Owner-side wholesale arbitrage revenue is a transfer payment, not new
system value -- a framing clarification, not a numerical fix.** Per
explicit project direction: wholesale arbitrage revenue captured by a DER
owner represents value that "would go to some other generator anyway" if
this specific DER did not exist -- a transfer among generation market
participants determined by which resource happens to serve the marginal
MWh, not new value the DER's existence creates. `DER_Owner_Economics`'s
owner-revenue calculations (Section H) use a wholesale-equivalent energy
price without this distinction stated explicitly; a reader could
otherwise misread owner NPV as representing new societal/system value
rather than a distributional transfer. This is a different mechanism from
the NSPM's wholesale market price effects (MPE) principle above (MPE
concerns how demand reduction shifts the clearing price paid by ALL
buyers -- a real, additive system effect; this concerns WHICH specific
generator captures an existing margin -- a transfer). Both are legitimate
BCA considerations under NSPM guidance, but they should not be conflated
with each other, and neither changes any figure already in this model --
only how the owner-side numbers should be interpreted.

**Regulatory basis for VPP/wholesale-market-participation assumptions:**
FERC Order No. 2222 requires all RTOs/ISOs to permit DER aggregation
participation in wholesale markets. For PJM specifically (Docket
ER22-962), FERC's own explainer documents a staged implementation: Capacity
Market participation targeted for February 1, 2027; Energy and Ancillary
Services for February 1, 2028. This timeline has a real history of
slippage (originally targeted February 2026, delayed twice), so should be
read as PJM's current target as of this writing rather than a firm
commitment -- but it is the actual regulatory basis for why VPP/wholesale
participation is a realistic modeling assumption for PJM-territory DERs
going forward, not merely a hopeful construct.

---
