"""
capacity_accreditation.py

Class hierarchy for capacity accreditation: how much firm capacity a resource is credited with at
the hours that actually bind.

WHY A HIERARCHY (2026-09-10, Software Engineering Standards Rule 1)

This replaces two free-standing function modules, `storage_accreditation.py` and
`scenario2_reserve_margin.py`. Rule 1 requires that new code with no existing OO structure have one
conceptualized rather than being written as loose functions, and both modules were doing the same
three things with different spellings:

    identify the peak net-demand hours -> credit resources at those hours -> compare standards

They even both defined the peak-hour finder, one named `peak_net_demand_hours` and the other
`peak_net_demand_hour`, differing only in whether they returned one index or several. That is the
duplication a shared base exists to prevent, and it was live in the codebase.

THE HIERARCHY

    PeakHourAnalysis              identifies binding hours; shared by everything below
      StorageCapacityCredit       own-data credit from an observed dispatch
      ReserveMarginRequirement    capacity a scenario must carry to meet PJM's IRM

THE FINDING THIS HIERARCHY EXISTS TO PRESERVE (2026-09-10)

Own-data accreditation must be computed from a NO-FORESIGHT dispatch. Measured on the same 2045
fleet, same weather, same peak-hour definition:

    LP dispatch (perfect foresight)          100.0%
    Heuristic dispatch (no foresight)         31.8%

and the LP series rises with penetration (40.3% at 27% penetration to 100.0% at 228%) when capacity
credit should FALL -- PJM's own fixed-tilt solar rating fell from 33% to 7-8% for exactly that
reason. The cause is that an optimizer knowing which hours are peak pre-positions storage to be
full for them, so measuring availability there measures the optimizer's foresight rather than the
fleet's capability. `StorageCapacityCredit` therefore requires callers to state which kind of
dispatch they are passing, rather than accepting an array and hoping.
"""
import numpy as np

import assumptions
import lp_model as lp


class PeakHourAnalysis:
    """Identifies the hours at which capacity binds: highest net demand after all
    non-dispatchable clean generation.

    One definition, shared. Previously spelled two different ways in two modules.
    """

    def __init__(self, demand, nuclear, exist_solar, wind_cf=None, solar_cf=None,
                 wind_generation_mw=None, solar_generation_mw=None):
        """Accepts generation either as capacity factors (which are scaled by CVOW_MW internally,
        matching ReserveMarginMixin.find_hour_of_maximum_net_demand) or as absolute MW.

        Rule 5: supplying both forms for the same resource raises, rather than one silently
        winning -- that ambiguity is how a build-size artifact gets into a capacity credit.
        """
        if wind_cf is not None and wind_generation_mw is not None:
            raise ValueError("supply wind as EITHER wind_cf OR wind_generation_mw, not both")
        if solar_cf is not None and solar_generation_mw is not None:
            raise ValueError("supply solar as EITHER solar_cf OR solar_generation_mw, not both")
        self.demand = np.asarray(demand, dtype=float)
        self.nuclear = np.asarray(nuclear, dtype=float)
        self.exist_solar = np.asarray(exist_solar, dtype=float)
        self.wind_mw = (lp.CVOW_MW * np.asarray(wind_cf, dtype=float)
                        if wind_cf is not None else np.asarray(wind_generation_mw, dtype=float))
        self.solar_mw = (np.zeros_like(self.demand) if solar_cf is None and solar_generation_mw is None
                         else np.asarray(solar_generation_mw if solar_generation_mw is not None
                                         else solar_cf, dtype=float))

    def net_demand(self):
        return self.demand - self.nuclear - self.exist_solar - self.wind_mw - self.solar_mw

    def peak_hour(self):
        """Single binding hour -- the reserve-margin constraint's own convention."""
        return int(np.argmax(self.net_demand()))

    def peak_hours(self, count=None):
        """The `count` highest net-demand hours, per Appendix A.13 Algorithm 1 step 2."""
        count = assumptions.CAPACITY_CREDIT_PEAK_HOURS_COUNT if count is None else count
        if count < 1:
            raise ValueError(f"count must be at least 1, got {count}")
        return np.argsort(self.net_demand())[-count:][::-1]


