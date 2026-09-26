import pytest

from core import safety


@pytest.mark.parametrize(
    "text",
    [
        "I want to die",
        "I keep thinking about suicide",
        "I want to hurt myself",
        "I don't want to be here anymore",
        "I might kill myself",
        "There is no reason to live",
        "mujhe khudkushi ke khayal aate hain",
        "main marna chahta hoon",
    ],
)
def test_detects_risk_language(text):
    assert safety.is_crisis(text)


@pytest.mark.parametrize(
    "text", ["I'm dying to see that film", "I could kill for a coffee", "Work was stressful", "", None]
)
def test_ignores_everyday_language(text):
    assert not safety.is_crisis(text)


def test_every_country_has_helplines_and_an_emergency_number():
    assert set(safety.HELPLINES) == set(safety.EMERGENCY)
    assert all(safety.HELPLINES[country] for country in safety.COUNTRIES)


def test_dial_strips_formatting():
    assert safety.dial("022 2754 6669") == "02227546669"
