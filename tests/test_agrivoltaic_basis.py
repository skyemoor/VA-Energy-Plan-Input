"""
test_agrivoltaic_basis.py

Tests the 85%-of-total-solar agrivoltaic basis, its land footprint, farm lease income, and
Va. Code § 58.1-2636 local revenue share.

As with parking_ratio_basis, several tests lock LIMITATIONS rather than capabilities. The 85%
share is a stated assumption rather than a bottom-up result, and every figure derived from it
inherits that. A later edit that quietly drops the caveat would leave the numbers looking like
measurements.
"""
import pytest

import agrivoltaic_basis as ag


class TestSharedBasis:
    def test_share_is_eighty_five_percent_of_TOTAL_solar(self):
        """Not 90% of a non-urban subset, which is how scenario3_build.py frames it. The two
        differ by 13 points on every derived figure, so the distinction is load-bearing."""
        assert ag.AGRIVOLTAIC_SHARE_OF_TOTAL_SOLAR == 0.85

    def test_footprint_splits_the_build_correctly(self):
        f = ag.footprint(100_000.0)
        assert f.agrivoltaic_mw == pytest.approx(85_000.0)
        assert f.non_agrivoltaic_mw == pytest.approx(15_000.0)

    def test_firmed_acreage_exceeds_solar_only_but_modestly(self):
        """Storage adds real land but only ~2.5-4% -- reported separately so a reader comparing
        against another study's acres/MW knows whether storage is inside it."""
        f = ag.footprint(100_000.0)
        assert f.firmed_acres_low > f.solar_acres_low
        assert f.firmed_acres_low / f.solar_acres_low < 1.05

    def test_invalid_inputs_raise(self):
        with pytest.raises(ValueError, match='must be positive'):
            ag.footprint(0.0)
        with pytest.raises(ValueError, match='fraction'):
            ag.footprint(1000.0, agrivoltaic_share=1.5)


class TestTheAssumptionTravelsWithEveryFigure:
    def test_footprint_carries_the_assumption(self):
        assert 'STATED ALLOCATION ASSUMPTION' in ag.footprint(1000.0).assumption

    def test_assumption_names_current_practice_is_far_below(self):
        """NREL counts 13 existing Virginia agrivoltaic projects. Presenting 85% without that
        context would read as descriptive rather than aspirational."""
        s = ag.share_is_assumed()
        assert '13 existing' in s and 'not a description of current practice' in s

    def test_lease_income_inherits_the_assumption(self):
        assert ag.lease_income(ag.footprint(1000.0)).assumption == ag.share_is_assumed()


class TestLeaseIncomeAppliesBroadlyByDefault:
    """A real distinction from the appendix: a landowner is paid for hosting the array whether or
    not the siting is agrivoltaic. Restricting lease income to the agrivoltaic share would
    understate the income effect."""

    def test_default_covers_all_utility_scale_acreage(self):
        li = ag.lease_income(ag.footprint(100_000.0))
        assert 'whether or not the siting is agrivoltaic' in li.applies_to

    def test_agrivoltaic_only_is_smaller_and_says_why(self):
        f = ag.footprint(100_000.0)
        assert (ag.lease_income(f, agrivoltaic_only=True).annual_income_low
                < ag.lease_income(f).annual_income_low)
        assert 'also retains agricultural production' in ag.lease_income(f, agrivoltaic_only=True).applies_to

    def test_virginia_rates_exceed_the_national_average(self):
        assert ag.VA_LEASE_RATE_LOW > ag.NATIONAL_LEASE_RATE_HIGH

    def test_the_stability_argument_does_not_rest_on_yield(self):
        """The NSPM-relevant claim is income VARIANCE reduction. Crop yield under panels is
        contested and has no Virginia field-trial basis, so a benefit case resting on yield is
        far weaker than one resting on contracted revenue."""
        note = ag.lease_income(ag.footprint(1000.0)).income_stability_note
        assert 'VARIANCE' in note
        assert 'does not depend on agrivoltaic crop yields' in note

    def test_production_value_is_not_estimated(self):
        """Adding a speculative production figure to a well-sourced lease figure would degrade
        the latter. No field should offer one."""
        li = ag.lease_income(ag.footprint(1000.0))
        assert not any('production_value' in f or 'crop_income' in f
                       for f in li.__dataclass_fields__)


