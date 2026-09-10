"""
test_provenance.py

Baseline-locked tests for provenance.py, following Software_Engineering_Standards Rule 2.

Each test class names the specific real failure it guards against, so a future reader understands
the class of error without re-reading the full session history. Baselines are the actual figures
from this project's own work, not synthetic stand-ins (Rule 2.2).
"""
import json
import os
import tempfile
import pytest

from provenance import (AssumptionRecord, ResultRecord, RunManifest, ProvenanceRegister,
                        VALID_RESULT_STATUSES)


class TestStaleDerivedFigureDetection:
    """Guards the PWC-parking failure: revising one assumption silently invalidated a downstream
    figure with nothing flagging it.

    Real chain: the Prince William parking estimate fed the four-county NoVA total (6,159.0 MW),
    which was the fleet basis for the six-day lookahead firming figure (~4.3%). Re-basing PWC
    parking from a population anchor to a C&I-footprint anchor moved the total to 4,638.6 MW,
    making the firming figure stale. Nothing caught it at the time.
    """

    def build_real_dependency_chain(self):
        register = ProvenanceRegister()
        register.add_assumption(AssumptionRecord(
            record_id='A-PWC-PARKING',
            description='Prince William County parking-lot solar potential, population-anchored',
            value=1734.7, units='MW'))
        register.add_result(ResultRecord(
            record_id='R-NOVA-TOTAL',
            description='Four-county NoVA distributed solar potential, combined',
            value=6159.0, units='MW', status='current',
            depends_on_assumption_ids=['A-PWC-PARKING']))
        register.add_result(ResultRecord(
            record_id='R-FIRMING-PCT',
            description='Six-day lookahead firming percentage for the NoVA fleet',
            value=4.3, units='percent', status='current',
            depends_on_assumption_ids=['R-NOVA-TOTAL']))
        return register

    def test_direct_dependent_is_found(self):
        register = self.build_real_dependency_chain()
        assert 'R-NOVA-TOTAL' in register.find_results_invalidated_by('A-PWC-PARKING')

    def test_transitive_dependent_is_found(self):
        """The firming figure depends on PWC parking only through the NoVA total. Missing this
        transitive link is exactly how the stale figure survived unnoticed."""
        register = self.build_real_dependency_chain()
        assert register.find_results_invalidated_by('A-PWC-PARKING') == [
            'R-FIRMING-PCT', 'R-NOVA-TOTAL']

    def test_superseded_results_are_excluded(self):
        register = self.build_real_dependency_chain()
        register.results_by_id['R-NOVA-TOTAL'].status = 'superseded'
        register.results_by_id['R-NOVA-TOTAL'].superseded_by = 'R-NOVA-TOTAL-V2'
        invalidated = register.find_results_invalidated_by('A-PWC-PARKING')
        assert 'R-NOVA-TOTAL' not in invalidated

    def test_unknown_assumption_raises_rather_than_reporting_clean(self):
        """Rule 5: returning an empty list for an unregistered assumption would read as 'nothing
        is affected' when it actually means 'this was never tracked'."""
        register = self.build_real_dependency_chain()
        with pytest.raises(KeyError, match='unknown assumption_id'):
            register.find_results_invalidated_by('A-NEVER-REGISTERED')


class TestSupersessionIsExplicit:
    """Guards the multiple-SLCOE-vintages failure: $39.03, $42.45 and $129.28/MWh all existed
    concurrently with no register stating which was current for which scenario and year."""

    def test_real_slcoe_vintages_coexist_with_one_current_per_scenario_year(self):
        register = ProvenanceRegister()
        register.add_result(ResultRecord(
            record_id='R-SLCOE-S1-2030-V1',
            description='Scenario 1 SLCOE, workbook tab, pre-reserve-margin',
            value=39.03, units='$/MWh', scenario='S1', year=2030,
            status='superseded', superseded_by='R-SLCOE-S1-2030-V2'))
        register.add_result(ResultRecord(
            record_id='R-SLCOE-S1-2030-V2',
            description='Scenario 1 SLCOE, Python pipeline with reserve margin',
            value=42.45, units='$/MWh', scenario='S1', year=2030, status='current'))
        register.add_result(ResultRecord(
            record_id='R-SLCOE-S1-2045',
            description='Scenario 1 SLCOE, 2045 checkpoint, 100 percent clean',
            value=129.28, units='$/MWh', scenario='S1', year=2045, status='provisional'))

        current_2030 = register.current_results(scenario='S1', year=2030)
        assert len(current_2030) == 1
        assert current_2030[0].value == 42.45
        # The 2045 figure is provisional, not current -- it rests on a single design weather year
        # and a pinned distributed-solar cap, so it must not be returned as settled.
        assert register.current_results(scenario='S1', year=2045) == []

    def test_superseded_without_successor_raises(self):
        with pytest.raises(ValueError, match='requires superseded_by'):
            ResultRecord(record_id='R-X', description='x', value=1.0, status='superseded')

    def test_invalid_status_raises(self):
        with pytest.raises(ValueError, match='not one of'):
            ResultRecord(record_id='R-X', description='x', value=1.0, status='final')

    def test_valid_statuses_are_the_documented_three(self):
        assert VALID_RESULT_STATUSES == ('current', 'provisional', 'superseded')


