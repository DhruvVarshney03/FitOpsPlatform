CREATE TABLE IF NOT EXISTS imports (
    import_id TEXT PRIMARY KEY,
    source_filename TEXT NOT NULL,
    source_sha256 TEXT NOT NULL UNIQUE,
    parser_version TEXT NOT NULL,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    workout_entry_count INTEGER NOT NULL,
    set_cell_count INTEGER NOT NULL,
    set_attempt_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS exercise_library (
    canonical_exercise TEXT PRIMARY KEY,
    category TEXT,
    times_logged INTEGER,
    raw_name_variants TEXT
);

CREATE TABLE IF NOT EXISTS workout_entries (
    import_id TEXT NOT NULL REFERENCES imports(import_id),
    workout_id TEXT NOT NULL,
    source_tab TEXT NOT NULL,
    source_row INTEGER NOT NULL,
    session_label TEXT NOT NULL,
    day_label TEXT NOT NULL,
    exercise TEXT NOT NULL,
    category TEXT,
    target_sets TEXT,
    target_reps TEXT,
    rest TEXT,
    period_label TEXT,
    period_start DATE,
    period_end DATE,
    date_precision TEXT NOT NULL,
    location TEXT,
    early_rpe TEXT,
    last_set_rpe TEXT,
    notes TEXT,
    skipped BOOLEAN NOT NULL,
    PRIMARY KEY (import_id, workout_id)
);

CREATE TABLE IF NOT EXISTS set_cells (
    import_id TEXT NOT NULL,
    workout_id TEXT NOT NULL,
    set_column TEXT NOT NULL,
    raw_cell_value TEXT NOT NULL,
    parse_status TEXT NOT NULL,
    parsed_note TEXT,
    parsed_attempt_count INTEGER NOT NULL,
    PRIMARY KEY (import_id, workout_id, set_column),
    FOREIGN KEY (import_id, workout_id) REFERENCES workout_entries(import_id, workout_id)
);

CREATE TABLE IF NOT EXISTS set_attempts (
    import_id TEXT NOT NULL,
    workout_id TEXT NOT NULL,
    set_column TEXT NOT NULL,
    attempt_number INTEGER NOT NULL,
    raw_cell_value TEXT NOT NULL,
    parse_status TEXT NOT NULL,
    parsed_note TEXT,
    raw_value TEXT NOT NULL,
    weight_value DOUBLE PRECISION NOT NULL,
    weight_unit TEXT NOT NULL,
    equipment_type TEXT,
    reps DOUBLE PRECISION NOT NULL,
    note TEXT,
    PRIMARY KEY (import_id, workout_id, set_column, attempt_number),
    FOREIGN KEY (import_id, workout_id) REFERENCES workout_entries(import_id, workout_id)
);

CREATE TABLE IF NOT EXISTS cleanup_notes (
    import_id TEXT NOT NULL REFERENCES imports(import_id),
    note_number INTEGER NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY (import_id, note_number)
);

CREATE INDEX IF NOT EXISTS idx_workout_entries_exercise
    ON workout_entries (exercise, period_start);
CREATE INDEX IF NOT EXISTS idx_set_attempts_workout
    ON set_attempts (workout_id, set_column);
