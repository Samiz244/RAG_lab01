#!/usr/bin/env python3
"""
Milestone 5 — Grounded Generation
Ivy League Admissions RAG Pipeline

Pipeline stage:  user question
                   → retrieve top-5 chunks (Milestone 4)
                   → build a context-only prompt
                   → Groq Llama 3.3 70B
                   → grounded answer + programmatic source list

The model is instructed to answer ONLY from the retrieved context. Source
citations are NOT trusted to the model — they are appended from the retrieved
chunk metadata after generation, so attribution is guaranteed.

Usage:
    python3 query.py          # run the built-in covered/uncovered test questions
    python3 query.py "..."     # ask a single question from the command line
"""

import os
import sys

from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

# Reuse Milestone 4 retrieval — do NOT redesign embedding/retrieval here.
from milestone4_retrieval import (
    EMBED_MODEL,
    TOP_K,
    load_or_build_collection,
    retrieve,
)

GROQ_MODEL    = "llama-3.3-70b-versatile"
FALLBACK_ANSWER = "I don't have enough information on that."

# Strong grounding instructions (planning.md → grounded generation).
SYSTEM_PROMPT = (
    "You are an Ivy League admissions assistant. You answer questions using ONLY "
    "the context provided to you below. Follow these rules strictly:\n"
    "1. Use ONLY the information in the provided context. Do not use any outside "
    "knowledge.\n"
    "2. Do not guess, infer beyond the text, or make up facts.\n"
    "3. If the context does not contain enough information to answer the question, "
    f'reply with EXACTLY this sentence and nothing else: "{FALLBACK_ANSWER}"\n'
    "4. Keep the answer concise and directly supported by the context."
)

# ── Load model + collection once at import (reused across calls) ──────────────
load_dotenv()
_model = SentenceTransformer(EMBED_MODEL)
_collection = load_or_build_collection(_model)
_groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a numbered context block for the prompt."""
    blocks = []
    for i, c in enumerate(chunks, start=1):
        header = f"[Source {i}] {c.get('source_name', '')} ({c.get('school', '')})"
        blocks.append(f"{header}\n{c.get('text', '')}")
    return "\n\n---\n\n".join(blocks)


def _format_sources(chunks: list[dict]) -> list[dict]:
    """Build the guaranteed source list from retrieved metadata."""
    sources = []
    for c in chunks:
        sources.append({
            "filename":    c.get("filename", ""),
            "topic":       c.get("topic", ""),
            "school":      c.get("school", ""),
            "source_name": c.get("source_name", ""),
            "source_url":  c.get("source_url") or "",
        })
    return sources


def ask(question: str, k: int = TOP_K) -> dict:
    """
    Answer a question using only the top-k retrieved chunks.

    Returns:
        {"answer": "...", "sources": [ {filename, topic, school,
                                        source_name, source_url}, ... ]}
    """
    chunks = retrieve(question, _collection, _model, k=k)
    context = _build_context(chunks)

    user_prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer using only the context above."
    )

    response = _groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.2,
        max_tokens=1024,
    )
    answer = response.choices[0].message.content.strip()

    # Source attribution is guaranteed from retrieved metadata, not the LLM.
    return {"answer": answer, "sources": _format_sources(chunks)}


def _print_result(question: str, result: dict) -> None:
    print("=" * 78)
    print(f"Q: {question}")
    print("-" * 78)
    print(f"A: {result['answer']}")
    print("\nSources:")
    for i, s in enumerate(result["sources"], start=1):
        url = s["source_url"] or "(no url)"
        print(f"  [{i}] {s['source_name']}  |  {s['school']}")
        print(f"      {s['filename']} · {s['topic']} · {url}")
    print()


# ── CLI / test block ──────────────────────────────────────────────────────────

# 1–2 covered questions (from Evaluation Plan), 3rd uncovered to test grounding.
TEST_QUESTIONS = [
    "What three academic metrics make up Harvard's Academic Index?",        # covered
    "Which Ivy League program lets low-income students apply early to "
    "multiple schools at once?",                                            # covered
    "What dorm has the best food at Harvard?",                              # uncovered
]


def main() -> None:
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        _print_result(question, ask(question))
        return

    print("\nRunning Milestone 5 grounding tests "
          "(2 covered questions, 1 uncovered)...\n")
    for q in TEST_QUESTIONS:
        _print_result(q, ask(q))


if __name__ == "__main__":
    main()
