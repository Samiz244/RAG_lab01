#!/usr/bin/env python3
"""
Milestone 5 — Gradio Interface
Ivy League Admissions RAG Pipeline

A minimal terminal-launched web UI over query.ask():
  - question textbox
  - Ask button
  - answer textbox
  - retrieved sources textbox

Run:
    python3 app.py
Then open the local URL Gradio prints (default http://127.0.0.1:7860).
"""

import gradio as gr

from query import ask


def _format_sources_text(sources: list[dict]) -> str:
    """Turn the structured source list into readable text for the UI box."""
    lines = []
    for i, s in enumerate(sources, start=1):
        url = s["source_url"] or "(no url)"
        lines.append(
            f"[{i}] {s['source_name']}\n"
            f"     school : {s['school']}\n"
            f"     file   : {s['filename']}  ·  topic: {s['topic']}\n"
            f"     url    : {url}"
        )
    return "\n\n".join(lines)


def answer_question(question: str):
    """Gradio callback: returns (answer_text, sources_text)."""
    if not question or not question.strip():
        return "Please enter a question.", ""
    result = ask(question.strip())
    return result["answer"], _format_sources_text(result["sources"])


with gr.Blocks(title="Ivy League Admissions RAG") as demo:
    gr.Markdown(
        "# 🎓 Ivy League Admissions Assistant\n"
        "Ask a question about Ivy League admissions. Answers are grounded **only** "
        "in the retrieved source documents. If the documents don't cover your "
        "question, the assistant will say so."
    )

    question_box = gr.Textbox(
        label="Your question",
        placeholder="e.g. What is the ideal number of deep extracurricular commitments?",
        lines=2,
    )
    ask_btn = gr.Button("Ask", variant="primary")

    answer_box = gr.Textbox(label="Answer", lines=6, interactive=False)
    sources_box = gr.Textbox(label="Retrieved sources", lines=12, interactive=False)

    ask_btn.click(
        fn=answer_question,
        inputs=question_box,
        outputs=[answer_box, sources_box],
    )
    question_box.submit(
        fn=answer_question,
        inputs=question_box,
        outputs=[answer_box, sources_box],
    )


if __name__ == "__main__":
    demo.launch()
