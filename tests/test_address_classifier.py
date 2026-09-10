"""
test_address_classifier.py

Tests address_classifier.py against REAL entries from
raw_active_business_accounts_A.txt (Loudoun County's own official Active
Business Accounts list), not synthetic stand-ins, per this project's own
standing practice of cross-verifying against real, independently-sourced
data wherever the real path is fast enough to run in a test.
"""
import os
import unittest

from address_classifier import (
    BusinessRecord,
    EntityTypeSignal,
    classify_address,
    classify_entity_type,
    has_suite_indicator,
    is_po_box,
    is_zip_in_known_loudoun_zips,
    parse_mixed_delimiter_docx_export,
    parse_raw_business_accounts_file,
    recover_city_from_unsplit_address,
)

RAW_DATA_PATH = os.path.join(os.path.dirname(__file__), "raw_active_business_accounts_A.txt")


class TestHardExcludes(unittest.TestCase):
    """Unambiguous exclusions: out-of-state, PO Box, not-a-Loudoun-city."""

    def test_out_of_state_address_is_hard_excluded(self):
        """Real record: Advanced Dermatology of Virginia Inc, mailing to
        Maitland, FL despite the name -- a Loudoun business license does not
        imply a Loudoun physical address."""
        record = BusinessRecord(
            business_name="ADVANCED DERMATOLOGY OF VIRGINIA INC",
            trade_name="",
            address="151 SOUTHHALL LN STE 300",
            city="MAITLAND",
            state="FL",
            zip_code="32751-7172",
        )
        result = classify_address(record)
        self.assertTrue(result.hard_excluded)
        self.assertIn("out-of-state", result.hard_exclude_reason)

    def test_po_box_only_address_is_hard_excluded(self):
        """Real record: Alchemy Wine Company, LLC -- address is purely a PO
        Box, no street address component at all."""
        record = BusinessRecord(
            business_name="ALCHEMY WINE COMPANY, LLC",
            trade_name="",
            address="PO BOX 154",
            city="STEPHENSON",
            state="VA",
            zip_code="22656-0000",
        )
        result = classify_address(record)
        self.assertTrue(result.hard_excluded)
        self.assertIn("PO Box", result.hard_exclude_reason)

    def test_manassas_city_is_hard_excluded_as_not_loudoun(self):
        """Real record: Alexander I Molina, mailing to Manassas -- a
        different city entirely, not one of Loudoun's own communities."""
        record = BusinessRecord(
            business_name="ALEXANDER I MOLINA",
            trade_name="",
            address="7790 WILLOW POND CT",
            city="MANASSAS",
            state="VA",
            zip_code="20111-8010",
        )
        result = classify_address(record)
        self.assertTrue(result.hard_excluded)
        self.assertIn("not a known Loudoun community", result.hard_exclude_reason)

    def test_compound_po_box_and_street_address_is_still_excluded(self):
        """KNOWN, DOCUMENTED EDGE CASE, not a silent default: the Albert Reed
        Patterson / Mr. Print of Middleburg LLC record's address field is
        'PO BOX 1121 5 E FEDERAL ST' -- a PO Box AND a real street address
        (E Federal St is Middleburg's own historic downtown corridor)
        concatenated in the same field. This test locks in the current,
        conservative behavior (exclude rather than risk trusting an unclear
        compound field) so a future change to this behavior is a deliberate
        choice, not an accidental regression. If a real street address is
        ever confidently extractable from compound fields like this one,
        that would recover real in-county buildings currently being dropped
        -- flagged here as a known limitation, not fixed by this test.
        """
        record = BusinessRecord(
            business_name="ALBERT REED PATTERSON",
            trade_name="MR. PRINT OF MIDDLEBURG LLC",
            address="PO BOX 1121 5 E FEDERAL ST",
            city="MIDDLEBURG",
            state="VA",
            zip_code="20117-0000",
        )
        result = classify_address(record)
        self.assertTrue(result.hard_excluded)
        self.assertIn("PO Box", result.hard_exclude_reason)

    def test_valid_in_county_address_is_not_hard_excluded(self):
        """Real record: AgileRank LLC -- a genuine in-county Sterling
        address with a suite, should pass all hard-exclude checks cleanly."""
        record = BusinessRecord(
            business_name="AGILERANK LLC",
            trade_name="AGILERANK LLC",
            address="21515 RIDGETOP CIR STE 310",
            city="STERLING",
            state="VA",
            zip_code="20166-6509",
        )
        result = classify_address(record)
        self.assertFalse(result.hard_excluded)
        self.assertIsNone(result.hard_exclude_reason)

    def test_bluemont_is_recognized_as_loudoun_not_wrongly_excluded(self):
        """Regression test for a real, measurable bug: 'Bluemont' (a real
        Loudoun historic village) was missing from KNOWN_LOUDOUN_CITIES,
        which wrongly hard-excluded 70 real records in a 23,373-record run
        before this was caught and fixed -- the single largest false-
        positive exclusion found. See Data_Sourcing_Log.md for the full
        finding."""
        record = BusinessRecord(
            business_name="TEST BUSINESS LLC", trade_name="", address="1 MAIN ST",
            city="BLUEMONT", state="VA", zip_code="20135-0000",
        )
        result = classify_address(record)
        self.assertFalse(result.hard_excluded)

    def test_other_user_confirmed_loudoun_communities_are_recognized(self):
        """The remaining real Loudoun locations added alongside Bluemont,
        cross-checked against a cited reference list (visitloudoun.org,
        Loudoun County GIS, Wikipedia) -- none appeared in the actual
        23,373-record run's city breakdown, but are real locations that
        should not be excluded if they appear in future data."""
        for city in ("ARCOLA", "WILLISVILLE", "AIRMONT", "BLOOMFIELD",
                     "BRITAIN", "CONKLIN", "DOVER", "WHEATLAND"):
            record = BusinessRecord(
                business_name="TEST BUSINESS LLC", trade_name="", address="1 MAIN ST",
                city=city, state="VA", zip_code="20135-0000",
            )
            result = classify_address(record)
            self.assertFalse(result.hard_excluded, f"{city} should not be hard-excluded")

    def test_upperville_is_recognized(self):
        """Added after the Zillow zip cross-check surfaced 11 real records
        with city=Upperville, zip=20184 (on Zillow's own Loudoun zip list),
        and Zillow's own page separately lists 'Upperville Real Estate'
        directly alongside the other unambiguously-Loudoun communities."""
        record = BusinessRecord(
            business_name="TEST BUSINESS LLC", trade_name="", address="1 MAIN ST",
            city="UPPERVILLE", state="VA", zip_code="20184-0000",
        )
        result = classify_address(record)
        self.assertFalse(result.hard_excluded)