class TestRunManifestCapturesReproducibleState:
    """Guards the hand-reconstructed-provenance failure, and the mislabeled-file failure:
    this session hit a .pdf that was plain text, a .pdf that was a ZIP of JPEGs, and two CVOW
    files sharing a filename convention but using different internal layouts. Hashing content
    rather than trusting names is the point."""

    def test_manifest_records_real_2045_run_parameters(self):
        manifest = RunManifest(
            record_id='RUN-2045-S1',
            description='2045 checkpoint, 100 percent clean, distributed solar pinned at siting cap',
            parameters={'year': 2045, 'gas_allowed_frac': 0.0, 'weather_year': '2016-17',
                        'enforce_closing_soc': True, 'distributed_solar_pinned_mw': 7440.0,
                        'distributed_share_of_total_solar': 0.99},
            build_results={'utility_solar_mw': 166340.7, 'iron_air_energy_mwh': 3635866.8},
            solver='highs-ds', runtime_seconds=253.0)
        as_dict = manifest.to_dict()
        assert as_dict['parameters']['gas_allowed_frac'] == 0.0
        assert as_dict['solver'] == 'highs-ds'
        assert as_dict['build_results']['iron_air_energy_mwh'] == 3635866.8

    def test_missing_input_file_is_marked_explicitly_not_silently_empty(self):
        marker = RunManifest.hash_file('/nonexistent/path/to/weather.npz')
        assert marker.startswith('MISSING:')

    def test_identical_content_hashes_identically_regardless_of_filename(self):
        """The mislabeled-extension problem: content identity is what matters, not the name."""
        with tempfile.TemporaryDirectory() as directory:
            first = os.path.join(directory, 'data.pdf')
            second = os.path.join(directory, 'data.txt')
            for path in (first, second):
                with open(path, 'wb') as handle:
                    handle.write(b'National Standard Practice Manual')
            assert RunManifest.hash_file(first) == RunManifest.hash_file(second)

    def test_missing_parameters_raises(self):
        with pytest.raises(ValueError, match='parameters is required'):
            RunManifest(record_id='RUN-X', description='x', parameters=None)

    def test_manifest_round_trips_through_json(self):
        manifest = RunManifest(record_id='RUN-X', description='x', parameters={'year': 2030})
        with tempfile.TemporaryDirectory() as directory:
            path = manifest.write_json(os.path.join(directory, 'manifest.json'))
            with open(path) as handle:
                restored = json.load(handle)
        assert restored['parameters']['year'] == 2030


class TestRecordsRefuseToBeUninterpretable:
    """Rule 5 applied to the registers themselves: a record that looks like tracking while
    carrying nothing checkable is worse than no record."""

    def test_empty_description_raises(self):
        with pytest.raises(ValueError, match='description is required'):
            ResultRecord(record_id='R-X', description='   ', value=1.0)

    def test_empty_record_id_raises(self):
        with pytest.raises(ValueError, match='record_id is required'):
            ResultRecord(record_id='', description='x', value=1.0)

    def test_duplicate_result_id_raises_rather_than_overwriting(self):
        register = ProvenanceRegister()
        register.add_result(ResultRecord(record_id='R-X', description='first', value=1.0))
        with pytest.raises(ValueError, match='duplicate result_id'):
            register.add_result(ResultRecord(record_id='R-X', description='second', value=2.0))

    def test_duplicate_assumption_id_raises(self):
        register = ProvenanceRegister()
        register.add_assumption(AssumptionRecord(record_id='A-X', description='first', value=1.0))
        with pytest.raises(ValueError, match='duplicate assumption_id'):
            register.add_assumption(AssumptionRecord(record_id='A-X', description='second', value=2.0))
