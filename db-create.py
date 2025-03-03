import sqlite3
from dotenv import load_dotenv
import os


load_dotenv()
DB_FILE = os.getenv("DB_FILE")


def create_database():
    """ Creates the SQLite database and table if not exists """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS build_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_name TEXT NOT NULL,
            build_number INTEGER NOT NULL,
            status TEXT NOT NULL,
            duration INTEGER NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

# Create the database on first run
create_database()
