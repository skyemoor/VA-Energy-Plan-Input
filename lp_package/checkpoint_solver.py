"""
checkpoint_solver.py

OOP wrapper layer for this project's scenario checkpoint solves.

DESIGN PRINCIPLE, stated explicitly: this module wraps and orchestrates
lp_model.py's build_problem()/solve_problem() and driver.py's
run_solve()/converge_frac()/add_reserve_margin_constraint() -- it does
NOT reimplement any of their numerical logic. Those functions carry
this project's own, extensively-debugged history (LP degeneracy fixes,
the BUILD_SCALE fix, the DoD-direction correction, and more, all
recorded in Internal_Debugging_Log.md). The class hierarchy below exists
to reduce duplication across the many solve_20XX_*.py scripts and give
each scenario's own distinct logic a clear place to live via
inheritance -- not to re-verify correctness from scratch. Any class
method that touches the actual LP should be a thin call into
lp_model/driver, not a parallel implementation.

Verified equivalent to the pre-refactor manual-replication scripts
before being adopted as the standing path forward -- see
Internal_Debugging_Log.md #25 for the initial numerical equivalence
check, and #26 for a second, necessary correction found immediately
after: that first check confirmed Scenario1Solver matches run_solve()/
converge_frac() exactly, but did not catch that run_solve() itself had
always lacked the SLCR RPS-constraint splice every manual-replication
"final" script applies. Confirmed genuinely necessary (not stale or
superseded) via direct testing at the 2035 checkpoint, then folded into
run_solve() as a default-on step (driver.apply_slcr_constraint()) --
this class hierarchy inherits that fix automatically, with no changes
needed here, since it calls run_solve()/converge_frac() rather than
reimplementing their own internals.
"""
import math

import numpy as np

import assumptions
import lp_model as lp
import driver as drv



_DIST_CF_CACHE = {}


def _distributed_design_year_cf():
    """Hourly distributed capacity-factor profile for the design year, cached.

    Five sites averaged at 45 degrees fixed, on the same April-March hydro-year boundaries as every
    other weather input -- so the distributed and utility profiles describe the same hours, and the
    correlation between them is meaningful.
    """
    if 'design' not in _DIST_CF_CACHE:
        import distributed_solar_profile as dsp
        _DIST_CF_CACHE['design'] = dsp.hydro_year_profile(2016)
    return _DIST_CF_CACHE['design']

class CheckpointSolver:
    """Base class for a single checkpoint's own year-solve (Appendix P.1's
    "checkpoint solve" -- optimizer decides both build and dispatch).
    Handles what every scenario shares: building the problem, applying
    the gas capacity cap, and verifying the result against this project's
    own standing requirements (Appendix P.2 #11/#13/#14) before it can be
    treated as final."""

    def new_gas_technology(self):
        """Which technology new gas capacity is built as: 'simple_cycle' or 'combined_cycle'.

        A TEMPLATE METHOD WITH NO DEFAULT, for the same reason gas_retirement_schedule has none:
        the choice is a scenario property, and silent inheritance is the failure mode.

        THE STANDING RULE IS CONDITIONAL, NOT ABSOLUTE. New gas is simple-cycle for Scenarios 1, 1B,
        3, 3B and 3C, on the stated rationale that "most anticipated shortfalls are likely
        short-duration (a few hours at a time) gap-filling needs" -- and the rule's own text carves
        out Scenario 2, "which retains its own established CCGT-based new-build methodology".

        THAT RATIONALE IS A PREDICTION AND CAN BE WRONG. Scenario 2 falsified it: its 2045 shortfall
        is 30.05 TWh across 5,671 hours at a 33.4% capacity factor, and the existing simple-cycle
        fleet runs at a 100% capacity factor until combined-cycle capacity is added. Whether the
        other scenarios' shortfalls are genuinely peaky is an EMPIRICAL question, and
        shortfall_duty_profile() measures it rather than assuming.

        So this method records a declaration; the diagnostic records whether the evidence supports
        it. A declaration that the evidence contradicts is visible rather than inferred.

        ONLY SCENARIO 2'S DECLARATION IS CONFIRMED BY MEASUREMENT. The other three carry the
        standing rule's default and are marked DRAFT: they were declared on 2026-09-14 alongside
        Scenario 2's, but their shortfall profiles have not been run since the carve-out, Bath and
        retirement-schedule corrections, so no evidence yet supports or contradicts them. They are
        not to be treated as settled.
        """
        raise NotImplementedError(
            f'{type(self).__name__} must declare how new gas capacity is built. '
            "Return 'simple_cycle' for the standing rule's three reference units, or "
            "'combined_cycle' for Scenario 2's own methodology. The choice follows the SHAPE of "
            'the shortfall, which shortfall_duty_profile() measures -- it is not a default.')

    def shortfall_duty_profile(self, unserved_mwh, ct_fleet_mwh=None, ct_fleet_mw=None):
        """Does this scenario's shortfall look like peaking duty or baseload duty?

        The standing simple-cycle rule rests on shortfalls being "short-duration (a few hours at a
        time) gap-filling needs". This measures whether that holds:

            median_run_hours    below a combined-cycle minimum uptime means peaking duty
            shortfall_hours     what share of the year the system is short
            ct_capacity_factor  an existing simple-cycle fleet running far above its economic duty
                                is serving load that wants combined-cycle plant

        Returns the measurements, NOT a recommendation. Three sizing criteria built on this
        project's 28.1% crossover during 2026-09-14 turned out to have no authority behind them --
        the crossover is a NEW-BUILD decision and existing plant has sunk capital. So this reports
        what is there and leaves the judgement where it belongs.
        """
        import numpy as np
        import gas_capacity_fit as gcf

        u = np.asarray(unserved_mwh, dtype=float)
        flag = u > 1.0
        edges = np.diff(np.concatenate(([0], flag.astype(np.int8), [0])))
        runs = np.flatnonzero(edges == -1) - np.flatnonzero(edges == 1)
        hours = len(u)
        out = {
            'shortfall_hours': int(flag.sum()),
            'shortfall_share_of_year': float(flag.sum()) / hours if hours else 0.0,
            'median_run_hours': float(np.median(runs)) if len(runs) else 0.0,
            'longest_run_hours': int(runs.max()) if len(runs) else 0,
            'event_count': int(len(runs)),
            'ccgt_min_uptime_hr': gcf.CCGT_MIN_UPTIME_HR,
            # NOT A CONCLUSION ON ITS OWN, and Scenario 2 is why. Its 2045 shortfall has a median
            # run of 3 hours at every tranche, which reads as peaking duty -- but that flat profile
            # is an ARTIFACT of the existing simple-cycle fleet filling the bottom of the gap,
            # leaving only its ragged surface exposed. Remove that fleet from the stack and the
            # profile becomes a staircase, 12-16 hours at the base: genuine combined-cycle duty.
            #
            # So a short median run means "new plant must serve short blocks GIVEN THE FLEET AS IT
            # IS", not "the system's duty is peaking". The two diverge whenever the existing fleet
            # is saturated, which ct_capacity_factor detects.
            'median_run_suggests_peaking': bool(
                len(runs) and np.median(runs) < gcf.CCGT_MIN_UPTIME_HR),
        }
        if ct_fleet_mwh is not None and ct_fleet_mw:
            ct_cf = float(ct_fleet_mwh) / (ct_fleet_mw * hours)
            out['ct_capacity_factor'] = ct_cf
            # A simple-cycle fleet near saturation is serving load that wants combined-cycle plant,
            # and it is also MASKING the true duty shape above -- so a short median run cannot be
            # read at face value while this is high. No threshold is applied: three sizing criteria
            # built on this project's 28.1% crossover during 2026-09-14 proved to have no authority,
            # the crossover being a new-build decision that does not transfer to plant with sunk
            # capital. The two measurements are reported together and the judgement stays outside.
            out['existing_ct_saturated'] = ct_cf > 0.90
            out['median_run_may_be_masked'] = bool(
                out['median_run_suggests_peaking'] and ct_cf > 0.90)
        return out

    def gas_retirement_schedule(self):
        """Which retirement world this scenario is in: 'A' physical, 'B' VCEA-driven.

        A TEMPLATE METHOD WITH NO DEFAULT, deliberately. The two schedules differ by 5,531 MW at
        2045, and which applies depends on whether the scenario gives gas plants a market -- a
        scenario property, not a fact about the fleet.

        Scenario 2 inherited Schedule B silently for its entire life and was modelling a
        retirement premised on a scenario it was not running: Schedule B has Brunswick County,
        Potomac Energy Center and Greensville retiring FOR LACK OF MARKET, while Scenario 2 runs
        gas at a 68% capacity factor supplying 132 TWh. An inherited default is what allowed that,
        so there is none.
        """
        raise NotImplementedError(
            f'{type(self).__name__} must declare its gas retirement schedule. '
            "Return 'A' for physical retirement on plant age, market-indifferent, or 'B' for "
            'VCEA-driven retirement where plants close for lack of market in a clean grid.')

    def gas_baseline_mw(self, year=None):
        """Existing gas capacity in `year` under this scenario's own declared schedule."""
        return drv.gas_baseline_mw(self.year if year is None else year,
                                   self.gas_retirement_schedule())

    def __init__(self, year, demand, exist_solar, solar_cf, wind_cf, nuclear,
                 sourced_annual_total_gwh=None):
        self.year = year
        self.demand = demand
        self.exist_solar = exist_solar
        self.solar_cf = solar_cf
        self.wind_cf = wind_cf
        self.nuclear = nuclear
        # Appendix P #14's own standing requirement: the caller should supply the current,
        # authoritative annual total for this input's own sourced table, so it can be checked
        # directly rather than assumed -- the exact gap that produced the demand-file finding
        # this class hierarchy was built in response to.
        self.sourced_annual_total_gwh = sourced_annual_total_gwh
        self.result = None  # populated by solve()

    def _carry_convergence_verdict(self, converge_result):
        """Copies converge_frac()'s verdict onto the result this solver actually returns.

        WHY IT IS NEEDED. converge_frac() sets 'converged' and 'convergence_gap' on ITS OWN result,
        but every caller here DISCARDS that result -- they re-solve at the converged fraction and
        return the new one. So the flag never reached a caller, and a build that missed its gas
        target was indistinguishable from one that hit it. That is precisely the failure the flag
        was added to prevent, defeated by where it was attached.

        A SHARED HELPER RATHER THAN THREE COPIES, because there are three convergence paths in this
        file and fixing one would leave the others silently wrong -- which is how the original gap
        survived.
        """
        if self.result is None:
            raise RuntimeError('_carry_convergence_verdict() called before a result exists')
        self.result['converged'] = bool(converge_result.get('converged', False))
        self.result['convergence_gap'] = float(converge_result.get('convergence_gap', 0.0))
        self.result['achieved_share'] = float(converge_result.get('achieved_share', 0.0))
        return self.result

    def _post_build_hook(self):
        """A callable applied to the freshly built problem before constraints, or None.

        The base class has nothing to add. A scenario that needs structural bounds -- Scenario 3's
        distributed segment -- OVERRIDES this rather than the base branching on scenario identity,
        per project direction 2026-09-13. Mixins that add constraints chain onto whatever the
        composing class returns, so both apply.
        """
        return None

    @staticmethod
    def _chain_hooks(*hooks):
        """Composes post_build hooks left to right, skipping None. run_solve takes one callable."""
        live = [h for h in hooks if h is not None]
        if not live:
            return None
        def composed(problem):
            for h in live:
                problem = h(problem)
            return problem
        return composed

    def _curtailment_kwargs(self):
        """Passed to run_solve so the hook, not driver.py's default, decides the value."""
        return {'slcr_curt_cost': self.curtailment_cost_mwh()}

    def _gas_merit_order_kwargs(self):
        """Merit-order kwargs for the driver, empty when no stack is set.

        ON THE BASE CLASS DELIBERATELY (Rule 1). Every scenario dispatches gas against the same
        fleet with the same cost formula -- only the checkpoint year differs, and that is already
        an attribute. Putting this on Scenario3Solver, where the need surfaced, would have meant
        the next scenario re-implementing it.

        HOW THE STACK IS SET: assign `solver.gas_merit_order = GasMeritOrder(...)` before calling
        converge_and_solve(). Absent that, this returns {} and every call path behaves exactly as
        it did before 2026-09-12 -- the stack is opt-in, so existing baselines stay valid.

        The year comes from self.year rather than being passed separately: a stack resolved for a
        different year than the checkpoint being solved would silently apply the wrong retirements
        and the wrong fuel price, and nothing downstream would catch it.
        """
        stack = getattr(self, 'gas_merit_order', None)
        if stack is None:
            return {}
        return {'gas_merit_order': stack, 'gas_merit_order_year': self.year}

    def verify_input_data(self):
        """Appendix P.2 #14: cached/passed-in input totals must be checked against their
        own current, authoritative source before use -- not assumed correct because the
        caller already believes them established."""
        if self.sourced_annual_total_gwh is not None:
            actual_total = self.demand.sum() / 1000.0
            diff_pct = abs(actual_total - self.sourced_annual_total_gwh) / self.sourced_annual_total_gwh * 100
            if diff_pct > 0.01:
                raise ValueError(
                    f"#14 INPUT DATA VERIFICATION FAILED: {self.year} demand totals "
                    f"{actual_total:.1f} GWh, but the sourced authoritative total is "
                    f"{self.sourced_annual_total_gwh} GWh ({diff_pct:.2f}% divergence). "
                    f"This is exactly the class of error found and fixed this session -- "
                    f"refusing to solve on unverified input rather than silently proceeding.")
        if len(self.demand) != 8760:
            raise ValueError(f"#14: demand array is {len(self.demand)} hours, expected 8760 "
                              f"(standardized, leap-day-trimmed convention).")
        if np.any(np.isnan(self.demand)):
            raise ValueError(f"#14: NaNs found in {self.year} demand array.")

    def curtailment_cost_mwh(self):
        """Cost applied to curtailed energy, $/MWh. Override per scenario where the treatment
        genuinely differs -- the base class holds what is common, a subclass states its own.

        DEFAULTS TO THE SOURCED FIGURE rather than a local literal. Internal Debugging Log #20 set
        $100/MWh and defended it as "a defensible figure (same order of magnitude as gas cost and
        the export price), not another arbitrary tie-breaker". That distinction matters for cost
        accounting: a shaping term could be netted out of an SLCOE; a price cannot.

        IT HAD REGRESSED. build_problem() carried no curtailment cost at all by 2026-09-13 -- its
        only one came from apply_slcr_constraint(curt_cost=5.0), twenty times too low -- while
        build_dispatch_problem() still set 100.0 behind a comment claiming it matched
        build_problem()'s default. This hook exists so the value has one owner that a scenario can
        override deliberately, rather than a default buried two layers from the solver.
        """
        return assumptions.CURTAILMENT_COST_MWH

    def apply_gas_cap(self):
        """Schedule A/B existing-fleet baseline + the standing 2,862 MW new-build pool
        (Appendix A #4). Subclasses may override for a scenario-specific cap policy."""
        drv.set_year_capex(self.year)
        return drv.schedule_b_baseline_mw(self.year) + 2862.0

    def verify_result(self):
        """Appendix P.2 #11/#13: standing verification before any result is presented as
        final -- zero unserved energy, zero simultaneous charge/discharge for every storage
        type. Raises rather than silently returning a suspect result."""
        if self.result is None:
            raise RuntimeError("verify_result() called before solve()")
        r = self.result
        if r['unserved_mwh'] > 1e-3:
            raise ValueError(f"#11 VERIFICATION FAILED: {self.year} has "
                              f"{r['unserved_mwh']:.1f} MWh unserved energy.")
        if 'hourly' in r:
            h = r['hourly']
            for charge_key, discharge_key, label in [('nc', 'nd', 'Na'), ('fc', 'fd', 'iron-air'),
                                                        ('bc', 'bd', 'Bath')]:
                if charge_key in h and discharge_key in h:
                    simul = np.sum((h[charge_key] > 1e-6) & (h[discharge_key] > 1e-6))
                    if simul > 0:
                        raise ValueError(
                            f"#13 VERIFICATION FAILED: {self.year} has {simul} hours of "
                            f"simultaneous charge/discharge for {label} storage.")
        return True

    def solve(self, frac, capacity_cap_mw=None, return_hourly=True, **run_solve_kwargs):
        """Thin wrapper around driver.run_solve() -- the actual LP call. Subclasses extend
        via run_solve_kwargs (prior_* linking, reserve_margin_hint, etc.), not by
        reimplementing this method."""
        self.verify_input_data()
        cap = capacity_cap_mw if capacity_cap_mw is not None else self.apply_gas_cap()
        self.result = drv.run_solve(
            self.year, frac, self.demand, self.exist_solar, self.solar_cf, self.wind_cf,
            self.nuclear, capacity_cap_mw=cap, return_hourly=return_hourly, **run_solve_kwargs, **self._curtailment_kwargs())
        self.verify_result()
        return self.result


