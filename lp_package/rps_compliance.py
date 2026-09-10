"""
rps_compliance.py

Computes STATUTORY RPS compliance under Va. Code § 56-585.5, as a layer alongside — never
replacing — the physical generation-share formulation in lp_model.build_problem().

WHY BOTH (decision recorded 2026-09-10, see docs/methodology/
Demand_Basis_and_RPS_Compliance_Working_Notes.md):

The two formulations answer different questions and the analysis needs both answers.

  PHYSICAL (lp_model.build_problem): gas <= frac * (gas + clean), where clean includes nuclear.
    Asks: what fleet must EXIST so that X% of electricity generated is carbon-free?
    At 2045 with frac=0 this requires new build to cover roughly 121,000 GWh.

  STATUTORY (this module): RECs retired >= pct * total_electric_energy, where
    total_electric_energy is Virginia retail SALES less in-Commonwealth nuclear operating by
    July 1 2020, less certified accelerated clean energy buyer load, less § H legacy customers.
    Asks: how many certificates must the utility RETIRE?
    At 2045 the same 100% headline covers roughly 75,000 GWh.

Same percentage, materially different requirement. Neither is wrong; they measure different things.

WHY NOT REPLACE THE PHYSICAL BASIS WITH THIS ONE: the RPS is certificate accounting and says
nothing about whether load is served. Every reliability finding this project has produced — the
seasonal iron-air drawdown, the 8-year adequacy cross-test, storage sizing, the pre-dawn failure
pattern — depends on hourly dispatch and is inexpressible in a REC framework.

WHY NOT KEEP ONLY THE PHYSICAL BASIS: the deliverables describe the scenarios as modeling
statutory compliance, and they do not. A reviewer reading § 56-585.5(A) would find the model
enforces something stricter — requiring new clean build to cover load that Surry and North Anna
already serve. The statutory basis also surfaces the accelerated-clean-energy-buyer lever, which
does not exist as a concept in the generation-share formulation and is plausibly the statute's own
answer to the demand-growth problem this project is about.

NAMING DISCIPLINE (Rule 12): the two results must never both be called "compliance." This module
returns statutory_rps_obligation_mwh; the physical requirement keeps its own name. Reporting one
without the other is the specific failure this dual-basis structure exists to prevent.
"""
import driver


# Statutory constants, § 56-585.5(D)(5). Rule 6: the RPS percentage schedule itself is NOT
# duplicated here -- driver.RPS_CLEAN_PCT_PHASE_II is already a direct transcription of the
# statute's own table and is referenced instead.
DEFICIENCY_PAYMENT_BASE_RATE_PER_MWH = 45.0
DEFICIENCY_PAYMENT_BASE_YEAR = 2021
DEFICIENCY_PAYMENT_ANNUAL_ESCALATION = 0.01
DEFICIENCY_PAYMENT_SUB_ONE_MW_RATE_PER_MWH = 75.0
DEFICIENCY_PAYMENT_GEOTHERMAL_RATE_PER_MWH = 100.0

# § 56-585.5(A), "Accelerated clean energy buyer" -- aggregate load threshold.
ACCELERATED_CLEAN_ENERGY_BUYER_THRESHOLD_MW = 25.0

# § 56-585.5(C)(3) -- from the 2027 compliance year, at least this share of RECs must come from
# RPS eligible resources located in the Commonwealth.
IN_COMMONWEALTH_REC_MINIMUM_SHARE = 0.75
IN_COMMONWEALTH_REC_MINIMUM_FIRST_YEAR = 2027

# § 56-585.5(C)(2) -- distributed carve-out: share of the RPS requirement that must come from
# solar/wind/anaerobic digestion resources of one megawatt or less located in the Commonwealth.
DISTRIBUTED_CARVE_OUT_SHARE_2026_THROUGH_2030 = 0.045
DISTRIBUTED_CARVE_OUT_SHARE_2031_THROUGH_2045 = 0.05


