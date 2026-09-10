# Project Acronym List

*Comprehensive reference across this project's own documentation
(appendices, Scenario 3 scope/notes, debugging log, tracker). Organized
by category, alphabetical within category. Flagged: any acronym reused
for two different things within this project (a real, easy-to-miss
confusion risk), and any expansion inferred rather than explicitly
confirmed in this project's own sources.*

## ⚠ Resolved this session — reused-acronym collisions closed, kept here for history

• **SCC** — settled, by direct instruction, as **State Corporation
  Commission** only, throughout this project. Previously also used for
  "Virginia SCC" (the statutory social-cost-of-carbon concept) — that
  usage has been renamed to **Virginia SC-CO2** (see Social Cost /
  Emissions category below) specifically to keep the Commission's own
  acronym unambiguous, given this project's readership includes SCC
  staff directly. Researched against the full priority chain (Virginia
  Code → SCC's own usage → VA Dept. of Energy → EPA) before renaming:
  Virginia Code itself never abbreviates the concept at all (spells out
  "the social cost of carbon" in full at every statutory use); the
  Commission's own filings and the broader legal/economic literature
  default to the same "SCC" now reserved; VA DOE has no distinct
  acronym of its own. Landed on the EPA's own current (2021-onward)
  terminology, which already distinguishes the single- and multi-gas
  versions by name.
• **DA** — no longer used in this project for DER Aggregator. Renamed
  throughout to **DERA**, the confirmed, widely-used industry-standard
  acronym (used directly by ISO New England's own official training
  materials and the FERC 2222 implementation tracker) — resolves the
  collision with the market sense of "DA" (day-ahead) entirely, rather
  than relying on context to disambiguate. Per direct instruction, "DA"
  itself is retained only for day-ahead, and only when paired with
  real-time as "DA/RT" — not used standalone.

## Still worth watching — no project-specific renaming needed

• **RRS** — within this project, always PJM's **Reserve Requirement
  Study** (verified directly against PJM's own source material this
  session — not "Reliability Requirement Study," an earlier,
  unconfirmed guess corrected before use).

## Statutory / Regulatory Bodies

• **DEQ** — (Virginia) Department of Environmental Quality
• **DOE** — (U.S.) Department of Energy
• **EPA** — (U.S.) Environmental Protection Agency
• **FERC** — Federal Energy Regulatory Commission
• **HB / SB** — House Bill / Senate Bill (Virginia General Assembly)
• **IWG** — Interagency Working Group (on the Social Cost of Greenhouse
  Gases — the source of the 2016 guidance Virginia SC-CO2 is
  statutorily tied to, per Appendix P #9)
• **NERC** — North American Electric Reliability Corporation
• **RGGI** — Regional Greenhouse Gas Initiative
• **SCC** — State Corporation Commission (Virginia) — see reused-acronym
  note above

## Market / Grid Structure (PJM)

• **BRA** — Base Residual Auction (PJM's capacity market auction)
• **DOM Zone** — Dominion Zone (PJM's transmission zone corresponding to
  Dominion's own service territory)
• **EFORd** — Equivalent Forced Outage Rate demand (a PJM/NERC
  generator-reliability metric)
• **IMM** — Independent Market Monitor (PJM's, operated by Monitoring
  Analytics)
• **IRM** — Installed Reserve Margin
• **ISO** — Independent System Operator
• **LMP** — Locational Marginal Price
• **LOLE** — Loss-of-Load Expectation (days/year)
• **LOLH** — Loss-of-Load Hours (hours/year)
• **LOLP** — Loss-of-Load Probability
• **EUE** — Expected Unserved Energy (MWh/year)
• **PJM** — PJM Interconnection (the Mid-Atlantic regional transmission
  organization this project's own grid territory sits within; no longer
  officially expanded by PJM itself, retained here as a proper name)
• **RTO** — Regional Transmission Organization
• **UCAP** — Unforced Capacity

## Resource Adequacy / Capacity Accreditation

• **ELCC** — Effective Load Carrying Capability
• **ELCCSTF** — ELCC Senior Task Force (the PJM stakeholder body the
  IMM's own recommendations were filed to — Appendix A.22)
• **FPR** — Forecast Pool Requirement
• **RRS** — Reserve Requirement Study — see reused-acronym note above
• **THI** — Temperature Humidity Index (used in PJM's own ELCC/RRS
  weather-scrambling methodology, Appendix A.22)

## DER / Distributed Energy and Market Participation

• **ARB** — Accelerated Renewable Energy Buyer (Virginia-specific
  status, exempting certain large customers from portions of RPS-related
  charges)
• **BTM** — Behind-the-Meter
• **BYOD** — Bring Your Own Device (Dominion's own device-agnostic
  aggregator-access program within its VPP Pilot filing — Appendix C
  program #5; see Dominion_VPP_Pilot_Research.md)
• **DER** — Distributed Energy Resource
• **DERA** — DER Aggregator (confirmed, industry-standard acronym —
  see resolved-collision note above; supersedes this project's earlier,
  now-retired use of "DA" for this concept)
• **VPP** — Virtual Power Plant

## Renewable Energy Certificates / Compliance

• **D-REC** — Distributed Renewable Energy Certificate (a
  distributed-generation-specific REC pricing/compliance mechanism
  referenced in Appendix E's DER compensation proposal)
• **GATS** — Generation Attribute Tracking System (PJM-EIS's own REC
  registry/trading platform)
• **REC** — Renewable Energy Certificate
• **SACP** — Solar Alternative Compliance Payment (Virginia's
  deficiency-payment penalty for RPS solar-carve-out shortfalls)
• **SREC** — Solar Renewable Energy Certificate

## Contracts and Ownership

• **CFD** — Contract for Differences (the financial-settlement mechanism
  underlying a virtual PPA)
• **PPA** — Power Purchase Agreement
• **VPPA** — Virtual Power Purchase Agreement (a PPA structured as a
  CFD, typically used by non-utility/corporate offtakers — distinct from
  the physical PPAs this project's own Rider PPA/B.1.b tier uses)

## Demand-Side Management / Demand Response

• **ADR** — Automated Demand Response
• **BEMS** — Building Energy Management System
• **CPP** — Critical Peak Pricing
• **DLC** — Direct Load Control
• **DR** — Demand Response
• **DSM** — Demand-Side Management
• **EE** — Energy Efficiency
• **GEB** — Grid-interactive Efficient Buildings (DOE's own framework,
  source for this project's "automated EE/DR hybrid" taxonomy category)
• **HEMS** — Home Energy Management System
• **PEMD** — Price Elasticity Matrix of Demand (a customer-class-
  disaggregated elasticity modeling approach referenced in this
  session's price-elasticity research)
• **RTP** — Real-Time Pricing
• **TOU** — Time-of-Use

## LP / Optimization / Technical Modeling

• **DoD** — Depth of Discharge
• **KKT** — Karush-Kuhn-Tucker (optimality conditions, used this session
  to verify true LP degeneracy vs. a solver bug)
• **LP** — Linear Program / Linear Programming
• **MILP** — Mixed-Integer Linear Program / Linear Programming
• **RBD** — *(expansion inferred, not explicitly confirmed in the source
  paper's own text)* likely "Realizable Battery Dispatch," from Nazir &
  Almassalkhi (2021)'s paper title, "Guaranteeing a Physically Realizable
  Battery Dispatch Without Charge-Discharge Complementarity Constraints"
  — the informal name this project's own debugging log uses for that
  paper's proposed method (Internal Debugging Log #20.5-20.6)
• **RTE** — Round-Trip Efficiency
• **SCD** — Simultaneous Charging and Discharging (the named literature
  problem this project's own storage-dispatch-degeneracy work, Appendix
  P #13, is an instance of)
• **SLCR** — Storage Loss Coverage by Renewables (Kittel & Schill 2022's
  RPS-constraint reformulation, trialed and found not applicable at this
  project's own high-RPS checkpoints — Internal Debugging Log #20.7)
• **SoC** — State of Charge
• **USC** — Unintended Storage Cycling (the phenomenon SLCR is designed
  to close)

## Cost / Economics

• **CAPEX** — Capital Expenditure
• **CRF** — Capital Recovery Factor
• **FOM** — Fixed Operations and Maintenance (cost)
• **LCOE** — Levelized Cost of Energy
• **NPV** — Net Present Value
• **O&M** — Operations and Maintenance
• **SLCOE** — System Levelized Cost of Energy (this project's own
  primary summary cost metric)
• **WACC** — Weighted Average Cost of Capital

## Social Cost / Emissions

• **BPT** — Benefit Per Ton (EPA's own standard metric/acronym for
  Tier 2 health-effects monetization — PM2.5/SO2/NOx benefit-per-ton
  values for the electric generating sector, confirmed directly from
  EPA's own published tables this session)
• **GHG** — Greenhouse Gas
• **NOx** — Nitrogen Oxides
• **PM / PM2.5** — Particulate Matter (fine particulate, ≤2.5 microns)
• **SC-CO2** — Social Cost of Carbon Dioxide (EPA/IWG's own current,
  2021-onward official acronym for the carbon-only concept — adopted
  this session as "Virginia SC-CO2" for Virginia's own statutory
  concept, specifically to avoid colliding with "SCC" = State
  Corporation Commission; see resolved-collision note above)
• **SC-GHG** — Social Cost of Greenhouse Gases (EPA/IWG's own official
  acronym for the combined multi-gas concept — CO2 + CH4 + N2O; scope-
  equivalent to this project's own "aggregate GHG cost"/"Tier 1")
• **SCoC** — Social Cost of Carbon (the generic economic term used
  elsewhere in the general literature — distinct from, though related
  to, the EPA's own more specific SC-CO2/SC-GHG usage above; this
  project uses SCoC for the general concept and SC-CO2/SC-GHG for
  Virginia's own statutory and this project's own Tier 1 figures
  specifically)
• **SO2** — Sulfur Dioxide

## Generation Technology

• **CCGT** — Combined-Cycle Gas Turbine
• **CT** — Combustion Turbine (simple-cycle)
• **CF** — Capacity Factor
• **CVOW** — Coastal Virginia Offshore Wind (this project's own offshore
  wind resource)
• **DLN** — Dry Low-NOx (a combustion technology reducing NOx emissions,
  used in this project's plant-specific NOx classification)

## Building / Efficiency

• **HVAC** — Heating, Ventilation, and Air Conditioning
• **PHIUS** — Passive House Institute US (the building-efficiency
  standard referenced in Scenario 3's own DSM scope, Category A.3)
• **SEER** — Seasonal Energy Efficiency Ratio

## Statutes and Named Legislation

• **RPS** — Renewable Portfolio Standard (Va. Code #56-585.5)
• **VCEA** — Virginia Clean Economy Act (2020) — the enabling statute;
  not a synonym for any single one of Dominion's own compliance riders
  (Rider CE, Rider PPA, Rider RPS all separately implement VCEA
  compliance — see Scenario3_Scope_and_Gaps.md #5.2)

## Units

• **GWh** — Gigawatt-hour
• **kW / kWh** — Kilowatt / Kilowatt-hour
• **MMBtu** — Million British Thermal Units
• **MW / MWh** — Megawatt / Megawatt-hour

## This Project's Own Scenario/Structural Shorthand (not industry-standard acronyms, included for completeness)

• **S1 / S1B / S2 / S3 / S3B** — Scenario 1 / 1B / 2 / 3 / 3B, this
  project's own scenario labels
• **IRP** — Integrated Resource Plan (Dominion's own statutory planning
  filing, distinct from this project's own analysis)