class SocialCostRGGIMixin:
    """Composable mixin for Tier 1/2 social costs (SC-CO2, SC-GHG, Health Impacts) and RGGI
    compliance cost, given a solved checkpoint/year's own gas dispatch array. Any CheckpointSolver
    subclass can opt into this -- the underlying formula (compute_tier123_social_costs.py's own
    compute_year(), and RGGI's simple co2_tons*price) is IDENTICAL across every scenario; only the
    existing/new MW split (needed for compute_year()'s own NOx-blend calculation) differs by
    scenario. Built directly in response to a real, repeated pattern this session (Internal
    Debugging Log #51-53): three separate, free-standing scripts independently reimplementing the
    same year-loop/PV-aggregation logic, with an independent bug (an undiscounted-over-discounted
    PV mismatch) introduced in one of the three and not the other two -- exactly the risk a single,
    shared implementation eliminates by construction, not by discipline.

    Subclasses MUST implement get_existing_new_mw(year); this class provides no default, since a
    silently-wrong default (e.g. always Scenario 1's own split) is worse than an explicit failure."""

    def get_existing_new_mw(self, year):
        raise NotImplementedError(
            f"{type(self).__name__} must implement get_existing_new_mw(year) -- no default is "
            f"provided deliberately, since a wrong-but-silent default (e.g. reusing another "
            f"scenario's own split) is worse than an explicit failure here.")

    def compute_year_social_cost_rggi(self, year, g_hourly):
        """One year's own SC-CO2/SC-GHG/Health/RGGI, given that year's own gas dispatch array.
        Thin wrapper into compute_tier123_final.py's own compute_year() -- does not reimplement
        any AP-42/SC-GHG/BenMAP/NOx-blend logic itself.

        BUG FOUND AND FIXED HERE (2026-08-23, before this method was ever used for real): an
        earlier draft imported compute_tier123_social_costs.py instead -- a SEPARATE, independent
        implementation of the same calculation (not a thin wrapper around this one), missing the
        CPI-to-2026$ inflation adjustment compute_tier123_final.py's own docstring documents as
        "corrected this session." Every Scenario 1B/Scenario 2 script built earlier this same
        session on compute_tier123_social_costs.py understated SC-CO2/SC-GHG by the CPI_DEFLATOR_
        2020_TO_2026 factor (~29%) and Health by CPI_DEFLATOR_2016_TO_2026 (~39%) -- confirmed
        directly: the ratio between the two modules' own output matched each deflator to 3-4
        significant figures, not a coincidence. Caught only because building this shared mixin
        forced a direct cross-check against Scenario 1's own established, correct figures -- see
        Internal Debugging Log #54."""
        import compute_tier123_final as t123
        import assumptions as asn
        existing_mw, new_mw = self.get_existing_new_mw(year)
        r = t123.compute_year(year, g_hourly, existing_mw, new_mw)
        rggi_price = asn.rggi_regulatory_schedule_price(year)
        rggi_cost = r['co2_tons'] * rggi_price
        return dict(year=year, va_scc_cost=r['social_cost_of_carbon'],
                    aggregate_ghg_cost=r['social_cost_of_ghg'],
                    tier2_cost=r['health_impacts_cost'], co2_tons=r['co2_tons'], rggi_cost=rggi_cost)

    @staticmethod
    def aggregate_social_cost_rggi(per_year_results, wacc=None, base_year=None):
        """Aggregates a dict of {year: compute_year_social_cost_rggi() result} into 20-year
        undiscounted totals AND PV (discounted) totals, plus PV-consistent per-MWh figures.

        BUG FIX BAKED IN HERE, NOT LEFT TO EACH CALLER TO GET RIGHT INDEPENDENTLY (Internal
        Debugging Log #53): per-MWh figures use the PV (discounted) cost total over PV (discounted)
        demand -- confirmed directly against Scenario 1's own established $39.84/$43.66/$3.19
        figures as the actual, correct convention, not the undiscounted total over PV demand a
        first attempt at this calculation used."""
        import assumptions as asn
        wacc = wacc if wacc is not None else asn.WACC
        base_year = base_year if base_year is not None else asn.BASE_YEAR

        years = sorted(per_year_results.keys())
        total_sc_co2 = sum(per_year_results[y]['va_scc_cost'] for y in years)
        total_sc_ghg = sum(per_year_results[y]['aggregate_ghg_cost'] for y in years)
        total_health = sum(per_year_results[y]['tier2_cost'] for y in years)
        total_rggi = sum(per_year_results[y]['rggi_cost'] for y in years)

        pv_sc_co2, pv_sc_ghg, pv_health, pv_rggi = 0.0, 0.0, 0.0, 0.0
        for y in years:
            df = 1.0 / (1 + wacc) ** (y - base_year)
            pv_sc_co2 += per_year_results[y]['va_scc_cost'] * df
            pv_sc_ghg += per_year_results[y]['aggregate_ghg_cost'] * df
            pv_health += per_year_results[y]['tier2_cost'] * df
            pv_rggi += per_year_results[y]['rggi_cost'] * df

        return dict(years=years,
                    total_sc_co2_undiscounted=total_sc_co2, total_sc_ghg_undiscounted=total_sc_ghg,
                    total_health_undiscounted=total_health, total_rggi_undiscounted=total_rggi,
                    pv_sc_co2=pv_sc_co2, pv_sc_ghg=pv_sc_ghg, pv_health=pv_health, pv_rggi=pv_rggi)

    @staticmethod
    def per_mwh(aggregated, pv_demand):
        """PV-consistent per-MWh figures (PV cost / PV demand, both discounted) -- the one, shared
        place this ratio is computed, so the discounting-basis mismatch (Internal Debugging Log
        #53) cannot recur independently per scenario."""
        return dict(sc_co2_per_mwh=aggregated['pv_sc_co2'] / pv_demand,
                    sc_ghg_per_mwh=aggregated['pv_sc_ghg'] / pv_demand,
                    health_per_mwh=aggregated['pv_health'] / pv_demand,
                    rggi_per_mwh=aggregated['pv_rggi'] / pv_demand)


