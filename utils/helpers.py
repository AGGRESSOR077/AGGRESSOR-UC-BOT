# 📁 JOYLASHUV: aggressor_uc_bot/utils/helpers.py
# ⚠ MAVJUD FAYL — bu faylni to'liq shu nom bilan almashtiring
# (yangi funksiyalar fayl oxiriga "YANGI FUNKSIYALAR" bo'limida qo'shilgan).
"""
AGGRESSOR UC BOT - Yordamchi funksiyalar moduli.

Bu modul loyiha bo'ylab qayta-qayta ishlatiladigan
kichik yordamchi funksiyalarni o'z ichiga oladi.
"""

from datetime import datetime
from typing import Optional

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


# ==========================================================
# YANGI FUNKSIYALAR UCHUN YORDAMCHI FUNKSIYALAR
# ==========================================================


def generate_referral_code(telegram_id: int) -> str:
    """
    Foydalanuvchi uchun unikal referral kod yaratadi.

    Kod Telegram ID asosida qisqa, o'qilishi oson formatda hosil qilinadi.
    Masalan: telegram_id=123456789 -> "REF123456789"
    """
    return f"REF{telegram_id}"


def generate_promo_code(prefix: str = "AGGR") -> str:
    """
    Tasodifiy, o'qilishi oson promo kod yaratadi.

    Masalan: generate_promo_code() -> "AGGR7F3K9Q"
    """
    import random
    import string

    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}{suffix}"


def is_valid_promo_code_format(code: str) -> bool:
    """Promo kod formati to'g'ri (faqat harf va raqamlardan iborat) ekanligini tekshiradi."""
    code = code.strip()
    if not code:
        return False
    return code.replace("_", "").replace("-", "").isalnum()


def calculate_uc_by_price(price: float, rate_per_uc: float) -> int:
    """
    Berilgan narx va 1 UC narxi asosida taxminiy UC miqdorini hisoblaydi.

    Args:
        price: Foydalanuvchi kiritgan summa (so'mda).
        rate_per_uc: 1 UC ning o'rtacha narxi (so'mda).
    """
    if rate_per_uc <= 0:
        return 0
    return int(price / rate_per_uc)


def calculate_price_by_uc(uc_amount: int, rate_per_uc: float) -> float:
    """
    Berilgan UC miqdori va 1 UC narxi asosida taxminiy summani hisoblaydi.

    Args:
        uc_amount: Foydalanuvchi kiritgan UC miqdori.
        rate_per_uc: 1 UC ning o'rtacha narxi (so'mda).
    """
    return uc_amount * rate_per_uc


def calculate_average_rate_per_uc(packages: list) -> float:
    """
    Mavjud paketlar asosida 1 UC ning o'rtacha narxini hisoblaydi.

    Args:
        packages: `Package` obyektlari ro'yxati (uc_amount va price maydonlari bilan).
    """
    valid_packages = [p for p in packages if p.uc_amount > 0]
    if not valid_packages:
        return 0.0
    rates = [p.price / p.uc_amount for p in valid_packages]
    return sum(rates) / len(rates)


def apply_percent_discount(price: float, percent: int) -> float:
    """Narxga foizli chegirma qo'llaydi va yangi narxni qaytaradi."""
    if percent <= 0:
        return price
    discounted = price - (price * percent / 100)
    return max(discounted, 0)


def apply_fixed_discount(price: float, amount: float) -> float:
    """Narxdan belgilangan summa chegirmasini ayiradi (manfiy bo'lmaydi)."""
    return max(price - amount, 0)


def calculate_expiry_datetime(minutes: int) -> str:
    """
    Joriy vaqtdan boshlab belgilangan daqiqadan keyingi vaqtni
    database formatida qaytaradi (Auto Cancel muddati uchun).
    """
    from datetime import timedelta

    expiry = datetime.now() + timedelta(minutes=minutes)
    return expiry.strftime("%Y-%m-%d %H:%M:%S")


def calculate_expiry_date_from_days(days: int) -> Optional[str]:
    """
    Joriy vaqtdan boshlab belgilangan kundan keyingi sanani
    database formatida qaytaradi (Promo kod muddati uchun).

    Agar days <= 0 bo'lsa, cheksiz muddat sifatida None qaytaradi.
    """
    from datetime import timedelta

    if days <= 0:
        return None
    expiry = datetime.now() + timedelta(days=days)
    return expiry.strftime("%Y-%m-%d %H:%M:%S")


def paginate_index_range(page: int, page_size: int, total_items: int) -> str:
    """
    Pagination uchun "1-10 / 45" ko'rinishidagi diapazon matnini qaytaradi.
    """
    start = (page - 1) * page_size + 1
    end = min(page * page_size, total_items)
    return f"{start}-{end} / {total_items}"


def mask_card_number(card_number: str) -> str:
    """
    Karta raqamini qisman yashiradi (masalan: "8600 1234 5678 9012"
    -> "8600 **** **** 9012") — admin ro'yxatlarida xavfsizroq ko'rsatish uchun.
    """
    digits_only = card_number.replace(" ", "")
    if len(digits_only) < 8:
        return card_number
    return f"{digits_only[:4]} **** **** {digits_only[-4:]}"
