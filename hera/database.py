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
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS PersonRelation (
            id TEXT PRIMARY KEY,
            person_id TEXT,
            related_person_id TEXT,
            relation_type TEXT,
            FOREIGN KEY(person_id) REFERENCES Person(id),
            FOREIGN KEY(related_person_id) REFERENCES Person(id)
        )
    """)
        self.conn.commit()