class TestCityNormalizationHandlesFormattingVariantsSafely(unittest.TestCase):
    """Real formatting-variant cases found in the actual 23,373-record
    dataset, where the city IS a known Loudoun city but wasn't recognized
    due to trailing state/zip text, punctuation, or a known typo/
    abbreviation -- plus, critically, confirmation that genuinely different
    Virginia places that are merely edit-distance-close to a Loudoun city
    name are NOT swept up by the fix."""

    def _excluded_for_city_reason(self, city: str) -> bool:
        record = BusinessRecord(
            business_name="TEST LLC", trade_name="", address="1 MAIN ST",
            city=city, state="VA", zip_code="20147-0000",
        )
        result = classify_address(record)
        return result.hard_excluded and "not a known Loudoun community" in (result.hard_exclude_reason or "")

    def test_trailing_state_text_variants_are_recognized(self):
        for city in ("ASHBURN, VA", "ASHBURN, VA, USA", "BROADLANDS VA",
                     "CHANTILLY, VA", "STERLING VA", "LEESBURG, VA", "LEESBURG,"):
            self.assertFalse(self._excluded_for_city_reason(city), f"{city!r} should be recognized")

    def test_zip_concatenated_into_city_field_is_still_recognized(self):
        """Real, confirmed case: 'LEESBURG VA  201764475' -- a zip code
        concatenated directly into the city field during conversion."""
        self.assertFalse(self._excluded_for_city_reason("LEESBURG VA  201764475"))

    def test_known_typo_and_abbreviation_aliases_are_recognized(self):
        for city in ("ASHBIRN", "CHANTILY", "LEESBUG", "LEESBURGE",
                     "LEESEBURG", "PAEONIAN SPGS", "PURCELLIVLLE", "LANDSDOWNE"):
            self.assertFalse(self._excluded_for_city_reason(city), f"{city!r} should be recognized")

    def test_genuinely_different_virginia_places_stay_excluded(self):
        """Critical negative test: these are REAL, independent Virginia
        cities/towns outside Loudoun that are merely edit-distance-close to
        a Loudoun city name (Bealeton/Brambleton, Hampton/Hamilton,
        Petersburg/Leesburg, Scottsville/Lovettsville). A fuzzy-matching
        approach was tried against the real dataset and would have wrongly
        aliased all four of these into being treated as in-county --
        confirming they must NOT match is what makes CITY_ALIASES a safe,
        hand-reviewed list rather than an automated fuzzy one."""
        for city in ("BEALETON", "HAMPTON", "PETERSBURG", "SCOTTSVILLE"):
            self.assertTrue(
                self._excluded_for_city_reason(city),
                f"{city!r} is a real, different Virginia place and must stay excluded"
            )


