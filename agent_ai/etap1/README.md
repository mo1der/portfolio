# AI Classifier Backend

Backend API do klasyfikowania zgłoszeń tekstowych oraz symulowanego wykonywania akcji po klasyfikacji.

Projekt jest pierwszym etapem nauki budowania agentów AI i backendów, które mogą być używane w firmach do automatyzacji obsługi zgłoszeń, wiadomości lub prostych procesów biznesowych.

---

## Co robi ten projekt?

Aplikacja przyjmuje tekst zgłoszenia i zwraca klasyfikację, czyli informację:

- jakiej kategorii dotyczy zgłoszenie,
- jaki ma priorytet,
- krótkie podsumowanie,
- sugerowaną akcję,
- źródło klasyfikacji.

Dodatkowo projekt posiada endpoint `/process`, który po klasyfikacji wybiera i symuluje wykonanie dalszej akcji biznesowej.

Przykładowe kategorie:

- `FINANCE`
- `IT_SUPPORT`
- `HR`
- `OTHER`

Przykładowe akcje po klasyfikacji:

- `CREATE_FINANCE_TICKET`
- `CREATE_IT_TICKET`
- `CREATE_HR_CASE`
- `MARK_AS_LOW_PRIORITY`
- `SEND_TO_GENERAL_QUEUE`
- `ESCALATE_TO_MANAGER`
- 
Projekt obsługuje klasyfikację:

- regułową, czyli na podstawie prostych zasad w kodzie,
- AI, czyli z użyciem modelu OpenAI, jeśli skonfigurowany jest klucz API.

---

## Główna idea projektu

Projekt pokazuje prosty przepływ automatyzacji biznesowej:

wiadomość użytkownika
→ klasyfikacja
→ wybór akcji
→ symulowane wykonanie akcji
→ odpowiedź API

Przykład:

"Mam pilny problem z fakturą za ostatni miesiąc."
→ FINANCE
→ HIGH
→ CREATE_FINANCE_TICKET
→ symulowane zgłoszenie do działu finansów

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
│   ├── action_agent.py
│   ├── action_executor.py
│   ├── process_service.py
│   ├── config.py
│   ├── exceptions.py
│   └── logging_config.py
├── tests/
│   ├── test_main.py
│   ├── test_classifier.py
│   ├── test_ai_classifier.py
│   ├── test_action_agent.py
│   ├── test_action_executor.py
│   ├── test_process_api.py
│   ├── test_process_service.py
│   └── test_agent_router.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```
## Diagram architektury

Poniżej schemat pokazujący przepływ danych w backendzie AI Classifier:

![Diagram AI Classifier Backend](a_full_page_screenshot_image_of_a_readme_style_d.png)

- FastAPI Backend przyjmuje requesty HTTP.
- Endpoint `/classify` klasyfikuje wiadomość.
- Endpoint `/process` klasyfikuje wiadomość i uruchamia symulowaną akcję.
- Agent Router wybiera, czy użyć klasyfikatora AI, czy regułowego.
- Action Agent wybiera dalszą akcję na podstawie kategorii i priorytetu.
- Action Executor symuluje wykonanie wybranej akcji.
- Middleware i logowanie monitorują requesty.
- Testy automatyczne sprawdzają poprawność działania aplikacji.
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
- routing między klasyfikatorem regułowym i AI
- wybór akcji po klasyfikacji,
- symulowane wykonanie akcji,
- pełny proces `/process`.

Poprawny wynik testów powinien wyglądać podobnie do:

```text
30 passed
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

### POST /process

Endpoint do przetwarzania wiadomości przez prostego agenta.

Ten endpoint:

1. przyjmuje tekst wiadomości,
2. klasyfikuje wiadomość,
3. wybiera odpowiednią akcję,
4. symuluje wykonanie akcji,
5. zwraca pełną odpowiedź z polem `executed_action`.


Przykładowe zapytanie:

```json
{
  "text": "Mam pilny problem z fakturą za ostatni miesiąc."
}
```
Przykładowa odpowiedź:
```json
{
  "category": "FINANCE",
  "priority": "HIGH",
  "summary": "Mam pilny problem z fakturą za ostatni miesiąc.",
  "suggested_action": "Przekazać do działu finansów.",
  "source": "RULE_BASED",
  "executed_action": {
    "action_type": "CREATE_FINANCE_TICKET",
    "target_department": "FINANCE",
    "status": "SIMULATED",
    "message": "Utworzono symulowane zgłoszenie do działu finansów."
  }
}
```

---

## Przykładowe akcje biznesowe

W obecnej wersji akcje są symulowane.

To znaczy, że backend nie tworzy jeszcze prawdziwego zgłoszenia w zewnętrznym systemie, ale pokazuje, jaka akcja zostałaby wykonana.

Przykładowe mapowanie:

```text
FINANCE + HIGH/MEDIUM → CREATE_FINANCE_TICKET
IT_SUPPORT + HIGH/MEDIUM → CREATE_IT_TICKET
HR + HIGH/MEDIUM → CREATE_HR_CASE
LOW → MARK_AS_LOW_PRIORITY
OTHER + HIGH → ESCALATE_TO_MANAGER
OTHER + MEDIUM → SEND_TO_GENERAL_QUEUE
```
W przyszłości w miejscu symulacji można podłączyć prawdziwe systemy, np.:

Jira,
CRM,
Helpdesk,
e-mail,
Slack,
Microsoft Teams,
bazę danych.

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
- endpoint `/process`,
- wybór akcji po klasyfikacji,
- symulowane wykonanie akcji,
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
30 passed
```

---

## Następny etap

Następny logiczny etap to:

```text
Etap 3 — zapis historii zgłoszeń do bazy danych
```

W tym etapie można przygotować:

- bazę danych,
- zapisywanie każdego zgłoszenia,
- historię klasyfikacji,
- historię wykonanych akcji,
- endpoint do pobierania zgłoszeń,
- możliwość filtrowania po kategorii, priorytecie i statusie,
- przygotowanie projektu pod realne integracje biznesowe.