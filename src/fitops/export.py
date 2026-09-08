"""Export normalized workbook records to a reviewable JSON document."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path

from .workbook import WorkbookContents, load_workbook_contents


def _json_value(value: object) -> object:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    return value


def normalized_document(contents: WorkbookContents) -> dict[str, object]:
    """Create a stable, reviewable representation of normalized workbook data."""
    workout_entries: list[dict[str, object]] = []
    set_cells: list[dict[str, object]] = []
    set_attempts: list[dict[str, object]] = []
    for workout in contents.workouts:
        workout_id = f"{workout.source_tab}:{workout.source_row}"
        workout_entries.append(
            {
                "workout_id": workout_id,
                "source_tab": workout.source_tab,
                "source_row": workout.source_row,
                "session_label": workout.session_label,
                "day_label": workout.day_label,
                "exercise": workout.exercise,
                "category": workout.category,
                "target_sets": workout.target_sets,
                "target_reps": workout.target_reps,
                "rest": workout.rest,
                "period": _json_value(asdict(workout.period)),
                "early_rpe": workout.early_rpe,
                "last_set_rpe": workout.last_set_rpe,
                "notes": workout.notes,
                "skipped": workout.skipped,
            }
        )
        for set_number, cell in enumerate(workout.set_cells, start=1):
            set_cells.append(
                {
                    "workout_id": workout_id,
                    "set_column": f"Set {set_number}",
                    "raw_cell_value": cell.raw_value,
                    "parse_status": cell.parse_status,
                    "parsed_note": cell.note,
                    "parsed_attempt_count": len(cell.sets),
                }
            )
            for attempt_number, parsed_set in enumerate(cell.sets, start=1):
                set_attempts.append(
                    {
                        "workout_id": workout_id,
                        "set_column": f"Set {set_number}",
                        "attempt_number": attempt_number,
                        "raw_cell_value": cell.raw_value,
                        "parse_status": cell.parse_status,
                        "parsed_note": cell.note,
                        **_json_value(asdict(parsed_set)),
                    }
                )

    return {
        "schema_version": "1.1",
        "source": "Gym_Training_Log_Cleaned.xlsx",
        "counts": {
            "workout_entries": len(workout_entries),
            "set_cells": len(set_cells),
            "set_attempts": len(set_attempts),
            "exercise_library_entries": len(contents.exercise_library),
            "cleanup_notes": len(contents.cleanup_notes),
        },
        "workout_entries": workout_entries,
        "set_cells": set_cells,
        "set_attempts": set_attempts,
        "exercise_library": list(contents.exercise_library),
        "cleanup_notes": list(contents.cleanup_notes),
    }


def export_normalized_json(
    workbook_path: str | Path,
    output_path: str | Path,
    year: int | None = None,
) -> Path:
    """Normalize a workbook and write its reviewable JSON export."""
    contents = load_workbook_contents(workbook_path, year=year)
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(normalized_document(contents), indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return destination
