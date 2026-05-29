# AI Classifier Backend

Backend API do klasyfikowania zgłoszeń tekstowych, rozpoznawania intencji, routingu do odpowiednich agentów, zapisu historii zgłoszeń, zmiany statusów ticketów oraz symulowanego wykonywania akcji biznesowych.

Projekt jest częścią nauki budowania backendów i agentów AI, które mogą być używane w firmach do automatyzacji obsługi zgłoszeń, wiadomości e-mail lub prostych procesów biznesowych.

---

## Aktualny status projektu

Aktualnie projekt jest rozwinięty do:

```text
Etap 15.1 — walidacja przejść statusów zgłoszeń
```

Aktualny wynik testów:

```text
69 passed
```

Projekt posiada już:

- działający backend FastAPI,
- klasyfikację zgłoszeń,
- hybrydową logikę RULE_BASED + AI,
- rozpoznawanie intencji wiadomości,
- routing zgłoszeń do agentów,
- wybór akcji na podstawie kategorii i intencji,
- symulowane wykonanie akcji biznesowych,
- zapis historii zgłoszeń do bazy danych,
- statusy ticketów,
- endpoint do zmiany statusu zgłoszenia,
- walidację poprawnych przejść statusów,
- endpoint historii zgłoszeń,
- endpoint statystyk zgłoszeń,
- endpoint statusu AI,
- endpoint analizy wiadomości e-mail,
- obsługę SQLite / MySQL,
- osobną konfigurację dla testów i normalnego uruchomienia,
- testową bazę SQLite,
- awaryjny fallback do SQLite, gdy MySQL jest niedostępny,
- ręczny endpoint synchronizacji SQLite do MySQL,
- opcjonalny klasyfikator AI z kontrolą kosztów,
- testy automatyczne,
- Dockerfile,
- docker-compose.yml,
- dokumentację techniczną.

---

## Co robi ten projekt?

Aplikacja przyjmuje tekst zgłoszenia i zwraca informację:

- jakiej kategorii dotyczy zgłoszenie,
- jaki ma priorytet,
- jaką ma intencję,
- jakie jest podsumowanie wiadomości,
- jaka akcja jest sugerowana,
- jakie jest źródło klasyfikacji,
- jakim kanałem przyszło zgłoszenie,
- jaki agent powinien obsłużyć sprawę,
- jaka jest domyślna akcja agenta,
- jaka akcja faktycznie została wykonana,
- jaki jest aktualny status ticketu,
- czy zgłoszenie zostało zapisane w historii.

Endpoint `/process` wykonuje pełny proces:

```text
wiadomość użytkownika
→ klasyfikacja kategorii
→ klasyfikacja intencji
→ routing do agenta
→ wybór akcji po category + intent
→ symulowane wykonanie akcji
→ zapis historii w bazie
→ odpowiedź API
```

---

## Aktualna logika AI

System działa hybrydowo:

```text
1. Najpierw działa klasyfikator RULE_BASED.
2. Jeśli RULE_BASED rozpozna kategorię inną niż OTHER, AI nie jest używane.
3. Jeśli RULE_BASED zwróci OTHER, system próbuje użyć OpenAI.
4. Jeśli AI jest wyłączone, limit jest przekroczony, tekst jest za długi albo AI zwróci błąd, system robi fallback do RULE_BASED.
```

To ogranicza zużycie tokenów, ponieważ AI jest używane tylko tam, gdzie reguły nie potrafią dobrze sklasyfikować wiadomości.

---

## Kontrola kosztów AI

Aktualne limity:

```text
AI_MAX_INPUT_CHARS=1200
AI_MAX_OUTPUT_TOKENS=300
AI_DAILY_REQUEST_LIMIT=50
timeout=10.0
```

Endpoint `/ai/status` pokazuje między innymi:

- `ai_enabled`,
- `model`,
- `daily_request_limit`,
- `request_count_today`,
- `remaining_requests_today`,
- `max_input_chars`,
- `max_output_tokens`.

