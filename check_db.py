import sqlite3

conn = sqlite3.connect("medical_diagnosis_assistant.db")
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [r[0] for r in c.fetchall() if r[0] != 'sqlite_sequence']

print("======================================================")
print("DATABASE: medical_diagnosis_assistant.db SUMMARY")
print("======================================================")
for t in tables:
    c.execute(f"SELECT count(*) FROM {t};")
    cnt = c.fetchone()[0]
    print(f"Table: {t:<25} | Rows: {cnt}")
print("======================================================")
conn.close()
