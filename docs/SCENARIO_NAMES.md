# Scenario Naming

Licensed [CC BY 4.0](../LICENSE-DOCS).

Presentation names are used in the whitepaper and any external communication. Short codes are
stable internal identifiers used in code, filenames, and test baselines.

| Presentation name | Code | Appears in code as |
|---|---|---|
| Build to Zero | `S1` | `Scenario1Solver`, `Scenario1WithReserveMargin`, `VA_YYYY_Scenario1_hourly_*.csv` |
| Build to Zero, 2045 Gas Exception | `S1B` | `Scenario1BSolver` |
| Statutory Floor | `S2` | `Scenario2Solver`, `build_scenario2_problem()` |
| Distributed Build | `S3` | `Scenario3Solver`, `Scenario3WithReserveMargin`, `scenario3_build.py` |
| Moderated Demand | `S5` | not yet implemented |
| Utility Preferred Plan | — | not yet implemented |

## Why codes are not renamed

Renaming class and file identifiers would break baseline-locked tests (Software Engineering
Standards Rule 2) and stale every cross-reference in `docs/Internal_Debugging_Log.md`, for purely
cosmetic benefit. The codes are treated as stable identifiers; presentation names may be revised
without touching code.

## Why the presentation names changed

The earlier labels had three problems:

1. **"Scenario 2" implied less compliance than Scenario 1.** After HB 895 / SB 448 it contains
   20,000 MW of storage — a very large build. "Statutory Floor" names the mechanism (this is what
   the law compels, and nothing beyond it) without implying scale.
2. **Numbering implied a preference ranking.** These are alternatives, not an ordering.
3. **"Full compliance" became ambiguous** once the physical and statutory bases were separated.
   A scenario can satisfy § 56-585.5 through certificate retirement or deficiency payment while
   burning gas. Names now describe what a scenario *builds*, and compliance is reported
   separately on both bases.
