"""
compute_tier123_final.py

Tier 1/2/3 social costs for Scenario 1, all 20 years (2026-2045), on
today's fully corrected hourly dispatch (demand basis, SLCR, reserve
margin for the four checkpoints; statutory RPS share, SLCR, corrected
demand shape for the 16 non-checkpoint years -- Internal Debugging Log
#24/#26/#27/#29/#30/#31/#32).

Relabeling, per direct user direction (this session):
  - "Social Cost of Carbon" -- Virginia's own statutory concept (Va. Code
    SS56-585.1(A)(6)/56-598(2)(d)), CO2-only, addressed individually
    because the statute specifically calls it out by name. This
    project's own "Virginia SC-CO2".
  - "Social Cost of Greenhouse Gases" -- CO2 + CH4 + N2O (confirmed
    directly with the user: N2O, not NOx -- easy to mistype, deliberately
    checked before building this). Reported alongside SC-CO2, both
    required, not one or the other.
  - Tier 2 relabeled "Health Impacts" throughout -- no bare "Tier 2" in
    any reader-facing output.
  - Tier 3 (air toxics) stays qualitative only, no dollar figure --
    confirmed no credible monetized basis exists at this project's level
    of sourcing.

Both undiscounted and NPV figures reported (per direct user decision):
researched how state IRPs handle this before building either -- physical
emissions (tons) are reported undiscounted essentially universally
across surveyed IRPs (Indiana Michigan Power, PG&E); once MONETIZED,
practice genuinely diverges (Kansas City Power & Light folds monetized
environmental cost into the same discounted NPV used to rank plans;
Glendale Water & Power explicitly excludes it from its own NPV figure
and reports it separately). No single settled convention found, so both
are reported: the undiscounted total as the primary/headline figure
(the more universal convention), and an NPV figure at SLCOE's own 4.5%
WACC/2026 base year as a secondary figure for direct comparison against
SLCOE's own discounting -- neither presented as the sole correct answer.

CPI re-basing (this session, second direct user question): EPA's own
SC-GHG table is denominated in 2020$, but this project's WACC/SLCOE use
a 2026 base year -- "real 2020$" and "real 2026$" are different
reference points, not interchangeable. Re-based using a BLS-sourced
1.2902 deflator (29.02% cumulative inflation, 2020 annual average to
July 2026) before use -- see EPA_SCGHG_TABLE_2020_DOLLARS/
CPI_DEFLATOR_2020_TO_2026 below for the full sourcing.

Scope confirmed with the user: natural-gas emissions and impacts only
(no diesel) -- verified this was already true of the existing
methodology before this rewrite, not a new restriction: AP-42 factors
are already Section 3.1 (stationary GAS turbines, not diesel/
reciprocating engines), and the BenMAP rates are already the EGU
category. The LP model itself never dispatches diesel either -- there
is no diesel variable anywhere in lp_model.py.

CORRECTED existing/new-build split (this session): the prior version of
this calculation assumed 100% existing-fleet, zero new-build gas
throughout Scenario 1, confirmed true of the OLD (pre-correction)
dispatch. Checked directly against today's new dispatch before reusing
that assumption: today's corrected gas dispatch reaches the FULL
capacity cap (existing fleet + the 2,862 MW overhaul/retain pool) at
every checkpoint, not just the existing-fleet-only bound -- the old
assumption no longer holds. existing_mw/new_mw now use the genuine
split (schedule_b_baseline_mw(year) / 2,862.0) rather than treating all
capacity as existing.
"""
import numpy as np
import driver as drv

# ---- EPA SC-GHG rates (2020$/ton), Table ES.1, 2.0% discount rate ----
EPA_SCGHG_TABLE_2020_DOLLARS = {
    2020: {'CO2': 190, 'CH4': 1600, 'N2O': 54000},
    2030: {'CO2': 230, 'CH4': 2400, 'N2O': 66000},
    2040: {'CO2': 270, 'CH4': 3300, 'N2O': 79000},
    2050: {'CO2': 310, 'CH4': 4200, 'N2O': 93000},
}

# CORRECTED (this session): the table above is EPA's own 2020$, but this project's SLCOE/WACC use a
# 2026 base year -- "real 2020$" and "real 2026$" are NOT the same reference point, and treating them
# as interchangeable would understate every Tier 1 dollar figure by the actual inflation between the
# two years. Direct user question prompted checking this rather than assuming consistency. Deflator
# sourced directly from BLS: 2020 annual average CPI-U = 258.811 (BLS historical CPI-U table,
# https://www.bls.gov/cpi/tables/supplemental-files/historical-cpi-u-202402.pdf); July 2026 CPI-U
# (most recent available, NSA) = 333.918 (BLS CPI Summary, July 2026 release,
# https://www.bls.gov/news.release/cpi.nr0.htm). Ratio = 333.918/258.811 = 1.2902 (29.02% cumulative
# inflation) -- applied to every rate in the table above before use, not left as an unstated gap.
CPI_2020_ANNUAL_AVG = 258.811
CPI_2026_JULY_NSA = 333.918
CPI_DEFLATOR_2020_TO_2026 = CPI_2026_JULY_NSA / CPI_2020_ANNUAL_AVG  # 1.2902

