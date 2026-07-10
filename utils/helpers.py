"""
AGGRESSOR UC BOT - Yordamchi funksiyalar moduli.

Bu modul loyiha bo'ylab qayta-qayta ishlatiladigan
kichik yordamchi funksiyalarni o'z ichiga oladi.
"""

from datetime import datetime

import pytz

from config import config


def format_price(price: float) -> str:
    """
    Narxni foydalanuvchiga chiroyli ko'rinishda formatlaydi.

    Masalan: 150000 -> "150 000 so'm"
    """
    return f"{price:,.0f} so'm".replace(",", " ")


def is_valid_pubg_uid(uid: str) -> bool:
    """
    PUBG Mobile UID formatini tekshiradi.

    UID faqat raqamlardan iborat bo'lishi va uzunligi
    5 tadan 15 tagacha bo'lishi kerak.
    """
    uid = uid.strip()
    if not uid.isdigit():
        return False
    if len(uid) < 5 or len(uid) > 15:
        return False
    return True


def is_valid_number(value: str) -> bool:
    """Berilgan qator faqat musbat butun sondan iboratligini tekshiradi."""
    value = value.strip()
    return value.isdigit() and int(value) > 0


def is_valid_price(value: str) -> bool:
    """
    Berilgan qator to'g'ri narx (musbat butun yoki kasr son)
    ekanligini tekshiradi.
    """
    value = value.strip().replace(" ", "")
    try:
        price = float(value)
        return price > 0
    except ValueError:
        return False


def get_local_datetime() -> datetime:
    """Konfiguratsiyada belgilangan timezone bo'yicha joriy vaqtni qaytaradi."""
    tz = pytz.timezone(config.TIMEZONE)
    return datetime.now(tz)


def format_datetime_display(raw_datetime: str) -> str:
    """
    Database'dagi 'YYYY-MM-DD HH:MM:SS' formatidagi sanani
    foydalanuvchi uchun o'qilishi oson formatga o'tkazadi.

    Masalan: "2025-01-15 14:30:00" -> "15.01.2025 14:30"
    """
    try:
        dt = datetime.strptime(raw_datetime, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d.%m.%Y %H:%M")
    except (ValueError, TypeError):
        return raw_datetime


def escape_html(text: str) -> str:
    """
    Telegram HTML parse_mode uchun maxsus belgilarni escape qiladi.

    Foydalanuvchi kiritgan matnlarni (username, full_name va h.k.)
    xabar ichida ishlatishdan oldin ishlatiladi.
    """
    if not text:
        return ""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def get_username_display(username: str, telegram_id: int) -> str:
    """
    Username mavjud bo'lsa @username, aks holda Telegram ID
    ko'rinishida qaytaradi (admin xabarlarida ishlatish uchun).
    """
    if username:
        return f"@{escape_html(username)}"
    return f"ID: <code>{telegram_id}</code>"


def truncate_text(text: str, max_length: int = 50) -> str:
    """Uzun matnlarni belgilangan uzunlikkacha qisqartiradi va '...' qo'shadi."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def chunk_list(items: list, chunk_size: int) -> list:
    """
    Ro'yxatni belgilangan o'lchamdagi kichik bo'laklarga bo'ladi.

    Inline keyboard tugmalarini qatorlarga taqsimlash uchun ishlatiladi.
    Masalan: chunk_list([1,2,3,4,5], 2) -> [[1,2], [3,4], [5]]
    """
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
