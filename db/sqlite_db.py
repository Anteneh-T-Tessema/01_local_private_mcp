# SQLite DB integration skeleton
import sqlite3

class SQLiteDB:
    def __init__(self, db_path="mcp_data.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL
            )
            """)

    def add_data(self, content):
        with self.conn:
            self.conn.execute("INSERT INTO data (content) VALUES (?)", (content,))

    def read_data(self, data_id):
        cur = self.conn.cursor()
        cur.execute("SELECT content FROM data WHERE id = ?", (data_id,))
        return cur.fetchone()
