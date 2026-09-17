# Common Mistake Log

## Purpose
A catalog of recurring or noteworthy mistake *patterns* -- not a chronological update record.
Each entry names a pattern, gives a real example of when it happened in this project, and states
how to catch or avoid it. The test is not "was this a big deal" (that's Internal_Debugging_Log.md's
territory for major LP/high-level problems) -- it's "could this same kind of mistake plausibly
happen again in a different context," which is what makes it worth naming as a pattern rather than
just fixing once and moving on.

Log structure established 2026-08-27, per direct user instruction. Populated below with patterns
already identified this session; not retroactively backfilled from every prior session.

---

## Pattern: Informal summary table vs. official numbered source

**The mistake**: when a source document has both an informal summary table (e.g. an early
overview section) and a separate, official, numbered/lettered reference (e.g. a formal appendix
with legal numbering), reading only the informal summary and citing its ordering as if it were the
official numbering.

**Real example**: Dominion's VPP Pilot filing was initially cited using an informal Table 1
summary's own ordering, mislabeling BYOD as program "#11" and Managed Charging as "#8/#9" --
when the filing's own official, legally-numbered Appendix C had BYOD as #5 and Managed Charging
as the single entry #9 (with #8 being a completely different, unrelated program). See
Internal_Debugging_Log.md entry #111 for the full correction record.

**How to catch it**: when a filing/report has both a plain-language overview and a
numbered/lettered official reference section, always verify against the official numbered version
before citing a number -- an informal summary's ordering is not a source of truth for numbering,
even when it's easier to read.

---

## Pattern: Mischaracterizing an existing value as an unreasoned placeholder

**The mistake**: seeing an existing number in a model without immediately-visible justification
and concluding it must be a rough, unreasoned placeholder -- without first reading the surrounding
comments, adjacent cells, or context that might show it was actually a deliberate, reasoned choice.

**Real example**: a prior turn's own plan described the existing $200/kW-summer / $100/kW-winter
VPP rate in the DER_Owner_Economics tab as a "rough, round-number placeholder" before making a
change. Reading the actual surrounding cells showed it was New Hampshire's own specific
ConnectedSolutions-family rate, deliberately chosen over Massachusetts's $275/$50 split because
Virginia's own demand analysis found a genuine winter-peak character that NH's structure better
matches -- a reasoned choice, not a placeholder. Caught and corrected before the mischaracterization
propagated into actually overwriting the value. See Internal_Debugging_Log.md entry #122.

**How to catch it**: before describing any existing value as a "placeholder," "rough guess," or
similar in a plan -- read the value's own surrounding context first. If a number has a comment,
citation, or adjacent rationale, treat that as the default explanation until direct evidence says
otherwise, not the reverse.

---

## Pattern: Stale figure surviving in an older raw-notes working file after a later correction

**The mistake**: a later research pass corrects an earlier, flagged-as-uncertain figure -- but the
original raw-notes or working file where the figure was first recorded is never updated to match.
A future turn that pulls "the sourcing notes" from that original file, rather than checking for a
later correction, silently reintroduces the stale value.

**Real example**: Prince William County's school counts were first recorded in
`xlsx_update/school_counts_raw.txt` as 62 elementary / 18 middle / 13-or-16 high (high school
count explicitly flagged as an unresolved discrepancy). A later research pass, prompted by a
direct follow-up request, found the corrected figures via a full NCES federal database count:
62/17/13, with the high-school figure independently confirmed via two Wikipedia articles stating
directly and sequentially that two named schools were "the 12th" and "the 13th" high school in the
division. The original raw-notes file was never edited to reflect this. When building
`school_rooftop_solar_assumptions.py`, the corrected 62/17/13 figures were used deliberately, with
a dedicated test guarding against a future edit accidentally copying the stale 62/18/13-or-16
figures back in from the original file.

**How to catch it**: when reusing a figure from an older working/notes file, check whether a later
turn or file superseded it before treating the older file as current -- especially if the older
file itself flagged the figure as an unresolved discrepancy. An unresolved flag in an old note is
a signal to search for a resolution, not a stopping point.

---

## Pattern: Elicitation-tool selection not reflecting actual user intent

