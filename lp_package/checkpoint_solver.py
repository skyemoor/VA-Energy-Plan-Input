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
import numpy as np
import lp_model as lp
import driver as drv


class CheckpointSolver:
    """Base class for a single checkpoint's own year-solve (Appendix P.1's
    "checkpoint solve" -- optimizer decides both build and dispatch).
    Handles what every scenario shares: building the problem, applying
    the gas capacity cap, and verifying the result against this project's
    own standing requirements (Appendix P.2 #11/#13/#14) before it can be
    treated as final."""

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
            self.nuclear, capacity_cap_mw=cap, return_hourly=return_hourly, **run_solve_kwargs)
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

    def converge_and_solve(self, start_frac=None, tol=0.003, max_iter=3):
        """Converges frac against this checkpoint's own gas_target_share (linking included
        throughout, not bolted on after convergence -- linking changes the LP's own energy
        balance, so frac convergence without it can converge to the wrong value)."""
        self.verify_input_data()
        cap = self.apply_gas_cap()
        prior_kwargs = self._prior_kwargs()
        frac, converge_result, history = drv.converge_frac(
            self.year, self.gas_target_share, self.demand, self.exist_solar, self.solar_cf,
            self.wind_cf, self.nuclear, tol=tol, max_iter=max_iter, capacity_cap_mw=cap,
            start_frac=start_frac, **prior_kwargs)
        self.converged_frac = frac
        self.result = drv.run_solve(
            self.year, frac, self.demand, self.exist_solar, self.solar_cf, self.wind_cf,
            self.nuclear, capacity_cap_mw=cap, return_hourly=True, **prior_kwargs)
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

    def _converge_and_solve_with_reserve(self, reserve_margin_hint, IRM, start_frac=None, tol=0.003, max_iter=3):
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
        frac, converge_result, history = drv.converge_frac(
            self.year, self.gas_target_share, self.demand, self.exist_solar, self.solar_cf,
            self.wind_cf, self.nuclear, tol=tol, max_iter=max_iter, capacity_cap_mw=cap,
            start_frac=start_frac, **prior_kwargs, **dist_kwargs)
        self.converged_frac = frac
        result = drv.run_solve(
            self.year, frac, self.demand, self.exist_solar, self.solar_cf, self.wind_cf,
            self.nuclear, capacity_cap_mw=cap, return_hourly=True,
            reserve_margin_hint=reserve_margin_hint, IRM=IRM, **prior_kwargs, **dist_kwargs)
        self.result = result
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


class Scenario1WithReserveMargin(ReserveMarginMixin, Scenario1Solver):
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

    def converge_and_solve(self, start_frac=None, tol=0.003, max_iter=3):
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
        frac, converge_result, history = drv.converge_frac(
            self.year, self.gas_target_share, self.demand, self.exist_solar, self.solar_cf,
            self.wind_cf, self.nuclear, tol=tol, max_iter=max_iter, capacity_cap_mw=cap,
            start_frac=start_frac, **prior_kwargs, **dist_kwargs)
        self.converged_frac = frac
        self.result = drv.run_solve(
            self.year, frac, self.demand, self.exist_solar, self.solar_cf, self.wind_cf,
            self.nuclear, capacity_cap_mw=cap, return_hourly=True,
            **prior_kwargs, **dist_kwargs)
        self.verify_result()
        prior_solar_degraded = prior_kwargs['prior_solar_mw']
        prior_dist_solar_degraded = prior_kwargs['prior_distributed_solar_mw']
        self.result['S_mw_total'] = self.result['S_mw'] + prior_solar_degraded
        self.result['dist_S_mw_total'] = self.result['dist_S_mw'] + prior_dist_solar_degraded
        self.result['year'] = self.year
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


class Scenario3WithReserveMargin(ReserveMarginMixin, Scenario3Solver):
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

    def solve(self, gas_price_mwh, return_hourly=True):
        self.verify_input_data()
        problem = lp.build_scenario2_problem(
            self.solar_cf, self.wind_cf, self.nuclear, self.exist_solar, self.demand,
            self.vcea_solar_mw, gas_price_mwh=gas_price_mwh)
        res = lp.solve_problem(problem)
        # Scenario 2's own extraction convention differs from run_solve()'s (Appendix C) --
        # kept as its own path rather than forced into Scenario1Solver's own result shape.
        self.result = dict(status=res.status, success=res.success, obj=res.fun, raw=res)
        return self.result
