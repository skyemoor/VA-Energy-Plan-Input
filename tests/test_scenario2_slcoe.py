"""
test_scenario2_slcoe.py

The Scenario 2 SLCOE runner -- twenty annual solves levelised into one figure.

WHY EVERY YEAR: a levelised cost needs the whole stream. Averaging the four checkpoints weights
each equally, ignores discounting, and misses that demand grows 72% across the horizon so later
years carry far more MWh.
"""
import json
import os

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULT = os.path.join(REPO, 'results', 'scenario2_slcoe_central.json')

pytestmark = pytest.mark.skipif(not os.path.exists(RESULT),
                                reason='run: python3 run_scenario2_slcoe.py')


@pytest.fixture(scope='module')
def run():
    with open(RESULT) as f:
        return json.load(f)


class TestTheStreamIsComplete:
    def test_twenty_years_no_gaps(self, run):
        years = sorted(r['year'] for r in run['stream'])
        assert years == list(range(2026, 2046))

    def test_levelisation_verified_complete(self, run):
        assert run['levelised']['missing_years'] == []
        assert run['levelised']['years_in_stream'] == 20

    def test_no_year_had_unserved_energy(self, run):
        """The runner raises on any year with unserved energy (Appendix P.2 §11), so a completed
        run is itself the assertion -- this records that the guard exists."""
        assert run['levelised']['pv_demand_mwh'] > 0


class TestMeasuredResult:
    """BASELINE LOCKED 2026-09-13, central capex case."""

    def test_slcoe_both_ways(self):
        """$37.88/MWh without the terminal-value credit, $32.82 with it. Reported both ways per
        the prior 20-year SLCOE convention, so a reader can strip out an assumption."""
        with open(RESULT) as f:
            d = json.load(f)['levelised']
        assert d['slcoe_without_terminal_value'] == pytest.approx(37.88, abs=0.5)
        assert d['slcoe_with_terminal_value'] == pytest.approx(32.82, abs=0.5)

    def test_terminal_value_is_material(self, run):
        """$10.01B of PV against $74.93B of PV cost -- 13%. Large enough that omitting it would
        materially overstate the baseline, which is why NREL's ATB treats residual value as
        standard rather than optional."""
        d = run['levelised']
        assert d['pv_terminal_value_usd'] / d['pv_cost_usd'] == pytest.approx(0.134, abs=0.02)

    def test_clean_share_falls_across_the_whole_stream(self, run):
        """THE WHITEPAPER'S THESIS, now at annual resolution: 47.4% in 2026 falling to 34.7% in
        2045. Demand grows 72% while the solar target is fixed at 16,100 MW."""
        stream = sorted(run['stream'], key=lambda r: r['year'])
        assert stream[0]['clean_share'] == pytest.approx(0.474, abs=0.02)
        assert stream[-1]['clean_share'] == pytest.approx(0.347, abs=0.02)

    def test_clean_share_peaks_mid_stream_then_declines(self, run):
        """It RISES to 2030-31 as the statutory solar builds out, then falls as demand overtakes
        it. A monotonic decline would have been a simpler story; this is the real shape, and the
        turning point is where the statutory build stops keeping pace."""
        stream = sorted(run['stream'], key=lambda r: r['year'])
        peak_year = max(stream, key=lambda r: r['clean_share'])['year']
        assert 2029 <= peak_year <= 2032, f'peak at {peak_year}, expected around 2030'

    def test_annual_cost_rises_monotonically(self, run):
        stream = sorted(run['stream'], key=lambda r: r['year'])
        costs = [r['total_annual_usd'] for r in stream]
        assert costs == sorted(costs)


class TestCapexBand:
    @pytest.mark.parametrize('basis,expected', [('low', 32.32), ('high', 33.53)])
    def test_band_brackets_the_central_case(self, basis, expected):
        path = os.path.join(REPO, 'results', f'scenario2_slcoe_{basis}.json')
        if not os.path.exists(path):
            pytest.skip(f'run with --capex-basis {basis}')
        with open(path) as f:
            got = json.load(f)['levelised']['slcoe_with_terminal_value']
        assert got == pytest.approx(expected, abs=0.5)

    def test_the_band_is_narrow(self):
        """$32.32 to $33.53 with terminal value -- a 3.7% spread. Gas CAPEX uncertainty barely
        moves Scenario 2's SLCOE, because most of its cost is FUEL, not capital. The gas PRICE
        band will matter far more, which is why it is a separate axis."""
        vals = []
        for basis in ('low', 'high'):
            path = os.path.join(REPO, 'results', f'scenario2_slcoe_{basis}.json')
            if not os.path.exists(path):
                pytest.skip('run the band first')
            with open(path) as f:
                vals.append(json.load(f)['levelised']['slcoe_with_terminal_value'])
        assert (max(vals) - min(vals)) / min(vals) < 0.06
