"""
Answer engine.
Assembles search passages into a Claude prompt and generates a grounded answer.
"""
import logging
from dataclasses import dataclass

import anthropic
from api.search_engine import search_and_fetch, SearchPassage
from config import (ANTHROPIC_API_KEY, LLM_MODEL, LLM_MAX_TOKENS,
                    MAX_CONVERSATION_TURNS)

log = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a helpful admissions assistant for Grand Valley State
University (GVSU). You answer questions using ONLY the web page content provided
below each question. These pages were fetched live from gvsu.edu.

Rules:
- Base every answer strictly on the provided page content. Do not invent facts.
- Be concise, friendly, and well-organized. Use bullet points for lists.
- If the provided content does not contain enough information to answer, say:
  "I couldn't find a clear answer on gvsu.edu for that. Please contact GVSU
  Admissions directly at admissions@gvsu.edu or call 616-331-2025."
- Do NOT include a Sources section — sources are shown separately in the UI.
- Do NOT use emojis in your responses.
"""


@dataclass
class AnswerResponse:
    answer: str
    sources: list[dict]   # [{title, url}]
    pages_fetched: int
    fallback: bool


def build_context_block(passages: list[SearchPassage]) -> str:
    """Format fetched passages into a numbered context block for the prompt."""
    parts = []
    for i, p in enumerate(passages, 1):
        parts.append(
            f"[Page {i}]\n"
            f"Title: {p.title}\n"
            f"URL: {p.url}\n"
            f"Content:\n{p.text}"
        )
    return "\n\n---\n\n".join(parts)


def generate_answer(
    query: str,
    passages: list[SearchPassage],
    history: list[dict],
    topic: str | None = None,
) -> str:
    """Call Claude with the assembled context and conversation history."""
    context = build_context_block(passages)

    messages = []

    for turn in history[-MAX_CONVERSATION_TURNS:]:
        messages.append({"role": turn["role"], "content": turn["content"]})

    topic_note = f"The user has indicated they are interested in the **{topic}** category. Tailor your answer accordingly.\n\n" if topic else ""

    messages.append({
        "role": "user",
        "content": (
            f"{topic_note}"
            f"Here are the relevant GVSU web pages I found for your question:\n\n"
            f"{context}\n\n"
            f"Question: {query}"
        )
    })

    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=LLM_MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text


def answer(query: str, history: list[dict], topic: str | None = None) -> AnswerResponse:
    """
    Full pipeline: search gvsu.edu → fetch pages → generate answer.
    Topic (if set) is prepended to the search query and passed to Claude.
    """
    search_query = f"{topic} {query}" if topic else query
    passages = search_and_fetch(search_query)

    if not passages:
        return AnswerResponse(
            answer=(
                "I couldn't find any relevant results on gvsu.edu for that question. "
                "Please contact GVSU Admissions directly at admissions@gvsu.edu "
                "or call 616-331-2025."
            ),
            sources=[],
            pages_fetched=0,
            fallback=True,
        )

    answer_text = generate_answer(query, passages, history, topic)

    sources = [
        {"title": p.title, "url": p.url}
        for p in passages
    ]

    return AnswerResponse(
        answer=answer_text,
        sources=sources,
        pages_fetched=len(passages),
        fallback=False,
    )