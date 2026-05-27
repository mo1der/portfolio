import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def classify_text_with_ai(text: str) -> dict:
    if not OPENAI_API_KEY:
        raise RuntimeError("Brak OPENAI_API_KEY")

    client = OpenAI(api_key=OPENAI_API_KEY)

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
        model="gpt-4.1-mini",
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
    )

    content = response.choices[0].message.content

    try:
        result = json.loads(content)
        result["source"] = "AI"
        return result
    except json.JSONDecodeError:
        raise RuntimeError("AI zwróciło niepoprawny JSON")