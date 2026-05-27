# AI Classifier Backend

Backend API do klasyfikowania zgłoszeń tekstowych, routingu do odpowiednich agentów, zapisu historii zgłoszeń oraz symulowanego wykonywania akcji biznesowych.

Projekt jest częścią nauki budowania backendów i agentów AI, które mogą być używane w firmach do automatyzacji obsługi zgłoszeń, wiadomości lub prostych procesów biznesowych.

---

## Aktualny status projektu

Aktualnie ukończone są etapy:

```text
Etap 1–5 — podstawowy backend, klasyfikacja, baza danych, routing agentów i akcje
Etap 6 — statystyki zgłoszeń
Etap 7 — osobna konfiguracja dla testów i aplikacji
```

Aktualny wynik testów:

```text
47 passed
```

Projekt posiada już:

- działający backend FastAPI,
- klasyfikację zgłoszeń,
- routing zgłoszeń do agentów,
- symulowane wykonanie akcji,
- zapis historii zgłoszeń do bazy danych,
- endpoint historii zgłoszeń,
- endpoint statystyk zgłoszeń,
- obsługę SQLite / MySQL,
- osobną konfigurację dla testów i normalnego uruchomienia,
- testową bazę SQLite,
- awaryjny fallback do SQLite, gdy MySQL jest niedostępny,
- opcjonalny klasyfikator AI,
- testy automatyczne,
- Dockerfile,
- docker-compose.yml,
- dokumentację techniczną.

---

## Co robi ten projekt?

Aplikacja przyjmuje tekst zgłoszenia i zwraca informację:

- jakiej kategorii dotyczy zgłoszenie,
- jaki ma priorytet,
- jakie jest podsumowanie wiadomości,
- jaka akcja jest sugerowana,
- jakie jest źródło klasyfikacji,
- do jakiego agenta zgłoszenie powinno trafić,
- jaka akcja została zasymulowana,
- czy zgłoszenie zostało zapisane w historii.

Endpoint `/process` wykonuje pełny proces:

```text
wiadomość użytkownika
→ klasyfikacja
→ routing do agenta
→ symulowane wykonanie akcji
→ zapis historii w bazie
→ odpowiedź API
```

---

## Kategorie zgłoszeń

System rozpoznaje następujące kategorie:

```text
FINANCE
IT_SUPPORT
HR
OTHER
```

Przykłady:

| Tekst zgłoszenia | Kategoria |
|---|---|
| Mam problem z fakturą. | FINANCE |
| Mam problem z logowaniem. | IT_SUPPORT |
| Chcę zgłosić urlop. | HR |
| Mam pytanie ogólne. | OTHER |

---

## Priorytety zgłoszeń

System obsługuje priorytety:

```text
LOW
MEDIUM
HIGH
```

Przykłady:

| Treść | Priorytet |
|---|---|
| Mam pilny problem z fakturą. | HIGH |
| Mam problem z logowaniem. | HIGH |
| Mam pytanie ogólne. | LOW / MEDIUM |

---

## Agenci i routing

System kieruje zgłoszenia do odpowiednich agentów.

| Kategoria | Słowa kluczowe | Agent | Typ akcji |
|---|---|---|---|
| FINANCE | faktur, płatność, przelew, rachunek | finance_invoice_agent | CREATE_FINANCE_TICKET |
| IT_SUPPORT | hasł, logowan, zalog, komputer, drukarka, vpn | it_access_agent | CREATE_IT_TICKET |
| HR | urlop, zwoln, wynagrodzen, wniosek | hr_leave_agent | CREATE_HR_CASE |
| OTHER | brak dopasowania | general_agent | SEND_TO_GENERAL_QUEUE |

Reguły używają fragmentów słów, dzięki czemu obsługują odmiany, np.:

```text
faktur → faktura, faktury, fakturą
logowan / zalog → logowanie, zalogować, zalogowaniem
zwoln → zwolnienie, zwolnienia
```

---

## Przykład działania

Tekst:

```text
Mam problem z logowaniem.
```

System zwraca:

