"""
test_chesapeake_siting.py

Tests chesapeake_ci_rooftop_solar_estimate.py.

Chesapeake is the first extract with a NAME field, which no other county provided. That makes the
classification spot-checkable against reality rather than only against the coded domain -- see
TestClassificationAgainstRealBuildingNames, which is the closest thing this project has to
ground truth on whether a building-class legend means what it says.
"""
import os

import pandas as pd
import pytest

import chesapeake_ci_rooftop_solar_estimate as ch
from rooftop_solar_estimation_base import BaseRooftopSolarEstimator

REAL_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'source',
                        'ChesapeakeSelectedBuilding_Outlines.csv')
real_data = pytest.mark.skipif(not os.path.exists(REAL_CSV),
                               reason='Chesapeake extract not present in data/source/')


class TestBuildCiEligiblePopulation:

    def df(self, rows):
        return pd.DataFrame(rows)

    def test_all_five_included_classes_pass(self):
        rows = [{'BUILDINGCLASS': c, 'SHAPESTArea': 5000.0}
                for c in ch.CI_ELIGIBLE_BUILDING_CLASSES]
        assert len(ch.build_ci_eligible_population(self.df(rows))) == 5

    def test_excluded_classes_never_pass_regardless_of_size(self):
        """Government, Education, Transportation, Religious, Recreation, Cultural/Heritage,
        Airport, CommunityCenter and General/Residential, all at implausible size."""
        excluded = [1, 2, 4, 5, 7, 8, 9, 11, 13]
        rows = [{'BUILDINGCLASS': c, 'SHAPESTArea': 500_000.0} for c in excluded]
        assert len(ch.build_ci_eligible_population(self.df(rows))) == 0

    def test_general_residential_excluded_entirely_no_size_heuristic(self):
        """Arlington had to assume General/Residential over 2,000 sqft was commercial, because it
        had no Apartment category. Chesapeake states Apartment outright, so the heuristic is not
        needed and must NOT be applied -- a large General/Residential building here is a large
        house, not an unlabelled apartment block."""
        rows = [{'BUILDINGCLASS': 1, 'SHAPESTArea': 50_000.0}]
        assert len(ch.build_ci_eligible_population(self.df(rows))) == 0

    def test_six_hundred_sqft_floor_applies_to_included_classes(self):
        rows = [{'BUILDINGCLASS': 6, 'SHAPESTArea': 599.0},
                {'BUILDINGCLASS': 6, 'SHAPESTArea': 600.0}]
        result = ch.build_ci_eligible_population(self.df(rows))
        assert len(result) == 1
        assert result.iloc[0]['SHAPESTArea'] == 600.0

    def test_wrong_area_column_raises_with_guidance(self):
        """Chesapeake uses SHAPESTArea; Fairfax Shape__Area; Arlington SHAPE_Area. Three
        conventions across five counties, so this fails loudly rather than with a KeyError."""
        with pytest.raises(ValueError, match='SHAPESTArea'):
            ch.build_ci_eligible_population(pd.DataFrame({'BUILDINGCLASS': [6],
                                                          'Shape__Area': [5000.0]}))


class TestLegendIsSourcedNotInferred:
    """Chesapeake's coded domain came from its own ArcGIS REST endpoint. Richmond's Structures
    SubType was ASSUMED from Prince William's numbering and proved wrong -- subtype 3 was
    accessory buildings at 200 sqft median, not C&I. These lock the sourced values."""

    def test_legend_has_all_fourteen_classes(self):
        assert len(ch.BUILDING_CLASS_LEGEND) == 14

    def test_key_codes_match_the_published_domain(self):
        assert ch.BUILDING_CLASS_LEGEND[6] == 'Commercial'
        assert ch.BUILDING_CLASS_LEGEND[12] == 'Industrial'
        assert ch.BUILDING_CLASS_LEGEND[14] == 'Apartment'
        assert ch.BUILDING_CLASS_LEGEND[1] == 'General/Residential'

    def test_included_set_is_the_five_intended_classes(self):
        assert sorted(ch.CI_ELIGIBLE_BUILDING_CLASSES) == [3, 6, 10, 12, 14]


class TestSharedHierarchyReuse:
    def test_estimator_subclasses_the_shared_base(self):
        assert issubclass(ch._ChesapeakeRooftopEstimator, BaseRooftopSolarEstimator)

    def test_density_matches_the_same_nvrc_sample_as_the_other_counties(self):
        df = pd.DataFrame([{'BUILDINGCLASS': 6, 'SHAPESTArea': 10_000.0}])
        r = ch.estimate_chesapeake_ci_rooftop_solar(df)
        assert r.density_stats.n == 8
        assert r.density_stats.mean_kw_per_sqft == pytest.approx(0.006792, abs=1e-6)

    def test_hand_computed_case(self):
        """2 buildings, 10,000 sqft total, mean density 0.006792 kW/sqft
        -> 10,000 x 0.006792 / 1000 = 0.06792 MW. Same arithmetic as Fairfax, Arlington and
        Prince William's own hand-checked cases, confirming the shared hook is reused."""
        df = pd.DataFrame([{'BUILDINGCLASS': 6, 'SHAPESTArea': 6000.0},
                           {'BUILDINGCLASS': 12, 'SHAPESTArea': 4000.0}])
        r = ch.estimate_chesapeake_ci_rooftop_solar(df)
        assert r.total_mw_mean_based == pytest.approx(0.06792, abs=1e-5)

    def test_no_combined_field_exists(self):
        df = pd.DataFrame([{'BUILDINGCLASS': 6, 'SHAPESTArea': 6000.0}])
        r = ch.estimate_chesapeake_ci_rooftop_solar(df)
        assert not hasattr(r, 'total_mw_combined')
        assert not hasattr(r, 'total_mwh_per_year_combined')


