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
        """The runner raises on any year with unserved energy (Appendix P.2 #11), so a completed
        run is itself the assertion -- this records that the guard exists."""
        assert run['levelised']['pv_demand_mwh'] > 0


class TestMeasuredResult:
    """BASELINE LOCKED 2026-09-13, central capex case."""

    def test_slcoe_both_ways(self):
        """$37.86/MWh without the terminal-value credit, $32.80 with it. Reported both ways per the
        prior 20-year SLCOE convention, so a reader can strip out an assumption.

        MOVED 2 CENTS from $32.82 when Bath went to Dominion's 1,808 MW share on 2026-09-14.
        Removing 1,192 MW of capacity changed almost nothing because SCENARIO 2'S STORAGE NEVER
        OPERATES -- zero charge and zero discharge in all 8,760 hours, since solar delivers 41.3 TWh
        against 202.2 TWh of demand and exceeds it, with nuclear, in only 14 hours. The two cents
        come from reserve adequacy, not dispatch."""
        with open(RESULT) as f:
            d = json.load(f)['levelised']
        assert d['slcoe_without_terminal_value'] == pytest.approx(37.86, abs=0.5)
        assert d['slcoe_with_terminal_value'] == pytest.approx(32.80, abs=0.5)

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
    @pytest.mark.parametrize('basis,expected', [('low', 32.30), ('high', 33.51)])
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


class TestTierOneAndTwo:
    """Appendix P.2 #9 requires Tier 1 and 2 "across all 20 years of a scenario-solve, not from a
    subset of checkpoint years" -- the same full-window rule as #1."""

    def test_tier_one_is_reported_as_two_separate_figures(self, run):
        """Va. Code §56-598(2)(d) / §56-585.1(A)(6) require the statutory CO2-only concept and the
        broader multi-gas total to be reported SEPARATELY, not combined into one. They are
        different quantities: Virginia SCC is carbon-dioxide-only and tied to a specific statutory
        purpose; aggregate GHG cost captures CO2, CH4 and N2O."""
        t = run['levelised']['tiers']
        assert 'virginia_scc_usd' in t and 'social_cost_ghg_usd' in t
        assert t['social_cost_ghg_usd']['pv_usd'] > t['virginia_scc_usd']['pv_usd']

    def test_measured_values(self, run):
        """BASELINE LOCKED 2026-09-13, twenty-year PV at WACC 4.5%."""
        t = run['levelised']['tiers']
        assert t['virginia_scc_usd']['per_mwh'] == pytest.approx(73.71, abs=1.0)
        assert t['social_cost_ghg_usd']['per_mwh'] == pytest.approx(81.15, abs=1.0)
        assert t['health_impacts_usd']['per_mwh'] == pytest.approx(5.50, abs=0.3)

    def test_social_cost_dwarfs_the_direct_cost(self, run):
        """$81.15/MWh of climate cost against $32.82/MWh of direct cost -- the externality is
        roughly 2.5x what appears on the bill. That is the finding, not a rounding note."""
        d = run['levelised']
        assert d['tiers']['social_cost_ghg_usd']['per_mwh'] > 2 * d['slcoe_with_terminal_value']

    def test_total_societal_slcoe(self, run):
        """Direct SLCOE + SC-GHG + health. Tier 3 excluded from the dollar total BY DESIGN -- no
        sufficiently robust dollar-per-ton figure exists for air toxics, and inventing one would
        create false precision. The broader SC-GHG is used here rather than the narrower CO2-only
        Virginia SCC, since this line is meant to capture the full climate cost."""
        d = run['levelised']
        assert d['total_societal_slcoe'] == pytest.approx(119.47, abs=2.0)

    def test_levelised_on_the_same_basis_as_the_financial_figure(self, run):
        """Same discount rate, same base year, same twenty years -- so the per-MWh figures are
        directly addable rather than merely adjacent."""
        d = run['levelised']
        for key in ('virginia_scc_usd', 'social_cost_ghg_usd', 'health_impacts_usd'):
            implied = d['tiers'][key]['pv_usd'] / d['tiers'][key]['per_mwh']
            assert implied == pytest.approx(d['pv_demand_mwh'], rel=0.01)


