"""
test_agrivoltaic_overlay.py

Agrivoltaic siting as an overlay applied to every scenario, not a Scenario 3 property.
"""
import pytest

import agrivoltaic_basis as ab
import agrivoltaic_overlay as ao


class TestItAppliesEverywhere:
    """Carrying it in Scenario 3 alone gave that scenario a benefit stream the others were denied
    by construction -- and it is unphysical besides: Scenario 1's 156,737 MW has to go somewhere,
    and that somewhere is overwhelmingly agricultural land."""

    def test_the_share_defaults_to_the_project_assumption(self):
        o = ao.apply(10_000.0)
        assert o.agrivoltaic_mw == pytest.approx(8_500.0)
        assert ab.AGRIVOLTAIC_SHARE_OF_TOTAL_SOLAR == 0.85

    def test_the_split_sums_to_the_build(self):
        o = ao.apply(4_583.0)
        assert o.agrivoltaic_mw + o.conventional_mw == pytest.approx(4_583.0)

    def test_an_out_of_range_share_raises(self):
        with pytest.raises(ValueError, match='must be a fraction'):
            ao.apply(1_000.0, share=1.5)


class TestItChangesCostAndLandNotGeneration:
    """A sheep-grazed tracking array generates exactly what a conventional tracking array generates
    -- NREL gives both 5.9 acres/MW and the same structures, because they ARE the same structures.

    That is why this is arithmetic on a solved build rather than a constraint inside the LP. The
    C.2 carve-out had to enter the residual because it changes what is generated; this does not."""

    def test_land_does_not_vary_with_the_share(self):
        """Only who else uses the land changes, not how much there is."""
        a, b = ao.apply(10_000.0, share=0.0), ao.apply(10_000.0, share=1.0)
        assert a.acres_low == b.acres_low and a.acres_high == b.acres_high

    def test_nrel_gives_grazing_the_same_acreage_as_conventional(self):
        assert ab.AGRIVOLTAIC_SHEEP_ACRES_PER_MW == 5.9
        assert ab.ACRES_PER_MW_LOW <= 5.9 <= ab.ACRES_PER_MW_HIGH

    def test_the_premium_scales_with_agrivoltaic_capacity_only(self):
        assert ao.apply(10_000.0, share=0.0).capex_premium_usd == 0.0
        full = ao.apply(10_000.0, share=1.0).capex_premium_usd
        assert full == pytest.approx(10_000.0 * 1e6 * 0.07)


class TestTheGrazingPremiumIsTheLowEndOfNRELsRange:
    """NREL/TP-6A20-77811 gives $0.07-0.80/W-DC across all dual-use cases. SHEEP GRAZING IS THE LOW
    END, because these systems "can use conventional PV structures and do not require as much site
    preparation or seeding" -- and several site-prep costs FALL relative to bare ground, since the
    land was already pasture."""

    def test_the_figure(self):
        assert ab.AGRIVOLTAIC_SHEEP_CAPEX_PREMIUM_USD_PER_WDC == 0.07

    def test_the_500kw_benchmark_is_recorded_as_conservative(self):
        """NREL states larger systems "benefit significantly from economies of scale", so a
        utility-scale premium should be lower. Carrying the benchmark unadjusted overstates it."""
        import re
        src = re.sub(r'\s+', ' ', open(ab.__file__).read())
        assert 'economies of scale' in src


class TestCattleAreRefusedRatherThanApproximated:
    """Rule 5. NREL says cattle "are expected to be more expensive because of the need to elevate
    the panels and, in some cases, reinforce the system structure" -- 9.8 acres/MW against 5.9, a
    two-thirds increase in LAND as well as capital -- but gives no equivalent of the $0.07/W-DC
    grazing figure."""

    def test_cattle_raises_rather_than_reusing_the_sheep_premium(self):
        with pytest.raises(NotImplementedError, match='would understate it'):
            ao.apply(1_000.0, livestock='cattle')

    def test_an_unknown_livestock_raises(self):
        with pytest.raises(ValueError, match='expected "sheep" or "cattle"'):
            ao.apply(1_000.0, livestock='goats')

    def test_the_cattle_acreage_is_recorded_even_though_unusable(self):
        assert ab.AGRIVOLTAIC_CATTLE_ACRES_PER_MW == 9.8


class TestMeasuredOnScenario2:
    """MEASURED 2026-09-14 against Scenario 2's utility-scale new build after the carve-out."""

    def test_2045(self):
        o = ao.apply(4_583.0)
        assert o.agrivoltaic_mw == pytest.approx(3_896, abs=1)
        assert o.capex_premium_usd / 1e6 == pytest.approx(273, abs=1)
        assert o.acres_low == pytest.approx(22_915, abs=1)