```json
{
  "category": "IT_SUPPORT",
  "priority": "HIGH",
  "summary": "Mam problem z logowaniem.",
  "suggested_action": "Przekazać do działu IT.",
  "source": "RULE_BASED",
  "route": {
    "agent_name": "it_access_agent",
    "department": "IT_SUPPORT",
    "reason": "Wiadomość dotyczy problemów IT.",
    "action_type": "CREATE_IT_TICKET"
  },
  "executed_action": {
    "action_type": "CREATE_IT_TICKET",
    "target_department": "IT_SUPPORT",
    "status": "SIMULATED",
    "message": "Utworzono symulowane zgłoszenie do działu IT_SUPPORT."
  }
}
```

---

## Technologie

Projekt używa:

- Python 3.11
- FastAPI
- Uvicorn
- Pydantic
- pydantic-settings
- SQLAlchemy
- SQLite
- MySQL
- PyMySQL
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
│   ├── schemas.py
│   ├── classifier.py
│   ├── ai_classifier.py
│   ├── agent_router.py
│   ├── action_agent.py
│   ├── action_executor.py
│   ├── process_service.py
│   ├── classification_service.py
│   ├── database.py
│   ├── models.py
│   ├── repositories.py
│   ├── response_builders.py
│   ├── middleware.py
│   ├── error_handlers.py
│   ├── exceptions.py
│   ├── logger.py
│   ├── prompt_loader.py
│   └── core/
│       └── settings.py
│
├── tests/
│   ├── conftest.py
│   ├── test_action_agent.py
│   ├── test_action_executor.py
│   ├── test_agent_router.py
│   ├── test_ai_classifier.py
│   ├── test_ai_errors.py
│   ├── test_api.py
│   ├── test_classification_and_process.py
│   ├── test_classification_service.py
│   ├── test_classifier.py
│   ├── test_error_handlers.py
│   ├── test_health.py
│   ├── test_process_api.py
│   ├── test_process_service.py
│   ├── test_prompt_loader.py
│   └── test_ticket_history.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Diagram architektury

```text
Użytkownik
   |
   v
FastAPI Backend
   |
   |-- GET /health
   |       |
   |       v
   |   Status aplikacji + informacja o bazie
   |
   |-- POST /classify
   |       |
   |       v
   |   Rule-based classifier / AI classifier
   |       |
   |       v
   |   Agent Router
   |       |
   |       v
   |   ProcessResponse
   |       |
   |       v
   |   Zapis historii w bazie
   |
   |-- POST /process
   |       |
   |       v
   |   Rule-based classifier / AI classifier
   |       |
   |       v
   |   Agent Router
   |       |
   |       v
   |   Symulowana akcja
   |       |
   |       v
   |   Zapis historii w bazie
   |
   |-- GET /tickets
   |       |
   |       v
   |   Lista zapisanych zgłoszeń
   |
   |-- GET /stats
           |
           v
       Statystyki zgłoszeń
```

---

## Najważniejsze komponenty

### `app/main.py`

Główny plik aplikacji FastAPI.

Zawiera endpointy:

- `GET /`
- `GET /health`
- `POST /classify`
- `POST /process`
- `GET /tickets`
- `GET /stats`

---

### `app/core/settings.py`

Centralna konfiguracja aplikacji.

Odpowiada za wczytywanie ustawień z plików środowiskowych:

- `.env` — normalne uruchomienie aplikacji,
- `.env.test` — środowisko testowe.

Testy dodatkowo wymuszają tryb testowy w `tests/conftest.py`, więc nie trzeba ręcznie wpisywać:

```powershell
$env:ENVIRONMENT="test"
```

przed uruchomieniem pytest.

---

### `app/database.py`

Konfiguracja połączenia z bazą danych.

Aplikacja może działać z:

- MySQL,
- SQLite,
- awaryjnym fallbackiem do SQLite.

Główna zasada:

```text
normalna aplikacja → MySQL z .env
testy → SQLite testowa ai_classifier_test.db
awaria MySQL → SQLite awaryjna ai_classifier.db
```

---

### `app/classifier.py`

Klasyfikator regułowy.

Rozpoznaje kategorię na podstawie słów kluczowych.

Przykład:

```text
Mam problem z logowaniem.
```

zostanie sklasyfikowane jako:

```text
IT_SUPPORT
```

---

### `app/ai_classifier.py`

Opcjonalny klasyfikator AI oparty o OpenAI API.

