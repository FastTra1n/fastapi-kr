import sqlite3

DB_NAME = "./todo.sqlite"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE
)
""")

conn.commit()
conn.close()