"""
provenance.py

Tracking artifacts for modeling results, the assumptions they rest on, and the runs that
produced them.

WHY THIS EXISTS (2026-09-10): three concrete failures in prior sessions motivated each class here.
1. STALE DERIVED FIGURES. Revising the Prince William parking-lot estimate moved the four-county
   NoVA total from 6,159.0 MW to 4,638.6 MW. But 6,159 MW was the fleet basis for the six-day
   lookahead firming analysis, so its ~4.3% firming figure silently became stale -- and nothing in
   the existing artifacts flagged it. AssumptionRecord.dependent_result_ids exists specifically so
   that revision mechanically identifies what it invalidates.
2. NO SINGLE SOURCE OF TRUTH FOR REPORTED VALUES. SLCOE has appeared as $39.03/MWh (workbook tab),
   $42.45/MWh (Python pipeline, reserve margin added) and $129.28/MWh (2045 checkpoint) -- all
   legitimate for their own vintage, with no register stating which is current for which scenario
   and year. ResultRecord.status makes supersession explicit rather than tribal knowledge.
3. RUN PROVENANCE RECONSTRUCTED BY HAND. Which weather year, which gas fraction, pinned or free
   build, closing-SoC on or off, which solver -- this was re-derived repeatedly from memory and
   script names. RunManifest captures it at run time instead.

Per Software_Engineering_Standards Rule 1, these share a base class rather than being three
free-standing scripts: all three are provenance records with an identifier, a creation date and a
description, differing only in what else they carry.
"""
import json
import hashlib
import os
from datetime import date, datetime


VALID_RESULT_STATUSES = ('current', 'provisional', 'superseded')


class ProvenanceRecord:
    """Base for anything that records where a number or a run came from.

    Rule 5 (fail loudly): every field required for a record to be interpretable later is required
    at construction. A record missing its description or date is worse than no record, because it
    looks like tracking while providing nothing checkable.
    """

    def __init__(self, record_id, description, created_date=None):
        if not record_id or not str(record_id).strip():
            raise ValueError("record_id is required and must be non-empty")
        if not description or not str(description).strip():
            raise ValueError(
                f"{record_id}: description is required -- a record without one cannot be "
                "interpreted by a future reader and defeats the purpose of the register")
        self.record_id = str(record_id).strip()
        self.description = str(description).strip()
        self.created_date = created_date or date.today().isoformat()

    def to_dict(self):
        return {'record_id': self.record_id, 'description': self.description,
                'created_date': self.created_date}


class AssumptionRecord(ProvenanceRecord):
    """One assumption, its value, its citation, and every result that depends on it.

    dependent_result_ids is the field that solves failure mode 1 above. It is maintained
    deliberately rather than inferred, because dependency here is analytical (this figure was
    computed using that assumption), not something a tool can detect from code alone.
    """

    def __init__(self, record_id, description, value, units=None, citation_key=None,
                 dependent_result_ids=None, created_date=None):
        super().__init__(record_id, description, created_date)
        self.value = value
        self.units = units
        self.citation_key = citation_key
        self.dependent_result_ids = list(dependent_result_ids or [])

    def to_dict(self):
        base = super().to_dict()
        base.update(value=self.value, units=self.units, citation_key=self.citation_key,
                    dependent_result_ids=list(self.dependent_result_ids))
        return base


class ResultRecord(ProvenanceRecord):
    """One quantitative claim that could appear in the whitepaper.

    The rule this enforces: a number does not reach the paper without a row here. status and
    superseded_by make vintage explicit so that $39.03, $42.45 and $129.28 can coexist in the
    project's history without any ambiguity about which is current for a given scenario and year.
    """

    def __init__(self, record_id, description, value, units=None, scenario=None, year=None,
                 status='provisional', generating_script=None, input_files=None,
                 depends_on_assumption_ids=None, superseded_by=None, notes=None,
                 created_date=None):
        super().__init__(record_id, description, created_date)
        if status not in VALID_RESULT_STATUSES:
            raise ValueError(
                f"{record_id}: status {status!r} is not one of {VALID_RESULT_STATUSES}. "
                "Rule 5 -- an unrecognized status is rejected rather than silently treated as "
                "provisional, because a wrongly-'current' figure is exactly the failure this "
                "register exists to prevent.")
        if status == 'superseded' and not superseded_by:
            raise ValueError(
                f"{record_id}: status 'superseded' requires superseded_by naming the replacement. "
                "A figure marked superseded with no pointer to its successor leaves a future "
                "reader worse off than an unmarked one.")
        self.value = value
        self.units = units
        self.scenario = scenario
        self.year = year
        self.status = status
        self.generating_script = generating_script
        self.input_files = list(input_files or [])
        self.depends_on_assumption_ids = list(depends_on_assumption_ids or [])
        self.superseded_by = superseded_by
        self.notes = notes

    def to_dict(self):
        base = super().to_dict()
        base.update(value=self.value, units=self.units, scenario=self.scenario, year=self.year,
                    status=self.status, generating_script=self.generating_script,
                    input_files=list(self.input_files),
                    depends_on_assumption_ids=list(self.depends_on_assumption_ids),
                    superseded_by=self.superseded_by, notes=self.notes)
        return base


