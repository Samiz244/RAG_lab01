#!/usr/bin/env python3
"""
Milestone 3 — Document Ingestion and Chunking
Ivy League Admissions RAG Pipeline

Format A: 60-dash-separated entries with === header dividers
          (academics, essays, extracurriculars, interviews, leadership, research, test_scores)
Format B: ---separated entries with TOPIC line in header
          (application_strategy, common_mistakes, personal_stories)

Both formats use multi-line section labels; URLs are on their own line in the Source block.
"""

import json
import random
import re
from collections import Counter
from pathlib import Path
from typing import Optional

DOCUMENTS_DIR = Path("documents")
OUTPUT_FILE   = Path("data/chunks.json")

MAX_WORDS     = 1200   # split an entry only if it exceeds this
OVERLAP_WORDS = 125    # mid-point of the 100-150-word overlap spec


# ── 1. LOAD ───────────────────────────────────────────────────────────────────

def load_documents(doc_dir: Path) -> list[dict]:
    docs = []
    for path in sorted(doc_dir.glob("*.txt")):
        topic = path.stem.replace("_", " ").title()
        docs.append({
            "filename": path.name,
            "topic":    topic,
            "raw_text": path.read_text(encoding="utf-8"),
        })
    return docs


# ── 2. CLEAN ──────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    for entity, char in {
        "&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"',
        "&#39;": "'", "&nbsp;": " ", "&mdash;": "—", "&ndash;": "–",
        "&hellip;": "…",
    }.items():
        text = text.replace(entity, char)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ── 3. FORMAT DETECTION & HEADER PARSING ─────────────────────────────────────

def detect_format(text: str) -> str:
    """'A' = 60-dash-separated entries with === header; 'B' = ---separated."""
    return "A" if re.search(r"^-{50,}", text, re.MULTILINE) else "B"


def _parse_format_a_header(text: str) -> tuple[str, str]:
    """Return (topic, description) from the full Format A document text."""
    topic_m = re.search(r"^Topic:\s*(.+)$", text, re.MULTILINE | re.IGNORECASE)
    topic   = topic_m.group(1).strip() if topic_m else ""

    dividers = list(re.finditer(r"={10,}", text))
    if len(dividers) >= 2:
        description = text[dividers[0].end():dividers[1].start()].strip()
    elif len(dividers) == 1:
        description = text[dividers[0].end():].strip()
    else:
        description = ""

    return topic, description


def _strip_format_a_header(text: str) -> str:
    """Remove everything up to and including the second ===== divider."""
    dividers = [m.end() for m in re.finditer(r"={10,}", text)]
    if len(dividers) >= 2:
        return text[dividers[1]:].strip()
    if len(dividers) == 1:
        return text[dividers[0]:].strip()
    return text


def _parse_format_b_header(header: str) -> tuple[str, str]:
    """Return (topic, description) from the first ---split part of a Format B document."""
    topic_m     = re.search(r"^TOPIC:\s*(.+)$", header, re.MULTILINE | re.IGNORECASE)
    topic       = topic_m.group(1).strip() if topic_m else ""
    description = header[topic_m.end():].strip() if topic_m else header.strip()
    return topic, description


def _strip_document_footer(text: str) -> str:
    """Remove end-of-file SUMMARY and Sources Used sections."""
    text = re.sub(r"\n={10,}\n+SUMMARY OF RECURRING THEMES\b.*", "", text, flags=re.DOTALL)
    text = re.sub(r"\nSUMMARY OF RECURRING THEMES\b.*",           "", text, flags=re.DOTALL)
    text = re.sub(r"\nSources Used:.*",                           "", text, flags=re.DOTALL)
    return text.strip()


# ── 4. ENTRY SPLITTING ────────────────────────────────────────────────────────

def parse_document(raw_text: str, filename_topic: str) -> tuple[str, str, list[str]]:
    """
    Returns (topic, description, raw_entries).
    Handles Format A (60-dash separators) and Format B (--- separators).
    Intro text before the first entry is never turned into a chunk.
    """
    cleaned = clean_text(raw_text)
    cleaned = _strip_document_footer(cleaned)
    fmt     = detect_format(cleaned)

    if fmt == "A":
        topic, description = _parse_format_a_header(cleaned)
        body  = _strip_format_a_header(cleaned)
        parts = re.split(r"\n-{50,}\n?", body)
    else:
        parts  = re.split(r"\n---\n?", cleaned)
        topic, description = _parse_format_b_header(parts[0] if parts else "")
        parts  = parts[1:]

    entries = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        # Must contain a Source: or Story: label to be a real entry
        if re.search(r"^(Source|Story):", part, re.MULTILINE):
            entries.append(part)

    return topic or filename_topic, description, entries


