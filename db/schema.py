"""SQLite schema — DDL for all 5 tables."""

CREATE_DOCUMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS documents (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    filename        TEXT    NOT NULL,
    title           TEXT,
    source          TEXT,
    total_chunks    INTEGER DEFAULT 0,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_CHUNKS_TABLE = """
CREATE TABLE IF NOT EXISTS chunks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id     INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index     INTEGER NOT NULL,
    content         TEXT    NOT NULL,
    char_count      INTEGER,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id, chunk_index)
);
"""

CREATE_EXTRACTED_ENTITIES_TABLE = """
CREATE TABLE IF NOT EXISTS extracted_entities (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id          INTEGER NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    document_id       INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    company_name      TEXT,
    industry          TEXT,
    revenue           REAL,
    revenue_unit      TEXT,
    revenue_period    TEXT,
    net_profit        REAL,
    net_profit_unit   TEXT,
    net_profit_period TEXT,
    growth_rate       REAL,
    event_date        TEXT,
    event_summary     TEXT,
    key_persons       TEXT,
    location          TEXT,
    stock_code        TEXT,
    stock_exchange    TEXT,
    extraction_raw    TEXT,
    confidence_score  REAL,
    extraction_model  TEXT,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_entities_company ON extracted_entities(company_name);
CREATE INDEX IF NOT EXISTS idx_entities_doc ON extracted_entities(document_id);
CREATE INDEX IF NOT EXISTS idx_entities_event_date ON extracted_entities(event_date);
"""

CREATE_ANALYSIS_REPORTS_TABLE = """
CREATE TABLE IF NOT EXISTS analysis_reports (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text          TEXT    NOT NULL,
    retrieved_chunk_ids TEXT,
    report_content      TEXT,
    model_used          TEXT,
    generation_time_ms  INTEGER,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_EVALUATION_RESULTS_TABLE = """
CREATE TABLE IF NOT EXISTS evaluation_results (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    evaluation_type   TEXT NOT NULL,
    reference_id      INTEGER,
    metric_name       TEXT NOT NULL,
    metric_value      REAL NOT NULL,
    details           TEXT,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

ALL_TABLES = [
    CREATE_DOCUMENTS_TABLE,
    CREATE_CHUNKS_TABLE,
    CREATE_EXTRACTED_ENTITIES_TABLE,
    CREATE_ANALYSIS_REPORTS_TABLE,
    CREATE_EVALUATION_RESULTS_TABLE,
]


def init_db(conn) -> None:
    """Run all CREATE TABLE statements on the given connection."""
    for ddl in ALL_TABLES:
        conn.executescript(ddl)
    conn.commit()
