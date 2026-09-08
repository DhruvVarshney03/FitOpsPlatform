from fitops.storage import build_import_metadata, sha256_file
from fitops.workbook import load_workbook_contents


def test_sha256_file_is_stable(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text("fitops", encoding="utf-8")

    assert sha256_file(source) == sha256_file(source)
    assert len(sha256_file(source)) == 64


def test_import_metadata_tracks_source_and_counts():
    workbook_path = "Gym_Training_Log_Cleaned.xlsx"
    contents = load_workbook_contents(workbook_path)

    metadata = build_import_metadata(workbook_path, contents, import_id="test-import")

    assert metadata["import_id"] == "test-import"
    assert metadata["source_filename"] == workbook_path
    assert metadata["parser_version"] == "1.1"
    assert metadata["counts"] == {
        "workout_entries": 1173,
        "set_cells": 4692,
        "set_attempts": 3112,
        "exercise_library_entries": 111,
        "cleanup_notes": 11,
    }
