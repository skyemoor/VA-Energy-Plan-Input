"""
test_model_wide_findings_documented.py

Asserts that the four model-wide findings of 2026-09-11 stay documented and discoverable.

These are documentation tests, which is unusual, and the reason is specific: each finding was
initially recorded ONLY in Scenario3_Technical_Notes.md, where someone reading Scenario 1 or 2
would never have found it. Two of them (the flat dual, the dormant reserve constraint) invalidate
particular classes of result. A later edit that quietly drops one would leave the invalidated
results looking sound.
"""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINDINGS = os.path.join(REPO, 'docs', 'MODEL_WIDE_FINDINGS.md')


def read(p):
    with open(p) as f:
        return f.read()


class TestFindingsDocumentExists:

    def test_the_document_exists(self):
        assert os.path.exists(FINDINGS)

    def test_flat_dual_is_recorded_with_its_measurement(self):
        s = read(FINDINGS)
        assert '$54.70' in s
        assert '8,760' in s

    def test_dormant_reserve_constraint_is_recorded(self):
        """Exists, documented as 'current standard', never called. Highest-value fix available."""
        s = read(FINDINGS)
        assert 'all_hours_reserve.py' in s
        assert 'Nothing calls it' in s

    def test_missing_imports_is_recorded(self):
        s = read(FINDINGS)
        assert 'zero\noccurrences' in s or 'zero occurrences' in s

    def test_foresight_asymmetry_is_recorded(self):
        s = read(FINDINGS)
        assert '100.0%' in s and '31.8%' in s

    def test_truncated_pdfs_are_recorded(self):
        """Any prior finding citing them is unverifiable from the current files."""
        assert '/Root' in read(FINDINGS)


class TestScopeIsStatedHonestly:

    def test_what_is_invalidated_and_what_is_not_are_both_stated(self):
        """A finding that says only what breaks invites over-reaction; one that says only what
        survives invites under-reaction."""
        s = read(FINDINGS)
        assert 'Invalidated:' in s
        assert 'Not invalidated:' in s

    def test_the_net_load_versus_gross_peak_question_is_raised(self):
        """The peak-hour constraint uses gross demand. At ~174 GW of solar the binding hour is
        almost certainly a net-load evening ramp, so it may size against the wrong hour."""
        s = read(FINDINGS)
        assert 'net-load' in s and 'gross peak' in s


class TestDiscoverability:
    """The original failure was scope, not content: real findings filed where the people who
    needed them would not look."""

    def test_scenario3_notes_point_outward(self):
        s = read(os.path.join(REPO, 'docs', 'methodology', 'Scenario3_Technical_Notes.md'))
        assert 'MODEL_WIDE_FINDINGS' in s
        assert 'NOT Scenario-3-specific' in s

    def test_pipeline_completeness_points_at_findings(self):
        assert 'MODEL_WIDE_FINDINGS' in read(os.path.join(REPO, 'docs', 'PIPELINE_COMPLETENESS.md'))

    def test_gas_documents_point_at_the_consolidated_notes(self):
        for rel in (('docs', 'methodology', 'Gas_Merit_Order.md'),
                    ('docs', 'methodology', 'VA_gas_capacity_schedules.md')):
            assert 'Gas_Fleet_Working_Notes' in read(os.path.join(REPO, *rel))

    def test_gas_notes_point_back_at_model_wide_findings(self):
        s = read(os.path.join(REPO, 'docs', 'methodology', 'Gas_Fleet_Working_Notes.md'))
        assert 'MODEL_WIDE_FINDINGS' in s


class TestDefinitionsAreRecorded:
    """Several terms were used loosely; two caused real confusion -- VOLL being a penalty rather
    than a price, and the dual being the LP's internal energy price rather than an LMP."""

    def test_ambiguous_terms_are_defined(self):
        s = read(os.path.join(REPO, 'docs', 'methodology', 'Gas_Fleet_Working_Notes.md'))
        for term in ('**VOM', '**VOLL', '**Dual', '**Merit order', '**LMP', '**Heat rate',
                     '**Aeroderivative', '**EOH'):
            assert term in s, f'{term} not defined'

    def test_voll_is_distinguished_from_a_price(self):
        s = read(os.path.join(REPO, 'docs', 'methodology', 'Gas_Fleet_Working_Notes.md'))
        assert 'penalty, not a price' in s

    def test_dual_is_distinguished_from_an_lmp(self):
        s = read(os.path.join(REPO, 'docs', 'methodology', 'Gas_Fleet_Working_Notes.md'))
        assert 'It is not an LMP' in s