class Scenario1Solver(CheckpointSolver, SocialCostRGGIMixin):
    """Scenario 1: optimizer-chosen build, multi-checkpoint continuity (prior-checkpoint
    linking), frac convergence against a statutory target share, VCEA storage floors --
    all via driver.py's own run_solve()/converge_frac(), which this session extended to
    accept prior_* kwargs specifically so linking and convergence could be combined in one
    call (previously required bypassing run_solve() entirely -- see Internal Debugging Log)."""

    def new_gas_technology(self):
        """DRAFT, NOT CONFIRMED -- see the note below.

        SIMPLE CYCLE, under the standing rule. Scenario 1 builds to a 100% clean target, so gas
        fills residual gaps after a large clean build -- the duty the rule was written for.

        WHAT WOULD CHANGE THIS: the scenario's shortfall profile has not been run since the
        carve-out, Bath and retirement-schedule corrections, and its clean build arrives late -- 59%
        of the fleet in the final checkpoint -- so 2035 and 2040 carry large residuals against a
        retiring fleet. Those years are where this declaration is most likely to prove wrong."""
        return 'simple_cycle'

    def gas_retirement_schedule(self):
        """SCHEDULE B. Scenario 1 reaches 100% clean at 2045, so Brunswick County, Potomac Energy
        Center and Greensville genuinely have no market -- which is the world Schedule B describes
        and the scenario it was written for."""
        return 'B'

    def __init__(self, year, demand, exist_solar, solar_cf, wind_cf, nuclear,
                 gas_target_share, sourced_annual_total_gwh=None, prior_result=None):
        super().__init__(year, demand, exist_solar, solar_cf, wind_cf, nuclear,
                          sourced_annual_total_gwh)
        self.gas_target_share = gas_target_share
        self.prior_result = prior_result  # a dict with S_mw/PNA_mw/ENA_mwh/EFE_mwh, or None
        self.converged_frac = None

    def _prior_kwargs(self):
        """Degrades the prior checkpoint's own solar forward to this checkpoint's year, per
        Appendix A #2's vintage-tracking convention. Returns the four prior_* kwargs
        run_solve()/converge_frac() now accept directly."""
        if self.prior_result is None:
            return dict(prior_solar_mw=0.0, prior_na_power_mw=0.0,
                        prior_na_energy_mwh=0.0, prior_ironair_energy_mwh=0.0)
        prior_year = self.prior_result['year']
        prior_solar_degraded = self.prior_result['S_mw_total'] * lp.solar_degradation_factor(self.year - prior_year)
        return dict(prior_solar_mw=prior_solar_degraded,
                    prior_na_power_mw=self.prior_result['PNA_mw'],
                    prior_na_energy_mwh=self.prior_result['ENA_mwh'],
                    prior_ironair_energy_mwh=self.prior_result['EFE_mwh'])

    def converge_and_solve(self, start_frac=None, tol=0.003, max_iter=8):
        """Converge the gas fraction, then solve at it.

        max_iter RAISED FROM 3 TO 8 on 2026-09-13. converge_frac now bisects rather than
        extrapolating proportionally, and bisection needs enough iterations to halve the interval
        to tolerance: from a starting gap of 0.115 against tol 0.003 that is six. Three was chosen
        for the old proportional step, which was expected to land in one or two jumps -- it did not,
        and an overnight scenario-3 run exhausted all three without converging.
        """
        """Converges frac against this checkpoint's own gas_target_share (linking included
        throughout, not bolted on after convergence -- linking changes the LP's own energy
        balance, so frac convergence without it can converge to the wrong value)."""
        self.verify_input_data()
        cap = self.apply_gas_cap()
        prior_kwargs = self._prior_kwargs()
        gas_kwargs = self._gas_merit_order_kwargs()
        frac, converge_result, history = drv.converge_frac(
            self.year, self.gas_target_share, self.demand, self.exist_solar, self.solar_cf,
            self.wind_cf, self.nuclear, tol=tol, max_iter=max_iter, capacity_cap_mw=cap,
            start_frac=start_frac, **prior_kwargs, **self._curtailment_kwargs())
        self.converged_frac = frac
        self.result = drv.run_solve(
            self.year, frac, self.demand, self.exist_solar, self.solar_cf, self.wind_cf,
            self.nuclear, capacity_cap_mw=cap, return_hourly=True, **prior_kwargs, **gas_kwargs, **self._curtailment_kwargs())
        self._carry_convergence_verdict(converge_result)
        self.verify_result()
        # Store this checkpoint's own total solar (incremental + degraded prior) for the
        # NEXT checkpoint's own linking -- keeps the "total vs. incremental" distinction
        # explicit rather than a source of the kind of ambiguity this project has hit before.
        prior_solar_degraded = prior_kwargs['prior_solar_mw']
        self.result['S_mw_total'] = self.result['S_mw'] + prior_solar_degraded
        self.result['year'] = self.year
        self._verify_monotonicity(prior_kwargs)
        return self.result

    def _verify_monotonicity(self, prior_kwargs):
        """Multi-checkpoint continuity requires each build variable >= the prior checkpoint's
        own value (Appendix A #2) -- checked directly, not assumed."""
        checks = [
            ('PNA_mw', self.result['PNA_mw'], prior_kwargs['prior_na_power_mw']),
            ('ENA_mwh', self.result['ENA_mwh'], prior_kwargs['prior_na_energy_mwh']),
            ('EFE_mwh', self.result['EFE_mwh'], prior_kwargs['prior_ironair_energy_mwh']),
        ]
        for name, current, prior in checks:
            if current < prior - 0.01:
                raise ValueError(f"Monotonicity violated for {name} at {self.year}: "
                                  f"{current:.1f} < prior checkpoint's {prior:.1f}")

    def get_existing_new_mw(self, year):
        """Schedule A/B existing-fleet baseline + the standing 2,862 MW overhaul/retain pool
        (new_peaker_ccgt_costs_by_size.md's own established standing rule) -- Scenario 1's own
        split, unchanged from what every Scenario 1/1B Tier 1/2/RGGI script already used
        independently before this refactor (Internal Debugging Log #51-52)."""
        return drv.schedule_b_baseline_mw(year), 2862.0


