import re


def split_complex_message(text: str):
    normalized_text = text.strip()

    if not normalized_text:
        return []

    parts = re.split(
        r"\s+(?:i|oraz|a także|plus|dodatkowo)\s+|[,;]+",
        normalized_text,
        flags=re.IGNORECASE,
    )

    cleaned_parts = []

    for part in parts:
        cleaned = part.strip()

        if not cleaned:
            continue

        if len(cleaned) < 3:
            continue

        cleaned_parts.append(cleaned)

    if not cleaned_parts:
        return [normalized_text]

    return cleaned_parts


def is_complex_message(text: str):
    parts = split_complex_message(text)

    return len(parts) > 1