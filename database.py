# database.py
import aiosqlite

DATABASE = "roadtop.db"

async def init_db():
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                places_count INTEGER DEFAULT 0,
                level TEXT DEFAULT 'Новичок'
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS places (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                photo_url TEXT,
                review TEXT,
                user_id INTEGER,
                FOREIGN KEY(user_id) REFERENCES users(telegram_id)
            )
        ''')
        await db.commit()