# ── 5. SECTION EXTRACTION ─────────────────────────────────────────────────────

_SECTION_LABELS = ["Source", "School", "Advice", "Key Takeaway", "Story"]
_LABEL_PATTERN  = "|".join(re.escape(l) for l in _SECTION_LABELS)


def _extract_section(raw: str, label: str) -> str:
    pattern = rf"^{re.escape(label)}:\s*\n?(.*?)(?=\n(?:{_LABEL_PATTERN}):|\Z)"
    m = re.search(pattern, raw, re.DOTALL | re.MULTILINE)
    return m.group(1).strip() if m else ""


def _parse_source_block(source_text: str) -> tuple[str, Optional[str]]:
    """Split source block into (source_name_without_url, source_url)."""
    url        = None
    name_lines = []
    for line in source_text.strip().splitlines():
        line = line.strip()
        if re.match(r"https?://", line):
            if url is None:
                url = line.rstrip(".,)>")
        elif line:
            name_lines.append(line)
    return "\n".join(name_lines), url


def parse_entry(raw: str, fallback_num: int) -> dict:
    m         = re.match(r"^Entry (\d+)", raw)
    entry_num = int(m.group(1)) if m else fallback_num

    source_text  = _extract_section(raw, "Source")
    school       = _extract_section(raw, "School")
    advice       = _extract_section(raw, "Advice")
    story        = _extract_section(raw, "Story")
    key_takeaway = _extract_section(raw, "Key Takeaway")

    if story and not advice:
        content_type, content = "Story", story
    else:
        content_type, content = "Advice", advice

    source_name, source_url = _parse_source_block(source_text)

    return {
        "entry_number": entry_num,
        "source_name":  source_name,
        "source_url":   source_url,
        "school":       school,
        "content_type": content_type,
        "content":      content,
        "key_takeaway": key_takeaway,
    }


# ── 6. CHUNK CONSTRUCTION ─────────────────────────────────────────────────────

def _word_count(text: str) -> int:
    return len(text.split())