class TestRevenueShareStatute:
    """§ 58.1-2636, verified against the Code rather than assumed."""

    def test_base_rate_matches_the_statute(self):
        assert ag.REVENUE_SHARE_BASE_RATE_PER_MW == 1_400.0
        assert ag.revenue_share_rate_per_mw(2025) == 1_400.0

    def test_escalates_ten_percent_every_five_years_from_2026(self):
        assert ag.revenue_share_rate_per_mw(2026) == pytest.approx(1_540.0)
        assert ag.revenue_share_rate_per_mw(2030) == pytest.approx(1_540.0)
        assert ag.revenue_share_rate_per_mw(2031) == pytest.approx(1_694.0)
        assert ag.revenue_share_rate_per_mw(2045) == pytest.approx(2_049.74, abs=0.01)

    def test_storage_is_assessed_separately_from_generation(self):
        """§ 58.1-2636(A)(1)(ii). Easy to overlook, and at 2045 storage is roughly a third of the
        total -- omitting it understates the rural benefit by that much."""
        r = ag.revenue_share(2045, 173_780.7, 86_905.5)
        assert r.storage_revenue > 0
        assert r.storage_revenue / r.total_revenue == pytest.approx(0.33, abs=0.02)

    def test_omitting_storage_is_recorded_not_silent(self):
        assert 'storage_mw was not supplied' in ag.revenue_share(2045, 100_000.0).caveat

    def test_caveat_states_the_rate_is_a_ceiling(self):
        """'Up to' -- adopted by ordinance. Not every locality has one, and some adopt below the
        maximum, so these are upper bounds."""
        c = ag.revenue_share(2045, 1000.0, 100.0).caveat
        assert 'MAXIMUM' in c and 'ceiling' in c

    def test_caveat_flags_the_small_project_and_net_metering_exemptions(self):
        """Distributed rooftop and canopy are largely outside this mechanism -- a real asymmetry
        between the utility-scale and distributed paths."""
        c = ag.revenue_share(2045, 1000.0, 100.0).caveat
        assert 'exempt' in c and 'distributed rooftop and canopy' in c

    def test_caveat_flags_the_ac_versus_dc_ambiguity(self):
        assert 'measured in AC' in ag.revenue_share(2045, 1000.0, 100.0).caveat

    def test_2045_headline_figure(self):
        r = ag.revenue_share(2045, 173_780.7, 50_546.5 + 36_359.0)
        assert r.total_revenue / 1e6 == pytest.approx(534.3, abs=1.0)


class TestSLEACFarmIncomeComparison:
    """Virginia Tech / SLEAC net returns -- the statutory basis for agricultural use-value
    assessment under Va. Code § 58.1-3239. These are the numbers Virginia's own tax system runs
    on, which is what makes the comparison hard to dispute."""

    def test_composite_farm_net_return_matches_the_publication(self):
        assert ag.SLEAC_COMPOSITE_FARM_NET_RETURN_PER_ACRE == 17.69

    def test_per_crop_net_returns_match_the_publication(self):
        assert ag.SLEAC_NET_RETURN_PER_ACRE['soybeans'] == 197.83
        assert ag.SLEAC_NET_RETURN_PER_ACRE['corn'] == 76.27
        assert ag.SLEAC_NET_RETURN_PER_ACRE['hay'] == 0.32

    def test_lease_exceeds_composite_farm_return_by_two_orders_of_magnitude(self):
        r = ag.lease_versus_farm_income()
        assert r.multiple_low == pytest.approx(68, abs=1)
        assert r.multiple_high == pytest.approx(141, abs=1)

    def test_lease_exceeds_even_the_best_crop_severalfold(self):
        """Soybeans is the composite farm's best performer at $197.83/acre. The lease still
        exceeds it 6-13x, so the comparison does not depend on picking a weak crop."""
        r = ag.lease_versus_farm_income('soybeans')
        assert r.multiple_low > 6.0

    def test_unknown_crop_raises_rather_than_substituting(self):
        """Rule 5. The comparison's value is that it rests on Virginia's own statutory
        methodology; an out-of-state figure would silently destroy that."""
        with pytest.raises(ValueError, match='statutory'):
            ag.lease_versus_farm_income('cotton')

    def test_interpretation_states_yield_is_secondary_at_these_ratios(self):
        i = ag.lease_versus_farm_income().interpretation
        assert 'lose the entire crop' in i

    def test_interpretation_records_the_negative_years(self):
        """Four of seven years negative for Prince Edward corn, floored at zero before averaging.
        That is the income-variance case in Virginia's own official data."""
        assert 'NEGATIVE in four of the seven years' in ag.lease_versus_farm_income().interpretation

    def test_cross_jurisdiction_range_is_carried_for_the_conservative_case(self):
        """Prince Edward is the publication's worked example, not a Virginia average. Backing net
        returns out of published use-values across jurisdictions gives ~$20-88/acre."""
        lo, hi = ag.SLEAC_NET_RETURN_RANGE_ACROSS_JURISDICTIONS
        assert (lo, hi) == (20.0, 88.0)
        assert ag.VA_LEASE_RATE_LOW / hi > 13.0, 'even the most favourable county is far behind'

    def test_source_is_cited_on_every_result(self):
        assert '58.1-3239' in ag.lease_versus_farm_income().source