class Scenario1BSolver(Scenario1Solver):
    """Scenario 1B: identical to Scenario 1 in every respect except the target share at
    2045-and-beyond checkpoints allows 5% gas rather than the ~0.08% 'true 100% clean'
    target -- the entire class body is this one override, versus a fully duplicated
    solve_2045_1b_*.py script under the pre-refactor pattern."""

    def new_gas_technology(self):
        """DRAFT, NOT CONFIRMED -- see the note below.

        SIMPLE CYCLE, under the standing rule -- and the declaration most worth testing.

        1B allows gas 5% of the statutory base from 2045, which is an ENERGY allowance rather than
        gap-filling. If its simple-cycle fleet runs hard against that allowance, the same arithmetic
        that moved Scenario 2 to combined cycle would apply here.

        WHAT WOULD CHANGE THIS: a shortfall_duty_profile showing the existing simple-cycle fleet
        near saturation, or a cost comparison in which combined cycle wins at 1B's capacity factor.
        Neither has been run."""
        return 'simple_cycle'

    def gas_retirement_schedule(self):
        """SCHEDULE B. At 5% gas from 2045 the fleet needs very little, so it retires as in a VCEA
        world with enough retained to cover the following year -- which is exactly what
        SCENARIO_1B_GAS_CAPACITY_MW and the overhaul/retain pool represent."""
        return 'B'

    def apply_gas_cap(self):
        """6,000 MW from 2045, the figure Appendix N.2's capacity sweep locked in.

        THE INHERITED CAP WAS WRONG FOR THIS SCENARIO. Scenario1Solver's apply_gas_cap returns
        schedule_b_baseline_mw(year) + 2,862, which is 4,722 MW at 2045 -- the "existing only" row
        of N.2's own sweep table, costing $10,065.2M against $9,469.3M at 6,000 MW. The 1,278 MW of
        new simple-cycle CT that the sweep selected was never implemented anywhere.

        N.4's finding that gas reaches only 1.63% of demand, and that "the 5% statutory ceiling is
        largely moot... the binding constraint is physical fleet capacity", was measured at 4,722 MW
        and is therefore an artifact of the omission rather than a result about the scenario.

        Before 2045 this scenario is identical to Scenario 1 -- same RPS target every year through
        2044 -- so the inherited cap applies unchanged.
        """
        drv.set_year_capex(self.year)
        if self.year >= 2045:
            return assumptions.SCENARIO_1B_GAS_CAPACITY_MW
        return super().apply_gas_cap()

    def retain_and_overhaul_plan(self):
        """Which plants the 2045 capacity target implies retaining, overhauling, or building new.

        Wires driver.select_overhaul_retain(), which had no caller since it was written. It
        reproduces Appendix N.2's locked figure by a completely different route:

            6,000 MW target - 1,860 Schedule B survivors - 2,862 POOL = 1,278 MW residual
            N.2's capacity sweep, independently:                        1,278 MW new CT

        Two figures from unconnected work agreeing exactly is the strongest evidence available that
        the 6,000 MW target is right.

        REPORTS BOTH THE CONTINUOUS AND DISCRETE ANSWERS. F-Class units are 237 MW, so the 1,278 MW
        residual takes six of them -- 1,422 MW, 144 MW more than needed. N.2's sweep treated
        capacity as continuous; this is the buildable version. Which applies depends on whether the
        question is cost (1,278) or procurement (1,422).
        """
        if self.year < 2045:
            return None
        survivors = drv.schedule_b_baseline_mw(self.year)
        shortfall = assumptions.SCENARIO_1B_GAS_CAPACITY_MW - survivors
        plan = drv.select_overhaul_retain(shortfall)
        pool_mw = sum(p[1] for p in plan['selected'])
        return {
            'schedule_b_survivors_mw': survivors,
            'shortfall_mw': shortfall,
            'retained_pool_mw': pool_mw,
            'retained_plants': [p[0] for p in plan['selected']],
            'needing_overhaul': [p[0] for p in plan['selected'] if p[3]],
            'residual_gap_mw': shortfall - pool_mw,
            'new_build_units': len(plan['newbuild']),
            'new_build_mw_discrete': plan['cum_mw'] - pool_mw,
            'new_build_mw_continuous': assumptions.SCENARIO_1B_NEW_CT_MW,
            'overhaul_annual_cost_usd': plan['overhaul_annual_cost'],
            'newbuild_annual_cost_usd': plan['newbuild_annual_cost'],
        }

    def __init__(self, year, demand, exist_solar, solar_cf, wind_cf, nuclear,
                 sourced_annual_total_gwh=None, prior_result=None, additional_peaker_mw=0.0):
        # BUG FIXED (2026-08-23): was `0.95 if year >= 2045`, contradicting this class's own
        # docstring ("5% gas"). gas_target_share is used throughout Scenario1Solver/converge_frac()
        # as the GAS share the convergence loop targets (confirmed directly: drv.gas_target_share()
        # returns the gas share, e.g. 0.05 for 2044's own 95%-clean/5%-gas statutory requirement,
        # and Scenario1BSolver's own 2044 solve under the old code correctly matched Scenario 1's
        # target there). At year >= 2045 the old code set gas_target_share=0.95, which the same
        # convergence loop read as "target 95% GAS" -- not 95% clean / 5% gas as the docstring and
        # this scenario's own definition require. Caught because the resulting solve tried to push
        # frac toward 0.95, failed (the physical gas-fleet cap won't allow anywhere near that), and
        # landed at ~4.82% purely as a byproduct of cap saturation while never actually targeting
        # the real 5% ceiling -- a real result on a wrong target, not evidence the target itself
        # was ever correctly specified.
        gas_target_share = 0.05 if year >= 2045 else drv.gas_target_share(year)
        super().__init__(year, demand, exist_solar, solar_cf, wind_cf, nuclear,
                          gas_target_share, sourced_annual_total_gwh, prior_result)
        # New-build simple-cycle peaker capacity added at 2045+ to close the real shortfall against
        # the full 5% statutory allowance (Internal Debugging Log #51 -- direct user decision, sized
        # via new_peaker_ccgt_costs_by_size.md's own standing rule; F-Class, 237 MW, this session).
        # Configurable rather than hardcoded: a future re-sizing decision (different unit, different
        # MW) should not require editing this class.
        self.additional_peaker_mw = additional_peaker_mw

    def get_existing_new_mw(self, year):
        """Scenario 1B's own split is identical to Scenario 1's at every year EXCEPT 2045+, where
        the new-build peaker (if any) is genuinely new capacity, not existing fleet -- it belongs
        in new_mw for compute_year()'s own NOx-blend calculation (Internal Debugging Log #52's own
        finding: the F-Class unit is new-build, DLN-controlled, distinct from the legacy fleet)."""
        existing_mw, new_mw = super().get_existing_new_mw(year)
        if year >= 2045:
            new_mw += self.additional_peaker_mw
        return existing_mw, new_mw


class ReserveMarginMixin:
    """Composable, not scenario-specific -- PJM's own IRM applies project-wide (Appendix A
    #12/#13), so this is a mixin any CheckpointSolver subclass can opt into, rather than a
    reserve-margin-specific scenario subclass. Requires the base class's own solve()/
    converge_and_solve() to have already run once (to identify the peak-net-demand hour)
    before the reserve-margin-constrained solve/convergence can run."""

    def find_hour_of_maximum_net_demand(self):
        net_demand = self.demand - self.nuclear - self.exist_solar - lp.CVOW_MW * self.wind_cf
        hour_of_maximum_net_demand = int(np.argmax(net_demand))
        return hour_of_maximum_net_demand, self.demand[hour_of_maximum_net_demand], self.nuclear[hour_of_maximum_net_demand], self.wind_cf[hour_of_maximum_net_demand]

    def solve_with_reserve_margin(self, IRM=0.177, max_iter=5, **solve_kwargs):
        """Iterates the peak-net-demand hour check per Appendix A #13.1's own documented
        process: solve, check whether the peak hour moved, re-solve if it did."""
        hour_of_maximum_net_demand, demand_at_peak, nuclear_at_peak, wind_cf_at_peak = self.find_hour_of_maximum_net_demand()
        for _ in range(max_iter):
            solar_cf_at_peak = self.solar_cf[hour_of_maximum_net_demand]
            reserve_margin_hint = (hour_of_maximum_net_demand, demand_at_peak, nuclear_at_peak, wind_cf_at_peak, solar_cf_at_peak)
            if hasattr(self, 'converge_and_solve'):
                self.result = self._converge_and_solve_with_reserve(
                    reserve_margin_hint, IRM, **solve_kwargs)
            else:
                self.result = self.solve(reserve_margin_hint=reserve_margin_hint, IRM=IRM, **solve_kwargs)
            new_hour_of_maximum_net_demand, new_demand_at_peak, new_nuclear_at_peak, new_wind_cf_at_peak = \
                self.find_hour_of_maximum_net_demand()
            if new_hour_of_maximum_net_demand == hour_of_maximum_net_demand:
                return self.result
            hour_of_maximum_net_demand, demand_at_peak, nuclear_at_peak, wind_cf_at_peak = \
                new_hour_of_maximum_net_demand, new_demand_at_peak, new_nuclear_at_peak, new_wind_cf_at_peak
        return self.result

    def _converge_and_solve_with_reserve(self, reserve_margin_hint, IRM, start_frac=None, tol=0.003, max_iter=8):
        """Scenario1Solver-specific path: converge_frac() itself doesn't accept a
        reserve_margin_hint (the constraint depends on a peak hour identified from an
        already-built problem, which convergence doesn't have until it's run) -- so this
        converges frac WITHOUT the reserve constraint first, then does one final solve WITH
        it at the converged frac. Disclosed as a simplification: the reserve-margin
        constraint could, in principle, shift which frac hits gas_target_share exactly, the same
        reasoning that motivated combining linking and convergence earlier in this file --
        not yet extended here, flagged rather than silently assumed equivalent.

        EXTENDED (2026-09-09): also forwards _distributed_kwargs() when the composing class
        provides one (Scenario3Solver does), same hasattr-gated pattern as _prior_kwargs directly
        below -- without this, a Scenario3WithReserveMargin composition would silently solve
        WITHOUT the distributed segment despite being built from Scenario3Solver, since this method
        previously had no path to those kwargs at all. Caught while wiring this through, not found
        by observing a wrong result -- flagged as a real, non-obvious integration gap between this
        mixin and the new distributed-segment work, not a hypothetical concern."""
        self.verify_input_data()
        cap = self.apply_gas_cap()
        prior_kwargs = self._prior_kwargs() if hasattr(self, '_prior_kwargs') else {}
        dist_kwargs = self._distributed_kwargs() if hasattr(self, '_distributed_kwargs') else {}
        gas_kwargs = self._gas_merit_order_kwargs()
        frac, converge_result, history = drv.converge_frac(
            self.year, self.gas_target_share, self.demand, self.exist_solar, self.solar_cf,
            self.wind_cf, self.nuclear, tol=tol, max_iter=max_iter, capacity_cap_mw=cap,
            start_frac=start_frac, **prior_kwargs, **dist_kwargs, **gas_kwargs, **self._curtailment_kwargs())
        self.converged_frac = frac
        result = drv.run_solve(
            self.year, frac, self.demand, self.exist_solar, self.solar_cf, self.wind_cf,
            self.nuclear, capacity_cap_mw=cap, return_hourly=True,
            reserve_margin_hint=reserve_margin_hint, IRM=IRM, **prior_kwargs, **dist_kwargs, **self._curtailment_kwargs())
        self.result = result
        self._carry_convergence_verdict(converge_result)
        self.verify_result()
        if prior_kwargs:
            prior_solar_degraded = prior_kwargs.get('prior_solar_mw', 0.0)
            self.result['S_mw_total'] = self.result['S_mw'] + prior_solar_degraded
            self.result['year'] = self.year
            if dist_kwargs:
                prior_dist_solar_degraded = prior_kwargs.get('prior_distributed_solar_mw', 0.0)
                self.result['dist_S_mw_total'] = self.result['dist_S_mw'] + prior_dist_solar_degraded
            if hasattr(self, '_verify_monotonicity'):
                self._verify_monotonicity(prior_kwargs)
        return self.result


