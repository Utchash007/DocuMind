"""Grounded answer generation from authorized PDF evidence.

:func:`generate_answer` implements the frozen ``AnswerGenerator``
contract (:mod:`app.schemas.services`)::

    generate_answer(*, question, history, authorized_sources) -> GeneratedAnswer

It performs scoped retrieval, asks Groq through Instructor for a
structured answer, and refines the model citations against the
retrieved chunks.  It **never** writes conversation rows (persistence
is owned by the message repository) and never treats earlier assistant
output as source evidence: history is passed as context, retrieved PDF
text is passed as evidence, and the current question is assembled
exactly once.

Model settings: ``openai/gpt-oss-120b``, temperature 0, structured
``ModelAnswer``.  The call uses Instructor's JSON mode rather than
forced tool calling: Groq validates tool-call arguments server-side
against the schema and rejects mismatches with ``400 tool_use_failed``
before Instructor can repair them (e.g. a model writing ``text``/
``source`` instead of ``sentence``/``filename``, or replying with plain
prose under a required ``tool_choice``).  JSON mode moves validation
into Pydantic, where Instructor's retries can actually repair output.
"""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Any

from pydantic import Field

from app.rag.citations import ModelCitationLike, refine_citations
from app.rag.retrieval import RetrievedChunk, retrieve_context
from app.schemas.common import CamelModel
from app.schemas.services import AuthorizedSource, GeneratedAnswer, HistoryTurn

MODEL_NAME = "openai/gpt-oss-120b"
TEMPERATURE = 0.0


class ModelAnswer(CamelModel):
    """Structured LLM output (answer + untrusted citation hints)."""

    answer: str = Field(description="The comprehensive answer grounded in the provided context.")
    citations: list[ModelCitationLike] = Field(
        description="Exact supporting sentences with page numbers and source filenames."
    )


class GenerationError(Exception):
    """Provider/answer-generation failure (mapped to ``503``)."""


def build_llm_messages(
    *,
    question: str,
    history: Sequence[HistoryTurn],
    context_chunks: Sequence[RetrievedChunk],
) -> list[dict[str, str]]:
    """Assemble system + user messages for the structured LLM call.

    History (prior questions and answers) is explicitly labeled as
    context only; the retrieved chunks are the only evidence.  The
    current question is included exactly once, at the end.
    """
    if not question.strip():
        raise ValueError("question must not be blank")
    history_lines = [
        f"[{turn.role}] {turn.content}" for turn in history if turn.content.strip()
    ]
    history_block = (
        "Conversation history (context only - not source evidence):\n"
        + "\n".join(history_lines)
        + "\n\n"
        if history_lines
        else ""
    )
    evidence_lines = [
        (
            f"[Document Chunk {rank + 1} | Source: {chunk.source} "
            f"| Page {chunk.page_number}]: {chunk.text}"
        )
        for rank, chunk in enumerate(context_chunks)
    ]
    evidence_block = "\n\n".join(evidence_lines) if evidence_lines else "(no source evidence retrieved)"
    user_content = (
        f"{history_block}"
        f"Source evidence from authorized documents:\n{evidence_block}\n\n"
        f"Question: {question}"
    )
    return [
        {
            "role": "system",
            "content": (
                "You are a meticulous, document-answering assistant. "
                "Answer the user's question using ONLY the provided source "
                "evidence as evidence. Conversation history, when present, "
                "is context for what was discussed and is never itself "
                "evidence. For every statement or fact you write, extract "
                "the exact supporting sentence from the source evidence "
                "(not from history) and specify its page number and exact "
                "source filename. Do not make up facts or use external "
                "knowledge.\n\n"
                "Reply with one JSON object and no other text, using exactly "
                'these keys: {"answer": string, "citations": [{"sentence": '
                'string, "page": integer, "filename": string}]}. Copy '
                "`sentence` verbatim from a single source-evidence chunk; "
                "`page` is that chunk's page number; `filename` is that "
                "chunk's Source value exactly as written. If the evidence "
                "does not answer the question, say so briefly in `answer` "
                "and return an empty `citations` list. Never invent "
                "sentences, pages, or filenames."
            ),
        },
        {"role": "user", "content": user_content},
    ]


def default_groq_client():
    """Build the Groq client from the environment per request."""
    from groq import Groq

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise GenerationError("GROQ_API_KEY environment variable is missing.")
    return Groq(api_key=api_key)


def generate_answer(
    *,
    question: str,
    history: Sequence[HistoryTurn],
    authorized_sources: Sequence[AuthorizedSource],
    user_id: Any | None = None,
    project_id: Any | None = None,
    collection: Any | None = None,
    embedder: Any | None = None,
    groq_client: Any | None = None,
) -> GeneratedAnswer:
    """Generate a grounded answer with refined citations (no row writes).

    ``history`` is bounded recent completed context (already excluding
    the current question, which is added once by the prompt builder).
    ``authorized_sources`` are the exact permitted
    ``(document, index_version)`` pairs; retrieval never runs unscoped.
    """
    import instructor

    chunks = retrieve_context(
        question=question,
        user_id=user_id,
        project_id=project_id,
        authorized_sources=authorized_sources,
        collection=collection,
        embedder=embedder,
    )
    messages = build_llm_messages(
        question=question, history=history, context_chunks=chunks
    )
    llm = groq_client or default_groq_client()
    try:
        structured = (
            instructor.from_groq(llm, mode=instructor.Mode.JSON)
            .chat.completions.create(
                model=MODEL_NAME,
                response_model=ModelAnswer,
                messages=messages,
                temperature=TEMPERATURE,
                max_retries=2,
            )
        )
    except GenerationError:
        raise
    except Exception as exc:  # provider outage surfaces as retryable service error
        raise GenerationError(f"Answer generation failed: {exc}") from exc
    citations = refine_citations(
        retrieved_chunks=chunks,
        model_citations=[
            ModelCitationLike(
                sentence=citation.sentence,
                page=citation.page,
                filename=citation.filename,
            )
            for citation in structured.citations
        ],
    )
    return GeneratedAnswer(answer=structured.answer, citations=citations)


__all__ = [
    "MODEL_NAME",
    "TEMPERATURE",
    "GenerationError",
    "ModelAnswer",
    "build_llm_messages",
    "default_groq_client",
    "generate_answer",
]