class TestVirginiaLandUseFit:
    """2022 Census of Agriculture. The choice of denominator IS the argument here, so all three
    are reported and tested -- all farmland flatters the case, cropland alone damns it, forage
    land is the one matching where the compatibility evidence actually is."""

    def test_census_land_use_totals_match_the_state_profile(self):
        assert ag.VA_LAND_IN_FARMS_BY_USE_ACRES['cropland'] == 2_884_293
        assert ag.VA_LAND_IN_FARMS_BY_USE_ACRES['pastureland'] == 1_915_266
        assert ag.VA_TOTAL_LAND_IN_FARMS_ACRES == 7_309_687

    def test_all_three_denominators_are_reported(self):
        r = ag.land_use_fit(ag.footprint(173_780.7))
        assert r.share_of_all_farmland[0] == pytest.approx(0.083, abs=0.005)
        assert r.share_of_cropland[0] == pytest.approx(0.210, abs=0.005)
        assert r.share_of_forage_land[0] == pytest.approx(0.200, abs=0.005)  # was 0.217 on the derived hay figure

    def test_cropland_share_is_the_hard_number_and_is_not_hidden(self):
        """21-32% of Virginia's cropland is what an opponent would reach for. It must be
        computed and available, not omitted in favour of the flattering denominator."""
        r = ag.land_use_fit(ag.footprint(173_780.7))
        assert r.share_of_cropland[1] > 0.30

    def test_requirement_fits_within_forage_land(self):
        """The central finding: pasture plus hay can absorb the whole requirement without
        touching corn, soybeans, cotton, peanuts or tobacco."""
        assert ag.land_use_fit(ag.footprint(173_780.7)).fits_within_forage is True

    def test_finding_names_the_compatibility_alignment(self):
        f = ag.land_use_fit(ag.footprint(173_780.7)).finding
        assert 'sheep grazing is the most mature practice' in f
        assert 'almost nonexistent' in f

    def test_finding_names_the_economic_alignment(self):
        """Pasture and hay carry the LOWEST SLEAC net returns, so lease income is most
        transformative exactly where compatibility is best. That alignment is the core of the
        case and should not be glossed."""
        f = ag.land_use_fit(ag.footprint(173_780.7)).finding
        assert 'LOWEST SLEAC net returns' in f
        assert ag.SLEAC_NET_RETURN_PER_ACRE['pasture'] < ag.SLEAC_NET_RETURN_PER_ACRE['corn']
        assert ag.SLEAC_NET_RETURN_PER_ACRE['hay'] < ag.SLEAC_NET_RETURN_PER_ACRE['corn']

    def test_derived_hay_constant_was_removed_not_merely_superseded(self):
        """An earlier version carried VA_HAY_ACRES_APPROX = 870,000, derived from NASS tonnage
        because the Census figure had not been located. The Census reports 1,117,726 -- the
        derivation was 22% LOW. The constant was deleted rather than left available, so it cannot
        be picked up by mistake."""
        assert not hasattr(ag, 'VA_HAY_ACRES_APPROX')
        assert not hasattr(ag, 'HAY_ACRES_IS_DERIVED')

    def test_forage_now_uses_the_census_figure(self):
        assert ag.VA_TOP_CROPS_ACRES['forage_hay_haylage'] == 1_117_726
        r = ag.land_use_fit(ag.footprint(173_780.7))
        assert r.forage_acres == 1_915_266 + 1_117_726

    def test_correction_moved_the_finding_favourably(self):
        """20.0-30.4% of forage land, against 21.7-33.1% under the understated derivation."""
        r = ag.land_use_fit(ag.footprint(173_780.7))
        assert r.share_of_forage_land[1] == pytest.approx(0.304, abs=0.005)

    def test_top_crops_list_is_flagged_as_partial(self):
        """It omits cotton, peanuts, tobacco, vegetables and orchards, so it must not be summed
        as total cropland."""
        r = ag.land_use_fit(ag.footprint(173_780.7))
        assert 'does NOT include cotton' in r.caveat
        assert sum(ag.VA_TOP_CROPS_ACRES.values()) < ag.VA_LAND_IN_FARMS_BY_USE_ACRES['cropland']

    def test_forage_comfortably_exceeds_the_weak_evidence_row_crops(self):
        """Forage land is 2.6x the soybean + corn + wheat acreage, so the compatible base is not
        merely sufficient but has margin."""
        forage = ag.VA_LAND_IN_FARMS_BY_USE_ACRES['pastureland'] + ag.VA_TOP_CROPS_ACRES['forage_hay_haylage']
        row = sum(ag.VA_TOP_CROPS_ACRES[c] for c in ('soybeans', 'corn_for_grain', 'wheat_for_grain'))
        assert forage / row > 2.5

    def test_weak_evidence_crops_are_named_explicitly(self):
        assert 'soybeans' in ag.WEAK_EVIDENCE_ROW_CROPS
        assert 'corn_for_grain' in ag.WEAK_EVIDENCE_ROW_CROPS

    def test_forage_uses_deliberately_exclude_cropland_as_a_whole(self):
        """Within cropland, hay and winter wheat are supported while corn and soybeans are not.
        Treating cropland as uniformly compatible would overstate the case."""
        assert 'cropland' not in ag.FORAGE_COMPATIBLE_USES


