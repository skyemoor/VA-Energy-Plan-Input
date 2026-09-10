"""
demand_side_feature.py

Abstract base class hierarchy for every Scenario 3 demand-side/supply-side feature this project
models -- EE, DLC, WMA pathways, and price-based DR. Direct user request, 2026-08-26: proactively
eliminate ambiguity across features via shared, subclassable structure rather than independently
reimplementing the same shape of calculation per module (the exact problem found in entry #109's
own review -- large_ci's `avoided_generation_capacity_cost_comparison()` and dlc's
`avoided_cost_comparison()` answered the identical question with two inconsistent output shapes).

CORE DESIGN PRINCIPLE, direct user instruction: a subclass for which an inherited method does not
structurally apply should override it to explicitly raise NotImplementedError, not silently return
None or inherit a default. This project uses TWO deliberately different mechanisms for "no value,"
and confusing them is exactly the ambiguity this hierarchy exists to prevent:

  - `current_compensation_usd()` returns None  => the concept genuinely applies to this feature,
    but the actual rate is not yet publicly known (e.g. A.7 data center flexibility's own event
    frequency; Citizen EV V2G's own unpublished BYOD rate). A real, disclosed sourcing gap.

  - `current_compensation_usd()` raises NotImplementedError => the concept does not apply to this
    feature AT ALL, structurally, regardless of sourcing (e.g. A.5 Conservation Voltage Reduction --
    there is no customer-facing compensation mechanism to even ask about; it's a grid-side measure
    with no enrollment). Not a gap to fill later -- a question that doesn't apply to this feature.

No shared package structure exists elsewhere in this project (confirmed directly, entry #109 --
no __init__.py, no cross-module imports anywhere in lp_package/) -- this is the first module to
establish one, specifically because shared inheritance requires it. Consuming modules add this
directory to their own import path via sys.path.insert(), not a package-relative import.
"""

from abc import ABC, abstractmethod
from typing import Optional


class DemandSideFeature(ABC):
    """Abstract root of every Scenario 3 demand-side/supply-side feature. Every concrete feature
    (a specific Dominion program, a specific EE measure, a specific WMA pathway) must implement
    both abstract methods below -- Python's own `abc` machinery enforces this at instantiation
    time, not just by convention, so a subclass that forgets one cannot silently exist as a
    half-built object.
    """

    #: Short, human-readable name for this feature -- used in comparison output and error messages
    #: so a caller working with a list of mixed feature types can always identify which one they're
    #: looking at without inspecting the class name directly.
    feature_name: str = "UNNAMED FEATURE -- subclass must set this"

    @abstractmethod
    def magnitude_per_unit(self) -> float:
        """The core physical/energy magnitude this feature delivers per participant, per bus, per
        building, etc. -- units are feature-specific (kW, kWh, MWh/yr) and should be documented in
        the concrete subclass's own docstring, not standardized here, since forcing a single unit
        across genuinely different feature types would be a false consistency, not a real one.
        """
        raise NotImplementedError

    @abstractmethod
    def current_compensation_usd(self) -> Optional[float]:
        """The actual, current, real-world compensation for this feature, in whatever unit this
        feature's own docstring specifies (most commonly $/kW-yr or a flat $/yr).

        THREE deliberately distinct cases, not to be confused -- found and finalized while
        migrating real modules onto this hierarchy (a third case, beyond the two originally
        designed, was discovered during the school bus V2G migration and added here rather than
        forcing a dishonest fit into one of the first two):

        1. Return a float -- the concept applies and the rate is known.
        2. Return None -- the concept genuinely applies but the actual rate is not yet publicly
           known (a real, disclosed sourcing gap -- e.g. A.7 data center flexibility's own event
           frequency, Citizen EV V2G's own unpublished BYOD rate).
        3. Raise NotImplementedError -- EITHER because the concept does not apply to this feature
           at all, structurally (e.g. A.5 CVR -- no customer-facing compensation mechanism exists
           to even ask about), OR because compensation exists but is not monetary (check
           `compensation_is_monetary()` first in this case -- e.g. school bus V2G's own in-kind
           free battery replenishment; the raised message should point the caller to
           `compensation_description()` instead).

        Never silently substitute a default, a zero, or a value borrowed from a different feature.
        """
        raise NotImplementedError

    def compensation_is_monetary(self) -> bool:
        """Concrete, not abstract -- defaults to True so every subclass built before this method
        existed continues to work unmodified. Override to return False for features whose real
        compensation is not expressible as a dollar figure at all (e.g. an in-kind service) --
        `current_compensation_usd()` should then raise NotImplementedError, and
        `compensation_description()` should be overridden to describe the real mechanism instead.
        """
        return True

    def compensation_description(self) -> str:
        """Concrete, not abstract -- only meaningful for features where
        `compensation_is_monetary()` is False. Raises by default (mirroring
        `current_compensation_usd()`'s own default) so calling this on a feature with ordinary
        monetary compensation fails loudly rather than returning a placeholder string.
        """
        raise NotImplementedError(
            "This feature's own compensation is monetary -- use current_compensation_usd() "
            "instead of compensation_description()."
        )


