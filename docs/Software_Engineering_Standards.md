## Software Engineering Standards
 
Standing rules for this project's own codebase, read this before writing or modifying any code.
 
### Rule 1: Extend any existing OO structure -- do not add free-standing scripts for logic another class already owns. When creating code where no existing OO structure is present, consider other similar tasks that would likely have common attributes and/or services, then conceptualize an OO structure.
 
checkpoint_solver.py is this project's own class hierarchy (CheckpointSolver → Scenario1Solver/Scenario1BSolver/Scenario2Solver, plus composable mixins like ReserveMarginMixin and SocialCostRGGIMixin). Other class hierarchies exist for other areas within the project. When a new calculation is needed:
1.	First check whether it belongs on an existing class or mixin. If every scenario needs it and the underlying formula is the same (differing only in scenario-specific inputs), it belongs in a shared method or mixin -- not reimplemented per scenario.
2.	If it's genuinely scenario-specific, it's a method override on that scenario's own subclass, following the same pattern get_existing_new_mw() already establishes: the base class/mixin defines the shared logic and calls an abstract hook; each scenario class implements only the hook.
3.	Free-standing scripts (compute_*.py, solve_*.py) are for orchestration and one-off analysis, not for logic that will be called more than once across scenarios. If a second scenario needs the same calculation a free-standing script already has, that is the signal to move the logic into the class hierarchy, not to copy the script.
### Rule 2: Every shared calculation needs a test that locks it to a trusted baseline
 
test_checkpoint_solver.py is the standing test suite. Before trusting any new shared method's own output:
1.	Find or establish a known-good baseline -- a figure already independently verified (ideally from a different code path, so the comparison is a genuine cross-check, not the same bug checking itself).
2.	Write a test that reproduces that baseline exactly (or within a stated, small tolerance), using the real code path, not a synthetic stand-in, wherever the real path is fast enough to run in a test.
3.	Every bug found and fixed in this codebase gets a regression test, named and documented well enough that the next person (or the next session) understands what class of error it guards against without needing to re-read the full debugging-log entry. See test_checkpoint_solver.py's own four test classes for the pattern: each one's docstring names the specific bug and the log entry that found it.
4.	Standard requirement, applied uniformly, not just where a bug happened to be found: every scenario gets its own end-to-end, baseline-locked test for every shared calculation it uses -- not only the scenario where a bug happened to surface. See TestSocialCostRGGIMixinCorrectness's three test_scenarioN_reproduces_established_figures_exactly tests for the pattern every new scenario (or new shared calculation on an existing scenario) should follow: same structure, same baseline-comparison approach, scenario-specific only in which dispatch files it loads.
### Rule 3: Any time a code file is modified, examine the test suite for whether it needs upgrading -- and if so, upgrade it, every time
 
This applies to every edit, not just refactors or bug fixes:
1.	Before considering any edit to lp_package/ complete, check test_checkpoint_solver.py against the change. Does the edit change a return value, a formula, a default, a class's own public interface, or a file path a test depends on? If yes, the test suite is now potentially stale relative to the code, even if every test still technically passes.
2.	"Still passes" is not the same as "still correct." A test can pass trivially after an edit if the edit didn't touch the code path that test exercises, or if a baseline figure embedded in the test was itself never updated to match a legitimate change elsewhere. Check the actual content of what's being asserted, not just the exit code.
3.	If the change legitimately shifts a baseline (e.g. a new, correctly-sourced constant changes an established figure), update the test's own expected value in the same change, with a comment explaining why the baseline moved and pointing to the debugging-log entry that justifies it -- never silently loosen a tolerance or delete an inconvenient assertion to make a test pass.
4.	If the change adds new shared logic, apply Rule 2 directly: it needs its own baseline-locked test before the change is done, not as a follow-up.
5.	Run the full suite (python3 -m pytest test_checkpoint_solver.py -v) after every edit, not a subset chosen because it seemed relevant -- a change in one method can have non-obvious effects on another (exactly what MRO/inheritance makes possible in this class hierarchy).
### Rule 4: Cross-verify against an independent baseline as a standing habit -- not only at formal test time
 
Rule 2 covers this for the test suite specifically; this rule states the broader habit, which paid off before any formal test existed:
1.	Before presenting any new figure as correct, ask whether it agrees with an independently-derived version of the same thing -- a different script, a different scenario's own analogous figure, or a value already established in prior work.
2.	A single calculation path, however carefully built, is not sufficient evidence of correctness on its own. Agreement between two independent paths is much stronger evidence than internal consistency within one path.
3.	When two independent figures disagree, chase the disagreement to its actual root cause before accepting either one -- don't assume the newer, more carefully-built, or more recently-checked path is the correct one by default.
### Rule 5: Fail loudly, never silently default or guess
 