def _split_with_overlap(text: str, max_words: int, overlap: int) -> list[str]:
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        end = min(start + max_words, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = end - overlap
    return chunks


def _build_chunk_text(entry: dict) -> str:
    parts = []
    src = entry["source_name"]
    if entry["source_url"]:
        src += "\n" + entry["source_url"]
    if src.strip():
        parts.append(f"Source:\n{src}")
    if entry["school"]:
        parts.append(f"School:\n{entry['school']}")
    label = entry.get("content_type", "Advice")
    if entry["content"]:
        parts.append(f"{label}:\n{entry['content']}")
    if entry["key_takeaway"]:
        parts.append(f"Key Takeaway:\n{entry['key_takeaway']}")
    return "\n\n".join(parts)


def chunk_entry(
    entry: dict,
    filename: str,
    topic: str,
    document_description: str,
    counter: list,
) -> list[dict]:
    text = _build_chunk_text(entry)
    if not text.strip():
        return []

    base_meta = {
        "filename":             filename,
        "topic":                topic,
        "document_description": document_description,
        "entry_number":         entry["entry_number"],
        "school":               entry["school"],
        "source_url":           entry["source_url"],
        "source_name":          entry["source_name"],
        "content_type":         entry["content_type"],
    }

    wc = _word_count(text)

    if wc <= MAX_WORDS:
        counter[0] += 1
        return [{
            **base_meta,
            "chunk_id":   f"chunk_{counter[0]:04d}",
            "split_part": None,
            "word_count": wc,
            "text":       text,
        }]

    # Entry exceeds max — split with overlap
    sub_texts = _split_with_overlap(text, MAX_WORDS, OVERLAP_WORDS)
    chunks = []
    for i, sub in enumerate(sub_texts, start=1):
        counter[0] += 1
        chunks.append({
            **base_meta,
            "chunk_id":   f"chunk_{counter[0]:04d}",
            "split_part": i,
            "word_count": _word_count(sub),
            "text":       sub,
        })
    return chunks


# ── 7. PIPELINE ───────────────────────────────────────────────────────────────

def build_chunks(docs: list[dict]) -> list[dict]:
    all_chunks = []
    counter    = [0]

    for doc in docs:
        topic, description, raw_entries = parse_document(
            doc["raw_text"], doc["topic"]
        )
        for i, raw_entry in enumerate(raw_entries, start=1):
            entry  = parse_entry(raw_entry, fallback_num=i)
            chunks = chunk_entry(
                entry, doc["filename"], topic, description, counter
            )
            all_chunks.extend(chunks)

    return [c for c in all_chunks if c["text"].strip()]


# ── 8. INSPECTION REPORT ──────────────────────────────────────────────────────

def print_report(docs: list[dict], chunks: list[dict]) -> None:
    bar = "=" * 62
    print(f"\n{bar}")
    print("  MILESTONE 3 — INGESTION & CHUNKING REPORT")
    print(bar)
    print(f"  Documents loaded : {len(docs)}")
    print(f"  Total chunks     : {len(chunks)}")

    counts = Counter(c["filename"] for c in chunks)
    print(f"\n  Chunks per source file:")
    for fn in sorted(counts):
        print(f"    {fn:<38} {counts[fn]:>3} chunk(s)")

    split_chunks = [c for c in chunks if c["split_part"] is not None]
    if split_chunks:
        print(f"\n  Entries split due to length: {len(split_chunks)} sub-chunks "
              f"(from oversized entries)")
    else:
        print(f"\n  No entries exceeded the {MAX_WORDS}-word limit — no splits needed.")

    wcs = [c["word_count"] for c in chunks]
    print(f"\n  Word-count stats across all chunks:")
    print(f"    min={min(wcs)}  max={max(wcs)}  avg={sum(wcs)//len(wcs)}")

    # Source URL completeness
    missing_url = [c for c in chunks if c["source_url"] is None]
    if missing_url:
        missing_by_file = Counter(c["filename"] for c in missing_url)
        print(f"\n  WARNING — {len(missing_url)} chunk(s) have no source URL:")
        for fn in sorted(missing_by_file):
            print(f"    {fn:<38} {missing_by_file[fn]:>3} chunk(s)")
    else:
        print(f"\n  Source URLs: all {len(chunks)} chunks have a URL.")

    # Intro / footer leak check
    LEAK_PATTERNS = [
        "SUMMARY OF RECURRING THEMES",
        "Sources Used:",
        "TOPIC:",
    ]
    leaked = [c for c in chunks if any(p in c["text"] for p in LEAK_PATTERNS)]
    if leaked:
        print(f"\n  ERROR — {len(leaked)} chunk(s) contain header/footer leakage:")
        for c in leaked:
            print(f"    {c['chunk_id']}  {c['filename']}")
    else:
        print(f"  Intro/footer leak check: 0 chunks contain leakage.")

    print(f"\n{bar}")
    print("  5 REPRESENTATIVE CHUNKS (random sample)")
    print(bar)
    sample = random.sample(chunks, min(5, len(chunks)))
    for i, c in enumerate(sample, start=1):
        print(f"\n  ── Sample {i} ──────────────────────────────────────────")
        print(f"  chunk_id     : {c['chunk_id']}")
        print(f"  filename     : {c['filename']}")
        print(f"  topic        : {c['topic']}")
        print(f"  entry_number : {c['entry_number']}")
        print(f"  school       : {c['school']}")
        print(f"  source_url   : {c['source_url'] or '(none)'}")
        print(f"  content_type : {c['content_type']}")
        print(f"  split_part   : {c['split_part']}")
        print(f"  word_count   : {c['word_count']}")
        preview = c["text"][:400].replace("\n", " ")
        print(f"\n  TEXT PREVIEW:\n  {preview!r}")
    print()


# ── 9. MAIN ───────────────────────────────────────────────────────────────────

def main() -> None:
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    print("Loading documents...")
    docs = load_documents(DOCUMENTS_DIR)
    if not docs:
        raise SystemExit(f"No .txt files found in {DOCUMENTS_DIR}/")

    print("Cleaning and chunking...")
    chunks = build_chunks(docs)

    print_report(docs, chunks)

    with OUTPUT_FILE.open("w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(chunks)} chunks → {OUTPUT_FILE}\n")


if __name__ == "__main__":
    main()
