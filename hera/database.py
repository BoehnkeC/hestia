import sqlite3


class DB:
    def __init__(self):
        self._init_db()
        self.create_table("Person")  # ensure Person table exists at startup
        self._add_position_columns()  # ensure pos_x and pos_y columns exist

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

    def _add_position_columns(self):
        # Add pos_x and pos_y columns if they do not exist
        self.cursor.execute("PRAGMA table_info(Person)")
        columns = [col[1] for col in self.cursor.fetchall()]
        if "pos_x" not in columns:
            self.cursor.execute("ALTER TABLE Person ADD COLUMN pos_x INTEGER")
        if "pos_y" not in columns:
            self.cursor.execute("ALTER TABLE Person ADD COLUMN pos_y INTEGER")
        self.conn.commit()