Aktualnie używany model:

```text
gpt-4.1-mini
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
| Mam nietypową sytuację i potrzebuję pomocy. | OTHER |

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
| Mam ogólne pytanie. | LOW / MEDIUM |

---

## Intencje wiadomości

Od Etapu 12 system rozpoznaje intencję wiadomości.

Obsługiwane intencje:

```text
CREATE_TICKET
CHECK_STATUS
UPDATE_DATA
CONTACT_HUMAN
COMPLAINT
THANKS
OTHER
```

Przykłady:

| Wiadomość | Intent |
|---|---|
| Mam problem z fakturą. | CREATE_TICKET |
| Chcę sprawdzić status mojego zgłoszenia z fakturą. | CHECK_STATUS |
| Chcę poprawić dane w zgłoszeniu. | UPDATE_DATA |
| Chcę porozmawiać z konsultantem. | CONTACT_HUMAN / OTHER |
| Chcę złożyć skargę. | COMPLAINT |
| Dziękuję za pomoc. | THANKS |

---

## Kanały źródłowe zgłoszeń

System obsługuje źródło wiadomości:

```text
CHAT
EMAIL
FORM
API
MANUAL
```

Przykładowe zapytanie:

```json
{
  "text": "Mam problem z fakturą.",
  "source_channel": "CHAT"
}
```

---

## Statusy ticketów

Od Etapu 14 system zapisuje status zgłoszenia.

Obsługiwane statusy:

```text
NEW
IN_PROGRESS
WAITING_FOR_USER
RESOLVED
CLOSED
```

Nowo utworzone zgłoszenie przez `/process` otrzymuje domyślnie:

```text
ticket_status = NEW
```

---

## Walidacja przejść statusów

Od Etapu 15.1 system blokuje nielogiczne przejścia statusów.

Dozwolone przejścia:

```text
NEW → IN_PROGRESS
IN_PROGRESS → WAITING_FOR_USER
IN_PROGRESS → RESOLVED
WAITING_FOR_USER → IN_PROGRESS
WAITING_FOR_USER → RESOLVED
RESOLVED → CLOSED
ten sam status → ten sam status
```

Przykłady dozwolonych zmian:

```text
NEW → IN_PROGRESS
IN_PROGRESS → IN_PROGRESS
IN_PROGRESS → WAITING_FOR_USER
WAITING_FOR_USER → RESOLVED
RESOLVED → CLOSED
CLOSED → CLOSED
```

Przykłady blokowanych zmian:

```text
NEW → CLOSED
CLOSED → NEW
RESOLVED → IN_PROGRESS
```

Przykład błędnej odpowiedzi:

```json
{
  "detail": "Invalid ticket status transition: CLOSED -> NEW"
}
```

---

## Agenci i routing

System kieruje zgłoszenia do odpowiednich agentów.

| Kategoria | Przykładowe słowa kluczowe | Agent | Domyślna akcja agenta |
|---|---|---|---|
| FINANCE | faktur, płatność, przelew, rachunek | finance_invoice_agent | CREATE_FINANCE_TICKET |
| IT_SUPPORT | hasł, logowan, zalog, komputer, drukarka, vpn | it_access_agent | CREATE_IT_SUPPORT_TICKET |
| HR | urlop, zwoln, wynagrodzen, wniosek | hr_leave_agent | CREATE_HR_TICKET |
| OTHER | brak dopasowania | general_agent | SEND_TO_GENERAL_QUEUE |

Reguły używają fragmentów słów, dzięki czemu obsługują odmiany, np.:

```text
faktur → faktura, faktury, fakturą
logowan / zalog → logowanie, zalogować, zalogowaniem
zwoln → zwolnienie, zwolnienia
```

---

## Ważne rozróżnienie: route vs executed_action

W projekcie są dwa różne poziomy decyzji.

### `route`

Odpowiada na pytanie:

```text
Kto / jaki dział / jaki agent powinien obsłużyć sprawę?
```

Przykład:

```json
"route": {
  "agent_name": "finance_invoice_agent",
  "department": "FINANCE",
  "reason": "Wiadomość dotyczy faktury, płatności lub rozliczeń.",
  "default_action_type": "CREATE_FINANCE_TICKET"
}
```

### `route.default_action_type`

To domyślna akcja agenta wynikająca z routingu.

Przykład:

```text
FINANCE → CREATE_FINANCE_TICKET
```

### `executed_action.action_type`

To faktycznie wykonana akcja wynikająca z kategorii i intencji.

Przykład:

```text
category = FINANCE
intent = CHECK_STATUS
executed_action.action_type = CHECK_FINANCE_STATUS
```

Dzięki temu system może rozróżnić:

```text
zgłoszenie finansowe → agent finansowy
ale intencja sprawdzenia statusu → akcja CHECK_FINANCE_STATUS
```

---

## Typy akcji

System obsługuje między innymi:

```text
CREATE_FINANCE_TICKET
CREATE_IT_SUPPORT_TICKET
CREATE_HR_TICKET
CREATE_OTHER_TICKET

