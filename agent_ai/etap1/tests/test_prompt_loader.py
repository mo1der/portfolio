from app.prompt_loader import load_prompt


def test_load_classification_prompt():
    prompt = load_prompt("classification_prompt.txt")

    assert "Jesteś klasyfikatorem zgłoszeń firmowych" in prompt
    assert "IT_SUPPORT" in prompt
    assert "FINANCE" in prompt
    assert "HR" in prompt
    assert "OTHER" in prompt