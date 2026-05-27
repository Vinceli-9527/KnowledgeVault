"""Utility helpers: JSON parsing, retry logic, timing, logging."""

import json
import re
import time
import logging
import functools
from contextlib import contextmanager

# ---- JSON Safe Parse ----


def safe_json_parse(text: str) -> dict | None:
    """Try to parse JSON from LLM response, with repair fallbacks."""
    if not text:
        return None
    text = text.strip()

    # Attempt 1: direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Attempt 2: extract from markdown code fence
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Attempt 3: find first { ... } block
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass

    return None


# ---- Retry ----


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator: retry on common API errors with exponential backoff."""

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2**attempt)
                        logging.warning(
                            "Retry %d/%d for %s after %.1fs: %s",
                            attempt + 1,
                            max_retries,
                            func.__name__,
                            delay,
                            e,
                        )
                        time.sleep(delay)
            raise last_exc  # type: ignore

        return wrapper

    return decorator


# ---- Timer ----


@contextmanager
def timer_context(label: str):
    """Context manager that prints elapsed time for a block."""
    start = time.perf_counter()
    print(f"[START] {label} ...")
    yield
    elapsed = time.perf_counter() - start
    print(f"[DONE]  {label} — {elapsed:.2f}s")


# ---- Logging ----


def setup_logging(log_file: str | None = None):
    """Configure logging to console (INFO) and optionally a file (DEBUG)."""
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    # File handler
    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(fmt)
        root.addHandler(fh)
