import json

from openai import OpenAI

from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.schemas import Category, ClassificationResponse, Priority

from app.prompt_loader import load_prompt
from app.exceptions import AIResponseError

client = OpenAI(api_key=OPENAI_API_KEY)


def classify_text_with_ai(text: str) -> ClassificationResponse:
    system_prompt = load_prompt("classification_prompt.txt")
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": (
                    f"Zaklasyfikuj zgłoszenie:\n{text}\n\n"
                    "Zwróć JSON z polami: category, priority, summary, suggested_action."
                ),
            },
        ],
        temperature=0,
    )

    content = response.choices[0].message.content

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise AIResponseError(
            f"Invalid AI JSON response: {content}"
        ) from e

    return ClassificationResponse(
        category=Category(data["category"]),
        priority=Priority(data["priority"]),
        summary=data["summary"],
        suggested_action=data["suggested_action"],
        source="AI",
    )