class TestCropAcreageAndSales:
    def test_top_crops_is_five_not_ten(self):
        """The state profile publishes a top-FIVE list; there is no top ten. Recorded so a reader
        expecting ten does not assume five are missing."""
        assert len(ag.VA_TOP_CROPS_ACRES) == 5
        assert ag.VA_TOP_CROPS_ACRES['cotton'] == 91_073

    def test_top_five_cover_most_but_not_all_cropland(self):
        listed = sum(ag.VA_TOP_CROPS_ACRES.values())
        cropland = ag.VA_LAND_IN_FARMS_BY_USE_ACRES['cropland']
        assert listed / cropland == pytest.approx(0.82, abs=0.01)
        assert cropland - listed == pytest.approx(515_000, abs=5_000)

    def test_sales_categories_are_separate_from_acreage(self):
        """Acreage is not published for the sales groupings, so the two must not be mixed."""
        assert 'vegetables_melons_potatoes' in ag.VA_CROP_SALES_BY_CATEGORY_THOUSANDS
        assert 'vegetables_melons_potatoes' not in ag.VA_TOP_CROPS_ACRES

    def test_vegetables_are_small_in_value_despite_strongest_evidence(self):
        """The compatibility gradient does not track acreage or value: vegetables have the
        strongest evidence in the agrivoltaics literature but are a small share of Virginia crop
        sales, so they cannot carry the buildout."""
        sales = ag.VA_CROP_SALES_BY_CATEGORY_THOUSANDS
        assert sales['vegetables_melons_potatoes'] < sales['grains_oilseeds_dry_beans_peas'] / 5


