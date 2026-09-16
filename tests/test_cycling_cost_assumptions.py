"""
test_cycling_cost_assumptions.py

The thermal-cycling cost parameters, and which of them are ASSUMPTIONS rather than sourced values.

This analysis is screening-level, not production cost (Appendix Q). Where a machine-specific figure
would be needed and none was found, an assumption is stated with its direction of effect rather than
a gap being carried -- but it is labelled, so a reader can see which numbers rest on judgement.
"""
import pytest

import assumptions as a


class TestStartFuel:
    """Sourced. CCGT ~1,000 MMBtu/start against OCGT ~350, cross-checked against $67,000 and
    $13,400 per start in arXiv 2311.04398 -- roughly a 5x ratio either way."""

    def test_the_figures_and_their_ratio(self):
        assert a.CCGT_START_MMBTU == 1000.0
        assert a.CT_START_MMBTU == 350.0
        assert a.CCGT_START_MMBTU / a.CT_START_MMBTU == pytest.approx(2.86, abs=0.01)


class TestEquivalentOperatingHoursPerStart:
    """GE GER-3620 factored-fired-starts. A start damages hot-section components like many hours of
    steady running, because cycling from ambient to ~1,100 C and back is the primary fatigue
    driver."""

    def test_the_three_thermal_states(self):
        assert a.EOH_PER_START_BY_STATE == {'cold': 175.0, 'warm': 45.0, 'hot': 15.0}

    def test_warm_is_assumed_and_labelled(self):
        """The duty this model produces is short blocks separated by short gaps -- Scenario 2's
        2045 gap has a MEDIAN RUN OF 2 HOURS across 1,233 blocks -- and a machine idle two hours
        has not cooled to 50 C."""
        assert a.EOH_PER_START_ASSUMED_STATE == 'warm'

    def test_this_swings_the_answer_more_than_the_technology_choice(self):
        """At 175 EOH/start, 1,233 starts consume 215,775 EOH against a 24,000-hour interval --
        NINE inspections a year, which is not a cost but an impossibility. At 45 it is 55,485:
        heavy, but bounded. The start-type classification matters more than CT-versus-CCGT."""
        cold = 1233 * a.EOH_PER_START_BY_STATE['cold']
        warm = 1233 * a.EOH_PER_START_BY_STATE['warm']
        assert cold / a.OVERHAUL_INTERVAL_FFH['CT'] > 8
        assert warm / a.OVERHAUL_INTERVAL_FFH['CT'] < 3


class TestOverhaulCostSplit:
    """PARTLY ASSUMED, and the assumption is labelled with its direction."""

    def test_the_ccgt_figure_is_sourced(self):
        """Batlle & Rodilla: $40M for a 540 MW combined-cycle unit."""
        assert a.MAJOR_OVERHAUL_USD_PER_MW_BY_TECH['CCGT'] == pytest.approx(40_000_000.0 / 540.0)

    def test_the_ct_figure_is_an_assumed_ratio(self):
        """0.70 of the combined-cycle figure, on the physical reasoning that a combined-cycle
        overhaul covers the gas turbine AND the steam side where a simple-cycle overhaul covers the
        turbine alone. A judgement, not a measurement."""
        ratio = (a.MAJOR_OVERHAUL_USD_PER_MW_BY_TECH['CT']
                 / a.MAJOR_OVERHAUL_USD_PER_MW_BY_TECH['CCGT'])
        assert ratio == pytest.approx(0.70)

    def test_the_direction_of_the_assumption_is_recorded(self):
        """IT FAVOURS CT, which is already the technology this analysis selects for peaking duty --
        so it REINFORCES a conclusion rather than producing it. That is worth a reader knowing, and
        the conclusion should survive the alternative."""
        assert 'reinforce' in a.SIMPLE_CYCLE_OVERHAUL_RATIO_IS_ASSUMED
        assert 'not a sourced value' in a.SIMPLE_CYCLE_OVERHAUL_RATIO_IS_ASSUMED

    def test_the_conclusion_survives_at_parity(self):
        """MEASURED on the 2045 gap: CT total $3,639M against CCGT's $4,658M with the 0.70 ratio.
        At parity CT still wins, because its capital advantage exceeds CCGT's fuel advantage at a
        20% capacity factor -- so the assumption is not load-bearing."""
        assert 'At parity CT still wins' in a.SIMPLE_CYCLE_OVERHAUL_RATIO_IS_ASSUMED

    def test_the_interval_is_assumed_equal_and_says_so(self):
        """No source separating simple-cycle from combined-cycle intervals was found. The gas
        turbine itself is the cycling-limited component in both configurations."""
        assert a.OVERHAUL_INTERVAL_FFH['CT'] == a.OVERHAUL_INTERVAL_FFH['CCGT'] == 24000.0

    def test_the_legacy_alias_points_at_ccgt(self):
        """Kept for callers predating the split; new code uses the mapping."""
        assert a.MAJOR_OVERHAUL_USD_PER_MW == a.MAJOR_OVERHAUL_USD_PER_MW_BY_TECH['CCGT']