Może być użyty zamiast klasyfikatora regułowego, jeśli w konfiguracji ustawione jest:

```env
AI_ENABLED=true
```

W środowisku testowym AI jest wyłączone, aby testy nie zużywały tokenów i nie zależały od zewnętrznego API.

---

### `app/agent_router.py`

Wybiera konkretnego agenta na podstawie kategorii i treści zgłoszenia.

Przykłady:

```text
IT_SUPPORT + logowanie → it_access_agent
FINANCE + faktura → finance_invoice_agent
HR + urlop → hr_leave_agent
OTHER → general_agent
```

---

### `app/schemas.py`

Zawiera modele danych Pydantic.

Najważniejsze modele:

- `ClassificationRequest`
- `ClassificationResponse`
- `ProcessResponse`
- `RouteDecision`
- `ActionResult`
- `TicketHistoryResponse`

---

### `app/repositories.py`

Odpowiada za zapis i odczyt historii zgłoszeń z bazy danych.

---

### `app/models.py`

Zawiera modele SQLAlchemy, czyli opis tabel w bazie danych.

---

### `tests/conftest.py`

Centralna konfiguracja testów.

Odpowiada za:

- automatyczne ustawienie środowiska testowego,
- wymuszenie `AI_ENABLED=false`,
- wymuszenie bazy `sqlite:///./ai_classifier_test.db`,
- stworzenie testowego klienta FastAPI,
- podmianę dependency `get_db`,
- tworzenie i kasowanie tabel w testowej SQLite.

Dzięki temu testy:

- nie dotykają MySQL,
- nie zużywają tokenów OpenAI,
- nie zapisują danych do prawdziwej historii,
- mogą być uruchamiane zwykłą komendą pytest.

---

## Endpointy API

---

## `GET /`

Endpoint testowy.

Sprawdza, czy backend działa.

Przykładowa odpowiedź:

```json
{
  "message": "AI Classifier Backend działa"
}
```

---

## `GET /health`

Endpoint zdrowia aplikacji.

Pokazuje status aplikacji, konfigurację i aktualnie używaną bazę danych.

Przykładowa odpowiedź dla MySQL:

```json
{
  "status": "ok",
  "app_name": "AI Classifier Backend",
  "version": "1.5.0",
  "environment": "development",
  "ai_enabled": false,
  "database": "ai_classifier",
  "dialect": "mysql"
}
```

Przykładowa odpowiedź dla SQLite testowej:

```json
{
  "status": "ok",
  "app_name": "AI Classifier Backend",
  "version": "1.5.0",
  "environment": "test",
  "ai_enabled": false,
  "database": "ai_classifier_test.db",
  "dialect": "sqlite"
}
```

---

## `POST /classify`

Endpoint do klasyfikowania tekstu i wyboru agenta.

### Przykładowe zapytanie

```json
{
  "text": "Mam problem z logowaniem."
}
```

### Przykładowa odpowiedź

```json
{
  "category": "IT_SUPPORT",
  "priority": "HIGH",
  "summary": "Mam problem z logowaniem.",
  "suggested_action": "Przekazać do działu IT.",
  "source": "RULE_BASED",
  "route": {
    "agent_name": "it_access_agent",
    "department": "IT_SUPPORT",
    "reason": "Wiadomość dotyczy problemów IT.",
    "action_type": "CREATE_IT_TICKET"
  },
  "executed_action": {
    "action_type": "CREATE_IT_TICKET",
    "target_department": "IT_SUPPORT",
    "status": "SIMULATED",
    "message": "Utworzono symulowane zgłoszenie do działu IT_SUPPORT."
  }
}
```

