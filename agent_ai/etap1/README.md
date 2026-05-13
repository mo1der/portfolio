# AI Classifier Backend

Backend API built with FastAPI for classifying user messages into business categories using an AI classifier with a rule-based fallback.

This project is part of a staged learning path for building commercial AI agents and AI-powered backend systems.

---

## Features

- FastAPI backend
- `/classify` endpoint for message classification
- `/health` endpoint for application diagnostics
- AI-based classification using OpenAI
- Rule-based fallback classifier
- AI can be enabled or disabled using environment variables
- Prompt loading from external files
- Pydantic schemas for request and response validation
- Application settings loaded from `.env`
- Basic logging
- Automated tests with pytest

---

## Project Structure

```text
app/
├── main.py
├── agent_router.py
├── agents.py
├── classification_service.py
├── ai_classifier.py
├── classifier.py
├── schemas.py
├── prompt_loader.py
├── logger.py
├── exceptions.py
├── core/
│   └── settings.py
└── prompts/
    └── classification_prompt.txt

tests/
├── test_agent_router.py
├── test_ai_classifier.py
├── test_ai_errors.py
├── test_api.py
├── test_classification_service.py
├── test_classifier.py
├── test_health.py
└── test_prompt_loader.py
```

---

## Architecture

The application is split into several layers:

```text
HTTP request
    ↓
FastAPI endpoint
    ↓
agent_router.py
    ↓
classification_service.py
    ↓
AI classifier or rule-based fallback
    ↓
ClassificationResponse
```

### Main Components

| Component | Responsibility |
|---|---|
| `main.py` | Creates the FastAPI application and registers routes |
| `agent_router.py` | Defines API routes for the classification agent |
| `agents.py` | Contains agent-level logic |
| `classification_service.py` | Decides whether to use AI or fallback |
| `ai_classifier.py` | Handles AI-based classification |
| `classifier.py` | Rule-based fallback classifier |
| `prompt_loader.py` | Loads prompts from files |
| `schemas.py` | Defines request and response models |
| `settings.py` | Loads configuration from environment variables |
| `logger.py` | Provides application logging |
| `exceptions.py` | Defines custom application exceptions |

---

## Classification Flow

The backend first checks whether AI is enabled.

If `AI_ENABLED=true`:

```text
Try AI classifier
    ↓
If AI succeeds → return AI result
    ↓
If AI fails → use rule-based fallback
```

If `AI_ENABLED=false`:

```text
Skip AI
    ↓
Use rule-based fallback directly
```

This allows the backend to work even without an active OpenAI API key or when OpenAI quota is unavailable.

---

## Environment Variables

Create a `.env` file based on `.env.example`.

Example `.env` file:

```env
APP_NAME=AI Classifier Backend
APP_VERSION=1.5.0
ENVIRONMENT=development

AI_ENABLED=false
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_KEY=
```

Do not commit your real `.env` file to GitHub.

The `.gitignore` file should contain:

```gitignore
venv/
__pycache__/
.pytest_cache/
*.pyc
.env
.idea/
```

---

## Installation

Create a virtual environment:

```powershell
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\activate
```

If activation is blocked by PowerShell execution policy, you can run commands directly through the virtual environment Python:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Install dependencies:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## Running the Application

Start the development server:

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

## API Endpoints

### Root Endpoint

```http
GET /
```

Example response:

```json
{
  "message": "AI Classifier Backend działa"
}
```

---

### Health Endpoint

```http
GET /health
```

Example response:

```json
{
  "status": "ok",
  "app_name": "AI Classifier Backend",
  "version": "1.5.0",
  "environment": "development",
  "ai_enabled": true
}
```

---

### Classification Endpoint

```http
POST /classify
```

Example request:

```json
{
  "text": "Nie mogę zalogować się do systemu."
}
```

Example response:

```json
{
  "category": "IT_SUPPORT",
  "priority": "HIGH",
  "summary": "User cannot log into the system.",
  "suggested_action": "Forward the issue to the IT support team.",
  "source": "RULE_BASED"
}
```

---

## Running Tests

Run all tests:

```powershell
.\venv\Scripts\python.exe -m pytest
```

Current test status:

```text
13 passed
```

---

## Current Stage

This project is currently at:

```text
Stage 1.5 - Backend configuration, health checks, fallback control, and portfolio readiness
```

Completed so far:

- FastAPI backend
- Classification endpoint
- Health endpoint
- AI classifier layer
- Rule-based fallback
- Settings loaded from environment variables
- AI enable/disable switch
- Prompt loading
- Custom exceptions
- Logging
- Automated tests

---

## Next Steps

Planned improvements:

- Global exception handlers
- Better structured error responses
- Request logging middleware
- More advanced classification categories
- Docker support
- CI workflow with GitHub Actions
- Deployment-ready configuration