"""
large_ci_curtailment_feature.py

Thin adapter migrating the existing, already-tested `large_ci_curtailment_derived.py` onto the
shared `DLCProgram` base class (`shared_base_classes/demand_side_feature.py`), per direct user
request 2026-08-26.

DELIBERATE DESIGN: `large_ci_curtailment_derived.py` itself is NOT modified -- it remains the
single source of truth for every constant and its own `avoided_generation_capacity_cost_comparison()`
function remains callable exactly as before. This file only ADDS a class that wraps those existing,
untouched values to conform to the shared interface -- a low-risk migration pattern that leaves
already-tested code paths completely intact.

A real methodological subtlety, checked directly before writing this adapter: the ORIGINAL entry #82
comparison (`avoided_generation_capacity_cost_comparison()`) compares the $36/kW/yr rate against the
RAW avoided-cost benchmark -- no utility-margin concept was ever applied. At the time this adapter
was first built, the shared `DLCProgram.avoided_cost_comparison()` method defaulted to a 5% margin,
so `utility_margin_pct=0` was passed explicitly to reproduce the original finding faithfully.

UPDATED 2026-08-26 (entry #112): the shared method's own default margin was changed to 0.0 (direct
user decision -- 5% was never a sourced figure). The explicit `utility_margin_pct=0` override below
became redundant at that point but was kept anyway for self-documentation.

UPDATED AGAIN 2026-08-27 (entry #116), direct user request: the margin value was further
consolidated into a single true global (`DEFAULT_UTILITY_MARGIN_PCT`, `shared_base_classes/
demand_side_feature.py`) -- given the user's own explicit goal was reducing the NUMBER OF PLACES
this value is hardcoded or restated, the explicit `utility_margin_pct=0` argument below was REMOVED
rather than kept for self-documentation, since keeping it would itself be exactly one more such
place. `avoided_cost_comparison_matching_original_methodology()` below now calls the shared method
with no margin argument at all, relying entirely on the single global default -- verified this still
reproduces the original 40.7%/70.9% figures exactly (see this file's own tests).
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'shared_base_classes'))
from demand_side_feature import DLCProgram  # noqa: E402

import large_ci_curtailment_derived as lci  # noqa: E402  (same-directory, untouched module)


class LargeCICurtailment(DLCProgram):
    """Adapter for Dominion's real, currently-active Non-Residential Curtailment Program (A.2
    extended). All underlying values are read live from `large_ci_curtailment_derived.py` --
    this class adds no new numbers, only the shared interface.
    """

    feature_name = "Large C&I Curtailment (A.2 extended)"

    def magnitude_per_unit(self) -> float:
        """Returns the program's own eligibility threshold (100 kW) -- the minimum enrolled
        curtailable capacity per participant. NOTE, stated directly rather than glossed over: this
        is structurally different from EV Charger Rewards' own `magnitude_per_unit()` (an average
        expected kW reduction per enrolled participant, derived bottom-up). This program is priced
        and eligibility-gated per kW directly, with no single 'typical participant' magnitude the
        way a residential program has -- ELIGIBILITY_THRESHOLD_KW is the most honest single number
        to return here, not an average, since no average enrolled-customer size has been sourced.
        """
        return lci.ELIGIBILITY_THRESHOLD_KW

    def current_compensation_usd(self) -> float:
        """Returns the real, currently-active $36/kW/yr rate -- read live from the existing module,
        not restated as a separate literal."""
        return lci.COMPENSATION_USD_PER_KW_YEAR

    def original_avoided_cost_finding(self) -> dict:
        """Direct passthrough to the existing, untouched, already-tested
        `avoided_generation_capacity_cost_comparison()` -- preserved and exposed as-is so the
        original entry #82 finding (and its own caveats, documented in that function's own
        docstring) remains directly accessible through this adapter, not just through the
        underlying module directly.
        """
        return lci.avoided_generation_capacity_cost_comparison()

    def avoided_cost_comparison_matching_original_methodology(
        self, avoided_capacity_usd_per_kw_yr: float
    ) -> dict:
        """Calls the SHARED base-class method with NO explicit margin argument, relying entirely on
        `DEFAULT_UTILITY_MARGIN_PCT` (the single global, `shared_base_classes/demand_side_
        feature.py`) -- which happens to reproduce the original entry #82 finding's own methodology
        (no margin concept was ever applied there) because that global is currently 0.0. See this
        file's own top-level docstring for the full history of how this method's own margin
        handling changed as the shared hierarchy evolved.
        """
        return self.avoided_cost_comparison(
            avoided_capacity_usd_per_kw_yr=avoided_capacity_usd_per_kw_yr,
            avoided_energy_usd_per_kw=0.0,
        )
