# AI Classifier Backend - Etap 1

Prosty backend FastAPI do klasyfikacji zgłoszeń tekstowych.

## Funkcje

- endpoint `GET /`
- endpoint `POST /classify`
- klasyfikacja tekstu do kategorii:
  - `IT_SUPPORT`
  - `FINANCE`
  - `HR`
  - `OTHER`
- priorytety:
  - `LOW`
  - `MEDIUM`
  - `HIGH`
- testy jednostkowe i testy API

## Uruchomienie

```powershell
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload