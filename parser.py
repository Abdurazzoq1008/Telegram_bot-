import aiohttp
import feedparser
import re
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_html(raw_html: str) -> str:
    """HTML teglarini tozalab, chiroyli matn qaytaradi."""
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text

def extract_image(entry) -> Optional[str]:
    """Yangilik ichidan eng sifatli rasm URLini ajratib oladi."""
    # 1. media_content tekshirish
    if hasattr(entry, "media_content") and entry.media_content:
        for media in entry.media_content:
            if "url" in media:
                return media["url"]

    # 2. enclosures tekshirish
    if hasattr(entry, "enclosures") and entry.enclosures:
        for enc in entry.enclosures:
            if enc.get("type", "").startswith("image/") or "url" in enc:
                return enc.get("url")

    # 3. description yoki content ichidagi <img> tegini tekshirish
    content_html = ""
    if hasattr(entry, "content") and entry.content:
        content_html = entry.content[0].value
    elif hasattr(entry, "summary"):
        content_html = entry.summary

    if content_html:
        soup = BeautifulSoup(content_html, "html.parser")
        img = soup.find("img")
        if img and img.get("src"):
            return img["src"]

    return None

async def fetch_article_image(url: str) -> Optional[str]:
    """Maqola sahifasidan og:image rasmini oladi."""
    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    og_img = soup.find("meta", property="og:image")
                    if og_img and og_img.get("content"):
                        return og_img["content"]
    except Exception as e:
        logger.warning(f"Rasm olishda xatolik ({url}): {e}")
    return None

class KunUzParser:
    def __init__(self, rss_url: str = "https://kun.uz/news/rss"):
        self.rss_url = rss_url

    async def fetch_latest_news(self) -> List[Dict]:
        """RSS orqali eng so'nggi yangiliklarni yuklab oladi."""
        try:
            async with aiohttp.ClientSession(headers=HEADERS) as session:
                async with session.get(self.rss_url, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    if resp.status != 200:
                        logger.error(f"Kun.uz RSS xato status qaytardi: {resp.status}")
                        return []
                    content = await resp.text()

            feed = feedparser.parse(content)
            news_items = []

            for entry in feed.entries:
                link = entry.get("link", "").strip()
                title = entry.get("title", "").strip()
                summary_raw = entry.get("summary", "")
                summary = clean_html(summary_raw)
                
                # Qisqa tavsifni chiroyli qisqartirish (agar uzun bo'lsa)
                if len(summary) > 450:
                    summary = summary[:447].rsplit(" ", 1)[0] + "..."

                published = entry.get("published", "")
                image_url = extract_image(entry)

                if link and title:
                    news_items.append({
                        "link": link,
                        "title": title,
                        "summary": summary,
                        "image_url": image_url,
                        "published": published
                    })

            # RSS da eng yangilari yuqorida turadi, biz tartib bilan ketma-ket tashlash uchun teskari qilamiz
            news_items.reverse()
            return news_items

        except Exception as e:
            logger.error(f"Kun.uz yangiliklarini olishda xatolik: {e}")
            return []