def deficiency_payment_rate_per_mwh(year, rate_category='standard'):
    """§ 56-585.5(D)(5). Base rate escalates one percent annually after 2021.

    rate_category selects among the three rates the statute names: 'standard' ($45),
    'sub_one_mw' ($75, for shortfalls in sub-1 MW Virginia solar/wind/anaerobic digestion),
    'geothermal' ($100). Rule 5: an unrecognized category raises rather than silently
    falling back to the standard rate, since a wrongly-cheap deficiency rate would make
    non-compliance look more attractive than it is.
    """
    base_rates = {'standard': DEFICIENCY_PAYMENT_BASE_RATE_PER_MWH,
                  'sub_one_mw': DEFICIENCY_PAYMENT_SUB_ONE_MW_RATE_PER_MWH,
                  'geothermal': DEFICIENCY_PAYMENT_GEOTHERMAL_RATE_PER_MWH}
    if rate_category not in base_rates:
        raise ValueError(
            f"unrecognized rate_category {rate_category!r} -- expected one of "
            f"{sorted(base_rates)}. § 56-585.5(D)(5) names exactly these three rates.")
    if year < DEFICIENCY_PAYMENT_BASE_YEAR:
        raise ValueError(
            f"year {year} precedes the deficiency payment's own base year "
            f"({DEFICIENCY_PAYMENT_BASE_YEAR}); the statute provides no rate before then.")
    years_escalated = year - DEFICIENCY_PAYMENT_BASE_YEAR
    return base_rates[rate_category] * (1 + DEFICIENCY_PAYMENT_ANNUAL_ESCALATION) ** years_escalated


class StatutoryComplianceBase:
    """The § 56-585.5(A) "total electric energy" denominator for one compliance year.

    Deliberately a class rather than a function (Rule 1): the denominator has several
    independently-sourced components that callers need to inspect and report separately, and
    the accelerated-clean-energy-buyer component is a scenario variable rather than a fixed
    input. Bundling them keeps the derivation visible instead of collapsing it into one number.

    All quantities in MWh.
    """

    def __init__(self, year, virginia_retail_sales_mwh, in_commonwealth_nuclear_generation_mwh,
                 accelerated_clean_energy_buyer_load_mwh,
                 legacy_competitive_service_load_mwh=0.0):
        if virginia_retail_sales_mwh is None or virginia_retail_sales_mwh <= 0:
            raise ValueError(
                f"{year}: virginia_retail_sales_mwh is required and must be positive. This is the "
                "§ 56-585.5(A) base before exclusions -- Virginia retail SALES, not total load and "
                "not VA+NC DOM LSE. See the working notes: the project's cached annual totals are "
                "Appendix 2B-1 (Total DOM LSE), which is the wrong table for this purpose.")
        if in_commonwealth_nuclear_generation_mwh is None:
            raise ValueError(
                f"{year}: in_commonwealth_nuclear_generation_mwh is required. Rule 5 -- passing "
                "zero silently would overstate the obligation by roughly 30%, since § 56-585.5(A) "
                "excludes energy from in-Commonwealth nuclear operating by July 1, 2020 (Surry, "
                "North Anna). If the intent is genuinely no exclusion, pass 0.0 explicitly.")
        if accelerated_clean_energy_buyer_load_mwh is None:
            raise ValueError(
                f"{year}: accelerated_clean_energy_buyer_load_mwh is required. Rule 5 -- ACEB "
                "participation is a behavioral scenario variable, not a knowable constant: "
                "customers over 25 MW aggregate load must actually contract under subsection G "
                "AND be certified by the Commission. Pass 0.0 for a no-participation scenario, "
                "explicitly, rather than leaving it to default.")
        self.year = year
        self.virginia_retail_sales_mwh = virginia_retail_sales_mwh
        self.in_commonwealth_nuclear_generation_mwh = in_commonwealth_nuclear_generation_mwh
        self.accelerated_clean_energy_buyer_load_mwh = accelerated_clean_energy_buyer_load_mwh
        self.legacy_competitive_service_load_mwh = legacy_competitive_service_load_mwh

    def total_electric_energy_mwh(self):
        """§ 56-585.5(A). Floored at zero -- the exclusions cannot produce a negative base."""
        base = (self.virginia_retail_sales_mwh
                - self.in_commonwealth_nuclear_generation_mwh
                - self.accelerated_clean_energy_buyer_load_mwh
                - self.legacy_competitive_service_load_mwh)
        return max(0.0, base)

    def exclusion_breakdown(self):
        """Each exclusion as a share of unadjusted sales, for reporting the derivation."""
        sales = self.virginia_retail_sales_mwh
        return {
            'virginia_retail_sales_mwh': sales,
            'nuclear_excluded_mwh': self.in_commonwealth_nuclear_generation_mwh,
            'nuclear_excluded_share': self.in_commonwealth_nuclear_generation_mwh / sales,
            'aceb_excluded_mwh': self.accelerated_clean_energy_buyer_load_mwh,
            'aceb_excluded_share': self.accelerated_clean_energy_buyer_load_mwh / sales,
            'legacy_excluded_mwh': self.legacy_competitive_service_load_mwh,
            'total_electric_energy_mwh': self.total_electric_energy_mwh(),
            'base_as_share_of_sales': self.total_electric_energy_mwh() / sales,
        }


