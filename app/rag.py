"""
rag.py — RAG pipeline for DocuMind.

Responsibilities:
  - Parse PDF / DOCX / TXT files into text + page metadata
  - Chunk text (~2000 chars with 200-char overlap)
  - Embed chunks with SentenceTransformers (all-MiniLM-L6-v2)
  - Store / retrieve chunks via ChromaDB (persistent on disk)
"""

from __future__ import annotations

import os
import re
import hashlib
import unicodedata
from pathlib import Path
from typing import Optional

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_THIS_DIR = Path(__file__).parent
STORAGE_DIR = _THIS_DIR / "storage" / "chroma_db"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Module-level singletons (loaded once, reused across all calls)
# ---------------------------------------------------------------------------
_embedding_model: Optional[SentenceTransformer] = None
_chroma_client: Optional[chromadb.PersistentClient] = None
_collection = None  # chromadb.Collection


def _get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model


def _get_collection():
    global _chroma_client, _collection
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=str(STORAGE_DIR),
            settings=Settings(anonymized_telemetry=False),
        )
    if _collection is None:
        _collection = _chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


# ---------------------------------------------------------------------------
# Text parsing helpers
# ---------------------------------------------------------------------------

def _parse_pdf(file_bytes: bytes) -> list[tuple[int, str]]:
    """Return list of (page_number, text) tuples. Page numbers are 1-indexed."""
    import fitz  # PyMuPDF

    pages: list[tuple[int, str]] = []
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            text = page.get_text("text")
            text = _clean_text(text)
            if text.strip():
                pages.append((page_idx + 1, text))
    return pages


