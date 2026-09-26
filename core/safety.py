"""Crisis resources and a deterministic risk check that runs alongside the AI's own safety rules."""

import re

DIRECTORY_URL = "https://findahelpline.com"

# country -> [(service, number, note)]. Numbers were checked against official sources; re-verify periodically.
HELPLINES = {
    "India": [
        ("Tele-MANAS", "14416", "Free, 24/7, 20+ languages. Also 1-800-891-4416"),
        ("AASRA", "022 2754 6669", "24/7 emotional support in English and Hindi"),
    ],
    "USA": [("988 Suicide & Crisis Lifeline", "988", "Call or text, 24/7, free and confidential")],
    "UK": [("Samaritans", "116 123", "Free, 24/7 emotional support")],
    "Canada": [("9-8-8 Suicide Crisis Helpline", "988", "Call or text, 24/7, English and French")],
    "Australia": [("Lifeline", "13 11 14", "24/7 crisis support")],
}
EMERGENCY = {"India": "112", "USA": "911", "UK": "999", "Canada": "911", "Australia": "000"}
COUNTRIES = list(HELPLINES)

CRISIS_RE = re.compile(
    r"\b(suicid\w*|kill(ing)?\s+my\s?self|end(ing)?\s+(my\s+(own\s+)?life|it\s+all)|take\s+my\s+(own\s+)?life"
    r"|want(ed)?\s+to\s+die|wanna\s+die|better\s+off\s+dead|(don'?t|do\s+not)\s+want\s+to\s+(live|be\s+alive|be\s+here|exist)"
    r"|(hurt|harm|cut)(ting)?\s+my\s?self|self[-\s]?harm\w*|no\s+reason\s+to\s+live"
    r"|khud\s?kushi|aatm\s?hatya|marna\s+chah\w+|jeena\s+nahi\s+chah\w+|jeene\s+ka\s+man+\s+nahi)\b",
    re.IGNORECASE,
)


def is_crisis(text):
    """True when text contains common self-harm or suicide language (English plus a few Hinglish phrases)."""
    return bool(CRISIS_RE.search(text or ""))


def dial(number):
    return re.sub(r"[^\d+]", "", number)
