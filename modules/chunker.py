"""Text chunker — paragraph-aware splitting with overlap."""

import re
from dataclasses import dataclass


@dataclass
class Chunk:
    document_id: int
    chunk_index: int
    content: str
    char_count: int


def _split_by_sentence(text: str, max_chars: int) -> list[str]:
    """Split a long paragraph into chunks at sentence boundaries."""
    sentences = re.split(r"(?<=[。！？；\n])\s*", text)
    chunks = []
    current = ""
    for sent in sentences:
        if len(current) + len(sent) <= max_chars:
            current += sent
        else:
            if current:
                chunks.append(current.strip())
            current = sent
    if current.strip():
        chunks.append(current.strip())
    return chunks


def chunk_document(
    document_id: int,
    text: str,
    max_chars: int = 1000,
    overlap_chars: int = 200,
    min_chars: int = 50,
) -> list[Chunk]:
    """Split document text into overlapping chunks.

    Strategy:
    1. Split by paragraphs (double newline)
    2. If a paragraph exceeds max_chars, split at sentence boundaries
    3. Merge short adjacent paragraphs when possible
    4. Apply overlap between consecutive chunks
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    raw_chunks = []

    # Step 1-2: split long paragraphs
    for para in paragraphs:
        if len(para) <= max_chars:
            if para:
                raw_chunks.append(para)
        else:
            raw_chunks.extend(_split_by_sentence(para, max_chars))

    # Step 3: filter short chunks
    raw_chunks = [c for c in raw_chunks if len(c) >= min_chars]

    # Step 4: build final chunks with overlap
    result = []
    idx = 0
    for rc in raw_chunks:
        chunk_content = rc
        # Prepend overlap from previous chunk
        if idx > 0 and overlap_chars > 0:
            prev = raw_chunks[idx - 1]
            overlap_text = prev[-overlap_chars:] if len(prev) > overlap_chars else prev
            chunk_content = overlap_text + "\n...\n" + rc

        result.append(
            Chunk(
                document_id=document_id,
                chunk_index=idx,
                content=chunk_content,
                char_count=len(chunk_content),
            )
        )
        idx += 1

    return result