MARK_AS_LOW_PRIORITY
SEND_TO_GENERAL_QUEUE
ESCALATE_TO_MANAGER

CHECK_FINANCE_STATUS
CHECK_IT_SUPPORT_STATUS
CHECK_HR_STATUS
CHECK_OTHER_STATUS

UPDATE_FINANCE_DATA
UPDATE_IT_SUPPORT_DATA
UPDATE_HR_DATA
UPDATE_OTHER_DATA

ESCALATE_FINANCE_COMPLAINT
ESCALATE_IT_SUPPORT_COMPLAINT
ESCALATE_HR_COMPLAINT
ESCALATE_OTHER_COMPLAINT

ROUTE_TO_HUMAN
NO_ACTION
```

Na tym etapie akcje są symulowane, czyli nie tworzą jeszcze realnych ticketów w zewnętrznych systemach.

---

## Statusy wykonania akcji

Możliwe statusy wykonania akcji:

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

## Endpointy API

Aktualne endpointy:

```text
GET    /
GET    /health
GET    /ai/status
POST   /classify
POST   /process
POST   /emails/analyze
GET    /tickets
PATCH  /tickets/{ticket_id}/status
GET    /stats
POST   /sync/sqlite-to-mysql
```

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
  "ai_enabled": true,
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

## `GET /ai/status`

Endpoint pokazujący aktualny status konfiguracji AI i limitów.

Przykładowa odpowiedź:

```json
{
  "ai_enabled": true,
  "model": "gpt-4.1-mini",
  "daily_request_limit": 50,
  "request_count_today": 3,
  "remaining_requests_today": 47,
  "max_input_chars": 1200,
  "max_output_tokens": 300
}
```

---

## `POST /classify`

Endpoint do klasyfikowania tekstu i wyboru agenta.

W aktualnej wersji zwraca `ProcessResponse`, zapisuje historię zgłoszenia i zawiera routing oraz wykonaną akcję.

### Przykładowe zapytanie

```json
{
  "text": "Mam problem z logowaniem.",
  "source_channel": "CHAT"
}
```

### Przykładowa odpowiedź

```json
{
  "category": "IT_SUPPORT",
  "priority": "HIGH",
  "intent": "CREATE_TICKET",
  "summary": "Mam problem z logowaniem.",
  "suggested_action": "Przekazać do działu IT.",
  "source": "RULE_BASED",
  "source_channel": "CHAT",
  "route": {
    "agent_name": "it_access_agent",
    "department": "IT_SUPPORT",
    "reason": "Wiadomość dotyczy problemów IT, dostępu, logowania lub sprzętu.",
    "default_action_type": "CREATE_IT_SUPPORT_TICKET"
  },
  "executed_action": {
    "action_type": "CREATE_IT_SUPPORT_TICKET",
    "target_department": "IT_SUPPORT",
    "status": "SIMULATED",
    "message": "Utworzono symulowane zgłoszenie do działu IT."
  },
  "ticket_status": "NEW"
}
```

### Przykład curl

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/classify' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "Mam problem z logowaniem.",
  "source_channel": "CHAT"
}'
```

