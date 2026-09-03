from datetime import date

from fitops.importer import parse_period, parse_set_cell


def test_parses_dumbbell_suffix_as_kg():
    parsed = parse_set_cell("7.5s-10")

    assert parsed.parse_status == "parsed"
    assert parsed.sets[0].weight_value == 7.5
    assert parsed.sets[0].weight_unit == "kg"
    assert parsed.sets[0].equipment_type == "dumbbell"
    assert parsed.sets[0].reps == 10


def test_parses_multiple_pairs_in_drop_set_cell():
    parsed = parse_set_cell("15-2,10-6")

    assert [(item.weight_value, item.reps) for item in parsed.sets] == [(15, 2), (10, 6)]
    assert parsed.note is None


def test_preserves_assistance_note_after_pair():
    parsed = parse_set_cell("50-6+1 with help")

    assert len(parsed.sets) == 1
    assert parsed.note == "+1 with help"
    assert parsed.parse_status == "parsed_with_note"


def test_keeps_prose_as_note():
    parsed = parse_set_cell("next up the weight of set")

    assert parsed.sets == ()
    assert parsed.note == "next up the weight of set"
    assert parsed.parse_status == "note"


def test_explicit_period_requires_year_to_create_dates():
    without_year = parse_period("24-08 to 30-08 (Blr)")
    with_year = parse_period("24-08 to 30-08 (Blr)", year=2026)

    assert without_year.period_start is None
    assert without_year.period_end is None
    assert without_year.date_precision == "week"
    assert with_year.period_start == date(2026, 8, 24)
    assert with_year.period_end == date(2026, 8, 30)
    assert with_year.location == "Blr"
