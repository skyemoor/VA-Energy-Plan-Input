# Rationale Log

The explanatory justification for each rule in `claude.md` -- why each rule exists, what specific incident or bug motivated it, and pointers to the debugging-log entries that document the full history. This file is reference material for understanding *why* a rule was established; `claude.md` itself contains only the actionable rule text needed to follow the standards day to day.

### Rule 1: Extend any existing OO structure

**Why this is a rule, not a preference**: entries #51-54 in Internal_Debugging_Log.md are the direct cost of not following this from the start. Three separate, free-standing scripts (compute_scenario1b_tier123_rggi_CORRECTED.py, compute_scenario2_tier123_full20yr_CORRECTED.py, compute_scenario2_rggi_CORRECTED.py) independently reimplemented the same year-loop/PV-aggregation logic. Two of the three shared an undiscovered bug (a stale, un-CPI-adjusted formula module) precisely because they were separate implementations that never got cross-checked against each other or against a trusted baseline. Consolidating this into SocialCostRGGIMixin fixed the bug in one place and made it structurally impossible for the three scenarios' own figures to silently drift apart again -- the class hierarchy is a correctness mechanism here, not just tidiness.

### Rule 2: Every shared calculation needs a test that locks it to a trusted baseline

**Additional context on Rule 2.4 specifically**: established 2026-08-23 directly because Scenario 1B and Scenario 2 initially had bug-specific regression tests but no end-to-end check on their own output figures, unlike Scenario 1 -- an uneven, incomplete pattern that itself risked hiding exactly the kind of error Rule 2 exists to catch.

**Why this is a rule, not a preference**: the SocialCostRGGIMixin refactor itself only caught the CPI-adjustment bug (entry #54) because building it forced a cross-check against Scenario 1's own established figure. Without that check, the refactor would have faithfully consolidated a wrong answer into a single, authoritative-looking place -- arguably worse than three inconsistent wrong answers, since a single "authoritative" wrong figure is more likely to be trusted without further scrutiny. The test suite exists so this check happens automatically, every time, not only when someone happens to think to do it. Applying it unevenly across scenarios (Rule 2.4) reintroduces the same risk in a different shape: a gap that looks like coverage exists, until the one scenario without a baseline check is exactly the one that drifts.

### Rule 3: Any time a code file is modified, examine the test suite for whether it needs upgrading

**Why this is a rule, not a preference**: a test suite that isn't actively maintained alongside the code degrades into false confidence -- worse than no suite at all, since "13 passed" reads as a clean bill of health regardless of whether the 13 tests still exercise anything meaningful about the current code. The cost of checking is a few minutes; the cost of a stale suite is a wrong answer that looks verified.

### Rule 4: Cross-verify against an independent baseline as a standing habit

**Why this is a rule, not a preference**: Scenario 1B's un-reproducible $42.14 figure (entry #38-39) led directly to finding the 2040-vs-2044 capex-linking bug. The CPI-adjustment bug (entry #54) surfaced only because building the SocialCostRGGIMixin forced a comparison against Scenario 1's own established figure -- and even then, the first comparison target chosen (the pre-existing compute_scenario2_tier12_20yr.py) turned out to share the same bug as the new code, producing false agreement; only a comparison against Scenario 1's own, differently-sourced figure caught it. The lesson generalizes past formal testing: verification against one already-trusted source can still fail if that source shares the same defect.

### Rule 5: Fail loudly, never silently default or guess

**Why this is a rule, not a preference**: a wrong number that fails silently costs nothing to produce and everything to catch later, often after it has already been trusted and built upon (exactly what happened with entries #52-53's own stale-CPI figures, which looked complete and were presented as final before the underlying bug was found).

### Rule 6: Single source of truth for constants

**Additional context on Rule 6.1 specifically**: WACC, BASE_YEAR, CCGT capex, and the RGGI schedule were all centralized here specifically because independent local copies had drifted or risked drifting.

**Why this is a rule, not a preference**: this is distinct from Rule 1 (shared behavior) -- this is about shared parameters, and the assumptions.py centralization eliminated an entire class of drift bugs before this session's own work even began, the same category of problem Rules 1/2 address for calculations rather than constants.

### Rule 7: Unambiguous naming, especially for concepts with a natural opposite

**Why this is a rule, not a preference**: target_share, used ambiguously as either "target clean share" or "target gas share" depending on context, was the direct root cause of Scenario1BSolver's own 0.95-instead-of-0.05 bug (entry #51). The rename to gas_target_share (entry #52) was a genuine fix, not cosmetic -- the ambiguity was load-bearing in the bug, not incidental to it.

### Rule 8: Configurable parameters for decisions and for facts, avoid hard coded values

*(No rationale paragraph was included for this rule in the version provided -- flagged, not silently filled in.)*

### Rule 9: Physical invariants checked automatically after every solve, not eyeballed

**Why this is a rule, not a preference**: these checks caught real problems this session without requiring manual inspection each time -- exactly the leverage automated invariant-checking is supposed to provide, and exactly what an ad-hoc, print-and-eyeball verification habit would eventually miss under time pressure.

### Rule 10: Comments explain why, with a pointer to the log entry that justifies it

**Why this is a rule, not a preference**: nearly every fix this session follows this pattern already (e.g. additional_peaker_mw's own default of 0.0 is explained inline with a pointer to entry #51, not left as an unexplained magic default). It's what makes the reasoning behind a choice recoverable without re-deriving it from scratch or re-reading an entire log entry to understand one line of code.

### Rule 11: Increment/build quantities floored at zero explicitly, with the physical reasoning stated inline

**Additional context on Rule 11.3 specifically**: this pattern has been applied manually, ad-hoc, at least four separate times this session (2045-vs-2044 capex, each of the relinked 2041-2043 years, etc.) despite not yet being centralized into a shared helper.

**Why this is a rule, not a preference**: this exact class of omission (failing to floor a fresh increment at zero) is a specific case of the broader 2040-vs-2044/2043 linking bug found repeatedly this session (entries #51, and again while assembling the Scenario 1B rebuild) -- worth naming as its own rule since it recurred independently more than once before being caught each time.

### Rule 12: Always use readable, unambiguous names for variables, constants, functions, and classes

**Why this is a rule, not a preference**: established directly, 2026-08-25, as a standing rule rather than left implicit. Distinct from Rule 7's own justification (a specific, already-occurred bug) -- this rule is preventative rather than a fix for a specific past incident, extending the same underlying concern (a name should never be a source of ambiguity a reader has to resolve by inference) to every naming decision, not only the opposite-concept case Rule 7 was written to address.
