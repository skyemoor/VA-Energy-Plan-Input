# VA-Energy-Plan-Input

Open modeling of pathways to Virginia Clean Economy Act (VCEA) and Renewable Portfolio
Standard (RPS) compliance for the Dominion Energy Virginia service territory, intended as
input to the Virginia Energy Plan and to the Virginia Department of Energy.

Everything here runs on **public data**, so any result can be independently reproduced.

## Why this exists

Virginia's projected electricity demand has roughly doubled since the VCEA was enacted in 2020.
HB 895 / SB 448 (signed April 2026) raised Dominion's storage mandate to 16,000 MW
short-duration plus 3,480 MW long-duration by 2045. Planning documents filed before that law
cannot reflect it. This work provides an independent analysis of what enacted law requires,
using methods and data anyone can check.

## Scenarios

| | Description |
|---|---|
| **S1** | Full VCEA/RPS compliance; firmed solar co-located with storage, no standalone storage |
| **S1B** | S1 with a 5% gas allowance from 2045 |
| **S2** | Minimum statutory build only (RPS D.2, E.2, E.4) |
| **S3** | S1 plus distributed solar: 10% rooftop, 10% parking canopy, agrivoltaics, FERC 2222 participation |

## Layout

- `lp_package/` — model classes: LP formulation, solver drivers, scenario classes, provenance tracking
- `tests/` — baseline-locked test suite
- `scripts/` — orchestration and one-off analyses
- `docs/` — methodology, engineering standards, and the internal debugging log
- `registers/` — provenance register (which figures are current) and citation tracker
- `data/weather_years/` — derived hourly weather years (April–March hydrological convention)

## Reading the results

**Start with `registers/Provenance_Register.xlsx`.** Every reported figure carries a status:

- `current` — believed correct and citable
- `provisional` — computed, but resting on a stated limitation; not settled
- `superseded` — replaced, with a pointer to the replacement

Most 2045 figures are currently **provisional**. They rest on a single design weather year and
a pinned distributed-solar siting cap. They should not be quoted as settled.

## Known limitations

Stated plainly, because they bound what this work can support:

1. Build optimization uses a single design weather year; cross-testing against eight historical
   years is a separate validation step, not part of the sizing.
2. No probabilistic resource adequacy — no LOLE, no forced outages, no load forecast error.
3. The investment model (LP, perfect foresight) and the dispatch validation model (heuristic)
   differ; that gap has not been fully quantified.
4. Single-node — no transmission representation, which the secondary transmission-avoidance
   objective needs.
5. No technology cost-decline curves applied to 2045; costs are likely conservative.

`docs/Internal_Debugging_Log.md` records hypotheses that were tested and discarded, not just
those that worked.

## License

Licensed under the **Apache License, Version 2.0**. See [LICENSE](LICENSE).

You may use, modify, and redistribute this work, including commercially, provided you
retain attribution and the license notice. The license includes an express patent grant
and requires that modified files be marked as changed.

This work is offered freely as public input to Virginia energy planning. Independent
reproduction, extension, and critique are all explicitly welcomed.
