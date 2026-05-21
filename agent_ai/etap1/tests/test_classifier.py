# tests/test_classifier.py

from app.classifier import classify_text_rule_based as classify_text
from app.schemas import Category, Priority


def test_classifies_it_support():
    result = classify_text("Nie mogę zalogować się do systemu.")

    assert result["category"] == Category.IT_SUPPORT
    assert result["priority"] == Priority.HIGH


def test_classifies_finance():
    result = classify_text("Mam problem z fakturą za ostatni miesiąc.")

    assert result["category"] == Category.FINANCE
    assert result["priority"] == Priority.HIGH


def test_classifies_hr():
    result = classify_text("Chcę zgłosić urlop na przyszły tydzień.")

    assert result["category"] == Category.HR
    assert result["priority"] == Priority.MEDIUM


def test_classifies_other():
    result = classify_text("Mam pytanie dotyczące ekspresu do kawy.")

    assert result["category"] == Category.OTHER
    assert result["priority"] == Priority.LOW