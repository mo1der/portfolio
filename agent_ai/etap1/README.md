# AI Classifier Backend

Backend AI do klasyfikacji zgłoszeń firmowych zbudowany w FastAPI.

## Funkcje

- klasyfikacja zgłoszeń
- integracja z OpenAI API
- fallback rule-based
- agent router
- service layer
- prompt management
- structured AI outputs
- logging
- testy automatyczne

---

# Architektura

```text
FastAPI
↓
agent_router.py
↓
agents.py
↓
classification_service.py
↓
ai_classifier.py / classifier.py
↓
prompt_loader.py
↓
prompts/classification_prompt.txt
↓
OpenAI API
```

---

# Endpointy

## GET /

Sprawdzenie działania backendu.

## GET /health

Health check endpoint.

## POST /classify

Klasyfikacja zgłoszenia.

Przykład request:

```json
{
  "text": "Mam problem z fakturą."
}
```

Przykład response:

```json
{
  "category": "FINANCE",
  "priority": "HIGH",
  "summary": "Klient zgłasza problem z fakturą.",
  "suggested_action": "Przekazać do działu finansów.",
  "source": "AI"
}
```

---

# Uruchomienie

## Instalacja

```bash
pip install -r requirements.txt
```

## Start serwera

```bash
uvicorn app.main:app --reload
```

## Dokumentacja API

```text
http://127.0.0.1:8000/docs
```

---

# Testy

```bash
pytest tests -v
```

---

# Technologie

- Python
- FastAPI
- Pydantic
- OpenAI API
- Pytest
- Uvicorn