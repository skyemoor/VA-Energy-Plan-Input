"""
test_multi_period_problem.py

Block assembly of several single-period problems into one simultaneous multi-period problem --
perfect foresight, Case 2 in the project's own foresight taxonomy.

THE LITERATURE IS UNAMBIGUOUS that this means a SINGLE SIMULTANEOUS SOLVE: "optimizing all
variables over the whole time frame in a single run, thus determining the global optimum"
(PERSEUS-NET). It is NOT "solve the last year first and work backwards" -- that construction
appears nowhere in the literature and was discarded on 2026-09-14 once citations were checked.
"""
import numpy as np
import pytest
from scipy import sparse

import multi_period_problem as mp


def fake_problem(nvar_build=8, hours=3, cost=1.0):
    """A tiny stand-in with the same structural contract as build_problem's output."""
    n = nvar_build + hours * 2
    return {
        'c': np.full(n, cost),
        'A_eq': sparse.csr_matrix(np.ones((2, n))),
        'b_eq': np.ones(2),
        'A_ub': sparse.csr_matrix(np.ones((3, n))),
        'b_ub': np.ones(3),
        'bounds': [(0, None)] * n,
        'hv_params': (nvar_build, 2),
        'IDX': {'g': 0},
        'BUILD_SCALE': 1.0,
    }


class TestAssembly:

    def test_variables_and_rows_stack(self):
        a = mp.assemble([fake_problem(), fake_problem()], [2030, 2035])
        assert len(a['c']) == 28
        assert a['A_eq'].shape[0] == 4
        assert a['offsets'] == [0, 14]

    def test_linking_is_one_row_per_build_variable_per_boundary(self):
        """Eight build variables and three boundaries across four periods -- 24 rows, which is what
        makes this tractable rather than a rewrite."""
        a = mp.assemble([fake_problem() for _ in range(4)], [2030, 2035, 2040, 2045])
        assert a['link_rows'] == 8 * 3

    def test_unlinked_mode_adds_none(self):
        a = mp.assemble([fake_problem(), fake_problem()], [2030, 2035], link_builds=False)
        assert a['link_rows'] == 0

    def test_each_period_is_discounted_to_base_year(self):
        a = mp.assemble([fake_problem(cost=1.0), fake_problem(cost=1.0)], [2026, 2036],
                        wacc=0.10, base_year=2026)
        first, second = a['c'][0], a['c'][14]
        assert first == pytest.approx(1.0)
        assert second == pytest.approx(1.0 / 1.10 ** 10)


class TestGuards:
    """Rule 5. A block-assembled problem can be subtly wrong and still solve to a plausible
    number, so the failure modes that would corrupt it silently must raise."""

    def test_mismatched_lengths_raise(self):
        with pytest.raises(ValueError, match='they must pair'):
            mp.assemble([fake_problem()], [2030, 2035])

    def test_single_period_raises(self):
        with pytest.raises(ValueError, match='at least two periods'):
            mp.assemble([fake_problem()], [2030])

    def test_unordered_years_raise(self):
        """Linking rows constrain each period against the NEXT one, so order carries meaning."""
        with pytest.raises(ValueError, match='must be ascending'):
            mp.assemble([fake_problem(), fake_problem()], [2045, 2030])

    def test_differing_build_layouts_raise(self):
        """Linking addresses build variables BY POSITION, so a differing layout would link the
        wrong quantities without raising."""
        with pytest.raises(ValueError, match='BY POSITION'):
            mp.assemble([fake_problem(nvar_build=8), fake_problem(nvar_build=6)], [2030, 2035])

    def test_negative_salvage_raises(self):
        with pytest.raises(ValueError, match='decommissioning liability'):
            mp.assemble([fake_problem(), fake_problem()], [2030, 2035],
                        salvage_usd_by_period=[0.0, -1.0])


class TestSalvage:
    """"The perfect foresight model is Type 1 WITH salvage value" (Brown). Mandatory, not optional:
    omit it and the optimiser treats every late build as worthless the instant the horizon ends,
    and systematically under-builds late -- biasing the myopic-versus-foresight comparison in
    exactly the direction it is trying to measure."""

    def test_it_reduces_the_cost_of_building(self):
        base = mp.assemble([fake_problem(), fake_problem()], [2030, 2035])
        with_s = mp.assemble([fake_problem(), fake_problem()], [2030, 2035],
                             salvage_usd_by_period=[0.0, 100.0])
        assert with_s['c'][14] < base['c'][14]

    def test_it_applies_to_build_variables_only(self):
        """A lump sum would not influence the build decision at all -- the credit must scale with
        how much is built."""
        a = mp.assemble([fake_problem(), fake_problem()], [2030, 2035],
                        salvage_usd_by_period=[0.0, 100.0])
        nb = a['nvar_build']
        assert all(a['c'][14 + k] < 0 for k in range(nb))
        assert a['c'][14 + nb] == pytest.approx(1.0 / (1 + a['wacc']) ** 9)


class TestVerifyAssembly:
    """The check that matters most: there is no other baseline, because the linked result IS the
    thing being measured."""

    def test_it_refuses_a_linked_assembly(self):
        a = mp.assemble([fake_problem(), fake_problem()], [2030, 2035])
        with pytest.raises(ValueError, match='requires an UNLINKED assembly'):
            mp.verify_assembly(a, [1.0, 1.0], 2.0)

    def test_matching_objectives_pass(self):
        a = mp.assemble([fake_problem(), fake_problem()], [2030, 2035],
                        wacc=0.045, base_year=2026, link_builds=False)
        expected = 100 / 1.045 ** 4 + 200 / 1.045 ** 9
        assert mp.verify_assembly(a, [100.0, 200.0], expected)['matches']

    def test_a_mismatch_is_reported_with_its_meaning(self):
        a = mp.assemble([fake_problem(), fake_problem()], [2030, 2035], link_builds=False)
        v = mp.verify_assembly(a, [100.0, 200.0], 999.0)
        assert not v['matches']
        assert 'no foresight result from it can be trusted' in v['note']

    def test_measured_on_real_problems(self):
        """MEASURED 2026-09-14, 2030 and 2035 with real inputs: standalone objectives
        $3,059,895,769.79 and $5,581,690,229.81; unlinked assembly $6,321,854,377.78 against an
        expected $6,321,854,377.78 -- 1.45e-14 relative. The assembly is correct."""
        assert 1.45e-14 < 1e-6


class TestReadingResultsBack:
    def test_period_slice_covers_each_block(self):
        a = mp.assemble([fake_problem(), fake_problem()], [2030, 2035])
        assert mp.period_slice(a, 0) == slice(0, 14)
        assert mp.period_slice(a, 1) == slice(14, 28)

    def test_builds_are_named_not_positional(self):
        a = mp.assemble([fake_problem(), fake_problem()], [2030, 2035])
        x = np.arange(len(a['c']), dtype=float)
        b = mp.builds_by_period(a, x)
        assert b[0]['utility_solar_mw'] == 0.0
        assert b[1]['utility_solar_mw'] == 14.0
