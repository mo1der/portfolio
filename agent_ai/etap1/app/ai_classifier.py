import json

from openai import OpenAI

from app.core.settings import settings
OPENAI_API_KEY = settings.openai_api_key
OPENAI_MODEL = settings.openai_model
AI_MAX_OUTPUT_TOKENS = settings.ai_max_output_tokens

def classify_text_with_ai(text: str) -> dict:
    if not OPENAI_API_KEY:
        raise RuntimeError("Brak OPENAI_API_KEY")

    client = OpenAI(
        api_key=OPENAI_API_KEY,
        timeout=10.0,
    )

    prompt = f"""
Klasyfikuj wiadomość użytkownika.

Zwróć odpowiedź wyłącznie jako JSON w formacie:
{{
  "category": "FINANCE | IT_SUPPORT | HR | OTHER",
  "priority": "LOW | MEDIUM | HIGH",
  "summary": "krótkie streszczenie",
  "suggested_action": "proponowana akcja"
}}

Wiadomość:
{text}
"""

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {
                "role": "system",
                "content": "Jesteś agentem AI do klasyfikacji wiadomości biznesowych.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
        max_tokens=settings.ai_max_output_tokens,
    )

    content = response.choices[0].message.content

    try:
        result = json.loads(content)
        result["source"] = "AI"
        return result
    except json.JSONDecodeError:
        raise RuntimeError("AI zwróciło niepoprawny JSON")