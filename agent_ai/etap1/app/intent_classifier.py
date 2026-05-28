from app.schemas import Intent


def classify_intent(text: str) -> Intent:
    normalized_text = text.lower()

    if any(phrase in normalized_text for phrase in [
        "status",
        "sprawdź status",
        "sprawdz status",
        "sprawdzić status",
        "sprawdzic status",
        "co z moim zgłoszeniem",
        "co z moim zgloszeniem",
        "na jakim etapie",
        "czy wiadomo coś",
        "czy wiadomo cos",
        "jaki jest status",
    ]):
        return Intent.CHECK_STATUS

    if any(phrase in normalized_text for phrase in [
        "zmienić",
        "zmienic",
        "poprawić",
        "poprawic",
        "zaktualizować",
        "zaktualizowac",
        "aktualizacja",
        "uzupełnić",
        "uzupelnic",
        "zmiana danych",
        "popraw dane",
        "zmienić dane",
        "zmienic dane",
    ]):
        return Intent.UPDATE_DATA

    if any(phrase in normalized_text for phrase in [
        "człowiekiem",
        "czlowiekiem",
        "konsultant",
        "pracownik",
        "kontakt z człowiekiem",
        "kontakt z czlowiekiem",
        "proszę o kontakt",
        "prosze o kontakt",
        "zadzwońcie",
        "zadzwoncie",
        "oddzwońcie",
        "oddzwoncie",
    ]):
        return Intent.CONTACT_HUMAN

    if any(phrase in normalized_text for phrase in [
        "skarga",
        "reklamacja",
        "jestem niezadowolony",
        "jestem niezadowolona",
        "nie jestem zadowolony",
        "nie jestem zadowolona",
        "to niedopuszczalne",
        "fatalnie",
        "źle obsłużony",
        "zle obsluzony",
        "tragiczna obsługa",
        "tragiczna obsluga",
    ]):
        return Intent.COMPLAINT

    if any(phrase in normalized_text for phrase in [
        "dziękuję",
        "dziekuje",
        "dzięki",
        "dzieki",
        "wszystko działa",
        "wszystko dziala",
        "problem rozwiązany",
        "problem rozwiazany",
        "już działa",
        "juz dziala",
        "ok działa",
        "ok dziala",
    ]):
        return Intent.THANKS

    if any(phrase in normalized_text for phrase in [
        "problem",
        "nie działa",
        "nie dziala",
        "błąd",
        "blad",
        "awaria",
        "pilne",
        "pilny",
        "faktura",
        "logowanie",
        "urlop",
        "konto",
        "hasło",
        "haslo",
        "nie mogę",
        "nie moge",
        "brak dostępu",
        "brak dostepu",
    ]):
        return Intent.CREATE_TICKET

    return Intent.OTHER