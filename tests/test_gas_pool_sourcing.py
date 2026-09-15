"""
test_gas_pool_sourcing.py

The retain pool's MW figures are GAS capability on dual-fuel plants, not plant totals.

RESOLVED 2026-09-14 against Dominion's 2024 Annual Report (SEC, dei-ars-12312024.pdf), Virginia
Power Utility Generation, Net Summer Capability. An apparent discrepancy against EIA-860 nearly
prompted a change to GAS_POOL_MW -- a constant reaching every scenario's apply_gas_cap().
"""
import driver as drv
import pytest

#: Dominion 2024 Annual Report, Virginia Power Utility Generation, Net Summer Capability (MW).
#: Gravel Neck and Darbytown appear TWICE -- once under Gas, once under Oil.
ANNUAL_REPORT_GAS = {'Remington': 619, 'Elizabeth River': 327, 'Gordonsville': 218,
                     'Gravel Neck': 170, 'Darbytown': 168}
ANNUAL_REPORT_OIL = {'Gravel Neck': 198, 'Darbytown': 168}

#: EIA-860 (2025) net summer, which is gas PLUS oil on the dual-fuel units.
EIA_860_SUMMER = {'Gravel Neck': 368.0, 'Darbytown': 340.0, 'Elizabeth River': 325.0,
                  'Gordonsville': 218.0}


def pool():
    return {name: mw for name, mw, _year, _ovh in drv.POOL}


class TestPoolMatchesTheGasColumn:

    @pytest.mark.parametrize('plant', sorted(ANNUAL_REPORT_GAS))
    def test_each_plant_matches_the_annual_report_gas_figure(self, plant):
        assert pool()[plant] == pytest.approx(ANNUAL_REPORT_GAS[plant])

    def test_dual_fuel_plants_reconcile_to_eia_when_oil_is_added(self):
        """THE RESOLUTION. Gravel Neck 170 gas + 198 oil = 368, matching EIA-860 to the megawatt.
        The apparent 0.46 ratio was a fuel split, not a capacity discrepancy."""
        for plant, oil in ANNUAL_REPORT_OIL.items():
            combined = ANNUAL_REPORT_GAS[plant] + oil
            assert combined == pytest.approx(EIA_860_SUMMER[plant], abs=5)

    def test_single_fuel_plants_match_eia_directly(self):
        """Gordonsville and Elizabeth River are NOT dual-fuel, which is exactly why they looked
        inconsistent with the other two and why the pattern was misread."""
        for plant in ('Gordonsville', 'Elizabeth River'):
            assert pool()[plant] == pytest.approx(EIA_860_SUMMER[plant], abs=3)
            assert plant not in ANNUAL_REPORT_OIL

    def test_the_pool_total_is_unchanged(self):
        """The investigation correctly changed nothing."""
        import assumptions
        assert sum(pool().values()) == pytest.approx(2862.0)
        assert assumptions.GAS_NEW_BUILD_POOL_MW == pytest.approx(2862.0)

    def test_the_sourcing_is_recorded_at_the_definition(self):
        """Rule 10.3 -- so the next reader comparing against EIA-860 does not repeat the
        investigation and reach for GAS_POOL_MW."""
        # Reads the FILE, not inspect.getsource: the sourcing is in module-level comments, which
        # getsource on a module object does not return.
        #
        # AND JOINS COMMENT LINES FIRST. "2024 Annual Report" is split across a line break -- "2024"
        # ends one comment line and "Annual Report" begins the next -- so an unbroken substring
        # search fails on text that is plainly present. Eighth time in this project a check has
        # needed source-vs-prose or line-join handling before it was trustworthy.
        import os
        import re
        raw = open(os.path.join(os.path.dirname(drv.__file__), 'driver.py')).read()
        src = re.sub(r'\n#\s*', ' ', raw)
        assert 'GAS-FIRED CAPABILITY, NOT PLANT TOTAL' in src
        assert '2024 Annual Report' in src


class TestTheZeroGenerationReadingWasTooPessimistic:
    """VA_gas_capacity_schedules.md records these plants showing zero generation since Dec 2024,
    cause unconfirmed, and treats them conservatively as unavailable."""

    def test_the_series_ends_at_dec_2024_rather_than_falling_to_zero(self):
        """MEASURED from the EIA monthly series: Darbytown 42,561 MWh in July 2024 and 13,916 MWh
        in December; Gravel Neck 40,380 MWh in July. A 17% capacity factor on a 336 MW plant is
        ordinary peaker duty, and the near-zero months recur every February and December."""
        assert 13_916 > 0 and 42_561 > 0

    def test_eia_860_postdates_the_cutoff_and_lists_them_operating(self):
        """The 2025 vintage is after December 2024, and every Gravel Neck and Darbytown unit is OP.
        Of the three hypotheses the schedule records, the reporting-gap one is what the evidence
        supports."""
        import os
        src = open(os.path.join(os.path.dirname(drv.__file__), 'driver.py')).read()
        assert 'END OF THE DATASET, NOT THE END OF OPERATION' in src

    def test_elizabeth_river_is_the_genuine_exception(self):
        """All three units SB (standby), output already a fraction of 2023 levels through 2024."""
        import os
        src = open(os.path.join(os.path.dirname(drv.__file__), 'driver.py')).read()
        assert 'Elizabeth River is the genuine exception' in src


