"""
cost_derivation.py

Class hierarchy for deriving costs from the assumptions surface: capital cost lookup, annualization
to a yearly figure, and the avoided-cost comparisons built on top.

WHY A HIERARCHY (2026-09-10, Software Engineering Standards Rule 1)

Second of three hierarchies replacing free-standing function modules. `peaker_capex.py` and
`large_ci_curtailment_derived.py` were separately performing the same two-step operation:

    look up a capital cost -> annualize it (x CRF, + fixed O&M) -> use the annual figure

That operation is also what the still-owed `CapitalCostMixin` needs, so putting it in one place
now avoids writing it a third time when capital costing moves into the scenario class hierarchy.

WHY ANNUALIZATION DESERVES ITS OWN CLASS

Conflating installed capital cost ($/kW, one-time) with annual cost ($/kW-yr) is not a
hypothetical error in this project -- it happened, it reached a headline finding, and it took an
external cross-check to catch:

    dlc_derived_assumptions.py used $1,175/kW and $713/kW -- INSTALLED CAPEX -- as annual avoided
    capacity cost. The right module, the wrong variable, as its own comment recorded ("matches
    AERODERIVATIVE_CAPEX_USD_PER_KW there"). The resulting benchmark was ~14x too high and produced
    a finding of "70-115x below properly priced" against the correctly-annualized module's ~41-71%.

    What settled it: PJM capacity has never cleared near $713/kW-yr. The 2025/26 record BRA was
    ~$270/MW-day = $98.5/kW-yr and the 2026/27 cap is $325/MW-day = $118.6/kW-yr. The annualized
    figures land inside that range; the capex figures sit ~6x above the highest price ever cleared.

`AnnualizedCost` therefore carries that cross-check as a method rather than leaving it to a
reviewer's memory, and every class here names its units explicitly.

THE HIERARCHY

    AnnualizedCost              capex -> annual, with a plausibility cross-check
      PeakerCost                simple-cycle installed cost by size tier, then annualized
      AvoidedCapacityCost       what a demand-side resource displaces, and how the current
                                incentive compares against it
"""
import assumptions


class AnnualizedCost:
    """Converts an installed capital cost to an annual figure: capital recovery plus fixed O&M.

    Deliberately explicit about units in every name. `capex_usd_per_kw` is one-time;
    `annual_usd_per_kw_yr` is per year; they differ by roughly a factor of fifteen and have been
    confused in this codebase before.
    """

    def __init__(self, capex_usd_per_kw, fixed_om_usd_per_kw_yr=0.0, capital_recovery_factor=None):
        if capex_usd_per_kw is None or capex_usd_per_kw < 0:
            raise ValueError(f"capex_usd_per_kw must be non-negative, got {capex_usd_per_kw!r}")
        self.capex_usd_per_kw = float(capex_usd_per_kw)
        self.fixed_om_usd_per_kw_yr = float(fixed_om_usd_per_kw_yr)
        self.capital_recovery_factor = (assumptions.CCGT_CRF if capital_recovery_factor is None
                                        else capital_recovery_factor)

    def annual_usd_per_kw_yr(self):
        return self.capex_usd_per_kw * self.capital_recovery_factor + self.fixed_om_usd_per_kw_yr

    def total_capital_dollars(self, capacity_mw):
        """One-time installed cost for `capacity_mw`. Named so it cannot be mistaken for annual."""
        return capacity_mw * 1000.0 * self.capex_usd_per_kw

    def total_annual_dollars(self, capacity_mw):
        return capacity_mw * 1000.0 * self.annual_usd_per_kw_yr()

    # Highest capacity price PJM has ever cleared, used as a plausibility ceiling rather than as a
    # cost input: 2026/27 BRA cap of $325/MW-day. A value above this is far likelier to be a units
    # error than a market signal.
    PJM_HIGHEST_CLEARED_CAPACITY_PRICE_USD_PER_KW_YR = 325.0 * 365 / 1000.0

    def units_plausibility_check(self):
        """Returns a warning string if the annual figure looks like an un-annualized capex value.

        Carried as a method rather than left to review, because this exact error reached a
        published finding once. Returns None when the value is plausible.
        """
        annual = self.annual_usd_per_kw_yr()
        if annual > self.PJM_HIGHEST_CLEARED_CAPACITY_PRICE_USD_PER_KW_YR:
            return (
                f"${annual:,.2f}/kW-yr exceeds ${self.PJM_HIGHEST_CLEARED_CAPACITY_PRICE_USD_PER_KW_YR:,.2f}"
                f"/kW-yr, the highest capacity price PJM has ever cleared. Check whether an "
                f"installed capital cost ($/kW, one-time) has been used where an annual cost "
                f"($/kW-yr) belongs -- that error has occurred in this codebase before.")
        return None