class StorageCapacityCredit(PeakHourAnalysis):
    """Own-data storage capacity credit, measured from an observed dispatch.

    The credit is the mean, across the peak net-demand hours, of what the fleet could actually have
    delivered divided by its power rating -- so a fleet that is empty when it matters accredits
    near zero regardless of nameplate.
    """

    def __init__(self, *args, state_of_charge_mwh, power_rating_mw,
                 dispatch_has_foresight, energy_capacity_mwh=None,
                 depth_of_discharge_floor_fraction=None, **kwargs):
        """`dispatch_has_foresight` is REQUIRED and has no default.

        A caller must state whether the dispatch being measured knew when the peak hours would
        arrive. Passing an LP's own dispatch produces the least conservative possible answer -- the
        opposite of what own-data accreditation is usually reached for -- and the difference is
        threefold, not marginal. Making it a required argument means the question cannot be
        skipped; making it a keyword means it cannot be answered by accident through positional
        order.
        """
        super().__init__(*args, **kwargs)
        if power_rating_mw is None or power_rating_mw <= 0:
            raise ValueError(
                "power_rating_mw must be positive -- a capacity credit for a fleet with no power "
                "rating has no meaning. If this class was not built, omit it from the "
                "accreditation rather than passing zero.")
        self.state_of_charge_mwh = np.asarray(state_of_charge_mwh, dtype=float)
        self.power_rating_mw = float(power_rating_mw)
        self.dispatch_has_foresight = bool(dispatch_has_foresight)
        self.energy_capacity_mwh = (float(energy_capacity_mwh) if energy_capacity_mwh is not None
                                    else float(self.state_of_charge_mwh.max()))
        self.depth_of_discharge_floor_fraction = (
            assumptions.NA_DOD_FLOOR if depth_of_discharge_floor_fraction is None
            else depth_of_discharge_floor_fraction)

    def credit(self, peak_hours_count=None):
        unusable = self.depth_of_discharge_floor_fraction * self.energy_capacity_mwh
        idx = self.peak_hours(peak_hours_count)
        usable = np.maximum(0.0, self.state_of_charge_mwh[idx] - unusable)
        deliverable = np.minimum(self.power_rating_mw, usable)
        return float(np.mean(deliverable) / self.power_rating_mw)

    def accredited_mw(self, peak_hours_count=None):
        return self.power_rating_mw * self.credit(peak_hours_count)

    def penetration_ratio(self):
        return self.power_rating_mw / float(self.demand.max())

    def cross_validated(self, published_credit, resource_label='', peak_hours_count=None):
        """Appendix A.13's cross-validation step: adopt the LOWER of own-data and published, and
        disclose the divergence rather than silently choosing the more favourable.

        This rule is what prevented the foresight artifact's 100% figure from being adopted.
        Returns a dict rather than a bare number so the divergence travels with the value.
        """
        own = self.credit(peak_hours_count)
        return {
            'resource': resource_label,
            'own_data_credit': own,
            'published_credit': published_credit,
            'adopted_credit': min(own, published_credit),
            'source_adopted': 'own_data' if own <= published_credit else 'published',
            'divergence': published_credit - own,
            'dispatch_has_foresight': self.dispatch_has_foresight,
            'foresight_warning': (
                'Own-data credit computed from a dispatch WITH foresight -- this is an optimistic '
                'bound, not a conservative estimate. See this module docstring.'
                if self.dispatch_has_foresight else None),
        }


class ReserveMarginRequirement(PeakHourAnalysis):
    """Capacity a scenario must carry at its peak net-demand hour to satisfy PJM's IRM.

    Exists because the Statutory Floor scenario was never held to the same standard as the others:
    Scenario 1 and Scenario 3 compose ReserveMarginMixin, Scenario 2 composes nothing, and
    Appendix C.2 sizes its gas to the worst hourly gap while crediting storage at ZERO. Those are
    conservative in opposite directions and are not comparable -- which is the defect, rather than
    either rule being indefensible on its own.
    """

    def __init__(self, *args, firm_capacity_mw=0.0,
                 installed_reserve_margin=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.firm_capacity_mw = float(firm_capacity_mw)
        self.installed_reserve_margin = (assumptions.INSTALLED_RESERVE_MARGIN
                                         if installed_reserve_margin is None
                                         else installed_reserve_margin)

    def required_capacity_mw(self):
        return (1.0 + self.installed_reserve_margin) * float(self.demand[self.peak_hour()])

    def credited_at_peak_mw(self):
        t = self.peak_hour()
        return float(self.nuclear[t] + self.wind_mw[t] + self.exist_solar[t] + self.solar_mw[t]
                     + self.firm_capacity_mw)

    def dispatchable_shortfall_mw(self):
        """Floored at zero -- a fleet already meeting the margin needs no more, and a negative
        requirement has no physical meaning (Rule 11)."""
        return max(0.0, self.required_capacity_mw() - self.credited_at_peak_mw())

    def zero_credit_shortfall_mw(self):
        """Appendix C.2's own rule: worst hourly gap, firm capacity credited at ZERO, no margin.

        Retained alongside the reserve-margin figure rather than replaced, because the two are
        conservative in different directions and reporting either alone hides that.
        """
        t = self.peak_hour()
        clean = float(self.nuclear[t] + self.wind_mw[t] + self.exist_solar[t] + self.solar_mw[t])
        return max(0.0, float(self.demand[t]) - clean)

    def compare_standards(self):
        """Both figures side by side. The intended reporting entry point."""
        t = self.peak_hour()
        reserve = self.dispatchable_shortfall_mw()
        zero_credit = self.zero_credit_shortfall_mw()
        return {
            'peak_net_demand_hour': t,
            'demand_at_peak_mw': float(self.demand[t]),
            'clean_generation_at_peak_mw': self.credited_at_peak_mw() - self.firm_capacity_mw,
            'firm_capacity_credited_mw': self.firm_capacity_mw,
            'appendix_c2_gas_mw_zero_storage_credit_no_margin': zero_credit,
            'reserve_margin_gas_mw_storage_credited': reserve,
            'difference_mw': reserve - zero_credit,
            'installed_reserve_margin': self.installed_reserve_margin,
        }