EPA_SCGHG_TABLE = {
    year: {gas: rate * CPI_DEFLATOR_2020_TO_2026 for gas, rate in gases.items()}
    for year, gases in EPA_SCGHG_TABLE_2020_DOLLARS.items()
}

def scghg_rate(year, gas):
    years = sorted(EPA_SCGHG_TABLE.keys())
    for i in range(len(years) - 1):
        y0, y1 = years[i], years[i + 1]
        if y0 <= year <= y1:
            v0, v1 = EPA_SCGHG_TABLE[y0][gas], EPA_SCGHG_TABLE[y1][gas]
            return v0 + (v1 - v0) * (year - y0) / (y1 - y0)
    raise ValueError(f"{year} out of range")

# ---- AP-42 emission factors (lb/MMBtu), Section 3.1 STATIONARY GAS TURBINES (not diesel) ----
EF_CO2 = 110.0
EF_CH4_COMBUSTION = 0.0086
EF_N2O = 0.003
EF_PM = 0.0066
EF_SO2 = 0.0034
EF_NOX_UNCONTROLLED = 0.32
EF_NOX_DLN = 0.099

UPSTREAM_CH4_LEAK_FRAC = 0.023
GAS_ENERGY_CONTENT_MMBTU_PER_MCF = 1.037
CH4_KG_PER_MCF = 19.3

# ---- Health Impacts: EPA EGU benefit-per-ton (2016$/ton, BenMAP) ----
BPT_PM25_2016_DOLLARS = 140000.0
BPT_SO2_2016_DOLLARS = 40000.0
BPT_NOX_2016_DOLLARS = 6000.0

# CORRECTED (this session, same check applied consistently): these BenMAP rates are EPA's own 2016$,
# an even larger gap to this project's 2026 base year than the SC-GHG table's 2020$ (10 years, not 6).
# Caught only because the Health Impacts total did not move after the first CPI fix -- worth checking
# rather than assuming the fix was complete. Same BLS data already sourced above: 2016 annual average
# CPI-U = 240.007 (same BLS historical table); deflator = 333.918/240.007 = 1.3913 (39.13% cumulative).
CPI_2016_ANNUAL_AVG = 240.007
CPI_DEFLATOR_2016_TO_2026 = CPI_2026_JULY_NSA / CPI_2016_ANNUAL_AVG  # 1.3913

BPT_PM25 = BPT_PM25_2016_DOLLARS * CPI_DEFLATOR_2016_TO_2026
BPT_SO2 = BPT_SO2_2016_DOLLARS * CPI_DEFLATOR_2016_TO_2026
BPT_NOX = BPT_NOX_2016_DOLLARS * CPI_DEFLATOR_2016_TO_2026

HEAT_RATE_CCGT = 6.4
HEAT_RATE_CT = 9.5

PLANT_NOX_CLASS = [
    ("Greensville County", 1605, 'DLN', 'confirmed', 2048),
    ("Brunswick County", 1376, 'DLN', 'strong_inference', 2046),
    ("Warren County", 1349, 'DLN', 'strong_inference', 2044),
    ("Bear Garden", 622, 'DLN', 'confirmed', 2041),
    ("Possum Point", 573, 'DLN', 'confirmed', 2045),
    ("Potomac Energy Center", 793, 'DLN', 'strong_inference', 2047),
    ("Tenaska Virginia", 975, 'DLN', 'weak_inference', 2034),
    ("Chesterfield", 386, 'uncontrolled', 'no_evidence_found', 2045),
    ("Doswell CT-half", 450.5, 'uncontrolled', 'no_evidence_found', 2045),
    ("Doswell CCGT-half", 450.5, 'uncontrolled', 'no_evidence_found', 2045),
    ("Ladysmith", 782, 'uncontrolled', 'no_evidence_found', 2045),
    ("Marsh Run", 550, 'uncontrolled', 'no_evidence_found', 2034),
    ("Louisa", 525, 'uncontrolled', 'no_evidence_found', 2033),
    ("Wolf Hills", 285, 'uncontrolled', 'no_evidence_found', 2031),
    ("Remington", 619, 'uncontrolled', 'no_evidence_found', 2030),  # already offline, moot
]

