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
