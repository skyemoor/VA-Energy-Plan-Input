"""
test_scenario3_scarcity_proxy.py

Locks the 2026-09-11 finding that six_day_scarcity_value_proxy() does not behave as its docstring
describes: it produces a near-constant offset rather than a scarcity signal.

These tests assert the DEFECT, not the ideal. If the function is later corrected to include a
capacity reference, they fail -- which is the intent: the Scenario 3 interpretation notes would
then need revisiting, and a silent fix should not leave those notes stale.
"""
import numpy as np
import pytest

import lp_model as lp
import paths
import scenario3_build as s3b


@pytest.fixture(scope='module')
def scarcity():
    import os
    p = paths.intermediate('demand_2045fy_va_only.npy')
    if not os.path.exists(p):
        pytest.skip('demand intermediate not built; run run_all.py --only demand')
    w = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
    dist_cf = np.load(paths.weather_year('dist_solar_cf_8yr_chained_REAL.npy'))[:8760]
    demand = np.load(p)
    exist = lp.exist_solar_mw(2045) * w['solar']
    return s3b.six_day_scarcity_value_proxy(
        demand, exist, dist_cf, w['wind'], w['nuclear'], lp.CVOW_MW)


class TestScarcityProxyIsNearlyConstant:

    def test_it_never_approaches_zero(self, scarcity):
        """The docstring promises 'near-zero when the upcoming week looks comfortable'. The
        measured minimum is 84% of the mean."""
        assert scarcity.min() / scarcity.mean() > 0.8

    def test_coefficient_of_variation_is_tiny(self, scarcity):
        """~4%. A scarcity signal should vary by orders of magnitude across a year."""
        assert scarcity.std() / scarcity.mean() < 0.10

    def test_no_hour_falls_below_half_the_mean(self, scarcity):
        assert (scarcity < scarcity.mean() * 0.5).sum() == 0

    def test_the_defect_is_documented_at_source(self):
        """So anyone reading the function sees it before using the output."""
        src = open(s3b.__file__).read()
        assert 'DOES NOT BEHAVE AS THE DOCSTRING ABOVE DESCRIBES' in src
        assert 'NO CAPACITY REFERENCE TERM' in src

    def test_consequence_for_scenario3_is_recorded(self):
        """The time-varying content of the price series comes entirely from congestion and loss.
        A Scenario 3 result must not be described as incorporating a six-day-lookahead scarcity
        signal -- it incorporates a constant."""
        src = open(s3b.__file__).read()
        assert 'It incorporates a constant.' in src


class TestForesightAsymmetryIsRecorded:
    """The most consequential consequence of the flat scarcity term: within one model, utility
    storage dispatches with perfect foresight while distributed storage responds to a price signal
    carrying no lookahead content. That biases the very comparison Scenario 3 exists to make."""

    def test_the_asymmetry_is_documented(self):
        src = open(s3b.__file__).read()
        assert 'PERFECT lookahead, knows the year' in src
        assert 'effectively NO lookahead' in src
        assert 'compete while blindfolded' in src

    def test_it_points_at_the_measured_foresight_finding(self):
        """100.0% from LP dispatch against 31.8% no-foresight on the same fleet -- already
        established in capacity_accreditation.py, and the same mechanism."""
        src = open(s3b.__file__).read()
        assert '100.0% against 31.8%' in src
        assert 'capacity_accreditation' in src

    def test_rebound_effect_is_recorded_as_a_coordination_failure(self):
        """Short lookahead does not merely forgo value -- it manufactures the scarcity it failed
        to anticipate."""
        src = open(s3b.__file__).read()
        assert 'manufactures the scarcity it failed' in src
        assert 'self-correcting over time' in src

    def test_multi_day_rationing_is_named_as_the_missing_behaviour(self):
        """A correct signal switches the operating mode from 'cycle daily' to 'ration across
        days'. The proxy produces none of that behaviour, not a weakened version."""
        src = open(s3b.__file__).read()
        assert 'RATION ACROSS DAYS' in src
        assert 'not merely a weakened version' in src


class TestExogenousPriceIsAnAdderNotTheFullPrice:
    """Corrects a 2026-09-11 misreading. Distributed storage appears in the LP's own energy
    balance, so it receives system marginal value implicitly; the exogenous series is the
    locational adder on top. Adding full LMP would double-count the energy component."""

    def test_the_correction_is_documented(self):
        src = open(s3b.__file__).read()
        assert 'ADDER, NOT THE WHOLE ARBITRAGE PRICE' in src
        assert 'would DOUBLE-COUNT the energy component' in src

    def test_distributed_storage_is_in_the_lp_energy_balance(self):
        """The structural fact the correction rests on -- verified against the source rather than
        asserted, since the original error came from not checking."""
        src = open(__import__('lp_model').__file__).read()
        i = src.index("eq_cols += [DISTRIBUTED_SOLAR_MW")
        block = src[i:i + 400]
        for v in ('dist_na_discharge_mw', 'dist_na_charge_mw',
                  'dist_fe_discharge_mw', 'dist_fe_charge_mw'):
            assert v in block, f'{v} missing from the energy balance block'

    def test_what_remains_true_is_still_recorded(self):
        """The correction does not clear the locational adder: month-hour averaging still removes
        94.5% of the real extreme and the top 1% of hours holding 29.4% of congestion value.

        Matches against wrap-normalised source. An earlier version asserted contiguous phrases and
        failed on a comment line break -- the third time that pattern bit today, so these checks
        normalise rather than assume formatting."""
        import re
        src = re.sub(r'\s*\n#?\s+', ' ', open(s3b.__file__).read())
        assert '94.5% of the real extreme' in src
        assert '29.4% of all positive congestion value' in src
