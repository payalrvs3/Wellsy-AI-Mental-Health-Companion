from types import SimpleNamespace as NS

import groq
import httpx
import pytest

from core import ai


def chunk(text):
    return NS(choices=[NS(delta=NS(content=text))])


class FakeClient:
    """Stands in for the Groq client and records the request it receives."""

    def __init__(self, chunks=(), error=None):
        self.chunks, self.error, self.calls = chunks, error, []
        self.chat = NS(completions=self)

    def create(self, **options):
        self.calls.append(options)
        if self.error:
            raise self.error
        if options.get("stream"):
            return iter(self.chunks)
        return NS(choices=[NS(message=NS(content="  Take a breath.  "))])


@pytest.fixture
def fake(monkeypatch):
    client = FakeClient([chunk("Hel"), chunk(None), chunk("lo")])
    monkeypatch.setattr(ai, "_client", lambda: client)
    return client


ASK = [{"role": "user", "content": "hi"}]


def test_prompt_lists_only_the_users_country_helplines():
    prompt = ai.system_prompt("Growth Coach", "India")
    assert "Tele-MANAS 14416" in prompt and "988" not in prompt
    assert "none on file" in ai.system_prompt("Growth Coach", None)


def test_prompt_includes_risk_and_context_when_given():
    plain = ai.system_prompt("Growth Coach")
    full = ai.system_prompt("Growth Coach", context="last 7 days: 3 check-ins", risk=True)
    assert "signal risk" not in plain and "signal risk" in full and "3 check-ins" in full


def test_stream_reply_joins_chunks_and_sets_reasoning_options(fake, monkeypatch):
    monkeypatch.setattr(ai, "MODEL", "openai/gpt-oss-120b")
    assert "".join(ai.stream_reply(ASK, "Wellsy Counselor")) == "Hello"
    call = fake.calls[0]
    assert call["stream"] and call["reasoning_effort"] == "low" and call["include_reasoning"] is False
    assert call["messages"][0]["role"] == "system"


def test_reasoning_options_are_skipped_for_other_models(fake, monkeypatch):
    monkeypatch.setattr(ai, "MODEL", "some-other-model")
    list(ai.stream_reply(ASK, "Wellsy Counselor"))
    assert "reasoning_effort" not in fake.calls[0]


def test_history_is_trimmed(fake):
    history = [{"role": "user", "content": str(i)} for i in range(100)]
    list(ai.stream_reply(history, "Wellsy Counselor"))
    assert len(fake.calls[0]["messages"]) == ai.HISTORY_MESSAGES + 1


def test_api_errors_become_friendly_messages(monkeypatch):
    response = httpx.Response(429, request=httpx.Request("POST", "https://api.groq.com"))
    error = groq.RateLimitError("limit", response=response, body=None)
    monkeypatch.setattr(ai, "_client", lambda: FakeClient(error=error))
    with pytest.raises(ai.AIError, match="busy"):
        list(ai.stream_reply(ASK, "Growth Coach"))


def test_missing_key_gives_a_clear_message(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    ai._client.cache_clear()
    with pytest.raises(ai.AIError, match="GROQ_API_KEY"):
        ai._client()


def test_complete_returns_stripped_text(fake):
    assert ai.complete("hi") == "Take a breath."