class TestSuiteDetectionIsNotTreatedAsNegativeWhenAbsent(unittest.TestCase):
    """Confirms has_suite is recorded as its own fact, not used to penalize
    a record when absent -- per direct user correction that a business
    owning its whole building has no suite for the opposite reason a
    home-based registration doesn't."""

    def test_suite_present_is_detected(self):
        self.assertTrue(has_suite_indicator("21515 RIDGETOP CIR STE 310"))

    def test_suite_absent_is_detected_as_false_not_penalized(self):
        """Real record: Advanced Electro LLC, a real Broadlands address with
        no suite designation at all."""
        self.assertFalse(has_suite_indicator("21213 SUNDIAL CT"))
        # The absence itself is the only fact asserted here -- this function
        # returns a bool, not a score, so there is nothing to "penalize."


class TestEntityTypeSignalChecksBothNameFields(unittest.TestCase):
    """The core case this module was specifically built to handle: an
    entity-type suffix that appears in trade_name while business_name is a
    bare person's name. Checking business_name alone would miss this."""

    def test_pc_suffix_detected_as_licensed_profession(self):
        """Real record: Allergy & Asthma Associates PC."""
        signal = classify_entity_type("ALLERGY & ASTHMA ASSOCIATES PC", "ALLERGY & ASTHMA ASSOCIATES PC")
        self.assertEqual(signal, EntityTypeSignal.PC_PLLC)

    def test_pllc_suffix_detected_as_licensed_profession(self):
        """Real record: Aldie Dental Care, PLLC."""
        signal = classify_entity_type("ALDIE DENTAL CARE, PLLC", "")
        self.assertEqual(signal, EntityTypeSignal.PC_PLLC)

    def test_inc_suffix_detected(self):
        """Real record: Advanced Fueling Systems Inc."""
        signal = classify_entity_type("ADVANCED FUELING SYSTEMS INC", "ADVANCED FUELING SYSTEMS INC")
        self.assertEqual(signal, EntityTypeSignal.INC_CORP)

    def test_llc_with_company_style_name(self):
        """Real record: Advanced Electro LLC -- an LLC, but 'Advanced
        Electro' is not a person-name pattern."""
        signal = classify_entity_type("ADVANCED ELECTRO LLC", "ADVANCED ELECTRO LLC")
        self.assertEqual(signal, EntityTypeSignal.LLC_COMPANY_NAME)

    def test_llc_signal_found_via_trade_name_when_business_name_is_bare_person(self):
        """THE key test case: Albert Reed Patterson / Mr. Print of
        Middleburg LLC. business_name alone ('Albert Reed Patterson') has no
        entity suffix at all -- checking it in isolation would produce
        PERSON_NO_SUFFIX, silently missing the real LLC signal sitting in
        trade_name. This test locks in that the combined check finds it.
        """
        signal = classify_entity_type("ALBERT REED PATTERSON", "MR. PRINT OF MIDDLEBURG LLC")
        self.assertNotEqual(
            signal, EntityTypeSignal.PERSON_NO_SUFFIX,
            "Business-name-only checking would wrongly miss the LLC signal in trade_name"
        )
        self.assertEqual(signal, EntityTypeSignal.LLC_PERSON_NAME)

    def test_bare_person_name_no_suffix_anywhere_is_recorded_but_not_excluded(self):
        """Real record: Aaron Curtis Emery -- no trade name, no entity
        suffix anywhere. This IS correctly flagged as PERSON_NO_SUFFIX (the
        signal exists to be recorded), but per direct user guidance this
        signal alone must never be used to auto-exclude -- see the
        Charles-Schwab counterexample in the module's own docstring."""
        signal = classify_entity_type("AARON CURTIS EMERY", "")
        self.assertEqual(signal, EntityTypeSignal.PERSON_NO_SUFFIX)

    def test_person_name_with_llc_suffix_is_weak_sole_proprietor_signal(self):
        """A bare person name that DOES have its own LLC suffix directly
        (not via a separate trade name) is tagged as the weaker
        LLC_PERSON_NAME signal, distinct from a company-style LLC name."""
        signal = classify_entity_type("JOHN SMITH LLC", "")
        self.assertEqual(signal, EntityTypeSignal.LLC_PERSON_NAME)