---

## `POST /process`

Endpoint do pełnego przetwarzania wiadomości przez prostego agenta.

Ten endpoint:

1. przyjmuje tekst wiadomości,
2. klasyfikuje wiadomość,
3. rozpoznaje intencję,
4. wybiera agenta,
5. dobiera akcję na podstawie kategorii i intencji,
6. tworzy symulowaną akcję,
7. zapisuje historię w bazie,
8. zwraca pełną odpowiedź.

### Przykładowe zapytanie

```json
{
  "text": "Chcę sprawdzić status mojego zgłoszenia z fakturą.",
  "source_channel": "API"
}
```

### Przykładowa odpowiedź

```json
{
  "category": "FINANCE",
  "priority": "HIGH",
  "intent": "CHECK_STATUS",
  "summary": "Chcę sprawdzić status mojego zgłoszenia z fakturą.",
  "suggested_action": "Przekazać do działu finansów.",
  "source": "RULE_BASED",
  "source_channel": "API",
  "route": {
    "agent_name": "finance_invoice_agent",
    "department": "FINANCE",
    "reason": "Wiadomość dotyczy faktury, płatności lub rozliczeń.",
    "default_action_type": "CREATE_FINANCE_TICKET"
  },
  "executed_action": {
    "action_type": "CHECK_FINANCE_STATUS",
    "target_department": "FINANCE",
    "status": "SIMULATED",
    "message": "Sprawdzono symulowany status zgłoszenia finansowego."
  },
  "ticket_status": "NEW"
}
```

