"""Retrieval module — embed query and search ChromaDB for relevant chunks."""

import logging
import chromadb
from sentence_transformers import SentenceTransformer

from modules.embedder import encode_text

logger = logging.getLogger(__name__)


def retrieve_relevant_chunks(
    model: SentenceTransformer,
    collection: chromadb.Collection,
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """Embed a query and retrieve top-k relevant chunks from ChromaDB.

    Returns list of dicts with keys: id, document, metadata, distance.
    """
    query_embedding = encode_text(model, query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    chunks = []
    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    for i in range(len(ids)):
        chunks.append(
            {
                "id": ids[i],
                "document": documents[i],
                "metadata": metadatas[i],
                "distance": distances[i],
            }
        )

    logger.info("Retrieved %d chunks for query: %s", len(chunks), query[:60])
    return chunks


def format_retrieved_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a readable string for the generator."""
    parts = []
    for i, c in enumerate(chunks, 1):
        chunk_id = c["metadata"].get("chunk_id", "?")
        doc_id = c["metadata"].get("document_id", "?")
        dist = c.get("distance", 0)
        parts.append(
            f"[片段 {i}] (chunk_id={chunk_id}, doc_id={doc_id}, 距离={dist:.4f})\n{c['document']}\n"
        )
    return "\n".join(parts)
