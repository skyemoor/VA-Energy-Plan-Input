"""
rooftop_solar_estimation_base.py

Shared base class for C&I rooftop solar MW/MWh estimation, factored out after direct user request
following the same review that fixed fairfax_ci_rooftop_solar_estimate.py's statistically
indefensible "combined" (mean+median averaged) total -- the identical issue existed in
loudoun_ci_rooftop_solar_estimate.py too, since Fairfax's module was built by mirroring Loudoun's
pattern in the first place.

WHY THIS BELONGS IN A SHARED BASE, PER RULE 1 ("if every scenario needs it and the underlying
formula is the same, differing only in scenario-specific inputs, it belongs in a shared method or
mixin -- not reimplemented per scenario"): comparing the two counties' own estimate functions
directly --

  Loudoun:  total_mw_mean = unique_buildings * kw_stats.mean_kw / 1000
            total_mw_median = unique_buildings * kw_stats.median_kw / 1000
  Fairfax:  total_mw_mean = total_footprint_sqft * density_stats.mean_kw_per_sqft / 1000
            total_mw_median = total_footprint_sqft * density_stats.median_kw_per_sqft / 1000

-- both counties compute a mean-based total and a median-based total (deliberately NOT averaged
into a single "combined" figure -- see RooftopSolarTotals' own docstring for why), then convert
each to annual MWh via the identical capacity-factor formula. The ONLY genuine difference is what
the per-unit mean/median gets multiplied by: a building COUNT for Loudoun (whose source data was
business records with no area field), a total footprint AREA for Fairfax (whose source data
already had real per-building area). That one difference is the abstract hook
(scale_per_unit_value_to_total_mw); everything else is shared, identical logic that lives here
once, not reimplemented in each county's own module.

Run tests with: python3 -m pytest test_rooftop_solar_estimation_base.py -v
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from statistics import mean, median
from typing import List


@dataclass
class DescriptiveStats:
    """A genuinely generic descriptive-stats container (n/mean/median/
    min/max over a list of floats) -- the actual shared computation
    beneath both counties' own, semantically-named stats dataclasses
    (loudoun_ci_rooftop_solar_estimate.PerBuildingKwStats,
    fairfax_ci_rooftop_solar_estimate.PerSqftKwDensityStats). Those two
    stay as separate, properly-named types rather than being collapsed
    into this one directly -- their field names carry real meaning
    ("mean_kw" vs "mean_kw_per_sqft"), and reusing one shared type across
    genuinely different units would reintroduce the exact clarity problem
    this module's own design otherwise avoids -- but both are built by
    calling compute_descriptive_stats() internally (see each module),
    so the computation itself is genuinely shared, not duplicated."""
    n: int
    mean: float
    median: float
    min: float
    max: float


def compute_descriptive_stats(values: List[float]) -> DescriptiveStats:
    return DescriptiveStats(n=len(values), mean=mean(values), median=median(values),
                             min=min(values), max=max(values))


@dataclass
class RooftopSolarTotals:
    """Shared result shape: mean-based and median-based MW+MWh totals.

    Deliberately has NO 'combined' field. Direct user challenge on
    fairfax_ci_rooftop_solar_estimate.py's own now-removed
    total_mw_combined property established why: when scaling a per-unit
    rate across a KNOWN, FIXED total (a building count or a total
    footprint area) to estimate a sum, the sample MEAN is the correct,
    unbiased estimator of that sum -- the sample MEDIAN is a BIASED
    estimator of the same sum whenever the underlying sample is skewed
    (both counties' own NVRC-derived samples are: Loudoun's raw kW
    values span ~23x min-to-max, Fairfax's derived kW/sqft ratios span
    ~2.5x), because median-based scaling implicitly assumes a symmetry
    the data doesn't have. Averaging a correct estimator with a biased
    one produces a third number with no clear interpretation -- not a
    more conservative or more robust estimate, just an undefined one.
    The mean-based total is the primary, recommended figure for this
    reason; the median-based total is retained as an explicit, separately
    -labeled sensitivity check (how much the estimate would shift if the
    sample's mean were being pulled upward by its largest point), not
    blended into a headline number."""
    total_mw_mean_based: float
    total_mw_median_based: float
    total_mwh_per_year_mean_based: float
    total_mwh_per_year_median_based: float
    capacity_factor_used: float


class BaseRooftopSolarEstimator(ABC):
    """Base class for C&I rooftop solar MW/MWh estimation across
    counties. Shares: the mean-based/median-based totals + MWh
    conversion logic (via compute_totals(), defined once here, not
    reimplemented per county). Scenario-specific: how a per-unit
    mean/median value gets scaled up to a county-wide total MW figure
    (via the abstract scale_per_unit_value_to_total_mw hook) -- Loudoun
    scales a flat per-building kW by a building count; Fairfax scales a
    kW/sqft density by a total footprint area. Each county's own
    estimator class implements only this hook, following the same
    pattern this project's get_existing_new_mw()-style base/mixin
    scenario classes already establish elsewhere: the base class defines
    the shared logic and calls an abstract hook; each scenario class
    implements only the hook."""

    @abstractmethod
    def scale_per_unit_value_to_total_mw(self, per_unit_value: float) -> float:
        """Given a per-unit value (e.g. mean or median kW per building,
        or mean or median kW per sq ft), returns the county-wide total
        MW. Each scenario's own scale factor (building count, total
        footprint sq ft, etc.) lives here in the subclass, not in this
        shared base -- there is no sensible universal default, so this
        raises unconditionally rather than silently falling back to some
        other scenario's own scale factor if a subclass forgets to
        implement it."""
        raise NotImplementedError

    def compute_totals(self, mean_per_unit: float, median_per_unit: float,
                        capacity_factor: float, hours_per_year: float) -> RooftopSolarTotals:
        """Shared logic: scales both the mean and median per-unit values
        to their own totals (via this instance's own
        scale_per_unit_value_to_total_mw hook), then converts each to
        MWh via the identical capacity-factor formula -- the same for
        every county, not reimplemented per scenario."""
        total_mw_mean = self.scale_per_unit_value_to_total_mw(mean_per_unit)
        total_mw_median = self.scale_per_unit_value_to_total_mw(median_per_unit)
        return RooftopSolarTotals(
            total_mw_mean_based=total_mw_mean,
            total_mw_median_based=total_mw_median,
            total_mwh_per_year_mean_based=total_mw_mean * hours_per_year * capacity_factor,
            total_mwh_per_year_median_based=total_mw_median * hours_per_year * capacity_factor,
            capacity_factor_used=capacity_factor,
        )
