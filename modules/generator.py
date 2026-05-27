"""Report generator — LLM-powered analysis report generation."""

import json
import logging
import time
import openai

from prompts.generation import build_generation_messages, GENERATION_SYSTEM
from db.repository import get_extracted_entities_for_chunks
from modules.privacy import redact_retrieved

logger = logging.getLogger(__name__)


def build_structured_summary(entities: list[dict]) -> str:
    """Build a text summary from extracted entities for the generation prompt."""
    if not entities:
        return "（无结构化数据）"

    lines = []
    for e in entities:
        parts = []
        if e.get("company_name"):
            parts.append(f"公司：{e['company_name']}")
        if e.get("industry"):
            parts.append(f"行业：{e['industry']}")
        if e.get("location"):
            parts.append(f"地点：{e['location']}")
        if e.get("revenue") is not None:
            parts.append(f"营收：{e['revenue']}{e.get('revenue_unit', '')} ({e.get('revenue_period', '')})")
        if e.get("net_profit") is not None:
            parts.append(f"净利润：{e['net_profit']}{e.get('net_profit_unit', '')} ({e.get('net_profit_period', '')})")
        if e.get("growth_rate") is not None:
            parts.append(f"增长率：{e['growth_rate']}%")
        if e.get("event_date") and e.get("event_summary"):
            parts.append(f"事件：{e['event_date']} — {e['event_summary']}")
        if e.get("key_persons"):
            kp = json.loads(e["key_persons"]) if isinstance(e["key_persons"], str) else e["key_persons"]
            parts.append(f"关键人物：{', '.join(kp)}")
        if e.get("stock_code"):
            parts.append(f"股票：{e['stock_code']}.{e.get('stock_exchange', '')}")
        if parts:
            lines.append("  |  ".join(parts))
    return "\n".join(lines)


def generate_report(
    client: openai.OpenAI,
    conn,
    query: str,
    retrieved_chunks: list[dict],
    model: str,
    temperature: float = 0.3,
    timeout: int = 120,
) -> dict:
    """Generate an analysis report using DeepSeek with RAG context.

    Returns dict with keys:
        report              — markdown report text
        generation_time_ms  — milliseconds taken
        prompt_system       — system message content
        prompt_user         — user message content (with injected context)
    """
    chunk_ids = [int(c["metadata"]["chunk_id"]) for c in retrieved_chunks]
    entities = get_extracted_entities_for_chunks(conn, chunk_ids)

    # Redact PII from retrieved chunks before they reach the LLM API
    redacted_chunks, redaction_count = redact_retrieved(retrieved_chunks)

    from modules.retriever import format_retrieved_context

    retrieved_contexts = format_retrieved_context(redacted_chunks)
    structured_summary = build_structured_summary(entities)

    messages = build_generation_messages(
        user_query=query,
        retrieved_contexts=retrieved_contexts,
        structured_summary=structured_summary,
    )

    start = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        timeout=timeout,
    )
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    report = response.choices[0].message.content or ""
    logger.info("Report generated in %dms, length=%d chars, PII redacted=%d", elapsed_ms, len(report), redaction_count)

    return {
        "report": report,
        "generation_time_ms": elapsed_ms,
        "prompt_system": messages[0]["content"],
        "prompt_user": messages[1]["content"],
        "pii_redacted": redaction_count,
    }