class TestGrazingCapacityConstraint:
    """The constraint the compatibility argument conceals. Sheep grazing is the strongest per-acre
    evidence in agrivoltaics and is NOT a scalable answer at Virginia's buildout -- a rebuttal
    available to anyone who looks up the state's flock size."""

    def test_virginia_flock_is_smaller_than_the_national_solar_grazing_flock(self):
        assert ag.VA_LIVESTOCK_INVENTORY['sheep_and_lambs'] < ag.NATIONAL_SOLAR_GRAZING_SHEEP

    def test_sheep_cannot_cover_the_acreage(self):
        g = ag.grazing_capacity(605_626)
        assert g.sheep_can_cover is False
        assert g.multiple_of_state_flock_low > 14

    def test_the_shortfall_is_more_than_an_order_of_magnitude(self):
        """Not a margin question -- 15x to 44x. Any framing implying sheep could manage this
        acreage is wrong by more than a factor of ten."""
        g = ag.grazing_capacity(605_626)
        assert g.multiple_of_state_flock_low > 10
        assert g.multiple_of_state_flock_high > 40

    def test_cattle_are_named_as_the_scalable_alternative_with_its_cost(self):
        f = ag.grazing_capacity(605_626).finding
        assert 'Cattle' in f and 'taller, costlier racking' in f

    def test_finding_directs_load_to_hay_which_needs_no_animals(self):
        """The honest resolution: forage LAND is abundant while grazing LIVESTOCK is not, so hay
        and haylage carry more of the load than the grazing literature suggests."""
        assert 'needs no\nanimals at all' in ag.grazing_capacity(605_626).finding.replace('  ', ' ') \
            or 'needs no animals at all' in ag.grazing_capacity(605_626).finding

    def test_stocking_rate_is_a_range_not_a_point(self):
        lo, hi = ag.SOLAR_GRAZING_SHEEP_PER_ACRE
        assert lo < hi


class TestFSACropAcreage:
    """USDA FSA 2026 Virginia crop acreage -- a second, independent and much finer source than the
    Census state profile: 121 crops against a top-five list, 2026 against 2022, county resolution,
    and intended use recorded."""

    def test_mixed_forage_is_the_largest_crop_in_virginia(self):
        """1,373,771 acres, 45.6% of all planted acreage -- larger than soybeans and corn
        combined. The forage finding does not rest on a marginal category."""
        f = ag.FSA_2026_TOP_CROPS_PLANTED_ACRES
        assert f['mixed_forage'] == max(f.values())
        assert f['mixed_forage'] > f['soybeans'] + f['corn']

    def test_forage_is_nearly_half_of_planted_acreage(self):
        assert ag.FSA_FORAGE_ACRES / ag.FSA_2026_TOTAL_PLANTED_ACRES == pytest.approx(0.478, abs=0.01)

    def test_fsa_excludes_pasture_and_says_so(self):
        """FSA counts PLANTED acres. Pasture is not planted, so 1.9M Census acres are absent.
        Summing the two sources carelessly is the error this caveat prevents."""
        assert 'excludes pastureland' in ag.FSA_SOURCE_CAVEAT
        assert 'Do not sum FSA planted acres with Census cropland' in ag.FSA_SOURCE_CAVEAT

    def test_fsa_forage_and_census_pasture_are_disjoint_and_combinable(self):
        """The one combination that IS valid, and it gives the compatible base."""
        base = ag.FSA_FORAGE_ACRES + ag.VA_LAND_IN_FARMS_BY_USE_ACRES['pastureland']
        assert base == 3_355_276
        assert 605_626 / base < 0.20
        assert 921_733 / base < 0.28

    def test_two_sources_agree_on_the_forage_conclusion(self):
        """Census route gave 20.0-30.4%; FSA route gives 18-27%. Independent data, same finding --
        which is worth more than either alone."""
        census_base = (ag.VA_LAND_IN_FARMS_BY_USE_ACRES['pastureland']
                       + ag.VA_TOP_CROPS_ACRES['forage_hay_haylage'])
        fsa_base = ag.FSA_FORAGE_ACRES + ag.VA_LAND_IN_FARMS_BY_USE_ACRES['pastureland']
        assert abs(921_733 / census_base - 921_733 / fsa_base) < 0.05

    def test_cover_crop_is_present_but_not_counted_as_compatible(self):
        """302,940 acres, 10.1% of planted acreage, but not a cash crop and not addressed in the
        agrivoltaic literature reviewed. Neither claimed nor counted."""
        assert ag.FSA_2026_TOP_CROPS_PLANTED_ACRES['cover_crop'] == 302_940
        assert 'cover_crop' not in ag.FSA_FORAGE_CROPS

    def test_coverage_is_statewide_and_fine_grained(self):
        assert ag.FSA_2026_COUNTIES == 98
        assert ag.FSA_2026_DISTINCT_CROPS == 121
