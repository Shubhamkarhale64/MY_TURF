import sqlite3
import os

db_file = "db_backup.sqlite3"

if not os.path.exists(db_file):
    print("Backup file not found!")
else:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )

    for (table,) in cursor.fetchall():
        cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
        print(f"{table}: {cursor.fetchone()[0]} records")

    conn.close()