class TestBathIsDominionsShare:
    """CHANGED 2026-09-14 from 3,000 MW (whole plant) to 1,808 MW (Dominion's 60%).

    Two independent Dominion documents give 1,808 MW net summer: the 2024 Annual Report's Virginia
    Power Utility Generation table, footnote (3) excluding the "40% undivided interest owned by
    Allegheny Generating Company", and the 2025 IRP Update's Figure 3.1.1.1 Pumped Storage line."""

    def test_the_power_rating_is_dominions_share(self):
        import lp_model as lp
        assert lp.BATH_MW == 1808.0

    def test_the_energy_rating_follows_the_same_share(self):
        """An undivided interest is a share of the whole works -- reservoir, penstocks and machines
        alike -- so the energy rating scales with the power rating rather than being independently
        owned. 24,000 x (1,808/3,000) = 14,464."""
        import lp_model as lp
        assert lp.BATH_MWH == pytest.approx(24_000.0 * 1808.0 / 3000.0, abs=1.0)

    def test_the_duration_is_unchanged_at_eight_hours(self):
        """The check that the share was applied consistently: scaling one rating and not the other
        would silently change Bath's duration."""
        import lp_model as lp
        assert lp.BATH_MWH / lp.BATH_MW == pytest.approx(8.0, abs=0.01)

    def test_it_reaches_all_three_problem_builders_and_reserve(self):
        """THREE builders, not two -- build_problem, build_dispatch_problem AND
        build_scenario2_problem -- plus the reserve credit added earlier the same day. I asserted
        two and the test caught the third, which is the point of counting rather than assuming.

        Every scenario's dispatch therefore moves with this change, Scenario 2 included."""
        import os
        src = open(os.path.join(os.path.dirname(drv.__file__), 'lp_model.py')).read()
        assert src.count("bounds[hv(t,IDX['bd'])] = (0, BATH_MW)") == 3
        assert src.count("bounds[hv(t,IDX['bc'])] = (0, BATH_MW)") == 3
        ahr_src = open(os.path.join(os.path.dirname(drv.__file__), 'all_hours_reserve.py')).read()
        assert 'rhs.append(BATH_MW)' in ahr_src

    def test_the_change_is_documented_with_both_sources(self):
        import os
        import re
        raw = open(os.path.join(os.path.dirname(drv.__file__), 'assumptions.py')).read()
        src = re.sub(r'\n#:?\s*', ' ', raw)
        assert 'Allegheny Generating Company' in src
        assert 'CHANGED TO 1,808' in src


class TestScenario2BathWiring:
    """Audit of the Scenario 2 path after BATH_MW moved to 1,808, 2026-09-14."""

    def test_the_hardcoded_bath_literal_is_gone(self):
        """scripts/rerun_scenario2_virginia_only.py passed bath_county_mw=3000.0 as a LITERAL while
        run_all.py and compare_scenario2_capacity_standards.py both passed lp.BATH_MW. It alone
        would have kept 3,000 after the change -- 1,192 MW the model no longer credits. Every other
        input on those lines already came from a function."""
        import os
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for rel in ('scripts/rerun_scenario2_virginia_only.py',
                    'run_all.py',
                    'scripts/compare_scenario2_capacity_standards.py'):
            src = open(os.path.join(root, rel)).read()
            for line in src.split('\n'):
                if 'bath_county_mw=' in line and not line.strip().startswith('#'):
                    assert not re.search(r'bath_county_mw\s*=\s*\d', line), f'{rel}: {line.strip()}'

    def test_build_scenario2_problem_uses_the_constant_throughout(self):
        """Four live uses -- charge bound, discharge bound, a hard bc+bd <= BATH_MW constraint, and
        BATH_MWH for state of charge and initial fill. All follow the constant."""
        import inspect
        import lp_model as lp
        src = inspect.getsource(lp.build_scenario2_problem)
        code = [ln for ln in src.split('\n') if not ln.strip().startswith('#')]
        assert '\n'.join(code).count('BATH_M') == 5      # 3 x BATH_MW, 2 x BATH_MWH

    def test_scenario2s_own_reserve_module_is_marked_superseded(self):
        """It holds TWO reserve variables per hour where the generalised constraint holds five, and
        credits nothing for Bath -- the same gap all_hours_reserve had. Its stated justification
        (a different problem shape) no longer holds: measured, build_scenario2_problem and
        build_dispatch_problem are both NVAR_BUILD=0, NPH=14, BUILD_SCALE=None with the same keys."""
        import scenario2_all_hours_reserve as m
        assert 'SUPERSEDED 2026-09-14' in m.__doc__
        assert 'MISSING BATH' in m.__doc__

    def test_the_slcoe_runner_calls_neither_reserve_module(self):
        """Scenario 2 has no reserve constraint by design, so nothing published depends on either
        module -- which is why the superseded one could be marked rather than removed."""
        import os
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        src = open(os.path.join(root, 'run_scenario2_slcoe.py')).read()
        assert 'scenario2_all_hours_reserve' not in src
        assert 'scenario2_reserve_margin' not in src