### Przykład curl

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/process' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "Chcę sprawdzić status mojego zgłoszenia z fakturą.",
  "source_channel": "API"
}'
```

---

## `POST /emails/analyze`

Endpoint do analizy wiadomości e-mail.

Przyjmuje dane e-maila, buduje z nich tekst, klasyfikuje go i zapisuje jako zgłoszenie z `source_channel = EMAIL`.

### Przykładowe zapytanie

```json
{
  "from_email": "klient@example.com",
  "subject": "Problem z fakturą",
  "body": "Dzień dobry, widzę nieprawidłową kwotę na fakturze.",
  "received_at": "2026-05-29T10:00:00"
}
```

### Przykładowa odpowiedź

```json
{
  "category": "FINANCE",
  "priority": "HIGH",
  "intent": "CREATE_TICKET",
  "summary": "Problem z fakturą",
  "suggested_action": "Przekazać do działu finansów.",
  "source": "RULE_BASED",
  "source_channel": "EMAIL",
  "route": {
    "agent_name": "finance_invoice_agent",
    "department": "FINANCE",
    "reason": "Wiadomość dotyczy faktury, płatności lub rozliczeń.",
    "default_action_type": "CREATE_FINANCE_TICKET"
  },
  "executed_action": {
    "action_type": "CREATE_FINANCE_TICKET",
    "target_department": "FINANCE",
    "status": "SIMULATED",
    "message": "Utworzono symulowane zgłoszenie do działu finansów."
  },
  "ticket_status": "NEW"
}
```

---

## `GET /tickets`

Endpoint zwracający historię zgłoszeń z bazy danych.

W odpowiedzi pojawia się między innymi:

```text
intent
ticket_status
source_channel
route_default_action_type
executed_action_type
```

Ważne rozróżnienie:

```text
route_default_action_type = domyślna akcja agenta
executed_action_type = faktycznie wykonana akcja
```

### Przykładowa odpowiedź

```json
[
  {
    "id": 35,
    "input_text": "Chcę porozmawiać z kimś o mojej sprawie, ale nie wiem do jakiego działu to należy.",
    "source_channel": "API",
    "category": "OTHER",
    "priority": "MEDIUM",
    "intent": "OTHER",
    "ticket_status": "IN_PROGRESS",
    "summary": "Użytkownik potrzebuje pomocy w określeniu odpowiedniego działu do swojej sprawy.",
    "suggested_action": "Skontaktować użytkownika z działem obsługi klienta lub doradcą, który pomoże skierować sprawę do właściwego działu.",
    "source": "AI",
    "executed_action_type": "SEND_TO_GENERAL_QUEUE",
    "executed_action_status": "SIMULATED",
    "executed_action_message": "Sprawa została przekazana do kolejki ogólnej.",
    "route_agent_name": "general_agent",
    "route_department": "OTHER",
    "route_reason": "Brak dopasowania do reguł. Kierowane do agenta ogólnego.",
    "route_default_action_type": "SEND_TO_GENERAL_QUEUE",
    "created_at": "2026-05-29T09:26:54"
  }
]
```

---

## `PATCH /tickets/{ticket_id}/status`

Endpoint do zmiany statusu istniejącego zgłoszenia.

### Przykładowe zapytanie

```json
{
  "ticket_status": "IN_PROGRESS"
}
```

### Przykładowa odpowiedź

```json
{
  "id": 30,
  "input_text": "Chcę porozmawiać z konsultantem.",
  "source_channel": "API",
  "category": "OTHER",
  "priority": "MEDIUM",
  "intent": "OTHER",
  "ticket_status": "CLOSED",
  "summary": "Użytkownik chce porozmawiać z konsultantem.",
  "suggested_action": "Skierować użytkownika do dostępnego konsultanta.",
  "source": "AI",
  "executed_action_type": "ROUTE_TO_HUMAN",
  "executed_action_status": "SIMULATED",
  "executed_action_message": "Sprawa została przekazana do obsługi przez człowieka.",
  "route_agent_name": "general_agent",
  "route_department": "OTHER",
  "route_reason": "Brak dopasowania do reguł. Kierowane do agenta ogólnego.",
  "route_default_action_type": "SEND_TO_GENERAL_QUEUE",
  "created_at": "2026-05-29T07:56:52"
}
```

### Przykład błędnego przejścia

Zapytanie:

```json
{
  "ticket_status": "NEW"
}
```

Dla zgłoszenia o statusie `CLOSED` zwróci:

```json
{
  "detail": "Invalid ticket status transition: CLOSED -> NEW"
}
```

### Przykład curl

```bash
curl -X 'PATCH' \
  'http://127.0.0.1:8000/tickets/32/status' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "ticket_status": "NEW"
}'
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

## `POST /sync/sqlite-to-mysql`

Endpoint do ręcznej synchronizacji danych z awaryjnej SQLite do MySQL.

Używany po sytuacji awaryjnej:

```text
MySQL nie działał
→ aplikacja zapisała zgłoszenia do SQLite
→ MySQL wrócił
→ uruchamiamy ręczną synchronizację
```

Przykładowa odpowiedź:

```json
{
  "status": "completed",
  "message": "Synchronizacja została uruchomiona. Szczegóły sprawdź w logach serwera."
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
- Pandas
- Pytest
- OpenAI SDK
- Docker
- Docker Compose

---

## Struktura projektu

Przykładowa aktualna struktura katalogów:

```text
etap1/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── classifier.py
│   ├── ai_classifier.py
│   ├── ai_usage_limiter.py
│   ├── agent_router.py
│   ├── action_agent.py
│   ├── action_router.py
│   ├── action_executor.py
│   ├── intent_classifier.py
│   ├── ticket_status_rules.py
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
├── scripts/
│   └── sync_sqlite_to_mysql.py
│
├── tests/
│   ├── conftest.py
│   ├── test_action_agent.py
│   ├── test_action_executor.py
│   ├── test_action_router.py
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
│   ├── test_ticket_history.py
│   └── test_ticket_status.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
├── restart_server.ps1
└── README.md
```

---

## Diagram architektury

```text
Użytkownik / system zewnętrzny / e-mail
   |
   v
