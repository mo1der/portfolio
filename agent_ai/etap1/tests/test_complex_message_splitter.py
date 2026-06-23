from app.complex_message_splitter import (
    is_complex_message,
    split_complex_message,
)


def test_split_complex_message_by_comma():
    parts = split_complex_message(
        "Mam problem z fakturą, nie mogę się zalogować"
    )

    assert parts == [
        "Mam problem z fakturą",
        "nie mogę się zalogować",
    ]


def test_split_complex_message_by_and():
    parts = split_complex_message(
        "Mam problem z fakturą i chcę zgłosić urlop"
    )

    assert parts == [
        "Mam problem z fakturą",
        "chcę zgłosić urlop",
    ]


def test_single_message_returns_one_part():
    parts = split_complex_message("Mam problem z fakturą.")

    assert parts == ["Mam problem z fakturą."]


def test_is_complex_message_returns_true_for_multiple_parts():
    assert is_complex_message(
        "Mam problem z fakturą i nie mogę się zalogować"
    ) is True


def test_is_complex_message_returns_false_for_single_part():
    assert is_complex_message("Mam problem z fakturą.") is False