class TestPersonNameHeuristicDoesNotOverreach(unittest.TestCase):
    """Confirms the person-name pattern matcher stays conservative -- it
    should not fire on company-style names, and should not be the sole
    basis for excluding anything (enforced structurally: nothing in this
    module ever hard-excludes based on is_likely_person_name)."""

    def test_bare_two_word_name_matches(self):
        signal = classify_entity_type("AARON EMERY", "")
        self.assertEqual(signal, EntityTypeSignal.PERSON_NO_SUFFIX)

    def test_company_style_name_does_not_match_as_person(self):
        """'Advanced Electro' should not be mistaken for a person's name
        even though it's two capitalized words."""
        signal = classify_entity_type("ADVANCED ELECTRO", "")
        self.assertNotEqual(signal, EntityTypeSignal.PERSON_NO_SUFFIX)

    def test_name_containing_company_style_word_does_not_match_as_person(self):
        signal = classify_entity_type("SMITH CONSULTING", "")
        self.assertNotEqual(signal, EntityTypeSignal.PERSON_NO_SUFFIX)


class TestFullClassificationOnRealRecord(unittest.TestCase):
    """End-to-end check on one real, clean, in-county record -- confirms all
    signal fields land correctly together, not just in isolation."""

    def test_agilerank_llc_classified_correctly_end_to_end(self):
        record = BusinessRecord(
            business_name="AGILERANK LLC",
            trade_name="AGILERANK LLC",
            address="21515 RIDGETOP CIR STE 310",
            city="STERLING",
            state="VA",
            zip_code="20166-6509",
        )
        result = classify_address(record)
        self.assertFalse(result.hard_excluded)
        self.assertTrue(result.has_suite)
        self.assertEqual(result.entity_type_signal, EntityTypeSignal.LLC_COMPANY_NAME)
        self.assertFalse(result.is_likely_person_name)


class TestZipCodeCrossVerification(unittest.TestCase):
    """Tests the separate, supplementary zip_in_known_loudoun_zips signal --
    deliberately kept as a cross-check alongside the city-based hard
    exclusion, not a replacement for it. See KNOWN_LOUDOUN_ZIPS' own
    docstring for the confirmed reason: some Loudoun zips genuinely extend
    into adjacent counties."""

    def test_known_loudoun_zip_is_detected(self):
        self.assertTrue(is_zip_in_known_loudoun_zips("20147-5910"))
        self.assertTrue(is_zip_in_known_loudoun_zips("20135"))  # Bluemont

    def test_non_loudoun_zip_is_not_detected(self):
        self.assertFalse(is_zip_in_known_loudoun_zips("22102-5213"))  # Tysons

    def test_zip_plus_four_is_handled_by_extracting_five_digit_prefix(self):
        self.assertTrue(is_zip_in_known_loudoun_zips("20166-6509"))

    def test_centreville_and_herndon_zips_are_not_on_the_known_list(self):
        """Confirms the switch to Zillow's tighter zip list (made after
        direct comparison against the user-provided Zillow zip list) cleanly
        resolves the earlier concern: 20120 (Centreville) and 20170
        (Herndon) were on an earlier, zipdatamaps.com-derived version of
        this set (which documents these as zips extending into adjacent
        counties), but are NOT on Zillow's own list. Since both are
        independently confirmed, from the real dataset, to be genuine
        Fairfax County locations (89 and 181 records respectively), their
        absence here means the boundary-straddle conflict this signal was
        originally built to guard against no longer arises for these two
        specific zips."""
        self.assertFalse(is_zip_in_known_loudoun_zips("20120"))
        self.assertFalse(is_zip_in_known_loudoun_zips("20170"))

    def test_newly_added_zips_are_recognized(self):
        """The three zips added when switching to Zillow's list, each
        independently verified via multiple other sources before being
        trusted: 20107 (Arcola -- also cross-verified via
        unitedstateszipcodes.org explicitly listing it as 'Arcola · Loudoun
        County'), 20151 (a second, Loudoun-side Chantilly zip distinct from
        20152), and 22093 (a second, unique Ashburn zip)."""
        self.assertTrue(is_zip_in_known_loudoun_zips("20107"))
        self.assertTrue(is_zip_in_known_loudoun_zips("20151"))
        self.assertTrue(is_zip_in_known_loudoun_zips("22093"))

    def test_zip_membership_does_not_structurally_override_city_based_exclusion(self):
        """Structural guarantee test, using a hypothetical (not necessarily
        real-world) combination: even if a record's zip happens to be on
        KNOWN_LOUDOUN_ZIPS, a city name that is NOT recognized must still
        result in hard_excluded=True. The zip signal is recorded accurately
        but must never be used to flip the city-based decision -- this is
        the structural reason the two signals are kept separate rather than
        merged into one, regardless of which specific zips are on the list
        at any given time."""
        record = BusinessRecord(
            business_name="TEST BUSINESS LLC", trade_name="", address="1 MAIN ST",
            city="SOME UNRECOGNIZED CITY", state="VA", zip_code="20147-0000",
        )
        result = classify_address(record)
        self.assertTrue(result.hard_excluded)
        self.assertTrue(result.zip_in_known_loudoun_zips, "the zip signal itself should still be recorded accurately")

    def test_zip_signal_is_useful_for_blank_city_records(self):
        """The case where the zip signal actually adds value: a record with
        a blank city (e.g. from the unsplit-address+city corruption pattern)
        has no city text to check at all, so the zip signal is the only
        available cross-check."""
        record = BusinessRecord(
            business_name="TEST BUSINESS LLC", trade_name="", address="1 MAIN ST",
            city="", state="VA", zip_code="20147-0000",
        )
        result = classify_address(record)
        self.assertTrue(result.zip_in_known_loudoun_zips)
        # hard_excluded is still True here (blank city fails the city check),
        # but the zip signal at least tells a human reviewer this one is a
        # good candidate for manual recovery, unlike a blank-city record
        # whose zip ISN'T on the known list at all.
        self.assertTrue(result.hard_excluded)