FastAPI Backend
   |
   |-- GET /
   |       |
   |       v
   |   Prosty test działania aplikacji
   |
   |-- GET /health
   |       |
   |       v
   |   Status aplikacji + informacja o bazie
   |
   |-- GET /ai/status
   |       |
   |       v
   |   Status AI + limity użycia
   |
   |-- POST /classify
   |       |
   |       v
   |   Klasyfikacja + routing + zapis historii
   |
   |-- POST /process
   |       |
   |       v
   |   Rule-Based / AI
   |       |
   |       v
   |   Intent Classifier
   |       |
   |       v
   |   Agent Router
   |       |
   |       v
   |   Action Router
   |       |
   |       v
   |   Action Executor
   |       |
   |       v
   |   Zapis historii w bazie
   |
   |-- POST /emails/analyze
   |       |
   |       v
   |   Analiza wiadomości e-mail
   |
   |-- GET /tickets
   |       |
   |       v
   |   Lista zapisanych zgłoszeń
   |
   |-- PATCH /tickets/{ticket_id}/status
   |       |
   |       v
   |   Walidacja przejścia statusu
   |       |
   |       v
   |   Aktualizacja ticket_status
   |
   |-- GET /stats
   |       |
   |       v
   |   Statystyki zgłoszeń
   |
   |-- POST /sync/sqlite-to-mysql
           |
           v
       Ręczna synchronizacja awaryjnej SQLite do MySQL
```

---

## Najważniejsze komponenty

### `app/main.py`

Główny plik aplikacji FastAPI.

Zawiera endpointy:

- `GET /`
- `GET /health`
- `GET /ai/status`
- `POST /classify`
- `POST /process`
- `POST /emails/analyze`
- `GET /tickets`
- `PATCH /tickets/{ticket_id}/status`
- `GET /stats`
- `POST /sync/sqlite-to-mysql`

---

### `app/core/settings.py`

Centralna konfiguracja aplikacji.

Odpowiada za wczytywanie ustawień z plików środowiskowych:

- `.env` — normalne uruchomienie aplikacji,
- `.env.test` — środowisko testowe.

Testy dodatkowo wymuszają tryb testowy w `tests/conftest.py`.

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

---

### `app/ai_classifier.py`

Opcjonalny klasyfikator AI oparty o OpenAI API.

W obecnej logice AI jest używane tylko wtedy, gdy klasyfikator regułowy zwróci kategorię `OTHER`.

---

### `app/ai_usage_limiter.py`

Odpowiada za dzienny limit użycia AI.

Pilnuje, aby liczba zapytań do AI nie przekroczyła ustawienia:

```env
AI_DAILY_REQUEST_LIMIT=50
```

---

### `app/intent_classifier.py`

Klasyfikator intencji.

Rozpoznaje, czy użytkownik chce:

- utworzyć zgłoszenie,
- sprawdzić status,
- zaktualizować dane,
- skontaktować się z człowiekiem,
- złożyć skargę,
- podziękować,
- albo wykonać inną czynność.

---

### `app/action_router.py`

Wybiera faktyczną akcję na podstawie:

```text
category + intent
```

Przykład:

```text
FINANCE + CHECK_STATUS → CHECK_FINANCE_STATUS
IT_SUPPORT + UPDATE_DATA → UPDATE_IT_SUPPORT_DATA
HR + COMPLAINT → ESCALATE_HR_COMPLAINT
```

---

### `app/action_executor.py`

Symuluje wykonanie akcji biznesowej.

Zwraca między innymi:

- `action_type`,
- `target_department`,
- `status`,
- `message`.

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

### `app/ticket_status_rules.py`

Zawiera reguły przejść statusów ticketów.

Pilnuje, żeby nie dało się wykonać np.:

```text
CLOSED → NEW
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
- `TicketStatusUpdateRequest`
- `EmailAnalyzeRequest`

