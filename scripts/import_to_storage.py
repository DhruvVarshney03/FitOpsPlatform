#!/usr/bin/env python3
"""Import the local workbook into PostgreSQL and LocalStack S3."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from fitops.export import export_normalized_json
from fitops.storage import (
    build_import_metadata,
    insert_normalized_document,
    load_normalized_json,
    upload_import_artifacts,
)
from fitops.workbook import load_workbook_contents


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--normalized-output", type=Path, default=Path("normalized-data/workbook-normalized.json"))
    args = parser.parse_args()

    contents = load_workbook_contents(args.workbook)
    export_normalized_json(args.workbook, args.normalized_output)
    metadata = build_import_metadata(args.workbook, contents)
    artifacts = upload_import_artifacts(args.workbook, args.normalized_output, metadata["import_id"])

    import psycopg

    connection = psycopg.connect(os.getenv("FITOPS_DATABASE_URL", "postgresql://fitops:fitops-local@localhost:5432/fitops"))
    try:
        inserted = insert_normalized_document(
            connection, load_normalized_json(args.normalized_output), metadata
        )
    finally:
        connection.close()

    print(f"import_id={metadata['import_id']}")
    print(f"inserted={inserted}")
    print(f"sha256={metadata['source_sha256']}")
    print(f"raw_s3_key={artifacts['raw_key']}")
    print(f"normalized_s3_key={artifacts['normalized_key']}")


if __name__ == "__main__":
    main()