class EEMeasure(DemandSideFeature):
    """Abstract base for permanent energy-efficiency measures (equipment/building-standard
    upgrades) -- e.g. heat pump efficiency improvements, PHIUS building envelope standards, heat
    pump water heaters. Distinct from DLCProgram: EE measures reduce energy use permanently and do
    not involve a per-event dispatch or a customer-facing participation payment the way DLC
    programs do, so no shared `avoided_cost_comparison()`-style method is added at this level --
    that comparison genuinely doesn't apply the same way here.
    """
    pass


# TRUE GLOBAL, single source of truth for every module that needs this value -- direct user
# request, 2026-08-27: previously duplicated (this file's own default parameter value, PLUS
# dlc_analysis/dlc_derived_assumptions.py's own separate module-level constant), requiring manual,
# error-prone synchronization whenever it changed (entry #112 had to update both together by hand).
# Now a single definition; every other location imports this rather than defining its own copy.
# Value (0.0) and full rationale: see avoided_cost_comparison()'s own docstring below.
DEFAULT_UTILITY_MARGIN_PCT = 0.0


class DLCProgram(DemandSideFeature):
    """Abstract base for incentive-based, direct-load-control-style demand response programs --
    e.g. EV Charger Rewards, Smart Thermostat Rewards, Large C&I Curtailment, Conservation Voltage
    Reduction. Adds ONE shared, CONCRETE method (not reimplemented per subclass) for comparing a
    program's actual current compensation against avoided-cost benchmarks -- the exact calculation
    that was independently, inconsistently reimplemented in `large_ci_curtailment_analysis` and
    `dlc_analysis` before this refactor (entry #109/#110).
    """

    def avoided_cost_comparison(
        self,
        avoided_capacity_usd_per_kw_yr: float,
        avoided_energy_usd_per_kw: float = 0.0,
        utility_margin_pct: float = None,
    ) -> dict:
        """Shared avoided-cost comparison, used identically by every DLCProgram subclass rather
        than reimplemented per program. Computes a properly-priced benchmark (avoided capacity +
        avoided energy/WMA, after a utility margin) and compares it against this feature's own
        `current_compensation_usd()`.

        `utility_margin_pct` defaults to `None`, which resolves to `DEFAULT_UTILITY_MARGIN_PCT`
        (module-level, below) at CALL time, not at function-definition time -- a deliberate `None`-
        sentinel pattern, not a direct embed of the global as the parameter's own default value.
        Python binds default argument values once, when a function is defined (at import), so
        writing `utility_margin_pct: float = DEFAULT_UTILITY_MARGIN_PCT` directly would freeze in
        whatever the global's value was at import time -- a later, deliberate change to the global
        wouldn't be picked up by already-defined calls. The sentinel pattern looks the global up
        fresh on every call instead, which is the correct behavior for a true, live, single-source
        global (direct user request, 2026-08-27 -- consolidate what were two independently-defined
        copies of this value into exactly one, given entry #112 already had to manually keep both
        in sync when this value changed once, a fragile, error-prone pattern going forward).
        `DEFAULT_UTILITY_MARGIN_PCT` was itself introduced 2026-08-26 (entry #112) at 0.0 -- an
        earlier version of this constant was 5.0, but that figure was never a sourced Dominion or
        SCC figure; it was the user's own illustrative assumption for a hypothetical question.
        Defaulting a shared, reusable class method to an unsourced number risked quietly treating
        it as an established methodological standard just because it was the code's own default.
        0.0 does not assert "the correct margin is zero" -- it reflects "no margin figure has been
        sourced yet," the more defensible default absent one. Callers with a specific, sourced
        margin should pass it explicitly.

        `avoided_energy_usd_per_kw` defaults to 0.0 so this method works cleanly for programs where
        only a capacity benchmark is being applied (e.g. large C&I's own original cross-check,
        entry #82, used capacity only) as well as programs where an energy/WMA component is also
        available (e.g. residential EV DLC, entry #109, which added the LMP-based energy figure).

        Calls `self.current_compensation_usd()` directly -- if that raises NotImplementedError
        (this feature has no compensation concept at all, e.g. CVR), that exception is allowed to
        propagate rather than being caught here: asking "how does this program's incentive compare
        to avoided cost" is itself a malformed question for a feature with no incentive, and
        silently catching that would hide the real problem rather than surface it.

        If `current_compensation_usd()` returns None (the concept applies, but the rate isn't
        published yet -- e.g. an unpublished BYOD rate), this method still returns the full
        avoided-cost benchmark calculation, with the current-rate-dependent fields explicitly set
        to None rather than raising -- there is real, useful information here (what the rate
        SHOULD be) even when the actual current rate isn't yet known.
        """
        if utility_margin_pct is None:
            utility_margin_pct = DEFAULT_UTILITY_MARGIN_PCT

        current_rate = self.current_compensation_usd()  # propagates NotImplementedError if raised

        properly_priced = (avoided_capacity_usd_per_kw_yr + avoided_energy_usd_per_kw) * (
            1 - utility_margin_pct / 100
        )

        result = {
            "feature_name": self.feature_name,
            "avoided_capacity_usd_per_kw_yr": avoided_capacity_usd_per_kw_yr,
            "avoided_energy_usd_per_kw": avoided_energy_usd_per_kw,
            "utility_margin_pct": utility_margin_pct,
            "properly_priced_usd_per_kw_yr": round(properly_priced, 2),
            "current_rate_usd_per_kw_yr": current_rate,
            "current_rate_as_pct_of_properly_priced": None,
            "properly_priced_as_multiple_of_current": None,
        }

        if current_rate is not None:
            result["current_rate_as_pct_of_properly_priced"] = round(
                current_rate / properly_priced * 100, 1
            )
            result["properly_priced_as_multiple_of_current"] = round(
                properly_priced / current_rate, 1
            )

        return result


class WMAPathway(DemandSideFeature):
    """Abstract base for wholesale-market-access pathways -- e.g. School Bus V2G, Citizen EV V2G,
    Municipal Transit Bus V2G. Kept minimal at this level deliberately: only one concrete
    subclass (SchoolBusV2G, once migrated) exists with a fully-built magnitude chain so far, so
    adding shared concrete methods now risks an abstraction that doesn't actually fit once a
    second and third subclass are built out. Grown organically as real subclasses migrate onto
    this base, not designed speculatively ahead of them.
    """
    pass


class PriceBasedDR(DemandSideFeature):
    """Abstract base for retail price-based demand response -- e.g. day-ahead/real-time pricing,
    ComEd-style. Deliberately separate from DLCProgram: no utility control of a device, no $/kW
    participation payment -- the customer simply faces a time-varying price and responds or
    doesn't. `current_compensation_usd()` does not map cleanly onto this mechanism type at all
    (there is no compensation payment, only a price signal) -- concrete subclasses should raise
    NotImplementedError from it, the same CVR-style pattern, since the concept of "compensation"
    genuinely does not apply to a pricing mechanism the way it does to a DLC program.
    """
    pass