class TestRecoverCityFromUnsplitAddress(unittest.TestCase):
    """Tests recover_city_from_unsplit_address using real examples from the
    actual 44-record blank-city + zip-match set, confirming the
    two-signals-must-agree safety property (address text and zip-implied
    city), not just that a value gets filled in somehow."""

    def test_recovers_city_when_address_ends_with_zip_implied_city(self):
        """Real example: Air Cleaning Technologies Inc -- the merged address
        genuinely ends with 'STERLING', which is also zip 20166's primary
        city. Both signals agree, so recovery is safe."""
        record = BusinessRecord(
            business_name="AIR CLEANING TECHNOLOGIES INC", trade_name="",
            address="[UNSPLIT ADDRESS+CITY, NEEDS REVIEW] 44966 FALCON PL STE 190  STERLING",
            city="", state="VA", zip_code="20166-9504",
        )
        recovered = recover_city_from_unsplit_address(record)
        self.assertIsNotNone(recovered)
        self.assertEqual(recovered.city, "STERLING")
        self.assertEqual(recovered.address, "44966 FALCON PL STE 190")
        self.assertEqual(recovered.business_name, "AIR CLEANING TECHNOLOGIES INC")

    def test_recovers_city_when_merged_text_is_only_the_city_itself(self):
        """Real example: Balance Wellness Systems -- the merged 'address' is
        literally just 'ROUND HILL' with no separate street address at all
        (the original source row apparently had none). Recovery still
        works; the resulting street address is correctly left empty rather
        than guessed at."""
        record = BusinessRecord(
            business_name="BALANCE WELLNESS SYSTEMS", trade_name="",
            address="[UNSPLIT ADDRESS+CITY, NEEDS REVIEW] ROUND HILL",
            city="", state="VA", zip_code="20141-3535",
        )
        recovered = recover_city_from_unsplit_address(record)
        self.assertIsNotNone(recovered)
        self.assertEqual(recovered.city, "ROUND HILL")
        self.assertEqual(recovered.address, "")

    def test_does_not_recover_when_signals_disagree(self):
        """Safety test: if the merged address text does NOT end with the
        city its own zip implies, recovery must refuse rather than guess --
        confirming this is a two-signals-must-agree check, not a
        zip-only lookup that fabricates a city with no textual evidence."""
        record = BusinessRecord(
            business_name="TEST BUSINESS LLC", trade_name="",
            address="[UNSPLIT ADDRESS+CITY, NEEDS REVIEW] 123 MAIN ST  SOME OTHER PLACE",
            city="", state="VA", zip_code="20166-0000",  # zip implies STERLING
        )
        self.assertIsNone(recover_city_from_unsplit_address(record))

    def test_does_not_recover_when_city_is_not_actually_blank(self):
        record = BusinessRecord(
            business_name="TEST LLC", trade_name="", address="1 MAIN ST",
            city="STERLING", state="VA", zip_code="20166-0000",
        )
        self.assertIsNone(recover_city_from_unsplit_address(record))

    def test_does_not_recover_when_address_lacks_the_unsplit_flag(self):
        """A blank-city record whose address is a normal, clean street
        address (not the merged-corruption pattern) should not be touched
        by this function at all -- it's not the pattern being targeted."""
        record = BusinessRecord(
            business_name="TEST LLC", trade_name="", address="123 MAIN ST",
            city="", state="VA", zip_code="20166-0000",
        )
        self.assertIsNone(recover_city_from_unsplit_address(record))

    def test_does_not_recover_when_zip_has_no_mapped_city(self):
        record = BusinessRecord(
            business_name="TEST LLC", trade_name="",
            address="[UNSPLIT ADDRESS+CITY, NEEDS REVIEW] 1 MAIN ST  SOMEWHERE",
            city="", state="VA", zip_code="99999-0000",
        )
        self.assertIsNone(recover_city_from_unsplit_address(record))

    def test_recovered_record_is_no_longer_hard_excluded(self):
        """End-to-end: once recovered, re-classifying the new record should
        no longer trigger the wrong-city hard exclusion."""
        record = BusinessRecord(
            business_name="BALANCED BEAN SOLUTIONS LLC", trade_name="",
            address="[UNSPLIT ADDRESS+CITY, NEEDS REVIEW] CHANTILLY",
            city="", state="VA", zip_code="20152-1761",
        )
        recovered = recover_city_from_unsplit_address(record)
        result = classify_address(recovered)
        self.assertFalse(result.hard_excluded)

    def test_recovery_also_fixes_a_genuinely_empty_state_field(self):
        """Real example: 'KI & KA LLC' -- a distinct corruption sub-variant
        where the street address merged into trade_name instead (not the
        address+city field), which shifted the remaining fields so state
        ended up genuinely empty rather than 'VA'. Confirms recovery closes
        this gap too, since a confirmed Loudoun zip + textually-confirmed
        Loudoun city is definitive evidence of being in Virginia regardless
        of what the original state field held."""
        record = BusinessRecord(
            business_name="KI & KA LLC",
            trade_name="KI & KA LLC 25504 FALLING CEDARS CT",
            address="[UNSPLIT ADDRESS+CITY, NEEDS REVIEW] CHANTILLY",
            city="", state="", zip_code="20152-1963",
        )
        recovered = recover_city_from_unsplit_address(record)
        self.assertIsNotNone(recovered)
        self.assertEqual(recovered.city, "CHANTILLY")
        self.assertEqual(recovered.state, "VA")
        result = classify_address(recovered)
        self.assertFalse(result.hard_excluded)

    def test_does_not_recover_when_zip_is_also_missing(self):
        """Real example: a severely corrupted row (Otsuka Pharmaceutical)
        with an empty zip in addition to a blank city -- confirms recovery
        correctly declines rather than attempting a partial fix, since
        there's no zip at all to confirm a city against."""
        record = BusinessRecord(
            business_name="OTSUKA PHARMACEUTICAL DEVELOPMENT AND COMMERCIALZA COMMERCIALZA",
            trade_name="", address="[UNSPLIT ADDRESS+CITY, NEEDS REVIEW] ",
            city="", state="", zip_code="",
        )
        self.assertIsNone(recover_city_from_unsplit_address(record))


