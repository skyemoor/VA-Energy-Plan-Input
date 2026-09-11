"""
population_extrapolation.py

OO class structure (ReferenceCounty, ExtrapolationTarget, PopulationExtrapolation) for
estimating C&I rooftop and parking-lot solar MW potential across Virginia counties/cities
beyond the four already directly drilled down (Loudoun, Fairfax, Arlington, Prince William),
by population-based extrapolation from those same four counties' own real, GIS-measured MW
figures -- direct user request, 2026-09-05, given schools are "a tiny percentage when
compared to C&I and Parking lots."

METHODOLOGY, and why it's a RANGE, not a single point (direct user-approved approach,
refined 2026-09-05 to exclude Arlington as well): Loudoun and Arlington are BOTH
excluded from the reference-rate basis -- Loudoun's own C&I MW/capita is a documented,
known outlier (data-center-driven commercial boom); Arlington is excluded for a
separate reason, per direct user observation -- it is genuinely, distinctively dense
(Virginia's smallest county by land area, a high-rise urban-core commercial character
along corridors like Rosslyn-Ballston and Crystal City) unlike any of the 28
extrapolation targets below, which are a mix of suburban/exurban counties and mid-sized
independent cities. Including either outlier in the reference basis would distort the
rate applied to every other jurisdiction. Fairfax and Prince William -- the two
remaining reference counties -- still produce a real range (not a single point), so
every extrapolated jurisdiction still gets a LOW/HIGH range (this basis's own min/max
MW-per-capita), not a single, falsely-precise number. NOTE: Arlington's own real,
GIS-measured C&I/parking figures remain part of this project's separate, already-
established four-directly-measured-counties total elsewhere -- excluding it here only
means it is no longer used to DERIVE the extrapolation rate for other jurisdictions.

DEDUPLICATION: the user's own two source population lists (top-20 counties, top-20
localities) overlap -- several "locality" list entries are Census-Designated Places or
incorporated towns already embedded inside a county already on the counties list (Dale
City/Woodbridge -> Prince William; Centreville/Reston/McLean -> Fairfax; Tuckahoe ->
Henrico; Leesburg -> Loudoun), verified directly against Virginia's actual jurisdictional
structure before building this module, not assumed. Only counties and INDEPENDENT CITIES
(which are genuinely separate from any county's own population under Virginia's
independent-city system) are included as extrapolation targets.

Run tests with: python3 -m pytest test_population_extrapolation.py -v
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ReferenceCounty:
    """One of the two reference counties (Loudoun and Arlington deliberately excluded --
    see module docstring) this project has real, GIS-measured C&I and parking-lot MW
    for, used to derive the per-capita rate range applied to every extrapolation target."""
    name: str
    population: int
    ci_mw: float
    parking_mw_low: float
    parking_mw_high: float

    @property
    def ci_kw_per_capita(self) -> float:
        return self.ci_mw * 1000 / self.population

    @property
    def parking_kw_per_capita_mid(self) -> float:
        return ((self.parking_mw_low + self.parking_mw_high) / 2) * 1000 / self.population


REFERENCE_COUNTIES = [
    ReferenceCounty("Fairfax", population=1_175_940, ci_mw=132.4, parking_mw_low=377.0, parking_mw_high=471.3),
    ReferenceCounty("Prince William", population=507_580, ci_mw=272.8, parking_mw_low=1734.7, parking_mw_high=2168.4),
]


def ci_kw_per_capita_range() -> tuple:
    """(low, high) C&I kW/capita across the three reference counties -- the basis applied
    to every extrapolation target below. NOT including Loudoun (see module docstring)."""
    rates = [c.ci_kw_per_capita for c in REFERENCE_COUNTIES]
    return (min(rates), max(rates))


def parking_kw_per_capita_range() -> tuple:
    """(low, high) parking-lot kW/capita across the three reference counties, using each
    reference county's own MID (average of its low/high) figure as the single point that
    feeds into this cross-county range -- avoids conflating within-county GIS-methodology
    uncertainty (low vs. high kW/space assumption) with across-county extrapolation
    uncertainty (which this range exists to capture)."""
    rates = [c.parking_kw_per_capita_mid for c in REFERENCE_COUNTIES]
    return (min(rates), max(rates))


@dataclass(frozen=True)
class ExtrapolationTarget:
    """One county or independent city being extrapolated to (not already one of the four
    directly-drilled-down counties). entity_type distinguishes "county" from
    "independent_city" for reporting purposes only (both are treated identically by the
    extrapolation math itself -- Virginia's independent cities are genuinely separate
    population bases, not a different kind of solar-potential question)."""
    name: str
    population: int
    entity_type: str  # "county" or "independent_city"

    def ci_mw_range(self) -> tuple:
        low_rate, high_rate = ci_kw_per_capita_range()
        return (low_rate * self.population / 1000, high_rate * self.population / 1000)

    def parking_mw_range(self) -> tuple:
        low_rate, high_rate = parking_kw_per_capita_range()
        return (low_rate * self.population / 1000, high_rate * self.population / 1000)


#: Deduplicated against the four already-covered counties AND against CDPs/incorporated
#: towns already embedded in a county elsewhere on this same list (see module docstring).
#: Populations exactly as the user supplied them (worldpopulationreview.com, both lists).
EXTRAPOLATION_TARGETS = [
    # Counties (from the top-20-counties list, excluding Fairfax/Loudoun/Prince William/
    # Arlington, already directly covered)
    ExtrapolationTarget("Chesterfield", 403_053, "county"),
    ExtrapolationTarget("Henrico", 345_526, "county"),
    ExtrapolationTarget("Stafford", 172_818, "county"),
    ExtrapolationTarget("Spotsylvania", 158_315, "county"),
    ExtrapolationTarget("Albemarle", 119_400, "county"),
    ExtrapolationTarget("Hanover", 117_293, "county"),
    ExtrapolationTarget("Frederick", 101_730, "county"),
    ExtrapolationTarget("Montgomery", 98_511, "county"),
    ExtrapolationTarget("Roanoke County", 96_927, "county"),  # distinct from Roanoke
                                                                 # (independent city), below
    ExtrapolationTarget("Rockingham", 90_313, "county"),
    ExtrapolationTarget("James City", 83_756, "county"),
    ExtrapolationTarget("Bedford", 83_651, "county"),
    ExtrapolationTarget("Augusta", 79_116, "county"),
    ExtrapolationTarget("Fauquier", 77_141, "county"),
    ExtrapolationTarget("York", 71_410, "county"),
    ExtrapolationTarget("Pittsylvania", 59_475, "county"),
    # Independent cities (from the top-20-localities list, excluding Arlington -- already
    # covered -- and excluding every CDP/incorporated town, per module docstring)
    ExtrapolationTarget("Virginia Beach", 452_271, "independent_city"),
    ExtrapolationTarget("Chesapeake", 256_610, "independent_city"),
    ExtrapolationTarget("Richmond", 239_227, "independent_city"),
    ExtrapolationTarget("Norfolk", 229_324, "independent_city"),
    ExtrapolationTarget("Newport News", 182_572, "independent_city"),
    ExtrapolationTarget("Alexandria", 160_717, "independent_city"),
    ExtrapolationTarget("Hampton", 137_345, "independent_city"),
    ExtrapolationTarget("Suffolk", 106_746, "independent_city"),
    ExtrapolationTarget("Roanoke", 98_807, "independent_city"),  # distinct from Roanoke
                                                                    # County, above
    ExtrapolationTarget("Portsmouth", 96_490, "independent_city"),
    ExtrapolationTarget("Lynchburg", 81_677, "independent_city"),
    ExtrapolationTarget("Harrisonburg", 50_612, "independent_city"),
]


def total_extrapolated_mw() -> dict:
    """Sums ci_mw_range()/parking_mw_range() across every target -- the low bound is the
    sum of every target's own low, the high bound is the sum of every target's own high
    (NOT summing low-vs-high inconsistently across targets), giving a genuine aggregate
    range, not an average-of-averages."""
    ci_low = sum(t.ci_mw_range()[0] for t in EXTRAPOLATION_TARGETS)
    ci_high = sum(t.ci_mw_range()[1] for t in EXTRAPOLATION_TARGETS)
    parking_low = sum(t.parking_mw_range()[0] for t in EXTRAPOLATION_TARGETS)
    parking_high = sum(t.parking_mw_range()[1] for t in EXTRAPOLATION_TARGETS)
    return {
        "num_targets": len(EXTRAPOLATION_TARGETS),
        "total_population": sum(t.population for t in EXTRAPOLATION_TARGETS),
        "ci_mw_low": ci_low, "ci_mw_high": ci_high,
        "parking_mw_low": parking_low, "parking_mw_high": parking_high,
    }


if __name__ == '__main__':
    print(f"Reference C&I kW/capita range: {ci_kw_per_capita_range()}")
    print(f"Reference parking kW/capita range: {parking_kw_per_capita_range()}")
    print(f"\n{len(EXTRAPOLATION_TARGETS)} extrapolation targets, total population "
          f"{sum(t.population for t in EXTRAPOLATION_TARGETS):,}")
    totals = total_extrapolated_mw()
    print(f"\nC&I MW range: {totals['ci_mw_low']:,.1f} - {totals['ci_mw_high']:,.1f}")
    print(f"Parking MW range: {totals['parking_mw_low']:,.1f} - {totals['parking_mw_high']:,.1f}")
