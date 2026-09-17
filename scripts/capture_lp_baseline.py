"""
capture_lp_baseline.py

Captures or checks LP fingerprints for a representative call of each scenario builder.

    python3 scripts/capture_lp_baseline.py --capture   # before a refactor
    python3 scripts/capture_lp_baseline.py             # after, to compare

See lp_package/lp_invariance.py for why this exists and what it does not catch.
"""
import argparse
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(REPO, 'lp_package'))

import assumptions                                       # noqa: E402
import demand_basis                                      # noqa: E402
import distributed_solar_profile as dsp                   # noqa: E402
import driver                                            # noqa: E402
import gas_merit_order                                   # noqa: E402
import lp_invariance                                     # noqa: E402
import lp_model as lp                                    # noqa: E402
import paths                                             # noqa: E402

BASELINE = os.path.join(REPO, 'results', 'lp_fingerprints.json')
YEAR = 2045


def _inputs():
    weather = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    demand = demand_basis.VirginiaOnlyGeneration(YEAR).hourly_mw()
    driver.set_year_capex(YEAR)
    return weather, demand, lp.exist_solar_mw(YEAR) * weather['solar']


def build_all():
    """One representative problem per builder configuration currently in use."""
    weather, demand, exist_solar = _inputs()
    common = (weather['solar'], weather['wind'], weather['nuclear'], exist_solar, demand)
    gas_price = lp.gas_price_mwh(YEAR, 'deloitte')
    problems = {}

    # Scenario 1 / 1B shape: build variables, no distributed segment.
    problems['build_problem_plain'] = lp.build_problem(
        *common, gas_price, verbose=False)

    # Scenario 3 shape: the co-optimised distributed segment.
    problems['build_problem_distributed'] = lp.build_problem(
        *common, gas_price, verbose=False,
        enable_distributed_segment=True, distributed_solar_cf=weather['solar'],
        # A flat price is enough to fingerprint the SHAPE of the distributed segment; the real
        # series is an exogenous hourly input and its values do not change which rows exist.
        distributed_exogenous_price_mwh=np.full(len(demand), 40.0))

    # With the merit-order stack, which every scenario now uses.
    problems['build_problem_merit_order'] = lp.build_problem(
        *common, gas_price, verbose=False,
        gas_merit_order=gas_merit_order.GasMeritOrder(), gas_merit_order_year=YEAR)

    # Scenario 2: its own builder, pinned build, carve-out, merit order.
    problems['build_scenario2_problem'] = lp.build_scenario2_problem(
        *common, vcea_solar_mw=4583.0, ccgt_mw=16800.0,
        na_power_mw=16000.0, na_duration_hr=4.0, fe_power_mw=4000.0, fe_duration_hr=100.0,
        gas_price_mwh=gas_price, ccgt_vom_mwh=assumptions.CCGT_VOM_MWH, verbose=False,
        gas_merit_order=gas_merit_order.GasMeritOrder(), gas_merit_order_year=YEAR,
        dist_solar_mw=6862.0, dist_solar_cf=dsp.hydro_year_profile(2016))
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[2])
    parser.add_argument('--capture', action='store_true',
                        help='write the baseline instead of comparing against it')
    args = parser.parse_args()

    problems = build_all()
    if args.capture:
        baseline = lp_invariance.capture_baseline(problems, BASELINE)
        print(f'  captured {len(baseline)} fingerprints -> {BASELINE}')
        for name, entry in sorted(baseline.items()):
            shape = entry['shape']
            print(f"    {name:<32}{shape['variables']:>9,} vars"
                  f"{shape['equality_rows']:>9,} eq{shape['inequality_rows']:>9,} ub")
        return

    differences = lp_invariance.compare_to_baseline(problems, BASELINE)
    if not differences:
        print(f'  {len(problems)} problems IDENTICAL to baseline')
        return
    print(f'  {len(differences)} DIFFERENCE(S) from baseline:')
    for difference in differences:
        print(f'    {difference}')
    sys.exit(1)


if __name__ == '__main__':
    main()
