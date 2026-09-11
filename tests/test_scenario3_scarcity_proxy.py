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
