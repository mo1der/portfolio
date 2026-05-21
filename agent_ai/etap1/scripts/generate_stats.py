import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy
from datetime import datetime, timedelta

# -----------------------
# 1. Wczytanie zmiennych środowiskowych
# -----------------------
load_dotenv()
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("Nie znaleziono zmiennej DATABASE_URL w .env")

engine = sqlalchemy.create_engine(database_url)

# -----------------------
# 2. Pobranie danych z ticket_history
# -----------------------
query = """
SELECT
    id,
    input_text,
    category,
    priority,
    summary,
    suggested_action,
    source,
    executed_action_type,
    executed_action_status,
    executed_action_message,
    created_at,
    route_agent_name,
    route_department,
    route_reason,
    route_action_type
FROM ticket_history
"""
df = pd.read_sql(query, engine)
df['created_at'] = pd.to_datetime(df['created_at'])

# -----------------------
# 3. Filtr daty (ostatnie 30 dni)
# -----------------------
end_date = datetime.now()
start_date = end_date - timedelta(days=30)
df_filtered = df[(df['created_at'] >= start_date) & (df['created_at'] <= end_date)]

if df_filtered.empty:
    print("Brak zgłoszeń w wybranym okresie.")
else:
    df = df_filtered

# -----------------------
# 4. Podstawowe statystyki
# -----------------------
print("Liczba zgłoszeń wg kategorii:")
print(df['category'].value_counts(), "\n")

print("Liczba zgłoszeń wg priorytetu:")
print(df['priority'].value_counts(), "\n")

print("Liczba zgłoszeń wg statusu wykonania:")
print(df['executed_action_status'].value_counts(), "\n")

print("Najczęściej przypisani agenci:")
print(df['route_agent_name'].value_counts().head(10), "\n")

# -----------------------
# 5. Trend dzienny zgłoszeń wg kategorii
# -----------------------
df_daily = df.groupby([df['created_at'].dt.date, 'category']).size().unstack(fill_value=0)
df_daily.plot(kind='line', figsize=(12,6), marker='o')
plt.title("Liczba zgłoszeń dziennie wg kategorii")
plt.xlabel("Data")
plt.ylabel("Liczba zgłoszeń")
plt.grid(True)
plt.legend(title='Kategoria')
plt.tight_layout()
plt.show()

# -----------------------
# 6. Wykres kołowy udziału kategorii
# -----------------------
df['category'].value_counts().plot(
    kind='pie', autopct='%1.1f%%', figsize=(6,6), startangle=90
)
plt.title("Procentowy udział zgłoszeń wg kategorii")
plt.ylabel("")
plt.show()

# -----------------------
# 7. Wykres priorytetów wg agentów (słupkowy)
# -----------------------
priority_agent = df.pivot_table(
    index='route_agent_name',
    columns='priority',
    values='id',
    aggfunc='count',
    fill_value=0
)
priority_agent.plot(kind='bar', stacked=True, figsize=(12,6))
plt.title("Liczba zgłoszeń wg priorytetu i agenta")
plt.xlabel("Agent")
plt.ylabel("Liczba zgłoszeń")
plt.grid(axis='y')
plt.tight_layout()
plt.show()

# -----------------------
# 8. Trend priorytetów w czasie (dni)
# -----------------------
df_priority_time = df.groupby([df['created_at'].dt.date, 'priority']).size().unstack(fill_value=0)
df_priority_time.plot(kind='line', figsize=(12,6), marker='o')
plt.title("Trendy priorytetów zgłoszeń w czasie")
plt.xlabel("Data")
plt.ylabel("Liczba zgłoszeń")
plt.grid(True)
plt.legend(title='Priorytet')
plt.tight_layout()
plt.show()

# -----------------------
# 9. Eksport do CSV i Excel
# -----------------------
df.to_csv("ticket_history_report_filtered.csv", index=False)
df.to_excel("ticket_history_report_filtered.xlsx", index=False)
print("Raport wyeksportowany do CSV i Excel (30 dni).")