class AllHoursReserveMixin:
    """Applies the installed reserve margin in EVERY hour, not only at the peak-net-demand hour.

    REPLACES ReserveMarginMixin, per Weather_Year_Robustness_Approaches_and_Findings_2026-08-23.md,
    which lists the two as alternatives (1a peak-hour, 1c all-hours) and calls the all-hours
    constraint "the real fix" and "current standard". The peak-hour version was found to have
    left 769 hours short of margin while reporting zero unserved energy -- different tests, and
    only the all-hours one is a guarantee.

    SINGLE PASS, NO ITERATION. ReserveMarginMixin loops up to five times because the peak hour can
    MOVE between solves, and it must find it again. An all-hours constraint has no peak hour to
    find, so that loop is dead weight here and is not reproduced.

    WIRED THROUGH run_solve's post_build_hook, which was added specifically for all_hours_reserve.py
    -- its own comment names the module -- and had never been used. That is the ninth instance in
    this project of a component built for a documented purpose and left unconnected.

    MEASURED BEFORE WIRING: no solve-time cost (26.2 s against 27.5 s without, within noise) and a
    +1.75% objective at 2030, so the constraint binds.

    ON STRICTNESS: this applies the INSTALLED reserve margin at every hour. IRM is a planning
    standard evaluated at peak, not an hourly operating requirement, so holding it in all 8,760
    hours is stricter than PJM asks of anyone. Defensible as a conservative reliability floor; it
    must be labelled MORE CONSERVATIVE THAN PJM, not as "the PJM reserve margin".
    """

    def _all_hours_reserve_hook(self, IRM):
        """Builds the post_build_hook closure. Gas enters at the scenario's own existence cap --
        apply_gas_cap() -- not the merit-order stack, because reserve margin is about capacity
        available to be CALLED, and the two limits were shown (issue #18) to disagree."""
        from all_hours_reserve import add_all_hours_reserve_margin_constraint
        gas_cap = self.apply_gas_cap()
        if gas_cap is None:
            raise ValueError(
                'AllHoursReserveMixin needs a finite gas cap from apply_gas_cap(); this scenario '
                'returned None. Reserve margin cannot be computed against unbounded gas -- it '
                'would trivially pass every hour.')
        dist = self._distributed_kwargs() if hasattr(self, '_distributed_kwargs') else {}
        dist_cf = dist.get('distributed_solar_cf')
        if dist_cf is None:
            import numpy as np
            dist_cf = np.zeros(len(self.demand))
        return lambda problem: add_all_hours_reserve_margin_constraint(
            problem, self.nuclear, self.wind_cf, self.exist_solar, self.solar_cf, dist_cf,
            gas_cap, self.demand, IRM=IRM)

    def solve_with_reserve_margin(self, IRM=0.177, **solve_kwargs):
        """Same interface as ReserveMarginMixin.solve_with_reserve_margin so the WithReserveMargin
        classes and every runner keep working unchanged; the iteration arguments it accepted are
        ignored here because there is nothing to iterate on."""
        solve_kwargs.pop('max_iter', None)
        # Chain onto whatever the composing scenario already applies (Scenario 3's distributed
        # bounds), so both take effect. Order: scenario bounds first, then the reserve rows.
        hook = self._chain_hooks(self._post_build_hook(), self._all_hours_reserve_hook(IRM))
        self.verify_input_data()
        cap = self.apply_gas_cap()
        prior_kwargs = self._prior_kwargs() if hasattr(self, '_prior_kwargs') else {}
        dist_kwargs = self._distributed_kwargs() if hasattr(self, '_distributed_kwargs') else {}
        gas_kwargs = self._gas_merit_order_kwargs()
        frac, converge_result, history = drv.converge_frac(
            self.year, self.gas_target_share, self.demand, self.exist_solar, self.solar_cf,
            self.wind_cf, self.nuclear, capacity_cap_mw=cap, post_build_hook=hook,
            **prior_kwargs, **dist_kwargs, **gas_kwargs, **self._curtailment_kwargs(), **solve_kwargs)
        self.converged_frac = frac
        self.result = drv.run_solve(
            self.year, frac, self.demand, self.exist_solar, self.solar_cf, self.wind_cf,
            self.nuclear, capacity_cap_mw=cap, return_hourly=True, post_build_hook=hook,
            **prior_kwargs, **dist_kwargs, **gas_kwargs, **self._curtailment_kwargs())
        self._carry_convergence_verdict(converge_result)
        self.result['reserve_margin_method'] = 'all_hours'
        self.verify_result()
        if prior_kwargs:
            self.result['S_mw_total'] = self.result['S_mw'] + prior_kwargs.get('prior_solar_mw', 0.0)
            self.result['year'] = self.year
            if dist_kwargs:
                self.result['dist_S_mw_total'] = (self.result['dist_S_mw']
                                                  + prior_kwargs.get('prior_distributed_solar_mw', 0.0))
            if hasattr(self, '_verify_monotonicity'):
                self._verify_monotonicity(prior_kwargs)
        return self.result


#: The peak-hour mixin is retained under a name that says what it is, for A/B comparison against
#: the all-hours standard. It is no longer what the WithReserveMargin classes use.
#:
#: IT IS THEREFORE DORMANT, and so are the two driver functions only it reaches --
#: add_reserve_margin_constraint() and find_hour_of_maximum_net_demand(). An audit on 2026-09-14
#: found both with no external caller, which is correct rather than a defect: nothing should be
#: using the peak-hour constraint now that all-hours replaced it.
#:
#: WHY IT IS KEPT RATHER THAN DELETED. The A/B at 2045 gave IDENTICAL results -- at 100% compliance
#: with 47 GW of storage the all-hours margin never binds -- but at 2030 the same constraint cost
#: +1.75%. So the comparison will matter again at the sweep's lower compliance levels, where gas
#: does the work and storage is smaller, and re-deriving the peak-hour path to run it would be
#: worse than keeping it.
#:
#: The module-level orphan check in scripts/audit_documented_fixes.py works on MODULES, not
#: functions, so it cannot see this. Stated here instead.
PeakHourReserveMarginMixin = ReserveMarginMixin


class Scenario1WithReserveMargin(AllHoursReserveMixin, Scenario1Solver):
    """Scenario 1, with the PJM reserve margin constraint applied -- the composition this
    project's own reserve-margin work (Appendix A #12/#13) has been building toward,
    now expressed as a mixin rather than a separate, hand-built constraint script per
    checkpoint."""
    pass