---

### `app/repositories.py`

Odpowiada za zapis, odczyt i aktualizację historii zgłoszeń z bazy danych.

Zawiera między innymi:

- `save_ticket_history`,
- `get_ticket_history`,
- `get_ticket_by_id`,
- `update_ticket_status`.

---

### `app/models.py`

Zawiera modele SQLAlchemy, czyli opis tabel w bazie danych.

Tabela `ticket_history` przechowuje między innymi:

- treść zgłoszenia,
- kategorię,
- priorytet,
- intencję,
- status ticketu,
- dane routingu,
- dane wykonanej akcji,
- datę utworzenia.

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

Dane zapisane awaryjnie w SQLite można ręcznie zsynchronizować endpointem:

```text
POST /sync/sqlite-to-mysql
```

---

## Plik `.env`

Projekt używa pliku `.env` do przechowywania ustawień lokalnych.

Przykład:

```env
APP_NAME=AI Classifier Backend
APP_VERSION=1.5.0
ENVIRONMENT=development

AI_ENABLED=true
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini

AI_MAX_INPUT_CHARS=1200
AI_MAX_OUTPUT_TOKENS=300
AI_DAILY_REQUEST_LIMIT=50

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
OPENAI_MODEL=gpt-4.1-mini

AI_MAX_INPUT_CHARS=1200
AI_MAX_OUTPUT_TOKENS=300
AI_DAILY_REQUEST_LIMIT=50

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
OPENAI_MODEL=gpt-4.1-mini

AI_MAX_INPUT_CHARS=1200
AI_MAX_OUTPUT_TOKENS=300
AI_DAILY_REQUEST_LIMIT=50

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

albo przez przygotowany skrypt:

```powershell
.\restart_server.ps1
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
- wybór akcji po kategorii i intencji,
- symulowane wykonanie akcji,
- zapis historii zgłoszeń,
- pełny proces `/process`,
- analizę wiadomości e-mail,
- statystyki zgłoszeń,
- osobną konfigurację testową,
- endpoint `/ai/status`,
- aktualizację statusu ticketu,
- walidację przejść statusów.

Aktualny poprawny wynik testów:

```text
69 passed
```

Przykładowy wynik:

```text
tests\test_action_agent.py ......                              [  8%]
tests\test_action_executor.py ...........                      [ 24%]
tests\test_action_router.py ...........                        [ 40%]
tests\test_agent_router.py ........                            [ 52%]
tests\test_ai_classifier.py .                                  [ 53%]
tests\test_ai_errors.py .                                      [ 55%]
tests\test_api.py ...                                          [ 59%]
tests\test_classification_and_process.py ........              [ 71%]
tests\test_classification_service.py ....                      [ 76%]
tests\test_classifier.py ....                                  [ 82%]
tests\test_error_handlers.py .                                 [ 84%]
tests\test_health.py .                                         [ 85%]
tests\test_process_api.py .                                    [ 86%]
tests\test_process_service.py .                                [ 88%]
tests\test_prompt_loader.py .                                  [ 89%]
tests\test_ticket_history.py .                                 [ 91%]
tests\test_ticket_status.py ......                             [100%]

69 passed
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

Utworzenie commita po obecnym etapie:

```bash
git commit -m "Add ticket status workflow validation"
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

## Historia etapów rozwoju projektu

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

### Etap 8 — synchronizacja awaryjnej SQLite do MySQL

Dodano ręczny mechanizm synchronizacji danych zapisanych awaryjnie w SQLite do MySQL.

### Etap 9–11 — rozwój struktury projektu i przygotowanie pod dalszą automatyzację

