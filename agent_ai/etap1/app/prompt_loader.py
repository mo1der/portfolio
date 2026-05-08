from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def load_prompt(filename: str) -> str:
    prompt_path = BASE_DIR / "prompts" / filename

    with open(prompt_path, "r", encoding="utf-8") as file:
        return file.read()