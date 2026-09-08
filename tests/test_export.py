import json

from fitops.export import export_normalized_json, normalized_document
from fitops.workbook import WorkbookContents


def test_normalized_document_flattens_set_attempts():
    contents = WorkbookContents(workouts=(), exercise_library=(), cleanup_notes=())

    document = normalized_document(contents)

    assert document["schema_version"] == "1.1"
    assert document["counts"] == {
        "workout_entries": 0,
        "set_cells": 0,
        "set_attempts": 0,
        "exercise_library_entries": 0,
        "cleanup_notes": 0,
    }


def test_export_writes_valid_json(tmp_path):
    output_path = tmp_path / "normalized.json"

    result = export_normalized_json("Gym_Training_Log_Cleaned.xlsx", output_path)
    document = json.loads(result.read_text(encoding="utf-8"))

    assert result == output_path
    assert document["counts"]["workout_entries"] == 1173
    assert document["counts"]["set_cells"] == 4692
    assert document["counts"]["set_attempts"] == 3112
    assert document["counts"]["exercise_library_entries"] == 111
    assert document["set_attempts"][0]["raw_cell_value"]
    assert document["set_cells"][0]["set_column"] == "Set 1"
