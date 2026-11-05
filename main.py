import asyncio
import html
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, URLInputFile
from aiogram.filters import Command

from config import config
from database import Database
from parser import KunUzParser, fetch_article_image

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Windows tarmoq uzilishlarini (WinError 1236) oldini olish uchun sessiya timeout sozlamasi
session = AiohttpSession(timeout=30.0)
bot = Bot(token=config.BOT_TOKEN, session=session)
dp = Dispatcher()
db = Database(config.DB_PATH)
parser = KunUzParser(config.RSS_URL)

def create_news_keyboard(news_url: str) -> InlineKeyboardMarkup:
    """Post ostidagi tugma (To'liq o'qish va ulashish)."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=" Batafsil o'qish", url=news_url),
            InlineKeyboardButton(text=" Ulashish", url=f"https://t.me/share/url?url={news_url}")
        ]
    ])
    return keyboard

def format_news_post(news: dict) -> str:
    """Postni estetik va zamonaviy ko'rinishda formatlash."""
    title = html.escape(news.get("title", "").strip())
    summary = html.escape(news.get("summary", "").strip())
    link = news.get("link", "")
    
    # HTML formatlash
    post_text = (
        f"<b>{title}</b>\n\n"
        f"{summary}\n\n"
        f"<a href=\"{link}\">Batafsil Kun.uz saytida o'qing</a>\n\n"
        f"<i>Bizning kanalga obuna bo'ling!</i>"
    )
    return post_text

async def post_news_to_channel(news: dict):
    """Kanalga yangilikni rasm va tugmalar bilan yuborish."""
    caption = format_news_post(news)
    keyboard = create_news_keyboard(news["link"])
    image_url = news.get("image_url")

    try:
        if image_url:
            await bot.send_photo(
                chat_id=config.CHANNEL_ID,
                photo=image_url,
                caption=caption,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
        else:
            await bot.send_message(
                chat_id=config.CHANNEL_ID,
                text=caption,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False,
                reply_markup=keyboard
            )
        logger.info(f"Yangi xabar kanalga yuborildi: {news['title']}")
        return True
    except Exception as e:
        logger.error(f"Xabarni kanalga yuborishda xatolik yuz berdi: {e}")
        # Agar rasm yuklashda xatolik bo'lsa (URL noto'g'ri bo'lsa), matn sifatida yuborib ko'ramiz
        if image_url:
            try:
                await bot.send_message(
                    chat_id=config.CHANNEL_ID,
                    text=caption,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard
                )
                return True
            except Exception as ex:
                logger.error(f"Zaxira matn yuborishda ham xatolik: {ex}")
        return False

async def news_monitor_loop():
    """Doimiy ravishda yangi xabarlarni tekshirib turuvchi fon jarayoni."""
    logger.info("Yangiliklar monitoringi ishga tushdi...")
    while True:
        try:
            news_items = await parser.fetch_latest_news()
            for news in news_items:
                link = news["link"]
                # Agar ushbu yangilik avval yuborilmagan bo'lsa
                if not await db.is_posted(link):
                    if not news.get("image_url"):
                        news["image_url"] = await fetch_article_image(link)
                    success = await post_news_to_channel(news)
                    if success:
                        await db.save_news(link=link, title=news["title"], published_at=news.get("published", ""))
                    # Telegram spam filtrlari (FloodWait)ga tushmaslik uchun 3 soniya kutish
                    await asyncio.sleep(3)

        except Exception as e:
            logger.error(f"Monitoring davomida kutilmagan xatolik: {e}")

        # Belgilangan vaqtcha kutish (masalan, 2 daqiqa)
        await asyncio.sleep(config.CHECK_INTERVAL)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    count = await db.get_stats()
    await message.answer(
        f" Assalomu alaykum!\n\n"
        f"Kun.uz Auto-Poster boti faol ishlamoqda.\n"
        f" Hozirgacha kanalga yuborilgan jami yangiliklar soni: <b>{count} ta</b>.\n\n"
        f" Kanal sozlamasi: <code>{config.CHANNEL_ID}</code>\n"
        f" Interval: <code>{config.CHECK_INTERVAL} soniya</code>",
        parse_mode=ParseMode.HTML
    )

@dp.message(Command("check"))
async def cmd_check(message: types.Message):
    """Qo'lda darhol yangiliklarni tekshirish buyrug'i."""
    await message.answer(" Yangi xabarlar tekshirilmoqda...")
    news_items = await parser.fetch_latest_news()
    new_count = 0
    for news in news_items:
        if not await db.is_posted(news["link"]):
            if not news.get("image_url"):
                news["image_url"] = await fetch_article_image(news["link"])
            if await post_news_to_channel(news):
                await db.save_news(news["link"], news["title"], news.get("published", ""))
                new_count += 1
                await asyncio.sleep(2)
    await message.answer(f" Tekshiruv tugadi. Yangi joylangan postlar soni: {new_count}")

async def main():
    if not config.BOT_TOKEN or config.BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.error("DIQQAT: .env faylida BOT_TOKEN ko'rsatilmagan! Iltimos, token kiriting.")
        return

    # Ma'lumotlar bazasini initsializatsiya qilish
    await db.init()

    # Yangiliklar monitoringini fon rejimida boshlash
    asyncio.create_task(news_monitor_loop())

    logger.info("Bot muvaffaqiyatli ishga tushirildi.")
    # Bot polling jarayoni (tarmoq uzilishlarini kamaytirish uchun polling_timeout=20)
    await dp.start_polling(bot, polling_timeout=20)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")

