"""
test_pathway_comparison.py

PathwayComparison -- myopic chain against target-first snapshot.

Several tests lock the CAVEATS rather than the arithmetic. The comparison's headline number is a
myopia penalty, and the literature's 14-23% figures are cumulative net present cost while ours is
an endpoint annual cost. Presenting one as the other would be the easiest error to make here.
"""
import pytest

from pathway_comparison import (LITERATURE_MYOPIA_PENALTY_RANGE, MATERIAL_DIFFERENCE_FRACTION,
                                PathwayComparison)


def chain(iron_air=(0.0, 0.0, 0.0, 100_000.0), solar=120_000.0, cost=None):
    rows = []
    for i, year in enumerate((2030, 2035, 2040, 2045)):
        r = {'year': year, 'solar_mw_total': solar * (i + 1) / 4,
             'na_power_mw': 40_000.0, 'na_energy_mwh': 240_000.0,
             'ironair_energy_mwh': iron_air[i]}
        if cost is not None and year == 2045:
            r['annual_cost_usd'] = cost
        rows.append(r)
    return rows


def target(solar=120_000.0, iron_air=100_000.0, cost=None):
    r = {'year': 2045, 'solar_mw_total': solar, 'na_power_mw': 40_000.0,
         'na_energy_mwh': 240_000.0, 'ironair_energy_mwh': iron_air}
    if cost is not None:
        r['annual_cost_usd'] = cost
    return r


class TestInputValidation:
    """Rule 5. A comparison built on the wrong inputs is worse than no comparison."""

    def test_empty_chain_raises(self):
        with pytest.raises(ValueError, match='chain_checkpoints is empty'):
            PathwayComparison([], target())

    def test_chain_not_reaching_2045_raises(self):
        with pytest.raises(ValueError, match='does not reach 2045'):
            PathwayComparison(chain()[:3], target())

    def test_out_of_order_chain_raises(self):
        """The chain is sequential and a later checkpoint depends on the earlier one, so order
        carries meaning rather than being presentational."""
        c = chain()
        with pytest.raises(ValueError, match='out of order'):
            PathwayComparison([c[2], c[0], c[1], c[3]], target())


class TestFinalSystemAgreement:
    """The literature claims intertemporal and myopic models reach a similar final system while
    differing in pathway. This tests that claim against our own numbers rather than assuming it."""

    def test_identical_builds_agree(self):
        assert PathwayComparison(chain(), target()).final_systems_agree() is True

    def test_material_difference_is_detected(self):
        c = PathwayComparison(chain(solar=120_000.0), target(solar=90_000.0))
        assert c.final_systems_agree() is False
        assert any(d.is_material for d in c.build_deltas() if d.name == 'solar_mw_total')

    def test_difference_below_threshold_is_not_material(self):
        small = 120_000.0 * (1 + MATERIAL_DIFFERENCE_FRACTION / 2)
        assert PathwayComparison(chain(solar=small), target()).final_systems_agree() is True

    def test_zero_base_reports_none_not_zero_percent(self):
        """A percentage against a zero base is undefined. Reporting 0.0 would read as agreement
        when one pathway built nothing and the other built a fleet."""
        c = PathwayComparison(chain(iron_air=(0, 0, 0, 50_000.0)), target(iron_air=0.0))
        d = next(d for d in c.build_deltas() if d.name == 'ironair_energy_mwh')
        assert d.fraction is None
        assert d.is_material is False


class TestMyopiaPenalty:

    def test_penalty_is_computed_when_both_costs_present(self):
        c = PathwayComparison(chain(cost=1.2e10), target(cost=1.0e10))
        assert c.cumulative_myopia_penalty() == pytest.approx(0.20)

    def test_missing_cost_returns_none_not_zero(self):
        """A missing cost is not a zero penalty (Rule 5)."""
        assert PathwayComparison(chain(), target()).cumulative_myopia_penalty() is None

    def test_reading_states_the_comparability_caveat(self):
        """Ours is endpoint ANNUAL cost; the literature's 14-23% is CUMULATIVE NPC. Conflating
        them is the easiest error available here."""
        r = PathwayComparison(chain(cost=1.2e10), target(cost=1.0e10)).penalty_against_literature()
        assert 'not directly comparable' in r.lower()

    def test_negative_penalty_is_flagged_as_suspicious(self):
        """A myopic pathway cheaper than target-first inverts the literature, and the usual cause
        is the two pathways not solving the same problem."""
        r = PathwayComparison(chain(cost=0.9e10), target(cost=1.0e10)).penalty_against_literature()
        assert 'CHEAPER' in r and 'inverts the literature' in r

    def test_literature_range_is_recorded(self):
        assert LITERATURE_MYOPIA_PENALTY_RANGE == (0.14, 0.23)


class TestIronAirDeferral:
    """The specific risk: at 2030 with 59% gas there is little reason to build 100-hour storage; at
    2045 with zero gas it is essential. A chain that builds the whole fleet in the final checkpoint
    is the delay-then-overbuild pattern, and implausible against any deployment rate."""

    def test_deferral_is_detected(self):
        r = PathwayComparison(chain(iron_air=(0, 0, 0, 100_000.0)), target()).iron_air_deferral()
        assert r['deferred'] is True
        assert r['share_built_in_final_checkpoint'] == pytest.approx(1.0)
        assert 'delay-then-overbuild' in r['note']

    def test_spread_build_is_not_deferral(self):
        r = PathwayComparison(chain(iron_air=(25_000, 50_000, 75_000, 100_000.0)),
                              target()).iron_air_deferral()
        assert r['deferred'] is False
        assert 'spread across checkpoints' in r['note']

    def test_no_iron_air_is_not_reported_as_deferral(self):
        """Building none is a different finding from deferring, and conflating them would report a
        false alarm on a scenario that simply does not use the technology."""
        r = PathwayComparison(chain(iron_air=(0, 0, 0, 0)), target()).iron_air_deferral()
        assert r['deferred'] is False
        assert 'not the question here' in r['note']


class TestCaveatsTravelWithTheSummary:

    def test_all_three_caveats_present(self):
        s = PathwayComparison(chain(cost=1.2e10), target(cost=1.0e10)).summary()
        assert len(s['caveats']) == 3

    def test_summary_names_the_npc_mismatch(self):
        s = PathwayComparison(chain(), target()).summary()
        assert any('CUMULATIVE NET PRESENT COST' in c for c in s['caveats'])

    def test_summary_records_that_case_2_is_not_implemented(self):
        """Target-first here is a standalone snapshot (Case 1), not a perfect-foresight transition
        (Case 2). Case 2 is the true backcasting equivalent."""
        s = PathwayComparison(chain(), target()).summary()
        assert any('Case 2' in c and 'not implemented' in c for c in s['caveats'])

    def test_summary_warns_that_agreement_is_expected(self):
        """A similar final system is the literature's own predicted result, not evidence that the
        pathway choice does not matter."""
        s = PathwayComparison(chain(), target()).summary()
        assert any('not evidence that the pathway choice does not matter' in c for c in s['caveats'])