Rozwijano strukturę aplikacji, testy, obsługę błędów, logowanie i konfigurację.

### Etap 12 — klasyfikacja intencji

Dodano:

- `Intent`,
- `app/intent_classifier.py`,
- zwracanie intencji w odpowiedzi,
- zapis intencji w `ticket_history`,
- pokazywanie intencji w `/tickets`.

### Etap 13 — wybór akcji po kategorii i intencji

Dodano:

- `app/action_router.py`,
- `route_action(category, intent)`,
- akcje zależne od kategorii i intencji,
- użycie `category + intent` w `/process`.

### Etap 13.1 — rozdzielenie route default action i executed action

Zmieniono znaczenie pól:

```text
route.default_action_type = domyślna akcja agenta
executed_action.action_type = faktycznie wykonana akcja
```

Dzięki temu system rozróżnia routing od wykonanej akcji.

### Etap 14 — status ticketu

Dodano:

- `TicketStatus`,
- `ticket_status = NEW`,
- kolumnę `ticket_status` w bazie,
- zwracanie statusu w odpowiedziach,
- pokazywanie statusu w `/tickets`.

### Etap 15 — endpoint zmiany statusu

Dodano:

```text
PATCH /tickets/{ticket_id}/status
```

Endpoint pozwala zmieniać status istniejącego zgłoszenia.

### Etap 15.1 — walidacja przejść statusów

Dodano:

- `app/ticket_status_rules.py`,
- sprawdzanie dozwolonych przejść,
- blokowanie nielogicznych zmian,
- testy statusów,
- dokumentację błędów 400 / 404 / 422 w Swaggerze.

---

## Możliwe dalsze kroki

Kolejne etapy mogą obejmować:

- Etap 16: historia zmian statusów ticketów,
- Etap 17: przypisywanie ticketów do użytkownika / konsultanta,
- Etap 18: komentarze do zgłoszeń,
- Etap 19: filtrowanie `/tickets` po statusie, kategorii, intencji i kanale,
- Etap 20: panel administratora,
- Etap 21: autoryzacja użytkowników,
- Etap 22: prawdziwe integracje z systemami ticketowymi,
- Etap 23: deployment produkcyjny,
- Etap 24: pełniejszy workflow agentowy z AI.

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
- rozpoznawanie intencji,
- wybór akcji biznesowej,
- obsługa statusów ticketów,
- walidacja workflow,
- integracja z AI jako opcjonalnym modułem,
- kontrola kosztów AI,
- obsługa Docker / Docker Compose,
- przygotowanie projektu do dalszej rozbudowy komercyjnej.

---

## Autor

Projekt portfolio rozwijany jako backend do nauki budowy agentów AI dla firm.

Cel projektu:

```text
nauczyć się tworzyć agentów AI, których można wdrażać komercyjnie w firmach do usprawniania procesów biznesowych
```

---

## Przykłady przewagi AI nad klasyfikacją regułową

System potrafi rozpoznać kategorię zgłoszenia nawet wtedy, gdy wiadomość nie zawiera oczywistych słów kluczowych.

| Wiadomość | Wynik AI | Dlaczego to ważne |
|---|---|---|
| W systemie widzę inną sumę niż ta, którą powinienem zapłacić. | FINANCE | Brak słów „faktura” lub „przelew”, ale sens jest finansowy. |
| Od rana nie mogę dostać się do narzędzia, z którego korzystam w pracy. | IT_SUPPORT | Brak słów „hasło”, „login”, „VPN”, ale chodzi o dostęp do narzędzia. |
| Potrzebuję informacji, jakie dokumenty muszę dostarczyć po powrocie od lekarza. | HR | Brak słów „urlop” lub „kadry”, ale sprawa dotyczy dokumentów pracowniczych. |
| Na ostatnim zestawieniu widzę pozycję, której nie powinno tam być. | FINANCE | Model rozumie kontekst rozliczenia mimo braku typowych słów kluczowych. |
