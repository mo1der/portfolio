# AI Classifier Backend

Backend API do klasyfikacji wiadomości biznesowych.

Projekt powstał jako Etap 1 nauki budowania agentów AI i backendów, które można później wdrażać komercyjnie w firmach.

Aplikacja przyjmuje wiadomość tekstową i klasyfikuje ją do jednej z kategorii, np.:

- FINANCE
- IT_SUPPORT
- HR
- OTHER

Dodatkowo określa priorytet wiadomości oraz sugerowaną akcję.

---

## Technologie

Projekt używa:

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- Pytest
- OpenAI API
- Docker

---

## Struktura projektu

```text
etap1/
├── app/
│   ├── main.py
│   ├── schemas.py
│   ├── classifier.py
│   ├── ai_classifier.py
│   ├── classification_service.py
│   ├── agent_router.py
│   ├── agents.py
│   ├── exceptions.py
│   ├── error_handlers.py
│   ├── logging_config.py
│   ├── middleware.py
│   └── prompt_loader.py
├── tests/
│   ├── test_api.py
│   ├── test_health.py
│   ├── test_classifier.py
│   ├── test_ai_classifier.py
│   ├── test_ai_errors.py
│   ├── test_classification_service.py
│   ├── test_agent_router.py
│   ├── test_error_handlers.py
│   └── test_prompt_loader.py
├── prompts/
├── Dockerfile
├── .dockerignore
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## Jak działa aplikacja

Aplikacja ma dwa sposoby klasyfikacji wiadomości.

### 1. Klasyfikacja AI

Jeśli dostępny jest klucz OpenAI, aplikacja może użyć modelu AI do klasyfikacji wiadomości.

AI zwraca dane takie jak:

```json
{
  "category": "FINANCE",
  "priority": "HIGH",
  "summary": "Klient zgłasza problem z fakturą.",
  "suggested_action": "Przekazać do działu finansów."
}
```

### 2. Klasyfikacja regułowa

Jeśli OpenAI nie działa albo brakuje klucza API, aplikacja korzysta z prostego klasyfikatora regułowego.

Dzięki temu backend nadal działa nawet bez dostępu do OpenAI.

---

## Endpointy API

### Strona główna

```http
GET /
```

Przykładowa odpowiedź:

```json
{
  "message": "AI Classifier Backend działa"
}
```

### Health check

```http
GET /health
```

Służy do sprawdzenia, czy aplikacja działa.

Przykładowa odpowiedź:

```json
{
  "status": "ok"
}
```

### Klasyfikacja wiadomości

```http
POST /classify
```

Przykładowe zapytanie:

```json
{
  "message": "Nie dostałem faktury za ostatni miesiąc."
}
```

Przykładowa odpowiedź:

```json
{
  "category": "FINANCE",
  "priority": "HIGH",
  "summary": "Klient zgłasza problem z fakturą.",
  "suggested_action": "Przekazać do działu finansów.",
  "source": "AI"
}
```

Jeśli aplikacja użyje klasyfikatora regułowego, pole `source` może mieć wartość:

```text
RULE_BASED
```

---

## Dokumentacja API

Po uruchomieniu aplikacji dokumentacja Swagger jest dostępna pod adresem:

```text
http://127.0.0.1:8000/docs
```

---

## Uruchomienie lokalne

### 1. Utworzenie środowiska wirtualnego

```bash
python -m venv venv
```

### 2. Aktywacja środowiska

Windows PowerShell:

```powershell
.\venv\Scripts\activate
```

Jeśli aktywacja jest zablokowana przez politykę PowerShell, można uruchamiać komendy bez aktywacji, np.:

```powershell
.\venv\Scripts\python.exe -m pytest
```

### 3. Instalacja bibliotek

```bash
pip install -r requirements.txt
```

### 4. Uruchomienie aplikacji

```bash
uvicorn app.main:app --reload
```

Aplikacja będzie dostępna pod adresem:

```text
http://127.0.0.1:8000
```

---

## Zmienne środowiskowe

Aplikacja może korzystać z pliku `.env`.

Przykład:

```env
OPENAI_API_KEY=tu_wklej_swoj_klucz_api
```

Plik `.env` nie powinien być dodawany do repozytorium.

Dlatego znajduje się w `.gitignore` oraz `.dockerignore`.

---

## Uruchamianie testów

Aby uruchomić wszystkie testy:

```powershell
.\venv\Scripts\python.exe -m pytest
```

Oczekiwany wynik:

```text
16 passed
```

---

## Uruchamianie przez Docker

Projekt można uruchomić również w kontenerze Dockera.

Docker pozwala uruchomić aplikację w osobnym środowisku, które zawiera własnego Pythona, biblioteki i kod aplikacji.

Dzięki temu nie trzeba ręcznie konfigurować środowiska na każdym komputerze.

### Budowanie obrazu

W głównym folderze projektu uruchom:

```bash
docker build -t ai-classifier-backend .
```

Kropka na końcu oznacza:

```text
buduj obraz z aktualnego folderu
```

### Uruchomienie kontenera

```bash
docker run -p 8000:8000 ai-classifier-backend
```

Po uruchomieniu aplikacja będzie dostępna pod adresami:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

### Uruchomienie kontenera z plikiem `.env`

Jeśli aplikacja ma korzystać z klucza OpenAI, można uruchomić kontener z plikiem `.env`:

```bash
docker run --env-file .env -p 8000:8000 ai-classifier-backend
```

Plik `.env` nie jest kopiowany do obrazu Dockera, ponieważ znajduje się w `.dockerignore`.

### Zatrzymanie kontenera

Jeśli kontener działa w terminalu, można go zatrzymać skrótem:

```text
CTRL + C
```

---

## Eksport obrazu Dockera do pliku

Gotowy obraz Dockera można zapisać do jednego pliku:

```bash
docker save -o ai-classifier-backend.tar ai-classifier-backend
```

Powstanie plik:

```text
ai-classifier-backend.tar
```

Taki plik można przenieść na inny komputer, na którym jest Docker.

### Załadowanie obrazu na innym komputerze

```bash
docker load -i ai-classifier-backend.tar
```

Potem można uruchomić aplikację:

```bash
docker run -p 8000:8000 ai-classifier-backend
```

---

## Plik Dockerfile

Projekt zawiera plik:

```text
Dockerfile
```

Odpowiada on za zbudowanie obrazu Dockera.

Aktualna wersja:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Plik .dockerignore

Projekt zawiera plik:

```text
.dockerignore
```

Odpowiada on za pomijanie niepotrzebnych plików przy budowaniu obrazu Dockera.

Aktualna wersja:

```text
venv/
__pycache__/
.pytest_cache/
*.pyc
.env
.git/
.idea/
```

Dzięki temu do obrazu Dockera nie trafiają m.in.:

- lokalne środowisko `venv`,
- cache Pythona,
- prywatny plik `.env`,
- folder `.git`,
- ustawienia PyCharma.

---

## Git — podstawowy workflow

Najczęstszy schemat pracy:

```bash
git status
git add .
git status
git commit -m "Opis zmian"
git push
```

Znaczenie:

```text
git status   -> sprawdza, co się zmieniło
git add .    -> dodaje zmiany do najbliższego commita
git commit   -> zapisuje punkt w historii projektu
git push     -> wysyła zmiany na GitHub
```

---

## Status projektu

Aktualny etap:

```text
Etap 1.6 — Docker
```

Zrobione:

- backend FastAPI,
- endpoint `/`,
- endpoint `/health`,
- endpoint `/classify`,
- dokumentacja `/docs`,
- klasyfikator regułowy,
- klasyfikator AI,
- fallback z AI na reguły,
- obsługa błędów,
- logowanie requestów,
- testy automatyczne,
- Dockerfile,
- .dockerignore,
- uruchomienie aplikacji w kontenerze,
- poprawione testy po zmianie klienta OpenAI.

Aktualny wynik testów:

```text
16 passed
```

---

## Kolejne możliwe kroki

Planowane następne etapy:

- dodanie `docker-compose.yml`,
- uporządkowanie konfiguracji aplikacji,
- rozbudowa klasyfikatora,
- dodanie prostego frontendu,
- przygotowanie aplikacji pod wdrożenie na serwerze,
- dodanie CI/CD, czyli automatycznego uruchamiania testów po wypchnięciu kodu na GitHub.