# Work tracking migration — xlsx tracker to GitHub Issues

**EXECUTED 2026-09-12.** 26 labels, 3 milestones and 11 open issues created;
cross-references added; the xlsx frozen as an archive of closed items.

| tracker | issue | | tracker | issue |
|---:|---|---|---:|---|
| 56 | #1 | | 63 | #7 |
| 57 | #2 | | 66 | #8 |
| 59 | #3 | | 67 | #9 |
| 60 | #4 | | 68 | #10 |
| 61 | #5 | | 70 | #11 |
| 62 | #6 | | | |

Items 64, 65 and 69 were closed before migration and remain in the xlsx only. Item 58 closed
2026-09-12 when the merit order was wired in.

---

## Why move

`registers/Virginia_Grid_Analysis_Tracker_updated.xlsx` has three problems that showed up in
practice this week:

**It is a binary blob.** Git records that it changed, not what changed. A reviewer cannot see which
row moved from `NS` to `C` without opening two versions side by side.

**It cannot link to work.** Nothing connects tracker #57 to the commit that addresses it, or to the
module it concerns. The relationships live only in prose.

**It went un-updated for an entire session** (2026-09-11, eight trackable items) and nothing
noticed. An issue tracker that sits beside the code is harder to forget than a spreadsheet in a
subdirectory.

---

## Label scheme

Four axes. An issue may carry one from each, and the scenario axis may repeat.

### Scenario — *which scenarios does this affect?*

| label | colour | meaning |
|---|---|---|
| `scenario:1` | blue | VCEA/RPS compliance, firmed solar + storage |
| `scenario:1B` | blue | as S1 but 5% gas from 2045 |
| `scenario:2` | blue | statutory minimum build only |
| `scenario:3` | blue | distributed, agrivoltaic, FERC 2222 |
| `scenario:utility-preferred` | blue | the Dominion comparison case |
| `common` | grey | **affects every scenario** — shared model structure |

**An issue can be both.** Several items this week are `common` *and* `scenario:3` — they live in
shared code but were found through, or matter most to, one scenario. Forcing a single choice would
lose that.

### Domain — *what part of the work?*

`domain:model` · `domain:gas` · `domain:storage` · `domain:solar-siting` · `domain:agrivoltaics` ·
`domain:demand` · `domain:reserves` · `domain:pricing` · `domain:statute` · `domain:data` ·
`domain:docs` · `domain:process`

Mirrors `docs/INDEX.md`, so an issue points at the domain whose START HERE file to read first.

### State — *what is needed?*

| label | meaning |
|---|---|
| `decision-needed` | blocked on the modeler, not on work |
| `blocked` | blocked on another issue — say which in the body |
| `needs-data` | blocked on a source we do not hold |
| `in-progress` | actively being worked |

### Kind — *what sort of item?*

| label | meaning |
|---|---|
| `finding` | something discovered about the model or the world |
| `defect` | something wrong that needs fixing |
| `regression` | **a documented fix that stopped being true** — its own label because it happened twice |
| `research` | an external question to answer |
| `deliverable` | whitepaper or output work |

`regression` earns a dedicated label rather than being a `defect`: two occurred on 2026-09-11
(`all_hours_reserve` dormant, the `t_peak` rename reverting), and the pattern is worth being able
to filter for.

---

## Priority

Use **milestones**, not labels — they sort and show progress:

- `P1 — blocks results`
- `P2 — affects results`
- `P3 — improves quality`

---

## Migration plan

### What moves

**Open items only** — roughly 15 of 73 rows. Closed history stays in the xlsx as an archive, which
avoids re-litigating settled work and keeps the migration to an afternoon.

### Proposed mapping for the current open set

| # | title | scenario | domain | kind | milestone |
|---|---|---|---|---|---|
| 56 | Flat hourly energy dual — 2030 measured, 2045 unverified | `common` | `model`, `pricing` | `finding` | P1 |
| 57 | `all_hours_reserve.py` exists but is never called | `common` | `reserves` | **`regression`** | P1 |
| 58 | Gas merit order — sourced, ready to wire in | `common` | `gas`, `model` | `defect` | P1 |
| 59 | No import capability | `common` | `model`, `pricing` | `finding` + `decision-needed` | P2 |
| 60 | Nodal price zones + weather-driven prices | `scenario:3`, `common` | `pricing` | `research` | P2 |
| 61 | Foresight bracketing | `scenario:3` | `storage` | `finding` + `blocked` (by 56) | P2 |
| 62 | Accreditation under precautionary operation | `common` | `storage`, `reserves` | `research` | P3 |
| 63 | Documentation index | — | `docs` | `deliverable` | P3 |
| 66 | No ramp constraints | `scenario:1B`, `scenario:utility-preferred` | `model`, `gas` | `finding` | P2 |
| 67 | CT-specific VOM constant missing | `common` | `gas` | `defect` | P3 |
| 68 | Midday surplus demand flexibility | `scenario:3`, `common` | `demand` | `research` + `blocked` (by 58) | P2 |

**Note #58 moved to P1.** It was P2 as "adds realism." It is the mechanism by which *any* intraday
price structure can exist — gas output already varies across the day, but with a single gas price
that variation cannot reach the dual. It unblocks 56, 61 and 68.

### Sequence

1. Create labels and milestones
2. Open the ~15 issues, bodies copied from tracker descriptions (they are already detailed)
3. Add `Blocked by #N` / `Blocks #N` cross-references
4. Add a line to `docs/README.md` pointing at Issues for open work and the xlsx for history
5. Freeze the xlsx: add a header note that open tracking moved, with the cutover date

### What to watch

**The repo is public**, so issues are public. Fine for methodology and defects; worth a moment's
thought before posting anything pre-decisional about scenario choices or anything quoting
unpublished sources.

**Commits can close issues** — `Fixes #57` in a message links and closes on merge. That is the main
practical gain, and it directly addresses how #57 and the `t_peak` rename went stale: the work and
the record would no longer be separate artifacts.
