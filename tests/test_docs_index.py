"""
test_docs_index.py

Asserts the documentation index stays accurate and that domain entry points stay wired.

Exists because two collisions occurred on 2026-09-11 -- a gas fleet note written without checking
docs/research/, which already held a gas turbine lifespans reference; and an extended wholesale
market arbitrage discussion conducted without consulting DERA_VPP_WMA_Consolidated_Working_Notes.md,
which had already resolved several of the questions being asked. The index is the countermeasure;
these tests keep it from silently going stale.
"""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(REPO, 'docs', 'INDEX.md')


def read(*parts):
    with open(os.path.join(REPO, *parts)) as f:
        return f.read()


class TestIndexExistsAndIsComplete:

    def test_index_exists(self):
        assert os.path.exists(INDEX)

    def test_every_markdown_file_under_docs_is_listed(self):
        """A file missing from the index is a file the next task will not know exists."""
        listed = read('docs', 'INDEX.md')
        missing = []
        for root, _, files in os.walk(os.path.join(REPO, 'docs')):
            for f in files:
                if not f.endswith('.md') or f == 'INDEX.md':
                    continue
                if f not in listed and os.path.basename(root) != 'statutes':
                    missing.append(os.path.join(os.path.basename(root), f))
        assert not missing, f'not in INDEX.md: {missing}'

    def test_index_states_why_it_exists(self):
        s = read('docs', 'INDEX.md')
        assert 'prevent work being redone' in s


class TestDomainEntryPointsAreMarked:

    def test_fragmented_domains_have_a_start_here(self):
        s = read('docs', 'INDEX.md')
        for hub in ('Gas_Fleet_Working_Notes.md', 'DERA_VPP_WMA_Consolidated_Working_Notes.md',
                    'Agrivoltaics_Evidence_Base.md', 'MODEL_WIDE_FINDINGS.md'):
            assert hub in s, f'{hub} not in index'
        assert 'START HERE' in s

    def test_gas_files_point_at_the_hub(self):
        for rel in (('docs', 'research', 'Gas_turbine_lifespans_reference.md'),
                    ('docs', 'research', 'new_peaker_ccgt_costs_by_size.md'),
                    ('docs', 'methodology', 'Gas_Technology_Selection_By_Scenario.md'),
                    ('docs', 'methodology', 'METHODOLOGY_gas_allowed_frac_derivation.md'),
                    ('docs', 'methodology', 'Gas_Merit_Order.md'),
                    ('docs', 'methodology', 'VA_gas_capacity_schedules.md')):
            assert 'Gas_Fleet_Working_Notes' in read(*rel), f'{rel[-1]} does not point at the hub'

    def test_gas_hub_maps_the_whole_domain(self):
        s = read('docs', 'methodology', 'Gas_Fleet_Working_Notes.md')
        assert 'Seven files cover gas' in s
        for f in ('Gas_turbine_lifespans_reference.md', 'new_peaker_ccgt_costs_by_size.md',
                  'Gas_Technology_Selection_By_Scenario.md'):
            assert f in s


class TestPJMConstraintsSurfacedInTheIndex:
    """Three findings from the DERA notes that constrain Scenario 3 and were missed once."""

    def test_single_node_energy_constraint_is_surfaced(self):
        """Energy aggregations must sit at ONE p-node. A distributed fleet scattered across a
        county cannot bid as one block for energy arbitrage -- which the model assumes it can."""
        s = read('docs', 'INDEX.md')
        assert 'single PJM pricing node' in s
        assert 'cannot bid as one block' in s

    def test_order_2222_timeline_is_surfaced(self):
        s = read('docs', 'INDEX.md')
        assert '2028' in s and 'CSP' in s

    def test_component_der_ceiling_is_surfaced(self):
        assert '5 MW per Component DER' in read('docs', 'INDEX.md')


class TestConsolidationBacklogIsRecorded:

    def test_priority_order_exists(self):
        s = read('docs', 'INDEX.md')
        assert 'Consolidation candidates' in s

    def test_ct_split_lead_is_recorded_as_a_lead_not_a_resolution(self):
        """Size-based inference from the capex tiers, not a sourced unit-type finding."""
        import assumptions as a
        assert 'LEAD (not a resolution)' in a.GAS_CT_SPLIT_UNRESOLVED
        assert 'inference from unit size' in a.GAS_CT_SPLIT_UNRESOLVED