### Przykład curl

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/classify' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "Mam problem z logowaniem."
}'
```

---

## `POST /process`

Endpoint do pełnego przetwarzania wiadomości przez prostego agenta.

Ten endpoint:

1. przyjmuje tekst wiadomości,
2. klasyfikuje wiadomość,
3. wybiera agenta,
4. tworzy symulowaną akcję,
5. zapisuje historię w bazie,
6. zwraca pełną odpowiedź.

### Przykładowe zapytanie

```json
{
  "text": "Mam pilny problem z fakturą za ostatni miesiąc."
}
```

### Przykładowa odpowiedź

```json
{
  "category": "FINANCE",
  "priority": "HIGH",
  "summary": "Mam pilny problem z fakturą za ostatni miesiąc.",
  "suggested_action": "Przekazać do działu finansów.",
  "source": "RULE_BASED",
  "route": {
    "agent_name": "finance_invoice_agent",
    "department": "FINANCE",
    "reason": "Wiadomość dotyczy faktury lub płatności.",
    "action_type": "CREATE_FINANCE_TICKET"
  },
  "executed_action": {
    "action_type": "CREATE_FINANCE_TICKET",
    "target_department": "FINANCE",
    "status": "SIMULATED",
    "message": "Symulacja wykonania akcji CREATE_FINANCE_TICKET dla agenta finance_invoice_agent"
  }
}
```

### Przykład curl

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/process' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "Mam pilny problem z fakturą za ostatni miesiąc."
}'
```

---

## `GET /tickets`

Endpoint zwracający historię zgłoszeń z bazy danych.

### Przykładowa odpowiedź

```json
[
  {
    "id": 1,
    "input_text": "Mam pilny problem z fakturą za ostatni miesiąc.",
    "category": "FINANCE",
    "priority": "HIGH",
    "summary": "Mam pilny problem z fakturą za ostatni miesiąc.",
    "suggested_action": "Przekazać do działu finansów.",
    "source": "RULE_BASED",
    "executed_action_type": "CREATE_FINANCE_TICKET",
    "executed_action_status": "SIMULATED",
    "executed_action_message": "Symulacja wykonania akcji CREATE_FINANCE_TICKET dla agenta finance_invoice_agent",
    "created_at": "2026-05-20T11:49:39"
  }
]
```

---

## `GET /stats`

Endpoint zwracający statystyki zgłoszeń.

Domyślnie analizuje ostatnie 30 dni.

Przykład:

```text
GET /stats
```

Można też podać liczbę dni:

```text
GET /stats?days=7
```

Przykładowa odpowiedź:

```json
{
  "count_by_category": {
    "FINANCE": 5,
    "IT_SUPPORT": 3,
    "HR": 2
  },
  "count_by_priority": {
    "HIGH": 6,
    "MEDIUM": 3,
    "LOW": 1
  },
  "count_by_status": {
    "SIMULATED": 10
  },
  "top_agents": {
    "finance_invoice_agent": 5,
    "it_access_agent": 3,
    "hr_leave_agent": 2
  },
  "total_tickets": 10
}
```

Jeśli nie ma zgłoszeń w podanym okresie, endpoint zwróci komunikat:

```json
{
  "message": "Brak zgłoszeń w ostatnich 30 dniach."
}
```

---

## Typy akcji

System obsługuje następujące typy akcji:

```text
CREATE_FINANCE_TICKET
CREATE_IT_TICKET
CREATE_HR_CASE
MARK_AS_LOW_PRIORITY
SEND_TO_GENERAL_QUEUE
ESCALATE_TO_MANAGER
```

Na tym etapie akcje są symulowane, czyli nie tworzą jeszcze realnych ticketów w zewnętrznych systemach.

---

## Statusy akcji

Możliwe statusy akcji:

```text
SIMULATED
COMPLETED
FAILED
```

Aktualnie używany jest głównie:

```text
SIMULATED
```

---

## Baza danych

Projekt obsługuje bazę danych przez SQLAlchemy.

Można korzystać z:

- MySQL,
- SQLite.

Aktualny podział baz:

| Tryb | Baza | Opis |
|---|---|---|
| Normalna aplikacja | MySQL `ai_classifier` | Główna baza historii zgłoszeń |
| Testy | `ai_classifier_test.db` | Osobna baza SQLite tylko do testów |
| Awaria MySQL | `ai_classifier.db` | Awaryjna lokalna baza SQLite |

Przykładowy connection string dla MySQL:

```text
mysql+pymysql://user:password@localhost:3306/ai_classifier
```

Historia zgłoszeń jest zapisywana w bazie i dostępna przez endpoint:

```text
GET /tickets
```

---

## Ważne: fallback SQLite a spójność danych

Jeśli MySQL działa, aplikacja zapisuje historię do MySQL.

Jeśli MySQL jest niedostępny, aplikacja może przejść awaryjnie na lokalną bazę SQLite:

