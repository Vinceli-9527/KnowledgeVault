"""Document loader — read .txt files from sample_docs directory."""

import os
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Document:
    filename: str
    title: str
    content: str
    source: str


def load_documents(docs_dir: str) -> list[Document]:
    """Load all .txt files from the given directory.

    The first line of each file is treated as the document title.
    """
    docs = []
    doc_path = Path(docs_dir)
    if not doc_path.exists():
        raise FileNotFoundError(f"Documents directory not found: {docs_dir}")

    for txt_file in sorted(doc_path.glob("*.txt")):
        content = txt_file.read_text(encoding="utf-8").strip()
        if not content:
            continue
        lines = content.split("\n", 1)
        title = lines[0].strip() if lines else txt_file.stem
        body = lines[1].strip() if len(lines) > 1 else content

        docs.append(
            Document(
                filename=txt_file.name,
                title=title,
                content=body,
                source=str(txt_file),
            )
        )

    return docs
