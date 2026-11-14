import sqlite3
from config import DATABASE_PATH


class ItemDatabase:

    def __init__(self):

        self.create_tables()


    def connect(self):

        return sqlite3.connect(DATABASE_PATH)


    def create_tables(self):

        with self.connect() as conn:

            conn.execute("""
                CREATE TABLE IF NOT EXISTS items (

                    id INTEGER PRIMARY KEY AUTOINCREMENT,

                    item_name TEXT NOT NULL,

                    description TEXT,

                    category TEXT,

                    location TEXT,

                    image_path TEXT NOT NULL,

                    item_type TEXT NOT NULL,

                    status TEXT DEFAULT 'active',

                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS
                idx_items_type_status
                ON items(item_type, status)
            """)


    def add_item(
        self,
        item_name,
        description,
        category,
        location,
        image_path,
        item_type
    ):

        with self.connect() as conn:

            cursor = conn.execute("""
                INSERT INTO items (

                    item_name,
                    description,
                    category,
                    location,
                    image_path,
                    item_type

                )

                VALUES (?, ?, ?, ?, ?, ?)

            """, (
                item_name,
                description,
                category,
                location,
                image_path,
                item_type
            ))

            return cursor.lastrowid


    def get_item(self, item_id):

        with self.connect() as conn:

            conn.row_factory = sqlite3.Row

            item = conn.execute("""
                SELECT *
                FROM items
                WHERE id = ?
            """, (item_id,)).fetchone()

            return dict(item) if item else None


    def get_items(self, item_type=None):

        with self.connect() as conn:

            conn.row_factory = sqlite3.Row

            if item_type:

                rows = conn.execute("""
                    SELECT *
                    FROM items
                    WHERE item_type = ?
                    AND status = 'active'
                    ORDER BY created_at DESC
                """, (item_type,)).fetchall()

            else:

                rows = conn.execute("""
                    SELECT *
                    FROM items
                    WHERE status = 'active'
                    ORDER BY created_at DESC
                """).fetchall()

            return [dict(row) for row in rows]


    def delete_item(self, item_id):

        with self.connect() as conn:

            cursor = conn.execute("""
                DELETE FROM items
                WHERE id = ?
            """, (item_id,))

            return cursor.rowcount > 0


    def update_status(self, item_id, status):

        allowed_statuses = {
            "active",
            "resolved"
        }

        if status not in allowed_statuses:

            raise ValueError("Invalid item status")

        with self.connect() as conn:

            cursor = conn.execute("""
                UPDATE items
                SET status = ?
                WHERE id = ?
            """, (status, item_id))

            return cursor.rowcount > 0