```text
ai_classifier.db
```

Po powrocie MySQL nowe zgłoszenia znowu będą zapisywane do MySQL.

Ważne:

```text
Dane zapisane awaryjnie w ai_classifier.db nie synchronizują się automatycznie z MySQL.
```

To oznacza, że fallback SQLite zapewnia ciągłość działania aplikacji, ale nie zapewnia jeszcze automatycznej synchronizacji danych.

Planowany kolejny etap:

```text
Etap 8 — synchronizacja awaryjnej SQLite do MySQL
```

---

## Plik `.env`

Projekt używa pliku `.env` do przechowywania ustawień lokalnych.

Przykład:

```env
APP_NAME=AI Classifier Backend
APP_VERSION=1.5.0
ENVIRONMENT=development

AI_ENABLED=false
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

DATABASE_URL=mysql+pymysql://user:password@localhost:3306/ai_classifier
```

Jeżeli chcesz używać lokalnej SQLite zamiast MySQL, można ustawić:

```env
DATABASE_URL=sqlite:///./ai_classifier.db
```

Pliku `.env` nie należy dodawać do Gita, ponieważ może zawierać prywatne dane.

W `.gitignore` powinny znajdować się wpisy:

```gitignore
.env
.env.*
*.db
```

---

## Plik `.env.test`

Testy używają osobnej konfiguracji testowej.

Przykład lokalnego pliku `.env.test`:

```env
APP_NAME=AI Classifier Backend
APP_VERSION=1.5.0
ENVIRONMENT=test

AI_ENABLED=false
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

DATABASE_URL=sqlite:///./ai_classifier_test.db
```

Pliku `.env.test` również nie należy dodawać do Gita.

Testy dodatkowo wymuszają ustawienia testowe w `tests/conftest.py`, więc zwykle nie trzeba ręcznie ustawiać zmiennej `ENVIRONMENT`.

---

## Przykładowy plik `.env.example`

Do repozytorium można dodać `.env.example`, ale bez prawdziwych danych dostępowych:

```env
APP_NAME=AI Classifier Backend
APP_VERSION=1.5.0
ENVIRONMENT=development

AI_ENABLED=false
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini

DATABASE_URL=sqlite:///./ai_classifier.db
```

---

## Uruchamianie lokalne bez Dockera

### 1. Utworzenie środowiska wirtualnego

W folderze projektu uruchom:

```bash
python -m venv venv
```

albo:

```powershell
py -3.11 -m venv venv
```

---

### 2. Aktywacja środowiska

Na Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Jeśli PowerShell blokuje aktywację środowiska, można użyć:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

A potem ponownie:

```powershell
.\venv\Scripts\Activate.ps1
```

Można też uruchamiać komendy bez aktywacji środowiska:

```powershell
.\venv\Scripts\python.exe -m pytest
```

---

### 3. Instalacja zależności

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

### 4. Uruchomienie aplikacji

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Po uruchomieniu aplikacja będzie dostępna pod adresem:

```text
http://127.0.0.1:8000
```

Dokumentacja API będzie dostępna pod adresem:

```text
http://127.0.0.1:8000/docs
```

Endpoint zdrowia:

```text
http://127.0.0.1:8000/health
```

---

## Sprawdzenie aktualnie używanej bazy

Najprościej wejść na:

```text
http://127.0.0.1:8000/health
```

Przykład dla MySQL:

```json
{
  "environment": "development",
  "database": "ai_classifier",
  "dialect": "mysql"
}
```

Przykład dla SQLite:

```json
{
  "environment": "development",
  "database": "ai_classifier.db",
  "dialect": "sqlite"
}
```

Przykład dla testów:

```json
{
  "environment": "test",
  "database": "ai_classifier_test.db",
  "dialect": "sqlite"
}
```

---

## Uruchamianie przez Docker

Docker pozwala uruchomić aplikację w kontenerze, czyli w odizolowanym środowisku.

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

### Uruchomienie aplikacji

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

### Zatrzymanie aplikacji

Jeśli aplikacja działa w terminalu, można ją zatrzymać skrótem:

```text
CTRL + C
```

Można też użyć komendy:

```bash
docker compose down
```

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

```powershell
.\venv\Scripts\python.exe -m pytest
```