def _parse_docx(file_bytes: bytes) -> list[tuple[int, str]]:
    """
    Return list of (page_number, text) tuples.
    DOCX has no hard page concept; we group every 30 paragraphs as a pseudo-page.
    """
    import io
    from docx import Document

    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]

    GROUP_SIZE = 30
    pages: list[tuple[int, str]] = []
    for i in range(0, max(len(paragraphs), 1), GROUP_SIZE):
        group = paragraphs[i : i + GROUP_SIZE]
        text = "\n".join(group)
        text = _clean_text(text)
        if text.strip():
            pages.append((i // GROUP_SIZE + 1, text))

    if not pages:
        pages = [(1, "")]

    return pages


def _parse_txt(file_bytes: bytes) -> list[tuple[int, str]]:
    """Return a single (1, text) tuple for plain-text files."""
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = file_bytes.decode("latin-1", errors="replace")
    text = _clean_text(text)
    return [(1, text)]


def _clean_text(text: str) -> str:
    """Normalize unicode, remove null bytes, collapse excessive whitespace."""
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\x00", "")
    # Collapse runs of blank lines to a maximum of two
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

CHUNK_SIZE = 2000      # characters
CHUNK_OVERLAP = 200    # characters


def _chunk_text(text: str, page: int, source: str) -> list[dict]:
    """
    Split text into overlapping chunks and return list of chunk dicts:
    {id, text, source, page}
    """
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + CHUNK_SIZE, text_len)

        # Try to break at the last sentence boundary within the window
        if end < text_len:
            boundary = _find_sentence_boundary(text, end)
            if boundary > start:
                end = boundary

        chunk_text = text[start:end].strip()
        if chunk_text:
            chunk_id = _make_chunk_id(source, page, start)
            chunks.append(
                {
                    "id": chunk_id,
                    "text": chunk_text,
                    "source": source,
                    "page": page,
                }
            )

        # Move forward, respecting overlap
        next_start = end - CHUNK_OVERLAP
        if next_start <= start:
            next_start = start + 1  # safety: always advance
        start = next_start

    return chunks


def _find_sentence_boundary(text: str, pos: int) -> int:
    """Walk backwards from pos to find a sentence-ending punctuation + space."""
    search_window = text[max(0, pos - 200) : pos]
    # Look for '. ', '! ', '? ' from the right
    for patt in (". ", "! ", "? ", "\n\n", "\n"):
        idx = search_window.rfind(patt)
        if idx != -1:
            return max(0, pos - 200) + idx + len(patt)
    return pos


def _make_chunk_id(source: str, page: int, offset: int) -> str:
    raw = f"{source}::p{page}::o{offset}"
    return hashlib.md5(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# DocumentStore
# ---------------------------------------------------------------------------

class DocumentStore:
    """High-level interface for document ingestion and retrieval."""

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def add_document(self, file_bytes: bytes, filename: str, file_type: str) -> int:
        """
        Parse, chunk, embed, and store a document.

        Args:
            file_bytes: Raw file content.
            filename:   Original filename (used as the source identifier).
            file_type:  One of 'pdf', 'docx', 'txt'.

        Returns:
            Number of chunks indexed.
        """
        # 1. Parse into pages
        file_type = file_type.lower().lstrip(".")
        if file_type == "pdf":
            pages = _parse_pdf(file_bytes)
        elif file_type in ("docx", "doc"):
            pages = _parse_docx(file_bytes)
        else:
            pages = _parse_txt(file_bytes)

        # 2. Chunk each page
        all_chunks: list[dict] = []
        for page_num, page_text in pages:
            if not page_text.strip():
                continue
            all_chunks.extend(_chunk_text(page_text, page_num, filename))

        if not all_chunks:
            return 0

        # 3. Embed
        model = _get_embedding_model()
        texts = [c["text"] for c in all_chunks]
        embeddings = model.encode(texts, show_progress_bar=False).tolist()

        # 4. Store in ChromaDB (upsert to handle re-uploads)
        collection = _get_collection()
        collection.upsert(
            ids=[c["id"] for c in all_chunks],
            embeddings=embeddings,
            documents=texts,
            metadatas=[{"source": c["source"], "page": c["page"]} for c in all_chunks],
        )

        return len(all_chunks)

    # ------------------------------------------------------------------
    # Listing & deletion
    # ------------------------------------------------------------------

    def list_documents(self) -> list[str]:
        """Return sorted list of unique document names currently indexed."""
        collection = _get_collection()
        # Fetch all metadata (no embeddings needed)
        result = collection.get(include=["metadatas"])
        sources = {m["source"] for m in result["metadatas"]} if result["metadatas"] else set()
        return sorted(sources)

    def delete_document(self, doc_name: str) -> int:
        """
        Remove all chunks belonging to doc_name from ChromaDB.

        Returns:
            Number of chunks deleted.
        """
        collection = _get_collection()
        result = collection.get(
            where={"source": doc_name},
            include=["metadatas"],
        )
        ids_to_delete = result["ids"]
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
        return len(ids_to_delete)

    def document_chunk_count(self) -> dict[str, int]:
        """Return {doc_name: chunk_count} for all indexed documents."""
        collection = _get_collection()
        result = collection.get(include=["metadatas"])
        counts: dict[str, int] = {}
        for m in (result["metadatas"] or []):
            src = m["source"]
            counts[src] = counts.get(src, 0) + 1
        return counts

    def total_chunks(self) -> int:
        """Total number of chunks in the collection."""
        return _get_collection().count()

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def query(self, question: str, top_k: int = 4) -> list[dict]:
        """
        Embed the question and retrieve the top-k most relevant chunks.

        Returns:
            List of dicts: [{text, source, page, score}, ...]
        """
        collection = _get_collection()
        if collection.count() == 0:
            return []

        model = _get_embedding_model()
        q_embedding = model.encode([question], show_progress_bar=False).tolist()

        results = collection.query(
            query_embeddings=q_embedding,
            n_results=min(top_k, collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        dists = results.get("distances", [[]])[0]

        for text, meta, dist in zip(docs, metas, dists):
            # ChromaDB cosine distance: 0 = identical, 2 = opposite
            # Convert to a similarity score in [0, 1]
            similarity = max(0.0, 1.0 - dist / 2.0)
            chunks.append(
                {
                    "text": text,
                    "source": meta.get("source", "unknown"),
                    "page": meta.get("page", 0),
                    "score": round(similarity, 4),
                }
            )

        return chunks
