"""Repository helpers — CRUD operations on SQLite tables."""

import json
import sqlite3


def insert_document(conn: sqlite3.Connection, filename: str, title: str = None, source: str = None) -> int:
    cur = conn.execute(
        "INSERT INTO documents (filename, title, source) VALUES (?, ?, ?)",
        (filename, title, source),
    )
    conn.commit()
    return cur.lastrowid


def update_document_total_chunks(conn: sqlite3.Connection, doc_id: int, total: int) -> None:
    conn.execute("UPDATE documents SET total_chunks = ? WHERE id = ?", (total, doc_id))
    conn.commit()


def insert_chunk(conn: sqlite3.Connection, document_id: int, chunk_index: int, content: str) -> int:
    cur = conn.execute(
        "INSERT INTO chunks (document_id, chunk_index, content, char_count) VALUES (?, ?, ?, ?)",
        (document_id, chunk_index, content, len(content)),
    )
    conn.commit()
    return cur.lastrowid


def insert_extracted_entity(
    conn: sqlite3.Connection,
    chunk_id: int,
    document_id: int,
    entity: dict,
    extraction_raw: str,
    model: str,
) -> int:
    cur = conn.execute(
        """
        INSERT INTO extracted_entities (
            chunk_id, document_id,
            company_name, industry,
            revenue, revenue_unit, revenue_period,
            net_profit, net_profit_unit, net_profit_period,
            growth_rate,
            event_date, event_summary,
            key_persons, location,
            stock_code, stock_exchange,
            extraction_raw, confidence_score, extraction_model
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            chunk_id,
            document_id,
            entity.get("company_name"),
            entity.get("industry"),
            entity.get("revenue"),
            entity.get("revenue_unit"),
            entity.get("revenue_period"),
            entity.get("net_profit"),
            entity.get("net_profit_unit"),
            entity.get("net_profit_period"),
            entity.get("growth_rate"),
            entity.get("event_date"),
            entity.get("event_summary"),
            json.dumps(entity.get("key_persons"), ensure_ascii=False) if entity.get("key_persons") else None,
            entity.get("location"),
            entity.get("stock_code"),
            entity.get("stock_exchange"),
            extraction_raw,
            entity.get("confidence_score"),
            model,
        ),
    )
    conn.commit()
    return cur.lastrowid


def get_extracted_entities_for_chunks(
    conn: sqlite3.Connection, chunk_ids: list[int]
) -> list[dict]:
    """Fetch extracted entities for a list of chunk IDs."""
    placeholders = ",".join("?" * len(chunk_ids))
    rows = conn.execute(
        f"SELECT * FROM extracted_entities WHERE chunk_id IN ({placeholders})",
        chunk_ids,
    ).fetchall()
    return [dict(row) for row in rows]


def get_all_extracted_entities(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT * FROM extracted_entities").fetchall()
    return [dict(row) for row in rows]


def insert_analysis_report(
    conn: sqlite3.Connection,
    query_text: str,
    retrieved_chunk_ids: list[int],
    report_content: str,
    model: str,
    generation_time_ms: int,
) -> int:
    cur = conn.execute(
        "INSERT INTO analysis_reports (query_text, retrieved_chunk_ids, report_content, model_used, generation_time_ms) VALUES (?, ?, ?, ?, ?)",
        (
            query_text,
            json.dumps(retrieved_chunk_ids),
            report_content,
            model,
            generation_time_ms,
        ),
    )
    conn.commit()
    return cur.lastrowid


def insert_evaluation_result(
    conn: sqlite3.Connection,
    evaluation_type: str,
    metric_name: str,
    metric_value: float,
    reference_id: int = None,
    details: str = None,
) -> int:
    cur = conn.execute(
        "INSERT INTO evaluation_results (evaluation_type, reference_id, metric_name, metric_value, details) VALUES (?, ?, ?, ?, ?)",
        (evaluation_type, reference_id, metric_name, metric_value, details),
    )
    conn.commit()
    return cur.lastrowid