Nie trzeba ręcznie ustawiać:

```powershell
$env:ENVIRONMENT="test"
```

ponieważ testy same ustawiają środowisko testowe w `tests/conftest.py`.

Testy używają:

```text
sqlite:///./ai_classifier_test.db
```

i nie dotykają MySQL.

Projekt posiada testy sprawdzające między innymi:

- działanie endpointów API,
- klasyfikację regułową,
- obsługę klasyfikacji AI,
- obsługę błędnej odpowiedzi AI,
- routing zgłoszeń do agentów,
- wybór akcji po klasyfikacji,
- symulowane wykonanie akcji,
- zapis historii zgłoszeń,
- pełny proces `/process`,
- statystyki zgłoszeń,
- osobną konfigurację testową.

Aktualny poprawny wynik testów:

```text
47 passed
```

Przykładowy wynik:

```text
tests\test_action_agent.py ......                              [ 12%]
tests\test_action_executor.py ......                           [ 25%]
tests\test_agent_router.py ........                            [ 42%]
tests\test_ai_classifier.py .                                  [ 44%]
tests\test_ai_errors.py .                                      [ 46%]
tests\test_api.py ...                                          [ 53%]
tests\test_classification_and_process.py ........              [ 70%]
tests\test_classification_service.py ....                      [ 78%]
tests\test_classifier.py ....                                  [ 87%]
tests\test_error_handlers.py .                                 [ 89%]
tests\test_health.py .                                         [ 91%]
tests\test_process_api.py .                                    [ 93%]
tests\test_process_service.py .                                [ 95%]
tests\test_prompt_loader.py .                                  [ 97%]
tests\test_ticket_history.py .                                 [100%]

47 passed
```

---

## Tryb AI vs Rule-Based

Tryb AI jest sterowany przez zmienną środowiskową:

```env
AI_ENABLED=true
```

lub:

```env
AI_ENABLED=false
```

Jeśli AI jest wyłączone, aplikacja używa klasyfikacji regułowej.

Jeśli AI jest włączone, aplikacja może korzystać z OpenAI API.

W przypadku braku środków na koncie OpenAI, niepoprawnego klucza API lub przekroczenia limitu może pojawić się błąd 429 `insufficient_quota`.

Do pracy lokalnej i testów można bezpiecznie ustawić:

```env
AI_ENABLED=false
```

---

## Git — bezpieczny workflow

Po zmianach w projekcie warto sprawdzić status:

```bash
git status
```

Dodanie zmian do commita:

```bash
git add app tests README.md .gitignore .env.example
```

Lepiej unikać:

```bash
git add .
```

jeśli w katalogu mogą znajdować się pliki `.env`, `.db` lub inne dane lokalne.

Utworzenie commita:

```bash
git commit -m "Add isolated test configuration with SQLite"
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

## Czego nauczyliśmy się w Etapie 6?

W Etapie 6 dodane zostały statystyki zgłoszeń.

Zrobione zostało:

- dodanie endpointu `GET /stats`,
- liczenie zgłoszeń według kategorii,
- liczenie zgłoszeń według priorytetu,
- liczenie zgłoszeń według statusu wykonanej akcji,
- analiza najczęściej używanych agentów,
- filtrowanie statystyk po liczbie ostatnich dni.

---

## Czego nauczyliśmy się w Etapie 7?

W Etapie 7 projekt został uporządkowany pod kątem środowisk.

Zrobione zostało:

- dodanie osobnej konfiguracji dla testów,
- dodanie `.env.test`,
- automatyczne wymuszanie środowiska testowego w `conftest.py`,
- testowa baza SQLite `ai_classifier_test.db`,
- brak używania MySQL w testach,
- brak zużywania tokenów AI w testach,
- usunięcie ręcznego czyszczenia rekordów testowych z MySQL,
- uporządkowanie fallbacku SQLite,
- ujednolicenie awaryjnej bazy SQLite jako `ai_classifier.db`,
- potwierdzenie działania testów: `47 passed`.

---

## Aktualny status projektu

Projekt posiada:

- działający backend FastAPI,
- endpoint `/`,
- endpoint `/health`,
- endpoint `/classify`,
- endpoint `/process`,
- endpoint `/tickets`,
- endpoint `/stats`,
- klasyfikator regułowy,
- opcjonalny klasyfikator AI,
- routing agentów,
- symulowane akcje,
- zapis historii zgłoszeń,
- statystyki zgłoszeń,
- obsługę SQLite / MySQL,
- fallback SQLite,
- osobną bazę testową,
- logowanie requestów,
- obsługę błędów,
- testy automatyczne,
- Dockerfile,
- docker-compose.yml,
- dokumentację w README.

Aktualny stan testów:

```text
47 passed
```

---

## Etapy rozwoju projektu

### Etap 1 — podstawowy backend FastAPI

Dodano podstawową aplikację FastAPI i pierwszy endpoint testowy.

### Etap 2 — klasyfikacja wiadomości

Dodano klasyfikację tekstu na kategorie biznesowe.

### Etap 3 — zapis historii zgłoszeń

Dodano zapis zgłoszeń do bazy danych.

### Etap 4 — obsługa SQLite / MySQL

Dodano możliwość pracy z różnymi bazami danych przez SQLAlchemy.

### Etap 5 — routing agentów i symulowane akcje

Dodano:

- `RouteDecision`,
- routing agentów,
- `route_message`,
- `/process`,
- `executed_action`,
- zapis historii po klasyfikacji,
- pełniejsze testy.

### Etap 6 — statystyki zgłoszeń

Dodano:

- endpoint `/stats`,
- liczenie zgłoszeń według kategorii,
- liczenie zgłoszeń według priorytetu,
- liczenie zgłoszeń według statusu,
- top agentów.

### Etap 7 — osobna konfiguracja dla testów i aplikacji

Dodano:

- `.env` dla aplikacji,
- `.env.test` dla testów,
- testową SQLite,
- automatyczne ustawianie środowiska testowego,
- izolację testów od MySQL,
- brak zużywania tokenów AI w testach.

---

## Możliwe dalsze kroki

Kolejne etapy mogą obejmować:

- Etap 8: synchronizacja danych z awaryjnej SQLite do MySQL,
- Etap 9: frontend panelu administratora,
- Etap 10: autoryzacja użytkowników,
- Etap 11: prawdziwe integracje z systemami ticketowymi,
- Etap 12: deployment produkcyjny,
- Etap 13: pełniejszy workflow agentowy z AI.

---

## Co pokazuje ten projekt w portfolio?

Projekt pokazuje praktyczne umiejętności:

- tworzenie backendu w FastAPI,
- projektowanie API,
- praca z Pydantic,
- praca z SQLAlchemy,
- obsługa bazy danych,
- obsługa konfiguracji środowisk,
- izolowanie testów od danych produkcyjnych,
- testowanie backendu przez pytest,
- tworzenie logiki agentowej,
- routing zgłoszeń,
- integracja z AI jako opcjonalnym modułem,
- obsługa Docker / Docker Compose,
- przygotowanie projektu do dalszej rozbudowy komercyjnej.

---

## Autor

Projekt portfolio rozwijany jako backend do nauki budowy agentów AI dla firm.

Cel projektu:

```text
nauczyć się tworzyć agentów AI, których można wdrażać komercyjnie w firmach do usprawniania procesów biznesowych
```

## Przykłady przewagi AI nad klasyfikacją regułową

System potrafi rozpoznać kategorię zgłoszenia nawet wtedy, gdy wiadomość nie zawiera oczywistych słów kluczowych.

| Wiadomość | Wynik AI | Dlaczego to ważne |
|---|---|---|
| W systemie widzę inną sumę niż ta, którą powinienem zapłacić. | FINANCE | Brak słów "faktura" lub "przelew", ale sens jest finansowy. |
| Od rana nie mogę dostać się do narzędzia, z którego korzystam w pracy. | IT_SUPPORT | Brak słów "hasło", "login", "VPN", ale chodzi o dostęp do narzędzia. |
| Potrzebuję informacji, jakie dokumenty muszę dostarczyć po powrocie od lekarza. | HR | Brak słów "urlop" lub "kadry", ale sprawa dotyczy dokumentów pracowniczych. |
| Na ostatnim zestawieniu widzę pozycję, której nie powinno tam być. | FINANCE | Model rozumie kontekst rozliczenia mimo braku typowych słów kluczowych. |