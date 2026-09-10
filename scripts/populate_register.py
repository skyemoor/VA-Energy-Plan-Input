"""Seeds the provenance register with figures established or revised in the 2026-09 sessions."""
from provenance import AssumptionRecord, ResultRecord, ProvenanceRegister

register = ProvenanceRegister()

for a in [
    AssumptionRecord('A-PWC-PARKING-V2', 'PWC parking-lot solar, re-anchored to C&I building '
        'footprint (population anchor imported Loudoun data-center distortion)', 335.6, 'MW'),
    AssumptionRecord('A-SITING-CAP-DOM', 'Distributed solar siting cap, DOM zone, extrapolated '
        'from re-based four-county NoVA at 0.93 kW/capita excluding Loudoun', 7440.0, 'MW'),
    AssumptionRecord('A-DIST-STORAGE-PAIR', 'Distributed storage pairing: 1:1 MW with distributed '
        'solar, 4-hour duration', 4.0, 'hours'),
    AssumptionRecord('A-FE-DURATION', 'Iron-air duration (power = energy/100)', 100.0, 'hours',
                     citation_key='C122'),
    AssumptionRecord('A-FE-CAPEX', 'Iron-air energy capex', 18.03, '$/kWh'),
    AssumptionRecord('A-NA-CAPEX-ENERGY', 'Sodium-ion energy capex', 65.16, '$/kWh'),
    AssumptionRecord('A-DEMAND-2045', 'DOM zone 2045 annual demand, April-March fiscal year',
                     206.3, 'TWh'),
    AssumptionRecord('A-STORAGE-MANDATE-2045', 'Dominion storage mandate under HB895/SB448: '
        '16,000 MW short-duration + 3,480 MW LDES by 2045', 19480.0, 'MW'),
]:
    register.add_assumption(a)

for r in [
    ResultRecord('R-NOVA-TOTAL-V1', 'Four-county NoVA distributed solar potential (original)',
        6159.0, 'MW', status='superseded', superseded_by='R-NOVA-TOTAL-V2',
        notes='PWC parking population-anchored; inflated by Loudoun data-center density'),
    ResultRecord('R-NOVA-TOTAL-V2', 'Four-county NoVA distributed solar potential, PWC re-based',
        4638.6, 'MW', status='current', depends_on_assumption_ids=['A-PWC-PARKING-V2']),
    ResultRecord('R-FIRMING-PCT', 'Six-day lookahead firming percentage, NoVA fleet',
        4.3, 'percent', status='superseded', superseded_by='TBD',
        depends_on_assumption_ids=['R-NOVA-TOTAL-V1'],
        notes='STALE: computed on the 6,159 MW fleet basis, now revised to 4,638.6 MW. '
              'Needs recomputation.'),
    ResultRecord('R-SLCOE-S1-2030', 'Scenario 1 SLCOE 2030, Python pipeline with reserve margin',
        42.45, '$/MWh', scenario='S1', year=2030, status='current'),
    ResultRecord('R-BUILD-2045-SOLAR', 'Total solar, 2045 checkpoint (166,340.7 utility + 7,440 distributed)',
        173780.7, 'MW', scenario='S1', year=2045, status='provisional',
        generating_script='solve_2045_v3.py',
        depends_on_assumption_ids=['A-SITING-CAP-DOM', 'A-DEMAND-2045'],
        notes='Single design weather year 2016-17; distributed solar pinned at siting cap'),
    ResultRecord('R-BUILD-2045-FE-LP', 'Iron-air energy, 2045 LP solve',
        3635866.8, 'MWh', scenario='S1', year=2045, status='superseded',
        superseded_by='R-BUILD-2045-FE-UPLIFT',
        depends_on_assumption_ids=['A-FE-DURATION', 'A-FE-CAPEX'],
        notes='Failed 8-year cross-test in design year 2016-17 (470,502 MWh unserved)'),
    ResultRecord('R-BUILD-2045-FE-UPLIFT', 'Iron-air energy, 2045, +20% uplift after 8-year cross-test',
        4363040.2, 'MWh', scenario='S1', year=2045, status='provisional',
        generating_script='sim_2045_uplift.py',
        depends_on_assumption_ids=['A-FE-DURATION', 'A-FE-CAPEX'],
        notes='Manual sweep, not optimization -- cheapest technology to close the gap was never '
              'tested. Sized partly against heuristic-dispatch shortfall, not purely physical.'),
    ResultRecord('R-SLCOE-S1-2045', 'Scenario 1 SLCOE 2045 at +20% iron-air uplift',
        133.5, '$/MWh', scenario='S1', year=2045, status='provisional',
        depends_on_assumption_ids=['R-BUILD-2045-SOLAR', 'R-BUILD-2045-FE-UPLIFT'],
        notes='No technology cost-decline curve applied; likely conservative'),
    ResultRecord('R-UNSERVED-2030-8YR', '8-year continuous dispatch unserved energy, 2030 build',
        6444435.4, 'MWh', scenario='S1', year=2030, status='current',
        generating_script='simulate_8yr_dispatch.py',
        notes='Storage charge-starved: already captures 75.4% of all available surplus'),
    ResultRecord('R-DOMINION-IRP-NPV', 'Dominion 2025 IRP Company Preferred Plan, Total Plan NPV',
        148.7, '$B', year=2045, status='current',
        notes='Case PUR-2025-00184, 2026-2045, 6.62% discount rate. Includes only 2,000 MW '
              'storage -- predates HB895/SB448 requiring 19,480 MW.',
        depends_on_assumption_ids=['A-STORAGE-MANDATE-2045']),
]:
    register.add_result(r)

register.write_json('provenance_register.json')
print(f"Results: {len(register.results_by_id)}  Assumptions: {len(register.assumptions_by_id)}")
print("\nCurrent results:")
for r in register.current_results():
    print(f"  {r.record_id:<26} {r.value:>12,.1f} {r.units or ''}")
print("\nStaleness check -- results invalidated by A-PWC-PARKING-V2:")
print(f"  {register.find_results_invalidated_by('A-PWC-PARKING-V2')}")
print("\nStaleness check -- results depending on the storage mandate:")
print(f"  {register.find_results_invalidated_by('A-STORAGE-MANDATE-2045')}")