@real_data
class TestClassificationAgainstRealBuildingNames:
    """The closest thing this project has to ground truth on a building-class legend.

    Every other county's extract carried only a code, so 'is this legend applied correctly' could
    not be checked -- and that gap is exactly how Richmond's Structures subtype was misread.
    Chesapeake's NAME field allows a direct check.
    """

    def frame(self):
        return pd.read_csv(REAL_CSV, low_memory=False)

    def test_named_warehouses_are_NOT_reliably_classified_industrial(self):
        """FINDING, 2026-09-11 -- this test asserts the defect, not the ideal.

        Chesapeake's 636,190 sqft Amazon distribution centre (14.6 acres) is classified
        BUILDINGCLASS=6 Commercial, not 12 Industrial, despite the schema having an Industrial
        class. So the published coded domain tells us what the codes MEAN, not how consistently
        they were APPLIED.

        Consequences, in order of importance:
          - The C&I TOTAL is unaffected: Commercial and Industrial are both included, so the
            412.2 MW figure stands either way.
          - The PER-CLASS BREAKDOWN is not reliable. The 32.0% Industrial share understates real
            industrial presence, so the split must not be used for anything load-shape dependent
            -- an industrial roof and a retail roof have very different consumption profiles
            beneath them.
          - No other county's extract could have revealed this. Chesapeake is the only one with a
            NAME field. The same inconsistency may exist in Fairfax, Arlington and Prince William
            and be undetectable there.

        Written as an assertion rather than a comment so that if Chesapeake ever cleans its
        classification, this fails and prompts the breakdown caveat to be revisited.
        """
        df = self.frame()
        warehouses = df[df['NAME'].fillna('').str.contains('Warehouse|Distribution|Logistics',
                                                           case=False, regex=True)]
        assert len(warehouses) > 0, 'expected named warehouses to check against'
        misclassified = warehouses[warehouses['BUILDINGCLASS'] == 6]
        assert len(misclassified) > 0, (
            'named warehouses are now classified Industrial -- the classification may have been '
            'cleaned upstream. Revisit the per-class breakdown caveat in the module docstring.')
        assert misclassified['SHAPESTArea'].max() > 500_000, (
            'the specific case recorded was a 636,190 sqft Amazon distribution centre')

    def test_a_named_shopping_center_is_classified_commercial(self):
        df = self.frame()
        centers = df[df['NAME'].fillna('').str.contains('Shopping Center', case=False)]
        assert len(centers) > 0
        assert (centers['BUILDINGCLASS'] == 6).any()

    def test_named_care_and_living_facilities_are_classified_medical(self):
        df = self.frame()
        care = df[df['NAME'].fillna('').str.contains('Assisted Living|Adult Care',
                                                     case=False, regex=True)]
        assert len(care) > 0
        assert (care['BUILDINGCLASS'] == 3).any()


@real_data
class TestRealDataCrossCheck:
    """Locks the figures this project will cite. The per-class breakdown is asserted as well as
    the total, because Industrial and Apartment are included on this project's own judgment rather
    than established precedent and together account for 45.9% of the footprint -- a decision that
    size should stay visible, not sit inside an unexplained total."""

    def result(self):
        return ch.estimate_chesapeake_ci_rooftop_solar(pd.read_csv(REAL_CSV, low_memory=False))

    def test_headline_figures(self):
        r = self.result()
        assert r.n_buildings == 4_859
        assert r.total_footprint_sqft == pytest.approx(60_686_088, rel=1e-4)
        assert r.total_mw_mean_based == pytest.approx(412.2, abs=0.5)

    def test_extract_contains_only_the_five_included_classes(self):
        """The supplied file was pre-filtered in Chesapeake's own map interface. If a future
        export is broader, this fails and the defensive filter in build_ci_eligible_population
        is what keeps the result correct."""
        assert set(pd.read_csv(REAL_CSV, low_memory=False)['BUILDINGCLASS'].unique()) == {3, 6, 10, 12, 14}

    def test_the_two_judgment_calls_are_material(self):
        r = self.result()
        judgment = (r.buildings_by_class['Industrial']['share_of_footprint']
                    + r.buildings_by_class['Apartment']['share_of_footprint'])
        assert judgment == pytest.approx(0.459, abs=0.01), (
            'Industrial + Apartment share moved -- these are included on judgment rather than '
            'precedent, so a change here needs a documented decision, not a silent pass')

    def test_commercial_is_the_largest_single_class(self):
        r = self.result()
        assert max(r.buildings_by_class.items(),
                   key=lambda kv: kv[1]['footprint_sqft'])[0] == 'Commercial'
