# Dominion's FRR / RPM capacity status

**Research note, 2026-09-11.** Establishes which capacity construct Dominion operates under, because
it determines whether modelling Virginia as self-supplying its capacity is *correct* or
*conservative*.

---

## The record

| date | status |
|---|---|
| through **31 May 2021** | procured capacity through the **PJM RPM** auction |
| **June 2021 or June 2022** — sources disagree, see below | elected the **FRR alternative** |
| **2 May 2024** | *"publicly provided notice of its **termination of FRR status** and election to return to procuring its capacity obligation through the PJM annual capacity auction"* (SCC 2025 Combined Annual Report) |
| **current** | *"Dominion Energy **currently participates in RPM** capacity market"* (2025 IRP Update) |

**Dominion is not presently an FRR entity.** It elected FRR, ran under it for roughly two to three
years, and terminated that election in May 2024. The RTO Insider piece of July 2024 — FERC allowing
planned capacity resources to shift from FRR to RPM — documents that transition, not an ongoing FRR
position.

**Appalachian Power is different**: APCo *"has always participated through the FRR since joining PJM
in 2004."* If any Virginia utility is treated as self-supplying, it is APCo, not Dominion — and APCo
is outside the DOM Zone this analysis models.

### An unresolved date discrepancy

SCC filing PUR-2024-00193: *"Beginning June 1, 2021, the Company elected the FRR alternative."*
SCC 2025 Combined Annual Report: *"Dominion elected FRR status beginning on June 1, 2022."*

Not material to the current-status finding, but recorded rather than silently picking one.

---

## What this means for the capacity modelling assumption

Under **RPM**, Dominion **procures** its capacity obligation through the PJM auction rather than
self-supplying it. The DOM Zone is its Locational Deliverability Area and carries its own
reliability requirement, but the obligation is met by buying cleared capacity — not necessarily by
building it.

**So modelling Virginia as building its own capacity IS a conservative simplification**, and the
earlier reasoning that FRR made self-supply correct does not apply.

### But the conservatism is smaller than it looks, for a reason Dominion itself states

From the 2025 IRP Update:

> *"For resources offered under the RPM construct, PJM procured 134,205 MW of unforced capacity for
> 2026/2027. Excluding resources offered under the Fixed Resource Requirement alternative, PJM
> calculated an RTO reliability requirement of 134,414 MW of UCAP. In other words, **PJM already
> finds itself on the verge of falling short of its capacity targets**. With **the DOM Zone a net
> importer of energy**, this further underscores the need for additional capacity."*

Two things follow:

**Buying capacity requires someone else to have built it.** PJM cleared 209 MW *below* its own
reliability requirement for 2026/27. A planning model that assumes Virginia can buy its way out of
building assumes regional surplus that does not currently exist.

**Dominion states the DOM Zone is a net importer.** That is the utility's own characterisation, and
it bears directly on this project's absence of an import variable — see `MODEL_WIDE_FINDINGS.md` §3.
The zone imports today; our model cannot.

The IRP also records a **$444.26/MW-day** capacity price for Dominion *"due to system constraints
and lower quantities of available generation within the PJM DOM Zone"* — and notes the 2026/27 and
2027/28 BRAs have **price caps**, so *"to the extent the market clears at the price cap, any needs
would not be visible in a market clearing at the price cap."* Scarcity is being masked by the cap.

---

## The distinction that survives regardless of FRR or RPM

FRR and RPM are **capacity-market constructs**. Neither changes who the Balancing Authority is.

| | who holds it | affected by FRR/RPM election? |
|---|---|---|
| **Capacity obligation** | Dominion — bought (RPM) or self-supplied (FRR) | **yes** |
| **Contingency reserve** (NERC BAL-002) | **PJM**, as Balancing Authority and Reserve Sharing Group | **no** |

So requiring a Virginia-standalone model to self-provide full Most Severe Single Contingency
reserve remains conservative **under either construct**, because that obligation is met jointly at
PJM level either way.

---

## Open — further SCC filings likely

Dominion's FRR termination and the surrounding capacity-market questions have generated litigation
and regulatory attention beyond what is captured here: **LS Power filed a FERC complaint** arguing
the original FRR election should be invalidated because Dominion had not filed capacity plans for
all five obligated years; the Attorney General's Division of Consumer Counsel stated it would
*"monitor the impacts of the company's decision in appropriate proceedings before the SCC."*

Relevant case numbers seen: **PUR-2024-00193**, **PUR-2024-00184** (2024 IRP), **PUR-2023-00066**
(2023 IRP).

**Note:** `scc.virginia.gov` **disallows automated access** (robots), so filings cannot be fetched
directly. Content here is from search snippets and secondary sources. Direct retrieval requires a
manual download.

---

## Sources

- SCC 2025 Combined Annual Report — FRR termination date, APCo comparison, capacity price
- SCC filing PUR-2024-00193 — the RPM/FRR election history in Dominion's own words
- Dominion 2025 IRP Update — current RPM participation, PJM capacity shortfall, DOM Zone as net
  importer, price caps masking need
- RTO Insider, 8 July 2024 — FERC allowing planned resources to shift FRR → RPM
- Virginia Mercury, 25 May 2021 — the original FRR election, LS Power complaint, AG monitoring
- Monitoring Analytics (PJM IMM), May 2021 — *Potential Impacts of the Creation of Virginia FRRs*
