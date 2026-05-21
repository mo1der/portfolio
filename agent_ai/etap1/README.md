# AI Classifier Backend

Backend API do klasyfikowania zgłoszeń tekstowych, routingu do odpowiednich agentów oraz symulowanego wykonywania akcji biznesowych.

Projekt jest częścią nauki budowania backendów i agentów AI, które mogą być używane w firmach do automatyzacji obsługi zgłoszeń, wiadomości lub prostych procesów biznesowych.

---

## Aktualny status projektu

Aktualnie ukończony jest:

```text
Etap 5 — Rozbudowa logiki agentów i routingu zgłoszeń
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
- obsługę SQLite / MySQL,
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
- do jakiego agenta zgłoszenie powinno trafić.

Dodatkowo endpoint `/process` wykonuje pełny proces:

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

## Agenci i routing

W Etapie 5 dodany został routing zgłoszeń do konkretnych agentów.

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
- SQLAlchemy
- SQLite / MySQL
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
│   ├── middleware.py
│   ├── error_handlers.py
│   ├── exceptions.py
│   ├── logger.py
│   ├── prompt_loader.py
│   └── core/
│       └── settings.py
│
├── tests/
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

Poniżej przykładowy przepływ danych w backendzie:

```text
Użytkownik
   |
   v
FastAPI Backend
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
   |   RouteDecision
   |       |
   |       v
   |   Zapis historii w bazie
   |
   |-- POST /process
           |
           v
       Rule-based classifier / AI classifier
           |
           v
       Agent Router
           |
           v
       Action Executor
           |
           v
       executed_action
           |
           v
       Zapis historii w bazie
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

Może być użyty zamiast klasyfikatora regułowego.

W `main.py` można przełączyć tryb:

```python
USE_AI = False
```

lub:

```python
USE_AI = True
```

---

### `app/agent_router.py`

Wybiera konkretnego agenta na podstawie kategorii i treści zgłoszenia.

Przykład:

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

Pokazuje status aplikacji, konfigurację i używaną bazę danych.

Przykładowa odpowiedź:

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

- SQLite
- MySQL

Przykładowy connection string dla MySQL:

```text
mysql+pymysql://mo1der:sqlmo1der@localhost:3306/ai_classifier
```

Historia zgłoszeń jest zapisywana w bazie i dostępna przez endpoint:

```text
GET /tickets
```

---

## Plik `.env`

Projekt może używać pliku `.env` do przechowywania ustawień lokalnych.

Przykład:

```env
APP_NAME=AI Classifier Backend
APP_VERSION=1.5.0
ENVIRONMENT=development
AI_ENABLED=false

DATABASE_URL=mysql+pymysql://mo1der:sqlmo1der@localhost:3306/ai_classifier

OPENAI_API_KEY=your_api_key_here
```

Jeżeli używasz SQLite, można ustawić np.:

```env
DATABASE_URL=sqlite:///./tickets.db
```

Pliku `.env` nie należy dodawać do Gita, ponieważ może zawierać prywatne dane.

Dlatego w `.gitignore` powinien znajdować się wpis:

```text
.env
```

---

## Przykładowy plik `.env.example`

```env
APP_NAME=AI Classifier Backend
APP_VERSION=1.5.0
ENVIRONMENT=development
AI_ENABLED=false
DATABASE_URL=sqlite:///./tickets.db
OPENAI_API_KEY=
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

Projekt posiada testy sprawdzające między innymi:

- działanie endpointów API,
- klasyfikację regułową,
- obsługę klasyfikacji AI,
- obsługę błędnej odpowiedzi AI,
- routing zgłoszeń do agentów,
- wybór akcji po klasyfikacji,
- symulowane wykonanie akcji,
- zapis historii zgłoszeń,
- pełny proces `/process`.

Aktualny poprawny wynik testów:

```text
47 passed in 5.29s
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

47 passed in 5.29s
```

---

## Tryb AI vs Rule-Based

Aktualnie domyślnie działa tryb rule-based:

```python
USE_AI = False
```

Aby włączyć klasyfikację AI:

```python
USE_AI = True
```

Wtedy aplikacja może korzystać z `ai_classifier.py`.

W przypadku błędu AI, braku klucza API lub braku środków na API można wrócić do stabilnego trybu rule-based.

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
git commit -m "Complete stage 5 agent routing logic"
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

## Czego nauczyliśmy się w Etapie 5?

W Etapie 5 projekt został rozbudowany z prostego klasyfikatora do bardziej agentowego backendu.

Zrobione zostało:

- dodanie modelu `RouteDecision`,
- dodanie pola `route` w odpowiedziach API,
- rozbudowanie `agent_router.py`,
- routing zgłoszeń do agentów,
- rozpoznawanie odmian słów przez fragmenty,
- rozbudowanie `/classify`,
- rozbudowanie `/process`,
- symulowane wykonanie akcji `executed_action`,
- zapis historii zgłoszeń po klasyfikacji,
- poprawienie i rozszerzenie testów,
- doprowadzenie projektu do stanu `47 passed`.

---

## Aktualny status projektu

Projekt posiada:

- działający backend FastAPI,
- endpoint `/`,
- endpoint `/health`,
- endpoint `/classify`,
- endpoint `/process`,
- endpoint `/tickets`,
- klasyfikator regułowy,
- opcjonalny klasyfikator AI,
- routing agentów,
- symulowane akcje,
- zapis historii zgłoszeń,
- obsługę SQLite / MySQL,
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

### Etap 1

Podstawowy backend FastAPI.

### Etap 2

Dodanie klasyfikacji wiadomości.

### Etap 3

Zapis historii zgłoszeń do bazy danych.

### Etap 4

Obsługa różnych baz danych, SQLite / MySQL.

### Etap 5

Rozbudowa logiki agentów i routingu zgłoszeń.

Dodano:

- `RouteDecision`,
- routing agentów,
- `route_message`,
- `/process`,
- `executed_action`,
- zapis historii po klasyfikacji,
- pełniejsze testy.

---

## Co pokazuje ten projekt w portfolio?

Projekt pokazuje praktyczne umiejętności:

- tworzenie backendu w FastAPI,
- projektowanie API,
- praca z Pydantic,
- praca z SQLAlchemy,
- obsługa bazy danych,
- testowanie backendu przez pytest,
- tworzenie logiki agentowej,
- routing zgłoszeń,
- integracja z AI jako opcjonalnym modułem,
- obsługa Docker / Docker Compose,
- przygotowanie projektu do dalszej rozbudowy komercyjnej.

---

## Możliwe dalsze kroki

Kolejne etapy mogą obejmować:

- Etap 6: statystyki i dashboard zgłoszeń,
- Etap 7: prawdziwe integracje z systemami ticketowymi,
- Etap 8: frontend panelu administratora,
- Etap 9: autoryzacja użytkowników,
- Etap 10: deployment produkcyjny,
- Etap 11: pełna integracja z AI Agent workflow.

---

## Autor

Projekt portfolio rozwijany jako backend do nauki budowy agentów AI dla firm.

Cel projektu:

```text
nauczyć się tworzyć agentów AI, których można wdrażać komercyjnie w firmach do usprawniania procesów biznesowych
```
