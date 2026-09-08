"""Persistence adapters for local PostgreSQL and LocalStack S3."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

from .export import normalized_document
from .workbook import WorkbookContents

PARSER_VERSION = "1.1"


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_import_metadata(
    workbook_path: str | Path,
    contents: WorkbookContents,
    import_id: str | None = None,
) -> dict[str, Any]:
    document = normalized_document(contents)
    return {
        "import_id": import_id or str(uuid4()),
        "source_filename": Path(workbook_path).name,
        "source_sha256": sha256_file(workbook_path),
        "parser_version": PARSER_VERSION,
        "counts": document["counts"],
    }


def create_s3_client() -> Any:
    import boto3

    return boto3.client(
        "s3",
        endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"),
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "test"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "test"),
    )


def upload_import_artifacts(
    workbook_path: str | Path,
    normalized_json_path: str | Path,
    import_id: str,
    bucket: str | None = None,
    client: Any | None = None,
) -> dict[str, str]:
    """Upload raw and normalized artifacts, returning their object keys."""
    bucket_name = bucket or os.getenv("FITOPS_RAW_BUCKET", "fitops-raw")
    s3 = client or create_s3_client()
    workbook_key = f"imports/{import_id}/raw/{Path(workbook_path).name}"
    normalized_key = f"imports/{import_id}/normalized/workbook-normalized.json"
    s3.upload_file(str(workbook_path), bucket_name, workbook_key)
    s3.upload_file(str(normalized_json_path), bucket_name, normalized_key)
    return {"raw_key": workbook_key, "normalized_key": normalized_key}


def insert_normalized_document(connection: Any, document: dict[str, Any], metadata: dict[str, Any]) -> bool:
    """Insert one normalized import, returning False when its checksum already exists."""
    counts = metadata["counts"]
    with connection.cursor() as cursor:
        cursor.execute(
            """INSERT INTO imports
            (import_id, source_filename, source_sha256, parser_version,
             workout_entry_count, set_cell_count, set_attempt_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (source_sha256) DO NOTHING
            RETURNING import_id""",
            (
                metadata["import_id"], metadata["source_filename"], metadata["source_sha256"],
                metadata["parser_version"], counts["workout_entries"], counts["set_cells"],
                counts["set_attempts"],
            ),
        )
        if cursor.fetchone() is None:
            connection.rollback()
            return False
        for entry in document["workout_entries"]:
            period = entry["period"]
            cursor.execute(
                """INSERT INTO workout_entries
                (import_id, workout_id, source_tab, source_row, session_label, day_label,
                 exercise, category, target_sets, target_reps, rest, period_label,
                 period_start, period_end, date_precision, location, early_rpe,
                 last_set_rpe, notes, skipped)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING""",
                (
                    metadata["import_id"], entry["workout_id"], entry["source_tab"], entry["source_row"],
                    entry["session_label"], entry["day_label"], entry["exercise"], entry["category"],
                    entry["target_sets"], entry["target_reps"], entry["rest"], period["label"],
                    period["period_start"], period["period_end"], period["date_precision"],
                    period["location"], entry["early_rpe"], entry["last_set_rpe"], entry["notes"],
                    entry["skipped"],
                ),
            )
        for cell in document["set_cells"]:
            cursor.execute(
                """INSERT INTO set_cells
                (import_id, workout_id, set_column, raw_cell_value, parse_status,
                 parsed_note, parsed_attempt_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING""",
                (
                    metadata["import_id"], cell["workout_id"], cell["set_column"],
                    cell["raw_cell_value"], cell["parse_status"], cell["parsed_note"],
                    cell["parsed_attempt_count"],
                ),
            )
        for attempt in document["set_attempts"]:
            cursor.execute(
                """INSERT INTO set_attempts
                (import_id, workout_id, set_column, attempt_number, raw_cell_value,
                 parse_status, parsed_note, raw_value, weight_value, weight_unit,
                 equipment_type, reps, note)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING""",
                (
                    metadata["import_id"], attempt["workout_id"], attempt["set_column"],
                    attempt["attempt_number"], attempt["raw_cell_value"], attempt["parse_status"],
                    attempt["parsed_note"], attempt["raw_value"], attempt["weight_value"],
                    attempt["weight_unit"], attempt["equipment_type"], attempt["reps"], attempt["note"],
                ),
            )
        for index, note in enumerate(document["cleanup_notes"], start=1):
            cursor.execute(
                """INSERT INTO cleanup_notes (import_id, note_number, note)
                VALUES (%s, %s, %s) ON CONFLICT DO NOTHING""",
                (metadata["import_id"], index, note),
            )
    connection.commit()
    return True


def load_normalized_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