**The mistake**: treating a selection that arrives through an interactive elicitation tool (e.g. a
button/option picker) as unambiguous, deliberate user intent -- without noticing when it
contradicts the user's own immediately-prior, explicitly-stated framing, which is a signal worth
a beat of hesitation before acting on it.

**Real example**: after the user's own message observed that estimating rooftop/parking-lot area
"infers an OO class structure," an elicitation tool offered three granularity options. A selection
came back for "Full individual schools now" (694 objects) -- but the user's next message clarified
this was an interface misclick while trying to enter a free-form comment, and their actual intent
("we are at a strategic level here... grouping by county/city is fine") was the third option, not
the first. No real damage occurred this time only because a subsequent file-write happened to fail
on an unrelated technical error before any content was produced -- not because the selection was
independently sanity-checked against the user's own prior framing before acting on it.

**How to catch it**: an elicitation-tool result is still worth a moment's sanity check against the
conversation's own recent context, the same as any other input -- particularly when the selected
option would mean doing substantially more work than the conversation's tone otherwise suggested,
or when it sits oddly next to something the user just said in their own words.

---

## Pattern: A regex meant to match a standalone token instead matches a substring at the start of a longer, unrelated word

**The mistake**: writing a regex with a word-boundary anchor (`\b`) only on ONE side of an
alternation group (e.g. `\b(ste|suite|unit)...`), intending to match standalone abbreviation
tokens like "Ste 130" -- but since both sides of a boundary check whether adjacent characters are
word/non-word, having the anchor on only the leading side lets the pattern match the first letters
of a completely unrelated longer word, as long as a boundary exists before it.

