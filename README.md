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
# Run the focused tests
cd fitops-engine
PYTHONPATH=src .venv/bin/python -m pytest -q

# Inspect the workbook normalization
PYTHONPATH=src .venv/bin/python - <<'PY'
from fitops.workbook import load_workbook_contents

contents = load_workbook_contents("Gym_Training_Log_Cleaned.xlsx")
print(len(contents.workouts), "workout rows")
print(len(contents.exercise_library), "library entries")
PY

# The virtual environment can be created with:
# python -m venv .venv
# .venv/bin/pip install -e '.[dev]'
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

## Repository Layout

- `fitops-engine/src/fitops/importer.py` - deterministic set and period parsing
- `fitops-engine/src/fitops/workbook.py` - cleaned workbook normalization
- `fitops-engine/tests/` - focused parser tests
- `fitops-engine/Gym_Training_Log_Cleaned.xlsx` - preserved historical source workbook
- `bin/act` - GitHub Actions local testing utility

## Development

See [AGENTS.md](AGENTS.md) for detailed development guidelines and conventions.

## Resources

- [Python DevOps Best Practices](https://docs.python-guide.org/)
- [Infrastructure as Code](https://www.terraform.io/language)
- [GitHub Actions Documentation](https://docs.github.com/actions)

---

**Last Updated**: 2026-09-03
