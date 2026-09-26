"""Groq-backed replies: persona prompts, streaming chat and one-shot completions."""

import os
from functools import cache

import groq

from core import safety

MODEL = os.getenv("WELLSY_MODEL", "openai/gpt-oss-120b")
HISTORY_MESSAGES = 30

PERSONAS = {
    "Wellsy Counselor": {
        "icon": "🌿",
        "tagline": "Balanced, structured support",
        "style": "Calm, warm and professional. Validate feelings first, then offer gentle structure.",
    },
    "Empathetic Listener": {
        "icon": "🫶",
        "tagline": "Feel heard and understood",
        "style": "Deeply empathetic and unhurried. Reflect feelings back and avoid problem-solving unless asked.",
    },
    "Growth Coach": {
        "icon": "🌱",
        "tagline": "Small steps, real progress",
        "style": "Encouraging and practical. Suggest one small realistic step. "
        "Stay calm, never pushy, if the user is overwhelmed.",
    },
    "CBT Companion": {
        "icon": "🧩",
        "tagline": "Reframe unhelpful thoughts",
        "style": "Structured and curious. Help spot thinking traps and weigh evidence with simple CBT techniques. "
        "Validate first and pause techniques if the user is in acute distress.",
    },
    "Mindfulness Guide": {
        "icon": "🧘",
        "tagline": "Ground yourself in the moment",
        "style": "Slow, gentle and present-focused. "
        "Guide short grounding, breathing or body-scan practices step by step.",
    },
}


class AIError(RuntimeError):
    """An error message that is safe to show to the user."""


@cache
def _client():
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise AIError("Wellsy's AI isn't configured yet. Set GROQ_API_KEY to turn on chat and reflections.")
    return groq.Groq(api_key=key, timeout=45, max_retries=2)


def system_prompt(persona, country=None, context="", risk=False):
    lines = safety.HELPLINES.get(country)
    helplines = "; ".join(f"{name} {number}" for name, number, _ in lines) if lines else "none on file"
    parts = [
        f"You are Wellsy, a warm AI wellbeing companion, speaking as the {persona}. {PERSONAS[persona]['style']}",
        "You are not a therapist, doctor or crisis service. Never diagnose, prescribe or promise outcomes.",
        "Guidelines:",
        "- Acknowledge feelings first. Keep replies under about 150 words and ask at most one question.",
        "- Offer evidence-based skills (grounding, paced breathing, CBT reframing, small behavioural "
        "steps) when they fit, "
        "and point to Wellsy's Toolkit, Mood tracker or Journal when relevant.",
        "- Encourage real-world connection and professional care. Never encourage dependence on you.",
        "- If the user mentions suicide, self-harm, abuse or immediate danger: respond with calm compassion, encourage "
        "contacting local emergency services or a helpline, and suggest reaching someone they trust.",
        f"- Helplines you may mention (never invent numbers): {helplines}. Otherwise suggest local emergency services "
        f"or {safety.DIRECTORY_URL}.",
        "- Reply in the language the user writes in.",
    ]
    if risk:
        parts.append("The latest message may signal risk. Prioritise safety and support over any technique.")
    if context:
        parts.append(
            "Recent activity from the user's own tracking, for background only — weave it in naturally "
            f"if it helps and never list it back verbatim: {context}"
        )
    return "\n".join(parts)


def _create(messages, **options):
    if "gpt-oss" in MODEL:
        options |= {"reasoning_effort": "low", "include_reasoning": False}
    return _client().chat.completions.create(model=MODEL, messages=messages, max_completion_tokens=1500, **options)


def _explain(error):
    if isinstance(error, (groq.AuthenticationError, groq.PermissionDeniedError)):
        return "The AI service rejected the API key. Please check GROQ_API_KEY."
    if isinstance(error, (groq.NotFoundError, groq.BadRequestError)):
        return f"The model '{MODEL}' is unavailable. Set WELLSY_MODEL to a model listed in the Groq console."
    if isinstance(error, groq.RateLimitError):
        return "Wellsy is busy right now. Please try again in a moment."
    return "I couldn't reach the AI service. Please try again."


def stream_reply(history, persona, country=None, context="", risk=False):
    """Yield the assistant's reply in chunks. `history` is a list of {"role", "content"} dicts."""
    messages = [{"role": "system", "content": system_prompt(persona, country, context, risk)}]
    messages += [{"role": m["role"], "content": m["content"]} for m in history[-HISTORY_MESSAGES:]]
    try:
        for chunk in _create(messages, stream=True, temperature=0.7):
            if chunk.choices and (text := chunk.choices[0].delta.content):
                yield text
    except groq.GroqError as error:
        raise AIError(_explain(error)) from error


def complete(prompt, system="You are Wellsy, a warm and concise wellbeing companion."):
    """Return a single short reply for one-off tasks such as journal reflections."""
    messages = [{"role": "system", "content": system}, {"role": "user", "content": prompt}]
    try:
        return (_create(messages, temperature=0.6).choices[0].message.content or "").strip()
    except groq.GroqError as error:
        raise AIError(_explain(error)) from error


if __name__ == "__main__":
    ask = [{"role": "user", "content": "Say hello in one sentence."}]
    print("".join(stream_reply(ask, "Wellsy Counselor")))
