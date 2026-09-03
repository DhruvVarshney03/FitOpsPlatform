"""Deterministic parsing for the cleaned workout workbook."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

_SET_PAIR = re.compile(r"(?P<weight>\d+(?:\.\d+)?)\s*(?P<suffix>s)?\s*-\s*(?P<reps>\d+(?:\.\d+)?)")
_PERIOD = re.compile(r"(?P<start>\d{1,2})-(?P<start_month>\d{1,2})\s+to\s+(?P<end>\d{1,2})-(?P<end_month>\d{1,2})", re.I)


@dataclass(frozen=True)
class ParsedSet:
    raw_value: str
    weight_value: float
    weight_unit: str
    equipment_type: str | None
    reps: float
    note: str | None = None


@dataclass(frozen=True)
class ParsedSetCell:
    raw_value: str
    sets: tuple[ParsedSet, ...]
    note: str | None
    parse_status: str


@dataclass(frozen=True)
class ParsedPeriod:
    label: str
    period_start: date | None
    period_end: date | None
    date_precision: str
    location: str | None


def parse_set_cell(value: object) -> ParsedSetCell:
    """Extract set pairs while retaining the original notation and leftovers."""
    raw_value = "" if value is None else str(value).strip()
    if not raw_value or raw_value == ".":
        return ParsedSetCell(raw_value=raw_value, sets=(), note=None, parse_status="empty")

    matches = tuple(_SET_PAIR.finditer(raw_value))
    parsed_sets = tuple(
        ParsedSet(
            raw_value=match.group(0),
            weight_value=float(match.group("weight")),
            weight_unit="kg" if match.group("suffix") else "unknown",
            equipment_type="dumbbell" if match.group("suffix") else None,
            reps=float(match.group("reps")),
        )
        for match in matches
    )
    remainder = _SET_PAIR.sub(" ", raw_value)
    remainder = remainder.replace(",", " ")
    remainder = " ".join(remainder.split()).strip()
    status = "parsed" if matches and not remainder else "parsed_with_note" if matches else "note"
    return ParsedSetCell(
        raw_value=raw_value,
        sets=parsed_sets,
        note=remainder or None,
        parse_status=status,
    )


def parse_period(label: object, year: int | None = None) -> ParsedPeriod:
    """Parse explicit day-month ranges without inventing a year by default."""
    text = "" if label is None else str(label).strip()
    match = _PERIOD.search(text)
    start = end = None
    precision = "unknown"
    if match and year is not None:
        start = date(year, int(match.group("start_month")), int(match.group("start")))
        end_year = year + 1 if int(match.group("end_month")) < int(match.group("start_month")) else year
        end = date(end_year, int(match.group("end_month")), int(match.group("end")))
        precision = "week"
    elif match:
        precision = "week"
    elif re.search(r"week", text, re.I):
        precision = "week"

    location_match = re.search(r"\(([^()]*)\)", text)
    location = location_match.group(1).strip() if location_match else None
    return ParsedPeriod(
        label=text,
        period_start=start,
        period_end=end,
        date_precision=precision,
        location=location,
    )
