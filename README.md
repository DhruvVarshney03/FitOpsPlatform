# FitOps Engine

A local-first MLOps platform for importing workout history, tracking daily training, and forecasting strength progression. The project is designed to be useful day to day while keeping each infrastructure and data decision inspectable.

## Current State

The cleaned workbook is treated as a historical import source. The first implementation slice provides a deterministic normalizer in `fitops.workbook` and a conservative set parser in `fitops.importer`.

The parser preserves every raw set cell and extracts only recognizable weight-rep pairs:

- `5s-10` becomes a 5 kg dumbbell set with 10 reps.
- `15-2,10-6` becomes two set attempts.
- `50-6+1 with help` becomes one set plus the note `+1 with help`.
- Text such as `myo reps` or `next up the weight of set` remains a note.
- Bare numeric weights remain `unknown` units until exercise context confirms kg or machine plates.

Historical periods retain their original label. Explicit ranges can produce start and end dates when a year is supplied; week labels do not receive invented calendar dates.

## Quick Start

```bash
# Install locked dependencies
uv sync --extra dev

# Run the test suite
uv run pytest -q

# Inspect the workbook normalization
uv run python - <<'PY'
from fitops.workbook import load_workbook_contents

contents = load_workbook_contents("Gym_Training_Log_Cleaned.xlsx")
print(len(contents.workouts), "workout rows")
print(len(contents.exercise_library), "library entries")
PY

# Export normalized records locally for review
uv run python -c \
  'from fitops.export import export_normalized_json; export_normalized_json("Gym_Training_Log_Cleaned.xlsx", "normalized-data/workbook-normalized.json")'
```

## Project Goals

- Import the historical Excel workbook without losing original notation.
- Support future CSV, JSON, and manual workout entries through the same normalized schema.
- Store raw artifacts in LocalStack S3 and structured records in local PostgreSQL.
- Train explainable progression and peak-performance models.
- Serve predictions through FastAPI and operate the stack on Docker Compose and Kind.
- Add Terraform, Kubernetes, Prometheus, Grafana, local CI, and SRE runbooks incrementally.

## Data Contract

The normalized model has one workout-entry record per `Master Log` row and one parsed set-attempt record for each recognized pair. Each record retains its source tab, source row, session label, raw set value, notes, and parse status. Machine plate counts remain exercise-specific and are never converted to kilograms. `25s` is interpreted as 25 kg dumbbells.

The workbook currently contains 1,173 master rows, 58 explicit skipped rows, and 111 populated exercise-library entries. The current `Exercise Library` tab is authoritative; the importer reads and preserves those 111 entries dynamically.

The local export at `normalized-data/workbook-normalized.json` uses schema `1.1` and contains the normalized workout entries, every original set cell (including blank and note-only cells), flattened parsed set attempts, exercise library, cleanup notes, source provenance, and raw set-cell values. It is generated from the workbook and excluded from GitHub along with the workbook itself.

## Local Storage

Docker Compose provides PostgreSQL on `localhost:5432` and LocalStack S3 on `localhost:4566`. Start the services with:

```bash
docker compose up -d
```

After installing the project dependencies with `uv sync --extra dev`, import the local workbook with:

```bash
uv run python scripts/import_to_storage.py Gym_Training_Log_Cleaned.xlsx
```

The importer stores the raw workbook and normalized JSON under an import-specific S3 prefix, and inserts the structured records into PostgreSQL. Source checksums make repeated imports idempotent. The workbook and normalized output remain local and are excluded from GitHub.

## Terraform

The `terraform/` module owns the LocalStack `fitops-raw` S3 bucket and the Kubernetes `fitops` namespace. PostgreSQL remains owned by Docker Compose because its schema is initialized from `storage/schema.sql`.

Validate the module with:

```bash
terraform -chdir=terraform init
terraform -chdir=terraform fmt -check
terraform -chdir=terraform validate
```

If you are already inside the Terraform directory, the equivalent commands are:

```bash
cd terraform
terraform init
terraform fmt -check
terraform validate
```

After Docker Compose is running, apply the LocalStack resources with:

```bash
terraform -chdir=terraform import aws_s3_bucket.raw fitops-raw  # one-time, if the bucket already exists
terraform -chdir=terraform apply -auto-approve
```

Kubernetes provisioning is disabled by default. Once Kind is available, enable it explicitly:

```bash
terraform -chdir=terraform apply -var='enable_kubernetes=true' -auto-approve
```

## Repository Layout

- `src/fitops/importer.py` - deterministic set and period parsing
- `src/fitops/workbook.py` - cleaned workbook normalization
- `src/fitops/export.py` - reviewable JSON export
- `src/fitops/storage.py` - PostgreSQL and LocalStack adapters
- `scripts/import_to_storage.py` - end-to-end local import command
- `storage/schema.sql` - PostgreSQL schema
- `terraform/` - LocalStack and Kubernetes IaC
- `tests/` - parser, export, and storage tests
- `uv.lock` - locked Python dependencies

## Development

See [AGENTS.md](AGENTS.md) for detailed development guidelines and conventions.

## Resources

- [Python DevOps Best Practices](https://docs.python-guide.org/)
- [Infrastructure as Code](https://www.terraform.io/language)
- [GitHub Actions Documentation](https://docs.github.com/actions)

---

**Last Updated**: 2026-09-07