def existing_fleet_nox_blend(year):
    total_mw = 0.0
    weighted_ef = 0.0
    for name, mw, cls, conf, ret_yr in PLANT_NOX_CLASS:
        if ret_yr > year:
            ef = EF_NOX_DLN if cls == 'DLN' else EF_NOX_UNCONTROLLED
            total_mw += mw
            weighted_ef += mw * ef
    return weighted_ef / total_mw if total_mw > 0 else EF_NOX_UNCONTROLLED, total_mw


def baseload_split(g_hourly, pct=0.70):
    g_sorted = np.sort(g_hourly)[::-1]
    idx = min(int(len(g_sorted) * pct), len(g_sorted) - 1)
    baseload_mw = g_sorted[idx]
    ccgt_mwh = np.minimum(g_hourly, baseload_mw).sum()
    ct_mwh = np.maximum(0.0, g_hourly - baseload_mw).sum()
    return ccgt_mwh, ct_mwh, baseload_mw


def compute_year(year, g_hourly, existing_mw, new_mw):
    ccgt_mwh, ct_mwh, baseload_mw = baseload_split(g_hourly)
    mmbtu_ccgt = ccgt_mwh * HEAT_RATE_CCGT
    mmbtu_ct = ct_mwh * HEAT_RATE_CT
    mmbtu_total = mmbtu_ccgt + mmbtu_ct

    total = existing_mw + new_mw
    existing_share = existing_mw / total if total > 0 else 1.0
    new_share = 1.0 - existing_share
    existing_nox_ef, existing_fleet_mw_at_year = existing_fleet_nox_blend(year)

    co2_tons = mmbtu_total * EF_CO2 / 2000.0
    ch4_combustion_tons = mmbtu_total * EF_CH4_COMBUSTION / 2000.0
    mcf_burned = mmbtu_total / GAS_ENERGY_CONTENT_MMBTU_PER_MCF
    mcf_produced = mcf_burned / (1 - UPSTREAM_CH4_LEAK_FRAC)
    ch4_upstream_tons = mcf_produced * UPSTREAM_CH4_LEAK_FRAC * CH4_KG_PER_MCF / 1000.0
    ch4_total_tons = ch4_combustion_tons + ch4_upstream_tons
    n2o_tons = mmbtu_total * EF_N2O / 2000.0

    social_cost_of_carbon = co2_tons * scghg_rate(year, 'CO2')
    social_cost_of_ghg = (social_cost_of_carbon +
                           ch4_total_tons * scghg_rate(year, 'CH4') +
                           n2o_tons * scghg_rate(year, 'N2O'))

    pm_tons = mmbtu_total * EF_PM / 2000.0
    so2_tons = mmbtu_total * EF_SO2 / 2000.0
    nox_ef_blended = existing_share * existing_nox_ef + new_share * EF_NOX_DLN
    nox_tons = mmbtu_total * nox_ef_blended / 2000.0
    health_impacts_cost = pm_tons * BPT_PM25 + so2_tons * BPT_SO2 + nox_tons * BPT_NOX

    return dict(year=year, gas_mwh=g_hourly.sum(), ccgt_mwh=ccgt_mwh, ct_mwh=ct_mwh,
                mmbtu_total=mmbtu_total, co2_tons=co2_tons, ch4_total_tons=ch4_total_tons,
                n2o_tons=n2o_tons, pm_tons=pm_tons, so2_tons=so2_tons, nox_tons=nox_tons,
                existing_share=existing_share, new_share=new_share, existing_nox_ef=existing_nox_ef,
                social_cost_of_carbon=social_cost_of_carbon, social_cost_of_ghg=social_cost_of_ghg,
                health_impacts_cost=health_impacts_cost)


CHECKPOINT_FILES = {
    2030: '/tmp/hourly_2030_WITH_RESERVE_MARGIN_final.npz',
    2035: '/tmp/hourly_2035_WITH_RESERVE_MARGIN_final.npz',
    2040: '/tmp/hourly_2040_WITH_RESERVE_MARGIN_final.npz',
    2045: '/tmp/hourly_2045_WITH_RESERVE_MARGIN_final.npz',
}
NON_CHECKPOINT_FILES = {y: f'/tmp/hourly_{y}_CORRECTED_final.npz'
                          for y in [2026, 2027, 2028, 2029, 2031, 2032, 2033, 2034,
                                    2036, 2037, 2038, 2039, 2041, 2042, 2043, 2044]}
ALL_YEARS = sorted(list(CHECKPOINT_FILES.keys()) + list(NON_CHECKPOINT_FILES.keys()))

# Same WACC/base-year convention as compute_final_slcoe_20yr.py, for direct side-by-side
# comparability against SLCOE's own discounted figure.
WACC = 0.045
BASE_YEAR = 2026