**Real example**: `strip_suite_and_unit()` in `query_nvrc_building_footprints.py` was written to
strip suite/unit designations (e.g. "Ste 130") from addresses before deduplicating by base street.
The pattern `r"\b(ste|suite|unit|...)\.?\s*[\w-]+\b"` matched "ste" at the *start* of "Sterling"
(there's a word boundary between the preceding comma+space and the "S"), then greedily consumed
"rling" as if it were a suite number -- silently deleting the city name from
"21631 Ridgetop Cir Ste 265, **Sterling**, VA 20166". Caught immediately by running a direct test
with a real Sterling, VA address before considering the fix complete -- not caught by reading the
regex and reasoning about it, only by actually executing it against real input.

**How to catch it**: a word-boundary anchor is only doing its full job when it's on both sides of
what needs to be a standalone token, not just the leading side -- `\b(keyword)\b`, not `\b(keyword)`.
More generally: any regex meant to match short, common substrings (abbreviations, unit codes,
2-4 letter tokens) is a strong candidate for accidentally matching inside longer, unrelated words,
and should be tested against realistic real-world strings that happen to contain the target
substring in an unintended position -- not just against the cases it's meant to match.

---

## Pattern: str_replace edit consumes a following section's header line without an equivalent replacement

**The mistake**: when `old_str` for an edit ends at or near a following section's header line, and
`new_str` doesn't include an equivalent header of its own, the edit can silently consume that
header -- leaving the next section's content still present but now unheaded, merged into whatever
precedes it.

**Real example**: recurred at least six times in one project (Internal_Debugging_Log.md entries
#91, #95, #96, #97, #100 x2, #107) -- most often inserting new content directly before an existing
`## N. Title` or `## 8. Summary` header consumed that header line. Caught each time via a standing
post-edit grep/header check, but the underlying editing habit that produced it did not change
after being caught the first few times. A deeper mechanistic finding from entry #100: even
including the following header in `new_str` as a deliberate safeguard did not reliably prevent the
issue on this file -- suggesting the real fix is anchoring `old_str`'s own end further into the
UNIQUE body content of the following section, past its header line, rather than trusting
header-line inclusion alone.

**How to catch it**: don't anchor `old_str` to end at the start of a following header. Anchor it to
end within the preceding section's own unique body content instead, so the edit boundary never sits
adjacent to a header line the edit doesn't intend to touch. If a header must be included for
uniqueness, treat that as a signal to extend `old_str` further into the section that follows, not as
a sufficient safeguard on its own -- verify with a post-edit header/sequence check every time
regardless.

---

## Pattern: A silently misplaced block in a long, sequentially-numbered file goes undetected because header-sequence checks alone can't catch it

**The mistake**: a block appended to a long, actively-growing, numbered file lands in the wrong
location (e.g. inserted mid-file instead of at the current end) while remaining internally
well-formed -- correct header, correct internal structure. A standard "are the headers present and
sequential" check passes, because it doesn't verify each block sits at the *position* it should,
only that headers exist and increment correctly wherever they are.

**Real example**: Internal_Debugging_Log.md entry #97 discovered a block that had been silently
inserted between entries #85-87 instead of appended at the file's actual end, sitting undetected
since entry #88 was originally written. Found only because a routine "check the end of the log
before appending" step happened to reveal the file's actual tail didn't match the expected next
entry number -- not by the standing header-check habit, which had already been passing the whole
time. A distinct failure mode from the header-consuming edit pattern above, not a variant of it.

**How to catch it**: a header-sequence check confirms headers are present and internally ordered,
not that each block is physically located where it belongs. After any append to a long,
actively-growing file, separately verify the file's own actual tail matches the expected next
entry/section -- don't rely on a sequence check alone to catch a misplaced-but-well-formed block.

---

## Pattern: Two files with the same name differing only by case coexist undetected, with no tooling flagging either as stale

**The mistake**: two files (or two intermediate outputs) share an identical name except for
letter case -- nothing in standard file listings, git status, or this project's own tooling treats
this as a collision worth flagging, so both persist silently, and whichever one gets read back
depends on which call happened to reference it.

**Real example, confirmed twice independently in this project's own history**: Internal_Debugging_
Log.md entry #25 found `hourly_2030_final.npz` and `hourly_2030_FINAL.npz` sitting side by side in
`/tmp` -- different sizes, different content, neither flagged as stale by anything in this
project's own tooling. Independently, in a later session's text-file reorganization pass,
`software_engineering_standards.md` (lowercase, current) and `Software_Engineering_Standards.md`
(capitalized, superseded, with a real, substantive Rule 8 wording divergence between the two) were
found coexisting the same way in the project's own outputs directory.

**How to catch it**: when listing or searching a directory for a specific file, do a
case-insensitive check for near-duplicate names, not just an exact-name lookup -- an exact match
finds the file you already know to look for, not the second copy you don't. Worth a standing habit
whenever a file is about to be treated as authoritative: confirm no case-variant sibling exists
first, rather than assume the filename alone is unique.


## Pattern: A name that follows a domain convention contradicts the ordinary reading, and the docstring does the work the name should

`demand_basis.VirginiaOnlyLoad` returned the GENERATION-side quantity -- what must be produced at
the generator, losses included. "Load" followed the utility-planning convention (what is needed to
serve load) rather than the ordinary reading (the quantity at the meter). The two differ by the
9.25% loss factor.

**The docstring said so plainly**, and warned that dividing it *"strips the losses back out and
understates generation need by roughly 9%."* That warning existed precisely because the name invites
the error.

**I read that docstring and made the error within the hour**, in the opposite direction: I described
the meter-side figure as "sales" and the generation-side figure as "load", which is backwards from
both the ordinary reading and from how the statute uses "sold".

**What makes this a pattern rather than a one-off:** the name was not wrong within its convention,
so nothing flagged it. A domain convention that inverts a common word is invisible to reviewers who
share the convention and misleading to everyone else -- and this project's readers include
legislators and county officials who do not share it.

**Sharpened by the same series having two correct treatments.** Dispatch uses it undivided;
statutory obligations divide by 1.0925, because Va. Code 56-585.5(C) sets the RPS requirement as a
percentage of energy "sold". Same number, opposite handling, sometimes within one function.

**How to catch it:** when a name and its docstring disagree about what a thing is, the NAME is the
defect -- a docstring is read once and a name is read every time. Renamed to
VirginiaOnlyGeneration across 45 occurrences in 19 files, and the basis question moved to
docs/Common_Reference.md section 1 so the next scenario does not re-derive it.


## Pattern: Carrying a metric from one domain into another where it measures the wrong thing

Every crop agrivoltaic study measures **biomass or grain**, so I carried biomass into the forage
case and treated declining tonnage under shade as the cautionary counterweight to Oregon State's
land-equivalent-ratio finding. I wrote that framing into the appendix limitations: *"shade reduces
herbage yield, and the optimistic and cautionary findings must be cited together."*

**Biomass is the wrong output for forage.** The relevant product is animal product. A shaded sward
with higher crude protein and higher fibre digestibility converts better per kilogram, so tonnage
understates the agricultural result:

    lamb growth        120 vs 119 g/head/day under panels vs open (P = 0.90)
    stocking           36.6 vs 30 lambs/ha -- 22% MORE ANIMALS
    liveweight         1.5 vs 1.3 kg/ha/day

The array did not merely fail to harm the animals; it supported higher carrying capacity at equal
per-animal performance. And the JDS 2026 study that found the biomass decline **also found protein
and digestibility up with minerals maintained**, concluding that quality offsets tonnage -- which I
had read for its biomass figure alone.

**What makes this a pattern:** the metric was correct in the domain it came from, so nothing flagged
it. Reporting the biomass decline would have been accurate and misleading at once -- the worst
combination, because it survives fact-checking.

**How to catch it:** when moving a finding between domains, ask what the OUTPUT of the receiving
domain actually is. Grain is the output of a grain crop; animal product is the output of a pasture.
The intermediate quantity is not the result.


## Pattern: A consolidation drops a scope qualifier, and the surviving text reads as universal

The standing new-build rule opens "For Scenario 1, 1B, 3, 3B, and 3C specifically (NOT Scenario 2,
which retains its own established CCGT-based new-build methodology)". When seven gas documents were
merged into one reference, the merged version starts at "any new gas capacity needed to fill a
shortfall...", and the carve-out is gone.

**The surviving sentence is not wrong. It is unqualified**, which reads as universal, and I acted on
it: I reported a conflict between Scenario 2's 6,500 MW of combined-cycle capacity and a
simple-cycle-only rule that had never applied to it.

**Why the consolidation is still right.** Seven fragmented documents cost more than one merged
document with a dropped clause -- the merge was undertaken precisely because "the CT capex figures
the project needed were in one file while another recorded 'no simple-cycle capex exists in the
code' as an open gap". The fix is not to un-merge.

**What makes this a pattern:** a scope qualifier is the easiest thing to lose in a merge, because it
often sits in a parenthesis before the substantive text, and the substantive text survives
grammatically without it. Nothing flags the loss -- the result is a complete, readable, confident
sentence about a wider case than the original covered.

**How to catch it:** when merging, treat every "for X specifically", "NOT Y", "except where" and
"applies to" as load-bearing and check it survives. And when a rule seems to conflict with an
established practice, read the ORIGINAL before concluding the practice is wrong -- the qualifier may
be in the source and not in the summary, which is exactly what happened here.


## Pattern: A broad `except` around code that cannot fail will only ever catch your own mistakes

`_cached_hydro_year` opened with:

    try:
        path = paths.weather_year(CACHED_PROFILE_FILE)
    except Exception:
        return None

`paths` was never imported -- not at module level, not in the function. Every call raised
`NameError`, the bare `except Exception` swallowed it, and the function returned `None` as though
the cache file were simply absent. **The committed 260 KB profile sat on disk and was never read
once.** The caller fell through to the NSRDB path and failed on a missing map image, which is the
exact error the cache had been built to eliminate -- so the fix appeared not to have worked, twice,
across two sessions of the user's time.

**What `weather_year` actually does is one `os.path.join`.** It cannot raise. I wrote the guard
against a failure mode that does not exist, and what it caught instead was my own missing import.

**What makes this a pattern rather than a typo:** a broad except is usually added defensively, at a
point where the author has not thought hard about what could actually go wrong. When the guarded
code genuinely cannot fail, the only exceptions it can ever catch are the author's own errors --
`NameError`, `AttributeError`, `TypeError` -- and it converts each into a plausible-looking fallback
value. The result passes every test that does not specifically exercise the cache hit.

**And it was fixed by accident.** Adding `import paths` inside the function, while making the
missing-cache case fail loudly, removed the `NameError` without my realising the import had been
the bug. A defect fixed without being diagnosed will recur.

**How to catch it:** before writing `except`, name the specific exception and the specific
circumstance that raises it. If neither can be named, the guard is not protecting against anything
known -- delete it, or narrow it to the exception that was actually in mind. Never `except
Exception` around a single library call that does not do I/O.

