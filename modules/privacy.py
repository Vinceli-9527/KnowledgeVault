"""PII redaction — scrubs sensitive data before prompts reach the LLM API.

Detects and replaces: phone numbers, ID card numbers, bank card numbers,
email addresses, person names in common patterns, and tabular data.
"""

import re
import logging

logger = logging.getLogger(__name__)

# ── Detection patterns (order matters: specific before general) ──────

_PATTERNS = [
    # Phone: exactly 11 digits starting with 1, not part of a longer digit sequence
    (re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"), "[手机号已隐藏]"),

    # ID card: exactly 18 chars (17 digits + digit/X), not part of a longer sequence
    (re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)"), "[身份证号已隐藏]"),

    # Email
    (re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"), "[邮箱已隐藏]"),

    # Bank card: 16-19 isolated digits (only after phone/ID are redacted)
    (re.compile(r"(?<!\d)\d{16,19}(?!\d)"), "[银行卡号已隐藏]"),

    # Names in common intro patterns: "姓名：张三", "联系人：李四", "法定代表人：王五"
    (re.compile(r"(?:姓名|联系人|法定代表人|负责人|经办人|法人代表|授权人|受托人|签字人)[：:]\s*[一-鿿]{2,4}"),
     lambda m: m.group(0)[:m.group(0).index("：") if "：" in m.group(0) else m.group(0).index(":")] +
               ("：[姓名已隐藏]" if "：" in m.group(0) else ":[姓名已隐藏]")),

    # Tabular data: markdown tables or 4+ pipe-separated columns
    (re.compile(r"\|[^\n|]+\|[^\n|]+\|[^\n|]+\|[^\n|]+\|.*"), "[表格行已隐藏]"),

    # Tabular data: lines with 3+ tab characters (TSV)
    (re.compile(r"[^\t\n]+\t[^\t\n]+\t[^\t\n]+\t[^\t\n]+.*"), "[表格行已隐藏]"),

    # Numeric grid: lines with 5+ numbers separated by spaces/commas
    (re.compile(r"[\d.,%]+\s{2,}[\d.,%]+\s{2,}[\d.,%]+\s{2,}[\d.,%]+\s{2,}[\d.,%]+.*"), "[数据行已隐藏]"),
]

# ── Compile-time aggregated fallback for quick scan ───────────────────

_PII_PATTERNS_COMBINED = re.compile(
    r"|".join(f"(?:{p.pattern})" for p in _PATTERNS if hasattr(p, "pattern"))
)


def redact_text(text: str) -> tuple[str, int]:
    """Redact PII from a single text string.

    Returns (redacted_text, replacement_count).
    """
    if not text:
        return text, 0

    result = text
    count = 0

    for pattern, replacement in _PATTERNS:
        matches = list(pattern.finditer(result))
        if not matches:
            continue
        # Replace from right to left to preserve positions
        for m in reversed(matches):
            if callable(replacement):
                repl = replacement(m)
            else:
                repl = str(replacement)
            result = result[:m.start()] + repl + result[m.end():]
            count += 1

    return result, count


def redact_chunks(chunks: list[str]) -> tuple[list[str], int]:
    """Redact a list of text chunks. Returns (redacted_chunks, total_redactions)."""
    total = 0
    redacted = []
    for chunk in chunks:
        r, c = redact_text(chunk)
        redacted.append(r)
        total += c
    if total:
        logger.info("PII redaction: %d field(s) hidden across %d chunks", total, len(chunks))
    return redacted, total


def redact_retrieved(chunks: list[dict]) -> tuple[list[dict], int]:
    """Redact the 'document' field of retrieved ChromaDB result dicts (in-place copy)."""
    total = 0
    redacted = []
    for c in chunks:
        doc_text = c.get("document", "")
        r_text, cnt = redact_text(doc_text)
        total += cnt
        rc = dict(c)
        rc["document"] = r_text
        redacted.append(rc)
    if total:
        logger.info("PII redaction: %d field(s) hidden in retrieved chunks", total)
    return redacted, total
