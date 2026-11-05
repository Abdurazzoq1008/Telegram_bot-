import os
from dataclasses import dataclass
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class Config:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    CHANNEL_ID: str = os.getenv("CHANNEL_ID", "")
    CHECK_INTERVAL: int = int(os.getenv("CHECK_INTERVAL_SECONDS", "120"))
    DB_PATH: str = os.getenv("DB_PATH", "news.db")
    RSS_URL: str = "https://kun.uz/news/rss"

config = Config()