class TestParseRawFile(unittest.TestCase):
    """Confirms the real, full raw data file parses cleanly end to end --
    not just the individual hand-picked examples above."""

    def test_parses_all_lines_without_error(self):
        records = parse_raw_business_accounts_file(RAW_DATA_PATH)
        self.assertEqual(len(records), 65, "Expected exactly 65 real records in the source file")

    def test_spot_check_first_record_matches_known_content(self):
        records = parse_raw_business_accounts_file(RAW_DATA_PATH)
        first = records[0]
        self.assertEqual(first.business_name, "ADVANCED DERMATOLOGY OF VIRGINIA INC")
        self.assertEqual(first.city, "MAITLAND")
        self.assertEqual(first.state, "FL")

    def test_spot_check_patterson_record_parses_with_compound_address_intact(self):
        records = parse_raw_business_accounts_file(RAW_DATA_PATH)
        patterson = next(r for r in records if r.business_name == "ALBERT REED PATTERSON")
        self.assertEqual(patterson.trade_name, "MR. PRINT OF MIDDLEBURG LLC")
        self.assertEqual(patterson.address, "PO BOX 1121 5 E FEDERAL ST")

    def test_full_file_classification_summary_is_internally_consistent(self):
        """Sanity check across the whole real file: every record gets a
        classification, and the hard-excluded count plus not-hard-excluded
        count equals the total -- a basic cross-check per this project's
        own standing practice of verifying computed results, not just
        trusting that the loop ran without raising."""
        records = parse_raw_business_accounts_file(RAW_DATA_PATH)
        results = [classify_address(r) for r in records]
        excluded_count = sum(1 for r in results if r.hard_excluded)
        included_count = sum(1 for r in results if not r.hard_excluded)
        self.assertEqual(excluded_count + included_count, len(records))
        # Both buckets should be non-trivial for this real, mixed data source
        self.assertGreater(excluded_count, 0)
        self.assertGreater(included_count, 0)