if __name__ == '__main__':
    print("=" * 78)
    print("TIER 1/2/3 SOCIAL COSTS -- SCENARIO 1, ALL 20 YEARS (2026-2045)")
    print("Corrected demand + SLCR + reserve margin (checkpoints) / statutory RPS")
    print("share + SLCR (non-checkpoint years). Natural gas emissions only.")
    print("=" * 78)

    results = {}
    for y in ALL_YEARS:
        path = CHECKPOINT_FILES.get(y) or NON_CHECKPOINT_FILES[y]
        g = np.load(path)['g']
        existing_mw = drv.schedule_b_baseline_mw(y)
        new_mw = 2862.0
        r = compute_year(y, g, existing_mw, new_mw)
        results[y] = r
        print(f"{y}: gas={g.sum()/1000:8.1f} GWh  "
              f"SC-CO2=${r['social_cost_of_carbon']/1e6:7.2f}M  "
              f"SC-GHG=${r['social_cost_of_ghg']/1e6:7.2f}M  "
              f"Health=${r['health_impacts_cost']/1e6:6.2f}M  "
              f"existing_share={r['existing_share']:.3f}")

    total_sc_co2 = sum(results[y]['social_cost_of_carbon'] for y in ALL_YEARS)
    total_sc_ghg = sum(results[y]['social_cost_of_ghg'] for y in ALL_YEARS)
    total_health = sum(results[y]['health_impacts_cost'] for y in ALL_YEARS)

    # NPV version -- same WACC/base-year as SLCOE, for direct comparability. Per this project's
    # own research (this session): physical emissions (tons) are universally reported undiscounted
    # across surveyed state IRPs; once MONETIZED, practice genuinely diverges -- some IRPs (e.g.
    # Kansas City Power & Light, Missouri) fold monetized environmental cost directly into the same
    # discounted NPV used to rank plans, others (e.g. Glendale Water & Power) explicitly exclude it
    # from their own NPV figure and report it separately. No single settled convention found -- per
    # direct user decision, both the undiscounted total (the more universal convention, and the
    # primary/headline figure) and this NPV version (for direct comparison against SLCOE's own
    # discounting) are reported side by side, neither presented as the sole "correct" figure.
    pv_sc_co2 = 0.0
    pv_sc_ghg = 0.0
    pv_health = 0.0
    for y in ALL_YEARS:
        df = 1.0 / (1 + WACC) ** (y - BASE_YEAR)
        pv_sc_co2 += results[y]['social_cost_of_carbon'] * df
        pv_sc_ghg += results[y]['social_cost_of_ghg'] * df
        pv_health += results[y]['health_impacts_cost'] * df

    print()
    print(f"20-YEAR UNDISCOUNTED TOTALS, 2026$ (primary/headline figure -- the universal convention")
    print(f"across surveyed state IRPs for physical/monetized emissions alike; EPA's own 2020$ SC-GHG")
    print(f"table and 2016$ BenMAP rates both re-based to 2026$ via BLS-sourced deflators):")
    print(f"  Social Cost of Carbon (CO2 only):              ${total_sc_co2/1e9:.3f}B")
    print(f"  Social Cost of Greenhouse Gases (CO2+CH4+N2O): ${total_sc_ghg/1e9:.3f}B")
    print(f"  Health Impacts (PM2.5+SO2+NOx):                ${total_health/1e9:.3f}B")
    print()
    print(f"20-YEAR NPV, {WACC*100:.1f}% WACC, {BASE_YEAR}$ (secondary figure -- for direct comparison")
    print(f"against SLCOE's own discounting; NOT the primary/headline figure):")
    print(f"  Social Cost of Carbon (CO2 only):              ${pv_sc_co2/1e9:.3f}B")
    print(f"  Social Cost of Greenhouse Gases (CO2+CH4+N2O): ${pv_sc_ghg/1e9:.3f}B")
    print(f"  Health Impacts (PM2.5+SO2+NOx):                ${pv_health/1e9:.3f}B")
    print()
    print("Tier 3 (air toxics): qualitative only -- no credible monetized basis")
    print("found at this project's level of sourcing. Not included above.")

    np.savez('/tmp/tier123_final_20yr.npz',
              years=np.array(ALL_YEARS),
              social_cost_of_carbon=np.array([results[y]['social_cost_of_carbon'] for y in ALL_YEARS]),
              social_cost_of_ghg=np.array([results[y]['social_cost_of_ghg'] for y in ALL_YEARS]),
              health_impacts_cost=np.array([results[y]['health_impacts_cost'] for y in ALL_YEARS]),
              total_sc_co2_undiscounted=total_sc_co2, total_sc_ghg_undiscounted=total_sc_ghg,
              total_health_undiscounted=total_health,
              pv_sc_co2=pv_sc_co2, pv_sc_ghg=pv_sc_ghg, pv_health=pv_health,
              wacc=WACC, base_year=BASE_YEAR)
    print("\nSaved to /tmp/tier123_final_20yr.npz")
