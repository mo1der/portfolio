from pathlib import Path

from sqlalchemy import and_, create_engine, inspect, select
from sqlalchemy.orm import Session

from app.core.settings import Settings
from app.models import TicketHistory


PROJECT_ROOT = Path(__file__).resolve().parents[1]

SQLITE_DB_PATH = PROJECT_ROOT / "ai_classifier.db"
SQLITE_URL = f"sqlite:///{SQLITE_DB_PATH}"

MYSQL_SETTINGS = Settings(_env_file=PROJECT_ROOT / ".env")
MYSQL_URL = MYSQL_SETTINGS.database_url


def create_sqlite_engine():
    return create_engine(
        SQLITE_URL,
        connect_args={"check_same_thread": False},
    )


def create_mysql_engine():
    if not MYSQL_URL.startswith("mysql"):
        raise RuntimeError(
            f"DATABASE_URL z .env nie wskazuje na MySQL: {MYSQL_URL}"
        )

    return create_engine(MYSQL_URL)


def sqlite_has_ticket_history_table(sqlite_engine) -> bool:
    inspector = inspect(sqlite_engine)
    return "ticket_history" in inspector.get_table_names()


def get_sqlite_tickets(sqlite_engine):
    with Session(sqlite_engine) as session:
        return session.execute(select(TicketHistory)).scalars().all()


def ticket_exists_in_mysql(ticket, mysql_session: Session) -> bool:
    existing_ticket = mysql_session.execute(
        select(TicketHistory).where(
            and_(
                TicketHistory.input_text == ticket.input_text,
                TicketHistory.category == ticket.category,
                TicketHistory.priority == ticket.priority,
                TicketHistory.summary == ticket.summary,
                TicketHistory.suggested_action == ticket.suggested_action,
                TicketHistory.source == ticket.source,
            )
        )
    ).first()

    return existing_ticket is not None


def copy_ticket_to_mysql(ticket, mysql_session: Session):
    mysql_ticket = TicketHistory(
        input_text=ticket.input_text,
        category=ticket.category,
        priority=ticket.priority,
        summary=ticket.summary,
        suggested_action=ticket.suggested_action,
        source=ticket.source,
        executed_action_type=ticket.executed_action_type,
        executed_action_status=ticket.executed_action_status,
        executed_action_message=ticket.executed_action_message,
        route_agent_name=ticket.route_agent_name,
        route_department=ticket.route_department,
        route_reason=ticket.route_reason,
        route_action_type=ticket.route_action_type,
        created_at=ticket.created_at,
    )

    mysql_session.add(mysql_ticket)


def sync():
    if not SQLITE_DB_PATH.exists():
        print(f"Brak pliku SQLite: {SQLITE_DB_PATH}")
        print("Nie ma danych awaryjnych do synchronizacji.")
        return

    sqlite_engine = create_sqlite_engine()

    if not sqlite_has_ticket_history_table(sqlite_engine):
        print(f"Plik SQLite istnieje, ale nie ma tabeli ticket_history: {SQLITE_DB_PATH}")
        print("Nie ma danych awaryjnych do synchronizacji.")
        return

    sqlite_tickets = get_sqlite_tickets(sqlite_engine)

    if not sqlite_tickets:
        print("Tabela ticket_history w SQLite jest pusta.")
        print("Nie ma danych awaryjnych do synchronizacji.")
        return

    mysql_engine = create_mysql_engine()

    synced_count = 0
    skipped_count = 0

    with Session(mysql_engine) as mysql_session:
        for ticket in sqlite_tickets:
            if ticket_exists_in_mysql(ticket, mysql_session):
                skipped_count += 1
                continue

            copy_ticket_to_mysql(ticket, mysql_session)
            synced_count += 1

        mysql_session.commit()

    print("Synchronizacja zakończona.")
    print(f"Dodano do MySQL: {synced_count}")
    print(f"Pominięto duplikaty: {skipped_count}")


if __name__ == "__main__":
    sync()