class Scenario3Solver(Scenario1Solver):
    """Scenario 3: same as Scenario 1 -- optimizer-chosen build, multi-checkpoint continuity, frac
    convergence, VCEA storage floors -- ALL inherited, unchanged. Structural addition: a distributed
    solar+storage segment, CO-OPTIMIZED within the same central LP as of 2026-09-09 (see lp_model.
    build_problem()'s own docstring for the full mechanism) -- REPLACES the earlier blended-CF, post-
    hoc compute_distributed_shares() approach entirely, per direct user decision. That approach is
    gone from this class, not just deprecated in place.

    self.solar_cf is now pure utility-scale CF, unblended -- no separate self.utility_solar_cf
    attribute is needed anymore, since there's no blend to unwind after the fact.

    Ownership sub-allocation (residential NEM 6%, rooftop/canopy WMA) and the B.1.a-c/C.1 utility-
    scale ownership/land-use splits are POST-HOC allocations of the solved total, same as before --
    those don't touch generation physics and were never the thing being co-optimized. Only the
    distributed segment's own STORAGE dispatch and the NEM/WMA solar SIZE split moved into the LP
    itself. Residential NEM (6% of distributed solar, Scenario 3) has NO storage, by direct user
    decision -- it is not part of the co-optimized segment at all; its own generation contribution
    should be computed the same way it always was, from a fixed share of dist_S_mw_total, once this
    checkpoint's own solve is complete. Rooftop-WMA and canopy-WMA share ONE combined distributed
    pool (direct user decision, to avoid an overly complex LP) -- not modeled as separate LP segments."""

    def new_gas_technology(self):
        """DRAFT, NOT CONFIRMED -- see the note below.

        SIMPLE CYCLE, as Scenario 1: the same 100% clean terminal year, reached by different
        siting. Unmeasured for the same reason.

        WHAT WOULD CHANGE THIS: Scenario 3's distributed siting shifts generation toward urban load,
        which may leave a differently shaped residual than Scenario 1's. It has never been solved
        with the merit-order stack."""
        return 'simple_cycle'

    def gas_retirement_schedule(self):
        """SCHEDULE B, as Scenario 1: the same 100% clean terminal year, reached by different
        siting."""
        return 'B'

    def __init__(self, year, demand, exist_solar, solar_cf, wind_cf, nuclear, gas_target_share,
                 distributed_solar_cf, distributed_exogenous_price_mwh,
                 sourced_annual_total_gwh=None, prior_result=None, policy=None,
                 distributed_share_of_total_solar=0.20,
                 distributed_reserve_margin_credit_fraction=0.0):
        """distributed_solar_cf, distributed_exogenous_price_mwh: REQUIRED, not optional with a
        silent default (SES Rule 5) -- there is no safe default for either (a wrong CF or price array
        produces a real, wrong answer, not an obvious failure) and this class has no way to construct
        either one itself. distributed_exogenous_price_mwh is the six-day-scarcity + congestion +
        losses stack (see the design discussion this class's rewrite followed) -- construction of that
        array is this project's own separate, not-yet-built responsibility; this class only consumes
        it, doesn't build it."""
        import scenario3_build as s3b
        self.policy = policy if policy is not None else s3b.STANDARD
        self.distributed_solar_cf = distributed_solar_cf
        self.distributed_exogenous_price_mwh = distributed_exogenous_price_mwh
        self.distributed_share_of_total_solar = distributed_share_of_total_solar
        self.distributed_reserve_margin_credit_fraction = distributed_reserve_margin_credit_fraction
        # ADDED 2026-09-05, direct user confirmation: A.2 (EV Charger DLC) + A.3/A.4
        # (heat pump/PHIUS/HPWH) demand-side reduction, applied to the base `demand`
        # series here -- built fresh, not reusing the project's own `demand_dsm` series
        # (unverified provenance, reduction too small to be this full stack -- see
        # scenario3_build.py's own module-level comment on apply_scenario3_demand_
        # adjustment for the full rationale). Raises explicitly (SES Rule 5) if `year`
        # is not one of this project's four checkpoint years, rather than silently
        # passing an unadjusted demand series through.
        adjusted_demand = s3b.apply_scenario3_demand_adjustment(demand, year)
        super().__init__(year, adjusted_demand, exist_solar, solar_cf, wind_cf, nuclear,
                          gas_target_share, sourced_annual_total_gwh, prior_result)

    def _prior_kwargs(self):
        """Extends Scenario1Solver's own _prior_kwargs() (Rule 1: extend, not duplicate) with the
        distributed segment's own prior-checkpoint floors -- same treatment as the utility-scale
        ones: solar degrades forward via lp.solar_degradation_factor(), storage does not (this
        project's standing no-battery-degradation-within-the-analysis-window convention -- see the
        Na-ion/iron-air calendar-life discussion this build followed for how far that convention is
        and isn't independently verified for each chemistry)."""
        base = super()._prior_kwargs()
        if self.prior_result is None:
            base.update(prior_distributed_solar_mw=0.0, prior_distributed_na_power_mw=0.0,
                        prior_distributed_na_energy_mwh=0.0, prior_distributed_ironair_energy_mwh=0.0)
            return base
        prior_year = self.prior_result['year']
        prior_dist_solar_degraded = (self.prior_result.get('dist_S_mw_total', 0.0)
                                      * lp.solar_degradation_factor(self.year - prior_year))
        base.update(prior_distributed_solar_mw=prior_dist_solar_degraded,
                    prior_distributed_na_power_mw=self.prior_result.get('dist_PNA_mw', 0.0),
                    prior_distributed_na_energy_mwh=self.prior_result.get('dist_ENA_mwh', 0.0),
                    prior_distributed_ironair_energy_mwh=self.prior_result.get('dist_EFE_mwh', 0.0))
        return base

    def _distributed_kwargs(self):
        """The 5 distributed-segment kwargs, shared between converge_and_solve() below and
        ReserveMarginMixin._converge_and_solve_with_reserve() (hasattr-gated there) -- factored
        out to one place (Rule 6) rather than written inline twice, so the two call sites can't
        silently drift apart if one of these ever needs to change."""
        return dict(enable_distributed_segment=True, distributed_solar_cf=self.distributed_solar_cf,
                    distributed_share_of_total_solar=self.distributed_share_of_total_solar,
                    distributed_exogenous_price_mwh=self.distributed_exogenous_price_mwh,
                    distributed_reserve_margin_credit_fraction=self.distributed_reserve_margin_credit_fraction)

    def get_existing_new_mw(self, year):
        """Identical to Scenario 1's split, stated explicitly rather than inherited silently.

        WHY THIS EXISTS WHEN IT CHANGES NOTHING. SocialCostRGGIMixin refuses to supply a default,
        on the stated grounds that "a wrong-but-silent default (e.g. reusing another scenario's own
        split) is worse than an explicit failure here". That guard cannot fire for this class:
        Scenario3Solver inherits from Scenario1Solver, so it picks up Scenario 1's implementation
        through the MRO and the raise is never reached. The decision the guard exists to force was
        being made by the class hierarchy instead of by anyone.

        VERIFIED IDENTICAL, not assumed. Scenario 3 does not override apply_gas_cap, so its gas
        fleet IS Scenario 1's -- schedule_b_baseline_mw(year) plus the standing 2,862 MW
        overhaul/retain pool. The distributed segment adds solar and storage, not gas capacity, so
        the existing/new split that feeds compute_year()'s NOx blend is unchanged.

        IF SCENARIO 3 EVER GAINS ITS OWN GAS CAPACITY -- as Scenario 1B did at 2045 -- this must be
        revisited. Delegating to super() keeps the two in step until then, while leaving a place
        where the divergence would be written.
        """
        return super().get_existing_new_mw(year)

    def _post_build_hook(self):
        """Scenario 3's structural bounds on the distributed segment.

        distributed_physical_bounds.py HAD NEVER BEEN WIRED IN -- no importer since the commit
        that added it (issue #20), so every Scenario 3 result ever produced ran without these. Its
        own docstring records why they exist: a 2026-09-09 stress run built 1.43 TWh of DISTRIBUTED
        iron-air, 60x the entire utility Na-ion fleet, because iron-air energy capex is 3.6x cheaper
        and FE_DURATION=100 derives power as energy/100.

        allow_distributed_iron_air=False by decision: the 4-hour canopy pairing convention the
        siting analysis assumed does not admit 100-hour storage, and letting the LP choose silently
        broke that convention.
        """
        from distributed_physical_bounds import add_distributed_physical_bounds
        base = super()._post_build_hook()
        mine = lambda p: add_distributed_physical_bounds(p, allow_distributed_iron_air=False)
        return self._chain_hooks(base, mine)

    def converge_and_solve(self, start_frac=None, tol=0.003, max_iter=8):
        """OVERRIDDEN, not just extended via super() -- Scenario1Solver's own version calls
        drv.converge_frac()/drv.run_solve() with a fixed call signature that has no hook for the
        distributed_* kwargs this subclass needs threaded through at every iteration. This is a
        genuinely necessary override (the parent has no extension point for these new, Scenario-3-
        specific parameters), not a convenience duplication of shared logic -- everything else
        (frac convergence mechanics, prior-checkpoint linking, SLCR, verification) still calls
        through to the exact same driver.py functions Scenario1Solver itself uses."""
        self.verify_input_data()
        cap = self.apply_gas_cap()
        prior_kwargs = self._prior_kwargs()
        dist_kwargs = self._distributed_kwargs()
        hook = self._post_build_hook()
        gas_kwargs = self._gas_merit_order_kwargs()
        frac, converge_result, history = drv.converge_frac(
            self.year, self.gas_target_share, self.demand, self.exist_solar, self.solar_cf,
            self.wind_cf, self.nuclear, tol=tol, max_iter=max_iter, capacity_cap_mw=cap, post_build_hook=hook,
            start_frac=start_frac, **prior_kwargs, **dist_kwargs, **self._curtailment_kwargs())
        self.converged_frac = frac
        self.result = drv.run_solve(
            self.year, frac, self.demand, self.exist_solar, self.solar_cf, self.wind_cf,
            self.nuclear, capacity_cap_mw=cap, post_build_hook=hook, return_hourly=True,
            **prior_kwargs, **dist_kwargs, **gas_kwargs, **self._curtailment_kwargs())
        self.verify_result()
        prior_solar_degraded = prior_kwargs['prior_solar_mw']
        prior_dist_solar_degraded = prior_kwargs['prior_distributed_solar_mw']
        self.result['S_mw_total'] = self.result['S_mw'] + prior_solar_degraded
        self.result['dist_S_mw_total'] = self.result['dist_S_mw'] + prior_dist_solar_degraded
        self.result['year'] = self.year
        self._carry_convergence_verdict(converge_result)
        self._verify_monotonicity(prior_kwargs)
        return self.result

    def _verify_monotonicity(self, prior_kwargs):
        """Extends Scenario1Solver's own _verify_monotonicity() (Rule 1) with the distributed
        storage build variables -- same requirement, same reasoning: each checkpoint's own build
        must be >= the prior checkpoint's already-built capacity."""
        super()._verify_monotonicity(prior_kwargs)
        checks = [
            ('dist_PNA_mw', self.result['dist_PNA_mw'], prior_kwargs['prior_distributed_na_power_mw']),
            ('dist_ENA_mwh', self.result['dist_ENA_mwh'], prior_kwargs['prior_distributed_na_energy_mwh']),
            ('dist_EFE_mwh', self.result['dist_EFE_mwh'], prior_kwargs['prior_distributed_ironair_energy_mwh']),
        ]
        for name, current, prior in checks:
            if current < prior - 0.01:
                raise ValueError(f"Monotonicity violated for {name} at {self.year}: "
                                  f"{current:.1f} < prior checkpoint's {prior:.1f}")


class Scenario1BWithReserveMargin(AllHoursReserveMixin, Scenario1BSolver):
    """Scenario 1B with the all-hours reserve margin.

    ADDED 2026-09-14. There was no reserve-margin variant for 1B, so it solved with NO RESERVE
    MARGIN AT ALL while Scenarios 1 and 3 carried the all-hours constraint. Comparing them would
    have held 1B to a looser reliability standard than the scenarios it is measured against -- the
    same defect Scenario 2 had, and the same one that makes a comparison meaningless.

    Nothing else differs: 1B's divergence from Scenario 1 is its gas target (5% from 2045, against
    0%), which Scenario1BSolver already sets.
    """


class Scenario3WithReserveMargin(AllHoursReserveMixin, Scenario3Solver):
    """Scenario 3, with the PJM reserve margin constraint applied -- the same composition pattern
    as Scenario1WithReserveMargin above, now actually built (2026-09-09). This is the specific gap
    identified several turns into this session's own distributed-segment work: Scenario3Solver had
    always inherited from Scenario1Solver (without reserve margin), not Scenario1WithReserveMargin,
    so even a fully-built Scenario3Solver would have silently reproduced the same staleness this
    project's own xlsx-vs-Python-pipeline SLCOE discrepancy was traced to. distributed_reserve_
    margin_credit_fraction still defaults to 0.0 here (see run_solve()'s own docstring) -- this
    class makes the reserve-margin MECHANISM available to Scenario 3, it does not, on its own,
    resolve how much of the distributed segment's own capacity should count toward it."""
    pass


class Scenario2Solver(CheckpointSolver, SocialCostRGGIMixin):
    """Scenario 2: build-out follows a statutory schedule, not an optimizer decision --
    structurally the most different from Scenario 1's own family, sharing only the base
    class's input-verification and result-verification machinery. Does NOT inherit from
    Scenario1Solver -- frac convergence, prior-checkpoint linking, and VCEA storage floors
    are all Scenario-1-specific concepts that don't apply here. Wraps
    lp_model.build_scenario2_problem() directly, per that function's own, separate
    calling convention (Appendix C)."""

    def new_gas_capacity_mw(self, year=None):
        """New combined-cycle capacity in place in `year`, MW, as whole reference units.

        SIZED ON COST, NOT ON ADEQUACY ALONE. Adequacy sets a FLOOR -- unserved energy reaches zero
        at about 5,000 MW at 2045 -- and cost sets the optimum ABOVE it at 6,500 MW, because the
        extra capacity pays for itself in fuel saved on the existing fleet. Reporting only the
        adequacy floor would understate what a least-cost plan builds.

        THE COST CURVE IS FLAT: $8,307M/yr at 6,500 MW against $8,323M at 7,000 and $8,342M at
        7,500, a 0.4% spread across a 1,000 MW range. The answer is weakly determined, which is
        itself a finding -- Scenario 2's cost is dominated by fuel on a fleet that must run hard
        regardless, so the CCGT/CT split moves it far less than the QUANTITY of gas the scenario
        forces. See the Scenario 2 working document, section 9.

        WHOLE UNITS, because megawatts are not divisible in procurement. Six H-Class multi-shaft
        units give 6,498 MW against the 6,500 MW optimum -- a 0.03% shortfall, against Scenario
        1B's 11% overshoot when 1,278 MW becomes six F-Class units.

        CAPACITY PERSISTS, so this is a running maximum: nothing already built is unbuilt, and a
        year needing less than an earlier year simply runs what exists at lower utilisation.

        THREE SIZING CRITERIA WERE TRIED AND REJECTED before cost (build log 149): a CT-utilisation
        diagnostic with no support in the literature, a run-length fit on the unbounded gas series
        which described what gas SERVED rather than what capacity was MISSING, and a rule holding
        the existing simple-cycle fleet at or below its 28.1% crossover -- which is a NEW-BUILD
        decision that does not transfer to plant with sunk capital.
        """
        year = self.year if year is None else year
        targets = assumptions.SCENARIO2_NEW_CCGT_UNITS_BY_YEAR
        if year not in targets:
            # Rule 5. Interpolating would feed a reported figure, and the requirement is NOT
            # monotonic -- it dips when statutory solar arrives faster than load grows -- so no
            # interpolation between neighbouring years is safe.
            raise ValueError(
                f'no new-gas capacity target for {year}. Targets run '
                f'{min(targets)}-{max(targets)}; a year outside that range needs its own sizing '
                'solve rather than an interpolated guess.')
        # CAPACITY PERSISTS: what is built is the running maximum, not this year's requirement.
        # A year needing less than an earlier year runs what exists at lower utilisation.
        # CAPACITY PERSISTS: the running maximum, not this year's own entry. The requirement is NOT
        # monotonic -- 2031 needs a unit that 2033 does not -- because statutory solar arrives
        # faster than load grows in some years. Nothing already built is unbuilt.
        units = max(n for y, n in targets.items() if y <= year)
        return units * assumptions.CCGT_REFERENCE_UNIT_MW

    def apply_gas_cap(self):
        """Existing fleet under Schedule A, plus the new combined-cycle capacity built by this year.

        THE INHERITED DEFAULT DISPATCHED GAS THE FLEET DOES NOT HAVE. Scenario2Solver.solve left
        ccgt_mw at unbounded_gas_ceiling_mw -- 200,000 MW -- so the published run reported ZERO
        unserved energy while a run bounded by the real fleet showed 30.05 TWh at 2045 over 5,671
        hours. Those were two specifications, and every figure downstream rested on the wrong one.

        Overriding here rather than in the runner follows the hook Scenario1BSolver already uses,
        and means the sweep and any future caller inherit the bound rather than having to remember
        to pass it.
        """
        # THE RETAIN POOL IS PART OF THE EXISTING FLEET, not new build. Omitting it in the first
        # version of this override gave 13,889 MW against the merit-order stack's 12,216 MW plus
        # 6,498 MW of new capacity, and the solve showed 15.82 TWh unserved where an independent
        # probe at the same capacity showed zero. Rule 4: the disagreement between two paths was
        # the signal, not either figure on its own.
        return (drv.gas_baseline_mw(self.year, self.gas_retirement_schedule())
                + assumptions.GAS_NEW_BUILD_POOL_MW
                + self.new_gas_capacity_mw())

    def new_gas_technology(self):
        """COMBINED CYCLE, and the standing rule's own text carves this scenario out: "NOT Scenario
        2, which retains its own established CCGT-based new-build methodology".

        MEASURED, and the rule's rationale does not describe this shortfall. It was written for
        needs that are "short-duration (a few hours at a time)"; Scenario 2's 2045 shortfall is
        30.05 TWh across 5,671 hours -- 65% of the year -- at a 33.4% capacity factor, with the
        existing simple-cycle fleet at a 100% capacity factor until combined-cycle capacity is
        added.

        What the new capacity does is not fill peaks but displace that fleet from baseload duty,
        where it burns at an 11.0 heat rate on load that wants 6.4."""
        return 'combined_cycle'

    def carve_out_mw(self, year=None):
        """Distributed capacity the C.2 carve-out requires in `year`, MW.

        Va. Code 56-585.5(C): the RPS Program requirement is "a percentage of the total electric
        energy SOLD in the previous calendar year", and C.2 requires 4.5% (2026-2030) or 5%
        (2031-2045) of that requirement from resources of 1 MW or less.

            energy sold (n-1)  =  VirginiaOnlyGeneration(n-1) / loss factor
            RPS requirement    =  Phase II share  x  energy sold
            carve-out MWh      =  carve-out share x  RPS requirement
            x (MW)             =  carve-out MWh   /  (8,760 x distributed capacity factor)

        SOLD MEANS METERED, so the generation series is divided by the 1.0925 loss factor. The same
        series is used UNDIVIDED for dispatch, because the hourly file already carries the gross-up.
        See docs/Common_Reference.md section 1.

        NOT CIRCULAR. The base is energy sold, a quantity the demand series gives independently of
        what the scenario builds -- so the carve-out is computable even though Scenario 2 does not
        meet the RPS.

        THE CAPACITY FACTOR DECIDES THE MEGAWATTS. The obligation is energy, so a worse capacity
        factor means more nameplate for the same RECs. The 45-degree fixed array assumed for
        distributed resources delivers 0.1526 against utility tracking's 0.2252, which is why the
        swap loses energy at constant total capacity.
        """
        import demand_basis
        import distributed_solar_profile as dsp
        import rps_compliance as rc

        year = self.year if year is None else year
        sold_mwh = (demand_basis.VirginiaOnlyGeneration(year - 1).hourly_mw().sum()
                    / assumptions.TRANSMISSION_LOSS_FACTOR)
        requirement_mwh = sold_mwh * rc.phase_ii_rps_share(year)
        carve_out_mwh = requirement_mwh * rc.distributed_carve_out_share(year)
        return carve_out_mwh / (8760.0 * dsp.DESIGN_YEAR_CAPACITY_FACTOR)

    def solar_split_mw(self, year=None, new_build_mw=None):
        """(distributed, utility) MW of NEW BUILD, within the capped total.

        THE SPLIT APPLIES TO NEW BUILD, NOT TO THE STATUTORY TOTAL. The 16,100 MW of D.2 is a total
        INCLUDING the existing fleet -- assumptions.vcea_new_solar_mw already nets that off, giving
        11,445 MW of new build at 2045 against 4,819 MW existing. Splitting the 16,100 itself and
        passing both parts to the builder would add the existing fleet on top, taking total solar to
        20,918 MW and RAISING the clean share, which is how this was first written and how it was
        caught: the result moved the wrong way.

        The carve-out is capped at the new build available. If it ever exceeded that, the obligation
        could not be met from new build alone -- which the cap assumption forbids.
        """
        year = self.year if year is None else year
        if new_build_mw is None:
            new_build_mw = assumptions.vcea_new_solar_mw(year, self.vcea_solar_mw)
        dist = min(self.carve_out_mw(year), new_build_mw)
        return dist, new_build_mw - dist

    def gas_retirement_schedule(self):
        """SCHEDULE A -- CORRECTED 2026-09-14, having inherited B silently until then.

        Schedule B has three plants retiring FOR LACK OF MARKET. Scenario 2 runs gas at a 68%
        capacity factor supplying 132 TWh of 202 TWh demand: the most valuable market those plants
        will ever see. They do not close for want of one.

        The correction is worth 5,531 MW at 2045 -- 7,391 against 1,860 -- and Schedule A also
        carries 2041 and 2044 retirement steps the old flat baseline ignored, so the intermediate
        years were overstated too."""
        return 'A'

    def __init__(self, year, demand, exist_solar, solar_cf, wind_cf, nuclear,
                 vcea_solar_mw, sourced_annual_total_gwh=None, peak_gas_mw=None):
        super().__init__(year, demand, exist_solar, solar_cf, wind_cf, nuclear,
                          sourced_annual_total_gwh)
        self.vcea_solar_mw = vcea_solar_mw
        # For get_existing_new_mw() -- Scenario 2's own peak gas MW at this year, from its own
        # already-solved 20-year gas capex schedule (/tmp/scenario2_20yr_gas_capex.npz's own
        # 'peak' array). Not required unless the social-cost/RGGI mixin is actually used.
        self.peak_gas_mw = peak_gas_mw

    def get_existing_new_mw(self, year):
        """Scenario 2's own split: existing fleet by type (CT + CCGT, via compute_scenario2_
        gas_replacement.py's own existing_fleet_mw_by_type()) vs. new-build back-computed from
        this year's own peak gas MW -- the exact split every Scenario 2 Tier 1/2/RGGI script
        already used independently before this refactor (Internal Debugging Log #53)."""
        if self.peak_gas_mw is None:
            raise ValueError(
                f"Scenario2Solver.get_existing_new_mw({year}) called but peak_gas_mw was never "
                f"set -- pass it at __init__ time if social-cost/RGGI calculation is needed.")
        import compute_scenario2_gas_replacement as c10
        ct_avail, ccgt_avail = c10.existing_fleet_mw_by_type(year)
        existing_mw = ct_avail + ccgt_avail
        new_mw = max(0.0, self.peak_gas_mw - existing_mw)
        return existing_mw, new_mw

    def lifecycle_cost(self, ccgt_capex_basis='central'):
        """Full annualised cost: capital and FOM on every asset, plus the LP's operating cost.

        WHY THIS IS NOT result['obj']. build_scenario2_problem is dispatch-only -- its objective
        carries fuel, VOM, storage cycling, export revenue and the unserved penalty, and NO CAPITAL
        WHATSOEVER. Everything is pinned, so there is nothing for the LP to trade capital against.
        Reading result['obj'] as a scenario cost understates Scenario 2 by billions, and does so in
        the direction that flatters the baseline the whitepaper is measured against.

        CAPITAL IS CHARGED ON NEW BUILD ONLY. Charging it on the existing fleet would bill Dominion
        twice for plant already paid for; charging none would treat ~10 GW of new gas and ~11 GW of
        new solar as free. FOM applies to existing capacity too -- an already-paid-for plant still
        costs money to keep available.
        """
        if self.result is None:
            raise RuntimeError('lifecycle_cost() called before solve()')

        from gas_lifecycle_cost import CCGT_CAPEX_KW
        from gas_merit_order import GasMeritOrder
        from scenario_lifecycle_cost import ScenarioLifecycleCost

        x, IDX = self.result['raw'].x, self.result['problem']['IDX']
        peak_gas_mw = max(x[t * 14 + IDX['g']] for t in range(len(self.demand)))
        existing_gas_mw = GasMeritOrder().total_available_mw(self.year)

        c = ScenarioLifecycleCost(self.year, operating_cost_usd=self.result['obj'])
        c.add_asset('solar',
                    existing_mw=lp.exist_solar_mw(self.year),
                    new_mw=self.result['vcea_new_build_mw'],
                    capex_usd_per_kw=lp.SOLAR_CAPEX,
                    fixed_om_usd_per_kw_yr=lp.SOLAR_OM,
                    note='new build is the statutory target net of post-VCEA capacity delivered')
        c.add_asset('storage_sodium_power',
                    existing_mw=0.0, new_mw=self.result['na_power_mw'],
                    capex_usd_per_kw=lp.NA_POWER_CAPEX,
                    fixed_om_usd_per_kw_yr=lp.NA_POWER_CAPEX * assumptions.STOR_FOM_PCT,
                    note='statutory short-duration floor; no existing fleet credited')
        # Storage ENERGY is priced per kWh, so it enters as a $/kW figure on an equivalent-MW basis
        # rather than through add_asset's power convention. Kept separate and labelled, because
        # silently folding energy capex into a power figure is exactly the units error
        # AnnualizedCost.units_plausibility_check exists to catch.
        c.add_asset('storage_sodium_energy',
                    existing_mw=0.0,
                    new_mw=self.result['na_power_mw'] * self.result['na_duration_hr'],
                    capex_usd_per_kw=lp.NA_ENERGY_CAPEX,
                    fixed_om_usd_per_kw_yr=0.0,
                    note='MW figure is MWh of energy capacity; capex is $/kWh')
        c.add_asset('storage_ironair_energy',
                    existing_mw=0.0,
                    new_mw=self.result['fe_power_mw'] * lp.FE_DURATION,
                    capex_usd_per_kw=lp.FE_ENERGY_CAPEX,
                    fixed_om_usd_per_kw_yr=0.0,
                    note='MW figure is MWh of energy capacity; capex is $/kWh')
        # NEW CAPACITY IS WHAT WAS BUILT, NOT WHAT DISPATCH HAPPENED TO REACH. This read
        # `new_mw = max(0.0, peak_gas_mw - existing_gas_mw)`, inferring the build from the peak
        # hour -- which was defensible while gas ran against an unbounded ceiling and nothing
        # declared a build, but understates capacity in any year whose peak falls below what was
        # installed. A plant that runs below nameplate is still paid for. See build log 154.
        new_gas_mw = self.new_gas_capacity_mw()
        c.add_asset('gas',
                    existing_mw=existing_gas_mw,
                    new_mw=new_gas_mw,
                    capex_usd_per_kw=CCGT_CAPEX_KW[ccgt_capex_basis],
                    fixed_om_usd_per_kw_yr=assumptions.CCGT_FOM_KW_YR,
                    note=f'{new_gas_mw:,.0f} MW new combined cycle, '
                         f'{round(new_gas_mw / assumptions.CCGT_REFERENCE_UNIT_MW)} x '
                         f'{assumptions.CCGT_REFERENCE_UNIT_MW:,.0f} MW reference units; '
                         f'capex basis {ccgt_capex_basis}')
        self.result['lifecycle_cost'] = c
        return c

    def solve(self, gas_price_mwh, return_hourly=True, ccgt_mw=None,
              na_duration_hr=None, unbounded_gas_ceiling_mw=200_000.0,
              deduct_existing_post_vcea=True):
        """Dispatch the statutory build and let gas fill the residual.

        BROKEN UNTIL 2026-09-13: this passed six arguments to build_scenario2_problem(), which
        requires thirteen. Every call raised TypeError. The scenario had never been runnable
        through the solver class.

        THE PINNED CAPACITIES ARE THE WHOLE POINT. Scenario 2 is the baseline -- Dominion's
        approach of building only what the Code specifically names -- so solar, short-duration and
        long-duration storage are all FIXED inputs, not build variables. build_scenario2_problem()
        is dispatch-only (NVAR = 14 x T, no build block), which is exactly right for this. If any
        of the three were optimised instead, the run would be a partially-optimised hybrid rather
        than Dominion's approach, and the baseline point would move toward the least-cost curve for
        the wrong reason.

        GAS IS EFFECTIVELY UNBOUNDED by decision (2026-09-13). The docstring for
        build_scenario2_problem describes CCGT as "sized externally to cover the worst hour with
        zero storage credit", but that external sizing lived in /tmp/scenario2_20yr_gas_capex.npz,
        a temp file that did not survive any session. Rather than invent a replacement, gas runs
        against a ceiling high enough never to bind, and THE RESULTING PEAK IS AN OUTPUT: how much
        gas capacity the statutory build implies. That is a better question than whether Dominion's
        gas fits a number we made up.

        WHAT THIS CANNOT TELL YOU is the CCGT/CT split within that peak. This function has one gas
        variable and one gas price -- no merit order -- so everything is CCGT by construction. Even
        with the merit order the LP would pick CCGT for peaking duty, since it is cheapest on
        marginal cost and minimum up/down times are not modelled. See
        assumptions.GAS_UNIT_COMMITMENT_NOT_MODELLED.
        """
        self.verify_input_data()
        if na_duration_hr is None:
            # 4-hour, by decision 2026-09-13. The Code names MW, not MWh, so duration is an
            # INTERPRETATION rather than a requirement -- and it is the single largest
            # discretionary number in the baseline. 4-hour is the conventional assumption and
            # matches DISTRIBUTED_STORAGE_DURATION_HR.
            na_duration_hr = assumptions.DISTRIBUTED_STORAGE_DURATION_HR
        if ccgt_mw is None:
            # BOUNDED BY THE REAL FLEET, corrected 2026-09-14 (build log 154). This read
            # `ccgt_mw = unbounded_gas_ceiling_mw` -- 200,000 MW -- so the published run dispatched
            # gas the fleet does not have and reported ZERO unserved energy, while a run bounded by
            # apply_gas_cap showed 30.05 TWh at 2045 over 5,671 hours. Two specifications, and
            # every figure downstream rested on the wrong one.
            #
            # unbounded_gas_ceiling_mw is retained for diagnostic callers that deliberately want an
            # unbounded solve -- measuring what gas WOULD serve, as distinct from what the fleet
            # CAN. Passing it is now explicit rather than the default.
            ccgt_mw = self.apply_gas_cap()
        # THE STATUTORY TARGET IS A TOTAL, NOT AN INCREMENT (corrected 2026-09-13).
        #
        # build_scenario2_problem subtracts BOTH exist_solar and vcea_solar_mw from demand, so
        # passing the full 16,100 MW alongside the existing fleet treated the target as entirely
        # new build on top of everything already there. It is not: § 56-585.5 D.4 requires Dominion
        # to petition the SCC annually for new solar, and that process is the statutory mechanism
        # the 16,100 MW is measured by. Capacity approved through it counts toward the target.
        #
        # Only 645 MW of the existing 5,300 predates the VCEA. The other ~4,655 MW counts, so the
        # NEW build required is ~11,445 MW. The uncorrected version overstated Scenario 2's clean
        # generation share by about four percentage points.
        # YEAR-AWARE since 2026-09-13. The earlier call passed no year and returned the full
        # remaining target in every checkpoint, so Scenario 2 built the entire statutory fleet in
        # 2030 -- five years before the # D.2 deadline -- and overstated that checkpoint's clean
        # share. The trajectory is linear to 2035 then flat; see assumptions.vcea_new_solar_mw for
        # why linear is the neutral reading of a statute with one deadline and no interim
        # milestones.
        vcea_new_mw = (assumptions.vcea_new_solar_mw(self.year, self.vcea_solar_mw)
                       if deduct_existing_post_vcea else self.vcea_solar_mw)
        # THE C.2 CARVE-OUT TAKES ITS SHARE FROM WITHIN THE CAPPED TOTAL, not on top of it. See
        # assumptions.SCENARIO2_SOLAR_CAP_IS_AN_ASSUMPTION for why that is an assumption rather
        # than a reading of the Code, and what it costs: utility-scale falls from about 13,244 MW
        # at 2035 to 9,238 MW at 2045 as the energy obligation outgrows the capacity target.
        _dist_mw, _util_mw = self.solar_split_mw(new_build_mw=vcea_new_mw)
        _dist_cf = _distributed_design_year_cf()
        vcea_new_mw = _util_mw

        problem = lp.build_scenario2_problem(
            self.solar_cf, self.wind_cf, self.nuclear, self.exist_solar, self.demand,
            vcea_solar_mw=vcea_new_mw,
            dist_solar_mw=_dist_mw, dist_solar_cf=_dist_cf,
            ccgt_mw=ccgt_mw,
            na_power_mw=drv.vcea_short_duration_floor_mw(self.year),
            na_duration_hr=na_duration_hr,
            fe_power_mw=drv.vcea_long_duration_floor_mw(self.year),
            fe_duration_hr=lp.FE_DURATION,
            gas_price_mwh=gas_price_mwh,
            ccgt_vom_mwh=assumptions.CCGT_VOM_MWH,
            verbose=False)
        res = lp.solve_problem(problem)
        # Scenario 2's own extraction convention differs from run_solve()'s (Appendix C) --
        # kept as its own path rather than forced into Scenario1Solver's own result shape.
        self.result = dict(status=res.status, success=res.success, obj=res.fun, raw=res,
                           problem=problem, ccgt_ceiling_mw=ccgt_mw,
                           vcea_target_mw=self.vcea_solar_mw, vcea_new_build_mw=vcea_new_mw,
                           na_power_mw=drv.vcea_short_duration_floor_mw(self.year),
                           na_duration_hr=na_duration_hr,
                           fe_power_mw=drv.vcea_long_duration_floor_mw(self.year))
        return self.result