class TestParseMixedDelimiterDocxExport(unittest.TestCase):
    """Tests the full-county docx-export parser against real, hand-verified
    examples of every row pattern found in the actual file -- clean pipe
    rows, clean and no-trade-name tab rows, the confirmed address+city-merge
    corruption, and the confirmed two-records-merged-onto-one-line
    corruption. Uses in-memory fixture files (via tempfile) rather than
    requiring the full 2MB source file to be present, since that file is
    not checked into this project directory."""

    def _parse_text(self, text: str):
        import os
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".txt")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(text)
            return parse_mixed_delimiter_docx_export(path)
        finally:
            os.remove(path)

    def test_header_footer_noise_lines_are_skipped(self):
        text = (
            "**LOUDOUN COUNTY**\n"
            "**ACTIVE BUSINESS ACCOUNTS**\n"
            "| **BUSINESS NAME** | **TRADE NAME** | **ADDRESS** | **CITY** | **ST** | **ZIP** |\n"
            "**As of July 01, 2026**\n"
            "**Prepared by: Office of the Commissioner of the Revenue, PO Box 8000, Leesburg, VA 20177**\n"
        )
        records, unparseable = self._parse_text(text)
        self.assertEqual(len(records), 0)
        self.assertEqual(len(unparseable), 0)

    def test_clean_six_field_pipe_row_parses_correctly(self):
        """Real row: AgileRank LLC."""
        text = "| AGILERANK LLC | AGILERANK LLC | 21515 RIDGETOP CIR STE 310 | STERLING | VA | 20166-6509 |\n"
        records, unparseable = self._parse_text(text)
        self.assertEqual(len(unparseable), 0)
        self.assertEqual(len(records), 1)
        r = records[0]
        self.assertEqual(r.business_name, "AGILERANK LLC")
        self.assertEqual(r.address, "21515 RIDGETOP CIR STE 310")
        self.assertEqual(r.zip_code, "20166-6509")

    def test_patterson_record_parses_correctly_from_pipe_format(self):
        """The key cross-format test case, now via the pipe-table parser."""
        text = "| ALBERT REED PATTERSON | MR. PRINT OF MIDDLEBURG LLC | PO BOX 1121 5 E FEDERAL ST | MIDDLEBURG | VA | 20117-0000 |\n"
        records, unparseable = self._parse_text(text)
        self.assertEqual(len(unparseable), 0)
        self.assertEqual(records[0].trade_name, "MR. PRINT OF MIDDLEBURG LLC")

    def test_pipe_row_with_merged_address_city_is_flagged_not_guessed(self):
        """Real, confirmed corruption pattern: Air Cartage Express LLC --
        address and city merged into one field during conversion. Must be
        preserved and flagged, not silently split on a guess."""
        text = "| AIR CARTAGE EXPRESS LLC | AIR CARTAGE EXPRESS LLC | PO BOX 16678  WASHINGTON | DC | 20041-6678 |\n"
        records, unparseable = self._parse_text(text)
        self.assertEqual(len(unparseable), 0)
        self.assertEqual(len(records), 1)
        r = records[0]
        self.assertIn("UNSPLIT ADDRESS+CITY", r.address)
        self.assertIn("WASHINGTON", r.address)  # the merged content is preserved verbatim
        self.assertEqual(r.city, "")  # not guessed -- left explicitly empty
        self.assertEqual(r.zip_code, "20041-6678")  # state/zip still reliable, still populated

    def test_clean_six_field_tab_row_parses_correctly(self):
        """Real row: 007 Executive Sedan Limo Inc, with leading empty tabs
        from the conversion stripped correctly."""
        text = "\t\t\t\t\t007 EXECUTIVE SEDAN LIMO INC\t007EXECUTIVE SEDAN LIMO INC\t25409 ELM TER \tALDIE\tVA\t20105-2588\n"
        records, unparseable = self._parse_text(text)
        self.assertEqual(len(unparseable), 0)
        self.assertEqual(len(records), 1)
        r = records[0]
        self.assertEqual(r.business_name, "007 EXECUTIVE SEDAN LIMO INC")
        self.assertEqual(r.city, "ALDIE")

    def test_five_field_tab_row_with_no_trade_name_parses_correctly(self):
        """Real row: 001VA LLC -- genuinely no trade name (not just blank),
        confirmed by cross-checking the same record in the plain-text
        export. Different leading-tab count (4, not 5) than the six-field
        case above -- confirms leading-empty-stripping handles both."""
        text = "\t\t\t\t001VA LLC\tPO BOX 25523 \tWASHINGTON\tDC\t20027-8523\n"
        records, unparseable = self._parse_text(text)
        self.assertEqual(len(unparseable), 0)
        self.assertEqual(len(records), 1)
        r = records[0]
        self.assertEqual(r.business_name, "001VA LLC")
        self.assertEqual(r.trade_name, "")
        self.assertEqual(r.city, "WASHINGTON")

    def test_merged_two_records_on_one_tab_line_is_flagged_not_guessed(self):
        """Real, confirmed corruption pattern: a lost line-break merged two
        entire records onto one line (170 West Main Street LLC's zip code
        sits directly against 1758 Antiques LLC's business name with only a
        space, not a newline, between them). Must be flagged for manual
        review, not force-split -- the merge point isn't reliably
        identifiable without re-deriving the same field boundaries this
        parser otherwise avoids guessing at."""
        text = (
            "170 WEST MAIN STREET, LLC\t170 WEST MAIN STREET, LLC\t4245 BUCKSKIN WOOD DR \t"
            "ELLICOTT CITY\tMD\t21042-1217 1758 ANTIQUES LLC\t1758 ANTIQUES LLC\t431 S DAVIS DR \t"
            "PURCELLVILLE\tVA\t20132-3212\n"
        )
        records, unparseable = self._parse_text(text)
        self.assertEqual(len(records), 0, "Should not guess-split a merged record into a clean result")
        self.assertEqual(len(unparseable), 1)
        self.assertIn("170 WEST MAIN STREET", unparseable[0])

    def test_repeated_table_header_row_is_skipped_not_counted_as_data(self):
        text = "| **BUSINESS NAME** | **TRADE NAME** | **ADDRESS** | **CITY** | **ST** | **ZIP** |\n"
        records, unparseable = self._parse_text(text)
        self.assertEqual(len(records), 0)
        self.assertEqual(len(unparseable), 0)

    def test_markdown_table_separator_row_is_skipped_not_counted_as_fake_record(self):
        """Regression test for a real bug caught during full-file testing:
        the Markdown table separator row ('|---|---|---|---|---|---|',
        repeating once per table block throughout the file) was being
        parsed as a genuine 6-field data row with every field literally
        '---', inflating the parsed record count by roughly the number of
        repeated table blocks before this check existed. Confirmed via the
        real file: 863 exact-duplicate BusinessRecord(business_name='---',
        ...) entries were found in the parsed output, all traced to this
        one root cause."""
        text = "|---|---|---|---|---|---|\n"
        records, unparseable = self._parse_text(text)
        self.assertEqual(len(records), 0)
        self.assertEqual(len(unparseable), 0)

    def test_undelimited_merged_fragment_is_flagged_not_guessed(self):
        """Real, confirmed third variant of the lost-line-break corruption:
        some rows lost tab-delimiting entirely, not just the inter-record
        newline, leaving two complete records concatenated with zero
        separators at all. Must land in unparseable, not be silently
        dropped or force-parsed as a single garbled record."""
        text = (
            "J&R PAINTING AND DRYWALL LLC 1100 S STERLING BLVD STERLING VA 20164-4316 "
            "J&T SHOPS LLC THE LAZY DAISY GIFT STORE 43815 TIMBER SQ UNIT 406 LEESBURG VA 20176-3429\n"
        )
        records, unparseable = self._parse_text(text)
        self.assertEqual(len(records), 0)
        self.assertEqual(len(unparseable), 1)

    def test_mixed_file_with_both_formats_and_noise_parses_all_parts_correctly(self):
        """End-to-end check: one file with a pipe row, a tab row, header/
        footer noise, and a merged-record corruption case, all together --
        confirms the dispatch logic routes each line correctly rather than
        only working when tested in isolation."""
        text = (
            "**LOUDOUN COUNTY**\n"
            "**ACTIVE BUSINESS ACCOUNTS**\n"
            "| **BUSINESS NAME** | **TRADE NAME** | **ADDRESS** | **CITY** | **ST** | **ZIP** |\n"
            "| AGILERANK LLC | AGILERANK LLC | 21515 RIDGETOP CIR STE 310 | STERLING | VA | 20166-6509 |\n"
            "\t\t\t\t001VA LLC\tPO BOX 25523 \tWASHINGTON\tDC\t20027-8523\n"
            "**As of July 01, 2026**\n"
        )
        records, unparseable = self._parse_text(text)
        self.assertEqual(len(records), 2)
        self.assertEqual(len(unparseable), 0)
        self.assertEqual({r.business_name for r in records}, {"AGILERANK LLC", "001VA LLC"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
