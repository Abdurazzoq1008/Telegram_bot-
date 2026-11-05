import aiosqlite
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "news.db"):
        self.db_path = db_path

    async def init(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS posted_news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link TEXT UNIQUE,
                    title TEXT,
                    published_at TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Agar eski baza mavjud bo'lsa, yetishmayotgan ustunlarni avtomatik qo'shish (Migration)
            try:
                await db.execute("ALTER TABLE posted_news ADD COLUMN published_at TEXT")
            except Exception:
                pass  # Ustun allaqachon mavjud bo'lsa xatoni e'tiborsiz qoldiramiz

            try:
                await db.execute("ALTER TABLE posted_news ADD COLUMN title TEXT")
            except Exception:
                pass

            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_link ON posted_news(link)
            """)
            await db.commit()

    async def is_posted(self, link: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT 1 FROM posted_news WHERE link = ?", (link,)) as cursor:
                row = await cursor.fetchone()
                return row is not None

    async def save_news(self, link: str, title: str, published_at: str = ""):
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT OR IGNORE INTO posted_news (link, title, published_at) VALUES (?, ?, ?)",
                    (link, title, published_at)
                )
                await db.commit()
        except Exception as e:
            logger.error(f"Xatolik bazaga yozishda: {e}")

    async def get_stats(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM posted_news") as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

