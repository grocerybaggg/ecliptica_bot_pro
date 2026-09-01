import json
import aiosqlite
from datetime import datetime, timezone

DB_PATH = "/app/data/ecliptica.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            university TEXT NOT NULL,
            faculty TEXT NOT NULL,
            task TEXT NOT NULL,
            file_ids TEXT NOT NULL DEFAULT '[]',
            contact TEXT,
            source TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'new',
            created_at TEXT NOT NULL
        )
        """)
        await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_requests_user_status
        ON requests(user_id, status)
        """)
        await db.commit()

async def create_request(user_id, username, university, faculty, task,
                         file_ids, contact, source):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            INSERT INTO requests
            (user_id, username, university, faculty, task, file_ids,
             contact, source, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'new', ?)
        """, (
            user_id, username, university, faculty, task,
            json.dumps(file_ids, ensure_ascii=False),
            contact, source,
            datetime.now(timezone.utc).isoformat()
        ))
        await db.commit()
        return cur.lastrowid

async def get_request(request_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT * FROM requests WHERE id=?", (request_id,)
        )
        row = await cur.fetchone()
        return dict(row) if row else None

async def set_status(request_id, status):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE requests SET status=? WHERE id=?",
            (status, request_id)
        )
        await db.commit()

async def has_active_request(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            SELECT id FROM requests
            WHERE user_id=? AND status IN ('new', 'accepted')
            LIMIT 1
        """, (user_id,))
        return await cur.fetchone()

async def get_last_request_time(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("""
            SELECT created_at FROM requests
            WHERE user_id=?
            ORDER BY id DESC LIMIT 1
        """, (user_id,))
        row = await cur.fetchone()
        return row[0] if row else None