class StatutoryRPSObligation:
    """Required REC retirement for one compliance year, and the cost of not meeting it.

    Pairs with — never substitutes for — the physical clean-generation requirement produced by
    the LP. See this module's docstring for why both are reported.
    """

    def __init__(self, compliance_base, eligible_rec_generation_mwh, utility_phase='II'):
        if utility_phase not in ('I', 'II'):
            raise ValueError(f"utility_phase must be 'I' or 'II', got {utility_phase!r}")
        if utility_phase == 'I':
            raise NotImplementedError(
                "Phase I percentages differ from Phase II and are not yet transcribed into "
                "driver.RPS_CLEAN_PCT_PHASE_II (which is Phase II only, as its name states). "
                "Rule 5 -- raising rather than silently applying Phase II percentages to a "
                "Phase I utility. See docs/statutes/56-585.5.md § C.1.a for the Phase I column.")
        self.compliance_base = compliance_base
        self.eligible_rec_generation_mwh = eligible_rec_generation_mwh
        self.utility_phase = utility_phase

    def required_percentage(self):
        """§ 56-585.5(C)(1)(a). Uses driver's own transcription of the statutory table (Rule 6)."""
        year = self.compliance_base.year
        if year > 2045:
            return 1.00  # "2045 and thereafter"
        if year not in driver.RPS_CLEAN_PCT_PHASE_II:
            raise KeyError(
                f"no statutory RPS percentage for {year} in driver.RPS_CLEAN_PCT_PHASE_II "
                f"(covers {min(driver.RPS_CLEAN_PCT_PHASE_II)}-{max(driver.RPS_CLEAN_PCT_PHASE_II)}).")
        return driver.RPS_CLEAN_PCT_PHASE_II[year]

    def required_rec_mwh(self):
        return self.required_percentage() * self.compliance_base.total_electric_energy_mwh()

    def shortfall_mwh(self):
        """Floored at zero -- surplus generation is not a negative shortfall. Note § 56-585.5(C)(4)
        permits banking excess RECs for five years, which this does NOT model."""
        return max(0.0, self.required_rec_mwh() - self.eligible_rec_generation_mwh)

    def deficiency_payment_dollars(self):
        """§ 56-585.5(D)(5) at the standard rate.

        This is the economic ceiling on compliance cost, and it is why the statutory and physical
        bases can diverge in PRACTICE and not merely in accounting: a utility facing a physical
        build cost above this rate can lawfully pay the deficiency instead of building.
        """
        return self.shortfall_mwh() * deficiency_payment_rate_per_mwh(
            self.compliance_base.year, 'standard')

    def distributed_carve_out_mwh(self):
        """§ 56-585.5(C)(2): share of the RPS requirement that must come from Virginia-located
        solar/wind/anaerobic digestion resources of one megawatt or less. Returns 0.0 outside
        the 2026-2045 window the statute specifies."""
        year = self.compliance_base.year
        if 2026 <= year <= 2030:
            share = DISTRIBUTED_CARVE_OUT_SHARE_2026_THROUGH_2030
        elif 2031 <= year <= 2045:
            share = DISTRIBUTED_CARVE_OUT_SHARE_2031_THROUGH_2045
        else:
            return 0.0
        return share * self.required_rec_mwh()

    def summary(self):
        return {
            'year': self.compliance_base.year,
            'required_percentage': self.required_percentage(),
            'total_electric_energy_mwh': self.compliance_base.total_electric_energy_mwh(),
            'required_rec_mwh': self.required_rec_mwh(),
            'eligible_rec_generation_mwh': self.eligible_rec_generation_mwh,
            'shortfall_mwh': self.shortfall_mwh(),
            'deficiency_rate_per_mwh': deficiency_payment_rate_per_mwh(
                self.compliance_base.year, 'standard'),
            'deficiency_payment_dollars': self.deficiency_payment_dollars(),
            'distributed_carve_out_mwh': self.distributed_carve_out_mwh(),
        }


