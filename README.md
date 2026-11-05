# Kun.uz Auto-Poster Telegram Boti

Bu bot **Kun.uz** saytidan yangi chiqqan xabarlarni avtomatik tarzda aniqlaydi va sizning shaxsiy Telegram kanalingizga rasm, sarlavha, qisqacha tavsif va chiroyli tugmalar bilan joylab boradi.

---

##  Bu botning boshqalardan ustunliklari:
1. **To'liq Asinxron (`aiogram 3.x`, `aiohttp`, `aiosqlite`)**: Bot hech qachon qotib qolmaydi yoki Telegram tezligini pasaytirmaydi.
2. **Dublikat bo'lmaydi**: SQLite bazasida yuborilgan har bir postning unikal havolasi saqlanadi — bir xabar qayta tashlanmaydi (botni o'chirib yoqsangiz ham).
3. **Rasmlar bilan**: RSS dagi har bir yangilikning asosiy rasmini avtomatik ajratib olib, postni rasm tagida (caption) qilib yuboradi.
4. **Chiroyli format va tugmalar**: " Batafsil o'qish" va " Ulashish" inline tugmalari bilan postlar professional ko'rinishga ega bo'ladi.
5. **Anti-flood & Xatolikdan himoya**: Telegram spam chegarasiga tushmaslik uchun navbat bilan xavfsiz yuborish mexanizmiga ega.

---

## 🛠 O'rnatish va ishga tushirish

### 1. Kerakli kutubxonalarni o'rnatish
Terminalda loyiha papkasiga kiring va quyidagilarni o'rnating:
```bash
pip install -r requirements.txt
```

### 2. Sozlamalarni kiritish (.env)
Loyihada `.env` faylini oching (yoki `.env.example` dan nusxa olib `.env` nomlang):
```env
BOT_TOKEN=123456789:ABCDefghIJKLmnOPQRstuvWXYZ
CHANNEL_ID=@sizning_kanalingiz
CHECK_INTERVAL_SECONDS=120
```

> **Muhim eslatma:**
> 1. `@BotFather` dan olgan bot tokeningizni kiriting.
> 2. Botingizni kanalingizga **Admin** qilib qo'shing va unga **Post yuborish (Post messages)** huquqini bering.
> 3. `CHANNEL_ID` o'rniga ochiq kanal bo'lsa `@kanalingiz_nomi`, yopiq kanal bo'lsa ID raqamini (masalan: `-1001234567890`) yozing.

### 3. Botni ishga tushirish
```bash
python main.py
```

