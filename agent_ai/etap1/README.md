# AI Classifier Backend

Backend API do klasyfikowania zgłoszeń tekstowych.

Projekt jest pierwszym etapem nauki budowania agentów AI i backendów, które mogą być używane w firmach do automatyzacji obsługi zgłoszeń, wiadomości lub prostych procesów biznesowych.

---

## Co robi ten projekt?

Aplikacja przyjmuje tekst zgłoszenia i zwraca klasyfikację, czyli informację:

- jakiej kategorii dotyczy zgłoszenie,
- jaki ma priorytet,
- krótkie podsumowanie,
- sugerowaną akcję,
- źródło klasyfikacji.

Przykładowe kategorie:

- `FINANCE`
- `IT_SUPPORT`
- `HR`
- `OTHER`

Projekt obsługuje klasyfikację:

- regułową, czyli na podstawie prostych zasad w kodzie,
- AI, czyli z użyciem modelu OpenAI, jeśli skonfigurowany jest klucz API.

---

## Technologie

Projekt używa:

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- Pytest
- OpenAI SDK
- Docker
- Docker Compose

---

## Struktura projektu

Przykładowa struktura katalogów:

```text
etap1/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   ├── classifier.py
│   ├── ai_classifier.py
│   ├── agent_router.py
│   ├── config.py
│   ├── exceptions.py
│   └── logging_config.py
├── tests/
│   ├── test_main.py
│   ├── test_classifier.py
│   ├── test_ai_classifier.py
│   └── test_agent_router.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Uruchamianie lokalne bez Dockera

### 1. Utworzenie środowiska wirtualnego

W folderze projektu uruchom:

```bash
python -m venv venv
```

### 2. Aktywacja środowiska

Na Windows PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

Jeśli PowerShell blokuje aktywację środowiska, można uruchomić:

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

A potem ponownie:

```bash
.\venv\Scripts\Activate.ps1
```

### 3. Instalacja zależności

```bash
pip install -r requirements.txt
```

### 4. Uruchomienie aplikacji

```bash
uvicorn app.main:app --reload
```

Po uruchomieniu aplikacja będzie dostępna pod adresem:

```text
http://127.0.0.1:8000
```

Dokumentacja API będzie dostępna pod adresem:

```text
http://127.0.0.1:8000/docs
```

---

## Uruchamianie przez Docker

Docker pozwala uruchomić aplikację w kontenerze, czyli w odizolowanym środowisku.

Dzięki temu projekt nie musi polegać wyłącznie na ustawieniach lokalnego komputera.

### 1. Zbudowanie obrazu Docker

```bash
docker build -t ai-classifier-backend .
```

### 2. Uruchomienie kontenera

```bash
docker run -p 8000:8000 ai-classifier-backend
```

Po uruchomieniu aplikacja będzie dostępna tutaj:

```text
http://localhost:8000
```

Dokumentacja API:

```text
http://localhost:8000/docs
```

---

## Uruchamianie przez Docker Compose

Docker Compose pozwala uruchomić projekt prostszą komendą.

Nie trzeba ręcznie podawać wszystkich parametrów kontenera, ponieważ są zapisane w pliku:

```text
docker-compose.yml
```

### 1. Uruchomienie aplikacji

```bash
docker compose up --build
```

Ta komenda:

- buduje obraz aplikacji,
- tworzy sieć Dockera,
- tworzy kontener,
- uruchamia backend.

Po uruchomieniu aplikacja będzie dostępna tutaj:

```text
http://localhost:8000
```

Dokumentacja API:

```text
http://localhost:8000/docs
```

### 2. Zatrzymanie aplikacji

Jeśli aplikacja działa w terminalu, można ją zatrzymać skrótem:

```text
CTRL + C
```

Można też użyć komendy:

```bash
docker compose down
```

Ta komenda zatrzymuje i usuwa kontenery utworzone przez Compose.

---

## Ważne komendy Docker Compose

### Uruchomienie aplikacji

```bash
docker compose up --build
```

### Uruchomienie aplikacji w tle

```bash
docker compose up --build -d
```

Opcja `-d` oznacza tryb w tle.

Aplikacja działa, ale nie zajmuje terminala.

### Sprawdzenie działających kontenerów

```bash
docker ps
```

### Sprawdzenie wszystkich kontenerów

```bash
docker ps -a
```

### Zatrzymanie aplikacji

```bash
docker compose down
```

### Podejrzenie logów

```bash
docker compose logs
```

### Podejrzenie logów na żywo

```bash
docker compose logs -f
```

---

## Testowanie aplikacji

Testy uruchamia się komendą:

```bash
pytest
```

Albo dokładniej:

```bash
python -m pytest
```

Projekt posiada testy sprawdzające między innymi:

- działanie endpointów API,
- klasyfikację regułową,
- obsługę klasyfikacji AI,
- obsługę błędnej odpowiedzi AI,
- routing między klasyfikatorem regułowym i AI.

Poprawny wynik testów powinien wyglądać podobnie do:

```text
16 passed
```

---

## Endpointy API

### GET /

Endpoint testowy.

Sprawdza, czy backend działa.

Przykładowa odpowiedź:

```json
{
  "message": "AI Classifier Backend działa"
}
```

### GET /health

Endpoint zdrowia aplikacji.

Służy do sprawdzania, czy aplikacja działa poprawnie.

Przykładowa odpowiedź:

```json
{
  "status": "ok"
}
```

### POST /classify

Endpoint do klasyfikowania tekstu.

Przykładowe zapytanie:

```json
{
  "text": "Mam problem z fakturą za ostatni miesiąc."
}
```

Przykładowa odpowiedź:

```json
{
  "category": "FINANCE",
  "priority": "HIGH",
  "summary": "Zgłoszenie dotyczy problemu z fakturą.",
  "suggested_action": "Przekazać zgłoszenie do działu finansowego.",
  "source": "RULE_BASED"
}
```

---

## Plik .env

Projekt może używać pliku `.env` do przechowywania ustawień lokalnych.

Przykład:

```env
OPENAI_API_KEY=tu_wklej_swoj_klucz_api
USE_AI_CLASSIFIER=false
```

Pliku `.env` nie należy dodawać do Gita, ponieważ może zawierać prywatne dane.

Dlatego w `.gitignore` powinien znajdować się wpis:

```text
.env
```

Do repozytorium można dodać plik przykładowy:

```text
.env.example
```

---

## Przykładowy plik .env.example

```env
OPENAI_API_KEY=
USE_AI_CLASSIFIER=false
```

---

## Git — podstawowy workflow

Po zmianach w projekcie warto sprawdzić status:

```bash
git status
```

Dodanie wszystkich zmienionych plików:

```bash
git add .
```

Utworzenie commita:

```bash
git commit -m "Update README after Docker Compose setup"
```

Wysłanie zmian na GitHub:

```bash
git push
```

Jeśli Git pokazuje:

```text
nothing to commit, working tree clean
```

to znaczy, że nie ma żadnych nowych zmian do zapisania.

---

## Czego nauczyliśmy się w tym etapie?

W tym etapie projekt został uporządkowany pod kątem uruchamiania w Dockerze.

Zrobione zostało:

- dodanie Dockerfile,
- dodanie docker-compose.yml,
- uruchomienie aplikacji w kontenerze,
- sprawdzenie działania FastAPI w Dockerze,
- uporządkowanie README,
- opisanie lokalnego uruchamiania,
- opisanie uruchamiania przez Docker,
- opisanie uruchamiania przez Docker Compose,
- opisanie podstawowych komend testowych i gitowych.

---

## Aktualny status projektu

Projekt posiada:

- działający backend FastAPI,
- endpoint `/`,
- endpoint `/health`,
- endpoint `/classify`,
- klasyfikator regułowy,
- obsługę klasyfikatora AI,
- obsługę błędów AI,
- logowanie requestów,
- testy automatyczne,
- Dockerfile,
- docker-compose.yml,
- dokumentację w README.

Aktualny stan testów:

```text
16 passed
```

---

## Następny etap

Następny logiczny etap to:

```text
Etap 1.9 — przygotowanie projektu pod portfolio i prezentację techniczną
```

W tym etapie można przygotować:

- opis projektu po polsku i angielsku,
- krótką sekcję „Business use case”,
- opis architektury,
- screeny z działania aplikacji,
- przykładowe requesty i response,
- finalny commit kończący Etap 1.