class RunManifest(ProvenanceRecord):
    """Everything needed to reproduce one model run, captured at run time rather than recalled.

    input_file_hashes matters more than input file NAMES: this session repeatedly hit files whose
    name implied one thing and whose content was another (a .pdf that was plain text; a .pdf that
    was a ZIP of JPEGs; two CVOW files sharing a naming convention but using different internal
    layouts). A hash makes "same inputs?" answerable rather than assumed from the filename.
    """

    def __init__(self, record_id, description, parameters, input_file_paths=None,
                 build_results=None, solver=None, runtime_seconds=None, created_date=None):
        super().__init__(record_id, description, created_date)
        if parameters is None:
            raise ValueError(
                f"{record_id}: parameters is required. A manifest without the parameters that "
                "produced the run records nothing reproducible.")
        self.parameters = dict(parameters)
        self.input_file_hashes = {p: self.hash_file(p) for p in (input_file_paths or [])}
        self.build_results = dict(build_results or {})
        self.solver = solver
        self.runtime_seconds = runtime_seconds
        self.created_timestamp = datetime.now().isoformat(timespec='seconds')

    @staticmethod
    def hash_file(path, chunk_bytes=1 << 20):
        """SHA-256 of a file's contents, or an explicit marker when it is unreadable.

        Rule 5: a missing input file returns an explicit MISSING marker rather than None or an
        empty string, so a manifest recording an absent input is obviously wrong on inspection
        rather than quietly indistinguishable from one recording an empty file.
        """
        if not os.path.exists(path):
            return f'MISSING:{path}'
        digest = hashlib.sha256()
        with open(path, 'rb') as handle:
            for chunk in iter(lambda: handle.read(chunk_bytes), b''):
                digest.update(chunk)
        return digest.hexdigest()

    def to_dict(self):
        base = super().to_dict()
        base.update(parameters=dict(self.parameters), input_file_hashes=dict(self.input_file_hashes),
                    build_results=dict(self.build_results), solver=self.solver,
                    runtime_seconds=self.runtime_seconds,
                    created_timestamp=self.created_timestamp)
        return base

    def write_json(self, output_path):
        with open(output_path, 'w') as handle:
            json.dump(self.to_dict(), handle, indent=2)
        return output_path


class ProvenanceRegister:
    """Holds results and assumptions together, and answers the staleness question.

    Kept as one register rather than two, because its most important operation --
    find_results_invalidated_by() -- spans both, and splitting them would put that query in
    neither class.
    """

    def __init__(self):
        self.results_by_id = {}
        self.assumptions_by_id = {}

    def add_result(self, result_record):
        if result_record.record_id in self.results_by_id:
            raise ValueError(
                f"duplicate result_id {result_record.record_id!r} -- refusing to overwrite. "
                "Supersede the existing record explicitly instead.")
        self.results_by_id[result_record.record_id] = result_record
        return result_record

    def add_assumption(self, assumption_record):
        if assumption_record.record_id in self.assumptions_by_id:
            raise ValueError(
                f"duplicate assumption_id {assumption_record.record_id!r} -- refusing to overwrite.")
        self.assumptions_by_id[assumption_record.record_id] = assumption_record
        return assumption_record

    def find_results_invalidated_by(self, assumption_id):
        """Every non-superseded result depending on this assumption, directly or transitively.

        This is the query that would have caught the PWC parking revision invalidating the
        six-day firming figure. Transitive because derived figures chain: a revised siting
        estimate moves a fleet total, which moves every firming percentage computed from it.
        """
        if assumption_id not in self.assumptions_by_id:
            raise KeyError(
                f"unknown assumption_id {assumption_id!r} -- refusing to report 'no dependents' "
                "for an assumption that isn't registered, which would read as a clean bill of "
                "health when it actually means the assumption was never tracked.")
        directly_affected = {
            result.record_id for result in self.results_by_id.values()
            if assumption_id in result.depends_on_assumption_ids and result.status != 'superseded'}
        # Transitive closure: a result naming another result's id among its dependencies inherits
        # that result's staleness.
        affected = set(directly_affected)
        changed = True
        while changed:
            changed = False
            for result in self.results_by_id.values():
                if result.status == 'superseded' or result.record_id in affected:
                    continue
                if affected & set(result.depends_on_assumption_ids):
                    affected.add(result.record_id)
                    changed = True
        return sorted(affected)

    def current_results(self, scenario=None, year=None):
        """Results marked current, optionally filtered -- the 'what do we actually believe' query."""
        return sorted(
            (r for r in self.results_by_id.values()
             if r.status == 'current'
             and (scenario is None or r.scenario == scenario)
             and (year is None or r.year == year)),
            key=lambda r: r.record_id)

    def to_dict(self):
        return {'results': [r.to_dict() for r in self.results_by_id.values()],
                'assumptions': [a.to_dict() for a in self.assumptions_by_id.values()]}

    def write_json(self, output_path):
        with open(output_path, 'w') as handle:
            json.dump(self.to_dict(), handle, indent=2)
        return output_path