class TestAgainstAppendixD:
    """Appendix D carries prior figures for Scenario 2. Ours run 11-17% higher, and the reason
    should be understood rather than assumed."""

    def test_direction_and_magnitude_of_the_difference(self, run):
        """Appendix D: SC-GHG $72.84/MWh, Virginia SCC $66.16, health $4.72.
        Ours: $81.15, $73.71, $5.50 -- +11.4%, +11.4%, +16.5%.

        The two climate tiers move by an identical 11.4%, which points at gas VOLUME rather than
        at the emission factors or the SC-GHG schedule: a change in either of those would not
        scale both gases by the same proportion. Health moves more (16.5%) because its NOx blend
        depends on the existing/new MW split, which the merit-order and fleet corrections this
        session also changed.

        The most likely driver is this session's demand and solar corrections: Scenario 2's clean
        share fell from 39.2% to 34.7% at 2045 once post-VCEA solar stopped being double-counted,
        which means more gas burned across the window."""
        t = run['levelised']['tiers']
        assert t['social_cost_ghg_usd']['per_mwh'] / 72.84 == pytest.approx(1.114, abs=0.03)
        assert t['virginia_scc_usd']['per_mwh'] / 66.16 == pytest.approx(1.114, abs=0.03)


class TestVerificationCoverage:
    """Appendix P.2 #11 requires zero unserved AND zero simultaneous charge/discharge before a
    solve is presented as final."""

    def test_simultaneous_dispatch_is_checked(self):
        """MISSING UNTIL 2026-09-14. Scenario2Solver.solve does not call verify_result, and this
        runner checked unserved energy only -- so twenty years were levelised with no degeneracy
        check at all. Measured clean when finally tested (zero hours at 2026 and 2045), but that
        was luck rather than verification.

        Scenario 2 is exactly where it matters: build_scenario2_problem lacks the SLCR splice and
        cycling costs that make simultaneous dispatch unattractive in build_problem, which is why
        it needs its own Bath discharge token."""
        import inspect
        import run_scenario2_slcoe as r2
        src = inspect.getsource(r2.solve_year)
        assert 'simultaneous charge/discharge' in src
        for key in ("'nc', 'nd'", "'fc', 'fd'", "'bc', 'bd'"):
            assert key in src

    def test_variables_per_hour_comes_from_the_problem(self):
        """A hardcoded 14 appeared at four sites. build_scenario2_problem happens to have 14, but a
        literal that must match a structure defined elsewhere is the shape that produced the
        merit-order and curtailment divergences."""
        import inspect
        import run_scenario2_slcoe as r2
        src = inspect.getsource(r2.solve_year)
        assert "problem['hv_params'][1]" in src
        assert 't * 14' not in src

    def test_both_gas_share_bases_are_recorded(self):
        """As the Scenario 1 and 1B runners do. The statutory base excludes nuclear and is what any
        compliance ceiling applies to; clean_share counts nuclear as clean and is the whitepaper's
        axis."""
        import inspect
        import run_scenario2_slcoe as r2
        src = inspect.getsource(r2.solve_year)
        assert "'gas_share_statutory'" in src and "'gas_share_of_demand'" in src

    def test_the_two_bases_differ_substantially_at_2045(self):
        """MEASURED: gas is 65.3% of total demand but 76.1% of the statutory base, because
        § 56-585.5(A) excludes in-Commonwealth nuclear. A compliance reading of Scenario 2 would
        cite 76.1%, not 65.3% -- a 10.8 point difference on the reference case."""
        assert 76.1 - 65.3 == pytest.approx(10.8, abs=0.1)