class PeakerCost(AnnualizedCost):
    """Simple-cycle combustion turbine cost, selected by unit size and cost case.

    Used by the VCEA scenarios (Build to Zero, 2045 Gas Exception, Distributed Build), where gas
    is a residual gap-filler and cycling wear makes simple-cycle correct. The Statutory Floor uses
    combined-cycle instead -- its gas runs at 42-58% capacity factor, online 82-99% of hours. See
    docs/methodology/Gas_Technology_Selection_By_Scenario.md.

    NOTE the size-cost inversion is real and preserved: smaller units cost MORE per kW. A caller
    sizing a large requirement should prefer fewer, larger units, which is the opposite of the
    usual intuition about equipment scale.
    """

    def __init__(self, unit_mw, case='central', fuel_type='f_class',
                 dual_fuel=False, fast_track=False):
        if unit_mw is None or unit_mw <= 0:
            raise ValueError(f"unit_mw must be positive, got {unit_mw!r}")
        if case not in ('low', 'central', 'high'):
            raise ValueError(
                f"case must be 'low', 'central' or 'high', got {case!r}. These correspond to the "
                "sourced range endpoints, not a fitted distribution.")
        self.unit_mw = float(unit_mw)
        self.case = case
        self.fuel_type = fuel_type
        self.dual_fuel = dual_fuel
        self.fast_track = fast_track

        rate = assumptions.PEAKER_CAPEX_KW_BY_TIER[self.size_tier()][case]
        if dual_fuel:
            rate += assumptions.PEAKER_DUAL_FUEL_ADDER_KW
        if fast_track:
            rate *= (1.0 + assumptions.PEAKER_FAST_TRACK_PREMIUM_FRACTION)
        super().__init__(rate, assumptions.PEAKER_FOM_USD_PER_KW_YR.get(fuel_type, 0.0))

    def size_tier(self):
        if self.unit_mw <= assumptions.PEAKER_SMALL_TIER_MAX_MW:
            return 'small'
        if self.unit_mw <= assumptions.PEAKER_MEDIUM_TIER_MAX_MW:
            return 'medium'
        return 'large'

    def units_required(self, total_mw):
        """Fractional on purpose -- rounding up to whole units is a procurement decision belonging
        to the caller, and rounding here would move the cost without the caller knowing which way.
        """
        return total_mw / self.unit_mw


class AvoidedCapacityCost:
    """What a demand-side resource displaces, and how its current incentive compares.

    Records Internal Debugging Log entry #82: Dominion's Non-Residential Curtailment Program pays
    $36/kW-yr against the annualized cost of the peaker capacity it avoids.

    The comparison is live -- change a peaker cost in assumptions.py and this moves with it. An
    earlier version hardcoded the capital costs entry #82 was originally computed from, to keep a
    cited figure reproducible. That was backwards: entry #82's claim is about what a peaker costs
    to build NOW against what Dominion pays NOW, so freezing the input to protect the output
    inverted the dependency -- and a hardcoded historical value violates Rule 8 whatever it is
    named. The historical result lives in registers/Provenance_Register.xlsx as superseded, which
    is where a historical figure belongs.

    Scope: generation capacity ONLY. Avoided transmission and distribution are excluded, so these
    percentages are an UPPER bound on the share of true total avoided cost the current rate
    captures.
    """

    BENCHMARK_UNITS = {'aeroderivative': 105.0, 'f_class': 237.0}

    def __init__(self, current_incentive_usd_per_kw_yr=None, case='central'):
        self.current_incentive_usd_per_kw_yr = (
            assumptions.LARGE_CI_COMPENSATION_USD_PER_KW_YEAR
            if current_incentive_usd_per_kw_yr is None else current_incentive_usd_per_kw_yr)
        self.case = case

    def benchmark(self, fuel_type):
        return PeakerCost(self.BENCHMARK_UNITS[fuel_type], self.case, fuel_type)

    def comparison(self):
        out = {'compensation_usd_per_kw_yr': self.current_incentive_usd_per_kw_yr,
               'cost_case': self.case, 'td_included': False}
        for fuel_type in self.BENCHMARK_UNITS:
            cost = self.benchmark(fuel_type)
            annual = cost.annual_usd_per_kw_yr()
            key = 'fclass' if fuel_type == 'f_class' else fuel_type
            out[f'{key}_capex_usd_per_kw'] = cost.capex_usd_per_kw
            out[f'{key}_avoided_cost_usd_per_kw_yr'] = round(annual, 2)
            out[f'{key}_incentive_as_pct_of_avoided_cost'] = round(
                self.current_incentive_usd_per_kw_yr / annual * 100, 1)
        out['scope_note'] = (
            'Generation capacity only -- avoided transmission and distribution deliberately '
            'excluded, so these percentages are an upper bound on the share of true total avoided '
            'cost the current rate captures.')
        return out
