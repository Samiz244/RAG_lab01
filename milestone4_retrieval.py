#!/usr/bin/env python3
"""
Milestone 4 — Embedding and Retrieval
Ivy League Admissions RAG Pipeline

Pipeline stage:  data/chunks.json
                   → all-MiniLM-L6-v2 embeddings
                   → ChromaDB vector store (persistent, cosine similarity)
                   → top-k semantic retrieval

This milestone stops at retrieval. There is NO generation / LLM here.

Usage:
    python3 milestone4_retrieval.py          # build store, then interactive Q&A loop
    python3 milestone4_retrieval.py --test   # build store, then run Evaluation-Plan questions
"""

import json
import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

# ── Configuration (from planning.md → Retrieval Approach) ─────────────────────
CHUNKS_FILE     = Path("data/chunks.json")
CHROMA_DIR      = Path("data/chroma_db")
COLLECTION_NAME = "ivy_admissions"
EMBED_MODEL     = "all-MiniLM-L6-v2"   # sentence-transformers, 384-dim
TOP_K           = 5

# Metadata fields to store alongside each chunk (per requirements).
META_FIELDS = [
    "chunk_id", "filename", "topic", "entry_number",
    "source_name", "source_url", "school", "content_type", "word_count",
]

# Test questions taken directly from planning.md → Evaluation Plan.
TEST_QUESTIONS = [
    'What three academic metrics make up the "Academic Index" that Harvard uses '
    'as an initial screening filter?',
    "Which two Ivy League schools currently maintain explicitly evaluative "
    "interviews where the written report is reviewed alongside the application file?",
    "According to the analysis of over 1,100 admitted student profiles, what is the "
    "ideal number of deep, sustained extracurricular commitments an applicant should have?",
    "According to Cornell's Common Data Set for 2024-2025, what is considered the "
    "single highest-weighted academic factor in their admissions decisions?",
    "Which program allows eligible low-income students to apply early to multiple "
    "Ivy League schools simultaneously, bypassing single-school Early Decision?",
]


# ── 1. LOAD CHUNKS ────────────────────────────────────────────────────────────

def load_chunks(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"Loaded {len(chunks)} chunks from {path}")
    return chunks


# ── 2. BUILD / REBUILD THE VECTOR STORE ───────────────────────────────────────

def build_collection(chunks: list[dict], model: SentenceTransformer):
    """
    Create a fresh ChromaDB collection from the chunks and return it.

    The collection is recreated every run so re-running the script never inserts
    duplicate chunks (requirement #9).
    """
    # PersistentClient writes the database to disk so it survives between runs.
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Drop any previous collection of the same name, then recreate it empty.
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass  # nothing to delete on the first run

    # metadata={"hnsw:space": "cosine"} tells Chroma to use cosine distance for
    # its similarity index (matches the planning.md architecture diagram).
    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    texts = [c["text"] for c in chunks]
    ids   = [c["chunk_id"] for c in chunks]

    print(f"Embedding {len(texts)} chunks with '{EMBED_MODEL}'...")
    embeddings = model.encode(texts, show_progress_bar=True).tolist()

    # Keep only the metadata fields we care about (Chroma needs flat, non-null values).
    metadatas = []
    for c in chunks:
        meta = {}
        for field in META_FIELDS:
            value = c.get(field)
            meta[field] = "" if value is None else value
        metadatas.append(meta)

    # add() stores the documents, their vectors, ids, and metadata in one call.
    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    print(f"Stored {collection.count()} chunks in ChromaDB at {CHROMA_DIR}/\n")
    return collection


# ── 3. RETRIEVAL ──────────────────────────────────────────────────────────────

def retrieve(query: str, collection, model: SentenceTransformer, k: int = TOP_K) -> list[dict]:
    """
    Embed the query and return the top-k most similar chunks.

    Each result is a dict with the stored metadata, the chunk text, and the
    cosine distance score (smaller distance = more similar).
    """
    query_embedding = model.encode([query]).tolist()

    # query() runs the nearest-neighbour search and returns documents, metadata,
    # and distances for the closest k chunks.
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
    )

    hits = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        hit = dict(meta)
        hit["text"] = doc
        hit["distance"] = dist
        hits.append(hit)
    return hits


# ── 4. DISPLAY ────────────────────────────────────────────────────────────────

def print_results(query: str, hits: list[dict]) -> None:
    print("=" * 78)
    print(f"QUERY: {query}")
    print("=" * 78)
    for rank, hit in enumerate(hits, start=1):
        preview = hit["text"].replace("\n", " ")
        if len(preview) > 320:
            preview = preview[:320] + "..."
        print(f"\n[Rank {rank}]  distance={hit['distance']:.4f}")
        print(f"  chunk_id    : {hit.get('chunk_id', '')}")
        print(f"  filename    : {hit.get('filename', '')}")
        print(f"  topic       : {hit.get('topic', '')}")
        print(f"  school      : {hit.get('school', '')}")
        print(f"  source_name : {hit.get('source_name', '')}")
        print(f"  source_url  : {hit.get('source_url') or '(none)'}")
        print(f"  preview     : {preview}")
    print()


# ── 5. MODES ──────────────────────────────────────────────────────────────────

def run_test_mode(collection, model: SentenceTransformer) -> None:
    print("\n" + "#" * 78)
    print("# TEST MODE — Evaluation-Plan questions from planning.md")
    print("#" * 78 + "\n")
    for query in TEST_QUESTIONS:
        hits = retrieve(query, collection, model, k=TOP_K)
        print_results(query, hits)


def run_interactive(collection, model: SentenceTransformer) -> None:
    print("Vector store ready. Ask questions about Ivy League admissions.\n")
    while True:
        try:
            query = input("Ask a question (or type 'exit'): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not query:
            continue
        if query.lower() in {"exit", "quit"}:
            break
        hits = retrieve(query, collection, model, k=TOP_K)
        print_results(query, hits)


# ── 6. MAIN ───────────────────────────────────────────────────────────────────

def main() -> None:
    if not CHUNKS_FILE.exists():
        raise SystemExit(f"Missing {CHUNKS_FILE}. Run milestone3_ingest.py first.")

    chunks = load_chunks(CHUNKS_FILE)

    print(f"Loading embedding model '{EMBED_MODEL}'...")
    model = SentenceTransformer(EMBED_MODEL)

    collection = build_collection(chunks, model)

    if "--test" in sys.argv:
        run_test_mode(collection, model)
    else:
        run_interactive(collection, model)


if __name__ == "__main__":
    main()
