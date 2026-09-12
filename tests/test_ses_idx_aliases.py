"""
test_ses_idx_aliases.py

Locks the SES-compliant IDX aliases added 2026-09-12.

WHY THEY EXIST. A 2026-09-09 decision deliberately kept the short keys ('g' through 'export')
because driver.py and every solve_*.py script reference IDX['g'] directly, and renaming would
cascade into files that change could not verify. That decision then aged the way the t_peak one
did: in review, 'g' was described as "the gas total" and the reviewer asked -- total WHAT, fuel,
cost, MWh? And 'gascum' says "cumulative gas" without saying cumulative what, in what units, or
what for.

Aliasing is the interim: both spellings address the same column, so new code can be readable
without the cascade. The full rename is scheduled for after the first successful 2045 solve, when
it can be verified against real solve data rather than assumed safe.
"""
import pytest

import lp_model as lp


class TestAliasesResolveToTheSameColumn:

    @pytest.fixture(scope='class')
    def index_map(self):
        return lp._add_ses_aliases(dict(
            g=0, bc=1, bd=2, bsoc=3, nc=4, nd=5, nsoc=6, fc=7, fd=8, fsoc=9, gascum=10,
            unserved=11, curt=12, export=13))

    def test_every_alias_points_at_its_short_key(self, index_map):
        for readable, short in lp.SES_IDX_ALIASES.items():
            if short in index_map:
                assert index_map[readable] == index_map[short], f'{readable} != {short}'

    def test_gas_generation_states_quantity_and_units(self, index_map):
        """'g' is gas GENERATION in MW during hour t -- not fuel, not cost, not cumulative."""
        assert index_map['gas_generation_mw'] == index_map['g']

    def test_cumulative_gas_states_quantity_and_units(self, index_map):
        """'gascum' is cumulative gas GENERATION in GWh, accumulating g * 0.001 hourly. It exists
        only so the gas-share constraint can test a year-end total."""
        assert index_map['cumulative_gas_generation_gwh'] == index_map['gascum']

    def test_short_keys_still_work(self, index_map):
        """Legacy callers in driver.py and solve_*.py must keep working -- that is the whole point
        of aliasing rather than renaming."""
        for short in ('g', 'gascum', 'bd', 'nd', 'fd', 'unserved', 'curt'):
            assert short in index_map


class TestAliasingIsSafe:

    def test_absent_columns_are_not_aliased(self, ):
        """Rule 5. The four IDX dicts in this module carry different subsets; creating an alias to
        a column this problem does not have would be worse than having no alias."""
        small = lp._add_ses_aliases(dict(g=0, bc=1, bd=2, bsoc=3))
        assert 'gas_generation_mw' in small
        assert 'cumulative_gas_generation_gwh' not in small, 'aliased a column that does not exist'
        assert 'sodium_ion_discharge_mw' not in small

    def test_existing_ses_compliant_keys_are_not_overwritten(self):
        """The seven distributed keys were already SES-compliant and must not be disturbed."""
        m = lp._add_ses_aliases(dict(g=0, dist_na_charge_mw=14))
        assert m['dist_na_charge_mw'] == 14

    def test_aliases_are_applied_by_build_problem(self):
        import numpy as np, os, driver as drv, paths
        p = paths.intermediate('demand_2030fy_va_only.npy')
        if not os.path.exists(p):
            pytest.skip('demand intermediate not built')
        w = np.load(paths.weather_year('hydro_year1_2016_17_RECONSTRUCTED.npz'))
        d = np.load(p)
        prob = lp.build_problem(w['solar'], w['wind'], w['nuclear'],
                                lp.exist_solar_mw(2030) * w['solar'], d,
                                drv.gas_target_share(2030), verbose=False)
        assert prob['IDX']['gas_generation_mw'] == prob['IDX']['g']


class TestRowCounterIsDocumented:
    def test_the_row_reuse_trap_is_recorded_at_the_reset_site(self):
        """`row` is not a running index across the problem -- it is one variable reused and reset
        per constraint block, eight times. Using it as an equality row count late in build_problem
        produced an A_eq of 175,566 rows against a b_eq of 61,325."""
        src = open(lp.__file__).read()
        assert 'REUSED and RESET to zero at the start of each' in src
        assert 'must use len(eq_rhs)' in src