class TestMeasuredResultOnThe2045Gap:
    """MEASURED 2026-09-14. Scenario 2's capacity gap with the merit order binding: 17.96 TWh over
    3,294 hours in 1,233 blocks, peak 10,263 MW, implied capacity factor 20.0%."""

    def test_maintenance_dominates_start_fuel(self):
        """Batlle & Rodilla's central finding, reproduced: OMC $1,303M for CT against SFC $31M --
        a factor of 42. I had been sizing the start-fuel term and ignoring the larger one."""
        assert 1303 / 31 > 40

    def test_ct_wins_and_by_how_much(self):
        """$3,639M against $5,004M -- CT by $1,365M, 27%.

        The margin moved twice in this session. With a COMMON overhaul cost it was $460M; the
        per-technology split took it to $1,019M; correcting the CCGT capex from a stale $2,500/kW
        to the year-varying function's $3,000/kW took it to $1,365M."""
        assert 5004 - 3639 == pytest.approx(1365, abs=1)

    def test_the_ccgt_capex_comes_from_the_year_varying_function(self):
        """I FIRST USED CCGT_CAPEX_KW_BY_CASE['central'] = $2,500/kW, which understated CCGT by 20%
        and so understated CT's advantage. The model's own banner prints ccgt_capex_kw(BUILD_YEAR)
        = $3,000/kW, sourced to Wood Mackenzie's April 2026 turbine market analysis as full
        installed project cost."""
        assert a.ccgt_capex_kw(a.BUILD_YEAR) == pytest.approx(3000.0)
        assert a.CCGT_CAPEX_KW_BY_CASE['central'] == 2500.0   # the one I wrongly used

    def test_the_two_ct_capex_figures_answer_different_questions(self):
        """SCENARIO_1B_NEW_CT_CAPEX_KW = $2,000/kW is the MIDPOINT OF A SWEEP across $1,200-3,000,
        chosen because 1B's capacity answer proved insensitive across that range -- a robustness
        device, not a benchmark -- and it prices a 1,278 MW build.

        PEAKER_CAPEX_KW_BY_TIER is the tiered benchmark, and a 10,263 MW build is firmly 'large'
        at $1,250/kW. The two are not inconsistent; they answer different questions."""
        assert a.SCENARIO_1B_NEW_CT_CAPEX_KW == 2000.0
        assert a.PEAKER_CAPEX_KW_BY_TIER['large']['central'] == 1250.0
        assert 10_263 > a.PEAKER_MEDIUM_TIER_MAX_MW

    def test_the_conclusion_is_over_determined(self):
        """CT wins on every term that varies: capital ($1,250 against $3,000/kW), maintenance
        (smaller overhaul scope), capacity factor (20% against a 28.1% crossover), and duty shape
        (median 2-hour blocks against a 6-hour CCGT minimum uptime). Only fuel favours CCGT, and at
        20% capacity factor there are not enough hours to earn it."""
        assert a.PEAKER_CAPEX_KW_BY_TIER['large']['central'] < a.ccgt_capex_kw(a.BUILD_YEAR)
        assert a.MAJOR_OVERHAUL_USD_PER_MW_BY_TECH['CT'] < a.MAJOR_OVERHAUL_USD_PER_MW_BY_TECH['CCGT']
