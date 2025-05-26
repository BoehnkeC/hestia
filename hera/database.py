import sqlite3


class DB:
    def __init__(self):
        self._init_db()
        self.create_table("Person")  # ensure Person table exists at startup

    def _init_db(self):
        self.conn = sqlite3.connect("family_tree.db")
        self.cursor = self.conn.cursor()

    def create_table(self, name: str):
        self.cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {name} (
            id TEXT PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            date_of_birth TEXT
        )
        """)
        self.conn.commit()
