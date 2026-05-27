"""Embedding module — local SentenceTransformer + ChromaDB storage.

Uses BAAI/bge-small-zh-v1.5, a Chinese-optimized embedding model that runs
fully offline — no external API calls needed for embeddings.
"""

import logging
import chromadb
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# Module-level singleton, lazy-loaded
_model: SentenceTransformer | None = None


def _get_model(model_name: str) -> SentenceTransformer:
    """Get or create the SentenceTransformer singleton."""
    global _model
    if _model is None:
        logger.info("Loading embedding model: %s ...", model_name)
        _model = SentenceTransformer(model_name)
        logger.info("Embedding model loaded (dim=%d)", _model.get_sentence_embedding_dimension())
    return _model


def encode_text(model: SentenceTransformer, text: str) -> list[float]:
    """Encode a single text to a vector."""
    return model.encode(text, normalize_embeddings=True).tolist()


def encode_batch(
    model: SentenceTransformer,
    texts: list[str],
    batch_size: int = 32,
) -> list[list[float]]:
    """Encode a batch of texts to vectors."""
    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        batch_size=batch_size,
        show_progress_bar=True,
    )
    return embeddings.tolist()


def build_chroma_collection(
    persist_dir: str,
    collection_name: str,
) -> chromadb.Collection:
    """Create or recreate a ChromaDB collection (fresh start for demo)."""
    chroma_client = chromadb.PersistentClient(path=persist_dir)
    try:
        chroma_client.delete_collection(collection_name)
    except Exception:
        pass
    return chroma_client.create_collection(name=collection_name)


def embed_and_store_chunks(
    model: SentenceTransformer,
    collection: chromadb.Collection,
    chunks: list,
) -> None:
    """Embed all chunks and store in ChromaDB."""
    texts = [c.content for c in chunks]
    ids = [f"chunk_{c.chunk_id}" for c in chunks]
    metadatas = [
        {
            "document_id": str(c.document_id),
            "chunk_index": c.chunk_index,
            "chunk_id": str(c.chunk_id),
        }
        for c in chunks
    ]

    logger.info("Generating embeddings for %d chunks ...", len(texts))
    embeddings = encode_batch(model, texts)

    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    logger.info("Stored %d embeddings in ChromaDB", len(embeddings))