# ---------------------------------------------------------------------------
# NOT YET IMPLEMENTED -- Activity Tracker ID 55, priority 2
#
# REC BANKING (§ 56-585.5(C)(4)): excess RECs may be applied "in the year in which it was
# generated and the five calendar years after" -- a six-year validity window. This module is
# single-year and does not model it, so a utility's ability to smooth compliance across years by
# banking surplus is currently absent from every figure produced here.
#
# The tracked feature is deliberately BEHAVIORAL rather than accounting-only: it should model the
# utility's economic CHOICE between banking surplus and paying the § 56-585.5(D)(5) deficiency,
# in order to locate the point at which the deficiency ceiling (~$57/MWh by 2045) becomes cheaper
# than building -- against a 2045 physical SLCOE modeled near $133/MWh. That crossover is the
# weakness in the compliance regime the analysis is looking for.
#
# Design sketch, ordering decisions already reasoned through: a RECBank holding vintaged balances;
# retire FIFO (oldest vintage first, since those expire soonest); expire AFTER retirement (vintage
# Y is valid THROUGH Y+5, so during Y+5 it remains usable). A MultiYearComplianceTrajectory
# sequences years and owns the bank; the single-year classes above stay unchanged and are used
# inside it.
#
# Open question carried into that work: whether the § C.2 distributed and § C.1.b geothermal
# carve-outs bank in separate vintage pools. Recommended conservative reading is that they do.
# ---------------------------------------------------------------------------


def compare_bases(statutory_obligation, physical_clean_requirement_mwh):
    """Reports the two bases together. This is the intended reporting entry point.

    The GAP is the finding: the distance between what the statute compels and what physical
    decarbonization requires. Reporting either number alone is what the dual-basis structure
    exists to prevent (see module docstring, NAMING DISCIPLINE).
    """
    statutory = statutory_obligation.required_rec_mwh()
    return {
        'statutory_rps_obligation_mwh': statutory,
        'physical_clean_generation_requirement_mwh': physical_clean_requirement_mwh,
        'gap_mwh': physical_clean_requirement_mwh - statutory,
        'statutory_as_share_of_physical': (statutory / physical_clean_requirement_mwh
                                            if physical_clean_requirement_mwh else None),
        'deficiency_payment_ceiling_per_mwh': deficiency_payment_rate_per_mwh(
            statutory_obligation.compliance_base.year, 'standard'),
    }