1.	A method that needs a value it wasn't given should raise, not substitute a plausible-looking guess. Scenario2Solver.get_existing_new_mw() raises ValueError if peak_gas_mw was never set, rather than falling back to some default split that would produce a wrong-but-unremarkable-looking number.
2.	An abstract method with no sensible universal default should have no default at all. SocialCostRGGIMixin.get_existing_new_mw() raises NotImplementedError unconditionally -- there is no "reuse Scenario 1's own split" fallback, because a silently-wrong default (reusing the wrong scenario's own methodology) is worse than a crash that points directly at the missing override.
3.	When in doubt between "guess something reasonable and continue" and "stop and demand the caller be explicit," choose the latter for anything that feeds into a reported figure.
### Rule 6: Single source of truth for constants
 
1.	A parameter used in more than one place and/or defined by a policy or assumption belongs in assumptions.py, not duplicated locally in each file that needs it.
2.	When a value must legitimately be re-derived in more than one place (e.g. a sourced constant documented with its own citation in the file that originally derived it), add a runtime assertion cross-checking the two rather than trusting them to stay in sync by convention. See compute_tier123_final.py's own CPI_DEFLATOR_2020_TO_2026 assertion against assumptions.py's copy as the pattern.
3.	Before adding a new named constant, check assumptions.py first -- a re-derivation of an existing value under a new name is exactly the kind of duplication Rule 6 exists to prevent.
### Rule 7: Unambiguous naming, especially for concepts with a natural opposite
 
1.	When a quantity could reasonably be read as either of two opposite things (a clean share vs. a gas share; an existing value vs. a new increment), the name must disambiguate, not rely on context or convention to carry the distinction.
2.	Always use a longer, self-documenting name over a shorter, ambiguous one, especially for any value that flows through multiple layers of the call stack before being used.
3.	When an ambiguous name is found, rename it project-wide in one pass (with a context-aware substitution that doesn't corrupt already-correct usages of a similar name), not just at the one call site where the ambiguity happened to cause a problem.
### Rule 8: Configurable parameters for decisions and for facts, avoid hard coded values
 
1.	A value that reflects a specific, revisitable DECISION -- a turbine size, a peaker capacity, a scenario-defining threshold -- belongs as a constructor parameter or configurable attribute, not a hardcoded literal inside a method body, even if only one value has ever been used so far.
2.	Ask the modeler first, when considering hardcoding any number.
3.	Every constant or value used in this project must be categorized under one of the following source types when documented (e.g. in the Assumptions & Sources tab, or in a code comment/docstring):
#### VA Law
Data points found in the VCEA, RPS, or other VA code.
 
#### SCC Policy
Data points found in SCC statements, rulings, etc.
 
#### Common Derived Data
Data the team itself derived -- such as load demand modifications using 2023 data altered to reflect increasing numbers of data centers, etc.
 
#### Mathematical/Definitional Fact
Constants or values commonly used in math or physics -- e.g. unit conversions (kWh↔BTU, metric↔US tons).
 
#### Federal Data
Non-VA-specific federal statistical/data agency sources -- e.g. EIA, NOAA.
 
#### Federal Direction
Federal regulatory or standards-setting bodies -- e.g. FERC, NERC, and related.
 
#### PJM
Data associated with PJM Interconnection specifically -- zonal load, LMPs, capacity market results, and similar PJM-sourced data.
 
#### Third-Party Research
Independent industry or technical analysis -- e.g. Lazard, NREL, academic papers, engineering/safety standards (e.g. NFPA 855).
 
#### DEV
Data associated with Dominion Energy Virginia's own filings, statements, tariff pages, or published claims.
 
#### AEP
Data associated with American Electric Power's own filings, statements, tariff pages, or published claims (including its VA-jurisdiction subsidiary, Appalachian Power Company).
 
#### Other Utility Filings & Statements
A regulated utility's own published claims, tariff pages, or filings, for any utility not specifically broken out above -- distinct from SCC Policy because these haven't necessarily been ruled on or approved.
 
#### Modeler Assumptions
Anything the modeler has stated as direction other than the above -- the catch-all for anything not covered by the source types preceding it.
 
### Rule 9: Physical invariants checked automatically after every solve, not eyeballed
 
1.	Any invariant that must hold for a result to be physically valid -- zero unserved energy, no simultaneous charge/discharge, monotonically non-decreasing build variables across checkpoints -- gets checked in code, immediately after the solve that could violate it, not inspected manually or assumed from a plausible-looking objective value.
2.	These checks raise, they don't warn and continue -- verify_result() and _verify_monotonicity() both raise rather than log a warning, because a result that fails a physical invariant is not usable regardless of how the rest of the output looks.
3.	New solve paths inherit these checks automatically by extending CheckpointSolver rather than reimplementing the solve loop -- another concrete benefit of Rule 1's own OO-structure requirement.
### Rule 10: Comments explain why, with a pointer to the log entry that justifies it -- not just what
 
1.	A comment describing what code does is rarely worth its own maintenance cost --  code with fully readable, unambiguous parameters, names, and branching logic already says what it does. A comment is worth writing when it explains why a non-obvious choice was made, especially when the obvious-looking alternative was tried and found wrong.
2.	Reference the specific debugging-log entry that justifies a non-obvious value or design choice, so a future reader (or a future session) can go verify the reasoning in full rather than take the comment's own summary on faith.
3.	When fixing a bug, the comment at the fix site should name the specific wrong behavior being corrected, not just describe the new, correct behavior in isolation -- so a future edit doesn't accidentally reintroduce the same error by "simplifying" what looks like an odd, unexplained special case.
### Rule 11: Increment/build quantities floored at zero explicitly, with the physical reasoning stated inline
 
1.	Any calculation of a "fresh increment" (this year's new build, on top of a prior, degraded total) must be explicitly floored at zero -- max(0.0, current_total - prior_total * degradation_factor) -- never left to produce a negative value even transiently.
2.	State the physical reasoning at the point of the floor, not just the mechanical max(0.0, ...) -- e.g. "no un-building an asset" -- so the floor reads as a deliberate physical constraint, not an arbitrary numerical safeguard.
3.	This pattern is not yet centralized into a shared helper -- TestFreshIncrementNeverNegative documents the required behavior specifically so a future centralization has something concrete to be checked against. Centralizing this into a shared utility function is flagged here as follow-up work, not yet done.
### Rule 12: Always use readable, unambiguous names for variables, constants, functions, and classes
 
1.	This is broader than Rule 7. Rule 7 addresses one specific failure mode -- a name that could be misread as its own opposite. This rule is the general case: every name should be readable and unambiguous on its own, whether or not an opposite concept is involved.
2.	No abbreviations, single-letter names, or terse fragments where a clear word or short phrase would fit -- peak_gas_mw over pgm, battery_capacity_stated_kwh over cap_kwh. The cost of a longer name is trivial; the cost of a name that requires guessing or checking is not.
3.	A name should describe what a value is or what a function does, not merely hint at it. If a value carries a caveat that matters for correct use (a derived figure resting on a now-unreliable assumption, a figure that should not be treated as settled), that caveat belongs in the name itself where practical -- see BATTERY_CAPACITY_DERIVED_KWH_DO_NOT_USE in dominion_school_bus_v2g_assumptions.py for the pattern: the name alone stops a future reader from using it incorrectly, without requiring them to have first read the surrounding comment.
4.	This applies uniformly -- constants, function/method names, class names, loop variables, test names. A quick loop counter in a short-lived, obvious scope is the narrow exception; anything that outlives a few lines or crosses a function boundary gets a real name.
### Rule 13 Log all changes
1. Always update the build.log with the request change text and the code module.
2. If any results change values in the VA SLCOE, update them after notifying the modeler
3. Log any data sources used to extract data for coding use or any other analytical use.
4. If there is a substantive problem solved, enter the issues, options considered and their tradeoffs, and the solution that worked in the debugging-log
5. Update the Virginia grid analysis tracker updated.xlsx


## Practical checklist before considering any code change complete
- Does this logic already exist somewhere else in the class hierarchy? If yes, extend/override, don't duplicate. (Rule 1)
- If this is genuinely new shared logic, does it belong on a base class or mixin, with scenario-specific parts as overridable hooks? (Rule 1)
- Is there a trusted baseline this output can be checked against? If yes, has it actually been checked (not just assumed consistent)? (Rule 2)
- Does EVERY scenario using this calculation have its own baseline-locked test, not just the one where a bug happened to surface? (Rule 2.4)
- Has the existing test suite been examined against this specific change -- not just re-run, but checked for whether any assertion's own expected value needs updating? (Rule 3)
- If a baseline legitimately moved, was the test's expected value updated in this same change, with a comment pointing to the debugging-log entry that justifies the new figure? (Rule 3.3)
- Does this new figure agree with an independently-derived version of the same thing, not just internal self-consistency? (Rule 4)
- Does any function that needs a value it might not receive raise explicitly, rather than silently defaulting or guessing? (Rule 5)
- Is every constant sourced from assumptions.py (or cross-checked against it via assertion, if legitimately re-derived elsewhere), rather than a new local duplicate? (Rule 6)
- Could this name be misread as its own opposite (clean vs. gas, existing vs. new, total vs. incremental)? If so, rename before proceeding. (Rule 7)
- Is every hardcoded number either (a) a revisitable decision that should be a parameter instead, or (b) correctly categorized under one of the source types listed in Rule 8? (Rule 8)
- Does every new solve path inherit (not reimplement) the standing physical-invariant checks -- unserved energy, simultaneous dispatch, monotonicity? (Rule 9)
- Does every non-obvious choice have a comment explaining why, with a pointer to the debugging-log entry that justifies it? (Rule 10)
- Is every fresh-increment/build calculation explicitly floored at zero, with the physical reasoning stated inline? (Rule 11)
- Is every name -- variable, constant, function, class -- readable and unambiguous on its own, without requiring the reader to check a comment or infer intent? (Rule 12)
- Run python3 -m pytest test_checkpoint_solver.py -v -- the full suite, not a subset -- before considering the change done.
 
