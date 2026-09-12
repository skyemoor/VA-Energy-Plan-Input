# Documentation

> **Start with [`INDEX.md`](INDEX.md)** — documentation organised by domain, with entry points
> marked. Check it before starting work in any domain.

Licensed under [CC BY 4.0](../LICENSE-DOCS) — free to share and adapt with attribution.

| File | Contents |
|---|---|
| `Internal_Debugging_Log.md` | Numbered, dated record of problems found and how they were resolved — including hypotheses tested and discarded |
| `Northern_Virginia_Solar_Assessment_Methodology_and_Findings.md` | Four-county distributed solar siting assessment (Loudoun, Prince William, Arlington, Fairfax) |
| `Weather_Year_Robustness_Approaches_and_Findings_2026-08-23.md` | Weather-year selection and cross-testing methodology |
| `Software_Engineering_Standards.md` | Standing code rules for this project |
| `DATA_SOURCES.md` | Provenance and retrieval for all external data |
| `claude.md` | Working process conventions |

**Note on the debugging log:** it deliberately records analytical dead ends alongside
successes. A hypothesis tested and refuted by evidence is part of the method, not a defect
in it, and publishing that record is intentional.

## Session protocol: documented-fix audit

`python3 scripts/audit_documented_fixes.py`

**Cadence (set 2026-09-12): hourly during an active session, and again whenever a session resumes
after more than an hour idle.** It reads files and greps — it does not solve — so there is no
reason to skip it.

It checks that things the documentation says are fixed, wired in, or standard are actually true of
the code *now*. Two regressions on 2026-09-11 prompted it, both found by reading code rather than
documentation:

- `all_hours_reserve.py` implements what `Weather_Year_Robustness_...2026-08-23.md` calls the
  "current standard" — and nothing calls it
- a `t_peak` rename done 2026-08-23, *for the very reason it was needed*, did not survive, and the
  same class of analysis error recurred

**A failing check means either the code regressed or the document is wrong. Both need fixing;
neither should be left.** `all_hours_reserve` currently fails by design — it is a known open item
(tracker #57), and the audit is expected to keep failing until it is wired in or the document is
corrected.
